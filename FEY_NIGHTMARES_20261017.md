# Fey Wilds nightmares — 2026-10-17

Six additional hostile species, each with a distinct articulated native model,
three regional appearances and individually selectable matching head items.
They extend the accepted monster material/UV system; the original six remain.

| Creature | Body height | Anatomy and attack |
|---|---:|---|
| Wendigo | 3.8 blocks | Huge hunched deer skeleton, arched spine, open ribs, branching antlers, long hooked claws and cloven hooves; heavy weakening/slowing strike |
| Duskweaver | 1.55 blocks | Six-jointed-leg spider-moth, feathered antennae, skull mask, hooked mandibles and torn eye-patterned wings; leaping venom attack |
| Hollow Bride | 2.8 blocks | Broken hollow mask, thorn circlet, strand-built veil, exposed bones, tattered layered gown and dead bouquet; short-range magic soul touch causes darkness and weakness |
| Barrow Maw | 2.1 blocks | Broad fungal quadruped, enormous open skull-jaw, multiple fang rows, exposed ribs, shell plates and tiered mushroom growths; slowing/weakening bite |
| Nuckelavee | 3.2 blocks | Fused equine and humanoid skeleton/musculature, two heads, exposed ribs, ragged mane, four hooved legs and long needle-fingered arms; heavy weakening strike |
| Redcap Reaver | 1.45 blocks | Crooked goblin, patched red cap, layered lapels, buttons, pouch and pack, heavy boots and hooked cleaver; quick repeated melee attacks |

Heights are collision-body heights. Antlers, veils and headgear extend beyond
some body bounds. The Wendigo is explicitly a fictional deer-skeleton design
for this pack. Wings are modeled and animated; Duskweavers use ground movement
and leaps, rather than continuous flight. Wendigo and Hollow Bride use the
native undead creature classification.

## Regional selections

- Wendigo: Hollowwood, Barrowbone, Hoarfrost.
- Duskweaver: Gloamsilk, Sporeveil, Starless.
- Hollow Bride: Moonveil, Mourning, Rimeveil.
- Barrow Maw: Rootgrave, Mirebloom, Sepulchral.
- Nuckelavee: Brinebound, Cinderhide, Rimebound.
- Redcap Reaver: Thorncoat, Ashcoat, Frostcoat.

The new set adds 24 explicit Alfheim habitat entries: forest hollows and grave
reaches for Wendigos; infested, spore and starless regions for Duskweavers;
shore, mire and grave regions for Brides; mire, fungal and burial regions for
Barrow Maws; shore, scorched and frozen reaches for Nuckelavees; woodland,
ashen and frozen regions for Redcaps. Spawn weights are 2 except Duskweaver
(3) and Redcap (4). All groups contain one creature and use the existing
hostile darkness, ground, dimension and body-clearance checks. Existing caps
remain in force. Small loot tables use existing vanilla ingredients only.

All hits use the normal pack damage pipeline and recheck distance and sight.
There is no terrain destruction, infestation spreading, player equipment
replacement or new progression material.

## Build and review

The native model export covers all 12 different rigs and matching heads;
source, material, UV and generated-asset checks cover all 36 appearances.
This release was packaged and installed after those focused checks. No new
server boot or client gameplay review was performed for this set. The previous
`tools/monstrosities_build.json` is historical server evidence for the first six,
not proof of these additions. Current artifact: `tools/fey_nightmares_build.json`.

`tools/fey_nightmares_review.png` and `tools/fey_nightmares_detail.png` render
the actual native models and UV skins, rather than concept art or client
screenshots. Restart Minecraft to load the installed companion jar.
