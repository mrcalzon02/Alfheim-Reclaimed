"""Protect the existing Forge server mod mirror from a partial source pack.

The repository currently tracks two root mods/ JARs and 84 server/mods JARs.
The old mirror_instance() blindly removed server/mods before replacing it with
root mods/, which would silently wipe necessary dependencies. Exercise the
ACTUAL source preflight function and destructive-path ordering with fixtures.
"""
import ast
import glob
import os
from pathlib import Path
import shutil
import tempfile


def main():
    code = Path("tools/run_server.py").read_text(encoding="utf-8")
    tree = ast.parse(code)
    funcs = {node.name: node for node in tree.body
             if isinstance(node, ast.FunctionDef)}
    assert {"mirror_source_check", "mirror_instance", "run"} <= funcs.keys()
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in (
                        "MIRROR_MIN_MOD_JARS", "MIRROR_REQUIRED_PREFIXES", "MIRROR"):
                    assignments[target.id] = ast.literal_eval(node.value)
    assert assignments["MIRROR_MIN_MOD_JARS"] >= 70
    run_body = ast.get_source_segment(code, funcs["run"])
    assert run_body.index("mirror_source_check()") < run_body.index("os.makedirs(SERVER"),
    mirror_body = ast.get_source_segment(code, funcs["mirror_instance"])
    assert mirror_body.index("mirror_source_check()") < mirror_body.index("shutil.rmtree(dst)")
    ns = {"os": os, "glob": glob, "shutil": shutil, "SERVER": "server",
          "MIRROR": assignments["MIRROR"],
          "MIRROR_MIN_MOD_JARS": assignments["MIRROR_MIN_MOD_JARS"],
          "MIRROR_REQUIRED_PREFIXES": assignments["MIRROR_REQUIRED_PREFIXES"]}
    subset = ast.Module(body=[funcs["mirror_source_check"], funcs["mirror_instance"]],
                        type_ignores=[])
    exec(compile(ast.fix_missing_locations(subset), "run_server.py", "exec"), ns)
    guard, mirror = ns["mirror_source_check"], ns["mirror_instance"]
    required = (
        "Botania-1.jar", "MythicBotany-1.jar", "ars_nouveau-1.jar",
        "Mine_and_Slash-1.jar", "kubejs-forge-1.jar", "ftb-quests-forge-1.jar",
        "minecolonies-1.jar", "alfheim_companion-1.jar",
        "alfheim_leyworks-1.jar", "alfheim_golems-1.jar",
    )
    with tempfile.TemporaryDirectory(prefix="alfheim-mod-mirror-preflight-") as directory:
        base = Path(directory)
        for folder in ("mods", "config", "defaultconfigs", "kubejs", "server/mods"):
            (base / folder).mkdir(parents=True)
        for index in range(84):
            (base / "server/mods" / f"protected-{index}.jar").write_bytes(b"keep")
        sentinel = base / "server/mods/protected-0.jar"
        for name in ("alfheim_companion-0.2.0.jar", "alfheim_leyworks-0.1.0.jar"):
            (base / "mods" / name).write_bytes(b"partial")
        good, reason = guard(str(base), str(base / "server"))
        assert not good and "only 2 source" in reason
        old_cwd = Path.cwd()
        try:
            os.chdir(base)
            try:
                mirror()
            except RuntimeError as expected:
                assert "refusing destructive mirror" in str(expected)
            else:
                raise AssertionError("partial source destroyed an existing server mirror")
        finally:
            os.chdir(old_cwd)
        assert sentinel.read_bytes() == b"keep", "existing tracked server JAR overwritten"
        assert len(list((base / "server/mods").glob("*.jar"))) == 84

        for item in (base / "mods").iterdir():
            item.unlink()
        for index in range(85):
            (base / "mods" / f"other-{index}.jar").write_bytes(b"complete")
        good, reason = guard(str(base), str(base / "server"))
        assert not good and "required source gameplay mod" in reason
        for name in required:
            (base / "mods" / name).write_bytes(b"complete")
        good, reason = guard(str(base), str(base / "server"))
        assert good, reason
        for item in (base / "mods").iterdir():
            item.unlink()
        for name in required:
            (base / "mods" / name).write_bytes(b"complete")
        for index in range(70):
            (base / "mods" / f"other-{index}.jar").write_bytes(b"complete")
        good, reason = guard(str(base), str(base / "server"))
        assert not good and "would replace an existing" in reason
    print("SERVER_MIRROR_PREFLIGHT_PASS: partial source refused without destroying 84 stored jars, required mods checked, complete source accepted")


if __name__ == "__main__":
    main()
