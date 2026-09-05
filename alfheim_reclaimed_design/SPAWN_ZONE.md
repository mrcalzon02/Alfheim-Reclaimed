# The Spawn Zone — The Hollow Court

**Status:** design record. Architecture specified against verified vanilla limits and MythicBotany's
existing jigsaw system. No pieces built.

---

## 1. What is being built

The player arrives through a colossal elven tree into a drained, dilapidated forest city — a canopy
settlement gone dark. Roughly **1000 blocks of radius** around spawn: dead trees, elven bungalows,
collapsed tree-bridges, cobwebs, dead bushes, spider spawners, and no mana at all.

It is the pack's thesis statement in geography. The player should be able to see, in the first sixty
seconds, both what the elves had and what they lost.

> **Naming.** "Lothlórien" is Tolkien's and cannot ship in content. The reference is right; the word
> is not. Working names below are descriptive and IP-clean — **the Greatbole** for the arrival tree,
> **the Hollow Court** for the city, **the Drained Grove** for the biome. Rename freely; just not to
> anything from Tolkien.

## 2. Why this cannot be one structure

Three hard vanilla limits govern the whole design. They are the reason the architecture below is
layered rather than monolithic.

| Limit | Value | Consequence |
|---|---|---|
| Structure block save volume | **48 × 48 × 48** | No authored `.nbt` piece may exceed this. The Greatbole must be an *assembly*. |
| Jigsaw `size` (recursion depth) | **0–20** | Caps how far a single jigsaw structure can propagate. |
| Jigsaw `max_distance_from_center` | **1–128** | A single jigsaw structure reaches at most 128 blocks. **Eight times too small.** |

A 1000-block radius is ~3.1 million m² of surface. Nothing authored by hand covers that. The zone is
therefore built as **five layers**, only two of which are hand-built.

Structurize `.blueprint` files can exceed 48³, but vanilla jigsaw cannot read them — they are a
MineColonies build format, not a worldgen format. Useful for authoring, not for generation.

## 3. The architecture

| Layer | Mechanism | Covers | Hand-built? |
|---|---|---|---|
| 1. The Greatbole | Jigsaw structure, `concentric_rings` count 1 distance 0 | Spawn point | **Yes** — the centrepiece |
| 2. The Hollow Court | Jigsaw structures, `concentric_rings` rings 1–62 chunks | 0–1000 blocks | **Yes** — ~40–80 pieces |
| 3. The dead canopy | Configured/placed features in the biome | Unlimited | No — procedural |
| 4. The decay dressing | Placed features: cobwebs, dead bushes, debris | Unlimited | No — procedural |
| 5. The drained state | Biome definition + mob spawns | Unlimited | No — data |

Layers 3–5 are what make 1000 blocks feasible. You author a few dozen buildings and a tree; the
biome fills everything between them.

### 3.1 Spawn anchoring — `concentric_rings`

This is the vanilla mechanism for "place near world spawn," and it is what strongholds use. It is the
correct tool and it removes the need for any spawn-forcing code.

```json
// worldgen/structure_set/greatbole.json
{
  "structures": [ { "structure": "<ns>:greatbole", "weight": 1 } ],
  "placement": {
    "type": "minecraft:concentric_rings",
    "distance": 0,
    "spread": 0,
    "count": 1,
    "preferred_biomes": "#<ns>:drained_grove"
  }
}
```

For the city, a second set with `distance: 2`, `spread: 6`, `count: 64` scatters pieces outward
through the ring. Tuning `distance`/`spread`/`count` is how the 1000-block figure is actually dialled
in, and it is cheap to iterate — no rebuilding, just numbers.

### 3.2 Build on MythicBotany's jigsaw, do not replace it

MythicBotany already ships a complete elven village system, verified present:

```
worldgen/structure/elven_house.json          size 5, max_distance_from_center 52,
                                             terrain_adaptation "beard_thin"
worldgen/structure_set/elven_house.json      random_spread, spacing 24, separation 6
worldgen/template_pool/elven_houses/
    buildings.json      house (w2), shed (w1), tower (w1)
    gardens.json
    basement_entrances.json
structures/elven_houses/buildings/{house,shed,tower}.nbt
structures/elven_houses/gardens/{crop_garden,flower_garden}.nbt
```

