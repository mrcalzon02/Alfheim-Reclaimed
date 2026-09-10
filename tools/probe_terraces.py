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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('region_dir')
    ap.add_argument('--min-columns', type=int, default=400)
    ap.add_argument('--deep', action='store_true',
                    help='also read block states for the deep-void share (much slower)')
    a = ap.parse_args()

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
