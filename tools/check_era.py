"""Check that one era's quests, items and recipes line up before moving to the next era.

Builds the set of every item id the pack can actually produce -- from every mod's lang file,
the vanilla client jar, and this pack's own KubeJS registrations -- then holds each era to
the invariants that decide whether it is playable:

  E1  every item named by a quest task or reward is registered somewhere
  E2  every item named by the era's recipe scripts is registered somewhere
  E3  every alfheim: item the era needs is PRODUCED by some recipe (obtainability)
  E4  nothing is required before the era that makes it (cross-era ordering)
  E5  a recipe filed as a "use" for an item actually consumes that item
  E6  no two recipes share an id
  E7  no recipe is emitted twice with identical type, inputs and outputs
  E8  no recipe turns an item into more of itself (duplication exploit)
  E9  quest ids are unique and every dependency resolves inside the chapter
  E10 every manifest item is registered and has a model and a texture

Existence alone is not playability: E1/E2 were the whole of the previous version of this
tool, and they pass on a pack whose custom items no recipe can make.

    python tools/check_era.py 1
    python tools/check_era.py --all
"""
import argparse
import ast
import glob
import json
import os
import re
import sys
import zipfile

CLIENT_JAR = (r'C:\Users\Admin\curseforge\minecraft\Install\versions'
              r'\1.20.1\1.20.1.jar')
NS = 'alfheim'
SCRIPTS = os.path.join('kubejs', 'server_scripts')
MANIFEST = os.path.join('tools', 'items_manifest.json')

# Keys whose values name a recipe serialiser, a tag or a recipe group -- never an item.
# `fluid` and `fluidTag` name FLUIDS, which live in their own registry. Without them a
# Create mixing recipe's `fluid: 'minecraft:water'` is read as an item id, and E2/E12 report
# minecraft:water as an unregistered item -- true of the item registry, irrelevant to the
# recipe, and the fix is to stop asking the wrong registry.
NON_ITEM_KEYS = ('type', 'tag', 'category', 'group', 'recipe_type', 'fluid', 'fluidTag')

# Smallest jar sample from which E10 will assert an ingredient-count invariant. See the
# note in check_schemas: below this, unanimity is coincidence rather than evidence.
MIN_ARITY_SAMPLE = 20

ITEM_RE = re.compile(r'^[a-z0-9_]+:[a-z0-9_./-]+$')
COUNT_PREFIX = re.compile(r'^\d+x\s+')


# --------------------------------------------------------------------------- id universe

def scan_jars(type_namespaces=(), verbose=True):
    """One pass over the jars for everything the static checks need.

    Returns (item ids, recipe ids, tag ids, recipe serialiser types). Recipe and tag ids come
    from file names, which is cheap; serialiser types need the file contents, so only the
    namespaces we actually reference are read.
    """
    ids, recipes, tags, types = set(), set(), set(), set()

    def take(lang_bytes):
        try:
            d = json.loads(lang_bytes.decode('utf-8', 'replace'))
        except Exception:
            return
        for k in d:
            parts = k.split('.', 2)
            if len(parts) == 3 and parts[0] in ('item', 'block'):
                ids.add(f'{parts[1]}:{parts[2]}')

    if os.path.exists(CLIENT_JAR):
        with zipfile.ZipFile(CLIENT_JAR) as z:
            for e in z.namelist():
                if e.endswith('assets/minecraft/lang/en_us.json'):
                    take(z.read(e))
    elif verbose:
        print(f'  ! vanilla client jar not found at {CLIENT_JAR} -- vanilla ids unverified')

    want = set(type_namespaces)
    for jar in sorted(glob.glob(os.path.join('mods', '*.jar'))):
        try:
            z = zipfile.ZipFile(jar)
        except Exception:
            continue
        with z:
            for e in z.namelist():
                if re.match(r'assets/[^/]+/lang/en_us\.json$', e):
                    take(z.read(e))
                    continue
                m = re.match(r'data/([^/]+)/recipes?/(.+)\.json$', e)
                if m:
                    recipes.add(f'{m.group(1)}:{m.group(2)}')
                    if m.group(1) in want:
                        for mm in re.finditer(rb'"type"\s*:\s*"([^"]+)"', z.read(e)):
                            types.add(mm.group(1).decode('utf-8', 'replace'))
                    continue
                m = re.match(r'data/([^/]+)/tags/(?:items?|blocks?)/(.+)\.json$', e)
                if m:
                    tags.add(f'{m.group(1)}:{m.group(2)}')

    for it in manifest_items():
        ids.add(f"{NS}:{it['id']}")
    ids |= our_registrations()

    # A dumped registry, when we have one, is GROUND TRUTH and replaces the lang-derived set
    # entirely. Lang keys are translations, not registrations: Mine and Slash ships
    # `item.mmorpg.map` and registers no `mmorpg:map`, and its real ids are slash-pathed
    # (`mmorpg:currency/chaos_orb`). Eleven recipes were rejected at load while every static
    # check reported them fine, because every static check was reading translations.
    real = registry_items()
    if real:
        ids = real | {i for i in ids if i.startswith(NS + ':')}
    return ids, recipes, tags, types


