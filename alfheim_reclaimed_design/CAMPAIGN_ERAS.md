# Campaign Structure — Ten Eras

**Status:** design record. Structure fixed; individual quest text not yet authored.
**Target:** 10 eras × 20+ quests = **215 quests** as budgeted below.

---

## 1. The spine of the campaign

MythicBotany implements the Nine Realms as nine real, craftable rune items. That is not decoration —
each rune is an obtainable object with a place in the mod's own progression. The campaign therefore
uses them directly:

> **Each era ends when you earn its rune. The rune *is* the era's capstone.**

One prologue era carries no rune, giving ten in total. The order is not the Norse cosmological order;
it is the order in which an elf rebuilding a dead world would need each realm's gift.

| # | Era | Rune earned | The question the era answers |
|---:|---|---|---|
| I | The Ashen Grove | — | Can anything still grow here? |
| II | The First Light | `alfheim_rune` | Can we hold ground? |
| III | The Green Return | `vanaheim_rune` | Can we feed ourselves? |
| IV | The Long Silence | `midgard_rune` | Is anyone still out there? |
| V | The Deep Forges | `nidavellir_rune` | Can we make our own metal? |
| VI | The Wild Marches | `joetunheim_rune` | Can we take back the frontier? |
| VII | The Burning Cradle | `muspelheim_rune` | Can we survive our own fire? |
| VIII | The Frozen Archive | `niflheim_rune` | What did we forget? |
| IX | The Debt | `helheim_rune` | What did it cost? |
| X | The Crown of Branches | `asgard_rune` | What do we become? |

## 1b. The tier ladder — settled 2026-09-02

**One base material per era. Each era adds a new process. Output and cost double.**

Era N's tier material = **2 x (Era N-1's material) + one new process**. Not a flat recipe that grows
to 1024 ingredients — a recursive one. That gives all three curves at once:

| Axis | Growth | Era X |
|---|---|---|
| Raw material cost | doubles per era | **512x** Era II |
| Chain depth | +1-2 steps per era | ~12-18 steps |
| Distinct ingredients | +1-2 per era | ~10-14 |

The doubling is real and felt; it is expressed through composition rather than recipe size.

### Binding rules

1. **One tier material per era.** Not every foundational component. Everything else scales gently
   around the ladder. Doubling everything is 512x on all fronts and breaks the pack.
2. **Each era's addition must be a new *process*, not a new item.** A machine, ritual, or step the
   player has not used. Nine tiers of the same tedium in different hats is the failure mode.
3. **Automation must land ahead of the curve.** Doubling bites hardest at Era V-VI, when cost has
   arrived but automation has not. The unlock belongs in Era III, not Era VI. This is where packs
   die.
4. **Quests must state real transitive cost.** A 512x cost is invisible in JEI — the player sees
   "2 of the previous thing". Unstated, it reads as an ambush forty hours in.
5. **Later eras get automation quests, not craft-this quests.** The 7 Leaf quests in Era VII should
   be "build the system that makes the thing", not "make seven things".

This is *why* the pack forces automation: past Era IV manual crafting stops being viable, so
"gardens are factories" becomes mechanically compulsory rather than thematic.

### Open

Whether the ladder is **one shared material** both spines feed, or **one per spine**. Shared is
recommended — `TWIN_SPINES.md` §2 already makes Alfsteel require a Song ritual, so the pinnacle
metals are co-authored by construction. Two full ladders means two 512x curves in parallel.

## 2. Quest budget

Every era carries four tracks. Both spines advance in every era — that is the structural rule that
makes them twins rather than alternatives.

| Track | Per era | Purpose |
|---|---:|---|
| **Spine of Leaf** (Botania / MythicBotany) | 7 | Material and power progression |
| **Spine of Song** (Ars Nouveau) | 7 | Knowledge, ritual and automation |
| **Support** (settlement, food, building, worldgen) | 4 | Makes the world feel inhabited |
| **The Wound** (Mine and Slash) | 3 | Combat, expedition, reward |
| **Capstone** (the rune) | 1 | Era gate |
| | **22** | |

