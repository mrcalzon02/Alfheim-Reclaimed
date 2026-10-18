"""Remaining eight original Ashen Cloister anatomies; art only, no game actors."""
import math
from labyrinth_creature_wave_02 import bind

PALETTES={
    'sepulcher_hound':[(147,142,118),(157,120,93),(119,158,163)],
    'briar_witness':[(114,132,84),(142,113,78),(92,144,142)],
    'wicker_pilgrim':[(139,129,99),(160,119,86),(113,150,147)],
    'pale_deacon':[(178,177,156),(181,148,118),(145,184,188)],
    'carrion_lurker':[(139,135,105),(151,112,92),(115,151,149)],
    'coffin_strider':[(157,154,134),(167,131,103),(127,167,173)],
    'choir_wight':[(169,177,170),(175,144,132),(134,184,190)],
    'hollow_sexton':[(142,148,130),(168,131,101),(122,163,169)],
}


def sepulcher_hound(cube,segment):
    p,c,s=bind(cube,segment)
    c('lean_barrel',(0,14,1),(7.5,9,17),'shadow_skin')
    c('shoulder_hump',(0,17,-4),(8.5,6,7),'fur',rotation=(-10,0,0))
    c('pelvis',(0,13,8),(6.5,7,6),'skin')
    for side in (-1,1):
        for i in range(5):
            c(f'exposed_rib_{side}_{i}',(side*3.7,14.7,-4+i*2.2),(1.1,5.3-i*.3,1.4),'bone',rotation=(0,0,side*13))
        for front in (True,False):
            g=('left' if side==-1 else 'right')+('_front_leg' if front else '_rear_leg')
            z=-5 if front else 7
            a=[side*3,14,z];b=[side*4,7,z+(1 if front else 2.7)];foot=[side*4,1.7,z-1]
            s(g+'_upper',a,b,2.5,3,'skin',g)
            s(g+'_lower',b,foot,1.3,1.7,'bone',g)
            c(g+'_joint',b,(2.5,2.5,2.8),'bone',g)
            c(g+'_paw',(side*4,1.3,z-1.4),(3.1,2,4.1),'fur',g)
            for i in range(3):
                c(g+f'_claw_{i}',(side*4+(i-1)*.85,.85,z-3.7),(.6,.8,1.2),'ivory',g)
            c(g+'_fetlock',(side*4,4,z),(2,1.2,2.2),'wrap',g)
    for i in range(7):
        c(f'vertebra_{i}',(0,18.2,-4+i*1.8),(1.9,1.3,1.7),'bone')
    c('neck',(0,17,-8),(5,7,5),'fur','head',rotation=(-20,0,0))
    c('skull',(0,19,-10.3),(5.5,5,6),'bone','head')
    c('long_muzzle',(0,17.8,-14.3),(4.1,3.1,4.5),'bone','head')
    c('nose',(0,18,-16.8),(2.5,1.9,1.2),'void','head')
    c('mandible',(0,15.8,-13.5),(4.2,1.8,6),'bone','jaw')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*2.6,19.1,-11.8),(.7,1.7,2.2),'void','head')
        c(f'eye_{side}',(side*3,19.1,-12.1),(.35,.8,1),'eye','head')
        c(f'ear_{side}',(side*2.7,22,-9),(1.8,4.2,2.1),'fur','head',rotation=(0,0,side*-16))
        c(f'ear_inner_{side}',(side*2.7,22,-10.2),(1,2.7,.5),'skin','head',rotation=(0,0,side*-16))
        for i in range(3):
            c(f'fang_{side}_{i}',(side*1.8,16.6,-12.8-i*1.2),(.65,1.3,.7),'ivory','jaw')
        c(f'collar_clasp_{side}',(side*3.4,16,-7),(1.1,2.5,3),'iron','head')
        c(f'snout_scar_{side}',(side*2,18,-14.7),(.55,1.3,2),'scar','head')
    for i in range(3):
        c(f'collar_token_{i}',((i-1)*1.3,13.6,-9),(1,1.8,.8),'metal','head')
    tail=[(0,14,10),(0,15,13),(1,16,16),(2,15,18),(3,13,19.5)]
    for i,(a,b) in enumerate(zip(tail,tail[1:])):
        s(f'tail_{i}',a,b,1.8-i*.25,2-i*.25,'fur','tail')
        c(f'tail_knot_{i}',b,(1.7-i*.2,1.3,1.7-i*.2),'bone','tail')
    return p