def load_ids(verbose=True):
    """Item/block ids only. Kept for callers that do not need the rest of the scan."""
    return scan_jars(verbose=verbose)[0]


def manifest_items():
    if not os.path.exists(MANIFEST):
        return []
    try:
        return json.load(open(MANIFEST, encoding='utf-8'))['items']
    except Exception as e:
        print(f'  ! items_manifest.json unreadable: {e}')
        return []


def check_all_script_items(all_recipes, ids, problems):
    """E12 -- every item named by ANY recipe script must be registered.

    E2 only inspects era-scoped scripts (`*_eraN_*.js`), so 14_mmo_bridge.js, 12_rites.js,
    30_item_uses.js and the gate scripts were never id-checked at all. Eleven bridge recipes
    referenced Mine and Slash items that do not exist -- `mmorpg:chaos_orb` where the registry
    says `mmorpg:currency/chaos_orb` -- and were rejected at every single load while this tool
    reported zero problems.

    Runs against the dumped registry, so it is checking registrations rather than translations.
    """
    bad = {}
    for r in all_recipes:
        if r['method'] == 'remove':
            continue
        for i in r['inputs'] + r['outputs']:
            if i not in ids:
                bad.setdefault(i, set()).add(r['file'])
    for i, files in sorted(bad.items()):
        problems.append(('global', 'E12',
                         f'{i} is named by {", ".join(sorted(files))} but is not registered'))
        print(f'  E12  {problems[-1][2]}')
    print(f'  --   {len({i for r in all_recipes for i in r["inputs"] + r["outputs"]})} '
          'distinct item id(s) across all recipe scripts checked')


def _code_strings(path):
    """Every string literal in a module EXCEPT its docstrings.

    A generator writes a file by naming it in code -- os.path.join(OUT, 'chapter_groups.snbt').
    A generator that merely says which OTHER generator owns that file names it in prose. The
    first version of this guard separated the two by asking whether the line started with '#',
    which is true of a comment and false of every line of a docstring: gen_cartographer.py's
    header says, correctly, that it does not touch chapter_groups.snbt, and was reported as a
    second writer for saying so.

    Parsing is the precise version of that distinction, and it is not the weaker one -- a
    filename in a non-docstring literal still counts, which is exactly the case E11 exists to
    catch.
    """
    tree = ast.parse(open(path, encoding='utf-8').read())
    docs = set()
    for node in ast.walk(tree):
        body = getattr(node, 'body', None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))                 and body and isinstance(body[0], ast.Expr)                 and isinstance(body[0].value, ast.Constant)                 and isinstance(body[0].value.value, str):
            docs.add(id(body[0].value))
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]


def single_writer_guard(problems):
    """E11 -- exactly one generator may write each shared FTB Quests file.

    chapter_groups.snbt declares BOTH chapter groups, so a generator that writes it while
    knowing only its own group silently deletes the other one. This has now happened twice:
    once in gen_quests.py, once in gen_quests_bulk.py, and the second copy survived a fix to
    the first because nothing checked for it. It only surfaced when a reproducibility run
    happened to execute the generators in a different order.

    Cheaper to assert than to rediscover.
    """
    shared = {'chapter_groups.snbt': 'gen_compendium.py'}
    for fname, owner in shared.items():
        writers = []
        for p in sorted(glob.glob(os.path.join('tools', 'gen_*.py'))):
            if any(fname in lit for lit in _code_strings(p)):
                writers.append(os.path.basename(p))
        extra = [w for w in writers if w != owner]
        if extra:
            problems.append(('global', 'E11',
                             f'{fname} is owned by {owner} but also written by '
                             f'{", ".join(extra)} -- whichever runs last wins, and the '
                             'loser chapter groups vanish'))
            print(f'  E11  {problems[-1][2]}')


def registry_items():
    """Item ids dumped from a running server, if a dump exists.

    tools/registry_items.json is written from `/kubejs export` (see tools/run_server.py). It is
    the only source here that reflects what the game actually registered.
    """
    p = os.path.join('tools', 'registry_items.json')
    if not os.path.exists(p):
        return set()
    try:
        return set(json.load(open(p, encoding='utf-8'))['ids'])
    except Exception as e:
        print(f'  ! registry_items.json unreadable: {e}')
        return set()


