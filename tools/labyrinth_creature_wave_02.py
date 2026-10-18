"""Second original Act I sculpture wave: six distinct catalogue anatomies.

The rat is one small member of a future pack. The grave thorn is a rooted trap,
not a reskin of the installed mobile Thorn Infestor. No runtime actors are added.
"""
import math

PALETTES = {
    'hollow_veil': [(146,154,155),(160,132,117),(128,168,172)],
    'lantern_ghoul': [(127,143,111),(158,127,92),(116,154,151)],
    'corvid_undertaker': [(87,91,101),(112,92,81),(77,112,122)],
    'rotmilk_ratpack': [(158,142,119),(148,112,89),(122,156,155)],
    'grave_thorn': [(101,119,79),(136,111,75),(92,137,135)],
    'mourning_matron': [(171,167,145),(181,144,119),(145,176,176)],
}


def bind(cube,segment):
    p=[]
    def c(*args,**kwargs):cube(p,*args,**kwargs)
    def s(*args,**kwargs):segment(p,*args,**kwargs)
    return p,c,s


def hollow_veil(cube,segment):
    p,c,s=bind(cube,segment)
    c('empty_thorax',(0,25,1),(7,11,5),'void')
    for i in range(7):
        x=(i-3)*1.7
        for side in (-1,1):
            low=3+(i%3)*1.2
            c(f'veil_streamer_{side}_{i}',(x,(low+27)/2,side*3.8),(1.9,27-low,.75),'cloth',rotation=(side*7,0,(i-3)*2))
        c(f'frayed_hem_{i}',(x,low,-4.1),(1.1,2,.5),'wrap',rotation=(0,0,(i-3)*7))
    for side in (-1,1):
        for i in range(5):
            c(f'cloak_fold_{side}_{i}',(side*(5+i*.8),28-i*2,2),(1.7,13-i,4),'cloth',rotation=(0,0,side*(10+i*3)))
        for i in range(4):
            c(f'floating_rib_{side}_{i}',(side*2.7,28-i*1.8,-2.3),(4.3,.8,1.1),'bone',rotation=(0,0,side*14))
    c('sternum_key',(0,25,-3.2),(1.2,7,1),'rune')
    c('neck',(0,32,0),(2.5,3,3),'bone','head')
    c('skull_mask',(0,36,-.7),(5,6,4.6),'bone','head')
    c('veil_void_face',(0,35.7,-3.3),(4.5,4,.6),'void','head')
    for side in (-1,1):
        c(f'eye_{side}',(side*1.2,36,-3.8),(.65,1.1,.45),'rune','head')
        c(f'cheek_{side}',(side*2.3,34.7,-3),(1,2.5,1),'ivory','head')
        c(f'hood_wing_{side}',(side*3.6,36,0),(1.8,9,6),'cloth','head',rotation=(0,0,side*-10))
        c(f'hood_border_{side}',(side*2.9,37,-3.7),(.8,8,.6),'wrap','head',rotation=(0,0,side*-10))
        for i in range(3):
            c(f'face_veil_strip_{side}_{i}',(side*(.5+i*.7),33.7,-3.9),(.4,4+i*.6,.35),'web','head')
    c('hood_crown',(0,41,0),(8,2,6.5),'cloth','head')
    c('hood_peak',(0,42.5,1),(4,2,4),'cloth','head',rotation=(10,0,0))
    for side in (-1,1):
        g='left_arm' if side==-1 else 'right_arm'
        shoulder=[side*5,29,0];elbow=[side*9,24,-1];wrist=[side*10,18,-4]
        s(g+'_upper',shoulder,elbow,1.8,2,'bone',g)
        s(g+'_forearm',elbow,wrist,1.3,1.6,'shadow_skin',g)
        c(g+'_pauldron',shoulder,(4,2.5,5),'cloth',g,rotation=(0,0,side*-18))
        c(g+'_wrist',wrist,(2.6,1.8,2.6),'wrap',g)
        for i in range(4):
            a=[wrist[0]+(i-1.5)*.65,wrist[1]-.7,wrist[2]]
            b=[a[0]+side*.4,a[1]-2.7,a[2]-1]
            s(g+f'_finger_{i}',a,b,.45,.55,'bone',g)
            s(g+f'_talon_{i}',b,[b[0],b[1]-.7,b[2]-.9],.3,.4,'ivory',g)
    for i in range(5):
        c(f'back_seal_{i}',(0,22+i*2,4),(1.8,1.3,1),'metal')
    return p


