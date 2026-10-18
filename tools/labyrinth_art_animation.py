"""Editable art-motion prototypes in Blockbench's inspected save representation.

These clips do not create game AI, hit events, audio, projectiles or native models.
"""
from __future__ import annotations

import copy
import math

import numpy as np

SIGNATURES = {
    'ashen_novice': ('bell_stagger', 1.4, ['bell response', 'formation rupture', 'recovery']),
    'lurking_silkmaw': ('ceiling_ambush', 1.6, ['suspended warning', 'descent', 'landing']),
    'bell_warden': ('rally_toll', 1.8, ['raise arms', 'visible clapper swing', 'rally recovery']),
    'ossuary_bowyer': ('marked_shot', 1.6, ['glowing drawn string', 'release reference arrow', 'reload']),
    'reliquary_sentinel': ('bulwark_slam', 2.0, ['frontal shield lock', 'mace slam', 'exposed recovery']),
    'the_ossuary_prior': ('bell_convergence', 3.0, ['choir preparation', 'converging toll', 'altar-response window']),
    'hollow_veil': ('phase_slip', 1.8, ['veil gathers', 'brief contraction', 'rearward reappearance gesture']),
    'lantern_ghoul': ('gloom_charge', 2.0, ['exposed lantern swings', 'charge preparation', 'lantern recovery']),
    'corvid_undertaker': ('carrion_call', 2.2, ['beak opens', 'wing call', 'corpse-marker response window']),
    'rotmilk_ratpack': ('grate_rush', 1.3, ['low crouch', 'short individual rush', 'pack regroup reference']),
    'grave_thorn': ('thorn_snare', 2.0, ['soil pulse gesture', 'root fan spreads', 'barbs recover']),
    'mourning_matron': ('grief_transfer', 2.4, ['cradle and palms presented', 'wound-silk gesture', 'recovery']),
    'censer_revenant': ('smoke_vent', 2.2, ['censer lid opens', 'venting gesture', 'lid closes']),
    'rift_acolyte': ('rift_needles', 1.8, ['channel alignment gesture', 'gauntlet salvo gesture', 'recovery']),
    'skullglass_shardling': ('fracture_scatter', 1.6, ['core braces', 'outer facets separate', 'art cycle reset']),
    'coal_moth': ('ember_dust', 1.7, ['wings spread', 'dust-shedding flutter gesture', 'flight recovery reference']),
    'chapel_butcher': ('cleaver_cleave', 2.0, ['cleaver windup', 'broad sweep', 'exposed recovery side']),
    'dust_friar': ('dust_benediction', 2.2, ['hand-held censer rises', 'benediction gesture', 'lower censer']),
}


