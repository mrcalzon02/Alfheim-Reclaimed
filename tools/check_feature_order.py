"""Static pre-check for feature order cycles -- the crash no other checker can see.

Minecraft does not generate a biome's features in the order that biome lists them. It
flattens every loaded biome's list into ONE global order per generation step
(`net.minecraft.world.level.biome.FeatureSorter`), by topologically sorting the pairwise
"A comes before B" constraints each biome asserts. If biome X says `sugar_cane, pumpkin`
and biome Y says `pumpkin, sugar_cane`, no global order exists and the game throws:

    java.lang.IllegalStateException: Feature order cycle found, involved sources: [...]

The trap is *when* it throws. FeatureSorter runs lazily, from `ChunkGenerator`, the first
time a chunk resolves an affected biome -- so the pack loads clean, the title screen
appears, the datapack parses, and the crash lands on world creation. `check_worldgen.py`
resolves ids and cannot see this: the ids are all valid, it is their *sequence* that is
impossible. Only the whole load path together shows it, which is what this does.

  F1  no cycle in the merged feature order, over every biome the pack can load

Sources are read in load order -- vanilla client jar, then mod jars, then our datapack --
so an override is compared in the form the game will actually see.

BIOME MODIFIERS ARE HALF THE PROBLEM
------------------------------------
A biome's JSON is not its final feature list. Forge applies `forge:add_features` biome
modifiers at runtime, and they **append** to the end of a step. Two modifiers that add the
same feature to different biome sets, under names that sort on opposite sides of a third
modifier, hand two biomes contradictory orders **even when their JSON is byte-identical**.

That is not hypothetical: the first version of this checker read only the files, reported
0 cycles, and the very next launch crashed on `continuityworks_biomes:ash_wastes` against
`continuityworks_biomes:quarry_megaplex` -- two biomes whose JSON is identical. Recorded as
CW-4.

Application order matters and is not obvious. Forge loads these through `RegistryDataLoader`,
whose ResourceManager listing is a TreeMap over `ResourceLocation`, and
`ResourceLocation.compareTo` compares **path first, namespace second**. So modifiers apply in
order of file path across every mod -- not grouped by mod, and not by declaration order.

    python tools/check_feature_order.py
    python tools/check_feature_order.py --verbose      # every biome asserting each edge
    python tools/check_feature_order.py --self-test    # prove it fires on a known cycle
"""
import argparse
import glob
import json
import os
import sys
import zipfile
from collections import defaultdict

CLIENT_JAR = (r'C:\Users\Admin\curseforge\minecraft\Install\versions'
              r'\1.20.1\1.20.1.jar')
DATA = os.path.join('kubejs', 'data')

# GenerationStep.Decoration, in order. A biome's feature list is indexed by these.
STEPS = ['raw_generation', 'lakes', 'local_modifications', 'underground_structures',
         'surface_structures', 'strongholds', 'underground_ores', 'underground_decoration',
         'fluid_springs', 'vegetal_decoration', 'top_layer_modification']


def _strip_comments(text):
    """Remove `//` line comments outside string literals.

    Forge parses these files with GSON in lenient mode, so some mods ship commented JSON --
    `irons_spellbooks:necromancer_spawns` does. Python's json is strict, and silently skipping
    such a file would leave a modifier unmodelled and a possible cycle invisible."""
    out, i, in_str, esc = [], 0, False, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif c == '/' and i + 1 < len(text) and text[i + 1] == '/':
            while i < len(text) and text[i] not in '\r\n':
                i += 1
            continue
        else:
            out.append(c)
        i += 1
    return ''.join(out)


def _json(raw):
    text = raw.decode('utf-8-sig')
    try:
        return json.loads(text)
    except ValueError:
        return json.loads(_strip_comments(text))


