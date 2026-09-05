"""Patch a Continuity Works jar: CW-1, CW-3 and CW-4 -- three world-generation crashes.

All three share a signature -- the pack loads clean, the title screen appears, every
static check passes, and `ChunkGenerator` throws the first time a chunk resolves an
affected biome. None is visible before world creation. They are otherwise unrelated.

CW-1 -- a placed_feature that does not exist
-------------------------------------------
136 of Continuity Works' 146 biome definitions list `minecraft:ore_diamond_medium` in their
UNDERGROUND_ORES step. **That placed_feature does not exist in Minecraft 1.20.1.** Vanilla ships
exactly three diamond ore features -- `ore_diamond`, `ore_diamond_large`, `ore_diamond_buried` --
and all three are already in the list beside it. `ore_diamond_medium` is a spurious fourth entry.

When a datapack biome names a placed_feature that no pack provides, the registry still creates a
`Holder.Reference` for the key but never binds it. Nothing complains at load. The failure comes
later, in `FeatureSorter`, the first time a chunk resolves a biome carrying that holder:

    IllegalStateException: Trying to access unbound value
      'ResourceKey[minecraft:worldgen/placed_feature / minecraft:ore_diamond_medium]'

which is why it surfaced 625 chunks out rather than at spawn, and why it is seed-dependent.

The earlier diagnosis in CONTINUITY_WORKS_DEFECTS.md guessed at code-side holder construction
through `AnthologyBiomeCatalog`. That was wrong. The biomes are ordinary datapack JSON and the
bug is one bad string. Verified: of 5,219 feature references across the 146 biomes, this id is
the only one that resolves against nothing in vanilla, the mod set, or CW itself.

**The fix.** Remove the entry. Do not substitute another feature -- `ore_diamond` and
`ore_diamond_large` are already present, so substituting would double diamond generation.

CW-3 -- feature lists that contradict vanilla's order
----------------------------------------------------
Minecraft does not generate a biome's features in the order that biome lists them. It flattens
every loaded biome into ONE global order per generation step, by topologically sorting the
"A immediately before B" constraints each biome asserts. Continuity Works authors its lists
thematically, and in 67 biomes that order contradicts vanilla's:

    minecraft:badlands            ... sugar_cane_badlands, pumpkin, cactus_decorated
    continuityworks:rocky_badlands ... cactus_decorated, sugar_cane_badlands

No global order satisfies both, so:

    IllegalStateException: Feature order cycle found, involved sources: [...]

Four such cycles exist against a 1.20.1 pack: sugar_cane/pumpkin (41 biomes), the badlands
trio, flower_meadow/patch_grass_plain, and a savanna trio (25 biomes). Measured with
`tools/check_feature_order.py`, which is also how the fix is confirmed.

**The fix.** Sort each affected step into the order the rest of the pack already agrees on,
derived at patch time by topologically sorting every OTHER biome source -- the vanilla client
jar, the other mod jars and our datapack. That reference is acyclic on its own (152 biomes,
0 cycles), so adopting it cannot introduce a new contradiction. Nothing is added or removed:
the same features generate, in a sequence the game can actually honour.

CW-4 -- two biome modifiers add one feature under names that sort inconsistently
-------------------------------------------------------------------------------
A biome's JSON is not its final feature list. Forge applies `forge:add_features` biome modifiers
at runtime and they **append** to the end of a step, in order of **file path** across every mod
(`RegistryDataLoader` reads a TreeMap over `ResourceLocation`, and `ResourceLocation.compareTo`
compares path first, namespace second). Three Continuity Works modifiers therefore interleave:

    anthology_land_topology  -> land/topology       -> #anthology            (128 biomes)
    biome_cave_networks      -> caves/biome_network -> #all_primary_biomes   (all of them)
    foundation_land_topology -> land/topology       -> #templates            (8 biomes)

An anthology biome ends up with `land/topology` BEFORE `caves/biome_network`; a template biome
gets the reverse. Both are asserted, so no global order exists:

    IllegalStateException: Feature order cycle found, involved sources:
      [continuityworks_biomes:ash_wastes, continuityworks_biomes:quarry_megaplex]

Those two biomes' JSON is byte-identical -- which is why a file-only check saw nothing.

**The fix.** Rename both `land/topology` modifiers to a shared `land_topology_` prefix, so they
land adjacent in the global sort and every biome receives the two features in the same order.
Content is untouched; only the entry name, which is the registry key that decides order.
Verified: nothing in the jar -- JSON, class files or metadata -- references either name, and no
other modifier in the pack sorts between the two new names.

The first two edits rewrite the JSON text in place rather than reserialising, so the patched jar
differs from the original only where a defect was. CW-3 permutes the CONTENTS of the existing
string literals and touches no whitespace, so blanking every feature string makes the two files
byte-identical -- which the tool asserts rather than assumes. CW-4 changes no bytes at all.

    python tools/patch_continuity_works.py <in.jar> <out.jar>
    python tools/patch_continuity_works.py <in.jar> <out.jar> --check
"""
import argparse
import glob
import json
import os
import re
import shutil
import sys
import zipfile
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_feature_order as cfo

