"""Generate the bespoke Elder Kings funerary blocks, pixel textures and review grid."""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import random

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "funerary_set_manifest.json"
ASSET = "kubejs/assets/alfheim"
DATA = "kubejs/data/alfheim"
STARTUP = "kubejs/startup_scripts/24_funerary_set.js"


def element(frm, to, texture, *, faces=None, shade=True):
    used = faces or ("north", "south", "east", "west", "up", "down")
    return {"from": frm, "to": to, "shade": shade,
            "faces": {face: {"texture": f"#{texture}"} for face in used}}


def model(elements, *, ambient=True):
    return {"parent": "minecraft:block/block", "ambientocclusion": ambient,
            "textures": {
                "stone": "alfheim:block/funerary/tomb_stone",
                "cracked": "alfheim:block/funerary/tomb_cracked",
                "gold": "alfheim:block/funerary/grave_gold",
                "cloth": "alfheim:block/funerary/funerary_cloth",
                "cloth_torn": "alfheim:block/funerary/funerary_cloth_torn",
                "carving": "alfheim:block/funerary/memorial_carving",
                "door": "alfheim:block/funerary/grave_door",
                "particle": "alfheim:block/funerary/tomb_stone"
            }, "elements": elements}


def debris():
    return model([
        element([1, 0, 2], [8, 2, 10], "cracked"),
        element([7, 0, 5], [15, 3, 14], "stone"),
        element([3, 1, 9], [10, 5, 15], "cracked"),
        element([11, 2, 2], [15, 5, 7], "stone"),
        element([5, 4, 11], [8, 6, 14], "gold"),
    ])


def sarcophagus(part):
    e = [
        element([1, 0, 0], [15, 3, 16], "stone"),
        element([2, 3, 0], [14, 10, 16], "cracked"),
        element([1, 10, 0], [15, 13, 16], "stone"),
        element([1, 4, 0], [3, 10, 16], "gold"),
        element([13, 4, 0], [15, 10, 16], "gold"),
    ]
    if part == "head":
        e += [element([4, 13, 4], [12, 15, 16], "carving"),
              element([5, 15, 8], [11, 16, 14], "gold")]
    elif part == "middle":
        e += [element([5, 13, 0], [11, 15, 16], "carving"),
              element([3, 13, 7], [13, 14, 9], "gold")]
    else:
        e += [element([3, 13, 0], [13, 15, 12], "carving"),
              element([1, 3, 0], [15, 14, 2], "gold")]
    return model(e)


def tapestry(part):
    if part == "top":
        e = [element([1, 14, 13], [15, 16, 16], "gold"),
             element([2, 0, 14], [14, 14, 15], "cloth"),
             element([4, 3, 13.75], [12, 11, 14], "gold", shade=False)]
    elif part == "middle":
        e = [element([2, 0, 14], [14, 16, 15], "cloth"),
             element([5, 3, 13.75], [11, 13, 14], "gold", shade=False)]
    else:
        e = [element([2, 5, 14], [14, 16, 15], "cloth_torn"),
             element([2, 2, 14], [5, 7, 15], "cloth_torn"),
             element([7, 1, 14], [10, 7, 15], "cloth_torn"),
             element([12, 3, 14], [14, 8, 15], "cloth_torn")]
    return model(e, ambient=False)


def carving():
    return model([
        element([1, 1, 14], [15, 15, 16], "stone"),
        element([3, 3, 13.5], [13, 13, 14], "carving"),
        element([7, 5, 13], [9, 12, 13.5], "gold"),
        element([4, 7, 13], [12, 9, 13.5], "gold"),
    ])


def door(side, part):
    inner = (12, 16) if side == "left" else (0, 4)
    outer = (0, 3) if side == "left" else (13, 16)
    e = [
        element([0, 0, 13], [16, 16, 16], "door"),
        element([outer[0], 0, 11], [outer[1], 16, 16], "stone"),
        element([inner[0], 2, 11.5], [inner[1], 14, 16], "gold"),
    ]
    if part == "base":
        e += [element([0, 0, 10], [16, 3, 16], "stone"),
              element([3, 5, 12], [13, 8, 13], "carving")]
    elif part == "middle":
        e += [element([3, 3, 12], [13, 13, 13], "carving"),
              element([7, 1, 11.5], [9, 15, 13], "gold")]
    else:
        e += [element([0, 13, 10], [16, 16, 16], "stone"),
              element([2, 9, 12], [14, 14, 13], "carving")]
    return model(e)


