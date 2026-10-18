"""Naturally generate a complete Worldstone in a fresh world and read saved blocks."""
import argparse,hashlib,json,math,re,time
from collections import Counter
from pathlib import Path
import run_server
from probe_terraces import chunks,section_blocks

ROOT=Path(__file__).resolve().parents[1]
SEED='-5876049240305171930';REPORT=ROOT/'tools/worldstone_runtime_report.json'
HOME='execute in mythicbotany:alfheim run '


def density(x,y,z):
    a=(x+2.5*math.sin(z*.035))/114;b=(z+2*math.sin(x*.029))/110;c=(y-60)/100
    return a*a+b*b+c*c+.018*math.sin(x*.11+z*.07)*math.cos(y*.06)+.012*math.cos(z*.14-y*.03)


def crystal(x,y,z):
    if -8<=y<=128:
        t=(y+8)/136;r=32*t/.30 if t<.30 else 32-(t-.30)*9 if t<.67 else (1-t)*28.67/.33
        a=x-(-8+18*t);b=z-(4-9*t);u=.9238795*a+.3826834*b;v=-.3826834*a+.9238795*b
        d=max(abs(u),abs(v),(abs(u)+abs(v))*.70710678)
        if d<=max(.6,r):
            return 2 if d<r*.60 or abs(u-v*.36-2*math.sin(y*.045))<1.1 or abs(v+u*.22-6)<.65 else 1
    for a,b,c,r,h in ((-49,36,16,6,15),(44,74,-26,7,19),(-37,108,-29,5,12),(33,13,35,5,11)):
        d=abs(x-a)/r+abs(z-c)/r+abs(y-b)/h
        if d<=1:return 2 if d<.32 else 1
    return 0


def shelf(x,y,z):
    return y<=12 and (math.hypot(x,z)>=82 or (-88<=x<=-52 and abs(z)<=5 and y>=-12+(x+88)*.3))


class Plan:
    def __init__(self):self.expanded=False;self.site=None;self.commands=[(1,'gamerule doMobSpawning false'),(0,'gamerule randomTickSpeed 0'),(1,HOME+'alfheim_fairy_islands_audit -12 -4')]
    def __iter__(self):return iter(self.commands) if self.expanded else self.expand()
    def expand(self):
        yield from self.commands;self.expanded=True
        queries=[(-16,0),(8,8),(-16,8),(8,-16),(-16,-16)]
        queries += [(x,z) for x in (-32,-24,-16,-8,0,8,16,24) for z in (-32,-24,-16,-8,0,8,16,24) if (x,z) not in queries]
        for x,z in queries:
            command=(1,HOME+f'alfheim_worldstone_audit {x} {z}');self.commands.append(command);yield command
            deadline=time.monotonic()+90
            while True:
                console=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
                log=console.read_text(encoding='utf-8',errors='replace')
                if f'WORLDSTONE_AUDIT region={x},{z} ' in log:break
                if time.monotonic()>deadline:raise RuntimeError('Native Worldstone audit did not finish')
                time.sleep(.25)
            sites=re.findall(r'WORLDSTONE_SITE x=(-?\d+) z=(-?\d+) summit=(\d+) cover=(\d+)',log)
            if sites:
                a,b,h,cover=map(int,sites[0]);self.site=dict(x=a,z=b,summit=h,minimum_sampled_cover=cover);break
        extra=[]
        if self.site:
            x,z=self.site['x'],self.site['z']
            extra=[(1,HOME+f'forceload add {x-119} {z-119} {x+119} {z+119}'),
                   (90,'save-all flush'),(1,HOME+f'alfheim_worldstone_gameplay {x} {z}'),
                   (2,'save-all flush'),(2,HOME+'forceload remove all'),(4,'save-all flush')]
        extra.append((1,'stop'));self.commands.extend(extra);yield from extra


