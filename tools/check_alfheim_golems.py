#!/usr/bin/env python3
"""Validate and optionally install the first-party Alfheim Golems artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "first_party_mods" / "alfheim_golems"
EXPECTED_NAME = "alfheim_golems-0.1.0.jar"
DEFAULT_JAR = PROJECT / "build" / "libs" / EXPECTED_NAME
REQUIRED = {
    "META-INF/mods.toml",
    "META-INF/MANIFEST.MF",
    "pack.mcmeta",
    "com/continuityworks/alfheimgolems/AlfheimGolems.class",
    "com/continuityworks/alfheimgolems/domain/Element.class",
    "com/continuityworks/alfheimgolems/data/GolemNetworkSavedData.class",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def class_major(raw: bytes) -> int:
    if len(raw) < 8 or raw[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("main class has no Java class-file header")
    return struct.unpack(">H", raw[6:8])[0]


def validate(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"artifact missing: {path}")
    if path.name != EXPECTED_NAME:
        raise ValueError(f"unexpected artifact name: {path.name}")

    with zipfile.ZipFile(path) as jar:
        names = set(jar.namelist())
        missing = sorted(REQUIRED - names)
        if missing:
            raise ValueError("artifact missing entries: " + ", ".join(missing))
        forbidden = sorted(name for name in names if "examplemod" in name.lower())
        if forbidden:
            raise ValueError("example-mod residue: " + ", ".join(forbidden[:10]))

        mods = jar.read("META-INF/mods.toml").decode("utf-8")
        if 'modId="alfheim_golems"' not in mods or "${" in mods:
            raise ValueError("mods.toml is unexpanded or has the wrong mod id")
        if 'modId="forge"' not in mods or 'modId="minecraft"' not in mods:
            raise ValueError("mandatory Forge/Minecraft dependency metadata missing")

        pack = json.loads(jar.read("pack.mcmeta"))
        if pack.get("pack", {}).get("pack_format") != 15:
            raise ValueError("pack.mcmeta must target resource pack format 15")
        if class_major(jar.read("com/continuityworks/alfheimgolems/AlfheimGolems.class")) != 61:
            raise ValueError("main class is not Java 17 bytecode")

    return digest(path)


def install(path: Path, sha256: str) -> None:
    targets = [ROOT / "mods" / EXPECTED_NAME, ROOT / "server" / "mods" / EXPECTED_NAME]
    for directory in (ROOT / "mods", ROOT / "server" / "mods"):
        conflicts = [item for item in directory.glob("alfheim_golems-*.jar")
                     if item.name != EXPECTED_NAME]
        if conflicts:
            raise ValueError("refusing install beside another version: "
                             + ", ".join(str(item) for item in conflicts))

    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        if digest(target) != sha256:
            raise ValueError(f"installed artifact hash mismatch: {target}")
    print(f"INSTALL PASS client/server sha256={sha256}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jar", type=Path, default=DEFAULT_JAR)
    parser.add_argument("--install", action="store_true",
                        help="copy the one validated artifact to client and server mods")
    args = parser.parse_args()
    try:
        sha256 = validate(args.jar.resolve())
        print(f"PASS {EXPECTED_NAME} entries={len(REQUIRED)} java=17 sha256={sha256}")
        if args.install:
            install(args.jar.resolve(), sha256)
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