def briar_witness(cube,segment):
    p,c,s=bind(cube,segment)
    c('trunk',(0,20,1),(7,21,6),'bark')
    c('heart_cavity',(0,22,-2.5),(3.8,9,.8),'void')
    for side in (-1,1):
        for i in range(5):
            c(f'trunk_rib_{side}_{i}',(side*2.7,17+i*2.7,-2.6),(1.6,2.2,1.4),'bark',rotation=(0,0,side*11))
        for front in (True,False):
            g=('left' if side==-1 else 'right')+('_front_leg' if front else '_rear_leg')
            z=-2.5 if front else 4
            a=[side*2.7,12,z];b=[side*6,5,z*1.7];foot=[side*9,.9,z*2]
            s(g+'_root',a,b,2.4,2.8,'bark',g)
            s(g+'_runner',b,foot,1.4,1.7,'bark',g)
            c(g+'_knuckle',b,(2.9,2,2.8),'bone',g)
            for i in range(2):
                s(g+f'_toe_{i}',foot,[foot[0]+side*1.8,.6,foot[2]+(i*2-1)*2],.7,1,'bark',g)
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*4.8,29,1];b=[side*9,23,0];hand=[side*10,15,-3]
        s(g+'_bough',a,b,2.5,3,'bark',g)
        s(g+'_forebranch',b,hand,1.7,2,'bark',g)
        c(g+'_joint',b,(3.2,2.2,3),'moss',g)
        for i in range(3):
            s(g+f'_root_finger_{i}',[hand[0]+(i-1)*.8,15,-3],[hand[0]+(i-1)*1.4,11.3,-4.4],.6,.8,'bark',g)
        s(g+'_thorn',b,[b[0]+side*3,25,0],.8,1,'ivory',g)
    c('eye_crown',(0,33,0),(7.5,8,6),'bark','head')
    c('single_socket',(0,34,-3.5),(6,5,.9),'void','head')
    c('single_iris',(0,34,-4.1),(3.8,3.8,.6),'eye','head')
    c('vertical_pupil',(0,34,-4.5),(.75,3.5,.35),'void','head')
    for y in (31.5,36.5):
        c(f'eye_lid_{y}',(0,y,-3.8),(6.3,1,1.3),'bone','head')
    for side in (-1,1):
        c(f'eye_rim_{side}',(side*2.8,34,-4),(1.1,5,1),'bone','head')
        for i in range(4):
            a=[side*3,32+i*1.5,1];b=[side*(6+i*1.5),36+i*2.3,2]
            s(f'crown_briar_{side}_{i}',a,b,1.3,1.7,'bark','head')
            s(f'crown_tip_{side}_{i}',b,[b[0]+side*1.2,b[1]+2,1.4],.6,.8,'ivory','head')
    for i in range(6):
        c(f'back_bark_plate_{i}',(0,13+i*3,4),(5.8-i*.3,2.6,1.5),'bark',rotation=(0,0,(i%2*2-1)*7))
    for i in range(5):
        c(f'heart_bud_{i}',((i%2)*.9-.45,18+i*1.7,-3.2),(1.2,1.2,.7),'rune')
        c(f'root_lichen_{i}',((i-2)*1.3,10,2),(1.8,1.5,2),'moss')
    return p


