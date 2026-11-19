"""Source-to-generated predicate contract for the Greatbole origin height gate.

The deepest authored foundation extends 40 blocks under the surface datum.
Test the generator constant and the actual datapack JSON rather than a copied
predicate reimplementation. A future generator run must retain this fix.
"""
import ast
import json
from pathlib import Path


def check():
    source = Path("tools/gen_world_hub.py").read_text(encoding="utf-8")
    node = ast.parse(source)
    constants = {}
    for entry in node.body:
        if isinstance(entry, ast.Assign):
            for target in entry.targets:
                if isinstance(target, ast.Name) and target.id in ("GROUND_MIN_Y", "GROUND_MAX_Y"):
                    constants[target.id] = ast.literal_eval(entry.value)
    assert set(constants) == {"GROUND_MIN_Y", "GROUND_MAX_Y"}, "generator missing bounds"
    low, high = constants["GROUND_MIN_Y"], constants["GROUND_MAX_Y"]
    assert isinstance(low, int) and isinstance(high, int)
    assert low <= 63 <= high, "normal sea-level origin must not be rejected"
    assert low - 40 >= -64, "foundation could pierce the dimension floor"
    assert high <= 200 and low < high, "crown could breach world build height"
    assert "'min':GROUND_MIN_Y,'max':GROUND_MAX_Y" in source, (
        "generator JSON must reference the declared height bounds")

    actual = json.loads(Path(
        "kubejs/data/alfheim/predicates/hub/ground_height.json").read_text(encoding="utf-8"))
    assert actual["condition"] == "minecraft:location_check"
    assert actual["predicate"]["position"]["y"] == {"min": low, "max": high}, (
        "shipping predicate drifted from its generator")
    placement = Path(
        "kubejs/data/alfheim/functions/hub/place.mcfunction").read_text(encoding="utf-8")
    assert ("positioned over motion_blocking_no_leaves "
            "if predicate alfheim:hub/ground_height run function alfheim:hub/assemble"
            in placement), "runtime must test the same generated predicate"
    print(f"WORLD_HUB_HEIGHT_CONTRACT_PASS: terrain Y{low}..Y{high}, safe foundation, generator and datapack agree")


if __name__ == "__main__":
    check()
