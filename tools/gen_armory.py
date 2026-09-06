"""Generate the Reclaimed Armory: items, textures, models, armor skins, MMO data and recipes.

The six AI-generated source atlases are production references. This script removes their
backgrounds with a border-connected flood fill, then crops, cleans, resizes and recolours the art.
The source atlases are preserved byte-for-byte under the design record.

    python tools/gen_armory.py
    python tools/gen_armory.py --check
"""
from collections import deque
import argparse, colorsys, hashlib, json, os, shutil, zipfile
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
NS = 'alfheim'
ART = ROOT/'alfheim_reclaimed_design/armory/source_art'
TEX = ROOT/'kubejs/assets/alfheim/textures/item/armory'
MODELS = ROOT/'kubejs/assets/alfheim/models/item/armory'
ARMOR = ROOT/'kubejs/assets/alfheim/textures/models/armor'
DATA = ROOT/'kubejs/data/alfheim'
STARTUP = ROOT/'kubejs/startup_scripts/17_armory.js'
LANG = ROOT/'kubejs/assets/alfheim/lang/en_us.json'
MANIFEST_OUT = ROOT/'tools/armory_manifest.json'
CLIENT_JAR = Path(r'C:/Users/Admin/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar')

SOURCES = {
 'warrior': ('thornwarden-atlas-source-v1.png', 'Thornwarden'),
 'hunter': ('waywatcher-atlas-source-v2.png', 'Waywatcher'),
 'sorcerer': ('leyweaver-atlas-source-v1.png', 'Leyweaver'),
 'shaman': ('rootspeaker-atlas-source-v1.png', 'Rootspeaker'),
 'warlock': ('duskkeeper-atlas-source-v1.png', 'Duskkeeper'),
 'minstrel': ('dawnsinger-atlas-source-v1.png', 'Dawnsinger'),
}
GRADES = [
 (1,'Dreamwood','botania:dreamwood_log',0,40,0.78,['common']),
 (2,'Quickened','alfheim:quickened_palebloom',0,80,0.42,['common','uncommon']),
 (3,'Verdant','alfheim:verdant_filament',1,115,0.30,['uncommon','rare']),
 (4,'Gatewrought','alfheim:gatewrought_cord',1,150,0.14,['uncommon','rare']),
 (5,'Elementium','alfheim:elementium_core',2,190,0.90,['rare','epic']),
 (6,'Wildmarch','alfheim:wildmarch_sinew',2,230,0.52,['rare','epic']),
 (7,'Emberbound','alfheim:emberbound_weave',3,280,0.05,['epic','legendary']),
 (8,'Rimebound','alfheim:rimebound_lattice',4,340,0.53,['epic','legendary']),
 (9,'Grave-Gilt','alfheim:gravegilt_thread',4,410,0.78,['legendary','mythic']),
 (10,'Crown','alfheim:crown_filament',5,500,0.14,['legendary','mythic']),
]
FAMILIES = {
 'warrior': [('blade','sword'),('axe','axe'),('spear','trident'),('ward','shield')],
 'hunter': [('bow','bow'),('crossbow','crossbow'),('blade','sword'),('charm','totem')],
 'sorcerer': [('focus','staff'),('blade','sword'),('spear','trident'),('folio','tome')],
 'shaman': [('focus','staff'),('spear','trident'),('axe','axe'),('ward','tome')],
 'warlock': [('focus','staff'),('blade','sword'),('bow','bow'),('folio','tome')],
 'minstrel': [('focus','staff'),('blade','sword'),('crossbow','crossbow'),('folio','tome')],
}
ARMOR_META = {
 'warrior': ('plate','Boughguard',['Leaf Helm','Bark Cuirass','Root Tassets','March Sabatons'],'rootglass_shard'),
 'hunter': ('leather','Waywatcher',['Trail Hood','Leaf Jerkin','Briar Leggings','Silent Boots'],'galeglass_shard'),
 'sorcerer': ('cloth','Leyweaver',['Prism Circlet','Ley Robe','Starweave Leggings','Glassstep Boots'],'emberglass_shard'),
 'shaman': ('cloth','Rootspeaker',['Antler Crown','Rain Mantle','Rootweave Leggings','Fenwalk Boots'],'rootglass_shard'),
 'warlock': ('cloth','Duskkeeper',['Mourning Veil','Memory Vestment','Graveweave Leggings','Hushstep Boots'],'duskglass_shard'),
 'minstrel': ('cloth','Dawnsinger',['Laurel Circlet','Chorus Coat','Ribbon Leggings','Courtstep Boots'],'dawnglass_shard'),
}
NAMES = {
 'warrior': [['Leafknife','Boughblade','Crownleaf Falchion'],['Root Hatchet','Thorncleaver','Greatbole Crescent'],['Reed Spear','Branchguard Trident','Ninebough Glaive'],['Bark Buckler','Leafguard Shield','Hollow Court Aegis']],
 'hunter': [['Twig Bow','Grove Recurve','Wildmarch Greatbow'],['Bough Crossbow','Thornstock Arbalest','Galeglass Windlass'],['Trailknife','Briar Sabre','Moonbranch Fang'],['Leaf Charm','Waywatcher Ward','Spiritwolf Crest']],
 'sorcerer': [['Leybranch','Crystal Spire','Sixfold Conductor'],['Rune Knife','Ley Sabre','Starfall Falchion'],['Glass Spear','Prism Trident','Comet Fork'],['Bark Folio','Ley Atlas','Archive of Returning Stars']],
 'shaman': [['Rainbranch','Stormroot Crook','Worldroot Conductor'],['Tide Spear','Raincaller Trident','Stormtide Glaive'],['Grove Hatchet','Rootwarden Crescent','Tempest Boughcleaver'],['Root Tablet','Rainward Tablet','Memory of the First Grove']],
 'warlock': [['Hushbranch','Mourning Crook','Ancestor Reliquary'],['Dusk Knife','Grief Sabre','Last-Oath Falchion'],['Gloam Bow','Widow Recurve','Pale Procession Greatbow'],['Nameleaf Folio','Mourning Ledger','Book of Unforgotten Names']],
 'minstrel': [['Tuning Branch','Chorus Fork','Greatbole Resonator'],['Danceknife','Ribbon Rapier','Dawncourt Estoc'],['Chord Crossbow','Harpstock Arbalest','Dawnchorus Ballista'],['Songleaf','Court Songbook','Canticle of the Reclaimed']],
}
SLOTS = ['helmet','chest','pants','boots']

