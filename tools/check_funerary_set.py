"""Static acceptance checks for the bespoke Elder Kings funerary block set."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "funerary_set_manifest.json"
STARTUP = ROOT / "kubejs" / "startup_scripts" / "24_funerary_set.js"
MODELS = ROOT / "kubejs" / "assets" / "alfheim" / "models" / "block" / "funerary"
TEXTURES = ROOT / "kubejs" / "assets" / "alfheim" / "textures" / "block" / "funerary"
TOMB = ROOT / "kubejs" / "data" / "alfheim" / "structures" / "deepworks_archaeology" / "elder_kings_tomb"


def main():
    problems = []
    fail = problems.append
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_semantics = {"tomb_debris", "royal_sarcophagus", "funerary_tapestry",
                          "memorial_carving", "grave_door", "funerary_statue"}
    if set(data.get("semantic_assets", [])) != expected_semantics:
        fail("semantic funerary coverage drift")
    blocks = data.get("blocks", [])
    ids = [b["id"] for b in blocks]
    if len(blocks) != 17 or len(ids) != len(set(ids)):
        fail(f"expected 17 unique physical modules, found {len(set(ids))}")
    for b in blocks:
        path = MODELS / f"{b['kind']}.json"
        if not path.exists():
            fail(f"missing model {path.relative_to(ROOT)}")
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        if obj.get("parent") != "minecraft:block/block" or not obj.get("elements"):
            fail(f"{b['id']}: invalid custom model")
        for el in obj.get("elements", []):
            coords = el.get("from", []) + el.get("to", [])
            if len(coords) != 6 or not all(0 <= value <= 16 for value in coords):
                fail(f"{b['id']}: model geometry leaves local block bounds")
        for bounds in b.get("boxes", []):
            if len(bounds) != 6 or not all(0 <= value <= 16 for value in bounds):
                fail(f"{b['id']}: invalid collision bounds")

    pngs = sorted(TEXTURES.glob("*.png"))
    if len(pngs) != 7:
        fail(f"expected 7 custom pixel textures, found {len(pngs)}")
    for path in pngs:
        with Image.open(path) as image:
            if image.size != (32, 32) or image.mode != "RGBA":
                fail(f"{path.name}: expected 32x32 RGBA")
            alphas = image.getchannel("A").getextrema()
            if path.name == "funerary_cloth_torn.png" and alphas[0] != 0:
                fail("tattered cloth has no transparent torn edge")

    script = STARTUP.read_text(encoding="utf-8") if STARTUP.exists() else ""
    for bid in ids:
        if f"event.create('{bid}', 'cardinal')" not in script:
            fail(f"{bid}: missing cardinal registration")
    if ".rotateState(" not in script or ".mirrorState(" not in script:
        fail("custom directional blocks lack structure transform callbacks")
    node = shutil.which("node")
    if node and STARTUP.exists():
        checked = subprocess.run([node, "--check", str(STARTUP)], capture_output=True, text=True)
        if checked.returncode:
            fail("startup syntax: " + (checked.stderr or checked.stdout).strip())

    sys.path.insert(0, str(ROOT / "tools"))
    import nbt
    palettes = {}
    for role in ("centre", "approach", "wing"):
        _, piece = nbt.load(str(TOMB / f"{role}.nbt"))
        palettes[role] = [entry["Name"] for entry in piece["palette"]]
    tomb_ids = set(palettes["centre"] + palettes["wing"])
    if not set(ids) <= tomb_ids:
        fail("not every funerary module is integrated into the Elder Kings tomb")
    _, wing = nbt.load(str(TOMB / "wing.nbt"))
    wing_names = [wing["palette"][int(entry["state"])]["Name"] for entry in wing["blocks"]]
    for part in ("head", "middle", "foot"):
        if wing_names.count(f"alfheim:elder_sarcophagus_{part}") != 3:
            fail(f"tomb wing must contain three sarcophagus {part} modules")

    spec = importlib.util.spec_from_file_location("gen_funerary_set", ROOT / "tools" / "gen_funerary_set.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    for rel, payload in mod.build().items():
        path = ROOT / rel
        if not path.exists() or path.read_bytes() != payload:
            fail(f"generated output drift {rel}")
    if problems:
        print("ELDER KINGS FUNERARY SET: FAIL")
        for problem in problems: print(" - " + problem)
        return 1
    print("ELDER KINGS FUNERARY SET: PASS semantics=6 modules=17 textures=7 tomb_sarcophagi=12")
    print("Acceptance boundary: static source/generated and structure integration; runtime load not claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
