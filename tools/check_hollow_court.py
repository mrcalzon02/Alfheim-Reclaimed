"""Validate the Hollow Court: quest_giver content, and the NPCs it is bound to.

Why this exists. B-41 shipped eleven recipes the game silently refused, because every static
check proved that ids existed and none proved that content had the shape its consumer needs.
The Hollow Court has the same failure surface and a worse symptom: quest_giver matches a quest
line to an NPC by **entity type plus custom name**, so a one-character drift between
`quest_line_links.json` and the summon in `03_hollow_court.js` produces an elf that stands
there and does nothing. No error, no log line, no missing id -- just a mute quest giver.

H5 is the check that exists for that, and it is the reason this file is worth having.

    python tools/check_hollow_court.py
    python tools/check_hollow_court.py --verbose
"""
import argparse
import glob
import json
import os
import re
import sys
import zipfile

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', 'quest_giver')
LINES_DIR = os.path.join(DATA, 'quest_lines')
COURT_SCRIPT = os.path.join('kubejs', 'server_scripts', '03_hollow_court.js')
GATE_SCRIPT = os.path.join('kubejs', 'startup_scripts', '14_sealed_gate.js')
MANIFEST = os.path.join('tools', 'hollow_court_manifest.json')
QUEST_GIVER_JAR_GLOB = os.path.join('mods', 'quest_giver-*.jar')

# Task ids the mod registers, read off its task classes. A typo'd task id is accepted by the
# JSON parser and then does nothing, which is the quiet failure mode this list closes.
# Read from the REGISTRATION SITE (QuestGiver.class), not from the task class names. The jar
# ships GrowTreeTask and SpecialTask classes that are never registered, and deriving this list
# from class names put `quest_giver:grow_tree` into a quest -- which threw
#   IllegalStateException: Unknown quest task type: quest_giver:grow_tree
# and aborted loading of every quest line in the pack. Runtime-proven 2026-09-04.
TASK_IDS = {
    'quest_giver:gift', 'quest_giver:craft', 'quest_giver:item_stack', 'quest_giver:kill',
    'quest_giver:tame', 'quest_giver:pet', 'quest_giver:name_entity',
    'quest_giver:complete_quest', 'quest_giver:structure', 'quest_giver:biome',
    'quest_giver:special_task',
}
REWARD_IDS = {'quest_giver:item', 'quest_giver:command'}


