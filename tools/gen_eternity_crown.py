"""Deterministic native crown meshes and catalogue-complete recipes, emitted through CW."""
from pathlib import Path
import hashlib,io,json,math,sys
from PIL import Image,ImageDraw
from gemstone_catalog import GEMS

ROOT=Path(__file__).resolve().parents[1]
RES='first_party_mods/alfheim_companion/src/main/resources/'
ASSET=RES+'assets/alfheim_companion/'
DATA=RES+'data/alfheim_companion/'
NS='alfheim_companion:'
LAYERS=[GEMS[i:i+8] for i in range(0,len(GEMS),8)]

def geometry():
    mesh=[]
    def box(a,b,metal='gold',gem=None):
        uv=[0,0] if metal=='gold' else [64,0]
        if gem is not None:uv=[gem%32*8,128+gem//32*8]
        row={'from':a,'to':b,'uv':uv,'material':metal}
        if gem is not None:row['gem']=gem;row['item']=GEMS[gem]['item']
        mesh.append(row)
    # A hollow circlet, stepped mouldings and six rows of individually bezel-set stones.
    for side in range(4):
        def face(x,y,z,w,h,d,metal='gold',gem=None):
            corners=[]
            for px,pz in [(x,z),(x+w,z+d)]:
                for _ in range(side):px,pz=16-pz,px
                corners.append((px,pz))
            box([min(p[0] for p in corners),y,min(p[1] for p in corners)],[max(p[0] for p in corners),y+h,max(p[1] for p in corners)],metal,gem)
        face(3.6,2,3.6,8.8,4.5,.45)
        for y in (2,2.4,6,6.45):face(3.4,y,3.4,9.2,.18,.5,'platinum')
        for col in range(11):
            x=3.75+col*.77
            face(x,2.6,3.47,.11,3.3,.2,'platinum')
        for col in range(3):
            x=4.2+col*3.0
            # Stepped fleurons rise from the rim; their tips and sockets are platinum.
            for y,w,h in [(6.5,1.65,.4),(6.9,1.3,.5),(7.4,.9,1),(8.4,.55,1.1),(9.5,.25,.7)]:
                face(x-w/2,y,3.7,w,h,.45)
            face(x-.23,10.2,3.62,.46,.4,.6,'platinum')
            face(x-.8,7.0,3.55,.35,.5,.6,'platinum')
            face(x+.45,7.0,3.55,.35,.5,.6,'platinum')
        for row in range(6):
            for col in range(10):
                index=row*40+side*10+col
                if index>=len(GEMS):continue
                x=3.94+col*.77;y=2.7+row*.53
                face(x-.07,y-.06,3.3,.59,.49,.22,'platinum')
                face(x,y,3.2,.45,.37,.24,'gem',index)
    return mesh

def png(image):
    b=io.BytesIO();image.save(b,format='PNG');return b.getvalue()

def palette():
    image=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(image)
    for start,color in [(0,(221,172,57)),(64,(202,221,231))]:
        for y in range(64):
            factor=.68+.38*(1-y/63)+.12*math.sin(y*.3)
            d.line((start,y,start+63,y),fill=tuple(min(255,int(c*factor)) for c in color)+(255,))
        for y in (1,15,31,47):d.line((start,y,start+63,y),fill=(255,241,190,255) if start==0 else (246,253,255,255))
    for i,g in enumerate(GEMS):
        x=i%32*8;y=128+i//32*8;rgb=tuple(bytes.fromhex(g['color']))
        for sy in range(8):
            for sx in range(8):
                factor=1.35 if sx+sy<5 else .92 if sx<4 else .6
                image.putpixel((x+sx,y+sy),tuple(min(255,int(c*factor)) for c in rgb)+(255,))
        d.point((x+1,y+1),fill=(255,255,255,255))
    return image

def build():
    out={};mesh=geometry()
    def js(path,obj):out[path]=(json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf8')
    def recipe(key,obj):js(DATA+'recipes/eternity/'+key+'.json',obj)
    def shaped(key,pattern,keys,result,count=1):recipe(key,{'type':'minecraft:crafting_shaped','category':'equipment','pattern':pattern,'key':{k:{'item':v} for k,v in keys.items()},'result':{'item':NS+result,'count':count}})
    def item_model(key,elements,textures=None):
        js(ASSET+'models/item/'+key+'.json',{'textures':textures or {'0':'alfheim_companion:models/armor/eternity_crown'},'elements':elements,'display':{'gui':{'rotation':[25,35,0],'translation':[0,2,0],'scale':[1.35,1.35,1.35]},'ground':{'translation':[0,2,0],'scale':[.6,.6,.6]},'fixed':{'rotation':[0,180,0]},'thirdperson_righthand':{'rotation':[75,45,0],'scale':[.5,.5,.5]},'firstperson_righthand':{'rotation':[0,45,0],'scale':[.7,.7,.7]}}})
    def element(e):
        u,v=e['uv'];size=4 if 'gem' in e else 12
        return {'from':e['from'],'to':e['to'],'faces':{f:{'texture':'#0','uv':[u/16,v/16,(u+size)/16,(v+size)/16]} for f in ('north','south','east','west','up','down')}}
    js(ASSET+'crown_geometry.json',mesh)
    out[ASSET+'textures/models/armor/eternity_crown.png']=png(palette())
    for count in range(30):
        key='crown_of_eternity' if count==29 else f'eternity/crown_{count:02d}'
        item_model(key,[element(e) for e in mesh if 'gem' not in e or e['gem']<count*8])
    js(ASSET+'models/item/gold_platinum_crown.json',{'parent':'alfheim_companion:item/eternity/crown_00','overrides':[{'predicate':{'alfheim_companion:inlays':n},'model':f'alfheim_companion:item/eternity/crown_{n:02d}'} for n in range(1,29)]})
    # Native geometric components share the same metal palette as the worn crown.
    def block(a,b,uv=(64,0)):
        return element({'from':a,'to':b,'uv':uv})
    item_model('platinum_ingot',[block([3,6,5],[13,9,11]),block([4,9,6],[12,9.5,10])])
    item_model('platinum_billet',[block([3,3,3],[13,13,13]),block([2.8,5,2.8],[13.2,5.5,13.2],(0,0)),block([2.8,10.5,2.8],[13.2,11,13.2],(0,0))])
    item_model('platinum_concentrate',[block([3,4,4],[13,8,12],(0,0)),block([5,8,6],[11,11,10]),block([2,5,6],[5,9,9]),block([10,7,8],[14,10,11],(0,0))])
    item_model('royal_crown_segment',[block([3,3,6],[13,7,10],(0,0)),block([2.8,3,5.8],[13.2,3.5,10.2]),block([2.8,6.5,5.8],[13.2,7,10.2]),block([7,7,7],[9,13,9],(0,0)),block([6.5,12,6.5],[9.5,13,9.5])])
    item_model('eternity_setter',[block([5,2,7],[6.3,10,8.3],(0,0)),block([9.7,2,7],[11,10,8.3],(0,0)),block([5.8,9,7],[7.2,13,8.3]),block([8.8,9,7],[10.2,13,8.3]),block([6.8,12.5,7],[7.5,15,8.3]),block([8.5,12.5,7],[9.2,15,8.3]),block([5,1.5,6.8],[11,3,8.5],(0,0)),block([6.5,7,6.8],[9.5,8.5,8.5])])
    # Platinum is concentrated from vast amounts of auriferous raw material, not added as free ore.
    shaped('concentrate',['GGG','GBG','GGG'],{'G':'minecraft:raw_gold_block','B':'minecraft:blaze_powder'},'platinum_concentrate')
    recipe('refine_platinum',{'type':'minecraft:blasting','ingredient':{'item':NS+'platinum_concentrate'},'result':NS+'platinum_ingot','experience':3,'cookingtime':1200})
    shaped('platinum_billet',['PPP','PPP','PPP'],{'P':NS+'platinum_ingot'},'platinum_billet')
    recipe('unpack_platinum',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':NS+'platinum_billet'}],'result':{'item':NS+'platinum_ingot','count':9}})
    shaped('royal_crown_segment',['GGG','GPG','GGG'],{'G':'minecraft:gold_block','P':NS+'platinum_billet'},'royal_crown_segment')
    shaped('gold_platinum_crown',['SSS','SNS','SSS'],{'S':NS+'royal_crown_segment','N':'minecraft:nether_star'},'gold_platinum_crown')
    shaped('eternity_setter',['D D',' P ',' B '],{'D':'minecraft:diamond','P':NS+'platinum_ingot','B':'minecraft:blaze_rod'},'eternity_setter')
    for i,gems in enumerate(LAYERS):
        key=f'eternity_inlay_{i+1:02d}'
        keys={str(n):g['item'] for n,g in enumerate(gems)};keys['P']=NS+'platinum_ingot'
        shaped(key,['012','3P4','567'],keys,key)
        recipe(f'set_inlay_{i+1:02d}',{'type':NS+'crown_setting','category':'equipment','required_inlays':i,'ingredients':[{'item':NS+'gold_platinum_crown'},{'item':NS+'eternity_setter'},{'item':NS+key}],'result':{'item':NS+('crown_of_eternity' if i==28 else 'gold_platinum_crown')}})
        positions=[(3,11),(7,11),(11,11),(3,7),(11,7),(3,3),(7,3),(11,3)]
        elems=[block([2.5,2.5,7],[13.5,3,8]),block([2.5,13,7],[13.5,13.5,8]),block([2.5,3,7],[3,13,8]),block([13,3,7],[13.5,13,8]),block([6,6,7],[10,10,8])]
        textures={'0':'alfheim_companion:models/armor/eternity_crown'}
        for n,(g,(x,y)) in enumerate(zip(gems,positions)):
            textures[str(n+1)]=('minecraft:item/'+g['item'].split(':')[1]) if g['item'].startswith('minecraft:') else 'alfheim:item/gemstones/'+g['id']
            elems.append({'from':[x-1.6,y-1.6,6.9],'to':[x+1.6,y+1.6,7],'faces':{f:{'texture':'#'+str(n+1),'uv':[0,0,16,16],'tintindex':n} for f in ('north','south')}})
        item_model(key,elems,textures)
    js(DATA+'tags/items/platinum_ingots.json',{'replace':False,'values':[NS+'platinum_ingot']})
    js(RES+'data/forge/tags/items/ingots/platinum.json',{'replace':False,'values':[NS+'platinum_ingot']})
    js(RES+'data/forge/tags/items/ingots.json',{'replace':False,'values':[NS+'platinum_ingot']})
    lang=json.loads((ROOT/ASSET/'lang/en_us.json').read_text('utf8'))
    names={'platinum_ingot':'Platinum Ingot','platinum_billet':'Dense Platinum Billet','platinum_concentrate':'Auriferous Platinum Concentrate','royal_crown_segment':'Royal Gold and Platinum Crown Segment','eternity_setter':"Jeweller's Eternity Setter",'gold_platinum_crown':'Gold and Platinum Crown','crown_of_eternity':'Crown of Eternity'}
    names.update({f'eternity_inlay_{i+1:02d}':f'Eternity Inlay {i+1}' for i in range(29)})
    lang.update({'item.alfheim_companion.'+k:v for k,v in names.items()});js(ASSET+'lang/en_us.json',lang)
    js(DATA+'advancements/eternity/completed.json',{'display':{'icon':{'item':NS+'crown_of_eternity'},'title':'Crown of Eternity','description':'Set one of every gemstone into the gold and platinum crown.','frame':'challenge','show_toast':True,'announce_to_chat':True,'hidden':True,'background':'minecraft:textures/block/gilded_blackstone.png'},'criteria':{'crown':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':[NS+'crown_of_eternity']}]}}}})
    # Unlock all inlay recipes after obtaining the crown, and the metal route after finding raw gold.
    for name,item,recipes in [('inlays','gold_platinum_crown',[NS+'eternity/'+f'eternity_inlay_{i+1:02d}' for i in range(29)]+[NS+'eternity/'+f'set_inlay_{i+1:02d}' for i in range(29)]),('metal','minecraft:raw_gold',[NS+'eternity/'+k for k in ('concentrate','refine_platinum','platinum_billet','unpack_platinum','royal_crown_segment','gold_platinum_crown','eternity_setter')])]:
        js(DATA+'advancements/recipes/eternity/'+name+'.json',{'criteria':{'has_item':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':[item if ':' in item else NS+item]}]}}},'rewards':{'recipes':recipes}})
    manifest={'gems':[g['item'] for g in GEMS],'layers':[[g['item'] for g in group] for group in LAYERS],'gem_count':232,'inlay_count':29,'setting_tool_reusable':True,'wearable':True,'cost':{'gold_blocks':64,'platinum_ingots_in_crown':101,'platinum_ingots_in_tool':1,'raw_gold_blocks_for_all_platinum':816,'nether_stars':1,'extra_diamonds_for_tool':2,'gems_inset':232},'native_mesh_gem_count':sum('gem' in e for e in mesh),'native_items':list(names),'runtime':'Crafting, recipe transfer, reload, equip and multiplayer synchronization pending in game'}
    return out,manifest

class Provider:
    provider_id='alfheim_eternity_crown_v1';aliases=('alfheim_eternity_crown',)
    def __init__(self,out):self.out=out
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases)}
    def generate(self,request,resolver):
        probes={}
        for key in ['minecraft:raw_gold_block','minecraft:blaze_powder','minecraft:blaze_rod','minecraft:gold_block','minecraft:nether_star','minecraft:diamond']:
            probes[key]=resolver.probe(key,kind='item');assert probes[key]['level'] in ('vanilla','exact'),probes[key]
        return {'provider_id':self.provider_id,'status':'GENERATED_NOT_VALIDATED','generated_layout':{'files':[{'file':rel,'sha256':hashlib.sha256(data).hexdigest()} for rel,data in self.out.items()],'registry_probes':probes,'inlay_count':29,'gem_count':232},'structure_artifact':{'format':'minecraft_datapack','piece_count':0},'artifact_bytes':{rel.replace('/','_'):data for rel,data in self.out.items()}}

def main():
    out,manifest=build()
    if '--check' in sys.argv:
        for rel,data in out.items():assert (ROOT/rel).read_bytes()==data,rel
        print('CROWN GENERATED SOURCE EQUALITY PASS',len(out));return
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=ROOT/'build/eternity_crown/snapshots')
    cap.inventory.add_registry_ids(json.loads((ROOT/'server/local/kubejs/export/registries/item.json').read_text()),kind='item')
    cap.register_generator(Provider(out))
    result=cap.generate({'structure_id':'alfheim_companion:eternity_crown','target_version':'1.20.1','grade':3,'purpose':{'kind':'catalogue_complete_crown_crafting','required_zones':['precious metal refining','gem inlays','wearable crown']},'generation':{'kind':'alfheim_eternity_crown','materialize_nbt':False}})
    for rel,data in out.items():p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (ROOT/'tools/eternity_crown_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'tools/eternity_crown_generation.json').write_text(json.dumps({'capability':'Continuity Works','snapshot_id':result['snapshot']['snapshot_id'],'generation':result['generation'],'layout':result['generated_layout'],'placement_contract':'No structures or world-generation changes'},indent=2)+'\n')
    print('CW emitted',len(out),'files; 29 inlays, 232 unique gemstone settings')

if __name__=='__main__':main()
