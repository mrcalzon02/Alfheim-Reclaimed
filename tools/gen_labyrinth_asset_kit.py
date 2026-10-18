"""Author the staged Ashen Cloister kit through Continuity Works' provider API.

No runtime resources, registrations, existing worlds or JARs are changed.
"""
from __future__ import annotations

import argparse
from collections import deque
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys

import nbt
from structure_nbt import Piece

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'alfheim_reclaimed_design/monastery_labyrinth/asset_batch_01'
SEED = 2026101801
ROOMS = {
    'monastery_vestibule': 'Processional thresholds, memorial benches and paired oath tablets',
    'ruined_nave': 'Facing pews, broken side chapels and a choir apse',
    'bone_cloister': 'Corner colonnades around an unobstructed processional crossing',
    'novices_cells': 'Four small sleeping cells with screened beds and personal shelves',
    'ossuary': 'Supported bone shelves and recessed stone burial drawers',
    'spider_gallery': 'Ceiling web bays and marked ambush alcoves clear of the main route',
    'bell_chamber': 'Wall-supported bell frames with suspended bronze-colored bells',
    'scriptorium': 'Writing desks, reading benches and protected manuscript shelves',
    'reliquary': 'Stone display plinths with glass reliquary cases; no free progression loot',
    'cistern': 'Four sealed shallow basins around dry service walkways',
    'refectory': 'Paired long tables and benches in the corner bays',
    'grave_gallery': 'Raised sarcophagi and inscribed memorial markers',
    'ritual_chapel': 'Four small ritual dais bays and supported light niches',
    'descent_hub': 'Clear central circulation with four marked checkpoint alcoves',
    'elite_arena': 'Open combat floor with perimeter cover and four readable exits',
    'boss_sanctuary': 'Open arena with choir monuments outside the combat crossing',
    'return_shrine': 'Inactive return-arch sculpture; no working portal claimed',
    'switchback_stair': 'Two real six-step flights with a landing; twelve-block rise',
}
SERVICES = {
    'arms_refuge': 'Weapon and armor display racks',
    'provisions_refuge': 'Food preparation counters and sealed storage',
    'apothecary_refuge': 'Bottle-shaped display vessels and an herb shelf',
    'repair_refuge': 'Repair bench and spare-part storage',
    'salvage_refuge': 'Sorting bins and weighing counter',
    'waykeeper_refuge': 'Quest desk and inactive return-arch sculpture',
}
CONDITION = ('kept', 'weathered', 'ruined')
CONNECTORS = {'connector_straight': 'Five-wide passage spanning the inclusive 29-block gap on the native 56-block pitch'}


def B(name, **props):
    return ('minecraft:' + name, {k: str(v).lower() for k, v in props.items()} or None)


AIR, STONE, FLOOR, TRIM, WOOD = map(B, ('air', 'stone_bricks', 'polished_andesite', 'chiseled_stone_bricks', 'spruce_planks'))


def box(p, a, b, block):
    for x in range(a[0], b[0] + 1):
        for y in range(a[1], b[1] + 1):
            for z in range(a[2], b[2] + 1):
                assert p.set(x, y, z, block), (p.size, x, y, z)


def arch(p, x, z, width=7, y=2):
    for xx in (x, x + width - 1):
        box(p, (xx, y, z), (xx, y + 5, z), TRIM)
    box(p, (x + 1, y + 5, z), (x + width - 2, y + 5, z), STONE)
    p.set(x + 1, y + 4, z, B('stone_brick_stairs', facing='east', half='top', shape='straight', waterlogged=False))
    p.set(x + width - 2, y + 4, z, B('stone_brick_stairs', facing='west', half='top', shape='straight', waterlogged=False))


def plinth(p, x, z, h=2):
    box(p, (x, 2, z), (x + 3, h + 1, z + 3), STONE)
    box(p, (x, h + 2, z), (x + 3, h + 2, z + 3), TRIM)


def table(p, x, z, length=7):
    for zz in (z, z + length - 1):
        for xx in (x, x + 2):
            p.set(xx, 2, zz, WOOD)
    box(p, (x, 3, z), (x + 2, 3, z + length - 1), B('spruce_slab', type='top', waterlogged=False))
    for xx in (x - 2, x + 4):
        for zz in range(z, z + length):
            p.set(xx, 2, zz, B('spruce_slab', type='bottom', waterlogged=False))


