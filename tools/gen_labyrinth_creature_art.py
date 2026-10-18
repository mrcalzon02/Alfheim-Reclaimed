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
    'ossuary_bowyer': [(163, 159, 131), (171, 144, 102), (138, 166, 160)],
    'reliquary_sentinel': [(117, 126, 119), (150, 127, 98), (103, 143, 151)],
    'the_ossuary_prior': [(189, 184, 156), (188, 151, 104), (151, 187, 183)],
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


def bowyer():
    """A narrow, bent-legged ossuary archer carrying an articulated bone bow."""
    p = []
    cube(p, 'pelvis', (0, 15, 1), (7, 3, 4), 'bone')
    for side in (-1, 1):
        g = 'left_leg' if side == -1 else 'right_leg'
        hip, knee, ankle = [side*3, 15, 1], [side*4, 8, -1], [side*3.5, 2, 1]
        segment(p, g+'_femur', hip, knee, 1.6, 1.9, 'bone', g)
        segment(p, g+'_tibia', knee, ankle, 1.2, 1.3, 'bone', g)
        segment(p, g+'_fibula', [knee[0]+side,8,-1], [ankle[0]+side,2,1], .6,.7,'bone',g)
        cube(p, g+'_knee', knee, (2.6,2.2,2.6),'ivory',g)
        cube(p, g+'_heel', (side*3.5,1.2,1),(2.5,2,3),'leather',g)
        for toe in range(3):
            segment(p, g+f'_toe_{toe}', [side*3.5+(toe-1)*.7,1,0], [side*3.5+(toe-1)*.9,.7,-2.8],.6,.8,'bone',g)
        for i in range(2):
            cube(p,g+f'_binding_{i}',(side*3.7,4+i*1.5,.5),(2.7,.7,2.5),'wrap',g)
    for i in range(6):
        cube(p,f'vertebra_{i}',(0,17+i*1.6,1.8),(2,1.3,2.4),'bone')
    for side in (-1,1):
        for i in range(5):
            cube(p,f'rib_{side}_{i}',(side*(2.8-i*.2),25-i*1.5,-1.2),(4.3-i*.25,.8,1.2),'bone',rotation=(0,side*12,side*11))
        cube(p,f'clavicle_{side}',(side*2.5,27,-.2),(5,1,2),'ivory',rotation=(0,0,side*10))
        cube(p,f'scapula_{side}',(side*2.8,25.4,3.1),(3.6,4,.8),'shadow_skin')
    cube(p,'sternum',(0,23,-2.2),(1,7,1),'bone')
    for i in range(4):
        x=(i-1.5)*2
        cube(p,f'waist_wrap_{i}',(x,13,-1.8),(2.3,6+(i%2),1.2),'cloth',rotation=(0,0,(i-1.5)*4))
        cube(p,f'waist_hem_{i}',(x,10,-2.5),(2,.7,.5),'trim')
    cube(p,'neck',(0,28,0),(2.5,3,2.8),'wrap','head')
    cube(p,'skull_cranium',(0,32,-.8),(5.8,6,5.8),'bone','head',rotation=(7,0,0))
    cube(p,'jaw',(0,29.1,-1.5),(4.4,1.8,3.6),'bone','head')
    cube(p,'nasal_void',(0,31,-3.9),(1.1,1.5,.5),'void','head')
    for side in (-1,1):
        cube(p,f'eye_socket_{side}',(side*1.4,32.3,-3.8),(2,1.8,.6),'void','head')
        cube(p,f'eye_{side}',(side*1.4,32.2,-4.15),(.6,.7,.35),'eye','head')
        cube(p,f'cheek_{side}',(side*2.4,30.6,-3.1),(1.1,1.7,1.6),'bone','head')
        cube(p,f'brow_{side}',(side*1.4,33.5,-3.7),(2.2,.7,.8),'bone','head',rotation=(0,0,side*-13))
    for i in range(5):
        cube(p,f'tooth_{i}',((i-2)*.7,29.8,-3.5),(.45,.8,.6),'ivory','head')
    cube(p,'torn_hood_crown',(0,35,.7),(7,1.6,6.5),'cloth','head')
    cube(p,'trailing_hood',(1.6,31.3,3.2),(4.4,7,1.6),'cloth','head',rotation=(0,0,-12))
    arms = {
        'left_arm': ([-5,26,0],[-9,22,-2],[-11,23,-8]),
        'right_arm': ([5,26,0],[8,24,-2],[3,24,-6]),
    }
    for g,(shoulder,elbow,hand) in arms.items():
        segment(p,g+'_humerus',shoulder,elbow,1.6,1.9,'bone',g)
        segment(p,g+'_radius',elbow,hand,1.1,1.2,'bone',g)
        segment(p,g+'_ulna',[v+.6 if i==0 else v for i,v in enumerate(elbow)],hand,.65,.7,'bone',g)
        cube(p,g+'_palm',hand,(2.4,1.7,1.8),'bone',g)
        for i in range(3):
            segment(p,g+f'_finger_{i}',[hand[0]+(i-1)*.6,hand[1],hand[2]],[hand[0]+(i-1)*.7,hand[1]-1.5,hand[2]-.8],.45,.55,'ivory',g)
        for i in range(2):
            cube(p,g+f'_wrap_{i}',(elbow[0],elbow[1]+i*.9,elbow[2]),(2.5,.6,2.6),'wrap',g)
    curve=[(-11,8,-8),(-14,12,-8),(-16,17,-8),(-15,21,-8),(-11,24,-8),(-15,28,-8),(-16,33,-8),(-14,38,-8),(-11,42,-8)]
    for i,(a,b) in enumerate(zip(curve,curve[1:])):
        segment(p,f'bow_limb_{i}',a,b,1.2,1.7,'bone','left_arm')
    for i in (1,4,7):
        cube(p,f'bow_binding_{i}',curve[i],(2.3,1.2,2.3),'wrap','left_arm')
    segment(p,'bowstring_upper',curve[-1],[2.5,24,-8],.32,.32,'rune','right_arm')
    segment(p,'bowstring_lower',curve[0],[2.5,24,-8],.32,.32,'rune','right_arm')
    segment(p,'nocked_arrow',[-17,24,-8],[4,24,-8],.45,.45,'bark','right_arm')
    for side in (-1,1):
        cube(p,f'arrow_point_{side}',(-18,24,-8+side*.4),(2,.8,.8),'iron','right_arm',rotation=(0,side*28,0))
    for i in range(3):
        cube(p,f'arrow_fletch_{i}',(2+i*.6,24,-8),(1.4,2.2,.35),'web','right_arm',rotation=(i*60,0,0))
    cube(p,'back_quiver',(4,20.5,4),(3.5,8.5,3),'leather',rotation=(0,0,-13))
    for i in range(3):
        segment(p,f'quiver_arrow_{i}',[3+i,19,4],[3+i,29+i*.7,4],.35,.35,'bark')
        cube(p,f'quiver_fletch_{i}',(3+i,28+i*.7,4),(1,2,1),'web')
    return p


