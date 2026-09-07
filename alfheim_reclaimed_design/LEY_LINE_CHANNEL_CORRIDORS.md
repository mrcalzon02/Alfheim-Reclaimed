# Ley Line Channel Corridor Network

**Role:** Authoritative concept and implementation template for Alfheim's underground ley line corridor structure, its six-direction conduit blocks, beacon-pyramid transmission network, node auras, and custom status effects.

**Status:** Design accepted for staged development. Phase 1 registry foundation is in progress.

**Authority:** Subordinate to `INSTRUCTIONS.md`. Extends `THE_DEEP.md`, `DEEPWORKS.md`, and `LIVINGROCK_LIBRARY.md` without replacing the Quarries, Tombs, or Faultworks.

## Current implementation status

The first Phase 1 slice is present in the pack:

- `kubejs/startup_scripts/23_leyline_effects.js` registers `Leyline Presence` and all six primary MMO resonances with stable IDs, display names, beneficial classification, and effect colours.
- `kubejs/assets/alfheim/textures/mob_effect/` contains a distinct 18-by-18 icon for every registered effect.
- `tools/gen_leyline_effect_icons.py` owns deterministic regeneration of those icons.
- MMO bonuses remain intentionally inactive until Mine and Slash and Ars Nouveau integration hooks are proven. Registration must not be mistaken for completed gameplay behavior.
- The next runtime gate is a full client restart followed by effect-registry and icon verification. Transmission, aura refresh, and amplifier behavior begin after that gate passes.

## Design summary

The Ley Line Channel Corridor Network replaces abandoned mine tunnels with ancient elven mana infrastructure. A Minecraft jigsaw assembly creates long, branching, multi-level networks of maintenance corridors, relay nodes, ladder exchanges, distributor hubs, terminal chambers, and central pyramid chambers.

The defining image is a beacon-like ley beam suspended through the exact middle of a five-block-wide by five-block-high corridor. Players travel in two-block maintenance lanes on either side. Custom Ley Conduit Nodes project along all six cardinal directions. Air and approved glass transmit the projection; ordinary blocks stop it. Architecture masks unused faces, producing straights, bends, junctions, vertical links, and hubs from the same six-direction rule.

A valid beacon pyramid injects its effects into the network. Every connected node receives the payload, applies an aura, and retransmits the complete signal. Transmission distance resets at every relay. Pyramid tier controls the radius around each node and the maximum distance to the next node.

Every powered node also applies `Leyline Presence`, a passive indicator that the player is inside an active field. Focus rings made from Alfheim materials add pack-specific MMO and utility effects to the vanilla beacon payload.

Central pyramid chambers contain a bay for a complete four-tier beacon pyramid. Generated chambers never provide a working pyramid for free. Their bays are empty, unfinished, or obstructed by inert obsidian and magmatic decay that the player must excavate and rebuild.

## Fixed design decisions

- The normal corridor has a five-by-five clear interior.
- The ley beam occupies the exact horizontal and vertical center.
- A one-block structural shell produces a normal seven-by-seven outer envelope.
- Ley Conduit Nodes project north, south, east, west, up, and down.
- Air and approved glass transmit the beam; ordinary blocks stop it.
- Architecture blocks unused directions instead of requiring a different block for every shape.
- Every powered relay retransmits the received signal at full tier.
- Transmission range resets at every node.
- Every powered node applies a local aura and `Leyline Presence`.
- Pyramid tier determines node-to-node range and aura radius.
- A four-block focus ring selects one pack-specific primary resonance.
- Tier four may carry one additional utility resonance.
- Generated structures contain no complete active pyramid and grant no free beacon effects.
- Jigsaw pools are staged so branches terminate before the hard depth limit.

## Player experience

The player enters a broad, dark maintenance passage split by a luminous central line. A narrow inner strand identifies the transmitted beacon effect. A second spiral or pulse identifies the Alfheim resonance selected at the injector. Glass focusing rings catch and tint the beam. Stone mounting collars appear at regular intervals, while solid relay nodes force the player into the side lanes.

Long arterial corridors provide orientation. Hubs interrupt them with larger radial silhouettes. Short spokes lead to resonators, reservoirs, damaged receivers, pyramid chambers, quarry interfaces, tomb seals, or Faultwork breaches. Vertical exchanges wrap ladders and landings around upright beam segments.

