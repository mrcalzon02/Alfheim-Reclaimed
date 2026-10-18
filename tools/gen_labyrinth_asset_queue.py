"""Track art production against all five Acts without changing the runtime bestiary."""
import json
from pathlib import Path

from gen_labyrinth_asset_kit import OUT, ROOMS, SERVICES

ROOT=Path(__file__).resolve().parents[1]
ACTS=[
    (1,'Ashen Cloister','Forest abbey; worn ash, ivory ossuaries, violet mourning cloth, oxidized bronze.',
     ['stone_bricks','mossy_stone_bricks','chiseled_stone_bricks','spruce_planks','bone_block'],
     list(ROOMS), ['ashen_novice','lurking_silkmaw','bell_warden','ossuary_bowyer','reliquary_sentinel','the_ossuary_prior']),
    (2,'Buried Covenant','Sun-bleached caravan abbey; recessed sandstone bands, funerary gold, cobalt cistern channels.',
     ['cut_sandstone','chiseled_sandstone','smooth_sandstone','terracotta','blue_terracotta'],
     'sandstone_vestibule caravan_nave sunken_cloister embalmer_cells scarab_ossuary dart_gallery cistern_belfry sand_scriptorium seal_vault water_cistern caravan_refectory pharaoh_gallery funerary_chapel well_descent_hub trap_arena dune_sanctuary caravan_return_shrine cistern_switchback'.split(),
     ['dune_reliquary','scarlet_scarab_host','cistern_whisper']),
    (3,'Verdant Blight','Flooded root cloister; sheltered dry refuges, fungal shelves, green-black roots and visible poison sacs.',
     ['mud_bricks','mossy_cobblestone','mangrove_planks','rooted_dirt','green_terracotta'],
     'root_vestibule flooded_nave strangled_cloister fever_cells spore_ossuary root_lash_gallery drowned_belfry mold_scriptorium bog_reliquary sewer_cistern fungal_refectory root_grave_gallery blighted_chapel sump_descent_hub fever_arena heartroot_sanctuary marsh_return_shrine sluice_switchback'.split(),
     ['bog_lanternling','verdigris_ravager','spore_matriarch']),
    (4,'Cinder Testament','Burned fortress-monastery; load-bearing black masonry, riveted ash armor, chain arcs, banked coals.',
     ['nether_bricks','chiseled_nether_bricks','polished_blackstone_bricks','basalt','red_terracotta'],
     'cinder_vestibule furnace_nave chain_cloister ash_cells charnel_ossuary chain_gallery furnace_belfry soot_scriptorium ember_reliquary quench_cistern ash_refectory pyre_gallery blood_chapel furnace_descent_hub chain_arena cinder_sanctuary forge_return_shrine ash_switchback'.split(),
     ['cinder_initiate','chain_bailiff','furnace_gnasher']),
    (5,'Winter Crown','Besieged snow monastery; massive slate buttresses, ivory frost burial markers, fur and glacial fissures.',
     ['deepslate_bricks','polished_deepslate','packed_ice','snow_block','blue_ice'],
     'rime_vestibule besieged_nave snow_cloister penitent_cells ice_ossuary prison_gallery frost_belfry frozen_scriptorium crown_reliquary thaw_cistern survivor_refectory burial_hold glacial_chapel abyss_descent_hub siege_arena winter_sanctuary survivor_return_shrine glacier_switchback'.split(),
     ['rime_penitent','snowblind_stalker','hailcarved_watcher']),
]


def main():
    catalog=json.loads((ROOT/'alfheim_reclaimed_design/monastery_labyrinth/monster_catalog.json').read_text())
    art=json.loads((OUT/'creature_art_manifest.json').read_text())
    existing={row['catalog_id']:row for row in art['models']}
    known={row['id'] for row in catalog['creatures']}
    rows=[]
    registry=set(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text()))
    for act,title,brief,palette,families,priority in ACTS:
        assert len(families)==18 and len(set(families))==18
        assert all('minecraft:'+block in registry for block in palette), palette
        assert all(name in known for name in priority)
        creatures=[]
        for monster in catalog['creatures']:
            if monster['act']!=act:continue
            creature={'catalog_id':monster['id'],'role':monster['role'],
                      'telegraph_to_model':monster['primary']['description'],
                      'counterplay_to_preserve':monster['counterplay'],
                      'art_state':'textured_prototype' if monster['id'] in existing else 'planned',
                      'mechanical_state':'design_only','sound':'unassigned'}
            if monster['id'] in existing:
                creature['asset']=existing[monster['id']]['blockbench']
            creatures.append(creature)
        rows.append({'act':act,'title':title,'art_direction':brief,
                     'catalogue_species':len(creatures),
                     'textured_species_prototypes':sum(c['art_state']=='textured_prototype' for c in creatures),
                     'masonry_materials':['minecraft:'+b for b in palette],
                     'room_families':[{'id':family,'state':'static_validated_prototype' if act==1 else 'planned'} for family in families],
                     'refuge_services':list(SERVICES),'priority_creature_art':priority,
                     'next_creature_art':([name for name in priority if name not in existing] or
                                          [c['catalog_id'] for c in creatures if c['art_state']=='planned'][:6]),
                     'creatures':creatures,
                     'boss_id':next(c['id'] for c in catalog['creatures'] if c['act']==act and c['role']=='boss'),
                     'encounter_level_policy':'existing Mine and Slash distance from spawn; no descent multiplier'})
    queue={'batch':'01','acts':rows,'runtime_species_implemented':0,'textured_species_prototypes':len(existing),
           'next_art_act':next((r['act'] for r in rows if r['next_creature_art']),None),
           'production_order':['Act I shell-to-template adapter and gap/height fitting',
                               'Act I animated native models and twelve distinct AI implementations',
                               'Functional refuge trades, encounter controllers and boss',
                               'Act II-V authored silhouettes/rooms; expand to full catalogue',
                               'Fresh-world, multiplayer, performance and client acceptance'],
           'species_rule':'Skins and affixes do not count as new mechanical species.',
           'stair_adapter_gate':'Prototype rise is 12 blocks. Native strata vary; fit exact floor delta and headroom before replacing shafts.',
           'placement_gate':'One reservation for monastery/village/labyrinth; existing court/castle/district priority and independent-structure gap remain runtime gates.'}
    (OUT/'five_act_asset_queue.json').write_text(json.dumps(queue,indent=2)+'\n',encoding='utf-8')
    print(f'Five-Act queue: 90 room designs, 130 catalogue links, {len(existing)} textured prototypes; 0 implemented species.')


if __name__=='__main__':main()
