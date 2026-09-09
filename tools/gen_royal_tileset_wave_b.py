"""Generate Royal Tile Set I Wave B room-completion models and registrations."""
from __future__ import annotations
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/"kubejs"/"assets"/"alfheim"; D=ROOT/"kubejs"/"data"/"alfheim"; S=ROOT/"kubejs"/"startup_scripts"/"26_royal_tileset_wave_b.js"
T={"wood":"botania:block/dreamwood_planks","log":"botania:block/dreamwood_log","metal":"botania:block/elementium_block","glass":"botania:block/elf_glass_0","stone":"minecraft:block/quartz_block_side","textile":"minecraft:block/purple_wool","trim":"minecraft:block/magenta_wool","dark":"minecraft:block/polished_blackstone","glow":"minecraft:block/sea_lantern","leaf":"minecraft:block/azalea_leaves","particle":"botania:block/dreamwood_planks"}
def b(a,z,t):return {"from":a,"to":z,"faces":{f:{"texture":"#"+t} for f in ("north","south","east","west","up","down")}}
def m(e,ao=True):return {"parent":"minecraft:block/block","ambientocclusion":ao,"textures":T,"elements":e}

def geom(kind,part="single"):
    side=part in ("left","nw","sw"); outer=(1,3) if side else (13,15)
    if kind=="oath_basin": return m([b([0,0,0],[16,3,16],"stone"),b([2,3,2],[14,8,14],"metal"),b([3,8,3],[13,11,13],"stone"),b([5,9,5],[11,12,11],"glass")],False)
    if kind=="offering_stand": return m([b([4,0,4],[12,3,12],"stone"),b([6,3,6],[10,11,10],"wood"),b([3,11,3],[13,14,13],"metal"),b([6,14,6],[10,16,10],"glow")],False)
    if kind=="crescent_settee":
        e=[b([0,5,3],[16,9,14],"textile"),b([0,9,12],[16,15,15],"wood")]
        if part=="left":e+=[b([1,0,3],[4,12,7],"log")]
        if part=="right":e+=[b([12,0,3],[15,12,7],"log")]
        return m(e)
    if kind in ("banquet_table","salon_table"):
        h=11 if kind=="banquet_table" else 9;e=[b([0,h,2],[16,h+3,14],"wood"),b([1,h+1,3],[15,h+3,13],"stone")]
        if part in ("left","right"):e+=[b([outer[0],0,3],[outer[1],h,6],"log"),b([outer[0],0,10],[outer[1],h,13],"log")]
        return m(e)
    if kind=="glass_display_case":return m([b([0,0,3],[16,3,14],"wood"),b([0,3,12],[16,16,14],"wood"),b([0,14,3],[16,16,14],"metal"),b([0,3,3],[2,14,13],"metal"),b([14,3,3],[16,14,13],"metal"),b([2,3,3],[14,14,5],"glass")],False)
    if kind=="wardrobe":return m([b([0,0,4],[16,16,16],"wood"),b([0,2,3],[7.7,14,5],"dark"),b([8.3,2,3],[16,14,5],"dark"),b([7,7,2.5],[8,9,5.5],"metal"),b([8,7,2.5],[9,9,5.5],"metal")])
    if kind=="washstand":return m([b([3,0,3],[6,10,6],"log"),b([10,0,3],[13,10,6],"log"),b([2,9,2],[14,12,14],"wood"),b([4,11,4],[12,14,12],"stone"),b([6,12,6],[10,15,10],"glass")],False)
    if kind=="vanity":return m([b([0,8,3],[16,11,14],"wood"),b([outer[0],0,5],[outer[1],8,8],"log"),b([outer[0],0,11],[outer[1],8,14],"log"),b([2,11,12],[14,16,14],"metal"),b([4,12,11],[12,16,13],"glass")],False)
    if kind=="floor_candelabrum":return m([b([5,0,5],[11,2,11],"stone"),b([7,2,7],[9,13,9],"metal"),b([2,11,7],[14,13,9],"metal"),b([2,13,6],[5,16,10],"glow"),b([7,13,6],[10,16,10],"glow"),b([12,13,6],[15,16,10],"glow")],False)
    if kind=="ceiling_pennant":return m([b([6,13,6],[10,16,10],"metal"),b([7,4,7],[9,14,9],"log"),b([3,3,7],[13,11,9],"textile"),b([5,1,7],[8,4,9],"trim")])
    if kind=="tea_service":return m([b([2,0,2],[14,1,14],"stone"),b([6,1,6],[11,6,11],"stone"),b([7,6,7],[10,8,10],"metal"),b([3,1,3],[6,4,6],"glass"),b([11,1,3],[14,4,6],"glass")],False)
    if kind=="scroll_rack":return m([b([2,0,4],[14,3,14],"wood"),b([2,3,12],[14,16,15],"wood"),b([3,5,4],[13,7,13],"metal"),b([3,11,4],[13,13,13],"metal"),b([4,6,5],[6,11,12],"stone"),b([7,6,5],[9,11,12],"stone"),b([10,6,5],[12,11,12],"stone")])
    if kind=="book_lectern":return m([b([5,0,5],[11,3,11],"stone"),b([7,3,7],[9,11,9],"log"),b([3,10,4],[13,13,12],"wood"),b([4,12,3],[12,14,11],"textile")])
    if kind=="carved_wall_panel":return m([b([1,1,14],[15,16,16],"wood"),b([3,3,13],[13,14,15],"stone"),b([6,5,12.5],[10,12,14.5],"leaf"),b([4,7,12.5],[12,9,14.5],"metal")])
    if kind=="trough_planter":return m([b([0,0,2],[16,3,14],"stone"),b([0,3,2],[3,10,14],"stone"),b([13,3,2],[16,10,14],"stone"),b([3,3,3],[13,7,13],"dark"),b([1,8,3],[15,14,13],"leaf")])
    if kind=="trellis_panel":return m([b([1,0,7],[3,16,9],"wood"),b([7,0,7],[9,16,9],"wood"),b([13,0,7],[15,16,9],"wood"),b([1,4,7],[15,6,9],"wood"),b([1,10,7],[15,12,9],"wood"),b([3,2,6],[13,15,10],"leaf")])
    if kind=="shield_display":return m([b([4,2,14],[12,16,16],"wood"),b([2,4,11],[14,14,15],"metal"),b([5,6,10],[11,12,14],"textile")])
    if kind=="armor_display":return m([b([4,0,4],[12,2,12],"stone"),b([7,2,7],[9,14,9],"log"),b([4,8,4],[12,14,12],"metal"),b([5,14,5],[11,16,11],"textile")])
    raise KeyError(kind)