def lantern_ghoul(cube,segment):
    p,c,s=bind(cube,segment)
    c('hunched_ribcage',(0,19,2),(12,13,9),'skin',rotation=(14,0,0))
    c('shoulder_hump',(0,25,4),(13,7,9),'shadow_skin',rotation=(18,0,0))
    c('belly',(0,12,0),(8,8,7),'shadow_skin')
    for side in (-1,1):
        for i in range(4):
            c(f'rib_{side}_{i}',(side*3.2,22-i*1.7,-2.9),(4.8,.9,1.4),'bone',rotation=(0,0,side*13))
        g='left_leg' if side==-1 else 'right_leg'
        hip=[side*3.2,12,1];knee=[side*5.2,7,-1];ankle=[side*4,2,1]
        s(g+'_thigh',hip,knee,4,4,'skin',g)
        s(g+'_shin',knee,ankle,2.7,3,'skin',g)
        c(g+'_knee',knee,(4.5,2,4),'bone',g)
        c(g+'_foot',(side*4,1.3,-1),(4,2,6),'shadow_skin',g)
        for i in range(3):
            c(g+f'_nail_{i}',(side*4+(i-1)*1.1,.8,-4),(1,1.1,1.8),'ivory',g)
        c(g+'_wrap',(side*4.4,4.4,.5),(3.4,1.4,3.8),'wrap',g)
    for i in range(7):
        c(f'spinal_knob_{i}',(0,15+i*1.9,7.1),(2,1.3,1.7),'bone')
    for i in range(5):
        c(f'loincloth_panel_{i}',((i-2)*1.7,9,-3.8),(2,5+(i%2),.9),'leather',rotation=(0,0,(i-2)*4))
    c('neck',(0,27,-1),(5,4,5),'shadow_skin','head')
    c('cranium',(0,29.5,-3),(7,6.5,7),'skin','head',rotation=(16,0,0))
    c('lower_jaw',(0,26.5,-5.2),(7.5,3.5,5),'shadow_skin','head')
    c('maw_void',(0,27,-7.8),(5.8,2.3,.6),'void','head')
    c('nose',(0,30,-7),(1.8,2.7,2),'skin','head')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*2.2,30,-6.6),(2,1.6,.8),'void','head')
        c(f'eye_{side}',(side*2.2,30,-7.1),(.7,.6,.35),'eye','head')
        c(f'brow_{side}',(side*2.2,31.2,-6.5),(2.8,1.2,1.2),'skin','head',rotation=(0,0,side*15))
        c(f'ear_{side}',(side*4.2,30,-2.5),(1.6,3.8,2),'skin','head',rotation=(0,0,side*-20))
        for i in range(3):
            c(f'tooth_{side}_{i}',(side*(.8+i*.85),27.1,-8.2),(.6,1.3+(i%2)*.4,.8),'ivory','head')
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*7,24,1];b=[side*11,17,-1];w=[side*12,9,-4]
        s(g+'_upper',a,b,4.5,5,'skin',g)
        s(g+'_forearm',b,w,3,3.5,'shadow_skin',g)
        c(g+'_elbow',b,(4,2.3,4.5),'bone',g)
        c(g+'_wrist',w,(3.6,2,3.8),'wrap',g)
        c(g+'_palm',(w[0],8,-4),(3.6,3,3),'skin',g)
        for i in range(3):
            a=[w[0]+(i-1)*1,7,-4.6];b=[a[0],4.7,-6.4]
            s(g+f'_finger_{i}',a,b,.8,.9,'skin',g)
            s(g+f'_claw_{i}',b,[b[0],4.4,-7.7],.45,.55,'ivory',g)
    # An exposed, separately posed lantern makes the intended counterplay legible.
    s('lantern_hook',[6,26,5],[16,33,-1],1.2,1.4,'iron')
    s('lantern_top_link',[16,33,-1],[16,30,-1],.6,.8,'iron')
    for y in (20,27):
        c(f'lantern_frame_{y}',(10,y,3),(6.5,1.1,6.5),'metal','lantern')
    for x in (7.4,12.6):
        for z in (.4,5.6):
            c(f'lantern_stile_{x}_{z}',(x,23.5,z),(.8,6,.8),'iron','lantern')
    c('lantern_wick',(10,23.5,3),(2,4,2),'rune','lantern')
    c('lantern_shutter',(10,24,5.8),(4,5,.6),'iron','lantern')
    c('lantern_cap',(10,28,3),(4,1,4),'metal','lantern')
    # Keep the counterplay object outside the shoulder/forearm silhouette.
    for part in p:
        if part['group']=='lantern':
            for key in ('from','to','origin'):
                part[key]=[v+offset for v,offset in zip(part[key],(6,2,-4))]
    return p