def our_registrations():
    """Everything the pack itself registers, read from the registrations rather than a manifest.

    items_manifest.json holds the 80 tier-ladder intermediates and nothing else, so blooms,
    crystals, grove woods and the sealed gate -- 153 `event.create` calls across the startup
    scripts -- were invisible to every id check. That produced false E1s on our own items the
    moment a quest named one, which is exactly backwards: the pack's own content should be the
    part the checker is surest about.

    Reading the `event.create` calls rather than the three extra manifests means one source,
    and it cannot drift from what the game actually registers.

    Our own resource-pack lang files count too: quest_giver ships `quest_scroll` with no lang
    entry of its own, so the name we supply in kubejs/assets is the only thing that makes it a
    named item in game.
    """
    ids = set()
    for p in sorted(glob.glob(os.path.join('kubejs', 'startup_scripts', '*.js'))):
        txt = open(p, encoding='utf-8').read()
        for m in re.finditer(r"""event\.create\(\s*['"]([a-z0-9_]+:[a-z0-9_/.]+)['"]""", txt):
            ids.add(m.group(1))

        # A FLUID registration creates more than the fluid. KubeJS's FluidBuilder also builds a
        # FluidBlockBuilder and a FluidBucketItemBuilder, so `event.create('alfheim:x')` inside
        # a fluid registry yields alfheim:x, alfheim:x_bucket and the fluid block -- none of
        # which appear as their own event.create call. Without this, E12 reports the bucket as
        # unregistered the moment a recipe names it, which is a false positive on our own fluid.
        for blk in re.finditer(
                r"""StartupEvents\.registry\(\s*['"]fluid['"](?:.|
)*?
\}\)""", txt):
            for m in re.finditer(
                    r"""event\.create\(\s*['"]([a-z0-9_]+:[a-z0-9_/.]+)['"]""", blk.group(0)):
                ids.add(m.group(1))
                ids.add(m.group(1) + '_bucket')
    for p in sorted(glob.glob(os.path.join('kubejs', 'assets', '*', 'lang', '*.json'))):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        for k in d:
            parts = k.split('.', 2)
            if len(parts) == 3 and parts[0] in ('item', 'block'):
                ids.add(f'{parts[1]}:{parts[2]}')
    return ids


def world_sourced():
    """Items obtained from the world rather than from a recipe.

    E3 asks whether anything produces an item. A raw bloom is mined out of stone: no recipe
    makes one and none should. Without this, every worldgen material a quest names reads as
    unobtainable, and the honest fix is to teach the checker the other way of getting things
    rather than to author a fake recipe to satisfy it.

    `addSimpleBlock(block, item)` in a blockLootTables handler is the pack's standard ore
    contract, so it is the pattern read here.

    A FLUID'S BUCKET is world-sourced in exactly the same sense and for the same reason. You
    fill a bucket from a pool; there is no recipe and there should not be one. E3 reported
    `alfheim:liquid_bifrost_bucket` as unobtainable the moment a recipe consumed it, which is
    the checker being right about the pattern and wrong about the world -- the honest fix is to
    teach it the other way of getting things, not to author a fake recipe to satisfy it.

    Read from the STARTUP scripts, since that is where fluids are registered.
    """
    ids = set()
    for p in sorted(glob.glob(os.path.join('kubejs', 'startup_scripts', '*.js'))):
        txt = open(p, encoding='utf-8').read()
        for blk in re.finditer(
                r"""StartupEvents\.registry\(\s*['"]fluid['"](?:.|
)*?
\}\)""", txt):
            for m in re.finditer(
                    r"""event\.create\(\s*['"]([a-z0-9_]+:[a-z0-9_/.]+)['"]""", blk.group(0)):
                ids.add(m.group(1) + '_bucket')
    for p in sorted(glob.glob(os.path.join(SCRIPTS, '*.js'))):
        txt = open(p, encoding='utf-8').read()
        for m in re.finditer(
                r"""addSimpleBlock\(\s*['"][^'"]+['"]\s*,\s*['"]([a-z0-9_]+:[a-z0-9_/.]+)['"]""",
                txt):
            ids.add(m.group(1))
        for m in re.finditer(r"""addBlock\(\s*['"][^'"]+['"]\s*,\s*['"]([a-z0-9_]+:[a-z0-9_/.]+)['"]""",
                             txt):
            ids.add(m.group(1))
    return ids


# --------------------------------------------------------------------------- JS parsing

def _balanced(txt, open_at):
    """Index of the bracket closing the one at open_at, string-aware."""
    depth = 0
    i = open_at
    quote = None
    while i < len(txt):
        c = txt[i]
        if quote:
            if c == '\\':
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in '\'"`':
            quote = c
        elif c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(txt) - 1


