"""Generate Alfheim's crystallised mana — six transparent 32px crystals and six bifurcated geodes.

Worldgen, growth, loot and pairing behavior are preserved from the runtime-proven crystal generator.
The visual source is now tools/material_texture.py rather than tinted vanilla amethyst assets.
"""
import argparse
import hashlib
import io
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from material_texture import (  # noqa: E402
    OUTPUT_SIZE, VARIANT_COUNT, ROTATIONS, render_crystal_texture
)

NS='alfheim'
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST=os.path.join(ROOT,'tools','crystals_manifest.json')
DATA=os.path.join(ROOT,'kubejs','data')
TEX_BLOCK=os.path.join(ROOT,'kubejs','assets',NS,'textures','block')
TEX_ITEM=os.path.join(ROOT,'kubejs','assets',NS,'textures','item')
MODEL_ITEM=os.path.join(ROOT,'kubejs','assets',NS,'models','item')
MODEL_BLOCK=os.path.join(ROOT,'kubejs','assets',NS,'models','block')
BLOCKSTATE=os.path.join(ROOT,'kubejs','assets',NS,'blockstates')
STARTUP=os.path.join(ROOT,'kubejs','startup_scripts','13_crystals.js')
LOOT=os.path.join(ROOT,'kubejs','server_scripts','13_crystal_loot.js')


def _png(image):
    stream=io.BytesIO(); image.save(stream,format='PNG'); return stream.getvalue()


def _variant_name(name,variant):
    return name if variant==0 else f'{name}_v{variant}'


def _model_variant_name(name,variant):
    return name if variant==0 else f'{name}__v{variant}'


def _write(path,content,dry=False,check=False,binary=False):
    if isinstance(content,str) and binary:
        content=content.encode()
    if dry:
        print('   [dry]',os.path.relpath(path,ROOT)); return
    if check:
        mode='rb' if isinstance(content,(bytes,bytearray)) else 'r'
        kwargs={} if 'b' in mode else {'encoding':'utf-8'}
        with open(path,mode,**kwargs) as f:
            actual=f.read()
        if actual!=content:
            raise AssertionError(os.path.relpath(path,ROOT))
        return
    os.makedirs(os.path.dirname(path),exist_ok=True)
    mode='wb' if isinstance(content,(bytes,bytearray)) else 'w'
    kwargs={} if 'b' in mode else {'encoding':'utf-8'}
    with open(path,mode,**kwargs) as f:
        f.write(content)


def _write_json(path,obj,dry=False,check=False):
    _write(path,json.dumps(obj,indent=2)+'\n',dry,check)


def noise_split(a,b,kind,seed,p):
    def state(cid):
        return {'Name':f'{NS}:{cid}_block'} if kind=='block' else {'Name':f'{NS}:budding_{cid}'}
    return {
        'type':'minecraft:noise_threshold_provider','seed':seed,
        'noise':{'firstOctave':p['noise_first_octave'],'amplitudes':[1.0]},
        'scale':p['noise_scale'],'threshold':0.0,'high_chance':1.0,
        'default_state':state(a),'low_states':[state(a)],'high_states':[state(b)]
    }


def geode_config(g,p,small):
    a,b=g['pair']
    seed=int(hashlib.sha1(g['id'].encode()).hexdigest()[:6],16)
    clusters=[{'Name':f'{NS}:{c}_cluster','Properties':{'facing':'up','waterlogged':'false'}} for c in (a,b)]
    layers=({'filling':1.0,'inner_layer':1.5,'middle_layer':2.0,'outer_layer':2.6} if small else
            {'filling':1.7,'inner_layer':2.2,'middle_layer':3.2,'outer_layer':4.2})
    wall=({'type':'minecraft:uniform','value':{'min_inclusive':1,'max_inclusive':2}} if small else
          {'type':'minecraft:uniform','value':{'min_inclusive':4,'max_inclusive':6}})
    points=({'type':'minecraft:uniform','value':{'min_inclusive':1,'max_inclusive':2}} if small else
            {'type':'minecraft:uniform','value':{'min_inclusive':3,'max_inclusive':4}})
    return {
        'type':'minecraft:geode','config':{
            'blocks':{
                'filling_provider':{'type':'minecraft:simple_state_provider','state':{'Name':'minecraft:air'}},
                'inner_layer_provider':noise_split(a,b,'block',seed,p),
                'alternate_inner_layer_provider':noise_split(a,b,'budding',seed,p),
                'middle_layer_provider':{'type':'minecraft:simple_state_provider','state':{'Name':'minecraft:calcite'}},
                'outer_layer_provider':{'type':'minecraft:simple_state_provider','state':{'Name':'minecraft:smooth_basalt'}},
                'inner_placements':clusters,
                'cannot_replace':'#minecraft:features_cannot_replace',
                'invalid_blocks':'#minecraft:geode_invalid_blocks'
            },
            'layers':layers,
            'crack':{'generate_crack_chance':0.95 if not small else 1.0,'base_crack_size':2.0,'crack_point_offset':2},
            'noise_multiplier':0.05,'use_potential_placements_chance':0.4,
            'use_alternate_layer0_chance':0.14,'placements_require_layer0_alternate':True,
            'outer_wall_distance':wall,'distribution_points':points,
            'point_offset':{'type':'minecraft:uniform','value':{'min_inclusive':1,'max_inclusive':2}},
            'min_gen_offset':-16,'max_gen_offset':16,'invalid_blocks_threshold':1
        }
    }