def wicker_pilgrim(cube,segment):
    p,c,s=bind(cube,segment)
    c('inner_spine',(0,22,1),(2.2,17,2.8),'bark')
    c('inner_pelvis',(0,14,1),(5,3,4),'bark')
    for i in range(5):
        c(f'inner_rib_{i}',(0,18+i*2,0),(4,1,2),'bone')
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        s(g+'_thigh',[side*2,14,1],[side*3.4,7,2.5],1.8,2.1,'bark',g)
        s(g+'_shin',[side*3.4,7,2.5],[side*3.5,1.5,-.5],1.1,1.4,'bark',g)
        c(g+'_knee',(side*3.4,7,2.5),(2.3,2,2.3),'bone',g)
        for i in range(3):
            s(g+f'_toe_{i}',[side*3.5,1,-.5],[side*3.5+(i-1)*.8,.5,-3],.5,.7,'bark',g)
        c(g+'_binding',(side*3.4,4,1.5),(2,1,2.1),'wrap',g)
        g='left_arm' if side==-1 else 'right_arm'
        s(g+'_upper',[side*5,27,1],[side*8.5,21,1],1.7,2,'bark',g)
        s(g+'_forearm',[side*8.5,21,1],[side*9,15,-3],1.2,1.6,'bark',g)
        c(g+'_binding',(side*8.5,21,1),(2.5,1.3,2.6),'wrap',g)
        for i in range(3):
            s(g+f'_finger_{i}',[side*9+(i-1)*.7,15,-3],[side*9+(i-1)*1.1,12,-4.3],.5,.65,'bark',g)
    # Entire exterior cage is a separately posed art reference for the future decoy.
    for side in (-1,1):
        for i in range(5):
            c(f'shell_front_reed_{side}_{i}',((i-2)*2,22,1+side*4),(1.1,17,1),'bark','decoy_shell')
        for i in range(4):
            c(f'shell_woven_band_{side}_{i}',(0,15+i*4.5,1+side*4.6),(10.5,1.4,.7),'wrap','decoy_shell')
        for i in range(4):
            c(f'shell_side_reed_{side}_{i}',(side*5.2,22,-2+i*2),(1,17,1.2),'bark','decoy_shell')
    for y in (14,30):
        c(f'shell_rim_{y}',(0,y,1),(11,1.5,9.8),'bark','decoy_shell')
    for side in (-1,1):
        for i in range(4):
            c(f'shell_diagonal_{side}_{i}',((i-1.5)*2,22,1+side*5.1),(.7,16,.6),'bark','decoy_shell',rotation=(0,0,18))
    c('neck',(0,31,1),(2,4,2.5),'bark','head')
    c('basket_skull',(0,35,0),(6,6,5),'bark','head')
    c('face_void',(0,35,-2.8),(4.8,4.2,.7),'void','head')
    for side in (-1,1):
        c(f'eye_{side}',(side*1.3,35.3,-3.3),(.8,.7,.4),'rune','head')
        c(f'basket_cheek_{side}',(side*2.7,34,-2.4),(1.1,3.7,1),'wrap','head')
    for i in range(4):
        c(f'face_reed_{i}',((i-1.5)*1.15,33.6,-3.4),(.45,1.7,.4),'bark','head')
    c('basket_brow',(0,38,-.2),(7,1.3,6),'wrap','head')
    for side in (-1,1):
        for i in range(3):
            c(f'head_weave_{side}_{i}',(0,33.1+i*1.3,side*3.6),(5.2,.35,.35),'wrap','head')
    return p