def statue(part):
    if part == "base":
        e = [element([1, 0, 1], [15, 4, 15], "stone"),
             element([3, 4, 3], [13, 8, 13], "cracked"),
             element([4, 8, 4], [8, 16, 10], "carving"),
             element([8, 8, 4], [12, 16, 10], "carving")]
    elif part == "body":
        e = [element([4, 0, 4], [12, 16, 12], "carving"),
             element([2, 7, 5], [5, 15, 11], "stone"),
             element([11, 7, 5], [14, 15, 11], "stone"),
             element([7, 2, 2], [9, 14, 5], "gold")]
    else:
        e = [element([5, 0, 5], [11, 9, 11], "carving"),
             element([4, 8, 4], [12, 12, 12], "stone"),
             element([3, 11, 3], [13, 14, 13], "gold"),
             element([2, 14, 2], [5, 16, 5], "gold"),
             element([7, 14, 2], [9, 16, 5], "gold"),
             element([11, 14, 2], [14, 16, 5], "gold")]
    return model(e)


BUILDERS = {
    "debris": debris, "sarcophagus_head": lambda: sarcophagus("head"),
    "sarcophagus_middle": lambda: sarcophagus("middle"),
    "sarcophagus_foot": lambda: sarcophagus("foot"),
    "tapestry_top": lambda: tapestry("top"), "tapestry_middle": lambda: tapestry("middle"),
    "tapestry_bottom": lambda: tapestry("bottom"), "carving": carving,
    "door_left_base": lambda: door("left", "base"), "door_right_base": lambda: door("right", "base"),
    "door_left_middle": lambda: door("left", "middle"), "door_right_middle": lambda: door("right", "middle"),
    "door_left_crown": lambda: door("left", "crown"), "door_right_crown": lambda: door("right", "crown"),
    "statue_base": lambda: statue("base"),
    "statue_body": lambda: statue("body"), "statue_crown": lambda: statue("crown")
}


def texture_bytes(kind):
    rng = random.Random("alfheim-funerary-" + kind)
    palettes = {
        "tomb_stone": ((190, 189, 170, 255), (139, 143, 134, 255), (218, 211, 181, 255)),
        "tomb_cracked": ((145, 146, 137, 255), (83, 88, 87, 255), (181, 176, 151, 255)),
        "grave_gold": ((174, 126, 42, 255), (91, 61, 29, 255), (232, 190, 75, 255)),
        "funerary_cloth": ((48, 25, 67, 255), (22, 13, 35, 255), (130, 90, 151, 255)),
        "funerary_cloth_torn": ((60, 31, 77, 255), (24, 13, 34, 255), (159, 120, 56, 255)),
        "memorial_carving": ((171, 169, 153, 255), (79, 87, 84, 255), (206, 192, 153, 255)),
        "grave_door": ((90, 83, 87, 255), (35, 29, 39, 255), (139, 117, 84, 255)),
    }
    base, dark, light = palettes[kind]
    im = Image.new("RGBA", (32, 32), base)
    px = im.load()
    for y in range(32):
        for x in range(32):
            n = rng.randrange(-13, 14)
            px[x, y] = tuple(max(0, min(255, base[i] + n)) for i in range(3)) + (255,)
    d = ImageDraw.Draw(im)
    if "cloth" in kind:
        for x in range(1, 32, 4): d.line((x, 0, x, 31), fill=dark, width=1)
        d.polygon([(16, 4), (25, 16), (16, 28), (7, 16)], outline=light)
        d.rectangle((14, 11, 18, 21), fill=light)
        if kind.endswith("torn"):
            d.polygon([(0, 27), (4, 31), (8, 25), (13, 31), (18, 26), (24, 31), (31, 24), (31, 31), (0, 31)], fill=(0,0,0,0))
    elif kind == "grave_door":
        d.rectangle((2, 2, 29, 29), outline=dark, width=3)
        d.rectangle((7, 6, 24, 27), outline=light, width=2)
        d.ellipse((11, 9, 21, 19), outline=light, width=2)
        d.line((16, 18, 16, 27), fill=dark, width=3)
    elif kind == "memorial_carving":
        d.ellipse((10, 3, 21, 14), outline=dark, width=2)
        d.line((16, 14, 16, 29), fill=dark, width=3)
        d.line((7, 20, 25, 20), fill=light, width=2)
        d.line((16, 18, 9, 28), fill=dark, width=2)
        d.line((16, 18, 23, 28), fill=dark, width=2)
    else:
        for y in (7, 15, 23): d.line((0, y, 31, y), fill=dark, width=1)
        for _ in range(11):
            x, y = rng.randrange(2, 30), rng.randrange(2, 30)
            d.line((x, y, min(31, x+rng.randrange(2,8)), min(31, y+rng.randrange(1,6))), fill=light)
    out = BytesIO(); im.save(out, format="PNG", optimize=False, compress_level=9)
    return out.getvalue()


