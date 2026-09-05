"""Verify fey-wildlife generator source reproduces committed shipping artifacts.

This is a deterministic Level-6/source-to-shipping check. It runs the authoritative
``tools/gen_fey_wildlife.py`` in an isolated temporary directory, with the generator's
own fey language keys removed from the shared language seed so the run must recreate
them. Generated artifacts are compared against shipping, and stale generator-owned fey
biome modifiers are rejected. This does not claim runtime spawning or EntityJS acceptance.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CREATURES = 18
EXPECTED_GENERATED_FILES = EXPECTED_CREATURES * 4 + 3
LANG = Path("kubejs/assets/alfheim/lang/en_us.json")
MANIFEST = Path("tools/fey_manifest.json")
GENERATOR = Path("tools/gen_fey_wildlife.py")
FEY_MODIFIER_DIR = Path("kubejs/data/alfheim/forge/biome_modifier")


def generated_files(root: Path) -> list[Path]:
    """Return every file present in an isolated generator output tree."""
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def generated_fey_modifiers(root: Path) -> set[Path]:
    """Return generator-owned fey biome modifiers beneath ``root``."""
    directory = root / FEY_MODIFIER_DIR
    if not directory.is_dir():
        return set()
    return {
        path.relative_to(root)
        for path in directory.glob("fey_*.json")
        if path.is_file()
    }


def load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("manifest root must be a list")
    return data


def language_keys(roster: list[dict]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for entry in roster:
        ident = entry.get("id")
        name = entry.get("name")
        if not isinstance(ident, str) or not ident.startswith("alfheim:"):
            raise ValueError(f"invalid fey id in manifest: {ident!r}")
        if not isinstance(name, str) or not name:
            raise ValueError(f"invalid fey display name for {ident}")
        dotted = ident.replace(":", ".")
        expected[f"entity.{dotted}"] = name
        expected[f"item.{dotted}_spawn_egg"] = name + " Spawn Egg"
    return expected


def seed_shared_language(reference_root: Path, generated_root: Path, roster: list[dict]) -> None:
    """Seed shared lang minus fey-owned keys so the generator must recreate them."""
    shipping = json.loads((reference_root / LANG).read_text(encoding="utf-8"))
    if not isinstance(shipping, dict):
        raise ValueError(f"{LANG} root must be an object")
    for key in language_keys(roster):
        shipping.pop(key, None)
    target = generated_root / LANG
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(shipping, indent=2) + "\n", encoding="utf-8")


def compare_language(reference_root: Path, generated_root: Path, roster: list[dict]) -> list[str]:
    problems: list[str] = []
    try:
        shipping = json.loads((reference_root / LANG).read_text(encoding="utf-8"))
        generated = json.loads((generated_root / LANG).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"language output unreadable: {exc}"]
    if not isinstance(shipping, dict) or not isinstance(generated, dict):
        return [f"{LANG} must be a JSON object"]

    expected = language_keys(roster)
    for key, value in expected.items():
        if generated.get(key) != value:
            problems.append(f"generator did not recreate fey language entry: {key}")
        if shipping.get(key) != value:
            problems.append(f"shipping fey language entry drift: {key}")

    shipping_shared = {k: v for k, v in shipping.items() if k not in expected}
    generated_shared = {k: v for k, v in generated.items() if k not in expected}
    if shipping_shared != generated_shared:
        problems.append("generator changed non-fey entries in shared language file")
    return problems


def compare_outputs(reference_root: Path, generated_root: Path) -> list[str]:
    problems: list[str] = []
    paths = generated_files(generated_root)
    if len(paths) != EXPECTED_GENERATED_FILES:
        problems.append(
            f"generator emitted {len(paths)} files; expected {EXPECTED_GENERATED_FILES} "
            f"for {EXPECTED_CREATURES} creatures"
        )

    for rel in paths:
        if rel == LANG:
            continue
        expected = reference_root / rel
        actual = generated_root / rel
        if not expected.is_file():
            problems.append(f"generated output missing from repository: {rel}")
            continue
        if expected.read_bytes() != actual.read_bytes():
            problems.append(f"generator/source drift: {rel}")

    expected_modifiers = generated_fey_modifiers(generated_root)
    shipping_modifiers = generated_fey_modifiers(reference_root)
    for rel in sorted(shipping_modifiers - expected_modifiers):
        problems.append(f"stale generator-owned fey biome modifier in repository: {rel}")
    return problems


def check(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    generator = root / GENERATOR
    lang = root / LANG
    manifest = root / MANIFEST
    if not generator.is_file():
        return [f"missing authoritative generator: {GENERATOR}"]
    if not lang.is_file():
        return [f"missing language seed required by generator: {LANG}"]
    if not manifest.is_file():
        return [f"missing authoritative fey manifest: {MANIFEST}"]

    try:
        roster = load_manifest(manifest)
        if len(roster) != EXPECTED_CREATURES:
            return [f"shipping manifest contains {len(roster)} entries; expected {EXPECTED_CREATURES}"]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"shipping manifest invalid: {exc}"]

    with tempfile.TemporaryDirectory(prefix="alfheim-fey-generation-") as tmp:
        generated_root = Path(tmp)
        try:
            seed_shared_language(root, generated_root, roster)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            return [f"cannot prepare isolated language seed: {exc}"]

        proc = subprocess.run(
            [sys.executable, str(generator)],
            cwd=generated_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        if proc.returncode != 0:
            tail = "\n".join(proc.stdout.splitlines()[-20:])
            return [f"authoritative fey generator failed with exit {proc.returncode}:\n{tail}"]

        problems = compare_outputs(root, generated_root)
        generated_manifest = generated_root / MANIFEST
        if not generated_manifest.is_file():
            problems.append(f"generator did not emit {MANIFEST}")
            return problems
        try:
            regenerated_roster = load_manifest(generated_manifest)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            problems.append(f"generated manifest invalid: {exc}")
            return problems
        if len(regenerated_roster) != EXPECTED_CREATURES:
            problems.append(
                f"generated manifest contains {len(regenerated_roster)} entries; "
                f"expected {EXPECTED_CREATURES}"
            )
        problems.extend(compare_language(root, generated_root, regenerated_roster))
        return problems


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="alfheim-fey-check-selftest-") as tmp:
        root = Path(tmp) / "reference"
        generated = Path(tmp) / "generated"
        root.mkdir()
        generated.mkdir()
        for index in range(EXPECTED_GENERATED_FILES):
            rel = Path("out") / f"{index:03d}.json"
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (generated / rel).parent.mkdir(parents=True, exist_ok=True)
            payload = f"file-{index}\n".encode()
            (root / rel).write_bytes(payload)
            (generated / rel).write_bytes(payload)
        assert compare_outputs(root, generated) == []

        (generated / "out/000.json").write_text("drift\n", encoding="utf-8")
        assert compare_outputs(root, generated) == ["generator/source drift: out/000.json"]
        (generated / "out/000.json").write_bytes((root / "out/000.json").read_bytes())

        (generated / "out/001.json").unlink()
        assert any("generator emitted" in item for item in compare_outputs(root, generated))
        shutil.copyfile(root / "out/001.json", generated / "out/001.json")

        stale = root / FEY_MODIFIER_DIR / "fey_retired_species.json"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("{}\n", encoding="utf-8")
        assert compare_outputs(root, generated) == [
            "stale generator-owned fey biome modifier in repository: "
            "kubejs/data/alfheim/forge/biome_modifier/fey_retired_species.json"
        ]

        roster = [{"id": "alfheim:test_fey", "name": "Test Fey"}]
        for base in (root, generated):
            lang = base / LANG
            lang.parent.mkdir(parents=True, exist_ok=True)
            lang.write_text(
                json.dumps(
                    {
                        "shared.key": "Shared",
                        "entity.alfheim.test_fey": "Test Fey",
                        "item.alfheim.test_fey_spawn_egg": "Test Fey Spawn Egg",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        assert compare_language(root, generated, roster) == []
        generated_lang = json.loads((generated / LANG).read_text(encoding="utf-8"))
        generated_lang.pop("entity.alfheim.test_fey")
        (generated / LANG).write_text(json.dumps(generated_lang, indent=2) + "\n", encoding="utf-8")
        assert compare_language(root, generated, roster) == [
            "generator did not recreate fey language entry: entity.alfheim.test_fey"
        ]

    print("self-test: generated-output, stale-output, and language ownership contracts PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    problems = check(args.root)
    if problems:
        for problem in problems:
            print("PROBLEM:", problem)
        print(f"fey generator equality: FAIL ({len(problems)} problem(s))")
        return 1
    print(
        f"fey generator equality: PASS ({EXPECTED_CREATURES} creatures, "
        f"{EXPECTED_GENERATED_FILES} generated files reconciled, language ownership proven, "
        "no stale fey modifiers)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