The network begins as archaeology rather than infrastructure. Most nodes are dormant or disconnected. Repairing relays and constructing a beacon pyramid turns an explored ruin into a persistent traversal and support network.

## Corridor geometry

### Standard cross section

| Element | Dimension | Rule |
|---|---:|---|
| Clear interior | 5 wide by 5 high | Usable corridor volume |
| Structural envelope | 7 wide by 7 high | Floor, ceiling, and side shells outside the clear interior |
| Central beam axis | center width and center height | Two clear blocks between beam and each wall, floor, and ceiling |
| Maintenance lanes | 2 wide on each side | Solid relays may be passed on either side |
| Horizontal module | 8 blocks | Straights use 8, 16, or 24 block lengths |
| Deck interval | 8 blocks | Vertical pieces move between repeatable floor datums |
| Connection aperture | 5 wide by 5 high | Every horizontal jigsaw throat uses the same opening |

With the corridor floor at `Y 0`, the clear interior occupies `Y 1` through `Y 5`. The beam axis is at `Y 3`. The outer ceiling is at `Y 6`. Aligned horizontal jigsaw joints preserve both the floor and beam datums.

### Center channel treatment

- The projection is non-solid and may be crossed.
- Solid relay cores appear at turns, junctions, transitions, and deliberate intervals.
- Glass focusing rings or partial cages frame the beam without continuously enclosing it.
- Navigation happens primarily in the two side lanes.
- Detail may obstruct one side lane at a time, but both lanes require an authored alternate route if blocked.
- Structural ribs cross the ceiling and floor at four-block or eight-block intervals.

## Custom conduit system

### Ley Conduit Node

The principal custom block is `alfheim:ley_conduit_node`, a block entity with one potential output on every cardinal face.

The node:

1. Discovers the first compatible node visible along each exposed axis.
2. Renders a beacon-like projection to the obstruction or receiving node.
3. Receives and retransmits a beacon signal payload.
4. Applies the received effects inside its aura radius.

| Property | Values | Purpose |
|---|---|---|
| `active` | true or false | Projection and aura activity |
| `condition` | intact, dormant, unstable, fractured | Visual and audio presentation |
| `alignment` | neutral, fire, water, earth, air, shadow, light | Base ley colour |
| `role` | relay, junction, hub, injector, receiver | Interaction and presentation |

Injector and receiver blocks may later be separated if their interactions diverge, but they should share one network and renderer implementation.

### Direction masking

Every active node attempts all six directions. Structure geometry determines usable faces.

- A straight exposes two opposite faces.
- A bend exposes two perpendicular faces.
- A T junction exposes three horizontal faces.
- A crossroad exposes four horizontal faces.
- A vertical exchange exposes up, down, and selected horizontal faces.
- A six-way hub may expose every face.
- Opaque mounting collars immediately stop unwanted rays.

Removing a casing block can expose a direction; replacing it can shut that direction down.

### Beam transparency

```text
air, cave_air, void_air                          transmit
#alfheim:ley_beam_transparent                    transmit
ordinary solid blocks                           block
unlisted fluids, leaves, slabs, and machinery   block
another Ley Conduit Node                        receive and retransmit
```

The transparent tag initially includes vanilla glass, stained glass, glass panes, and all six Mana-glass variants. Glass may tint the broad outer projection, while payload strands retain their effect colours.

### Beam rendering

- A narrow, bright inner core establishes direction.
- A wider, low-opacity sheath creates haze.
- Slow texture movement travels from transmitter to receiver.
- A receiving node pulses when its payload changes.
- The beam fades at its tier limit when no receiver is in range.
- The beam ends sharply against an opaque block.
- Connected nodes must not create doubled brightness or z-fighting.

| Tier | Beam presentation |
|---|---|
| 1 | Thin payload strand and soft node halo |
| 2 | Brighter strand with a slow relay pulse |
| 3 | Thicker strand with a restrained spiral accent |
| 4 | Layered transmission with a second strand for a secondary effect |

## Beacon injection and retransmission

### Source assembly

A working source contains:

1. A valid vanilla beacon pyramid.
2. A vanilla beacon above the pyramid.
3. An unobstructed vertical beacon path.
4. A matching primary focus ring around that path.
5. A Ley Conduit Node in injector role aligned with the corridor beam.
6. An optional secondary utility focus ring for tier four.

