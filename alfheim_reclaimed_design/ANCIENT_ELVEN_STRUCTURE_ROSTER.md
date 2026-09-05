# Ancient Elven Structure Roster — the remains of a civilization, not a ruin set

**Role:** authoritative master roster for the built environment of ancient Alfheim. This record expands the current sparse surface-landmark layer into the archaeological remains of a vast, advanced elven civilization whose institutions, districts, homes, infrastructure and social order failed slowly over time.

**Status:** `planned` 2026-09-05 — design-authoritative, not yet implemented. The existing thirty-two surface structures in `THE_SURFACE.md` remain valid as the first landmark layer, but they are explicitly **not** the complete civilizational footprint.

**Authority:** subordinate to `INSTRUCTIONS.md`; extends `THE_SURFACE.md`, `SPAWN_ZONE.md`, `THE_DEEP.md` and the existing terrain/detail acceptance doctrine. This document owns the civilization-scale structure roster, settlement hierarchy, district relationships, collapse chronology and remains/mortuary language.

---

## 1. Design thesis

Alfheim must not read as a wilderness with occasional fantasy ruins. It was once a **vast, technically and magically advanced elven civilization** with government, nobility, common households, archives, schools, hospitals, temples, workshops, agriculture, roads, ports, logistics, military institutions and burial customs. The player should repeatedly encounter evidence that enormous populations once lived here in organized communities.

The world did not disappear in one clean instant. It **declined slowly enough for institutions to react**. Roofs were patched. Streets were barricaded. Temples became shelters. Noble estates became ration depots. Libraries became emergency record offices. Guard halls became infirmaries. Cemeteries overflowed into trench burials. People kept working, governing, praying, treating the sick and burying the dead until the systems around them failed.

That chronology is the core of the visual language.

A structure succeeds when a player can infer all three of these things without reading a quest entry:

1. **What this place was for when Alfheim was healthy.**
2. **How its purpose changed during decline.**
3. **How it finally failed and what centuries of decay did afterward.**

The present thirty-two structures remain useful, but they currently function mostly as isolated landmarks. This roster adds the missing **civilization around the landmarks**.

---

## 2. The world must show settlement hierarchy

Not every ruin should be the same size or social importance. Ancient Alfheim needs a readable hierarchy of settlement forms.

| Settlement class | Intended read | Typical generated extent | Required composition |
|---|---|---:|---|
| **Imperial / High City Remnant** | A once-major urban center whose surviving fragments imply tens of thousands of inhabitants | 300–900+ blocks across as a district family | Multiple civic, noble, residential, sacred, logistical and mortuary anchors linked by roads/plazas |
| **Great City District** | One surviving quarter of a larger city | 160–400 blocks | 1–2 hero anchors + 4–12 subordinate buildings/fragments + circulation/infrastructure |
| **Provincial Town** | A self-contained community with administration, market, homes and a local shrine | 100–240 blocks | 1 civic anchor + 3–8 domestic/economic pieces + cemetery/utility traces |
| **Lineage Estate / Sacred Precinct** | A large institutional or noble complex outside dense urban fabric | 80–220 blocks | Main hall/temple + service wings + gardens + burial/utility pieces |
| **Village / Kin Cluster** | Small community, agricultural or craft-focused | 60–160 blocks | 3–8 homes/workspaces + shared hall/well/garden + paths |
| **Outpost / Waystation** | Remote infrastructure that proves the civilization reached everywhere | 24–100 blocks | 1 principal building + 1–4 support traces |
| **Fragment / Trace Field** | Archaeological residue between larger finds | 8–64 blocks | walls, foundations, graves, road fragments, collapsed utilities, debris fields |

**Generation rule:** do not implement the roster as seventy-two independent `random_spread` structure sets. The correct shape is **district anchors plus family members**, with jigsaw or equivalent controlled assembly so roads, houses, service buildings, graves and utilities appear as parts of the same historical place.

