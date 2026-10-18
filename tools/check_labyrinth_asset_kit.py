"""Artifact evidence for the staged kit; deliberately does not claim a game test."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

import nbt
from gen_labyrinth_asset_kit import OUT, generate_piece, validate
from gen_labyrinth_creature_art import rotation_matrix
from labyrinth_art_animation import pose


def main():
    structures = json.loads((OUT / 'structure_manifest.json').read_text())
    art = json.loads((OUT / 'creature_art_manifest.json').read_text())
    assert len(structures['pieces']) == 75
    assert len({r['family'] for r in structures['pieces']}) == 25
    assert structures['deployment'] == 'staged only'
    template_rows = []
    for row in structures['pieces']:
        path = OUT / row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], path
        root = nbt.load(path)[1]
        source, sockets, _ = generate_piece(row['family'], row['condition'])
        assert root == source.to_nbt(), (path, 'source-to-NBT drift')
        assert root['size'] == row['size'] and len(root['blocks']) == row['block_count']
        assert not source.dropped
        positions = [tuple(b['pos']) for b in root['blocks']]
        assert len(set(positions)) == len(positions)
        assert len(positions) == np.prod(root['size']), (path, 'missing owned cells')
        assert all(0 <= b['state'] < len(root['palette']) for b in root['blocks'])
        template_rows.append({'path': row['path'], **validate(root, sockets, row['family'])})
    for path, expected in art['sha256'].items():
        assert hashlib.sha256((OUT/path).read_bytes()).hexdigest() == expected, path
    model_rows = []
    for row in art['models']:
        g = json.loads((OUT / row['geometry']).read_text())
        quads, parts = g['quads'], g['parts']
        assert 86 <= len(parts) <= 130 and len(quads) == len(parts) * 6
        assert len({p['name'] for p in parts}) == len(parts)
        assert len({p['uuid'] for p in parts}) == len(parts)
        assert len({p['material'] for p in parts}) >= 5
        occupied = np.zeros((512, 512), dtype=bool)
        for q in quads:
            vertices, normal, uv = np.array(q['vertices']), np.array(q['normal']), np.array(q['uv'])
            assert np.isfinite(vertices).all() and np.isfinite(uv).all()
            assert np.all(uv >= 0) and np.all(uv <= 1)
            assert abs(np.linalg.norm(normal) - 1) < 1e-4
            assert np.linalg.norm(np.cross(vertices[1]-vertices[0], vertices[2]-vertices[0])) > .001
            low, high = np.rint(uv.min(axis=0)*512).astype(int), np.rint(uv.max(axis=0)*512).astype(int)
            x0,y0=low; x1,y1=high
            assert x1>x0 and y1>y0 and not occupied[y0:y1,x0:x1].any(), (row['catalog_id'], 'overlapping face islands')
            occupied[y0:y1,x0:x1]=True
        for look in row['looks']:
            im = np.array(Image.open((OUT / row['geometry']).parent / (row['catalog_id']+'_'+look+'.png')))
            assert im.shape == (512,512,4)
            assert np.all(im[:,:,3][occupied] == 255), (row['catalog_id'],'invisible face')
        obj = (OUT / row['blender_import']).read_text().splitlines()
        vertices = np.array([[float(v) for v in line.split()[1:]] for line in obj if line.startswith('v ')])
        faces = [[int(s.split('/')[0])-1 for s in line.split()[1:]] for line in obj if line.startswith('f ')]
        assert len(vertices) == len(quads)*4 and len(faces) == len(quads)
        for face,q in zip(faces,quads):
            a,b,c,_=vertices[face]
            assert np.dot(np.cross(b-a,c-a),q['normal']) > 0, (row['catalog_id'],'inside-out OBJ face')
        bb = json.loads((OUT / row['blockbench']).read_text())
        refs=[]; groups={}; parents={}
        def walk_group(nodes,parent=None):
            for node in nodes:
                if isinstance(node,str):refs.append(node)
                else:
                    groups[node['uuid']]=node
                    parents[node['name']]=parent
                    walk_group(node['children'],node['name'])
        walk_group(bb['outliner'])
        for child,parent in {'jaw':'head','bowstring':'left_arm','arrow':'left_arm',
                             'clapper':'body','lantern':'body','tail':'body','cleaver':'right_arm',
                             'censer':'right_arm' if row['catalog_id']=='dust_friar' else 'body',
                             'censer_lid':'censer'}.items():
            if child in parents:assert parents[child]==parent,(row['catalog_id'],child,'detached accessory')
        assert set(refs) == {p['uuid'] for p in parts} and len(refs)==len(parts)
        assert row['runtime_entity']=='not implemented' and len(bb['animations'])==3
        if row['catalog_id']=='grave_thorn':
            for clip in bb['animations']:
                for animator in clip['animators'].values():
                    if animator['name']=='root':
                        assert all(all(float(k['data_points'][0][axis])==0 for axis in ('x','y','z'))
                                   for k in animator['keyframes'] if k['channel']=='position'), 'rooted trap lifts off its base'
        assert {a['name'] for a in bb['animations']} >= {'idle','walk'}
        for clip in bb['animations']:
            assert clip['length']>0 and clip['loop'] in ('loop','once')
            for key,animator in clip['animators'].items():
                assert key in groups and groups[key]['name']==animator['name']
                for channel in {k['channel'] for k in animator['keyframes']}:
                    assert channel in ('position','rotation','scale')
                    keys=sorted([k for k in animator['keyframes'] if k['channel']==channel],key=lambda k:k['time'])
                    assert keys[0]['time']==0 and keys[-1]['time']==clip['length']
                    assert len({k['time'] for k in keys})==len(keys)
                    for keyframe in keys:
                        assert 0<=keyframe['time']<=clip['length']
                        v=[float(keyframe['data_points'][0][axis]) for axis in ('x','y','z')]
                        assert np.isfinite(v).all()
                        if channel=='scale': assert all(value>0 for value in v)
                    if clip['loop']=='loop':assert keys[0]['data_points']==keys[-1]['data_points']
            for time in np.linspace(0,clip['length'],9):
                sample=pose(quads,bb,clip,float(time),rotation_matrix)
                assert np.isfinite([q['vertices'] for q in sample]).all()
        model_rows.append({'id':row['catalog_id'],'sculpted_parts':len(parts),'quad_count':len(quads),
                           'unique_face_islands':len(quads),'outward_obj_winding':True,'blockbench_group_coverage':True,
                           'art_clips':len(bb['animations']),'finite_motion_samples':27,'loop_endpoints_match':True})
    assert len(art['models'])==18
    assert len({row['catalog_id'] for row in art['models']})==18
    rat=next(row for row in art['models'] if row['catalog_id']=='rotmilk_ratpack')
    assert rat['model_bounds_blocks'][1]<.5 and 'single small rat' in rat['representation']
    thorn=next(row for row in art['models'] if row['catalog_id']=='grave_thorn')
    assert 'stationary rooted trap' in thorn['representation']
    report={'acceptance':'static validated; runtime pending','templates':template_rows,'creatures':model_rows,
            'checks':['NBT version/bounds/palette indices','deterministic source-to-artifact equality',
                      'socket reachability with two-block headroom','five-wide dry room/passsage routes',
                      'twelve-block switchback route','file hashes','finite nondegenerate model faces',
                      'unique UV face islands','opaque used texels','OBJ outward winding','Blockbench group references',
                      'art clip references/timelines','loop endpoint continuity','finite sampled art motion'],
            'not_executed':['in-game template placement','actual stair collision movement','native model baking',
                            'native game animation','Blockbench editor import','AI state machines','merchant trades','loot integration',
                            'worldgen reservations','fresh-world natural generation','multiplayer/performance']}
    (OUT/'static_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Static validation passed: 75 NBT modules, 18 creature sculptures, 54 skins, 54 art clips. Runtime acceptance pending.')


if __name__=='__main__':
    main()