def _write_cube_variants(name,texture_names,dry,check):
    alternatives=[]
    for variant,tex in enumerate(texture_names):
        model=_model_variant_name(name,variant)
        _write_json(os.path.join(MODEL_BLOCK,model+'.json'),{
            'parent':'minecraft:block/cube_all','textures':{'all':f'{NS}:block/{tex}'}
        },dry,check)
        for rotation in ROTATIONS:
            entry={'model':f'{NS}:block/{model}'}
            if rotation: entry['y']=rotation
            alternatives.append(entry)
    _write_json(os.path.join(BLOCKSTATE,name+'.json'),{'variants':{'':alternatives}},dry,check)


def _generate_visuals(crystals,dry,check):
    catalog=[]
    for c in crystals:
        row={'id':c['id'],'element':c['element'],'variants':{}}
        for kind in ('block','budding','cluster'):
            name={'block':f"{c['id']}_block",'budding':f"budding_{c['id']}",'cluster':f"{c['id']}_cluster"}[kind]
            names=[]
            for variant in range(VARIANT_COUNT):
                tex=_variant_name(name,variant); names.append(tex)
                image=render_crystal_texture(c,kind,variant)
                _write(os.path.join(TEX_BLOCK,tex+'.png'),_png(image),dry,check)
            row['variants'][kind]=names
            if kind in ('block','budding'):
                _write_cube_variants(name,names,dry,check)
            else:
                # Keep the runtime-proven cross geometry. Texture is genuinely transparent now.
                _write_json(os.path.join(MODEL_BLOCK,name+'.json'),{
                    'parent':'minecraft:block/cross','textures':{'cross':f'{NS}:block/{name}'}
                },dry,check)
        shard=f"{c['id']}_shard"
        image=render_crystal_texture(c,'shard',0)
        _write(os.path.join(TEX_ITEM,shard+'.png'),_png(image),dry,check)
        _write_json(os.path.join(MODEL_ITEM,shard+'.json'),{
            'parent':'minecraft:item/generated','textures':{'layer0':f'{NS}:item/{shard}'}
        },dry,check)
        catalog.append(row)
        if not check:
            print(f"   crystal {c['id']:<12} {c['element']:<7} 32px transparent block/budding/cluster/shard")
    _write_json(os.path.join(ROOT,'kubejs','crystal_texture_catalog.json'),{
        'resolution':OUTPUT_SIZE,'variant_count':VARIANT_COUNT,'rotations':list(ROTATIONS),'crystals':catalog
    },dry,check)
    return catalog