def _strings(txt):
    return [m.group(1) for m in re.finditer(r"""['"]([^'"\n]*)['"]""", txt)]


def _non_item_values(body):
    """Values of keys that name serialisers, tags or groups rather than items."""
    out = set()
    for key in NON_ITEM_KEYS:
        for m in re.finditer(key + r"""\s*:\s*['"]([^'"]+)['"]""", body):
            out.add(m.group(1))
    return out


def _value_after(body, key):
    """Text of the value assigned to `key`, whether object, array or string."""
    out = []
    for m in re.finditer(r'\b' + key + r'\s*:\s*', body):
        j = m.end()
        while j < len(body) and body[j] in ' \n\t':
            j += 1
        if j >= len(body):
            continue
        if body[j] in '{[':
            out.append(body[j:_balanced(body, j) + 1])
        elif body[j] in '\'"':
            try:
                k = body.index(body[j], j + 1)
            except ValueError:
                continue
            out.append(body[j:k + 1])
    return out


def _top_keys(body):
    """Keys assigned at the top level of a recipe literal, ignoring nested objects.

    `sequence:` in a Create sequenced assembly holds sub-recipes with their own
    `ingredients`/`results`; counting those as top-level keys would make the outer
    recipe look like it had fields it does not.
    """
    # parse_recipes hands us the whole argument list of event.custom(...), so the recipe
    # object still wears its own braces and every real key sits one level in. Unwrap them,
    # or a depth-0 scan finds nothing and every recipe looks like it is missing every field.
    body = body.strip()
    if body.startswith('{') and body.endswith('}'):
        body = body[1:-1]

    keys, depth, i = set(), 0, 0
    while i < len(body):
        c = body[i]
        if c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
        elif c in '\'"':
            j = i + 1
            while j < len(body) and body[j] != c:
                j += 2 if body[j] == '\\' else 1
            i = j
        elif depth == 0:
            m = re.match(r'([A-Za-z_]\w*)\s*:', body[i:])
            if m:
                keys.add(m.group(1))
                i += m.end() - 1
        i += 1
    return keys


def _list_arity(body, key):
    """How many entries the list assigned to `key` holds, or None if it is not a list.

    Counts entries at the list's own depth, so a nested object counts once.
    """
    for chunk in _value_after(body, key):
        if not chunk.startswith('['):
            continue
        inner, depth, n, i = chunk[1:-1], 0, 0, 0
        started = False
        while i < len(inner):
            c = inner[i]
            if c in '{[':
                if depth == 0:
                    n += 1
                    started = True
                depth += 1
            elif c in '}]':
                depth -= 1
            elif c in '\'"':
                if depth == 0 and not started:
                    n += 1
                j = i + 1
                while j < len(inner) and inner[j] != c:
                    j += 2 if inner[j] == '\\' else 1
                i = j
            elif c == ',' and depth == 0:
                started = False
            i += 1
        return n
    return None


def jar_schemas(types_wanted, verbose=True):
    """Profile each recipe type against the shipping recipes that define it.

    B-41: eleven of our recipes were rejected at load while every static check reported
    zero problems, because the checks proved that ids exist and never proved that a
    recipe had the shape its serialiser demands. Guessing a schema is how that happened,
    so nothing here is guessed. For each type we emit, the mod's own recipes are read out
    of its jar and reduced to: keys present in every one of them (mandatory), keys present
    in any of them (permitted), and the ingredient-list lengths actually observed.

    A type the jars do not define -- ours, or one only ever created by script -- yields no
    profile and is skipped rather than guessed at.
    """
    want_ns = {t.split(':')[0] for t in types_wanted}
    prof = {t: {'n': 0, 'always': None, 'ever': set(), 'arity': set()} for t in types_wanted}
    for jar in sorted(glob.glob(os.path.join('mods', '*.jar'))):
        try:
            z = zipfile.ZipFile(jar)
        except Exception:
            continue
        with z:
            for e in z.namelist():
                m = re.match(r'data/([^/]+)/recipes?/(.+)\.json$', e)
                if not m or m.group(1) not in want_ns:
                    continue
                try:
                    d = json.loads(z.read(e))
                except Exception:
                    continue
                t = d.get('type')
                if t not in prof or not isinstance(d, dict):
                    continue
                p = prof[t]
                p['n'] += 1
                keys = set(d) - {'conditions'}
                p['always'] = keys if p['always'] is None else (p['always'] & keys)
                p['ever'] |= keys
                for k in ('ingredients', 'input', 'inputs'):
                    if isinstance(d.get(k), list):
                        p['arity'].add(len(d[k]))
                        break
    live = {t: p for t, p in prof.items() if p['n']}
    if verbose:
        print(f'recipe schemas profiled from jars: {len(live)} of {len(types_wanted)} type(s)')
    return live