class Sources:
    """Biomes, tags and biome modifiers, later sources overriding earlier ones."""

    def __init__(self):
        self.biomes = {}      # "ns:path" -> features (list of 11 lists)
        self.origin = {}      # "ns:path" -> where it was read from
        self.tags = defaultdict(list)          # placed_feature tags
        self.biome_tags = defaultdict(list)    # biome tags, for modifier targets
        self.modifiers = {}   # sort key -> (id, doc, where)
        self.unmodelled = []  # modifier types that touch features but we cannot read

    def _take(self, name, raw, where):
        parts = name.split('/')
        if len(parts) >= 5 and parts[0] == 'data' and parts[2:4] == ['worldgen', 'biome']:
            try:
                doc = _json(raw)
            except ValueError:
                return
            if isinstance(doc.get('features'), list):
                bid = parts[1] + ':' + '/'.join(parts[4:])[:-5]
                self.biomes[bid] = doc['features']
                self.origin[bid] = where
        elif len(parts) >= 6 and parts[0] == 'data' and \
                parts[2:5] == ['tags', 'worldgen', 'placed_feature']:
            try:
                doc = _json(raw)
            except ValueError:
                return
            tid = parts[1] + ':' + '/'.join(parts[5:])[:-5]
            self.tags[tid].append(doc)
        elif len(parts) >= 6 and parts[0] == 'data' and \
                parts[2:5] == ['tags', 'worldgen', 'biome']:
            try:
                doc = _json(raw)
            except ValueError:
                return
            tid = parts[1] + ':' + '/'.join(parts[5:])[:-5]
            self.biome_tags[tid].append(doc)
        elif len(parts) >= 5 and parts[0] == 'data' and \
                parts[2:4] == ['forge', 'biome_modifier']:
            # Forge loads these through RegistryDataLoader, whose ResourceManager listing is a
            # TreeMap over ResourceLocation -- and ResourceLocation.compareTo compares PATH
            # first, namespace second. So the application order is by file path, across
            # namespaces, not by mod. Key on exactly that.
            path = '/'.join(parts[2:])
            mid = parts[1] + ':' + '/'.join(parts[4:])[:-5]
            try:
                doc = _json(raw)
            except ValueError:
                # Some mods ship JSON5-ish modifier files. Only spawn modifiers have done so
                # here, but record it rather than pretend the file was read.
                self.unmodelled.append((mid, 'unparseable JSON', where))
                return
            self.modifiers[(path, parts[1])] = (mid, doc, where)

    def add_jar(self, path):
        try:
            z = zipfile.ZipFile(path)
        except (OSError, zipfile.BadZipFile):
            return False
        for n in z.namelist():
            if n.endswith('.json'):
                self._take(n, z.read(n), os.path.basename(path))
        return True

    def add_datapack(self, root, where):
        for f in glob.glob(os.path.join(root, '**', '*.json'), recursive=True):
            rel = 'data/' + os.path.relpath(f, root).replace('\\', '/')
            with open(f, 'rb') as fh:
                self._take(rel, fh.read(), where)

    def resolve(self, entry, seen=None):
        """One biome feature entry -> the placed_feature ids it stands for."""
        seen = set() if seen is None else seen
        if isinstance(entry, list):
            return [i for e in entry for i in self.resolve(e, seen)]
        if not isinstance(entry, str):
            return []
        if not entry.startswith('#'):
            return [entry]
        tid = entry[1:]
        if tid in seen:
            return []
        seen.add(tid)
        out = []
        for doc in self.tags.get(tid, []):
            for v in doc.get('values', []):
                if isinstance(v, dict):
                    v = v.get('id')
                out.extend(self.resolve(v, seen))
        return out

    def biomes_in(self, spec, seen=None):
        """A modifier's `biomes` value -> the set of biome ids it targets."""
        seen = set() if seen is None else seen
        if isinstance(spec, list):
            out = set()
            for e in spec:
                out |= self.biomes_in(e, seen)
            return out
        if not isinstance(spec, str):
            return set()
        if not spec.startswith('#'):
            return {spec}
        tid = spec[1:]
        if tid in seen:
            return set()
        seen.add(tid)
        acc = []
        for doc in self.biome_tags.get(tid, []):
            if doc.get('replace'):
                acc = []
            acc.extend(doc.get('values', []))
        out = set()
        for v in acc:
            if isinstance(v, dict):
                v = v.get('id')
            if isinstance(v, str):
                out |= self.biomes_in(v, seen)
        return out

    def apply_modifiers(self):
        """Apply Forge biome modifiers the way the game does, before the sort runs.

        This is the half that a file-only reading misses, and it is where the second wave of
        cycles came from. `forge:add_features` APPENDS to the end of a step's list at runtime,
        so two modifiers adding the same feature to different biome sets, under names that sort
        on opposite sides of a third modifier, hand two biomes contradictory orders even when
        their JSON is byte-identical. That is exactly CW-4.

        Returns (applied, touched) counts."""
        applied = touched = 0
        for key in sorted(self.modifiers):
            mid, doc, where = self.modifiers[key]
            kind = doc.get('type')
            if kind == 'forge:add_features':
                targets, feats, steps = doc.get('biomes'), doc.get('features'), doc.get('step')
                remove = False
            elif kind == 'farmersdelight:add_features_by_filter':
                targets, feats, steps = doc.get('allowed_biomes'), doc.get('features'), doc.get('step')
                remove = False
            elif kind == 'forge:remove_features':
                targets, feats = doc.get('biomes'), doc.get('features')
                steps = doc.get('steps', list(STEPS))
                remove = True
            else:
                if kind and 'feature' in str(kind):
                    self.unmodelled.append((mid, kind, where))
                continue

            if isinstance(steps, str):
                steps = [steps]
            idxs = [STEPS.index(s) for s in steps if s in STEPS]
            ids = self.resolve(feats)
            if not idxs or not ids:
                continue
            denied = self.biomes_in(doc.get('denied_biomes')) if 'denied_biomes' in doc else set()
            hit = self.biomes_in(targets) - denied
            applied += 1
            for bid in hit:
                feature_lists = self.biomes.get(bid)
                if feature_lists is None:
                    continue
                while len(feature_lists) <= max(idxs):
                    feature_lists.append([])
                for i in idxs:
                    if not isinstance(feature_lists[i], list):
                        continue
                    if remove:
                        feature_lists[i] = [f for f in feature_lists[i] if f not in ids]
                    else:
                        feature_lists[i] = list(feature_lists[i]) + list(ids)
                    touched += 1
        return applied, touched


