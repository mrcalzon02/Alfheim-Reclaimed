# Act I town services and authored dungeon interiors

Acceptance: build and static checks passed. Runtime validation was stopped at the
user's request to conserve remaining usage. This candidate is not installed in
the active pack, and natural monastery/refuge registration remains staged.

Continuity Works `StructureCapability.plan` and `generate` executed locally with
seed 2026101801 for Minecraft 1.20.1 / Forge 47.4.10. The pack-authored provider
emitted six furnished 13×14×19 shop templates, 17 dungeon interior templates and
a 43-offer merchant catalogue. [Town service plan](town_services.png).

| Merchant | Offers | Function |
|---|---:|---|
| Arms dealer | 7 | Native common level-one MMO sword, bow, staff, shield and three armor families |
| Provisioner | 8 | Food, arrows, torches, milk and native MMO food |
| Apothecary | 11 | Three rarities each of MMO health/resource potions; regeneration, speed, fire resistance, night vision and water breathing |
| Repairer | 4 + repair service | Paid repairs, anvil, grindstone, experience bottles and sharpening stones |
| Combat supplier | 9 | Six native MMO buff potions, sharpening stones, weapon/armor enchantment items |
| Salvage broker | 4 | Common MMO profession materials plus a Source Gem for health potions |

Purchases normally consume Manasteel Ingots and Source Gems. Prices increase with
potion rarity; stock is bounded and resets once per 24,000 elapsed game ticks.
Native MMO restrictions remain authoritative. Equipment rolls once into saved
merchant stock; daily restocking restores uses without rerolling the equipment.

To repair, crouch and interact with the repairer while holding damaged equipment.
Each started 100 points of missing durability costs one Manasteel Ingot and one
Source Gem from the inventory. Insufficient payment changes nothing; successful
repair changes durability while preserving enchantments and MMO item data.

Act I native village pieces select these shop templates and their persistent
elven merchant profiles. Non-central Act I dungeon rooms receive authored
interiors cropped inside their existing walls. Graph door masks, central shaft
routes, existing ladders and the shared site allocator remain authoritative.
Later Acts and existing ordinary elven social trades retain their catalogues.

The installed pack JAR was preserved. The disposable validation harness restores
its prior server JAR and properties. The candidate JAR is under the companion
project's `build/libs/`; source changes require a future accepted installation.

Already executed: companion Gradle build/test suite, shop access and stock checks,
existing elven-trade checks and feature-order validation (zero cycles across 313
loaded biomes). Initial game startup encountered sandbox network restrictions;
the retry was stopped on request. No runtime success is claimed.

Remaining: native merchant/repair acceptance, fresh-world natural placement,
client interaction and appearance review, multiplayer, protected town combat
boundaries, encounter controllers, dungeon monsters/boss and portal/quest services.
The 26 creature sculptures remain separate art prototypes.

Sources: `tools/gen_act_one_refuge.py`, `tools/check_act_one_refuge.py`,
`tools/render_act_one_refuge.py`, `tools/run_act_one_refuge_validation.py`.