The injector remains transparent to vanilla beacon validation and reads the real pyramid tier and selected effects.

### Per node range

Every receiving node retransmits at the complete tier received. Distance resets at that node.

| Pyramid tier | Maximum distance to next node | Aura radius around each node | Payload |
|---|---:|---:|---|
| 1 | 32 blocks | 20 blocks | Primary beacon effect and primary Alfheim resonance |
| 2 | 64 blocks | 30 blocks | Primary beacon effect and primary Alfheim resonance |
| 3 | 128 blocks | 40 blocks | Primary beacon effect and stronger primary resonance |
| 4 | 256 blocks | 50 blocks | Primary and secondary beacon effects plus primary and utility resonance |

A relayed chain may carry a signal across the complete loaded network. Branching does not reduce strength. A relay never amplifies tier.

### Signal identity and loops

Every payload carries a source identity made from dimension, beacon position, and signal revision. A node processes each source revision once, preventing circular pieces from retransmitting the same update forever.

When sources overlap:

- Identical effects use the strongest amplifier.
- Different vanilla beacon effects follow normal Minecraft coexistence rules.
- Only one primary Alfheim combat resonance affects a player at a time.
- Two weak sources never combine into a higher tier.
- An optional utility resonance remains attached to its tier-four source.

### Chunk behaviour

- The network does not force-load chunks initially.
- Nodes scan and retransmit only through loaded chunks.
- Cached payloads expire after their source or upstream relay becomes unavailable.
- A node cannot provide permanent effects from an unloaded or destroyed source.
- A costly player-built Ley Anchor may be considered in a later era.

## Status effects

### Leyline Presence

`alfheim:leyline_presence` is always applied by a powered node.

- It is an indicator with no statistical bonus.
- Its amplifier displays received pyramid tier I through IV.
- It uses a neutral-beneficial classification and a six-direction node icon.
- Ambient particles are disabled.
- Overlapping fields display the highest tier.
- Losing it indicates that the player has left powered coverage.

A practical first pass is a five-second effect refreshed every two seconds.

### Complete payload

Each node aura can apply:

1. `Leyline Presence`.
2. Valid primary and secondary vanilla beacon effects.
3. One primary Alfheim resonance and an optional tier-four utility resonance.

Effects originate around nodes rather than across every beam segment. Overlapping auras refresh smoothly and do not stack duplicate amplifiers.

## Focus rings and Alfheim effects

### Focus ring rule

A focus ring contains four matching blocks at the cardinal positions around the injector's vertical beam path. The center remains open.

- Four matching valid blocks select an effect.
- An incomplete or mixed ring selects no Alfheim effect.
- The ring selects the signal but does not generate power.
- Replacing it updates the propagated payload and visible strands.
- Tiers one through three accept one primary ring.
- Tier four may accept one additional utility ring.

Decorative materials may be inexpensive selectors because the beacon pyramid supplies the power and progression cost.

### Primary MMO resonances

| Focus material | Effect ID | Display name | Target role |
|---|---|---|---|
| Fire Mana-glass | `ember_current` | Ember Current | Weapon damage with modest fire protection |
| Water Mana-glass | `tidal_recovery` | Tidal Recovery | Health, healing received, and resource recovery |
| Earth Mana-glass | `rootguard` | Rootguard | Armor and knockback resistance |
| Air Mana-glass | `gale_tempo` | Gale Tempo | Movement, attack speed, and casting tempo |
| Shadow Mana-glass | `dusk_precision` | Dusk Precision | Critical chance and critical damage |
| Light Mana-glass | `dawn_clarity` | Dawn Clarity | Spell power, cooldown recovery, and Ars source regeneration |

| Tier | Typical percentage-scale target |
|---|---:|
| 1 | about 4 percent |
| 2 | about 7 percent |
| 3 | about 10 percent |
| 4 | about 13 percent |

Armor, healing, regeneration, and knockback resistance require effect-specific values. Mine and Slash and Ars Nouveau integration must use proven hooks; unavailable statistics must not be silently faked.

### Utility resonances

