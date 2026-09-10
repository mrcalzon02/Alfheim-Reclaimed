"""The shared detail vocabulary: the five layers `THE_SURFACE.md` 3.2 asks every ruin to carry.

Design record: `alfheim_reclaimed_design/THE_SURFACE.md` 3.2 and 7 (passes 5 and 6).
Checker: `tools/check_structure_detail.py`. Users: `gen_surface_works.py`,
`gen_deep_archaeology.py`, `gen_spawn_hub.py`, `gen_leyline_corridors.py`,
`gen_pixie_settlements.py`.

Extracted for the same reason `structure_nbt.py` was: a second generator needed it, and
copying it would have made two divergent answers to one question. The question here is
"what turns a correct silhouette into a place somebody lived in", and the 2026-09-07 field
review answered it with five named layers -- monumental massing, architectural logic, elven
technology, causal decay, human-scale residue. Four of the five were missing from every
generator in the pack, and the census that proved it is in `EXECUTION_STATE.md`: the
Greatbole, the leyline corridors and every crater carried a **zero** detail-block share.

THE ONE IDEA THAT MAKES THIS REUSABLE
-------------------------------------
A pass here is never told where the rooms are. It **reads the finished piece** and derives
its own candidates from geometry: a wall face is a solid with a free cell beside it, a floor
is a solid with headroom above it, an overhang is a solid with nothing under it. That is why
the same `sconces()` call works on a castle keep, a mine drift and a pixie house without any
of the three declaring a floor plan -- and why a builder can be rewritten without breaking
its detailing.

THREE INVARIANTS EVERY PASS HOLDS, BECAUSE A CHECKER ASSERTS THEM
-----------------------------------------------------------------
1.  **Nothing is placed that touches nothing.** Every candidate is derived from an existing
    solid and placed against it, so `check_spawn_hub.py` S11 stays clean by construction.
    A block resting on a cell the piece does not own is supported too -- `place template`
    leaves terrain there.
2.  **Nothing overwrites a block entity or a jigsaw.** Chests, spawners, barrels and jigsaw
    blocks are load-bearing for loot, encounters and assembly. Passes skip any cell whose
    entry carries NBT.
3.  **Nothing is placed into a cell the builder carved on purpose**, unless the pass exists
    to do that. Explicit `minecraft:air` is a carved interior; an absent cell is untouched
    world. The asymmetry is the same one the crater and the quarry stand on, and it is the
    cheapest interior/exterior discriminator in the codebase -- `unowned()` means "outside
    the built envelope", so exterior trim can project into it without ever blocking a route.

ORDER MATTERS, AND IT IS CAUSAL
-------------------------------
`dress()` runs **before** the decay pass and `aftermath()` runs **after** it. That is not a
convention, it is the mechanism: detail applied before decay is what the building HAD, so
decay eats it in the same places it eats the walls, and what survives is residue rather than
decoration. Detail applied after decay is what the collapse DID -- debris at the foot of the
wall it fell from, moss where the roof stopped keeping the rain out, roots through the floor
that no longer has anyone sweeping it.
"""
import math
import random

# --------------------------------------------------------------------------- vocabulary

STEP = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}
OPPOSITE = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
FACES6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))

AIR_NAMES = frozenset({'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'})

# Blocks that do not hold anything up and must not be treated as mass. Kept in step with
# `gen_surface_works.NON_SOLID`; anything a pass places is added here as it is introduced,
# because a sconce is not a wall to hang the next sconce on.
NON_SOLID = frozenset({
    'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air', 'minecraft:water',
    'minecraft:lava', 'minecraft:torch', 'minecraft:wall_torch', 'minecraft:soul_torch',
    'minecraft:soul_wall_torch', 'minecraft:lantern', 'minecraft:soul_lantern',
    'minecraft:vine', 'minecraft:cobweb', 'minecraft:rail', 'minecraft:ladder',
    'minecraft:chain', 'minecraft:moss_carpet', 'minecraft:scaffolding',
    'minecraft:flower_pot', 'minecraft:pointed_dripstone', 'minecraft:lightning_rod',
    'minecraft:campfire', 'minecraft:soul_campfire', 'minecraft:cauldron',
    'minecraft:hanging_roots', 'minecraft:end_rod', 'minecraft:candle',
    'minecraft:decorated_pot', 'minecraft:lectern', 'minecraft:sea_pickle',
    'minecraft:big_dripleaf', 'minecraft:small_dripleaf',
})

# Every id below was checked against `tools/registry_items.json`, the registry dumped from a
# running server. An unknown block does not error -- `NbtUtils.readBlockState` returns AIR --
# so a typo here ships a hole rather than a crash. `minecraft:wall_torch` has no item and is
# in the checker's NO_ITEM exemption; it is legal and deliberate.
CHAIN = 'minecraft:chain'
COBWEB = 'minecraft:cobweb'
MOSS_CARPET = 'minecraft:moss_carpet'
HANGING_ROOTS = 'minecraft:hanging_roots'
END_ROD = 'minecraft:end_rod'
WALL_TORCH = 'minecraft:wall_torch'
SOUL_WALL_TORCH = 'minecraft:soul_wall_torch'


def _b(name, **props):
    """A block state tuple. Booleans become Minecraft's 'true'/'false' strings."""
    if not props:
        return (name, None)
    return (name, {k: (('true' if v else 'false') if isinstance(v, bool) else str(v))
                   for k, v in props.items()})


def stair(name, facing, half='bottom', shape='straight'):
    return _b(name, facing=facing, half=half, shape=shape, waterlogged=False)