10 × 22 = 220, less 5 for the prologue's reduced Song track = **215**.

**Era gate rule:** the capstone unlocks only when *both* spine tracks are complete. Support and Wound
quests are optional for the gate but supply materials the next era assumes you have.

---

## 3. The eras

### Era I — The Ashen Grove
*No rune. 17 quests: Leaf 7, Song 2, Support 5, Wound 3.*

You wake in a grove that burned. The prologue teaches the pack's one non-obvious rule: **the elven
materials are the ones you can get.**

- **Leaf:** first Pure Daisy → **Dreamwood** (not Livingwood — the reversal's first visible statement).
  Dreamwood Twig, Wand of the Forest, first Petal Apothecary, first Mana Spreader (Elven), Diluted
  Mana Pool.
- **Song:** find a Worn Notebook in the ruins; craft the Novice Spell Book. Deliberately thin — Song
  is a thing you *discover* here, not a thing you have.
- **Support:** shelter, first crops (Farmer's Delight), clear a ruin, recover a readable fragment.
- **Wound:** survive the first night, kill ten corrupted things, find your first gear drop.

### Era II — The First Light
*`mythicbotany:alfheim_rune`. 22 quests.*

Hold a piece of ground and light it.

- **Leaf:** full Mana Pool, Mana Spreader network, first generating flower (Endoflame), Runic Altar,
  first Botania runes, Mana Tablet, Livingrock production.
- **Song:** Imbuement Chamber, first Source Jar, Agronomic Sourcelink, Magelight, first three glyphs,
  first spell, Starbuncle familiar.
- **Support:** first MineColonies builder hut, a bridge, a functional kitchen, restore a shrine.
- **Wound:** first Adventure Map, first currency orbs, a named ruin boss.
- **Capstone:** Rune of Alfheim — the ground is yours.

### Era III — The Green Return
*`mythicbotany:vanaheim_rune`. 22 quests.*

Growth as a system, not an accident. This is where the pack's "gardens are factories" thesis becomes
literal.

- **Leaf:** Agricarnation, Hydroangeas, mana automation, Elven Quartz native route, Floral Fertilizer,
  Horn of the Wild, first passive generator array.
- **Song:** Whirlisprig, Drygmy Henge, Mycelial and Vitalic Sourcelinks, Source Relay network, Ritual
  Brazier, Ritual of Growth.
- **Support:** MineColonies farmer + forester, Miner's Delight, The Harvest crops, a working village
  square.
- **Wound:** map tier 2, a gear set, a talent tree commitment.
- **Capstone:** Rune of Vanaheim.

### Era IV — The Long Silence
*`mythicbotany:midgard_rune`. 22 quests. **The pivot era.***

You build the gate — and it opens *outward*. The player stands in Alfheim
(`mythicbotany:alfheim`) and the gate leads to **Midgard, which is `minecraft:overworld`**
(`WORLD_STRUCTURE.md` §1). The portal is not a way in; it is the elves' first contact with Midgard
since the devastation. Everything the player assumed about Botania progression inverts here, and the
quest text should say so plainly.

> **✅ SETTLED 2026-09-03 by the user — the gate opens in Era IV.**
>
> *"Yeah I changed my mind there. Record the earlier gate as when the gate opens."*
>
> Of the two candidate eras, the **earlier** one is when the gate opens. The gate is built,
> lit and traversable in **Era IV**, and Era IV alone. The user's earlier instruction of
> 2026-09-02 — that the portal is "completable only in **Era VI**" — is **withdrawn** by this
> decision and must not be reinstated from the older record.
>
> **What this settles, across six documents:**
>
> | Document | Was | Now |
> |---|---|---|
> | this section | Era IV (already correct) | Era IV, confirmed |
> | `BACKLOG.md` B-36 | "completable only in Era VI" | completable in Era IV |
> | `IMPLEMENTATION_PLAN.md` §Era VI | "gate becomes a mandatory link" | Era VI is frontier expedition; the gate is already open |
> | `ERA_EXPANSION.md` §8 | blocking decision, 132 quests held | resolved; nothing blocked |
> | `WORLD_STRUCTURE.md` | "Midgard: visits, from Era VI" | from Era IV |
> | `PROCESS_INDEX.md` | `botania:elven_trade` mandatory from Era VI | mandatory from Era IV |
>
> **The gating material moves with it.** B-36 keyed the final component to Era VI's capstone
> (`alfheim:wildmarch_sinew`). It is now Era IV's capstone, **`alfheim:gatewrought_cord`** —
> whose tooltip has read *"Era IV. Elven work, finished on the far side of the gate"* since the
> roster was authored. The naming was pointing at Era IV the whole time.
>
> **What Era VI loses, and gains.** It is no longer the gate era. Its subject is what it always
> was in this section — the frontier, taken back. It keeps `joetunheim_rune` and the Wild
> Marches. What changes is that Era VI's expeditions now depart through a gate the player has
> already been using for two eras, which is a better story than a gate that opens late for no
> reason the fiction supports.

- **Leaf:** Alfheim Portal construction, first **export** trade (Dreamwood → Livingwood), Pixie Dust
  native route, Elf Glass, first Manasteel *received*, Mana Pearl import, Elven Mana Spreader upgrade.
- **Song:** Enchanting Apparatus, Arcane Core, Wixie Cauldron, Source Relay: Warper, Scry ritual,
  Spell Turret, Mage's Spell Book.
- **Support:** trade post building, Domum Ornamentum decoration, a road, a lit border.
- **Wound:** map tier 3, first unique drop, an Orb of Ascension.
- **Capstone:** Rune of Midgard — you have touched the other side.

### Era V — The Deep Forges
*`mythicbotany:nidavellir_rune`. 22 quests.*

Metal of your own. Elementium stops being a trade good and becomes an ore.

- **Leaf:** locate `mythicbotany:elementium_ore` in Alfheim, Raw Elementium smelting, Elementium
  tools, Dragonstone via Runic Altar, Alfsteel Pylon, Mana Infuser, **Alfsteel Ingot** (1,500,000 mana).
- **Song:** Alchemical and Volcanic Sourcelinks, Archmage Spell Book, armour upgrades, Amplify/Pierce
  glyph tier, Wilden summoning ritual, automated enchanting.
- **Support:** MineColonies smeltery, Create-assisted ore processing *(see open question §4)*, a forge
  district, Conquest Reforged stonework.
- **Wound:** map tier 4, a boss with a gear-level requirement, gem socketing.
- **Capstone:** Rune of Nidavellir.

### Era VI — The Wild Marches
*`mythicbotany:joetunheim_rune`. 22 quests.*

Outward. Twilight Forest and the hostile biomes open as expedition ground.

- **Leaf:** Terrasteel *attempt* — blocked, because it needs three imports; establish the trade volume
  to afford it. Tiny Planet, Rosa Arcana, Gaia preparation, mana capacity tier 3.
- **Song:** Vexing Archwood, Warding, familiars fully upgraded, ritual chaining, Source teleport network.
- **Support:** Twilight Forest portal, an outpost colony, Macaw's bridges over the marches, Ancient
  Obelisk survey.
- **Wound:** map tier 5, Twilight Forest bosses, Knight Quest encounters.
- **Capstone:** Rune of Jötunheim.

### Era VII — The Burning Cradle
*`mythicbotany:muspelheim_rune`. 22 quests.*

Fire. Both the Nether and the memory of what burned Alfheim.

- **Leaf:** Blazing Archwood, Entropinnyum, Nether mana generation, Gaia Spreader, Ender Air, Blaze
  infrastructure.
- **Song:** Volcanic Sourcelink at scale, fire glyph tier, Blazing familiars, fire-resistant ritual work.
- **Support:** Nether outpost, Create-assisted heat *(see §4)*, a fire-shrine restoration.
- **Wound:** map tier 6, Nether expedition, fire-resistance gear tier.
- **Capstone:** Rune of Muspelheim.

### Era VIII — The Frozen Archive
*`mythicbotany:niflheim_rune`. 22 quests.*

The elves wrote things down before the devastation. Most of it is under ice.

- **Leaf:** Cascading Archwood, ice-biome flora, Mana Enchanter, Manaweave Cloth, Ring of Andwari
  (ritual, four Runes of Greed + two Runes of Alfheim — verified recipe).
- **Song:** the full glyph library, Caster Tomes, Scry rituals for lost sites, an automated research
  loop, Archmage armour.
- **Support:** BetterEnd / frozen archive delving, library restoration, Modonomicon lore entries.
- **Wound:** map tier 7, frozen bosses, Orb of Knowledge farming.
- **Capstone:** Rune of Niflheim.

### Era IX — The Debt
*`mythicbotany:helheim_rune`. 22 quests.*

What the devastation cost, and who paid. The pack's darkest chapter.

- **Leaf:** Wither Aconite, Blood of Kvasir (ritual: Ender Dagger + Alfsteel Nugget + Vial, 20,000
  mana, four realm runes — verified), Mead of Kvasir, Gaia Guardian I, Dice of Fate.
- **Song:** death-aspect glyphs, the Fimbultyr tablet, Occultism cross-binding, ritual of the lost.
- **Support:** Infectious / zombie-variant siege defence, a memorial build, Better Archeology digs.
- **Wound:** map tier 8, Gaia Guardian as a Mine and Slash encounter, mythic gear.
- **Capstone:** Rune of Helheim.

### Era X — The Crown of Branches
*`mythicbotany:asgard_rune`. 22 quests.*

Alfheim reclaimed — and Midgard reachable as an equal.

- **Leaf:** **Terrasteel** at last (the alloy of two worlds), Gaia Guardian II, Alfsteel armour set,
  Branch of Yggdrasil, Gjallarhorn, Mjöllnir (500,000 mana, twenty runes — verified).
- **Song:** every ritual mastered, an autonomous source economy, the Archmage capstone.
- **Support:** a fully restored elven city, the great gate rebuilt in stone, the colony at maximum tier.
- **Wound:** map tier 9–10, the final encounter, legendary gear.
- **Capstone:** Rune of Asgard — the crown of the world tree.

---

## 4. Open questions

These block quest authoring for the eras named, and are decisions rather than defects.

1. ~~**Ars Nouveau vs. Ars Magica.**~~ **Resolved 2026-09-02** — Ars Nouveau confirmed. The Spine of
   Song is unblocked.
2. **Create's role.** Resolved in principle by `INSTRUCTIONS.md` §2.3 — Create stays only if every
   progression-relevant recipe in it routes through a spine. Eras V and VII assume it is present as
   elven waterwheel-and-gear craft, subordinate to mana. What is still open is the *gating design*
   for twelve Create-family mods, which is a substantial body of recipe work in its own right.
3. **Mine and Slash map tiers.** The tier-per-era mapping above is a placeholder; real tier numbers
   must come from the mod's own level curve, read from config after first boot.
4. **Realms beyond Alfheim.** Era X's climax and Era IV's destination both depend on the Continuity
   Works custom mod, which is not yet available. Until it ships, Midgard exists in the fiction and in
   the trade recipes but not as a place. See `WORLD_STRUCTURE.md` §5–6.
5. **Regions Unexplored.** Making Alfheim the Overworld kills all 170 of its biomes outright. It is
   either rebuilt as tag-injected biomes by the custom mod, or it leaves the pack.
   See `WORLD_STRUCTURE.md` §4.

## 5. Authoring rule

From `INSTRUCTIONS.md` §6.4: **one chapter at a time.** Author Era I, load it, complete it in-game,
fix what the schema teaches you, and only then author Era II. Do not generate 215 quests against an
unverified SNBT schema — that is exactly the failure the original design note warned about, at
ten times the scale.