The existing thirty-two `THE_SURFACE.md` structures remain the discoverable landmark layer and can become anchors for these larger families where appropriate.

---

## 3. Scale classes and technical boundary

Minecraft's 48×48×48 structure-block save limit still binds individual template pieces. Large architecture therefore uses assemblies.

| Scale | Use | Approximate finished footprint |
|---|---|---:|
| **S0 — Trace** | graves, collapsed wall runs, shrines, debris, road segments | 8–24 blocks |
| **S1 — Building** | house, shop, small chapel, guard post | 20–48 blocks |
| **S2 — Complex** | manor, archive, hospice, guild hall | 48–96 blocks assembled |
| **S3 — Hero** | high assembly hall, elder lineage palace, great temple, major harbor work | 80–180+ blocks assembled |
| **S4 — District** | several structures with streets, courts, infrastructure and shared collapse history | 160–400+ blocks |
| **S5 — City remnant** | multiple districts that imply a metropolis beyond what still survives | 300–900+ blocks |

No single `.nbt` piece may exceed the proven template limits. Monumental scale comes from **joined geometry, layered pieces and district composition**, not illegal monoliths.

---

## 4. The five-stage decline chronology

Every major structure family should carry a historical state drawn from the same decline sequence. Hero structures should visibly contain at least **three** stages at once; ordinary buildings should show at least **two**.

### Stage I — High Alfheim

Original function, clean civic planning, intact magical infrastructure, ornament, water management, formal gardens, carved lineage symbols, functioning transport, ample storage and deliberate public space.

### Stage II — Strain

Patchwork repairs, reused materials, closed wings, deferred maintenance, failing mana conduits, temporary supports, ration accounting, reduced ornament and improvised utility changes.

### Stage III — Emergency order

Barricades, checkpoints, triage beds, ration counters, sealed doors, quarantine markings, guard stations, emergency kitchens, improvised sleeping areas, public notices, hurried graves and converted ceremonial rooms.

### Stage IV — Collapse

Bodies where people died, abandoned treatment rooms, broken defenses, unfinished burials, overturned carts, breached stores, burned records, abandoned tools, dead guards at posts, families sheltering in homes, mass graves dug by exhausted survivors.

### Stage V — Long decay

Roof loss, water ingress, root pressure, subsidence, salt damage, frost, fungal growth, silt, tree intrusion, secondary collapses, scavenger disturbance and partial later reuse.

**Random block removal is not a decline system.** Damage must have causes and direction.

---

## 5. Remains, death and mass-grave language

The dead are part of the setting's evidence, not decorative gore. Large communities should contain places where people **died in the spaces they were using**, as well as places where survivors attempted organized burial.

### 5.1 In-place remains

Use clustered remains to show the final function of a room or street: citizens beside ration counters, healers among ward beds, guards at barricades, scribes in archive rooms, families in shelter spaces, servants in estate service corridors, sailors in drowned dock works, mourners or attendants near funeral courts.

The visual implementation should prefer low-cost block-state and decorative evidence — bone blocks, skulls, scattered possessions, broken furniture, burial cloth analogues, armor/weapon residue where appropriate — over excessive persistent entities. Entities are reserved for places where the pose itself materially carries the story and performance remains acceptable.

### 5.2 Organized mass graves

Mass graves must read as **attempts to preserve order under impossible conditions**. They require more than a hole full of bones.

A proper mass-burial site may include:

- parallel trenches or layered burial pits;
- temporary marker rows, prayer stones or numbered stakes;
- corpse-cart tracks and unloading areas;
- abandoned digging tools and soil spoil;
- ash pits or failed cremation works;
- small officiant shelters or record tables;
- nearby guard/quarantine boundaries;
- the remains of diggers, clergy or wardens who died before the work was complete;
- a transition from early orderly rows to later rushed, crowded and unfinished interments.

### 5.3 Mortuary density bands