def corvid_undertaker(cube,segment):
    p,c,s=bind(cube,segment)
    c('breast',(0,20,1),(9,12,7),'fur')
    c('keel',(0,19,-3),(2,8,1.8),'bone')
    for side in (-1,1):
        g='left_leg' if side==-1 else 'right_leg'
        s(g+'_femur',[side*3,16,2],[side*4,10,4],2.4,2.7,'fur',g)
        s(g+'_hock',[side*4,10,4],[side*3.5,3,0],1.4,1.7,'iron',g)
        c(g+'_joint',(side*4,10,4),(2.8,2.6,3),'bone',g)
        for i in range(3):
            a=[side*3.5,2.1,0];b=[side*3.5+(i-1)*2,.9,-4.5]
            s(g+f'_toe_{i}',a,b,.7,.9,'bone',g)
            s(g+f'_talon_{i}',b,[b[0],.5,-5.8],.4,.5,'iron',g)
        s(g+'_rear_toe',[side*3.5,2,0],[side*4,1,3],.65,.8,'bone',g)
        for i in range(3):
            c(g+f'_scale_{i}',(side*3.7,4+i*1.3,.5),(1.8,.6,1.7),'iron',g)
    for i in range(7):
        c(f'tail_feather_{i}',((i-3)*1.3,12,5.8),(1.5,9+(i%3),1),'fur',rotation=(25,0,(i-3)*7))
    for side in (-1,1):
        g='left_arm' if side==-1 else 'right_arm'
        s(g+'_humerus',[side*5,24,1],[side*10,19,2],2.5,3,'bone',g)
        s(g+'_wing_bone',[side*10,19,2],[side*13,13,1],1.6,2,'bone',g)
        for i in range(6):
            c(g+f'_primary_{i}',(side*(8+i*1.15),16-i*.6,3),(2,14-i*.7,1.2),'fur',g,rotation=(8,0,side*(18+i*3)))
        for i in range(4):
            c(g+f'_covert_{i}',(side*(5.5+i*1.2),23-i*1.4,3),(2.1,5,1.4),'fur',g,rotation=(0,0,side*25))
        c(g+'_wrist_wrap',(side*13,13,1),(2.7,1.4,3),'wrap',g)
    c('neck',(0,27,0),(4,6,4),'fur','head')
    c('avian_cranium',(0,31,-1),(5.7,5.7,6),'fur','head')
    c('beak_root',(0,30,-5.1),(3.5,2.3,4),'bone','head')
    c('beak_tip',(0,29.6,-7.9),(2,2,2.4),'ivory','head',rotation=(19,0,0))
    c('beak_hook',(0,28.5,-8.8),(1.4,2,1),'iron','head',rotation=(18,0,0))
    c('lower_beak',(0,28.9,-5.5),(2.5,.9,4),'bone','jaw')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*2.7,31,-2.4),(.7,1.8,2),'void','head')
        c(f'eye_{side}',(side*3.1,31,-2.6),(.4,.8,.9),'eye','head')
        for i in range(3):
            c(f'neck_ruff_{side}_{i}',(side*(2+i*.8),27-i*.9,2),(1.5,4,2),'fur','head',rotation=(0,0,side*26))
        c(f'cheek_ossicle_{side}',(side*2.8,29.3,-.7),(.8,2.3,2),'bone','head')
    for i in range(3):
        c(f'crown_feather_{i}',((i-1)*1.4,34,1),(1,4-i*.4,1.3),'fur','head',rotation=(12,0,(i-1)*10))
    # Grave markers are worn call-tokens; actual corpse markers remain unimplemented.
    for i in range(4):
        c(f'grave_token_{i}',((i-1.5)*1.8,17,-3.4),(1.4,2.5,.8),'bone')
    s('token_cord',[-4,19,-3.6],[4,19,-3.6],.5,.6,'wrap')
    return p


