"""Third original Act I art wave; catalogue behaviors remain unimplemented."""
import math
from labyrinth_creature_wave_02 import bind

PALETTES={
    'censer_revenant':[(154,146,124),(167,131,99),(124,160,160)],
    'rift_acolyte':[(146,160,149),(160,133,111),(119,169,179)],
    'skullglass_shardling':[(153,171,190),(175,132,144),(111,174,183)],
    'coal_moth':[(91,86,71),(126,91,65),(82,122,133)],
    'chapel_butcher':[(163,133,121),(161,116,96),(129,154,151)],
    'dust_friar':[(161,157,135),(180,145,111),(136,168,168)],
}


def censer_revenant(cube,segment):
    p,c,s=bind(cube,segment)
    c('hollow_core',(0,24,1),(5.5,10,4),'void')
    for i in range(6):
        c(f'vertebra_{i}',(0,19+i*2,3.5),(2.5,1.3,2),'bone')
    for side in (-1,1):
        for i in range(5):
            c(f'bronze_rib_{side}_{i}',(side*3.2,29-i*2,-1.3),(5.5,1.1,1.8),'metal',rotation=(0,0,side*16))
        c(f'shoulder_yoke_{side}',(side*5.2,30,1),(5.5,2.5,6),'iron',rotation=(0,0,side*-14))
        s(f'chest_chain_{side}',[side*4,28,-2],[side*3,19,-5],.7,.9,'iron')
        for i in range(4):
            low=4+(i%2)*1.4
            c(f'leather_tatter_{side}_{i}',(side*(1+i*1.3),(low+20)/2,2),(1.3,20-low,.8),'leather',rotation=(0,0,side*(i+1)*3))
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*6,29,0];b=[side*10,23,-1];hand=[side*8.5,18,-4]
        s(g+'_upper',a,b,1.9,2.2,'bone',g)
        s(g+'_forearm',b,hand,1.3,1.6,'bone',g)
        c(g+'_bracer',b,(3.3,2,3.6),'metal',g)
        c(g+'_palm',hand,(2.3,2,2),'bone',g)
        for i in range(3):
            s(g+f'_finger_{i}',[hand[0]+(i-1)*.65,17.4,-4],[hand[0]+(i-1)*.8,15.3,-5.3],.5,.6,'ivory',g)
    c('neck',(0,32,0),(3,4,3.5),'bone','head')
    c('mask',(0,36,-1),(5.5,6,4.8),'bone','head')
    c('jaw',(0,33.1,-2),(4.2,1.6,3),'bone','head')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*1.5,36.3,-3.6),(2,1.7,.5),'void','head')
        c(f'eye_{side}',(side*1.5,36.3,-4),(.7,.6,.35),'rune','head')
        c(f'face_grille_{side}',(side*2.5,34.9,-3.3),(.9,3,.8),'iron','head')
    for i in range(5):
        c(f'tooth_{i}',((i-2)*.65,33.8,-3.5),(.4,.7,.6),'ivory','head')
    for i in range(8):
        a=math.tau*i/8
        c(f'ritual_halo_{i}',(math.cos(a)*5.5,37+math.sin(a)*5.5,2),(2,3,1.4),'metal','head',rotation=(0,0,90+i*45))
    c('censer_floor',(0,13,-5),(8,1.4,7),'iron','censer')
    c('censer_embers',(0,14.2,-5),(5,1.2,4),'eye','censer')
    for x in (-3.5,3.5):
        for z in (-7.8,-2.2):
            c(f'censer_stile_{x}_{z}',(x,16.2,z),(.9,5,.9),'metal','censer')
    for side in (-1,1):
        c(f'censer_rim_{side}',(side*3.7,18.4,-5),(1.2,1.3,7.8),'metal','censer')
        c(f'censer_ring_{side}',(0,18.4,-5+side*3.2),(7.5,1.3,1.2),'metal','censer')
    c('censer_lid',(0,19.5,-5),(8,1.2,7),'iron','censer_lid')
    c('censer_finial',(0,20.8,-5),(2,1.7,2),'metal','censer_lid')
    for i in range(4):
        c(f'censer_vent_{i}',((i-1.5)*1.6,15.8,-8.2),(.8,3,.5),'void','censer')
    for i in range(6):
        c(f'shoulder_stud_{i}',((i-2.5)*2,31,2),(1.2,1.3,1.4),'bone')
    return p