def pivots(species, parts):
    result = {g: list(next(p['origin'] for p in parts if p['group'] == g)) for g in sorted({p['group'] for p in parts})}
    result['body'] = [0, 0, 0]
    axes = {
        'ashen_novice': (6, 22, 3.1, 10, 22.2),
        'bell_warden': (8, 29, 3.1, 10, 35.2),
        'ossuary_bowyer': (5, 26, 3, 15, 28),
        'reliquary_sentinel': (10, 30, 4.5, 15, 34),
        'the_ossuary_prior': (9, 40, 0, 0, 44),
        'hollow_veil': (5,29,0,0,32),
        'lantern_ghoul': (7,24,3.2,12,27),
        'corvid_undertaker': (5,24,3,16,27),
        'mourning_matron': (6,30,0,0,34),
        'censer_revenant': (6,29,0,0,32),
        'rift_acolyte': (5,27,2.6,17,30),
        'chapel_butcher': (10,33,5,17,37),
        'dust_friar': (8,25,3.4,9,29),
    }
    if species in axes:
        shoulder, shoulder_y, hip, hip_y, neck_y = axes[species]
        for side in (-1, 1):
            prefix = 'left' if side == -1 else 'right'
            result[prefix+'_arm'] = [side*shoulder, shoulder_y, 0]
            if prefix+'_leg' in result:
                result[prefix+'_leg'] = [side*hip, hip_y, 1]
        result['head'] = [0, neck_y, 0]
    elif species=='lurking_silkmaw':
        result['head'] = [0, 12, -7]
        for side in (-1,1):
            for i in range(4):
                result[('left' if side==-1 else 'right')+f'_leg_{i}'] = [side*4,12,-7+i*5]
    elif species=='rotmilk_ratpack':
        result['head']=[0,3.6,-2.625]
        result['tail']=[0,3.375,4.875]
        for side in (-1,1):
            for front in (True,False):
                name=('left' if side==-1 else 'right')+('_front_leg' if front else '_rear_leg')
                result[name]=[side*2.1*.75,4.4*.75,(-2.5 if front else 4)*.75]
    elif species=='grave_thorn':
        result['head']=[0,8,2]
        for i in range(4):
            angle=math.pi/4+i*math.pi/2
            result[f'root_lash_{i}']=[math.cos(angle)*3,5,math.sin(angle)*3]
    elif species=='skullglass_shardling':
        result['head']=[0,10,-3.5]
        for side in (-1,1):
            for i in range(3):
                result[('left' if side==-1 else 'right')+f'_leg_{i}']=[side*3.5,7,-3+i*3]
        for i in range(6):
            angle=math.tau*i/6
            result[f'shard_{i}']=[math.cos(angle)*3.4,11,math.sin(angle)*3.4]
    elif species=='coal_moth':
        result['head']=[0,12,-3]
        for side in (-1,1):
            name='left' if side==-1 else 'right'
            result[name+'_wing']=[side*2,12,-1]
            result[name+'_hindwing']=[side*2,12,3]
            for i in range(3):
                result[name+f'_leg_{i}']=[side*2,11,-1+i*2]
    else:
        raise ValueError('Missing anatomical pivots for '+species)
    if 'clapper' in result:
        result['clapper']=[0,40,4]
    if 'bowstring' in result:
        result['bowstring']=[-11,24,-8]
    if 'arrow' in result:
        result['arrow']=[-11,24,-8]
    if 'lantern' in result:
        result['lantern']=[16,30,-1]
    if 'jaw' in result:
        result['jaw']=[0,29.3,-3.7]
    if 'cleaver' in result:
        result['cleaver']=[14,19,-4]
    if 'censer' in result:
        result['censer']=[10,15,-5] if species=='dust_friar' else [0,19,-5]
    if 'censer_lid' in result:
        result['censer_lid']=[0,19.5,-1.5]
    result['root']=[0,0,0]
    return result


