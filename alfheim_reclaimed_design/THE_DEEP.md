# The Deep — what is worth finding underground

**Role:** design record for Alfheim's underground content: the quarries the elves cut, the tombs
they left, and the reason to dig at all.
**Status:** `draft` — designed, nothing built.
**Authority:** subordinate to `INSTRUCTIONS.md`. Sits alongside `ORE_SUPPLEMENTATION.md` (which
owns the blooms and crystals) and `SPAWN_HUB.md` (which owns the surface centrepiece).
**Asked for by the user, 2026-09-04:** *"I feel like we need some kind of magical underworld
features, like deep quarries that are filled with all kinds of ores or buried ancient tombs of
the elder kings of old. Things worth finding in the deep."*

---

## 1. The gap this closes

Alfheim's underground currently contains ore and nothing else.

Twelve blooms and seven geodes generate at measurable depths — `tools/ore_chart.py` prints the
distribution — and that is the whole of it. There is no reason to go down that is not "I need
more of a thing I already know how to get". Caving is a supply run.

Compare the surface, which has a premise: a dead city, a sealed gate, a court of eight
survivors. The underground has no premise at all, which is strange for a world whose disaster
was *magical* rather than geological. Something happened here. It should be legible from below.

**The fiction the deep should carry:** the elves did not only live in the trees. They mined, and
they buried their dead, and both stopped abruptly. What is down there is not treasure left for a
player — it is a civilisation's unfinished business.

---

## 2. Three kinds of place, deliberately not one

Each answers a different question, so a player who finds all three has learned three things.

| | What it is | What it answers |
|---|---|---|
| **The Quarries** | Vast cut galleries, abandoned mid-work | *How did they get materials?* |
| **The Tombs** | Sealed barrows of the elder kings | *What did they believe?* |
| **The Faultworks** | Where a working went wrong and the rock remembers | *What actually happened?* |

### 2.1 The Quarries — industry, stopped

Deep open galleries cut into `#mythicbotany:base_stone_alfheim`, not natural caves: square
corners, pillar-and-stall floors, cut faces, rails of dreamwood. **Rich in ore by construction**
— the seams are exposed in the walls because that is what the elves were following.

- Multiple blooms visible in one place, which teaches the bloom vocabulary faster than any
  Compendium entry.
- Abandoned tools, half-loaded carts, a Petal Apothecary left in a corner — now that
  apothecaries are rare on the surface (thinned to 1-in-20 chunks on 2026-09-04), one down here
  reads as *someone worked here* rather than as scenery.
- **No mobs authored in.** The danger is the depth and the dark, and whatever wandered in.

**Depth:** y −20 to −55, under the bloom peaks so the walls actually intersect seams.

### 2.2 The Tombs — the elder kings

Sealed barrows. A tomb is a *room*, not a dungeon: an antechamber, a sealed door, a burial
chamber, and one thing worth taking.

- **Marble and quartz**, the amphitheatre's palette (`SPAWN_HUB.md` §3), so the Court and the
  tombs are visibly one culture.
- Each holds a **named king** — the Compendium can carry the names, which makes the world older
  than the player.
- The loot is **one significant item**, not a chest of commodities. A rune. A crystal of a kind
  that no longer forms. Something the Guides can reference.
- **Sealed** means sealed: the entrance is buried and must be found by reading the surface, the
  way geodes already teach with their surface markers.

**Depth:** y −10 to −40, shallower than the quarries. You find tombs by accident while mining.

### 2.3 The Faultworks — the wound, underground

The one that carries the premise. A place where a working failed catastrophically: stone fused
to glass, a ley-line severed and still discharging, Occultism's `burnt_otherstone` in quantity.

This is where **Era I's `g_occult` Guide** — *"You will find stone that is the wrong colour and
was never quarried"* — stops being a hint and becomes a location. That Guide already exists and
currently points at nothing in particular.

**Depth:** y −40 to −64, the deepest of the three.

---

## 3. What this must not become

Three failure modes, named so the build can be checked against them:

1. **A loot pinata.** `INSTRUCTIONS.md` §2.3: power and capability route through a spine. A tomb
   may hold a rune or a unique crystal; it may not hold a shortcut past an era.
2. **A parallel dungeon system.** Mine and Slash owns instanced expeditions (`MAGIC_SYSTEMS.md`
   §2.3, four mods). These are *world* features — found while mining, not entered from a device.
   If a player cannot stumble into it, it belongs to the Wound instead.
3. **Another thing that generates everywhere.** The apothecary lesson: 1-in-2 chunks is scenery.
   Quarries should be a genuine find.

---

## 4. Build order

Same shape as the spawn hub, and for the same reason — the user's own observation that
*"automated structure generation typically needs multiple passes of detailed improvement"*.