Three of the five NBT pieces we need already exist in a working, terrain-adapting jigsaw. The Hollow
Court extends this rather than starting over: same pool structure, same `beard_thin` adaptation, many
more elements, plus **processors** to apply decay.

It also already ships `mythicbotany:abandoned_apothecaries` — a configured feature that scatters empty
Petal Apothecaries with spilled petals. That is *precisely* the note this zone wants, already written.
Raise its rarity inside the Drained Grove and it becomes free set dressing.

### 3.3 Decay via processors, not via rebuilding

Do not author "ruined" copies of each building. Author the building intact once, then apply a
`processor_list` that:

- replaces a percentage of blocks with air (collapse);
- swaps intact wood for stripped/mossy variants (rot);
- scatters `minecraft:cobweb` into interiors;
- replaces glass with air or broken variants.

One `rule` processor list, applied across every pool element, decays the entire city. It also means
the same pieces can be reused *intact* later — for the restored city in Era X — by swapping the
processor list for `minecraft:empty`. That is a large saving and it makes restoration visible.

## 4. The Greatbole

The arrival portal. A single tree large enough to hold a city in its branches, built as a **jigsaw
assembly** because of the 48³ limit:

| Piece | Approx. size | Role |
|---|---|---|
| `greatbole/base` | 48³ | Root mass, the arrival chamber, the portal frame |
| `greatbole/trunk_a`–`trunk_d` | 32×48×32 | Stackable trunk segments, vertically jigsawed |
| `greatbole/bough_*` | 48×24×48 | Branches with jigsaw sockets for platforms |
| `greatbole/platform_*` | 32×16×32 | Canopy dwellings and walkways |
| `greatbole/crown` | 48³ | The dead top |

Stacking trunk segments vertically through jigsaw connections is how you exceed 48 blocks of height.
With `size: 20` there is ample recursion depth for a tree of 150–200 blocks.

The arrival portal itself sits in `base`. Whether it is a MythicBotany return portal, a custom block
from the Continuity Works mod, or a decorative frame with a `setworldspawn` is an open question —
see §8.

## 5. The city — piece inventory

Target ~40–80 authored pieces. Grouped into pools so the jigsaw can vary them.

| Pool | Pieces | Notes |
|---|---|---|
| `buildings/bungalow` | 10–14 | Ground-level elven dwellings. Extend MythicBotany's `house`/`shed`. |
| `buildings/canopy` | 8–12 | Platform dwellings, for placement on boughs |
| `buildings/civic` | 6–8 | Library, apothecary hall, shrine, moot-ring |
| `bridges/span` | 6–10 | Tree-bridge segments — **collapsed variants essential** |
| `bridges/anchor` | 4 | Bridge terminals and stairs |
| `gardens` | 4–6 | Dead garden beds. MythicBotany ships two to extend. |
| `infra/aqueduct` | 4–6 | Drained water channels, the visible dead mana grid |
| `ruins/rubble` | 6–8 | Pure debris fill, no interiors — cheap and fills space |

Block palette is already unusually strong: **Conquest Reforged** (227 MB of medieval/organic blocks),
**Domum Ornamentum**, **FramedBlocks** for custom shapes, **Macaw's Bridges**, plus Botania's Dreamwood
and Ars Nouveau's four Archwood species for the canopy.

## 6. The decay layer — features, not structures

Everything between buildings is procedural, defined in the Drained Grove biome:

- **dead trees** — a configured feature using dead/stripped Dreamwood trunks with no leaves, high count;
- **cobwebs** — placed feature, surface and interior, moderate density;
- **dead bushes and dry grass** — replacing `mythicbotany:alfheim_grass`, which is lush;
- **fallen logs and debris** — low-cost variation;
- **collapsed bridge remnants** — small NBTs placed as features, cheaper than full structures;
- **no mystical flowers, no mana crystals** — MythicBotany's `mana_crystals` and `motif_flowers`
  features are simply *omitted* from this biome. Their absence is the strongest single signal that
  the grove is dead, and it costs nothing to implement.