SEMANTICS=["oath_basin","offering_stand","crescent_settee","banquet_table","salon_table","glass_display_case","wardrobe","washstand","vanity","floor_candelabrum","ceiling_pennant","tea_service","scroll_rack","book_lectern","carved_wall_panel","trough_planter","trellis_panel","shield_display","armor_display"]
PARTS={"crescent_settee":["left","middle","right"],"banquet_table":["left","middle","right"],"salon_table":["left","right"],"glass_display_case":["left","right"],"wardrobe":["left","right"],"vanity":["left","right"],"trough_planter":["left","right"]}
BLOCKS=[]
for semantic in SEMANTICS:
    parts=PARTS.get(semantic,["single"])
    for part in parts:
        name=semantic if part=="single" else f"{semantic}_{part}";BLOCKS.append((name,semantic,part,part=="single",geom(semantic,part)))

def build():
    out={}
    for name,semantic,part,item,obj in BLOCKS:out[f"models/block/royal_tileset_b/{name}.json"]=obj
    lines=["// GENERATED by tools/gen_royal_tileset_wave_b.py — do not hand-edit.","const ROYAL_B_FACING = BlockProperties.HORIZONTAL_FACING","StartupEvents.registry('block', event => {"]
    for name,semantic,part,item,obj in BLOCKS:
        lines += [f"  let royal_b_{name}=event.create('alfheim:royal_{name}','cardinal')",f"    .displayName({json.dumps(('Royal '+semantic.replace('_',' ')).title())})",f"    .model('alfheim:block/royal_tileset_b/{name}')","    .hardness(1.2).resistance(4.0).fullBlock(false).notSolid().noValidSpawns(true)","    .tagBlock('alfheim:royal_tileset_wave_b')"]
        if semantic in ("carved_wall_panel","shield_display"):lines += ["    .box(1, 1, 12, 15, 16, 16)"]
        elif semantic=="ceiling_pennant":lines += ["    .box(3, 1, 6, 13, 16, 10)"]
        elif semantic in ("banquet_table","salon_table","vanity"):lines += ["    .box(0, 0, 2, 16, 13, 14)"]
        else:lines += ["    .box(1, 0, 1, 15, 16, 15)"]
        if item:lines += ["    .tagItem('alfheim:royal_tileset_wave_b')"]
        else:lines += ["    .noItem()"]
        if any(k in name for k in ("glass","tea","candelabrum")):lines += ["    .renderType('cutout')"]
        lines += [f"  royal_b_{name}.rotateState(s=>s.setValue(ROYAL_B_FACING,s.rotate(s.getValue(ROYAL_B_FACING))))",f"  royal_b_{name}.mirrorState(s=>s.setValue(ROYAL_B_FACING,s.mirror(s.getValue(ROYAL_B_FACING))))",""]
    lines += ["})",""];out["startup"]="\n".join(lines)
    ids=["alfheim:royal_"+x[0] for x in BLOCKS];out["tags/blocks/royal_tileset_wave_b.json"]={"replace":False,"values":ids};out["tags/items/royal_tileset_wave_b.json"]={"replace":False,"values":["alfheim:royal_"+x[0] for x in BLOCKS if x[3]]}
    review=["# GENERATED by tools/gen_royal_tileset_wave_b.py","say [Alfheim] placing Royal Tile Set Wave B gallery"]
    x=z=0
    for name,semantic,part,item,obj in BLOCKS:
        review.append(f"setblock ~{x} ~ ~{z} alfheim:royal_{name}[facing=north]");x+=1
        if x>=12:x=0;z+=3
    review += ["say [Alfheim] Wave B gallery placed",""];out["review"]="\n".join(review)
    return out
def path(k):
    if k=="startup":return S
    if k=="review":return D/"functions"/"royal_tileset_wave_b"/"review.mcfunction"
    if k.startswith("models/"):return A/k
    return D/k
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");q=ap.parse_args();bad=[]
    for k,v in build().items():
        raw=(v if isinstance(v,str) else json.dumps(v,separators=(",",":"))+"\n").encode();p=path(k)
        if q.check:
            if not p.exists() or p.read_bytes()!=raw:bad.append(str(p.relative_to(ROOT)))
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    if bad:raise SystemExit("Generated output mismatch:\n"+"\n".join(bad))
    print(f"{len(build())} Wave B resources; semantics={len(SEMANTICS)} blocks={len(BLOCKS)} "+("byte-identical" if q.check else "generated"))
if __name__=="__main__":main()