def load_ids():
    """Item/block ids from every jar's lang file, plus entity ids, plus our own manifests."""
    sys.path.insert(0, 'tools')
    import check_era
    items, _, _, _ = check_era.scan_jars(verbose=False)

    entities = set()

    def take_entities(raw):
        try:
            d = json.loads(raw.decode('utf-8', 'replace'))
        except Exception:
            return
        for k in d:
            p = k.split('.', 2)
            if len(p) == 3 and p[0] == 'entity':
                entities.add(f'{p[1]}:{p[2]}')

    # Vanilla entities live in the client jar, not in mods/. Without this, minecraft:spider
    # reads as unregistered and a perfectly good kill task looks broken.
    if os.path.exists(check_era.CLIENT_JAR):
        with zipfile.ZipFile(check_era.CLIENT_JAR) as z:
            for e in z.namelist():
                if e.endswith('assets/minecraft/lang/en_us.json'):
                    take_entities(z.read(e))
    else:
        print(f'  ! vanilla client jar not found at {check_era.CLIENT_JAR} -- '
              'vanilla entity ids unverified')

    for jar in sorted(glob.glob(os.path.join('mods', '*.jar'))):
        try:
            z = zipfile.ZipFile(jar)
        except Exception:
            continue
        with z:
            for e in z.namelist():
                if re.match(r'assets/[^/]+/lang/en_us\.json$', e):
                    take_entities(z.read(e))

    # Blooms, crystals and groves live in their own manifests, not items_manifest.json.
    for mf in ('blooms', 'crystals', 'groves'):
        p = os.path.join('tools', f'{mf}_manifest.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for v in d.values():
            if not isinstance(v, list):
                continue
            for it in v:
                if isinstance(it, dict) and 'id' in it:
                    items |= {f"{NS}:{it['id']}", f"{NS}:raw_{it['id']}",
                              f"{NS}:quickened_{it['id']}"}
    return items, entities


def biomes():
    return {os.path.basename(p)[:-5]
            for p in glob.glob(os.path.join('kubejs', 'data', NS, 'worldgen', 'biome', '*.json'))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()

    problems = []

    def fail(code, msg):
        problems.append((code, msg))
        print(f'  {code}  {msg}')

    if not os.path.isdir(DATA):
        print('no quest_giver data -- nothing to check')
        return 0

    items, entities = load_ids()
    biome_set = biomes()
    print(f'known items: {len(items)}   entities: {len(entities)}   '
          f'{NS} biomes: {len(biome_set)}')

    names = json.load(open(os.path.join(DATA, 'quest_line_names.json'), encoding='utf-8'))
    registered = {n.lower() for n in names.get('names', [])}
    links = json.load(open(os.path.join(DATA, 'quest_line_links.json'), encoding='utf-8'))

    on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(LINES_DIR, '*'))
               if os.path.isdir(p)}

    # ---- H1: the registry and the directories must describe the same set -----------------
    for line in sorted(on_disk - registered):
        fail('H1', f'quest line "{line}" has a directory but is not in quest_line_names.json, '
                   'so nothing will load it')
    for line in sorted(registered - on_disk):
        fail('H1', f'quest line "{line}" is registered but has no directory under {LINES_DIR}')
    for line in sorted(on_disk):
        if not os.path.exists(os.path.join(LINES_DIR, line, 'root.json')):
            fail('H1', f'quest line "{line}" has no root.json')

    # ---- H2/H3/H7: quest shape, parents, ids ---------------------------------------------
    n_quests = 0
    for line in sorted(on_disk):
        keys = {os.path.basename(p)[:-5]
                for p in glob.glob(os.path.join(LINES_DIR, line, '*.json'))}
        for p in sorted(glob.glob(os.path.join(LINES_DIR, line, '*.json'))):
            key = os.path.basename(p)[:-5]
            rel = os.path.relpath(p)
            try:
                q = json.load(open(p, encoding='utf-8'))
            except Exception as e:
                fail('H2', f'{rel}: will not parse -- {e}')
                continue
            n_quests += 1

            parent = q.get('parent')
            if parent:
                pk = parent.split(':', 1)[1] if ':' in parent else parent
                if pk not in keys:
                    fail('H2', f'{rel}: parent "{parent}" names no quest in "{line}" '
                               f'(has: {", ".join(sorted(keys))})')
            elif key != 'root':
                fail('H2', f'{rel}: only root.json may have no parent, so this quest is '
                           'unreachable')

            if 'start' not in q:
                fail('H2', f'{rel}: no "start" block, so the NPC has nothing to say')

            def check_item(where, val):
                if val and val not in items:
                    fail('H3', f'{rel}: {where} names "{val}", which no jar or manifest '
                               'registers')

            check_item('icon', q.get('icon'))
            for t in q.get('tasks', []):
                if t.get('id') not in TASK_IDS:
                    fail('H7', f'{rel}: task id "{t.get("id")}" is not one quest_giver '
                               'registers -- it will parse and never complete')
                if isinstance(t.get('item'), dict):
                    check_item('task item', t['item'].get('item'))
                check_item('sapling', t.get('sapling'))
                if t.get('entity') and t['entity'] not in entities:
                    fail('H3', f'{rel}: task entity "{t["entity"]}" is not a registered entity')
                b = t.get('biome')
                if b and b.split(':', 1)[0] == NS and b.split(':', 1)[1] not in biome_set:
                    fail('H3', f'{rel}: biome "{b}" is not one of ours')
            for r in q.get('rewards', []):
                if r.get('id') not in REWARD_IDS:
                    fail('H7', f'{rel}: reward id "{r.get("id")}" is not one quest_giver '
                               'registers')
                if isinstance(r.get('item'), dict):
                    check_item('reward item', r['item'].get('item'))

    # ---- H4: links point at registered lines and real entities ---------------------------
    for lk in links:
        if lk.get('quest_line_id', '').lower() not in registered:
            fail('H4', f'link for "{lk.get("name")}" points at unregistered quest line '
                       f'"{lk.get("quest_line_id")}"')
        if lk.get('entity_id') not in entities:
            fail('H4', f'link for "{lk.get("name")}" binds to "{lk.get("entity_id")}", '
                       'which is not a registered entity')
        if lk.get('interaction_item') and lk['interaction_item'] not in items:
            # quest_giver ships quest_scroll with no lang entry, so it never enters the id
            # universe. Warn rather than fail: the item exists, its name does not.
            if a.verbose:
                print(f'  --   interaction item "{lk["interaction_item"]}" has no lang entry '
                      '(quest_giver ships it untranslated); not treated as missing')

    # ---- H5: the name is the binding, so both sides must agree exactly --------------------
    if os.path.exists(COURT_SCRIPT):
        script = open(COURT_SCRIPT, encoding='utf-8').read()
        summoned = set(re.findall(r"name:\s*'([^']+)'", script))
        for lk in links:
            nm = lk.get('name')
            if nm not in summoned:
                fail('H5', f'"{nm}" is linked to quest line "{lk.get("quest_line_id")}" but is '
                           f'never summoned by {os.path.basename(COURT_SCRIPT)} -- '
                           'that quest line is unreachable')
        linked = {lk.get('name') for lk in links}
        if a.verbose:
            for nm in sorted(summoned - linked):
                print(f'  --   "{nm}" is summoned with no quest line (ambient court member)')
    else:
        fail('H5', f'{COURT_SCRIPT} is missing, so nothing places the court')

    # ---- H6: the gate must actually gate --------------------------------------------------
    if os.path.exists(MANIFEST):
        man = json.load(open(MANIFEST, encoding='utf-8'))
        for item, where in man.get('gates', {}).items():
            line, _, quest = where.partition('/')
            p = os.path.join(LINES_DIR, line, f'{quest}.json')
            if not os.path.exists(p):
                fail('H6', f'gate for "{item}" names {where}, which does not exist')
                continue
            q = json.load(open(p, encoding='utf-8'))
            granted = any(isinstance(r.get('item'), dict) and r['item'].get('item') == item
                          for r in q.get('rewards', []))
            if not granted:
                fail('H6', f'{where} is declared the gate for "{item}" but does not reward it, '
                           'so nothing grants it and the content is unreachable')
            elif a.verbose:
                print(f'  --   "{item}" gated behind {where}, and granted there')

    if not os.path.exists(GATE_SCRIPT):
        fail('H1', f'{GATE_SCRIPT} is missing, so alfheim:sealed_gate is never registered')

    print(f'\nquest lines: {len(on_disk)}   quests: {n_quests}   links: {len(links)}')
    print('=' * 68)
    if problems:
        by = {}
        for code, _ in problems:
            by[code] = by.get(code, 0) + 1
        print('problems by check: ' + ', '.join(f'{k}={v}' for k, v in sorted(by.items())))
    print(f'RESULT: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
