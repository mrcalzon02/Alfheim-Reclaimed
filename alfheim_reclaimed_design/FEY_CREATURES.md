# Fey Creatures — entity texture and model-fit direction

**Role:** authoritative visual-design record for Alfheim Reclaimed's custom Fey creature entities.
**Status:** `runtime observed` 2026-09-04 — the creature concepts and models are accepted, but the first in-world review opened a texture/skin refinement pass before the suite is production-ready.
**Authority:** subordinate to `INSTRUCTIONS.md`. This record governs the custom Fey entity art under `kubejs/assets/alfheim/models/entity/` and its paired textures; it does not replace gameplay, spawn, balance or ecology records.

---

## 1. Runtime verdict

The custom Fey creatures themselves are working visually as concepts. Their silhouettes, identities and overall creature designs are worth keeping. The problem is narrower: **the skins are a little wrong for the models they are wrapped around.**

The first live review found three recurring visual defects:

1. **Stretching and compression.** Some markings, gradients and material detail distort across model faces or joints instead of following the actual geometry.
2. **Uneven detail density.** Some regions are comparatively rough or under-resolved while others carry more high-frequency texture information than the model can use, creating a noisy or over-detailed read.
3. **Model/skin disagreement.** A texture can be attractive on the atlas and still fail on the entity when important edges, material transitions, facial features, plates, membranes, fur, crystal facets or decorative markings do not line up with the geometry that is meant to carry them.

This is therefore a **fitting and restraint pass, not a creature redesign**. Do not throw away successful silhouettes or replace the Fey suite merely because the skin work needs tuning.

---

## 2. The model is the texture's source of truth

Every texture revision must be judged on the rendered entity, not on the flat PNG by itself. The relevant asset is the complete model/UV/texture combination.

The custom suite already includes a broad set of entity models under `kubejs/assets/alfheim/models/entity/`, including creatures such as the Crown Stag, Dream Moth, Crystalback, Grove Behemoth, Ley Manta, Mirror Hart, Mist Sylph, Rune Spirit, Shard Serpent, Song Sprite, Veil Serpent, Waylight Spirit, Bloom Wisps and the Bifrost entities. The refinement standard applies across that suite rather than to one unusually visible creature.

### 2.1 Texture-fit rules

A finished Fey skin should satisfy all of the following:

| Requirement | Acceptance read |
|---|---|
| **UV fit** | Lines, gradients and motifs follow the intended body surface without obvious stretching, compression or discontinuity. |
| **Consistent apparent texel density** | Head, torso, limbs, wings, horns and accessories do not look as though they were painted at radically different resolutions unless that difference is deliberate. |
| **Geometry-aware detail** | Facial features, joints, membranes, armor/plate boundaries, crystal facets, fur transitions and decorative markings land where the model gives them a physical reason to exist. |
| **Controlled high-frequency detail** | Micro-noise and tiny surface variation are reduced where they turn into visual grit at normal gameplay distance. More pixels are not automatically more finish. |
| **Readable material planes** | The large color/value/material regions remain legible while the creature moves. Broad form wins over texture noise. |
| **Seam integrity** | UV islands do not produce conspicuous breaks at shoulders, necks, tails, wings, limbs or mirrored surfaces. |
| **Identity preservation** | The creature remains recognizably the same design after refinement. This pass polishes the established art direction rather than replacing it. |

Where a bad result is caused by the texture, repair the texture. Where the live render proves that a UV island itself is malformed or has unusably uneven scale, correct the UV/model mapping at the authoritative model rather than painting increasingly elaborate compensation into the skin.

---

## 3. Detail hierarchy

The Fey suite should look intentionally stylized for Minecraft rather than like high-resolution concept art shrunk onto low-poly geometry.

At ordinary play distance, the player should first read **silhouette, dominant material, face/head orientation and one or two signature markings**. Secondary patterning should become visible as the player approaches. Fine surface texture should be the last layer, not the first thing the eye sees.

That means reducing unnecessary pixel-scale noise in regions that are currently too detailed, cleaning rough transitions where the atlas resolution is being asked to carry more information than the model supports, and using larger coherent shapes where a stretched face would otherwise smear fine detail. A less busy skin that fits the geometry correctly is preferable to a more intricate skin that looks painted over the model.

Creature families may still have different texture character — crystalline creatures should not be flattened into the same surface treatment as furred, spectral, vegetal or membranous Fey — but they should share the same **level of finish and visual discipline**.

---

## 4. Animation is part of texture QA

A texture can look correct in a static model viewer and fail as soon as the model moves. Stretching around shoulders, legs, jaws, wings, tails and other articulated parts must be reviewed in representative animation states.

For each creature or model family, the refinement pass should inspect at minimum:

- idle/rest pose;
- locomotion or flight;
- attack/action pose when the entity has one;
- major turns, wing extension, jaw movement or other high-deformation motion specific to the model;
- close inspection and ordinary gameplay viewing distance.

The acceptance image is the entity **in the world and in motion**, not the texture atlas in isolation.

---

## 5. Refinement workflow

1. Capture representative in-game views of each custom Fey family, including the most visibly distorted animation poses.
2. Mark stretching, seam failures, rough transitions, over-detailed/noisy regions and areas where motifs do not respect model geometry.
3. Correct UV/model mapping only where the mapping itself is the defect; otherwise leave successful models alone.
4. Retune the skins to the actual UV shapes, normalize apparent detail density and simplify excessive high-frequency detail.
5. Re-test the edited entities in motion and at normal gameplay distance.
6. Compare the result against the previous version so that refinement does not erase the identity or material language that already works.

**Production acceptance:** no custom Fey entity is accepted merely because it has a unique texture and renders without a missing-texture error. It must look deliberately fitted to its model, remain readable in motion, avoid conspicuous stretching and inconsistent detail density, and fit the visual scale of Minecraft while preserving the creature design that the runtime review already found successful.