Not every ruin should be carpeted in bones. Density should tell the history.

| Band | Use |
|---|---|
| **Sparse** | remote homes, estates abandoned early, infrastructure sites |
| **Localized** | ordinary urban structures with one failed refuge/ward/barricade |
| **Heavy** | hospitals, ration halls, siege points, quarantine districts |
| **Catastrophic** | mass graves, last-muster grounds, sealed shelters, terminal collapse sites |

The contrast makes catastrophic sites matter.

---

# 6. Master roster — 72 archetypes in 12 systems

The roster below is the required civilization vocabulary. Names are working canonical archetype names; individual generated structures may receive region- or lineage-specific proper names.

## 6.1 Civic government and administration

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **High Assembly Hall** | S3 | Major legislative and diplomatic chamber | galleries converted to shelter, barricaded speaker floor, bodies among benches, cracked ceremonial roof |
| **Provincial Council House** | S2 | Town/regional government | ration ledgers, sealed offices, emergency maps, improvised guard desks |
| **Record House** | S2 | Civil registers, taxes, land and population records | shelves stripped for fuel, burned ledgers, emergency death rolls, collapsed stacks |
| **Magisterial Court** | S2 | Law, petitions, dispute resolution | holding rooms converted to quarantine, broken judgment dais, dead clerks/guards |
| **Census & Measure Hall** | S1–S2 | Standard weights, survey, census and public accounting | stockpiled measures, abandoned population boards, emergency ration tallies |
| **District Forum** | S3–S4 | Public plaza with offices and meeting courts | market/shelter conversion, barricaded entrances, public notices, clustered civilian remains |

## 6.2 Elder lineages and noble society

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Hall of the Elder Lineage** | S3 | Dynastic seat with audience hall and ancestral identity | sealed family wings, rationed retainers, dead household in ceremonial rooms, lineage panels surviving roof loss |
| **Lineage Manor Court** | S2–S3 | Provincial noble household | servant passages, kitchens, guard rooms, family shrine, emergency stores, partial defensive conversion |
| **Ancestral Gallery** | S2 | Portraits, genealogy, relics and legal claims | vandalized/removed relics, broken display niches, untouched stone genealogies |
| **Retainer House** | S1–S2 | Residence and offices for household officials | crowded refugee use, ration cots, abandoned account books and service gear |
| **Noble Garden Pavilion** | S1–S2 | Formal retreat, diplomacy, poetry and private ceremony | overgrown waterworks, collapsed trellis roofs, emergency graves in ornamental beds |
| **Lineage Crypt & Tomb Garden** | S2–S3 | Multi-generation noble burial precinct | later overcrowding, breached vaults, emergency common burials intruding on formal tombs |

## 6.3 Residential and community life

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Common Row Houses** | S1 family | Dense ordinary urban housing | shared walls, broken upper floors, household remains, improvised roof repairs |
| **Courtyard Home** | S1–S2 | Multi-room family residence around a garden/light court | garden used for food, water storage, later burials, sealed sick room |
| **Extended Kin Hall** | S2 | Large multigenerational household | sleeping galleries, family workrooms, refuge crowding, several generations represented in possessions |
| **Artisan House-Shop** | S1–S2 | Residence plus workshop/storefront | unfinished work, tools abandoned at benches, shop converted to ration exchange |
| **Guild Residence** | S2 | Skilled workers' communal housing and meeting space | bunk conversion, emergency production, profession insignia, partial fire damage |
| **Neighborhood Common Hall** | S2 | Meals, meetings, celebrations and local coordination | public kitchen, ration queue, barricades, concentrated civilian remains |

