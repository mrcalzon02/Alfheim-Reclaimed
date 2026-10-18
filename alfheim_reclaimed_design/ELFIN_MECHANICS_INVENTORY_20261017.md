# Elfin mechanics inventory and expansion priorities

Inspection date: 2026-10-17. Scope: the local pack as installed and authored, not merely the recent creatures and crown. This is a source/artifact inventory and a set of proposals, not an in-game acceptance pass. No gameplay, recipes, configuration or mod jars were changed for this review.

**User correction after review:** MineColonies owns living settlements and reclamation. Those
recommendations are not authorization for parallel custom systems. Current approved follow-up:
fix regalia acquisition and plan usable workshop golems. The golem plan is
`../first_party_mods/alfheim_golems/docs/USABLE_GOLEMS_20261017.md`; 63 native regalia recipes are
now authored, with attunement effects still pending. The inventory below records the earlier
inspection baseline rather than claiming those later changes existed at inspection time.

## Overall finding

The pack has substantial magical production, exploration, architecture, creatures and collecting. Its strongest next additions would connect those assets to a homeland that visibly recovers, settlements with daily life, and relationships with their inhabitants. Those themes fit the existing premise: an elf reclaiming devastated Alfheim through botanical magic.

Use Botania/MythicBotany and Ars Nouveau for production and unlocks, and retain Mine and Slash as the combat/profession authority. Nature's Aura, Feywild, MineColonies and the first-party mods can supply the supporting interactions. Additional mods are not needed for the first proposed passes.

## What is actually present

Measured on disk: **89 root-level mod jars**, **27 KubeJS startup scripts**, **26 server scripts**, and **19 FTB quest chapter files** (ten campaign, one cartographer and eight reference chapters). File presence does not establish that every quest or integration has been played successfully.

| Area | Present foundation | Important limit or expansion opportunity |
|---|---|---|
| Magical production | Botania, MythicBotany and Ars Nouveau; Twelve Blooms, Four Rites, Archive Groves, crystal resources and staged material chains | Already a strong production vocabulary. Extend these processes rather than creating another universal magical currency. |
| Other magical traditions | Nature's Aura, Feywild, Occultism, Iron's Spells, Create: Wizardry and Occult Engineering are installed | Distinguish installed native capabilities from custom pack integration. Entry quests and recipes do not prove complete integration across the campaign. |
| Cross-system materials | Liquid Bifrost and its refinement/exchange chain | This is a material bridge, not a general travel network. New systems should use its existing exchange costs where appropriate. |
| Combat and professions | Mine and Slash, Dungeon Realm, The Harvest, Ancient Obelisks, Knight Quest; the custom armory bridge | Keep damage, gear scaling and personal profession rewards under their existing owners. Avoid a competing combat or profession XP system. |
| World and discoveries | Alfheim as home, Midgard beyond the gate, custom regional terrain, Deepworks, tombs, ley corridors, districts, royal sites and war remnants | Numerous structures exist. Persistent consequences for repairing, inhabiting and defending them are a stronger addition than another generic ruin family. Natural/client acceptance varies by feature. |
| Elven society | Twelve custom adult civilian roles, 48 appearances, whispers, and 72 role-based late-game offers | The inspected citizen goals cover trading, panic, looking and wandering. They do not provide a home/work schedule, settlement citizenship or player reputation. These citizens are separate from MineColonies workers. |
| Fey settlements | Expanded seasonal sky villages, modeled log apartments, resident shelter/release, plant visits, bounded crop growth and harvestable Pixie Dust | Basic fey habitation and gardening already exist. Different household specialties and court interactions would extend that behavior. |
| Companion | A persistent elven companion with native tasks, inventory, memory and claim-aware service layers | Do not turn its singleton lifecycle into a whole-town worker system. Keep construction/logistics ownership and real material consumption. |
| Workers and automation | Native Ars helpers, Occultism spirits, MineColonies and Create are installed | These already overlap item handling, farming and crafting. First-party golems should have a distinct purpose rather than repeat every helper. |
| First-party golems | `alfheim_golems-0.1.0.jar`, persistence/order contracts, configuration and diagnostics | The inspected entry point explicitly registers **no entities or items**; the installed jar has no recipes. Worker, Artisan and Sentinel gameplay remains future work. Older planning headers incorrectly say even the scaffold/jar is absent. |
| Leyworks and furnishings | A native conduit node with pyramid detection, six-axis particles, obstruction checks and local Leyline Presence; Manna Stone storage, utility furnishings and decoration | This node implementation does not establish a functioning inherited multi-node payload network. Complete relay transmission and the planned resonances before promising settlement-wide wards. |
| Regalia | **63 custom registered/slotted items:** 36 class pieces and 27 profession pieces | The manifest explicitly says **no effect, no recipe**. Existing functional third-party Curios remain separate. Completing selected regalia workflows offers more value than adding another large accessory catalogue. |
| Wildlife and threats | Biome/style creature selections, detailed native enemy additions, regional monstrosities, void crystal golems, Titan parasites and custom sounds | Add ecology, field signs, encounter purposes and progression-compatible counterplay. The numerous variants should not be represented as an equal number of distinct behavior systems. |
| Gems and collecting | 232 catalogue gemstones, 28 source pools, host-matched deposits, geologist displays, a staged wearable Crown of Eternity | Gem availability, displays and the collection goal are authored. The 232 collection materials do not thereby have 232 functional jewelry or socket effects. Recent content still has named in-game checks pending. |
| Food and domestic life | Farmer's Delight, Miner's Delight, furniture mods, Mine and Slash cooking, agricultural districts and utility objects | Strong ingredients and scenery exist. Feasts, hospitality, gathering events and court commissions could give them shared purposes. |
| Teaching and discovery | FTB Quests, reference chapters, quest givers, JEI, Jade and generated process/use descriptions | Extend the existing Compendium for new regional restoration, inhabitants, monsters and gems; do not add another disconnected manual. |