def shell(height=15):
    p = Piece(29, height, 29)
    box(p, (0, 0, 0), (28, height - 1, 28), AIR)
    box(p, (0, 0, 0), (28, 1, 28), FLOOR)
    for x in (0, 1, 27, 28):
        box(p, (x, 2, 0), (x, height - 1, 28), STONE)
    for z in (0, 1, 27, 28):
        box(p, (0, 2, z), (28, height - 1, z), STONE)
    box(p, (0, height - 1, 0), (28, height - 1, 28), STONE)
    # Supported pilasters, springing courses and roof ribs, not loose scatter.
    for x in (3, 9, 19, 25):
        for z in (2, 26):
            box(p, (x, 2, z), (x, 11, z), TRIM)
            box(p, (x, 12, 2), (x, 13, 26), STONE)
    for z in (3, 9, 19, 25):
        for x in (2, 26):
            box(p, (x, 2, z), (x, 11, z), TRIM)
    for x in (5, 23):
        for z in (2, 26):
            p.set(x, 7, z, B('sea_lantern'))
    # Original floor datum matches MonasteryLabyrinthPiece: floors 0/1, feet 2.
    for x in range(2, 27):
        for z in range(2, 27):
            if x in (11, 17) or z in (11, 17):
                p.set(x, 1, z, TRIM)
    return p


def furnish(p, family):
    for x in (4, 20):
        for z in (4, 20):
            if family in ('monastery_vestibule', 'descent_hub'):
                plinth(p, x, z, 1)
                box(p, (x + 1, 4, z + 1), (x + 2, 6, z + 1), TRIM)
            elif family in ('ruined_nave', 'bone_cloister'):
                if family == 'ruined_nave':
                    for zz in (z, z + 3):
                        box(p, (x, 2, zz), (x + 5, 2, zz), WOOD)
                        box(p, (x, 3, zz + 1), (x + 5, 3, zz + 1), WOOD)
                else:
                    arch(p, x, z)
                    arch(p, x, z + 4)
            elif family == 'novices_cells':
                box(p, (x, 2, z), (x + 5, 6, z), STONE)
                box(p, (x, 2, z), (x, 6, z + 5), STONE)
                box(p, (x + 1, 2, z + 1), (x + 2, 2, z + 4), WOOD)
                box(p, (x + 1, 3, z + 1), (x + 2, 3, z + 3), B('gray_carpet'))
                box(p, (x + 4, 2, z + 1), (x + 4, 4, z + 1), B('bookshelf'))
            elif family == 'ossuary':
                for yy in (2, 5, 8):
                    box(p, (x, yy, z), (x + 5, yy, z + 2), STONE)
                    for xx in (x, x + 5):
                        box(p, (xx, yy + 1, z), (xx, yy + 2, z + 2), STONE)
                    box(p, (x + 1, yy + 1, z + 1), (x + 4, yy + 1, z + 1), B('bone_block', axis='x'))
            elif family == 'spider_gallery':
                arch(p, x, z)
                box(p, (x, 9, z), (x + 5, 9, z + 5), WOOD)
                for xx in (x, x + 2, x + 4):
                    box(p, (xx, 10, z), (xx, 13, z + 3), B('cobweb'))
            elif family == 'bell_chamber':
                arch(p, x, z)
                box(p, (x + 1, 8, z), (x + 4, 8, z), WOOD)
                box(p, (x + 2, 6, z), (x + 2, 7, z), B('chain', axis='y', waterlogged=False))
                box(p, (x + 1, 5, z), (x + 3, 5, z + 2), B('cut_copper'))
                p.set(x + 2, 6, z + 1, B('cut_copper'))
            elif family == 'scriptorium':
                table(p, x + 1, z, 5)
                box(p, (x, 2, z + 6), (x + 5, 5, z + 6), B('bookshelf'))
            elif family == 'reliquary':
                plinth(p, x, z)
                box(p, (x + 1, 5, z + 1), (x + 2, 6, z + 2), B('glass'))
                box(p, (x, 7, z), (x + 3, 7, z + 3), TRIM)
            elif family == 'cistern':
                box(p, (x - 1, 2, z - 1), (x + 5, 2, z + 5), STONE)
                box(p, (x, 2, z), (x + 4, 2, z + 4), B('water', level=0))
            elif family == 'refectory':
                table(p, x + 1, z)
            elif family == 'grave_gallery':
                plinth(p, x, z, 1)
                box(p, (x + 1, 4, z), (x + 2, 4, z + 5), B('smooth_stone_slab', type='bottom', waterlogged=False))
                box(p, (x + 1, 2, z + 4), (x + 2, 3, z + 5), STONE)
                box(p, (x + 1, 4, z + 5), (x + 2, 6, z + 5), TRIM)
            elif family in ('ritual_chapel', 'boss_sanctuary'):
                plinth(p, x, z, 1)
                for xx in (x, x + 3):
                    box(p, (xx, 4, z), (xx, 8 if family == 'boss_sanctuary' else 5, z), B('bone_block', axis='y'))
                box(p, (x, 9 if family == 'boss_sanctuary' else 6, z), (x + 3, 9 if family == 'boss_sanctuary' else 6, z), TRIM)
            elif family == 'elite_arena':
                box(p, (x, 2, z), (x + 3, 4, z + 2), STONE)
                box(p, (x, 5, z), (x + 3, 5, z + 2), TRIM)
            elif family == 'return_shrine':
                arch(p, x, z, 7)
                box(p, (x, 2, z), (x + 6, 2, z + 1), TRIM)
            elif family in SERVICES:
                table(p, x + 1, z, 5)
                if family == 'arms_refuge':
                    for xx in (x, x + 3):
                        box(p, (xx, 2, z + 6), (xx, 6, z + 6), WOOD)
                        p.set(xx, 7, z + 6, B('polished_andesite'))
                elif family == 'provisions_refuge':
                    box(p, (x, 2, z + 6), (x + 4, 3, z + 6), B('hay_block', axis='y'))
                elif family == 'apothecary_refuge':
                    for xx in (x, x + 2, x + 4):
                        box(p, (xx, 2, z + 6), (xx, 3, z + 6), B('green_stained_glass'))
                elif family == 'repair_refuge':
                    box(p, (x, 2, z + 6), (x + 4, 3, z + 6), B('polished_andesite'))
                elif family == 'salvage_refuge':
                    box(p, (x, 2, z + 5), (x + 4, 2, z + 6), WOOD)
                    for xx in (x, x + 4):
                        box(p, (xx, 3, z + 5), (xx, 4, z + 6), WOOD)
                else:
                    arch(p, x, z + 6, 7)


