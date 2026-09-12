# Field review — 2026-09-12, `New World burnshire`

**Status:** `complete for the four screenshots supplied` — two findings, F1 upstream and already diagnosed, F2 new.
**Budget note:** evaluation only. Nothing is being repaired in this session; fixes are Monday's
work. Every finding below carries enough detail to act on without re-deriving it.

**Evidence:** `screenshots/2026-09-12_14.16.50 / 14.16.54 / 14.17.01 / 14.18.48.png`,
save `saves/New World burnshire`.

**Shipped state under test:** `68b25513` — void margin after the three-scale body carve, surface
detail, frozen void water, coast slope, terrace amplitude 0.175, terrain-authority selector
wired (inert), ley line straights at 64.

---

## Findings

_(appended as they are established)_

### F1 — Ordinary terrain is stacked plates and fluted columns — **upstream `libx:smash`, confirmed a second time**

`14.16.50` looking down: the hillside is a stack of thin flat shelves, one to three blocks thick,
each with vertical sides, plus a free-standing square pillar two blocks across in the foreground.
`14.18.48` looking up a slope: long fluted organ-pipe columns with grass caps, and another
isolated pillar at the right edge.

Both are **ordinary Alfheim land, not the void margin**, so none of this session's void work
touches it.

This is the signature already traced on 2026-09-11:

```
alfheim_initial -> quarter_negative(alfheim_height)
alfheim_height  -> libx:smash{ axis: "y", density: interpolated(lerp(low, high, erosion)) }
```

A Y-axis quantiser upstream of every column in Alfheim. It is MythicBotany's, not ours: upstream
`alfheim_final` is literally `min(alfheim_initial, alfheim_caves)`, identical to our ordinary
branch above Y 28, and the terrace weight is provably 0.000 outside Golden Fields.

**The fix is built and untested**, waiting only on a decision — override
`mythicbotany:alfheim_height` with the same expression minus the wrapper:

```json
{"type":"minecraft:interpolated","argument":{"type":"libx:lerp",
 "argument1":"mythicbotany:alfheim_low","argument2":"mythicbotany:alfheim_high",
 "deviation":0.4,"mean":0.15,"niveau":"mythicbotany:alfheim_erosion"}}
```

One file, fully reversible. **It changes the character of the whole dimension**, which is why it
has not been shipped unasked. Monday: run it as an A/B against a control on one seed and compare
`probe_terraces.py --steps` jump histograms — a quantiser shows as a spike, its removal as a
smooth decay.

**Cost if wrong:** one datapack file to delete. **Cost if skipped:** this is now the third review
to raise it.

### F2 — Silverbark Wood grows no silverbark — **content gap, ours, cheap to close**

`14.17.01` at **x 177, z 572, y 109, biome `silverbark_wood`**. The pale scattered features are
trees whose trunks run diagonally at roughly 40 degrees with a tuft of foliage at one end, and
they are the biome's *only* tree.

Its whole feature list is seven MythicBotany metamorphic stones, three ores, and:

```
mythicbotany:alfheim_grass
mythicbotany:loose_dreamwood_trees
```

So the diagonal trunks are **MythicBotany's own loose dreamwood**, which grows in that scattered
leaning form by design. Not a defect in itself.

**The defect is that a biome named Silverbark Wood generates no silverbark.** It has no canopy
feature of its own at all, which is also why the landscape in these shots reads as bare stepped
grass: nothing is covering it.

This is a gap rather than a regression. B-84 gave the three wooded shores real canopies
(`shore_mistbark_canopy`, `shore_tidewood_canopy`, `shore_sporecaps`) and silverbark_wood never
got the equivalent. `BIOME_INDEX.md` tracks "land biomes with a single vegetal feature" and
silverbark passes it on a technicality — it has two, and one of them is grass.

**Monday:** author a silverbark canopy feature the way the shore canopies were authored, and add
it to the biome's vegetal step. Then re-check the other land biomes against the same question —
does each one generate the thing it is named after — because this was found by accident and
nothing asserts it.

---

## Priority for Monday

1. **F1 `libx:smash`** — the largest visual change available, one file, reversible, and raised by
   three consecutive reviews. Needs an A/B against a control on one seed; do this first because
   it changes what every other terrain judgement is made against.
2. **F2 silverbark canopy** — small, self-contained, no worldgen risk.
3. Then the outstanding items from before this review: the client walk still clears six backlog
   entries (B-82, B-84, B-85, B-89, B-93, B-94), and B-55 is still the only open item that
   unblocks other work.

## Not re-raised

The void margin does not appear in this set — all four shots are ordinary land. Nothing here
speaks to the margin work of 2026-09-11/12, which remains measured but unwalked.
