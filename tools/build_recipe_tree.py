"""Rebuild the pack-wide static recipe graph, CSVs and a single zoomable SVG.

Reads installed jars and pack data; does not change game files. Python standard library only.
Run from the instance root: python tools/build_recipe_tree.py
"""
from __future__ import annotations
import collections as C
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/recipe-tree'
CLIENT = Path(r'C:\Users\Admin\curseforge\minecraft\Install\versions\1.20.1\1.20.1.jar')
ID = re.compile(r'^[a-z0-9_.-]+:[a-z0-9_./-]+$')
recipes, tags, names, files = {}, {}, {}, []
warnings = []
loaded_mods={'minecraft','forge','kubejs'}

def ingest(entry, raw, source):
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        return
    m = re.fullmatch(r'data/([^/]+)/recipes/(.+)\.json', entry)
    if m:
        recipes[m[1]+':'+m[2]] = dict(id=m[1]+':'+m[2],data=data,source=source)
    m = re.fullmatch(r'data/([^/]+)/tags/(items|fluids)/(.+)\.json',entry)
    if m:
        key = ('fluid:' if m[2]=='fluids' else '')+'#'+m[1]+':'+m[3]
        if data.get('replace'): tags[key]=[]
        tags.setdefault(key,[]).extend(data.get('values',[]))
    if re.fullmatch(r'assets/[^/]+/lang/en_us.json',entry):
        for key,value in data.items():
            m = re.match(r'(?:item|block)\.([^.]+)\.(.+)', key)
            if m and isinstance(value,str): names[m[1]+':'+m[2]]=value