def rotmilk_rat(cube,segment):
    p,c,s=bind(cube,segment)
    c('barrel_body',(0,5,1),(6,5.5,10),'fur')
    c('rump',(0,5,5),(5.5,5,4),'fur')
    c('belly',(0,3,1),(4.5,2,8),'skin')
    for side in (-1,1):
        for i in range(6):
            c(f'flank_fur_{side}_{i}',(side*2.7,5.5+(i%2)*.7,-2+i*1.35),(1.1,2.2,2),'fur',rotation=(0,0,side*14))
        for front in (True,False):
            g=('left' if side==-1 else 'right')+('_front_leg' if front else '_rear_leg')
            z=-2.5 if front else 4
            s(g+'_upper',[side*2.1,4.4,z],[side*3,2.5,z+.4],1.2,1.4,'skin',g)
            s(g+'_ankle',[side*3,2.5,z+.4],[side*3.2,.9,z-.6],.7,.9,'skin',g)
            for i in range(3):
                s(g+f'_toe_{i}',[side*3.2,.7,z-.6],[side*3.2+(i-1)*.45,.45,z-1.7],.25,.35,'skin',g)
                c(g+f'_nail_{i}',(side*3.2+(i-1)*.45,.45,z-1.85),(.25,.3,.5),'ivory',g)
    c('rat_skull',(0,5.4,-5),(4.3,4,4.5),'fur','head')
    c('muzzle',(0,4.7,-7.2),(3.4,2.4,2.7),'skin','head')
    c('nose',(0,5,-8.6),(1.5,1.1,.8),'shadow_skin','head')
    c('jaw',(0,3.6,-6.8),(2.8,1.2,2.6),'skin','head')
    for side in (-1,1):
        c(f'incisor_{side}',(side*.5,3.9,-8.1),(.6,1.3,.6),'ivory','head')
        c(f'eye_socket_{side}',(side*2,5.9,-5.8),(.7,1.3,1.5),'void','head')
        c(f'eye_{side}',(side*2.4,6,-6),(.35,.8,.8),'eye','head')
        c(f'ear_outer_{side}',(side*2.3,7.8,-3.7),(2.6,3.2,1),'fur','head',rotation=(0,0,side*-18))
        c(f'ear_inner_{side}',(side*2.3,7.9,-4.3),(1.7,2.3,.45),'skin','head',rotation=(0,0,side*-18))
        c(f'ear_rim_{side}',(side*2.3,9,-3.9),(1.6,.5,1),'wrap','head')
        for i in range(4):
            a=[side*1.2,4.6,-7.6];b=[side*(4+i*.35),4.4+(i-1.5)*.5,-8.4+i*.6]
            s(f'whisker_{side}_{i}',a,b,.14,.18,'web','head')
    points=[(0,4.5,6.5),(1,4,8.5),(2.5,3,10),(4,2.1,11),(5.8,1.4,11.2),(7.5,.9,10.8),(8.8,.7,9.6),(9.4,.6,8.2)]
    for i,(a,b) in enumerate(zip(points,points[1:])):
        s(f'tail_segment_{i}',a,b,.85-i*.08,1-i*.08,'skin','tail')
        c(f'tail_scale_{i}',b,(.6-i*.045,.5,.55),'wrap','tail')
    for i in range(4):
        c(f'back_fur_tuft_{i}',(0,7.7,-1+i*1.8),(1.8,1.1,2),'fur',rotation=(14,0,0))
    # One member is under half a block high; the runtime swarm is not a giant actor.
    for part in p:
        for key in ('from','to','origin'):
            part[key]=[round(v*.75,6) for v in part[key]]
    return p