def clips(species, parts, uid):
    groups = pivots(species,parts)
    def clip(name,length,loop,tracks,stages=()):
        animators={}
        for group,channel,values in tracks:
            assert group in groups, (species,group)
            animator=animators.setdefault(uid(species+'/'+group),{'name':group,'type':'bone','keyframes':[]})
            for i,(time,value) in enumerate(values):
                animator['keyframes'].append({'uuid':uid(f'{species}/{name}/{group}/{channel}/{i}'),
                    'channel':channel,'time':time,'interpolation':'linear',
                    'data_points':[dict(zip(('x','y','z'),map(str,value)))]})
        return {'uuid':uid(species+'/clip/'+name),'name':name,'loop':loop,'length':length,
                'snapping':20,'override':False,'animators':animators,
                'markers':[{'time':round(length*t,3),'color':i%8} for i,t in enumerate((.2,.55,.8))] if stages else []}
    idle_bob=0 if species=='grave_thorn' else .1 if species=='rotmilk_ratpack' else .35
    walk_bob=0 if species=='grave_thorn' else .18 if species=='rotmilk_ratpack' else .6
    idle_tracks=[
        ('root','position',[(0,[0,0,0]),(1,[0,idle_bob,0]),(2,[0,0,0])]),
        ('head','rotation',[(0,[0,-2,0]),(1,[0,2,0]),(2,[0,-2,0])])]
    if species=='coal_moth':
        for side in (-1,1):
            for hind in (False,True):
                name=('left' if side==-1 else 'right')+('_hindwing' if hind else '_wing')
                a=side*(10 if hind else 15)
                idle_tracks.append((name,'rotation',[(0,[0,0,a]),(1,[0,0,-a]),(2,[0,0,a])]))
    idle=clip('idle',2,'loop',idle_tracks)
    walk_tracks=[('root','position',[(0,[0,0,0]),(.25,[0,walk_bob,0]),(.5,[0,0,0]),(.75,[0,walk_bob,0]),(1,[0,0,0])])]
    for group in groups:
        if 'leg' in group:
            if species=='lurking_silkmaw':
                side=-1 if group.startswith('left') else 1
                phase=side*(-1 if int(group[-1])%2 else 1)
                channel='rotation'; axis=1; angle=9*phase
            else:
                channel='rotation'; axis=0; angle=14 if group.startswith('left') else -14
                if species=='rotmilk_ratpack' and '_rear_' in group:angle=-angle
            a=[0,0,0]; a[axis]=angle
            b=[0,0,0]; b[axis]=-angle
            walk_tracks.append((group,channel,[(0,a),(.5,b),(1,a)]))
    if species!='lurking_silkmaw':
        for group,sign in [('left_arm',1),('right_arm',-1)]:
            if group in groups:
                walk_tracks.append((group,'rotation',[(0,[5*sign,0,0]),(.5,[-5*sign,0,0]),(1,[5*sign,0,0])]))
    if species=='rotmilk_ratpack':
        walk_tracks.append(('tail','rotation',[(0,[0,-8,0]),(.5,[0,8,0]),(1,[0,-8,0])]))
    if species=='grave_thorn':
        walk_tracks.append(('head','rotation',[(0,[0,0,-1]),(.5,[0,0,1]),(1,[0,0,-1])]))
    if species=='coal_moth':
        for side in (-1,1):
            for hind in (False,True):
                name=('left' if side==-1 else 'right')+('_hindwing' if hind else '_wing')
                a=side*(20 if hind else 28)
                walk_tracks.append((name,'rotation',[(0,[0,0,a]),(.25,[0,0,-a]),(.5,[0,0,a]),(.75,[0,0,-a]),(1,[0,0,a])]))
    walk=clip('walk',1,'loop',walk_tracks)
    signature,length,stages=SIGNATURES[species]
    tracks=[]
    def arc(group,channel,value,peak=.4,release=None):
        default=[1,1,1] if channel=='scale' else [0,0,0]
        track=[(0,default),(round(length*peak,3),value)]
        if release is not None:track.append((round(length*.65,3),release))
        track.append((length,default))
        tracks.append((group,channel,track))
    if species=='ashen_novice':
        arc('head','rotation',[16,0,3])
        arc('body','rotation',[0,0,4])
        arc('left_arm','rotation',[-9,0,25])
        arc('right_arm','rotation',[-9,0,-25])
    elif species=='lurking_silkmaw':
        tracks.append(('root','position',[(0,[0,16,0]),(.55,[0,15,0]),(1.05,[0,0,0]),(1.3,[0,.7,0]),(length,[0,0,0])]))
        for group in groups:
            if 'leg_' in group:
                arc(group,'rotation',[0,12 if group.startswith('left') else -12,0],peak=.3)
        arc('head','rotation',[-12,0,0])
    elif species=='bell_warden':
        arc('left_arm','rotation',[-16,0,24])
        arc('right_arm','rotation',[-16,0,-24])
        tracks.append(('clapper','rotation',[(0,[0,0,0]),(.5,[0,0,19]),(.8,[0,0,-19]),(1.1,[0,0,12]),(length,[0,0,0])]))
    elif species=='ossuary_bowyer':
        arc('head','rotation',[0,-8,0])
        arc('right_arm','rotation',[0,-3,0],peak=.4,release=[0,3,0])
        tracks.append(('bowstring','scale',[(0,[1,1,1]),(.6,[1,1,1]),(.72,[.12,1,1]),(1.25,[.12,1,1]),(length,[1,1,1])]))
        tracks.append(('arrow','position',[(0,[0,0,0]),(.6,[0,0,0]),(.85,[-18,0,0]),(1.45,[-18,0,0]),(length,[0,0,0])]))
        tracks.append(('arrow','scale',[(0,[1,1,1]),(.75,[1,1,1]),(.86,[.01,.01,.01]),(1.45,[.01,.01,.01]),(length,[1,1,1])]))
    elif species=='reliquary_sentinel':
        arc('left_arm','rotation',[0,18,0],peak=.3,release=[0,-12,0])
        arc('right_arm','rotation',[-38,0,-8],peak=.4,release=[16,0,4])
        arc('head','rotation',[-4,-10,0],peak=.3)
    elif species=='the_ossuary_prior':
        arc('root','position',[0,1.8,0],peak=.4,release=[0,1,0])
        arc('left_arm','rotation',[-8,0,-14],peak=.4,release=[4,0,6])
        arc('right_arm','rotation',[-20,0,-24],peak=.4,release=[0,0,-9])
        arc('head','rotation',[-9,0,0],peak=.3,release=[7,0,0])
    elif species=='hollow_veil':
        arc('root','scale',[.62,.92,.62],peak=.43,release=[1.04,1,1.04])
        arc('root','position',[0,2,0],peak=.4,release=[0,1,2])
        arc('left_arm','rotation',[-8,15,32],peak=.3)
        arc('right_arm','rotation',[-8,-15,-32],peak=.3)
        arc('head','rotation',[0,-24,0],peak=.6)
    elif species=='lantern_ghoul':
        arc('lantern','rotation',[0,0,27],peak=.3,release=[0,0,-18])
        arc('head','rotation',[16,0,0],peak=.35,release=[-8,0,0])
        arc('left_arm','rotation',[-24,0,8],peak=.35,release=[13,0,0])
        arc('right_arm','rotation',[-24,0,-8],peak=.35,release=[13,0,0])
        arc('root','position',[0,0,-1],peak=.35,release=[0,.8,-6])
    elif species=='corvid_undertaker':
        arc('jaw','rotation',[24,0,0],peak=.35)
        arc('head','rotation',[-14,0,0],peak=.35)
        arc('left_arm','rotation',[-8,0,-48],peak=.45)
        arc('right_arm','rotation',[-8,0,48],peak=.45)
    elif species=='rotmilk_ratpack':
        arc('head','rotation',[11,0,0],peak=.2,release=[-5,0,0])
        arc('root','position',[0,.15,-4],peak=.6)
        arc('tail','rotation',[0,25,0],peak=.35,release=[0,-15,0])
        for group in groups:
            if 'leg' in group:arc(group,'rotation',[18 if group.startswith('left') else -18,0,0],peak=.45)
    elif species=='grave_thorn':
        for i in range(4):
            arc(f'root_lash_{i}','scale',[1.18,1,1.18],peak=.55)
            arc(f'root_lash_{i}','rotation',[0,12 if i%2 else -12,0],peak=.55)
        arc('head','rotation',[-4,0,0],peak=.25,release=[3,0,0])
    elif species=='mourning_matron':
        arc('left_arm','rotation',[-14,0,-12],peak=.4)
        arc('right_arm','rotation',[-14,0,12],peak=.4)
        arc('head','rotation',[10,0,0],peak=.5)
        arc('root','position',[0,.7,0],peak=.4)
    elif species=='censer_revenant':
        arc('censer_lid','rotation',[68,0,0],peak=.35)
        arc('left_arm','rotation',[12,0,-14],peak=.4)
        arc('right_arm','rotation',[12,0,14],peak=.4)
        arc('head','rotation',[-10,0,0],peak=.4)
    elif species=='rift_acolyte':
        arc('left_arm','rotation',[28,-12,0],peak=.35,release=[-8,-5,0])
        arc('right_arm','rotation',[28,12,0],peak=.35,release=[-8,5,0])
        arc('head','rotation',[12,0,0],peak=.25)
    elif species=='skullglass_shardling':
        for i in range(6):
            angle=math.tau*i/6
            arc(f'shard_{i}','position',[math.cos(angle)*7,2,math.sin(angle)*7],peak=.65)
            arc(f'shard_{i}','rotation',[0,0,(i-2.5)*12],peak=.65)
        arc('head','rotation',[8,0,0],peak=.25)
    elif species=='coal_moth':
        for side in (-1,1):
            for hind in (False,True):
                name=('left' if side==-1 else 'right')+('_hindwing' if hind else '_wing')
                a=side*(25 if hind else 38)
                tracks.append((name,'rotation',[(0,[0,0,0]),(.4,[0,0,a]),(.7,[0,0,-a]),(1,[0,0,a]),(1.3,[0,0,-a]),(length,[0,0,0])]))
        arc('root','position',[0,2,0],peak=.45)
    elif species=='chapel_butcher':
        arc('right_arm','rotation',[35,-55,-18],peak=.43,release=[10,60,12])
        arc('left_arm','rotation',[8,0,-12],peak=.4)
        arc('head','rotation',[0,-12,0],peak=.35,release=[0,13,0])
    elif species=='dust_friar':
        arc('right_arm','rotation',[65,0,-12],peak=.4)
        arc('left_arm','rotation',[25,0,10],peak=.4)
        arc('head','rotation',[-12,0,0],peak=.4)
    return [idle,walk,clip(signature,length,'once',tracks,stages)]