## 6.4 Scholarship, magic and advanced knowledge

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Lore College** | S3–S4 | Higher learning, lecture halls and scholar residence | lecture rooms converted to planning cells, damaged mana systems, abandoned experiments |
| **Archive Cloister** | S2–S3 | Protected manuscripts and long-term records | humidity/fire damage, sealed vaults, emergency copying rooms, dead scribes |
| **Astral Conservatory** | S2–S3 | Star observation, calendrics and planar study | collapsed dome, frozen mechanisms, last observations left incomplete |
| **Runic Engineering Hall** | S2–S3 | Applied magical infrastructure design | broken test rigs, shattered conduits, containment partitions, repair prototypes |
| **Botanical Research Garden** | S2–S4 | Managed magical plant research | greenhouses gone feral, failed irrigation, experimental beds overtaking paths |
| **Philosopher's Court** | S2 | Debate, teaching and civic scholarship | discussion courts repurposed for public instruction/coordination, abandoned notes and memorials |

## 6.5 Sacred life and formal ritual

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Great Temple Court** | S3–S4 | Major urban ritual center | nave/court used as shelter, side chapels as infirmaries, sacred stores exhausted |
| **Shrine of Root and Star** | S1–S2 | Neighborhood devotional site | votive clutter from crisis period, weathered offerings, small refuge traces |
| **Ancestor Reflection Pool** | S1–S2 | Memorial water garden | silted basin, emergency names cut into surrounding stone, later grave use |
| **Pilgrim Chapel** | S1 | Roadside worship and rest | abandoned travel packs, emergency bedding, collapsed roof and overgrowth |
| **Rite House** | S2 | Weddings, naming, funerary and civic rites | funeral function overwhelms other uses, stacked biers, unfinished records |
| **Temple Treasury & Reliquary** | S1–S2 | Safekeeping of sacred objects and offerings | emptied outer stores, sealed inner chamber, evidence of controlled redistribution during decline |

## 6.6 Relief, medicine, quarantine and mass death

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Hospice Hall** | S2–S3 | Long-term care and healing | wards overcrowded, side rooms used as morgues, broken cleansing apparatus |
| **Healer Cloister** | S2 | Medical teaching, apothecary and treatment | drying racks, preparation rooms, exhausted stores, dead staff in workspaces |
| **Plague Triage Court** | S2–S3 | Emergency sorting and treatment | divided patient lanes, privacy screens, burned bedding, high remains density |
| **Quarantine Ring** | S3–S4 | Controlled isolation district | perimeter wards, supply gates, watch posts, mass graves outside the boundary |
| **Public Bread & Ration Hall** | S2–S3 | Emergency food distribution | empty bins, queue rails, serving counters, crush/barricade evidence, many civilian dead |
| **Mass Grave of the Last Order** | S2–S4 | Organized emergency burial | ordered early trenches grading into hurried/unfilled later pits, digger camps and corpse-cart approaches |

## 6.7 Military, wardens and civil order

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Gate Barracks** | S2 | City-entry defense and customs support | reinforced doors, refugee screening, dead guards at final posts |
| **Warden Tower** | S1–S2 | Local observation and patrol control | failed signal equipment, abandoned watch logs, collapsed upper platform |
| **Watch Captain House** | S1–S2 | Command office and residence | maps, equipment racks, emergency orders, defended stairwell |
| **Last Muster Ground** | S2–S4 | Assembly for militia/wardens | weapon issue points, roll-call markers, casualty collection and nearby burial trenches |
| **Border Keep** | S3 | Regional military stronghold | layered repairs, sealed magazines, breach points, retreat through inner courts |
| **Discipline Yard & Guard Court** | S2 | Training, detention and civic policing | converted to refugee camp, temporary cells, ration and triage traces |