def check_schemas(all_recipes, schemas, problems):
    """E10 -- our recipe literals must match the shape their serialiser demands."""
    def fail(code, msg):
        problems.append(('schema', code, msg))
        print(f'  {code}  {msg}')

    checked = 0
    for r in all_recipes:
        p = schemas.get(r['type'])
        if not p or r['method'] != 'custom' or not r.get('body'):
            continue
        checked += 1
        ours = _top_keys(r['body'])
        where = f'{r["id"] or "(no id)"} ({r["file"]})'

        for k in sorted(p['always'] - ours):
            fail('E10', f'{where}: {r["type"]} requires "{k}", which this recipe does not set '
                        f'({p["n"]} shipping recipe(s) all set it)')
        for k in sorted(ours - p['ever'] - {'type'}):
            fail('E10', f'{where}: {r["type"]} has no "{k}" field -- '
                        f'no shipping recipe of this type uses it')
        # Arity is asserted only from a sample big enough to mean something. A profile is
        # evidence about what shipping recipes DO, not a reading of the serialiser, and the
        # two part company on small samples: MythicBotany ships 2 infuser recipes and both
        # take 3 ingredients, but our own working Rites recipes take 4. Botania ships
        # exactly 1 terra_plate recipe. Neither is an invariant. The observed counts fall
        # into two clean groups -- 1, 2 (speculative) and 22+ (unanimous across a real
        # sample) -- so the floor sits in the gap, and it still keeps every arity rule the
        # game actually enforced on us at load: milling 231, pressing 39, deploying 112.
        if len(p['arity']) == 1 and p['n'] >= MIN_ARITY_SAMPLE:
            want = next(iter(p['arity']))
            for k in ('ingredients', 'input', 'inputs'):
                if k not in ours:
                    continue
                got = _list_arity(r['body'], k)
                if got is not None and got != want:
                    fail('E10', f'{where}: {r["type"]} takes exactly {want} ingredient(s), '
                                f'this recipe gives {got}')
                break
    print(f'  --   {checked} recipe(s) checked against a jar-derived schema')


def _items_in(txt, exclude):
    found = []
    for s in _strings(txt):
        s = COUNT_PREFIX.sub('', s.strip())
        if s.startswith('#') or s in exclude:
            continue
        if ITEM_RE.match(s):
            found.append(s)
    return found


def parse_recipes(path):
    """Every recipe a script emits: id, method, type, outputs, inputs."""
    txt = open(path, encoding='utf-8').read()
    prefix = ''
    m = re.search(r'const\s+id\s*=\s*\w+\s*=>\s*`([^`]*)\$\{\w+\}`', txt)
    if m:
        prefix = m.group(1)

    out = []
    for m in re.finditer(r'event\.(\w+)\s*\(', txt):
        method = m.group(1)
        open_at = m.end() - 1
        close_at = _balanced(txt, open_at)
        body = txt[open_at + 1:close_at]
        tail = txt[close_at:close_at + 240]

        # The .id(...) must chain directly off THIS call. Searching the whole tail let an
        # event.remove({...}) -- which has no .id() -- adopt the id of the next recipe.
        rid = None
        mi = re.match(r"\s*\)?\s*\.id\(\s*id\(\s*['\"]([^'\"]+)['\"]", tail)
        if mi:
            rid = prefix + mi.group(1)
        else:
            mi = re.match(r"\s*\)?\s*\.id\(\s*['\"]([^'\"]+)['\"]", tail)
            if mi:
                rid = mi.group(1)

        non_item = _non_item_values(body)
        rtype = None
        mt = re.search(r"""\btype\s*:\s*['"]([^'"]+)['"]""", body)
        if mt:
            rtype = mt.group(1)

        outputs, inputs = [], []
        if method in ('shaped', 'shapeless', 'smelting', 'blasting', 'smoking'):
            first = _strings(body)
            if first:
                cand = COUNT_PREFIX.sub('', first[0].strip())
                if ITEM_RE.match(cand):
                    outputs.append(cand)
            rest = body[body.find(',') + 1:] if ',' in body else ''
            inputs = _items_in(rest, non_item)
        elif method == 'custom':
            for key in ('output', 'result', 'results'):
                for chunk in _value_after(body, key):
                    outputs.extend(_items_in(chunk, non_item))
            consumed = body
            for key in ('output', 'result', 'results'):
                for chunk in _value_after(body, key):
                    consumed = consumed.replace(chunk, ' ')
            inputs = _items_in(consumed, non_item)
        elif method == 'remove':
            pass
        else:
            continue

        # Tags named either as a bare '#ns:path' ingredient or as tag: 'ns:path'.
        tags = {s[1:] for s in _strings(body) if s.startswith('#')}
        for mm in re.finditer(r"""\btag\s*:\s*['"]([^'"#]+)['"]""", body):
            tags.add(mm.group(1))

        # What an event.remove targets. A remove that matches nothing is silent, and leaves
        # the route it was meant to close wide open.
        removes = None
        if method == 'remove':
            mr = re.search(r"""\bid\s*:\s*['"]([^'"]+)['"]""", body)
            if mr:
                removes = mr.group(1)

        out.append({
            'file': os.path.basename(path),
            'id': rid,
            'method': method,
            'type': rtype,
            'outputs': outputs,
            'inputs': inputs,
            'tags': sorted(tags),
            'removes': removes,
            'body': body,
        })
    return out


