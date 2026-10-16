"""Load the real Forge recipe manager in an owned disposable world and audit IDs.

The temporary server script only logs evidence. It is removed after the server stops.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import run_server

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-war-salvage-20261015'

def main():
    audit=ROOT/'kubejs/server_scripts/zz_war_salvage_validation.js'
    assert not audit.exists()
    audit.write_text("""// Temporary validation harness; no world or recipe mutation.
ServerEvents.loaded(event => {
  let count = 0
  event.server.recipeManager.getRecipes().forEach(recipe => {
    let id = String(recipe.id)
    if (!id.startsWith('alfheim:war_salvage/')) return
    let missing = 0
    let output
    if (String(recipe.type) == 'ars_nouveau:enchanting_apparatus') {
      // The installed Ars class intentionally returns EMPTY from getResultItem.
      // Its actual station output uses getResult; keepNbtOfReagent is false here.
      if (recipe.reagent.itemIds.size() == 0) missing++
      recipe.pedestalItems.forEach(ingredient => { if (ingredient.itemIds.size() == 0) missing++ })
      output = recipe.getResult(null, Item.of('minecraft:air'), null)
    } else {
      recipe.ingredients.forEach(ingredient => { if (ingredient.itemIds.size() == 0) missing++ })
      output = recipe.getResultItem(event.server.registryAccess())
    }
    console.info('WAR_SALVAGE_RECIPE ' + id + ' output=' + output.id + ' count=' + output.count + ' emptyIngredients=' + missing)
    count++
  })
  console.info('WAR_SALVAGE_TOTAL ' + count)
})
""",encoding='utf-8')
    props=ROOT/'server/server.properties';old=props.read_bytes();before=set((ROOT/'server').glob('console-*.log'))
    try:
        code=run_server.run('3536368297089363045',WORLD,8,[(2,'gamerule randomTickSpeed 0'),(2,'save-all flush'),(1,'stop')],360)
    finally:
        audit.unlink(missing_ok=True)
        (ROOT/'server/kubejs/server_scripts/zz_war_salvage_validation.js').unlink(missing_ok=True)
        props.write_bytes(old)
        jade=ROOT/'server/config/jade/server-plugin-overrides.json';jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    console=max(set((ROOT/'server').glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    text=console.read_text(errors='replace')
    rows=re.findall(r'WAR_SALVAGE_RECIPE (alfheim:war_salvage/\S+) output=(\S+) count=(\d+) emptyIngredients=(\d+)',text)
    manifest=json.loads((ROOT/'tools/war_salvage_manifest.json').read_text())
    assert len(rows)==len(manifest['recipes']),f'Loaded {len(rows)} / {len(manifest["recipes"])}; see {console}'
    for rid,item,count,missing in rows:
        r=manifest['recipes'][rid.split('war_salvage/')[1]]
        result=r.get('result',r.get('output'))
        assert item==result['item'] and int(count)==result.get('count',1) and missing=='0',(rid,item,count,missing)
    errors=[line for line in text.splitlines() if ('27_war_salvage' in line or 'war_salvage/' in line) and ('ERROR' in line or 'Exception' in line)]
    assert not errors,errors
    hashes={}
    for name in manifest['recipes']:
        rel='kubejs/data/alfheim/recipes/war_salvage/'+name+'.json'
        assert (ROOT/rel).read_bytes()==(ROOT/'server'/rel).read_bytes(),('Runtime mirror mismatch',rel)
        hashes[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    report={'status':'FORGE_RECIPE_MANAGER_PASS','world':WORLD,'console':str(console.relative_to(ROOT)),
        'recipes_registered':len(rows),'empty_ingredients':0,'outputs_verified':True,
        'recipe_sha256':hashes,
        'evidence':[dict(id=a,output=b,count=int(c)) for a,b,c,_ in rows],
        'startup_sha256':hashlib.sha256((ROOT/'kubejs/startup_scripts/27_war_salvage.js').read_bytes()).hexdigest(),
        'limits':'Recipe deserialization, resolved ingredients and outputs verified; station interaction and client visuals require play review.'}
    (ROOT/'tools/war_salvage_runtime_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('WAR SALVAGE FORGE PASS:',len(rows),'resolved recipes / outputs')

if __name__=='__main__':main()
