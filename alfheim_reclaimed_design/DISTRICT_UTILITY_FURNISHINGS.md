# District utility furnishings

Eleven modeled, craftable objects extend the functional furnishing library.
The native implementation lives in Alfheim Leyworks; all geometry, collision boxes,
recipes, blockstates, drops and translations are generated from
`tools/gen_district_furnishings.py`.

## Furniture with actual functions

| Object | Use | District emphasis |
|---|---|---|
| Living Seed Cabinet | 27 persistent inventory slots | Agriculture, botanical gardens |
| Apothecary Cabinet | 18 persistent inventory slots | Relief, quarantine, field medicine |
| Warden's Armory Locker | 54 persistent inventory slots | Military, frontier, royal guard |
| Provision Hutch | 27 persistent inventory slots | Residential, civic kitchens |
| Scholar's Archive Cabinet | 54 persistent inventory slots | Scholastic, lineage, royal archives |
| Tradehall Service Counter | 27 persistent inventory slots | Roads/trade, harbor, civic service |
| Artificer's Workdesk | Real 3×3 crafting grid | Production, residential workshops |
| Livingrock Mason's Bench | Actual stonecutting recipes | Production, civic repair yards |
| Dreamwood Weaving Frame | Banner pattern selection and dye consumption | Residential, lineage, ceremonial rooms |
| Frontier Cartographer's Table | Map copying, scaling and locking | Frontier, harbor, military command |
| Warden's Mending Bench | Vanilla grindstone repair/disenchanting | Military, production, expedition stores |

All storage accepts ordinary items; its names describe the room role, not a hidden
filter. Existing wide storage screens synchronize active capacity. Hoppers can
access the active inventory; comparators report fullness. Breaking the furniture
releases contents into the world rather than putting an inventory inside its
dropped block item. These are supplies/storage/work stations, not automatic
healing, trading, food-preservation or Mine and Slash gear-reroll machines.

Workstations use native Minecraft menus, recipes and material costs. Their custom
block/distance validity checks let them remain open at their own furniture block,
then close when the player leaves range or the block is removed. Ordinary input
return on closing remains the native menu behavior. They add no ticking block
entities, global scans, district search loops or passive power generation.

## Model language

Dreamwood and gold frames tie the wave to the existing royal/elven palette.
Shelves, drawer pulls, seed fronts, potion bottles, book spines, weapon supports,
map rolls, loom threads, work surfaces and tools distinguish their room roles.
All eleven stay inside one block and rotate in four horizontal directions.
Collision is generated from the same source cuboids as the models and rotates
with them. Coincident and hidden surfaces use the established clipping utility.
Native item models display the furniture itself in inventory.

`tools/district_furnishings_review.png` is an offline geometry diagram from emitted
model faces. It is not a game screenshot or a client rendering acceptance claim.

## Recipes and progression

Every object has its own 3×3 shaped recipe, emitted with the installed Continuity
Works `minecraft_recipe_generate` tool for Minecraft Java 1.20.1. Authoring ID
policy is namespace-aware; native runtime acceptance is recorded separately.

All six storage recipes use Dreamwood, Source Gems and Purified Titan Resin,
plus a chest (54 slots) or barrel (18/27 slots) and a role-specific ordinary item.
That gives the preceding war-salvage resin a durable settlement-building use.
All five workstation recipes consume their corresponding vanilla workstation,
Dreamwood, mana powder, Source Gems and Tempered War Lattice. The wrappers therefore
retain existing station acquisition requirements and also consume both magical
spines' processed supplies. They do not yield a tier ladder item or bypass a rune.

## Placement boundary

This wave supplies usable objects and the district furnishing inventory. It does
not automatically replace existing dungeon loot barrels or rewrite saved rooms.
No natural structure set, district spacing rule, foundation or terrain file is
changed. In particular, the new fixed containers do not implement randomized loot
tables, so replacing a loot-bearing barrel would lose its unopened loot contract.
That conversion is deliberately outside this modeling wave.

For a manual review, `/function alfheim_leyworks:district_furnishings/review` places
all eleven **empty** fixtures relative to the caller in a 16×4-block gallery. Use a
clear review area. The native audit commands refuse non-validation worlds and are
not an installation step for normal players.

## Validation

`tools/check_district_furnishings.py` checks model bounds, face overlaps, recipe
uniqueness, output IDs, spine ingredients and source-to-collision equality.
`tools/check_field_review.py` retains the protected terrain and geometry baseline.

`tools/run_district_furnishing_validation.py audit` loads a disposable Forge world
and runs native tests: real output pickup/input consumption for all five stations;
near/far/removed-block validity; six storage capacities; blocked inactive slots;
shift-click item conservation; NBT round trips; comparator signal; exact content
recovery on removal; and real timed hopper transfer.
Its `reload` mode restarts that world and checks each saved container/hopper pair
still conserves its 32 test items. The recorded proof is
`tools/district_furnishings_runtime_report.json` and pins the built/installed/server
jar SHA-256. In-client screen synchronization, textures, hand placement and
multiplayer use remain play-review tasks even when server interactions pass.

Accepted native evidence (2026-10-15):

- `server/console-20261015-215117.log`: six storage profiles, five actual station
  output transactions, eleven resolved recipes, six successful timed hopper pairs.
- `server/console-20261015-215326.log`: after a full restart, each of the six
  cabinet/hopper pairs still totals 32 items. Hoppers finish moving the contents
  after reload, leaving all 32 items in each hopper.
- Built, installed and server jars match
  `510704ed782673eb7c9b93dc14b7158b11857895791a998341a21ae18f0d1a94`.
- The previous seven-container source/resource contract still passes. Protected
  terrain remains 39/39 unchanged; all 123 custom cuboid models pass the face check.

The existing material Shift-tooltip generator now also reads the owned Leyworks
recipe sources, so resin and lattice describe their new furnishing uses. Native
furniture item tooltips describe each object's actual function and capacity.
