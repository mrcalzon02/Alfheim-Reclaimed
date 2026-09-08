"""Validate the spawn hub: structure NBT, jigsaw wiring, the seated court, and script syntax.

Design: alfheim_reclaimed_design/SPAWN_HUB.md.

Three of these checks exist because of failures this project has already paid for:

  S1  A piece over 48 on any axis cannot be saved or placed. The limit is the reason the tree
      is four pieces, and a pass that grows the trunk is exactly when it would be breached.
  S4  A jigsaw whose `target` no piece answers generates as an orphan -- the base alone, with
      no trunk, no crown and no court, and no error anywhere. Same class as the Hollow Court's
      name-drift problem: silent, and only visible in a world.
  S7  `node --check` over every KubeJS script. A generated apostrophe inside a single-quoted
      string killed 04_spawn_hub.js during pass 1 and was caught by eye. Never again by eye.

    python tools/check_spawn_hub.py
    python tools/check_spawn_hub.py --verbose
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', NS)
STRUCT_DIR = os.path.join(DATA, 'structures')
POOL_DIR = os.path.join(DATA, 'worldgen', 'template_pool')
MAX_AXIS = 48
DATA_VERSION = 3465
SCRIPT_DIRS = [os.path.join('kubejs', d) for d in
               ('server_scripts', 'startup_scripts', 'client_scripts')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    problems = []

    def fail(code, msg):
        problems.append((code, msg))
        print(f'  {code}  {msg}')

    if not os.path.isdir(STRUCT_DIR):
        print('no structures -- nothing to check')
        return 0

    import check_era
    ids, _, _, _ = check_era.scan_jars(verbose=False)
    ids |= {f'{NS}:sealed_gate'}          # ours, registered by KubeJS not by a lang file

    # BLOCKS THAT HAVE NO ITEM FORM. scan_jars() returns the ITEM registry, which is the right
    # ground truth for recipes and the reason lang-derived ids were abandoned -- but a handful
    # of blocks legitimately have no item, so an item-registry lookup reports them missing.
    # minecraft:water is the one that bit: the courtyard fountain is real, placeable, and was
    # flagged as unregistered. Enumerated rather than pattern-matched, so a genuine typo in a
    # block name is still caught.
    ids |= {'minecraft:water', 'minecraft:lava', 'minecraft:air', 'minecraft:cave_air',
            'minecraft:void_air', 'minecraft:fire', 'minecraft:soul_fire',
            'minecraft:nether_portal', 'minecraft:end_portal', 'minecraft:end_gateway',
            'minecraft:bubble_column', 'minecraft:moving_piston', 'minecraft:piston_head',
            'minecraft:wheat', 'minecraft:carrots', 'minecraft:potatoes', 'minecraft:beetroots',
            'minecraft:nether_wart', 'minecraft:cocoa', 'minecraft:sweet_berry_bush',
            'minecraft:pumpkin_stem', 'minecraft:melon_stem',
            'minecraft:potted_fern', 'minecraft:potted_dandelion',
            'minecraft:potted_poppy', 'minecraft:potted_blue_orchid',
            'minecraft:potted_allium'}

    # ---- S1/S2/S3: the pieces ------------------------------------------------------------
    pieces, jigsaws = {}, []
    paths = sorted(glob.glob(os.path.join(STRUCT_DIR, '**', '*.nbt'), recursive=True))
    for p in paths:
        key = os.path.relpath(p, STRUCT_DIR).replace(os.sep, '/')[:-4]
        try:
            _, root = nbt.load(p)
        except Exception as e:
            fail('S1', f'{key}: will not load -- {e}')
            continue
        size = [int(v) for v in root['size']]
        pieces[key] = root

        for axis, n in zip('xyz', size):
            if n > MAX_AXIS:
                fail('S1', f'{key}: {axis}={n} exceeds the {MAX_AXIS}-block structure limit, '
                           'so it cannot be saved or placed')
        if int(root['DataVersion']) != DATA_VERSION:
            fail('S1', f'{key}: DataVersion {int(root["DataVersion"])}, expected '
                       f'{DATA_VERSION} for 1.20.1')

        pal = [e['Name'] for e in root['palette']]
        for block in root['blocks']:
            pos = [int(v) for v in block['pos']]
            if any(v < 0 or v >= size[i] for i, v in enumerate(pos)):
                fail('S1', f'{key}: block position {pos} lies outside declared size {size}')
        for name in sorted(set(pal)):
            if name in ('minecraft:jigsaw', 'minecraft:air'):
                continue
            if name not in ids:
                fail('S2', f'{key}: palette block "{name}" is not registered by any jar or '
                           'by our own scripts')

        for b in root['blocks']:
            be = b.get('nbt')
            if be and be.get('id') == 'minecraft:jigsaw':
                # A connector's facing lives in the BLOCK STATE, not the block entity: the
                # entity carries name/target/pool/joint/final_state and nothing else, while
                # `orientation` is a blockstate property of minecraft:jigsaw. S9 needs it to
                # tell a VERTICAL connector (which extends the tree's height) from the
                # horizontal one reaching out to the court, so lift it into `be` here rather
                # than re-reading the palette at the point of use.
                props = root['palette'][int(b['state'])].get('Properties', {})
                be = dict(be)
                be['orientation'] = str(props.get('orientation', ''))
                jigsaws.append((key, [int(v) for v in b['pos']], be))

        if a.verbose:
            print(f'  --   {key:22} {size[0]}x{size[1]}x{size[2]}  {len(root["blocks"]):>6} blocks'
                  f'  {len(root.get("entities", []))} entities')

    greatbole_palette = {entry['Name'] for key, root in pieces.items()
                         if key.startswith('greatbole/') for entry in root['palette']}
    if {'minecraft:oak_log', 'minecraft:oak_wood', 'minecraft:oak_leaves'} & greatbole_palette:
        fail('S2', 'Greatbole still contains vanilla oak material')
    if not {'alfheim:gloambark_log', 'alfheim:hushbark_log',
            'alfheim:gloambark_leaves'} <= greatbole_palette:
        fail('S2', 'Greatbole is missing its custom Elder-wood material family')

    # ---- S12: court expansions must be authored rooms with their own terrain beard -------
    # The first expansion pass technically placed three 48x48 pieces, but all three were the
    # same sparse four-platform layout on a shallow square slab. In a cliff-side runtime world
    # that read as a floating plate on the low side and solid hillside on the high side. These
    # checks make the detail pass measurable: deep support, excavated occupiable volume, clear
    # ceremonial circulation and a distinct furnishing vocabulary for each wing.
    annex_specs = {
        'court/west_residence': {
            'required': {'alfheim:royal_canopy_bed_head_left',
                         'alfheim:royal_highback_chair', 'minecraft:bookshelf'},
            'forbidden': {'minecraft:smoker', 'alfheim:royal_astrolabe_nw'},
            'axis': 'x',
        },
        'court/east_service': {
            'required': {'minecraft:smoker', 'minecraft:cauldron', 'minecraft:barrel',
                         'minecraft:brewing_stand'},
            'forbidden': {'alfheim:royal_canopy_bed_head_left', 'alfheim:royal_astrolabe_nw'},
            'axis': 'x',
        },
        'court/north_council': {
            'required': {'alfheim:royal_astrolabe_nw', 'alfheim:royal_highback_chair',
                         'minecraft:lectern'},
            'forbidden': {'minecraft:smoker', 'alfheim:royal_canopy_bed_head_left'},
            'axis': 'z',
        },
    }
    for key, spec in annex_specs.items():
        root = pieces.get(key)
        if root is None:
            fail('S12', f'{key}: missing court expansion template')
            continue
        palette = [entry['Name'] for entry in root['palette']]
        names = set(palette)
        states = {tuple(int(v) for v in b['pos']): palette[int(b['state'])]
                  for b in root['blocks']}
        counts = {}
        for name in states.values():
            counts[name] = counts.get(name, 0) + 1

        if len(root['blocks']) < 8500 or len(root['palette']) < 28:
            fail('S12', f'{key}: only {len(root["blocks"])} blocks / '
                         f'{len(root["palette"])} palette states; high-detail floor is 8500 / 28')
        missing = spec['required'] - names
        if missing:
            fail('S12', f'{key}: missing role-defining detail {", ".join(sorted(missing))}')
        leaked = spec['forbidden'] & names
        if leaked:
            fail('S12', f'{key}: contains another wing\'s role vocabulary '
                         f'{", ".join(sorted(leaked))}')

        bottom = {pos for pos, name in states.items() if pos[1] == 0 and name != 'minecraft:air'}
        side_counts = {
            'west': sum(1 for x, _y, z in bottom if x <= 2 and 7 <= z <= 40),
            'east': sum(1 for x, _y, z in bottom if x >= 45 and 7 <= z <= 40),
            'north': sum(1 for x, _y, z in bottom if z <= 2 and 7 <= x <= 40),
            'south': sum(1 for x, _y, z in bottom if z >= 45 and 7 <= x <= 40),
        }
        if len(bottom) < 300 or min(side_counts.values()) < 20:
            fail('S12', f'{key}: terrain beard is too shallow/sparse '
                         f'({len(bottom)} bottom supports; sides {side_counts})')

        royal_count = sum(n for name, n in counts.items() if name.startswith('alfheim:royal_'))
        if royal_count < 55:
            fail('S12', f'{key}: only {royal_count} Royal Tile Set blocks; expected at least 55')

        if spec['axis'] == 'x':
            route = ((x, y, z) for x in range(48) for z in range(21, 28)
                     for y in range(7, 11))
            floor = ((x, 5, 24) for x in range(48))
        else:
            route = ((x, y, z) for z in range(48) for x in range(21, 28)
                     for y in range(7, 11))
            floor = ((24, 5, z) for z in range(48))
        blocked = [pos for pos in route if states.get(pos) != 'minecraft:air']
        unsupported = [pos for pos in floor if states.get(pos) in (None, 'minecraft:air')]
        if blocked:
            fail('S12', f'{key}: {len(blocked)} upper route cells are not explicitly clear')
        if unsupported:
            fail('S12', f'{key}: {len(unsupported)} processional floor cells lack support')
        if a.verbose:
            print(f'  --   {key:22} detail={len(root["blocks"])} palette={len(root["palette"])} '
                  f'royal={royal_count} beard={len(bottom)} sides={side_counts}')

    # ---- S3: pools a jigsaw points at must exist -----------------------------------------
    pools = {}
    for p in sorted(glob.glob(os.path.join(POOL_DIR, '**', '*.json'), recursive=True)):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            fail('S3', f'{os.path.relpath(p)}: will not parse -- {e}')
            continue
        pools[d.get('name', '')] = d

    for key, pos, be in jigsaws:
        pool = be.get('pool')
        if pool == 'minecraft:empty':
            continue
        if pool not in pools:
            fail('S3', f'{key} @{pos}: jigsaw points at pool "{pool}", which has no '
                       f'template_pool file')

    # every pool element must name a piece that exists
    for pname, d in pools.items():
        for el in d.get('elements', []):
            loc = el.get('element', {}).get('location', '')
            k = loc.split(':', 1)[1] if ':' in loc else loc
            if k not in pieces:
                fail('S3', f'pool "{pname}" lists element "{loc}", which has no .nbt')

    # ---- S4: every target must be answered -----------------------------------------------
    names = {be.get('name') for _, _, be in jigsaws}
    for key, pos, be in jigsaws:
        target = be.get('target')
        if target and target != 'minecraft:empty' and target not in names:
            fail('S4', f'{key} @{pos}: jigsaw targets "{target}", which no piece declares as a '
                       'jigsaw name -- that branch generates as an orphan')
        if a.verbose:
            print(f'  --   jigsaw {key:20} {be.get("name"):24} -> {target:24} '
                  f'pool={be.get("pool")}')

    # ---- S5: structure and placement ------------------------------------------------------
    sp = os.path.join(DATA, 'worldgen', 'structure', 'greatbole.json')
    if not os.path.exists(sp):
        fail('S5', 'no worldgen/structure/greatbole.json, so nothing generates')
    else:
        st = json.load(open(sp, encoding='utf-8'))
        start = st.get('start_pool', '')
        if start not in pools:
            fail('S5', f'structure start_pool "{start}" has no template_pool file')
        mdc = st.get('max_distance_from_center', 0)
        if not 1 <= mdc <= 128:
            fail('S5', f'max_distance_from_center {mdc} is outside the vanilla 1..128 range')

        # The usable budget is NOT 128. JigsawStructure's codec validates
        #     max_distance_from_center + margin <= 128
        # where margin is 0 for terrain_adaptation `none` and 12 for every other value. Getting
        # this wrong does not degrade quietly -- world creation aborts with
        #     Structure size including terrain adaptation must not exceed 128
        # which is how it was found, after a run that never reached the main menu.
        ADAPTATION_MARGIN = {'none': 0, 'bury': 12, 'beard_thin': 12, 'beard_box': 12,
                             'encapsulate': 12}
        adapt = st.get('terrain_adaptation', 'none')
        margin = ADAPTATION_MARGIN.get(adapt, 12)
        budget = 128 - margin
        if mdc > budget:
            fail('S5', f'max_distance_from_center {mdc} with terrain_adaptation "{adapt}" '
                       f'(margin {margin}) exceeds the vanilla budget of {budget} -- the world '
                       'will refuse to load with "Structure size including terrain adaptation '
                       'must not exceed 128"')

        # ---- S9: the assembled tree must fit inside max_distance_from_center -------------
        #
        # WHY THIS EXISTS. The canopy did not generate, and nothing caught it: every piece was
        # individually legal, the pools paired, and the structure loaded without error. The
        # crown was simply CULLED at placement, because jigsaw rejects any piece landing
        # further than max_distance_from_center from the structure start -- and the tree was
        # 184 blocks tall against a cap of 116.
        #
        # SPAWN_HUB.md asserted the tree "spans +-96, inside the cap". It does not: a tree
        # grows UPWARD from its base, so its span is its full height, not half of it. That
        # single wrong sentence is what shipped the bug, which is exactly why the check is
        # here and not in the prose.
        #
        # Walks the pool graph upward from start_pool rather than trusting a constant, so it
        # measures what the data actually says.
        def tallest(pool_name, depth):
            """Tallest assembly rooted at this pool, in blocks."""
            if depth <= 0 or pool_name not in pools:
                return 0
            best = 0
            for el in pools[pool_name].get('elements', []):
                loc = el.get('element', {}).get('location', '')
                key = loc.split(':', 1)[1] if ':' in loc else loc
                piece = pieces.get(key)
                if piece is None:
                    continue
                h = int(piece['size'][1])
                up = 0
                for k, _pos, be in jigsaws:
                    if k != key:
                        continue
                    # Only vertical connectors extend the tree's HEIGHT. The court jigsaw is
                    # horizontal and must not be counted, or the check reads 48 blocks and
                    # passes a tree that does not fit.
                    if not str(be.get('orientation', '')).startswith('up_'):
                        continue
                    nxt = be.get('pool', '')
                    if nxt and nxt != 'minecraft:empty':
                        up = max(up, tallest(nxt, depth - 1))
                best = max(best, h + up)
            return best

        height = tallest(start, int(st.get('size', 6)))
        if height > min(mdc, budget):
            fail('S9', f'the assembled tree is {height} blocks tall but '
                       f'max_distance_from_center is {mdc}, so jigsaw will CULL every piece '
                       f'above {mdc} blocks -- the canopy will not generate. Either shorten '
                       f'the tree or raise the cap (vanilla allows at most 128).')
        elif a.verbose:
            print(f'  --   assembled tree {height} blocks tall, cap {mdc} '
                  f'(budget {budget} after the "{adapt}" margin of {margin})')

    # ---- S10: explicit placement must be unique and valid across the layer -----------------
    # New World Gamma proved that passive concentric-ring placement could leave the hub absent
    # forever. hub/place now selects legal ground and assembles the four templates directly;
    # a natural structure set would therefore be a duplicate source. The complete biome tag is
    # retained for the operator-facing structure definition and must not silently reject a site.
    tag_p = os.path.join(DATA, 'tags', 'worldgen', 'biome', 'has_greatbole.json')
    layer_p = os.path.join('kubejs', 'data', 'mythicbotany', 'libx', 'biome_layer',
                           'alfheim.json')
    if os.path.exists(tag_p) and os.path.exists(layer_p):
        tagged = set(json.load(open(tag_p, encoding='utf-8')).get('values', []))

        layer = set()

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == 'biome' and isinstance(v, str):
                        layer.add(v)
                    else:
                        walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(json.load(open(layer_p, encoding='utf-8')))

        missing = layer - tagged
        if missing:
            fail('S10', f'#alfheim:has_greatbole omits {len(missing)} biome(s) that exist in '
                        f'the Alfheim layer ({", ".join(sorted(missing))}). The safe-ground '
                        'probe may land in any layer biome, so this would reject an otherwise '
                        'valid explicit placement.')
        natural = os.path.join(DATA, 'worldgen', 'structure_set', 'greatbole.json')
        if os.path.exists(natural):
            fail('S10', 'worldgen/structure_set/greatbole.json still exists; explicit hub '
                        'placement and natural placement can create two Greatboles')
        place_p = os.path.join(DATA, 'functions', 'hub', 'place.mcfunction')
        place_text = open(place_p, encoding='utf-8').read() if os.path.exists(place_p) else ''
        assemble_p = os.path.join(DATA, 'functions', 'hub', 'assemble.mcfunction')
        assemble_text = (open(assemble_p, encoding='utf-8').read()
                         if os.path.exists(assemble_p) else '')
        templates = ('greatbole/trunk', 'greatbole/crown', 'court/amphitheatre',
                     'court/west_residence', 'court/east_service', 'court/north_council',
                     'greatbole/base')
        for template in templates:
            if f'place template alfheim:{template}' not in assemble_text:
                fail('S10', f'hub/assemble.mcfunction does not explicitly place {template}')
        for template, offset in (('west_residence', '~-72 ~-5 ~-72'),
                                 ('east_service', '~24 ~-5 ~-72'),
                                 ('north_council', '~-24 ~-5 ~-120')):
            if f'place template alfheim:court/{template} {offset}' not in assemble_text:
                fail('S12', f'court/{template} is not placed at its five-course beard datum '
                            f'({offset})')
        if 'if entity @e[type=minecraft:marker,tag=alfheim_hub_baked,limit=1] run scoreboard players set #already' not in place_text:
            fail('S10', 'hub/place.mcfunction does not snapshot the baked-anchor guard; retries can duplicate the hub')
        if assemble_text.find('place template alfheim:greatbole/base') < assemble_text.find('place template alfheim:court/amphitheatre'):
            fail('S10', 'the anchor-carrying base is not placed last, so a partial assembly can look committed')
        if 'candidate 0 0' not in place_text or 'candidate 192 0' in place_text:
            fail('S10', 'hub/place.mcfunction does not use the world origin as its sole X/Z candidate')
        if 'positioned over motion_blocking_no_leaves' not in place_text:
            fail('S10', 'hub placement does not vertically adapt the origin complex to terrain')
        if a.verbose:
            print(f'  --   explicit Greatbole placement: {len(tagged)} of {len(layer)} '
                  'layer biome(s), natural duplicate source absent')

    # ---- S6: the seated court must match the quest links ---------------------------------
    links_p = os.path.join('kubejs', 'data', 'quest_giver', 'quest_line_links.json')
    amph = pieces.get('court/amphitheatre')
    if amph is not None and os.path.exists(links_p):
        seated = set()
        for e in amph.get('entities', []):
            try:
                seated.add(json.loads(e['nbt']['CustomName'])['text'])
                if 'alfheim_hub_court' not in e['nbt'].get('Tags', []):
                    fail('S6', f'{json.loads(e["nbt"]["CustomName"])["text"]} lacks the '
                               'alfheim_hub_court tag used by runtime acceptance')
            except Exception:
                fail('S6', 'an amphitheatre entity has an unreadable CustomName')
        for lk in json.load(open(links_p, encoding='utf-8')):
            if lk.get('name') not in seated:
                fail('S6', f'"{lk.get("name")}" is bound to quest line '
                           f'"{lk.get("quest_line_id")}" but is not seated in the amphitheatre '
                           '-- that quest giver does not exist where the hub is')
        if a.verbose:
            print(f'  --   {len(seated)} court members seated in the amphitheatre')

    # ---- S7: every KubeJS script must parse ----------------------------------------------
    scripts = [f for d in SCRIPT_DIRS for f in sorted(glob.glob(os.path.join(d, '*.js')))]
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        bad = 0
        for f in scripts:
            r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
            if r.returncode != 0:
                first = (r.stderr or '').strip().splitlines()
                fail('S7', f'{f}: does not parse -- {first[1] if len(first) > 1 else first[:1]}')
                bad += 1
        print(f'  --   {len(scripts)} KubeJS script(s) parsed, {bad} syntax error(s)')
    except Exception:
        print('  --   node not available; KubeJS syntax unchecked (S7 skipped)')

    # ---- S11: protection generator closure and real FTB ownership read-back --------------
    import gen_spawn_hub
    protection_path = os.path.join('kubejs', 'server_scripts', '04_spawn_hub.js')
    protection = open(protection_path, encoding='utf-8').read()
    if protection != gen_spawn_hub.protection_script():
        fail('S11', '04_spawn_hub.js differs from the authoritative protection template')
    for token in ('new $ChunkDimPos(hubLevelKey, chunkX, chunkZ)',
                  'chunkData.claim(source, claimPosition, false)',
                  'claimedChunkManager.getChunk(claimPosition)',
                  'chunkData.saveNow()', 'chunkData.syncChunksToAll(server)'):
        if token not in protection:
            fail('S11', f'claim implementation is missing {token!r}')
    if 'ftbchunks admin claim_as' in protection:
        fail('S11', 'obsolete command-only FTB claim path returned')

    # ---- S8: KubeJS scripts share one scope per directory -------------------------------
    #
    # Runtime-proven 2026-09-04: three server scripts each declared `const HOME_DIMENSION`, and
    # KubeJS evaluates every script in a directory in ONE shared scope, so the later ones throw
    #   TypeError: redeclaration of const HOME_DIMENSION
    # and fail to load.
    #
    # S7's `node --check` cannot see this by construction -- each file parses perfectly on its
    # own, and the collision only exists once they are loaded together. It took a dedicated
    # server to find, which is the whole argument for having one.
    counts = {}
    for d in ('server_scripts', 'startup_scripts', 'client_scripts'):
        seen = {}
        for f in sorted(glob.glob(os.path.join('kubejs', d, '*.js'))):
            txt = open(f, encoding='utf-8').read()
            for m in re.finditer(r'^(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)', txt, re.M):
                seen.setdefault(m.group(1), []).append(os.path.basename(f))
        for name, files in sorted(seen.items()):
            if len(files) > 1:
                fail('S8', f'{d}: "{name}" is declared at top level in {len(files)} scripts '
                           f'({", ".join(files)}) -- KubeJS shares one scope per directory, so '
                           'the later ones throw redeclaration and never load')
        counts[d] = len(seen)
    if a.verbose:
        print('  --   top-level names: '
              + ', '.join(f'{k} {v}' for k, v in counts.items()))

    # ---- S9/S10/S11: the assembled complex ------------------------------------------------
    # Added 2026-09-07 after a field session found three faults that every existing check
    # passed over: the civic wings dead-ended against the amphitheatre's intact outer seating,
    # dressing hung in mid-air above the carved routes, and the FTB claim covered 289 chunks
    # around a 144-by-144 build. All three are geometry a reader cannot hold in their head, so
    # they are asserted here rather than re-inspected by eye.
    assemble = os.path.join(DATA, 'functions', 'hub', 'assemble.mcfunction')
    placed = {}
    if os.path.exists(assemble):
        for m in re.finditer(r'place template (\w+):([\w/]+) ~(-?\d+) ~(-?\d+) ~(-?\d+)',
                             open(assemble, encoding='utf-8').read()):
            placed[m.group(2)] = (int(m.group(3)), int(m.group(4)), int(m.group(5)))

    def world_box(key):
        """The XZ footprint one placed piece occupies, in world blocks, inclusive."""
        ox, _oy, oz = placed[key]
        sx, _sy, sz = [int(v) for v in pieces[key]['size']]
        return ox, ox + sx - 1, oz, oz + sz - 1

    missing = [k for k in placed if k not in pieces]
    for k in missing:
        fail('S9', f'assemble.mcfunction places {k}, which has no NBT')

    if placed and not missing:
        # S9: the claim envelope must contain every placed piece, chunk-snapped and no larger.
        import gen_spawn_hub
        boxes = [world_box(k) for k in placed]
        lo_x, hi_x = min(b[0] for b in boxes), max(b[1] for b in boxes)
        lo_z, hi_z = min(b[2] for b in boxes), max(b[3] for b in boxes)
        want = ((lo_x >> 4) * 16, ((hi_x >> 4) + 1) * 16 - 1,
                (lo_z >> 4) * 16, ((hi_z >> 4) + 1) * 16 - 1)
        got = (gen_spawn_hub.HUB_MIN_X, gen_spawn_hub.HUB_MAX_X,
               gen_spawn_hub.HUB_MIN_Z, gen_spawn_hub.HUB_MAX_Z)
        if got != want:
            fail('S9', f'claim envelope {got} does not chunk-snap the built footprint '
                       f'X {lo_x}..{hi_x} Z {lo_z}..{hi_z}; expected {want}')
        elif a.verbose:
            chunks = ((want[1] - want[0] + 1) // 16) * ((want[3] - want[2] + 1) // 16)
            print(f'  --   claim {want[0]}..{want[1]} x {want[2]}..{want[3]} = {chunks} chunks')

        # S10: every wing spine must open into the court.
        #
        # The four court pieces are 48 wide and tile flush, so a wing's clear spine and the
        # amphitheatre's matching approach occupy the same cross span in each piece's own local
        # coordinates: centre +/- AISLE_HALF. The amphitheatre's paving sits at world Y == the
        # surface datum, which is its own local y == -placement_y; the walkable column is the
        # five blocks above that. If any of it is solid the wing dead-ends.
        amph = pieces.get('court/amphitheatre')
        if amph is not None and 'court/amphitheatre' in placed:
            pal = [e['Name'] for e in amph['palette']]
            grid = {tuple(int(v) for v in b['pos']): pal[b['state']] for b in amph['blocks']}
            width = int(amph['size'][0])
            centre = width // 2
            floor_y = -placed['court/amphitheatre'][1]      # local y of the walking surface
            half = gen_spawn_hub.AISLE_HALF
            span = range(centre - half, centre + half + 1)
            seams = {                                       # wing -> (axis, local seam index)
                'court/west_residence': ('x', 0),
                'court/east_service': ('x', width - 1),
                'court/north_council': ('z', 0),
            }
            for wing, (axis, seam) in seams.items():
                if wing not in placed:
                    continue
                blocked = []
                for cross in span:
                    lx, lz = (seam, cross) if axis == 'x' else (cross, seam)
                    for ly in range(floor_y + 1, floor_y + 6):
                        b = grid.get((lx, ly, lz))
                        if b is not None and b != 'minecraft:air':
                            blocked.append((lx, ly, lz, b))
                if blocked:
                    fail('S10', f'court/amphitheatre does not open to {wing}: '
                                f'{len(blocked)} solid block(s) in the seam column, '
                                f'first {blocked[0]}')
                elif a.verbose:
                    print(f'  --   seam to {wing} is clear')

        # S11: no block may be wholly unattached.
        #
        # Deliberately the weakest defensible form of this test. A first pass demanded solid
        # support directly below and flagged 36 pieces -- but inspection showed most were
        # corbels hanging under an overhang, and stepped debris joined only on a diagonal.
        # Both are authored ruin geometry, and this project builds ruins on purpose. What is
        # never intentional is a block touching nothing at all on any of its six faces: that is
        # always a scatter loop placing at a computed height that its own terrain never
        # reached. Support-below is asserted where the datum is known, by S12.
        NEIGHBOURS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
        for key, root in sorted(pieces.items()):
            pal = [e['Name'] for e in root['palette']]
            grid = {tuple(int(v) for v in b['pos']): pal[b['state']] for b in root['blocks']}
            size = [int(v) for v in root['size']]
            floating = []
            for (x, y, z), name in grid.items():
                if name in ('minecraft:air', 'minecraft:jigsaw', 'minecraft:vine'):
                    continue
                attached = False
                for dx, dy, dz in NEIGHBOURS:
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if not (0 <= nx < size[0] and 0 <= ny < size[1] and 0 <= nz < size[2]):
                        attached = True       # the piece boundary; the world continues there
                        break
                    nb = grid.get((nx, ny, nz))
                    if nb is None or nb != 'minecraft:air':
                        # `None` means the piece does not own the cell, so natural terrain
                        # survives there and the block is resting against it.
                        attached = True
                        break
                if not attached:
                    floating.append((x, y, z, name))
            if floating:
                fail('S11', f'{key}: {len(floating)} block(s) touch nothing on any face, '
                            f'first {floating[0]}')

        # S12: loose dressing in the court pieces must have something under it. These are the
        # pieces whose vertical datum is fixed by assemble.mcfunction, so "below" is decidable.
        SCATTER = ('carpet', 'cobblestone', 'moss_block', 'rubble', 'gravel')
        for key in sorted(k for k in pieces if k.startswith('court/')):
            root = pieces[key]
            pal = [e['Name'] for e in root['palette']]
            grid = {tuple(int(v) for v in b['pos']): pal[b['state']] for b in root['blocks']}
            floor_y = -placed[key][1] if key in placed else 0
            unsupported = []
            for (x, y, z), name in grid.items():
                if y <= floor_y or not any(s in name for s in SCATTER):
                    continue
                below = grid.get((x, y - 1, z))
                if below is None or below == 'minecraft:air':
                    unsupported.append((x, y, z, name))
            if unsupported:
                fail('S12', f'{key}: {len(unsupported)} loose dressing block(s) sit above the '
                            f'floor datum with nothing beneath, first {unsupported[0]}')

    print(f'\npieces: {len(pieces)}   jigsaws: {len(jigsaws)}   pools: {len(pools)}')
    print('=' * 68)
    if problems:
        by = {}
        for code, _ in problems:
            by[code] = by.get(code, 0) + 1
        print('problems by check: ' + ', '.join(f'{k}={v}' for k, v in sorted(by.items())))
    print(f'RESULT: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
