"""Generate the Ley Line Channel Corridor network as worldgen.

    python tools/gen_leyline_corridors.py
    python tools/gen_leyline_corridors.py --check

WHY THIS EXISTS. Field report 2026-09-07: "I still haven't seen the Ley line conduit shafts
spawning. They may be missing a spawn criteria or Biome." They were missing neither. The
worldgen half did not exist at all -- only Phase 1, the status-effect registry and its icons.
There was no block, no structure, no template pool and no NBT anywhere in the pack, so there was
nothing for a spawn criterion to fail.

WHAT THIS BUILDS. The corridors, the relays, the hubs and the vertical exchanges -- and, since
2026-09-08, the dormant conduit nodes themselves, now that `first_party_mods/alfheim_leyworks`
owns the block. What it deliberately does NOT place is the ACTIVE node. That is the whole design:
LEY_LINE_CHANNEL_CORRIDORS.md states the intended starting state directly -- "The network begins
as archaeology rather than infrastructure. Most nodes are dormant or disconnected." So worldgen
seeds the world with inert nodes and the player lights them, one elementium core at a time.

The dormant block has no block entity, which is not an aesthetic choice: a size-6 network places
roughly a dozen nodes and there are thousands of these structures in a world. Ticking them all on
generation would be exactly the kind of load the 2026-09-07 field report was already complaining
about. Nothing in a generated corridor ticks until a player converts a node by hand.

This generator therefore depends on `alfheim_leyworks` being in `mods/`. If that jar is absent the
node palette entries will not resolve and the corridors will generate with holes where the nodes
belong -- see check `L1` below, which asserts the jar is present.

GEOMETRY, from the design's fixed decisions: five-by-five clear interior, one-block shell for a
seven-by-seven envelope, the channel on the exact horizontal and vertical centre, two-block
maintenance lanes either side, and relay collars at intervals that push the player into the lanes.
"""
import argparse
import glob
import hashlib
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
import structure_detail as sd  # noqa: E402
from structure_nbt import MAX_AXIS, Piece  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', NS)
STRUCT = os.path.join(DATA, 'structures', 'leyline')
POOL = os.path.join(DATA, 'worldgen', 'template_pool', 'leyline')

# --- the corridor section ---------------------------------------------------------------------
# 7x7 outer envelope, 5x5 clear. The channel sits at the exact centre of that clear span, which
# on a 7-wide piece is index 3 in both axes and y=3 in the interior.
W = 7                       # outer envelope, both horizontal axes
H = 7                       # outer envelope height
RUN = 16                    # length of one straight section
C = W // 2                  # 3 -- the channel column
FLOOR, ROOF = 0, H - 1

AIR = ('minecraft:air', None)


def B(name, **props):
    return (name, {k: str(v).lower() if isinstance(v, bool) else str(v)
                   for k, v in props.items()} or None)


SHELL = B('alfheim:leyline_livingrock_bricks')
SHELL_WORN = B('alfheim:cracked_livingrock')
DECK = B('alfheim:leyline_livingrock_polished')
COLLAR = B('alfheim:leyline_livingrock_carved')
CHANNEL = B('alfheim:mana_glass_light')          # the dormant channel itself
CHANNEL_DEAD = B('alfheim:leyline_livingrock')   # a length that has gone out
RELAY = B('alfheim:moonstone_livingrock_bricks')
# The node the player is meant to find: inert, faintly lit, and worth carrying home. Placing the
# dormant variant rather than the active one is what makes the network archaeology.
NODE = B('alfheim_leyworks:ley_conduit_node_dormant')
RAIL = B('alfheim:leyline_livingrock_wall')
LANTERN = B('minecraft:lantern', hanging=True)
CHAIN = B('minecraft:chain', axis='y')


def box(p, x0, y0, z0, x1, y1, z1, block):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                p.set(x, y, z, block)


def shell_run(p, rng, length, axis):
    """Solid 7x7 block, hollowed to 5x5, along `axis` ('z' or 'x')."""
    sx, sy, sz = p.size
    box(p, 0, 0, 0, sx - 1, sy - 1, sz - 1, SHELL)
    # Weathering: patches of the shell have failed to cracked stone.
    for _ in range(length * 6):
        x, y, z = rng.randrange(sx), rng.randrange(sy), rng.randrange(sz)
        p.set(x, y, z, SHELL_WORN)
    box(p, 1, 1, 1, sx - 2, sy - 2, sz - 2, AIR)
    box(p, 1, FLOOR + 1, 1, sx - 2, FLOOR + 1, sz - 2, DECK)


