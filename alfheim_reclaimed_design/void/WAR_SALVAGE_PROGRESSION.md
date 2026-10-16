# War salvage: recipes, recovered objects and era uses

Implemented 2026-10-15. Additive support economy for the Void Verge / Void Shore
war-remnant family. This does not change terrain, structure placement, titan hulls,
existing era ladders or rune gates.

## Recover and rebuild

All 32 war-remains blocks now have a crafting-table replica recipe and a Mana Pool
processing use. Each replica costs ordinary material, a clay ball and a decay-state
dye and produces one block. Organic remains use rotten flesh plus a family binder
(slimeball for sludge, beetroot for flesh/sinew, kelp for organs, leather for hide);
skeletal remains use a bone block; golem remains use an amethyst block; military
masonry uses stone bricks. Every shapeless input combination is distinct, so the
crafting grid can select every state unambiguously. JEI and Shift tooltips list dyes.
These are inert building replicas, including the explicitly empty core socket.
The recipes provide renewable building palettes without requiring demolition of a
finite landmark. There are no free recovered power cores, metals or era tokens.

All sludge, flesh, organ, hide, bone, cartilage, sinew and ligament states wash into
one Washed Titan Biomass per block for 4,000 mana. All dead crystal, empty sockets,
severed conduits and war masonry wash into one Washed Golem Grit for 6,000 mana.
The mixed mineral grit is deliberately a low-grade common recovery stream.

The Enchanting Apparatus then consumes a washed component, mana powder and a Source
Gem to make one Purified Titan Resin (2,000 Source) or Tempered War Lattice
(3,000 Source). Both useful components therefore require Leaf power and Song
processing. Washed matter has no direct recipe into combat currency or tier goods.

## Uses and progression

| Route | Inputs beyond the processed salvage | Station and cost | Output |
|---|---|---|---|
| Binding supplies | Resin + mana powder | Apparatus, 1,500 Source | 4 slimeballs |
| Hide preservation | Resin + leather + mana powder | Apparatus, 2,000 Source | 4 leather |
| Era III reclamation | Resin + Living Fibre + mana powder | Runic Altar, 8,000 mana | 4 Floral Fertilizer |
| Era VI expedition relief | Resin + lattice + Wildmarch Sinew | Apparatus, 6,000 Source | 2 Mine and Slash Orbs of Relief |
| Era VIII gear quality | 2 lattice + Rimebound Lattice | Apparatus, 10,000 Source | 2 Mine and Slash Orbs of Quality |

Era labels identify the actual existing ladder material consumed, not an invented
quest lock. None of these recipes yields a ladder intermediate, tier material,
rune, Alfsteel or active golem core. No existing gate recipe is replaced. This is
an optional expedition/building supply branch, not another doubling ladder.
Live balance of the currency costs remains subject to play review.

## Six custom objects

Four inert displays combine their corresponding remains block with Livingrock:
Salvaged Core Cradle (hollow empty socket), Severed Conduit Display (split length),
Titan Rib Reliquary (exposed ribs) and Sealed Organ Vessel (lidded specimen).
They are decorative objects, not storage containers or working machines.

The Reclaimed Ward Brazier gives light 12; the Restored Lattice Lamp gives light 15.
Each is restored in the Apparatus from its corresponding salvage block, tempered
lattice, mana powder and a Source Gem for 2,000 Source. These are real static block
lights without tickers, fuel inventories or spreading decay. No claim is made that
the light destroys enemies or confers a ward effect.

All six have bespoke cuboid models, matching collision boxes, item models and
self-drop loot. Hidden/coincident faces are clipped using the existing geometry
repair utility. The full-cube material blocks inside generated titan bodies remain
full cubes. The new objects are player-craftable; this pass does not retrofit their
geometry into the already validated structure templates.

## Evidence and limits

`tools/gen_war_salvage.py` invokes the installed Continuity Works
`minecraft_recipe_generate` content tool for 36 vanilla crafting recipes. The
41 Botania/Ars recipes use the same station schemas already shipped in the pack;
they are not claimed as supported by the simplified vanilla content generator.
Authoring uses namespace ID gates; actual recipe registration and resolved
ingredients/outputs are checked separately in the isolated Forge test world.

`tools/check_war_salvage.py` verifies 77 recipes, coverage of all 32 materials,
four non-dead-end intermediates, era consumables, six bounded models and zero
coplanar face overlaps. `tools/gen_process_tooltips.py` adds recipe-origin/use
instructions to the existing Shift tooltips; JEI supplies quantities and layouts.

Runtime evidence is recorded in `tools/war_salvage_runtime_report.json` by
`tools/run_war_salvage_validation.py`. The runner only touches its disposable
server world and removes its temporary audit script. Its check proves real recipe
deserialization, nonempty resolved ingredients and expected outputs. It does not
replace manual station operation, client rendering or balance review.

Final Forge console: `server/console-20261015-212951.log`, disposable world
`validation-war-salvage-20261015`: 77/77 registered recipes, expected outputs/counts,
and zero empty ingredients. Ars uses its real `getResult` API and explicit reagent
and pedestal lists; the installed class intentionally returns an empty stack from
Minecraft's generic `getResultItem` API. Recipe file hashes are frozen against the
server mirror. Startup scripts report zero errors. The unrelated existing
`mythicbotany:feysythia_petal_apothecary` warning about `feywild:lesser_fey_gem`
remains outside this addition.

The broad terrain baseline remains 39/39 unchanged; all 112 custom cuboid models
pass the face audit. The existing 25-template war-family navigation/core/fixture
audit also passes after this recipe/model addition.

Geometry preview: `tools/war_salvage_models_review.png` is an offline diagram,
not an in-game screenshot. A full game restart is needed for the new registrations.