def grave_thorn(cube,segment):
    p,c,s=bind(cube,segment)
    c('grave_anchor',(0,3,0),(12,6,9),'shadow_stone')
    c('tomb_slab',(0,14,1),(9,18,4),'stone')
    c('slab_crown',(0,24,1),(7,3,4),'stone','head')
    c('inscribed_recess',(0,16,-1.4),(5.5,10,.6),'void')
    for side in (-1,1):
        c(f'carved_border_{side}',(side*4.3,15,-1.2),(1.4,16,1.3),'bone')
        for i in range(3):
            c(f'burial_glyph_{side}_{i}',(side*1.4,12+i*3,-2),(.7,1.6,.5),'rune')
    for i in range(4):
        c(f'strata_course_{i}',(0,6+i*5,2.2),(10,1.1,3),'shadow_stone')
    # Four anchored lash fans. Warnings and snare motion are authored separately.
    for i in range(4):
        angle=math.pi/4+i*math.pi/2
        dx,dz=math.cos(angle),math.sin(angle)
        g=f'root_lash_{i}'
        a=[dx*3,5,dz*3];b=[dx*9,3,dz*9];tip=[dx*15,.7,dz*15]
        s(g+'_root',a,b,3.2,3.4,'bark',g)
        s(g+'_runner',b,tip,1.9,2,'bark',g)
        for j in range(4):
            base=[dx*(6+j*2.3),3-j*.45,dz*(6+j*2.3)]
            top=[base[0]+dz*1.5,base[1]+3.8-j*.4,base[2]-dx*1.5]
            s(g+f'_barb_{j}',base,top,1-j*.12,1.1-j*.12,'ivory',g)
            c(g+f'_knot_{j}',base,(2.2-j*.2,1.5,2.2-j*.2),'bark',g)
        for side in (-1,1):
            s(g+f'_fine_root_{side}',b,[dx*11+dz*side*5,.5,dz*11-dx*side*5],.8,1,'bark',g)
    for side in (-1,1):
        for i in range(5):
            a=[side*4,7+i*3,2]
            b=[side*(7+i*.6),12+i*3.4,2.5]
            s(f'crown_thorn_{side}_{i}',a,b,1.7-i*.1,2-i*.1,'bark','head')
            s(f'crown_tip_{side}_{i}',b,[b[0]+side*1.4,b[1]+2.5,b[2]],.7,.9,'ivory','head')
    for i in range(5):
        c(f'seed_eye_{i}',((i-2)*1.1,23.7,-1.5),(.7,1.2,.6),'rune','head')
        c(f'crown_moss_{i}',((i-2)*1.5,25.8,1),(1.6,1.3,2),'moss','head')
    for i in range(6):
        c(f'root_buttress_{i}',((i-2.5)*1.5,4,3.8),(1.3,6,2),'bark',rotation=(0,0,(i-2.5)*5))
    return p