def slab(name, kind='bottom'):
    return _b(name, type=kind, waterlogged=False)


def pillar(name, ax='y'):
    return _b(name, axis=ax)


# --------------------------------------------------------------------------- the kit


class Kit:
    """The block roles a detail pass needs, resolved once per structure.

    Every generator in the pack keeps its palettes in a different shape -- the surface
    manifest has sixteen named slots, the pixie generator carries four per season, the
    leyline corridors have three. A `Kit` is the narrow waist between them: a caller names
    whatever it has and everything unnamed falls back to something that exists, so a pass
    never has to ask whether this particular palette happens to own a wall block.
    """

    ROLES = ('stone', 'brick', 'brick_cracked', 'brick_mossy', 'pillar', 'stairs', 'slab',
             'wall', 'floor', 'accent', 'timber', 'plank', 'fence', 'glass', 'light',
             'crystal', 'rubble', 'litter', 'torch')

    def __init__(self, **roles):
        unknown = set(roles) - set(self.ROLES)
        if unknown:
            raise KeyError(f'unknown detail role(s): {sorted(unknown)}')
        stone = roles.get('stone') or roles.get('brick') or roles.get('floor')
        if not stone:
            raise KeyError('a Kit needs at least one of stone, brick or floor')
        self.stone = stone
        self.brick = roles.get('brick', stone)
        self.brick_cracked = roles.get('brick_cracked', self.brick)
        self.brick_mossy = roles.get('brick_mossy', self.brick)
        self.pillar = roles.get('pillar', self.brick)
        self.stairs = roles.get('stairs')
        self.slab = roles.get('slab')
        self.wall = roles.get('wall')
        self.floor = roles.get('floor', stone)
        self.accent = roles.get('accent', self.brick)
        self.timber = roles.get('timber')
        self.plank = roles.get('plank', self.timber)
        self.fence = roles.get('fence')
        self.glass = roles.get('glass')
        self.light = roles.get('light', 'minecraft:lantern')
        self.torch = roles.get('torch', WALL_TORCH)
        self.crystal = roles.get('crystal')
        rubble = roles.get('rubble') or [stone]
        self.rubble = list(rubble) if isinstance(rubble, (list, tuple)) else [rubble]
        litter = roles.get('litter') or []
        self.litter = list(litter) if isinstance(litter, (list, tuple)) else [litter]

    @classmethod
    def from_surface_palette(cls, pal):
        """Build a kit from one `surface_works_manifest.json` palette."""
        return cls(**{r: pal[r] for r in cls.ROLES if r in pal})


# --------------------------------------------------------------------------- reading a piece


def name_at(p, x, y, z):
    e = p.blocks.get((x, y, z))
    return None if e is None else p.palette[e[0]]['Name']


def has_be(p, x, y, z):
    e = p.blocks.get((x, y, z))
    return e is not None and e[1] is not None


def is_solid(p, x, y, z):
    n = name_at(p, x, y, z)
    return n is not None and n not in NON_SOLID


def is_air(p, x, y, z):
    """Explicitly carved air: a cell the builder decided is empty."""
    return name_at(p, x, y, z) in AIR_NAMES


def unowned(p, x, y, z):
    """A cell the template never touches, so the world's own terrain survives there."""
    return (x, y, z) not in p.blocks


def free(p, x, y, z):
    """Nothing of ours is in the way -- carved air or untouched world."""
    n = name_at(p, x, y, z)
    return n is None or n in AIR_NAMES


def inside(p, x, y, z):
    sx, sy, sz = p.size
    return 0 <= x < sx and 0 <= y < sy and 0 <= z < sz


def supported(p, x, y, z):
    """True when a block placed here would touch something on at least one of six faces.

    The rule `check_spawn_hub.py` S11 applies, reproduced so passes can hold it *before*
    placing rather than being swept up afterwards. Outside the piece counts as supported --
    the world continues there.
    """
    for dx, dy, dz in FACES6:
        nx, ny, nz = x + dx, y + dy, z + dz
        if not inside(p, nx, ny, nz):
            return True
        e = p.blocks.get((nx, ny, nz))
        if e is None or p.palette[e[0]]['Name'] not in AIR_NAMES:
            return True
    return False


def forbidden(p, x, y, z):
    """Cells a caller has declared off limits to every pass in this module.

    Set `piece.detail_forbidden` to a set of `(x, y, z)` before calling `dress` or
    `aftermath`. The spawn hub needs it: `check_spawn_hub.py` S10 and S12 assert that the
    processional route through each civic wing is *explicitly* `minecraft:air` for its whole
    cross-section, so one hanging lantern in the wrong corridor cell fails a gate that exists
    because a field session found the wings dead-ended. A pass cannot discover that rule from
    geometry -- the cells look like an ordinary room -- so the caller states it.
    """
    keep = getattr(p, 'detail_forbidden', None)
    return bool(keep) and (x, y, z) in keep


def place(p, x, y, z, block, protect_be=True):
    """Place a detail block, refusing every case a pass must never win.

    Returns True when the block went in. The five refusals are the invariants in the module
    docstring plus the piece bound and the caller's declared exclusions, and having them in
    one function is what keeps eight passes from each re-deriving them slightly differently.
    """
    if not inside(p, x, y, z):
        return False
    if protect_be and has_be(p, x, y, z):
        return False
    if name_at(p, x, y, z) == 'minecraft:jigsaw':
        return False
    if forbidden(p, x, y, z):
        return False
    if not supported(p, x, y, z):
        return False
    p.set(x, y, z, block)
    return True