def pale_deacon(cube,segment):
    p,c,s=bind(cube,segment)
    c('tunic',(0,22,1),(8.5,14,7),'wrap')
    for i in range(7):
        x=(i-3)*1.25
        for side in (-1,1):
            c(f'ivory_panel_{side}_{i}',(x,13,1+side*3.8),(1.5,14+(i%2),.8),'wrap',rotation=(0,(i-3)*1.2,0))
        c(f'tunic_hem_{i}',(x,6.5,-3.3),(1.1,.9,.5),'trim')
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        s(g+'_leg',[side*2.7,14,1],[side*3.1,2,0],2.3,2.8,'cloth',g)
        c(g+'_shoe',(side*3.1,1.3,-1),(3.6,2.5,5),'leather',g)
        for i in range(2):
            c(g+f'_buckle_{i}',(side*3.1,3+i*1.1,-1.4),(2.6,.6,.7),'metal',g)
        g='left_arm' if side==-1 else 'right_arm'
        s(g+'_sleeve',[side*5.5,27,1],[side*8.5,22,0],2.9,3.5,'wrap',g)
        s(g+'_forearm',[side*8.5,22,0],[side*8,17,-4],1.8,2.3,'skin',g)
        c(g+'_cuff',(side*8.1,18,-3.2),(3.4,1.8,3.7),'cloth',g)
        hand_group='command_hand' if side==1 else g
        c(g+'_palm',(side*8,16.5,-4.5),(2.6,2,2.5),'skin',hand_group)
        for i in range(3):
            s(g+f'_finger_{i}',[side*8+(i-1)*.7,15.8,-5],[side*8+(i-1)*.85,13.9,-6.2],.45,.55,'skin',hand_group)
            c(g+f'_finger_ring_{i}',(side*8+(i-1)*.7,15.6,-5.2),(.65,.45,.8),'metal',hand_group)
        c(f'stole_{side}',(side*3.2,23,-3),(1.7,12,.8),'cloth')
        for i in range(3):
            c(f'stole_seal_{side}_{i}',(side*3.2,19+i*3,-3.6),(.9,1.2,.45),'trim')
        for i in range(3):
            c(f'collar_fan_{side}_{i}',(side*(2.5+i*1.1),28-i*.5,1),(2.1,1,6),'wrap',rotation=(0,0,side*14))
    c('palm_command_seal',(8,16.7,-5.9),(1.3,1.3,.45),'rune','command_hand')
    c('neck',(0,30,0),(3,4,3.5),'skin','head')
    c('pale_face',(0,34,-.6),(5.2,6,4.7),'skin','head')
    c('nose',(0,34,-3.4),(1,1.8,1.1),'skin','head')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*1.4,34.7,-3.1),(1.6,1.2,.6),'shadow_skin','head')
        c(f'eye_{side}',(side*1.4,34.7,-3.5),(.6,.55,.3),'cloud_eye','head')
        c(f'cowl_side_{side}',(side*3.1,34,.5),(1.4,8,5.8),'wrap','head')
        c(f'cowl_border_{side}',(side*2.7,35,-2.8),(.65,6,.5),'trim','head')
    c('cowl_crown',(0,38,1),(7.2,1.7,6),'wrap','head')
    c('lower_mask',(0,32,-3.2),(3.3,1.2,.6),'wrap','head')
    for side in (-1,1):
        c(f'cloak_clasp_{side}',(side*4.5,28,-2.4),(1.5,1.3,1),'metal')
    c('collar_seal',(0,28.5,-2.5),(1.5,1.4,1),'metal')
    c('prayer_tablet',(-8,17,-5.7),(4.7,6,1),'bark','left_arm',rotation=(0,0,12))
    for i in range(4):
        c(f'tablet_inscription_{i}',(-8,15+i*1.2,-6.3),(2.7,.45,.4),'trim','left_arm')
    return p


