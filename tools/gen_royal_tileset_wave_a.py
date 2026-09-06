"""Generate Royal Tile Set I Wave A text assets.

Authority: alfheim_reclaimed_design/ROYAL_TILESET_I.md
Manifest: tools/royal_tileset_wave_a_manifest.json

This generator deliberately emits only UTF-8 text assets. It does not create NBT or PNG files:
Wave A proves geometry, registration, rotation, collision and assembly grammar while reusing
verified installed Botania/vanilla textures. House-specific overlays come after client geometry
acceptance.
"""
from __future__ import annotations
from pathlib import Path
import argparse, json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "royal_tileset_wave_a_manifest.json"
ASSET_ROOT = "kubejs/assets/alfheim"
DATA_ROOT = "kubejs/data/alfheim"
STARTUP = "kubejs/startup_scripts/21_royal_tileset_wave_a.js"

def element(frm, to, tex, *, shade=True):
    faces = {d: {"texture": f"#{tex}"} for d in ("north","south","east","west","up","down")}
    return {"from": frm, "to": to, "shade": shade, "faces": faces}

def model(textures, elements, *, ambient=True):
    return {
        "parent": "minecraft:block/block",
        "ambientocclusion": ambient,
        "textures": dict(textures, particle=textures.get("particle", next(iter(textures.values())))),
        "elements": elements,
    }

def highback(t):
    e=[]
    for x in (3,11):
        for z in (3,11):
            e.append(element([x,0,z],[x+2,6,z+2],"wood_log"))
    e += [
        element([3,6,3],[13,9,13],"textile"),
        element([3,9,12],[5,16,15],"wood"),
        element([11,9,12],[13,16,15],"wood"),
        element([5,10,13],[11,15,15],"textile"),
        element([6,14,12],[10,16,16],"metal"),
    ]
    return model(t,e)

def sconce(t):
    e=[
        element([5,4,14],[11,14,16],"stone"),
        element([6,5,13],[10,13,15],"metal"),
        element([7,8,9],[9,10,14],"metal"),
        element([5,6,7],[11,8,11],"metal"),
        element([6,8,8],[10,13,11],"glass",shade=False),
        element([7,9,8],[9,12,10],"glow",shade=False),
    ]
    return model(t,e,ambient=False)

def carpet(t):
    e=[
        element([1,0,0],[15,1,16],"textile"),
        element([1,0,0],[3,1,16],"textile_trim"),
        element([13,0,0],[15,1,16],"textile_trim"),
        element([6,0.1,2],[10,1.1,5],"metal"),
        element([7,0.1,5],[9,1.1,11],"textile_trim"),
        element([6,0.1,11],[10,1.1,14],"metal"),
    ]
    return model(t,e)

def balustrade(t):
    e=[
        element([1,0,6],[4,16,10],"stone"),
        element([12,0,6],[15,16,10],"stone"),
        element([3,10,7],[13,13,9],"stone"),
        element([3,4,7],[13,6,9],"metal"),
        element([4,6,7],[6,10,9],"wood"),
        element([7,6,7],[9,10,9],"wood"),
        element([10,6,7],[12,10,9],"wood"),
        element([1,15,5],[4,16,11],"metal"),
        element([12,15,5],[15,16,11],"metal"),
    ]
    return model(t,e)

def amphora(t):
    e=[
        element([6,0,6],[10,2,10],"stone"),
        element([4,2,4],[12,7,12],"stone"),
        element([5,7,5],[11,11,11],"stone"),
        element([6,11,6],[10,14,10],"metal"),
        element([5,14,5],[11,15,11],"metal"),
        element([7,15,7],[9,16,9],"metal"),
        element([3,5,5],[5,9,7],"metal"),
        element([11,5,5],[13,9,7],"metal"),
    ]
    return model(t,e)

