"""Count the biomes that a world ACTUALLY generated, read from its region files.

    python tools/biome_census.py                       # both dimensions of server/validation
    python tools/biome_census.py --world saves/"New World (1)"
    python tools/biome_census.py --dim overworld --top 40

WHY THIS EXISTS
---------------
Reported by the user 2026-09-04: *"Overall still had vanilla biomes not continuity works."*

Every instrument short of this one gave a misleading answer:

  * The mod list says Continuity Works and Regions Unexplored are installed. Installed is not
    generated.
  * TerraBlender logs `Registered region continuityworks_biomes:overworld_templates ... for type
    OVERWORLD` and `Initialized TerraBlender biomes for level stem minecraft:overworld`.
    Registered is not generated either.
  * `config/continuityworks-biomes-common.toml` has all 144 biomes enabled at `regionWeight = 20`,
    its maximum, and `config/terrablender.toml` sets `vanilla_overworld_region_weight = 0`.
    Configured is not generated.
  * `locate biome` reported "could not find within reasonable distance" for four CW biomes and
    one RU biome -- but its search radius is bounded and TerraBlender regions are large, so a
    miss is weak evidence and a hit from a *different* region proves nothing about weighting.

The region files are the ground truth. A chunk's `sections[].biomes.palette` is the list of
biomes the generator actually placed in that chunk, written by the server. Nothing sits between
that and the player.

This is the same lesson as `tools/registry_items.json`: when a claim matters, read what the game
wrote, not what something upstream said it would write.

WHAT IT MEASURES
----------------
Every chunk in every region file, every 4x4x4 biome cell, counted by biome id and grouped by
namespace. A namespace with zero cells is not generating, whatever the logs say about it.
"""
import argparse
import collections
import glob
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402

DEFAULT_WORLD = os.path.join('server', 'validation')

# Where each dimension keeps its regions inside a world folder.
DIMS = {
    'overworld': 'region',
    'nether': os.path.join('DIM-1', 'region'),
    'end': os.path.join('DIM1', 'region'),
    'alfheim': os.path.join('dimensions', 'mythicbotany', 'alfheim', 'region'),
}


def chunks(path):
    """Yield every chunk's root NBT compound from one .mca region file.

    Anvil layout: a 4 KiB location table of 1024 entries (3-byte sector offset, 1-byte sector
    count), a 4 KiB timestamp table, then the chunks themselves -- each a 4-byte big-endian
    length, a 1-byte compression id, and that many bytes of compressed NBT.
    """
    with open(path, 'rb') as f:
        header = f.read(4096)
        if len(header) < 4096:
            return
        for i in range(1024):
            off, cnt = struct.unpack('>I', header[i * 4:i * 4 + 4])[0] >> 8, header[i * 4 + 3]
            if off == 0 or cnt == 0:
                continue
            f.seek(off * 4096)
            head = f.read(5)
            if len(head) < 5:
                continue
            length, comp = struct.unpack('>I', head[:4])[0], head[4]
            payload = f.read(length - 1)
            try:
                if comp == 1:
                    import gzip as _gz
                    raw = _gz.decompress(payload)
                elif comp == 2:
                    raw = zlib.decompress(payload)
                elif comp == 3:
                    raw = payload
                else:
                    continue
            except Exception:
                continue
            try:
                r = nbt._Reader(raw)
                t = r.u1()
                r.string()
                yield r.payload(t)
            except Exception:
                continue


def census(region_dir):
    """(counter of biome id -> cells, number of FULL chunks read).

    ONLY `minecraft:full` chunks are counted, and that is not a refinement -- it is the
    difference between a true and a false answer. A region file is mostly proto-chunks: the
    first pass over a validation world found 945 chunks of which only 230 were full, the rest
    sitting at `structure_starts`, `biomes`, `carvers` or `initialize_light`. Their biome arrays
    are placeholder, and counting them reported ~55% `minecraft:plains` in BOTH the Overworld
    and Alfheim -- a dimension whose biome source is `libx:layered` and cannot contain plains at
    all. That impossible number is what exposed the bug; two dimensions agreeing on a figure
    they have no reason to share is a reader fault, not a finding.
    """
    counts = collections.Counter()
    n = 0
    skipped = 0
    for p in sorted(glob.glob(os.path.join(region_dir, '*.mca'))):
        for root in chunks(p):
            if str(root.get('Status', '')) != 'minecraft:full':
                skipped += 1
                continue
            n += 1
            for sec in root.get('sections', []):
                b = sec.get('biomes')
                if not isinstance(b, dict):
                    continue
                pal = b.get('palette') or []
                data = b.get('data')
                if data is None:
                    # A single-biome section stores only the palette entry, no index array.
                    if pal:
                        counts[str(pal[0])] += 64
                    continue
                # Packed indices. Cell count is fixed at 64 per section (4x4x4).
                bits = max(1, (len(pal) - 1).bit_length())
                per_long = 64 // bits
                mask = (1 << bits) - 1
                got = 0
                for word in data:
                    w = int(word) & 0xFFFFFFFFFFFFFFFF
                    for k in range(per_long):
                        if got >= 64:
                            break
                        idx = (w >> (k * bits)) & mask
                        if idx < len(pal):
                            counts[str(pal[idx])] += 1
                        got += 1
                    if got >= 64:
                        break
    return counts, n, skipped


def report(name, counts, n_chunks, top, skipped=0):
    total = sum(counts.values())
    print(f'\n{name}')
    print('=' * 74)
    if not total:
        print('  no chunks generated')
        return
    print(f'  {n_chunks} chunk(s), {total:,} biome cells, {len(counts)} distinct biome(s)\n')

    by_ns = collections.Counter()
    for bid, c in counts.items():
        by_ns[bid.split(':')[0]] += c
    print('  BY NAMESPACE -- this is the line that answers "is the mod generating?"')
    for ns, c in by_ns.most_common():
        print(f'    {ns:28} {c:>9,}  {100.0 * c / total:5.1f}%')

    print(f'\n  TOP {top} BIOMES')
    for bid, c in counts.most_common(top):
        print(f'    {bid:44} {c:>8,}  {100.0 * c / total:5.1f}%')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default=DEFAULT_WORLD)
    ap.add_argument('--dim', choices=sorted(DIMS) + ['all'], default='all')
    ap.add_argument('--top', type=int, default=15)
    ap.add_argument('--expect', action='append', default=[],
                    help='namespace that MUST appear; exits non-zero if it generated nothing')
    a = ap.parse_args()

    if not os.path.isdir(a.world):
        print(f'no such world: {a.world}')
        return 2

    wanted = sorted(DIMS) if a.dim == 'all' else [a.dim]
    seen = {}
    for d in wanted:
        rd = os.path.join(a.world, DIMS[d])
        if not os.path.isdir(rd):
            continue
        counts, n, skipped = census(rd)
        if n:
            report(f'{a.world}  ::  {d}', counts, n, a.top, skipped)
            seen[d] = counts

    missing = []
    for ns in a.expect:
        found = any(any(b.startswith(ns + ':') for b in c) for c in seen.values())
        print(f'\n  expect {ns:28} {"GENERATED" if found else "*** NOTHING GENERATED ***"}')
        if not found:
            missing.append(ns)
    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main())
