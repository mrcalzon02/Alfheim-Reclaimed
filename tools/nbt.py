"""Minimal NBT read/write for Minecraft Java saves. No external dependencies.

Values map to Python as:
    TAG_Byte/Short/Int/Long -> Int(v) wrappers (to preserve width on write)
    TAG_Float/Double        -> Float(v)/Double(v)
    TAG_String              -> str
    TAG_List                -> list           (element type inferred from contents)
    TAG_Compound            -> dict
    TAG_Byte_Array          -> bytes
    TAG_Int_Array/Long_Array-> IntArray/LongArray

Wrappers exist because a bare Python int cannot say whether it is a byte or an int, and
level.dat round-trips break if the width changes.
"""
import gzip
import struct

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = 9, 10, 11, 12


class _Typed(int):
    tag = None
    def __new__(cls, v): return super().__new__(cls, v)

class Byte(_Typed):  tag = TAG_BYTE
class Short(_Typed): tag = TAG_SHORT
class Int(_Typed):   tag = TAG_INT
class Long(_Typed):  tag = TAG_LONG

class _TypedF(float):
    tag = None
    def __new__(cls, v): return super().__new__(cls, v)

class Float(_TypedF):  tag = TAG_FLOAT
class Double(_TypedF): tag = TAG_DOUBLE

class IntArray(list):  tag = TAG_INT_ARRAY
class LongArray(list): tag = TAG_LONG_ARRAY


# --------------------------------------------------------------------------- read

class _Reader:
    def __init__(self, d): self.d, self.i = d, 0
    def take(self, n):
        b = self.d[self.i:self.i + n]; self.i += n; return b
    def u1(self): return self.take(1)[0]
    def u2(self): return struct.unpack('>H', self.take(2))[0]
    def i4(self): return struct.unpack('>i', self.take(4))[0]
    def string(self): return self.take(self.u2()).decode('utf-8', 'replace')

    def payload(self, t):
        if t == TAG_BYTE:   return Byte(struct.unpack('>b', self.take(1))[0])
        if t == TAG_SHORT:  return Short(struct.unpack('>h', self.take(2))[0])
        if t == TAG_INT:    return Int(self.i4())
        if t == TAG_LONG:   return Long(struct.unpack('>q', self.take(8))[0])
        if t == TAG_FLOAT:  return Float(struct.unpack('>f', self.take(4))[0])
        if t == TAG_DOUBLE: return Double(struct.unpack('>d', self.take(8))[0])
        if t == TAG_BYTE_ARRAY: return self.take(self.i4())
        if t == TAG_STRING: return self.string()
        if t == TAG_LIST:
            it, n = self.u1(), self.i4()
            out = [self.payload(it) for _ in range(max(0, n))]
            if n <= 0:
                out = _EmptyList(it)
            return out
        if t == TAG_COMPOUND:
            out = {}
            while True:
                nt = self.u1()
                if nt == TAG_END:
                    return out
                # Read the name into a local FIRST. In `out[self.string()] = self.payload(nt)`
                # Python evaluates the right-hand side before the subscript, so the payload
                # would be consumed before its own name — silently desynchronising the stream.
                key = self.string()
                out[key] = self.payload(nt)
        if t == TAG_INT_ARRAY:
            n = self.i4()
            return IntArray(self.i4() for _ in range(n))
        if t == TAG_LONG_ARRAY:
            n = self.i4()
            return LongArray(struct.unpack('>q', self.take(8))[0] for _ in range(n))
        raise ValueError(f'unknown tag {t} at byte {self.i}')


class _EmptyList(list):
    """An empty TAG_List still has to declare its element type on write."""
    def __init__(self, elem_tag): super().__init__(); self.elem_tag = elem_tag


def load(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    r = _Reader(raw)
    t = r.u1()
    name = r.string()
    return name, r.payload(t)


# -------------------------------------------------------------------------- write

def _tag_of(v):
    if isinstance(v, _Typed):  return v.tag
    if isinstance(v, _TypedF): return v.tag
    if isinstance(v, bool):    return TAG_BYTE
    if isinstance(v, IntArray):  return TAG_INT_ARRAY
    if isinstance(v, LongArray): return TAG_LONG_ARRAY
    if isinstance(v, bytes):   return TAG_BYTE_ARRAY
    if isinstance(v, str):     return TAG_STRING
    if isinstance(v, dict):    return TAG_COMPOUND
    if isinstance(v, list):    return TAG_LIST
    if isinstance(v, int):     return TAG_INT
    if isinstance(v, float):   return TAG_DOUBLE
    raise TypeError(f'cannot infer NBT tag for {type(v).__name__}')


def _w_string(out, s):
    b = s.encode('utf-8')
    out += struct.pack('>H', len(b)); out += b


def _w_payload(out, t, v):
    if t == TAG_BYTE:   out += struct.pack('>b', int(v))
    elif t == TAG_SHORT: out += struct.pack('>h', int(v))
    elif t == TAG_INT:   out += struct.pack('>i', int(v))
    elif t == TAG_LONG:  out += struct.pack('>q', int(v))
    elif t == TAG_FLOAT: out += struct.pack('>f', float(v))
    elif t == TAG_DOUBLE: out += struct.pack('>d', float(v))
    elif t == TAG_BYTE_ARRAY:
        out += struct.pack('>i', len(v)); out += bytes(v)
    elif t == TAG_STRING: _w_string(out, v)
    elif t == TAG_LIST:
        if isinstance(v, _EmptyList) or not v:
            et = getattr(v, 'elem_tag', TAG_END)
            out += bytes([et]); out += struct.pack('>i', 0)
        else:
            et = _tag_of(v[0])
            out += bytes([et]); out += struct.pack('>i', len(v))
            for e in v: _w_payload(out, et, e)
    elif t == TAG_COMPOUND:
        for k, val in v.items():
            vt = _tag_of(val)
            out += bytes([vt]); _w_string(out, k); _w_payload(out, vt, val)
        out += bytes([TAG_END])
    elif t == TAG_INT_ARRAY:
        out += struct.pack('>i', len(v))
        for e in v: out += struct.pack('>i', int(e))
    elif t == TAG_LONG_ARRAY:
        out += struct.pack('>i', len(v))
        for e in v: out += struct.pack('>q', int(e))
    else:
        raise ValueError(f'cannot write tag {t}')


def save(path, name, root, compress=True):
    out = bytearray()
    out += bytes([TAG_COMPOUND]); _w_string(out, name)
    _w_payload(out, TAG_COMPOUND, root)
    data = bytes(out)
    if compress:
        data = gzip.compress(data)
    with open(path, 'wb') as f:
        f.write(data)


def roundtrip_ok(path):
    """Read, write to memory, read again, and confirm the structures match."""
    import io, tempfile, os
    name, root = load(path)
    fd, tmp = tempfile.mkstemp(suffix='.dat')
    os.close(fd)
    try:
        save(tmp, name, root)
        name2, root2 = load(tmp)
        return name == name2 and repr(root) == repr(root2)
    finally:
        os.unlink(tmp)