def evaluate(model,clip,time,rotation_matrix):
    """Evaluate emitted art clips for offline motion inspection, not Minecraft AI."""
    groups={}
    def visit(nodes,parent=None):
        for node in nodes:
            if isinstance(node,dict):
                groups[node['name']]={'origin':node['origin'],'parent':parent}
                visit(node['children'],node['name'])
    visit(model['outliner'])
    transforms={}
    for animator in clip['animators'].values():
        values={}
        for channel in ('rotation','position','scale'):
            keys=sorted([k for k in animator['keyframes'] if k['channel']==channel],key=lambda k:k['time'])
            if not keys:continue
            def vec(k):return np.array([float(k['data_points'][0][axis]) for axis in ('x','y','z')])
            lo=keys[0]; hi=keys[-1]
            for k in keys:
                if k['time']<=time:lo=k
                if k['time']>=time:hi=k;break
            fraction=0 if hi['time']==lo['time'] else max(0,min(1,(time-lo['time'])/(hi['time']-lo['time'])))
            values[channel]=vec(lo)+(vec(hi)-vec(lo))*fraction
        transforms[animator['name']]=values
    return groups,transforms


def pose(quads,model,clip,time,rotation_matrix):
    groups,transforms=evaluate(model,clip,time,rotation_matrix)
    output=copy.deepcopy(quads)
    for q in output:
        vertices=np.array(q['vertices']); normal=np.array(q['normal'])
        group=q['group']
        while group is not None:
            tr=transforms.get(group,{})
            pivot=np.array(groups[group]['origin'])
            scale=np.array(tr.get('scale',[1,1,1]))
            rotation=rotation_matrix(tr.get('rotation',[0,0,0]))
            vertices=((vertices-pivot)*scale)@rotation.T+pivot+tr.get('position',[0,0,0])
            normal=rotation@(normal/scale)
            normal/=np.linalg.norm(normal)
            group=groups[group]['parent']
        q['vertices']=vertices.tolist(); q['normal']=normal.tolist()
    return output
