"""Bake the visible skin of overlapping axis-aligned model cuboids.

Minecraft draws every authored face, including coincident faces on the rear of
overlaid relief. Clip hidden faces and assign each coincident area to one layer.
Rotated elements remain unchanged; their planes do not use this axis-aligned pass.
"""
from copy import deepcopy

FACES = {'west': (0, -1), 'east': (0, 1), 'down': (1, -1),
         'up': (1, 1), 'north': (2, -1), 'south': (2, 1)}


def default_uv(face, lo, hi):
    x, y, z = lo; X, Y, Z = hi
    return {'down': [x, 16-Z, X, 16-z], 'up': [x, z, X, Z],
            'north': [16-X, 16-Y, 16-x, 16-y], 'south': [x, 16-Y, X, 16-y],
            'west': [z, 16-Y, Z, 16-y], 'east': [16-Z, 16-Y, 16-z, 16-y]}[face]


def clean_model(doc):
    doc = deepcopy(doc)
    elements = doc.get('elements', [])
    output = []
    for index, element in enumerate(elements):
        if 'rotation' in element:
            output.append(element)
            continue
        lo, hi = element['from'], element['to']
        for face, material in element.get('faces', {}).items():
            axis, direction = FACES[face]
            plane = hi[axis] if direction > 0 else lo[axis]
            u, v = [a for a in range(3) if a != axis]
            blockers = []
            for other_index, other in enumerate(elements):
                if other_index == index or 'rotation' in other:
                    continue
                a, b = other['from'], other['to']
                # Solid beyond this face hides it. At a shared outer plane,
                # the later-authored decorative element owns the exposed surface.
                outward = (a[axis] <= plane < b[axis] if direction > 0
                           else a[axis] < plane <= b[axis])
                # Transparent shells must retain the objects visible through them.
                if any(any(word in doc.get('textures', {}).get(f.get('texture', '')[1:], '').lower()
                           for word in ('glass', 'leaves', 'water'))
                       for f in other.get('faces', {}).values()):
                    outward = False
                coincident = (other_index > index and face in other.get('faces', {})
                              and (b[axis] if direction > 0 else a[axis]) == plane)
                if (outward or coincident) and a[u] < hi[u] and b[u] > lo[u] and a[v] < hi[v] and b[v] > lo[v]:
                    blockers.append((max(a[u], lo[u]), max(a[v], lo[v]),
                                     min(b[u], hi[u]), min(b[v], hi[v])))
            if not blockers:
                retained = deepcopy(element)
                retained['faces'] = {face: material}
                output.append(retained)
                continue
            us = sorted({lo[u], hi[u], *[c for r in blockers for c in (r[0], r[2])]})
            vs = sorted({lo[v], hi[v], *[c for r in blockers for c in (r[1], r[3])]})
            original_uv = default_uv(face, lo, hi)
            custom_uv = material.get('uv', original_uv)
            for U, UU in zip(us, us[1:]):
                for V, VV in zip(vs, vs[1:]):
                    if any(a <= (U+UU)/2 <= b and c <= (V+VV)/2 <= d
                           for a, c, b, d in blockers):
                        continue
                    a, b = list(lo), list(hi)
                    a[u], b[u], a[v], b[v] = U, UU, V, VV
                    patch_uv = default_uv(face, a, b)
                    if material.get('rotation', 0):
                        raise ValueError('Rotated UV clipping needs explicit handling')
                    uv = []
                    for k in range(4):
                        dim = k % 2
                        extent = original_uv[dim+2] - original_uv[dim]
                        fraction = (patch_uv[k] - original_uv[dim]) / extent
                        uv.append(custom_uv[dim] + fraction * (custom_uv[dim+2] - custom_uv[dim]))
                    patch = {key: deepcopy(value) for key, value in element.items()
                             if key not in ('from', 'to', 'faces')}
                    patch.update({'from': a, 'to': b, 'faces': {face: dict(material, uv=uv)}})
                    output.append(patch)
    doc['elements'] = output
    return doc