| Focus material | Effect ID | Display name | Target function |
|---|---|---|---|
| Leyline Livingrock | `ley_attunement` | Ley Attunement | Magical resource recovery and active-node feedback |
| Starfleck Livingrock | `astral_wayfinding` | Astral Wayfinding | Night vision and direction cues toward powered nodes |
| Magmatic Livingrock | `furnace_ward` | Furnace Ward | Fire resistance and reduced environmental heat damage |
| Tide Livingrock | `deep_current` | Deep Current | Water breathing and improved swimming |
| Frost Livingrock | `winter_step` | Winter Step | Reduced fall damage and reliable footing on ice |
| Moss or Rootbound Livingrock | `verdant_renewal` | Verdant Renewal | Natural recovery and reduced hunger drain |
| Gloam Livingrock | `veiled_passage` | Veiled Passage | Reduced hostile detection range |
| Amethyst Livingrock | `resonant_mind` | Resonant Mind | Skill-resource or experience recovery after balance review |

No focus effect may bypass an era gate, create an alternate resource economy, provide ore sight through walls, or substitute for progression equipment.

## Central pyramid chamber

### Chamber role

The Central Confluence Chamber is both the jigsaw start hub and the reconstruction site. It explains that the ancient network expected a beacon-like source while leaving the investment to the player.

Use an envelope around 17 blocks wide, 17 blocks long, and at least 13 blocks tall including the sunken bay. A four-block circulation walkway surrounds the maximum nine-by-nine footprint.

### Sunken maximum tier bay

The beacon and injector stay at a fixed height while the pyramid grows downward beneath the chamber floor.

Using the corridor floor as `Y 0`:

| Level | Construction | Purpose |
|---|---|---|
| `Y 3` | Ley Conduit Injector | Exact horizontal corridor beam datum |
| `Y 2` | Open beam path and primary focus ring | Selects primary Alfheim resonance |
| `Y 1` | Vanilla beacon | Reads completed layers beneath it |
| `Y 0` | 3 by 3 pyramid layer | Tier one and top layer of larger pyramids |
| `Y -1` | 5 by 5 pyramid layer | Tier two |
| `Y -2` | 7 by 7 pyramid layer | Tier three |
| `Y -3` | 9 by 9 pyramid layer | Tier four |

Players upgrade downward without moving the beacon, focus ring, injector, or horizontal connections.

### Generated chamber states

The bay never generates a valid pyramid or valuable pyramid blocks.

| State | Starting target | Treatment |
|---|---:|---|
| Empty foundation | 45 percent | Complete stepped excavation with alignment marks |
| Unfinished construction | 20 percent | Partial inert supports showing layer geometry |
| Obsidian decay | 20 percent | Obsidian or Obsidian Livingrock rubble in the bay |
| Magmatic collapse | 15 percent | Magmatic Livingrock, Cracked Livingrock, and slag in lower layers |

Remnants are removable obstructions, not beacon-base substitutes. The footprint contains no loose lava. Heat may appear behind glass, beneath sealed grates, or outside the construction volume.

### Build readability

- Every layer has a carved outline.
- The nine-by-nine lowest footprint remains legible through rubble.
- Cardinal stairs descend beside the bay without occupying valid cells.
- The beacon position is marked beneath the dormant injector.
- Focus-ring sockets differ visibly from pyramid cells.
- The tier-four utility-ring location is visible but inactive until the full pyramid is recognized.
- The vertical beam path remains clear or can be cleared without dismantling the chamber shell.

## Network topology

### Hierarchy

1. A Central Confluence Chamber starts the structure and contains the pyramid bay.
2. Two opposed arterial trunks leave the chamber.
3. Arterials emit spokes, bends, relay rooms, and vertical transitions.
4. Spokes terminate in nodes, interfaces, damaged receivers, or sealed ends.
5. Vertical exchanges establish two to four local decks.
6. Authored loop cassettes create local cycles without reconnecting independent jigsaw branches.

### Relay spacing and tier progression

- Intact arterial relays sit 24 to 32 blocks apart for tier one.
- Bends, junctions, and vertical exchanges always contain a relay.
- Tier-two damage gaps may require 33 to 64 blocks.
- Major cavern or fracture crossings may require 65 to 128 blocks.
- Exceptional regional links may require 129 to 256 blocks and tier four.
- Missing or blocked relays remain repairable.

Higher tiers reconnect increasingly damaged parts of the network without imposing a cumulative range limit.

## Piece library

### Arterial pieces

