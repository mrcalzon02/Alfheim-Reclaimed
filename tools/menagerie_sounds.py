"""Creature-specific pitched native sound-event palettes, verified against Minecraft 1.20.1 assets."""
import json
from pathlib import Path
INSTALL=Path('C:/Users/Admin/curseforge/minecraft/Install')
# ambient, alternate ambient, hurt, death, step, windup, attack, voice pitch
PROFILES={
'hulking_troll':('entity.ravager.ambient','entity.warden.ambient','entity.ravager.hurt','entity.ravager.death','entity.ravager.step','entity.ravager.roar','entity.iron_golem.attack',.7),
'cyclops':('entity.ravager.ambient','entity.iron_golem.damage','entity.ravager.hurt','entity.iron_golem.death','entity.iron_golem.step','entity.ravager.celebrate','entity.warden.attack_impact',.85),
'briar_beast':('entity.fox.aggro','block.wood.break','entity.ravager.hurt','block.azalea.break','block.rooted_dirt.step','entity.fox.aggro','entity.ravager.attack',.65),
'thorn_infestor':('block.roots.break','block.sculk_catalyst.bloom','block.wood.break','block.roots.break','block.rooted_dirt.step','block.vine.break','entity.player.attack.sweep',.7),
'stone_gargoyle':('entity.phantom.ambient','block.stone.break','entity.iron_golem.hurt','entity.iron_golem.death','block.stone.step','entity.phantom.swoop','entity.phantom.bite',.75),
'fen_hag':('entity.witch.ambient','entity.ghast.ambient','entity.witch.hurt','entity.witch.death','block.mud.step','entity.witch.celebrate','entity.evoker.cast_spell',.78),
'hollow_stag_wendigo':('entity.goat.screaming.ambient','entity.skeleton.ambient','entity.skeleton.hurt','entity.goat.screaming.death','entity.skeleton.step','entity.warden.agitated','entity.warden.attack_impact',.62),
'duskweaver':('entity.bee.loop_aggressive','entity.spider.ambient','entity.spider.hurt','entity.spider.death','entity.spider.step','entity.phantom.swoop','entity.spider.hurt',.85),
'hollow_bride':('entity.ghast.ambient','entity.allay.ambient_without_item','entity.ghast.hurt','entity.ghast.death','block.wool.step','entity.evoker.prepare_attack','entity.evoker.cast_spell',.8),
'barrow_maw':('entity.hoglin.ambient','entity.slime.squish','entity.hoglin.hurt','entity.hoglin.death','block.mud.step','entity.hoglin.angry','entity.hoglin.attack',.65),
'nuckelavee':('entity.horse.angry','entity.skeleton_horse.ambient','entity.skeleton_horse.hurt','entity.skeleton_horse.death','entity.horse.step','entity.horse.angry','entity.ravager.attack',.7),
'redcap_reaver':('entity.pillager.ambient','entity.witch.ambient','entity.pillager.hurt','entity.pillager.death','block.wood.step','entity.pillager.celebrate','entity.player.attack.sweep',1.2),
'corrupted_crystal_colossus':('block.amethyst_block.resonate','entity.iron_golem.damage','entity.iron_golem.hurt','block.amethyst_cluster.break','entity.iron_golem.step','entity.warden.sonic_charge','entity.warden.attack_impact',.62),
'shard_reaver':('block.amethyst_block.chime','block.amethyst_block.hit','block.amethyst_cluster.break','block.glass.break','block.amethyst_block.step','block.amethyst_block.resonate','entity.player.attack.sweep',.85),
'prism_warden':('block.amethyst_block.resonate','entity.warden.heartbeat','block.amethyst_block.break','entity.evoker.death','block.amethyst_cluster.step','entity.warden.sonic_charge','entity.evoker.cast_spell',.75),
'marrow_tick':('entity.silverfish.ambient','entity.slime.squish_small','entity.silverfish.hurt','entity.silverfish.death','entity.silverfish.step','entity.silverfish.ambient','entity.slime.attack',1.3),
'rib_burrower':('entity.silverfish.ambient','entity.skeleton.ambient','entity.silverfish.hurt','entity.skeleton.death','entity.skeleton.step','entity.silverfish.ambient','entity.silverfish.hurt',.82),
'sinew_leech':('entity.slime.squish','block.slime_block.hit','entity.slime.hurt_small','entity.slime.death','block.slime_block.step','entity.slime.jump','entity.slime.attack',.7),
'parasite_maw':('entity.hoglin.ambient','entity.bee.loop_aggressive','entity.slime.hurt','entity.slime.death','block.slime_block.step','entity.hoglin.angry','entity.hoglin.attack',.6)}

def vanilla_events():
    version=json.loads((INSTALL/'versions/1.20.1/1.20.1.json').read_text())
    asset_id=version['assetIndex']['id'];root=INSTALL/'assets'
    index=json.loads((root/'indexes'/f'{asset_id}.json').read_text())
    h=index['objects']['minecraft/sounds.json']['hash']
    return json.loads((root/'objects'/h[:2]/h).read_text())

def build_sounds(species,labels):
    vanilla=vanilla_events();sounds={};lang={}
    verbs={'ambient':'stirs','hurt':'is hurt','death':'dies','step':'moves','windup':'readies an attack','attack':'strikes'}
    for name in species:
        ambient,alternate,hurt,death,step,windup,attack,pitch=PROFILES[name]
        cues={'ambient':[ambient,alternate],'hurt':[hurt],'death':[death],'step':[step],'windup':[windup],'attack':[attack]}
        for cue,refs in cues.items():
            key=f'monstrosity.{name}.{cue}';subtitle='subtitles.alfheim_companion.'+key
            entries=[]
            for i,ref in enumerate(refs):
                assert ref in vanilla,('Unknown Minecraft 1.20.1 sound event',ref)
                entries.append({'name':'minecraft:'+ref,'type':'event','pitch':pitch,'volume':.55 if cue=='ambient' else .8,'weight':3 if i==0 else 1})
            sounds[key]={'subtitle':subtitle,'sounds':entries};lang[subtitle]=labels[name]+' '+verbs[cue]
    key='maggot_mound.ambient';sub='subtitles.alfheim_companion.'+key
    sounds[key]={'subtitle':sub,'sounds':[{'name':'minecraft:entity.slime.squish_small','type':'event','pitch':.7,'volume':.5},{'name':'minecraft:entity.silverfish.step','type':'event','pitch':.8,'volume':.4}]}
    lang[sub]='Maggots writhe'
    return sounds,lang
