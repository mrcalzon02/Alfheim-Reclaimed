"""Eight architectural detail layers; deliberately no new clutter in circulation cells.

Used by the original district generators and the Continuity Works downstream provider.
Only full masonry/beam cells are changed. Carved air, sockets, fixtures, foundations,
floor elevations and the original bounding box remain authoritative.
"""
import os
from collections import Counter

AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:structure_void'}
MASONRY = {
    'alfheim:ivory_livingrock_bricks', 'alfheim:ivory_livingrock_polished',
    'feywild:elven_quartz_brick', 'feywild:elven_quartz_polished',
    'botania:livingrock_bricks', 'ars_nouveau:sourcestone',
}
LAYERS = ('plinth', 'pilaster', 'spandrel', 'opening_frame', 'frieze',
          'coffer', 'paving_inlay', 'beam_joinery')


def detail_nbt(piece, family, name):
    """Render eight geometric motifs from existing full block faces, not random noise.

    The baseline switch is confined to child generator processes in cw_district_refit.
    It supplies a reproducible before/after comparison without storing a second corpus.
    """
    if os.environ.get('ALFHEIM_DISTRICT_BASELINE') == '1':
        return piece.to_nbt()
    source = dict(piece.blocks)
    counts = Counter()
    # Ground is inferred from boundary sockets, with the original builders' bedding fallback.
    sockets = [pos[1] - 1 for pos, (idx, be) in source.items()
               if piece.palette[idx]['Name'] == 'minecraft:jigsaw']
    ground = min(sockets) if sockets else 8
    sx, sy, sz = piece.size

    def state(pos):
        value = source.get(pos)
        return piece.palette[value[0]] if value else {}

    def air(pos):
        return state(pos).get('Name') in AIR

    for (x, y, z), (idx, be) in sorted(source.items()):
        old = piece.palette[idx]
        block = old['Name']
        # Leave the edge strips and every utility/fixture intact; this includes socket decks.
        if be is not None or not (1 <= x < sx - 1 and 1 <= z < sz - 1):
            continue
        if block == 'botania:dreamwood_log' and y >= ground + 5:
            axis = old.get('Properties', {}).get('axis', 'y')
            along = {'x': x, 'y': y - ground, 'z': z}[axis]
            if along % 6 == 0:
                piece.set(x, y, z, ('botania:stripped_dreamwood_log', {'axis': axis}))
                counts['beam_joinery'] += 1
            continue
        if block not in MASONRY or y < ground:
            continue
        # Hydraulic basin walls are a functional material contract, not facade trim.
        if family == 'agricultural_estate' and name == 'water_garden' and y <= ground + 2:
            continue
        if family == 'scholastic_quarter' and name == 'astral_conservatory' and x == 33 and y == ground + 8 and 13 <= z <= 22:
            continue
        if family == 'roads_trade' and name == 'bridge_gate' and y == ground and 19 <= x <= 27 and 14 <= z <= 24:
            continue
        # Full-cube materials only: the collision envelope and walking surfaces stay identical.
        ivory = block.startswith('alfheim:')
        carved = 'alfheim:moonstone_livingrock_carved' if ivory else 'botania:chiseled_elf_quartz'
        pillar = 'alfheim:ivory_livingrock_polished' if ivory else 'feywild:elven_quartz_pillar'
        dark = 'botania:livingrock_bricks'
        dy = y - ground
        exposed = [face for face, dx, dz in (('north',0,-1),('south',0,1),
                                            ('west',-1,0),('east',1,0))
                   if air((x+dx,y,z+dz))]
        layer = replacement = None
        # Floor rosettes and framed aisle panels have an eight-block module, not scattered pixels.
        if dy == 0 and air((x,y+1,z)):
            if x % 8 in (0,1) or z % 8 in (0,1):
                layer, replacement = 'paving_inlay', carved if (x+z)%8 == 0 else dark
        elif exposed:
            face = exposed[0]
            u = x if face in ('north','south') else z
            if dy in (1,2):
                layer, replacement = 'plinth', dark
            elif u % 8 == 0:
                layer, replacement = 'pilaster', pillar
            elif any(state((x+dx,y,z+dz)).get('Name') in ('botania:elf_glass','minecraft:glass')
                     for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))) and dy >= 4:
                layer, replacement = 'opening_frame', carved
            elif dy % 6 == 0:
                layer, replacement = 'frieze', carved
            elif dy % 6 == 1 and u % 8 in (3,4):
                layer, replacement = 'spandrel', carved
        # Coffer soffits retain their solid roof and all pre-existing holes through it.
        if layer is None and dy >= 8 and air((x,y-1,z)) and (x%6 == 0 or z%6 == 0):
            layer, replacement = 'coffer', carved
        if layer and replacement != block:
            props = {'axis':'y'} if replacement.endswith('_pillar') else None
            piece.set(x,y,z,(replacement,props))
            counts[layer] += 1
        # Upper-wall mouldings add actual relief. Never consume a walking cell or its
        # four-block headroom, even on upper galleries/stairs; never project out of bounds.
        upper = 25 if family == 'frontier_stewardship' else 13
        courses = (5,8,11,13,16,19,22,25) if family == 'frontier_stewardship' else (5,8,11,13)
        if exposed and 5 <= dy <= upper:
            for face in exposed:
                u = x if face in ('north','south') else z
                if dy not in courses and u % 8 != 0:
                    continue
                dx,dz = {'north':(0,-1),'south':(0,1),'west':(-1,0),'east':(1,0)}[face]
                px,pz = x+dx,z+dz
                target = (px,y,pz)
                if not (2 <= px < sx-2 and 2 <= pz < sz-2):
                    continue
                if any(not air((px,y-down,pz)) for down in range(1,5)):
                    continue
                current = piece.blocks.get(target)
                if current is None or piece.palette[current[0]]['Name'] not in AIR:
                    continue
                stair = 'alfheim:ivory_livingrock_stairs' if ivory else 'feywild:elven_quartz_brick_stairs'
                piece.set(px,y,pz,(stair,{'facing':face,'half':'top','shape':'straight','waterlogged':'false'}))
                counts['upper_moulding'] += 1
    piece.refit_counts = dict(counts)
    return piece.to_nbt()
