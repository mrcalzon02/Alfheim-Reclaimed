"""Read-only comparison of saved assembly poses with a same-seed reference patch.

These measurements are a review aid, not a natural-generation placement gate.
Vegetation is excluded from ground, and natural structure bounding boxes are
reported separately instead of treating existing masonry as native terrain.
"""
from collections import Counter
import argparse,hashlib,json
from pathlib import Path
import nbt
from probe_terraces import chunks,section_blocks,biome_at
from check_ancient_assembly import world_pos,rotate

ROOT=Path(__file__).resolve().parents[1]
FAMILIES=('sacred_precinct','military_warden','frontier_stewardship')
GROUND={'minecraft:'+n for n in ('stone','deepslate','andesite','diorite','granite','tuff','calcite',
    'grass_block','dirt','coarse_dirt','dirt_path','farmland','podzol','mycelium','rooted_dirt','mud','clay',
    'sand','red_sand','sandstone','red_sandstone','gravel','bedrock','ice','packed_ice','snow_block',
    'obsidian','end_stone','netherrack','smooth_basalt','amethyst_block','budding_amethyst',
    'raw_iron_block','raw_copper_block')} | {'botania:livingrock'}
for tag in ('livingrock_natural','void_natural','crystal_blocks','budding_crystals'):
    GROUND.update(json.loads((ROOT/f'kubejs/data/alfheim/tags/blocks/{tag}.json').read_text(encoding='utf-8'))['values'])

def natural(name):
    return (name in GROUND or name.endswith('_ore') or
            (name.startswith('alfheim:') and name.endswith('_livingrock')) or
            (name.startswith('botania:metamorphic_') and name.endswith('_stone')))

