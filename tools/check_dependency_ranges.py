"""Validate every declared dependency version range against what is actually installed.

Why this exists: an earlier scan checked only *mandatory* dependencies and passed the pack
clean. First boot then died on an **optional** one — MineColonies declares
`journeymap [5.9.8,)`, JourneyMap declares its version as `1.20.1-6.0.4`, and Maven reads
that as major version 1. Forge treats an installed-but-out-of-range optional dependency as
fatal: "optional" means it may be absent, not that any version will do.

So this checks both kinds, and only where the target mod is actually present.

    python tools/check_dependency_ranges.py [mods_dir]

Exit 0 = no violations. Exit 1 = at least one violation.
"""
import glob, io, os, re, sys, zipfile

try:
    import tomllib
except ImportError:                                    # pragma: no cover
    import tomli as tomllib


# --- Maven DefaultArtifactVersion semantics -------------------------------------------------

# Qualifier ordering from Maven's ComparableVersion. Anything unrecognised sorts after these
# and is compared lexically; the empty qualifier (a plain release) outranks all of them.
_QUALIFIERS = ["alpha", "beta", "milestone", "rc", "snapshot", "", "sp"]
_ALIASES = {"cr": "rc", "ga": "", "final": "", "release": ""}


class Version:
    """Approximates org.apache.maven.artifact.versioning.ComparableVersion.

    Maven's DefaultArtifactVersion delegates comparison to ComparableVersion, which tokenises
    the string rather than comparing fixed major/minor/incremental fields. That distinction
    matters here: a naive field parse rates '1.20.1-85-FORGE' *below* '1.20.1-83', which is
    wrong and produced a wave of false positives on this pack.

    Tokens split on '.', '-', and digit/letter boundaries. Numeric tokens compare numerically
    and outrank string tokens; string tokens compare by the qualifier order above.
    """

    __slots__ = ("raw", "items")

    def __init__(self, raw):
        self.raw = raw
        # Semver build metadata is not part of precedence: '0.4.32+ef105b4977'.
        s = raw.split("+", 1)[0].strip().lower()
        self.items = self._tokenise(s)

    @staticmethod
    def _tokenise(s):
        out, buf, buf_is_digit = [], "", None

        def flush():
            nonlocal buf, buf_is_digit
            if buf:
                out.append(int(buf) if buf_is_digit else _ALIASES.get(buf, buf))
                buf, buf_is_digit = "", None

        for ch in s:
            if ch in ".-_":
                flush()
                continue
            is_digit = ch.isdigit()
            if buf and is_digit != buf_is_digit:
                flush()
            buf += ch
            buf_is_digit = is_digit
        flush()
        return out

    @staticmethod
    def _cmp_item(a, b):
        if isinstance(a, int) and isinstance(b, int):
            return (a > b) - (a < b)
        if isinstance(a, int):
            return 1                      # a number always outranks a qualifier
        if isinstance(b, int):
            return -1
        ia = _QUALIFIERS.index(a) if a in _QUALIFIERS else len(_QUALIFIERS)
        ib = _QUALIFIERS.index(b) if b in _QUALIFIERS else len(_QUALIFIERS)
        if ia != ib:
            return (ia > ib) - (ia < ib)
        return (a > b) - (a < b)

    def _cmp(self, other):
        a, b = self.items, other.items
        for i in range(max(len(a), len(b))):
            # A missing token is a zero when the other side is numeric, and a release
            # qualifier otherwise — matching Maven's padding behaviour.
            x = a[i] if i < len(a) else (0 if i < len(b) and isinstance(b[i], int) else "")
            y = b[i] if i < len(b) else (0 if i < len(a) and isinstance(a[i], int) else "")
            c = self._cmp_item(x, y)
            if c:
                return c
        return 0

    def __lt__(self, o): return self._cmp(o) < 0
    def __le__(self, o): return self._cmp(o) <= 0
    def __gt__(self, o): return self._cmp(o) > 0
    def __ge__(self, o): return self._cmp(o) >= 0
    def __eq__(self, o): return self._cmp(o) == 0
    def __repr__(self): return self.raw


def in_range(version_str, range_str):
    """Evaluate a Maven version range. Returns (ok, explanation)."""
    if not range_str or range_str.strip() in ("*", ""):
        return True, "unbounded"
    v = Version(version_str)
    spec = range_str.strip()

    # A bare version (no brackets) means "recommended", not a hard bound — Forge accepts anything.
    if not (spec.startswith("[") or spec.startswith("(")):
        return True, "soft requirement"

    # Ranges may be comma-joined sets of intervals; any satisfied interval passes.
    intervals, depth, buf = [], 0, ""
    for ch in spec:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
            buf += ch
            intervals.append(buf.strip())
            buf = ""
            continue
        elif ch == "," and depth == 0:
            continue
        buf += ch
    if buf.strip():
        intervals.append(buf.strip())

    for iv in intervals:
        m = re.match(r"^([\[\(])\s*([^,\]\)]*)\s*(?:,\s*([^,\]\)]*)\s*)?([\]\)])$", iv)
        if not m:
            continue
        lb, lo, hi, ub = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
        if hi is None:                      # single-version interval like [1.2.3]
            if Version(lo) == v:
                return True, f"matches {iv}"
            continue
        hi = hi.strip()
        ok = True
        if lo:
            ok &= (v >= Version(lo)) if lb == "[" else (v > Version(lo))
        if hi:
            ok &= (v <= Version(hi)) if ub == "]" else (v < Version(hi))
        if ok:
            return True, f"satisfies {iv}"
    return False, f"outside {spec}"