def carrion_lurker(cube,segment):
    p,c,s=bind(cube,segment)
    c('long_carapace',(0,11,3),(10,8,16),'chitin')
    c('belly',(0,8,2),(8,4,13),'shadow_skin')
    c('shoulder_hump',(0,14,-2),(11,6,9),'skin',rotation=(-13,0,0))
    for i in range(7):
        c(f'dorsal_scute_{i}',(0,15,-4+i*2.2),(9.5-i*.35,1.8,2.5),'chitin',rotation=(7,0,0))
        c(f'dorsal_keel_{i}',(0,16.2,-4+i*2.2),(1.3,2.2,1.6),'bone',rotation=(-9,0,0))
    for side in (-1,1):
        for i in range(3):
            c(f'flank_ossicle_{side}_{i}',(side*4.8,10,-2+i*3.3),(1.4,3,2),'bone')
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*5.5,13,-2];b=[side*10,7.5,-5];palm=[side*11,3.2,-9]
        s(g+'_upper',a,b,3.6,4.2,'skin',g)
        s(g+'_forearm',b,palm,2.8,3.2,'chitin',g)
        c(g+'_elbow',b,(4.1,2.8,4),'bone',g)
        c(g+'_shovel_palm',palm,(6.4,2.3,5),'chitin',g)
        for i in range(3):
            s(g+f'_digging_blade_{i}',[side*11+(i-1)*1.9,3,-10],[side*11+(i-1)*2.2,.9,-14],1.2,1.8,'ivory',g)
            c(g+f'_blade_root_{i}',(side*11+(i-1)*1.9,3.8,-10),(1.6,1,2.1),'bone',g)
        for i in (-1,1):
            c(g+f'_carpal_plate_{i}',(side*11+i*.85,5.3,-7.5),(.8,3.1,1.3),'bone',g)
        g='left_leg' if side==-1 else 'right_leg'
        a=[side*3.5,11,8];b=[side*6.7,5,12];foot=[side*6.7,1.3,9]
        s(g+'_thigh',a,b,3,3.4,'skin',g)
        s(g+'_hock',b,foot,1.7,2,'bone',g)
        c(g+'_joint',b,(3.3,2.2,3.1),'chitin',g)
        c(g+'_paw',foot,(3.8,1.5,4.3),'chitin',g)
        for i in range(3):
            c(g+f'_claw_{i}',(foot[0]+(i-1)*1.1,.9,6.5),(.7,.7,1.6),'ivory',g)
    c('burrow_neck',(0,12,-7),(6,5,5),'skin','head')
    c('flat_cranium',(0,13,-9.3),(7,5,6),'chitin','head')
    c('snout_shield',(0,11.7,-12.3),(6.2,2.6,4),'bone','head')
    c('mouth_void',(0,10.1,-13.7),(4.8,1.7,.7),'void','head')
    for side in (-1,1):
        c(f'cheek_plate_{side}',(side*3.3,11.8,-10),(1.6,3.5,4.3),'bone','head')
        for i in range(2):
            c(f'eye_socket_{side}_{i}',(side*(1.4+i*1.4),14,-11.9),(1.6,1.4,.6),'void','head')
            c(f'eye_{side}_{i}',(side*(1.4+i*1.4),14,-12.3),(.65,.6,.35),'eye','head')
        c(f'mandible_{side}',(side*2.6,9.4,-11.7),(1.3,1.6,5.2),'chitin','jaw')
        for i in range(3):
            c(f'tooth_{side}_{i}',(side*2.1,10.1,-11.4-i*.9),(.55,1,.65),'ivory','jaw')
    s('tail_root',[0,9,10],[0,7,14],2.5,3,'chitin','tail')
    s('tail_tip',[0,7,14],[1.2,4,17],1.3,1.7,'chitin','tail')
    c('tail_barb',(1.2,4,17),(1.3,2.5,1.7),'bone','tail',rotation=(16,0,0))
    return p