# --------------------------------------------------------------------------- quests

def lines_with_depth(text):
    """(depth at the start of the line, line), counting braces outside string literals.

    Cheap structural awareness, which this parser needs because these files are not ours to
    format. FTB Quests rewrites `config/ftbquests/` whenever a world loads: it reorders every
    object's keys ALPHABETICALLY and expands minified objects across lines. Anything that assumes
    a field order, or that a task and its parent quest can be told apart by indentation, silently
    stops working the first time the game is launched."""
    depth, in_str, esc = 0, False, False
    for line in text.split('\n'):
        start_depth = depth
        for c in line:
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
            elif c in '{[':
                depth += 1
            elif c in '}]':
                depth -= 1
        yield start_depth, line


def parse_chapter(path):
    """Quest records with ids, dependencies and every item/entity they name.

    A quest is one brace-balanced object directly inside `quests: [`. `id` and `title` are read
    only at the quest's OWN top level, so a task's `title:` or a reward's `id:` cannot be mistaken
    for the quest's -- which is exactly what happened before: the old parser opened a new quest at
    every `title:` line and then took the next `id:`, and reported 42 phantom "quest has no id"
    failures the moment FTB Quests put `id` before `title`."""
    txt = open(path, encoding='utf-8').read()
    m = re.search(r'^\s*quests: \[', txt, re.M)
    if not m:
        return []
    body = txt[m.end():]

    quests = []
    cur = None
    for depth, line in lines_with_depth(body):
        stripped = line.strip()
        if depth == 0:
            if stripped.startswith('{'):
                cur = {'title': None, 'id': None, 'deps': [], 'items': [], 'entities': []}
                quests.append(cur)
            elif stripped.startswith(']'):
                break
        if cur is None:
            continue

        if depth == 1:
            mm = re.match(r'\s*id: "([0-9A-Fa-f]+)"\s*$', line)
            if mm and cur['id'] is None:
                cur['id'] = mm.group(1)
            mm = re.match(r'\s*title: "(.*)"\s*$', line)
            if mm and cur['title'] is None:
                cur['title'] = mm.group(1)

        mm = re.search(r'dependencies: \[([^\]]*)\]', line)
        if mm:
            cur['deps'].extend(re.findall(r'"([0-9A-Fa-f]+)"', mm.group(1)))
        # Both spellings: the minified `type: "item", item: "..."` our generator emitted, and the
        # expanded form FTB rewrites it into, where `item:` sits on its own line.
        for mm in re.finditer(r'item: "([^"]+)"', line):
            cur['items'].append(mm.group(1))
        for mm in re.finditer(r'entity: "([^"]+)"', line):
            cur['entities'].append(mm.group(1))

    # A chapter object with no title is not a quest -- guard against a stray leading brace.
    return [q for q in quests if q['id'] or q['title']]


# --------------------------------------------------------------------------- checking

def era_scripts(era):
    """Scripts belonging to exactly this era.

    The previous glob was *era{n}*.js, which matched 210_era10_tier_ladder.js for era 1 --
    so Era I was silently validated against Era X's ladder. The separator makes it exact.
    """
    found = sorted(glob.glob(os.path.join(SCRIPTS, f'*_era{era}_*.js')))
    if era == 1:
        found += sorted(glob.glob(os.path.join(SCRIPTS, '*starting_kit*.js')))
    return found