def bed_module(t, part):
    side = "left" if part.endswith("left") else "right"
    phase = part.rsplit("_",1)[0]
    e=[
        element([0,0,1],[16,3,15],"wood"),
        element([0,3,1],[16,6,15],"textile"),
        element([0,5,2],[16,7,14],"textile_trim"),
    ]
    outer=(0,3) if side=="left" else (13,16)
    if phase in ("head","foot"):
        e.append(element([outer[0],0,1],[outer[1],16,4],"wood_log"))
        e.append(element([outer[0],14,1],[outer[1],16,16],"metal"))
    if phase=="head":
        e += [
            element([0,6,13],[16,14,16],"wood"),
            element([1,7,13.5],[15,13,16],"textile"),
        ]
    if phase=="foot":
        e.append(element([0,6,1],[16,10,3],"wood"))
    if phase=="middle":
        e.append(element([outer[0],14,0],[outer[1],16,16],"wood_log"))
    return model(t,e)

def banner(t):
    e=[
        element([1,14,13],[15,16,16],"wood_log"),
        element([2,3,14],[14,14,15],"textile"),
        element([2,3,13.5],[4,14,15.5],"textile_trim"),
        element([12,3,13.5],[14,14,15.5],"textile_trim"),
        element([5,8,13.2],[11,11,15.8],"metal"),
        element([3,2,14],[6,4,15],"textile"),
        element([10,2,14],[13,4,15],"textile"),
    ]
    return model(t,e)

def astrolabe(t, quadrant):
    # Each module owns one quadrant of a 2x2 instrument. Geometry is local and joins at the
    # shared centre; no element crosses a block boundary.
    corner = {
        "nw": (12,12), "ne": (0,12), "sw": (12,0), "se": (0,0)
    }[quadrant]
    cx,cz=corner
    px0=max(0,cx); pz0=max(0,cz)
    px1=min(16,cx+4); pz1=min(16,cz+4)
    e=[
        element([0,0,0],[16,2,16],"stone"),
        element([1,2,1],[15,4,15],"metal"),
        element([px0,4,pz0],[px1,16,pz1],"metal"),
    ]
    if quadrant in ("nw","sw"):
        e += [element([3,11,6],[16,13,10],"metal"), element([4,12,7],[15,14,9],"glass",shade=False)]
    else:
        e += [element([0,11,6],[13,13,10],"metal"), element([1,12,7],[12,14,9],"glass",shade=False)]
    if quadrant in ("nw","ne"):
        e += [element([6,9,3],[10,15,16],"metal"), element([7,10,4],[9,14,15],"glass",shade=False)]
    else:
        e += [element([6,9,0],[10,15,13],"metal"), element([7,10,1],[9,14,12],"glass",shade=False)]
    # Local luminous calibration point.
    gx = 13 if quadrant in ("nw","sw") else 1
    gz = 13 if quadrant in ("nw","ne") else 1
    e.append(element([gx,7,gz],[gx+2,9,gz+2],"glow",shade=False))
    return model(t,e,ambient=False)

MODEL_BUILDERS={
    "highback_chair": highback,
    "wall_sconce": sconce,
    "carpet_runner": carpet,
    "balustrade": balustrade,
    "lidded_amphora": amphora,
    "wall_banner": banner,
}

