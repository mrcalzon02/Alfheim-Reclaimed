# Stone Transmutation — moving one stone into another, always through Livingrock

**Role:** design record for the magical conversion of Alfheim's stone library.
**Status:** `plan only — nothing implemented`.
**Owner direction, 2026-09-12:** *"various magical interactions to move our types of stone from
one form to another starting always with the base living rock."*
**Authority:** subordinate to `INSTRUCTIONS.md`. Bound by §2.3 (everything routes through the
spines) and by `VOID_MARGINS.md` §1 (decorative stone must not become a source of progression
material).

---

## 1. What exists to move between

**42 stones, already built and shipping.** Nothing here proposes new blocks.

**24 Deepworks families, in five groups** — `tools/deepworks_manifest.json`:

| group | families |
|---|---|
| Court | dawn, ivory, moonstone, rose, silvermist |
| Furnace | cinder, cracked, embervein, magmatic, obsidian |
| Grove | amber, fern, moss, petrified, rootbound |
| Ley | amethyst, gloam, leyline, starfleck |
| Water and sky | abyssal, frost, gale, storm, tide |

**18 void stones, in six biome-bound triples** — `void/void_catalog.json`. Riftchalk/Riftshale/
Veilstone, Shardbreccia/Anchorstone/Seamstone, Prismstone/Aetherquartzite/Glintschist,
Rootfossil/Resinshale/Hollowheart, Epitaph/Mourning/Oathstone, Nightmantle/Nullstone/Astralite.

Five carry light: cracked, magmatic, embervein, leyline, starfleck.

## 2. Topology — a hub, not a mesh

**Every conversion passes through `botania:livingrock`.** That is the owner's instruction and it
is also the only tractable shape: 42 stones fully connected is 1,722 recipes to author and
balance. Through a hub it is 84, and through the group ladder below it is 60.

```
        any stone ──(reversion, cheap, lossy)──> LIVINGROCK
        LIVINGROCK ──(attunement)──> group medium ──(inflection)──> family stone
```

**Two steps forward, one step back.** Reversion is deliberately cheap and deliberately lossy, so
the hub is always reachable and stone is never a store of value. Forward conversion costs.

**Why a group medium rather than livingrock straight to the stone.** It makes the five groups
legible as *things* rather than as a spreadsheet, it gives each spine an obvious place to hang a
distinct ritual, and it means adding a 25th family later costs one recipe rather than one per
source. The medium is a real item — five of them, plus one for the void.

## 3. The two spines do different work

Per §2.3 neither spine may be skipped, and they should not be two skins on one mechanic.

**Spine of Leaf — attunement, by material.** Botania/MythicBotany infusion: livingrock in a Mana
Pool with the group's signature offering. Leaf answers *what a stone is made of*. It is the
cheaper, bulk route and it is how a builder converts a stack.

**Spine of Song — inflection, by pattern.** Ars Nouveau apparatus with an inscribed glyph. Song
answers *what shape the pattern takes* — it is what selects the family within a group, and it is
the only route to the finer distinctions. It is per-item, not bulk.

So a full conversion is **Leaf for the group, Song for the family**. Neither spine alone produces
a named stone, which is the gating doctrine expressed as a recipe graph rather than as a lock.

## 4. The void is not on the same ladder

Void stones stay expensive on purpose. `VOID_MARGINS.md` §1: *"Mineral richness rewards careful
expeditions into the remaining rock, not an endless supply of islands."*

The void medium requires a reagent **obtainable only at the margin** and not craftable — so the
trip is still the cost, and transmutation converts what you carried home rather than replacing
the journey. Reversion of a void stone yields livingrock, never the reagent.

## 5. What must not become possible

These are the failure conditions, and each needs a static check before the recipes ship.

1. **No value creation.** No cycle anywhere in the graph may return more of any input than it
   consumed. Reversion is lossy specifically to guarantee this.
2. **No progression laundering.** No conversion may yield Elementium, Mana Diamonds, shards,
   quartz or any spine material. Stones convert to stones.
3. **No spine bypass.** No path from livingrock to a named stone may exist that uses only one
   spine, or neither.
4. **No void shortcut.** No path to a void stone that does not consume the margin reagent.
5. **Light is not free.** The five lit families must cost more than their unlit group siblings, or
   light becomes the only rational output.

## 6. Staging

| stage | delivers | acceptance |
|---|---|---|
| **1** | reversion: all 42 stones → livingrock, one recipe each | a static check proving every stone reaches the hub |
| **2** | the six media as items, and Leaf attunement livingrock → medium | media appear in JEI; recipes resolve |
| **3** | Song inflection medium → family stone, 24 + 18 recipes | every stone reachable; the five anti-invariants asserted |
| **4** | era gating and cost curve | each stone's cost sits in the era its group belongs to |

Stage 1 is independently useful and cannot break anything: it only adds a way to discard.

## 7. Open decisions — owner's call, not assumptions

1. **Do the media want to be items or blocks?** Items are simpler; blocks let a Court medium sit
   in a build as its own material.
2. **Which era opens which group?** Grove and Water read as early, Furnace and Ley as mid, Court
   as late — but that is a guess about the campaign, not a reading of `CAMPAIGN_ERAS.md`.
3. **Is bulk conversion wanted at all?** A Mana Pool converts one item at a time unless a
   catalyst is used. If a builder should be able to convert a shulker of stone, that wants a
   deliberate answer rather than emerging from recipe throughput.
4. **What is the margin reagent?** Something already dropped at the void, or a new item.
5. **Does reversion return anything besides livingrock** — a pinch of the group medium at low
   probability would make experimentation less punishing, at the cost of complicating rule 1.
