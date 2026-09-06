"""Static checker for Royal Tile Set I Wave A.

This proves source/generated text agreement, semantic/physical coverage, custom model structure,
collision bounds, explicit structure-rotation callbacks, and review-grid coverage. It does not
claim that Minecraft/KubeJS has loaded or rendered the blocks.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util, json, re, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"tools"/"royal_tileset_wave_a_manifest.json"
STARTUP=ROOT/"kubejs"/"startup_scripts"/"21_royal_tileset_wave_a.js"
ASSET_MODELS=ROOT/"kubejs"/"assets"/"alfheim"/"models"/"block"/"royal_tileset"
REVIEW=ROOT/"kubejs"/"data"/"alfheim"/"functions"/"royal_tileset_wave_a"/"review.mcfunction"

EXPECTED_SEMANTIC={
    "highback_chair","wall_sconce","carpet_runner","balustrade_segment",
    "lidded_amphora","canopy_bed","wall_banner","astrolabe"
}
FORBIDDEN_WORDS=("fey_stone","inventory","blockentity","block_entity","loot_table","quest")
Z_FIGHT_REPAIRS={"carpet_runner","balustrade","wall_sconce"}

def positive_overlap(a0,a1,b0,b1):
    return min(a1,b1)-max(a0,b0)>1e-9

def same_oriented_coplanar_faces(a,b):
    """Yield same-facing planes whose projected rectangles overlap with positive area."""
    af,at=a["from"],a["to"]; bf,bt=b["from"],b["to"]
    for axis in range(3):
        others=[i for i in range(3) if i!=axis]
        if not all(positive_overlap(af[i],at[i],bf[i],bt[i]) for i in others):continue
        if abs(af[axis]-bf[axis])<1e-9:yield axis,"min",af[axis]
        if abs(at[axis]-bt[axis])<1e-9:yield axis,"max",at[axis]

def main():
    problems=[]
    def fail(msg): problems.append(msg)

    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema")!="alfheim:royal_tileset_wave_a/v1":
        fail("manifest schema mismatch")
    semantic=set(data.get("pilot_semantic_assets",[]))
    if semantic!=EXPECTED_SEMANTIC:
        fail(f"semantic pilot drift: {sorted(semantic)}")
    blocks=data.get("blocks",[])
    if len(blocks)!=16:
        fail(f"expected 16 physical blocks, found {len(blocks)}")
    ids=[b.get("id") for b in blocks]
    if len(ids)!=len(set(ids)):
        fail("duplicate physical block id")
    mapped={b.get("semantic_asset") for b in blocks}
    if mapped!=EXPECTED_SEMANTIC:
        fail(f"physical coverage drift: {sorted(mapped)}")
    for b in blocks:
        if b.get("builder")!="cardinal":
            fail(f"{b.get('id')}: Wave A custom geometry must use cardinal builder")
        if not b.get("collision_boxes"):
            fail(f"{b.get('id')}: missing collision boxes")
        for box in b.get("collision_boxes",[]):
            if len(box)!=6:
                fail(f"{b.get('id')}: malformed collision box {box}")
                continue
            x0,y0,z0,x1,y1,z1=box
            if not all(0<=v<=16 for v in box):
                fail(f"{b.get('id')}: collision leaves local 0..16 bounds: {box}")
            if not (x0<x1 and y0<y1 and z0<z1):
                fail(f"{b.get('id')}: degenerate collision box {box}")
        model=ASSET_MODELS/f"{b['model_kind']}.json"
        if not model.exists():
            fail(f"{b.get('id')}: missing custom model {model.relative_to(ROOT)}")
            continue
        obj=json.loads(model.read_text(encoding="utf-8"))
        if obj.get("parent")!="minecraft:block/block":
            fail(f"{b.get('id')}: custom model parent drift")
        textures=obj.get("textures",{})
        elements=obj.get("elements",[])
        if not elements:
            fail(f"{b.get('id')}: model has no elements")
        for el in elements:
            frm,to=el.get("from"),el.get("to")
            if not (isinstance(frm,list) and isinstance(to,list) and len(frm)==3 and len(to)==3):
                fail(f"{b.get('id')}: malformed model element")
                continue
            if not all(0<=v<=16 for v in frm+to):
                fail(f"{b.get('id')}: model element leaves 0..16 local bounds: {frm}->{to}")
            if not all(a<bv for a,bv in zip(frm,to)):
                fail(f"{b.get('id')}: degenerate model element {frm}->{to}")
            for face in el.get("faces",{}).values():
                tex=face.get("texture","")
                if not tex.startswith("#") or tex[1:] not in textures:
                    fail(f"{b.get('id')}: unresolved texture slot {tex}")
        if b.get("model_kind") in Z_FIGHT_REPAIRS:
            for i,left in enumerate(elements):
                for right in elements[i+1:]:
                    for axis,side,plane in same_oriented_coplanar_faces(left,right):
                        fail(f"{b.get('id')}: same-facing coplanar overlap axis={axis} side={side} plane={plane}")

    # Multi-block semantic assets must be complete rectangular local-module matrices.
    for name, expected in (("canopy_bed",(2,3)),("astrolabe",(2,2))):
        a=data.get("assemblies",{}).get(name,{})
        rows=a.get("rows",[])
        w,h=expected
        if len(rows)!=h or any(len(row)!=w for row in rows):
            fail(f"{name}: assembly footprint does not match {w}x{h}")
        flat=[x for row in rows for x in row]
        for short in flat:
            if "alfheim:"+short not in ids:
                fail(f"{name}: assembly references unregistered module {short}")

    script=STARTUP.read_text(encoding="utf-8") if STARTUP.exists() else ""
    if not script:
        fail("missing generated startup script")
    for b in blocks:
        if f"event.create('{b['id']}', 'cardinal')" not in script:
            fail(f"{b['id']}: missing cardinal registration")
    if ".rotateState(state => state.setValue(ROYAL_FACING, state.rotate(state.getValue(ROYAL_FACING))))" not in script:
        fail("startup script lacks explicit structure-rotation callback")
    if ".mirrorState(state => state.setValue(ROYAL_FACING, state.mirror(state.getValue(ROYAL_FACING))))" not in script:
        fail("startup script lacks explicit structure-mirror callback")
    low=script.lower()
    for word in FORBIDDEN_WORDS:
        if word in low:
            fail(f"startup script unexpectedly contains forbidden gameplay term {word}")

    review=REVIEW.read_text(encoding="utf-8") if REVIEW.exists() else ""
    for bid in ids:
        if bid not in review:
            fail(f"review function does not place {bid}")

    # Generator must reproduce every committed generated output byte-for-byte.
    spec=importlib.util.spec_from_file_location("gen_wave_a",ROOT/"tools"/"gen_royal_tileset_wave_a.py")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    generated=mod.build()
    for rel,text in generated.items():
        path=ROOT/rel
        if not path.exists():
            fail(f"missing generated file {rel}")
        elif path.read_text(encoding="utf-8")!=text:
            fail(f"generated output drift {rel}")

    node=shutil.which("node")
    if node and STARTUP.exists():
        r=subprocess.run([node,"--check",str(STARTUP)],capture_output=True,text=True)
        if r.returncode:
            fail("startup JS syntax: "+(r.stderr or r.stdout).strip().splitlines()[-1])

    if problems:
        print("ROYAL TILESET WAVE A: FAIL")
        for p in problems: print(" - "+p)
        return 1
    print(f"ROYAL TILESET WAVE A: PASS semantics={len(semantic)} blocks={len(blocks)} generated={len(generated)}")
    print("Acceptance boundary: static source/generated contract only; client/KubeJS load not claimed.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