| Piece | Suggested envelope | Relay treatment |
|---|---:|---|
| Short straight | 7 by 7 by 8 | No mandatory relay unless resolving a gap |
| Standard straight | 7 by 7 by 16 | Focusing ring and optional midpoint relay |
| Long straight | 7 by 7 by 24 | Mandatory relay or deliberate higher-tier gap |
| Quarter bend | 11 by 7 by 11 | Solid corner relay |
| Offset bend | 15 by 7 by 11 | Relay at offset center |
| Single-spoke junction | 15 by 9 by 15 | Three-face distributor relay |

### Hub and node pieces

| Piece | Suggested envelope | Function |
|---|---:|---|
| Central Confluence Chamber | 17 by 13 by 17 | Start hub, pyramid bay, and injector site |
| Distributor wheel | 23 by 11 by 23 | Radial relay with three to six directions |
| Splitter gallery | 15 by 9 by 23 | Arterial with side spokes |
| Vertical exchange | 15 by 17 by 15 | Ladder landings around an up-down relay |
| Loop cassette | 23 by 9 by 31 | Two parallel internal corridors joined in one template |
| Resonator node | 13 by 9 by 17 | Crystal ribs and focal receiver |
| Mana reservoir | 15 by 11 by 19 | Glass cells and overflow channels |
| Fracture node | 17 by 13 by 21 | Vitrified tear and Faultwork interface |
| Sealed terminal | 9 by 7 by 9 | Intentional endpoint |

All templates remain below the 48-block-per-axis piece limit.

### Vertical pieces

- **Ladder stack:** protected ladders and landings around a vertical beam.
- **Offset riser:** stairs around a relay, changing height and position.
- **Broken drop:** partial ladders and a repairable missing relay.
- **Reservoir climb:** a wider vertical node surrounded by glass cells and controlled water.

Vertical pieces return to a horizontal pool at a landing and do not emit unrestricted shaft chains.

## Jigsaw generation model

### Staged pools

| Pool | Purpose | Allowed successors |
|---|---|---|
| `leyline/start` | Central Confluence variants | `arterial_1` and optional `vertical_1` |
| `arterial_1` to `arterial_3` | Establish long trunks | next arterial stage and low-weight junction |
| `arterial_4` to `arterial_5` | Thin and bend trunks | next stage, spoke, hub, interface, or terminal |
| `arterial_end` | Resolve trunk | sealed terminal or buried break |
| `spoke_1` to `spoke_3` | Build short branch | next spoke, node approach, or vertical landing |
| `spoke_end` | Resolve branch | node, interface, or terminal |
| `vertical_1` | Change deck once | horizontal landing only |
| `node` | Terminal room | no unrestricted network sockets |

The first tuning target is `size 7`, `max_distance_from_center 112`, and `terrain_adaptation: none`.

### Starting selection weights

| Selection | Weight |
|---|---:|
| Standard straight | 20 |
| Short straight | 10 |
| Long straight | 6 |
| Quarter or offset bend | 8 |
| Single-spoke junction | 5 |
| Hub gateway | 2 |
| Vertical exchange gateway | 2 |
| Sealed or collapsed resolution | 7 |

### Connector contract

```text
alfheim:ley_arterial_out  -> alfheim:ley_arterial_in
alfheim:ley_spoke_out     -> alfheim:ley_spoke_in
alfheim:ley_node_out      -> alfheim:ley_node_in
alfheim:ley_vertical_up   -> alfheim:ley_vertical_down
alfheim:ley_interface_out -> alfheim:ley_interface_in
```

Every connector preserves the five-by-five aperture, floor datum, and centered beam datum. Horizontal joints are aligned. Assembled structures contain no visible jigsaw blocks.

## Architectural language

### Material palette

| Role | Materials | Use |
|---|---|---|
| Structural shell | Leyline Livingrock bricks and polished forms | Main masonry |
| Node casing | Leyline carved forms with Gloam borders | Direction masking and relay silhouette |
| Beam optics | Six Mana-glasses | Focusing rings, tinting, and focus selection |
| Spark detail | Starfleck and Amethyst Livingrock | Navigational marks and node centers |
| Damage transition | Cracked Livingrock and local Deepworks stone | Breaches and geology interfaces |
| Pyramid decay | Obsidian Livingrock, Magmatic Livingrock, and slag | Reconstruction obstacles |
| Environmental intrusion | Moss, Rootbound, Tide, Frost, or Magmatic families | One coherent intrusion per branch |