def wall_faces(p, y0=None, y1=None, exterior=None):
    """Every (pos, direction) where a solid block presents a vertical face to a free cell.

    `exterior=True` restricts to faces opening onto **unowned** space, which is outside the
    built envelope by construction; `exterior=False` restricts to carved interior air.
    """
    out = []
    for (x, y, z), (idx, be) in p.blocks.items():
        if be is not None:
            continue
        if p.palette[idx]['Name'] in NON_SOLID:
            continue
        if y0 is not None and y < y0:
            continue
        if y1 is not None and y > y1:
            continue
        for face, (dx, dz) in STEP.items():
            nx, nz = x + dx, z + dz
            if not inside(p, nx, y, nz):
                continue
            if not free(p, nx, y, nz):
                continue
            if exterior is True and not unowned(p, nx, y, nz):
                continue
            if exterior is False and not is_air(p, nx, y, nz):
                continue
            out.append(((x, y, z), face))
    out.sort()
    return out


def floor_cells(p, headroom=2, y0=None, y1=None, interior_only=True):
    """Every walkable cell: a free cell with a solid floor under it and headroom above.

    `interior_only` demands the cell itself be carved air, which is how a builder says "this
    is a room" -- an unowned cell over a floor is just the top of an outside wall.
    """
    out = []
    for (x, y, z), (idx, be) in p.blocks.items():
        if be is not None or p.palette[idx]['Name'] in NON_SOLID:
            continue
        fy = y + 1
        if y0 is not None and fy < y0:
            continue
        if y1 is not None and fy > y1:
            continue
        if not inside(p, x, fy, z):
            continue
        if interior_only:
            if not is_air(p, x, fy, z):
                continue
        elif not free(p, x, fy, z):
            continue
        ok = True
        for h in range(1, headroom):
            if not free(p, x, fy + h, z):
                ok = False
                break
        if ok:
            out.append((x, fy, z))
    out.sort()
    return out


def ceiling_over(p, x, y, z, limit=6):
    """The y of the first solid block above (x, y, z), or None inside `limit`."""
    for h in range(1, limit + 1):
        cy = y + h
        if not inside(p, x, cy, z):
            return None
        if is_solid(p, x, cy, z):
            return cy
    return None


def exposed_tops(p, y0=None):
    """Solid blocks with nothing above them: the silhouette, and where weather lands."""
    out = []
    for (x, y, z), (idx, be) in p.blocks.items():
        if be is not None or p.palette[idx]['Name'] in NON_SOLID:
            continue
        if y0 is not None and y < y0:
            continue
        if not inside(p, x, y + 1, z):
            continue
        if free(p, x, y + 1, z):
            out.append((x, y, z))
    out.sort()
    return out


# --------------------------------------------------------------------------- layer 1+2
#   monumental massing and architectural logic


def exterior_trim(p, seed, kit, ys, rate=0.85, half='top'):
    """Cornices, string courses and plinths: a projecting course that breaks a flat face.

    Placed into **unowned** cells only, so it can never seal a door, a window or a route --
    the piece has already declared every cell it cares about, and this uses the ones it did
    not. A 34-block curtain wall with one moulded course at eaves height reads as
    architecture; the same wall without it reads as a texture swatch, which is what the field
    review said about the keeps.
    """
    if not kit.stairs or not ys:
        return 0
    rng = random.Random(seed ^ 0x5C0BE)
    n = 0
    ys = set(ys)
    for (x, y, z), face in wall_faces(p, exterior=True):
        if y not in ys or rng.random() > rate:
            continue
        dx, dz = STEP[face]
        if place(p, x + dx, y, z + dz, stair(kit.stairs, face, half=half)):
            n += 1
    return n


def corbels(p, seed, kit, rate=0.35, y0=None):
    """Brackets under an overhang, and under the outer edge of a walkway or balcony.

    An overhang with nothing under it is the single most common reason a parametric ruin
    reads as a stamped box: real masonry cannot do it, so the eye rejects it even when it
    cannot say why. This finds solids whose underside is open to unowned space and puts a
    bracket there.
    """
    if not kit.stairs:
        return 0
    rng = random.Random(seed ^ 0xC0B0E1)
    n = 0
    for (x, y, z), (idx, be) in sorted(p.blocks.items()):
        if be is not None or p.palette[idx]['Name'] in NON_SOLID:
            continue
        if y0 is not None and y < y0:
            continue
        if not inside(p, x, y - 1, z) or not unowned(p, x, y - 1, z):
            continue
        if rng.random() > rate:
            continue
        # A bracket needs a wall to spring from: one horizontal neighbour, one level down,
        # that is solid. Without it this is a floating stair, which is the defect it exists
        # to remove rather than to add.
        for face, (dx, dz) in sorted(STEP.items()):
            if is_solid(p, x + dx, y - 1, z + dz):
                if place(p, x, y - 1, z, stair(kit.stairs, OPPOSITE[face], half='top')):
                    n += 1
                break
    return n


