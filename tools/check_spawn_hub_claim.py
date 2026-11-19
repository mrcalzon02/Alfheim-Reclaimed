"""Validate the FTB Chunks ownership read-back for the Alfheim spawn hub.

This consumes the per-run console written by tools/run_server.py.  It does not infer success from
`claim_as` return values: it requires `ftbchunks info` to report the expected owner at every
chunk of the generated hub protection envelope, not merely its centre and corners.

    python tools/check_spawn_hub_claim.py
    python tools/check_spawn_hub_claim.py server/console-YYYYMMDD-HHMMSS.log

Only a matching successful completed-run manifest with every required probe
can establish ownership acceptance; a newer failed/incomplete attempt invalidates
stale evidence even when the older console is explicitly requested.
    python tools/check_spawn_hub_claim.py --self-test
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile

SCRIPT = os.path.join('kubejs', 'server_scripts', '04_spawn_hub.js')
CONSOLE_GLOB = os.path.join('server', 'console-*.log')


def required_chunks(bounds):
    """Every chunk intersecting the inclusive rectangular protection envelope."""
    min_x, max_x, min_z, max_z = bounds
    if min_x > max_x or min_z > max_z:
        raise ValueError(f'invalid hub claim bounds: {bounds}')
    return [(cx, cz) for cx in range(min_x >> 4, (max_x >> 4) + 1)
                     for cz in range(min_z >> 4, (max_z >> 4) + 1)]


def probe_commands(bounds, dimension):
    """Issue one FTB ownership read-back for every required chunk, including the interior."""
    return [(2, f'ftbchunks info {cx << 4} {cz << 4} {dimension}')
            for cx, cz in required_chunks(bounds)]


def protection_contract(path=SCRIPT):
    """Read the shipping protection script so validator expectations cannot drift from it."""
    text = open(path, encoding='utf-8').read()

    def one(pattern, label):
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f'{path}: cannot read {label} from generated protection script')
        return match.group(1)

    dimension = one(r"const\s+HUB_DIMENSION\s*=\s*'([^']+)'", 'HUB_DIMENSION')
    team = one(r"const\s+HUB_FTB_TEAM\s*=\s*'([^']+)'", 'HUB_FTB_TEAM')
    # The envelope became an explicit rectangle on 2026-09-07: the complex is not centred on
    # the tree, so a radius both over-claimed to the south and under-claimed to the north.
    bounds = tuple(int(one(rf'const\s+{name}\s*=\s*(-?\d+)', name)) for name in
                   ('HUB_MIN_X', 'HUB_MAX_X', 'HUB_MIN_Z', 'HUB_MAX_Z'))
    return dimension, team, bounds, required_chunks(bounds)


def verified_console(requested, expected_commands, directory=None):
    """Require the newest observed attempt's own successful run manifest.

    Neither filesystem mtimes nor an explicitly requested older console can
    override evidence that a newer server launch failed or was interrupted.
    """
    directory = directory or os.path.dirname(CONSOLE_GLOB)
    stamps = set()
    for prefix, suffix in (('console-', '.log'), ('manifest-', '.json')):
        for path in glob.glob(os.path.join(directory, prefix + '*' + suffix)):
            name = os.path.basename(path)
            stamp = name[len(prefix):-len(suffix)]
            if re.fullmatch(r'\d{8}-\d{6}', stamp):
                stamps.add(stamp)
    if not stamps:
        raise ValueError('no server run evidence found; run tools/run_server.py --run first')

    stamp = max(stamps)
    selected = os.path.join(directory, f'console-{stamp}.log')
    if requested and os.path.normcase(os.path.abspath(requested)) != os.path.normcase(os.path.abspath(selected)):
        raise ValueError(f'requested console is not newest observed run: {selected}')
    if not os.path.isfile(selected):
        raise ValueError(f'newest run is missing its console: {selected}')

    manifest_path = os.path.join(directory, f'manifest-{stamp}.json')
    try:
        with open(manifest_path, encoding='utf-8') as source:
            manifest = json.load(source)
    except (OSError, ValueError) as exc:
        raise ValueError(f'newest run has no valid manifest: {manifest_path} ({exc})') from exc
    if not isinstance(manifest, dict) or manifest.get('console') != os.path.basename(selected):
        raise ValueError(f'newest manifest does not identify its console: {manifest_path}')
    if manifest.get('status') not in (None, 'completed'):
        raise ValueError(f'newest run did not complete: {manifest_path}')
    if manifest.get('harness_exit_code') != 0 or manifest.get('exit_code') != 0:
        raise ValueError(f'newest run failed: {manifest_path}')
    commands = manifest.get('commands')
    if not isinstance(commands, list) or set(expected_commands) - set(commands):
        raise ValueError(f'newest run did not schedule every ownership probe: {manifest_path}')
    return selected


def location_line(dimension, cx, cz):
    """How FTB Chunks actually prints a chunk address.

    It is `Location: [mythicbotany:alfheim:-1:-4]` -- dimension and both chunk coordinates
    colon-joined inside one bracket. This validator was written expecting
    `Location: mythicbotany:alfheim [-1, -4]`, which no FTB Chunks build emits, so every probe
    read as "no read-back in console" and the check could only ever fail. Caught 2026-09-07,
    when all five probes in fact reported `Owner: alfheim_hub`.
    """
    return f'Location: [{dimension}:{cx}:{cz}]'


def validate_text(text, dimension, team, chunks):
    """Return human-readable failures for missing/unowned FTB Chunks read-back probes."""
    problems = []
    # A chat message or quoted line may contain the exact Location text. Only
    # standalone FTB info payloads count; preserve the bare, prefixed and
    # timestamped server-INFO formats from the headless console.
    log_prefix = re.compile(r'^(?:\[\d\d:\d\d:\d\d\]\s+)?\[Server thread/INFO\]:?\s+')
    lines = [log_prefix.sub('', line, count=1) for line in text.splitlines()]
    latest = {}
    for i, line in enumerate(lines):
        if re.fullmatch(r'Location: \[[^\]\r\n]+\]', line):
            latest[line] = lines[i + 1] if i + 1 < len(lines) else ''
    for cx, cz in chunks:
        location = location_line(dimension, cx, cz)
        if location not in latest:
            problems.append(f'{location}: no `ftbchunks info` read-back in console')
            continue
        # The last genuine probe wins. Its owner must be the immediate next
        # server payload, not a later unrelated line or a player chat message.
        owner = re.match(r'^Owner:\s*([^\r\n/]+)', latest[location])
        if not owner:
            problems.append(f'{location}: claim owner was not reported')
            continue
        actual = owner.group(1).strip()
        if actual != team:
            problems.append(f'{location}: owner is {actual!r}, expected {team!r}')
    return problems


def self_test():
    dimension = 'mythicbotany:alfheim'
    team = 'alfheim_hub'
    chunks = [(0, 0), (12, 12), (-12, 12), (12, -12), (-12, -12)]

    def claimed(owner=team, omit=None):
        out = []
        for pos in chunks:
            if pos == omit:
                continue
            cx, cz = pos
            out.append(f'[Server thread/INFO] {location_line(dimension, cx, cz)}')
            out.append(f'[Server thread/INFO] Owner: {owner} / 0123456789abcdef')
            out.append('[Server thread/INFO] Force-loaded: false')
        return '\n'.join(out)

    def reread(pos, owner=team):
        cx, cz = pos
        out = [f'[Server thread/INFO] {location_line(dimension, cx, cz)}']
        if owner is None:
            out.append('[Server thread/INFO] Chunk not claimed')
        else:
            out.append(f'[Server thread/INFO] Owner: {owner} / 0123456789abcdef')
        out.append('[Server thread/INFO] Force-loaded: false')
        return '\n'.join(out)

    cases = [
        ('complete', claimed(), 0),
        ('wrong owner', claimed('somebody_else'), 5),
        ('missing corner', claimed(omit=(-12, -12)), 1),
        ('unclaimed centre', claimed().replace(
            f'{location_line(dimension, 0, 0)}\n[Server thread/INFO] Owner: {team} '
            f'/ 0123456789abcdef',
            'Chunk not claimed', 1), 1),
        # A claim may change across restart/retry. The newest exact-position read-back
        # must win, even when the earlier probe was healthy.
        ('later wrong owner', claimed() + '\n' + reread((0, 0), 'somebody_else'), 1),
        ('later unclaimed corner', claimed() + '\n' + reread((-12, -12), None), 1),
        ('later missing owner', claimed() + '\n' +
            f'[Server thread/INFO] {location_line(dimension, 12, 12)}\n'
            '[Server thread/INFO] Force-loaded: false', 1),
        ('later unclaimed with unrelated Owner', claimed() + '\n' +
            reread((0, 0), None) + '\n'
            f'[Server thread/INFO] Owner: {team} / unrelated', 1),
        ('later missing with unrelated Owner', claimed() + '\n' +
            f'[Server thread/INFO] {location_line(dimension, 0, 0)}\n'
            '[Server thread/INFO] Force-loaded: false\n'
            f'[Server thread/INFO] Owner: {team} / unrelated', 1),
        # A player chat or an ordinary quote is not an FTB location reply.
        # An unrelated Owner line immediately afterward must not authenticate it.
        ('chat Location with unrelated Owner', claimed(omit=(0, 0)) + '\n' +
            f'[Server thread/INFO] [Not Secure] <Visitor> {location_line(dimension, 0, 0)}\n'
            f'[Server thread/INFO] Owner: {team} / unrelated', 1),
        ('quoted Location with unrelated Owner', claimed(omit=(0, 0)) + '\n' +
            f'[Server thread/INFO] [Server] quoted: {location_line(dimension, 0, 0)}\n'
            f'[Server thread/INFO] Owner: {team} / unrelated', 1),
        ('later chat is not a new probe', claimed() + '\n' +
            f'[Server thread/INFO] [Not Secure] <Visitor> {location_line(dimension, 0, 0)}\n'
            '[Server thread/INFO] Chunk not claimed', 0),
        ('bare FTB reply', '\n'.join(
            f'{location_line(dimension, cx, cz)}\nOwner: {team} / 0123456789abcdef'
            for cx, cz in chunks), 0),
        ('timestamped FTB reply', '\n'.join(
            f'[20:06:35] [Server thread/INFO]: {location_line(dimension, cx, cz)}\n'
            f'[20:06:35] [Server thread/INFO]: Owner: {team} / 0123456789abcdef'
            for cx, cz in chunks), 0),
        ('later corrected owner', claimed('somebody_else') + '\n' + claimed(), 0),
    ]
    bad = 0
    for name, text, expected in cases:
        got = len(validate_text(text, dimension, team, chunks))
        if got != expected:
            print(f'  FAIL  {name}: expected {expected} problem(s), got {got}')
            bad += 1
        else:
            print(f'  OK    {name}: {got} problem(s)')
    # Real relocated rectangle is ten by ten chunks; a five-point sampler misses
    # an isolated interior hole and incorrectly reports protection-ready.
    bounds = (-80, 79, -128, 31)
    full_chunks = required_chunks(bounds)
    commands = probe_commands(bounds, dimension)
    expected_commands = [(2, f'ftbchunks info {cx << 4} {cz << 4} {dimension}')
                         for cx in range(-5, 5) for cz in range(-8, 2)]
    if full_chunks != [(cx, cz) for cx in range(-5, 5) for cz in range(-8, 2)] or commands != expected_commands:
        print('  FAIL  full envelope command plan: expected 100 unique chunk probes')
        bad += 1
    else:
        print('  OK    full envelope command plan: 100 chunk probes')

    interior = (-2, -4)  # deliberately neither centre nor any of the four corners

    def full_claimed(omit=None, changed=None):
        lines = []
        for cx, cz in full_chunks:
            if (cx, cz) == omit:
                continue
            lines.append(f'[Server thread/INFO] {location_line(dimension, cx, cz)}')
            owner = 'another_team' if (cx, cz) == changed else team
            lines.append(f'[Server thread/INFO] Owner: {owner} / 0123456789abcdef')
        return '\n'.join(lines)

    for name, console, expected in (
        ('whole envelope claimed', full_claimed(), 0),
        ('missing interior chunk', full_claimed(omit=interior), 1),
        ('foreign-owned interior chunk', full_claimed(changed=interior), 1),
    ):
        got = len(validate_text(console, dimension, team, full_chunks))
        if got != expected:
            print(f'  FAIL  {name}: expected {expected} problem(s), got {got}')
            bad += 1
        else:
            print(f'  OK    {name}: {got} problem(s)')
    # Use actual temporary per-run files, not static strings alone. A newer failed
    # run must invalidate a former claimed console even if old mtime is fresher.
    with tempfile.TemporaryDirectory() as directory:
        prior, newest = '20261118-120000', '20261118-120100'
        required = [f'ftbchunks info {cx << 4} {cz << 4} {dimension}'
                    for cx, cz in chunks]

        def write_console(stamp, contents):
            path = os.path.join(directory, f'console-{stamp}.log')
            with open(path, 'w', encoding='utf-8') as out:
                out.write(contents)
            return path

        def write_manifest(stamp, *, status='completed', exit_code=0,
                           harness_exit=0, commands=None, filename=None):
            path = os.path.join(directory, f'manifest-{stamp}.json')
            record = {'console': filename or f'console-{stamp}.log',
                      'status': status, 'exit_code': exit_code,
                      'harness_exit_code': harness_exit,
                      'commands': required if commands is None else commands}
            with open(path, 'w', encoding='utf-8') as out:
                json.dump(record, out)
            return path

        def verify_fixture(name, wanted, requested=None):
            nonlocal bad
            try:
                selected = verified_console(requested, required, directory)
                with open(selected, encoding='utf-8') as source:
                    failures = validate_text(source.read(), dimension, team, chunks)
                actual = 'CLAIM_PROBLEMS' if failures else 'OK'
            except (OSError, ValueError):
                actual = 'REJECT'
            if actual == wanted:
                print(f'  OK    {name}: {actual}')
            else:
                print(f'  FAIL  {name}: expected {wanted}, got {actual}')
                bad += 1

        prior_log = write_console(prior, claimed())
        write_manifest(prior)
        verify_fixture('completed prior run', 'OK')
        write_manifest(newest, status='started')
        verify_fixture('new attempt without console', 'REJECT')
        os.remove(os.path.join(directory, f'manifest-{newest}.json'))
        new_log = write_console(newest, claimed(omit=(0, 0)))
        verify_fixture('new console without final manifest', 'REJECT')
        write_manifest(newest, status='started')
        verify_fixture('unfinished new run', 'REJECT')
        write_manifest(newest, exit_code=1, harness_exit=3)
        verify_fixture('failed new run cannot borrow prior ownership', 'REJECT')
        write_manifest(newest)
        verify_fixture('incomplete current probes', 'CLAIM_PROBLEMS')
        write_console(newest, claimed())
        verify_fixture('completed current run', 'OK')
        verify_fixture('explicit old log cannot bypass new run', 'REJECT', prior_log)
        verify_fixture('explicit latest log', 'OK', new_log)
        os.utime(prior_log, (2000000000, 2000000000))
        verify_fixture('stale log with newer mtime does not win', 'OK')
        write_manifest(newest, commands=required[:-1])
        verify_fixture('missing planned ownership command', 'REJECT')
        write_manifest(newest, filename='console-other.log')
        verify_fixture('manifest/console mismatch', 'REJECT')

    # Execute the real harness run() function's AST, isolated from global
    # Forge/structure imports that are absent from CI's intentional sparse checkout.
    # This tests the actual failed-preflight path, not a mocked reimplementation.
    import ast
    import time
    runner_path = os.path.join(os.path.dirname(__file__), 'run_server.py')
    with open(runner_path, encoding='utf-8') as source:
        runner_tree = ast.parse(source.read(), filename=runner_path)
    runner_fn = next(node for node in runner_tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == 'run')
    with tempfile.TemporaryDirectory() as directory:
        # run() is the real production AST. Only the complete-mod-inventory
        # dependency is replaced here so that no Forge/structure imports are
        # required in CI's sparse checkout. The ACTUAL inventory checker is
        # separately exercised by test_run_server_mirror_safety.py.
        namespace = {'os': os, 'json': json, 'time': time, 'SERVER': directory,
                     'mirror_source_check': lambda: (False, 'partial source fixture')}
        # Preserve actual module-level Forge identity while isolating this
        # preflight path from imports unavailable in the sparse source job.
        for name in ('MC', 'FORGE'):
            value = next(node.value for node in runner_tree.body
                         if isinstance(node, ast.Assign) and
                         any(isinstance(target, ast.Name) and target.id == name
                             for target in node.targets))
            namespace[name] = ast.literal_eval(value)
        exec(compile(ast.fix_missing_locations(
            ast.Module(body=[runner_fn], type_ignores=[])), runner_path, 'exec'),
             namespace)

        # New safety contract: incomplete root mods must NOT create a manifest
        # or touch a server world before returning an actionable failure code.
        code = namespace['run'](1, 'test-world', 4, [], 1)
        markers = glob.glob(os.path.join(directory, 'manifest-*.json'))
        if code == 2 and not markers:
            print('  OK    incomplete mod source rejected before server manifests')
        else:
            print('  FAIL  incomplete mod source modified server manifest')
            bad += 1

        # Historical contract: a *completed* source preflight followed by a
        # missing Forge runtime must still leave an incomplete 'started'
        # evidence marker. This cannot be borrowed as a successful prior run.
        namespace['mirror_source_check'] = lambda: (True, 'complete source fixture')
        code = namespace['run'](1, 'test-world', 4, [], 1)
        markers = glob.glob(os.path.join(directory, 'manifest-*.json'))
        state = {}
        if len(markers) == 1:
            with open(markers[0], encoding='utf-8') as source:
                state = json.load(source)
        if code == 2 and state.get('status') == 'started' and state.get('console'):
            print('  OK    post-preflight missing Forge runtime stays incomplete')
        else:
            print('  FAIL  missing Forge runtime preflight marker not recorded')
            bad += 1
    print(f'RESULT: {bad} self-test failure(s)')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('console', nargs='?', help='console log; defaults to newest server/console-*.log')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    try:
        dimension, team, bounds, chunks = protection_contract()
    except (OSError, ValueError) as exc:
        print(f'!! {exc}')
        return 2

    try:
        console = verified_console(a.console, [c for _, c in probe_commands(bounds, dimension)])
    except ValueError as exc:
        print(f'!! {exc}')
        return 2

    text = open(console, encoding='utf-8', errors='replace').read()
    problems = validate_text(text, dimension, team, chunks)
    print(f'claim contract: team={team} dimension={dimension} envelope X {bounds[0]}..{bounds[1]} Z {bounds[2]}..{bounds[3]} ({len(chunks)} probes)')
    print(f'console: {console}')
    for problem in problems:
        print(f'  C1  {problem}')
    if problems:
        print(f'RESULT: {len(problems)} problem(s) — hub claim is NOT runtime accepted')
        return 1
    print(f'RESULT: 0 problems — {len(chunks)}/{len(chunks)} ownership probes report {team}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