def scan():
    jars = ([CLIENT] if CLIENT.exists() else []) + sorted((ROOT/'mods').glob('*.jar'))
    for jar in jars:
        files.append(dict(path=str(jar),size=jar.stat().st_size,sha256=hashlib.file_digest(jar.open('rb'),'sha256').hexdigest()))
        with zipfile.ZipFile(jar) as z:
            if 'META-INF/mods.toml' in z.namelist():
                loaded_mods.update(re.findall(r'^\s*modId\s*=\s*[\'"]([^\'"]+)',z.read('META-INF/mods.toml').decode('utf-8','replace'),re.M))
            for entry in z.namelist():
                if re.match(r'data/[^/]+/(recipes|tags/(items|fluids))/.+\.json$',entry) or re.fullmatch(r'assets/[^/]+/lang/en_us.json',entry):
                    ingest(entry,z.read(entry),jar.name+'!/'+entry)
    # Later loose data overrides earlier jar data. World-selected packs cannot be inferred.
    for root in [ROOT/'data',ROOT/'datapacks',ROOT/'moonlight-global-datapacks',ROOT/'kubejs/data',ROOT/'kubejs/assets']:
        if not root.exists(): continue
        for p in sorted(root.rglob('*.json')):
            rel=p.relative_to(root).as_posix()
            if root.name in ('data','assets'):
                rel=root.name+'/'+rel
            elif '/data/' in '/'+rel:
                rel='data/'+rel.split('data/',1)[1]
            ingest(rel,p.read_bytes(),p.relative_to(ROOT).as_posix())
        for p in sorted(root.rglob('*.zip')):
            with zipfile.ZipFile(p) as z:
                for e in z.namelist():
                    if e.endswith('.json'): ingest(e,z.read(e),p.name+'!/'+e)
    scripts=json.loads((OUT/'script_recipes.json').read_text())
    assert not scripts['errors'], scripts['errors']
    for r in scripts['removals']:
        f=r['filter']; assert set(f)=={'id'},f
        recipes.pop(f['id'],None)
    for r in scripts['records']: recipes[r['id']]=r
    # Mine and Slash profession recipes use a separate data registry.
    for p in sorted((ROOT/'kubejs/data').glob('*/mmorpg_profession_recipe/*.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        rid='mmorpg_profession:'+p.stem
        recipes[rid]=dict(id=rid,source=p.relative_to(ROOT).as_posix(),data={
            'type':'mmorpg:profession_crafting','profession':d.get('profession'),
            'ingredients':[{'item':x['id'],'count':x.get('num',x.get('count',x.get('amount',1)))} for x in d.get('mats',[]) if x.get('type')=='ITEM'],
            'output':{'item':d.get('result'),'count':d.get('result_num',1)}, 'native_definition':d})
    # Display names of custom registered objects.
    import ast
    for p in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        for m in re.finditer(r'''event\.create\(\s*['"]([^'"]+)['"](?:\s*,[^)]*)?\)\s*\.displayName\(("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')\)''',p.read_text(encoding='utf-8')):
            names[m[1]]=ast.literal_eval(m[2])
    return scripts

def refs(value, count=1):
    """One input slot can contain alternatives; alternatives are never summed as requirements."""
    if isinstance(value,str):
        return [(value,count)] if ID.fullmatch(value.lstrip('#')) else []
    if isinstance(value,list):
        options=[]
        for v in value: options.extend(refs(v,count))
        return options
    if not isinstance(value,dict): return []
    n=value.get('count',value.get('amount',count))
    if not isinstance(n,(int,float)): n=count
    if 'item' in value:
        return [(value['item'],n)] if isinstance(value['item'],str) else refs(value['item'],n)
    if 'tag' in value:
        return [('#'+value['tag'],n)]
    if 'fluid' in value: return [('fluid:'+value['fluid'],n)]
    if 'fluidTag' in value: return [('fluid:#'+value['fluidTag'],n)]
    if 'FluidName' in value: return [('fluid:'+value['FluidName'],value.get('Amount',n))]
    if 'name' in value and isinstance(value['name'],str) and ID.fullmatch(value['name']):return [(value['name'],n)]
    if value.get('type')=='block' and 'block' in value: return [(value['block'],n)]
    if 'ingredient' in value: return refs(value['ingredient'],n)
    if 'value' in value: return refs(value['value'],n)
    return []

def normalize(r):
    d=r['data']; typ=d.get('type','unknown'); conditions=d.get('conditions',[])
    if typ=='forge:conditional':
        # Preserve each branch and its conditions rather than guessing mod/config predicates.
        result=[]
        for i,branch in enumerate(d.get('recipes',[])):
            rr=dict(r,id=r['id']+f'~branch{i+1}',data=branch.get('recipe',{}))
            children=normalize(rr)
            for x in children: x['conditions']=branch.get('conditions',[])
            result.extend(children)
        return result
    if typ=='botania:nbt_output_wrapper':
        rr=dict(r,data=d['recipe'])
        children=normalize(rr)
        for x in children:x['data']=d;x['conditions']=conditions
        return children
    slots=[]
    def add(v,role='ingredient',number=1):
        opts=refs(v,number)
        if opts: slots.append(dict(options=opts,role=role))
    if 'pattern' in d and 'key' in d:
        counts=C.Counter(''.join(d['pattern']))
        for k,v in d['key'].items():
            if counts[k]: add(v,number=counts[k])
    else:
        for key in ('ingredient','ingredients','input','inputs','base','addition','template','reagent','pedestalItems','inputItems','materials','additives','catalyst','sapling','seed','focus','tool','activation_item','entity_to_sacrifice','secondary_input','center','base_fluid'):
            v=d.get(key)
            if v is None: continue
            # Ingredient arrays mean OR within a single slot; ingredients/pedestals mean AND.
            if isinstance(v,list) and key not in ('ingredient','input','base','addition','template'):
                for vv in v: add(vv,role='catalyst' if key in ('catalyst','tool','focus') else 'ingredient')
            else: add(v,role='catalyst' if key in ('catalyst','tool','focus') else 'ingredient')
    for rune in d.get('runes',[]):
        add(rune.get('rune'),role='ingredient' if rune.get('consume') else 'catalyst')
    for step in d.get('sequence',[]):
        transitional={x for x,_ in refs(d.get('transitionalItem'))}
        for v in step.get('ingredients',[]):
            if not any(x in transitional for x,_ in refs(v)):
                before=len(slots);add(v,number=d.get('loops',1))
                if len(slots)>before:slots[-1]['role']='assembly step'
    outputs=[]
    for key in ('result','output','results','outputs'):
        if key not in d: continue
        v=d[key]
        for vv in v if isinstance(v,list) else [v]:
            outputs.extend(refs(vv,d.get('count',1)))
        break
    # Pure Daisy uses a bare block-state ID as output; trim properties if present.
    costs={k:d[k] for k in ('mana','source','sourceCost','aura','experience','cookingtime','time','processingTime','energy') if k in d and isinstance(d[k],(int,float))}
    if typ=='framedblocks:frame':
        slots.append(dict(options=[('process:framedblocks_frame_material',d.get('material',0))],role='material units'))
    return [dict(id=r['id'],type=typ,inputs=slots,outputs=outputs,costs=costs,conditions=conditions,source=r['source'],data=d)]

def tag_members(tag,seen=None):
    seen=set() if seen is None else seen
    if tag in seen:return set()
    seen=seen|{tag};result=set()
    for v in tags.get(tag,[]):
        v=v.get('id') if isinstance(v,dict) else v
        if not isinstance(v,str):continue
        if v.startswith('#'): result.update(tag_members(v,seen))
        else:result.add(v)
    return result

def condition(c):
    typ=c.get('type','')
    if typ in ('forge:true',):return True
    if typ in ('forge:false',):return False
    if typ in ('forge:mod_loaded','fabric:all_mods_loaded'):return c.get('modid') in loaded_mods
    if typ=='forge:tag_empty':return not tag_members('#'+c['tag'])
    if typ=='forge:not':
        v=condition(c['value']);return None if v is None else not v
    if typ in ('forge:and','forge:or'):
        vals=[condition(v) for v in c.get('values',[])]
        if typ=='forge:and':return False if False in vals else None if None in vals else True
        return True if True in vals else None if None in vals else False
    return None

def build_outputs(all_rows,scripts):
    from player_text import player_text
    rows=[r for r in all_rows if r['condition_status']!='disabled']
    items=set()
    for r in rows:
        for s in r['inputs']:items.update(i for i,_ in s['options'])
        items.update(i for i,_ in r['outputs'])
    # The registry snapshot is retained as evidence, not asserted to be current.
    registry=ROOT/'tools/registry_items.json'
    snapshot=set(json.loads(registry.read_text())['ids']) if registry.exists() else set()
    items.update(snapshot)
    for p in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        items.update(re.findall(r"event\.create\(['\"]([^'\"]+)",p.read_text(encoding='utf-8')))
    used_tags={i for i in items if i.startswith('#') or i.startswith('fluid:#')}
    members={t:tag_members(t) for t in sorted(used_tags)}
    for vv in members.values():items.update(vv)
    def label(i):
        if i.startswith('fluid:'):return 'Fluid: '+label(i[6:])
        if i.startswith('#'):return '# '+i[1:]
        return player_text(names.get(i,i.split(':')[-1].replace('_',' ').replace('/',' / ').title()))
    def method(r):return r['type'].split(':')[-1].replace('_',' ').title()
    def key(kind,i):return kind+hashlib.sha1(i.encode()).hexdigest()[:14]
    produced={i for r in rows for i,_ in r['outputs']}
    depth={i:0 for i in items if i not in produced and i not in used_tags}
    for _ in range(220):
        changed=False
        for t,vv in members.items():
            known=[depth[v] for v in vv if v in depth]
            if known and (t not in depth or min(known)<depth[t]):depth[t]=min(known);changed=True
        for r in rows:
            slotdepths=[]
            for s in r['inputs']:
                ds=[depth[i] for i,_ in s['options'] if i in depth]
                if not ds:break
                slotdepths.append(min(ds))
            else:
                d=1+max(slotdepths,default=0)
                for i,_ in r['outputs']:
                    if i not in depth or d<depth[i]:depth[i]=d;changed=True
        if not changed:break
    bounds=[0,1,2,3,4,5,6,8,12,20]
    def band(d):
        if d is None:return len(bounds)
        return next((n for n,b in enumerate(bounds) if d<=b),len(bounds)-1)
    nodes={}
    for i in sorted(items):
        nodes[key('i',i)]=dict(id=key('i',i),kind='tag' if i in used_tags else 'item',ref=i,label=label(i),depth=depth.get(i),band=band(depth.get(i)),produced=i in produced)
    for r in rows:
        ds=[min((depth.get(i,9999) for i,_ in s['options']),default=9999) for s in r['inputs']]
        d=1+max(ds,default=0)
        if d>=9999:d=None
        dynamic=not r['outputs'] or not r['inputs']
        rid=key('r',r['id'])
        outputs=' + '.join(label(i) for i,_ in r['outputs'])
        nodes[rid]=dict(id=rid,kind='dynamic' if dynamic else 'recipe',ref=r['id'],label=method(r)+': '+outputs if outputs else method(r)+' [dynamic]',method=method(r),depth=d,band=band(d),condition=r['condition_status'],source=r['source'],costs=r['costs'])
    groups=C.defaultdict(list)
    for n in nodes.values():groups[(n['band'],n['kind'] in ('recipe','dynamic'))].append(n)
    # Every box has its own cell; edges are drawn behind opaque boxes.
    NW=270; NH=76; DX=292; DY=106; TOP=500
    columns={k:max(2,math.ceil(len(v)/240)) for k,v in groups.items()}
    panels={};cursor=60
    for b in range(len(bounds)+1):
        ni=columns.get((b,False),0);nr=columns.get((b,True),0)
        width=max(900,(ni+nr)*DX+100)
        panels[b]=dict(x=cursor,w=width,recipe_x=cursor+ni*DX+60)
        cursor+=width+40
    for (b,isrecipe),nn in groups.items():
        nn.sort(key=lambda n:(n['depth'] or 0,n['ref'].split(':')[0],n['label'],n['ref']))
        for index,n in enumerate(nn):
            cols=columns[(b,isrecipe)];panel=panels[b]
            n.update(x=(panel['recipe_x'] if isrecipe else panel['x']+20)+(index%cols)*DX,y=TOP+(index//cols)*DY,w=NW,h=NH)
    W=cursor+60
    H=max(n['y'] for n in nodes.values())+220
    edges=[]
    for r in rows:
        rk=key('r',r['id'])
        for slot,s in enumerate(r['inputs'],1):
            for i,qty in s['options']:
                edges.append(dict(source=key('i',i),target=rk,recipe=r['id'],relation=s['role'],slot=slot,quantity=qty,alternative=len(s['options'])>1))
        for i,qty in r['outputs']:
            edges.append(dict(source=rk,target=key('i',i),recipe=r['id'],relation='output',slot='',quantity=qty,alternative=False))
    for t,vv in members.items():
        for i in sorted(vv):
            if key('i',i) in nodes:edges.append(dict(source=key('i',i),target=key('i',t),recipe='',relation='tag option',slot='',quantity='',alternative=True))
    def writecsv(name,fields,rr):
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rr)
    writecsv('dependency_edges.csv',['source','target','recipe','relation','slot','quantity','alternative'],edges)
    writecsv('items.csv',['node_id','item_id','name','has_extracted_recipe','minimum_recipe_hops','in_historical_registry'],[
        dict(node_id=key('i',i),item_id=i,name=label(i),has_extracted_recipe=i in produced,minimum_recipe_hops=depth.get(i,''),in_historical_registry=i in snapshot) for i in sorted(items)])
    writecsv('recipes.csv',['recipe_id','recipe_type','inputs','outputs','costs','condition_status','coverage','source','raw_json'],[
        dict(recipe_id=r['id'],recipe_type=r['type'],inputs=json.dumps(r['inputs'],ensure_ascii=False),outputs=json.dumps(r['outputs'],ensure_ascii=False),costs=json.dumps(r['costs']),condition_status=r['condition_status'],coverage='explicit endpoints' if r['inputs'] and r['outputs'] else 'dynamic or partial endpoints',source=r['source'],raw_json=json.dumps(r['data'],ensure_ascii=False)) for r in all_rows])
    writecsv('tag_members.csv',['tag','member'],[dict(tag=t,member=i) for t,vv in members.items() for i in sorted(vv)])
    report=dict(recipe_definitions=len(all_rows),included_recipe_nodes=len(rows),disabled_recipes=len(all_rows)-len(rows),script_recipes=len(scripts['records']),script_removals=len(scripts['removals']),item_and_tag_nodes=len(items),edges=len(edges),dynamic_or_partial_recipes=sum(not r['outputs'] or not r['inputs'] for r in rows),unresolved_conditions=sum(r['condition_status']=='unresolved' for r in rows),svg_width=W,svg_height=H,maximum_minimum_recipe_hops=max(depth.values()),historical_registry_items=len(snapshot),source_files=files,
        limitations=['Static reconstruction; not a final runtime RecipeManager export.','Historical registry snapshot supplemented with current script registrations and recipe endpoints.','Mod-loaded and tag-empty conditions evaluated from installed jars and static item tags; other conditions marked unresolved.','World-selected datapack order and dynamically injected recipes may differ at runtime.','Java-defined dynamic recipes retained as nodes with partial or unknown endpoints, never guessed.','Minimum recipe hops are layout hints, not an unlock or reachability proof.','No extracted recipe does not imply an item is unobtainable; mining, loot, trading and world interactions are not recipe routes.','Raw JSON preserves NBT, probabilities, workstation details and custom fields; the graph is a dependency map, not a crafting-grid guide.'])
    (OUT/'coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    E=html.escape
    color={'item':'#152b3a','tag':'#332c45','recipe':'#173f36','dynamic':'#4b3524'}
    stroke={'item':'#57839c','tag':'#ae8ae3','recipe':'#5ebd91','dynamic':'#d3a266'}
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Alfheim Reclaimed recipe dependency graph">',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#68999b"/></marker></defs>',
         '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#ecf4f5} .edge{fill:none;stroke:#294550;stroke-width:1;marker-end:url(#arrow)} .tag-edge{stroke:#30263e;stroke-dasharray:5 4} .node{cursor:default}</style>',
         f'<rect width="{W}" height="{H}" fill="#09151e"/>',
         '<text x="80" y="86" font-size="54" font-weight="700">ALFHEIM RECLAIMED / RECIPE DEPENDENCY TREE</text>',
         f'<text x="80" y="140" font-size="27">{len(rows):,} recipe nodes · {len(items):,} items and ingredient groups · {len(edges):,} directed connections</text>',
         '<text x="80" y="187" font-size="23">Read arrows: ingredient → recipe → product. Purple dashed arrows: alternatives within an ingredient tag. Separate recipe boxes: alternate routes.</text>',
         '<text x="80" y="227" font-size="23">Green = explicit recipe · blue = item / fluid · purple = ingredient group · amber = dynamic or partial recipe. Hover for IDs, quantities and source.</text>',
         '<text x="80" y="267" font-size="23">STATIC RECONSTRUCTION · Dynamic recipes retained with unknown endpoints. No extracted recipe ≠ unavailable. See coverage.json and recipes.csv.</text>',
         '<text x="80" y="307" font-size="23">Columns group minimum recipe hops for navigation; they do not prove progression or station access. Loops and alternate routes may point backward.</text>']
    for b in range(len(bounds)+1):
        x=panels[b]['x'];width=panels[b]['w']
        title='Unresolved cycles / dependencies' if b==len(bounds) else 'No recipe / sources / groups' if b==0 else f'Minimum recipe hops: {bounds[b-1]+1}–{bounds[b]}' if bounds[b]!=bounds[b-1]+1 else f'Minimum recipe hops: {bounds[b]}'
        svg.append(f'<rect x="{x}" y="365" width="{width}" height="{H-405}" rx="16" fill="{"#0e1e29" if b%2==0 else "#0b1a24"}"/>')
        svg.append(f'<text x="{x+22}" y="412" font-size="28" font-weight="600">{E(title)}</text><text x="{x+22}" y="455" font-size="21" fill="#96b0ba">ITEMS + GROUPS</text>')
        if (b,True) in columns:svg.append(f'<text x="{panels[b]["recipe_x"]}" y="455" font-size="21">RECIPES + PROCESSES</text>')
    svg.append('<g id="edges">')
    for index,e in enumerate(edges):
        a,b=nodes[e['source']],nodes[e['target']]
        x1,y1=a['x']+NW,a['y']+NH/2;x2,y2=b['x'],b['y']+NH/2
        delta=max(45,min(600,abs(x2-x1)*.45))
        path=f'M{x1},{y1} C{x1+delta},{y1} {x2-delta},{y2} {x2},{y2}'
        title=f"{nodes[e['source']]['label']} → {nodes[e['target']]['label']} | {e['relation']} | quantity: {e['quantity']}"+(' | alternative option' if e['alternative'] else '')
        svg.append(f'<path id="e{index}" class="edge {"tag-edge" if e["relation"]=="tag option" else ""}" data-from="{e["source"]}" data-to="{e["target"]}" d="{path}"><title>{E(title)}</title></path>')
    svg.append('</g><g id="nodes">')
    for n in nodes.values():
        x,y=n['x'],n['y'];kind=n['kind']
        title=n['label']+'\n'+n['ref']
        if kind in ('recipe','dynamic'):
            title+='\n'+n['method']+'\n'+json.dumps(n['costs'])+'\n'+n['source']+'\nConditions: '+n['condition']
        elif not n['produced'] and kind=='item':title+='\nNo extracted recipe. May be a world, loot, trade or dynamic source.'
        # Wrap without truncation. Full IDs and details remain in title and CSV.
        import textwrap
        lines=textwrap.wrap(n['label'],width=29,break_long_words=True) or ['']
        font=14 if len(lines)>3 else 16
        if len(lines)>4:
            lines=textwrap.wrap(n['label'],width=38);font=12
        svg.append(f'<g class="node" id="{n["id"]}" data-kind="{kind}" data-label="{E(n["label"],quote=True)}" data-ref="{E(n["ref"],quote=True)}"><title>{E(title)}</title><rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="9" fill="{color[kind]}" stroke="{stroke[kind]}" {"stroke-dasharray=\"6 3\"" if kind=="dynamic" else ""}/>' )
        for j,line in enumerate(lines[:5]):svg.append(f'<text x="{x+10}" y="{y+18+j*(font+1)}" font-size="{font}">{E(line)}</text>')
        svg.append('</g>')
    svg.append('</g></svg>')
    svgtext='\n'.join(svg)
    (OUT/'alfheim-recipe-tech-tree.svg').write_text(svgtext,encoding='utf-8')
    graph=dict(nodes=list(nodes.values()),edges=edges,width=W,height=H)
    (OUT/'graph.json').write_text(json.dumps(graph,ensure_ascii=False),encoding='utf-8')
    (OUT/'README.txt').write_text('ALFHEIM RECLAIMED RECIPE TREE\n\nSingle static image: alfheim-recipe-tech-tree.svg\nRaster copy: alfheim-recipe-tech-tree.png\nThe PNG contains the same complete diagram and can be viewed as an ordinary image.\nCSV files contain the supporting recipe, item, tag and connection data.\n\n'+'\n'.join(report['limitations'])+'\n\nRebuild SVG and CSV: python tools/build_recipe_tree.py\nRender PNG: python tools/render_recipe_tree.py\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='source_files'},indent=2))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    subprocess.run(['node',str(ROOT/'tools/capture_recipe_scripts.cjs')],cwd=ROOT,check=True)
    scripts=scan()
    normalized=[n for r in recipes.values() for n in normalize(r)]
    for r in normalized:
        vals=[condition(c) for c in r['conditions']]
        r['condition_status']='disabled' if False in vals else 'unresolved' if None in vals else 'included'
    (OUT/'normalized_recipes.json').write_text(json.dumps(normalized,ensure_ascii=False),encoding='utf-8')
    summary=C.Counter()
    for r in normalized: summary[(r['type'],bool(r['outputs']),bool(r['inputs']))]+=1
    (OUT/'schema_inventory.json').write_text(json.dumps([dict(type=t,outputs=o,inputs=i,count=n) for (t,o,i),n in sorted(summary.items())],indent=2))
    print('Recipe schema inventory:',len(normalized),'recipes',len(summary),'schemas')
    for (t,o,i),n in sorted(summary.items()): print(n,t,'outputs='+str(o),'inputs='+str(i))
    build_outputs(normalized,scripts)

if __name__=='__main__':main()
