"""Generate the finite biome appearance catalogue and vanilla enemy subclasses.

Visuals retain five vanilla rigs with biome/style skin recolors and matching head
inventory models. Vanilla/third-party assets and terrain/structures are unchanged.
"""
import argparse,json,hashlib,io,zipfile
from PIL import Image
from silverbark_boneguard import skin as silverbark_skin
from mire_riftmite import skin as mire_skin
from regional_monstrosity_skins import skin as regional_skin, verge_eyes, REGIONS
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JAVA='first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/enemy/'
RES='first_party_mods/alfheim_companion/src/main/resources/'
THEMES={
 'root':('stripped_dark_oak_log','oak_leaves'),
 'fungus':('mushroom_block_inside','red_mushroom_block'),
 'crystal':('amethyst_block','budding_amethyst'),
 'mist':('white_wool','prismarine'),
 'frost':('packed_ice','blue_ice'),
 'ash':('basalt_side','magma'),
 'tide':('prismarine','dark_prismarine'),
 'field':('stripped_birch_log','hay_block_side')}
ROWS='''alfheim:alfheim_ocean|Drowned|tide|93c6bd|8fe3df
alfheim:ashen_grove|Ashen|ash|a19b93|eab071
alfheim:bloomfall_vale|Bloomfall|root|d5baaa|e6a8c7
alfheim:decayed_mire|Mire|fungus|a3b197|bf8c9c
alfheim:hollow_marches|Hollow|root|b6bea0|d1c486
alfheim:infested_warren|Warren|fungus|b0ad86|cc875e
alfheim:mana_fen|Fen|mist|83bcaf|a5d3ce
alfheim:mistbark_shore|Mistbark|mist|c2d1d3|a6bfd3
alfheim:prism_drift|Prism|crystal|bdb5e0|8ee0e2
alfheim:rootfall|Rootfall|root|c2a38c|b3c091
alfheim:scorchfell|Scorchfell|ash|ae948d|ed9f73
alfheim:sepulchral_reach|Sepulchral|mist|b8b2c7|c3a3d9
alfheim:shatterfields|Shatter|crystal|b7bfca|e6caab
alfheim:silverbark_wood|Silverbark|root|c4cebb|a8c8b2
alfheim:sporebank_shore|Sporebank|fungus|d0bcb3|d9b1ce
alfheim:starless_reach|Starless|crystal|938da5|b7a5d1
alfheim:starved_reach|Rime|frost|bdc9da|91b7d8
alfheim:sundered_highlands|Sundered|crystal|c5bbaa|d7c792
alfheim:tidewood_shore|Tidewood|tide|a9c7b6|d6d6ad
alfheim:void_shore|Chalkshore|tide|c7cbd0|b0b7cf
alfheim:void_verge|Verge|crystal|b3acc6|d0b6e3
mythicbotany:alfheim_hills|Highland|field|b9c4a5|d1d5af
mythicbotany:alfheim_lakes|Lakeside|tide|9bbfb3|b8d8cd
mythicbotany:alfheim_plains|Meadow|field|c3c99d|e0ce99
mythicbotany:dreamwood_forest|Dreamwood|root|b1bcda|d4b6e1
mythicbotany:golden_fields|Golden|field|dbcf9b|e6ba76'''
SPECIES=[('Zombie','Zombie','zombie','Revenant'),('Skeleton','Skeleton','skeleton','Boneguard'),
 ('Pillager','Pillager','pillager','Outcast'),('Enderman','EnderMan','enderman','Riftwalker'),
 ('Endermite','Endermite','endermite','Riftmite')]

def profiles():
 return [dict(zip(('biome','title','theme','body','accent'),line.split('|'))) for line in ROWS.splitlines()]

def recolor_skin(data,body,accent,style):
 image=Image.open(io.BytesIO(data)).convert('RGBA')
 primary=tuple(bytes.fromhex(body));secondary=tuple(bytes.fromhex(accent))
 blend=(0,.18,.36)[style]
 primary=tuple(round(a*(1-blend)+b*blend) for a,b in zip(primary,secondary))
 pixels=[]
 for r,g,b,a in image.getdata():
  value=(r*3+g*6+b)/10
  tint=secondary if max(r,g,b)-min(r,g,b)>25 and (b>g*1.12 or r>g*1.3) else primary
  pixels.append(tuple(min(255,round(value*c/180)) for c in tint)+(a,))
 image.putdata(pixels);out=io.BytesIO();image.save(out,format='PNG');return out.getvalue()

