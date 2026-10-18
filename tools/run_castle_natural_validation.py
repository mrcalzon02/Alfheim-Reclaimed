"""Prove natural castle population without a place command or editing player saves."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import time

import nbt
import run_server
from probe_terraces import chunks, section_blocks

ROOT = Path(__file__).resolve().parents[1]
HOME = 'execute in mythicbotany:alfheim '
REPORT = ROOT / 'tools/castle_natural_runtime_report.json'


class Plan:
    def __init__(self, previous):
        self.previous = previous
        self.site = None
        self.ground_sites = []
        self.commands = []
        self.started = False

    def __iter__(self):
        if self.started:
            return iter(self.commands)
        self.started = True
        return self.expand()

    def expand(self):
        def command(delay, text):
            self.commands.append((delay, text))
            return delay, text
        for text in ('gamerule doMobSpawning false', 'gamerule randomTickSpeed 0',
                     'scoreboard players set #final alfheim.hub 1',
                     'scoreboard players set #created alfheim.hub 1',
                     'scoreboard players set #foundation_v1 alfheim.hub 1',
                     'schedule clear alfheim:hub/resolve',
                     'schedule clear alfheim:hub/inspect_burial',
                     'schedule clear alfheim:hub/repair_foundation',
                     HOME + 'run forceload remove all',
                     HOME + 'run alfheim_terrain_audit',
                     HOME + 'run alfheim_castle_audit',
                     HOME + 'positioned 0 100 0 run locate structure alfheim:royal_castle'):
            yield command(1, text)
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            consoles = set((ROOT / 'server').glob('console-*.log')) - self.previous
            if consoles:
                log = max(consoles, key=lambda p: p.stat().st_mtime).read_text(errors='replace')
                found = re.search(r'nearest alfheim:royal_castle is at \[(-?\d+), ~, (-?\d+)\]', log)
                if found:
                    self.site = [int(found[1]), int(found[2])]
                    break
                if 'Could not find a structure' in log:
                    raise RuntimeError('No viable natural castle candidate for this seed')
            time.sleep(.25)
        if self.site is None:
            raise RuntimeError('Castle locate did not finish')
        # One 16x16 chunk square contains every tile and the native foundation.
        x, z = self.site
        yield command(1, HOME + f'run forceload add {x-128} {z-128} {x+127} {z+127}')
        yield command(50, 'save-all flush')
        yield command(3, HOME + 'run forceload remove all')
        yield command(1, HOME + 'run alfheim_district_rings_audit')
        yield command(1, HOME + 'positioned 0 100 0 run locate structure alfheim:golden_field_dais')
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            log = max(set((ROOT/'server').glob('console-*.log'))-self.previous,key=lambda p:p.stat().st_mtime).read_text(errors='replace')
            small = re.search(r'nearest alfheim:golden_field_dais is at \[(-?\d+), ~, (-?\d+)\]',log)
            if small and 'DISTRICT_RING_AUDIT_PASS' in log:
                districts = re.findall(r'DISTRICT_RING_SITE ring=(\d+) slot=(\d+) family=(alfheim:\w+) x=(-?\d+) z=(-?\d+) viable=true',log)
                self.ground_sites = [dict(family='alfheim:golden_field_dais',x=int(small[1]),z=int(small[2]))]
                if districts:
                    r,s,f,dx,dz=districts[0]
                    self.ground_sites.append(dict(family=f,x=int(dx),z=int(dz),ring=int(r)))
                break
            time.sleep(.25)
        assert self.ground_sites, 'No naturally viable grounded test structure found'
        for site in self.ground_sites:
            gx,gz=site['x'],site['z']
            # The locate marker is the start chunk's minimum block coordinate.
            gx,gz=(gx//16)*16,(gz//16)*16
            site.update(x=gx,z=gz)
            yield command(1,HOME+f'run forceload add {gx-128} {gz-128} {gx+127} {gz+127}')
            yield command(40,'save-all flush')
            yield command(2,HOME+'run forceload remove all')
        yield command(3, 'stop')


def verify(world, site):
    x, z = site
    region = ROOT / 'server' / world / 'dimensions/mythicbotany/alfheim/region'
    needed = {(x//16+dx, z//16+dz) for dx in range(-8, 8) for dz in range(-8, 8)}
    grid = {}
    for rx, rz in sorted({(cx//32, cz//32) for cx, cz in needed}):
        for c in chunks(region / f'r.{rx}.{rz}.mca'):
            if (c['xPos'], c['zPos']) in needed:
                grid[c['xPos'], c['zPos']] = c
    start = grid[x//16, z//16]['structures']['starts'].get('alfheim:royal_castle')
    assert start and start.get('id') != 'INVALID', 'Natural castle start missing'
    pieces = start['Children']
    tiles = [p for p in pieces if 'pool_element' in p]
    assert len(pieces) == 26 and len(tiles) == 25, 'Incomplete native castle assembly'
    cache = {}
    def block(x, y, z):
        key = (x//16, y//16, z//16)
        if key not in cache:
            c = grid.get((x//16, z//16), {})
            sec = next((s for s in c.get('sections', []) if s['Y'] == y//16), None)
            cache[key] = section_blocks(sec) if sec else None
        data = cache[key]
        return data[((y&15)<<8)|((z&15)<<4)|(x&15)] if data else None
    proofs = []
    for p in tiles:
        location = p['pool_element']['location']
        template = nbt.load(ROOT / f'kubejs/data/alfheim/structures/{location.split(":",1)[1]}.nbt')[1]
        solid = [b for b in template['blocks'] if template['palette'][int(b['state'])]['Name'] not in
                 ('minecraft:air', 'minecraft:cave_air', 'minecraft:jigsaw')]
        sample = solid[::max(1, len(solid)//200)]
        rotations = ['NONE','CLOCKWISE_90','CLOCKWISE_180','COUNTERCLOCKWISE_90'].index(p['rotation'])
        matched = 0
        for b in sample:
            bx, by, bz = map(int, b['pos'])
            for _ in range(rotations):
                bx, bz = -bz, bx
            matched += block(p['PosX']+bx, p['PosY']+by, p['PosZ']+bz) == template['palette'][int(b['state'])]['Name']
        assert matched == len(sample), (location, matched, len(sample))
        proofs.append(dict(template=location, bounds=p['BB'], sampled=len(sample), matched=matched))
    base = int(tiles[0]['PosY'])
    x0, z0 = x-117, z-117
    for dx in (12,117,222):
        for dz in (12,117,222):
            assert all(block(x0+dx,y,z0+dz) not in (None,'minecraft:air','minecraft:water','minecraft:cave_air')
                       for y in range(base-1,base+8)), 'Unsupported castle deck'
    # Saved starts of other independent structures must stay 500 blocks away
    # from the actual castle footprint. Same-family pieces are one assembly.
    gaps = []
    for c in grid.values():
        for family, other in c.get('structures', {}).get('starts', {}).items():
            if family == 'alfheim:royal_castle' or other.get('id') == 'INVALID':
                continue
            for p in other.get('Children', []):
                bb = p['BB']
                dx = max(x0-bb[3]-1, bb[0]-(x0+234)-1, 0)
                dz = max(z0-bb[5]-1, bb[2]-(z0+234)-1, 0)
                gap = (dx*dx+dz*dz)**.5
                gaps.append(dict(family=family, gap=round(gap,2)))
                assert gap >= 500, ('Independent structure intrudes into castle clearance', family, gap)
    return dict(start_chunk=[x//16,z//16], centre=[x,base+9,z], footprint=[235,235],
                bounds=[x0,base,z0,x0+234,base+47,z0+234], tiles=proofs,
                verified_samples=sum(p['sampled'] for p in proofs), foundation_columns=9,
                nearby_start_clearance=gaps, clearance_scope='starts within loaded 16x16 chunks')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default='-5876049240305171930')
    parser.add_argument('--world', default='validation-natural-castle-20261018')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--jar', type=Path, help='Test a built candidate JAR without changing the installed mod')
    args = parser.parse_args()
    if args.verify_only:
        report = json.loads(REPORT.read_text())
    else:
        server = (ROOT / 'server').resolve()
        assert not (server / args.world).exists(), 'Use a new disposable world'
        for name in run_server.MIRROR:
            target = (server / name).resolve()
            assert target.is_relative_to(server) and target != server
        previous = set(server.glob('console-*.log'))
        props = server / 'server.properties'
        old = props.read_bytes()
        plan = Plan(previous)
        mirror = run_server.mirror_instance
        if args.jar:
            candidate = args.jar.resolve()
            assert candidate.is_file(), candidate
            def mirror_candidate():
                count = mirror()
                shutil.copyfile(candidate, server / 'mods/alfheim_companion-0.2.0.jar')
                return count
            run_server.mirror_instance = mirror_candidate
        try:
            code = run_server.run(args.seed, args.world, 8, plan, 600)
        finally:
            props.write_bytes(old)
            run_server.mirror_instance = mirror
        consoles = set(server.glob('console-*.log'))-previous
        assert consoles, f'Server did not launch; harness exit {code}'
        console = max(consoles, key=lambda p:p.stat().st_mtime)
        report = dict(status='PENDING_CENSUS' if code == 0 else 'RUNTIME_FAILED', world=args.world, seed=args.seed, site=plan.site,
                      console=str(console.relative_to(ROOT)), exit_code=code,ground_sites=plan.ground_sites,
                      tested_jar_sha256=hashlib.sha256((server/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest())
        REPORT.write_text(json.dumps(report, indent=2)+'\n')
    assert report['exit_code'] == 0, report
    log = (ROOT / report['console']).read_text(errors='replace')
    assert 'Generated structure "alfheim:royal_castle"' not in log, 'Forced placement invalidates natural proof'
    report['proof'] = verify(report['world'], report['site'])
    report.update(status='VERIFIED_IN_GAME', minecraft='1.20.1', forge='47.4.10',
                  method='native world generation; locate then load chunks; no place command',
                  installed_jar_sha256=hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest(),
                  visual_review='pending client inspection', player_saves_modified=False)
    REPORT.write_text(json.dumps(report, indent=2)+'\n')
    print('NATURAL CASTLE PASS:', report['proof']['centre'], report['proof']['verified_samples'], flush=True)


if __name__ == '__main__':
    main()
