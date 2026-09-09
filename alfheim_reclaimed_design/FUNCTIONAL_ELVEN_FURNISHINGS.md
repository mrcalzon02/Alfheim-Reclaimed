# Functional Elven Furnishings

**Role:** implementation-facing contract for custom elven furnishing blocks whose interaction matters as much as their silhouette.

**Status:** Manna Stone Storage and the seven-block fixed-container wave are implemented and statically built in Alfheim Leyworks. The first three statues, large crystal plinth, observatory prism stand and gemstone embellishments are registered/generated scenery blocks. Runtime acceptance remains pending.

## 1. Vocabulary

The functional set complements Royal Tile Set I rather than replacing it. Royal tiles explain a room visually; these blocks provide bounded, legible interactions without turning every prop into a machine.

| Family | First blocks | Functional contract |
| --- | --- | --- |
| Chests and coffers | royal chest, gemstone coffer, archive coffer | 18–54 ordinary inventory slots; no automatic loot unless the structure owns a separate loot table |
| Crates and service containers | Dreamwood crate, provision crate, scroll crate | 27 slots with material-specific silhouettes; hopper-compatible where practical |
| Vases, pots and urns | tall vase, garden pot, memorial urn | small 9-slot contents or plant socket according to the object; never a disguised full chest |
| Statues | ancestor statue, oathkeeper statue, mourning figure | inspectable cultural/lore focus; optional structure-owned interaction, never passive progression power by default |
| Crystal plinths | large crystal plinth, observatory prism stand | display/illumination socket for one crystal or governed structure component |
| Gemstone embellishments | wall jewel, floor inlay, finial gem, storage gem | reusable visible gem accents and the data-driven upgrade vocabulary for Manna Stone Storage |

### Implemented fixed-container wave

| Block | Capacity |
| --- | ---: |
| Royal Elven Chest | 54 slots |
| Gemstone Coffer | 18 slots |
| Dreamwood Crate | 27 slots |
| Provision Crate | 27 slots |
| Scroll Crate | 27 slots |
| Tall Elven Vase | 9 slots |
| Memorial Urn | 9 slots |

All seven use persistent inventories, the synchronized wide-vault interface, comparator output, recoverable contents, directional custom models and distinct Spine-routed recipes. Locked slots are genuinely unavailable to player insertion rather than merely hidden by the screen. `/function alfheim_leyworks:functional_elven_containers/review` places these seven alongside Manna Stone Storage.

### Implemented sculptural-detail wave

The scenery registry adds two-block Ancestor, Oathkeeper and Mourning statues; a two-block Large Crystal Plinth; an Observatory Prism Stand; and wall-jewel, floor-inlay and finial gemstone embellishments. These are intentionally decorative until a later structure or quest explicitly owns an interaction. `/function alfheim:elven_sculptural_details/review` places the complete review gallery.

## 2. Manna Stone Storage

The block is a large amethyst-like mana gem held above a gold and pale-stone cradle. It is a real persistent inventory, not decorative storage.

- Base capacity: **27 slots**, one chest-equivalent.
- Upgrade interface: use an accepted gemstone on the block.
- Each installed gemstone adds **27 slots**.
- Maximum: three installed upgrades, **108 slots / four chest-equivalents** total.
- Upgrade inputs are controlled by `alfheim_leyworks:manna_storage_gems`; the initial pack accepts Mana Diamonds and Dragonstones.
- The interface is a single 18×6 vault view. Inactive capacity is visible but locked, so expansion is understandable without paging or hidden sub-inventories.
- Installed gems are persisted separately from contents and are returned when the block is broken.
- Comparator output reflects inventory fullness. The block is directional, has non-cube collision, and brightens with installed-gem tier.
- Crafting is routed through the Spine of Leaf using Dreamwood, Elementium, Elf Quartz and a Mana Diamond.

This is deliberately AE-like only in the **installable capacity** idea. It does not create a network, remote terminal, item type partition, digital byte accounting or infinite nesting.

## 3. Boundaries

Functional storage may not be used to smuggle guaranteed progression loot into ruins. Structure loot remains governed independently. Vases and urns stay small; statues and plinths do not become passive buffs until a separate gameplay design establishes cost, limits and progression placement. No container accepts itself through an automation route if that would permit recursive storage exploits.

## 4. Acceptance

Static acceptance requires Java compilation, deterministic generated resources, valid blockstate/model/loot/recipe/tag JSON, client/server jar equality, and the pack dependency/feature-order checks. Runtime acceptance still requires exercising every fixed capacity, save/reload persistence, shift-clicking, breaking containers, verifying content and gem drops, comparator behavior, multiplayer synchronization and all three review galleries.

## 5. Exotic domestic expansion

`tools/exotic_elven_home_catalog.json` extends the household vocabulary by 32 semantic assets in seven families: light/song, reflection/memory, living botanical craft, hospitality, textile/repose, scholarly curios and domestic service. The set includes starbell chandeliers, moonmirrors, dream clocks, levitating planters, nectar fountains, bottled auroras, miniature ley gardens and similarly non-human domestic forms.

The first eight-object exotic pilot is now registered/generated: Starbell Chandelier, Moonpool Lamp, Whisper Harp, Moonmirror, Levitating Planter, Nectar Fountain, Bottled Aurora and Miniature Ley Garden. `/function alfheim:exotic_elven_home/review` places the pilot gallery. The remaining 24 catalog entries remain designed but unimplemented.

Names that imply behavior remain decorative candidates until their mechanics receive an explicit cost, progression and persistence contract. A “self-warming hearth,” for example, may glow and visually imply enchantment without becoming free furnace power by accident.