def check_era(era, ids, produced_by_era, all_recipes, problems, from_world=frozenset()):
    def fail(code, msg):
        problems.append((era, code, msg))
        print(f'  {code:4} {msg}')

    print(f'\n=== Era {era} ===')
    chapter = os.path.join('config', 'ftbquests', 'quests', 'chapters', f'era_{era}.snbt')
    if not os.path.exists(chapter):
        fail('E0', f'no chapter at {chapter}')
        return

    quests = parse_chapter(chapter)
    scripts = era_scripts(era)
    names = {os.path.basename(p) for p in scripts}
    recipes = [r for r in all_recipes if r['file'] in names]
    print(f'  {len(quests)} quests, {len(scripts)} script(s), {len(recipes)} recipes')

    # E1 -- quest items exist
    qitems = {i for q in quests for i in q['items']}
    for i in sorted(qitems):
        if i not in ids:
            fail('E1', f'quest item not registered: {i}')

    # E2 -- script items exist
    for r in recipes:
        for i in r['outputs'] + r['inputs']:
            if i not in ids:
                fail('E2', f'recipe id not registered: {i}  ({r["file"]} {r["id"]})')

    # E3 -- obtainability of our own items
    needed = {i for i in qitems if i.startswith(NS + ':')}
    for r in recipes:
        needed |= {i for i in r['inputs'] if i.startswith(NS + ':')}
    for i in sorted(needed):
        if i not in produced_by_era and i not in from_world:
            fail('E3', f'{i} is required but nothing produces it -- no recipe, and no '
                       'block-drop registration either')

    # E4 -- cross-era ordering
    for i in sorted(needed):
        made = produced_by_era.get(i)
        if made is not None and made > era:
            fail('E4', f'{i} is needed in Era {era} but first produced in Era {made}')

    # E9 -- quest structure
    seen_q = set()
    for q in quests:
        if q['id'] is None:
            fail('E9', f'quest has no id: "{q["title"]}"')
        elif q['id'] in seen_q:
            fail('E9', f'duplicate quest id {q["id"]} ("{q["title"]}")')
        else:
            seen_q.add(q['id'])
    for q in quests:
        for d in q['deps']:
            if d not in seen_q:
                fail('E9', f'"{q["title"]}" depends on {d}, not in this chapter')