def rift_acolyte(cube,segment):
    p,c,s=bind(cube,segment)
    c('torso',(0,24,0),(8,10,6),'cloth')
    c('tunic_waist',(0,17,1),(8.5,5,6.5),'cloth')
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        s(g+'_thigh',[side*2.6,17,1],[side*3.2,9,1],2.8,3.2,'cloth',g)
        s(g+'_shin',[side*3.2,9,1],[side*3.5,2,0],2,2.5,'leather',g)
        c(g+'_boot',(side*3.5,1.5,-1),(3.7,2.8,5.5),'leather',g)
        c(g+'_toe',(side*3.5,1.5,-4),(2.3,1.6,2.5),'metal',g,rotation=(10,0,0))
        for i in range(3):
            c(g+f'_greave_{i}',(side*3.3,4.2+i*1.6,-1.3),(2.7,.8,.8),'trim',g)
        for i in range(3):
            c(f'tunic_tail_{side}_{i}',(side*(1.2+i*1.1),12+i*.7,3.5),(1.3,9-i*.7,1),'cloth',rotation=(4,0,side*8))
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*5,27,0];b=[side*8,22,-1];hand=[side*7,19,-5]
        s(g+'_sleeve',a,b,3,3.4,'cloth',g)
        s(g+'_forearm',b,hand,2,2.5,'wrap',g)
        c(g+'_cuff',hand,(3.3,2,3.5),'metal',g)
        c(g+'_palm',(hand[0],18.4,-5.5),(2.6,1.6,2.4),'skin',g)
        for i in range(3):
            s(g+f'_finger_{i}',[hand[0]+(i-1)*.7,18.2,-6],[hand[0]+(i-1)*.8,17.1,-7.6],.45,.6,'skin',g)
        for i in range(3):
            c(g+f'_projector_prong_{i}',(side*7+(i-1),20,-5.8),(.55,2,2.4),'iron',g)
            c(g+f'_projector_seal_{i}',(side*7+(i-1),21.2,-5.6),(.5,.45,1.7),'rune',g)
            c(g+f'_knuckle_plate_{i}',(side*7+(i-1)*.7,18.5,-6.5),(.8,.5,.8),'metal',g)
        c(f'shoulder_conduit_{side}',(side*4.1,25,-3.5),(.75,5,.7),'rune')
        c(f'back_tablet_{side}',(side*2.4,24,3.8),(2.6,5,1.2),'iron')
        for i in range(3):
            c(f'collar_fan_{side}_{i}',(side*(2.8+i*1.3),29-i*.7,1),(2.2,1.4,6),'trim',rotation=(0,0,side*(15+i*8)))
    c('neck',(0,30,0),(3,3,3.5),'wrap','head')
    c('mask',(0,34,-1),(5.3,6.3,4.8),'iron','head')
    c('mask_inset',(0,34,-3.6),(3.7,4.7,.6),'void','head')
    c('mask_vertical_rune',(0,34,-4.1),(.8,4,.4),'rune','head')
    for side in (-1,1):
        c(f'eye_{side}',(side*1.2,34.8,-4),(.7,.6,.4),'rune','head')
        c(f'hood_side_{side}',(side*3.3,34,0),(1.5,8,6),'cloth','head',rotation=(0,0,side*-7))
        c(f'forked_crest_{side}',(side*2.5,39.2,.5),(1.3,5.5,2.2),'metal','head',rotation=(0,0,side*-17))
        c(f'crest_rune_{side}',(side*2.5,39.3,-.7),(.7,3.5,.4),'rune','head',rotation=(0,0,side*-17))
    c('hood_crown',(0,38,1),(7.6,1.6,6),'cloth','head')
    for i in range(5):
        c(f'waist_tablet_{i}',((i-2)*1.5,17,-3.7),(1.2,3,.8),'metal')
        c(f'tablet_glyph_{i}',((i-2)*1.5,17,-4.2),(.55,1.8,.4),'rune')
    c('back_spine',(0,23,3.6),(1.4,9,1.2),'iron')
    return p


