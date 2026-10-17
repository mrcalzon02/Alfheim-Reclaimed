# Crown of Eternity

Minecraft Java 1.20.1 / Forge 47.4.10. Additive companion-mod content. No world-generation changes.

The Jeweller's Eternity Setter, a gold-and-platinum crown, and the next Eternity Inlay combine in any crafting grid with three available slots. The setter returns after every use. The crown keeps its custom name and other saved data, records its completed inlays, and becomes the Crown of Eternity after the final setting. Incorrect, repeated and out-of-order inlays cannot match the setting recipes. Recipe previews include the actual resulting progress, rather than displaying an empty crown for every step.

The fixed roster is the existing 232-entry gemstone catalogue, including organic gems and the five reused vanilla gemstone items. Twenty-nine inlays each contain eight different gems around a platinum ingot. Across all inlays every catalogue gem appears exactly once. A catalogue change requires a deliberate migration; it cannot silently reinterpret old crowns.

Crafting route:

1. Eight raw gold blocks around blaze powder make one Auriferous Platinum Concentrate. Blast it for 60 seconds to recover one platinum ingot. This is an authored fantasy refining recipe, not a geological yield claim.
2. Nine platinum ingots compress into a Dense Platinum Billet; it unpacks without loss.
3. Eight gold blocks around a platinum billet make one Royal Gold and Platinum Crown Segment.
4. Eight crown segments around a nether star forge the Gold and Platinum Crown.
5. Two diamonds, a platinum ingot and a blaze rod make the reusable setter.
6. Craft and set all 29 inlays. The crown tooltip lists the next inlay and its eight gems; each inlay also lists its contents. Obtaining raw gold unlocks the metal recipes; obtaining the crown unlocks the inlay and setting recipes.

Total project cost, including setter: **64 gold blocks, 102 platinum ingots, one nether star, two extra diamonds, a blaze rod, and one of each of the 232 gemstones.** Refining that platinum consumes **816 raw gold blocks (7,344 raw gold), 102 blaze powder and blast-furnace fuel**. Raw gold is distinct from smelted gold; the refining route deliberately requires mined material. The crown itself accounts for 101 platinum ingots, and the reusable tool for one.

Both crown forms equip in the helmet slot. This is cosmetic regalia with no combat attributes or durability loss. The item model and worn model share a hollow gold circlet, platinum mouldings, fleurons, bezels and exactly 232 colored gem settings; installed gems appear with crafting progress. The completed crown has epic rarity, enchantment glint and a challenge advancement. No unrequested combat powers were added.

Generator: `tools/gen_eternity_crown.py`, using the installed local Continuity Works `StructureCapability` with provider `alfheim_eternity_crown_v1`. Emitted recipes use the verified installed vanilla registry and the existing gemstone catalogue. `tools/eternity_crown_generation.json` records the actual snapshot and artifact hashes. No independent structures are placed, so structure spacing is not applicable.

Validation: see `tools/eternity_crown_build.json` for the installed jar hash and source/package audit. The offline native geometry preview is `tools/eternity_crown_review.png`; it is not a game capture. Live recipe transfer, repeated/shift crafting, save/reload, equipment rendering and multiplayer remain pending in Minecraft. Existing third-party jars, recipes and world generation remain intact.
