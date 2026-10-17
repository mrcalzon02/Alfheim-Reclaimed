"""Deterministic native UV skins, habitat spawns, loot and skinned inventory heads."""
import argparse,copy,hashlib,io,json,math,random
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_companion/src/main/resources'
ASSETS='assets/alfheim_companion/'
PALETTES={
'hulking_troll':[(93,113,69),(117,111,98),(112,144,148)],
'cyclops':[(163,128,92),(128,91,75),(130,128,143)],
'briar_beast':[(91,102,51),(106,82,65),(106,106,69)],
'thorn_infestor':[(76,111,61),(95,91,110),(99,143,147)],
'stone_gargoyle':[(80,86,96),(102,103,139),(115,111,102)],
'fen_hag':[(129,151,117),(139,127,108),(143,161,166)]}
HABITATS={
'hulking_troll':['alfheim:rootfall','alfheim:hollow_marches','alfheim:sundered_highlands','alfheim:shatterfields','alfheim:starved_reach'],
'cyclops':['mythicbotany:alfheim_hills','alfheim:sundered_highlands','alfheim:ashen_grove','alfheim:scorchfell','alfheim:sepulchral_reach'],
'briar_beast':['alfheim:rootfall','alfheim:hollow_marches','alfheim:ashen_grove','alfheim:bloomfall_vale','mythicbotany:dreamwood_forest'],
'thorn_infestor':['alfheim:infested_warren','alfheim:rootfall','alfheim:decayed_mire','alfheim:mana_fen','alfheim:starved_reach'],
'stone_gargoyle':['alfheim:shatterfields','alfheim:prism_drift','alfheim:sepulchral_reach','alfheim:starless_reach'],
'fen_hag':['alfheim:mana_fen','alfheim:mistbark_shore','alfheim:decayed_mire','alfheim:sporebank_shore','alfheim:starved_reach']}
DROPS={'hulking_troll':'minecraft:leather','cyclops':'minecraft:bone','briar_beast':'minecraft:stick','thorn_infestor':'minecraft:vine','stone_gargoyle':'minecraft:flint','fen_hag':'minecraft:spider_eye'}

PALETTES.update({
'hollow_stag_wendigo':[(148,145,122),(113,106,119),(147,180,184)],
'duskweaver':[(78,72,104),(103,80,111),(64,88,110)],
'hollow_bride':[(177,184,175),(159,151,164),(160,187,198)],
'barrow_maw':[(97,105,76),(93,78,101),(128,118,105)],
'nuckelavee':[(129,107,104),(142,84,70),(110,143,153)],
'redcap_reaver':[(137,145,105),(144,124,113),(129,158,157)]})
HABITATS.update({
'hollow_stag_wendigo':['alfheim:rootfall','alfheim:hollow_marches','alfheim:sepulchral_reach','alfheim:starved_reach'],
'duskweaver':['alfheim:infested_warren','alfheim:sporebank_shore','alfheim:mana_fen','alfheim:starless_reach'],
'hollow_bride':['alfheim:mistbark_shore','alfheim:sepulchral_reach','alfheim:decayed_mire','alfheim:starved_reach'],
'barrow_maw':['alfheim:hollow_marches','alfheim:decayed_mire','alfheim:sporebank_shore','alfheim:sepulchral_reach'],
'nuckelavee':['alfheim:mistbark_shore','alfheim:decayed_mire','alfheim:scorchfell','alfheim:starved_reach'],
'redcap_reaver':['alfheim:rootfall','mythicbotany:dreamwood_forest','alfheim:ashen_grove','alfheim:starved_reach']})
DROPS.update({'hollow_stag_wendigo':'minecraft:bone','duskweaver':'minecraft:string','hollow_bride':'minecraft:string','barrow_maw':'minecraft:brown_mushroom','nuckelavee':'minecraft:rotten_flesh','redcap_reaver':'minecraft:leather'})
WEIGHTS={'briar_beast':4,'thorn_infestor':3,'fen_hag':3,'duskweaver':3,'redcap_reaver':4}

