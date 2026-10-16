# Biome-themed vanilla enemies — 2026-10-15

## Visual revision — 2026-10-16

The user rejected material-block outfits and additional ornamental geometry.
The final direction is explicitly one clean vanilla model per species plus
recolors. The renderers now select 390 generated biome/style skins, with no
material outfit layer. Native head inventory models sample the matching skins.
All 390 variants are named NBT selections in Spawn Eggs, alongside the existing
five automatic eggs. This reuses the five item/entity IDs. Selection NBT controls
both the item model and spawned appearance; item names do not rename creatures.
The former geometry descriptions below document the superseded implementation.
Java17 build/67 tests, generator equality and 390 resource/selection checks pass;
all 390 item serialization, real egg-spawn and persisted-appearance checks pass
in a disposable server world (`tools/enemy_item_runtime_report.json`). Client
visual acceptance remains pending. Restart Minecraft after installation.

Implemented in the first-party companion mod. Structure development is deferred
at the user's direction until the Continuity Works skill conversion finishes.
No structure, noise, terrain or biome-selection file is changed by this work.

## Roster and appearance

| Vanilla species | Entity ID (`alfheim_companion:`) | Display identity |
|---|---|---|
| Zombie | `biome_zombie` | Revenant |
| Skeleton | `biome_skeleton` | Boneguard |
| Pillager | `biome_pillager` | Outcast |
| Enderman | `biome_enderman` | Riftwalker |
| Endermite | `biome_endermite` | Riftmite |

All 26 home biomes have three appearances per species: **390 combinations**.
They use vanilla rigs with additional animated geometry and native material
textures; existing Fey creature skins are untouched. Five entity registrations
and 120 shared outfit definitions avoid hundreds of duplicate AI implementations.
No creeper variants are added.

The three physical outfits are **Bound** (cuirass, brow and cuffs), **Shrouded**
(hood, collar and mantle), and **Crowned** (crown and asymmetric armour).
Mites use segment shells, mantles and dorsal crests. Root, fungal, crystal, mist,
frost, ash, tidal and field grammars add different ornaments. Every biome has its
own body/accent palette. Exact colours/materials: `tools/themed_enemy_inventory.json`.
These are model layers, not 390 individually painted texture files.

Attachments follow vanilla head/body/limb or mite-segment transforms. Illager
torso depth is handled separately, and mite shells touch their segment anchors.
Existing armour takes precedence over outfit parts. Vanilla weapons, carried
blocks and enderman eye effects remain on the original rig.

## Spawning and persistence

`alfheim:themed_enemy_biomes` contains all home biomes plus
`#minecraft:is_overworld`, including the installed Continuity Works Overworld
biome tag. Natural placement is restricted to Alfheim and the Overworld.
Standard monster darkness, difficulty, ground rules and caps apply.

Existing entries for the five original species are replaced in place, retaining
weights, group sizes and spawn costs. Missing species receive defaults:
zombie/skeleton weight 20, groups 1–3; enderman weight 4, singles;
pillager/endermite weight 2, singles. Other species and custom Fey are retained.
Styles do not create additional spawn entries.

Home biomes choose the exact profile. Overworld biomes select the closest ecology
using biome tags, climate and mushroom/swamp identities. Styles are random on
spawn. Profile/style synchronize to clients and save as `AlfheimBiome` and
`AlfheimStyle`. Biome travel does not recolour an existing mob. Unknown profile
IDs fall back to meadow. Appearance names do not set custom-name persistence.

The subclasses retain vanilla AI, attributes, weapons, sunlight behaviour,
enderman teleportation and endermite lifetime. Loot is inherited directly from
the original species, without a nested loot wrapper. Mine and Slash / Library
of Exile capabilities attach just as they do to vanilla controls; this does not
establish combat balance. Five spawn eggs in the Spawn Eggs tab use the local
biome to choose an appearance.

## Evidence and limits

- Java17 build and **58 tests** pass: all 120 outfit definitions bake, styles
  have different geometry, attachment names match vanilla rigs, and tests guard
  illager torso clearance and mite shell contact.
- Generator/shipping equality, exact 26-biome coverage and every native material
  and loot reference pass checks against the installed Minecraft jar.
- A 15-appearance slice and full 390-appearance disposable-world run pass.
  A restart with the final jar retains the **same 390 UUIDs, species, biomes and
  styles**. Each run saves and exits cleanly.
- Runtime tables cover all 26 home biomes and four representative Overworld
  biomes. The five replaced vanilla species have no residual entries there.
  All five natural placement predicates accept in dark rooms in both dimensions.
- Explicit `NATURAL`-reason factory probes verify biome/style selection, vanilla
  loot tables and skeleton/pillager weapons. These are operator-triggered tests,
  not observation of player-driven natural spawning or final density.
- All five species have matching Mine and Slash / Library of Exile capability
  keys compared with saved vanilla controls.

**Client visual review in motion, combat balance and live-player density remain
pending.** Model baking and server evidence do not certify the final in-game look.
Known unrelated startup warnings are outside this checkpoint's acceptance.

Proof: `tools/themed_enemy_runtime_roster.json`; earlier slice and initial-roster
evidence are retained separately. Build hashes: `tools/themed_enemy_build.json`.
Source: `tools/gen_themed_enemies.py` and the first-party `enemy` package.
Validation tools modify only disposable `server/validation-enemies-*` worlds.
The permission-level-2 `/alfheim_enemies_audit` command is read-only; its explicit
`probe` subcommand creates five test mobs and is intended for disposable worlds.
Player saves were not modified by validation.
