"""Shore decoration contracts and source equality; not runtime acceptance."""
import copy,json,re
from gen_shore_details import ROOT,build,SPECS

def walk(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from walk(v)
    elif isinstance(value,list):
        for v in value:yield from walk(v)

def validate(config):
    errors=[]
    for name,doc in config.items():
        for column in (n['config'] for n in walk(doc) if n.get('type')=='minecraft:block_column'):
            predicates=column.get('allowed_placement',{}).get('predicates',[])
            if not any(p.get('blocks')==['minecraft:air'] for p in predicates):
                errors.append('occupied cells accepted: '+name)
            if not any(p.get('offset')==[0,-1,0] and
                       {'minecraft:sand','minecraft:gravel','alfheim:tide_livingrock'}<=set(p.get('blocks',[]))
                       for p in predicates):
                errors.append('per-cell shore support absent: '+name)
            axis={'east':'x','south':'z'}.get(column.get('direction'))
            if axis is None:errors.append('non-horizontal column: '+name)
            for node in walk(column):
                if str(node.get('Name','')).endswith('_log') and node.get('Properties',{}).get('axis')!=axis:
                    errors.append('log axis differs from trunk direction: '+name)
    return errors

def main():
    out=build()
    for relative,data in out.items():assert (ROOT/relative).read_bytes()==data,relative
    config={p.rsplit('/',1)[1][:-5]:json.loads(data) for p,data in out.items() if '/configured_feature/' in p}
    registry=set(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text(encoding='utf-8')))
    for script in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        registry.update(re.findall(r"event\.create\(['\"]([^'\"]+)['\"]",script.read_text(encoding='utf-8')))
    used=set()
    for node in walk(config):
        if 'Name' in node:used.add(node['Name'])
        if 'blocks' in node:used.update(node['blocks'])
    assert used<=registry,('unregistered shore blocks',used-registry)
    assert not validate(config),validate(config)
    from gen_alfheim_biomes import SHORE_CONFIGURED
    assert SHORE_CONFIGURED['shore_driftwood']==config['shore_driftwood'],'biome generator would revert driftwood'
    drift=config['shore_driftwood']['config']
    assert drift['tries']==2 and drift['xz_spread']==5 and drift['y_spread']==1
    for name,(biome,chance) in SPECS.items():
        placed=json.loads(out[f'kubejs/data/alfheim/worldgen/placed_feature/{name}.json'])
        assert placed['placement'][0]=={'type':'minecraft:rarity_filter','chance':chance}
        assert placed['placement'][-1]=={'type':'minecraft:biome'}
        modifier=json.loads(out[f'kubejs/data/alfheim/forge/biome_modifier/shore_{name}.json'])
        assert modifier['biomes']==[biome] and modifier['step']=='vegetal_decoration'
    # Mutations prove the safety checks catch missing per-cell support and vertical logs.
    broken=copy.deepcopy(config)
    column=next(n['config'] for n in walk(broken['shore_driftwood']) if n.get('type')=='minecraft:block_column')
    column['allowed_placement']={'type':'minecraft:matching_blocks','blocks':['minecraft:air']}
    assert any('per-cell' in e for e in validate(broken))
    broken=copy.deepcopy(config)
    log=next(n for n in walk(broken['shore_driftwood']) if str(n.get('Name','')).endswith('_log'))
    log['Properties']['axis']='y'
    assert any('axis differs' in e for e in validate(broken))
    print('SHORE STATIC PASS: seven files equal; shoreline hosts, horizontal axes, per-cell support and biome injections guarded; two defect fixtures detected')

if __name__=='__main__':main()
