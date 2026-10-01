"""Disable Library of Exile's game-directory-wide startup wipe.

Run with Minecraft closed. Defaults cover new worlds; existing worlds keep their
own Forge server configs, so update those as well, backing up changed files.
No dimension directories or saved map data are deleted.
"""
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = {
    "the_harvest_dimension-server.toml": "the_harvest:harvest",
    "ancient_obelisks_dimension-server.toml": "ancient_obelisks:obelisk",
    "dungeon_realm_dimension-server.toml": "dungeon_realm:dungeon",
}


def repair(root=ROOT):
    for filename, dimension in DIMENSIONS.items():
        default = root / "defaultconfigs" / filename
        if not default.exists():
            default.parent.mkdir(parents=True, exist_ok=True)
            default.write_text(
                '# Avoid scanning and wiping expedition folders across every saved world.\n'
                '# Expedition instances retain their normal in-game lifecycle.\n'
                f'["{dimension}"]\nWIPE_DIMENSION_ON_LOAD = false\n',
                encoding="utf-8",
            )
        paths = [default, *sorted((root / "saves").glob(f"*/serverconfig/{filename}"))]
        for path in paths:
            original = path.read_text(encoding="utf-8")
            parsed = tomllib.loads(original)
            if "WIPE_DIMENSION_ON_LOAD" not in parsed.get(dimension, {}):
                raise ValueError(f"Missing wipe setting: {path}")
            updated, count = re.subn(
                r"(?m)^(\s*WIPE_DIMENSION_ON_LOAD\s*=\s*)true\b",
                r"\g<1>false", original,
            )
            if updated != original:
                backup = path.with_name(path.name + ".boot-repair.bak")
                if not backup.exists():
                    backup.write_bytes(path.read_bytes())
                path.write_text(updated, encoding="utf-8")
                print(f"Repaired {path.relative_to(root)} ({count} setting)")
            assert tomllib.loads(path.read_text(encoding="utf-8"))[dimension][
                "WIPE_DIMENSION_ON_LOAD"
            ] is False, path


if __name__ == "__main__":
    repair()