def _generate_startup(crystals,dry,check):
    L=['// Alfheim Reclaimed — crystallised mana',
       '// GENERATED by tools/gen_crystals.py from tools/crystals_manifest.json — do not hand-edit.',
       '// 32px transparent material art comes from tools/material_texture.py.',
       "StartupEvents.registry('block', event => {"]
    for c in crystals:
        cid,nm=c['id'],c['name']
        L.append(f"    event.create('{NS}:{cid}_block').displayName('{nm} Block')"
                 f".soundType('amethyst').hardness(1.5).resistance(1.5).requiresTool(true)"
                 f".tagBlock('minecraft:mineable/pickaxe').tagBlock('{NS}:crystal_blocks')"
                 f".defaultTranslucent().textureAll('{NS}:block/{cid}_block')")
        L.append(f"    event.create('{NS}:budding_{cid}').displayName('Budding {nm}')"
                 f".soundType('amethyst').hardness(1.5).resistance(1.5).requiresTool(true)"
                 f".tagBlock('minecraft:mineable/pickaxe').tagBlock('{NS}:budding_crystals')"
                 f".defaultTranslucent().textureAll('{NS}:block/budding_{cid}')"
                 f".randomTick(ctx => growCluster(ctx, '{NS}:{cid}_cluster'))")
        L.append(f"    event.create('{NS}:{cid}_cluster').displayName('{nm} Cluster')"
                 f".soundType('amethyst_cluster').hardness(1.5).resistance(1.5)"
                 f".requiresTool(true).defaultTranslucent().notSolid().lightLevel(0.4)"
                 f".tagBlock('minecraft:mineable/pickaxe').tagBlock('{NS}:crystal_clusters')"
                 f".model('{NS}:block/{cid}_cluster')")
    L+=['})','',"StartupEvents.registry('item', event => {"]
    for c in crystals:
        L.append(f"    event.create('{NS}:{c['id']}_shard').displayName('{c['name']} Shard')"
                 f".tooltip('{c.get('tooltip', c['name'] + ' crystal shard.')}').rarity('uncommon').tag('{NS}:crystal_shards')")
    L+=['})','',
        'function growCluster(ctx, clusterId) {',
        '    if (ctx.random.nextFloat() > 0.2) return',
        "    const faces = ['up', 'down', 'north', 'south', 'east', 'west']",
        '    const face = faces[ctx.random.nextInt(faces.length)]',
        '    const target = ctx.block.offset(face)',
        "    if (target.id !== 'minecraft:air') return",
        '    target.set(clusterId, { facing: face })',
        '}','']
    _write(STARTUP,'\n'.join(L),dry,check)

    LL=['// Alfheim Reclaimed — crystal drops','// GENERATED by tools/gen_crystals.py — do not hand-edit.',
        'ServerEvents.blockLootTables(event => {']
    for c in crystals:
        cid=c['id']
        LL.append(f"    event.addSimpleBlock('{NS}:{cid}_block')")
        LL.append(f"    event.addSimpleBlock('{NS}:{cid}_cluster', Item.of('{NS}:{cid}_shard', 4))")
    LL+=['',f"    console.info('[Alfheim Reclaimed] {len(crystals)} crystal loot sets registered.')",'})','']
    _write(LOOT,'\n'.join(LL),dry,check)


def _generate_worldgen(crystals,geodes,p,dry,check):
    for g in geodes:
        gid=g['id']
        _write_json(os.path.join(DATA,NS,'worldgen','configured_feature',f'geode_{gid}.json'),geode_config(g,p,False),dry,check)
        _write_json(os.path.join(DATA,NS,'worldgen','configured_feature',f'geode_{gid}_marker.json'),geode_config(g,p,True),dry,check)
        _write_json(os.path.join(DATA,NS,'worldgen','placed_feature',f'geode_{gid}.json'),{
            'feature':f'{NS}:geode_{gid}','placement':[
                {'type':'minecraft:rarity_filter','chance':g['rarity']},
                {'type':'minecraft:in_square'},
                {'type':'minecraft:heightmap','heightmap':'OCEAN_FLOOR_WG'},
                {'type':'minecraft:random_offset','xz_spread':0,'y_spread':p['depth_max']},
                {'type':'minecraft:random_offset','xz_spread':0,'y_spread':{
                    'type':'minecraft:uniform','value':{
                        'min_inclusive':p['depth_min']-p['depth_max'],'max_inclusive':0}}},
                {'type':'minecraft:biome'}
            ]},dry,check)
        _write_json(os.path.join(DATA,NS,'worldgen','placed_feature',f'geode_{gid}_marker.json'),{
            'feature':f'{NS}:geode_{gid}_marker','placement':[
                {'type':'minecraft:count','count':p['marker_count']},
                {'type':'minecraft:in_square'},
                {'type':'minecraft:heightmap','heightmap':'OCEAN_FLOOR_WG'},
                {'type':'minecraft:environment_scan','direction_of_search':'down','max_steps':p['scan_steps'],
                 'target_condition':{'type':'minecraft:matching_block_tag','tag':f'{NS}:budding_crystals'},
                 'allowed_search_condition':{'type':'minecraft:true'}},
                {'type':'minecraft:heightmap','heightmap':'OCEAN_FLOOR_WG'},
                {'type':'minecraft:biome'}
            ]},dry,check)
        _write_json(os.path.join(DATA,NS,'forge','biome_modifier',f'geode_{gid}.json'),{
            'type':'forge:add_features','biomes':g['biomes'],'features':f'{NS}:geode_{gid}','step':'local_modifications'
        },dry,check)
        _write_json(os.path.join(DATA,NS,'forge','biome_modifier',f'zz_geode_{gid}_marker.json'),{
            'type':'forge:add_features','biomes':g['biomes'],'features':f'{NS}:geode_{gid}_marker','step':'top_layer_modification'
        },dry,check)
        if not check:
            print(f"   geode   {gid:<14} {g['pair'][0]:<11}|{g['pair'][1]:<11} rarity 1/{g['rarity']:<3} {len(g['biomes'])} biome(s)")

    for c in crystals:
        _write_json(os.path.join(DATA,NS,'loot_tables','blocks',f'budding_{c["id"]}.json'),
                    {'type':'minecraft:block','pools':[]},dry,check)
    for tag,vals in (
        ('budding_crystals',[f'{NS}:budding_{c["id"]}' for c in crystals]),
        ('crystal_blocks',[f'{NS}:{c["id"]}_block' for c in crystals]),
        ('crystal_clusters',[f'{NS}:{c["id"]}_cluster' for c in crystals])):
        _write_json(os.path.join(DATA,NS,'tags','blocks',tag+'.json'),{'replace':False,'values':vals},dry,check)
    _write_json(os.path.join(DATA,NS,'tags','items','crystal_shards.json'),{
        'replace':False,'values':[f'{NS}:{c["id"]}_shard' for c in crystals]
    },dry,check)


