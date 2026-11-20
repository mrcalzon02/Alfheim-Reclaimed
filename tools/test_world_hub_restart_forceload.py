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

    # Generated runtime functions may never wipe tickets belonging to other mods.
    def bounded(lines):
        return not any("forceload remove all" in line for line in lines
                       if not line.lstrip().startswith("#"))

    for name, generated_lines in mod["FILES"].items():
        assert bounded(generated_lines), f"global forced-chunk wipe in generated hub/{name}"
    assert not bounded(["execute in mythicbotany:alfheim run forceload remove all"]), (
        "negative control failed to reject an unsafe global reset")

    shipping = {}
    for name in ("place", "anchor", "fallback", "status"):
        generated_text = "\n".join(mod["FILES"][name]) + "\n"
        actual = Path(f"kubejs/data/alfheim/functions/hub/{name}.mcfunction").read_text(
            encoding="utf-8")
        assert actual == generated_text, f"hub/{name} drifted from the generator"
        shipping[name] = [line for line in actual.splitlines()
                          if line and not line.startswith("#")]
        assert bounded(shipping[name]), f"shipped hub/{name} wipes unrelated tickets"

    region = (f"-{mod['PLACE_LOAD_X']} -{mod['PLACE_LOAD_NORTH']} "
              f"{mod['PLACE_LOAD_X']} {mod['PLACE_LOAD_SOUTH']}")
    scoped_cleanup = (f"execute in {mod['HOME']} unless score #already {mod['OBJ']} matches 1 "
                      f"if score #place_result {mod['OBJ']} matches 0 "
                      f"run forceload remove {region}")
    assert scoped_cleanup in shipping["place"], (
        "failed placement must clean up the bounded candidate, never the dimension")
    assert f"execute in {mod['HOME']} run forceload add {region}" in shipping["anchor"], (
        "anchoring must reassert the deterministic origin without marker-relative loading")
    assert not any("forceload remove" in line for line in shipping["anchor"]), (
        "successful anchoring must not remove other forced chunk tickets")
    fallback_load = f"execute in {mod['HOME']} run forceload add -16 -16 16 16"
    assert shipping["fallback"].count(fallback_load) == 1, (
        "fallback must retain exactly one 3x3 forced-chunk envelope")
    assert not any("forceload remove" in line for line in shipping["fallback"]), (
        "provisional landing must not clear existing tickets")


    # Only provisional players actually present in Alfheim may be collected.
    # @a includes travelers in other dimensions; a global tag removal also
    # erased their recovery state even when they were not delivered.
    awaited = [line for line in shipping["anchor"]
               if mod["AWAIT"] in line]
    selector = f"@e[type=minecraft:player,tag={mod['AWAIT']}]"
    assert len(awaited) == 4, "two transfers, one message, one cleanup expected"
    assert all(line.startswith(f"execute in {mod['HOME']} ") and selector in line
               for line in awaited), (
        "all provisional recalls and tag changes must target Alfheim players only")
    assert sum("run tp @s" in line for line in awaited) == 1
    assert sum("run spawnpoint @s" in line for line in awaited) == 1
    assert sum("run tellraw @s" in line for line in awaited) == 1
    assert sum("run tag " in line and " remove " in line for line in awaited) == 1

    # This operator command is strictly observational. Reject any mutation
    # slipped in by a future generator refactor.
    status_lines = shipping["status"]
    destructive = (
        " run kill ", " run tp ", " run spawnpoint ", " run fill ",
        " run setblock ", " run summon ", " run function ", " run tag ",
        " run forceload add ", " run forceload remove ",
        "scoreboard players set ", "scoreboard players reset ",
        "scoreboard players add ", "scoreboard players remove "
    )
    assert not any(any(token in line for token in destructive)
                   for line in status_lines), "status must stay read-only"
    assert any("hub: BAKED" in line and "if score #final" in line
               for line in status_lines), "status must distinguish completed hub"
    assert any("hub: PROVISIONAL" in line and "unless score #final" in line
               for line in status_lines), "status must distinguish provisional spawn"
    assert any("retry limit reached" in line for line in status_lines)
    assert any("tag=alfheim_hub_baked" in line and "data get entity" in line
               for line in status_lines), "status must query real baked marker"
    assert not any(" at @s " in line or " run tellraw @s " in line
                   for line in status_lines), "status must work from console"

    print("WORLD_HUB_RESTART_FORCELOAD_PASS: scoped chunk loads, Alfheim-only collection, read-only operator diagnostics")


if __name__ == "__main__":
    main()