def mourning_matron(cube,segment):
    p,c,s=bind(cube,segment)
    c('underskirt',(0,14,2),(14,25,10),'cloth')
    for i in range(8):
        x=(i-3.5)*1.8
        low=1.7+(i%3)*.6
        for side in (-1,1):
            c(f'mourning_panel_{side}_{i}',(x,(low+27)/2,2+side*5.1),(2.1,27-low,1.1),'cloth',rotation=(side*3,0,(i-3.5)*1.4))
        c(f'silver_hem_{i}',(x,low+.8,-3.9),(1.7,1,.55),'trim')
    c('chest',(0,28,1),(9,9,7),'shadow_skin')
    c('healers_stole',(0,28,-3.2),(5,10,1),'wrap')
    for i in range(5):
        c(f'suture_{i}',((i%2)*.7-.35,25+i*1.5,-3.9),(2.6,.45,.5),'scar')
    for side in (-1,1):
        for i in range(4):
            c(f'shawl_fold_{side}_{i}',(side*(5+i*1.25),30-i,2),(2.1,8-i,7),'cloth',rotation=(0,0,side*25))
        for i in range(3):
            c(f'collar_bone_{side}_{i}',(side*(2.1+i*1.2),32-i*.6,-2.8),(2.5,.8,1.1),'bone',rotation=(0,0,side*16))
    c('neck',(0,34,0),(3.5,4,4),'bone','head')
    c('skull_cranium',(0,38,-.6),(6.4,6.4,5.6),'bone','head')
    c('jaw',(0,35,-1.8),(5,2,3.8),'shadow_skin','head')
    for side in (-1,1):
        c(f'eye_socket_{side}',(side*1.6,38,-3.7),(2,1.5,.6),'void','head')
        c(f'eye_{side}',(side*1.6,38,-4.1),(.7,.7,.35),'cloud_eye','head')
        c(f'cheek_{side}',(side*2.6,36.6,-3),(1.2,2,1.3),'bone','head')
        c(f'veil_side_{side}',(side*4,36.8,1),(1.5,12,7),'cloth','head',rotation=(0,0,side*-10))
        for i in range(3):
            c(f'veil_edge_{side}_{i}',(side*(2.2+i*.8),34-i*.9,-3.7),(.45,5+i,.4),'web','head')
    c('veil_crown',(0,42,1),(9,2,7.5),'cloth','head')
    for i in range(5):
        c(f'circlet_bead_{i}',((i-2)*1.4,41.2,-3.2),(.9,1.1,.7),'metal','head')
    for side in (-1,1):
        g='left_arm' if side==-1 else 'right_arm'
        a=[side*6,30,0];b=[side*11,25,-1];hand=[side*9,24,-7]
        s(g+'_upper',a,b,2.8,3.2,'cloth',g)
        s(g+'_forearm',b,hand,1.7,2,'bone',g)
        c(g+'_cuff',b,(3.7,1.5,4),'wrap',g)
        c(g+'_palm',hand,(2.8,1.4,2.8),'bone',g)
        for i in range(3):
            a=[hand[0]+(i-1)*.8,hand[1],hand[2]-1]
            b=[a[0],hand[1]+1.8,hand[2]-2.2]
            s(g+f'_finger_{i}',a,b,.5,.65,'ivory',g)
        # Short wound-silk tassels suggest transfer without a fake linked target.
        for i in range(3):
            s(g+f'_wound_silk_{i}',[hand[0]+(i-1)*.8,24,-8],[hand[0]+(i-1)*1.1,19-i*.5,-8.3],.22,.3,'scar',g)
    # An empty rib cradle hangs in front of the stole, separate from the skull.
    c('cradle_base',(0,20,-6),(7,1.3,4),'bark')
    for side in (-1,1):
        for i in range(3):
            s(f'cradle_rib_{side}_{i}',[side*3,20,-7+i*1.2],[side*4,23.8,-7+i*1.2],.65,.8,'bone')
    return p


def sculpts(cube,segment):
    return [(name,fn(cube,segment)) for name,fn in (
        ('hollow_veil',hollow_veil),('lantern_ghoul',lantern_ghoul),
        ('corvid_undertaker',corvid_undertaker),('rotmilk_ratpack',rotmilk_rat),
        ('grave_thorn',grave_thorn),('mourning_matron',mourning_matron))]
