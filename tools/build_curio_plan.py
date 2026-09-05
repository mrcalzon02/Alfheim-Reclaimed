"""Validate and emit the class/profession Curios planning catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'alfheim_reclaimed_design/curios'

RANKS = [
    {'id': 'apprentice', 'era': 2, 'frame': 'alfheim:quickened_palebloom', 'profession_tier': 0, 'role': 'eligibility and state visibility'},
    {'id': 'guild', 'era': 5, 'frame': 'alfheim:elementium_core', 'profession_tier': 2, 'role': 'cross-mod logistics and station handshake'},
    {'id': 'master', 'era': 8, 'frame': 'alfheim:rimebound_lattice', 'profession_tier': 4, 'role': 'bounded secondary loop and commission control'},
]

CLASSES = {
    'warrior': {
        'tradition': 'Thornwarden', 'emblem': 'Greatbole Torque', 'emblem_slot': 'necklace',
        'anchors': ['botania:knockback_belt', 'botania:balance_cloak', 'botania:holy_cloak', 'naturesaura:shockwave_creator', 'botania:odin_ring'],
        'hooks': ['successful shield block', 'Taunt hit', 'Charge arrival', 'melee skill hit'],
        'visibility': 'Show guard, threat target and the next valid Bough charge trigger.',
        'handshake': 'A successful block marks one attacker; the next Warrior threat skill consumes the mark instead of creating a second damage proc.',
        'mastery': 'Tectonic Girdle and Greatbole Torque share knockback-state feedback; resisted movement can arm utility, never bonus damage.',
        'guardrail': 'No passive damage reduction, extra heart package or Odin-ring effect is copied onto the suite.'},
    'hunter': {
        'tradition': 'Waywatcher', 'emblem': 'Wolfleaf Token', 'emblem_slot': 'charm',
        'anchors': ['supplementaries:quiver', 'botania:dodge_ring', 'botania:reach_ring', 'botania:travel_belt', 'botania:itemfinder'],
        'hooks': ['ranged skill shot', 'trap placement/trigger', 'spirit-wolf state', 'successful Dexterous Motion dodge'],
        'visibility': 'Show ammunition source, owned trap state, wolf state and recoverable projectile locations.',
        'handshake': 'Quiver-supplied shots and recovered arrows use one routing path; the suite never creates replacement ammunition.',
        'mastery': 'A successful native dodge can prime one trap-control utility window; damage remains on the soul and skill.',
        'guardrail': 'No arrow duplication, permanent invisibility, free projectile reach or trap cooldown reset.'},
    'sorcerer': {
        'tradition': 'Leyweaver', 'emblem': 'Leyglass Prism', 'emblem_slot': 'charm',
        'anchors': ['ars_nouveau:amulet_of_mana_boost', 'ars_nouveau:amulet_of_mana_regen', 'ars_nouveau:shapers_focus', 'irons_spellbooks:affinity_ring', 'irons_spellbooks:cast_time_ring', 'irons_spellbooks:cooldown_ring', 'botania:mana_ring'],
        'hooks': ['Fire school skill', 'Cold school skill', 'golem state', 'teleport completion'],
        'visibility': 'Display Mine and Slash mana, Ars Source access and Iron spell mana as separate meters with their actual owner.',
        'handshake': 'Prism attunement narrows class-signet affixes toward fire, cold or confluence without converting one mod resource into another.',
        'mastery': 'Alternating valid Fire and Cold Mine and Slash skills may arm a Confluence utility window; raw spell power stays in normal affix budget.',
        'guardrail': 'No Source↔mana conversion, duplicate cooldown reduction or cross-mod spell-power multiplication.'},
    'shaman': {
        'tradition': 'Rootspeaker', 'emblem': 'Rainseed Torque', 'emblem_slot': 'necklace',
        'anchors': ['naturesaura:aura_cache', 'naturesaura:aura_trove', 'naturesaura:eye_improved', 'botania:aura_ring', 'ars_nouveau:summon_focus', 'occultism:familiar_ring'],
        'hooks': ['totem summon/expiry', 'restoration skill', 'thorn garden hit', 'Lightning school hit'],
        'visibility': 'Show owned totems, their remaining time, restoration targets and local Aura condition when an ocular is present.',
        'handshake': 'Aura storage and summoning tools provide state/context for Rootspeaker actions; totems never generate free Aura or Source.',
        'mastery': 'Completing restoration and storm actions around the same active totem arms a bounded renewal utility window.',
        'guardrail': 'No passive Aura generation, immortal summons, autonomous healing loop or second copy of native totem restoration.'},
    'warlock': {
        'tradition': 'Duskkeeper', 'emblem': 'Mourning Nameleaf', 'emblem_slot': 'charm',
        'anchors': ['irons_spellbooks:conjurers_talisman', 'irons_spellbooks:greater_conjurers_talisman', 'irons_spellbooks:wicked_bone_ring', 'occultism:familiar_ring', 'botania:unholy_cloak', 'botania:invisibility_cloak'],
        'hooks': ['curse application/expiry', 'summon creation/expiry', 'damage-over-time kill', 'named familiar present'],
        'visibility': 'Show curse ownership, summon timers and whether a timeout or kill caused removal.',
        'handshake': 'Valid cursed or summoned encounters write bounded memory marks used by explicit Occultism cross-binding recipes.',
        'mastery': 'Conjurer talismans expose timeout state to the emblem; their cooldown exception is never duplicated by the class suite.',
        'guardrail': 'No free summon cooldown skip, extra ricochet, invisibility inheritance or loot from repeatedly resummoning.'},
    'minstrel': {
        'tradition': 'Dawnsinger', 'emblem': 'Dawncourt Brooch', 'emblem_slot': 'necklace',
        'anchors': ['botania:diva_charm', 'botania:aura_ring', 'ars_nouveau:amulet_of_mana_regen', 'irons_spellbooks:concentration_amulet', 'botania:balance_cloak', 'botania:holy_cloak'],
        'hooks': ['song cast', 'healing applied to another player', 'Power Chord hit', 'resource-support effect applied'],
        'visibility': 'Show song radius, eligible party members, active song families and overheal separately.',
        'handshake': 'Different valid song families build resonance; repeating one song refreshes state but does not farm additional stacks.',
        'mastery': 'Nearby crafters can receive an Inspired Work cue and commission attribution, never profession XP or free outputs.',
        'guardrail': 'No aura-ring mana duplication, permanent charm control, free healing echo or multiplicative party stacking.'},
}

PROFESSIONS = {
    'mining': {
        'title': 'Bloom Delver', 'cuff': 'Strata Cuff',
        'anchors': ['botania:mining_ring', 'botania:itemfinder', 'occultengineering:combined_goggles', 'naturesaura:aura_cache'],
        'action': 'player breaks a naturally generated, tier-mapped ore/bloom with a valid mining tool',
        'visibility': 'Show ore/bloom profession tier, expected depth band, tool validity and whether the block awards native XP.',
        'handshake': 'Ring of the Mantle supplies Haste; goggles/ocular data and native drops remain separate. Route mining materials to an equipped bag without duplicating them.',
        'mastery': 'Unlock survey commissions and tier-appropriate bloom targeting that consumes an explicit mana/aura reagent.',
        'guardrail': 'Placed blocks, Silk Touch replacement loops and automated breakers award no player proof or XP.'},
    'farming': {
        'title': 'Grove Tender', 'cuff': 'Seedkeeper Cuff',
        'anchors': ['naturesaura:eye_improved', 'naturesaura:aura_cache', 'botania:reach_ring', 'botania:goddess_charm'],
        'action': 'player harvests a mature mapped crop; growth-stage requirement must pass',
        'visibility': 'Show maturity, mapped profession tier, local Aura condition and missing crop integration.',
        'handshake': 'Agricarnation, Agronomic Sourcelink and Ritual of Growth may grow crops, but only the actual player harvest can award personal profession proof.',
        'mastery': 'Crop-family diversity unlocks seed and reagent commissions; it does not raise harvest yield.',
        'guardrail': 'No break/replant loop on immature crops, automated XP, passive growth pulse or duplicate produce.'},
    'fishing': {
        'title': 'Tidekeeper', 'cuff': 'Tideledger Cuff',
        'anchors': ['botania:water_ring', 'botania:reach_ring', 'naturesaura:aura_cache'],
        'action': 'player completes a valid fishing catch through the native hook',
        'visibility': 'Record water/biome condition, catch family, native material tier and cooking demand.',
        'handshake': 'Ring of Chordata improves underwater work while the cuff routes caught ingredients to the Hearthkeeper chain.',
        'mastery': 'Catch-family diversity produces a commission ledger used in native Cooking recipes; it never rolls a second catch.',
        'guardrail': 'No AFK catch multiplier, extra treasure roll, weather bypass or duplicate fishing material.'},
    'husbandry': {
        'title': 'Wildward', 'cuff': 'Herdsong Cuff',
        'anchors': ['botania:diva_charm', 'occultism:familiar_ring', 'ars_nouveau:summon_focus', 'naturesaura:eye'],
        'action': 'player completes a valid animal breeding event for a mapped adult pair',
        'visibility': 'Show valid feed, breeding cooldown, species mapping and lineage diversity.',
        'handshake': 'Diva/familiar/summoning tools assist handling and pickup; they do not count as player breeding or generate animals.',
        'mastery': 'Species-diverse husbandry commissions unlock hide, fibre and cooking routes using native meat materials.',
        'guardrail': 'No slaughter XP, child rebreeding, dispenser credit, summoned-creature breeding or repeated pair spam.'},
    'salvaging': {
        'title': 'Memory Reclaimer', 'cuff': 'Reclaimer Cuff',
        'anchors': ['botania:magnet_ring', 'botania:itemfinder', 'occultism:satchel', 'mmorpg:master_bag', 'occultism:storage_remote'],
        'action': 'player confirms a genuine soul-bearing item at the native salvage station',
        'visibility': 'Show salvage eligibility, protected/favorited state and a preview category without revealing hidden random results.',
        'handshake': 'Magnets and familiars collect drops; bags/satchels form a marked queue, but the native salvage station remains mandatory.',
        'mastery': 'Batch confirmation and commission attribution reduce clicks while preserving every input and output roll.',
        'guardrail': 'Never salvage equipped/favorited items, auto-salvage pickups, reroll results or create rarity escalation loops.'},
    'gear_crafting': {
        'title': 'Armsinger', 'cuff': 'Forge-Measure Cuff',
        'anchors': ['create:goggles', 'occultengineering:combined_goggles', 'botania:monocle', 'mmorpg:master_bag'],
        'action': 'player completes a native Gear Crafting recipe at its station',
        'visibility': 'Show frame era, profession tier, missing prepared step, soul outcome range and station validity.',
        'handshake': 'Create stress, Mana routing and otherworld materials appear in one read-only work order; each mod keeps its own power system.',
        'mastery': 'Signed commissions and class-crystal recipes narrow a legal soul profile while retaining native level/rarity rules.',
        'guardrail': 'No material discount, free rarity, NBT-destructive frame upgrade or crafting-table bypass.'},
    'enchanting': {
        'title': 'Runeweaver', 'cuff': 'Infuser Cuff',
        'anchors': ['ars_nouveau:ring_of_lesser_discount', 'ars_nouveau:ring_of_greater_discount', 'irons_spellbooks:affinity_ring', 'botania:mana_ring', 'botania:aura_ring', 'ars_nouveau:amulet_of_mana_regen'],
        'action': 'player completes a native Infusing/Enchanting recipe at its station',
        'visibility': 'Show compatible affix family, socket/rune state, resource owner and destructive choices before confirmation.',
        'handshake': 'Ars discounts, Iron affinity and Botania mana keep their native scopes; crystals only select explicit Mine and Slash recipe branches.',
        'mastery': 'A costly master recipe may protect one chosen affix family during a reroll while consuming the normal orb plus an added reagent.',
        'guardrail': 'No free reroll, cross-mod mana discount, copied enchantment, guaranteed maximum affix or hidden NBT loss.'},
    'cooking': {
        'title': 'Hearthkeeper', 'cuff': 'Hearthcord Cuff',
        'anchors': ['occultism:satchel', 'mmorpg:master_bag', 'naturesaura:aura_cache'],
        'action': 'player completes a native Cooking recipe or an explicitly mapped Farmer/Miners Delight preparation',
        'visibility': 'Show meal family, MMO food category, active-food conflict and missing side ingredients.',
        'handshake': 'Mapped Farmer/Miners Delight dishes become explicit inputs to native Cooking recipes instead of silently granting profession XP.',
        'mastery': 'Party platters divide the same total portions into a commission output; they do not multiply servings or stack duplicate food buffs.',
        'guardrail': 'No XP for ordinary crafting unless mapped, no passive feeding, no meal duplication and strongest-only overlapping MMO food rule.'},
    'alchemy': {
        'title': 'Dewbrewer', 'cuff': 'Dewglass Cuff',
        'anchors': ['ars_nouveau:alchemists_crown', 'botania:blood_pendant', 'irons_spellbooks:amethyst_resonance_charm', 'naturesaura:aura_cache', 'ars_nouveau:amulet_of_mana_regen'],
        'action': 'player completes a native Alchemy recipe or an explicitly mapped botanical/Ars preparation',
        'visibility': 'Show effect family, potency/duration branch, active conflict and whether a container preserves NBT.',
        'handshake': 'Botanical brews, Ars flasks and Mine and Slash potions meet through explicit conversion recipes with separate resource costs.',
        'mastery': 'Choose duration or potency at equal budget, or bind an eligible brew into a pendant through a validated NBT-preserving operation.',
        'guardrail': 'No instant-consumption duplication, permanent buff copy, free container, effect stacking exploit or generic potion XP.'},
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inv = json.loads((OUT / 'installed_curios_inventory.json').read_text(encoding='utf-8'))
    available = {x['id'] for x in inv['wearables'] if x['classification'] == 'functional'}
    evidence = json.loads((ROOT / 'alfheim_reclaimed_design/armory/installed_mns_evidence.json').read_text(encoding='utf-8'))
    assert set(PROFESSIONS) == set(evidence['professions'])
    assert set(CLASSES) == set(evidence['spell_schools'])
    anchors = {x for row in [*CLASSES.values(), *PROFESSIONS.values()] for x in row['anchors']}
    missing = sorted(anchors - available)
    assert not missing, f'anchors not wearable in installed pack: {missing}'
    registry = set(json.loads((ROOT / 'tools/registry_items.json').read_text(encoding='utf-8'))['ids'])
    assert all(rank['frame'] in registry for rank in RANKS)
    planned = []
    for class_id, row in CLASSES.items():
        for family, slot in [('signet', 'ring'), ('emblem', row['emblem_slot'])]:
            for rank in RANKS:
                planned.append({'id': f'alfheim:curio/class/{class_id}/{family}_{rank["id"]}', 'kind': 'class', 'owner': class_id, 'family': family, 'rank': rank['id'], 'era': rank['era'], 'slot': slot})
    for profession_id in PROFESSIONS:
        for rank in RANKS:
            planned.append({'id': f'alfheim:curio/profession/{profession_id}/{rank["id"]}', 'kind': 'profession', 'owner': profession_id, 'family': 'cuff', 'rank': rank['id'], 'era': rank['era'], 'slot': 'bracelet'})
    assert len(planned) == len({x['id'] for x in planned}) == 63
    catalog = {
        'status': 'design catalog; implementation status is recorded in tools/curios_manifest.json',
        'basis': {'live_slot_types': inv['live_slot_type_count'], 'installed_wearables': inv['wearable_count'], 'functional_wearables': inv['functional_count'], 'classes': 6, 'professions': 9},
        'slot_policy': {'new_slot_types': 0, 'profession_cuff_slot': 'bracelet', 'active_profession_cuffs': 1, 'class_signet_slot': 'ring', 'active_class_signets_max': 2, 'active_class_emblems_max': 1, 'modify_existing_slot_capacity': False},
        'ranks': RANKS,
        'counts': {'planned_items': 63, 'class_items': 36, 'profession_items': 27, 'existing_anchor_ids': len(anchors)},
        'classes': CLASSES,
        'professions': PROFESSIONS,
        'planned_items': planned,
        'high_power_items_not_required_for_progression': ['botania:loki_ring', 'botania:odin_ring', 'botania:thor_ring', 'mythicbotany:andwari_ring', 'mythicbotany:cursed_andwari_ring', 'botania:flight_tiara', 'naturesaura:death_ring'],
    }
    (OUT / 'curio_suite_catalog.json').write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = ['# Curio suite matrix', '', 'Generated by `tools/build_curio_plan.py`. Planning only.', '', '## Class suites', '', '| Native class | Elven suite | Emblem / slot | Existing anchors |', '|---|---|---|---|']
    for cid, row in CLASSES.items():
        lines.append(f"| `{cid}` | {row['tradition']} | {row['emblem']} / `{row['emblem_slot']}` | " + ', '.join(f'`{x}`' for x in row['anchors']) + ' |')
    lines += ['', '## Profession suites', '', '| Native profession | Elven trade | Cuff | Existing anchors |', '|---|---|---|---|']
    for pid, row in PROFESSIONS.items():
        lines.append(f"| `{pid}` | {row['title']} | {row['cuff']} | " + ', '.join(f'`{x}`' for x in row['anchors']) + ' |')
    (OUT / 'SUITE_MATRIX.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Curio plan checked: 6 class suites, 9 profession suites, 63 planned items, {len(anchors)} installed functional anchors, 0 missing IDs.')


if __name__ == '__main__':
    main()