def build():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = {}
    for b in m["blocks"]:
        out[f"{ASSET}/models/block/funerary/{b['kind']}.json"] = (json.dumps(BUILDERS[b["kind"]](), separators=(",", ":")) + "\n").encode()
    for kind in ("tomb_stone", "tomb_cracked", "grave_gold", "funerary_cloth", "funerary_cloth_torn", "memorial_carving", "grave_door"):
        out[f"{ASSET}/textures/block/funerary/{kind}.png"] = texture_bytes(kind)

    lines = ["// GENERATED by tools/gen_funerary_set.py — do not hand-edit.",
             "const FUNERARY_FACING = BlockProperties.HORIZONTAL_FACING", "",
             "function funeraryOrient(block) {", "  return block",
             "    .rotateState(state => state.setValue(FUNERARY_FACING, state.rotate(state.getValue(FUNERARY_FACING))))",
             "    .mirrorState(state => state.setValue(FUNERARY_FACING, state.mirror(state.getValue(FUNERARY_FACING))))", "}", "",
             "StartupEvents.registry('block', event => {"]
    for b in m["blocks"]:
        short = b["id"].split(":", 1)[1]
        lines += [f"  let {short} = event.create('{b['id']}', 'cardinal')",
                  f"    .displayName({json.dumps(b['name'])})",
                  f"    .model('alfheim:block/funerary/{b['kind']}')",
                  f"    .soundType('{b['sound']}')", "    .hardness(1.8).resistance(6.0)",
                  "    .fullBlock(false).notSolid().noValidSpawns(true)"]
        if b["render"] != "solid": lines.append(f"    .renderType('{b['render']}')")
        for bounds in b["boxes"]: lines.append("    .box(" + ", ".join(map(str, bounds)) + ")")
        lines += ["    .tagBlock('alfheim:elder_kings_funerary_set')",
                  "    .tagBlock('minecraft:mineable/pickaxe')"]
        if b["item"]:
            lines.append("    .tagItem('alfheim:elder_kings_funerary_set')")
        else:
            lines.append("    .noItem()")
        lines += [f"  funeraryOrient({short})", ""]
    lines += ["})", ""]
    out[STARTUP] = "\n".join(lines).encode()
    ids = [b["id"] for b in m["blocks"]]
    for tag, values in (("blocks", ids), ("items", [b["id"] for b in m["blocks"] if b["item"]])):
        out[f"{DATA}/tags/{tag}/elder_kings_funerary_set.json"] = (json.dumps({"replace":False,"values":values}, separators=(",", ":")) + "\n").encode()
    review = ["# GENERATED by tools/gen_funerary_set.py", "say [Alfheim] placing Elder Kings funerary review gallery"]
    for i, bid in enumerate(ids): review.append(f"setblock ~{i*2} ~ ~0 {bid}[facing=north]")
    review += ["# Complete assemblies", "setblock ~0 ~ ~5 alfheim:elder_sarcophagus_head[facing=north]", "setblock ~0 ~ ~6 alfheim:elder_sarcophagus_middle[facing=north]", "setblock ~0 ~ ~7 alfheim:elder_sarcophagus_foot[facing=north]"]
    for y, part in enumerate(("base", "middle", "crown")):
        review += [f"setblock ~4 ~{y} ~5 alfheim:elder_grave_door_left_{part}[facing=north]", f"setblock ~5 ~{y} ~5 alfheim:elder_grave_door_right_{part}[facing=north]"]
    review += ["setblock ~9 ~ ~5 alfheim:elder_statue_base[facing=north]", "setblock ~9 ~1 ~5 alfheim:elder_statue_body[facing=north]", "setblock ~9 ~2 ~5 alfheim:elder_statue_crown[facing=north]", "setblock ~13 ~2 ~5 alfheim:funerary_tapestry_top[facing=north]", "setblock ~13 ~1 ~5 alfheim:funerary_tapestry_middle[facing=north]", "setblock ~13 ~ ~5 alfheim:funerary_tapestry_bottom[facing=north]", ""]
    out[f"{DATA}/functions/elder_kings_funerary_set/review.mcfunction"] = "\n".join(review).encode()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); args = ap.parse_args()
    bad = []
    for rel, payload in build().items():
        path = ROOT / rel
        if args.check:
            if not path.exists() or path.read_bytes() != payload: bad.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
    if bad: raise SystemExit("Generated output mismatch:\n" + "\n".join(bad))
    print(f"{len(build())} funerary files " + ("byte-identical" if args.check else "generated"))


if __name__ == "__main__": main()
