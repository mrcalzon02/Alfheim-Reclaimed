"""Read-only field witnesses; never writes a player save or assumes a live snapshot."""
from pathlib import Path
from collections import Counter
import json
from probe_terraces import chunks,section_blocks,biome_at
from gen_void_worldgen import VOID_IDS
import nbt
ROOT=Path(__file__).resolve().parents[1]

def main():
    world=ROOT/'saves/New World staven'
    counts=Counter();witnesses=[];low_starts=[];overhead=[]
    # Finite origin-region sample. Unknown/missing sections are not counted as air.
    for name in ('r.0.0.mca','r.-1.0.mca','r.0.-1.mca','r.-1.-1.mca'):
        for c in chunks(world/'dimensions/mythicbotany/alfheim/region'/name):
            if c.get('Status')!='minecraft:full':continue
            sections=c.get('sections',[])
            if (int(c['xPos']),int(c['zPos']))==(0,-1):
                for y in (181,191,201):
                    sec=next(s for s in sections if s['Y']==y//16)
                    overhead.append({'pos':[0,y,-6],'block':section_blocks(sec)[((y&15)<<8)|(10<<4)]})
            sec=next((s for s in sections if s['Y']==-4),None)
            if not sec:continue
            blocks=section_blocks(sec)
            if not blocks:continue
            counts['full_chunks']+=1
            for z in range(16):
                for x in range(16):
                    biome=biome_at(sections,64,x,z)
                    if biome is None:counts['unknown_biome_columns']+=1;continue
                    if biome in VOID_IDS:counts['void_columns_excluded']+=1;continue
                    counts['non_void_columns']+=1
                    if blocks[z*16+x]!='minecraft:bedrock':
                        counts['non_void_without_bedrock']+=1
                        if len(witnesses)<12:witnesses.append({'pos':[int(c['xPos'])*16+x,-64,int(c['zPos'])*16+z],
                            'biome_at_y64':biome,'block':blocks[z*16+x]})
            for sid,start in c.get('structures',{}).get('starts',{}).items():
                boxes=[list(map(int,p['BB'])) for p in start.get('Children',[]) if p.get('BB') and p['BB'][1]<=-64]
                if boxes:low_starts.append({'id':sid,'chunk':[int(c['xPos']),int(c['zPos'])],'boxes':boxes})
    anchors=[]
    for name in ('r.0.0.mca','r.-1.0.mca','r.0.-1.mca','r.-1.-1.mca'):
        path=world/'dimensions/mythicbotany/alfheim/entities'/name
        if not path.exists():continue
        for c in chunks(path):
            for e in c.get('Entities',[]):
                if 'alfheim_hub_baked' in e.get('Tags',[]):anchors.append([float(v) for v in e['Pos']])
    report={'world':world.name,'seed':str(nbt.load(str(world/'level.dat'))[1]['Data']['WorldGenSettings']['seed']),
        'sample':'four origin regions, full chunks only; biome classified at Y64',
        'counts':dict(counts),'missing_floor_examples':witnesses,'structure_boxes_reaching_world_floor':low_starts,
        'baked_hub_anchors':anchors,'burial_probe_blocks':overhead,
        'limits':'Read-only snapshot of a potentially running save. Floor results are a bounded sample, not whole-world acceptance.'}
    (ROOT/'tools/staven_field_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('STAVEN AUDIT:',dict(counts),'anchors',anchors)

if __name__=='__main__':main()