def channel_line(p, rng, length, axis):
    """The luminous channel down the exact centre, with its mounting collars.

    Dormant, not live: roughly one length in six has gone out and reads as plain leyline stone,
    which is what makes the network read as something to repair rather than something working.
    """
    for i in range(1, length - 1):
        x, z = (C, i) if axis == 'z' else (i, C)
        lit = rng.random() > 0.17
        p.set(x, C, z, CHANNEL if lit else CHANNEL_DEAD)
        # Collars every four blocks, and a relay node every twelve. The relay is solid: it is
        # what forces the player out of the centre and into the maintenance lanes.
        if i % 12 == 6:
            for dy in (-1, 0, 1):
                for d in (-1, 0, 1):
                    cx, cz = (C + d, i) if axis == 'z' else (i, C + d)
                    p.set(cx, C + dy, cz, RELAY)
            # The relay's heart is a dormant node, seated in its housing. One per twelve blocks
            # of corridor: often enough to be the reason to walk a run, rare enough to matter.
            p.set(x, C, z, NODE)
        elif i % 4 == 0:
            for dy in (-1, 1):
                p.set(x, C + dy, z, COLLAR)
            p.set(x, ROOF - 1, z, CHAIN)
            p.set(x, ROOF - 2, z, LANTERN)


def lane_rails(p, rng, length, axis):
    """A low rail marking each two-block maintenance lane, broken in places."""
    for i in range(2, length - 2):
        for d in (-2, 2):
            if rng.random() < 0.62:
                x, z = (C + d, i) if axis == 'z' else (i, C + d)
                p.set(x, FLOOR + 2, z, RAIL)


def jig(p, x, y, z, name, target, pool, orientation):
    p.jigsaw(x, y, z, f'{NS}:{name}', f'{NS}:{target}',
             pool if pool == 'minecraft:empty' else f'{NS}:leyline/{pool}',
             orientation, joint='aligned', final_state='minecraft:air')


# --- the pieces ---------------------------------------------------------------------------------
def straight(size, seed):
    p, rng = Piece(*size), random.Random(seed)
    shell_run(p, rng, size[2], 'z')
    channel_line(p, rng, size[2], 'z')
    lane_rails(p, rng, size[2], 'z')
    box(p, 1, 1, 0, W - 2, H - 2, 0, AIR)
    box(p, 1, 1, size[2] - 1, W - 2, H - 2, size[2] - 1, AIR)
    jig(p, C, C, 0, 'leyline_in', 'leyline_out', 'minecraft:empty', 'north_up')
    jig(p, C, C, size[2] - 1, 'leyline_out', 'leyline_in', 'section', 'south_up')
    return p


def bend(size, seed):
    """A right-angle turn: enters on -Z, leaves on +X."""
    p, rng = Piece(*size), random.Random(seed)
    box(p, 0, 0, 0, W - 1, H - 1, W - 1, SHELL)
    for _ in range(24):
        p.set(rng.randrange(W), rng.randrange(H), rng.randrange(W), SHELL_WORN)
    box(p, 1, 1, 1, W - 2, H - 2, W - 2, AIR)
    box(p, 1, FLOOR + 1, 1, W - 2, FLOOR + 1, W - 2, DECK)
    # The channel turns the corner as two half-runs meeting at a carved knee.
    for z in range(1, C + 1):
        p.set(C, C, z, CHANNEL if rng.random() > 0.17 else CHANNEL_DEAD)
    for x in range(C, W - 1):
        p.set(x, C, C, CHANNEL if rng.random() > 0.17 else CHANNEL_DEAD)
    p.set(C, C, C, COLLAR)
    box(p, 1, 1, 0, W - 2, H - 2, 0, AIR)
    box(p, W - 1, 1, 1, W - 1, H - 2, W - 2, AIR)
    jig(p, C, C, 0, 'leyline_in', 'leyline_out', 'minecraft:empty', 'north_up')
    jig(p, W - 1, C, C, 'leyline_out', 'leyline_in', 'section', 'east_up')
    return p