Do not scatter every Livingrock family through one network.

### Condition packages

| Condition | Target | Character |
|---|---:|---|
| Dormant | 40 percent | Intact masonry and unpowered nodes |
| Fractured | 25 percent | Broken gaps, cracked bands, and drops |
| Overgrown | 15 percent | Root and moss intrusion |
| Flooded | 10 percent | Shallow water and broken reservoirs |
| Unstable | 7 percent | Intermittent projection without a beacon payload |
| Restorable intact | 3 percent | Complete relay path awaiting a player source |

Condition remains coherent across connected pieces.

### Haze and light

- Ambient block light generally stays between levels two and six.
- Bright elements sit behind glass, ribs, grates, or occluders.
- Nodes form bright silhouettes at the ends of dark approaches.
- Roots, chains, rings, and water curtains interrupt sightlines.
- The beam sheath supplies the principal haze.
- Optional particles travel along transmission and pulse from receivers.
- Particles and regional fog are enhancements, not dependencies.

## Gameplay and balance

### Navigation

- Arterials use two structural bands; spokes use one.
- Every hub has a unique floor or ceiling silhouette.
- Vertical landings repeat a deck glyph and alignment colour.
- Nodes place their brightest feature opposite the approach.
- Return-facing marks occupy the right wall leaving the Central Confluence Chamber.
- `Leyline Presence` confirms powered coverage without replacing physical navigation.

### Rewards

Rewards concentrate at terminals and interfaces rather than random corridor chests. Appropriate finds include decorative Leyline material, small aligned-glass quantities, survey tools, minor consumables, and lore evidence.

No generated node provides an active beacon, completed pyramid, progression-skipping focus, or high-value cache. The main reward is infrastructure that becomes useful after repair and investment.

### Deep structure interfaces

- **Quarry interface:** exposes a worked ore face without globally increasing ore.
- **Tomb seal:** reaches Court masonry without guaranteeing entry to a burial room.
- **Faultwork breach:** terminates on a ley wound and higher-tier gap.
- **Cavern bridge:** carries an arterial across a supported span.
- **Reservoir interface:** connects flooded branches to Stillwater formations.

## Implementation architecture

### Proposed pack data

```text
tools/gen_leyline_channels.py
tools/check_leyline_channels.py
tools/leyline_channel_manifest.json
kubejs/data/alfheim/structures/leyline_channels/...
kubejs/data/alfheim/worldgen/template_pool/leyline_channels/...
kubejs/data/alfheim/worldgen/processor_list/leyline_channels/...
kubejs/data/alfheim/worldgen/structure/leyline_channel_network.json
kubejs/data/alfheim/worldgen/structure_set/leyline_channel_network.json
kubejs/data/alfheim/tags/worldgen/biome/has_leyline_channel_network.json
kubejs/data/alfheim/tags/blocks/ley_beam_transparent.json
```

The renderer, block entity, beacon access, network graph, and custom effects require code-level support in the pack owner's first-party implementation. Do not approximate them with command blocks or repeated command-style searches. Structure geometry and worldgen remain generator-owned in this pack.

### Signal data

```text
source dimension and beacon position
signal revision
pyramid tier
primary vanilla effect
secondary vanilla effect if valid
primary Alfheim resonance
secondary utility resonance if valid
alignment colour
source last confirmed tick
```

### Performance boundaries

- Rendering is client-side; signal authority and effects are server-side.
- Rays never search beyond the received tier's range.
- The network does not force-load chunks.
- Nodes cache visible neighbors and source revisions.
- Relevant block changes invalidate registered segments.
- Aura application runs at controlled intervals rather than every tick.
- Source revision suppresses cycles.
- Particle density scales with distance and client settings.

## Development sequence

### Phase 1 Effects and registry foundation

- Register `Leyline Presence` and the first six primary resonances.
- Prove icons, refresh, amplifier display, and attribute cleanup.
- Establish narrow Mine and Slash and Ars Nouveau integration points.
- Build a controlled fixture without world generation.

### Phase 2 Conduit block and renderer

- Register the Ley Conduit Node and block entity.
- Implement six-axis air and glass discovery.
- Render vertical and horizontal beacon-style segments.
- Prove opaque termination, tinting, and chunk-edge safety.
- Build straight, bend, junction, and vertical fixtures.

