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
    }
    if species in axes:
        shoulder, shoulder_y, hip, hip_y, neck_y = axes[species]
        for side in (-1, 1):
            prefix = 'left' if side == -1 else 'right'
            result[prefix+'_arm'] = [side*shoulder, shoulder_y, 0]
            if prefix+'_leg' in result:
                result[prefix+'_leg'] = [side*hip, hip_y, 1]
        result['head'] = [0, neck_y, 0]
    else:
        result['head'] = [0, 12, -7]
        for side in (-1,1):
            for i in range(4):
                result[('left' if side==-1 else 'right')+f'_leg_{i}'] = [side*4,12,-7+i*5]
    if 'clapper' in result:
        result['clapper']=[0,40,4]
    if 'bowstring' in result:
        result['bowstring']=[-11,24,-8]
    if 'arrow' in result:
        result['arrow']=[-11,24,-8]
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
    idle=clip('idle',2,'loop',[
        ('root','position',[(0,[0,0,0]),(1,[0,.35,0]),(2,[0,0,0])]),
        ('head','rotation',[(0,[0,-2,0]),(1,[0,2,0]),(2,[0,-2,0])])])
    walk_tracks=[('root','position',[(0,[0,0,0]),(.25,[0,.6,0]),(.5,[0,0,0]),(.75,[0,.6,0]),(1,[0,0,0])])]
    for group in groups:
        if 'leg' in group:
            if species=='lurking_silkmaw':
                side=-1 if group.startswith('left') else 1
                phase=side*(-1 if int(group[-1])%2 else 1)
                channel='rotation'; axis=1; angle=9*phase
            else:
                channel='rotation'; axis=0; angle=14 if group.startswith('left') else -14
            a=[0,0,0]; a[axis]=angle
            b=[0,0,0]; b[axis]=-angle
            walk_tracks.append((group,channel,[(0,a),(.5,b),(1,a)]))
    if species!='lurking_silkmaw':
        for group,sign in [('left_arm',1),('right_arm',-1)]:
            walk_tracks.append((group,'rotation',[(0,[5*sign,0,0]),(.5,[-5*sign,0,0]),(1,[5*sign,0,0])]))
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
    return [idle,walk,clip(signature,length,'once',tracks,stages)]


def evaluate(model,clip,time,rotation_matrix):
    """Evaluate emitted art clips for offline motion inspection, not Minecraft AI."""
    groups={}
    def visit(nodes):
        for node in nodes:
            if isinstance(node,dict):
                groups[node['name']]=node
                visit(node['children'])
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
        for group in (q['group'],'root'):
            tr=transforms.get(group,{})
            pivot=np.array(groups[group]['origin'])
            scale=np.array(tr.get('scale',[1,1,1]))
            rotation=rotation_matrix(tr.get('rotation',[0,0,0]))
            vertices=((vertices-pivot)*scale)@rotation.T+pivot+tr.get('position',[0,0,0])
            normal=rotation@(normal/scale)
            normal/=np.linalg.norm(normal)
        q['vertices']=vertices.tolist(); q['normal']=normal.tolist()
    return output