class Reference:
    def __init__(self,world,bounds):
        self.bounds=bounds;self.grid={};self.decoded={};self.heights={};self.biomes={};self.structures={}
        x0,z0,x1,z1=bounds
        for file in (world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
            if file.stat().st_size<8192:continue
            for chunk in chunks(file):
                cx,cz=chunk['xPos'],chunk['zPos']
                if not (x0//16<=cx<=x1//16 and z0//16<=cz<=z1//16):continue
                self.grid[cx,cz]=chunk
                heights={}
                for sec in sorted(chunk.get('sections',[]),key=lambda s:s['Y'],reverse=True):
                    if not any(natural(p['Name']) for p in sec.get('block_states',{}).get('palette',[])):continue
                    blocks=self.section(cx,cz,int(sec['Y']))
                    for i in range(4095,-1,-1):
                        col=i&255
                        if col not in heights and natural(blocks[i]):heights[col]=(int(sec['Y'])*16+(i>>8),blocks[i])
                    if len(heights)==256:break
                for col,height in heights.items():self.heights[cx*16+(col&15),cz*16+(col>>4)]=height
                for sid,start in chunk.get('structures',{}).get('starts',{}).items():
                    for child in start.get('Children',[]):
                        bb=child.get('BB')
                        if bb:self.structures[sid,tuple(map(int,bb))]=True

    def section(self,cx,cz,sy):
        key=(cx,cz,sy)
        if key not in self.decoded:
            sec=next((s for s in self.grid[cx,cz].get('sections',[]) if s['Y']==sy),None)
            self.decoded[key]=section_blocks(sec) if sec else None
        return self.decoded[key]

    def block(self,x,y,z):
        if (x//16,z//16) not in self.grid:return None
        values=self.section(x//16,z//16,y//16)
        return values[((y&15)<<8)|((z&15)<<4)|(x&15)] if values else 'minecraft:air'

    def biome(self,x,z):
        y=self.heights.get((x,z),(-64,''))[0];key=(x//4,y//4,z//4)
        if key not in self.biomes:
            chunk=self.grid.get((x//16,z//16))
            self.biomes[key]=biome_at(chunk.get('sections',[]),y,x&15,z&15) if chunk else None
        return self.biomes[key]

def support(reference,points):
    contact=0;gaps=Counter();missing=0;wet=0
    for x,y,z in points:
        below=reference.block(x,y-1,z)
        if below is None:missing+=1;continue
        if natural(below):contact+=1;gaps[0]+=1;continue
        wet+=below in ('minecraft:water','minecraft:lava')
        gap=next((d for d in range(1,33) if natural(reference.block(x,y-1-d,z) or '')),33)
        gaps[gap]+=1
    return {'columns':len(points),'contact_columns':contact,'contact_fraction':round(contact/len(points),5),
        'missing_reference_columns':missing,'fluid_immediately_below':wet,
        'unsupported_columns':len(points)-contact-missing,'max_gap_below_base':max(gaps,default=0),
        'unresolved_beyond_32_columns':gaps[33],
        'gap_histogram':dict(sorted(gaps.items())),'gap_search_limit':32}

def seed(world):
    return int(nbt.load(str(world/'level.dat'))[1]['Data']['WorldGenSettings']['seed'])

def footing_plan(reference,points):
    """Compact review-only runs; no writes or executable fill commands."""
    groups={};blocked=[];unresolved=0
    airish={'minecraft:air','minecraft:cave_air','minecraft:void_air','minecraft:water','minecraft:lava',
            'minecraft:grass','minecraft:fern','minecraft:tall_grass','minecraft:large_fern','minecraft:wheat'}
    for x,y,z in points:
        below=reference.block(x,y-1,z)
        if below is None or natural(below):continue
        gap=next((d for d in range(1,33) if natural(reference.block(x,y-1-d,z) or '')),None)
        if gap is None:unresolved+=1;continue
        obstruction={reference.block(x,yy,z) for yy in range(y-gap,y)}-airish
        if obstruction:blocked.append({'position':[x,y,z],'blocks':sorted(str(b) for b in obstruction)});continue
        groups.setdefault((z,y-gap,y-1),[]).append(x)
    runs=[]
    for (z,lo,hi),xs in sorted(groups.items()):
        ordered=sorted(xs);start=last=ordered[0]
        for x in ordered[1:]+[ordered[-1]+2]:
            if x==last+1:last=x;continue
            runs.append([start,last,z,lo,hi]);start=last=x
    return {'run_format':['x_min','x_max','z','y_min','y_max'],'runs':runs,
        'block_count':sum((b-a+1)*(hi-lo+1) for a,b,z,lo,hi in runs),'obstructed_columns':blocked,
        'unresolved_columns':unresolved,'status':'review_only_not_applied',
        'limit':'Air/fluid or listed replaceable vegetation above existing ground within 32 blocks. Other blocks require review. Do not apply before normal terrain-adaptation review.'}

def self_test():
    class Plane:
        def block(self,x,y,z):return 'minecraft:stone' if y<=64 else 'minecraft:air'
    points=[(x,65,z) for x in range(4) for z in range(4)]
    assert support(Plane(),points)['contact_columns']==16
    raised=support(Plane(),[(x,69,z) for x,y,z in points])
    assert raised['contact_columns']==0 and raised['max_gap_below_base']==4
    class Wet:
        def block(self,x,y,z):return 'minecraft:stone' if y<=60 else 'minecraft:water' if y<=64 else 'minecraft:air'
    wet=support(Wet(),points)
    assert wet['contact_columns']==0 and wet['fluid_immediately_below']==16 and wet['max_gap_below_base']==4
    assert not natural('botania:dreamwood_log') and not natural('minecraft:oak_leaves')
    assert natural('mythicbotany:elementium_ore') and natural('minecraft:iron_ore')
    assert natural('botania:metamorphic_fungal_stone') and natural('alfheim:rootglass_block')
    assert footing_plan(Plane(),[(0,69,0),(1,69,0)])['runs']==[[0,1,0,65,68]]
    assert world_pos((1,0,2),(10,65,20),1)==(8,65,21)
    print('TERRAIN REVIEW SELF-TEST PASS: contact, exposed gaps, water, vegetation exclusion and rotation')

def review(reference,family):
    saved=json.loads((ROOT/f'tools/{family}_runtime_census.json').read_text(encoding='utf-8'))
    saved_world=Path(saved['world'])
    if not saved_world.is_absolute():saved_world=ROOT/saved_world
    assert seed(saved_world)==reference.seed,('reference seed differs from saved assembly',family)
    actual=Reference(saved_world,reference.bounds)
    pieces=[];hashes={};all_points=[];entries=[]
    for node in saved['layout']:
        path=ROOT/f'kubejs/data/alfheim/structures/ancient/{family}/{node["name"]}.nbt'
        raw=nbt.load(str(path))[1];sx,sy,sz=map(int,raw['size'])
        hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        origin=node['origin'];r=node['rotation'];floor=int(origin[1])+8
        points=[world_pos((x,0,z),origin,r) for x in range(sx) for z in range(sz)]
        all_points.extend(points);metrics=support(reference,points)
        biomes=Counter(reference.biome(x,z) or 'missing' for x,y,z in points)
        cuts=Counter();earth=0
        for x,y,z in points:
            top=reference.heights.get((x,z),(-64,''))[0];cuts[max(0,top-floor)]+=1
        for b in raw['blocks']:
            if raw['palette'][int(b['state'])]['Name']!='minecraft:air' or int(b['pos'][1])<9:continue
            x,y,z=world_pos(b['pos'],origin,r)
            if y<=reference.heights.get((x,z),(-64,''))[0] and natural(reference.block(x,y,z) or ''):earth+=1
        corners=[world_pos(p,origin,r) for p in ((0,0,0),(sx-1,sy-1,sz-1),(0,0,sz-1),(sx-1,0,0))]
        bounds=[min(p[i] for p in corners) for i in range(3)]+[max(p[i] for p in corners) for i in range(3)]
        collisions=[{'structure':sid,'bounds':bb} for sid,bb in reference.structures
            if all(max(bounds[i],bb[i])<=min(bounds[i+3],bb[i+3]) for i in range(3))]
        cells={tuple(map(int,b['pos'])):raw['palette'][int(b['state'])]['Name'] for b in raw['blocks']}
        for x,z,dx,dz in ((sx//2,0,0,-1),(sx//2,sz-1,0,1),(0,sz//2,-1,0),(sx-1,sz//2,1,0)):
            if cells.get((x,9,z)) not in ('minecraft:air','minecraft:jigsaw') or cells.get((x,10,z))!='minecraft:air':continue
            if any(cells.get((x-dx*k,y,z-dz*k))!='minecraft:air' for k in (1,2) for y in (9,10)):continue
            px,_,pz=world_pos((x,9,z),origin,r);ax,az=rotate(dx*2,dz*2,r)
            entries.append({'piece':node['name'],'edge':[px,pz],'outside':[px+ax,pz+az],
                            'feet_y':floor+1,'terrain_top':reference.heights.get((px+ax,pz+az),(-64,''))[0]})
        pieces.append({'name':node['name'],'origin':origin,'rotation':r,'floor_y':floor,'support':metrics,
            'actual_saved_native_contact':support(actual,points),
            'supplemental_footing_plan':footing_plan(actual,points),
            'terrain_above_floor_histogram':dict(sorted(cuts.items())),'natural_blocks_replaced_by_authored_air':earth,
            'biomes':dict(biomes),'preexisting_structure_bbox_intersections':collisions})
    footprint={(x,z) for x,y,z in all_points}
    exterior=[dict(e,grade_difference=e['feet_y']-(e['terrain_top']+1)) for e in entries if tuple(e['outside']) not in footprint]
    root=saved['layout'][0];center=world_pos((23,0,23),root['origin'],root['rotation'])
    original_floor=root['origin'][1]+8;candidates=[]
    for dx in (-32,0,32):
        for dz in (-32,0,32):
            height=reference.heights.get((center[0]+dx,center[2]+dz))
            if height is None:continue
            dy=height[0]+1-original_floor
            moved=[(x+dx,y+dy,z+dz) for x,y,z in all_points]
            metrics=support(reference,moved)
            deep=sum(reference.heights.get((x,z),(-64,''))[0]>y+12 for x,y,z in moved)
            candidates.append({'offset':[dx,dy,dz],'root_origin':[root['origin'][0]+dx,root['origin'][1]+dy,root['origin'][2]+dz],
                'rotation':root['rotation'],'support':metrics,'columns_with_more_than_four_blocks_above_floor':deep,
                'scope':'Offline translation with the saved rotation and ground-height projection; not an actual generated placement or an acceptance gate.'})
    return {'family':family,'saved_world':saved['world'],'pieces':pieces,'support':support(reference,all_points),
            'actual_saved_native_contact':support(actual,all_points),
            'exterior_openings':exterior,'nearby_offline_candidates':candidates,'template_content_sha256':hashes,
            'scope':'Direct underside contact and air-volume excavation against reference terrain; tree canopies and decorative blocks are excluded from natural ground. Bounding-box intersections are warnings, not exact solid collisions.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reference',default='validation-inland-terrain-baseline-20261014')
    ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:self_test();return
    source=json.loads((ROOT/'tools/inland_terrain_reference.json').read_text(encoding='utf-8'))
    assert args.reference==source['world'] and source['structures_placed_by_harness']==0
    ref=Reference(ROOT/'server'/args.reference,source['bounds']);ref.seed=seed(ROOT/'server'/args.reference)
    assert ref.seed==int(source['seed']) and len(ref.grid)==256,(ref.seed,len(ref.grid))
    results=[review(ref,family) for family in FAMILIES]
    report={'reference':source,'reference_chunks':len(ref.grid),'families':results,
        'ground_classification':{'explicit_blocks':sorted(GROUND),'additional_rules':['all *_ore blocks','alfheim raw *_livingrock','botania raw metamorphic_*_stone'],
                                'excluded':'Tree trunks, leaves, decorative clusters, plants and architectural block variants; not a full collision-shape simulation.'},
        'limits':'One shared Golden Fields locality, not biome-wide or natural-frequency acceptance. The reference uses current same-seed generation, not an exact historical snapshot; decoration can differ. Forced placement does not replay normal beard_thin terrain adaptation, which is not tested here. Measurements do not enable any natural structure set. Full lowest-layer foundation columns are checked; a gap value of 33 means no ground found within the 32-block search. Client review remains required.'}
    write_reports(report)

def write_reports(report):
    results=report['families']
    for family in results:
        for piece in family['pieces']:
            plan=piece['supplemental_footing_plan']
            covered=sum(x1-x0+1 for x0,x1,z,y0,y1 in plan['runs'])+len(plan['obstructed_columns'])+plan['unresolved_columns']
            assert covered==piece['actual_saved_native_contact']['unsupported_columns'],('incomplete footing plan',family['family'],piece['name'])
    (ROOT/'tools/inland_terrain_review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Inland prototype terrain review','',report['limits'],'',
        '| Family | Reference native contact | Saved native contact | Unsupported saved base columns | Largest saved gap | Reference ground replaced by room air |',
        '|---|---:|---:|---:|---:|---:|']
    for row in results:
        s=row['support'];a=row['actual_saved_native_contact'];earth=sum(p['natural_blocks_replaced_by_authored_air'] for p in row['pieces'])
        gap='>32' if a['max_gap_below_base']==33 else str(a['max_gap_below_base'])
        lines.append(f"| {row['family']} | {s['contact_fraction']:.1%} | {a['contact_fraction']:.1%} | {a['unsupported_columns']} | {gap} | {earth} |")
        print(row['family'],json.dumps(a))
    lines+=['','Foundation depth alone does not prove terrain fit. Inspect the piece-level gaps, excavation, exterior grades and existing-structure warnings in `tools/inland_terrain_review.json` before changing placement policy. All three natural sets remain disabled. The reference world retains normal natural generation; the harness placed no review structures and edited no player saves.']
    lines+=['','![Measured foundation gaps](inland_terrain_review.png)','','## Repair targets and bounded alternatives','']
    for row in results:
        worst=max(row['pieces'],key=lambda p:p['actual_saved_native_contact']['max_gap_below_base'])
        blocks=sum(p['supplemental_footing_plan']['block_count'] for p in row['pieces'])
        blocked=sum(len(p['supplemental_footing_plan']['obstructed_columns']) for p in row['pieces'])
        grades=[e['grade_difference'] for e in row['exterior_openings']]
        good=sum(c['support']['unsupported_columns']==0 and c['support']['missing_reference_columns']==0 and
                 c['columns_with_more_than_four_blocks_above_floor']==0 for c in row['nearby_offline_candidates'])
        lines.append(f"- {row['family']}: deepest saved gap at {worst['name']}; gap-only underpinning estimate {blocks} blocks, with {blocked} other-block obstructions requiring review. Direct exterior approach grades span {min(grades)} to {max(grades)} blocks. Of nine offline translations, {good} have both zero measured footing gaps and no ground more than four blocks above the proposed floor.")
    lines+=['','The proposed footing runs are review data only. No fill was applied. Deeper footings alone would not address buried approaches or extensive excavation.',
        '', '## Next validation step','',
        'Use a disposable world with a test-only natural structure set for one family at a time to measure normal terrain adaptation. Keep test starts sparse and finite; do not enable production sets or search indefinitely for a perfect site. Compare natural foundations and approaches with this forced-placement result, then review the result in the client. The accepted approximate harbor policy is unchanged.']
    (ROOT/'alfheim_reclaimed_design/INLAND_TERRAIN_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':main()
