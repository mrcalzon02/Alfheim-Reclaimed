"""Read-only survey of existing generated columns; no terrain or save writes."""
import argparse
from collections import Counter
import json
from pathlib import Path
from probe_terraces import chunks

ROOT=Path(__file__).resolve().parents[1]

def rotate(x,z,r):
    for _ in range(r):x,z=-z,x
    return x,z

def load_columns(world):
    region=Path(world)/'dimensions/mythicbotany/alfheim/region'
    grid={};chunk_count=0
    for f in region.glob('*.mca'):
        if f.stat().st_size<8192:continue
        for c in chunks(f):
            hm=c.get('Heightmaps',{})
            if 'WORLD_SURFACE' not in hm or 'OCEAN_FLOOR' not in hm:continue
            chunk_count+=1
            for i in range(256):
                surface=((int(hm['WORLD_SURFACE'][i//7])>>((i%7)*9))&511)-64
                floor=((int(hm['OCEAN_FLOOR'][i//7])>>((i%7)*9))&511)-64
                grid[(int(c['xPos'])*16+i%16,int(c['zPos'])*16+i//16)]=(surface,floor)
    return grid,chunk_count

def main():
    ap=argparse.ArgumentParser();ap.add_argument('world')
    ap.add_argument('--adaptive',action='store_true')
    ap.add_argument('--output',default='harbor_saved_coast_survey.json')
    args=ap.parse_args()
    grid,chunk_count=load_columns(args.world)
    parts=json.loads((ROOT/'tools/harbor_complex_layout.json').read_text())['layout']
    reasons=Counter();candidates=[];preflight=0;probes=[]
    # The roads-test district exclusion belongs only to that decorated save.
    # Native auditing must resolve any remaining decoration-related false positives.
    roads_fixture=Path(args.world).name=='validation-roads-trade-20261012'
    def artificial(x,z):return (abs(x)<400 and abs(z)<400) or (roads_fixture and -1550<=x<=-1250 and 540<=z<=820)
    for x,z in sorted(grid):
        if x%16 or z%16 or artificial(x,z):continue
        for r in range(4):
            dx,dz=rotate(23,-20,r);wet=grid.get((x+dx,z+dz))
            dx,dz=rotate(23,23,r);dry=grid.get((x+dx,z+dz))
            dx,dz=rotate(23,100,r);approach=grid.get((x+dx,z+dz))
            max_land=73 if args.adaptive else 67
            min_land=58 if args.adaptive else 64
            def dry_ok(c):return c and min_land<=c[0]<=max_land and c[1]>=58 and (not args.adaptive or c[0]==c[1])
            if not wet or not dry:continue
            if not(wet[0]==64 and 58<=wet[1]<64 and dry_ok(dry)):continue
            if args.adaptive and not dry_ok(approach):continue
            preflight+=1;probes.append({'x':x,'z':z,'rotation':r});failure=None
            for n in parts:
                b=n['bounds'];marine=n['name'] in ('wavebreak_pier','sunken_drydock')
                for px in sorted(set(range(b[0],b[3]+1,8))|{b[3]}):
                    for pz in sorted(set(range(b[2],b[5]+1,8))|{b[5]}):
                        dx,dz=rotate(px,pz,r);c=grid.get((x+dx,z+dz))
                        if not c:failure='outside_saved_columns'
                        else:
                            shallow=c[0]==64 and 58<=c[1]<64
                            mixed=args.adaptive and ((-16<=pz<16) or not marine)
                            if marine and not mixed:
                                if not shallow:failure='dock_waterline_or_depth'
                            elif mixed and shallow:pass
                            elif not dry_ok(c):failure='land_height_or_support'
                        if failure:break
                    if failure:break
                if failure:break
            if failure:reasons[failure]+=1
            else:candidates.append({'x':x,'z':z,'rotation':r})
    result={'world':str(Path(args.world)),'saved_chunks':chunk_count,'columns':len(grid),'shallow_water_columns':sum(s==64 and 58<=f<64 for s,f in grid.values()),'coarse_shore_candidates':preflight,'rejections':dict(reasons),'preflight_candidates':probes,'candidates_for_live_audit':candidates,'scope':'decorated saved heightmaps; fluid identity and full native generation require live checks'}
    result['policy']='adaptive with dry approach' if args.adaptive else 'original strict quay'
    output=Path(args.output)
    if output.name!=args.output or output.suffix!='.json':raise ValueError('Output must be a JSON filename')
    (ROOT/'tools'/output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('preflight_candidates','candidates_for_live_audit')},indent=2))
    print('Coarse candidates for native checks:',len(candidates))

if __name__=='__main__':main()
