# Reclaimed Armory texture source prompts

The six 2048×768 source atlases were generated as production references, then processed by
`tools/gen_armory.py`. Each prompt requested an eight-column by three-row sprite atlas: four
class weapon/offhand forms followed by helmet, chest, leggings and boots. Rows represented simple,
refined and intricate construction. The shared direction was crisp elven fantasy equipment,
strong readable silhouettes, restrained ornament at low tiers, ceremonial detail at high tiers,
consistent lighting, isolated objects, no labels, and a transparent background.

Class-specific direction:

- **Thornwarden / Warrior:** dreamwood, bark, thorn, leaf and green-gold plate; leafknife,
  root axe, reed spear, bark shield and heavy grove armor.
- **Waywatcher / Hunter:** pale bow wood, briars, wind-shaped limbs, leather and silent green
  trail gear; bow, crossbow, trail blade and spirit charm.
- **Leyweaver / Sorcerer:** pale branchwood, prismatic crystals, blue-gold ley lines and flowing
  cloth; focus, rune blade, glass spear and spell folio.
- **Rootspeaker / Shaman:** roots, antler, rain-dark wood, turquoise storm stones and mossed
  ritual cloth; crook, tide spear, grove axe and root tablet.
- **Duskkeeper / Warlock:** bone-pale wood, mourning silver, grave violet, name leaves and worn
  funerary cloth; reliquary focus, dusk blade, gloam bow and memory ledger.
- **Dawnsinger / Minstrel:** ivory dreamwood, dawn gold, ribbons, laurel and resonant crystal;
  tuning focus, dance blade, chord crossbow and court songbook.

The image generator did not reliably honor transparency: several atlases contained an opaque
checkerboard or white field, while the others still carried unwanted edge/background pixels.
Every source therefore goes through the same Pillow cleanup regardless of its apparent alpha:

1. Flood-fill light neutral pixels connected to the image edge.
2. In bow, crossbow and necklace cells, also remove large neutral background components enclosed
   by curves, strings, limbs and chains; these islands cannot be reached by an edge-only flood fill.
   The thresholds are family-specific so pale Dawnsinger crossbow limbs are not mistaken for the
   white generator background.
3. Write removed pixels as literal RGBA `(0, 0, 0, 0)`.
4. Crop each atlas cell, resize with antialiasing and quantize its palette.
5. Strip quantization haze at alpha 16 or below back to literal transparent pixels.
6. Reject an export with a nontransparent corner, fewer than 20 transparent pixels, fewer than
   20 foreground pixels, or a cleaned source with less than 35% alpha-zero area.
7. Reject any bow variant whose curve does not contain an enclosed alpha-zero region of at least
   20 pixels at the final 32×32 resolution.
8. Reject crossbows without a measurable enclosed alpha-zero opening and reject necklaces without
   a transparent chain loop. Necklace sprites retain only their principal connected foreground
   component, removing side fragments spilled into their atlas cell by adjacent artwork.

`tools/armory_manifest.json` records the source hashes and per-class alpha ranges. The images in
`visual_review/` deliberately draw a checkerboard behind final sprites for halo inspection; that
checkerboard is part of the review sheet only, not part of any production texture.