def coffin_strider(cube,segment):
    p,c,s=bind(cube,segment)
    c('pelvis',(0,17,1),(7,4,5),'bone')
    c('rib_core',(0,26,1),(7,14,5),'void')
    for side in (-1,1):
        for i in range(5):
            c(f'rib_{side}_{i}',(side*2.5,22+i*2,-2),(4.2,.9,1.2),'bone',rotation=(0,0,side*12))
        g='left_leg' if side==-1 else 'right_leg'
        a=[side*2.5,17,1];b=[side*3.5,9,1];foot=[side*3.5,1.5,0]
        s(g+'_femur',a,b,2.3,2.8,'bone',g)
        s(g+'_tibia',b,foot,1.3,1.7,'bone',g)
        c(g+'_knee',b,(2.8,2.1,2.8),'iron',g)
        c(g+'_foot',(side*3.5,1.3,-1.5),(3.5,2.5,5.3),'wrap',g)
        for i in range(3):
            c(g+f'_toe_{i}',(side*3.5+(i-1)*.85,1,-4.1),(.55,.9,1),'bone',g)
        for i in range(2):
            c(g+f'_binding_{i}',(side*3.5,4+i*2,1),(2.2,.9,2.5),'wrap',g)
        g='left_arm' if side==-1 else 'right_arm'
        s(g+'_upper',[side*5.3,30,1],[side*9,24,1],2,2.5,'bone',g)
        s(g+'_forearm',[side*9,24,1],[side*11,18,-2],1.4,1.7,'bone',g)
        c(g+'_hand',(side*11,17.5,-2),(2.7,2.7,2.5),'bone',g)
        c(g+'_bracer',(side*10,20,-.5),(3,2,3),'wrap',g)
        c(g+'_shoulder',(side*5.3,31,1),(4.2,2,5),'iron',g)
        for i in range(3):
            c(g+f'_finger_{i}',(side*11+(i-1)*.7,15.7,-2.7),(.5,1.8,1),'bone',g)
    for i in range(5):
        c(f'spine_{i}',(0,21+i*2.5,4),(2,1.6,1.4),'bone')
    for i in range(4):
        c(f'waist_rag_{i}',((i-1.5)*1.7,15,-2.8),(2,7+(i%2),1),'cloth',rotation=(0,0,(i-1.5)*4))
    c('neck',(0,34,1),(2.5,4,3),'wrap','head')
    c('skull',(0,38,-.5),(5.8,6.5,5.4),'bone','head')
    c('jaw',(0,35,-1.4),(4.5,1.9,3.6),'bone','head')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*1.6,38.4,-3.4),(2,1.7,.6),'void','head')
        c(f'eye_{side}',(side*1.6,38.4,-3.8),(.7,.6,.35),'cloud_eye','head')
        c(f'cheek_wrap_{side}',(side*2.8,37.1,-1.8),(1.1,4,4),'wrap','head')
    for i in range(5):
        c(f'tooth_{i}',((i-2)*.7,35.6,-3.5),(.45,.8,.5),'ivory','head')
    c('coffin_body',(-13,16.2,0),(9,28,4.5),'bark','coffin')
    for i in range(5):
        c(f'coffin_lid_board_{i}',(-13+(i-2)*1.65,16.2,-2.7),(1.5,25,1),'bark','coffin')
    for y in (3.5,29):
        c(f'coffin_end_band_{y}',(-13,y,-3.2),(10,1.5,1.2),'iron','coffin')
    for x in (-17.4,-8.6):
        c(f'coffin_side_band_{x}',(x,16,-3.1),(1.3,27,1.3),'iron','coffin')
        for y in (6,16,26):
            c(f'coffin_rivet_{x}_{y}',(x,y,-3.9),(.9,.9,.6),'metal','coffin')
    c('coffin_effigy_spine',(-13,17,-3.7),(1.1,11,.8),'bone','coffin')
    for i in range(4):
        c(f'effigy_rib_{i}',(-13,15+i*2,-3.8),(4,.7,.9),'bone','coffin')
    c('coffin_effigy_mask',(-13,24,-3.9),(3.3,3.5,1),'bone','coffin')
    c('coffin_handle',(-9,19,1.5),(2,5,2),'iron','coffin')
    return p


