"""Static validator for the Royal / Noble Cultural Asset Library."""
from __future__ import annotations
import hashlib, importlib.util, json, os, sys, tempfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import nbt
MANIFEST=ROOT/"tools"/"royal_asset_manifest.json"
METRICS=ROOT/"tools"/"royal_asset_metrics.json"
OUT=ROOT/"kubejs"/"data"/"alfheim"/"structures"/"royal_assets"
REQUIRED={"id","family","tier","purpose","size","condition","scale","room_compatibility",
          "house_affinity","placement_rules","storytelling_tags","generator_weight",
          "min_blocks","builder"}
REQUIRED_META_TEXT=("purpose","placement_rules")
BAD_PROGRESSION_BLOCKS={"minecraft:lodestone"}  # socket, not a substitute stone
def fail(msg, problems): problems.append(msg)

def socket_count(root):
    palette=root["palette"]; n=0
    for b in root["blocks"]:
        st=palette[int(b["state"])]
        if st["Name"]!="minecraft:jigsaw": continue
        be=b.get("nbt",{})
        if be.get("name")=="alfheim:fey_stone_socket":
            n+=1
            if be.get("target")!="alfheim:fey_stone_piece":
                raise AssertionError("Fey Stone socket target drift")
            if be.get("pool")!="alfheim:royal/fey_stones":
                raise AssertionError("Fey Stone socket pool drift")
    return n

def main():
    problems=[]
    data=json.loads(MANIFEST.read_text())
    assets=data.get("assets",[])
    ids=set(); fam=defaultdict(set); metrics={}
    if data.get("schema")!="alfheim:royal_cultural_assets/v1": fail("schema mismatch",problems)
    if data.get("rules",{}).get("worldgen_enabled") is not False: fail("first slice must not enable worldgen",problems)
    for a in assets:
        miss=REQUIRED-set(a)
        if miss: fail(f"{a.get('id','?')}: missing {sorted(miss)}",problems); continue
        if a["id"] in ids: fail(f"duplicate id {a['id']}",problems)
        ids.add(a["id"]); fam[a["family"]].add(a["condition"])
        if not all(isinstance(a[k],str) and a[k].strip() for k in REQUIRED_META_TEXT):
            fail(f"{a['id']}: empty narrative metadata",problems)
        if not a["room_compatibility"] or not a["storytelling_tags"] or not a["house_affinity"]:
            fail(f"{a['id']}: compatibility/story/affinity metadata empty",problems)
        if max(a["size"])>48: fail(f"{a['id']}: exceeds 48-block piece boundary",problems)
        path=OUT/f"{a['id']}.nbt"
        if not path.exists(): fail(f"{a['id']}: missing NBT",problems); continue
        name,root=nbt.load(path)
        if [int(v) for v in root["size"]]!=a["size"]:
            fail(f"{a['id']}: NBT size does not match manifest",problems)
        if len(root["blocks"])<a["min_blocks"]:
            fail(f"{a['id']}: {len(root['blocks'])} blocks < minimum {a['min_blocks']}",problems)
        palette={p["Name"] for p in root["palette"]}
        bad=palette & BAD_PROGRESSION_BLOCKS
        if bad: fail(f"{a['id']}: fake progression placeholder {sorted(bad)}",problems)
        try:
            sc=socket_count(root)
        except AssertionError as e:
            fail(f"{a['id']}: {e}",problems); sc=0
        if a["family"]=="reliquary_pedestal" and sc!=1:
            fail(f"{a['id']}: reliquary pedestal requires exactly one Fey Stone socket, found {sc}",problems)
        if a["id"]=="reliquary_core_prototype" and sc!=1:
            fail(f"{a['id']}: prototype requires exactly one Fey Stone socket, found {sc}",problems)
        if a["family"] not in ("reliquary_pedestal","reliquary_core") and sc:
            fail(f"{a['id']}: unexpected Fey Stone socket",problems)
    # Every ordinary family in this first slice is a family, never a singleton.
    for family,conditions in fam.items():
        if family=="reliquary_core": continue
        if not {"intact","damaged"}<=conditions:
            fail(f"{family}: requires intact + damaged derivatives; got {sorted(conditions)}",problems)
    # Damaged derivatives must be actual variants, not byte-identical aliases.
    for family in fam:
        if family=="reliquary_core": continue
        aa=[a for a in assets if a["family"]==family]
        intact=next(a for a in aa if a["condition"]=="intact")
        damaged=next(a for a in aa if a["condition"]=="damaged")
        _,ri=nbt.load(OUT/f"{intact['id']}.nbt"); _,rd=nbt.load(OUT/f"{damaged['id']}.nbt")
        if repr(ri)==repr(rd): fail(f"{family}: damaged variant is identical to intact",problems)
    # Metrics produced by the generator must agree with shipping NBT and report zero clipping.
    if not METRICS.exists(): fail("missing royal_asset_metrics.json",problems)
    else:
        mm=json.loads(METRICS.read_text())
        for r in mm.get("assets",[]): metrics[r["id"]]=r
        if set(metrics)!=ids: fail("metrics ids do not exactly match manifest ids",problems)
        for aid,r in metrics.items():
            if r.get("dropped")!=0: fail(f"{aid}: generator clipped {r.get('dropped')} writes",problems)
            _,rr=nbt.load(OUT/f"{aid}.nbt")
            if r.get("blocks")!=len(rr["blocks"]): fail(f"{aid}: metrics block count drift",problems)
    # Python syntax and generator dry regeneration into the real tree are intentionally avoided here;
    # generation is separately executed before this check. Validate source imports instead.
    spec=importlib.util.spec_from_file_location("gen_royal_assets",ROOT/"tools"/"gen_royal_assets.py")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if set(mod.BUILDERS)!={a["builder"] for a in assets}: fail("builder registry/manifest drift",problems)
    if problems:
        print("Royal asset validation FAILED")
        for p in problems: print(" -",p)
        return 1
    print(f"Royal asset validation OK: {len(assets)} templates, {len(fam)-1} reusable families + reliquary prototype, 0 clipped writes")
    print("Acceptance: static only; client visual/runtime review remains required.")
    return 0
if __name__=="__main__": raise SystemExit(main())
