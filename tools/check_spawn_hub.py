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
            'minecraft:bubble_column', 'minecraft:moving_piston', 'minecraft:piston_head'}

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
        if target and target not in names:
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
                     'greatbole/base')
        for template in templates:
            if f'place template alfheim:{template}' not in assemble_text:
                fail('S10', f'hub/assemble.mcfunction does not explicitly place {template}')
        if 'if entity @e[type=minecraft:marker,tag=alfheim_hub_baked,limit=1] run scoreboard players set #already' not in place_text:
            fail('S10', 'hub/place.mcfunction does not snapshot the baked-anchor guard; retries can duplicate the hub')
        if assemble_text.find('place template alfheim:greatbole/base') < assemble_text.find('place template alfheim:court/amphitheatre'):
            fail('S10', 'the anchor-carrying base is not placed last, so a partial assembly can look committed')
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