def sentinel():
    """A heavy reliquary body and a deliberately asymmetric frontal bulwark."""
    p=[]
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        cube(p,g+'_foot',(side*5,1.5,-1),(7,3,9),'stone',g)
        cube(p,g+'_toe_plate',(side*5,3,-4.5),(6,2,2),'iron',g)
        cube(p,g+'_shin',(side*5,8,1),(4.5,10,5),'shadow_stone',g)
        cube(p,g+'_thigh',(side*4.5,15,1),(5,5,5),'stone',g)
        cube(p,g+'_knee',(side*5,11,-2),(5.5,4,2.2),'metal',g)
        cube(p,g+'_hinge',(side*7.7,11,1),(1.2,3,3),'iron',g)
        for i in range(3):
            cube(p,g+f'_greave_course_{i}',(side*5,5+i*2,-1.9),(5.7,1.4,1.4),'stone',g)
    cube(p,'pelvic_block',(0,17,1),(13,4,8),'stone')
    cube(p,'torso_casket',(0,25,2),(15,14,10),'shadow_stone')
    cube(p,'breastplate',(0,26,-3.5),(12,10,1.4),'stone')
    for side in (-1,1):
        cube(p,f'chest_frame_{side}',(side*7.2,25,-4),(2,13,2),'trim')
        for i in range(3):
            cube(p,f'reliquary_rib_{side}_{i}',(side*3.8,23+i*2,-4.5),(5.5,1,1.5),'bone',rotation=(0,0,side*10))
    for y in (19,32):
        cube(p,f'casket_course_{y}',(0,y,1),(17,2,12),'trim')
    # The small rear reliquary exposes the flank identity without adding loot.
    cube(p,'rear_inset',(0,26,7.3),(8,8,1),'void')
    for x in (-4.7,4.7):
        cube(p,f'rear_frame_{x}',(x,26,8),(1.2,9,1.5),'metal')
    for i in range(3):
        cube(p,f'rear_soul_rib_{i}',(0,23+i*2,8),(7,1,.9),'rune')
    cube(p,'neck_ring',(0,34,1),(8,3,7),'iron','head')
    cube(p,'face_mask',(0,38,-1),(7,7,6),'stone','head')
    cube(p,'helmet_crown',(0,42,1),(10,2,9),'metal','head')
    cube(p,'visor_slit',(0,38.5,-4.3),(6,1.4,.7),'void','head')
    for side in (-1,1):
        cube(p,f'visor_eye_{side}',(side*1.8,38.5,-4.75),(1.8,.65,.4),'rune','head')
        cube(p,f'cheek_plate_{side}',(side*3.8,37.5,-2.7),(1.8,5,4),'iron','head')
        cube(p,f'helmet_fin_{side}',(side*4.6,42.3,1),(1.5,5,7),'stone','head',rotation=(0,0,side*-13))
        cube(p,f'jaw_grille_{side}',(side*1.7,35,-3.3),(2.6,1.7,2),'bone','head')
    for side in (-1,1):
        g='left_arm' if side==-1 else 'right_arm'
        shoulder=[side*10,30,1]; elbow=[side*12,24,0]; hand=[side*12,19,-3]
        segment(p,g+'_upper',shoulder,elbow,5,5,'shadow_stone',g)
        segment(p,g+'_forearm',elbow,hand,4,4,'stone',g)
        cube(p,g+'_elbow',elbow,(6,3.5,6),'iron',g)
        cube(p,g+'_hand',hand,(4.5,4,4),'iron',g)
        for i in range(3):
            cube(p,g+f'_finger_{i}',(hand[0]+(i-1)*1.4,17.3,-4),(1,2,2),'bone',g)
        for i in range(3):
            cube(p,g+f'_shoulder_plate_{i}',(side*(9+i*1.3),31-i,1),(4.4,2,8),'stone',g,rotation=(0,0,side*-14))
        for i in range(2):
            cube(p,g+f'_bracer_{i}',(hand[0],21+i,-1.5),(5.5,1.1,5.5),'metal',g)
    # Wall-sized shield, with an interrupted central slit and six inset panels.
    cube(p,'bulwark_back',(-12,21,-8),(13,25,2),'iron','left_arm')
    for x in (-17.8,-6.2):
        cube(p,f'shield_vertical_frame_{x}',(x,21,-9.7),(1.8,27,1.8),'trim','left_arm')
    for y in (8,34):
        cube(p,f'shield_horizontal_frame_{y}',(-12,y,-9.5),(13,1.8,2),'trim','left_arm')
    for col in (-1,1):
        for row in range(3):
            cube(p,f'shield_panel_{col}_{row}',(-12+col*2.7,13+row*7,-10),(4.5,6,1.4),'stone','left_arm')
    for x in (-17,-7):
        for y in (10,17,25,32):
            cube(p,f'shield_rivet_{x}_{y}',(x,y,-10.8),(1.1,1.1,.8),'metal','left_arm')
    cube(p,'shield_boss',(-12,21,-11.2),(4.5,5,2),'metal','left_arm')
    for i in range(3):
        cube(p,f'shield_lock_rune_{i}',(-12,16+i*5,-12.3),(1.3,2,.5),'rune','left_arm')
    segment(p,'mace_haft',[12,8,-3],[12,27,-3],1.6,1.6,'bark','right_arm')
    for y in (10,16,22):
        cube(p,f'mace_binding_{y}',(12,y,-3),(2.5,1.1,2.5),'wrap','right_arm')
    cube(p,'mace_head',(12,7,-3),(7,6,7),'stone','right_arm')
    for side in (-1,1):
        cube(p,f'mace_face_{side}',(12+side*3.5,7,-3),(1.5,5,6),'iron','right_arm')
    return p