## 7. Infestation and drain

**Spiders.** Two mechanisms, both wanted:
- spawner block entities placed inside the NBT pieces, for authored density;
- `spawn_overrides` in the structure JSON, forcing spider spawns across the structure's bounding box
  regardless of the biome's own spawner list.

The biome's own `monster` spawner list should be spider-weighted and otherwise thin — the threat
should read as *infestation*, not as a generic hostile biome.

### 7.1 Continuity Works spawn protection — hazard and opportunity

`continuityworks_spawn_protection` (installed 2026-09-02) enforces a **hard 500-block
footprint-based exclusion** around protected structures, with persistent reservations and per-piece
jigsaw collision protection.

**The hazard.** The Hollow Court is deliberately *dense* — dozens of pieces inside a 1000-block
radius. If its structures land in `#continuityworks_spawn_protection:protected`, they will exclude
each other and the city will generate as a scattering of isolated buildings, or not at all.

**The opportunity.** The Greatbole is exactly what that contract is for. Protect it, and nothing else
generates within 500 blocks of the arrival point — no stray village, no abyssal vent complex, no
Dungeon Realm dungeon punched through the roots.

**The configuration, therefore:**

| Structure | Tag | Why |
|---|---|---|
| `greatbole` | `protected` | Keep the arrival zone clean |
| Hollow Court pieces | `ignored` | They must be allowed to crowd |
| Hollow Court jigsaw pieces | *not* `jigsaw_piece_protected` | Per-piece collision would break the city |

All three tags ship `replace: false` and are datapack-extendable, so this is configurable entirely
from the pack side with no change to the mod.

**Drained of mana.** Three layers, in increasing order of effort:
1. **Absence** (free) — omit mana crystals, mystical flowers and lush grass, per §6.
2. **Nature's Aura** — the mod tracks a per-chunk aura value that is genuinely depletable. Setting the
   spawn region to near-zero aura makes the drain a *mechanic* the player must reverse, not just set
   dressing. Needs investigation: whether initial aura is datapack-reachable or requires KubeJS.
3. **Botania hook** — reduced or zero flower generation inside the biome until a quest restores it.
   Almost certainly KubeJS, and it risks soft-locking Era I. Design carefully or not at all.

Layer 1 is required. Layer 2 is the interesting one and should be scoped after first boot. Layer 3 is
a stretch goal that conflicts with the player needing mana in Era I.

## 8. Open questions

1. **Where does the player actually spawn?** `concentric_rings` places the structure at spawn, but
   vanilla spawn-point selection may put the player outside the Greatbole. Likely needs an explicit
   `setworldspawn` on world creation via KubeJS, or a fixed spawn in the world preset.
2. **What is the arrival portal, mechanically?** Decorative frame, MythicBotany return portal, or a
   custom block from the Continuity Works mod. Affects whether it is ever *usable*.
3. **Who builds the pieces?** ~50–90 hand-built NBTs is the single largest labour item in the project
   — larger than the 215 quests. In-game building with Conquest Reforged, exported through structure
   blocks. This needs a plan and probably needs to be someone's dedicated job.
4. **Does the Drained Grove get restored?** If the city can be rebuilt over the campaign, §3.3's
   intact-versus-decayed processor swap is the mechanism and it should be designed in from the start,
   not retrofitted.
5. **Custom mod or datapack?** Everything above is datapack-achievable *except* exceeding the 128-block
   jigsaw radius. If the Continuity Works mod places structures in code, the layering in §3 could
   collapse into something simpler. Worth asking before authoring 80 pieces.

## 9. Validation

