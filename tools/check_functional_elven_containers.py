"""Static source/generated contract for fixed-capacity elven containers and Manna storage."""
from __future__ import annotations
from pathlib import Path
import importlib.util,json,re,sys

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/"first_party_mods"/"alfheim_leyworks"/"src"/"main"/"resources"
JAVA=ROOT/"first_party_mods"/"alfheim_leyworks"/"src"/"main"/"java"/"com"/"continuityworks"/"leyworks"
EXPECTED={"royal_chest":54,"gemstone_coffer":18,"dreamwood_crate":27,"provision_crate":27,"scroll_crate":27,"tall_vase":9,"memorial_urn":9}

def main():
    problems=[]
    def fail(msg):problems.append(msg)
    spec=importlib.util.spec_from_file_location("gen_containers",ROOT/"tools"/"gen_functional_elven_containers.py")
    gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
    generated=gen.build()
    for rel,obj in generated.items():
        path=RES/rel;expected=(obj if isinstance(obj,str) else json.dumps(obj,separators=(",",":"))+"\n").encode()
        if not path.exists():fail(f"missing generated resource {rel}")
        elif path.read_bytes()!=expected:fail(f"generated drift {rel}")
    style=(JAVA/"ElvenContainerBlock.java").read_text()
    main_java=(JAVA/"Leyworks.java").read_text()
    entity=(JAVA/"ElvenContainerBlockEntity.java").read_text()
    for name,capacity in EXPECTED.items():
        enum=name.upper()
        if not re.search(rf"{enum}\({capacity},",style):fail(f"{name}: capacity is not {capacity}")
        if f'registerContainer("{name}"' not in main_java:fail(f"{name}: block registration missing")
        if f'registerBlockItem("{name}"' not in main_java:fail(f"{name}: item registration missing")
    if "slot<capacity()" not in entity:fail("fixed containers do not lock inactive slots")
    manna=(JAVA/"MannaStoneStorageBlockEntity.java").read_text()
    if "MAX_GEMS = 3" not in manna or "CHEST_SLOTS * (gemCount() + 1)" not in manna:fail("Manna four-chest capacity contract drift")
    for rel,obj in generated.items():
        if "/models/block/" in rel:
            for element in obj.get("elements",[]):
                vals=element["from"]+element["to"]
                if not all(0<=v<=16 for v in vals):fail(f"{rel}: element leaves model bounds")
                if not all(a<b for a,b in zip(element["from"],element["to"])):fail(f"{rel}: degenerate element")
    if problems:
        print("FUNCTIONAL ELVEN CONTAINERS: FAIL")
        for problem in problems:print(" - "+problem)
        return 1
    print(f"FUNCTIONAL ELVEN CONTAINERS: PASS fixed={len(EXPECTED)} generated={len(generated)} manna_slots=108")
    print("Acceptance boundary: static source/generated contract only; runtime interaction not claimed.")
    return 0

if __name__=="__main__":raise SystemExit(main())