def prior():
    """An immense grave-choir officiant with a rib halo and a hollow bell staff."""
    p=[]
    cube(p,'inner_vestment',(0,19,1),(13,31,10),'cloth')
    for i in range(10):
        x=(i-4.5)*1.8
        bottom=1.8+(i%3)*.6
        for side in (-1,1):
            cube(p,f'vestment_panel_{side}_{i}',(x,(bottom+32)/2,side*5),(2.2,32-bottom,1.4),'cloth',rotation=(0,0,(i-4.5)*1.1))
        cube(p,f'embroidered_hem_{i}',(x,bottom+.6,-5.8),(1.8,1.2,.55),'trim')
    cube(p,'thorax',(0,35,1),(13,13,7),'shadow_skin')
    for i in range(5):
        cube(p,f'spinal_seal_{i}',(0,29+i*2.5,5.3),(3,1.5,1.3),'bone')
    for side in (-1,1):
        for i in range(5):
            cube(p,f'pectoral_rib_{side}_{i}',(side*(3.7-i*.2),39-i*1.7,-3.3),(5.8,1.1,1.6),'bone',rotation=(0,0,side*13))
        for i in range(4):
            segment(p,f'choir_halo_rib_{side}_{i}',[side*4,32+i*3.2,5],
                    [side*(16-i*1.4),43+i*3.2,5.5],1.6,2,'bone')
        cube(p,f'pectoral_cord_{side}',(side*4,39,-4.2),(1.1,9,.8),'trim',rotation=(0,0,side*24))
    cube(p,'sternum_sigil',(0,34,-4.4),(3,6,1),'rune')
    cube(p,'neck',(0,44,0),(3.5,4,4),'wrap','head')
    cube(p,'skull_cranium',(0,49,-1),(7.2,7,6.6),'bone','head')
    cube(p,'jaw',(0,45.8,-2),(6,2.5,4.5),'bone','head')
    cube(p,'nasal_void',(0,48,-4.5),(1.3,1.6,.6),'void','head')
    for side in (-1,1):
        cube(p,f'eye_socket_{side}',(side*1.8,49.2,-4.4),(2.5,2,.7),'void','head')
        cube(p,f'eye_{side}',(side*1.8,49.2,-4.85),(1.1,.8,.4),'rune','head')
        cube(p,f'brow_{side}',(side*1.8,50.6,-4.2),(2.8,.9,1),'bone','head',rotation=(0,0,side*12))
        cube(p,f'cheek_{side}',(side*3.3,47.3,-3.6),(1.2,2.4,1.5),'bone','head')
        cube(p,f'mitre_side_{side}',(side*4.4,53.4,0),(2,8,6),'cloth','head',rotation=(0,0,side*-11))
        cube(p,f'mitre_inlay_{side}',(side*3.5,54,-3.3),(1.1,7,.6),'trim','head',rotation=(0,0,side*-11))
    for i in range(5):
        cube(p,f'tooth_{i}',((i-2)*.9,46.3,-4.35),(.55,1,.7),'ivory','head')
    cube(p,'mitre_center',(0,54,1),(7,5.5,5.5),'cloth','head')
    cube(p,'mitre_seal',(0,55,-2.3),(3,3,.8),'metal','head')
    for side in (-1,1):
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*9,40,0]; b=[side*15,32,-1]; c=[side*16,28,-4]
        segment(p,g+'_upper_sleeve',a,b,4.5,5,'cloth',g)
        segment(p,g+'_forearm',b,c,2.4,2.7,'bone',g)
        cube(p,g+'_cuff',b,(5.2,2,5.5),'trim',g)
        cube(p,g+'_hand',c,(3.3,3,2.7),'bone',g)
        for i in range(3):
            segment(p,g+f'_finger_{i}',[c[0]+(i-1),c[1]-.9,c[2]],[c[0]+(i-1)*1.2,c[1]-3,c[2]-1],.7,.8,'ivory',g)
    segment(p,'bell_staff',[-17,1,-4],[-17,53,-4],1.8,1.8,'bark','left_arm')
    for y in (8,26,42):
        cube(p,f'staff_wrap_{y}',(-17,y,-4),(2.8,2,2.8),'wrap','left_arm')
    for side in (-1,1):
        cube(p,f'staff_yoke_{side}',(-17+side*5,53,-4),(1.6,7,2),'iron','left_arm')
    cube(p,'staff_yoke_top',(-17,57,-4),(12,1.8,3),'metal','left_arm')
    cube(p,'staff_bell_crown',(-17,54.8,-4),(3,2,3),'metal','left_arm')
    for i in range(3):
        r=2.2+i*1.1
        for side in (-1,1):
            cube(p,f'staff_bell_side_{i}_{side}',(-17+side*r,53-i*1.4,-4),(1,1.8,r*2),'metal','left_arm')
            cube(p,f'staff_bell_face_{i}_{side}',(-17,53-i*1.4,-4+side*r),(r*2,1.8,1),'metal','left_arm')
    cube(p,'staff_clapper',(-17,50,-4),(1.3,6,1.3),'iron','left_arm')
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
    from labyrinth_art_animation import clips, pivots
    groups = sorted({p['group'] for p in parts})
    group_pivots = pivots(species, parts)
    elements = [{k: v for k, v in p.items() if k not in ('material', 'group')} | {'type': 'cube', 'rescale': False, 'autouv': 0} for p in parts]
    outliner = []
    for group in groups:
        subset = [p for p in parts if p['group'] == group]
        pivot = group_pivots[group]
        outliner.append({'name': group, 'origin': pivot, 'rotation': [0, 0, 0], 'uuid': uid(species + '/' + group),
                         'children': [p['uuid'] for p in subset]})
    # Accessories inherit their attachment's motion before the common root pose.
    attachments={'jaw':'head','bowstring':'left_arm','arrow':'left_arm',
                 'clapper':'body','lantern':'body','tail':'body','cleaver':'right_arm',
                 'censer':'right_arm' if species=='dust_friar' else 'body','censer_lid':'censer',
                 'command_hand':'right_arm','coffin':'left_arm','resonator':'body',
                 **{f'bell_{i}':'right_arm' for i in range(3)}}
    nodes={node['name']:node for node in outliner}
    for group,parent in attachments.items():
        if group in nodes and parent in nodes:
            outliner.remove(nodes[group])
            nodes[parent]['children'].append(nodes[group])
    return {'meta': {'format_version': '4.10', 'model_format': 'free', 'box_uv': False},
            'name': species, 'model_identifier': species, 'visible_box': [6, 6, 2],
            'resolution': {'width': ATLAS, 'height': ATLAS}, 'elements': elements,
            'outliner': [{'name': 'root', 'origin': [0, 0, 0], 'rotation': [0, 0, 0],
                          'uuid': uid(species+'/root'), 'children': outliner}],
            'textures': [{'name': species + '_cloister_ash.png', 'id': '0', 'uuid': uid(species + '/texture'),
                          'width': ATLAS, 'height': ATLAS, 'uv_width': ATLAS, 'uv_height': ATLAS,
                          'source': 'data:image/png;base64,' + base64.b64encode(texture).decode()}],
            'animations': clips(species, parts, uid)}


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
    from labyrinth_creature_wave_02 import PALETTES as WAVE_PALETTES, sculpts
    from labyrinth_creature_wave_03 import PALETTES as WAVE_03_PALETTES, sculpts as sculpts_03
    from labyrinth_creature_wave_04 import PALETTES as WAVE_04_PALETTES, sculpts as sculpts_04
    PALETTES.update(WAVE_PALETTES)
    PALETTES.update(WAVE_03_PALETTES)
    PALETTES.update(WAVE_04_PALETTES)
    catalog = json.loads((ROOT / 'alfheim_reclaimed_design/monastery_labyrinth/monster_catalog.json').read_text())
    by_id = {e['id']: e for e in catalog['creatures']}
    files, rows = {}, []
    roster = [('ashen_novice', humanoid('ashen_novice')),
                           ('lurking_silkmaw', silkmaw()), ('bell_warden', humanoid('bell_warden')),
                           ('ossuary_bowyer', bowyer()), ('reliquary_sentinel', sentinel()),
                           ('the_ossuary_prior', prior())] + sculpts(cube, segment) + sculpts_03(cube, segment) + sculpts_04(cube, segment)
    for species, parts in roster:
        if species == 'bell_warden':
            next(p for p in parts if p['name']=='bell_clapper')['group']='clapper'
        if species == 'ossuary_bowyer':
            for part in parts:
                if part['name'].startswith('bowstring_'): part['group']='bowstring'
                if part['name']=='nocked_arrow' or part['name'].startswith(('arrow_point_','arrow_fletch_')): part['group']='arrow'
        quads = bake(parts)
        assert 86 <= len(parts) <= 130, (species, len(parts))
        texture_bytes = [skin(species, v, quads, ATLAS) for v in range(3)]
        rel = 'creatures/' + species + '/'
        js = lambda value: (json.dumps(value, indent=2) + '\n').encode()
        files[rel + species + '.geometry.json'] = js({'coordinate_system': 'Minecraft model pixels; Y up; 16 pixels per block',
                                                      'atlas_size': ATLAS, 'parts': parts, 'quads': quads})
        model = bbmodel(species, parts, texture_bytes[0])
        files[rel + species + '.bbmodel'] = js(model)
        files[rel + species + '.obj'] = obj_text(species, quads).encode()
        files[rel + species + '.mtl'] = f'newmtl skin\nKd 1 1 1\nd 1\nillum 1\nmap_Kd {species}_{LOOKS[0]}.png\n'.encode()
        for look, data in zip(LOOKS, texture_bytes):
            files[rel + species + '_' + look + '.png'] = data
        vertices = np.array([v for q in quads for v in q['vertices']])
        rows.append({'catalog_id': species, 'act': 1, 'role': by_id[species]['role'],
                     'representation': 'single small rat member; pack composition pending' if species=='rotmilk_ratpack' else
                                       'stationary rooted trap; walk clip is root settling' if species=='grave_thorn' else
                                       'winged creature; walk clip is flutter reference; flight AI pending' if species=='coal_moth' else
                                       'single crystalline swarm member; scatter clip is art-only; no death projectiles' if species=='skullglass_shardling' else
                                       'separable shell art reference; no decoy actor spawned' if species=='wicker_pilgrim' else
                                       'coffin prop drop reference; no obstacle or collision deployed' if species=='coffin_strider' else
                                       'burial pounce gesture only; no terrain editing or grave spawning' if species=='carrion_lurker' else 'single creature',
                     'signature': by_id[species]['primary'], 'counterplay': by_id[species]['counterplay'],
                     'part_count': len(parts), 'quad_count': len(quads), 'atlas_size': ATLAS,
                     'model_bounds_blocks': ((vertices.max(axis=0) - vertices.min(axis=0)) / 16).round(4).tolist(),
                     'animation_groups': sorted({p['group'] for p in parts}), 'looks': list(LOOKS),
                     'geometry': rel + species + '.geometry.json', 'blockbench': rel + species + '.bbmodel',
                     'blender_import': rel + species + '.obj', 'asset_state': 'sculpted_textured_art_prototype',
                     'runtime_entity': 'not implemented', 'animation': 'three editable art clips; native animation pending',
                     'animation_clips': [{'name':a['name'],'length_seconds':a['length'],'loop':a['loop']} for a in model['animations']],
                     'duplicate_review': 'Original anatomy; no existing entity ID is replaced. Mechanical species count remains zero.'})
    from labyrinth_art_animation import SIGNATURES
    files['art_motion_contracts.json'] = (json.dumps({
        'status':'Editable art motion only; zero native hit, audio or AI events',
        'schema_reference':{'source':'Installed Blockbench app.asar',
                            'app_version':'4.12.4',
                            'entries':['js/io/formats/bbmodel.js','js/animations/animation.js','js/animations/keyframe.js'],
                            'entry_sha256':['70fe2b63612cc98cb1ffd9bba3a0f4117d7a5bab5dbcae823b9b70b4043a2d06',
                                            '3827f0b5bf16b2d7d676d83a8973b2b0f546602cca657a7deaff39a588d7fc95',
                                            'cba625d5f5b5683e8387ac16d80a980a6adbac31b1c07d70237a1f9ffa49900c'],
                            'inspection':'Animation.getUndoCopy and Keyframe data_points save representation inspected locally'},
        'models':[{'id':row['catalog_id'],'signature_clip':SIGNATURES[row['catalog_id']][0],
                   'visual_stages':SIGNATURES[row['catalog_id']][2],
                   'native_combat_contract':row['signature'],'counterplay':row['counterplay'],
                   'clips':row['animation_clips'],'acceptance':'offline motion preview; editor/client import pending'} for row in rows]
    }, indent=2)+'\n').encode()
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
    print(f"Twenty-six original Act I sculptures / seventy-eight skins / {len(files)} files " + ('byte-identical' if args.check else 'staged'))


if __name__ == '__main__':
    main()