| Level | Condition |
|---|---|
| 1 | All structure/pool/feature JSON parses; NBT loads in a structure block |
| 5 | Each piece: bounds correct, jigsaw blocks aligned, no floating or buried geometry, spawners present |
| 8 | Pack boots with the datapack loaded |
| **9** | **Fresh world: the Greatbole generates at spawn and the player arrives inside it** |
| 9b | City pieces distribute across the intended radius; measure the real extent, do not assume |
| 10 | Terrain adaptation is clean — no hard seams, no buildings half-buried, bridges connect |
| 11 | A player can traverse the zone, and it reads as a drained city rather than scattered debris |

Level 9b is the one that will surprise you. `concentric_rings` distance and spread are in **chunks**,
and the relationship between those numbers and a felt 1000-block radius is not obvious. Build three
pieces, generate, measure, then tune — before authoring eighty.

## 10. Dependencies

Blocked on `WORLD_STRUCTURE.md` B-12: the Drained Grove is a biome in an Overworld that does not yet
generate Alfheim. Piece authoring (§5) is *not* blocked and can begin as soon as the pack boots —
building NBTs needs only a creative world.

---

## 11. The village problem — observed 2026-09-04, and it is a real one

**User, after playing a fresh world:** *"we need a definitive pass on structures to get us better
elven villages. The scattered houses with a few cobwebs and missing blocks is not a
Lothlorien-esque tree village."*

Correct, and the gap is architectural rather than decorative. `tools/gen_elven_ruins.py` does
exactly what it was designed to do — it takes MythicBotany's three house NBTs, chains them into
clusters, and applies a `block_rot` + rule processor so they arrive decayed. That was the right
*first* move: §3.3 argues for decaying procedurally instead of authoring ruined copies, and it
still stands.

But it can only ever produce **damaged versions of the three buildings the mod ships**, and those
three are ground-level cottages. No amount of processor work turns a cottage into a canopy.

### 9.1 What is actually missing

| Have | Need |
|---|---|
| 3 ground cottages, decayed | Dwellings **in the boughs** |
| Clusters of 2–4 | A settlement with a centre and edges |
| Cobwebs and missing blocks | Collapse that reads as *causal* — a bridge fell, so what it carried fell |
| Nothing vertical | The vertical connective tissue: stairs, spiral trunks, rope, platforms |
| — | **Bridges between trees.** This is the single most identifying feature and there are none. |

§5's piece inventory already lists `buildings/canopy` (8–12) and `bridges/span` (6–10 with
collapsed variants). **None of it is built.** The inventory was written and never executed, and
what generates today is the MythicBotany fallback.

### 9.2 Why this is now cheaper than when §5 was written

`tools/gen_spawn_hub.py` proved the whole pipeline in one pass: `tools/nbt.py` writes real
structure NBT, `check_spawn_hub.py` asserts the 48³ limit and that every jigsaw target is
answered, and the Greatbole is four pieces stacked vertically through `rollable` joints — which
is exactly the mechanism a canopy village needs, pointed sideways instead of up.

A tree-village is a jigsaw of platform pieces socketed onto bough pieces. We have built and
validated that shape once already.

### 9.3 The constraint that shapes everything

**Do not modify MythicBotany's NBTs.** They are third-party art (`INSTRUCTIONS.md` §6.6). Ours
are additive: new pieces in our namespace, joined to the same pools so the two coexist. The
existing decay processor then applies to both, and MythicBotany's cottages become the
*ground floor* of a settlement whose upper storeys are ours — which is a better outcome than
replacing them.

### 9.4 Sequenced

Deliberately **after** the Greatbole is proven in a world (`SPAWN_HUB.md` pass 2). The Greatbole
is one tree; a village is dozens. Getting the trunk-and-bough jigsaw right once, at a scale where
a fault is obvious, is what makes the village pass affordable.

| Pass | Work |
|---|---|
| 1 | Bough and platform pieces; prove a single tree can carry a dwelling |
| 2 | Bridges, including collapsed variants — the identifying silhouette |
| 3 | Settlement layout: centre, edges, civic pieces |
| 4 | Causal collapse — damage that propagates along what it was carrying |
| 5 | Density and placement against the Hollow Court's `concentric_rings` |