def check_global(all_recipes, jar_recipes, jar_tags, jar_types, problems):
    def fail(code, msg):
        problems.append((0, code, msg))
        print(f'  {code:4} {msg}')

    print('\n=== Pack-wide ===')

    # E11 -- every event.remove must actually match something. This is the failure the
    # project doctrine warns about most: a remove that hits nothing passes every check and
    # leaves the recipe it was meant to close still craftable.
    for r in all_recipes:
        if r['method'] == 'remove' and r['removes'] and r['removes'] not in jar_recipes:
            fail('E11', f'event.remove targets {r["removes"]}, which no jar ships '
                        f'({r["file"]}) -- the old route stays open')

    # E12 -- referenced tags must exist. minecraft: and forge: tags are often contributed by
    # several mods at once, so accept them if any jar declares them.
    # Tags WE declare count too. kubejs/data/<ns>/tags/<kind>/<path>.json is a real tag the
    # game loads, and the pack ships several -- #alfheim:crystal_shards is the renewable-shard
    # contract the Era VII mixing recipe is built on. Asking only the jars reported our own
    # tag as undeclared, which is the same class of mistake as reading lang files for
    # registrations: right question, wrong source.
    own_tags = set()
    for tp in glob.glob(os.path.join('kubejs', 'data', '*', 'tags', '**', '*.json'),
                        recursive=True):
        parts = tp.replace(os.sep, '/').split('/')
        i = parts.index('tags')
        ns = parts[i - 1]
        # Everything after tags/<kind>/ is the tag path; the kind itself is not part of the id.
        own_tags.add(f'{ns}:{"/".join(parts[i + 2:])[:-5]}')

    for r in all_recipes:
        for t in r['tags']:
            if t not in jar_tags and t not in own_tags and not t.startswith('minecraft:'):
                fail('E12', f'tag {t} is referenced by {r["id"] or r["file"]} '
                            f'but no jar declares it and the pack does not either')

    # E13 -- custom recipe types must be serialisers a mod actually ships.
    for r in all_recipes:
        if r['method'] == 'custom' and r['type'] and r['type'] not in jar_types:
            fail('E13', f'recipe type {r["type"]} ({r["id"]}) is not shipped by any jar')

    # E5 -- a "use" must consume the item it is filed under
    uses = [r for r in all_recipes if r['id'] and r['id'].startswith(f'{NS}:uses/')]
    known = [it['id'] for it in manifest_items()]
    for r in uses:
        stem = r['id'].split('/', 1)[1]
        owner = None
        for iid in known:
            if stem.startswith(iid + '_') and (owner is None or len(iid) > len(owner)):
                owner = iid
        if owner is None:
            continue
        if f'{NS}:{owner}' not in r['inputs']:
            fail('E5', f'{r["id"]} is filed as a use for {NS}:{owner} but does not consume it')

    # E6 -- duplicate recipe ids
    seen = {}
    for r in all_recipes:
        if not r['id']:
            continue
        if r['id'] in seen:
            fail('E6', f'duplicate recipe id {r["id"]} ({seen[r["id"]]} and {r["file"]})')
        else:
            seen[r['id']] = r['file']

    # E7 -- identical recipes emitted more than once
    sig = {}
    for r in all_recipes:
        if r['method'] == 'remove':
            continue
        k = (r['type'] or r['method'], tuple(sorted(r['inputs'])), tuple(sorted(r['outputs'])))
        sig.setdefault(k, []).append(r['id'])
    for k, rids in sorted(sig.items(), key=lambda kv: -len(kv[1])):
        if len(rids) > 1:
            fail('E7', f'{len(rids)}x identical {k[0]} {list(k[1])} -> {list(k[2])}: '
                       f'{rids[0]} ... {rids[-1]}')

    # E8 -- self-multiplying recipes.
    #
    # Only FREE duplication is a defect: a recipe whose sole input is its own output can be
    # run forever and breaks the economy. A recipe that also consumes something else is a
    # cost-bearing multiplier -- which is exactly what the `reagent` use family is for --
    # so it is reported but not failed. Collapsing the two hid 17 real exploits among 48
    # deliberate recipes.
    advisories = []
    for r in all_recipes:
        for o in r['outputs']:
            if o not in r['inputs']:
                continue
            cost = [i for i in r['inputs'] if i != o]
            if cost:
                advisories.append(f'{r["id"]}: {o} x{len(r["outputs"])} for {", ".join(cost)}')
            else:
                fail('E8', f'{r["id"]} turns {o} into more of itself for free '
                           f'({r["type"] or r["method"]})')
    if advisories:
        print(f'  --   {len(advisories)} cost-bearing multipliers (not a defect), e.g. '
              f'{advisories[0]}')

    # E10 -- manifest items registered, modelled and textured
    reg = ''
    p = os.path.join('kubejs', 'startup_scripts', '10_items.js')
    if os.path.exists(p):
        reg = open(p, encoding='utf-8').read()
    for it in manifest_items():
        iid = it['id']
        if f"'{NS}:{iid}'" not in reg:
            fail('E10', f'{NS}:{iid} is in the manifest but not registered in 10_items.js')
        for kind, ext in (('models', 'json'), ('textures', 'png')):
            f = os.path.join('kubejs', 'assets', NS, kind, 'item', f'{iid}.{ext}')
            if not os.path.exists(f):
                fail('E10', f'{NS}:{iid} has no {kind[:-1]} at {f}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('era', nargs='?', type=int)
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    if a.era is None and not a.all:
        ap.error('give an era number or --all')

    scripts = sorted(glob.glob(os.path.join(SCRIPTS, '*.js')))
    all_recipes = []
    for p in scripts:
        all_recipes.extend(parse_recipes(p))

    namespaces = {r['type'].split(':')[0] for r in all_recipes if r['type']}
    ids, jar_recipes, jar_tags, jar_types = scan_jars(namespaces)
    print(f'known item/block ids: {len(ids)}   jar recipes: {len(jar_recipes)}   '
          f'tags: {len(jar_tags)}   serialisers: {len(jar_types)}')
    print(f'recipes parsed: {len(all_recipes)} from {len(scripts)} scripts')

    # Earliest era whose scripts produce each alfheim item.
    produced_by_era = {}
    for r in all_recipes:
        m = re.search(r'_era(\d+)_', r['file'])
        era_of = int(m.group(1)) if m else 0
        for o in r['outputs']:
            if not o.startswith(NS + ':'):
                continue
            if o not in produced_by_era or era_of < produced_by_era[o]:
                produced_by_era[o] = era_of

    from_world = world_sourced()
    print(f'world-sourced items (block drops, no recipe): {len(from_world)}')

    problems = []
    eras = range(1, 11) if a.all else [a.era]
    for e in eras:
        check_era(e, ids, produced_by_era, all_recipes, problems, from_world)
    if a.all:
        check_global(all_recipes, jar_recipes, jar_tags, jar_types, problems)
        single_writer_guard(problems)
        check_all_script_items(all_recipes, ids, problems)
        print('\n=== Recipe schemas ===')
        our_types = {r['type'] for r in all_recipes if r['type'] and r['method'] == 'custom'}
        check_schemas(all_recipes, jar_schemas(our_types), problems)

    print('\n' + '=' * 68)
    by_code = {}
    for _, code, _ in problems:
        by_code[code] = by_code.get(code, 0) + 1
    if by_code:
        print('problems by check: ' + ', '.join(f'{k}={v}' for k, v in sorted(by_code.items())))
    print(f'RESULT: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