def skullglass_shardling(cube,segment):
    p,c,s=bind(cube,segment)
    c('glass_core',(0,8,0),(7,7,7),'crystal')
    c('heart',(0,8,-3.6),(2.6,2.6,.8),'core')
    for i in range(6):
        angle=math.tau*i/6
        dx,dz=math.cos(angle),math.sin(angle)
        g=f'shard_{i}'
        c(g+'_facet',(dx*4.5,10.4,dz*4.5),(2.8,6,3.5),'crystal',g,rotation=(i*7,0,math.degrees(angle)))
        s(g+'_spine',[dx*3.4,11,dz*3.4],[dx*5.5,16.5,dz*5.5],1.3,1.8,'crystal',g)
        c(g+'_binding',(dx*4,8,dz*4),(1.7,2,1.7),'bone',g)
        c(g+'_seam',(dx*4.8,12,dz*4.8),(.7,2,1),'core',g)
    for side in (-1,1):
        for i in range(3):
            g=('left' if side==-1 else 'right')+f'_leg_{i}'
            a=[side*3.5,7,-3+i*3];b=[side*7.5,5,-5+i*5];tip=[side*10,.8,-6+i*6]
            s(g+'_upper',a,b,1.4,1.8,'bone',g)
            s(g+'_lower',b,tip,.9,1.3,'crystal',g)
            c(g+'_joint',b,(2,1.8,2),'ivory',g)
            c(g+'_toe',tip,(1.6,.8,1.7),'iron',g)
            c(g+'_joint_light',(b[0],b[1]+1,b[2]),(.8,.5,.9),'core',g)
        for i in range(4):
            c(f'glass_rib_{side}_{i}',(side*2.7,7.3+i*.8,-3.7),(2,.6,1.2),'bone')
    c('skull_plate',(0,10,-4.5),(5.8,5,2),'bone','head')
    c('jaw',(0,7.4,-4.7),(4.8,1.3,1.8),'bone','head')
    c('nose_void',(0,9.3,-5.6),(.9,1.1,.4),'void','head')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*1.5,10.4,-5.6),(1.9,1.5,.5),'void','head')
        c(f'eye_{side}',(side*1.5,10.4,-5.9),(.7,.7,.3),'eye','head')
        c(f'cheek_{side}',(side*2.5,8.9,-5.2),(.9,1.6,1),'ivory','head')
    for i in range(5):
        c(f'tooth_{i}',((i-2)*.7,7.9,-5.6),(.4,.75,.4),'ivory','head')
    for i in range(8):
        a=math.tau*i/8
        c(f'core_facet_{i}',(math.cos(a)*2.4,7.7,math.sin(a)*2.4),(1.2,3.5,2),'taint',rotation=(0,math.degrees(a),12))
    for i in range(4):
        c(f'crown_shard_{i}',((i-1.5)*1.8,13,.7),(1.2,4.3,1.8),'crystal',rotation=(0,0,(i-1.5)*10))
    return p


