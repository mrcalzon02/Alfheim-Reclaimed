# Void Margins — additive landmark family

**Role:** implementation-facing extension of `TERRAIN_AND_STRUCTURES.md` for the later user-requested floating geodes, astral towers and ley-line focus nodes.
**Status:** static implementation; fresh-world placement and client traversal pending.
**Source:** `tools/void_landmarks_manifest.json`.
**Generator:** `tools/gen_void_landmarks.py`.
**Checker:** `tools/check_void_landmarks.py`.

## Authority and scope

The twelve structures in `TERRAIN_AND_STRUCTURES.md` remain the **biome-core coverage set**: two terrain-supported ruins for each of the six Void Margin environments. This later landmark family is additive and does not replace, renumber, or satisfy those twelve coverage slots. It exists because the user subsequently requested another class of Void content: floating geodes, astral towers and ley-line focus nodes.

All six Void Margin biome IDs are already live: Void Verge, Shatterfields, Prism Drift, Rootfall, Sepulchral Reach and Starless Reach. This first landmark admission nevertheless targets only `alfheim:void_verge`. That biome occupies the continuous safe rim. The sibling biomes extend into debris and terminal bands, and a plain biome tag cannot by itself distinguish a supported fragment from the guaranteed-empty `< -0.94` far field. Expanding placement before that filter exists would violate the empty-horizon contract.

The landmark family therefore uses one conservative admission rule now and can be redistributed later when a continentalness/support-aware placement gate can prove the host. Starless far-field placement remains forbidden.

## Family 1 — floating geodes

Two genuinely suspended formations are authored: **Prism Drift Geode** and **Starfall Geode**. They are not substitute islands. Their templates contain no foundation, no hidden terrain fill and use `terrain_adaptation: none`. The start is projected from the local surface and raised ten blocks, leaving the whole formation visibly clear of the host shelf.

Prism Drift Geode uses Prismstone and Aetherquartzite with luminous Seamstone ribs. Starfall Geode uses Nightmantle and Astralite with Veilstone structure. Each is hollow, opened broadly on one face, and carries a central crystalline axis so the player reads the object as a fractured mana-geode rather than a random stone ball. These are landmarks in this pass, not a new processing route and not a replacement for the existing buried Rim geode resource feature.

## Family 2 — astral towers

**Astral Watchtower** and **Nightglass Spire** are observatories built to study the broken edge and old ley sky. Both use `terrain_adaptation: none`; neither invokes the old Verge Spire `island` behavior. The lowest disc is architectural footing only, no larger than the tower mass it carries.

Astral Watchtower combines Anchorstone, Veilstone, Astralite and Seamstone around an open orrery crown. Nightglass Spire combines Nightmantle, Aetherquartzite and Glintschist around a dark lens. Both contain multiple interior decks, a continuous central climb path and cardinal observing slits. Their source contract requires a substantial existing host volume. That metadata is not a claim that vanilla jigsaw placement has already measured it; fresh-world placement remains the acceptance gate for support and edge interaction.

## Family 3 — ley-line focus nodes

**Ley Focus Ring** and **Fractured Ley Focus** are compact civic/magical infrastructure remnants, not functional mana generators. Each leaves its centre open, uses a ring footing, raises multiple pylons and suspends one focus stone where ley energy would once have converged.

The intact ring uses Anchorstone, Seamstone, Veilstone and Astralite. The fractured node uses Shardbreccia, Glintschist, Riftshale and Seamstone. They require less host mass than the towers but still declare a non-zero host-volume requirement. They do not generate a rescue island.

## Placement and overlap contract

The six physical templates are exposed through three template pools and three jigsaw structure registrations, all using `terrain_adaptation: none`. The three structure registrations share one weighted `random_spread` structure set rather than three independent sets. A candidate cell therefore selects **one** family (geode, tower or focus) by manifest weight; the three landmark families cannot select the same random-spread cell and stack on one another.

This is a distinct additive landmark source family, not an alternate implementation of the twelve Surface Works Void ruins. It reuses the repository's canonical `structure_nbt.py` primitive and the existing geometry helpers from `gen_surface_works.py`; it does not fork those primitives or modify third-party jars.

## Acceptance boundary

Static acceptance requires exactly three families and six templates, all template axes at or below 48 blocks, one shared structure set, one conservative Void Verge biome tag, valid registered block IDs, no terrain adaptation, no generated support island, and source-to-shipping equality. JSON is compared structurally and NBT semantically so gzip timestamps cannot masquerade as content drift.

Fresh-world acceptance requires at least three separated Verge samples. Observe actual tower/focus support, geode clearance, approach safety, visibility from inland, absence of overlaps, and no landmark placement beyond the safe rim. Only after those observations may sibling-biome placement be considered; expanding the tag is not itself a support solution.
