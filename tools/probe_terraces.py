"""Read a generated world's region files and measure what the terracing actually did.

Two numbers, both read from chunks the game built rather than from the density function:

  ON-TREAD SHARE   the fraction of a biome's surface columns whose Y falls on one residue
                   mod STEP. A uniform surface gives 1/STEP; higher means the terracing is
                   pinning columns to tread lines.

  DEEP VOID SHARE  the fraction of air in the deep band, per SURFACE biome. This is the one
                   that caught the 2026-09-09 regression: the terrace sawtooth held a constant
                   -0.5 below its band instead of returning to zero, so it subtracted density
                   through 118 blocks of rock that a surface feature has no business touching.
                   Golden Fields read 42.2% void against 25.3% under Dreamwood Forest.

ON-TREAD SHARE IS NOT A TARGET, AND B-86 LEARNED THAT THE EXPENSIVE WAY. It rises as EVERY
column gets quantised, so it cannot tell terracing from a staircase; the amplitude was tuned
up against it until the result read as stacked floors.

AND IT HAS NO MEANINGFUL ZERO, WHICH COST A SECOND CALIBRATION CYCLE. Terrain that was never
terraced at all still returns roughly 1/STEP, and on real terrain it returns rather more than
that -- Golden Fields reads 27.8% with the addend removed entirely. A reading of 27.7% was
taken as "gentle terracing" on 2026-09-09 and it was the feature contributing nothing: a
baseline world on the same seed matched it to a tenth of a point on this number and to two
decimals on the deep-void share.

SO ALWAYS READ THIS AGAINST A BASELINE WORLD, never against the previous treatment:

    python tools/run_terrace_validation.py --mode treatment
    python tools/run_terrace_validation.py --mode baseline
    python tools/probe_terraces.py server/terrace-treatment-<stamp>/dimensions/... --deep
    python tools/probe_terraces.py server/terrace-baseline-<stamp>/dimensions/... --deep

What matters is the DELTA between them, per biome: it should be clearly positive in Golden
Fields, zero in Silverbark Wood and Dreamwood Forest, and zero in the deep band everywhere.
"""
import argparse
import collections
import glob
import gzip
import io
import os
import struct
import sys
import zlib

MIN_Y = -64
STEP = 4
# Below the terrace band, where a surface feature must leave no trace at all.
DEEP_LO, DEEP_HI = -64, 48
AIRISH = {'minecraft:air', 'minecraft:cave_air', 'minecraft:water', 'minecraft:lava'}


# --- the smallest NBT reader that can read a chunk ---------------------------------------------
def read_nbt(buf):
    f = io.BytesIO(buf)

    def u1():
        return f.read(1)[0]

    def u2():
        return struct.unpack('>H', f.read(2))[0]

    def s():
        return f.read(u2()).decode('utf-8', 'replace')

    def payload(t):
        if t == 1:
            return struct.unpack('>b', f.read(1))[0]
        if t == 2:
            return struct.unpack('>h', f.read(2))[0]
        if t == 3:
            return struct.unpack('>i', f.read(4))[0]
        if t == 4:
            return struct.unpack('>q', f.read(8))[0]
        if t == 5:
            return struct.unpack('>f', f.read(4))[0]
        if t == 6:
            return struct.unpack('>d', f.read(8))[0]
        if t == 7:
            return f.read(struct.unpack('>i', f.read(4))[0])
        if t == 8:
            return s()
        if t == 9:
            it = u1()
            n = struct.unpack('>i', f.read(4))[0]
            return [payload(it) for _ in range(n)] if n > 0 else []
        if t == 10:
            out = {}
            while True:
                tt = u1()
                if tt == 0:
                    return out
                # The name MUST be read before the payload. Writing `out[s()] = payload(tt)`
                # evaluates the payload first and desynchronises the stream.
                key = s()
                out[key] = payload(tt)
        if t == 11:
            n = struct.unpack('>i', f.read(4))[0]
            return list(struct.unpack('>%di' % n, f.read(4 * n)))
        if t == 12:
            n = struct.unpack('>i', f.read(4))[0]
            return list(struct.unpack('>%dq' % n, f.read(8 * n)))
        raise ValueError('tag %d' % t)

    t = u1()
    if t == 0:
        return None
    s()
    return payload(t)