def staircase(p):
    # Both flights are five blocks wide. Bottom and top sockets are on opposite walls.
    box(p, (6, 7, 12), (22, 7, 15), FLOOR)
    for i in range(6):
        box(p, (18, 2, 6 + i), (22, 2 + i, 6 + i), STONE)
        box(p, (18, 2 + i, 6 + i), (22, 2 + i, 6 + i), B('stone_brick_stairs', facing='south', half='bottom', shape='straight', waterlogged=False))
        box(p, (6, 2, 11 - i), (10, 8 + i, 11 - i), STONE)
        box(p, (6, 8 + i, 11 - i), (10, 8 + i, 11 - i), B('stone_brick_stairs', facing='north', half='bottom', shape='straight', waterlogged=False))
    box(p, (6, 13, 3), (16, 13, 5), FLOOR)
    box(p, (12, 13, 6), (16, 13, 28), FLOOR)
    for x in (11, 17):
        box(p, (x, 14, 6), (x, 14, 26), TRIM)
    # Clear roof ribs above the entire upper flight/landing and upper return aisle.
    box(p, (5, 14, 2), (17, 16, 26), AIR)
    for x in (11, 17):
        box(p, (x, 14, 6), (x, 14, 26), TRIM)
    # Lower path turns right at z=4 then climbs the first flight southwards.
    box(p, (12, 2, 0), (16, 6, 5), AIR)
    box(p, (12, 2, 3), (22, 5, 5), AIR)
    box(p, (12, 14, 27), (16, 16, 28), AIR)


