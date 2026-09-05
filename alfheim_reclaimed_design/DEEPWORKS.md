# Deepworks — implementation plan for Alfheim's living underworld

**Role:** build-ready design record for the Deepworks terrain province and its material set.
**Status:** `implementation ready — not yet built or runtime validated`.
**Authority:** subordinate to `INSTRUCTIONS.md`; expands `THE_DEEP.md` §5 and does not replace the
Quarries, Tombs or Faultworks described there.
**Runtime priority, 2026-09-04:** the pack now boots successfully. The next environmental pass can
therefore stop being speculative and move into actual block registration and fresh-world generation.

---

## 1. What the Deepworks is

The Deepworks is not "the Nether under Alfheim" and not a generic cave reskin. It is the place where
the mana lost by the surface collected, heated the livingrock, and changed the geology without ever
ceasing to be *Alfheim*.

The visual thesis is:

> **The surface is mana-starved. The deep is mana-saturated.**

The rock has cracked under magical pressure, lava lakes occupy the lowest cavities, elemental mana
has vitrified parts of the walls, and the existing crystalline alignments have grown to architectural
scale. Ruins, quarries and tombs found here should look like elven works swallowed by this process,
not like structures pasted into an unrelated cave biome.

This document deliberately separates the **materials**, which can be built now, from the
**gargantuan cavern generator**, which must be tuned with live worlds.

---

## 2. The first material set — build these now

The initial set remains exactly the four forms already established in `THE_DEEP.md`. The correction
is that Mana-glass is represented by six aligned variants rather than pretending one ordinary block
can dynamically inspect the nearest crystal at render time.

| ID | Display name | Role | Initial behaviour |
|---|---|---|---|
| `alfheim:cracked_livingrock` | Cracked Livingrock | transition stone | mineable stone; faint seam light; drops itself |
| `alfheim:magmatic_livingrock` | Magmatic Livingrock | deep hot stone | mineable stone; strong emissive seams; drops itself |
| `alfheim:livingrock_slag` | Livingrock Slag | cooled runoff/debris | brittle; dark; no resource value; no normal drop |
| `alfheim:mana_glass_fire` | Fire Mana-glass | Emberglass-aligned vitrification | translucent; warm light |
| `alfheim:mana_glass_water` | Water Mana-glass | Tidewake-aligned vitrification | translucent; cool light |
| `alfheim:mana_glass_earth` | Earth Mana-glass | Rootglass-aligned vitrification | translucent; subdued light |
| `alfheim:mana_glass_air` | Air Mana-glass | Galeglass-aligned vitrification | translucent; pale light |
| `alfheim:mana_glass_shadow` | Shadow Mana-glass | Duskglass-aligned vitrification | translucent/dark; little or no emitted light |
| `alfheim:mana_glass_light` | Light Mana-glass | Dawnglass-aligned vitrification | translucent; strongest light |

The six variants map directly to the six crystal alignments already authored in
`tools/crystals_manifest.json`:

```text
Emberglass  -> fire
Tidewake    -> water
Rootglass   -> earth
Galeglass   -> air
Duskglass   -> shadow
Dawnglass   -> light
```

Worldgen chooses the aligned Mana-glass variant belonging to the nearby crystal or ley formation.
That preserves the original design statement — *the glass takes the colour of the mana around it* —
without requiring every block to be a ticking block entity or a runtime neighbourhood scanner.

---

## 3. Mechanical properties

### 3.1 Cracked Livingrock

Cracked Livingrock is the **pressure warning**. It should appear before the player reaches the hottest
part of a cavern and around Faultworks, lava chambers and ley scars.

Initial properties:

- hardness and blast resistance close to ordinary livingrock, not deepslate;
- pickaxe mineable and tool-required;
- self-drop;
- low light level, just enough for fissures to remain legible in darkness without lighting the cave;
- no damage effect and no special crafting requirement in the first pass.

It must still read as livingrock first. The texture is the existing stone with irregular fine cracks,
not a generic cracked-stone tile.

### 3.2 Magmatic Livingrock

Magmatic Livingrock is livingrock close to melting, not ordinary magma block.

Initial properties:

- slightly tougher than cracked livingrock;
- pickaxe mineable and tool-required;
- self-drop;
- high light level from internal seams;
- no bubble-column behaviour and no automatic substitution for `minecraft:magma_block`;
- no movement damage in pass one unless the KubeJS callback is proven in the running game.

The eventual gameplay hook may make standing on exposed Magmatic Livingrock dangerous, but that is a
runtime-tested enhancement, not a reason to guess at an API while registering the foundation block.

### 3.3 Livingrock Slag

Slag is a **world-history block**, not a new ore.

Initial properties:

- low hardness;
- pickaxe mineable;
- drops nothing under ordinary mining;
- no recipes that turn it into progression materials;
- generated as crusts, runoff tongues and old lava high-water marks.

Its job is to show where molten livingrock cooled. If players start quarrying slag because it is the
best source of something, the block has failed its design role.

### 3.4 Mana-glass