## Proposed mechanics, in recommended order

These are design recommendations, not claims of existing features or promises that an adapter has already been implemented.

### 1. Reclaimable groves and districts — assigned to MineColonies

The user assigned this responsibility to MineColonies. Any future magical reclamation work should
extend colony construction, research, supply and land-development workflows. The earlier proposal
for an independent regional state machine is withdrawn.

Existing Nature's Aura measurements and Ars environmental rituals can remain available tools,
but they do not become a new custom settlement authority or an independent campaign requirement.

No independent reclamation implementation is planned by this inventory.

### 2. Inhabited elven settlements — assigned to MineColonies

MineColonies supplies the settlement population, homes, jobs, routines, construction and growth.
The useful elven work is citizen presentation, build styles, supply recipes and supported integration
with the existing districts. A separate household-attraction or custom colony simulation is withdrawn.

Use MineColonies for the actual worker/research/production colony and its resident population.
Custom merchants remain independent traders rather than a parallel settlement authority. Proper
MineColonies elven models, citizen theming and build styles are a distinct integration task,
not accomplished by the custom merchant skins.

### 3. Seasonal court favor, bargains and commissions

Use Feywild's installed seasonal alignment as the starting point. Give each court preferences and a recognizable service: restoring a spring, defending an orchard, supplying a feast, recovering an heirloom or clearing a Titan infestation. Favor earns permission, commissions, patterns, invitations and cosmetic honors.

The missing custom layer is persistent player/court relations and meaningful regional tasks. Do not duplicate alignment with an unrelated second faction scheme. Offer clear, recoverable consequences for breaking a bargain; avoid permanently losing campaign progression or being punished for rules the player could not know.

### 4. Functional elven gemcraft and guild regalia

Finish a small useful subset of the existing 63 regalia items. Supply reachable spine-based recipes, actual native profession eligibility and clear descriptions of what each piece does. Gems can form families of lenses, bezels and focuses, giving mining and displays practical connections to existing crafting stations.

Do not assign 232 arbitrary stacking combat bonuses or replace Mine and Slash's native gear sockets. The Crown of Eternity can remain a prestigious collection artifact, with a presentation stand or coronation ceremony as optional recognition. Crown ownership should not silently become a new campaign gate.

### 5. Repairable sanctuary wards

Turn a restored shrine or defended grove into a bounded sanctuary using existing magical supplies. A repaired focus, maintained offerings and connected relays could support warning chimes, clear field boundaries and selected protective functions.

Ars already ships a ward and a deny-spawn ritual; Botania also has established protective tools. The distinct custom addition is **a repairable settlement installation with visible costs and state**. Extend the present ley node foundation only after real relay propagation is implemented. Do not imply that a local presence effect currently powers a whole network.

### 6. Specialized fey households and gardens

Extend existing apartments with preferences: flowering groves, orchards, herb beds, fungi or suitable aquatic gardens. Appropriate habitat and plant visits can support different bounded services or dust-related ingredients. The world should visibly show what each household tends.

Keep the current housing, shelter and harvesting loop. This is an extension, not another generic pet-taming system. Use native Ars helpers where their job already fits.

### 7. Living architecture and grafting

Grow a few authored forms from prepared frames: a root stair, branch bridge, arbor, hollow-log room or small canopy platform. The player pays real timber, botanical materials and magical cost, chooses an orientation and sees the occupied volume before growth.