| Pass | Work |
|---|---|
| 1 | Parametric generator; one gallery piece, one tomb, one faultwork; jigsaw wiring; placement |
| 2 | Prove it: fresh world, all three findable, `locate structure` reports each |
| 3 | Ore integration — quarry walls actually intersect bloom seams |
| 4 | Tomb interiors and the named kings; Compendium entries |
| 5 | Faultwork as a place the Occultism chain points at |
| 6 | Density and depth tuning against the ore chart |

**Pass 1 depends on nothing that does not already exist.** `tools/gen_spawn_hub.py` proved the
NBT pipeline — `tools/nbt.py` writes structures, `check_spawn_hub.py` validates the 48³ limit and
jigsaw pairing — so this is the same machinery pointed downward.

---

## 5. The Deepworks — Alfheim's subterranean biome

**Added 2026-09-04 on the user's instruction:** *"massive deep caverns filled with lava and
mineralogical formations ... gargantuan cave complexes with lava lakes and distinctive mineral
formations but of our distinctly fantastical and mana-infused variety, cracked and heated and
magmatic versions of livingrock ... we need to develop this subterranean biome further with its
own in-depth environmental pass later."*

§2 describes three *places you find*. This is different in kind: a **biome**, a region you are
inside, with its own stone, its own light and its own rules. It is what §1 was really missing —
the deep needs somewhere to be, not just things to contain.

### 5.1 The premise it carries

The surface disaster was the ley-lines going out. Underground, the opposite happened: the mana
that drained out of the groves went *down*, and it is still there, molten. The Deepworks is
where Alfheim's magic pooled and cooked.

That gives it a distinct visual grammar from the Nether, which it should not simply imitate:
**Nether is dead and burning; the Deepworks is alive and burning.** Lava under a canopy of
crystal rather than lava in a wasteland.

### 5.2 Materials — magmatic livingrock

The keystone. `botania:livingrock` is the dimension's own stone and the substance every ore
feature already targets. The Deepworks needs its heated forms, and they should read as *the same
rock under pressure*, not as new rock:

| Form | Reads as |
|---|---|
| **Cracked livingrock** | Fissured, faint glow in the seams. The transitional stone. |
| **Magmatic livingrock** | Half-molten, emissive, warm to stand on. The deep floor. |
| **Livingrock slag** | Cooled runoff, brittle, drops nothing. Debris, not a resource. |
| **Mana-glass** | Where lava met a ley-line and vitrified. Translucent, coloured by whichever crystal is nearest. |

These are **new blocks** and belong to `gen_crystals.py`'s pipeline or a sibling generator — the
texture-derivation machinery already exists and would recolour livingrock cleanly.

### 5.3 Formations

Not scatter-decoration. Formations should have *causes*:

- **Lava lakes** with livingrock shores, the slag ring showing an old high-water mark.
- **Crystal chandeliers** hanging over the lakes — the geode crystals (§`ORE_SUPPLEMENTATION`)
  grown huge where heat and mana met, which ties the deep to a system the player already knows.
- **Ley-scars**: fused channels running through the rock, the underground continuation of §2.3's
  Faultworks. The two should be the same phenomenon at different scales.
- **Mineral columns** — floor-to-ceiling growths, the thing a player photographs.

### 5.4 Scale

"Gargantuan" is a constraint, not an adjective. Vanilla's largest caves come from
`minecraft:cave_cheese` noise; the Void Verge already uses that noise for its islands
(`gen_alfheim_biomes.py`), so the machinery and the tuning experience both exist.

The Deepworks needs its own carver or noise band rather than borrowing the surface one, and that
is the *environmental pass* the user has deferred. Recorded here so it is not rediscovered.

### 5.5 Sequencing

This is explicitly **later**. What matters now is that it is planned before the quarries and
tombs are built, because those must generate *inside* it rather than beside it — a marble tomb
opening onto a lava lake is a scene; a marble tomb in ordinary stone next to an unrelated lava
biome is two features that happened to collide.

**Order:** Deepworks biome and its stone → then §2's three place-types inside it.

---

## 6. Placement, and the one hard constraint

Underground jigsaw structures must declare `terrain_adaptation: none` and be placed by
`minecraft:random_spread` with a `structure_set` of their own. They must NOT be added to the
Greatbole's `continuityworks_spawn_protection` family (`BACKLOG` B-24) — that carries a 500-block
exclusion, and three underground families all claiming it would sterilise each other exactly the
way the Hollow Court's city pieces would.

**Open:** whether the quarries should intersect the Void Verge's floating islands. The islands
are livingrock and every ore feature already targets them, so a quarry hanging in the void is
mechanically free and thematically excellent. It is also the single most likely thing to generate
half-in-air and look broken, so it is a pass-3 question, not a pass-1 one.