def coal_moth(cube,segment):
    p,c,s=bind(cube,segment)
    c('thorax',(0,12,0),(4.8,5,6),'fur')
    c('abdomen',(0,10.8,6),(4,4,8),'chitin')
    for i in range(6):
        c(f'abdomen_ring_{i}',(0,11.4,2.7+i*1.2),(4.4-i*.25,2.1,1),'fur')
    c('tail_tip',(0,10,10.1),(1.6,2,2),'chitin')
    c('head',(0,12.3,-4.1),(4,4,3.5),'fur','head')
    for side in (-1,1):
        c(f'eye_{side}',(side*2,12.7,-4.8),(1.1,2,1.4),'eye','head')
        for i in range(3):
            a=[side*(1.2+i*.8),14+i*1.1,-4.7-i*.6];b=[side*(2+i*.8),15.1+i*1.1,-5.3-i*.6]
            s(f'antenna_{side}_{i}',a,b,.4,.5,'chitin','head')
        for i in range(3):
            c(f'neck_ruff_{side}_{i}',(side*(1.4+i*.65),13.8,-1.6+i*.8),(1.5,2,1.4),'fur')
        for i in range(3):
            g=('left' if side==-1 else 'right')+f'_leg_{i}'
            a=[side*2,11,-1+i*2];b=[side*4.7,7,-3+i*3];tip=[side*6,4.3,-4+i*4]
            s(g+'_coxa',a,b,.7,.9,'chitin',g)
            s(g+'_tarsus',b,tip,.45,.65,'iron',g)
            c(g+'_joint',b,(1,1,1.2),'chitin',g)
        for hind in (False,True):
            g=('left' if side==-1 else 'right')+('_hindwing' if hind else '_wing')
            for i in range(4):
                x=side*(4+i*2.3);z=(5+i*1.1) if hind else (-3.8-i*.8)
                y=12+(abs(x)-2)*.55
                c(g+f'_panel_{i}',(x,y,z),(3.2,1,7-i*.7),'membrane',g,rotation=(0,side*(12 if hind else -18),side*28))
                c(g+f'_ember_mark_{i}',(x,y+.65,z-1),(2.1,.35,1.4),'cap',g,rotation=(0,0,side*28))
            for i in range(3):
                s(g+f'_vein_{i}',[side*2,12,3 if hind else -1],[side*(7+i*2),12+(5+i*2)*.55,(9+i) if hind else (-8-i)],.35,.5,'chitin',g)
            c(g+'_eye_ring',(side*9.2,16.4,6.5 if hind else -5),(2.9,.45,3.2),'void',g,rotation=(0,0,side*28))
            c(g+'_eye_spot',(side*9.2,16.7,6.5 if hind else -5),(1.6,.3,1.9),'eye',g,rotation=(0,0,side*28))
    s('proboscis_upper',[0,11.8,-5.3],[0,10,-7],.55,.6,'chitin','head')
    s('proboscis_hook',[0,10,-7],[0,9.5,-5.6],.45,.5,'chitin','head')
    for i in range(4):
        c(f'dorsal_fur_{i}',(0,14.3,-1+i*1.6),(1.8,1.2,2),'fur')
    return p