### Phase 3 Relay network

- Implement node discovery, source identity, revisions, loop suppression, and caching.
- Retransmit full tier at every node.
- Apply `Leyline Presence` inside tier-scaled auras.
- Verify ranges of 32, 64, 128, and 256 blocks.

### Phase 4 Beacon injector and focus rings

- Read a real beacon's pyramid tier and effects.
- Preserve vanilla beam validation.
- Detect complete matching focus rings.
- Transmit vanilla and Alfheim payloads.
- Implement tier-four utility resonance and overlap rules.

### Phase 5 Structure generator

- Author the Central Confluence Chamber and sunken pyramid bay.
- Author straight, bend, junction, ladder, node, and terminal pieces.
- Generate staged pools and connector metadata.
- Add empty, unfinished, obsidian-decayed, and magmatic-decayed chamber variants.

### Phase 6 World generation

- Add the underground jigsaw structure, biome tag, and random-spread set.
- Begin around Y minus 28 to Y minus 52 in the Deepworks.
- Use `terrain_adaptation: none` and a solid-rock start contract.
- Keep it outside the Greatbole spawn-protection family.
- Tune from 48-chunk spacing and 20-chunk separation.

### Phase 7 Runtime acceptance

- Locate at least twenty networks across fresh-world seeds.
- Validate footprints, branches, decks, collisions, and terminals.
- Build all four pyramid tiers in generated chambers.
- Verify straight, branching, vertical, cyclic, broken, and repaired transmission.
- Confirm effects expire after source failure or unload.
- Review beam alignment, haze, tinting, and traversal in the client.

## Validation contract

### Static checks

- Every JSON file parses and every referenced pool, processor, tag, and structure exists.
- Every jigsaw target has a compatible connector.
- Every throat preserves five-by-five clearance and the centered beam datum.
- Every central chamber preserves the nine-by-nine by four-layer pyramid volume.
- Generated decay never forms a valid pyramid.
- Mandatory tier-one links do not exceed 32 blocks.
- Higher-tier gaps remain within their declared maximum.
- No piece exceeds 48 blocks on an axis.
- Terminals have no unrestricted network sockets.
- NBT contains no exposed jigsaws, command blocks, unintended spawners, or progression loot.
- Generator output matches its manifest and shipping paths.

### Runtime checks

- Air and tagged glass transmit the custom beam.
- Untagged solids and fluids stop it.
- Placing a block in a segment interrupts visuals and effects.
- Removing the obstruction restores the link without restart.
- Every powered node applies `Leyline Presence` at the correct tier.
- Aura radii are 20, 30, 40, and 50 blocks.
- Link limits are 32, 64, 128, and 256 blocks per node.
- Relays reset distance without amplifying tier.
- Cycles do not multiply updates, effects, or brightness.
- Overlapping nodes do not stack identical amplifiers.
- Invalid or unloaded sources expire downstream payloads.
- A four-tier pyramid fits without moving the beacon or injector.

## Prototype decisions requiring evidence

- Exact Mine and Slash attributes exposed by a stable API.
- Final numerical strength of custom resonances.
- Sphere, cube, or corridor-clipped aura shape.
- Signal and aura refresh intervals.
- Renderer thickness and particle density per tier.
- Literal or blended stained-glass tinting.
- Navigable occupied-deck count in generated terrain.
- Final spacing, height distribution, and biome placement.
- Whether a costly Ley Anchor belongs in a later era.

These questions do not reopen the centered corridor, six-direction node, per-relay transmission, tier range table, presence effect, focus-ring payload, or sunken pyramid chamber.

## First development target

Begin with a non-worldgen test rig containing two nodes on each axis, glass and opaque interruption samples, and one tier-one beacon injector.

The first accepted milestone is:

1. A valid beacon activates the injector.
2. The injector emits in every exposed direction.
3. Glass transmits the beam and stone stops it.
4. A receiving node retransmits the signal.
5. Both nodes apply `Leyline Presence I` within twenty blocks.
6. The connection fails beyond thirty-two blocks.
7. Breaking and restoring the path updates without restarting the world.

Only after this vertical slice passes should development add the remaining tiers, focus rings, MMO effects, and generated jigsaw corridors.