def is_bg(rgb):
    r,g,b=rgb; return (max(rgb)-min(rgb) <= 34 and max(rgb) >= 178) or min(rgb)>=235

def remove_connected_background(im):
    """Remove only light neutral pixels connected to the canvas edge; outlined white art survives."""
    im=im.convert('RGBA'); w,h=im.size; px=im.load(); seen=bytearray(w*h); q=deque()
    for x in range(w):
        for y in (0,h-1):
            i=y*w+x
            if px[x,y][3] < 16 or is_bg(px[x,y][:3]): seen[i]=1;q.append((x,y))
    for y in range(h):
        for x in (0,w-1):
            i=y*w+x
            if px[x,y][3] < 16 or is_bg(px[x,y][:3]): seen[i]=1;q.append((x,y))
    while q:
        x,y=q.popleft()
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<w and 0<=ny<h:
                i=ny*w+nx
                if not seen[i] and (px[nx,ny][3] < 16 or is_bg(px[nx,ny][:3])):
                    seen[i]=1;q.append((nx,ny))
    out=im.copy(); op=out.load()
    for i,v in enumerate(seen):
        if v: op[i%w,i//w]=(0,0,0,0)
    # The generator sometimes writes max alpha 254. Normalize useful foreground opacity.
    for y in range(h):
        for x in range(w):
            r,g,b,a=op[x,y]
            if a and a>235: op[x,y]=(r,g,b,255)
    return out

def remove_large_enclosed_background(im, min_area=1000):
    """Clear fake background islands trapped inside a closed silhouette such as a bow/string."""
    out=im.convert('RGBA').copy(); px=out.load(); w,h=out.size; seen=bytearray(w*h)
    for y in range(h):
      for x in range(w):
        start=y*w+x
        if seen[start] or not px[x,y][3] or not is_bg(px[x,y][:3]): continue
        q=deque([(x,y)]);seen[start]=1;component=[]
        while q:
            cx,cy=q.popleft();component.append((cx,cy))
            for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                if 0<=nx<w and 0<=ny<h:
                    i=ny*w+nx
                    if not seen[i] and px[nx,ny][3] and is_bg(px[nx,ny][:3]):
                        seen[i]=1;q.append((nx,ny))
        if len(component)>=min_area:
            for cx,cy in component:px[cx,cy]=(0,0,0,0)
    return out

def tint(im,target,amount):
    out=Image.new('RGBA',im.size); a=im.convert('RGBA').load(); b=out.load()
    for y in range(im.height):
      for x in range(im.width):
        r,g,bl,al=a[x,y]
        if not al: continue
        h,s,v=colorsys.rgb_to_hsv(r/255,g/255,bl/255)
        if s>.12:
            d=((target-h+0.5)%1)-0.5; h=(h+d*amount)%1; s=min(1,s*(0.94+amount*.28))
        nr,ng,nb=colorsys.hsv_to_rgb(h,s,v);b[x,y]=(round(nr*255),round(ng*255),round(nb*255),al)
    return out

def icon(cell):
    box=cell.getbbox()
    if not box:return Image.new('RGBA',(32,32))
    obj=cell.crop(box); obj.thumbnail((29,29),Image.Resampling.LANCZOS)
    out=Image.new('RGBA',(32,32));out.alpha_composite(obj,((32-obj.width)//2,(32-obj.height)//2))
    out=out.quantize(colors=56,method=Image.Quantize.FASTOCTREE).convert('RGBA')
    # Palette quantization can turn fully transparent pixels into alpha 1–2. Strip that
    # numerical haze so the exported canvas has literal RGBA (0, 0, 0, 0) background.
    px=out.load()
    for y in range(out.height):
      for x in range(out.width):
        r,g,b,a=px[x,y]
        if a<=16:px[x,y]=(0,0,0,0)
        elif a>=240:px[x,y]=(r,g,b,255)
    return out

def largest_enclosed_transparent_region(im):
    """Return the largest alpha-zero island that cannot reach the canvas edge."""
    alpha=im.convert('RGBA').getchannel('A'); w,h=im.size; seen=bytearray(w*h); largest=0
    for y in range(h):
      for x in range(w):
        start=y*w+x
        if seen[start] or alpha.getpixel((x,y))!=0:continue
        q=deque([(x,y)]);seen[start]=1;size=0;edge=False
        while q:
            cx,cy=q.popleft();size+=1;edge=edge or cx in (0,w-1) or cy in (0,h-1)
            for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                if 0<=nx<w and 0<=ny<h:
                    i=ny*w+nx
                    if not seen[i] and alpha.getpixel((nx,ny))==0:
                        seen[i]=1;q.append((nx,ny))
        if not edge:largest=max(largest,size)
    return largest

def keep_largest_foreground_component(im):
    """Remove detached atlas spill while preserving the principal connected item silhouette."""
    out=im.convert('RGBA').copy(); alpha=out.getchannel('A'); w,h=out.size; seen=bytearray(w*h); groups=[]
    for y in range(h):
      for x in range(w):
        start=y*w+x
        if seen[start] or alpha.getpixel((x,y))==0:continue
        q=deque([(x,y)]);seen[start]=1;group=[]
        while q:
            cx,cy=q.popleft();group.append((cx,cy))
            for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1),(cx-1,cy-1),(cx+1,cy-1),(cx-1,cy+1),(cx+1,cy+1)):
                if 0<=nx<w and 0<=ny<h:
                    i=ny*w+nx
                    if not seen[i] and alpha.getpixel((nx,ny))>0:
                        seen[i]=1;q.append((nx,ny))
        groups.append(group)
    if groups:
        keep=set(max(groups,key=len));px=out.load()
        for group in groups:
            if set(group)==keep:continue
            for x,y in group:px[x,y]=(0,0,0,0)
    return out

def remove_detached_horizontal_edge_spill(im):
    """Remove small neighbouring-atlas fragments crossing a cell's left/right cut lines.

    The principal silhouette is always preserved, even when it legitimately reaches an edge.
    Interior detached details are also preserved; only secondary components touching a vertical
    crop edge are discarded before the icon is resized and centred.
    """
    out=im.convert('RGBA').copy(); alpha=out.getchannel('A'); w,h=out.size; seen=bytearray(w*h); groups=[]
    for y in range(h):
      for x in range(w):
        start=y*w+x
        if seen[start] or alpha.getpixel((x,y))==0:continue
        q=deque([(x,y)]);seen[start]=1;group=[]
        while q:
            cx,cy=q.popleft();group.append((cx,cy))
            for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1),(cx-1,cy-1),(cx+1,cy-1),(cx-1,cy+1),(cx+1,cy+1)):
                if 0<=nx<w and 0<=ny<h:
                    i=ny*w+nx
                    if not seen[i] and alpha.getpixel((nx,ny))>0:
                        seen[i]=1;q.append((nx,ny))
        groups.append(group)
    if not groups:return out
    keep=max(groups,key=len); edge=max(1,w//64); px=out.load()
    for group in groups:
        if group is keep:continue
        xs=[p[0] for p in group]
        if min(xs)<=edge or max(xs)>=w-1-edge:
            for x,y in group:px[x,y]=(0,0,0,0)
    return out

def foreground_component_count(im):
    alpha=im.convert('RGBA').getchannel('A');w,h=im.size;seen=bytearray(w*h);count=0
    for y in range(h):
      for x in range(w):
        start=y*w+x
        if seen[start] or alpha.getpixel((x,y))==0:continue
        count+=1;q=deque([(x,y)]);seen[start]=1
        while q:
            cx,cy=q.popleft()
            for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1),(cx-1,cy-1),(cx+1,cy-1),(cx-1,cy+1),(cx+1,cy+1)):
                if 0<=nx<w and 0<=ny<h:
                    i=ny*w+nx
                    if not seen[i] and alpha.getpixel((nx,ny))>0:
                        seen[i]=1;q.append((nx,ny))
    return count