def openings(p, seed, kit, rate=0.7, min_height=3):
    """Arch heads and projecting sills, so a hole in a wall reads as a window or a door.

    A gap in a wall course is a hole. The same gap with an arched head and a sill under it is
    an opening somebody built, and the difference is two blocks.

    The conservative rules exist because this pass can otherwise seal a route. An arch head
    is only ever cut into the **topmost** cell of an opening at least `min_height` tall, so
    what is left is never shorter than two blocks; and the sill projects into unowned space
    outside the wall rather than eating the wall course under the opening.
    """
    if not kit.slab or not kit.stairs:
        return 0
    rng = random.Random(seed ^ 0x09E1)
    # Find the bottom of every opening: a free cell in a wall plane whose floor is solid.
    columns = []
    for (x, y, z), (idx, be) in sorted(p.blocks.items()):
        if be is not None or p.palette[idx]['Name'] in NON_SOLID:
            continue
        by = y + 1                                        # the cell above this solid sill
        if not inside(p, x, by, z) or not free(p, x, by, z):
            continue
        ns = is_solid(p, x, by, z - 1) and is_solid(p, x, by, z + 1)
        ew = is_solid(p, x - 1, by, z) and is_solid(p, x + 1, by, z)
        if not (ns or ew):
            continue
        top = by
        while inside(p, x, top + 1, z) and free(p, x, top + 1, z) and top - by < 6:
            top += 1
        if not inside(p, x, top + 1, z) or not is_solid(p, x, top + 1, z):
            continue                                      # open to the sky: not an opening
        columns.append((x, by, z, top, 'ew' if ns else 'ns'))
    n = 0
    for (x, by, z, top, run) in columns:
        if rng.random() > rate:
            continue
        # `run` is the axis the opening penetrates; the outward face is whichever side of it
        # is untouched world.
        faces = ('east', 'west') if run == 'ew' else ('south', 'north')
        outward = None
        for face in faces:
            dx, dz = STEP[face]
            if inside(p, x + dx, by, z + dz) and unowned(p, x + dx, by, z + dz):
                outward = face
                break
        if top - by + 1 >= min_height:
            if place(p, x, top, z, stair(kit.stairs, outward or faces[0], half='top')):
                n += 1
        if outward:
            dx, dz = STEP[outward]
            if place(p, x + dx, by - 1, z + dz, slab(kit.slab, 'top')):
                n += 1
    return n


# --------------------------------------------------------------------------- layer 3
#   elven technology and magic


def conduits(p, seed, kit, rate=0.6, node_every=5, min_run=4, y0=None, y1=None):
    """Mana channels run along the base of a wall, with a crystal node every few blocks.

    This is the layer the field review said was missing entirely: "medieval masonry with a
    different palette". A ley channel in the skirting -- accent stone, a crystal at the
    nodes, an emitter rod where a run ends against a wall -- is the cheapest possible way to
    say *this civilisation ran on something*, and it is legible from inside a dark room
    because the crystals light it.

    Runs are found geometrically: floor cells that touch a wall, grouped into straight lines,
    keeping only lines long enough to look deliberate. A two-block channel reads as a
    mistake.
    """
    if not kit.crystal:
        return 0
    rng = random.Random(seed ^ 0x1EA111)
    lines = {}
    for (x, y, z) in floor_cells(p, headroom=2, y0=y0, y1=y1):
        fy = y - 1                                    # the floor block itself
        for face in sorted(STEP):
            dx, dz = STEP[face]
            if not is_solid(p, x + dx, y, z + dz):
                continue
            # Group by the wall it hugs. The key must carry the coordinate the wall FIXES --
            # x for an east/west wall, z for a north/south one -- so that the run varies
            # along the wall instead of grouping cells that share no line at all.
            key = (face, y, x if dx else z)
            lines.setdefault(key, []).append((x, fy, z))
            break
    n = 0
    for key in sorted(lines):
        cells = sorted(lines[key])
        if len(cells) < min_run or rng.random() > rate:
            continue
        plain = masonry(kit)
        for i, (x, fy, z) in enumerate(cells):
            if has_be(p, x, fy, z) or name_at(p, x, fy, z) not in plain:
                continue
            if forbidden(p, x, fy, z):
                continue
            if i % node_every == node_every // 2:
                # A node in the floor channel grows upward out of it.
                p.set(x, fy, z, _b(kit.crystal, facing='up', waterlogged=False))
            else:
                p.set(x, fy, z, (kit.accent, None))
            n += 1
        # An emitter at the end of the run, standing on the channel it terminates.
        ex, efy, ez = cells[-1]
        if place(p, ex, efy + 1, ez, _b(END_ROD, facing='up')):
            n += 1
    return n


def masonry(kit):
    """The plain stone a pass is allowed to cut into: never carved trim, never a relic.

    This set is the whole reason a socket can be stamped into a wall safely. The tomb
    families frame every grave door in `moonstone_livingrock_carved` and a checker asserts
    those exact positions; the accent, the statues and the doors are all load-bearing for
    something. Plain brick, plain stone and plain floor are not.
    """
    return {kit.brick, kit.stone, kit.brick_cracked, kit.brick_mossy, kit.floor}


def crystal_sockets(p, seed, kit, count=3, y0=None):
    """A socket is a crystal set into a wall face, where a fitting was prised out or left.

    Deliberately rare and deliberately high: the read is "this was machinery", not "this is a
    mineral deposit". Placed into the wall itself rather than beside it, so it survives the
    decay pass exactly as the wall around it does -- and only into plain masonry, so it can
    never eat a carved frame that something else is counting.
    """
    if not kit.crystal or count <= 0:
        return 0
    rng = random.Random(seed ^ 0x50C4E7)
    plain = masonry(kit)
    faces = [f for f in wall_faces(p, y0=y0, exterior=False)
             if name_at(p, *f[0]) in plain]
    if not faces:
        faces = [f for f in wall_faces(p, y0=y0, exterior=True)
                 if name_at(p, *f[0]) in plain]
    if not faces:
        return 0
    rng.shuffle(faces)
    placed, seen = 0, []
    for (pos, face) in faces:
        if placed >= count:
            break
        if has_be(p, *pos):
            continue
        if any(abs(pos[0] - s[0]) + abs(pos[1] - s[1]) + abs(pos[2] - s[2]) < 5 for s in seen):
            continue
        if forbidden(p, *pos):
            continue
        # B-90 gave our clusters a real `facing`, so a socket points OUT of the wall it is set
        # into rather than defaulting upright. `wall_faces` already reports the direction of
        # the open side, which is the direction the crystal grew toward.
        p.set(pos[0], pos[1], pos[2], _b(kit.crystal, facing=face, waterlogged=False))
        seen.append(pos)
        placed += 1
    return placed