## 6.8 Industry, production and logistics

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Mana Mill** | S2–S3 | Magical power conversion and distribution | fractured conduits, bypass repairs, emergency local feeds, burned regulator chambers |
| **Resonance Foundry** | S2–S3 | Advanced material shaping | half-finished work, cracked furnaces/ritual beds, salvage stripping |
| **Stone-Song Quarry** | S3–S4 | Monumental stone extraction | terraced cuts, cranes/headframes, worker shelters, richer discovery value without progression skips |
| **Dreamwood Shaping Court** | S2–S3 | Timber preparation and precision construction | curing racks, fallen frames, unfinished structural members, later use as fuel depot |
| **Glass Bloom House** | S2 | Magical glass/crystal production | broken kilns/growth beds, dangerous shards, patched roof vents |
| **Public Storehouse & Distribution Depot** | S2–S3 | Bulk civic inventory and logistics | partitioned ration stores, looted outer bays, sealed emergency reserve, cart debris |

## 6.9 Agriculture, food and water systems

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Terraced Orchard Complex** | S3–S4 | Long-lived food production | retaining-wall failure, emergency vegetable plots among ornamental fruit rows |
| **Water Garden** | S2–S4 | irrigation, food, cooling and civic landscape | clogged channels, burst walls, silted basins, later drinking-water use |
| **Seed Vault** | S1–S2 | preserved crop and magical flora genetics | sealed chambers, inventory niches, desperate late withdrawals |
| **Fungus Conservatory** | S2–S3 | managed subterranean/covered food cultivation | runaway growth, collapsed humidity systems, worker shelters |
| **Granary of Living Roots** | S2–S3 | protected staple storage | empty bins, pest damage, emergency ration marks, guarded inner reserve |
| **Pollinator Sanctuary** | S2 | controlled ecological support | broken glass/screens, overgrown nesting gardens, abandoned keeper station |

## 6.10 Roads, bridges, trade and inland transport

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Processional Avenue** | S4 linear | ceremonial/civic arterial road | checkpoints, abandoned carts, grave pits in verge, trees breaking paving |
| **Caravan Court** | S2–S3 | travelers, freight and animal/construct staging | sealed gates, stranded cargo, sleeping halls turned refugee center |
| **Custom House** | S2 | tariffs, inspection and manifests | confiscated stores, emergency movement permits, abandoned counters |
| **Bridge Gate** | S2–S3 | controlled crossing and road defense | collapsed span, defended gatehouse, last evacuation traces |
| **Wayshrine & Rest Station** | S1 | long-distance travel support | small shelter use, memorial stones, weathered road markers |
| **Freight Exchange Yard** | S2–S4 | inland transshipment and warehousing | overturned carts, broken cranes, inventory spill, scavenged buildings |

## 6.11 Maritime, lake and shore civilization

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Harbor Exchange Hall** | S3 | trade administration and bonded goods | flooded lower stores, broken counters, evacuation records, roof collapse |
| **Harbormaster House** | S1–S2 | traffic control, berths and manifests | last ship lists, signal gear, partial inundation |
| **Wavebreak Pier & Seawall** | S3–S4 linear | coastal protection and docking | breached segments, storm-scoured foundations, drowned stairs |
| **Tide Temple** | S2–S3 | maritime ritual and navigation blessing | salt damage, flooded crypt/undercroft, emergency survivor use |
| **Signal Lighthouse Spire** | S2–S3 | coastal navigation and long-range signaling | shattered light chamber, broken stairs, storm damage, keeper quarters |
| **Half-Sunken Drydock** | S3–S4 | vessel construction and repair | collapsed gates, silted basin, unfinished hull fragments, submerged workshops |

## 6.12 Frontier, wilderness and remote stewardship

| Archetype | Scale | Original role | Decline / ruin signature |
|---|---:|---|---|
| **Surveyor's Tower** | S1–S2 | mapping, resource and land stewardship | weather instruments, map room collapse, isolated dead staff |
| **Forest Waystation** | S1–S2 | patrol and traveler support | overgrown yard, abandoned stores, small burial plot |
| **Green Noble Hunting Lodge** | S2–S3 | elite rural estate and stewardship center | family retreat converted to refuge, servants/commoners crowded into service wings |
| **Wild Ward Shrine** | S1–S2 | maintain magical boundaries and dangerous sites | failed ward stones, repair camps, local contamination evidence |
| **Moon Pool Sanctuary** | S2 | remote ritual/ecological site | cracked waterworks, overgrown paths, abandoned keeper cells |
| **Outlying Retreat Hall** | S2–S3 | scholarly, noble or sacred seclusion | sealed archives, food gardens, evidence of prolonged isolated survival |

