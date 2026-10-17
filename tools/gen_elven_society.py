"""Role-specific clothing and finery over the installed wood-elf skins. Faces/hair are external references."""
import argparse,hashlib,io,json,zipfile,math
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
RES='first_party_mods/alfheim_companion/src/main/resources/'
ASSETS=RES+'assets/alfheim_companion/'
CLOTH=['80775d','3f4a50','476e84','916e47','355e4a','883e51','324b81','69487e','7f3541','7aa5b7','34594b','57396b']

def png(im):
    stream=io.BytesIO();im.save(stream,format='PNG');return stream.getvalue()

def clothing(role,look):
    # The complete original skin, including every garment layer, remains visible.
    return png(Image.new('RGBA',(64,64),(0,0,0,0)))

def reference(role,look):
    row=json.loads((ROOT/'tools/elven_society_geometry.json').read_text())['roles'][role]
    ns,path=row['base_skins'][look].split(':');asset=f'assets/{ns}/textures/{path}.png'
    override=ROOT/'kubejs'/asset
    with zipfile.ZipFile(ROOT/'mods/richs_races_wood_elves-1.0.0-forge-1.20.1.jar') as archive:
        return Image.open(override if override.exists() else io.BytesIO(archive.read(asset))).convert('RGBA')

def wardrobe(role,look):
    source=np.array(reference(role,look))
    # Retain source embroidery and pixel shading; remove exposed flesh from fabric samples.
    patch=source[22:32,20:28,:3].copy().astype(float)
    pixels=patch.reshape(-1,3)
    fabric=pixels[(pixels[:,1]>pixels[:,0]*.96)&(pixels[:,1]>pixels[:,2]*1.08)]
    if len(fabric)<3:
        fabric=pixels[np.mean(pixels,axis=1)<100]
    if len(fabric)==0:fabric=pixels
    mid=np.median(fabric,axis=0)
    warm=(patch[:,:,0]>patch[:,:,1]*1.13)&(patch[:,:,0]>patch[:,:,2]*1.2)
    patch[warm]=mid
    im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im)
    for y in range(128):
        for x in range(128):
            c=patch[y%10,x%8]
            # Fourth look and role accents retain source contrast but vary their fabric dye.
            accent=np.array(tuple(bytes.fromhex(CLOTH[role])),dtype=float)
            source_luma=max(1,float(np.mean(mid)))
            dyed=accent*np.clip(float(np.mean(c))/source_luma,.55,1.15)
            mix=.36 if look!=3 else .65
            c=c*(1-mix)+dyed*mix
            fold=.73+.27*(.5+.5*math.cos((x%12-5.5)*math.pi/6))
            shade=fold*(.91+.09*math.sin(y*.21))
            im.putpixel((x,y),tuple(np.clip(c*shade,0,255).astype(int))+(255,))
    d=ImageDraw.Draw(im)
    gold=[(89,67,35),(145,112,52),(202,168,85),(235,210,139),(166,130,61)]
    # Woven borders, alternating leaf embroidery, shaded hems on the separate panels.
    for start in (0,24,64,80,96):
        for y in (start+2,start+16):
            for x in range(32):d.point((x,y),fill=gold[x%5]+(255,))
        for x in range(3,30,6):
            d.line((x,start+7,x+2,start+9,x,start+11),fill=gold[2]+(255,))
            d.point((x+1,start+8),fill=gold[3]+(255,))
    for y in range(21):
        for x in range(64,116):d.point((x,y),fill=gold[(x+y)%5]+(255,))
    jewel=[(36,120,105),(146,42,80),(53,100,169),(153,117,35)][look]
    d.rectangle((116,0,127,10),fill=jewel+(255,));d.line((117,1,123,1),fill=(226,237,209,255))
    # Pleated ivory cuffs carry warm shadows rather than a solid pale strip.
    for y in range(40,58):
        for x in range(32,64):
            f=[.66,.81,1,.92][x%4];d.point((x,y),fill=tuple(int(c*f) for c in (227,220,190))+(255,))
    # Match the exposed ear skin to the supplied face, with a darker inner edge.
    face=source[8:16,8:16,:3].reshape(-1,3).astype(float)
    flesh=face[(face[:,0]>face[:,1]*1.05)&(face[:,1]>face[:,2]*1.06)&(face[:,0]>130)]
    tone=np.median(flesh,axis=0) if len(flesh) else np.array([210,171,145])
    for y in range(64,80):
        for x in range(112,124):
            f=.78 if x%4==0 else (1.06 if x%4==2 else .96)
            d.point((x,y),fill=tuple(np.clip(tone*f,0,255).astype(int))+(255,))
    return png(im)

def build():
    catalogue=json.loads((ROOT/'tools/elven_society_geometry.json').read_text())
    for source in ('client/ElvenSocietyModels.java','society/ElvenSociety.java'):
        path=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion'/source
        assert hashlib.sha256(path.read_bytes()).hexdigest()==catalogue[source],source+' changed: re-export native heads'
    out={}
    def js(path,value):out[path]=(json.dumps(value,indent=2)+'\n').encode()
    overrides=[]
    for role,row in enumerate(catalogue['roles']):
        for look in range(4):
            key=row['id']+'_'+str(look)
            out[ASSETS+'textures/entity/society/'+key+'.png']=clothing(role,look)
            out[ASSETS+'textures/entity/society/wardrobe/'+key+'.png']=wardrobe(role,look)
            js(ASSETS+'models/item/society/'+key+'.json',catalogue['heads'][key])
            overrides.append({'predicate':{'alfheim_companion:social_appearance':role*4+look+1},'model':'alfheim_companion:item/society/'+key})
    js(ASSETS+'models/item/elven_citizen_spawn_egg.json',{'parent':'alfheim_companion:item/society/serf_0','overrides':overrides})
    js(RES+'data/alfheim_companion/loot_tables/entities/elven_citizen.json',{'type':'minecraft:entity','pools':[]})
    path=ROOT/(ASSETS+'lang/en_us.json');lang=json.loads(path.read_text())
    lang['entity.alfheim_companion.elven_citizen']='Elven Citizen';lang['item.alfheim_companion.elven_citizen_spawn_egg']='Elven Citizen Spawn Egg'
    js(ASSETS+'lang/en_us.json',lang)
    js('tools/elven_society_manifest.json',{'roles':catalogue['roles'],'source_skin_sha256':{row['base_skins'][look]:hashlib.sha256(png(reference(role,look))).hexdigest() for role,row in enumerate(catalogue['roles']) for look in range(4)},'appearances_per_role':4,'total_appearances':48,
        'natural_spawning':False,'adult_only':True,'identity_source':'Installed Richs Races wood-elf skins, including active pack overrides; faces and hair are unmodified external references'})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for name,data in build().items():
        path=ROOT/name
        if args.check:assert path.read_bytes()==data,name
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('ELVEN SOCIETY: 12 roles / 48 appearances; existing elf identities preserved; '+('source equal' if args.check else 'generated'))
if __name__=='__main__':main()
