"""Dump a player's inventory from a Minecraft save, without external NBT libraries.

Used to establish what mods actually hand the player at spawn, rather than inferring it
from configs. Reads level.dat-style gzipped NBT.

    python tools/read_player_inventory.py "saves/New World/playerdata/<uuid>.dat"
    python tools/read_player_inventory.py            # scans every save
"""
import glob
import gzip
import struct
import sys

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = 9, 10, 11, 12


class Reader:
    def __init__(self, data):
        self.d = data
        self.i = 0

    def take(self, n):
        b = self.d[self.i:self.i + n]
        self.i += n
        return b

    def u1(self):  return self.take(1)[0]
    def i1(self):  return struct.unpack('>b', self.take(1))[0]
    def i2(self):  return struct.unpack('>h', self.take(2))[0]
    def u2(self):  return struct.unpack('>H', self.take(2))[0]
    def i4(self):  return struct.unpack('>i', self.take(4))[0]
    def i8(self):  return struct.unpack('>q', self.take(8))[0]
    def f4(self):  return struct.unpack('>f', self.take(4))[0]
    def f8(self):  return struct.unpack('>d', self.take(8))[0]

    def string(self):
        return self.take(self.u2()).decode('utf-8', 'replace')

    def payload(self, t):
        if t == TAG_BYTE:   return self.i1()
        if t == TAG_SHORT:  return self.i2()
        if t == TAG_INT:    return self.i4()
        if t == TAG_LONG:   return self.i8()
        if t == TAG_FLOAT:  return self.f4()
        if t == TAG_DOUBLE: return self.f8()
        if t == TAG_BYTE_ARRAY: return self.take(self.i4())
        if t == TAG_STRING: return self.string()
        if t == TAG_LIST:
            it, n = self.u1(), self.i4()
            return [self.payload(it) for _ in range(max(0, n))]
        if t == TAG_COMPOUND:
            out = {}
            while True:
                nt = self.u1()
                if nt == TAG_END:
                    return out
                # Read the NAME before the payload, in two statements. `out[self.string()] =
                # self.payload(nt)` looks equivalent and is not: Python evaluates the right-hand
                # side first, so the payload gets read from the bytes where the name lives and
                # the whole stream desynchronises. It surfaces later as a bogus
                # `unknown tag <n>` deep in the file, which is why this looked like an
                # unsupported modded tag rather than a reader bug.
                name = self.string()
                out[name] = self.payload(nt)
        if t == TAG_INT_ARRAY:  return [self.i4() for _ in range(self.i4())]
        if t == TAG_LONG_ARRAY: return [self.i8() for _ in range(self.i4())]
        raise ValueError(f'unknown tag {t} at {self.i}')


def load(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    r = Reader(raw)
    t = r.u1()
    r.string()                       # root name
    return r.payload(t)


def describe(stack):
    sid = stack.get('id', '?')
    n = stack.get('Count', stack.get('count', 1))
    slot = stack.get('Slot')
    extra = ''
    tag = stack.get('tag') or {}
    if 'patchouli:book' in tag:
        extra = f"  [patchouli book: {tag['patchouli:book']}]"
    elif 'ftbquests:book' in tag or 'Book' in tag:
        extra = '  [quest book]'
    return f"  slot {str(slot):>3}  x{n:<3} {sid}{extra}"


def report(path):
    root = load(path)
    data = root.get('') if isinstance(root.get(''), dict) else root
    print(f'=== {path} ===')
    for key in ('Inventory', 'EnderItems'):
        items = data.get(key) or []
        print(f'  --- {key}: {len(items)} stack(s) ---')
        for st in items:
            if isinstance(st, dict):
                print(describe(st))
    ft = data.get('ForgeCaps') or {}
    if ft:
        print(f'  --- ForgeCaps keys: {len(ft)} ---')
        for k in sorted(ft)[:25]:
            print(f'      {k}')
    print()


def main():
    paths = sys.argv[1:] or glob.glob('saves/*/playerdata/*.dat')
    if not paths:
        print('no player data found')
        return 1
    for p in paths:
        if p.endswith('_old'):
            continue
        try:
            report(p)
        except Exception as e:
            print(f'{p}: FAILED — {type(e).__name__}: {e}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