BAD_FEATURE = 'minecraft:ore_diamond_medium'
BIOME_RE = re.compile(r'^data/[^/]+/worldgen/biome/.+\.json$')

# The jar ships two formattings: 128 biomes pretty-printed one id per line, 8 minified with no
# whitespace at all. The trailing newline is therefore optional -- in the pretty form the match
# swallows the whole line including its indent, in the minified form just the element and comma.
WITH_COMMA = re.compile(
    r'[ \t]*"' + re.escape(BAD_FEATURE) + r'"[ \t]*,[ \t]*(?:\r?\n)?')
AS_LAST = re.compile(
    r',[ \t]*(?:\r?\n)?[ \t]*"' + re.escape(BAD_FEATURE) + r'"')

STRING_RE = re.compile(r'"[^"\\]*"')

# CW-4. Two modifiers add the SAME feature to different biome sets, and their names sort on
# opposite sides of `biome_cave_networks`, which adds a different feature to a set containing
# both. Renaming them to a shared prefix makes them adjacent in the global sort, so every biome
# receives the two features in the same order. Content is not touched; only the entry name, which
# is the registry key that decides application order. Verified: nothing in the jar -- JSON, class
# files or metadata -- references either name.
MODIFIER_RENAMES = {
    'data/continuityworks_biomes/forge/biome_modifier/anthology_land_topology.json':
        'data/continuityworks_biomes/forge/biome_modifier/land_topology_anthology.json',
    'data/continuityworks_biomes/forge/biome_modifier/foundation_land_topology.json':
        'data/continuityworks_biomes/forge/biome_modifier/land_topology_templates.json',
}


# --- CW-1 ----------------------------------------------------------------------------

def features_of(doc):
    return [f for step in doc.get('features', []) or [] for f in step if isinstance(f, str)]


def patch_biome(raw):
    """Return (new_text, removed_count) with the bad feature deleted from the JSON text."""
    if BAD_FEATURE not in raw:
        return raw, 0

    before = json.loads(raw)
    out, n = WITH_COMMA.subn('', raw)
    if BAD_FEATURE in out:
        out, n2 = AS_LAST.subn('', out)
        n += n2
    if BAD_FEATURE in out:
        raise ValueError('bad feature still present after substitution -- unhandled formatting')

    # Prove the edit did exactly one thing: dropped that id, changed nothing else.
    after = json.loads(out)
    b, a = features_of(before), features_of(after)
    if [f for f in b if f != BAD_FEATURE] != a:
        raise ValueError('feature list changed beyond the removal')
    stripped = dict(before)
    stripped.pop('features', None)
    other = dict(after)
    other.pop('features', None)
    if stripped != other:
        raise ValueError('a field outside "features" changed')
    return out, n


# --- CW-3 ----------------------------------------------------------------------------

