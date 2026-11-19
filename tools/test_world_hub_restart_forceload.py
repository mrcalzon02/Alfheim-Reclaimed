"""Test the REAL generated hub/autoload commands against the shipped function.

Two-boot Forge runtime 44637365193: completion scores persisted, but the baked
anchor was absent because autoload selected it before its chunk could load.
"""
from pathlib import Path
import runpy


def main():
    mod = runpy.run_path("tools/gen_world_hub.py")
    generated = "\n".join(mod["FILES"]["autoload"]) + "\n"
    shipped = Path("kubejs/data/alfheim/functions/hub/autoload.mcfunction").read_text(
        encoding="utf-8")
    assert generated == shipped, "hub/autoload drifted from authoritative generator"
    assert mod["CANDIDATES"] == [(0, 0)], "hub is no longer at fixed origin"
    wanted = (f"execute if score #final {mod['OBJ']} matches 1 "
              f"in {mod['HOME']} run forceload add "
              f"-{mod['PLACE_LOAD_X']} -{mod['PLACE_LOAD_NORTH']} "
              f"{mod['PLACE_LOAD_X']} {mod['PLACE_LOAD_SOUTH']}")
    commands = [s for s in shipped.splitlines() if s and not s.startswith("#")]
    assert wanted in commands, "completed hub must force-load by absolute origin"
    assert not any("forceload add" in s and "at @e[" in s for s in commands), (
        "saved marker cannot be required to load its own chunks")
    assert shipped.index(wanted) < shipped.index(
        "execute if score #final alfheim.hub matches 1 unless score #foundation_v1"), (
        "autoload must force-load before subsequent recovery tasks")
    assert mod["PLACE_LOAD_X"] * 2 <= 256
    assert mod["PLACE_LOAD_NORTH"] + mod["PLACE_LOAD_SOUTH"] <= 256
    print("WORLD_HUB_RESTART_FORCELOAD_PASS: generator/shipped parity, absolute saved-hub load, bounded footprint")


if __name__ == "__main__":
    main()
