"""Read a save and answer one question: did the player actually wake in Alfheim?

This exists because the project already got this wrong once. `02_spawn_dimension.js` printed
"sent to mythicbotany:alfheim (first join)" and that line was recorded as a passed check --
but it is a `console.info` fired unconditionally after the commands are issued, and the player
was standing in Midgard the whole time (B-44). A script's statement about itself is intent, not
outcome.

So this asks the save instead:

  S1  the player's current dimension is the home dimension
  S2  the player's RESPAWN dimension is the home dimension -- dying bedless must not drop them
      into Midgard before the gate opens in Era VI
  S3  the home dimension actually generated chunks
  S4  the spawn flag latched, and it is the verifying one -- a v1 flag means the old script
      recorded success it never observed
  S5  MythicBotany's `lockAlfheim` is off, and no player is carrying its blindness

S5 is not a spawn bug but it is a spawn *consequence*, which is why it lives here. MythicBotany
ships `lockAlfheim: true`: "players that manage to get to alfheim via another mod but have not
drunk the mead of kvasir should get a blindness effect". That guard exists to stop people skipping
progression to reach Alfheim early — and this pack puts the player there on first join by design,
so the guard fires on the intended path and blinds them permanently. The symptom is continuous
blindness with a ~3 second duration, reapplied forever, `Ambient: 1`, particles hidden; nothing in
the log mentions it. Left undiagnosed it reads as a rendering fault, not a config toggle.

    python tools/check_spawn.py                       # newest save
    python tools/check_spawn.py "saves/New World"     # a specific save
    python tools/check_spawn.py --all
"""
import argparse
import glob
import gzip
import os
import struct

HOME_DIMENSION = 'mythicbotany:alfheim'
HOME_REGION_DIR = os.path.join('dimensions', 'mythicbotany', 'alfheim', 'region')
GOOD_FLAG = 'alfheim_home_spawn_v2'
STALE_FLAG = 'alfheim_home_spawn_v1'

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BARR, STR, LIST, COMP, IARR, LARR = range(13)


class Reader:
    def __init__(self, data):
        self.d, self.i = data, 0

    def take(self, n):
        b = self.d[self.i:self.i + n]
        self.i += n
        return b

    def u1(self):
        return self.take(1)[0]

    def string(self):
        n = struct.unpack('>H', self.take(2))[0]
        return self.take(n).decode('utf-8', 'replace')

    def payload(self, t):
        if t == BYTE:   return struct.unpack('>b', self.take(1))[0]
        if t == SHORT:  return struct.unpack('>h', self.take(2))[0]
        if t == INT:    return struct.unpack('>i', self.take(4))[0]
        if t == LONG:   return struct.unpack('>q', self.take(8))[0]
        if t == FLOAT:  return struct.unpack('>f', self.take(4))[0]
        if t == DOUBLE: return struct.unpack('>d', self.take(8))[0]
        if t == BARR:
            n = struct.unpack('>i', self.take(4))[0]
            return self.take(n)
        if t == STR:    return self.string()
        if t == LIST:
            et = self.u1()
            n = struct.unpack('>i', self.take(4))[0]
            return [self.payload(et) for _ in range(n)] if n > 0 else []
        if t == COMP:
            out = {}
            while True:
                nt = self.u1()
                if nt == END:
                    return out
                # Name before payload, in two statements. `out[self.string()] = self.payload(nt)`
                # evaluates the right-hand side FIRST and desynchronises the whole stream -- the
                # bug that made this file unreadable while B-44 was being diagnosed.
                name = self.string()
                out[name] = self.payload(nt)
        if t == IARR:
            n = struct.unpack('>i', self.take(4))[0]
            self.take(4 * n)
            return '<int[%d]>' % n
        if t == LARR:
            n = struct.unpack('>i', self.take(4))[0]
            self.take(8 * n)
            return '<long[%d]>' % n
        raise ValueError('unknown tag %d at byte %d' % (t, self.i))


def load(path):
    raw = open(path, 'rb').read()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    r = Reader(raw)
    t = r.u1()
    r.string()
    return r.payload(t)


MB_CONFIG = os.path.join('config', 'mythicbotany.json5')


def read_lock_alfheim():
    """True / False / None. Read textually -- it is JSON5 with comments, not JSON."""
    if not os.path.exists(MB_CONFIG):
        return None
    with open(MB_CONFIG, encoding='utf-8') as fh:
        for line in fh:
            stripped = line.split('//')[0]
            if '"lockAlfheim"' in stripped:
                if 'true' in stripped:
                    return True
                if 'false' in stripped:
                    return False
    return None