def choir_wight(cube,segment):
    p,c,s=bind(cube,segment)
    c('hollow_chest',(0,24,1),(6,11,5),'void')
    for side in (-1,1):
        for i in range(4):
            c(f'singing_rib_{side}_{i}',(side*2.7,21+i*2.3,-1.8),(4.3,.9,1.4),'bone',rotation=(0,0,side*15))
        for i in range(4):
            low=3+(i%2)*1.1
            c(f'vestment_{side}_{i}',(side*(1+i*1.4),(low+21)/2,2),(1.7,21-low,1.1),'membrane',rotation=(0,0,side*(4+i*3)))
        g='left_arm' if side==-1 else 'right_arm'
        s(g+'_upper',[side*5,28,1],[side*9,23,0],1.9,2.3,'bone',g)
        s(g+'_forearm',[side*9,23,0],[side*10,17,-4],1.2,1.6,'bone',g)
        c(g+'_cuff',(side*10,18.5,-3),(2.6,1.5,2.8),'membrane',g)
        c(g+'_palm',(side*10,16.8,-4.5),(2.5,2.1,2.1),'bone',g)
        for i in range(3):
            s(g+f'_finger_{i}',[side*10+(i-1)*.65,16,-5],[side*10+(i-1),13.8,-6.2],.45,.6,'ivory',g)
    for i in range(5):
        c(f'vertebra_{i}',(0,19+i*2.3,3.7),(1.8,1.3,1.2),'bone')
    # Three open throat rings visibly frame the singer's resonant cavity.
    for i in range(3):
        y=29+i*2.8
        for side in (-1,1):
            c(f'throat_side_{i}_{side}',(side*2.4,y,0),(.7,2.4,4),'bone','head')
            c(f'throat_lip_{i}_{side}',(0,y+side*1.2,-1.9),(5,.65,.7),'bone','head')
    c('cranium',(0,39,-.7),(6.3,6,5.8),'bone','head')
    c('mouth_void',(0,36.8,-3.7),(4.3,3,.7),'void','head')
    c('lower_jaw',(0,35.1,-2.5),(5,1.5,3.8),'bone','jaw')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*1.6,39.3,-3.8),(1.9,1.5,.6),'void','head')
        c(f'eye_{side}',(side*1.6,39.3,-4.2),(.65,.6,.35),'rune','head')
        c(f'cheek_{side}',(side*2.8,37.5,-3),(1,2.7,1.4),'bone','head')
        c(f'tuning_fork_{side}',(side*5.5,38,3),(1.7,22,2.2),'metal','resonator')
        c(f'fork_crossbrace_{side}',(side*2.7,28.5,3),(5.5,1.8,2.5),'iron','resonator')
        for i in range(3):
            c(f'fork_inscription_{side}_{i}',(side*5.5,34+i*4,1.7),(.75,2,.5),'rune','resonator')
    for i in range(5):
        c(f'teeth_{i}',((i-2)*.75,35.8,-4.2),(.45,.75,.6),'ivory','jaw')
    for i in range(5):
        c(f'choir_sigil_{i}',((i-2)*1.1,23,-3),(1,1.6,.7),'rune')
    for side in (-1,1):
        c(f'jaw_hinge_{side}',(side*2.7,35.7,-1.4),(1.2,1.5,1.3),'bone','head')
        for i in range(3):
            c(f'fork_baffle_{side}_{i}',(side*5.5,32+i*5,3),(2.6,.9,3.3),'iron','resonator')
    c('sternum_seal',(0,25,-2.8),(1.3,5,.9),'metal')
    return p


