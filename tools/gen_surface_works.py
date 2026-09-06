"""Generate Alfheim's surface structures: thirty-two of them, ten archetypes, sixteen biomes.

Design record: alfheim_reclaimed_design/THE_SURFACE.md.
Source of truth: tools/surface_works_manifest.json.
Checker: tools/check_surface_works.py. Quests: tools/gen_cartographer.py.

Everything is written from numbers rather than placed by hand, for the reason SPAWN_HUB.md §1
gives: the user's own observation that "automated structure generation typically needs multiple
passes of detailed improvement". A parametric build makes pass 2 an edit to a constant. Thirty-two
hand-placed buildings would make pass 2 a rebuild.

Emitted per structure:

    kubejs/data/alfheim/structures/surface/<id>.nbt
    kubejs/data/alfheim/worldgen/template_pool/surface/<id>.json
    kubejs/data/alfheim/worldgen/structure/<id>.json
    kubejs/data/alfheim/worldgen/structure_set/<id>.json
    kubejs/data/alfheim/tags/worldgen/biome/has_<id>.json

and per archetype:

    kubejs/data/alfheim/tags/worldgen/structure/<archetype>.json      <- the map's destination
    kubejs/data/alfheim/loot_tables/explorer_maps/<archetype>.json    <- the map itself

plus three shared chest tables under loot_tables/chests/.

THREE THINGS THAT ARE EASY TO GET WRONG, ALL PAID FOR ALREADY
-------------------------------------------------------------
1.  **A crater is a hole, and templates place blocks.** A position set to `minecraft:air` IS
    placed and overwrites terrain; a position never set is absent from the template and leaves
    terrain alone. That asymmetry is the whole mechanism behind the crater and the quarry.
    `structure_void` is a third case that behaves like "never set", so there is no reason to
    write one.

2.  **`start_height` is how a piece gets buried.** JigsawPlacement adds the heightmap value to
    the start position, so a piece whose bowl floor is 22 blocks below its own surface plane
    declares `start_height: {absolute: -22}`. Each archetype's `ground` in the manifest is that
    number.

3.  **Every structure_set needs its own salt.** Two `random_spread` sets sharing spacing and
    salt do not become neighbours -- they pick the SAME chunk in every cell and generate on top
    of each other. Salts here are derived from SHA-1 of the id, so they are unique by
    construction and stable across regeneration.

    python tools/gen_surface_works.py
    python tools/gen_surface_works.py --dry-run
    python tools/gen_surface_works.py --only ashwatch_keep
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from structure_nbt import ADAPTATION_MARGIN, MAX_AXIS, Piece  # noqa: E402

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', NS)
STRUCT_DIR = os.path.join(DATA, 'structures', 'surface')
MANIFEST = os.path.join('tools', 'surface_works_manifest.json')
BLOOMS = os.path.join('tools', 'blooms_manifest.json')

# --------------------------------------------------------------------------- block helpers

AIR = ('minecraft:air', None)
WATER = ('minecraft:water', {'level': '0'})
LAVA = ('minecraft:lava', {'level': '0'})
COBWEB = ('minecraft:cobweb', None)

# Blocks a wall, fence or pane must NOT treat as something to connect to, and that the decay
# pass may leave floating without it looking wrong.
NON_SOLID = {
    'minecraft:air', 'minecraft:cave_air', 'minecraft:water', 'minecraft:lava',
    'minecraft:torch', 'minecraft:lantern', 'minecraft:soul_lantern', 'minecraft:vine',
    'minecraft:cobweb', 'minecraft:rail', 'minecraft:ladder', 'minecraft:chain',
    'minecraft:moss_carpet', 'minecraft:scaffolding', 'minecraft:flower_pot',
    'minecraft:pointed_dripstone', 'minecraft:lightning_rod', 'minecraft:campfire',
    'minecraft:soul_campfire', 'minecraft:cauldron',
}


def B(name, **props):
    """A block state. Booleans are lowered to Minecraft's 'true'/'false' strings.

    Unknown properties are safe: NbtUtils.readBlockState looks each one up in the block's
    StateDefinition and silently ignores what it does not find. An unknown BLOCK, by contrast,
    becomes air -- which is why every id in the manifest is checked against the registry dump.
    """
    if not props:
        return (name, None)
    out = {}
    for k, v in props.items():
        out[k] = ('true' if v else 'false') if isinstance(v, bool) else str(v)
    return (name, out)


def stair(name, facing, half='bottom', shape='straight'):
    return B(name, facing=facing, half=half, shape=shape, waterlogged=False)


def slab(name, kind='bottom'):
    return B(name, type=kind, waterlogged=False)


def pillar(name, ax='y'):
    return B(name, axis=ax)


def vine(face):
    """A vine clinging to the block on the given side of its own position.

    Every face defaults to false, and a vine with no face set is a floating quad that drops on
    the first block update. Same helper, same reason, as gen_spawn_hub.py.
    """
    props = {d: 'false' for d in ('north', 'south', 'east', 'west', 'up')}
    props[face] = 'true'
    return ('minecraft:vine', props)


def chest(facing, table):
    return (B('minecraft:chest', facing=facing, type='single', waterlogged=False),
            {'id': 'minecraft:chest', 'LootTable': f'{NS}:chests/{table}'})


def barrel(facing, table):
    return (B('minecraft:barrel', facing=facing, open=False),
            {'id': 'minecraft:barrel', 'LootTable': f'{NS}:chests/{table}'})


OPPOSITE = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
STEP = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}

# --------------------------------------------------------------------------- coherent noise


class Noise3:
    """Value noise on a lattice, smoothstep-interpolated.

    Per-block `rng.random() < p` decay produces static -- a wall eaten evenly all over, which
    reads as texture rather than as damage. Damage is CONTIGUOUS: a section falls, not every
    third block. This gives blobs at the scale of `cell`, which is what makes a ruin look like
    a ruin.
    """

    def __init__(self, seed, cell=6.0):
        self.seed = seed & 0xFFFFFFFF
        self.cell = float(cell)

    def _lattice(self, i, j, k):
        h = (i * 0x9E3779B1) ^ (j * 0x85EBCA77) ^ (k * 0xC2B2AE3D) ^ self.seed
        h &= 0xFFFFFFFF
        h ^= h >> 15
        h = (h * 0x2545F491) & 0xFFFFFFFF
        h ^= h >> 13
        return (h & 0xFFFFFF) / float(0xFFFFFF)

    def __call__(self, x, y, z):
        fx, fy, fz = x / self.cell, y / self.cell, z / self.cell
        i, j, k = math.floor(fx), math.floor(fy), math.floor(fz)
        tx, ty, tz = fx - i, fy - j, fz - k
        sx = tx * tx * (3 - 2 * tx)
        sy = ty * ty * (3 - 2 * ty)
        sz = tz * tz * (3 - 2 * tz)
        c = self._lattice
        v00 = c(i, j, k) + (c(i + 1, j, k) - c(i, j, k)) * sx
        v10 = c(i, j + 1, k) + (c(i + 1, j + 1, k) - c(i, j + 1, k)) * sx
        v01 = c(i, j, k + 1) + (c(i + 1, j, k + 1) - c(i, j, k + 1)) * sx
        v11 = c(i, j + 1, k + 1) + (c(i + 1, j + 1, k + 1) - c(i, j + 1, k + 1)) * sx
        v0 = v00 + (v10 - v00) * sy
        v1 = v01 + (v11 - v01) * sy
        return v0 + (v1 - v0) * sz


# --------------------------------------------------------------------------- geometry


def box(p, x0, y0, z0, x1, y1, z1, block, be=None):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                p.set(x, y, z, block, be)


def shell(p, x0, y0, z0, x1, y1, z1, block):
    """The four vertical faces of a box. No floor, no ceiling."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            p.set(x, y, z0, block)
            p.set(x, y, z1, block)
    for z in range(z0 + 1, z1):
        for y in range(y0, y1 + 1):
            p.set(x0, y, z, block)
            p.set(x1, y, z, block)


def disc(p, cx, cz, y, r, block, r_inner=0.0):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if r_inner - 0.5 <= d <= r + 0.5 if r_inner else d <= r + 0.5:
                p.set(x, y, z, block)