def junction(size, seed):
    """Four-way crossing with a raised collar over the intersection."""
    p, rng = Piece(*size), random.Random(seed)
    box(p, 0, 0, 0, W - 1, H - 1, W - 1, SHELL)
    for _ in range(20):
        p.set(rng.randrange(W), rng.randrange(H), rng.randrange(W), SHELL_WORN)
    box(p, 1, 1, 1, W - 2, H - 2, W - 2, AIR)
    box(p, 1, FLOOR + 1, 1, W - 2, FLOOR + 1, W - 2, DECK)
    for i in range(1, W - 1):
        p.set(C, C, i, CHANNEL if rng.random() > 0.2 else CHANNEL_DEAD)
        p.set(i, C, C, CHANNEL if rng.random() > 0.2 else CHANNEL_DEAD)
    # Four channels meet here, so the crossing carries a node rather than a plain collar.
    p.set(C, C, C, NODE)
    p.set(C, ROOF - 1, C, CHAIN)
    p.set(C, ROOF - 2, C, LANTERN)
    for face in ('n', 's', 'e', 'w'):
        if face == 'n':
            box(p, 1, 1, 0, W - 2, H - 2, 0, AIR)
        elif face == 's':
            box(p, 1, 1, W - 1, W - 2, H - 2, W - 1, AIR)
        elif face == 'e':
            box(p, W - 1, 1, 1, W - 1, H - 2, W - 2, AIR)
        else:
            box(p, 0, 1, 1, 0, H - 2, W - 2, AIR)
    jig(p, C, C, 0, 'leyline_in', 'leyline_out', 'minecraft:empty', 'north_up')
    jig(p, C, C, W - 1, 'leyline_out', 'leyline_in', 'section', 'south_up')
    jig(p, W - 1, C, C, 'leyline_out', 'leyline_in', 'section', 'east_up')
    jig(p, 0, C, C, 'leyline_out', 'leyline_in', 'section', 'west_up')
    return p


def terminal(size, seed):
    """A sealed end: the channel stops at a dead relay face. Also the pool fallback."""
    p, rng = Piece(*size), random.Random(seed)
    box(p, 0, 0, 0, W - 1, H - 1, W - 1, SHELL)
    for _ in range(26):
        p.set(rng.randrange(W), rng.randrange(H), rng.randrange(W), SHELL_WORN)
    box(p, 1, 1, 1, W - 2, H - 2, W - 2, AIR)
    box(p, 1, FLOOR + 1, 1, W - 2, FLOOR + 1, W - 2, DECK)
    for z in range(1, W - 2):
        p.set(C, C, z, CHANNEL if rng.random() > 0.3 else CHANNEL_DEAD)
    # The terminal face: a dead relay, collapsed spoil at its foot.
    box(p, C - 1, C - 1, W - 2, C + 1, C + 1, W - 2, RELAY)
    # "Most nodes are dormant or disconnected" -- this is the disconnected one, walled into a
    # sealed face with nothing beyond it.
    p.set(C, C, W - 2, NODE)
    for _ in range(10):
        p.set(rng.randrange(1, W - 1), FLOOR + 2, rng.randrange(W - 4, W - 1), SHELL_WORN)
    box(p, 1, 1, 0, W - 2, H - 2, 0, AIR)
    jig(p, C, C, 0, 'leyline_in', 'leyline_out', 'minecraft:empty', 'north_up')
    return p


def hub(size, seed):
    """The start piece: a radial distributor with four corridor spokes."""
    p, rng = Piece(*size), random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx // 2, sz // 2
    box(p, 0, 0, 0, sx - 1, sy - 1, sz - 1, SHELL)
    for _ in range(90):
        p.set(rng.randrange(sx), rng.randrange(sy), rng.randrange(sz), SHELL_WORN)
    # A round chamber rather than a box, so the hub reads differently from a corridor.
    for x in range(sx):
        for z in range(sz):
            if math.hypot(x - cx, z - cz) <= 6.4:
                box(p, x, 1, z, x, sy - 3, z, AIR)
                p.set(x, 1, z, DECK)
    # The distributor column, and the ring of collars around it.
    box(p, cx - 1, 2, cz - 1, cx + 1, sy - 4, cz + 1, RELAY)
    # The distributor's crown. A hub node sits three courses of relay masonry up, which is also
    # the shape a player needs to reproduce to give it a pyramid -- the hint is the building.
    p.set(cx, sy - 4, cz, NODE)
    for k in range(8):
        a = k * math.tau / 8
        x, z = int(cx + math.cos(a) * 5), int(cz + math.sin(a) * 5)
        for y in range(2, 5):
            p.set(x, y, z, COLLAR if y == 4 else RELAY)
    # Four spoke mouths on the cardinal faces, at channel height.
    ch = C
    box(p, cx - 2, ch - 2, 0, cx + 2, ch + 2, 1, AIR)
    box(p, cx - 2, ch - 2, sz - 2, cx + 2, ch + 2, sz - 1, AIR)
    box(p, 0, ch - 2, cz - 2, 1, ch + 2, cz + 2, AIR)
    box(p, sx - 2, ch - 2, cz - 2, sx - 1, ch + 2, cz + 2, AIR)
    jig(p, cx, ch, 0, 'leyline_out', 'leyline_in', 'section', 'north_up')
    jig(p, cx, ch, sz - 1, 'leyline_out', 'leyline_in', 'section', 'south_up')
    jig(p, 0, ch, cz, 'leyline_out', 'leyline_in', 'section', 'west_up')
    jig(p, sx - 1, ch, cz, 'leyline_out', 'leyline_in', 'section', 'east_up')
    return p