def canonical_order(exclude_jar):
    """The order the rest of the pack agrees on: {step: {feature: rank}}.

    Built from every biome source EXCEPT the jar being patched, then topologically sorted.
    Raises if that reference is not itself acyclic -- in that case the contradiction is not
    Continuity Works' alone and reordering it would only move the crash."""
    ref = cfo.Sources()
    if not os.path.exists(cfo.CLIENT_JAR):
        raise SystemExit('!! vanilla client jar not found at %s -- cannot derive the '
                         'canonical order without it' % cfo.CLIENT_JAR)
    ref.add_jar(cfo.CLIENT_JAR)
    base = os.path.basename(exclude_jar).lower()
    for j in sorted(glob.glob(os.path.join('mods', '*.jar'))):
        if os.path.basename(j).lower() == base or 'continuityworks' in os.path.basename(j).lower():
            continue
        ref.add_jar(j)
    if os.path.isdir(cfo.DATA):
        ref.add_datapack(cfo.DATA, 'kubejs/data')

    rank, edges, _ = cfo.build_graph(ref)
    cycles = cfo.find_cycles(rank, edges)
    if cycles:
        raise SystemExit('!! the pack contradicts itself even without this jar (%d cycle(s)). '
                         'Run tools/check_feature_order.py and fix that first.' % len(cycles))

    nodes = set(edges) | {b for s in edges.values() for b in s}
    order = {}
    for step in range(len(cfo.STEPS)):
        here = {n for n in nodes if n[0] == step}
        adj = dict((n, set(m for m in edges.get(n, ()) if m[0] == step)) for n in here)
        indeg = defaultdict(int)
        for n in here:
            for m in adj[n]:
                indeg[m] += 1
        ready = sorted([n for n in here if not indeg[n]], key=lambda n: rank[n[1]])
        out = []
        while ready:
            n = ready.pop(0)
            out.append(n[1])
            for m in sorted(adj[n], key=lambda x: rank[x[1]]):
                indeg[m] -= 1
                if not indeg[m]:
                    ready.append(m)
            ready.sort(key=lambda x: rank[x[1]])
        if len(out) != len(here):
            raise SystemExit('!! step %d did not fully order -- reference is not acyclic' % step)
        order[step] = dict((f, i) for i, f in enumerate(out))
    return order, len(ref.biomes)


def _features_spans(raw):
    """Spans of each step array inside the "features" value, in order.

    Walks the raw text rather than reserialising, so every byte outside a feature string
    literal is preserved exactly."""
    key = raw.find('"features"')
    if key < 0:
        return []
    i = raw.index('[', key)
    depth, in_str, esc, spans, start = 0, False, False, [], None
    for j in range(i, len(raw)):
        c = raw[j]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == '[':
            depth += 1
            if depth == 2:
                start = j
        elif c == ']':
            if depth == 2:
                spans.append((start, j + 1))
            depth -= 1
            if depth == 0:
                return spans
    return spans


def reorder_biome(raw, order):
    """Return (new_text, steps_changed, skipped_steps) with each step in canonical order."""
    before = json.loads(raw)
    feats = before.get('features')
    if not isinstance(feats, list):
        return raw, 0, []

    spans = _features_spans(raw)
    if len(spans) != len(feats):
        raise ValueError('found %d step spans for %d steps' % (len(spans), len(feats)))

    out, changed, skipped = raw, 0, []
    # Right to left, so earlier spans keep their offsets.
    for step in range(len(feats) - 1, -1, -1):
        lst = feats[step]
        if not isinstance(lst, list) or len(lst) < 2:
            continue
        if any(not isinstance(f, str) for f in lst):
            continue
        unknown = [f for f in lst if f not in order.get(step, {})]
        if unknown:
            skipped.append((step, unknown))
            continue
        want = sorted(lst, key=order[step].__getitem__)
        if want == lst:
            continue
        s, e = spans[step]
        text = out[s:e]
        lits = list(STRING_RE.finditer(text))
        if len(lits) != len(lst):
            raise ValueError('step %d: %d literals for %d features' % (step, len(lits), len(lst)))
        # Write the permuted ids back into the SAME quote slots: punctuation, indentation and
        # line breaks are untouched, so the only bytes that move are inside the quotes.
        parts, at = [], 0
        for m, new in zip(lits, want):
            parts.append(text[at:m.start()])
            parts.append('"' + new + '"')
            at = m.end()
        parts.append(text[at:])
        out = out[:s] + ''.join(parts) + out[e:]
        changed += 1

    if changed:
        after = json.loads(out)
        for step, lst in enumerate(feats):
            if sorted(after['features'][step]) != sorted(lst):
                raise ValueError('step %d gained or lost a feature' % step)
        b, a = dict(before), dict(after)
        b.pop('features', None)
        a.pop('features', None)
        if b != a:
            raise ValueError('a field outside "features" changed')
        # Structural proof: with every feature string blanked, the two texts are identical.
        if STRING_RE.sub('""', raw) != STRING_RE.sub('""', out):
            raise ValueError('formatting changed outside the string literals')
    return out, changed, skipped