def ring(p, cx, cz, y, r, block, width=1.0):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if r - width + 0.5 <= d <= r + 0.5:
                p.set(x, y, z, block)


def cylinder(p, cx, cz, y0, y1, r, block, hollow=True):
    for y in range(y0, y1 + 1):
        if hollow:
            ring(p, cx, cz, y, r, block)
        else:
            disc(p, cx, cz, y, r, block)


def crenellate(p, positions, y, block, gap=2):
    """Merlons: every other position along a wall top."""
    for i, (x, z) in enumerate(positions):
        if i % gap == 0:
            p.set(x, y, z, block)


def perimeter(x0, z0, x1, z1):
    """The positions of a rectangle's edge, walked clockwise from the north-west corner."""
    out = []
    for x in range(x0, x1 + 1):
        out.append((x, z0))
    for z in range(z0 + 1, z1 + 1):
        out.append((x1, z))
    for x in range(x1 - 1, x0 - 1, -1):
        out.append((x, z1))
    for z in range(z1 - 1, z0, -1):
        out.append((x0, z))
    return out


# --------------------------------------------------------------------------- passes


def name_at(p, x, y, z):
    e = p.blocks.get((x, y, z))
    return None if e is None else p.palette[e[0]]['Name']


def is_solid(p, x, y, z):
    n = name_at(p, x, y, z)
    return n is not None and n not in NON_SOLID


def decay(p, seed, ruin, y0, y1, collapse='none', keep=()):
    """Take the structure apart. Higher is likelier to be gone; one side may be likelier still.

    `keep` is a set of positions the pass may not touch -- foundations, and anything whose
    removal would make the piece unreadable rather than ruined.
    """
    if ruin <= 0.0:
        return
    n = Noise3(seed, cell=5.0)
    span = max(1, y1 - y0)
    cx = p.size[0] / 2.0
    cz = p.size[2] / 2.0
    dirvec = STEP.get(collapse)
    doomed = []
    for (x, y, z), _ in p.blocks.items():
        if y < y0 or y > y1 or (x, y, z) in keep:
            continue
        h = (y - y0) / span
        threshold = ruin * (0.30 + 0.85 * h)
        if dirvec:
            # A collapse has a direction. Blocks on the failing side go first, and the
            # gradient is what makes it read as a collapse rather than as erosion.
            reach = ((x - cx) * dirvec[0] + (z - cz) * dirvec[1]) / max(cx, cz)
            threshold *= 0.55 + 0.9 * max(0.0, reach)
        if n(x, y, z) < threshold:
            doomed.append((x, y, z))
    for pos in doomed:
        del p.blocks[pos]


def weather(p, seed, pal, chance=0.5):
    """Swap dressed stone for its cracked and mossy forms, in patches rather than at random."""
    brick = pal['brick']
    cracked, mossy = pal['brick_cracked'], pal['brick_mossy']
    n = Noise3(seed ^ 0x5A5A5A, cell=4.0)
    for (x, y, z), (idx, be) in list(p.blocks.items()):
        if be is not None or p.palette[idx]['Name'] != brick:
            continue
        v = n(x, y, z)
        if v < chance * 0.45:
            p.set(x, y, z, (cracked, None))
        elif v < chance * 0.75:
            p.set(x, y, z, (mossy, None))


def scatter_rubble(p, seed, pal, y, positions, density=0.35):
    rng = random.Random(seed ^ 0x1234)
    for (x, z) in positions:
        if rng.random() < density:
            p.set(x, y, z, (rng.choice(pal['rubble']), None))


def drape(p, seed, pal, chance=0.18, webs=0.0):
    """Vines on the outside of standing walls, and cobwebs in enclosed air."""
    rng = random.Random(seed ^ 0xBEEF)
    sx, sy, sz = p.size
    additions = {}
    for (x, y, z), _ in list(p.blocks.items()):
        if not is_solid(p, x, y, z):
            continue
        for face, (dx, dz) in STEP.items():
            nx, nz = x + dx, z + dz
            if not (0 <= nx < sx and 0 <= nz < sz):
                continue
            if name_at(p, nx, y, nz) is not None:
                continue
            if rng.random() < chance:
                additions[(nx, y, nz)] = vine(OPPOSITE[face])
        if webs > 0 and rng.random() < webs * 0.25:
            if 0 <= y + 1 < sy and name_at(p, x, y + 1, z) is None:
                additions[(x, y + 1, z)] = COBWEB
    for pos, blk in additions.items():
        if name_at(p, *pos) is None:
            p.set(pos[0], pos[1], pos[2], blk)


def connect(p):
    """Resolve wall / fence / pane connection states from what is actually next to them.

    Structure placement does not run neighbour updates through the interior of a piece, so a
    parapet built without this is a row of unconnected posts. Vanilla's own rule for a wall's
    `up` is reproduced: a post is drawn unless the wall has exactly two opposite connections
    and nothing sitting on it.
    """
    for (x, y, z), (idx, be) in list(p.blocks.items()):
        name = p.palette[idx]['Name']
        if name.endswith('_wall'):
            kind = 'wall'
        elif name.endswith('_fence') or name.endswith('_fence_gate'):
            kind = 'fence'
        elif name == 'minecraft:iron_bars' or name.endswith('_pane'):
            kind = 'pane'
        else:
            continue
        if kind == 'fence' and name.endswith('_fence_gate'):
            continue
        sides = {}
        for face, (dx, dz) in STEP.items():
            nx, nz = x + dx, z + dz
            nn = name_at(p, nx, y, nz)
            same = nn is not None and (
                nn.endswith('_wall') if kind == 'wall' else
                nn.endswith('_fence') if kind == 'fence' else
                (nn == 'minecraft:iron_bars' or nn.endswith('_pane')))
            sides[face] = bool(same or is_solid(p, nx, y, nz))
        above_solid = is_solid(p, x, y + 1, z)
        if kind == 'wall':
            props = {f: ('tall' if (sides[f] and above_solid) else 'low' if sides[f] else 'none')
                     for f in STEP}
            straight = ((sides['north'] and sides['south'] and
                         not sides['east'] and not sides['west']) or
                        (sides['east'] and sides['west'] and
                         not sides['north'] and not sides['south']))
            props['up'] = 'false' if (straight and not above_solid) else 'true'
        else:
            props = {f: ('true' if sides[f] else 'false') for f in STEP}
        props['waterlogged'] = 'false'
        p.blocks[(x, y, z)] = (p._state(name, props), be)


# --------------------------------------------------------------------------- the archetypes
#
# Every builder takes (pal, shape, ground, size, seed) and returns a Piece. `ground` is the
# internal y that will coincide with the terrain surface; everything below it is buried and
# everything above it stands up.


