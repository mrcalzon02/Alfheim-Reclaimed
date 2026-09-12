#!/usr/bin/env python3
"""Emit the terrain-authority selector: one density function per owner, chosen by the same
partition that chooses the biome.

WHY THIS CAN WORK WHEN B-82's CLIMATE-THRESHOLDED DENSITY COULD NOT. Multi-noise biome selection
is nearest-neighbour in climate space. With overlapping or gappy claims, "which biome" is a
distance computation and no density function can reproduce it -- which is exactly how B-82 stamped
Hills terrain into Plains and Silverbark and had to be reverted. But this pack's layer is a
DISJOINT COVERING PARTITION of axis-aligned boxes: 44 entries, zero overlapping pairs, 0.000% of
climate space uncovered. Every point therefore lies in exactly one box at distance zero, and
membership reduces to axis-aligned threshold tests, which minecraft:range_choice reproduces
exactly. The partition IS the selection; this file does not re-derive it.

See alfheim_reclaimed_design/TERRAIN_AUTHORITIES.md for the architecture and its contracts.

THE CHAIN IS EMITTED AS NAMED FUNCTIONS, NOT INLINE, AND THAT IS NOT TIDINESS. Each band's test
is up to five nested range_choices, and every one of their false branches has to reach the rest of
the chain. Written inline the tail repeats once per axis test and the document grows as 5^44. As
`alfheim:authority/step_N` each false branch is a string.

    python tools/gen_terrain_authorities.py            # write
    python tools/gen_terrain_authorities.py --dry-run  # print what would be written
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NS = 'alfheim'
PREFIX = 'kubejs/data/%s/worldgen/density_function/authority/' % NS

# The climate axes a band may constrain, and the density function that carries each. `depth` is
# deliberately absent: no claim in this pack constrains it, and it is the one axis that varies
# with Y, which would make the selector depend on height.
AXES = (
    ('temperature', 'mythicbotany:alfheim_temperature'),
    ('humidity', 'mythicbotany:alfheim_humidity'),
    ('continentalness', 'mythicbotany:alfheim_continentalness'),
    ('erosion', 'mythicbotany:alfheim_erosion'),
    ('weirdness', 'mythicbotany:alfheim_weirdness'),
)
FULL = (-1.0, 1.0)


def authorities():
    """Ordered owners. The LAST one is the fallback and must own the remainder.

    STAGE 1 DELIBERATELY CHANGES NO TERRAIN. Both leaves reference the same expression, so the
    selector is functionally a no-op and a generated world must match the current one exactly.
    The framework is proven before anything moves, so that a later regression cannot be confused
    with the migration. Stage 2 splits the expressions; see TERRAIN_AUTHORITIES.md section 5.
    """
    from gen_void_worldgen import VOID_IDS, COAST_ID
    return [
        {'id': 'void', 'biomes': set(VOID_IDS) | {COAST_ID},
         'note': 'the margin and the coast it ends against'},
        {'id': 'upstream', 'biomes': None,
         'note': 'everything else: MythicBotany\'s own terrain, plus what we add to it'},
    ]


def span(parameters, axis):
    value = parameters.get(axis)
    if isinstance(value, dict):
        return (float(value['min']), float(value['max']))
    if isinstance(value, (list, tuple)):
        return (float(value[0]), float(value[1]))
    return FULL


def owner_of(biome, owners):
    for authority in owners:
        if authority['biomes'] is not None and biome in authority['biomes']:
            return authority['id']
    return owners[-1]['id']


def test_chain(parameters, hit, miss):
    """Nested range_choices for one band. Axes that span the whole range are skipped, which is
    most of them -- it keeps each step small and makes the emitted files readable."""
    node = hit
    for axis, function in reversed(AXES):
        low, high = span(parameters, axis)
        if (low, high) == FULL:
            continue
        node = {'type': 'minecraft:range_choice', 'input': function,
                'min_inclusive': low, 'max_exclusive': high,
                'when_in_range': node, 'when_out_of_range': miss}
    return node


def merge(boxes):
    """Fuse an authority's bands into the fewest boxes that cover exactly the same territory.

    THE SELECTOR ENCODES AUTHORITY BOUNDARIES, NOT BIOME ONES, and the difference is not cosmetic.
    Emitted per band it was 44 steps, and a 44-deep reference chain as `final_density` killed the
    dedicated server twice during level preparation -- no exception, no crash report, no JVM dump,
    both runs dying while DistantHorizons built its world-gen queues, where an unmerged run forty
    minutes earlier had reached Done in 49s. Merged, the void authority's seven biomes are one
    contiguous continentalness range and the chain is a handful of steps.

    Two boxes fuse when they differ on exactly one axis and are adjacent on it; their union is
    then exactly a box. Iterated to a fixed point. Correctness is not argued from this function:
    check_terrain_authorities A3 evaluates the emitted selector against the emitted layer point by
    point, so a wrong merge is caught by measurement rather than by review.
    """
    boxes = [dict(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                differing = [axis for axis, _ in AXES if span(a, axis) != span(b, axis)]
                if len(differing) != 1:
                    continue
                axis = differing[0]
                alow, ahigh = span(a, axis)
                blow, bhigh = span(b, axis)
                if ahigh == blow:
                    low, high = alow, bhigh
                elif bhigh == alow:
                    low, high = blow, ahigh
                else:
                    continue
                fused = dict(a)
                fused[axis] = [low, high]
                boxes[i] = fused
                boxes.pop(j)
                changed = True
                break
            if changed:
                break
    return boxes


def write_all(out):
    """Write the selector, and REMOVE anything stale first.

    The chain shortens whenever bands merge better, and a shorter chain leaves orphan steps whose
    references point at names no longer emitted. Minecraft resolves density functions at load
    time, so an orphan is not dead weight -- it is a datapack that refuses to load.
    """
    os.makedirs(PREFIX, exist_ok=True)
    keep = {os.path.basename(p) for p in out}
    for name in os.listdir(PREFIX):
        if name.endswith('.json') and name not in keep:
            os.remove(os.path.join(PREFIX, name))
    for path, data in sorted(out.items()):
        with open(path, 'wb') as handle:
            handle.write(data)
    return len(out)


def build(bands, owners):
    """bands -> {path: bytes}. The chain is walked in partition order, which is the order the
    layer itself resolves claims in, so selector and layer cannot disagree about precedence."""
    leaf = {a['id']: '%s:authority/%s' % (NS, a['id']) for a in owners}
    fallback = leaf[owners[-1]['id']]
    out = {}
    # One test per merged region per explicit authority; the last authority is the else.
    steps = []
    for authority in owners[:-1]:
        owned = [b['parameters'] for b in bands
                 if owner_of(b['biome'], owners) == authority['id']]
        for box in merge(owned):
            steps.append((authority['id'], box))
    # Emit from the tail backwards so each step knows the name of the next.
    following = fallback
    emitted = []
    for index in reversed(range(len(steps))):
        authority_id, parameters = steps[index]
        node = test_chain(parameters, leaf[authority_id], following)
        name = 'step_%03d' % index
        emitted.append((name, node))
        following = '%s:authority/%s' % (NS, name)
    for name, node in emitted:
        out[PREFIX + name + '.json'] = (json.dumps(node, indent=2) + '\n').encode()

    # THE LEAVES MUST EXIST OR THE DATAPACK WILL NOT LOAD. Minecraft resolves density-function
    # references at load time, so a chain naming an authority with no file is a hard error rather
    # than a silent fallback.
    #
    # Stage 1 gives every authority the SAME expression -- today's whole alfheim_final body,
    # INLINED rather than referenced. Inlined on purpose: wiring alfheim_final to the chain in
    # stage 1b would otherwise close a cycle through itself. Two copies of a 6 KB expression is
    # what it costs to have the framework provably inert before any terrain moves.
    import gen_alfheim_biomes
    body = gen_alfheim_biomes.void_final_density()
    for authority in owners:
        out[PREFIX + authority['id'] + '.json'] = (json.dumps(body, indent=2) + '\n').encode()
    return out, following


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    import gen_alfheim_biomes
    bands = gen_alfheim_biomes.LAYER['biomes']
    owners = authorities()

    # Every biome the layer places must be owned, and owned once. The fallback owns the
    # remainder by construction, so this only catches a biome claimed by two explicit owners.
    placed = {b['biome'] for b in bands}
    explicit = [a for a in owners if a['biomes'] is not None]
    for i in range(len(explicit)):
        for j in range(i + 1, len(explicit)):
            both = explicit[i]['biomes'] & explicit[j]['biomes']
            if both:
                raise SystemExit('%s and %s both claim %s'
                                 % (explicit[i]['id'], explicit[j]['id'], sorted(both)))
    for authority in explicit:
        missing = authority['biomes'] - placed
        if missing:
            raise SystemExit('%s claims %s, which the layer does not place'
                             % (authority['id'], sorted(missing)))

    out, entry = build(bands, owners)
    print('%d bands -> %d selector steps; entry point %s' % (len(bands), len(out), entry))
    for authority in owners:
        owned = sorted(b for b in placed if owner_of(b, owners) == authority['id'])
        print('  %-10s %2d biome(s)  %s' % (authority['id'], len(owned), authority['note']))
        for b in owned:
            print('               %s' % b)
    if args.dry_run:
        return 0
    written = write_all(out)
    print('wrote %d files under %s' % (written, PREFIX))
    return 0


if __name__ == '__main__':
    sys.exit(main())
