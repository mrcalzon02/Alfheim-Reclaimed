#!/usr/bin/env python3
"""
Acceptance check for an incoming mod jar — written ahead of delivery.

Role: development tooling. NOT a runtime artifact, never packaged, never placed in mods/.
Contract checked: alfheim_reclaimed_design/WORLD_STRUCTURE.md section 6.

Usage:
    python tools/check_incoming_mod.py <path-to.jar>

Reports PASS / FAIL / WARN per contract clause and exits non-zero on any FAIL.
Read-only: opens the jar, touches nothing else.
"""

import glob
import io
import json
import os
import re
import sys
import zipfile

CLIENT_JAR = (r"C:\Users\Admin\curseforge\minecraft\Install\versions"
              r"\1.20.1\1.20.1.jar")

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib

PACK_MC = "1.20.1"
PACK_LOADER = "forge"
PACK_MODS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mods")
ALFHEIM_TAG = "data/mythicbotany/tags/worldgen/biome/alfheim.json"
RESERVED_IDS = {"continuity"}  # installed connected-textures mod; must not collide

results = []


def record(level, clause, detail):
    results.append((level, clause, detail))


def existing_mod_ids(exclude=None):
    """Mod IDs already claimed by the installed jars, including JarJar-nested.

    `exclude` is the basename of the jar under test, so re-checking a jar that is
    already installed does not report it as colliding with itself.
    """
    found = {}

    def scan(src, label, depth=0):
        try:
            z = zipfile.ZipFile(src)
        except Exception:
            return
        names = set(z.namelist())
        for key in ("META-INF/mods.toml", "META-INF/neoforge.mods.toml"):
            if key in names:
                try:
                    d = tomllib.loads(z.read(key).decode("utf-8", "replace").lstrip("﻿"))
                except Exception:
                    continue
                for m in d.get("mods", []) or []:
                    if m.get("modId"):
                        found.setdefault(m["modId"], label)
                break
        if depth < 2:
            for e in names:
                if e.startswith("META-INF/jarjar/") and e.endswith(".jar"):
                    scan(io.BytesIO(z.read(e)), f"{label}!{os.path.basename(e)}", depth + 1)
        z.close()

    if os.path.isdir(PACK_MODS_DIR):
        for fn in sorted(os.listdir(PACK_MODS_DIR)):
            if fn.endswith(".jar") and fn != exclude:
                scan(os.path.join(PACK_MODS_DIR, fn), fn)
    return found


