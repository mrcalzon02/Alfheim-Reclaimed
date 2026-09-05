"""Stamp the armory manifest only after exact live Mine and Slash evidence is present."""
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools/armory_manifest.json'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--console', required=True)
    args = ap.parse_args()
    log = (ROOT / args.console).resolve()
    text = log.read_text(encoding='utf-8', errors='replace')
    required = [
        'Loaded 9/9 KubeJS startup scripts',
        'with 0 errors and 0 warnings',
        '[Armory Probe] gear_types=48 auto_items=480 custom_items=480 profession_recipes=480',
        '[Armory Probe] representatives gear=true auto=true custom=true recipe=true',
        'Done (',
    ]
    missing = [line for line in required if line not in text]
    assert not missing, f'missing runtime evidence: {missing}'
    runner_manifest = log.with_name(log.name.replace('console-', 'manifest-').replace('.log', '.json'))
    run = json.loads(runner_manifest.read_text(encoding='utf-8'))
    assert run['exit_code'] == 0, run
    payload = [ROOT / 'kubejs/startup_scripts/17_armory.js']
    for folder in ('mmorpg_base_gear_types', 'mmorpg_auto_item', 'mmorpg_custom_item', 'mmorpg_profession_recipe'):
        payload.extend((ROOT / 'kubejs/data/alfheim' / folder).glob('*.json'))
    digest = hashlib.sha256()
    for path in sorted(payload, key=str):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    data = json.loads(OUT.read_text(encoding='utf-8'))
    data['status'] = 'runtime validated on dedicated Forge server'
    data['runtime_validation'] = {
        'date': '2026-09-04',
        'minecraft': run['minecraft'],
        'forge': run['forge'],
        'log': log.relative_to(ROOT).as_posix(),
        'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
        'generated_payload_sha256': digest.hexdigest(),
        'startup_scripts': '9/9 loaded, 0 errors, 0 warnings',
        'live_mns_registry_counts': {'gear_types': 48, 'auto_items': 480, 'custom_items': 480, 'profession_recipes': 480},
        'representative_entries_resolved': True,
        'server_exit_code': 0,
    }
    OUT.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(f'Stamped runtime validation from {log.relative_to(ROOT)}; payload {digest.hexdigest()}')


if __name__ == '__main__':
    main()