# --- mod scanning ---------------------------------------------------------------------------

BUILTIN = {"minecraft", "forge", "neoforge", "fabricloader", "java", "fml", "mcp"}


def manifest_version(z):
    """Forge substitutes ${file.jarVersion} from the jar manifest's Implementation-Version."""
    try:
        text = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
    except Exception:
        return None
    # Manifest values wrap at 72 bytes with a leading space on continuation lines.
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n ", "")
    for line in text.split("\n"):
        if line.lower().startswith("implementation-version:"):
            return line.split(":", 1)[1].strip()
    return None


def scan(mods_dir):
    provided, declared = {}, []

    def read_toml(raw, source):
        try:
            return tomllib.loads(raw.decode("utf-8", "replace").lstrip("﻿"))
        except Exception as e:
            print(f"  ! {source}: TOML parse failed: {e}")
            return None

    def handle(data, source, jarversion):
        if not data:
            return
        deps = data.get("dependencies") or {}
        for mod in data.get("mods", []) or []:
            mid = mod.get("modId")
            if not mid:
                continue
            raw_v = str(mod.get("version", ""))
            if "${file.jarVersion}" in raw_v:
                raw_v = raw_v.replace("${file.jarVersion}", jarversion or "0.0NONE")
            # JarJar resolves duplicates to the HIGHEST version, so keep that one — not the
            # first seen, which is often an older copy nested inside another mod's jar.
            prev = provided.get(mid)
            if prev is None or Version(raw_v) > Version(prev[0]):
                provided[mid] = (raw_v, source)
            for d in deps.get(mid, []) or []:
                mandatory = d.get("mandatory")
                if mandatory is None:
                    mandatory = d.get("type", "required") == "required"
                declared.append({
                    "owner": mid, "dep": d.get("modId"),
                    "range": d.get("versionRange", ""),
                    "mandatory": bool(mandatory), "source": source,
                })

    def walk(fh, source, depth=0):
        try:
            z = zipfile.ZipFile(fh)
        except Exception as e:
            print(f"  ! {source}: not a readable jar: {e}")
            return
        names = set(z.namelist())
        if "META-INF/mods.toml" in names:
            handle(read_toml(z.read("META-INF/mods.toml"), source), source,
                   manifest_version(z))
        if depth < 2:
            for n in names:
                if n.startswith("META-INF/jarjar/") and n.endswith(".jar"):
                    walk(io.BytesIO(z.read(n)), f"{source}!{os.path.basename(n)}", depth + 1)
        z.close()

    for fn in sorted(os.listdir(mods_dir)):
        if fn.endswith(".jar"):
            walk(os.path.join(mods_dir, fn), fn)
    return provided, declared


def main():
    mods_dir = sys.argv[1] if len(sys.argv) > 1 else "mods"
    if not os.path.isdir(mods_dir):
        print(f"no such directory: {mods_dir}")
        return 2

    provided, declared = scan(mods_dir)
    print(f"mod IDs resolved : {len(provided)}")
    print(f"declared deps    : {len(declared)}")

    missing, violations = [], []
    for d in declared:
        dep = d["dep"]
        if not dep or dep.lower() in BUILTIN:
            continue
        if dep not in provided:
            if d["mandatory"]:
                missing.append(d)
            continue                                    # absent + optional = fine
        version, _ = provided[dep]
        ok, why = in_range(version, d["range"])
        if not ok:
            violations.append((d, version, why))

    print()
    print("=" * 74)
    print("MISSING MANDATORY DEPENDENCIES")
    print("=" * 74)
    if missing:
        for d in missing:
            print(f"  !! {d['dep']} required by {d['owner']} {d['range']}  [{d['source']}]")
    else:
        print("  none")

    print()
    print("=" * 74)
    print("VERSION RANGE VIOLATIONS  (installed, but outside the declared range)")
    print("=" * 74)
    if violations:
        for d, version, why in violations:
            kind = "mandatory" if d["mandatory"] else "OPTIONAL"
            print(f"  !! {d['owner']} requires {d['dep']} {d['range']} ({kind})")
            print(f"     installed: {version}  -> {why}")
            print(f"     source   : {d['source']}")
        print()
        print("  Forge halts on these, optional included. An optional dependency may be ABSENT;")
        print("  if present it must still satisfy the range.")
    else:
        print("  none")

    # A jar sitting in mods/ AND quarantine/ means a quarantine decision was undone without
    # the quarantine copy being cleared. That is how journeymap 6.0.4 got back into the load
    # path and re-broke ModSorter (B-27) between two recorded sessions -- the pack stopped
    # booting and nothing said so.
    print()
    print("=" * 74)
    print("QUARANTINE CONFLICTS  (same filename in mods/ and quarantine/)")
    print("=" * 74)
    live = {os.path.basename(p) for p in glob.glob(os.path.join("mods", "*.jar"))}
    held = {os.path.basename(p) for p in glob.glob(os.path.join("quarantine", "*.jar"))}
    conflicts = sorted(live & held)
    for name in conflicts:
        print(f"  !! {name} is in BOTH mods/ and quarantine/")
    if conflicts:
        print()
        print("  A quarantined jar was restored to the load path. Confirm that is intended,")
        print("  then remove the stale quarantine copy so the decision is unambiguous.")
    else:
        print("  none")

    print()
    total = len(missing) + len(violations) + len(conflicts)
    print(f"RESULT: {total} blocking issue(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