def main(path):
    if not os.path.isfile(path):
        print(f"error: no such file: {path}")
        return 2

    z = zipfile.ZipFile(path)
    names = set(z.namelist())

    # --- Clause 0: loader format and target version -------------------------
    has_forge = "META-INF/mods.toml" in names
    has_neo = "META-INF/neoforge.mods.toml" in names

    if has_forge:
        record("PASS", "loader format", "ships META-INF/mods.toml (Forge-readable)")
        toml_key = "META-INF/mods.toml"
    elif has_neo:
        record("FAIL", "loader format",
               "ships ONLY META-INF/neoforge.mods.toml. Forge 1.20.1 cannot read this. "
               "Same defect as the quarantined create_sophback_compat jar.")
        toml_key = "META-INF/neoforge.mods.toml"
    else:
        record("FAIL", "loader format", "no mods.toml of any kind — not a loadable Forge mod")
        toml_key = None

    meta = {}
    declared_ids = []
    if toml_key:
        try:
            meta = tomllib.loads(z.read(toml_key).decode("utf-8", "replace").lstrip("﻿"))
        except Exception as e:
            record("FAIL", "metadata", f"mods.toml does not parse: {e}")
        declared_ids = [m.get("modId") for m in meta.get("mods", []) or [] if m.get("modId")]

    # --- Clause 1: mod ID does not collide ----------------------------------
    installed = existing_mod_ids(exclude=os.path.basename(path))
    if not declared_ids:
        record("FAIL", "mod id", "no modId declared")
    for mid in declared_ids:
        if mid in RESERVED_IDS:
            record("FAIL", "mod id",
                   f'"{mid}" collides with the installed connected-textures mod Continuity. Rename.')
        elif mid in installed:
            record("FAIL", "mod id", f'"{mid}" already claimed by {installed[mid]}')
        else:
            record("PASS", "mod id", f'"{mid}" is unique against {len(installed)} installed IDs')

    # --- Clause 2: dependencies resolve against the pack --------------------
    for owner, deps in (meta.get("dependencies") or {}).items():
        for dep in deps or []:
            dep_id = dep.get("modId")
            mandatory = dep.get("mandatory")
            if mandatory is None:
                mandatory = dep.get("type", "required") == "required"
            if not mandatory or not dep_id:
                continue
            low = dep_id.lower()
            if low == "neoforge":
                record("FAIL", "dependencies",
                       f'requires "neoforge" {dep.get("versionRange","")} — this pack is Forge')
            elif low in ("minecraft", "forge", "java", "fml"):
                vr = dep.get("versionRange", "")
                if low == "minecraft" and vr and PACK_MC not in vr and "1.20" not in vr:
                    record("WARN", "dependencies", f'minecraft range "{vr}" may exclude {PACK_MC}')
            elif dep_id not in installed and dep_id not in declared_ids:
                record("FAIL", "dependencies", f'requires "{dep_id}", which is NOT installed')

    # --- Clause 3: every referenced placed_feature must resolve --------------
    #
    # This is CW-1, and it is the check that matters most for a worldgen mod. A biome naming a
    # placed_feature that nothing provides does NOT fail at load: the registry creates an unbound
    # Holder.Reference and says nothing. It throws later, inside FeatureSorter, the first time a
    # chunk resolves that biome -- so it surfaces hundreds of chunks out, seed-dependently, long
    # after the mod appeared to install cleanly.
    #
    # Continuity Works 0.3.0-rc.2 shipped `minecraft:ore_diamond_medium` in 136 of its 146 biomes.
    # No such placed_feature exists in 1.20.1; vanilla has ore_diamond, ore_diamond_large and
    # ore_diamond_buried, all three of which were already in the list beside it.
    available = set()
    for src in [CLIENT_JAR] + sorted(glob.glob(os.path.join("mods", "*.jar"))) + [path]:
        if not os.path.exists(src):
            continue
        try:
            with zipfile.ZipFile(src) as zz:
                for e in zz.namelist():
                    m = re.match(r"data/([^/]+)/worldgen/placed_feature/(.+)\.json$", e)
                    if m:
                        available.add(f"{m.group(1)}:{m.group(2)}")
        except Exception:
            continue

    biome_defs = [e for e in names
                  if re.match(r"data/[^/]+/worldgen/biome/[^/].*\.json$", e)
                  and "/tags/" not in e]
    unresolved = {}
    for e in biome_defs:
        try:
            doc = json.loads(z.read(e).decode("utf-8", "replace"))
        except Exception:
            continue
        for step in doc.get("features", []) or []:
            for f in step:
                if isinstance(f, str) and not f.startswith("#") and f not in available:
                    unresolved[f] = unresolved.get(f, 0) + 1

    if not biome_defs:
        pass
    elif unresolved:
        worst = sorted(unresolved.items(), key=lambda kv: -kv[1])
        detail = ", ".join(f"{k} (x{v})" for k, v in worst[:4])
        record("FAIL", "feature references",
               f"{sum(unresolved.values())} reference(s) to {len(unresolved)} placed_feature(s) "
               f"that nothing provides: {detail}. This crashes chunk generation in FeatureSorter, "
               "not at load — see CONTINUITY_WORKS_DEFECTS.md CW-1.")
    else:
        record("PASS", "feature references",
               f"all placed_feature references across {len(biome_defs)} biome(s) resolve")

    # --- Clause 4: must NOT own the Overworld generator ---------------------
    overworld_claims = [
        e for e in names
        if e.endswith(("worldgen/world_preset/normal.json", "dimension/overworld.json",
                       "worldgen/noise_settings/overworld.json"))
    ]
    if overworld_claims:
        record("WARN", "worldgen ownership",
               "claims the Overworld generator: " + ", ".join(sorted(overworld_claims)) +
               ". Only one owner allowed — reconcile against WORLD_STRUCTURE.md section 3.")
    else:
        record("PASS", "worldgen ownership", "does not claim the Overworld generator")

    # --- Clause 5: biomes carry vanilla convention tags ---------------------
    # Count DEFINITIONS, not tag files. Counting both is how "176 biomes" was reported for a mod
    # that ships 146 biomes and 30 tag files.
    biomes = biome_defs
    conv = [e for e in names
            if "/tags/worldgen/biome/" in e and e.endswith(".json")
            and ("data/minecraft/" in e or "data/forge/" in e or "data/c/" in e)]
    if biomes:
        if conv:
            record("PASS", "convention tags",
                   f"{len(biomes)} biome(s), {len(conv)} vanilla/forge convention tag file(s)")
        else:
            record("WARN", "convention tags",
                   f"{len(biomes)} biome(s) but no minecraft/forge convention tags. Existing "
                   "structure and mob placement will not find them — see WORLD_STRUCTURE.md "
                   "section 4.")

    # --- Inventory ----------------------------------------------------------
    dims = [e for e in names if "/dimension/" in e and e.endswith(".json")]
    structs = [e for e in names if "/worldgen/structure/" in e and e.endswith(".json")]
    nbts = [e for e in names if e.endswith(".nbt")]

    z.close()

    print(f"\n  {os.path.basename(path)}")
    print(f"  {'-' * 68}")
    print(f"  declared mod IDs : {', '.join(declared_ids) or '(none)'}")
    print(f"  biomes           : {len(biomes)}")
    print(f"  dimensions       : {len(dims)}")
    print(f"  structures       : {len(structs)}")
    print(f"  nbt pieces       : {len(nbts)}")
    print(f"  {'-' * 68}\n")

    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    for level, clause, detail in sorted(results, key=lambda r: order[r[0]]):
        print(f"  [{level:4}] {clause:20} {detail}")

    fails = sum(1 for r in results if r[0] == "FAIL")
    warns = sum(1 for r in results if r[0] == "WARN")
    print(f"\n  {fails} fail, {warns} warn, "
          f"{sum(1 for r in results if r[0] == 'PASS')} pass\n")
    if fails:
        print("  Do NOT place this jar in mods/ until the failures are resolved.\n")
    return 1 if fails else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
