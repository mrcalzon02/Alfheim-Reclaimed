"""Original Act I sculptures using the existing monstrosity UV/skin workflow.

Art prototypes only. No entity registration, behavior, encounter or loot is installed.
Coordinates use Minecraft model pixels (16 pixels = one block), Y up.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import uuid

import numpy as np
from PIL import Image
from gen_monstrosities import PALETTES, skin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'alfheim_reclaimed_design/monastery_labyrinth/asset_batch_01'
ATLAS = 512
LOOKS = ('cloister_ash', 'burial_ochre', 'moonlit_lichen')
PALETTES.update({
    'ashen_novice': [(141, 139, 119), (149, 122, 98), (125, 153, 149)],
    'lurking_silkmaw': [(85, 92, 75), (125, 97, 66), (79, 112, 116)],
    'bell_warden': [(139, 146, 134), (159, 135, 101), (121, 151, 157)],
})


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'alfheim/monastery/asset_01/' + name))


def cube(parts, name, center, size, material, group='body', rotation=(0, 0, 0), origin=None):
    a = [round(c - s / 2, 5) for c, s in zip(center, size)]
    b = [round(c + s / 2, 5) for c, s in zip(center, size)]
    assert all(x < y for x, y in zip(a, b)), name
    parts.append({'name': name, 'from': a, 'to': b, 'material': material, 'group': group,
                  'rotation': list(rotation), 'origin': list(origin or center), 'uuid': uid(name)})


def segment(parts, name, a, b, width, depth, material, group='body'):
    delta = np.array(b, dtype=float) - a
    length = float(np.linalg.norm(delta))
    # Rz * Rx maps the local vertical axis onto this segment's direction.
    rx = math.degrees(math.asin(float(delta[2]) / length))
    rz = -math.degrees(math.atan2(float(delta[0]), float(delta[1])))
    cube(parts, name, ((np.array(a) + b) / 2).tolist(), (width, length, depth), material,
         group, (rx, 0, rz))


def humanoid(kind):
    p = []
    warden = kind == 'bell_warden'
    height = 45 if warden else 31
    torso = 24 if warden else 17
    head = height - 5
    robe_width = 14 if warden else 10
    cube(p, 'robe_underbody', (0, 10, 1), (robe_width - 2, 17, 7), 'cloth')
    # Individually shaped overlapping skirt panels, hems and hanging strips.
    for i in range(7):
        x = (i - 3) * (robe_width / 7)
        low = 2 + (i % 3) * .7
        cube(p, f'robe_front_panel_{i}', (x, (low + torso) / 2, -3.4),
             (robe_width / 7 + .25, torso - low, 1.3), 'cloth', rotation=(3, 0, (i - 3) * 1.2))
        cube(p, f'robe_back_panel_{i}', (x, (low + torso) / 2, 4),
             (robe_width / 7 + .3, torso - low, 1.1), 'cloth', rotation=(-4, 0, (3 - i) * 1.1))
        cube(p, f'front_embroidered_hem_{i}', (x, low + .6, -4.1), (robe_width / 7, 1, .55), 'trim')
    for side in (-1, 1):
        g = 'left_leg' if side == -1 else 'right_leg'
        cube(p, f'{g}_foot', (side * 3.1, 1, -.7), (3.1, 2, 5), 'leather', g)
        cube(p, f'{g}_shin', (side * 3.1, 5, .3), (2.5, 6, 2.8), 'bone', g)
        for i in range(3):
            cube(p, f'{g}_binding_{i}', (side * 3.1, 3.5 + i * 1.4, .3), (2.9, .65, 3.1), 'wrap', g)
    cube(p, 'ribcage', (0, torso + 1, .2), (robe_width - 2, 10, 6), 'shadow_skin')
    for side in (-1, 1):
        for i in range(4):
            cube(p, f'rib_{side}_{i}', (side * 3, torso + 3 - i * 1.5, -3.1), (4.6, .8, 1), 'bone', rotation=(0, 0, side * 12))
    cube(p, 'sternum', (0, torso, -3.8), (1.1, 6, 1), 'bone')
    cube(p, 'hunched_mantle', (0, torso + 6, 2), (robe_width + 2, 4, 9), 'cloth', rotation=(-9, 0, 0))
    for i in range(5):
        cube(p, f'mantle_pleat_{i}', ((i - 2) * 2.7, torso + 6.8, 2), (2.2, 1.5, 8), 'cloth')
    cube(p, 'neck_wrap', (0, head - 4.8, -.9), (4, 3, 4), 'wrap', 'head')
    cube(p, 'skull_cranium', (0, head, -1.5), (6.2, 6.6, 5.8), 'bone', 'head')
    cube(p, 'skull_jaw', (0, head - 3, -2.4), (5.1, 1.8, 4.2), 'shadow_skin', 'head')
    cube(p, 'face_nasal_void', (0, head - .8, -4.55), (1, 1.5, .4), 'void', 'head')
    for side in (-1, 1):
        cube(p, f'eye_socket_{side}', (side * 1.7, head + .3, -4.5), (2.2, 1.9, .55), 'void', 'head')
        cube(p, f'eye_glint_{side}', (side * 1.7, head + .2, -4.9), (.8, .6, .35), 'eye', 'head')
        cube(p, f'brow_{side}', (side * 1.8, head + 1.5, -4.5), (2.5, .8, .8), 'bone', 'head', rotation=(0, 0, side * 14))
        cube(p, f'cheek_{side}', (side * 2.5, head - 1.5, -4.1), (1.1, 2.1, 1), 'bone', 'head')
        cube(p, f'hood_cheek_{side}', (side * 3.8, head, -.2), (1.6, 9, 6.4), 'cloth', 'head', rotation=(0, 0, side * -7))
    for i in range(5):
        cube(p, f'tooth_{i}', ((i - 2) * .8, head - 2.5, -4.6), (.55, .8 + (i % 2) * .3, .6), 'ivory', 'head')
    cube(p, 'hood_crown', (0, head + 4, -.1), (8.8, 2, 7), 'cloth', 'head')
    cube(p, 'hood_trailing_fold', (0, head - .5, 3.5), (6, 8, 2), 'cloth', 'head')
    for side in (-1, 1):
        g = 'left_arm' if side == -1 else 'right_arm'
        shoulder = [side * (robe_width / 2 + 1), torso + 5, 0]
        elbow = [side * (robe_width / 2 + 3), torso - 1, -1.5]
        hand = [side * (robe_width / 2 + 2.8), torso - 6, -4]
        segment(p, f'{g}_upper_sleeve', shoulder, elbow, 3.7, 4.4, 'cloth', g)
        segment(p, f'{g}_forearm', elbow, hand, 2.3, 2.7, 'shadow_skin', g)
        cube(p, f'{g}_cuff', elbow, (3.8, 1.8, 4.5), 'trim', g)
        cube(p, f'{g}_hand', hand, (2.4, 2, 1.8), 'bone', g)
        for finger in range(3):
            a = [hand[0] + (finger - 1) * .7, hand[1] - .8, hand[2]]
            b = [a[0], a[1] - 2, a[2] - .7]
            segment(p, f'{g}_finger_{finger}', a, b, .5, .6, 'bone', g)
    if warden:
        # A broad open bell yoke is the support monster's readable signature.
        for side in (-1, 1):
            segment(p, f'bell_yoke_{side}', [side * 8, torso + 4, 5], [side * 9, height + 2, 4], 2, 2, 'bark')
        cube(p, 'bell_crossbeam', (0, height + 2, 4), (20, 2, 3), 'bark')
        cube(p, 'bell_crown', (0, height - 1, 4), (4, 3, 4), 'metal')
        for i in range(4):
            r = 3 + i * 1.3
            y = height - 3.5 - i * 1.5
            for side in (-1, 1):
                cube(p, f'bell_side_{i}_{side}', (side * r, y, 4), (1.2, 2, r * 2), 'metal')
                cube(p, f'bell_front_back_{i}_{side}', (0, y, 4 + side * r), (r * 2, 2, 1.2), 'metal')
        cube(p, 'bell_clapper', (0, height - 8.5, 4), (2, 7, 2), 'iron')
        cube(p, 'rally_sigil', (0, torso + 3, -4.2), (3, 3, .6), 'rune')
    else:
        # Consecrated ash vial and a crooked prayer board distinguish the novice.
        cube(p, 'prayer_board', (7.2, 10, -5), (4, 7, 1), 'bark', 'right_arm', rotation=(0, 0, 12))
        for i in range(4):
            cube(p, f'prayer_board_glyph_{i}', (7, 8 + i * 1.3, -5.65), (2.7, .45, .4), 'trim', 'right_arm')
        for i in range(6):
            cube(p, f'prayer_bead_{i}', (-5 + i * .35, 13 - i * 1.1, -4.3), (.8, .8, .8), 'bone', 'left_arm')
        cube(p, 'ash_vial', (-3, 7, -4.3), (1.8, 2.8, 1.8), 'metal', 'left_arm')
    return p


def silkmaw():
    p = []
    cube(p, 'abdomen_core', (0, 13, 8), (13, 11, 18), 'chitin')
    for i in range(6):
        z = 1 + i * 2.5
        cube(p, f'abdomen_plate_{i}', (0, 17.5 + math.sin(i / 5 * math.pi), z), (13 - abs(i - 2.5), 2.6, 3), 'chitin', rotation=(0, 0, 0))
        cube(p, f'abdomen_belly_ring_{i}', (0, 8.1, z), (10, 1.3, 1.1), 'sinew')
    cube(p, 'thorax', (0, 12, -4), (10, 8, 9), 'chitin')
    cube(p, 'face_skull_mask', (0, 13.6, -9), (7.8, 6, 3), 'bone', 'head')
    for side in (-1, 1):
        for i in range(3):
            cube(p, f'eye_socket_{side}_{i}', (side * (1.2 + i * 1.1), 15 - i * 1.2, -10.8), (1.4, 1.3, .65), 'void', 'head')
            cube(p, f'eye_{side}_{i}', (side * (1.2 + i * 1.1), 15 - i * 1.2, -11.2), (.85, .8, .5), 'eye', 'head')
        segment(p, f'fang_root_{side}', [side * 3, 11, -10], [side * 4, 7, -12], 2, 2, 'bone', 'head')
        segment(p, f'fang_hook_{side}', [side * 4, 7, -12], [side * 1.8, 6.5, -13], 1, 1, 'ivory', 'head')
        for i in range(4):
            g = ('left' if side == -1 else 'right') + f'_leg_{i}'
            root = [side * 4, 12, -7 + i * 5]
            knee = [side * (16 + (i % 2) * 3), 17 - i * .7, -18 + i * 10]
            ankle = [side * (23 + (i % 2) * 2), 4, -22 + i * 12]
            toe = [side * (27 + (i % 2) * 2), .5, -24 + i * 13]
            segment(p, f'{g}_coxa', root, knee, 2.7, 3, 'chitin', g)
            segment(p, f'{g}_tibia', knee, ankle, 1.8, 2.1, 'chitin', g)
            segment(p, f'{g}_tarsus', ankle, toe, .8, 1.2, 'iron', g)
            cube(p, f'{g}_joint', knee, (3.4, 3.2, 3.4), 'bone', g)
            segment(p, f'{g}_thorn', knee, [knee[0] + side * 2, knee[1] + 2, knee[2]], .9, .9, 'ivory', g)
    # Silk glands and pale dorsal warning stripes have separate material islands.
    for side in (-1, 1):
        for i in range(4):
            cube(p, f'warning_stripe_{side}_{i}', (side * 4, 19, 3 + i * 3), (1.3, .8, 2), 'web')
        segment(p, f'spinneret_{side}', [side * 3, 11, 16], [side * 4, 8, 20], 1.5, 1.5, 'web')
        segment(p, f'mouth_palp_{side}', [side * 2, 10, -9], [side * 6, 9, -12], 1.4, 1.4, 'chitin', 'head')
        segment(p, f'mouth_palp_tip_{side}', [side * 6, 9, -12], [side * 5, 8, -15], .7, .8, 'ivory', 'head')
        cube(p, f'silk_gland_{side}', (side * 5, 10, 14), (3, 4, 4), 'web')
    return p


def rotation_matrix(rot):
    x, y, z = map(math.radians, rot)
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return rz @ ry @ rx


def bake(parts):
    quads = []
    for i, p in enumerate(parts):
        x, y, z = p['from']; X, Y, Z = p['to']
        faces = {
            'north': ([(X, Y, z), (x, Y, z), (x, y, z), (X, y, z)], [0, 0, -1], X-x, Y-y),
            'south': ([(x, Y, Z), (X, Y, Z), (X, y, Z), (x, y, Z)], [0, 0, 1], X-x, Y-y),
            'east': ([(X, Y, Z), (X, Y, z), (X, y, z), (X, y, Z)], [1, 0, 0], Z-z, Y-y),
            'west': ([(x, Y, z), (x, Y, Z), (x, y, Z), (x, y, z)], [-1, 0, 0], Z-z, Y-y),
            'up': ([(x, Y, Z), (X, Y, Z), (X, Y, z), (x, Y, z)], [0, 1, 0], X-x, Z-z),
            'down': ([(x, y, z), (X, y, z), (X, y, Z), (x, y, Z)], [0, -1, 0], X-x, Z-z),
        }
        p['faces'] = {}
        rot = rotation_matrix(p['rotation'])
        origin = np.array(p['origin'])
        for f, (name, (vertices, normal, width, height)) in enumerate(faces.items()):
            tile = i * 6 + f
            tx, ty = (tile % 28) * 18 + 1, (tile // 28) * 18 + 1
            w, h = max(2, min(16, math.ceil(width * 1.3))), max(2, min(16, math.ceil(height * 1.3)))
            assert ty + h < ATLAS
            p['faces'][name] = {'uv': [tx, ty, tx + w, ty + h], 'texture': 0}
            uv = [[tx, ty], [tx + w, ty], [tx + w, ty + h], [tx, ty + h]]
            quads.append({'vertices': np.round((np.array(vertices) - origin) @ rot.T + origin, 6).tolist(),
                          'normal': np.round(rot @ normal, 6).tolist(),
                          'uv': (np.array(uv) / ATLAS).tolist(), 'part': p['name'],
                          'material': p['material'], 'face': f, 'group': p['group']})
    return quads


def bbmodel(species, parts, texture):
    groups = sorted({p['group'] for p in parts})
    elements = [{k: v for k, v in p.items() if k not in ('material', 'group')} | {'type': 'cube', 'rescale': False, 'autouv': 0} for p in parts]
    outliner = []
    for group in groups:
        subset = [p for p in parts if p['group'] == group]
        pivot = [0, 0, 0] if group == 'body' else subset[0]['origin']
        outliner.append({'name': group, 'origin': pivot, 'rotation': [0, 0, 0], 'uuid': uid(species + '/' + group),
                         'children': [p['uuid'] for p in subset]})
    return {'meta': {'format_version': '4.10', 'model_format': 'free', 'box_uv': False},
            'name': species, 'model_identifier': species, 'visible_box': [6, 6, 2],
            'resolution': {'width': ATLAS, 'height': ATLAS}, 'elements': elements, 'outliner': outliner,
            'textures': [{'name': species + '_cloister_ash.png', 'id': '0', 'uuid': uid(species + '/texture'),
                          'width': ATLAS, 'height': ATLAS, 'uv_width': ATLAS, 'uv_height': ATLAS,
                          'source': 'data:image/png;base64,' + base64.b64encode(texture).decode()}],
            'animations': []}


def obj_text(species, quads):
    lines = ['# Original Alfheim art prototype; 1 unit = 1 Minecraft block; Y up',
             f'mtllib {species}.mtl', f'o {species}', 'usemtl skin']
    for i, q in enumerate(quads):
        lines.append('g ' + q['group'] + '__' + q['part'])
        for v in q['vertices']:
            lines.append('v ' + ' '.join(f'{n / 16:.7f}' for n in v))
        for u, v in q['uv']:
            lines.append(f'vt {u:.8f} {1-v:.8f}')
        first = i * 4 + 1
        order = list(range(first, first + 4))
        verts = np.array(q['vertices'])
        if np.dot(np.cross(verts[1] - verts[0], verts[2] - verts[0]), q['normal']) < 0:
            order.reverse()
        lines.append('f ' + ' '.join(f'{j}/{j}' for j in order))
    return '\n'.join(lines) + '\n'


def outputs():
    catalog = json.loads((ROOT / 'alfheim_reclaimed_design/monastery_labyrinth/monster_catalog.json').read_text())
    by_id = {e['id']: e for e in catalog['creatures']}
    files, rows = {}, []
    for species, parts in [('ashen_novice', humanoid('ashen_novice')),
                           ('lurking_silkmaw', silkmaw()), ('bell_warden', humanoid('bell_warden'))]:
        quads = bake(parts)
        assert 86 <= len(parts) <= 130, (species, len(parts))
        texture_bytes = [skin(species, v, quads, ATLAS) for v in range(3)]
        rel = 'creatures/' + species + '/'
        js = lambda value: (json.dumps(value, indent=2) + '\n').encode()
        files[rel + species + '.geometry.json'] = js({'coordinate_system': 'Minecraft model pixels; Y up; 16 pixels per block',
                                                      'atlas_size': ATLAS, 'parts': parts, 'quads': quads})
        files[rel + species + '.bbmodel'] = js(bbmodel(species, parts, texture_bytes[0]))
        files[rel + species + '.obj'] = obj_text(species, quads).encode()
        files[rel + species + '.mtl'] = f'newmtl skin\nKd 1 1 1\nd 1\nillum 1\nmap_Kd {species}_{LOOKS[0]}.png\n'.encode()
        for look, data in zip(LOOKS, texture_bytes):
            files[rel + species + '_' + look + '.png'] = data
        vertices = np.array([v for q in quads for v in q['vertices']])
        rows.append({'catalog_id': species, 'act': 1, 'role': by_id[species]['role'],
                     'signature': by_id[species]['primary'], 'counterplay': by_id[species]['counterplay'],
                     'part_count': len(parts), 'quad_count': len(quads), 'atlas_size': ATLAS,
                     'model_bounds_blocks': ((vertices.max(axis=0) - vertices.min(axis=0)) / 16).round(4).tolist(),
                     'animation_groups': sorted({p['group'] for p in parts}), 'looks': list(LOOKS),
                     'geometry': rel + species + '.geometry.json', 'blockbench': rel + species + '.bbmodel',
                     'blender_import': rel + species + '.obj', 'asset_state': 'sculpted_textured_art_prototype',
                     'runtime_entity': 'not implemented', 'animation': 'named groups only; keyframes pending',
                     'duplicate_review': 'Original anatomy; no existing entity ID is replaced. Mechanical species count remains zero.'})
    hashes = {path: hashlib.sha256(data).hexdigest() for path, data in files.items()}
    files['creature_art_manifest.json'] = (json.dumps({'status': 'art prototypes; no implemented entities',
        'source_catalog_sha256': hashlib.sha256((ROOT / 'alfheim_reclaimed_design/monastery_labyrinth/monster_catalog.json').read_bytes()).hexdigest(),
        'workflow': 'Original cuboid sculpture, per-face 512px UV islands, existing gen_monstrosities.skin material painter',
        'models': rows, 'sha256': hashes}, indent=2) + '\n').encode()
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    files = outputs()
    for rel, data in files.items():
        path = OUT / rel
        if args.check:
            assert path.read_bytes() == data, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"Three original creature sculptures / nine skins / {len(files)} files " + ('byte-identical' if args.check else 'staged'))


if __name__ == '__main__':
    main()