def load_world(report):
    site=report['site'];x,z=site['x'],site['z']
    required={(cx,cz) for cx in range((x-119)//16,(x+119)//16+1) for cz in range((z-119)//16,(z+119)//16+1)}
    region=ROOT/'server'/report['world']/'dimensions/mythicbotany/alfheim/region'
    grid={}
    for rx,rz in sorted({(a//32,b//32) for a,b in required}):
        for c in chunks(region/f'r.{rx}.{rz}.mca'):
            key=int(c['xPos']),int(c['zPos'])
            if key in required:grid[key]=c
    cache={}
    def block(dx,y,dz):
        ax,az=x+dx,z+dz;key=ax//16,y//16,az//16
        if key not in cache:
            section=next((s for s in grid.get((ax//16,az//16),{}).get('sections',[]) if int(s['Y'])==y//16),None)
            cache[key]=section_blocks(section) if section else None
        return cache[key][((y&15)<<8)|((az&15)<<4)|(ax&15)] if cache[key] else None
    return grid,required,block


def verify(report):
    assert report['site'],'No naturally eligible high-mountain site found'
    s=report['site'];assert s['summit']>=260 and s['minimum_sampled_cover']>=32
    grid,required,block=load_world(report);assert set(grid)==required,(len(grid),len(required))
    start=grid[s['x']//16,s['z']//16]['structures']['starts'].get('alfheim:mountain_worldstone')
    assert start and start.get('id')=='alfheim:mountain_worldstone' and len(start['Children'])==1,start
    piece=start['Children'][0];assert piece['CentreX']==s['x'] and piece['CentreZ']==s['z'],piece
    assert [int(v) for v in piece['BB']]==[s['x']-119,-48,s['z']-119,s['x']+119,168,s['z']+119]
    solids={'alfheim:obsidian_livingrock','alfheim:cracked_livingrock','alfheim:starfleck_livingrock'}
    matches=0;total=0;crystals=0;fluids=0
    for x in range(-112,113,8):
        for z in range(-112,113,8):
            for y in range(-40,161,8):
                q=density(x,y,z)
                if q>=.97:continue
                actual=block(x,y,z);material=crystal(x,y,z)
                expected=solids if shelf(x,y,z) else {'alfheim_companion:worldstone_crystal'} if material==1 else {'alfheim_companion:worldstone_heart'} if material==2 else {'minecraft:air','minecraft:cave_air'}
                total+=1;matches+=actual in expected;crystals+=actual in {'alfheim_companion:worldstone_crystal','alfheim_companion:worldstone_heart'}
                fluids+=actual in {'minecraft:water','minecraft:lava'}
    assert matches/total>=.98,(matches,total)
    assert crystals>=150 and fluids==0,(crystals,fluids)
    # Both pointed ends have a substantial open-air gap to the cavern itself.
    for y in range(-34,-9):assert block(-8,y,4) in ('minecraft:air','minecraft:cave_air'),('lower gap',y,block(-8,y,4))
    for y in range(130,154):assert block(10,y,-5) in ('minecraft:air','minecraft:cave_air'),('upper gap',y,block(10,y,-5))
    assert block(-8,-8,4).startswith('alfheim_companion:worldstone')
    assert block(10,128,-5).startswith('alfheim_companion:worldstone')
    # The mountain above the complete authored envelope still contains natural rock.
    roof_samples=0
    for x in range(-32,33,16):
        for z in range(-32,33,16):
            for y in range(180,225,4):
                b=block(x,y,z)
                if b not in ('minecraft:air','minecraft:cave_air','minecraft:water','minecraft:lava',None):roof_samples+=1
    assert roof_samples>=250,roof_samples
    for x in range(-112,113,16):
        for z in range(-112,113,16):assert block(x,-64,z)=='minecraft:bedrock',('bedrock',x,z,block(x,-64,z))
    # Lighting is read from the saved game's light arrays, not inferred from a texture.
    lit=any(any(int(v)!=0 for v in sec.get('BlockLight',b'')) for c in grid.values() for sec in c.get('sections',[]) if -1<=int(sec['Y'])<=8)
    assert lit,'Saved chamber has no block light'
    counts=Counter()
    for c in grid.values():
        for sec in c.get('sections',[]):
            if any(p['Name'].startswith('alfheim_companion:worldstone') for p in sec.get('block_states',{}).get('palette',[])):
                counts.update(b for b in section_blocks(sec) if b.startswith('alfheim_companion:worldstone'))
    assert counts['alfheim_companion:worldstone_fragment_ore']>=100,counts
    assert counts['alfheim_companion:worldstone_cluster']>=100,counts
    assert counts['alfheim_companion:worldstone_crystal']>=10000,counts
    gameplay=report.get('gameplay')
    assert gameplay and gameplay['harvest_regrowth'] and gameplay['compass_target_saved'] and len(gameplay['native_recipes'])==6,gameplay
    assert len(gameplay['growth_stages'])==4 and gameplay['budding_silk_touch_drops']==0,gameplay
    assert any('accepted=1' in s or re.search(r'accepted=[2-9]',s) for s in report['fairy_regression']),report['fairy_regression']
    report.update(status='NATURAL_WORLDSTONE_CAVERN_AND_SUSPENDED_CRYSTAL_VERIFIED',chunks=len(grid),sampled_blocks=total,
                  matching_blocks=matches,crystal_samples=crystals,fluid_samples=fluids,roof_solid_samples=roof_samples,
                  saved_block_light=True,pointed_tip_air_gaps=True,bedrock_preserved=True,piece=piece,
                  natural_resource_counts=dict(counts),gameplay_verified=True,
                  client_visual_review='pending; saved-chunk sections are not Minecraft screenshots')
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    print('WORLDSTONE PASS:',s,len(grid),'chunks;',matches,'/',total,'matching samples;',crystals,'crystal samples; open tip gaps and saved lighting')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify-only',action='store_true');args=ap.parse_args()
    if args.verify_only:return verify(json.loads(REPORT.read_text()))
    world=time.strftime('validation-worldstone-%Y%m%d-%H%M%S');server=(ROOT/'server').resolve()
    assert not (server/world).exists()
    for name in run_server.MIRROR:
        target=(server/name).resolve();assert target.is_relative_to(server) and target!=server
    props=server/'server.properties';old=props.read_bytes();before=set(server.glob('console-*.log'));plan=Plan()
    try:code=run_server.run(SEED,world,8,plan,900)
    finally:props.write_bytes(old)
    console=max(set(server.glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    log=console.read_text(encoding='utf-8',errors='replace')
    probes=re.findall(r'WORLDSTONE_GAMEPLAY (\{[^\n]+\})',log)
    report=dict(world=world,seed=SEED,console=console.name,exit_code=code,site=plan.site,
        survey=re.findall(r'WORLDSTONE_(?:SITE|AUDIT) [^\n]+',log),status='PENDING_SAVED_WORLD_VERIFICATION',
        gameplay=json.loads(probes[-1]) if probes else None,fairy_regression=re.findall(r'FAIRY_SURVEY [^\n]+',log),
        jar_sha256=hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest())
    REPORT.write_text(json.dumps(report,indent=2)+'\n');assert code==0;verify(report)


if __name__=='__main__':main()