def unpack_bits(longs, bits, count):
    """1.16+ packing: entries never span a long."""
    per, mask, out = 64 // bits, (1 << bits) - 1, []
    for value in longs:
        value &= 0xFFFFFFFFFFFFFFFF
        for k in range(per):
            if len(out) >= count:
                return out
            out.append((value >> (k * bits)) & mask)
    return out


def chunks(path):
    with open(path, 'rb') as fh:
        header = fh.read(4096)
        if len(header) < 4096:
            return []
        fh.read(4096)
        data = fh.read()
    out = []
    for i in range(1024):
        off = int.from_bytes(header[i * 4:i * 4 + 3], 'big')
        count = header[i * 4 + 3]
        if not off or not count:
            continue
        start = off * 4096 - 8192
        if start < 0 or start + 5 > len(data):
            continue
        try:
            raw = data[start:start + count * 4096]
            length = int.from_bytes(raw[0:4], 'big')
            comp = raw[4]
            if length <= 1 or length - 1 > len(raw) - 5:
                continue
            body = raw[5:4 + length]
            body = zlib.decompress(body) if comp == 2 else gzip.decompress(body) if comp == 1 else None
            if body is None:
                continue
            out.append(read_nbt(body))
        except Exception:
            continue
    return out


# --- the measurement ---------------------------------------------------------------------------
def biome_at(sections, top_y, x, z):
    for s_ in sections:
        if s_.get('Y') != top_y >> 4:
            continue
        b = s_.get('biomes')
        if not b:
            return None
        pal = b.get('palette') or []
        if not pal:
            return None
        if len(pal) == 1:
            return pal[0]
        bits = max(1, (len(pal) - 1).bit_length())
        arr = unpack_bits(b.get('data'), bits, 64)
        i = ((top_y & 15) >> 2) * 16 + ((z >> 2) * 4) + (x >> 2)
        return pal[arr[i]] if i < len(arr) and arr[i] < len(pal) else pal[0]
    return None


def section_blocks(sec):
    bs = sec.get('block_states')
    if not bs:
        return None
    pal = bs.get('palette') or []
    if not pal:
        return None
    names = [p.get('Name', '') for p in pal]
    if len(pal) == 1:
        return [names[0]] * 4096
    bits = max(4, (len(pal) - 1).bit_length())
    return [names[i] if i < len(names) else names[0]
            for i in unpack_bits(bs.get('data'), bits, 4096)]