def generate_piece(family, condition):
    if family == 'connector_straight':
        p = Piece(7, 8, 29)
        box(p, (0, 0, 0), (6, 7, 28), AIR)
        box(p, (0, 0, 0), (6, 1, 28), FLOOR)
        box(p, (0, 7, 0), (6, 7, 28), STONE)
        for x in (0, 6):
            box(p, (x, 2, 0), (x, 6, 28), STONE)
            for z in (4, 14, 24):
                box(p, (x, 2, z), (x, 6, z), TRIM)
                p.set(x, 5, z, B('sea_lantern'))
        if condition != 'kept':
            for z in range(2, 27, 3 if condition == 'ruined' else 7):
                p.set(0, 4, z, B('mossy_stone_bricks'))
                p.set(6, 4, z, B('cracked_stone_bricks'))
        return p, [{'face': 'north', 'feet': [3, 2, 0]}, {'face': 'south', 'feet': [3, 2, 28]}], 0
    p = shell(18 if family == 'switchback_stair' else 15)
    if family == 'switchback_stair':
        staircase(p)
        sockets = [{'face': 'north', 'feet': [14, 2, 0]}, {'face': 'south', 'feet': [14, 14, 28]}]
    else:
        furnish(p, family)
        # The crossing is immutable across all function and decay variants.
        box(p, (12, 2, 0), (16, 6, 28), AIR)
        box(p, (0, 2, 12), (28, 6, 16), AIR)
        sockets = [{'face': f, 'feet': xyz} for f, xyz in (
            ('north', [14, 2, 0]), ('east', [28, 2, 14]),
            ('south', [14, 2, 28]), ('west', [0, 2, 14]))]
    rng = random.Random(f'{SEED}/{family}/{condition}')
    # Surface decay never removes a bearing block or opens the containment shell.
    count = 0
    for pos, (idx, be) in list(p.blocks.items()):
        name = p.palette[idx]['Name']
        x, y, z = pos
        if name == 'minecraft:stone_bricks' and 0 < x < 28 and 0 < z < 28 and y >= 7:
            if rng.random() < (0, .24, .55)[CONDITION.index(condition)]:
                p.set(x, y, z, B(rng.choice(('cracked_stone_bricks', 'mossy_stone_bricks'))))
                count += 1
    if condition == 'ruined' and family != 'switchback_stair':
        # Lost internal pew/shelf sections are intentional; outer envelope remains sealed.
        for x, z in ((5, 5), (22, 22)):
            for y in range(3, 6):
                if p.palette[p.blocks[(x, y, z)][0]]['Name'] not in ('minecraft:water',):
                    p.set(x, y, z, AIR)
        for x, z in ((6, 5), (23, 22)):
            if p.palette[p.blocks[(x, 2, z)][0]]['Name'] == 'minecraft:air':
                p.set(x, 2, z, B('stone_brick_slab', type='bottom', waterlogged=False))
    return p, sockets, count


def walkable(root):
    palette = root['palette']
    cells = {tuple(b['pos']): palette[int(b['state'])] for b in root['blocks']}
    def air(pos):
        return cells.get(pos, {}).get('Name') == 'minecraft:air'
    def support(pos):
        name = cells.get(pos, {}).get('Name', '')
        return name not in ('', 'minecraft:air', 'minecraft:water', 'minecraft:cobweb') and not name.endswith(('_carpet', '_chain'))
    sx, sy, sz = root['size']
    nodes = {(x, y, z) for x in range(sx) for z in range(sz) for y in range(2, sy - 1)
             if air((x, y, z)) and air((x, y + 1, z)) and support((x, y - 1, z))}
    return nodes, cells


def validate(root, sockets, family):
    assert root['DataVersion'] == 3465 and max(root['size']) <= 48
    assert not root['entities'] and all('nbt' not in b for b in root['blocks'])
    nodes, cells = walkable(root)
    start = tuple(sockets[0]['feet'])
    assert start in nodes, (family, 'missing entrance', start)
    seen, queue = {start}, deque([start])
    while queue:
        x, y, z = queue.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (0, 1, -1):
                nxt = (x + dx, y + dy, z + dz)
                # One-block rise needs space above the lower step for a player's body.
                lower = (x, y + 2, z) if dy == 1 else (nxt[0], nxt[1] + 2, nxt[2])
                if nxt in nodes and nxt not in seen and (dy == 0 or cells[lower]['Name'] == 'minecraft:air'):
                    seen.add(nxt)
                    queue.append(nxt)
    assert all(tuple(s['feet']) in seen for s in sockets), (family, 'unreachable connector')
    if family == 'connector_straight':
        assert all((x, 2, z) in seen for x in range(1, 6) for z in range(29))
    elif family != 'switchback_stair':
        for i in range(29):
            for w in range(12, 17):
                assert (w, 2, i) in seen and (i, 2, w) in seen, (family, 'blocked five-wide crossing')
    return {'reachable_standing_cells': len(seen), 'all_sockets_reachable': True,
            'two_block_headroom': True, 'graph_only_test': True, 'client_movement_test': 'pending'}