---

## 7. District assemblies — structures must imply systems

Individual archetypes become convincing when they appear in historical relationships. The following district families are canonical targets.

### 7.1 Elder Lineage Precinct

Required core: Hall of the Elder Lineage + Retainer House + Lineage Crypt/Tomb Garden.

Optional satellites: Noble Garden Pavilion, servant housing, guard court, archive room, small shrine, stable/freight court, kitchen/service block, private water garden.

**Collapse story:** aristocratic household initially shelters dependents and retainers, converts ceremonial spaces into stores and wards, seals parts of the estate, then dies or disperses. Formal tomb grounds later receive hurried common burials.

### 7.2 Civic Center

Required core: High Assembly Hall or District Forum + Record House + Provincial Council House.

Optional satellites: market court, census hall, guard post, public kitchen, archive annex, processional avenue.

**Collapse story:** government continues functioning visibly into Stage III. Public architecture accumulates emergency functions instead of immediately becoming abandoned scenery.

### 7.3 Common Residential Quarter

Required core: 4–12 mixed homes + Neighborhood Common Hall.

Optional satellites: artisan shop-houses, shared garden, water point, small shrine, refuse/service alley, tiny burial court.

**Collapse story:** households adapt locally, combine food, shelter together, barricade alleys, bury some dead in gardens, and eventually leave or die in place.

### 7.4 Scholastic Quarter

Required core: Lore College + Archive Cloister or Astral Conservatory.

Optional satellites: student housing, philosopher court, botanical garden, runic engineering workshop, observatory tower.

**Collapse story:** scholars redirect expertise toward repair, forecasting, containment and record preservation; later spaces show unfinished last projects.

### 7.5 Relief / Quarantine District

Required core: Plague Triage Court or Hospice Hall + Quarantine Ring + Mass Grave of the Last Order.

Optional satellites: public ration hall, healer cloister, guard posts, corpse-cart way, ash pits, sealed storage.

**Collapse story:** one of the strongest terminal-history families. Order degrades visibly from measured treatment and burial into overwhelmed facilities and unfinished work.

### 7.6 Harbor Complex

Required core: Harbor Exchange Hall + Wavebreak/Seawall + Harbormaster House.

Optional satellites: drydock, bonded storehouses, lighthouse, tide temple, freight yards, worker housing.

**Collapse story:** trade diminishes, berths empty, lower infrastructure floods, warehouses become relief depots, storms finish what abandonment began.

### 7.7 Production District

Required core: one major production archetype + public storehouse/distribution depot.

Optional satellites: worker housing, freight yard, water system, guard post, small guild hall.

**Collapse story:** maintenance and salvage are explicit. Machinery should show bypasses, stripped components, repair staging and eventually abandonment.

### 7.8 Agricultural Estate / Food Belt

Required core: orchard, water garden or granary + worker/keeper housing.

Optional satellites: seed vault, pollinator sanctuary, fungus conservatory, freight court, shrine.

**Collapse story:** ornamental/optimized production becomes survival agriculture; terraces and irrigation are repaired crudely before long-term system failure.

---

## 8. Architectural evidence of an advanced elven society

The architecture must not become generic medieval buildings with elven blocks substituted into the palette. Across the roster, surviving ruins should repeatedly show:

