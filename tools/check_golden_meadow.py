"""Guard the local crop-overwrite repair, not broad terrain."""
import copy,json
from gen_golden_meadow import ROOT,build

def validate(feature):
    config=feature['config'];inner=config['feature'];problems=[]
    if inner['feature']['type']!='minecraft:simple_block':problems.append('must place vegetation only')
    predicate=inner['placement'][0]['predicate']
    predicates=predicate.get('predicates',[])
    if not any(p.get('blocks')==['minecraft:air'] for p in predicates):problems.append('must preserve occupied blocks')
    if not any(p.get('offset')==[0,-1,0] and set(p.get('blocks',[]))=={'minecraft:grass_block','minecraft:dirt'} for p in predicates):
        problems.append('must reject masonry and worked fields')
    entries=inner['feature']['config']['to_place']['entries']
    if {e['data']['Name'] for e in entries}!={'minecraft:grass','minecraft:fern','minecraft:dandelion'}:
        problems.append('unexpected crop or ground replacement')
    return problems

def main():
    out=build()
    for path,data in out.items():assert (ROOT/path).read_bytes()==data,path
    doc=json.loads(out['kubejs/data/alfheim/worldgen/configured_feature/golden_meadow_grass.json'])
    assert not validate(doc),validate(doc)
    broken=copy.deepcopy(doc);broken['config']['feature']['placement'][0]['predicate']['predicates'].pop()
    assert 'must reject masonry and worked fields' in validate(broken)
    broken=copy.deepcopy(doc);broken['config']['feature']['feature']['config']['to_place']['entries'][0]['data']['Name']='minecraft:wheat'
    assert 'unexpected crop or ground replacement' in validate(broken)
    print('GOLDEN MEADOW PASS: four files equal; soil-only, air-only vegetation; two crop/floor regression fixtures detected')

if __name__=='__main__':main()
