"""Static contract checker for Royal Tile Set I Wave B."""
from pathlib import Path
import importlib.util,json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
    bad=[]
    spec=importlib.util.spec_from_file_location("wave_b",ROOT/"tools"/"gen_royal_tileset_wave_b.py");g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    catalog=json.loads((ROOT/"tools"/"royal_tileset_catalog.json").read_text())
    expected={a["id"] for family in catalog["families"].values() for a in family["assets"] if a["wave"]=="B"}
    if set(g.SEMANTICS)!=expected:bad.append("Wave B semantic list differs from authoritative catalog")
    if len(g.BLOCKS)!=28:bad.append(f"expected 28 physical blocks, found {len(g.BLOCKS)}")
    out=g.build()
    for key,value in out.items():
        raw=(value if isinstance(value,str) else json.dumps(value,separators=(",",":"))+"\n").encode();p=g.path(key)
        if not p.exists() or p.read_bytes()!=raw:bad.append(f"generated drift {p.relative_to(ROOT)}")
        if key.startswith("models/"):
            for element in value.get("elements",[]):
                if not all(0<=v<=16 for v in element["from"]+element["to"]):bad.append(f"{key}: geometry outside 0..16")
                if not all(a<b for a,b in zip(element["from"],element["to"])):bad.append(f"{key}: degenerate geometry")
    script=(ROOT/"kubejs"/"startup_scripts"/"26_royal_tileset_wave_b.js").read_text()
    for name,semantic,part,item,obj in g.BLOCKS:
        if f"event.create('alfheim:royal_{name}','cardinal')" not in script:bad.append(f"missing registration {name}")
    node=shutil.which("node")
    if node:
        r=subprocess.run([node,"--check",str(ROOT/"kubejs"/"startup_scripts"/"26_royal_tileset_wave_b.js")],capture_output=True,text=True)
        if r.returncode:bad.append("startup JavaScript syntax failed")
    if bad:
        print("ROYAL TILESET WAVE B: FAIL");[print(" - "+x) for x in bad];return 1
    print(f"ROYAL TILESET WAVE B: PASS semantics={len(expected)} blocks={len(g.BLOCKS)} generated={len(out)}")
    print("Acceptance boundary: static source/generated contract only; client review not claimed.");return 0
if __name__=="__main__":raise SystemExit(main())
