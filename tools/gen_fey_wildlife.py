"""Generate native EntityJS fauna models, animations, habitats and loot. No jar edits.

The material atlas is a retained ImageGen output; regeneration never redraws it.
Run from the instance root. Runtime code lives in the two fey scripts, not here.
"""
import json
from pathlib import Path

DATA = Path('kubejs/data')
ASSETS = Path('kubejs/assets/alfheim')
ROSTER = []


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def cube(origin, size, material):
    # Per-face UVs sample inside the atlas cell, avoiding seams at cell boundaries.
    u, v = (material % 4) * 256 + 16, (material // 4) * 256 + 16
    return dict(origin=origin, size=size, uv={face: dict(uv=[u, v], uv_size=[224, 224])
                for face in ['north', 'south', 'east', 'west', 'up', 'down']})


def bone(name, cubes, pivot=None, parent='root', rotation=None):
    b = dict(name=name, parent=parent, pivot=pivot or [0, 0, 0], cubes=cubes)
    if rotation:
        b['rotation'] = rotation
    return b


def deer(buck):
    b = [bone('body', [cube([-3.5, 11, -7], [7, 8, 15], 0),
                       cube([-3, 10.7, -5], [6, 1, 11], 1)]),
         bone('neck', [cube([-2.5, 17, -8], [5, 8, 5], 0)], [0, 17, -5], rotation=[-18, 0, 0]),
         bone('head', [cube([-2.5, 23, -12], [5, 5, 7], 0),
                       cube([-2, 22.5, -14], [4, 3, 4], 0),
                       cube([-1.6, 23, -14.2], [3.2, 1.6, .5], 2),
                       cube([-2.7, 25.3, -11], [.5, 1, 1], 2),
                       cube([2.2, 25.3, -11], [.5, 1, 1], 2),
                       cube([-5, 26, -7], [3, 1, 4], 0),
                       cube([2, 26, -7], [3, 1, 4], 0)], [0, 24, -6]),
         bone('tail', [cube([-1, 16, 7], [2, 4, 2], 0),
                       cube([-1, 16, 8.5], [2, 4, .6], 1)], [0, 16, 7])]
    for i, (x, z) in enumerate([(-3,-5),(1,-5),(-3,5),(1,5)]):
        b.append(bone('leg'+str(i), [cube([x, 1, z], [2, 11, 2], 0),
                                    cube([x, 0, z-.2], [2, 1.5, 2.4], 2)], [x+1, 12, z+1]))
    if buck:
        for side in [-1,1]:
            c = [cube([side*3-.6, 27, -7], [1.2, 8, 1.2], 3),
                 cube([min(side*3, side*7)-.5, 32, -7], [5, 1, 1], 3)]
            for x, h in [(4,3),(6,4),(8,3)]:
                c.append(cube([side*x-.45, 32, -7], [.9, h, .9], 3))
            b.append(bone('antler_'+str(side), c, parent='head'))
    return b


def frog(material, toad=False):
    b = [bone('body', [cube([-5, 3, -4], [10, 5, 10], material),
                       cube([-4, 2, -4], [8, 1.5, 8], 1)]),
         bone('head', [cube([-5, 4, -7], [10, 4, 5], material),
                       cube([-4.5, 7, -6], [3, 2, 3], material),
                       cube([1.5, 7, -6], [3, 2, 3], material),
                       cube([-4, 7.5, -6.2], [2, 1, .3], 2),
                       cube([2, 7.5, -6.2], [2, 1, .3], 2),
                       cube([-3.5, 4.7, -7.1], [7, .35, .2], 2)])]
    for i, (x,z) in enumerate([(-5,-5),(3,-5),(-7,2),(4,2)]):
        b.append(bone('leg'+str(i), [cube([x, 0, z], [3, 3, 5], material)], [x+1,3,z+2]))
    if toad:
        b.append(bone('warts', [cube([x,8,z], [1.3,.8,1.3],7)
                               for x,z in [(-3,0),(1,3),(-1,4),(3,0),(-4,4)]]))
    return b


def sea(kind):
    if kind == 'abyssal_watcher':
        b = [bone('body', [cube([-6, 5, -6], [12, 11, 12], 8)]),
             bone('eye', [cube([-4, 8, -6.2], [8, 6, .5], 11)])]
        for i in range(6):
            x = (i%3-1)*4
            z = (-1 if i<3 else 1)*3
            b.append(bone('tendril'+str(i), [cube([x-1,-5,z-1], [2,11,2],9),
                                             cube([x-1,-5,z-1.2],[2,8,.5],10)], [x,6,z]))
        return b
    if kind == 'mire_tentacle':
        b = [bone('body',[cube([-5,6,-5],[10,7,10],9), cube([-3,9,-5.2],[6,3,.4],11)])]
        for i in range(8):
            x,z = [(-7,-4),(-7,1),(5,-4),(5,1),(-4,-7),(1,-7),(-4,5),(1,5)][i]
            b.append(bone('tendril'+str(i),[cube([x,0,z],[2,9,2],9),
                                           cube([x-.1,1,z-.1],[2.2,1,2.2],10)], [x+1,8,z+1]))
        return b
    b = [bone('body',[cube([-4,4,-12],[8,7,22],8)]),
         bone('head',[cube([-5,5,-19],[10,7,9],9),
                      cube([-3.5,7,-19.2],[7,3,.4],11),
                      cube([-4,4,-20],[8,1.5,10],10)])]
    b.append(bone('tendril0',[cube([-2.5,5,9],[5,4,14],9)], [0,7,9]))
    for i,x in enumerate([-8,4]):
        b.append(bone('tendril'+str(i+1),[cube([x,6,-2],[4,1,13],10)], [x+2,7,0]))
    return b


def elf(material):
    b = [bone('body',[cube([-4,12,-2],[8,11,4],material), cube([-4.5,12,-2.5],[9,2,5],2)]),
         bone('head',[cube([-3.5,23,-3.5],[7,7,7],15 if material!=14 else 14),
                      cube([-6,26,-1],[3,1.5,2],15 if material!=14 else 14),
                      cube([3,26,-1],[3,1.5,2],15 if material!=14 else 14),
                      cube([-2.5,26.5,-3.7],[2,.8,.3],11 if material==14 else 2),
                      cube([.5,26.5,-3.7],[2,.8,.3],11 if material==14 else 2),
                      cube([-3.7,29,-3.7],[7.4,1.5,7.4],material)], [0,23,0])]
    for i,x in enumerate([-4,0]):
        b.append(bone('leg'+str(i),[cube([x,0,-2],[4,12,4],material)], [x+2,12,0]))
    for i,x in enumerate([-7,4]):
        b.append(bone('arm'+str(i),[cube([x,12,-1.5],[3,11,3],material),
                                   cube([x,11,-1.5],[3,2,3],15)], [x+1.5,22,0]))
    if material == 14:
        b.append(bone('horns',[cube([-4,29,0],[1,5,1],3),cube([3,29,0],[1,5,1],3)],parent='head'))
    if material == 13:
        b.append(bone('spikes',[cube([-7.5,23,-1],[2,3,2],3),cube([5.5,23,-1],[2,3,2],3)]))
    return b


def add(name, family, bones, biomes, weight, width, height, health, speed,
        scale=1, damage=0, celestial=False):
    ident = 'alfheim:'+name
    ROSTER.append(dict(id=ident, name=name.replace('_',' ').title(), family=family,
                       width=width,height=height,health=health,speed=speed,scale=scale,
                       damage=damage,celestial=celestial,biomes=biomes,weight=weight))
    write(ASSETS/f'geo/entity/{name}.geo.json', {'format_version':'1.12.0', 'minecraft:geometry':[
        {'description':{'identifier':'geometry.'+name,'texture_width':1024,'texture_height':1024,
                        'visible_bounds_width':6,'visible_bounds_height':6,'visible_bounds_offset':[0,1,0]},
         'bones':[{'name':'root','pivot':[0,0,0]}]+bones}]})
    move = {}
    idle = {'head':{'rotation':[0,'math.sin(query.anim_time * 35) * 4',0]}} if family!='sea' else {}
    for b in bones:
        n = b['name']
        if n.startswith(('leg','arm')):
            phase = 180 if n[-1] in ('1','2') else 0
            move[n] = {'rotation':[f'math.sin(query.anim_time * 360 + {phase}) * 25',0,0]}
        elif n.startswith('tendril'):
            move[n] = {'rotation':[f'math.sin(query.anim_time * 160 + {int(n[-1])*45}) * 18',0,0]}
            idle[n] = move[n]
    write(ASSETS/f'animations/entity/{name}.animation.json', {'format_version':'1.8.0','animations':{
        'idle':{'loop':True,'animation_length':4,'bones':idle},
        'move':{'loop':True,'animation_length':1,'bones':move}}})
    category = 'monster' if family=='elf' else 'water_creature' if family=='sea' else 'creature'
    write(DATA/f'alfheim/forge/biome_modifier/fey_{name}.json',
          {'type':'forge:add_spawns','biomes':biomes,'spawners':{'type':ident,'weight':weight,
           'minCount':1 if celestial or family=='sea' else 2,
           'maxCount':1 if celestial or family=='sea' else 3}})
    # Modest existing loot, no custom progression shortcut or ritual-boss drops.
    drop = {'deer':'minecraft:leather','frog':'minecraft:slime_ball',
            'toad':'minecraft:slime_ball','sea':'minecraft:ink_sac','elf':'minecraft:stick'}[family]
    write(DATA/f'alfheim/loot_tables/entities/{name}.json', {'type':'minecraft:entity','pools':[
        {'rolls':1,'entries':[{'type':'minecraft:item','name':drop}],
         'conditions':[{'condition':'minecraft:killed_by_player'},
                       {'condition':'minecraft:random_chance','chance':0.35}]}]})


def main():
    woodland = ['alfheim:silverbark_wood','alfheim:bloomfall_vale',
                'mythicbotany:dreamwood_forest','mythicbotany:alfheim_plains','mythicbotany:golden_fields']
    for sex in ['doe','buck']:
        add('whitetail_'+sex,'deer',deer(sex=='buck'),woodland,10 if sex=='doe' else 6,.8,1.75,16,.28)
        add('celestial_'+sex,'deer',deer(sex=='buck'),woodland+['alfheim:void_verge'],1,.8,1.75,28,.32,celestial=True)
    habitats = {'moss':['alfheim:mana_fen','alfheim:decayed_mire'],
                'azure':['alfheim:silverbark_wood','mythicbotany:alfheim_lakes'],
                'amber':['alfheim:bloomfall_vale','mythicbotany:golden_fields']}
    for i,(color,biomes) in enumerate(habitats.items()):
        for size,scale,weight in [('small',.55,8),('large',1,4)]:
            add(color+'_'+size+'_frog','frog',frog(i+4),biomes,weight,.875*scale,.5625*scale,
                6 if size=='small' else 10,.18,scale)
    for color,material,biomes in [('bog',7,['alfheim:mana_fen','alfheim:decayed_mire']),
                                  ('mossback',4,['alfheim:infested_warren','mythicbotany:dreamwood_forest'])]:
        # Vanilla pig dimensions: .9 by .9. Separate model scaling keeps collision honest.
        add(color+'_toad','toad',frog(material,True),biomes,3,.9,.9,16,.14,1.45)
    for name,biomes,weight,width,height,hp,damage in [
        ('abyssal_watcher',['mythicbotany:alfheim_lakes','alfheim:void_verge'],2,1,1.5,26,4),
        ('mire_tentacle',['alfheim:mana_fen','alfheim:decayed_mire'],3,1,.9,20,3),
        ('drowned_maw',['mythicbotany:alfheim_lakes','alfheim:mana_fen'],1,1.1,.85,36,6)]:
        add(name,'sea',sea(name),biomes,weight,width,height,hp,.22,damage=damage)
    for name,mat,biomes,hp,damage in [
        ('wild_elf',12,['alfheim:ashen_grove','alfheim:silverbark_wood','alfheim:sundered_highlands'],20,3),
        ('savage_elf',13,['alfheim:infested_warren','alfheim:decayed_mire','alfheim:hollow_marches'],28,5),
        ('demonic_elf',14,['alfheim:scorchfell','alfheim:void_verge','alfheim:starved_reach'],36,7)]:
        add(name,'elf',elf(mat),biomes,5,.65,1.9,hp,.25,damage=damage)
    write(Path('kubejs/fey_roster.json'),ROSTER)
    write(Path('tools/fey_manifest.json'),ROSTER)
    lang_path=ASSETS/'lang/en_us.json'
    lang=json.loads(lang_path.read_text(encoding='utf-8')) if lang_path.exists() else {}
    for r in ROSTER:
        lang['entity.'+r['id'].replace(':','.')]=r['name']
        lang['item.'+r['id'].replace(':','.')+'_spawn_egg']=r['name']+' Spawn Egg'
    write(lang_path,lang)
    print(f'{len(ROSTER)} creatures: models, animations, spawn modifiers, loot and names generated')


if __name__ == '__main__':
    main()