- integrated mana/source conduits built into walls and floors;
- service voids and maintenance access behind ceremonial surfaces;
- light wells, passive magical illumination infrastructure and crystal sockets;
- advanced water capture, filtration, drainage and controlled irrigation;
- modular structural frames designed for very long service lives;
- magical transport or loading interfaces in industrial/logistical sites;
- acoustic/runic signaling systems in civic and military buildings;
- climate-managed botanical spaces;
- durable public paving and retaining systems;
- monumental spans and terraces that require obvious engineering logic;
- purpose-built accessibility and circulation rather than arbitrary stairs;
- standardized civic markers, district signs, lineage seals and wayfinding.

The society can be graceful and organic without being technologically naive.

---

## 9. Terrain incorporation remains mandatory

Every new archetype inherits the terrain acceptance gate from `THE_SURFACE.md`.

A structure that clips into a cliff, hangs in open air, ignores a shoreline or floats above terrain has failed regardless of how good the architecture is.

Districts should preferentially use the terrain as part of their historical logic:

- noble precincts terrace hillsides;
- civic centers occupy broad engineered platforms;
- quarries and foundries cut into slopes;
- residential districts step with terrain and use retaining walls;
- harbors descend through deliberate waterline architecture;
- agricultural districts follow contour and irrigation logic;
- frontier structures deliberately exploit ridges, passes or clearings.

Where local relief is unsuitable, relocate or generate authored foundations/substructures. Do not rely on `beard_thin` as proof of visual integration.

---

## 10. Loot and discovery value

The structures are primarily evidence of civilization, but exploration must still pay.

Loot should follow historical function:

- noble halls: lineage relics, decorative valuables, records, limited household stores;
- archives/colleges: books, maps, knowledge items, magical components appropriate to progression;
- workshops/quarries: materials, half-finished mundane stock, tools and exposed resource faces;
- relief sites: exhausted medical stores with occasional surviving supplies;
- military sites: damaged equipment, maps, maintenance stores rather than free end-tier weapons;
- agricultural sites: seeds, food-preservation remnants, renewable crop leads;
- ports/logistics: mixed trade cargo and manifests;
- homes: low-value personal goods and small caches.

Rare finds must be materially worthwhile without bypassing era gates. A site can be rich in **quantity, variety, information and convenience** without handing out progression-locked materials.

---

## 11. Production sequencing

This roster is too large to build all at once. Implementation should proceed by families that immediately improve world coherence.

### Wave 1 — prove inhabited civilization

1. Common Residential Quarter family.
2. Elder Lineage Precinct family.
3. Civic Center family.
4. Relief/Quarantine + Mass Grave family.

These four make the setting's social scale visible fastest.

### Wave 2 — prove advanced systems

5. Scholastic Quarter.
6. Production District.
7. Agricultural/Food Belt.
8. Roads/Trade support pieces.

### Wave 3 — deepen regional identity

9. Harbor Complex.
10. Sacred precincts.
11. Military/warden complexes.
12. Frontier stewardship sites.

Each wave must include terrain-fit review, collapse chronology, remains placement, discovery-value tuning and fresh-world placement before the next family is admitted.

---

## 12. Acceptance standard

A new structure family is not accepted because the NBT places or `/locate` finds it.

For production admission, representative generated sites must demonstrate:

1. a clearly readable original purpose;
2. at least two visible chronological layers of decline, three for hero structures;
3. credible connection to neighboring structures/infrastructure when part of a district;
4. terrain incorporation that looks authored rather than stamped;
5. human/elven-scale residue showing actual occupation;
6. remains/burial evidence appropriate to the site's history without flattening every ruin into identical bone clutter;
7. advanced elven engineering/magical infrastructure appropriate to function;
8. coherent long-term decay after abandonment;
9. discovery value appropriate to rarity and role;
10. no progression bypass;
11. no obvious modular seams or disconnected circulation;
12. acceptable runtime/worldgen performance.

**Final visual target:** the player should be able to stand on a ruined avenue, look across a collapsed noble precinct, a roofless public hall, common homes, a broken water system and distant burial trenches, and understand that this was once a populated, ordered world whose people tried for a long time to keep it alive.