PIECES = {
    'straight': (straight, [W, H, RUN]),
    'bend': (bend, [W, H, W]),
    'junction': (junction, [W, H, W]),
    'terminal': (terminal, [W, H, W]),
    'hub': (hub, [17, 12, 17]),
}

# The section pool is what every corridor exit draws from. Weighted so straights dominate and the
# network reads as long arterial runs rather than a knot; the terminal is also the FALLBACK, so a
# branch that hits the depth limit is capped with a sealed face instead of an open hole.
SECTION_WEIGHTS = [('straight', 8), ('bend', 3), ('junction', 2), ('terminal', 2)]


# --- the detail pass ----------------------------------------------------------------------------
#
# The corridors already carried the ley vocabulary -- channel, collars, relays, dormant nodes --
# and the census still put `bend`, `terminal` and `hub` at a flat zero detail share, because all
# of the hanging light lived in `channel_line` and only the straights call it. What every piece
# lacked was age INSIDE the tunnel: nothing on the deck, nothing coming through the roof, and no
# corner a spider had ever found.
#
# Two deliberate omissions. The channel IS the conduit, so `conduits` and `crystal_sockets` are
# off -- adding a second ley run beside the real one would say the opposite of what the design
# says. And the light is hung, never bracketed: a wall torch in a sealed stone corridor reads as
# a mine, and this is not one.

LEY_KIT = dict(
    stone=f'{NS}:leyline_livingrock', brick=f'{NS}:leyline_livingrock_bricks',
    brick_cracked=f'{NS}:cracked_livingrock',
    floor=f'{NS}:leyline_livingrock_polished', accent=f'{NS}:leyline_livingrock_carved',
    stairs=f'{NS}:leyline_livingrock_stairs', slab=f'{NS}:leyline_livingrock_slab',
    wall=f'{NS}:leyline_livingrock_wall', pillar=f'{NS}:moonstone_livingrock_bricks',
    timber='botania:dreamwood_log', plank='botania:dreamwood_planks',
    fence='botania:dreamwood_fence', light='minecraft:lantern',
    rubble=[f'{NS}:cracked_livingrock', 'minecraft:gravel', f'{NS}:leyline_livingrock'])


def detail_section(piece, seed, name='straight'):
    """Light the pieces `channel_line` never reaches, and let three centuries into all of them.

    The hub is the one piece a player is meant to stand still in -- it is where four arteries
    meet and the only room in the network with floor to spare -- so it carries the denser
    tuning. Everything else is corridor and stays sparse: a maintenance run that is knee-deep
    in its own rubble is not a route.
    """
    kit = sd.Kit(**LEY_KIT)
    grand = (name == 'hub')
    counts = sd.dress(piece, seed, kit, ground=FLOOR + 1, bracket_light=False,
                      sconce=0.80 if grand else 0.55, sconce_spacing=4 if grand else 6,
                      furniture=0.35 if grand else 0.12,
                      furniture_allow=None if grand else ('crate',),
                      floor_litter=0.08 if grand else 0.05)
    counts.update(sd.aftermath(piece, seed, kit, ground=FLOOR + 1, rubble=0.10, reach=1,
                               heap=2, seep='damp', seep_rate=0.07, roots=0.10, hang='drip',
                               roofed_ok=True, webs=0.03))
    return counts


def pools():
    out = {}
    out[os.path.join(POOL, 'section.json')] = {
        'name': f'{NS}:leyline/section', 'fallback': f'{NS}:leyline/terminal',
        'elements': [{'weight': w, 'element': {
            'location': f'{NS}:leyline/{n}', 'processors': 'minecraft:empty',
            'projection': 'rigid', 'element_type': 'minecraft:single_pool_element'}}
            for n, w in SECTION_WEIGHTS]}
    for name in ('hub', 'terminal'):
        out[os.path.join(POOL, name + '.json')] = {
            'name': f'{NS}:leyline/{name}', 'fallback': 'minecraft:empty',
            'elements': [{'weight': 1, 'element': {
                'location': f'{NS}:leyline/{name}', 'processors': 'minecraft:empty',
                'projection': 'rigid', 'element_type': 'minecraft:single_pool_element'}}]}
    return out


