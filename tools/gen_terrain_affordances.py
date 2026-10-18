"""Complete, reviewable terrain contracts for every active pack-owned structure.

This is a runtime integration policy, not a replacement structure generator.
Existing NBT geometry and vanilla terrain blending remain authoritative.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'kubejs/data/alfheim'
OUT = DATA / 'terrain_affordances'

# These forms have meaningful negative space, water, roots, or suspended spans.
# They must never receive a rectangular underfill that destroys that purpose.
SPECIAL = {
    'greatbole': ('rooted_tree', 'Authored roots, Hollow Court foundation and arrival-site checks'),
    'ley_fracture': ('buried', 'Authored below-ground fracture; retain host cover and the Deep boundary'),
    'mountain_worldstone': ('cavern', 'Native solid host, roof cover, floor limit and cavern envelope checks'),
    'upper_underworld': ('buried', 'Native twelve-block surface cover and Y>=32 floor checks'),
    'harbor_complex': ('shoreline', 'Native wet/dry anchors, authored quay footers, preserved channels and waterline'),
    'royal_castle': ('castle', 'Native 96-block footings, bounded relief and supported coastal site; one-block perimeter apron'),
}
for name in ('cinderglass_crater','harvest_crater','marchfall_crater','hillcut_quarry','sundered_quarry','starveling_pit'):
    SPECIAL[name] = ('excavation', 'Preserve authored bowl/benches and natural rim; never fill the excavation')
for name in ('broken_causeway','canopy_span','driftwood_span','hushbark_causeway','severed_span'):
    SPECIAL[name] = ('span', 'Preserve open span and clearance; support abutments, never solid-fill the crossing')
for name in ('boneyard_wreck','mire_hulk','stormwreck','strandline_hulk'):
    SPECIAL[name] = ('wreck', 'Preserve hull, shoreline/seabed and authored wreck position; no artificial island')
for name in ('lake_arcade','lake_shrine','mistfall_shrine','tidal_arcade','drowned_arcade'):
    SPECIAL[name] = ('waterwork', 'Preserve ocean-floor projection, waterline and open water; authored footings only')
for name in ('anchor_bastion','fracture_gate','garden_archive_terrace','kings_cliff_tomb','last_watch','mourning_court',
             'prism_observatory','root_shrine','split_gallery','starless_orrery','verge_spire'):
    SPECIAL[name] = ('void_ledge', 'Require competent natural ledge using native support probes; no rescue island or below-floor relocation')


def templates(pool, seen=None):
    seen = set() if seen is None else seen
    if pool in seen or pool == 'minecraft:empty':
        return set()
    seen.add(pool)
    ns, path = pool.split(':', 1)
    source = ROOT / f'kubejs/data/{ns}/worldgen/template_pool/{path}.json'
    if not source.exists():
        return set()
    body = json.loads(source.read_text(encoding='utf-8'))
    result = set()
    for entry in body.get('elements', []):
        element = entry['element']
        if 'location' in element:
            result.add(element['location'])
        for nested in element.get('elements', []):
            if 'location' in nested:
                result.add(nested['location'])
    # Jigsaw links may reference other pools; inventory their actual NBT later.
    return result


def material(pool):
    import nbt
    counts = collections.Counter()
    for location in templates(pool):
        ns, path = location.split(':', 1)
        filename = ROOT / f'kubejs/data/{ns}/structures/{path}.nbt'
        root = nbt.load(filename)[1]
        for b in root['blocks']:
            if int(b['pos'][1]) > 2:
                continue
            name = root['palette'][int(b['state'])]['Name']
            if any(s in name for s in ('stone','rock','marble','calcite','terracotta','dirt','sand','gravel')) and not any(
                    s in name for s in ('stairs','slab','wall','button','pressure','ore','cluster','carpet')):
                counts[name] += 1
    return counts.most_common(1)[0][0] if counts else 'botania:livingrock_bricks'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    census = []
    for path in sorted((DATA / 'worldgen/structure').glob('*.json')):
        d = json.loads(path.read_text(encoding='utf-8'))
        name = path.stem
        layout = d.get('layout', d)
        typ = d['type']
        if name in SPECIAL:
            mode, reason = SPECIAL[name]
        elif typ == 'alfheim_companion:fey_sky_village':
            mode, reason = 'floating', 'Intentional authored floating island; native terrain/void clearance, no ground pillar'
        elif typ in ('alfheim_companion:allocated_underground','alfheim_companion:void_war') and name != 'deepworks_headworks':
            mode, reason = 'buried', 'Native underground host/cover/floor and reservation checks; retain authored chambers'
        elif layout.get('project_start_to_heightmap') == 'WORLD_SURFACE_WG':
            mode, reason = 'grounded', 'One-block plate edge, two-block feather, bounded supported contact; preserve authored interior'
        else:
            raise AssertionError(('Unclassified terrain contract', name, typ))
        ground = max(0, -int(layout.get('start_height', {}).get('absolute', 0)))
        p = dict(schema=1, structure=f'alfheim:{name}', mode=mode, reason=reason,
                 activate_ground_adapter=False,
                 edge_width=1 if mode in ('grounded','castle','shoreline') else 0,
                 feather_width=2 if mode == 'grounded' else 0,
                 ground_offset=ground, max_support_depth=16 if mode == 'grounded' else 96 if mode == 'castle' else 0,
                 max_terrain_rise=6, allow_water=name == 'fen_shrine',
                 foundation_material=material(layout['start_pool']) if mode == 'grounded' else 'botania:livingrock_bricks',
                 generation_only=True, replace_buried_solid_terrain=False,
                 independent_structure_gap=500,
                 enforcement='staged_native_plate_adapter' if mode=='grounded' else 'existing_native_or_authored_geometry',
                 runtime_gate='representative_fresh_world_check_required' if mode=='grounded' else 'existing_validation_not_superseded')
        (OUT / (name+'.json')).write_text(json.dumps(p, indent=2)+'\n', encoding='utf-8')
        census.append(p)
    stale = {p.stem for p in OUT.glob('*.json')} - {p['structure'].split(':')[1] for p in census}
    assert not stale, ('Stale terrain policies require explicit review', stale)
    report = dict(structures=len(census), modes=dict(collections.Counter(p['mode'] for p in census)),
                  policies=census, existing_worlds_modified=False,
                  warning='A classified exception is not a claim of newly verified host support')
    (ROOT/'tools/terrain_affordance_manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Terrain policies:', report['structures'], report['modes'])


if __name__ == '__main__':
    main()