def build():
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    t=m["texture_contract"]
    out={}
    def write(path,obj):
        out[path]=(json.dumps(obj,separators=(',',':'))+"\n") if not isinstance(obj,str) else obj

    # Custom model parents. KubeJS cardinal blocks generate their own rotated blockstates and
    # wrapper models that inherit these definitions.
    for b in m["blocks"]:
        kind=b["model_kind"]
        if kind.startswith("canopy_bed_"):
            obj=bed_module(t,kind.removeprefix("canopy_bed_"))
        elif kind.startswith("astrolabe_"):
            obj=astrolabe(t,kind.removeprefix("astrolabe_"))
        else:
            obj=MODEL_BUILDERS[kind](t)
        write(f"{ASSET_ROOT}/models/block/royal_tileset/{kind}.json",obj)

    # Registration. 'cardinal' owns placement-facing and rotates collision/model variants.
    # rotateState/mirrorState are still explicit because structure-template transforms call
    # Block.rotate/Block.mirror, and the base Kube block otherwise leaves custom facing alone.
    lines=[
        "// GENERATED by tools/gen_royal_tileset_wave_a.py — do not hand-edit.",
        "// Royal Tile Set I / Wave A. Restart the client after regeneration.",
        "const ROYAL_FACING = BlockProperties.HORIZONTAL_FACING",
        "",
        "function royalOrient(block) {",
        "  return block",
        "    .rotateState(state => state.setValue(ROYAL_FACING, state.rotate(state.getValue(ROYAL_FACING))))",
        "    .mirrorState(state => state.setValue(ROYAL_FACING, state.mirror(state.getValue(ROYAL_FACING))))",
        "}",
        "",
        "StartupEvents.registry('block', event => {"
    ]
    for b in m["blocks"]:
        bid=b["id"]
        short=bid.split(":",1)[1]
        model_id=f"alfheim:block/royal_tileset/{b['model_kind']}"
        lines.append(f"  let {short} = event.create('{bid}', 'cardinal')")
        lines.append(f"    .displayName({json.dumps(b['display_name'])})")
        lines.append(f"    .model('{model_id}')")
        lines.append(f"    .soundType('{b['sound']}')")
        lines.append("    .hardness(1.0).resistance(3.0)")
        lines.append("    .fullBlock(false).notSolid().noValidSpawns(true)")
        if b["render_type"]!="solid":
            lines.append(f"    .renderType('{b['render_type']}')")
        if b["light"]:
            lines.append(f"    .lightLevel({(b['light']+0.01)/15:.8f})")
        for box in b["collision_boxes"]:
            lines.append("    .box("+", ".join(str(v) for v in box)+")")
        for tag in b["tags"]:
            lines.append(f"    .tagBlock('{tag}')")
            if b["item"]:
                lines.append(f"    .tagItem('{tag}')")
        if not b["item"]:
            lines.append("    .noItem()")
        lines.append(f"  royalOrient({short})")
        lines.append("")
    lines.append("})")
    lines.append("")
    write(STARTUP,"\n".join(lines))

    block_ids=[b["id"] for b in m["blocks"]]
    item_ids=[b["id"] for b in m["blocks"] if b["item"]]
    write(f"{DATA_ROOT}/tags/blocks/royal_tileset_wave_a.json",{"replace":False,"values":block_ids})
    write(f"{DATA_ROOT}/tags/items/royal_tileset_wave_a.json",{"replace":False,"values":item_ids})

    # Non-destructive review function: it only places into the caller's chosen test area.
    f=[
        "# GENERATED by tools/gen_royal_tileset_wave_a.py",
        "# Run only in a disposable review area: /function alfheim:royal_tileset_wave_a/review",
        "say [Alfheim] placing Royal Tile Set I Wave A review grid",
        "setblock ~0 ~ ~0 alfheim:royal_highback_chair[facing=north]",
        "setblock ~3 ~ ~0 alfheim:royal_wall_sconce[facing=north]",
        "setblock ~6 ~ ~0 alfheim:royal_carpet_runner[facing=north]",
        "setblock ~9 ~ ~0 alfheim:royal_balustrade[facing=north]",
        "setblock ~12 ~ ~0 alfheim:royal_lidded_amphora[facing=north]",
        "setblock ~15 ~ ~0 alfheim:royal_wall_banner[facing=north]",
        "# 2x3 canopy bed",
    ]
    bed=m["assemblies"]["canopy_bed"]["rows"]
    for z,row in enumerate(bed):
        for x,bid in enumerate(row):
            f.append(f"setblock ~{x} ~ ~{5+z} alfheim:{bid}[facing=north]")
    f.append("# 2x2 astrolabe")
    ast=m["assemblies"]["astrolabe"]["rows"]
    for z,row in enumerate(ast):
        for x,bid in enumerate(row):
            f.append(f"setblock ~{5+x} ~ ~{5+z} alfheim:{bid}[facing=north]")
    f.append("say [Alfheim] Wave A grid placed; inspect geometry, collision, facing and seams")
    f.append("")
    write(f"{DATA_ROOT}/functions/royal_tileset_wave_a/review.mcfunction","\n".join(f))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    out=build()
    mismatches=[]
    for name,data in out.items():
        path=ROOT/name
        enc=data.encode("utf-8")
        if args.check:
            if not path.exists() or path.read_bytes()!=enc:
                mismatches.append(name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(enc)
    if mismatches:
        raise SystemExit("Generated output mismatch:\n"+"\n".join(mismatches))
    print(f"{len(out)} files "+("byte-identical" if args.check else "generated"))

if __name__=="__main__":
    main()