def build_graph(src):
    """Reproduce FeatureSorter's constraint graph. Edges join CONSECUTIVE entries in each
    biome's flattened list, exactly as `buildFeaturesPerStep` does -- which is why a cycle
    can only form inside one step, and why two biomes have to disagree about an ADJACENT
    pair to cause one."""
    rank = {}
    edges = defaultdict(set)
    asserted_by = defaultdict(set)

    for bid in sorted(src.biomes):
        flat = []
        for step, entries in enumerate(src.biomes[bid]):
            if not isinstance(entries, list):
                entries = [entries]
            for e in entries:
                for pf in src.resolve(e):
                    rank.setdefault(pf, len(rank))
                    flat.append((step, pf))
        for i in range(len(flat) - 1):
            a, b = flat[i], flat[i + 1]
            if a == b:
                continue
            edges[a].add(b)
            asserted_by[(a, b)].add(bid)
    return rank, edges, asserted_by


def find_cycles(rank, edges):
    nodes = set(edges) | {b for s in edges.values() for b in s}

    def key(n):
        return (n[0], rank[n[1]])

    colour = defaultdict(int)          # 0 unvisited, 1 on stack, 2 done
    stack, out, seen = [], [], set()

    def walk(u):
        colour[u] = 1
        stack.append(u)
        for v in sorted(edges.get(u, ()), key=key):
            if colour[v] == 1:
                cyc = stack[stack.index(v):]
                sig = frozenset(cyc)
                if sig not in seen:
                    seen.add(sig)
                    out.append(cyc + [v])
            elif colour[v] == 0:
                walk(v)
        stack.pop()
        colour[u] = 2

    sys.setrecursionlimit(max(10000, len(nodes) * 4))
    for n in sorted(nodes, key=key):
        if colour[n] == 0:
            walk(n)
    return out