def sconces(p, seed, kit, spacing=5, rate=0.8, y0=None, y1=None, soul=False,
            bracket=True):
    """Interior light, hung the way a builder would hang it.

    Tall rooms get a lantern on a chain dropped from the ceiling; low rooms get a wall
    bracket, because a chain in a three-block room is a trip hazard rather than a fixture.
    Spacing is enforced on a lattice so a corridor gets a rhythm instead of a clump.

    Both forms are load-bearing in the Minecraft sense as well as the visual one: a lantern
    needs a block above it or below it or it pops off on the first block update, and a wall
    torch needs the wall it names. `bracket=False` suppresses the torch form for callers
    whose validator has no item for `minecraft:wall_torch` -- the underground families check
    their palettes against an item registry, and a torch has none.
    """
    rng = random.Random(seed ^ 0x5C0)
    torch = SOUL_WALL_TORCH if soul else kit.torch
    taken = set()
    n = 0
    for (x, y, z) in floor_cells(p, headroom=3, y0=y0, y1=y1):
        key = (x // spacing, y // 4, z // spacing)
        if key in taken or rng.random() > rate:
            continue
        wall = None
        threshold = False
        for face, (dx, dz) in sorted(STEP.items()):
            if is_solid(p, x + dx, y + 1, z + dz):
                wall = wall or face
            elif unowned(p, x + dx, y + 1, z + dz):
                threshold = True
        # A cell with untouched world beside it at head height is a doorway or a breach, not
        # a room. Lighting one puts a torch in the middle of the opening, which is where the
        # first run of this pass put one.
        if wall is None or threshold:
            continue
        cy = ceiling_over(p, x, y, z, limit=7)
        if cy is not None and cy - y >= 4:
            hung = False
            for cyy in range(cy - 1, y + 1, -1):
                if not place(p, x, cyy, z, pillar(CHAIN, 'y')):
                    break
                if cy - cyy >= 2:
                    hung = place(p, x, cyy - 1, z,
                                 _b(kit.light, hanging=True, waterlogged=False))
                    break
            if hung:
                taken.add(key)
                n += 1
                continue
        # A wall torch's `facing` is the direction it points away from what holds it, so a
        # bracket on the north wall faces south.
        if bracket and place(p, x, y + 1, z, _b(torch, facing=OPPOSITE[wall])):
            taken.add(key)
            n += 1
    return n


# --------------------------------------------------------------------------- layer 5
#   human-scale residue


def furnish(p, seed, kit, density=0.5, y0=None, y1=None, allow=None):
    """Benches, tables, shelves and vessels, against the walls where furniture actually goes.

    The rule that keeps this from becoming clutter: a piece of furniture must stand on a
    floor cell that touches a wall, with its own headroom free. Everything is placed as a
    single block or a block plus one -- nothing here needs a room to be rectangular, which
    is why it works in a round tower and a mine drift as well as a hall.
    """
    rng = random.Random(seed ^ 0xF0F0)
    catalogue = []
    if kit.stairs:
        catalogue.append('bench')
    if kit.slab and kit.fence:
        catalogue.append('table')
    catalogue += ['pot', 'cauldron', 'shelf', 'lectern', 'crate']
    if allow is not None:
        catalogue = [c for c in catalogue if c in allow]
    if not catalogue:
        return 0
    taken = set()
    n = 0
    for (x, y, z) in floor_cells(p, headroom=2, y0=y0, y1=y1):
        key = (x // 4, y // 4, z // 4)
        if key in taken or rng.random() > density:
            continue
        wall = None
        for face, (dx, dz) in sorted(STEP.items()):
            if is_solid(p, x + dx, y, z + dz):
                wall = face
                break
        if wall is None:
            continue
        kind = catalogue[rng.randrange(len(catalogue))]
        ok = False
        if kind == 'bench':
            ok = place(p, x, y, z, stair(kit.stairs, OPPOSITE[wall]))
        elif kind == 'table':
            if place(p, x, y, z, _b(kit.fence, north=False, south=False, east=False,
                                    west=False, waterlogged=False)):
                place(p, x, y + 1, z, slab(kit.slab, 'bottom'))
                ok = True
        elif kind == 'pot':
            ok = place(p, x, y, z, _b('minecraft:decorated_pot', facing=OPPOSITE[wall],
                                      cracked=True, waterlogged=False))
        elif kind == 'cauldron':
            ok = place(p, x, y, z, ('minecraft:cauldron', None))
        elif kind == 'shelf':
            ok = place(p, x, y, z, ('minecraft:bookshelf', None))
        elif kind == 'lectern':
            ok = place(p, x, y, z, _b('minecraft:lectern', facing=OPPOSITE[wall],
                                      has_book=False, powered=False))
        elif kind == 'crate':
            block = kit.plank or kit.timber
            ok = bool(block) and place(p, x, y, z, (block, None))
        if ok:
            taken.add(key)
            n += 1
    return n


def litter(p, seed, kit, density=0.05, y0=None, y1=None):
    """Loose material on the floor: broken paving, swept rubble, whatever the palette drops.

    Small, cheap and the difference between a swept museum and a building nobody has been
    into for three hundred years. Half of it is the palette's own slab rather than a boulder,
    because most of what is loose on a floor is the floor.
    """
    pool = list(kit.litter) + list(kit.rubble)
    if not pool:
        return 0
    rng = random.Random(seed ^ 0x117E)
    n = 0
    for (x, y, z) in floor_cells(p, headroom=2, y0=y0, y1=y1):
        if rng.random() > density:
            continue
        block = (slab(kit.slab, 'bottom') if (kit.slab and rng.random() < 0.5)
                 else (pool[rng.randrange(len(pool))], None))
        if place(p, x, y, z, block):
            n += 1
    return n


# --------------------------------------------------------------------------- layer 4
#   causal decay -- everything below runs AFTER the decay pass


def debris(p, seed, kit, ground, collapse=None, rate=0.12, reach=3, heap=3,
           on_solid=False):
    """What fell, at the foot of what it fell from, drifting the way the building went.

    The decay pass deletes blocks and never asks where the mass went, so a collapsed keep
    stands in a clean field with its own walls missing. This walks the broken wall tops that
    decay left and drops the mass at the base of the wall, offset in the collapse direction.
    It is the same argument the directional collapse gradient already makes, run forward one
    step: if the east side failed, the east side is where the stone is.

    **It drops heaps, not grains.** The first run of this pass placed one fragment per
    broken top at a 0.45 rate and carpeted every hall floor evenly -- which is exactly the
    mistake `Noise3` exists to prevent one level up: damage is contiguous, and an even
    scatter reads as texture rather than as a building that fell over. A tenth of the tops
    now drop a small pile each, so the same mass arrives as something a player walks around
    instead of through.
    """
    rng = random.Random(seed ^ 0xDEB21)
    pool = list(kit.rubble)
    if kit.slab:
        pool.append('slab')
    if kit.stairs:
        pool.append('stairs')
    dirvec = STEP.get(collapse) if collapse else None

    def fragment():
        pick = pool[rng.randrange(len(pool))]
        if pick == 'slab':
            return slab(kit.slab, 'bottom')
        if pick == 'stairs':
            return stair(kit.stairs, sorted(STEP)[rng.randrange(4)])
        return (pick, None)

    def drop(tx, tz):
        """Land one fragment on the first thing at (tx, tz) that can hold it.

        `on_solid` is the stricter rule the assembled hub needs. Out in the world a fragment
        resting on a cell the template does not own is resting on terrain, which is why the
        default accepts it -- but the hub's court pieces are placed at a datum
        `assemble.mcfunction` fixes, so "below" is decidable there and `check_spawn_hub.py`
        S12 decides it. Under that rule, unowned is nothing.
        """
        if not inside(p, tx, ground, tz):
            return 0
        for ty in range(ground + 1, max(-1, ground - 4), -1):
            if not free(p, tx, ty, tz):
                continue
            below_solid = is_solid(p, tx, ty - 1, tz)
            below_world = (not on_solid) and (ty - 1 < 0 or unowned(p, tx, ty - 1, tz))
            if not (below_solid or below_world):
                continue
            return 1 if place(p, tx, ty, tz, fragment()) else 0
        return 0

    n = 0
    for (x, y, z) in exposed_tops(p, y0=ground + 3):
        if rng.random() > rate:
            continue
        if dirvec:
            ox = dirvec[0] * rng.randint(1, reach)
            oz = dirvec[1] * rng.randint(1, reach)
        else:
            ox, oz = rng.randint(-reach, reach), rng.randint(-reach, reach)
        tx, tz = x + ox, z + oz
        n += drop(tx, tz)
        # The rest of the pile, tapering outward from where the first block landed.
        chance = 0.7
        for _ in range(max(0, heap - 1)):
            if rng.random() > chance:
                break
            dx, dz = rng.randint(-1, 1), rng.randint(-1, 1)
            n += drop(tx + dx, tz + dz)
            chance *= 0.65
    return n


def ingress(p, seed, kit, ground, mode='moss', rate=0.22, roots=0.12, hang='roots',
            roofed_ok=False, into_world=False):
    """Water, root and weather damage arriving through the hole the roof used to fill.

    `mode` picks the agent: `moss` for anywhere it rains, `damp` for the fens and lakes,
    `ash` for what burned, `dust` for the dry and the buried, `none` to skip. The ceiling
    test is what makes it causal -- a floor with a roof over it stays clean, and a floor open
    to the sky does not. Underground the test inverts, because down there everything is
    roofed and the water arrives through the rock regardless: pass `roofed_ok=True` and
    `hang='drip'`, and the seep becomes groundwater rather than weather.
    """
    if mode == 'none':
        return 0
    rng = random.Random(seed ^ 0x1465E55)
    surface = {
        'moss': [MOSS_CARPET, MOSS_CARPET, 'minecraft:moss_block'],
        'damp': [MOSS_CARPET, 'minecraft:mud', 'minecraft:gravel'],
        'ash': ['minecraft:gravel', 'minecraft:basalt', 'minecraft:blackstone'],
        'dust': ['minecraft:gravel', 'minecraft:coarse_dirt', 'minecraft:sand'],
    }.get(mode, [MOSS_CARPET])
    n = 0
    for (x, y, z) in floor_cells(p, headroom=2, y0=ground):
        if not roofed_ok:
            # Open to the sky? Scan up for anything solid; a cell under a surviving roof is
            # skipped, which is what makes the pattern read as water finding the gap.
            roofed = False
            for cy in range(y + 1, p.size[1]):
                if is_solid(p, x, cy, z):
                    roofed = True
                    break
            if roofed:
                continue
        if rng.random() > rate:
            continue
        if place(p, x, y, z, (surface[rng.randrange(len(surface))], None)):
            n += 1
    if roots > 0 and hang != 'none':
        for (x, y, z), (idx, be) in sorted(p.blocks.items()):
            if be is not None or p.palette[idx]['Name'] in NON_SOLID:
                continue
            # The cell a root hangs into is normally carved interior air. `into_world`
            # relaxes that to any free cell, which is what a floating island needs: the space
            # under its underside is untouched world, and a fringe of roots trailing into it
            # is the whole reason the thing reads as afloat rather than as a plate.
            below_open = (free if into_world else is_air)(p, x, y - 1, z)
            if y <= ground or not inside(p, x, y - 1, z) or not below_open:
                continue
            if rng.random() > roots:
                continue
            if hang == 'drip':
                # A stalactite: one tip, or a frustum with a tip under it where there is
                # room. Those two lengths are the only ones whose `thickness` values are
                # unambiguous, and a wrong value here degrades silently to the default.
                long = (free if into_world else is_air)(p, x, y - 2, z) and rng.random() < 0.45
                if long:
                    if place(p, x, y - 1, z, _b('minecraft:pointed_dripstone',
                                                vertical_direction='down',
                                                thickness='frustum', waterlogged=False)):
                        n += 1
                        if place(p, x, y - 2, z, _b('minecraft:pointed_dripstone',
                                                    vertical_direction='down',
                                                    thickness='tip', waterlogged=False)):
                            n += 1
                elif place(p, x, y - 1, z, _b('minecraft:pointed_dripstone',
                                              vertical_direction='down',
                                              thickness='tip', waterlogged=False)):
                    n += 1
            elif place(p, x, y - 1, z, _b(HANGING_ROOTS, waterlogged=False)):
                n += 1
    return n


def wear(p, seed, kit, ground, rate=0.18):
    """Erode the exposed top course: a full block becomes a slab, an edge becomes a step.

    Cheap, and it is what stops every surviving wall ending in a ruler-straight line at the
    height the builder chose. Only exposed tops above the ground plane are eligible, and only
    blocks the palette owns -- a chest lid or a crystal node is not weather damage.
    """
    if not kit.slab:
        return 0
    rng = random.Random(seed ^ 0x3403E)
    ours = masonry(kit)
    n = 0
    for (x, y, z) in exposed_tops(p, y0=ground + 1):
        if rng.random() > rate:
            continue
        if name_at(p, x, y, z) not in ours:
            continue
        if has_be(p, x, y, z) or forbidden(p, x, y, z):
            continue
        p.set(x, y, z, slab(kit.slab, 'bottom'))
        n += 1
    return n


def cobwebs(p, seed, rate=0.05, y0=None):
    """Webs in the corners of enclosed air, which is where they actually are."""
    rng = random.Random(seed ^ 0x3B0)
    n = 0
    for (x, y, z), (idx, be) in sorted(p.blocks.items()):
        if be is not None or p.palette[idx]['Name'] not in AIR_NAMES:
            continue
        if y0 is not None and y < y0:
            continue
        walls = sum(1 for dx, dy, dz in FACES6 if is_solid(p, x + dx, y + dy, z + dz))
        if walls < 3 or rng.random() > rate:
            continue
        if place(p, x, y, z, (COBWEB, None)):
            n += 1
    return n


# --------------------------------------------------------------------------- the two calls


def dress(p, seed, kit, *, ground, cornice=(), trim_rate=0.85, corbel=0.0, opening=0.0,
          conduit=0.0, sockets=0, sconce=0.0, sconce_spacing=5, soul_light=False,
          bracket_light=True, furniture=0.0, furniture_allow=None,
          interior_y=None):
    """Everything the building HAD, applied before the decay pass takes it apart.

    Returns a dict of counts, which every generator prints and `check_structure_detail.py`
    reads back off the shipped NBT.

    NO CONTENT-BLIND LAYER RUNS FROM HERE. Field review 2026-09-09: the five layers below
    derive their CANDIDATES from geometry, which is the property that lets one `sconces()`
    call work on a keep, a mine drift and a pixie cottage. `furnish()` inherited that and
    also made its VOCABULARY universal, and 16 of the 18 call sites left `allow` unset, so
    every structure drew from the same list. The shipped result was 1,622 blocks across 48
    of 105 templates -- 309 lecterns, 496 bookshelves, 333 cauldrons and 432 decorated pots,
    including 147 lecterns through the tombs and a fault working carrying 157 of them.

    Geometry may choose WHERE. It may not choose WHAT. `furniture` therefore requires an
    explicit `furniture_allow`, so a caller that has not decided what belongs in this
    particular building cannot get furniture by default. `floor_litter` is gone entirely:
    it scattered one loose block per floor cell at a flat rate, which is the mistake
    `debris()`'s own docstring records being fixed one level up -- an even scatter reads as
    texture, not as a building that fell over.
    """
    if furniture and furniture_allow is None:
        raise ValueError(
            'furniture requires an explicit furniture_allow: name what belongs in this '
            'structure. A quarry does not have a lectern.')
    y0, y1 = interior_y if interior_y else (None, None)
    out = {}
    if cornice:
        out['trim'] = exterior_trim(p, seed, kit, cornice, rate=trim_rate)
    if corbel:
        out['corbels'] = corbels(p, seed, kit, rate=corbel, y0=ground)
    if opening:
        out['openings'] = openings(p, seed, kit, rate=opening)
    if conduit:
        out['conduits'] = conduits(p, seed, kit, rate=conduit, y0=y0, y1=y1)
    if sockets:
        out['sockets'] = crystal_sockets(p, seed, kit, count=sockets, y0=ground)
    if sconce:
        out['sconces'] = sconces(p, seed, kit, spacing=sconce_spacing, rate=sconce,
                                 y0=y0, y1=y1, soul=soul_light, bracket=bracket_light)
    if furniture:
        out['furniture'] = furnish(p, seed, kit, density=furniture, y0=y0, y1=y1,
                                   allow=furniture_allow)
    return out


def aftermath(p, seed, kit, *, ground, collapse=None, rubble=0.0, reach=3, heap=3,
              rubble_on_solid=False, weathering=0.0, seep='none', seep_rate=0.22, roots=0.12,
              hang='roots', roofed_ok=False, into_world=False, webs=0.0):
    """Everything the collapse DID, applied after the decay pass has decided what fell."""
    out = {}
    if rubble:
        out['debris'] = debris(p, seed, kit, ground, collapse=collapse, rate=rubble,
                               reach=reach, heap=heap, on_solid=rubble_on_solid)
    if weathering:
        out['wear'] = wear(p, seed, kit, ground, rate=weathering)
    if seep != 'none':
        out['ingress'] = ingress(p, seed, kit, ground, mode=seep, rate=seep_rate,
                                 roots=roots, hang=hang, roofed_ok=roofed_ok,
                                 into_world=into_world)
    if webs:
        out['webs'] = cobwebs(p, seed, rate=webs, y0=ground)
    return out


# --------------------------------------------------------------------------- measurement

DETAIL_SUFFIX = ('_stairs', '_slab', '_wall', '_fence', '_fence_gate', '_trapdoor', '_door',
                 '_pane', '_carpet', '_banner', '_button', '_pressure_plate', '_sign',
                 '_candle', '_bars', '_pot', '_head', '_skull', '_rod', '_torch',
                 '_lantern', '_chain', '_bed', '_cluster', '_roots')

DETAIL_EXACT = frozenset({
    'minecraft:lantern', 'minecraft:soul_lantern', 'minecraft:chain', 'minecraft:iron_bars',
    'minecraft:torch', 'minecraft:soul_torch', 'minecraft:cobweb', 'minecraft:vine',
    'minecraft:ladder', 'minecraft:scaffolding', 'minecraft:flower_pot', 'minecraft:lectern',
    'minecraft:barrel', 'minecraft:chest', 'minecraft:cauldron', 'minecraft:composter',
    'minecraft:bell', 'minecraft:campfire', 'minecraft:soul_campfire', 'minecraft:end_rod',
    'minecraft:decorated_pot', 'minecraft:brewing_stand', 'minecraft:grindstone',
    'minecraft:smithing_table', 'minecraft:loom', 'minecraft:cartography_table',
    'minecraft:fletching_table', 'minecraft:bookshelf', 'minecraft:chiseled_bookshelf',
    'minecraft:moss_carpet', 'minecraft:hanging_roots', 'minecraft:rail',
    'minecraft:pointed_dripstone', 'minecraft:amethyst_cluster',
})


# The plant class, and it is not a rounding error in this pack. Alfheim's decorative
# vocabulary IS botanical -- a tended crop row, a sapling by the path and two flowers at a
# doorstep are the human-scale residue layer in vegetable form, and the first version of this
# metric scored a pixie kitchen garden at exactly zero because none of it was made of stone.
# Counting them is a correction to the measurement, not a relaxation of the bar: every entry
# here is small-scale articulation and none of it is bulk mass.
PLANT_SUFFIX = ('_sapling', '_mushroom', '_flower', '_bush', '_fern', '_tulip', '_orchid',
                '_daisy', '_lily', '_sprouts', '_stem', '_petals', '_seagrass')
PLANT_EXACT = frozenset({
    'minecraft:wheat', 'minecraft:carrots', 'minecraft:potatoes', 'minecraft:beetroots',
    'minecraft:cocoa', 'minecraft:sugar_cane', 'minecraft:bamboo', 'minecraft:cake',
    'minecraft:dandelion', 'minecraft:poppy', 'minecraft:allium', 'minecraft:azure_bluet',
    'minecraft:cornflower', 'minecraft:torchflower', 'minecraft:sunflower',
    'minecraft:lilac', 'minecraft:peony', 'minecraft:short_grass', 'minecraft:grass',
    'minecraft:tall_grass', 'minecraft:vine', 'minecraft:glow_lichen',
    'minecraft:melon', 'minecraft:pumpkin', 'minecraft:carved_pumpkin',
})


def is_detail(name):
    """Is this block small-scale articulation rather than bulk mass?

    Suffix matching keeps it agnostic about which mod owns the family, which matters in a
    pack where the masonry is Feywild's, the timber is Botania's and half the flowers are
    ours.
    """
    if name in DETAIL_EXACT or name in PLANT_EXACT:
        return True
    if name.startswith('minecraft:potted_'):
        return True
    return name.endswith(DETAIL_SUFFIX) or name.endswith(PLANT_SUFFIX)


def census(p):
    """The numbers a generator prints and a checker asserts, read off a live Piece."""
    solid = detail = 0
    names = set()
    for (idx, be) in p.blocks.values():
        name = p.palette[idx]['Name']
        if name in AIR_NAMES:
            continue
        solid += 1
        names.add(name)
        if is_detail(name):
            detail += 1
    return {'solid': solid, 'detail': detail, 'names': len(names),
            'share': (detail / solid) if solid else 0.0}