PALETTES.update({
'corrupted_crystal_colossus':[(137,97,176),(102,148,74),(85,107,146)],
'shard_reaver':[(124,86,179),(85,144,112),(82,100,128)],
'prism_warden':[(153,103,184),(110,165,70),(94,121,157)],
'marrow_tick':[(141,125,106),(129,106,98),(164,164,147)],
'rib_burrower':[(154,142,115),(145,119,103),(180,178,159)],
'sinew_leech':[(167,142,125),(142,114,106),(159,174,160)],
'parasite_maw':[(181,168,128),(151,124,110),(179,184,159)]})
CRYSTALS={'corrupted_crystal_colossus','shard_reaver','prism_warden'}
PARASITES={'marrow_tick','rib_burrower','sinew_leech','parasite_maw'}
for species in CRYSTALS:HABITATS[species]=['alfheim:void_verge','alfheim:void_shore']
for species in PARASITES:HABITATS[species]=[]
DROPS.update({'corrupted_crystal_colossus':'minecraft:amethyst_shard','shard_reaver':'minecraft:amethyst_shard','prism_warden':'minecraft:amethyst_shard','marrow_tick':'minecraft:rotten_flesh','rib_burrower':'minecraft:bone','sinew_leech':'minecraft:rotten_flesh','parasite_maw':'minecraft:rotten_flesh'})
WEIGHTS.update({'corrupted_crystal_colossus':2,'shard_reaver':5,'prism_warden':3})
# Explicit habitat distribution: preserve regional identities and fill woodland/shore gaps.
for species,extra in {
'hulking_troll':['alfheim:silverbark_wood'],
'cyclops':['alfheim:prism_drift'],
'briar_beast':['alfheim:silverbark_wood'],
 'thorn_infestor':['alfheim:sporebank_shore'],
 'stone_gargoyle':['alfheim:void_shore'],
 'fen_hag':['alfheim:tidewood_shore'],
 'hollow_stag_wendigo':['alfheim:silverbark_wood','alfheim:sundered_highlands'],
 'duskweaver':['alfheim:bloomfall_vale'],
 'hollow_bride':['alfheim:hollow_marches'],
 'barrow_maw':['alfheim:infested_warren'],
 'nuckelavee':['alfheim:tidewood_shore','alfheim:void_shore'],
 'redcap_reaver':['alfheim:silverbark_wood','alfheim:bloomfall_vale']}.items():
    HABITATS[species]=list(dict.fromkeys(HABITATS[species]+extra))