def model(parent,texture,overrides=None):
    d={'parent':parent,'textures':{'layer0':texture}}
    if overrides:d['overrides']=overrides
    return d

def base_type(template,new_id,items,weapon=None):
    d=json.loads(json.dumps(template)); d['guid']=new_id; d['weight']=0
    d['possible_items']=[{'item_id':i,'min_rar':'common','weight':1000} for i in items]
    if weapon:
        d['weapon_type']=weapon
        if weapon=='axe': d['tags']['tags']=[('axe' if x=='sword' else x) for x in d['tags']['tags']]
    return d

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main(check=False):
    catalog=json.loads((ROOT/'alfheim_reclaimed_design/armory/equipment_catalog.json').read_text(encoding='utf-8'))
    entries={e['proposed_id']:e for e in catalog['equipment']}
    for p in [TEX,MODELS,ARMOR,DATA/'mmorpg_base_gear_types',DATA/'mmorpg_auto_item',DATA/'mmorpg_custom_item',DATA/'mmorpg_profession_recipe']:
        if p.exists() and not check: shutil.rmtree(p)
        if not check:p.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ROOT/'mods/Mine_and_Slash-1.20.1-6.4.7.jar') as z:
        bases={n.rsplit('/',1)[-1][:-5]:json.loads(z.read(n)) for n in z.namelist() if n.startswith('data/mmorpg/mmorpg_base_gear_types/') and n.endswith('.json')}
    with zipfile.ZipFile(CLIENT_JAR) as z:
        armor_base={}
        for layer in (1,2):
            with z.open(f'assets/minecraft/textures/models/armor/leather_layer_{layer}.png') as f: armor_base[layer]=Image.open(f).convert('RGBA').copy()
    generated=[]; source_meta={}
    startup=["// GENERATED by tools/gen_armory.py — do not hand-edit.","const $BowItem = Java.loadClass('net.minecraft.world.item.BowItem')","const $CrossbowItem = Java.loadClass('net.minecraft.world.item.CrossbowItem')","const $TridentItem = Java.loadClass('net.minecraft.world.item.TridentItem')","const $ShieldItem = Java.loadClass('net.minecraft.world.item.ShieldItem')","const $ItemProperties = Java.loadClass('net.minecraft.world.item.Item$Properties')","", "StartupEvents.registry('item', event => {"]
    # en_us.json is shared by several generators. Update armory-owned keys in place
    # so a texture/item regeneration cannot erase biome or entity names.
    lang=json.loads(LANG.read_text(encoding='utf-8')) if LANG.exists() else {}
    for school,(filename,title) in SOURCES.items():
        raw=Image.open(ART/filename).convert('RGBA'); cleaned=remove_connected_background(raw)
        clean_path=ART/(filename.replace('-source-v1','-clean').replace('-source-v2','-clean'))
        if not check: cleaned.save(clean_path)
        ca=cleaned.getchannel('A'); hist=ca.histogram(); transparent=hist[0]/(cleaned.width*cleaned.height)
        assert ca.getpixel((0,0))==0 and ca.getpixel((cleaned.width-1,cleaned.height-1))==0 and transparent>.35, (school,transparent)
        source_meta[school]={'source':filename,'source_sha256':hashlib.sha256((ART/filename).read_bytes()).hexdigest(),'cleaned':clean_path.name,'transparent_fraction':round(transparent,4)}
        cw,ch=cleaned.width//8,cleaned.height//3
        family_ids=[]
        for col,(family,gear_type) in enumerate(FAMILIES[school]):
            ids=[]
            for era,grade,material,prof_tier,dur,hue,rars in GRADES:
                stage=0 if era<=2 else 1 if era<=6 else 2
                iid=f'alfheim:armory/{school}/{family}/era_{era:02}'; path=iid.split(':',1)[1]
                display=f'{grade} {NAMES[school][col][stage]}'; ids.append(iid);generated.append(iid)
                cell=cleaned.crop((col*cw,stage*ch,(col+1)*cw,(stage+1)*ch))
                cell=remove_detached_horizontal_edge_spill(cell)
                if gear_type=='bow':cell=remove_large_enclosed_background(cell,1000)
                elif gear_type=='crossbow':cell=remove_large_enclosed_background(cell,600)
                elif school=='hunter' and family=='charm':cell=remove_large_enclosed_background(cell,1000)
                base_icon=icon(cell)
                if school=='hunter' and family=='charm':base_icon=keep_largest_foreground_component(base_icon)
                tex=tint(base_icon,hue,.14+.018*era)
                if not check:
                    tp=TEX/school/family/f'era_{era:02}.png';tp.parent.mkdir(parents=True,exist_ok=True);tex.save(tp)
                    parent='minecraft:item/handheld' if gear_type in ['sword','axe','trident','staff'] else 'minecraft:item/generated'
                    ovs=None
                    write(MODELS/school/family/f'era_{era:02}.json',model(parent,f'alfheim:item/{path}',ovs))
                key=f'item.alfheim.{path.replace("/",".")}';lang[key]=display
                if gear_type in ['bow','crossbow','trident','shield']:
                    cls={'bow':'$BowItem','crossbow':'$CrossbowItem','trident':'$TridentItem','shield':'$ShieldItem'}[gear_type]
                    startup.append(f"    event.createCustom('{iid}', () => new {cls}(new $ItemProperties().durability({dur})))")
                elif gear_type=='sword': startup.append(f"    event.create('{iid}', 'sword').tier('iron').maxDamage({dur})")
                elif gear_type=='axe': startup.append(f"    event.create('{iid}', 'axe').tier('iron').maxDamage({dur})")
                else: startup.append(f"    event.create('{iid}').unstackable().maxDamage({dur})")
                gen=f'alfheim_{school}_{family}_era_{era:02}'
                if not check:
                    write(DATA/'mmorpg_custom_item'/f'{gen}.json',{'id':gen,'min_lvl':1,'max_lvl':100,'possible_rar':rars,'uniq_id':'','gear_type':f'alfheim_{school}_{family}','disable_salvaging':False})
                    write(DATA/'mmorpg_auto_item'/f'{gen}.json',{'id':gen,'weight':1000,'item_id':iid,'custom_item_generation':gen})
                    mats=[{'type':'ITEM','id':material,'num':1},{'type':'ITEM','id':f'mmorpg:material/mining/{prof_tier}','num':1},{'type':'ITEM','id':f'mmorpg:stone/{prof_tier}','num':1}]
                    if era>=3:mats.append({'type':'ITEM','id':f'alfheim:{ARMOR_META[school][3]}','num':1})
                    write(DATA/'mmorpg_profession_recipe'/f'{gen}.json',{'exp':100+prof_tier*50,'id':gen,'mats':mats,'profession':'gear_crafting','requires_pinnacle_unlock':era==10,'result':iid,'result_num':1,'set_tier_nbt':False,'tier':prof_tier})
            family_ids.append((family,gear_type,ids))
            template='sword' if gear_type=='axe' else gear_type
            type_id=f'alfheim_{school}_{family}'
            lang[f'mmorpg.gear_type.{type_id}']=f'{title} {family.title()}'
            if not check:write(DATA/'mmorpg_base_gear_types'/f'{type_id}.json',base_type(bases[template],type_id,ids,'axe' if gear_type=='axe' else None))
        armor_kind,setname,pieces,crystal=ARMOR_META[school]
        for slot,col,piece in zip(SLOTS,range(4,8),pieces):
            ids=[]
            for era,grade,material,prof_tier,dur,hue,rars in GRADES:
                stage=0 if era<=2 else 1 if era<=6 else 2
                iid=f'alfheim:armory/{school}/{slot}/era_{era:02}';path=iid.split(':',1)[1];ids.append(iid);generated.append(iid)
                cell=cleaned.crop((col*cw,stage*ch,(col+1)*cw,(stage+1)*ch))
                cell=remove_detached_horizontal_edge_spill(cell)
                tex=tint(icon(cell),hue,.14+.018*era)
                if not check:
                    tp=TEX/school/slot/f'era_{era:02}.png';tp.parent.mkdir(parents=True,exist_ok=True);tex.save(tp)
                    write(MODELS/school/slot/f'era_{era:02}.json',model('minecraft:item/generated',f'alfheim:item/{path}'))
                lang[f'item.alfheim.{path.replace("/",".")}']=f'{grade} {piece}'
                builder_type={'chest':'chestplate', 'pants':'leggings'}.get(slot, slot)
                startup.append(f"    event.create('{iid}', '{builder_type}').tier('iron').maxDamage({dur}).modifyTier(t => t.setName('alfheim:{school}_era_{era:02}'))")
                gen=f'alfheim_{school}_{slot}_era_{era:02}'
                if not check:
                    write(DATA/'mmorpg_custom_item'/f'{gen}.json',{'id':gen,'min_lvl':1,'max_lvl':100,'possible_rar':rars,'uniq_id':'','gear_type':f'alfheim_{school}_{slot}','disable_salvaging':False})
                    write(DATA/'mmorpg_auto_item'/f'{gen}.json',{'id':gen,'weight':1000,'item_id':iid,'custom_item_generation':gen})
                    count=2 if slot in ['chest','pants'] else 1
                    mats=[{'type':'ITEM','id':material,'num':count},{'type':'ITEM','id':f'mmorpg:material/mining/{prof_tier}','num':1},{'type':'ITEM','id':f'mmorpg:stone/{prof_tier}','num':1}]
                    if era>=3:mats.append({'type':'ITEM','id':f'alfheim:{crystal}','num':1})
                    write(DATA/'mmorpg_profession_recipe'/f'{gen}.json',{'exp':100+prof_tier*50,'id':gen,'mats':mats,'profession':'gear_crafting','requires_pinnacle_unlock':era==10,'result':iid,'result_num':1,'set_tier_nbt':False,'tier':prof_tier})
            type_id=f'alfheim_{school}_{slot}'
            lang[f'mmorpg.gear_type.{type_id}']=f'{title} {slot.title()}'
            if not check:write(DATA/'mmorpg_base_gear_types'/f'{type_id}.json',base_type(bases[f'{armor_kind}_{slot}'],type_id,ids))
        # Worn layers use the generated armor art as actual pattern/color source within Mojang's UV mask.
        for era,grade,material,prof_tier,dur,hue,rars in GRADES:
            stage=0 if era<=2 else 1 if era<=6 else 2
            art=cleaned.crop((4*cw,stage*ch,8*cw,(stage+1)*ch)).resize((64,32),Image.Resampling.LANCZOS)
            art=tint(art,hue,.14+.018*era)
            for layer in (1,2):
                base=armor_base[layer]; out=Image.new('RGBA',(64,32));bp=base.load();ap=art.load();op=out.load()
                for y in range(32):
                  for x in range(64):
                    br,bg,bb,ba=bp[x,y]
                    if not ba:continue
                    ar,ag,ab,aa=ap[x,y]; shade=(br+bg+bb)/(3*255)
                    if aa<24: ar,ag,ab=(75,100,65) if school in ['warrior','hunter','shaman'] else (70,65,90)
                    op[x,y]=(round(ar*(.45+.55*shade)),round(ag*(.45+.55*shade)),round(ab*(.45+.55*shade)),ba)
                if not check: out.quantize(colors=64,method=Image.Quantize.FASTOCTREE).convert('RGBA').save(ARMOR/f'{school}_era_{era:02}_layer_{layer}.png')
    startup+=['})','']
    assert len(generated)==len(set(generated))==480
    item_paths=list(TEX.rglob('*.png'))
    assert len(item_paths)==480
    for path in item_paths:
        im=Image.open(path).convert('RGBA'); alpha=im.getchannel('A'); hist=alpha.histogram()
        assert im.size==(32,32), (path,im.size)
        corners=[alpha.getpixel(p) for p in ((0,0),(31,0),(0,31),(31,31))]
        assert not any(corners), (path,'nontransparent corner',corners)
        assert hist[0]>=20 and sum(hist[1:])>=20, (path,'invalid foreground/background alpha')
    bow_holes=[]
    for school in ('hunter','warlock'):
        for era in range(1,11):
            path=TEX/school/'bow'/f'era_{era:02}.png'
            hole=largest_enclosed_transparent_region(Image.open(path))
            assert hole>=20, (path,'bow interior is not transparent',hole)
            bow_holes.append(hole)
    crossbow_holes=[]
    for school in ('hunter','minstrel'):
        for era in range(1,11):
            path=TEX/school/'crossbow'/f'era_{era:02}.png'
            hole=largest_enclosed_transparent_region(Image.open(path))
            assert hole>=10, (path,'crossbow interior is not transparent',hole)
            crossbow_holes.append(hole)
    charm_holes=[]
    for era in range(1,11):
        path=TEX/'hunter'/'charm'/f'era_{era:02}.png'
        charm=Image.open(path);hole=largest_enclosed_transparent_region(charm)
        assert hole>=10, (path,'necklace interior is not transparent',hole)
        assert foreground_component_count(charm)==1, (path,'detached necklace atlas spill remains')
        charm_holes.append(hole)
    assert len(list(MODELS.rglob('*.json')))==480
    assert len(list((DATA/'mmorpg_base_gear_types').glob('*.json')))==48
    for folder in ('mmorpg_auto_item','mmorpg_custom_item','mmorpg_profession_recipe'):
        assert len(list((DATA/folder).glob('*.json')))==480, folder
    alpha_audit={}
    for school in SOURCES:
        fractions=[]
        for path in (TEX/school).rglob('*.png'):
            im=Image.open(path).convert('RGBA'); fractions.append(im.getchannel('A').histogram()[0]/1024)
        assert len(fractions)==80, school
        alpha_audit[school]={'textures':len(fractions),'literal_alpha_zero_min':round(min(fractions),4),'literal_alpha_zero_max':round(max(fractions),4),'corners_alpha_zero':True}
    armor_fractions=[]; armor_binary=True
    for path in ARMOR.glob('*.png'):
        im=Image.open(path).convert('RGBA'); hist=im.getchannel('A').histogram()
        assert im.size==(64,32), (path,im.size)
        armor_fractions.append(hist[0]/(64*32)); armor_binary=armor_binary and not any(hist[1:255])
    assert len(armor_fractions)==120 and armor_binary and min(armor_fractions)>.5
    if not check:
        STARTUP.write_text('\n'.join(startup),encoding='utf-8');write(LANG,lang)
        write(MANIFEST_OUT,{
            'status':'generated and static validated; runtime evidence must be refreshed after regeneration',
            'sources':source_meta,
            'alpha_method':'Pillow edge-connected background flood fill; post-quantization alpha haze <=16 is written as literal RGBA 0,0,0,0',
            'atlas_crop_cleanup':{'scope':'all 480 item sprites','method':'discard only non-principal foreground components touching a vertical source-cell cut before resizing and centering','review':'alfheim_reclaimed_design/armory/visual_review/armory_overview.png'},
            'alpha_audit':alpha_audit,
            'bow_interior_alpha':{'textures':len(bow_holes),'all_have_enclosed_alpha_zero_region':True,'enclosed_region_pixels_min':min(bow_holes),'enclosed_region_pixels_max':max(bow_holes)},
            'crossbow_interior_alpha':{'textures':len(crossbow_holes),'all_have_enclosed_alpha_zero_region':True,'enclosed_region_pixels_min':min(crossbow_holes),'enclosed_region_pixels_max':max(crossbow_holes)},
            'waywatcher_necklace_alpha':{'textures':len(charm_holes),'all_have_enclosed_alpha_zero_region':True,'enclosed_region_pixels_min':min(charm_holes),'enclosed_region_pixels_max':max(charm_holes),'detached_atlas_spill_removed':True},
            'worn_armor_alpha':{'textures':len(armor_fractions),'literal_alpha_zero_min':round(min(armor_fractions),4),'literal_alpha_zero_max':round(max(armor_fractions),4),'binary_alpha_only':armor_binary},
            'counts':{'items':480,'weapon_or_offhand':240,'armor':240,'item_textures':480,'worn_armor_textures':120,'mmo_base_types':48,'mmo_auto_items':480,'mmo_custom_items':480,'profession_recipes':480},
            'generator':'tools/gen_armory.py',
            'runtime_validation':None,
        })
    print('Armory checks passed: 480 items, 600 textures, 48 MMO gear types, 480 auto-soul mappings and 480 Gear Crafting recipes.')
    print('All six cleaned atlases have transparent corners and >35% alpha-zero pixels.')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');args=a.parse_args();main(args.check)