def chapel_butcher(cube,segment):
    p,c,s=bind(cube,segment)
    c('barrel_torso',(0,27,1),(17,19,11),'skin')
    c('belly',(0,19,-1),(16,12,12),'shadow_skin')
    c('spinal_hump',(0,34,4),(15,8,11),'skin',rotation=(13,0,0))
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        s(g+'_thigh',[side*5,17,1],[side*6,9,1],6,6.5,'skin',g)
        s(g+'_shin',[side*6,9,1],[side*5.5,2,0],4.2,5,'shadow_skin',g)
        c(g+'_boot',(side*5.5,1.8,-1),(6,3.5,8),'leather',g)
        c(g+'_knee',(side*6,10,-2),(5,3,2),'bone',g)
        for i in range(3):
            c(g+f'_binding_{i}',(side*5.5,4+i*1.4,0),(4.9,.8,5.6),'wrap',g)
        c(g+'_toe_cap',(side*5.5,2,-5.2),(5,2,1.4),'iron',g)
    for i in range(7):
        x=(i-3)*2
        c(f'apron_panel_{i}',(x,21,-7.7-(i%2)*.15),(2.4,22-(i%3),1.1),'leather',rotation=(0,(i-3)*1.5,0))
        c(f'apron_hem_{i}',(x,10.5+(i%3)*.4,-8.4),(2.1,1.1,.6),'wrap')
    for i in range(5):
        c(f'apron_stitch_{i}',(-4+i*2,27,-8.4),(1.2,.55,.5),'wrap')
        c(f'old_scar_{i}',(5,29+i*1.2,-4.8),(2.4,.5,.6),'scar',rotation=(0,0,12))
    c('belt',(0,19,0),(17.2,2,12),'iron')
    c('apron_belt_front',(0,19,-8.4),(17.2,2,.7),'iron')
    c('buckle',(0,19,-8.9),(4,3,1),'metal')
    for side in (-1,1):
        for i in range(3):
            c(f'spine_knob_{side}_{i}',(side*3,28+i*2.4,7.2),(2,1.7,1.6),'bone')
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*10,33,1];b=[side*14,26,0];hand=[side*14,19,-3]
        s(g+'_upper',a,b,6.5,7,'skin',g)
        s(g+'_forearm',b,hand,4.5,5.5,'shadow_skin',g)
        c(g+'_elbow',b,(6,3,6.5),'bone',g)
        c(g+'_wrist',hand,(5.5,2,6),'leather',g)
        c(g+'_palm',(side*14,18,-3),(5,4,4),'skin',g)
        for i in range(3):
            s(g+f'_finger_{i}',[side*14+(i-1)*1.4,17,-4],[side*14+(i-1)*1.4,14.7,-5.4],1,1.2,'skin',g)
        for i in range(2):
            c(g+f'_bracer_stud_{i}',(side*14,22+i*1.6,-2),(5.5,1,5),'iron',g)
    c('neck',(0,37,0),(7,4,7),'skin','head')
    c('skull',(0,41,-1),(8.5,8,7.5),'skin','head')
    c('jaw',(0,37.8,-3.2),(8,3.5,5),'shadow_skin','head')
    c('mask_plate',(0,41,-5),(8,7,1.5),'iron','head')
    c('mask_slit',(0,41,-6),(6,1.6,.6),'void','head')
    for side in (-1,1):
        c(f'eye_{side}',(side*2,41,-6.4),(1.2,.8,.35),'eye','head')
        c(f'mask_rivet_{side}',(side*3.2,43,-6),(1,1,.7),'metal','head')
        c(f'mandible_tusk_{side}',(side*3.3,38,-5.8),(1.2,3.1,1.3),'ivory','head',rotation=(0,0,side*-13))
    s('cleaver_handle',[14,9,-4],[14,23,-4],2,2.3,'bark','right_arm')
    for i in range(3):
        c(f'handle_wrap_{i}',(14,13+i*2,-4),(2.8,1,3),'wrap','right_arm')
    c('cleaver_spine',(18.5,10,-4),(11,2,2.5),'iron','cleaver')
    c('cleaver_blade',(19,5.7,-4),(10.5,7.5,1.4),'metal','cleaver')
    c('cleaver_edge',(19,1.6,-4),(10.8,.9,.6),'iron','cleaver')
    for i in range(3):
        c(f'blade_notch_{i}',(16+i*3,2.1,-4),(1.2,1.6,1.8),'iron','cleaver')
    c('blade_eye',(21,10.5,-4),(1.4,1.1,2.9),'void','cleaver')
    return p


