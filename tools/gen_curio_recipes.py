"""Emit all 63 native Gear Crafting recipes through the installed CW capability."""
from pathlib import Path
import hashlib,json,re,sys
from curio_crafting_catalog import recipe_for,acquisition_text

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'alfheim_reclaimed_design/curios/curio_suite_catalog.json'
OUT=ROOT/'kubejs/data/alfheim/mmorpg_profession_recipe'

def build():
    catalog=json.loads(CATALOG.read_text());ranks={r['id']:r for r in catalog['ranks']}
    recipes=[recipe_for(item,ranks) for item in catalog['planned_items']]
    assert len(recipes)==len({r['result'] for r in recipes})==63
    outputs={'kubejs/data/alfheim/mmorpg_profession_recipe/'+r['id']+'.json':(json.dumps(r,indent=2)+'\n').encode() for r in recipes}
    return outputs,recipes

class Provider:
    provider_id='alfheim_regalia_acquisition_v1';aliases=('alfheim_regalia_acquisition',)
    def __init__(self,outputs,recipes):self.outputs=outputs;self.recipes=recipes
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases)}
    def generate(self,request,resolver):
        ids={m['id'] for r in self.recipes for m in r['mats']}|{r['result'] for r in self.recipes}|{'mmorpg:gear_crafting_station'}
        probes={iid:resolver.probe(iid,kind='item') for iid in sorted(ids)}
        assert all(p['level'] in ('exact','vanilla') for p in probes.values()),{k:v for k,v in probes.items() if v['level'] not in ('exact','vanilla')}
        return {'provider_id':self.provider_id,'status':'GENERATED_NOT_VALIDATED',
                'generated_layout':{'files':[{'file':rel,'sha256':hashlib.sha256(data).hexdigest()} for rel,data in self.outputs.items()],'registry_probes':probes,'native_recipe_count':63,'schema_reference':'Installed Mine and Slash 6.4.7 ProfessionRecipe data and existing 480 pack armory recipes'},
                'structure_artifact':{'format':'minecraft_datapack','piece_count':0},
                'artifact_bytes':{rel.replace('/','_'):data for rel,data in self.outputs.items()}}

def main():
    outputs,recipes=build()
    if '--check' in sys.argv:
        for rel,data in outputs.items():assert (ROOT/rel).read_bytes()==data,rel
        print('REGALIA RECIPE SOURCE EQUALITY PASS',len(outputs));return
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=ROOT/'build/regalia_acquisition/snapshots')
    cap.inventory.add_registry_ids(json.loads((ROOT/'server/local/kubejs/export/registries/item.json').read_text()),kind='item')
    cap.register_generator(Provider(outputs,recipes))
    result=cap.generate({'structure_id':'alfheim:regalia_acquisition','target_version':'1.20.1','grade':2,'purpose':{'kind':'native_profession_regalia_crafting','required_zones':['apprentice acquisition','guild acquisition','master acquisition']},'generation':{'kind':'alfheim_regalia_acquisition','materialize_nbt':False}})
    for rel,data in outputs.items():path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    # Update text without touching the existing artwork, models or slot eligibility.
    import gen_curios
    catalog=json.loads(CATALOG.read_text());rows=gen_curios.plan(catalog)
    path=ROOT/gen_curios.SCRIPT_OUT;text=path.read_text('utf8')
    for row in rows:
        pattern=r"(event\.create\('alfheim:"+re.escape(row['id'])+r"'\)[^\n]*?\.tooltip\()('(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")(\))"
        text,count=re.subn(pattern,lambda m:m[1]+json.dumps(row['tooltip'])+m[3],text)
        assert count==1,row['id']
    path.write_text(text,encoding='utf8',newline='\n')
    path=ROOT/gen_curios.MANIFEST_OUT;manifest=json.loads(path.read_text());manifest['status']='registered and slotted; native Gear Crafting recipes authored; no attunement effects'
    manifest['crafting']={'station':'mmorpg:gear_crafting_station','native_recipe_count':63,'ranks':{'apprentice':0,'guild':2,'master':4},'generator':'tools/gen_curio_recipes.py','runtime':'Native loading and menu transactions pending in game'}
    path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    report={'capability':'Continuity Works','snapshot_id':result['snapshot']['snapshot_id'],'generation':result['generation'],'layout':result['generated_layout'],'recipes':recipes,'scope':'Acquisition only; fixed decorative items, no class/profession effects or native soul lifecycle claimed'}
    (ROOT/'tools/curio_recipes_generation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('CW emitted 63 native Gear Crafting recipes and updated acquisition descriptions')

if __name__=='__main__':main()