def json_files(manifest_biomes):
    out = dict(pools())
    # size 6 of the codec's 0..7: a hub plus five sections of branching. Deeper makes an
    # enormous network that costs generation time everywhere it lands.
    out[os.path.join(DATA, 'worldgen', 'structure', 'leyline_corridors.json')] = {
        'type': 'minecraft:jigsaw', 'biomes': manifest_biomes,
        'step': 'underground_structures', 'terrain_adaptation': 'none',
        'start_pool': f'{NS}:leyline/hub', 'size': 6,
        'max_distance_from_center': 112,
        'start_height': {'type': 'minecraft:uniform',
                         'min_inclusive': {'absolute': -28},
                         'max_inclusive': {'absolute': 6}},
        'use_expansion_hack': False, 'spawn_overrides': {}}
    out[os.path.join(DATA, 'tags', 'worldgen', 'structure', 'leyline_corridors.json')] = {
        'replace': False, 'values': [f'{NS}:leyline_corridors']}
    # Its own grid, deliberately offset from the archaeology salt so the two networks are
    # independent finds rather than always appearing together.
    out[os.path.join(DATA, 'worldgen', 'structure_set', 'leyline_corridors.json')] = {
        'structures': [{'structure': f'{NS}:leyline_corridors', 'weight': 1}],
        'placement': {'type': 'minecraft:random_spread', 'spacing': 40, 'separation': 18,
                      'spread_type': 'linear',
                      'salt': int(hashlib.sha1(b'alfheim:leyline_corridors').hexdigest()[:7], 16)}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    biomes = json.load(open(os.path.join(
        ROOT, 'tools', 'deep_archaeology_manifest.json'), encoding='utf-8'))['biomes']

    bad, total, nodes = 0, 0, 0

    # L1: the dormant node is a block from first_party_mods/alfheim_leyworks. A datapack cannot
    # declare that dependency, so assert it here rather than finding the hole in-world.
    if not glob.glob(os.path.join(ROOT, 'mods', 'alfheim_leyworks-*.jar')):
        print('  L1  no alfheim_leyworks jar in mods/ -- the node palette will not resolve')
        bad += 1

    for name, (builder, size) in sorted(PIECES.items()):
        assert max(size) <= MAX_AXIS, f'{name} exceeds the {MAX_AXIS}-block limit'
        seed = int(hashlib.sha1(f'leyline:{name}'.encode()).hexdigest()[:8], 16)
        piece = builder(tuple(size), seed)
        detail_section(piece, seed, name)
        piece.prune_orphans()
        path = os.path.join(ROOT, STRUCT, name + '.nbt')
        payload = piece.to_nbt()
        if a.check:
            if not os.path.exists(path):
                print(f'  MISSING {name}.nbt')
                bad += 1
            else:
                _, cur = nbt.load(path)
                if json.dumps(cur, default=str) != json.dumps(payload, default=str):
                    print(f'  STALE   {name}.nbt')
                    bad += 1
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            nbt.save(path, '', payload)
        total += len(piece.blocks)
        # blocks maps pos -> (palette index, be), so resolve the index before comparing.
        n = sum(1 for st, _be in piece.blocks.values()
                if piece.palette[st]['Name'] == NODE[0])
        nodes += n
        print(f'  {name:10} {size[0]}x{size[1]}x{size[2]}  {len(piece.blocks):6} blocks'
              f'  {n} node(s)')

    for rel, body in sorted(json_files(biomes).items()):
        text = json.dumps(body, indent=2) + '\n'
        full = os.path.join(ROOT, rel)
        if a.check:
            if not os.path.exists(full) or open(full, encoding='utf-8').read() != text:
                print(f'  STALE   {rel}')
                bad += 1
        else:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)

    if a.check:
        print('PASS: leyline corridors match their generator' if not bad
              else f'!! {bad} stale/missing output(s)')
        return 1 if bad else 0
    print(f'\n  {len(PIECES)} pieces, {total} blocks; 5x5 clear interior in a {W}x{W} envelope')
    print(f'  {nodes} dormant node(s) across the piece set, inert until crafted')
    return 0


if __name__ == '__main__':
    sys.exit(main())
