"""The shared structure-template builder: one `Piece`, used by every structure generator.

Extracted from `tools/gen_spawn_hub.py` on 2026-09-04 when `gen_surface_works.py` needed the
same class. Copying it would have been a parallel implementation of the pack's single most
load-bearing primitive -- the thing that decides whether a `.nbt` is placeable at all -- so it
moved here instead and `gen_spawn_hub.py` imports it. The extraction was proven by regenerating
the four spawn-hub pieces and comparing the DECOMPRESSED payloads: `gzip.compress` stamps the
current time into its header, so the `.nbt` files on disk are never byte-identical between runs
and comparing them directly would prove nothing.

The structure NBT format was read off MythicBotany's shipping `house.nbt` rather than assumed:
size / entities / blocks / palette / DataVersion, blocks as `{pos:[x,y,z], state:int}`, and
DataVersion 3465 for 1.20.1.

**The one fact worth knowing before extending a builder.** A position this class was never
asked to `set()` is absent from the block list, and a template does not touch what it does not
list -- so "leave the terrain alone" is the default and costs nothing. A position explicitly set
to `minecraft:air` IS placed, and overwrites whatever was there. That asymmetry is what makes a
crater or a quarry possible: they carve by writing air. (`minecraft:structure_void` is the third
case -- it is stripped by `BlockIgnoreProcessor.STRUCTURE_BLOCK` at placement time and behaves
like an omitted position, so there is no reason to write one.)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402

DATA_VERSION = 3465            # 1.20.1

# A structure block cannot save or place a piece larger than 48 on any axis. Data-loaded
# templates are not bound by the GUI, but staying inside the limit keeps every piece
# inspectable in-game with a structure block, which is how a pass-2 edit gets reviewed.
MAX_AXIS = 48

# JigsawStructure's codec validates `max_distance_from_center + margin <= 128`, where the
# margin is 0 for terrain_adaptation `none` and 12 for every other value.
ADAPTATION_MARGIN = {'none': 0, 'bury': 12, 'beard_thin': 12, 'beard_box': 12,
                     'encapsulate': 12}


class Piece:
    """A structure under construction. Deduplicates the palette and writes the NBT."""

    def __init__(self, sx, sy, sz):
        self.size = (sx, sy, sz)
        self.palette = []
        self._index = {}
        self.blocks = {}        # pos -> (state, nbt or None); a dict so later writes win
        self.entities = []
        # Every set() that fell outside the piece. A builder that draws a mast taller than its
        # own box loses the mast SILENTLY -- no error, no log, just a shorter structure that
        # still validates. Counting the misses turns that into a number a generator can print
        # and a checker can bound. Some overdraw is legitimate (a disc scans its bounding
        # square; rubble is scattered over a rectangle), so this is a diagnostic, not an
        # assertion -- but a builder whose drop count rivals its block count has clipped
        # something real.
        self.dropped = 0

    def _state(self, name, props):
        key = (name, tuple(sorted(props.items())) if props else None)
        if key not in self._index:
            self._index[key] = len(self.palette)
            entry = {'Name': name}
            if props:
                entry['Properties'] = dict(props)
            self.palette.append(entry)
        return self._index[key]

    def set(self, x, y, z, block, be=None):
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]):
            self.dropped += 1
            return False
        self.blocks[(x, y, z)] = (self._state(*block), be)
        return True

    def jigsaw(self, x, y, z, name, target, pool, orientation, joint='rollable',
               final_state='minecraft:air'):
        """A jigsaw block plus its block entity.

        `name` is what a parent's `target` must match; `pool` is where this jigsaw looks for
        the next piece. Getting these backwards is the classic way to build a structure that
        generates as a single orphaned block, so check_spawn_hub.py asserts every pair.
        """
        be = {'id': 'minecraft:jigsaw', 'name': name, 'target': target, 'pool': pool,
              'final_state': final_state, 'joint': joint}
        self.set(x, y, z, ('minecraft:jigsaw', {'orientation': orientation}), be)

    def to_nbt(self):
        blocks = []
        for (x, y, z), (state, be) in sorted(self.blocks.items()):
            e = {'pos': [nbt.Int(x), nbt.Int(y), nbt.Int(z)], 'state': nbt.Int(state)}
            if be:
                e['nbt'] = be
            blocks.append(e)
        return {
            'size': [nbt.Int(self.size[0]), nbt.Int(self.size[1]), nbt.Int(self.size[2])],
            'entities': self.entities,
            'blocks': blocks,
            'palette': self.palette,
            'DataVersion': nbt.Int(DATA_VERSION),
        }