def _review(crystals,dry,check):
    if dry: return
    # Checkerboard-backed contact sheet makes real transparency visible.
    cell=96; label=38; width=18+4*cell; height=56+len(crystals)*(cell+label)
    sheet=Image.new('RGB',(width,height),(24,30,38))
    from PIL import ImageDraw,ImageFont
    d=ImageDraw.Draw(sheet)
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    except Exception: font=ImageFont.load_default()
    d.text((16,16),'CRYSTAL TRANSPARENCY / BLOCK · BUDDING · CLUSTER · SHARD',font=font,fill=(235,227,210))
    for i,c in enumerate(crystals):
        y=50+i*(cell+label)
        d.text((16,y+cell+8),c['name'],font=font,fill=(220,220,214))
        names=[(TEX_BLOCK,f"{c['id']}_block"),(TEX_BLOCK,f"budding_{c['id']}"),(TEX_BLOCK,f"{c['id']}_cluster"),(TEX_ITEM,f"{c['id']}_shard")]
        for col,(root,name) in enumerate(names):
            im=Image.open(os.path.join(root,name+'.png')).convert('RGBA').resize((64,64),Image.Resampling.NEAREST)
            bg=Image.new('RGB',(64,64),(186,190,192)); bd=ImageDraw.Draw(bg)
            for yy in range(0,64,8):
                for xx in range(0,64,8):
                    if (xx//8+yy//8)%2: bd.rectangle((xx,yy,xx+7,yy+7),fill=(92,98,104))
            bg=bg.convert('RGBA'); bg.alpha_composite(im)
            sheet.paste(bg.convert('RGB'),(16+col*cell,y+10))
    path=os.path.join(ROOT,'tools','crystals_transparency_review.png')
    data=_png(sheet)
    if check:
        with open(path,'rb') as f: assert f.read()==data,path
    else:
        with open(path,'wb') as f: f.write(data)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    if args.dry_run and args.check: raise SystemExit('choose --dry-run or --check')
    m=json.load(open(MANIFEST,encoding='utf-8')); crystals=m['crystals']; geodes=m.get('geodes',[]); p=m.get('placement')
    _generate_visuals(crystals,args.dry_run,args.check)
    _generate_startup(crystals,args.dry_run,args.check)
    if geodes and p:
        _generate_worldgen(crystals,geodes,p,args.dry_run,args.check)
    _review(crystals,args.dry_run,args.check)
    if args.check:
        print(f'PASS: {len(crystals)} crystal families reproduce at {OUTPUT_SIZE}x{OUTPUT_SIZE}, '
              f'{VARIANT_COUNT} full-block variants with rotations {ROTATIONS}; transparent crystal assets')
        return 0
    pairs={frozenset(g['pair']) for g in geodes}; used={c for g in geodes for c in g['pair']}
    print(f'\n  {len(crystals)} crystals -> {len(crystals)*3} blocks, {len(crystals)} shards')
    print(f'  {len(geodes)} bifurcated geodes ({len(pairs)} distinct pairs), {len(geodes)*2} features, {len(geodes)*2} modifiers')
    print(f'  crystals appearing in at least one geode: {len(used)}/{len(crystals)}')
    per={}
    for g in geodes:
        for b in g['biomes']: per[b]=per.get(b,0.0)+1.0/g['rarity']
    if per:
        worst_b=max(per,key=per.get); worst=per[worst_b]; med=sorted(per.values())[len(per)//2]
        print(f'  geode density per biome: densest {worst_b} 1 in {1/worst:.0f} chunks ({worst*24:.1f}x vanilla amethyst), median 1 in {1/med:.0f}')
    return 0

if __name__=='__main__':
    sys.exit(main())