Give this a distinct elven construction identity while reusing existing materials and construction services. Growth must respect claims, block entities, occupied rooms, settlement reservations and player builds. This does not require unrestricted procedural tree cities as its first implementation.

### 8. Practical songs and instruments

Create a flute, harp or chime with a few learned performances: gathering nearby residents, calling housed fey home, opening a particular ancient seal or participating in a grove-restoration working. Audio, posture and particles should explain success and missing requirements.

This would give the existing “Song” theme an audible expression. A performance should invoke a defined existing working with its real cost, not introduce another mana pool or reproduce every spell as a free instrument effect. Avoid latency-sensitive rhythm requirements for basic progression.

### 9. Moonlit and seasonal craft

Use selected night/sky conditions for collecting moon-dew, charging a lens, tending a rare blossom or holding a court ceremony. Make the conditions visible on the item or workstation.

The installed Ars jar already contains Moonfall, Sunrise and weather-related ritual classes. Integrate and verify those native time/weather workings before inventing new ones. Keep moon conditions to optional quality, sidegrades or rituals with an attainable alternative; do not turn a required craft into a real-time calendar wait. Seasonal courts do not require installing a global seasons mod.

### 10. Hospitality, feasts and noble commissions

Let Hearthkeepers prepare a court-specific feast using existing cooking systems and the agricultural districts. A supplied table can host visitors, complete a commission or celebrate a repaired district. Flower arrangements, cups and furnishings then have a social purpose.

Keep native food effects and profession rewards authoritative. Add an event and its explicit reward, not a second set of duplicate cooking XP or unlimited passive buffs.

### 11. A field naturalist and monster-lore loop

Add tracks, shed fragments, parasite signs, disturbed vegetation and readable habitat clues for the existing enemy roster. Studying a regional threat can unlock a truthful Compendium entry, a ward recipe or a preparation recommendation using already implemented effects.

Give expensive expeditions a purpose beyond spawning another enemy variant. Differentiate real combat behavior from flavor text: an entry must not promise a weakness or immunity that the creature's code does not implement. Keep unique boss rewards and class power in the existing combat economy.

### 12. Ancestral remembrance and heirlooms

Use the existing tombs, funerary pieces and elder districts for respectful recovery: identify a lost person, return an heirloom, mend a memorial or settle a local haunting. An honorable resolution could grant an inscription, court favor or a decorative lineage token; a disturbance can trigger a clearly signaled encounter.

This gives elves history and obligations beyond trading and combat. Build on existing locations and loot instead of scattering another large structure roster.

## Suggested first connected release

The original independent grove/household release proposal is superseded by the user's MineColonies
ownership decision. The immediate follow-up is regalia acquisition and a usable golem delivery plan.

Later court, gemcraft, ward, music and feast work should integrate with the existing colony and
magical systems rather than require a parallel settlement/reclamation loop.

## Things to avoid duplicating

- Another generic mana currency, spellbook school or profession XP bar.
- New generic storage, item couriers, farming pets or unrestricted teleportation solely for their names: existing installed systems already cover those jobs.
- Free flight from new jewelry: Botania already documents its mana-powered Flügel Tiara and the installed Ars jar includes a flight ritual. Cost and access still need to respect this pack's gates. [Official Lexica Botania](https://botaniamod.net/lexicon.html).
- A unique damage bonus for every collectible gem or a giant catalogue of mechanically interchangeable accessories.
- More structure families before the current inhabitants, discovery rewards and restoration interactions have useful work to do.
- Claiming older plans are complete because a jar or an attractive model exists.

## Inspection evidence

Read the installed mod filenames and selected jar entries; current KubeJS registrations and server scripts; FTB chapter files; current native citizen, fey home, ley node and golem entry-point implementations; current manifests; and the pack doctrine and design records.

Key sources: `INSTRUCTIONS.md`, `EXECUTION_STATE.md`, `BACKLOG.md`; `MAGIC_SYSTEMS.md`, `PROFESSIONS_AND_MMO.md`, `CURIOS_AND_PROFESSIONS.md`, `MINECOLONIES_ELVES.md`, `ELVEN_GOLEMS.md`, `LEY_LINE_CHANNEL_CORRIDORS.md`, `LIQUID_BIFROST.md`, `COMPENDIUM.md`; `tools/curios_manifest.json`; `ElvenCitizenEntity.java`, `FeyGardenGoal.java`, `LeyConduitNodeBlockEntity.java` and `AlfheimGolems.java`.

The direct source inspection takes precedence over outdated status headers. Jar class names establish that a native capability is shipped, not that its behavior, recipe reachability or interaction with Alfheim has been validated. No fresh boot, playthrough, balance pass or complete recipe reachability audit was performed for this inventory.