class KitProvider:
    provider_id = 'alfheim_ashen_cloister_asset_kit_v1'
    aliases = ('ashen_cloister_asset_kit',)

    def describe(self):
        return {'provider_id': self.provider_id, 'aliases': list(self.aliases),
                'operation': 'original pack-authored staged room and refuge templates'}

    def generate(self, request, registry_resolver):
        files, rows, probes = {}, [], {}
        for family, purpose in {**ROOMS, **SERVICES, **CONNECTORS}.items():
            for condition in CONDITION:
                piece, sockets, changed = generate_piece(family, condition)
                assert piece.dropped == 0
                root = piece.to_nbt()
                for state in root['palette']:
                    rid = state['Name']
                    if rid not in probes:
                        probes[rid] = registry_resolver.probe(rid, kind='block')
                    assert probes[rid]['level'] in ('exact', 'vanilla'), probes[rid]
                checks = validate(root, sockets, family)
                rel = f'templates/act_1/{family}/{condition}.nbt'
                path = OUT / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                nbt.save(path, '', root)
                payload = gzip.compress(gzip.decompress(path.read_bytes()), mtime=0)
                path.write_bytes(payload)
                files[rel.replace('/', '_')] = payload
                rows.append({'family': family, 'condition': condition, 'purpose': purpose,
                             'path': rel, 'size': list(piece.size), 'sockets': sockets,
                             'decayed_masonry': changed, 'block_count': len(root['blocks']),
                             'sha256': hashlib.sha256(payload).hexdigest(), 'checks': checks,
                             'status': 'static validated', 'trading': 'not implemented' if family in SERVICES else 'not applicable'})
        return {'provider_id': self.provider_id, 'status': 'LOCALLY_VALIDATED',
                'generated_layout': {'pieces': rows, 'registry_probes': probes,
                                     'natural_placement': 'not registered', 'runtime_state': 'RUNTIME_TEST_REQUIRED'},
                'structure_artifact': {'format': 'minecraft_structure_nbt', 'piece_count': len(rows)},
                'artifact_bytes': files}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cw-source', type=Path, default=Path('C:/GITS/Structuresmith/StructureSmith'))
    args = ap.parse_args()
    sys.path.insert(0, str(args.cw_source / 'src'))
    from structure_capability import StructureCapability
    state = ROOT / 'build/labyrinth-asset-kit/snapshots'
    cap = StructureCapability(project_root=ROOT, state_root=state)
    assert cap.capabilities()['service'] == 'Continuity Works'
    registry_file = ROOT / 'server/local/kubejs/export/registries/block.json'
    cap.inventory.add_registry_ids(json.loads(registry_file.read_text()), kind='block')
    cap.register_generator(KitProvider())
    OUT.mkdir(parents=True, exist_ok=True)
    request = {'structure_id': 'alfheim:ashen_cloister_asset_kit', 'target_version': '1.20.1',
               'operation': 'generate', 'grade': 4,
               'purpose': {'kind': 'ruined_elven_abbey', 'required_zones': list(ROOMS) + list(SERVICES),
                           'required_routes': ['five-wide crossing', 'two-flight stair', 'safe refuge approaches']},
               'theme': {'name': 'Ashen Cloister', 'culture': 'Alfheim elven',
                         'palette_roles': {'masonry': ['minecraft:stone_bricks'], 'wood': ['minecraft:spruce_planks']}},
               'context': {'dimension': 'mythicbotany:alfheim', 'terrain': 'bounded authored modules; no site selected'},
               'preserve': ['native room floor datum', '29-block room envelope', 'existing worldgen'],
               'integration_contracts': {'independent_structure_gap': 500, 'same_family': 'monastery plus village plus labyrinth',
                                         'deployment': 'staged only; placement adapter not executed'},
               'generation': {'kind': 'ashen_cloister_asset_kit', 'seed': SEED, 'materialize_nbt': True}}
    plan = cap.plan(request)
    assert plan['audit']['status'] != 'FAIL'
    result = cap.generate(request)
    assert result['generation']['status'] == 'LOCALLY_VALIDATED'
    report = {'seed': SEED, 'target': 'Minecraft 1.20.1 / Forge 47.4.10',
              'execution': 'Continuity Works StructureCapability.plan / generate with pack-authored provider',
              'cw_source_sha256': hashlib.sha256((args.cw_source / 'src/structure_capability/api.py').read_bytes()).hexdigest(),
              'registry_sha256': hashlib.sha256(registry_file.read_bytes()).hexdigest(),
              'snapshot': result['snapshot'], 'provider': result['generation']['provider_id'],
              'deployment': 'staged only', **result['generated_layout']}
    (OUT / 'structure_manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (OUT / 'structure_plan.json').write_text(json.dumps(plan['plan'], indent=2) + '\n', encoding='utf-8')
    print(f"Staged {len(report['pieces'])} templates: 18 dungeon families + 6 service interiors + passage, three conditions each.")


if __name__ == '__main__':
    main()