# --- driver --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst', nargs='?')
    ap.add_argument('--check', action='store_true',
                    help='report the defect counts without writing anything')
    a = ap.parse_args()

    if not os.path.exists(a.src):
        print('!! no such jar: %s' % a.src)
        return 2

    with zipfile.ZipFile(a.src) as z:
        infos = z.infolist()
        signed = [i.filename for i in infos
                  if i.filename.upper().startswith('META-INF/')
                  and i.filename.upper().endswith(('.SF', '.RSA', '.DSA', '.EC'))]
        entries = dict((i.filename, z.read(i.filename)) for i in infos if not i.is_dir())

    if signed:
        print('!! jar carries signature files %s -- patching would invalidate them' % signed)
        return 2

    order, ref_biomes = canonical_order(a.src)

    cw1_biomes, cw1_refs = 0, 0
    cw3_biomes, cw3_steps, skipped = 0, 0, []
    patched = {}
    for name, data in entries.items():
        if not BIOME_RE.match(name):
            continue
        raw = data.decode('utf-8')
        text = raw
        if BAD_FEATURE in text:
            text, n = patch_biome(text)
            cw1_biomes += 1
            cw1_refs += n
        text, n2, skip = reorder_biome(text, order)
        if n2:
            cw3_biomes += 1
            cw3_steps += n2
        for s, u in skip:
            skipped.append((name, s, u))
        if text != raw:
            patched[name] = text.encode('utf-8')

    print('jar        : %s' % a.src)
    print('entries    : %d' % len(entries))
    print('biomes     : %d' % sum(1 for n in entries if BIOME_RE.match(n)))
    print('reference  : %d biomes outside this jar, acyclic' % ref_biomes)
    print('CW-1       : %d biome(s), %d reference(s) to %s' % (cw1_biomes, cw1_refs, BAD_FEATURE))
    print('CW-3       : %d biome(s), %d step list(s) reordered' % (cw3_biomes, cw3_steps))

    renames = dict((o, n) for o, n in MODIFIER_RENAMES.items() if o in entries)
    collide = [n for n in renames.values() if n in entries]
    if collide:
        print('!! rename target already exists in the jar: %s' % collide)
        return 2
    print('CW-4       : %d biome modifier(s) renamed for a stable application order'
          % len(renames))
    for o, n in sorted(renames.items()):
        print('             %s -> %s' % (o.split('/')[-1], n.split('/')[-1]))

    if skipped:
        print('  !! %d step(s) left alone -- features the reference never orders:' % len(skipped))
        for n, s, u in skipped[:10]:
            print('     %s step %d: %s' % (n, s, u))

    if a.check or not a.dst:
        if not patched and not renames:
            print('\nNone of CW-1, CW-3 or CW-4 is present in this jar.')
        return 0

    if not patched and not renames:
        print('\nNothing to patch, no jar written.')
        return 0

    # Rewrite the archive, preserving every original entry's metadata and every byte we did not
    # deliberately change.
    tmp = a.dst + '.tmp'
    with zipfile.ZipFile(a.src) as z, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for info in z.infolist():
            if info.is_dir():
                out.writestr(info, b'')
                continue
            data = patched.get(info.filename, entries[info.filename])
            keep = zipfile.ZipInfo(renames.get(info.filename, info.filename),
                                   date_time=info.date_time)
            keep.compress_type = info.compress_type
            keep.external_attr = info.external_attr
            keep.internal_attr = info.internal_attr
            keep.create_system = info.create_system
            out.writestr(keep, data)
    shutil.move(tmp, a.dst)

    # Read the result back and confirm it is what we intended.
    back = dict((n, renames.get(n, n)) for n in entries)     # original name -> expected name
    with zipfile.ZipFile(a.dst) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        if set(names) != set(back.values()):
            print('!! entry set changed beyond the declared renames')
            return 1
        still, unchanged, misordered = 0, 0, 0
        for orig, now in back.items():
            data = z.read(now)
            if BIOME_RE.match(now):
                doc = json.loads(data.decode('utf-8'))
                if BAD_FEATURE in data.decode('utf-8', 'replace'):
                    still += 1
                for step, lst in enumerate(doc.get('features') or []):
                    if not isinstance(lst, list) or len(lst) < 2:
                        continue
                    if any(f not in order.get(step, {}) for f in lst):
                        continue
                    if sorted(lst, key=order[step].__getitem__) != lst:
                        misordered += 1
            if orig not in patched and data != entries[orig]:
                unchanged += 1
        print('\nwrote      : %s' % a.dst)
        print('verify     : %d entries, %d renamed (contents byte-identical), %d still '
              'referencing %s, %d step(s) still out of canonical order, %d unintended byte '
              'changes' % (len(names), len(renames), still, BAD_FEATURE, misordered, unchanged))
        if still or unchanged or misordered:
            return 1
    print('OK -- CW-1 removed, CW-3 reordered, CW-4 renamed, every other entry byte-identical.')
    print('Confirm with: python tools/check_feature_order.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