def hollow_sexton(cube,segment):
    p,c,s=bind(cube,segment)
    c('torso',(0,24,1),(12,13,8),'skin')
    c('shoulder_coat',(0,29,2),(15,4,10),'leather')
    for i in range(6):
        x=(i-2.5)*2
        for side in (-1,1):
            c(f'grave_coat_{side}_{i}',(x,17,1+side*4.5),(2.3,16-(i%2),1),'leather',rotation=(0,(i-2.5)*1.5,0))
    c('belt',(0,20,1),(12.5,1.4,9.7),'iron')
    c('buckle',(0,20,-4.4),(3,2,1),'metal')
    for i in range(3):
        c(f'toll_token_{i}',((i-1)*2,17.8,-4.8),(1.4,1.6,.7),'metal')
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        s(g+'_thigh',[side*3.5,17,1],[side*4.5,9,1],3.4,4,'cloth',g)
        s(g+'_shin',[side*4.5,9,1],[side*4.2,2,0],2.5,3.1,'leather',g)
        c(g+'_boot',(side*4.2,1.5,-1),(4.5,3,6),'leather',g)
        for i in range(3):
            c(g+f'_greave_{i}',(side*4.3,4+i*1.5,-1.5),(3.3,.8,1),'iron',g)
        g='left_arm' if side==-1 else 'right_arm'
        s(g+'_upper',[side*8,28,1],[side*11,22,0],3.5,4.1,'leather',g)
        s(g+'_forearm',[side*11,22,0],[side*11.5,16,-4],2.2,2.8,'wrap',g)
        c(g+'_hand',(side*11.5,15.3,-4.5),(3.1,2.6,2.7),'skin',g)
        c(g+'_cuff',(side*11.4,17.5,-3),(3.7,1.7,4),'iron',g)
        for i in range(3):
            c(g+f'_finger_{i}',(side*11.5+(i-1)*.85,13.7,-5.1),(.65,1.6,1),'skin',g)
    c('neck',(0,32,0),(4,4,4.5),'wrap','head')
    c('gaunt_face',(0,36,-1),(6.2,6.4,5.5),'skin','head')
    c('lower_wrap',(0,33.9,-2.5),(5,2.2,3.4),'wrap','head')
    c('hood_crown',(0,40,1),(8.8,2,7.5),'leather','head')
    for side in (-1,1):
        c(f'hood_side_{side}',(side*3.8,36,.7),(1.6,8.5,6.5),'leather','head')
        c(f'eye_socket_{side}',(side*1.7,36.6,-3.9),(2,1.5,.6),'shadow_skin','head')
        c(f'eye_{side}',(side*1.7,36.6,-4.3),(.65,.6,.35),'cloud_eye','head')
        c(f'brow_{side}',(side*1.7,37.7,-3.7),(2.5,.75,.8),'skin','head',rotation=(0,0,side*9))
    s('bell_staff',[13,1,-3],[13,43,-3],1.8,2,'bark','right_arm')
    c('staff_crossbar',(13,42,-3),(15,1.7,2.5),'iron','right_arm')
    for i in range(3):
        c(f'staff_binding_{i}',(13,13+i*5,-3),(2.7,1.2,2.8),'wrap','right_arm')
    for i in range(3):
        x=8+i*5;y=36+i*1.2;g=f'bell_{i}'
        s(g+'_suspension',[x,41.5,-3],[x,y+2,-3],.5,.65,'iron',g)
        c(g+'_crown',(x,y+1.6,-3),(2,1.5,2),'metal',g)
        for side in (-1,1):
            c(g+f'_side_{side}',(x+side*1.8,y,-3),(.7,2.5,3.5),'metal',g)
            c(g+f'_front_back_{side}',(x,y,-3+side*1.5),(3.5,2.5,.7),'metal',g)
        c(g+'_clapper',(x,y-.7,-3),(.8,3,.9),'iron',g)
    s('grave_spade_haft',[-12,2,-4],[-12,25,-4],1.5,1.8,'bark','left_arm')
    c('grave_spade_blade',(-12,4,-4),(6.5,7,1.6),'iron','left_arm')
    c('grave_spade_edge',(-12,.6,-4),(5,.8,1),'metal','left_arm')
    return p


def sculpts(cube,segment):
    return [(name,fn(cube,segment)) for name,fn in (
        ('sepulcher_hound',sepulcher_hound),('briar_witness',briar_witness),
        ('wicker_pilgrim',wicker_pilgrim),('pale_deacon',pale_deacon),
        ('carrion_lurker',carrion_lurker),('coffin_strider',coffin_strider),
        ('choir_wight',choir_wight),('hollow_sexton',hollow_sexton))]