def build_castle(pal, s, ground, size, seed):
    p = Piece(*size)
    rng = random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx // 2, sz // 2
    half = s['wall'] // 2
    x0, x1 = cx - half, cx + half
    z0, z1 = cz - half, cz + half
    wall_h = ground + 8
    brick, stone = (pal['brick'], None), (pal['stone'], None)
    floor = (pal['floor'], None)

    # Foundation course at the surface plane, so the wall never stands on air where the
    # ground falls away. beard_thin fills under it; this gives beard_thin something to fill to.
    for (x, z) in perimeter(x0 - 1, z0 - 1, x1 + 1, z1 + 1):
        p.set(x, ground - 1, z, stone)

    # --- curtain wall, two thick, with a walkway and merlons
    edge = perimeter(x0, z0, x1, z1)
    inner = perimeter(x0 + 1, z0 + 1, x1 - 1, z1 - 1)
    for (x, z) in edge:
        box(p, x, ground - 1, z, x, wall_h - 1, z, brick)
    for (x, z) in inner:
        box(p, x, ground - 1, z, x, wall_h - 2, z, brick)
        p.set(x, wall_h - 1, z, floor)                       # the walkway
    crenellate(p, edge, wall_h, (pal['brick'], None))

    # --- corner towers. Three towers means one corner simply fell, and that is more
    # interesting than four short ones.
    corners = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    rng.shuffle(corners)
    for (tx, tz) in corners[:s['towers']]:
        r = 3.5
        ox = tx + (2 if tx == x0 else -2)
        oz = tz + (2 if tz == z0 else -2)
        cylinder(p, ox, oz, ground - 1, ground + s['tower_h'], r, brick)
        disc(p, ox, oz, ground + s['tower_h'], r - 1, floor)
        for y in range(ground + 3, ground + s['tower_h'] - 1, 4):        # arrow slits
            p.set(int(ox + r), y, int(oz), AIR)
            p.set(int(ox - r), y, int(oz), AIR)
        merlons = []
        for a in range(0, 360, 30):
            merlons.append((int(round(ox + r * math.cos(math.radians(a)))),
                            int(round(oz + r * math.sin(math.radians(a))))))
        crenellate(p, merlons, ground + s['tower_h'] + 1, (pal['brick'], None), gap=2)
        # hollow it out and give it a floor to stand on
        cylinder(p, ox, oz, ground, ground + s['tower_h'] - 1, r - 1, AIR, hollow=False)
        disc(p, ox, oz, ground - 1, r - 1, floor)

    # --- gatehouse
    gx, gz = STEP[s['gate']]
    mx = cx + gx * half
    mz = cz + gz * half
    for w in range(-4, 5):
        ax, az = (mx + (w if gx == 0 else 0)), (mz + (w if gz == 0 else 0))
        box(p, ax, ground - 1, az, ax, wall_h + 3, az, brick)
    # the arch: three wide, four tall, cut through both wall courses
    # The passage: three wide across the wall, four tall, cut through both wall courses and
    # one block either side of them so the arch is a tunnel rather than a slot.
    for w in (-1, 0, 1):
        for y in range(ground, ground + 4):
            for depth in (-2, -1, 0, 1, 2):
                ax = mx + (w if gx == 0 else depth)
                az = mz + (w if gz == 0 else depth)
                p.set(ax, y, az, AIR)
    for w in (-2, 2):
        ax = mx + (w if gx == 0 else 0)
        az = mz + (w if gz == 0 else 0)
        p.set(ax, ground + 4, az, stair(pal['stairs'], s['gate'], half='top'))

    # --- courtyard paving, patchy on purpose
    n = Noise3(seed ^ 0x77, cell=5.0)
    for x in range(x0 + 2, x1 - 1):
        for z in range(z0 + 2, z1 - 1):
            if n(x, ground, z) > 0.38:
                p.set(x, ground - 1, z, floor)

    # --- the keep
    kw, kd, kh = s['keep_w'], s['keep_d'], s['keep_h']
    kx0, kz0 = cx - kw // 2, cz - kd // 2
    kx1, kz1 = kx0 + kw - 1, kz0 + kd - 1
    box(p, kx0, ground - 1, kz0, kx1, ground - 1, kz1, floor)
    shell(p, kx0, ground, kz0, kx1, ground + kh, kz1, brick)
    box(p, kx0 + 1, ground, kz0 + 1, kx1 - 1, ground + kh, kz1 - 1, AIR)
    for corner in ((kx0, kz0), (kx1, kz0), (kx0, kz1), (kx1, kz1)):
        box(p, corner[0], ground, corner[1], corner[0], ground + kh + 1,
            corner[1], pillar(pal['pillar']))
    # floors every five, each with a stair well cut through it
    level = ground + 5
    while level < ground + kh:
        box(p, kx0 + 1, level, kz0 + 1, kx1 - 1, level, kz1 - 1, (pal['plank'], None))
        box(p, kx0 + 1, level, kz0 + 1, kx0 + 3, level, kz0 + 3, AIR)
        for i in range(4):
            p.set(kx0 + 1 + i, level - 1 - i, kz0 + 1, stair(pal['stairs'], 'east'))
        level += 5
    # door, on the courtyard side of the gate
    dx, dz = kx0 + kw // 2, kz1
    box(p, dx - 1, ground, dz, dx + 1, ground + 2, dz, AIR)
    # windows
    for y in (ground + 3, ground + 8, ground + 13):
        if y >= ground + kh:
            break
        for x in range(kx0 + 2, kx1 - 1, 3):
            p.set(x, y, kz0, (pal['glass'], None))
            p.set(x, y, kz1, (pal['glass'], None))
    # roof, gabled along the long axis
    for i in range(min(kw, kd) // 2):
        y = ground + kh + 1 + i
        for x in range(kx0 + i, kx1 - i + 1):
            p.set(x, y, kz0 + i, stair(pal['stairs'], 'south'))
            p.set(x, y, kz1 - i, stair(pal['stairs'], 'north'))
        for z in range(kz0 + i + 1, kz1 - i):
            p.set(kx0 + i, y, z, stair(pal['stairs'], 'east'))
            p.set(kx1 - i, y, z, stair(pal['stairs'], 'west'))

    # --- what is worth taking
    p.set(kx0 + 2, ground, kz1 - 2, *chest('north', 'surface_rare'))
    p.set(kx1 - 2, ground, kz0 + 2, *chest('south', 'surface_uncommon'))
    p.set(x0 + 3, ground, z1 - 3, *barrel('up', 'surface_common'))
    for pos in ((kx0 + 3, ground + 1, kz0 + 3), (kx1 - 3, ground + 1, kz1 - 3)):
        p.set(pos[0], pos[1], pos[2], B(pal['light'], hanging=False, waterlogged=False))

    keep_solid = {(x, ground - 1, z) for x in range(sx) for z in range(sz)}
    decay(p, seed, s['ruin'], ground, sy - 1, s['collapse'], keep=keep_solid)
    weather(p, seed, pal)
    scatter_rubble(p, seed, pal, ground - 1,
                   [(x, z) for x in range(x0 - 3, x1 + 4) for z in range(z0 - 3, z1 + 4)
                    if not (x0 <= x <= x1 and z0 <= z <= z1)], density=0.10)
    drape(p, seed, pal, chance=0.10, webs=s.get('webs', 0.0))
    connect(p)
    return p


def build_quarry(pal, s, ground, size, seed, ores=()):
    p = Piece(*size)
    rng = random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx / 2.0, sz / 2.0
    R, depth, benches = s['radius'], s['depth'], s['benches']
    floor_y = ground - depth
    step_h = max(2, depth // benches)
    step_r = (R - 5.0) / benches

    def radius_at(y):
        """Stepped: the pit widens by one bench every step_h blocks going up."""
        b = min(benches, max(0, (y - floor_y) // step_h))
        return 5.0 + step_r * b

    # --- carve. Air from the floor to the top of the piece, so nothing of the old hill is
    # left hanging over the cut.
    for y in range(floor_y, sy):
        r = radius_at(min(y, ground))
        for x in range(sx):
            for z in range(sz):
                if math.hypot(x - cx, z - cz) <= r:
                    p.set(x, y, z, AIR)

    # --- bench faces and their floors, and the ore the elves were following
    for b in range(benches + 1):
        y = floor_y + b * step_h
        r = 5.0 + step_r * b
        ring(p, cx, cz, y - 1, r, (pal['stone'], None), width=2.5)
        for x in range(sx):
            for z in range(sz):
                d = math.hypot(x - cx, z - cz)
                if r - 2.5 <= d <= r:
                    p.set(x, y - 1, z, (pal['stone'], None))
                    if ores and rng.random() < 0.06:
                        p.set(x, y, z, (rng.choice(ores), None))
    disc(p, cx, cz, floor_y - 1, 6.0, (pal['floor'], None))

    # --- the ramp: a three-wide ledge spiralling up the wall
    turns = benches + 1
    for t in range(int(turns * 360)):
        a = math.radians(t)
        y = floor_y + int(depth * (t / (turns * 360.0)))
        r = radius_at(y) - 1.5
        x = cx + r * math.cos(a)
        z = cz + r * math.sin(a)
        for w in (-1, 0, 1):
            rx = int(round(x + w * math.cos(a + math.pi / 2)))
            rz = int(round(z + w * math.sin(a + math.pi / 2)))
            p.set(rx, y, rz, (pal['stone'], None))
            p.set(rx, y + 1, rz, AIR)
            p.set(rx, y + 2, rz, AIR)

    # --- rails on the pit floor
    if s.get('rails', True):
        for x in range(int(cx - 5), int(cx + 6)):
            p.set(x, floor_y, int(cz), B('minecraft:rail', shape='east_west'))
        p.set(int(cx + 6), floor_y, int(cz), (pal['plank'], None))

    # --- the headframe: the winch tower over the lip
    if s.get('headframe', True):
        hx, hz = int(cx + R - 5), int(cz - 2)
        # Its own footing. Everything within the top bench radius has just been carved to air,
        # and R is 21 in a 48-wide piece, so there is no untouched ground left to stand it on.
        box(p, hx - 1, ground - 1, hz - 1, hx + 4, ground - 1, hz + 4, (pal['stone'], None))
        for leg in ((0, 0), (3, 0), (0, 3), (3, 3)):
            box(p, hx + leg[0], ground, hz + leg[1], hx + leg[0], ground + 9, hz + leg[1],
                pillar(pal['timber']))
        for x in range(hx, hx + 4):
            for z in range(hz, hz + 4):
                p.set(x, ground + 10, z, (pal['plank'], None))
        box(p, hx + 1, ground + 10, hz + 1, hx + 2, ground + 10, hz + 2, AIR)
        for y in range(ground, ground + 10):
            p.set(hx + 1, y, hz + 1, B('minecraft:chain', axis='y'))
        p.set(hx, ground, hz - 1, *chest('north', 'surface_uncommon'))

    # --- spoil heaps on the rim, which is how you spot a quarry from a distance. They sit ON
    # the lip rather than beyond it: R is already 21-22 in a 48-wide piece, so anything thrown
    # further out lands outside the box and is dropped.
    for _ in range(6):
        a = rng.uniform(0, math.tau)
        hx = cx + (R + rng.uniform(0.5, 2.5)) * math.cos(a)
        hz = cz + (R + rng.uniform(0.5, 2.5)) * math.sin(a)
        h = rng.randint(2, 4)
        for y in range(h):
            disc(p, hx, hz, ground + y, (h - y) * 1.3, (rng.choice(pal['rubble']), None))

    # --- water in the bottom, when the pumps stopped
    if s.get('flooded', 0):
        for y in range(floor_y, floor_y + s['flooded']):
            for x in range(sx):
                for z in range(sz):
                    if math.hypot(x - cx, z - cz) <= radius_at(y) - 1:
                        p.set(x, y, z, WATER)

    p.set(int(cx - 4), floor_y, int(cz + 4), *barrel('up', 'surface_common'))
    connect(p)
    return p


def build_crater(pal, s, ground, size, seed):
    p = Piece(*size)
    rng = random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx / 2.0, sz / 2.0
    R, depth = s['radius'], s['depth']
    n = Noise3(seed, cell=7.0)

    def bowl(x, z):
        """Depth below the surface at (x, z): a paraboloid, roughened so the rim is ragged."""
        d = math.hypot(x - cx, z - cz)
        rr = R * (0.86 + 0.28 * n(x * 0.9, 0, z * 0.9))
        if d >= rr:
            return None
        t = d / rr
        return depth * (1.0 - t * t)

    # --- carve, and lay the floor as it goes
    fused = [pal['accent'], 'minecraft:obsidian', 'minecraft:tinted_glass']
    for x in range(sx):
        for z in range(sz):
            b = bowl(x, z)
            if b is None:
                continue
            fy = ground - int(round(b))
            for y in range(fy + 1, sy):
                p.set(x, y, z, AIR)
            if rng.random() < s['glass']:
                p.set(x, fy, z, (rng.choice(fused), None))
            else:
                p.set(x, fy, z, (rng.choice(pal['rubble']), None))
            # shattered strata: two courses of stone under the skin so a dug edge reads right
            p.set(x, fy - 1, z, (pal['stone'], None))
            p.set(x, fy - 2, z, (pal['brick_cracked'], None))

    # --- the rim: what came out of the hole, thrown up around it
    for x in range(sx):
        for z in range(sz):
            d = math.hypot(x - cx, z - cz)
            rr = R * (0.86 + 0.28 * n(x * 0.9, 0, z * 0.9))
            if not (rr <= d <= rr + 4.5):
                continue
            h = int(round(s['rim'] * (1.0 - (d - rr) / 4.5) * (0.6 + 0.8 * n(x, 5, z))))
            for y in range(h):
                p.set(x, ground + y, z, (rng.choice(pal['rubble']), None))

    # --- the thing at the centre
    if s.get('spire'):
        h = max(4, depth - 2)
        for y in range(h):
            r = 2.6 * (1.0 - y / float(h))
            disc(p, cx, cz, ground - depth + y, r, ('minecraft:obsidian', None))
        p.set(int(cx), ground - depth + h, int(cz), (pal['accent'], None))
    if s.get('lava'):
        for y in range(s['lava']):
            for x in range(sx):
                for z in range(sz):
                    b = bowl(x, z)
                    if b is not None and ground - int(round(b)) + y < ground - depth + 3:
                        p.set(x, ground - int(round(b)) + 1 + y, z, LAVA)

    # --- one chest, half buried in the rim, because somebody came back to look
    bx, bz = int(cx + R * 0.75), int(cz - R * 0.35)
    box(p, bx - 1, ground - 1, bz - 1, bx + 1, ground + 1, bz + 1, (pal['brick_cracked'], None))
    box(p, bx, ground, bz, bx, ground + 1, bz, AIR)
    p.set(bx, ground, bz, *chest('east', 'surface_uncommon'))
    connect(p)
    return p


def build_tower(pal, s, ground, size, seed):
    p = Piece(*size)
    sx, sy, sz = size
    cx, cz = sx / 2.0, sz / 2.0
    r = float(s['radius'])
    h = s['height']
    top = ground + h
    brick = (pal['brick'], None)

    if s.get('island'):
        # Out on the rim there is very little ground and none of it is reliable, so the spire
        # brings its own: a flared foot that reads as the island's crown. It grows UPWARD --
        # a piece cannot build below its own y=0, and ground is 1.
        for y in range(4):
            disc(p, cx, cz, ground - 1 + y, r + 4.0 - y * 1.1, (pal['stone'], None))

    cylinder(p, cx, cz, ground - 1, top, r, brick)
    cylinder(p, cx, cz, ground, top - 1, r - 1, AIR, hollow=False)
    disc(p, cx, cz, ground - 1, r - 1, (pal['floor'], None))

    # --- floors first, then the stair, which cuts its own well through them.
    for level in range(ground + 7, top - 3, 7):
        disc(p, cx, cz, level, r - 1, (pal['plank'], None))
        disc(p, cx, cz, level, 1.6, AIR)

    # --- the spiral, and it has to be CLIMBABLE. The first draft stepped a fixed twelfth of a
    # turn per stair, which around a radius-4 ring puts consecutive steps two blocks apart --
    # a decorative helix nobody can walk up. Walk the ring at fine angular resolution instead,
    # keep each distinct integer cell once, and rise exactly one block per cell: adjacent
    # steps, one block of rise, which is the definition of a staircase.
    stair_r = r - 1.2
    seen, cells = set(), []
    for t in range(2048):
        a = math.tau * t / 2048.0
        x = int(round(cx + stair_r * math.cos(a)))
        z = int(round(cz + stair_r * math.sin(a)))
        if (x, z) in seen:
            continue
        seen.add((x, z))
        cells.append((x, z, a))
    for i in range(top - 3 - ground):
        x, z, a = cells[i % len(cells)]
        y = ground + i
        # The tread faces the way you are walking, which is tangential to the ring.
        tx, tz = -math.sin(a), math.cos(a)
        facing = ('east' if tx > abs(tz) else 'west' if -tx > abs(tz)
                  else 'south' if tz > 0 else 'north')
        p.set(x, y, z, stair(pal['stairs'], facing))
        p.set(x, y + 1, z, AIR)
        p.set(x, y + 2, z, AIR)

    # --- slits
    for y in range(ground + 3, top - 2, 4):
        p.set(int(cx + r), y, int(cz), AIR)
        p.set(int(cx - r), y, int(cz), AIR)
        p.set(int(cx), y, int(cz + r), AIR)
        p.set(int(cx), y, int(cz - r), AIR)

    # --- balcony: corbels one wider, then a parapet
    if s.get('balcony'):
        by = top - 5
        ring(p, cx, cz, by, r + 1.0, (pal['slab'], None))
        ring(p, cx, cz, by, r + 1.0, slab(pal['slab'], 'top'))
        ring(p, cx, cz, by + 1, r + 1.0, (pal['wall'], None))

    # --- the cap
    for i in range(int(r) + 2):
        ring(p, cx, cz, top + i, max(0.0, r - i * 0.9), brick)
    p.set(int(cx), top + int(r) + 2, int(cz), (pal['accent'], None))

    p.set(int(cx + 1), ground, int(cz + 1), *chest('west', 'surface_uncommon'))
    p.set(int(cx - 1), top - 7, int(cz - 1), *barrel('up', 'surface_common'))
    p.set(int(cx), ground + 2, int(cz), B(pal['light'], hanging=True, waterlogged=False))

    decay(p, seed, s['ruin'], ground + int(h * 0.35), sy - 1, 'none')
    weather(p, seed, pal)
    drape(p, seed, pal, chance=0.09)
    connect(p)
    return p


def build_hall(pal, s, ground, size, seed):
    p = Piece(*size)
    sx, sy, sz = size
    L, W, H = s['length'], s['width'], s['height']
    x0, z0 = (sx - L) // 2, (sz - W) // 2
    x1, z1 = x0 + L - 1, z0 + W - 1
    brick = (pal['brick'], None)

    box(p, x0, ground - 1, z0, x1, ground - 1, z1, (pal['floor'], None))
    shell(p, x0, ground, z0, x1, ground + H, z1, brick)
    box(p, x0 + 1, ground, z0 + 1, x1 - 1, ground + H, z1 - 1, AIR)

    # buttresses, which is what stops a 30-block wall reading as a fence
    for x in range(x0 + 3, x1 - 2, 5):
        box(p, x, ground, z0 - 1, x, ground + H - 3, z0 - 1, brick)
        box(p, x, ground, z1 + 1, x, ground + H - 3, z1 + 1, brick)
        p.set(x, ground + H - 2, z0 - 1, stair(pal['stairs'], 'north', half='top'))
        p.set(x, ground + H - 2, z1 + 1, stair(pal['stairs'], 'south', half='top'))

    # doors at both ends, tall and arched
    for (dx, face) in ((x0, 'west'), (x1, 'east')):
        box(p, dx, ground, z0 + W // 2 - 1, dx, ground + 3, z0 + W // 2 + 1, AIR)
        p.set(dx, ground + 4, z0 + W // 2, (pal['accent'], None))
        del face

    for y in (ground + 3, ground + 6):
        if y >= ground + H - 1:
            break
        for x in range(x0 + 2, x1 - 1, 4):
            p.set(x, y, z0, (pal['glass'], None))
            p.set(x, y, z1, (pal['glass'], None))

    if s.get('colonnade'):
        for x in range(x0 + 4, x1 - 3, 5):
            for z in (z0 + 2, z1 - 2):
                box(p, x, ground, z, x, ground + H - 3, z, pillar(pal['pillar']))
                p.set(x, ground + H - 2, z, (pal['accent'], None))

    # gabled roof along the length
    peak = W // 2
    for i in range(peak + 1):
        y = ground + H + 1 + i
        for x in range(x0 - 1, x1 + 2):
            p.set(x, y, z0 + i, stair(pal['stairs'], 'south'))
            p.set(x, y, z1 - i, stair(pal['stairs'], 'north'))
    for x in range(x0 - 1, x1 + 2):
        p.set(x, ground + H + 1 + peak, z0 + peak, (pal['slab'], None))

    # the long hearth down the middle
    for x in range(x0 + 6, x1 - 5, 6):
        p.set(x, ground - 1, z0 + W // 2, B('minecraft:campfire', lit=False,
                                            facing='north', signal_fire=False,
                                            waterlogged=False))
    for x in range(x0 + 3, x1 - 2, 7):
        p.set(x, ground, z0 + 1, (pal['plank'], None))
        p.set(x, ground, z1 - 1, (pal['plank'], None))

    if s.get('silo'):
        ox, oz = x1 + 4, z0 + W // 2
        cylinder(p, ox, oz, ground - 1, ground + H + 3, 3.5, brick)
        cylinder(p, ox, oz, ground, ground + H + 2, 2.5, AIR, hollow=False)
        for i in range(4):
            ring(p, ox, oz, ground + H + 4 + i, 3.5 - i * 0.9, (pal['slab'], None))
        p.set(ox + 3, ground, oz, AIR)
        p.set(ox + 3, ground + 1, oz, AIR)
        p.set(ox, ground, oz, *barrel('up', 'surface_uncommon'))

    p.set(x0 + 2, ground, z0 + 2, *chest('east', 'surface_uncommon'))
    p.set(x1 - 2, ground, z1 - 2, *chest('west', 'surface_common'))

    keep_floor = {(x, ground - 1, z) for x in range(sx) for z in range(sz)}
    decay(p, seed, s['roof'], ground + H, sy - 1, 'none')
    decay(p, seed ^ 0x11, s['roof'] * 0.4, ground, ground + H - 1, 'none', keep=keep_floor)
    weather(p, seed, pal)
    drape(p, seed, pal, chance=0.12)
    connect(p)
    return p


def build_aqueduct(pal, s, ground, size, seed):
    p = Piece(*size)
    sx, sy, sz = size
    span, H = s['span'], s['height']
    cz = sz // 2
    deck = ground + H
    brick = (pal['brick'], None)
    n_arch = s['arches']
    total = n_arch * span
    x0 = max(0, (sx - total) // 2)

    for a in range(n_arch):
        px = x0 + a * span
        fallen = (a == s['break_at'])
        # piers, four thick across the run
        for dz in range(-2, 3):
            box(p, px, ground - 1, cz + dz, px + 1, deck - 1, cz + dz, brick)
        if fallen:
            continue
        # the arch itself: a semicircle sprung between this pier and the next
        r = (span - 2) / 2.0
        mid = px + 1 + r + 0.5
        for x in range(px + 2, px + span):
            dx = x - mid
            if abs(dx) > r:
                continue
            rise = math.sqrt(max(0.0, r * r - dx * dx))
            for y in range(deck - 1 - int(round(rise)), deck):
                for dz in range(-2, 3):
                    p.set(x, y, cz + dz, brick)
        # deck and the channel it carries
        for x in range(px, px + span):
            for dz in range(-2, 3):
                p.set(x, deck, cz + dz, (pal['floor'], None))
            if s.get('channel'):
                p.set(x, deck + 1, cz - 2, (pal['wall'], None))
                p.set(x, deck + 1, cz + 2, (pal['wall'], None))
                for dz in (-1, 0, 1):
                    p.set(x, deck + 1, cz + dz, AIR)
                    p.set(x, deck, cz + dz, (pal['brick_mossy'], None))

    # the fallen arch, on the ground where it landed
    bx = x0 + s['break_at'] * span
    scatter_rubble(p, seed, pal, ground - 1,
                   [(x, cz + dz) for x in range(bx, min(sx, bx + span))
                    for dz in range(-4, 5)], density=0.55)
    scatter_rubble(p, seed ^ 3, pal, ground,
                   [(x, cz + dz) for x in range(bx + 1, min(sx, bx + span - 1))
                    for dz in range(-2, 3)], density=0.3)

    p.set(x0 + 1, ground, cz + 3, *chest('south', 'surface_common'))
    decay(p, seed, 0.22, deck, sy - 1, 'none')
    weather(p, seed, pal)
    drape(p, seed, pal, chance=0.16)
    connect(p)
    return p


def build_span(pal, s, ground, size, seed):
    p = Piece(*size)
    rng = random.Random(seed)
    sx, sy, sz = size
    cz = sz // 2
    deck = ground + s['height']
    L = min(s['length'], sx)
    brk = s['break_from']
    timber = s.get('timber')
    body = (pal['plank'], None) if timber else (pal['brick'], None)

    for x in range(L):
        # A ragged end rather than a clean cut: the last three blocks fray.
        if x >= brk:
            if x > brk + 2 or rng.random() < 0.45:
                continue
        for dz in range(-2, 3):
            p.set(x, deck, cz + dz, body)
        if s.get('rail'):
            p.set(x, deck + 1, cz - 2, (pal['wall'], None))
            p.set(x, deck + 1, cz + 2, (pal['wall'], None))
        if x % 8 == 0 and x < brk:
            for dz in (-2, 2):
                box(p, x, ground - 1, cz + dz, x, deck - 1, cz + dz,
                    pillar(pal['timber']) if timber else (pal['brick'], None))
            for y in range(ground, deck - 1, 3):
                p.set(x, y, cz - 1, (pal['slab'], None))
                p.set(x, y, cz + 1, (pal['slab'], None))

    # abutment at the standing end
    box(p, 0, ground - 1, cz - 3, 2, deck - 1, cz + 3, (pal['brick'], None))
    for i in range(4):
        p.set(2, deck - 1 - i, cz + 0, stair(pal['stairs'], 'east'))

    scatter_rubble(p, seed, pal, ground - 1,
                   [(x, cz + dz) for x in range(brk - 2, min(sx, brk + 8))
                    for dz in range(-4, 5)], density=0.4)
    p.set(1, deck + 1, cz + 1, *chest('west', 'surface_common'))
    decay(p, seed, 0.25, deck, sy - 1, 'none')
    weather(p, seed, pal)
    drape(p, seed, pal, chance=0.14)
    connect(p)
    return p


def build_barrow(pal, s, ground, size, seed):
    p = Piece(*size)
    rng = random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx / 2.0, sz / 2.0
    R, H = s['radius'], s['height']
    has_mound = s['door'] != 'none'

    if has_mound:
        # the mound: a squat dome of turf over a stone core
        for y in range(H):
            r = R * math.sqrt(max(0.0, 1.0 - (y / float(H)) ** 2))
            disc(p, cx, cz, ground + y, r, ('minecraft:coarse_dirt', None))
            if y < 2:
                ring(p, cx, cz, ground + y, r, (pal['stone'], None), width=1.5)
        # The chamber, cut into the ground under the mound. FLOOR is the lowest course the
        # piece owns: `ground` is 4, so anything below ground-4 is y<0 and Piece.set drops it
        # silently -- which is exactly how the first draft shipped a tomb with no floor.
        floor_y, air0, air1, roof_y = ground - 4, ground - 3, ground - 1, ground
        box(p, int(cx) - 3, floor_y, int(cz) - 3, int(cx) + 3, roof_y,
            int(cz) + 3, (pal['brick'], None))
        box(p, int(cx) - 2, floor_y, int(cz) - 2, int(cx) + 2, floor_y,
            int(cz) + 2, (pal['floor'], None))
        box(p, int(cx) - 2, air0, int(cz) - 2, int(cx) + 2, air1, int(cz) + 2, AIR)
        for corner in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            box(p, int(cx) + corner[0], air0, int(cz) + corner[1],
                int(cx) + corner[0], air1, int(cz) + corner[1], pillar(pal['pillar']))
        # the passage out to the door
        dx, dz = STEP[s['door']]
        for i in range(3, R + 3):
            ax, az = int(cx + dx * i), int(cz + dz * i)
            box(p, ax - 1, floor_y, az - 1, ax + 1, roof_y, az + 1, (pal['brick'], None))
            box(p, ax, air0, az, ax, air0 + 1, az, AIR)
        # the portal, standing proud of the mound
        px, pz = int(cx + dx * (R + 2)), int(cz + dz * (R + 2))
        for w in (-1, 1):
            wx, wz = (px + w, pz) if dx == 0 else (px, pz + w)
            box(p, wx, floor_y, wz, wx, ground + 1, wz, pillar(pal['pillar']))
        p.set(px, ground + 2, pz, (pal['accent'], None))
        box(p, px, air0, pz, px, air0 + 1, pz, AIR)
        p.set(int(cx), air0, int(cz), *chest(s['door'], 'surface_rare'))
        p.set(int(cx) + 1, air0, int(cz), B(pal['light'], hanging=False, waterlogged=False))
    else:
        # No mound. A paved ring, which is a meeting place rather than a grave.
        disc(p, cx, cz, ground - 1, R * 0.8, (pal['floor'], None))
        ring(p, cx, cz, ground - 1, R * 0.8, (pal['brick'], None), width=1.5)
        p.set(int(cx), ground, int(cz), (pal['accent'], None))
        p.set(int(cx) + 2, ground - 1, int(cz) + 2, *barrel('up', 'surface_common'))

    # the standing stones
    for i in range(s['menhirs']):
        a = math.tau * i / s['menhirs']
        mx = int(round(cx + (R + 4) * math.cos(a)))
        mz = int(round(cz + (R + 4) * math.sin(a)))
        fallen = rng.random() < 0.22
        h = s['menhir_h'] - rng.randint(0, 1)
        if fallen:
            # laid flat, pointing outward, the way a toppled stone actually lies
            for j in range(h):
                p.set(int(round(mx + j * math.cos(a))), ground,
                      int(round(mz + j * math.sin(a))), pillar(pal['pillar'], 'x'))
        else:
            box(p, mx, ground - 2, mz, mx, ground + h, mz, pillar(pal['pillar']))
            p.set(mx, ground + h + 1, mz, (pal['slab'], None))

    weather(p, seed, pal)
    drape(p, seed, pal, chance=0.10)
    connect(p)
    return p


def build_wreck(pal, s, ground, size, seed):
    p = Piece(*size)
    rng = random.Random(seed)
    sx, sy, sz = size
    L, Bm, H = s['length'], s['beam'], s['height']
    x0 = (sx - L) // 2
    cz = sz / 2.0
    heel = math.radians(s['list'])
    hull = (pal['plank'], None)
    rib = pillar(pal['timber'], 'x')

    for i in range(L):
        t = i / float(L - 1)
        # a hull section: full amidships, drawn to a point at bow and stern
        half = (Bm / 2.0) * math.sin(math.pi * (0.12 + 0.88 * t)) ** 0.6
        if t > s['broken']:
            # the broken end. Ribs, no planking, and fewer of them as you go aft.
            if rng.random() > (1.0 - t) / max(0.01, 1.0 - s['broken']):
                continue
        for y in range(H):
            yy = ground + y
            shift = (y - H / 2.0) * math.tan(heel)
            wide = half * math.sqrt(max(0.0, 1.0 - ((H - 1 - y) / float(H)) ** 2 * 0.8))
            for dz in range(-int(wide) - 1, int(wide) + 2):
                z = int(round(cz + dz + shift))
                edge = abs(dz) >= wide - 0.6
                if not edge and y > 0:
                    p.set(x0 + i, yy, z, AIR)
                    continue
                p.set(x0 + i, yy, z, rib if i % 4 == 0 else hull)
        # deck
        if t <= s['broken']:
            shift = (H - 1 - H / 2.0) * math.tan(heel)
            for dz in range(-int(half), int(half) + 1):
                p.set(x0 + i, ground + H, int(round(cz + dz + shift)), (pal['plank'], None))

    # the mast, snapped
    if s.get('mast'):
        mx = x0 + int(L * 0.35)
        shift = int((H / 2.0) * math.tan(heel))
        for y in range(12):
            p.set(mx, ground + H + y, int(cz) + shift + int(y * math.tan(heel)),
                  pillar(pal['timber']))
        for dz in range(-4, 5):
            p.set(mx, ground + H + 7, int(cz) + shift + dz, pillar(pal['timber'], 'z'))

    # A hatch amidships, and a ladder down it. A deck with no opening is a lid, and the hold
    # under it -- with both chests in it -- would be unreachable without a pickaxe.
    hxx = x0 + int(L * 0.42)
    hshift = int((H - 1 - H / 2.0) * math.tan(heel))
    for dx in range(3):
        for dz in range(-1, 2):
            p.set(hxx + dx, ground + H, int(round(cz)) + dz + hshift, AIR)
    for y in range(ground + 1, ground + H + 1):
        p.set(hxx, y, int(round(cz)) + hshift,
              B('minecraft:ladder', facing='east', waterlogged=False))

    # the hold: two chests and the cargo that spilled
    hx = x0 + int(L * 0.5)
    p.set(hx, ground + 1, int(cz), *chest('east', 'surface_uncommon'))
    p.set(hx + 2, ground + 1, int(cz) + 1, *barrel('up', 'surface_common'))
    p.set(x0 + int(L * 0.2), ground + 1, int(cz) - 1, *chest('west', 'surface_common'))
    scatter_rubble(p, seed, pal, ground - 1,
                   [(x, z) for x in range(x0 + int(L * s['broken']), min(sx, x0 + L + 6))
                    for z in range(int(cz) - 6, int(cz) + 7)], density=0.28)

    weather(p, seed, pal)
    drape(p, seed, pal, chance=0.20)
    connect(p)
    return p


def build_shrine(pal, s, ground, size, seed):
    p = Piece(*size)
    sx, sy, sz = size
    cx, cz = sx / 2.0, sz / 2.0
    R, H = float(s['radius']), s['height']
    brick = (pal['brick'], None)

    # A stilted shrine stands OUT of the water and its heightmap is OCEAN_FLOOR_WG, so
    # `ground` is the lake bed and the deck must be lifted clear of it. Stilts therefore go
    # UP: a piece cannot build below its own y=0, and the first draft's downward legs were
    # dropped silently by Piece.set, leaving a shrine floating with nothing under it.
    lift = 7 if s.get('stilts') else 1
    base = ground + lift                    # the deck or plinth top; everything stands on it

    if s.get('stilts'):
        for i in range(s['pillars']):
            a = math.tau * i / s['pillars']
            lx = int(round(cx + R * math.cos(a)))
            lz = int(round(cz + R * math.sin(a)))
            box(p, lx, ground - 1, lz, lx, base - 1, lz, pillar(pal['timber']))
        disc(p, cx, cz, base, R + 1.0, (pal['plank'], None))
        for i in range(int(R) + 2, int(R) + 9):              # a jetty, so it can be reached
            p.set(int(cx) + i, base, int(cz), (pal['plank'], None))
            p.set(int(cx) + i, base - 1, int(cz), pillar(pal['timber']))
    else:
        for y in range(ground - 1, base + 1):
            disc(p, cx, cz, y, R + 2.0 - (y - ground + 1) * 0.5, (pal['stone'], None))
        disc(p, cx, cz, base, R + 1.0, (pal['floor'], None))
        ring(p, cx, cz, base - 1, R + 2.5, slab(pal['slab'], 'bottom'))

    colonnade_h = H - 4
    for i in range(s['pillars']):
        a = math.tau * i / s['pillars']
        px = int(round(cx + R * math.cos(a)))
        pz = int(round(cz + R * math.sin(a)))
        box(p, px, base + 1, pz, px, base + colonnade_h, pz, pillar(pal['pillar']))
        p.set(px, base + colonnade_h + 1, pz, (pal['accent'], None))
    ring(p, cx, cz, base + colonnade_h + 2, R, brick)

    if s.get('dome'):
        rise = int(R) + 2
        for i in range(rise):
            r = R * math.sqrt(max(0.0, 1.0 - (i / float(rise)) ** 2))
            ring(p, cx, cz, base + colonnade_h + 3 + i, r, brick)
        p.set(int(cx), base + colonnade_h + 3 + rise, int(cz), (pal['accent'], None))
    else:
        # an open cage of beams, for the shrines that were never roofed at all
        for i in range(s['pillars']):
            a = math.tau * i / s['pillars']
            for j in range(3):
                p.set(int(round(cx + (R - j) * math.cos(a))),
                      base + colonnade_h + 3 + j,
                      int(round(cz + (R - j) * math.sin(a))), (pal['slab'], None))

    # the altar
    box(p, int(cx) - 1, base + 1, int(cz) - 1, int(cx) + 1, base + 1, int(cz) + 1, brick)
    p.set(int(cx), base + 2, int(cz), (pal['accent'], None))
    p.set(int(cx), base + 3, int(cz), B(pal['light'], hanging=False, waterlogged=False))
    p.set(int(cx) + 2, base + 1, int(cz) + 2, *chest('west', 'surface_common'))

    keep_deck = {(x, y, z) for x in range(sx) for z in range(sz)
                 for y in (ground - 1, base)}
    decay(p, seed, s['ruin'], base + 1, sy - 1, 'none', keep=keep_deck)
    weather(p, seed, pal)
    scatter_rubble(p, seed, pal, ground - 1,
                   [(x, z) for x in range(sx) for z in range(sz)
                    if R + 2 < math.hypot(x - cx, z - cz) < R + 6], density=0.12)
    drape(p, seed, pal, chance=0.13)
    connect(p)
    return p


BUILDERS = {
    'castle': build_castle, 'quarry': build_quarry, 'crater': build_crater,
    'tower': build_tower, 'hall': build_hall, 'aqueduct': build_aqueduct,
    'span': build_span, 'barrow': build_barrow, 'wreck': build_wreck,
    'shrine': build_shrine,
}


# --------------------------------------------------------------------------- datapack


def salt_for(sid):
    """Unique per structure and stable across runs. See the header, point 3."""
    return int(hashlib.sha1(('alfheim:surface:' + sid).encode()).hexdigest()[:7], 16)


def write_json(path, obj, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def chest_tables():
    """Three tiers. Commodities, ruin-appropriate tools, and the raw blooms of the era a
    player exploring this deep would already be in. THE_SURFACE.md §6.1: no runes, no tier
    materials, nothing that shortens an era."""

    def item(name, lo=1, hi=1, weight=10):
        e = {'type': 'minecraft:item', 'name': name, 'weight': weight}
        if (lo, hi) != (1, 1):
            e['functions'] = [{'function': 'minecraft:set_count',
                               'count': {'type': 'minecraft:uniform',
                                         'min': float(lo), 'max': float(hi)}, 'add': False}]
        return e

    def table(name, pools):
        return {'type': 'minecraft:chest', 'random_sequence': f'{NS}:chests/{name}',
                'pools': pools}

    common = table('surface_common', [
        {'rolls': {'type': 'minecraft:uniform', 'min': 2.0, 'max': 4.0}, 'bonus_rolls': 0.0,
         'entries': [
             item('botania:livingrock', 4, 12, 12), item('botania:dreamwood', 2, 6, 10),
             item('minecraft:string', 2, 6, 8), item('minecraft:bone', 1, 4, 8),
             item('minecraft:torch', 4, 10, 8), item('minecraft:coal', 1, 4, 8),
             item('botania:white_petal', 2, 5, 6), item('botania:gray_petal', 2, 5, 6),
             item('alfheim:raw_cinderbloom', 1, 3, 5),
             item('alfheim:raw_palebloom', 1, 3, 5),
             {'type': 'minecraft:empty', 'weight': 6}]},
    ])
    uncommon = table('surface_uncommon', [
        {'rolls': {'type': 'minecraft:uniform', 'min': 3.0, 'max': 5.0}, 'bonus_rolls': 0.0,
         'entries': [
             item('alfheim:raw_verdigris', 1, 4, 10), item('alfheim:raw_sparkroot', 1, 3, 8),
             item('alfheim:raw_duskbloom', 1, 3, 8), item('botania:livingrock', 8, 20, 10),
             item('botania:dreamwood', 4, 10, 8), item('botania:elf_glass', 2, 6, 6),
             item('minecraft:gold_nugget', 2, 8, 6),
             item('alfheim:emberglass_shard', 1, 3, 5),
             item('alfheim:tidewake_shard', 1, 3, 5),
             {'type': 'minecraft:empty', 'weight': 5}]},
        {'rolls': 1.0, 'bonus_rolls': 0.0,
         'entries': [item('minecraft:experience_bottle', 1, 3, 6),
                     item('botania:fertilizer', 1, 2, 6),
                     {'type': 'minecraft:empty', 'weight': 10}]},
    ])
    rare = table('surface_rare', [
        {'rolls': {'type': 'minecraft:uniform', 'min': 4.0, 'max': 6.0}, 'bonus_rolls': 0.0,
         'entries': [
             item('alfheim:raw_sunbloom', 1, 3, 8), item('alfheim:raw_cloudglass', 1, 3, 8),
             item('alfheim:raw_silverthorn', 1, 2, 5),
             item('alfheim:dawnglass_shard', 1, 4, 7),
             item('alfheim:duskglass_shard', 1, 4, 7),
             item('alfheim:rootglass_shard', 1, 4, 7),
             item('botania:elf_glass', 4, 10, 8), item('minecraft:gold_ingot', 1, 4, 6),
             item('minecraft:experience_bottle', 2, 5, 6)]},
        {'rolls': 1.0, 'bonus_rolls': 0.0,
         'entries': [item('alfheim:raw_grievebloom', 1, 2, 4),
                     item('minecraft:diamond', 1, 2, 3),
                     {'type': 'minecraft:empty', 'weight': 9}]},
    ])
    return {'surface_common': common, 'surface_uncommon': uncommon, 'surface_rare': rare}


def explorer_map(arch_key, arch):
    """One filled map, pointed at the nearest member of the archetype's structure tag.

    `destination` is a structure TAG written with no leading '#': the deserializer does
    TagKey.create(Registries.STRUCTURE, new ResourceLocation(s)) on the raw string. See
    THE_SURFACE.md §5.1.
    """
    return {
        'type': 'minecraft:chest',
        'random_sequence': f'{NS}:explorer_maps/{arch_key}',
        'pools': [{
            'rolls': 1.0, 'bonus_rolls': 0.0,
            'entries': [{
                'type': 'minecraft:item', 'name': 'minecraft:map',
                'functions': [
                    {'function': 'minecraft:exploration_map',
                     'destination': f'{NS}:{arch_key}',
                     'decoration': arch['icon'],
                     'zoom': arch['zoom'],
                     'search_radius': arch['search_radius'],
                     'skip_existing_chunks': False},
                    {'function': 'minecraft:set_name',
                     'name': {'text': f"Survey Chart — {arch['plural']}",
                              'italic': False, 'color': 'aqua'}},
                    {'function': 'minecraft:set_lore',
                     'lore': [{'text': arch['blurb'], 'italic': True, 'color': 'gray'}],
                     'replace': True},
                ]}]}]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', help='build one structure by id')
    a = ap.parse_args()
    dry = a.dry_run

    m = json.load(open(MANIFEST, encoding='utf-8'))
    blooms = json.load(open(BLOOMS, encoding='utf-8'))
    shallow_ores = [f"{NS}:{b['id']}_ore" for b in blooms['blooms'] if b['era'] <= 4]

    palettes, archetypes, bands = m['palettes'], m['archetypes'], m['bands']
    structures = [s for s in m['structures'] if not a.only or s['id'] == a.only]
    by_arch = {}
    total_blocks = 0
    drops = []

    for st in structures:
        arch = archetypes[st['archetype']]
        pal = palettes[st['palette']]
        shape = dict(arch['defaults'])
        shape.update(st.get('shape', {}))
        ground = arch['ground']
        size = tuple(arch['size'])
        seed = int(hashlib.sha1(st['id'].encode()).hexdigest()[:8], 16)

        builder = BUILDERS[st['archetype']]
        kw = {'ores': shallow_ores} if st['archetype'] == 'quarry' else {}
        piece = builder(pal, shape, ground, size, seed, **kw)

        for axis_len in size:
            assert axis_len <= MAX_AXIS, f"{st['id']} is {size} -- over the {MAX_AXIS} limit"

        path = os.path.join(STRUCT_DIR, st['id'] + '.nbt')
        if not dry:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            nbt.save(path, '', piece.to_nbt())
        total_blocks += len(piece.blocks)
        kb = (os.path.getsize(path) / 1024.0) if (not dry and os.path.exists(path)) else 0.0
        # `dropped` is every set() that fell outside the piece. Some overdraw is expected --
        # a disc scans its bounding square, rubble is scattered over a rectangle -- but a
        # ratio near 1 means real geometry was clipped and nothing said so.
        ratio = piece.dropped / max(1, len(piece.blocks))
        drops.append((st['id'], ratio))
        print(f"  {st['id']:20} {st['archetype']:9} {size[0]}x{size[1]}x{size[2]}  "
              f"{len(piece.blocks):>6} blocks  {len(piece.palette):>3} palette  "
              f"{kb:6.1f} KB  overdraw {ratio:4.2f}"
              + ("  <-- CLIPPED" if ratio > 0.60 else ""))

        # --- template pool: one element, no jigsaw blocks. `size: 1` on the structure means
        # the start piece is the whole structure, which is what a single-piece ruin wants.
        write_json(os.path.join(DATA, 'worldgen', 'template_pool', 'surface',
                                st['id'] + '.json'),
                   {'name': f"{NS}:surface/{st['id']}", 'fallback': 'minecraft:empty',
                    'elements': [{'weight': 1, 'element': {
                        'location': f"{NS}:surface/{st['id']}",
                        'processors': 'minecraft:empty', 'projection': 'rigid',
                        'element_type': 'minecraft:single_pool_element'}}]}, dry)

        adaptation = st.get('adaptation', arch['adaptation'])
        write_json(os.path.join(DATA, 'worldgen', 'structure', st['id'] + '.json'), {
            'type': 'minecraft:jigsaw',
            'biomes': f"#{NS}:has_{st['id']}",
            'step': 'surface_structures',
            'terrain_adaptation': adaptation,
            'start_pool': f"{NS}:surface/{st['id']}",
            'size': 1,
            # JigsawStructure's codec validates max_distance_from_center + margin <= 128, and
            # the margin is 12 for every terrain_adaptation except `none`. Exceeding it does
            # not cull a piece -- it REFUSES WORLD CREATION, which SPAWN_HUB.md paid for at
            # runtime. 116 is the value the Greatbole has been proven on, it clears the budget
            # under either adaptation, and no single 48-block piece comes close to needing it.
            'max_distance_from_center': min(116, 128 - ADAPTATION_MARGIN[adaptation]),
            'start_height': {'absolute': -ground},
            'project_start_to_heightmap': st.get('heightmap', 'WORLD_SURFACE_WG'),
            'use_expansion_hack': False,
            'spawn_overrides': {},
        }, dry)

        band = bands[arch['band']]
        write_json(os.path.join(DATA, 'worldgen', 'structure_set', st['id'] + '.json'), {
            'structures': [{'structure': f"{NS}:{st['id']}", 'weight': 1}],
            'placement': {'type': 'minecraft:random_spread',
                          'spacing': band['spacing'], 'separation': band['separation'],
                          'spread_type': 'linear', 'salt': salt_for(st['id'])},
        }, dry)

        write_json(os.path.join(DATA, 'tags', 'worldgen', 'biome',
                                f"has_{st['id']}.json"),
                   {'replace': False, 'values': st['biomes']}, dry)

        by_arch.setdefault(st['archetype'], []).append(st['id'])

    # --- one structure tag and one map per archetype
    for key, ids in sorted(by_arch.items()):
        write_json(os.path.join(DATA, 'tags', 'worldgen', 'structure', key + '.json'),
                   {'replace': False, 'values': [f'{NS}:{i}' for i in ids]}, dry)
        write_json(os.path.join(DATA, 'loot_tables', 'explorer_maps', key + '.json'),
                   explorer_map(key, archetypes[key]), dry)

    for name, tbl in chest_tables().items():
        write_json(os.path.join(DATA, 'loot_tables', 'chests', name + '.json'), tbl, dry)

    print(f"\n  {len(structures)} structures, {len(by_arch)} archetypes, "
          f"{total_blocks} blocks, {len(chest_tables())} chest tables")
    print('  maps: ' + ', '.join(f'{k}({len(v)})' for k, v in sorted(by_arch.items())))
    worst = max(drops, key=lambda d: d[1], default=None)
    if worst:
        print(f'  worst overdraw ratio {worst[1]:.2f} ({worst[0]})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