def dust_friar(cube,segment):
    p,c,s=bind(cube,segment)
    c('rounded_habit',(0,15,1),(14,23,11),'wrap')
    c('shoulder_mantle',(0,25,2),(16,6,12),'wrap')
    for i in range(8):
        x=(i-3.5)*1.65;low=2+(i%2)*.7
        for side in (-1,1):
            c(f'habit_fold_{side}_{i}',(x,(low+24)/2,1+side*5.5),(1.9,24-low,1),'wrap',rotation=(0,0,(i-3.5)*1.2))
        c(f'habit_hem_{i}',(x,low+.6,-5.2),(1.6,.9,.6),'cloth')
    c('rope_belt',(0,17,1),(14.5,1.2,11.7),'leather')
    for i in range(5):
        c(f'belt_bead_{i}',(-3,15-i*1.6,-5.3),(.9,.9,.9),'bone')
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        c(g+'_shin',(side*3.4,4,1),(2.3,5,3),'cloth',g)
        c(g+'_shoe',(side*3.4,1.2,-1),(4,2.3,5),'leather',g)
        c(g+'_toe',(side*3.4,1.3,-3.5),(3.4,1.8,1.4),'iron',g)
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*8,25,1];b=[side*11,20,0];hand=[side*10,15,-4]
        s(g+'_sleeve',a,b,4.5,5,'wrap',g)
        s(g+'_forearm',b,hand,2.5,3,'wrap',g)
        c(g+'_cuff',hand,(4,2,4),'cloth',g)
        c(g+'_palm',(side*10,14,-4),(3.3,2.6,3),'bone',g)
        for i in range(3):
            s(g+f'_finger_{i}',[side*10+(i-1)*.9,13.4,-4.5],[side*10+(i-1)*.9,12,-5.6],.6,.7,'bone',g)
    c('neck',(0,29,0),(4,3,4),'wrap','head')
    c('hood_recess',(0,32,-1),(7,6,5),'void','head')
    for side in (-1,1):
        c(f'hood_side_{side}',(side*4,32,0),(2,9,7.5),'wrap','head',rotation=(0,0,side*-8))
        c(f'eye_{side}',(side*1.6,32.2,-3.8),(.9,.7,.4),'cloud_eye','head')
        c(f'face_fold_{side}',(side*2.6,30.2,-3.6),(1.5,3,1),'wrap','head',rotation=(0,0,side*15))
    c('hood_crown',(0,36.8,1),(9,2,7.5),'wrap','head')
    c('chin_wrap',(0,29.5,-2.7),(4.5,2.3,2),'wrap','head')
    for i in range(5):
        c(f'collar_pleat_{i}',((i-2)*2,27,-3.5),(2,2,3),'wrap')
    # The friar's counterplay object is actually attached to the raised hand.
    c('censer_bowl',(10,10,-5),(6.5,2,6),'metal','censer')
    for side in (-1,1):
        c(f'bowl_rim_{side}',(10+side*3,12,-5),(1,2,6.4),'metal','censer')
        c(f'bowl_front_back_{side}',(10,12,-5+side*2.6),(5.8,2,1),'iron','censer')
    c('dust_bed',(10,11.6,-5),(4.5,.8,4),'bone','censer')
    for i in range(4):
        x=8.4+(i%2)*3.2;z=-6.5+(i//2)*3
        s(f'censer_chain_{i}',[x,12.7,z],[10,15,-5],.4,.55,'iron','censer')
    c('censer_grip',(10,15,-5),(1.8,1,2),'iron','censer')
    c('prayer_book_lower',(-10,12,-6),(5,.8,4),'leather','left_arm')
    c('prayer_book_pages',(-10,12.9,-6),(4.6,1,3.5),'wrap','left_arm')
    c('prayer_book_upper',(-10,13.8,-6),(5,.6,4),'leather','left_arm')
    c('prayer_book_spine',(-12.4,13,-6),(.7,2.5,4),'leather','left_arm')
    for side in (-1,1):
        c(f'book_clasp_{side}',(-10+side*1.6,14.2,-6),(.7,.45,3.7),'metal','left_arm')
        c(f'book_page_marker_{side}',(-10+side*.7,13,-8),(.45,1.5,.4),'cloth','left_arm')
    return p


def sculpts(cube,segment):
    return [(name,fn(cube,segment)) for name,fn in (
        ('censer_revenant',censer_revenant),('rift_acolyte',rift_acolyte),
        ('skullglass_shardling',skullglass_shardling),('coal_moth',coal_moth),
        ('chapel_butcher',chapel_butcher),('dust_friar',dust_friar))]