def build():
 out={}
 def emit(p,text):out[p]=text.encode('utf-8')
 def js(p,value):emit(p,json.dumps(value,indent=2)+'\n')
 rows=profiles();records=[]
 heads=json.loads((ROOT/'tools/themed_enemy_head_geometry.json').read_text())
 layer=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/client/ThemedMaterialLayer.java'
 exporter=ROOT/'first_party_mods/alfheim_companion/src/test/java/com/continuityworks/alfheimcompanion/client/EnemyHeadModelsTest.java'
 assert heads['layer_sha256']==hashlib.sha256(layer.read_bytes()).hexdigest(),'Re-export baked head geometry after layer changes'
 assert heads['exporter_sha256']==hashlib.sha256(exporter.read_bytes()).hexdigest(),'Re-export after head-exporter changes'
 regional=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/client/RegionalMonstrosityModels.java'
 assert heads['regional_sha256']==hashlib.sha256(regional.read_bytes()).hexdigest(),'Re-export after regional model changes'
 assert len(heads['models'])==390
 skins={'zombie':'zombie/zombie','skeleton':'skeleton/skeleton','pillager':'illager/pillager',
        'enderman':'enderman/enderman','endermite':'endermite'}
 with zipfile.ZipFile(ROOT.parent.parent/'Install/versions/1.20.1/1.20.1.jar') as archive:
  for species,skin in skins.items():
   original=archive.read('assets/minecraft/textures/entity/'+skin+'.png')
   for p,row in enumerate(rows):
    for style in range(3):
     out[RES+f'assets/alfheim_companion/textures/entity/themed/{species}_{p}_{style}.png']=recolor_skin(original,row['body'],row['accent'],style)
 out[RES+'assets/alfheim_companion/textures/entity/themed/skeleton_13_0.png']=silverbark_skin()
 out[RES+'assets/alfheim_companion/textures/entity/themed/endermite_3_0.png']=mire_skin()
 for species,profile in REGIONS.items():
  for style in range(3):
   out[RES+f'assets/alfheim_companion/textures/entity/themed/{species}_{profile}_{style}.png']=regional_skin(species,style)
 out[RES+'assets/alfheim_companion/textures/entity/themed/verge_eyes.png']=verge_eyes()
 for r in rows:
  tex,accent=THEMES[r['theme']]
  records.append('        new Profile("%s", "%s", %d, 0x%s, 0x%s, material("%s"), material("%s"))'%(
   r['biome'],r['title'],list(THEMES).index(r['theme']),r['body'],r['accent'],tex,accent))
 emit(JAVA+'EnemyProfiles.java','''package com.continuityworks.alfheimcompanion.enemy;

// GENERATED by tools/gen_themed_enemies.py. Stored biome IDs survive catalogue reordering.
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.biome.Biome;

public final class EnemyProfiles {
    public record Profile(String biome, String title, int theme, int body, int accent,
                          ResourceLocation texture, ResourceLocation detailTexture) {}
    public static final Profile[] ALL = {
'''+',\n'.join(records)+'''
    };
    private static ResourceLocation material(String name) {
        return new ResourceLocation("minecraft", "textures/block/"+name+".png");
    }
    public static int index(String id) {
        for (int i=0;i<ALL.length;i++) if (ALL[i].biome().equals(id)) return i;
        return indexOfDefault();
    }
    private static int indexOfDefault() { return 23; } // Alfheim plains
    public static Profile get(int i) { return ALL[i>=0 && i<ALL.length ? i : indexOfDefault()]; }
    public static int choose(Holder<Biome> biome) {
        String id=biome.unwrapKey().map(k->k.location().toString()).orElse("");
        for(int i=0;i<ALL.length;i++) if(ALL[i].biome().equals(id)) return i;
        // Midgard's vanilla and modded biomes use their closest material ecology.
        if(biome.is(BiomeTags.IS_OCEAN)) return index("alfheim:alfheim_ocean");
        if(biome.is(BiomeTags.IS_BEACH)) return index("alfheim:tidewood_shore");
        if(biome.is(BiomeTags.IS_RIVER)) return index("alfheim:mana_fen");
        if(biome.value().getBaseTemperature()<0.2F) return index("alfheim:starved_reach");
        if(biome.value().getBaseTemperature()>1.2F) return index("alfheim:scorchfell");
        if(biome.is(BiomeTags.IS_MOUNTAIN)) return index("alfheim:sundered_highlands");
        if(biome.is(BiomeTags.IS_JUNGLE)) return index("alfheim:infested_warren");
        if(id.contains("mushroom") || id.contains("fung") || id.contains("spore")) return index("alfheim:sporebank_shore");
        if(id.contains("swamp") || id.contains("marsh") || id.contains("bog")) return index("alfheim:decayed_mire");
        if(biome.is(BiomeTags.IS_FOREST)) return index("alfheim:silverbark_wood");
        return indexOfDefault();
    }
    private EnemyProfiles() {}
}
''')
 for name,parent,vanilla,label in SPECIES:
  emit(JAVA+'Themed'+name+'.java',f'''package com.continuityworks.alfheimcompanion.enemy;

// GENERATED by tools/gen_themed_enemies.py. Vanilla AI, equipment and lifespan are inherited.
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.{parent};
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

public final class Themed{name} extends {parent} implements ThemedEnemy {{
    private static final EnemyAppearance.State APPEARANCE=EnemyAppearance.state(Themed{name}.class);
    public Themed{name}(EntityType<? extends {parent}> type, Level level) {{ super(type,level); }}
    @Override public EnemyAppearance.State appearanceState() {{ return APPEARANCE; }}
    @Override protected void defineSynchedData() {{ super.defineSynchedData(); EnemyAppearance.define(this,APPEARANCE); }}
    @Override public void addAdditionalSaveData(CompoundTag tag) {{ super.addAdditionalSaveData(tag); EnemyAppearance.save(this,tag); }}
    @Override public void readAdditionalSaveData(CompoundTag tag) {{ super.readAdditionalSaveData(tag); EnemyAppearance.load(this,tag); }}
    @Override public SpawnGroupData finalizeSpawn(ServerLevelAccessor level,DifficultyInstance difficulty,MobSpawnType reason,SpawnGroupData group,CompoundTag tag) {{
        SpawnGroupData result=super.finalizeSpawn(level,difficulty,reason,group,tag);
        EnemyAppearance.assign(this); return result;
    }}
    @Override protected Component getTypeName() {{ return EnemyAppearance.name(this,"{label}"); }}
    @Override protected net.minecraft.resources.ResourceLocation getDefaultLootTable() {{ return EntityType.{vanilla.upper()}.getDefaultLootTable(); }}
}}
''')
  overrides=[]
  for profile in range(len(rows)):
   for style in range(3):
    key=f'{vanilla}_{profile}_{style}'
    js(RES+'assets/alfheim_companion/models/item/enemy_heads/'+key+'.json',heads['models'][key])
    overrides.append({'predicate':{'alfheim_companion:appearance':profile*3+style+1},
                      'model':'alfheim_companion:item/enemy_heads/'+key})
  js(RES+'assets/alfheim_companion/models/item/biome_'+vanilla+'_spawn_egg.json',
     {'parent':f'alfheim_companion:item/enemy_heads/{vanilla}_23_0','overrides':overrides})
 js('kubejs/data/alfheim/tags/worldgen/biome/themed_enemy_biomes.json',{'replace':False,'values':['#minecraft:is_overworld']+[r['biome'] for r in rows]})
 js('kubejs/data/alfheim/forge/biome_modifier/themed_enemies.json',{'type':'alfheim_companion:themed_enemies','biomes':'#alfheim:themed_enemy_biomes'})
 js(RES+'data/minecraft/tags/entity_types/skeletons.json',{'replace':False,'values':['alfheim_companion:biome_skeleton']})
 js(RES+'data/minecraft/tags/entity_types/raiders.json',{'replace':False,'values':['alfheim_companion:biome_pillager']})
 names={}
 for _,_,s,label in SPECIES:
  names['entity.alfheim_companion.biome_'+s]='Alfheim '+label
  names['item.alfheim_companion.biome_'+s+'_spawn_egg']='Alfheim '+label+' Spawn Egg'
 # Separate file merged into the existing language at generation, preserving companion strings.
 lang=ROOT/(RES+'assets/alfheim_companion/lang/en_us.json')
 current=json.loads(lang.read_text(encoding='utf-8')) if lang.exists() else {}
 current.update(names);js(lang.relative_to(ROOT).as_posix(),current)
 js('tools/themed_enemy_inventory.json',{'profiles':rows,'species':[s[2] for s in SPECIES],
    'styles':['bound','shrouded','crowned'],'themes':THEMES,'appearances':len(rows)*len(SPECIES)*3,
    'creeper_variants':0,'visual_method':'Five species; authored Silverbark, Mire, Ashen, Rime and Verge regional rigs; 390 biome/style skins and matching head inventory models; custom entity textures only.'})
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 for relative,data in build().items():
  p=ROOT/relative
  if args.check:assert p.read_bytes()==data,relative
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 print('ENEMY CATALOGUE:',26,'biomes x 5 species x 3 styles = 390 appearances;', 'equal' if args.check else 'generated')
if __name__=='__main__':main()