Mana-glass is rock vitrified by a ley-line/crystal alignment. It is environmental evidence first and
a decorative reward second.

Initial properties:

- glass-like hardness and sound;
- translucent/cutout-safe rendering;
- Silk Touch/self-drop behaviour preferred; without Silk Touch it should either drop nothing or a
  deliberately small shard-like residue after the loot API is proven;
- colour and emitted light come from alignment;
- no automatic redstone, potion or mana-generation behaviour in the first pass.

The block must not become a free alternate crystal economy. The actual six crystals remain the
progression-bearing resource; Mana-glass is the geological scar they leave around themselves.

---

## 4. Texture and asset pipeline

The Deepworks blocks should be generated by a **sibling pipeline**, not hand-edited into
`13_crystals.js`.

Create:

```text
tools/deepworks_manifest.json
tools/gen_deepworks.py
kubejs/startup_scripts/14_deepworks.js
kubejs/server_scripts/14_deepworks_loot.js
kubejs/assets/alfheim/textures/block/...
kubejs/assets/alfheim/models/block/...
kubejs/assets/alfheim/models/item/...
```

`gen_deepworks.py` should locate the installed Botania jar and use Botania's livingrock texture as
the **local derivation source**. It should never copy the jar into the repository. The generator is
responsible for deterministic overlays and can therefore be rerun whenever the source asset changes.

Texture rules:

- **Cracked Livingrock:** retain most original livingrock pixels; add a deterministic branching crack
  mask with a very restrained emissive seam palette.
- **Magmatic Livingrock:** darken the base selectively around broader fissures; fissures carry the
  hot colour. Do not tint the whole stone orange.
- **Slag:** cool and darken the livingrock, break up the original smoothness with rough vitrified
  patches and small trapped-bubble marks.
- **Mana-glass:** use one common glass structure and colour it from the six hue/saturation/value
  entries in `crystals_manifest.json`. The alignment palette therefore has one source of truth.

All generated textures should be deterministic from a fixed seed. Re-running the generator with no
manifest/source change must produce byte-identical output.

---

## 5. Registration and tags

The generated startup script owns all block registration. At minimum it must attach:

```text
minecraft:mineable/pickaxe
alfheim:deepworks_stone          cracked + magmatic + slag
alfheim:deepworks_hot_stone      magmatic
alfheim:mana_glass               all six glass variants
alfheim:deepworks_replaceable    cracked + ordinary livingrock where appropriate
```

Do **not** add the material set to broad vanilla stone/ore replacement tags merely to make worldgen
convenient. The pack already removed the old global livingrock-as-vanilla-stone shortcut. Deepworks
features should target Alfheim-specific tags directly.

A single `tools/check_deepworks.py` validator should prove:

- every manifest block is registered exactly once;
- every texture/model referenced by registration exists;
- every aligned Mana-glass variant maps to an existing crystal alignment;
- generated source and shipping files match;
- no broad vanilla ore-replaceable tags were modified.

---

## 6. Geological grammar

The Deepworks is built in layers so the player can read increasing heat and mana pressure while
moving downward or toward a major cavern.

### 6.1 Transition shell

**Approximate initial range:** y 0 to -24, plus local halos around major deep caverns.

Ordinary livingrock remains dominant. Cracked Livingrock appears in veins and sheets, becoming more
common near openings. Small Mana-glass traces can occur where a crystal alignment crosses the shell,
but Magmatic Livingrock is rare.

### 6.2 Active Deepworks

**Approximate initial range:** y -20 to -52.

This is the main cavern province. Cracked Livingrock is common along walls and ceilings. Magmatic
Livingrock appears around lava and ley scars. Mana-glass becomes visible in aligned seams, large
crystal formations and fault surfaces.

### 6.3 Basal furnace

**Approximate initial range:** y -48 to -64.

Lava lakes become substantial. Magmatic Livingrock forms the immediate shore and underside of hot
formations; Slag records former levels and cooled overflow. The lowest reachable cavities should be
beautiful and materially rich but physically difficult to traverse.

The ranges overlap intentionally. The Deepworks should not produce three horizontal stripes.
A separate low-frequency 3D field expands and contracts each layer so hot stone can climb around a
ley scar and cool stone can descend in stable pillars.

---

## 7. Gargantuan cavern generator — target shape

The cave system needs a distinct scale class rather than simply increasing vanilla cave frequency.
The desired spaces are chambers tens to hundreds of blocks across, connected by large throats and
interrupted by intact livingrock masses.

The initial target envelope is:

- major chambers roughly **48–160 blocks** across;
- occasional linked chambers producing complexes **200–400 blocks** end to end;
- ceilings commonly **25–70 blocks** above the floor;
- rare vertical chimneys connecting deep layers to ordinary cave systems;
- enough solid rock between complexes that finding one remains an event.

Use a dedicated deep 3D density/noise field masked by Y rather than increasing MythicBotany's cave
carvers dimension-wide. The surface and ordinary caves outside the Deepworks must remain recognisable.