def check(save):
    problems = []
    print('\n=== %s ===' % save)

    players = sorted(glob.glob(os.path.join(save, 'playerdata', '*.dat')))
    if not players:
        print('  no playerdata -- the world has never been joined, nothing to check')
        return None

    for path in players:
        who = os.path.basename(path)[:8]
        try:
            d = load(path)
        except Exception as e:
            problems.append(('S0', '%s unreadable: %s' % (who, e)))
            print('  %s  UNREADABLE: %s' % (who, e))
            continue

        dim = d.get('Dimension')
        spawn_dim = d.get('SpawnDimension')
        pos = [round(x) for x in d.get('Pos', []) if isinstance(x, float)]
        flags = dict(d.get('KubeJSPersistentData') or {})

        print('  player %s' % who)
        print('     Dimension        %s' % dim)
        print('     Pos              %s' % pos)
        print('     SpawnDimension   %s' % spawn_dim)
        print('     SpawnForced      %s' % d.get('SpawnForced'))
        print('     spawn flags      %s' % ({k: v for k, v in flags.items() if 'spawn' in k}
                                            or '(none)'))

        if dim != HOME_DIMENSION:
            problems.append(('S1', '%s is in %s, not %s' % (who, dim, HOME_DIMENSION)))
        if spawn_dim != HOME_DIMENSION:
            problems.append(('S2', '%s respawns into %s, not %s -- dying bedless drops them in '
                                   'Midgard before the gate' % (who, spawn_dim, HOME_DIMENSION)))
        if not flags.get(GOOD_FLAG):
            if flags.get(STALE_FLAG):
                problems.append(('S4', '%s carries only %s -- set by the old script, which '
                                       'recorded success it never observed (B-44)'
                                 % (who, STALE_FLAG)))
            else:
                problems.append(('S4', '%s has no %s -- the handler never confirmed an arrival'
                                 % (who, GOOD_FLAG)))

        for effect in (d.get('ActiveEffects') or d.get('active_effects') or []):
            if not isinstance(effect, dict):
                continue
            if effect.get('forge:id') == 'minecraft:blindness' or effect.get('Id') == 15:
                problems.append(('S5', '%s is blinded (duration %s, ambient %s) -- if this keeps '
                                       'coming back, it is MythicBotany lockAlfheim, not a bug in '
                                       'the pack' % (who, effect.get('Duration'),
                                                     effect.get('Ambient'))))

    lock = read_lock_alfheim()
    print('  mythicbotany lockAlfheim: %s' % ('MISSING' if lock is None else lock))
    if lock is True:
        problems.append(('S5', 'lockAlfheim is true in config/mythicbotany.json5 -- it blinds any '
                               'player who reaches Alfheim without the Mead of Kvasir, which is '
                               'every player in this pack, on the intended path'))

    region_dir = os.path.join(save, HOME_REGION_DIR)
    n_home = len(glob.glob(os.path.join(region_dir, '*.mca')))
    n_over = len(glob.glob(os.path.join(save, 'region', '*.mca')))
    print('  chunks: %s -> %d region file(s), minecraft:overworld -> %d'
          % (HOME_DIMENSION, n_home, n_over))
    if n_home == 0:
        problems.append(('S3', '%s generated no chunks at all' % HOME_DIMENSION))

    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('save', nargs='?', help='path to a save folder (default: the newest)')
    ap.add_argument('--all', action='store_true', help='check every save')
    a = ap.parse_args()

    saves = sorted(glob.glob(os.path.join('saves', '*')), key=os.path.getmtime, reverse=True)
    saves = [s for s in saves if os.path.isdir(s)]
    if not saves:
        print('no saves found')
        return 2

    if a.save:
        targets = [a.save.rstrip('/\\')]
    elif a.all:
        targets = saves
    else:
        targets = saves[:1]

    total = []
    checked = 0
    for s in targets:
        result = check(s)
        if result is None:
            continue
        checked += 1
        total.extend((s, code, msg) for code, msg in result)

    print('\n' + '=' * 68)
    if not checked:
        print('RESULT: no joined save to check -- create a world and join it')
        return 0
    for s, code, msg in total:
        print('  %s  %s  [%s]' % (code, msg, s))
    print('RESULT: %d problem(s) across %d save(s)' % (len(total), checked))
    return 1 if total else 0


if __name__ == '__main__':
    raise SystemExit(main())