def step_signature(region_dir, step=STEP, minimum=3000):
    """THE MEASUREMENT ON-TREAD SHARE COULD NEVER MAKE, AND IT HAS A REAL ZERO.

    On-tread share saturates and returns ~27.8% on terrain nobody touched, which is how a build
    contributing nothing was read as "gentle terracing" on 2026-09-09. This looks instead for the
    structural signature of a staircase: the histogram of height jumps between adjacent columns,
    restricted to ground that is ALREADY SLOPING, where a terrace has no business being.

    A sawtooth of tread height N puts a spike at exactly N in that histogram. Smooth terrain
    decays monotonically through it. And the zero is measured, not assumed: every biome whose
    terrace weight is provably 0.000 supplies the background rate for the same bucket, so
    "how much of the spike is the feature" is a subtraction rather than a judgement.

    Measured 2026-09-11 on `New World yellowhome` at AMPLITUDE 0.30: golden_fields 9.0% at a jump
    of exactly 4 against a 1.6..2.2% background in dreamwood_forest, alfheim_hills and
    starved_reach, with 57.7% of its sloping pairs flat against their 33..38%.
    """
    top, bio = {}, {}
    for path in sorted(glob.glob(os.path.join(region_dir, '*.mca'))):
        for ch in chunks(path):
            if not ch:
                continue
            hm = (ch.get('Heightmaps') or {}).get('WORLD_SURFACE')
            secs = ch.get('sections') or []
            cx, cz = ch.get('xPos'), ch.get('zPos')
            if not hm or cx is None:
                continue
            vals = unpack_bits(hm, 9, 256)
            for idx in range(256):
                z, x = divmod(idx, 16)
                t = vals[idx] + MIN_Y - 1
                b = biome_at(secs, max(t, MIN_Y), x, z)
                if b:
                    top[(cx * 16 + x, cz * 16 + z)] = t
                    bio[(cx * 16 + x, cz * 16 + z)] = b
    hist = collections.defaultdict(collections.Counter)
    for (x, z), t in top.items():
        b = bio[(x, z)]
        far = top.get((x + 16, z))
        # sloping only: a terrace on ground that was already flat is a field, not a staircase
        if far is None or bio.get((x + 16, z)) != b or abs(far - t) < 5:
            continue
        for d in range(16):
            a, c = top.get((x + d, z)), top.get((x + d + 1, z))
            if a is None or c is None or bio.get((x + d + 1, z)) != b:
                break
            hist[b][min(abs(c - a), 12)] += 1
    rows = []
    for b, h in hist.items():
        n = sum(h.values())
        if n >= minimum:
            rows.append((100 * h[step] / n, 100 * h[0] / n, n, b))
    if not rows:
        print('no biome had %d sloping pairs' % minimum)
        return 1
    rows.sort(reverse=True)
    background = sorted(r[0] for r in rows)[len(rows) // 2]
    print('jump of exactly %d between adjacent columns, on sloping ground only' % step)
    print('%-30s %9s %9s %9s' % ('biome', 'at %d' % step, 'flat', 'pairs'))
    for spike, flat, n, b in rows:
        mark = '   <-- %+.1f points over background' % (spike - background) if spike > background * 2 else ''
        print('%-30s %8.1f%% %8.1f%% %9d%s' % (b.split(':')[-1], spike, flat, n, mark))
    print()
    print('background (median biome): %.1f%% -- biomes with no terrace weight cannot be '
          'terraced, so this is the real zero' % background)
    return 0


def pin_excess(treatment_dir, control_dir, biome='mythicbotany:golden_fields', step=STEP):
    """THE FIRST TERRACE METRIC IN THIS PROJECT WITH A CONTROL THAT MEANS ANYTHING.

    Both previous instruments failed, in opposite directions and for the same reason -- no zero:

      on-tread share  saturates. It returns ~27.8% on terrain nobody touched, which is how a
                      build contributing literally nothing was accepted as "gentle terracing".
      flat-on-slope   is INSENSITIVE. Halving the amplitude from 0.30 to 0.12 moved it from
                      42.7% to 42.6%, and reading that alone would say the amplitude does
                      nothing at all.

    This compares the SAME COLUMNS in a treatment world and a control world generated on the
    same seed, and reports how far the surface has been pinned onto one residue mod `step`
    beyond where the control already sat. The control supplies the zero by construction, and the
    response is monotonic in amplitude -- measured 2026-09-11 over 1,008 Golden Fields columns:

        control          20.3% on residue 0        excess   0.0
        amplitude 0.12   35.1%                     excess +14.8
        amplitude 0.30   52.2%                     excess +31.9

    Build the control by replacing alfheim_final with upstream's own
    min(alfheim_initial, alfheim_caves) and generating on the same seed.
    """
    def heights(region_dir):
        out = {}
        for path in sorted(glob.glob(os.path.join(region_dir, '*.mca'))):
            for ch in chunks(path):
                if not ch or ch.get('Status') != 'minecraft:full':
                    continue
                hm = (ch.get('Heightmaps') or {}).get('WORLD_SURFACE')
                secs = ch.get('sections') or []
                cx, cz = ch.get('xPos'), ch.get('zPos')
                if not hm or cx is None:
                    continue
                vals = unpack_bits(hm, 9, 256)
                for idx in range(256):
                    z, x = divmod(idx, 16)
                    t = vals[idx] + MIN_Y - 1
                    if biome_at(secs, max(t, MIN_Y), x, z) == biome:
                        out[(cx * 16 + x, cz * 16 + z)] = t
        return out
    treat, ctrl = heights(treatment_dir), heights(control_dir)
    common = set(treat) & set(ctrl)
    if len(common) < 200:
        print('only %d columns of %s in both worlds; need the same seed and overlapping sites'
              % (len(common), biome))
        return 1
    tr = collections.Counter(treat[k] % step for k in common)
    co = collections.Counter(ctrl[k] % step for k in common)
    n = len(common)
    residue = max(range(step), key=lambda r: tr[r])
    excess = 100 * (tr[residue] - co[residue]) / n
    print('%s, %d columns shared with the control' % (biome, n))
    print()
    print('%-12s %s' % ('world', ' '.join('res %d' % r for r in range(step))))
    print('%-12s %s' % ('control', ' '.join('%5.1f%%' % (100 * co[r] / n) for r in range(step))))
    print('%-12s %s' % ('treatment', ' '.join('%5.1f%%' % (100 * tr[r] / n) for r in range(step))))
    print()
    print('terraced onto residue %d: %+.1f points over the control' % (residue, excess))
    print('  0 means the feature is doing nothing; the 2026-09-11 stacked-floor build read +31.9')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('region_dir')
    ap.add_argument('--min-columns', type=int, default=400)
    ap.add_argument('--pin', metavar='CONTROL_REGION_DIR',
                    help='terrace pinning against a control world on the same seed')
    ap.add_argument('--steps', action='store_true',
                    help='staircase signature: jump histogram on sloping ground, against the '
                         'background rate from biomes that cannot be terraced')
    ap.add_argument('--deep', action='store_true',
                    help='also read block states for the deep-void share (much slower)')
    a = ap.parse_args()
    if a.pin:
        return pin_excess(a.region_dir, a.pin)
    if a.steps:
        return step_signature(a.region_dir)

    residues = collections.defaultdict(collections.Counter)
    heights = collections.defaultdict(list)
    deep = collections.defaultdict(collections.Counter)
    read = 0

    for p in sorted(glob.glob(os.path.join(a.region_dir, '*.mca'))):
        for ch in chunks(p):
            if not ch:
                continue
            hm = (ch.get('Heightmaps') or {}).get('WORLD_SURFACE')
            secs = ch.get('sections') or []
            if not hm:
                continue
            vals = unpack_bits(hm, 9, 256)
            read += 1
            for idx in range(0, 256, 4):
                top = vals[idx] + MIN_Y - 1
                z, x = divmod(idx, 16)
                bi = biome_at(secs, top, x, z)
                if not bi:
                    continue
                residues[bi][top % STEP] += 1
                heights[bi].append(top)
            if a.deep:
                # PER COLUMN, NOT PER CHUNK. Attributing a whole chunk to the biome under its
                # centre column threw away every chunk whose centre happened to miss -- which
                # is most of them for a fragmented biome, and it is exactly why Golden Fields
                # fell under the reporting threshold on 2026-09-09 and its deep-void share went
                # unmeasured after the repair. Each column now carries its own surface biome.
                col_biome = [None] * 256
                for idx in range(256):
                    z, x = divmod(idx, 16)
                    col_biome[idx] = biome_at(secs, vals[idx] + MIN_Y - 1, x, z)
                for s_ in secs:
                    y0 = s_.get('Y', 0) * 16
                    if y0 < DEEP_LO or y0 > DEEP_HI:
                        continue
                    blocks = section_blocks(s_)
                    if blocks is None:
                        continue
                    for i, name in enumerate(blocks):
                        bi = col_biome[(i & 255)]
                        if not bi:
                            continue
                        c = deep[bi]
                        c['n'] += 1
                        if name in AIRISH:
                            c['air'] += 1
                        if name == 'minecraft:lava':
                            c['lava'] += 1

    print(f'chunks read: {read}   uniform baseline: {100 / STEP:.0f}%\n')
    print(f"{'biome':38s} {'cols':>7} {'peak':>7} {'enrich':>7} {'medY':>6}")
    rows = []
    for b, c in residues.items():
        n = sum(c.values())
        if n < a.min_columns:
            continue
        peak = max(c[r] / n for r in range(STEP))
        hs = sorted(heights[b])
        rows.append((peak, b, n, hs[len(hs) // 2]))
    for peak, b, n, med in sorted(rows, reverse=True):
        print(f'{b:38s} {n:7d} {peak * 100:6.1f}% {peak / (1 / STEP):6.2f}x {med:6d}')

    if a.deep:
        print(f"\n{'surface biome':38s} {'blocks':>12} {'deep void':>10} {'lava':>8}")
        for b, c in sorted(deep.items(), key=lambda kv: -kv[1]['air'] / max(1, kv[1]['n'])):
            if c['n'] < 50000:
                continue
            print(f"{b:38s} {c['n']:12d} {100 * c['air'] / c['n']:9.2f}% "
                  f"{100 * c['lava'] / c['n']:7.3f}%")


if __name__ == '__main__':
    sys.exit(main())