def skin(species,variant,quads,size):
    # Paint each native face in its own island. All values are selected material ramps;
    # no shared noise sheet, repeated block texture, or disconnected concept artwork.
    flesh=PALETTES[species][variant]
    flesh=tuple(min(255,int(c*1.12)) for c in flesh)
    cloth=[(67,55,86),(77,49,53),(36,77,89)][variant]
    if species=='fen_hag':cloth=[(58,54,86),(77,45,65),(43,70,91)][variant]
    bark=[(106,76,48),(87,64,67),(99,104,75)][variant]
    stone=[(106,119,137),(123,113,153),(137,131,112)][variant]
    materials={'skin':flesh,'shadow_skin':tuple(int(c*.72) for c in flesh),
      'scar':(160,102,93),'bone':(208,192,148),'ivory':(231,211,167),
      'bark':bark,'stone':stone,'shadow_stone':tuple(int(c*.58) for c in stone),
      'cloth':cloth,'leather':[(112,65,43),(96,51,57),(55,84,87)][variant],
      'metal':[(151,123,67),(153,119,114),(132,162,160)][variant],
      'wrap':[(150,137,99),(133,119,114),(154,162,156)][variant],
      'trim':[(191,156,78),(181,133,150),(143,189,186)][variant],
      'moss':[(93,126,67),(98,87,108),(127,166,160)][variant],
      'hair':[(55,44,41),(56,42,53),(97,106,117)][variant],
      'eye':[(239,171,48),(230,110,70),(104,231,220)][variant],
      'cloud_eye':(152,163,144),'void':(31,20,29),
      'rune':[(119,206,164),(213,141,186),(138,226,238)][variant],
      'fungus':[(163,61,59),(144,87,161),(83,162,172)][variant],
      'membrane':[(52,64,83),(72,53,85),(76,76,63)][variant]}
    materials.update({'fur':[(69,65,55),(64,53,65),(117,142,148)][variant],
      'web':[(192,194,174),(159,147,174),(168,202,211)][variant],
      'chitin':tuple(int(c*.62) for c in flesh),
      'sinew':[(126,68,70),(148,67,54),(94,117,132)][variant],
      'iron':[(104,110,109),(114,97,96),(112,138,145)][variant],
      'cap':[(151,41,48),(129,40,69),(132,68,91)][variant]})
    if species=='hollow_stag_wendigo':
        materials['bone']=[(197,181,143),(157,145,154),(178,210,212)][variant]
        materials['ivory']=[(223,208,168),(182,167,180),(203,228,223)][variant]
    if species=='hollow_bride':
        materials['cloth']=[(171,179,166),(132,119,146),(150,180,197)][variant]
        materials['trim']=[(153,139,101),(144,115,139),(148,199,209)][variant]
    if species=='duskweaver':materials['membrane']=[(88,72,108),(113,76,113),(60,91,121)][variant]
    materials.update({'crystal':flesh,'obsidian':[(57,48,74),(53,64,47),(45,54,75)][variant],
      'taint':[(35,22,45),(29,44,30),(18,26,38)][variant],
      'core':[(196,103,240),(185,238,64),(90,220,238)][variant],
      'maggot':[(187,175,139),(149,119,107),(178,185,163)][variant]})
    if species in PARASITES:materials['bone']=[(207,189,145),(162,137,117),(195,194,168)][variant]
    im=Image.new('RGBA',(size,size),(63,53,47,255));seen=set()
    def mul(c,f):return tuple(max(0,min(255,round(v*f))) for v in c)+(255,)
    for q in quads:
        uv=q['uv'];x0=round(min(t[0] for t in uv)*size);y0=round(min(t[1] for t in uv)*size)
        x1=round(max(t[0] for t in uv)*size);y1=round(max(t[1] for t in uv)*size)
        w=max(1,x1-x0);h=max(1,y1-y0);key=(x0,y0,x1,y1)
        if key in seen:continue
        seen.add(key);mat=q['material'];name=q['part'];base=materials[mat]
        rng=random.Random(f'{species}/{variant}/{name}/{q["face"]}')
        face=Image.new('RGBA',(w,h));px=face.load()
        light=[.88,.81,.72,1.14,1.03,.89][q['face']%6]
        for y in range(h):
            for x in range(w):
                u=(x+.5)/w;v=(y+.5)/h
                # Deliberate bevel and form lighting, quantised into pixel-art ramps.
                edge=min(x,y,w-1-x,h-1-y)
                form=1.04-.22*v+.06*math.sin(u*math.pi)
                if edge==0 and min(w,h)>3:
                    form*=(1.04 if y==0 or x==0 else .91) if mat in ('skin','shadow_skin','scar') else (1.12 if y==0 or x==0 else .76)
                if mat in ('skin','shadow_skin','scar','maggot'):
                    form+=.07*math.sin(u*7+math.sin(v*4))
                    form=round(form*12)/12
                elif mat=='bark':
                    grain=math.sin((x+.6*math.sin(y*.34))*1.7)
                    form*=.72 if grain<-.55 else 1.13 if grain>.82 else 1
                elif mat in ('cloth','leather','hair','wrap','fur','cap','sinew'):
                    fold=math.cos(x*1.5+.35*math.sin(y*.18))
                    form*=.76 if fold<-.4 else 1.12 if fold>.7 else 1
                    if mat=='wrap' and y%3==2:form*=.7
                    if mat=='fur' and (x+y//3)%3==0:form*=.68
                elif mat=='web':
                    form*=.74 if (x+y)%3==0 else 1.12
                elif mat=='crystal':
                    plane=u*.75+v*.25
                    form*=(.63 if plane<.25 else .88 if plane<.5 else 1.27 if plane<.74 else .94)
                elif mat in ('obsidian','taint'):form=round(form*8)/8
                elif mat in ('chitin','iron'):form=round((form+.08*math.sin(u*math.pi))*10)/10
                elif mat in ('bone','ivory'):form*=1-.11*math.sin(x*2.1)
                elif mat in ('stone','shadow_stone'):form=round(form*9)/9
                elif mat=='membrane':form*=.9+.18*math.sin(u*math.pi)
                px[x,y]=mul(base,light*form)
        d=ImageDraw.Draw(face)
        if mat in ('leather','cloth') and w>3 and h>4:
            # Contrast hems, repair stitches, and small fabric irregularities.
            for y in range(1,h-1,3):
                d.point((1,y),fill=mul(materials['wrap'],.85));d.point((w-2,y),fill=mul(base,.5))
            d.line((1,h-2,w-2,h-2),fill=mul(base,.52))
            if mat=='leather' and w>5 and h>7:
                d.line((w//2,2,w//2+1,h-3),fill=mul(base,.55))
                for y in range(3,h-2,3):d.point((w//2,y),fill=mul(materials['wrap'],.9))
        if mat=='trim':
            d.line((0,0,w-1,0),fill=mul(base,1.25));d.line((0,h-1,w-1,h-1),fill=mul(base,.55))
            for x in range(1,w,3):d.point((x,h//2),fill=mul(materials['cloth'],.65))
        if mat in ('skin','shadow_skin','maggot') and w>=5 and h>=5:
            # Creases describe the part: broad muscles, folded wrists, worn facial planes.
            if any(n in name for n in ('face','skull','cranium','cheek','jaw','brow','nose')):
                for y in (h//3,2*h//3):
                    d.line((1,y,min(w-2,w//2),y-1),fill=mul(base,.64))
                    d.point((1,max(0,y-1)),fill=mul(base,1.18))
            elif any(n in name for n in ('pectoral','bicep','thigh','belly','forearm','deltoid','rib')):
                d.line((1,h-2,w//2,h-3,w-2,h-2),fill=mul(base,.63))
                d.line((1,1,w//2,2,w-2,1),fill=mul(base,1.18))
            for i in range(max(1,w*h//90)):
                x=rng.randrange(1,w-1);y=rng.randrange(1,h-1)
                d.point((x,y),fill=mul(base,.76))
        if mat in ('bark','stone','shadow_stone') and w>=4 and h>=5:
            for i in range(max(1,w*h//70)):
                x=rng.randrange(1,w-1);y=rng.randrange(1,h-2)
                points=[(x,y),(max(0,x-1),y+1),(x,min(h-1,y+3))]
                d.line(points,fill=mul(base,.43));d.point((min(w-1,x+1),y),fill=mul(base,1.2))
            if mat=='bark':
                for i in range(max(1,w*h//100)):
                    x=rng.randrange(w);y=rng.randrange(h)
                    d.rectangle((x,y,min(w-1,x+1),min(h-1,y+1)),fill=mul(materials['moss'],.8))
        if mat=='crystal' and w>=3 and h>=4:
            d.line((0,0,w//2,max(1,h//3),w-1,max(1,h//3-1)),fill=mul(base,1.55))
            d.line((w//2,1,max(0,w//2-1),h//2,w//2,h-2),fill=mul(materials['taint'],.8))
            d.point((min(w-1,w//2+1),1),fill=mul(materials['core'],1))
        if mat=='maggot' and w>=4 and h>=4:
            for y in range(2,h-1,3):
                d.line((1,y,w-2,y),fill=mul(base,.68));d.line((1,y-1,w-2,y-1),fill=mul(base,1.12))
        if mat=='bone' and w>2 and h>3:
            d.line((0,1,0,h-2),fill=mul(base,.62));d.point((min(w-1,1),1),fill=mul(base,1.2))
        if mat=='fungus':
            for i in range(max(1,w*h//9)):
                d.point((rng.randrange(w),rng.randrange(h)),fill=mul(materials['bone'],.96))
            d.line((0,h-1,w-1,h-1),fill=mul(base,.5))
        if mat in ('eye','cloud_eye'):
            d.rectangle((0,0,w-1,h-1),fill=mul(base,.75))
            if w>1 and h>1:d.rectangle((0,0,w-1,max(0,h-2)),fill=mul(base,1.05))
            d.line((w//2,0,w//2,h-1),fill=(25,24,25,255));d.point((max(0,w//2-1),0),fill=(255,242,192,255))
        if mat in ('rune','core'):
            d.rectangle((0,0,w-1,h-1),fill=mul(base,.55))
            d.line((w//2,0,w//2,h-1),fill=mul(base,1.2))
            if w>2:d.line((0,h//3,w-1,h//2),fill=mul(base,1.12))
        if mat=='void':
            d.rectangle((0,0,w-1,h-1),fill=mul(base,.65));d.line((0,h-1,w-1,h-1),fill=(72,35,40,255))
        im.paste(face,(x0,y0))
    stream=io.BytesIO();im.save(stream,format='PNG');return stream.getvalue()

def build():
    geometry=json.loads((ROOT/'tools/monstrosity_geometry.json').read_text());out={}
    for source in ('client/MonstrosityModel.java','monstrosity/MonstrosityKind.java'):
        p=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion'/source
        assert hashlib.sha256(p.read_bytes()).hexdigest()==geometry[source],source+' requires native export'
    def js(name,data):out[name]=(json.dumps(data,indent=2)+'\n').encode()
    lang=json.loads((RES/(ASSETS+'lang/en_us.json')).read_text())
    for row in geometry['species']:
        species=row['id'];overrides=[]
        for variant in range(3):
            key=f'{species}_{variant}';out[ASSETS+f'textures/entity/monstrosities/{key}.png']=skin(species,variant,geometry['models'][species],geometry['atlas_size'])
            from render_monstrosities import head_icon
            icon=head_icon(geometry['heads'][species],out[ASSETS+f'textures/entity/monstrosities/{key}.png'])
            stream=io.BytesIO();icon.save(stream,format='PNG');out[ASSETS+f'textures/item/monstrosities/{key}.png']=stream.getvalue()
            js(ASSETS+f'models/item/monstrosities/{key}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'alfheim_companion:item/monstrosities/{key}'}})
            if species in CRYSTALS:
                glow=Image.new('RGBA',(geometry['atlas_size'],geometry['atlas_size']));body=Image.open(io.BytesIO(out[ASSETS+f'textures/entity/monstrosities/{key}.png']))
                for q in geometry['models'][species]:
                    if q['material']!='core':continue
                    uv=q['uv'];rect=(int(math.floor(min(t[0] for t in uv)*body.width)),int(math.floor(min(t[1] for t in uv)*body.height)),int(math.ceil(max(t[0] for t in uv)*body.width)),int(math.ceil(max(t[1] for t in uv)*body.height)))
                    glow.paste(body.crop(rect),rect[:2])
                stream=io.BytesIO();glow.save(stream,format='PNG');out[ASSETS+f'textures/entity/monstrosities/{key}_glow.png']=stream.getvalue()
            overrides.append({'predicate':{'alfheim_companion:monstrosity_variant':variant+1},'model':f'alfheim_companion:item/monstrosities/{key}'})
        js(ASSETS+f'models/item/{species}_spawn_egg.json',{'parent':f'alfheim_companion:item/monstrosities/{species}_0','overrides':overrides})
        lang['entity.alfheim_companion.'+species]=row['label'];lang['item.alfheim_companion.'+species+'_spawn_egg']=row['label']+' Spawn Egg'
        js(f'data/alfheim_companion/tags/worldgen/biome/{species}_habitats.json',{'replace':False,'values':HABITATS[species]})
        if HABITATS[species]:js(f'data/alfheim_companion/forge/biome_modifier/{species}_spawns.json',{'type':'forge:add_spawns','biomes':'#alfheim_companion:'+species+'_habitats','spawners':{'type':'alfheim_companion:'+species,'weight':WEIGHTS.get(species,2),'minCount':1,'maxCount':1}})
        js(f'data/alfheim_companion/loot_tables/entities/{species}.json',{'type':'minecraft:entity','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':DROPS[species],'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]}]}]})
    from menagerie_sounds import build_sounds
    sounds,subtitles=build_sounds([row['id'] for row in geometry['species']],{r['id']:r['label'] for r in geometry['species']})
    # Preserve audio owned by other content generators (for example elven voices).
    sound_path=RES/(ASSETS+'sounds.json')
    existing=json.loads(sound_path.read_text()) if sound_path.exists() else {}
    existing={k:v for k,v in existing.items() if not k.startswith('monstrosity.') and k!='maggot_mound.ambient'}
    existing.update(sounds)
    js(ASSETS+'sounds.json',existing);lang.update(subtitles)
    from maggot_mounds import build_mounds
    out.update(build_mounds());lang['block.alfheim_companion.maggot_mound']='Maggot Mound'
    js(ASSETS+'lang/en_us.json',lang)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for name,data in build().items():
        path=RES/name
        if args.check:assert path.read_bytes()==data,name
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('MONSTROSITIES: 19 native rigs / 57 skins and matching heads; habitat spawns and bounded existing-material drops; '+('source equal' if args.check else 'generated'))
if __name__=='__main__':main()
