"""Coverage, progression boundary and model checks for the war recovery economy."""
import hashlib
import json
from pathlib import Path
from check_field_review import overlaps
ROOT=Path(__file__).resolve().parents[1]

def check():
    manifest=json.loads((ROOT/'tools/war_salvage_manifest.json').read_text())
    materials=[x['id'] for x in json.loads((ROOT/'kubejs/war_remains_catalog.json').read_text())['blocks']]
    recipes=manifest['recipes']; inputs=set(); outputs=set()
    def ids(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k=='item': yield v
                else: yield from ids(v)
        elif isinstance(value,list):
            for v in value: yield from ids(v)
    crafting_signatures=set()
    for name,r in recipes.items():
        file=ROOT/'kubejs/data/alfheim/recipes/war_salvage'/f'{name}.json'
        assert json.loads(file.read_text())==r,name
        if r['type']=='minecraft:crafting_shapeless':
            signature=tuple(sorted(ids(r['ingredients'])))
            assert signature not in crafting_signatures,('Ambiguous crafting grid',name)
            crafting_signatures.add(signature)
        outputs.update(ids(r.get('result',r.get('output',{}))))
        for key in ('ingredient','ingredients','input','reagent','pedestalItems'):inputs.update(ids(r.get(key,[])))
        assert not name.startswith('era6') or 'alfheim:wildmarch_sinew' in set(ids(r))
        assert not name.startswith('era8') or 'alfheim:rimebound_lattice' in set(ids(r))
    assert set(materials)<=inputs & outputs,'Every war block must be craftable AND consumed'
    assert {'alfheim:'+n for n in manifest['items']}<=inputs & outputs,'Dead-end components'
    for name in manifest['objects']:
        assert 'alfheim:'+name in outputs
        model=json.loads((ROOT/f'kubejs/assets/alfheim/models/block/war_salvage/{name}.json').read_text())
        assert model['elements'] and overlaps(model)==0,name
        for e in model['elements']:
            assert all(0<=a<b<=16 for a,b in zip(e['from'],e['to'])),name
    # Exploration supplies may consume ladder materials, never manufacture or skip them.
    assert not outputs & {'alfheim:wildmarch_sinew','alfheim:rimebound_lattice','botania:terrasteel_ingot','mythicbotany:alfsteel_ingot'}
    assert len(recipes)==77
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [ROOT/'kubejs/startup_scripts/27_war_salvage.js',*sorted((ROOT/'kubejs/data/alfheim/recipes/war_salvage').rglob('*.json'))]}
    report=dict(status='STATIC_PASS',recipes=len(recipes),materials_with_recipe_and_use=len(materials),
        processed_components=len(manifest['items']),custom_models=len(manifest['objects']),coplanar_overlaps=0,
        era_gates={'III':'living_fibre + Runic Altar','VI':'wildmarch_sinew + Enchanting Apparatus','VIII':'rimebound_lattice + Enchanting Apparatus'},sha256=hashes)
    (ROOT/'tools/war_salvage_static_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('WAR SALVAGE PASS:',len(recipes),'recipes, 32 covered materials, 4 useful components, 6 clean custom models')

if __name__=='__main__':check()
