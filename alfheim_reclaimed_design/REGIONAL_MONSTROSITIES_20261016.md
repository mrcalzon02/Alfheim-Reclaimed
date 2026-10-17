# Regional monstrosities: first three-region rebuilding pass

This pass rebuilds three existing regional appearances, each across the Bound,
Shrouded and Crowned skin selections: nine appearances in the 390-entry catalogue.
It continues the two earlier Silverbark Boneguard and Mire Riftmite models.

| Habitat | Creature | Authored anatomy | Skin |
|---|---|---|---|
| Ashen Grove | Ashen Revenant | Forward-set heavy torso/head, protruding jaw, broad arms | Charcoal skin, hollow sockets, sparse ember seams |
| Starved Reach | Rime Outcast | Narrow long face and nose, lean torso and arms | Frost-pale face, worn blue coat, three cold palettes |
| Void Verge | Verge Riftwalker | Narrow trunk, long limbs and split fingers, extended chin | Dark rift skin, restrained pale fissures, aligned luminous eyes |

The three styles share a body within each habitat. They are intentionally skin
variations, not nine different anatomies. There are no new entity registrations
or extra natural-spawn entries. Existing appearance NBT, saved IDs, loot, combat,
movement and equipment rules remain. Regional selection follows the creature's
stored birth-biome profile; crossing a biome boundary does not change its body.

Native zombie, illager and enderman models own the animation. Open and crossed
illager arms remain mutually exclusive. The Riftwalker's custom 64px UV map has a
matching transparent eye layer; other endermen keep their normal eye texture.
Renderer model swaps are restored after every draw to prevent leakage between
different profiles of the same species.

`RegionalMonstrosityModels.java` owns body geometry; the finite region dispatch
selects exactly one biome per species. `tools/regional_monstrosity_skins.py` owns
the nine UV skins and Verge eye map. Baked head models are exported into
`tools/themed_enemy_head_geometry.json`; the generator checks source hashes so
stale heads cannot silently survive a regional geometry change.

Java17 build and the 70-test regression pass cover native constructors, required
animation/equipment channels, finite nondegenerate cubes, region dispatch and
all 390 head exports. Static checks verify source equality, ordered item model
predicates, existing biome coverage, three distinct skin payloads per new family
and eye-map alpha/size. Full-body neutral-pose review is generated from actual
baked cubes and shipped skins, rather than a concept painting.

Acceptance: static/build validated. Client animation, lighting, equipment clipping
and combat visual acceptance remain pending. The prior 390-item dedicated-server
proof remains historical evidence for the unchanged selection/spawn mechanics;
it does not certify these new client visuals. Restart Minecraft to load the models.

Preview: `tools/regional_monstrosities_review.png`.