def report(src, cycles, asserted_by, verbose):
    for cyc in cycles:
        step = cyc[0][0]
        print('\n  F1  feature order cycle in step %d (%s)'
              % (step, STEPS[step] if step < len(STEPS) else '?'))
        for i in range(len(cyc) - 1):
            a, b = cyc[i], cyc[i + 1]
            who = sorted(asserted_by[(a, b)])
            by_ns = defaultdict(int)
            for bid in who:
                by_ns[bid.split(':', 1)[0]] += 1
            spread = ', '.join('%s x%d' % (n, c) for n, c in
                               sorted(by_ns.items(), key=lambda kv: -kv[1]))
            print('        %s' % a[1])
            print('          must precede %s' % b[1])
            print('          asserted by %d biome(s): %s' % (len(who), spread))
            if verbose:
                for bid in who:
                    print('            %s   [%s]' % (bid, src.origin.get(bid, '?')))
            else:
                print('          e.g. %s   [%s]' % (who[0], src.origin.get(who[0], '?')))
        print('        -> no global order exists; world generation throws on the first')
        print('           chunk that resolves either biome.')


SELF_TEST = {
    'test:one': [[] for _ in range(9)] + [['minecraft:a', 'minecraft:b'], []],
    'test:two': [[] for _ in range(9)] + [['minecraft:b', 'minecraft:a'], []],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()

    if a.self_test:
        src = Sources()
        src.biomes.update(SELF_TEST)
        src.origin.update(dict((k, 'synthetic') for k in SELF_TEST))
        rank, edges, asserted = build_graph(src)
        cycles = find_cycles(rank, edges)
        print('self-test: 2 synthetic biomes, %d cycle(s) detected' % len(cycles))
        report(src, cycles, asserted, True)
        ok = len(cycles) == 1
        print('\nRESULT: self-test %s -- the checker %s on a known cycle'
              % ('PASSED' if ok else 'FAILED', 'fires' if ok else 'does NOT fire'))
        return 0 if ok else 1

    src = Sources()
    if os.path.exists(CLIENT_JAR):
        src.add_jar(CLIENT_JAR)
        print('  vanilla client jar   %s' % CLIENT_JAR)
    else:
        print('  !! client jar not found at %s -- vanilla biomes NOT checked' % CLIENT_JAR)
    jars = sorted(glob.glob(os.path.join('mods', '*.jar')))
    for j in jars:
        src.add_jar(j)
    print('  mod jars             %d' % len(jars))
    if os.path.isdir(DATA):
        src.add_datapack(DATA, 'kubejs/data')
        print('  instance datapack    %s' % DATA)

    by_ns = defaultdict(int)
    for bid in src.biomes:
        by_ns[bid.split(':', 1)[0]] += 1
    print('\nbiomes in the load path: %d across %d namespace(s)'
          % (len(src.biomes), len(by_ns)))
    if a.verbose:
        for ns, n in sorted(by_ns.items(), key=lambda kv: -kv[1]):
            print('    %-34s %4d' % (ns, n))

    applied, touched = src.apply_modifiers()
    print('biome modifiers:         %d of %d add or remove features, %d biome-step(s) changed'
          % (applied, len(src.modifiers), touched))
    if src.unmodelled:
        print('  !! %d modifier(s) could not be modelled -- a cycle involving these is invisible:'
              % len(src.unmodelled))
        for mid, kind, where in src.unmodelled:
            print('     %s  (%s)  [%s]' % (mid, kind, where))

    rank, edges, asserted = build_graph(src)
    print('ordering constraints:    %d edges over %d placed features'
          % (sum(len(v) for v in edges.values()), len(rank)))

    cycles = find_cycles(rank, edges)
    if cycles:
        report(src, cycles, asserted, a.verbose)

    print('\n' + '=' * 68)
    print('RESULT: %d feature order cycle(s)' % len(cycles))
    return 1 if cycles else 0


if __name__ == '__main__':
    raise SystemExit(main())