The generator should produce **void space first** and geological decoration second. Lava, crystals,
slag and ruins decorate a cavern that already has a coherent shape; they do not fake cavern scale by
placing dozens of unrelated features into a vanilla tunnel.

---

## 8. Environmental formations

### 8.1 Lava lakes

Large floor basins, not scattered single-source pockets. The immediate progression from the fluid
outward is:

```text
lava -> magmatic livingrock -> cracked livingrock -> ordinary livingrock
               \-> slag high-water marks where old levels receded
```

This material gradient is mandatory. A naked vanilla lava lake touching ordinary livingrock would
read as unfinished generation.

### 8.2 Crystal chandeliers

The existing six crystal families become oversized ceiling formations where mana pooled above lava.
They should use the same alignment pair logic as the geodes, but at a much larger silhouette scale.
A chandelier is not a geode pasted upside down: it has a thick livingrock root, Mana-glass halo,
crystal body and several descending branches.

### 8.3 Ley scars

Long fused bands cut through walls and floors. Their centre is aligned Mana-glass, bordered by
Magmatic or Cracked Livingrock depending on depth. A Faultwork structure may terminate on or exploit
a ley scar, making the natural and archaeological systems visibly connected.

### 8.4 Mineral columns

Floor-to-ceiling formations broad enough to function as landmarks and traversal obstacles. They can
carry Bloom seams and crystal inclusions. The largest columns should sometimes support quarry works,
bridges or tomb entrances.

### 8.5 Slag shelves and lava terraces

Repeated horizontal ledges around lake chambers show that the fluid level changed over time. These
are important because they turn a lava chamber from "Minecraft cave with custom blocks" into a place
with geological history.

---

## 9. Relationship to the Quarries, Tombs and Faultworks

The three archaeological families from `THE_DEEP.md` are placed **after** the Deepworks terrain and
materials exist.

- **Quarries** prefer solid walls and mineral columns, with galleries opening into major caverns.
- **Tombs** prefer stable shelves above the hottest floor, sometimes overlooking lava but never
  casually submerged in it.
- **Faultworks** prefer ley scars and the deepest transition zones; they are the structure family most
  allowed to be physically damaged by the geology.

All three need environmental anchor tests. "Generate at y -40" is not sufficient. A structure must
prove that its entry, floor and required support volume are solid before placement, or choose another
site. This is the underground counterpart to the surface structure terrain-integration rule: no
hero structure is allowed to hang halfway out of a cavern because the random spread found legal X/Z.

---

## 10. Implementation order from the successful boot

### D1 — build the blocks

Implement `deepworks_manifest.json`, `gen_deepworks.py`, registrations, models, textures, loot and
static validation. Run the generator and prove source-to-shipping equality.

### D2 — runtime block acceptance

Boot the pack, obtain every block, place them under normal and low light, mine them with intended
tools, and verify transparency/light/loot. Do this before any worldgen depends on them.

### D3 — transition geology

Add only Cracked Livingrock and small Magmatic Livingrock replacement features in controlled deep Y
ranges. Fresh world, inspect distribution, verify no surface pollution.

### D4 — cavern volume

Introduce the dedicated Deepworks density/carver field and tune **space** until the caverns have the
right scale. Do not add the spectacular formations yet; first make the room they need.

### D5 — lava and material gradients

Add proper lake basins and the lava -> magmatic -> cracked -> livingrock shore grammar, including
Slag terraces.

### D6 — alignment geology

Add Mana-glass ley scars, crystal chandeliers and mineral columns, driven by the six existing crystal
alignments rather than a separate colour table.

### D7 — archaeology

Only after the environment passes runtime inspection, build the Quarries, Tombs and Faultworks into
it and validate terrain anchoring.

---

## 11. Acceptance criteria

The material pass cannot advance to cavern generation until:

1. all nine block IDs register without startup errors;
2. every block has a correct model and texture with no missing-texture fallback;
3. Cracked and Magmatic Livingrock visibly remain members of the livingrock family;
4. Slag looks cooled and valueless rather than like an ore;
5. all six Mana-glass variants visibly correspond to the existing crystal palette;
6. transparent Mana-glass renders correctly against itself, liquids and adjacent solid blocks;
7. mining requirements and drops match this document;
8. no block registration or tag change alters ordinary Midgard stone/ore behaviour;
9. generator output is deterministic and source-to-shipping equality passes;
10. the running game, not only static files, confirms the block pass.

The cavern pass cannot be accepted until a fresh world demonstrates at least three separated
Deepworks complexes with: genuinely large chambers, coherent lava basins, readable material
gradients, aligned formations, intact ordinary rock between complexes, and no evidence that the
surface generator was globally destabilised.

---

## 12. Immediate next implementation target

The next code unit is deliberately small and concrete:

> **Build and runtime-prove the Deepworks material set before changing deep terrain.**

The successful boot means there is finally a stable enough runtime baseline to catch registration,
rendering and loot defects immediately. Once these blocks exist and are visually accepted, the cave
generator can use real materials rather than placeholder stone and the environmental tuning stops
being speculative.
