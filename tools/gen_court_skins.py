"""Custom textures for the Magister and the Captain.

Asked for by the user 2026-09-04: *"we need custom textures for the mage and the captain."*

    python tools/gen_court_skins.py
    python tools/gen_court_skins.py --dry-run

HOW THIS WORKS, AND WHY IT IS NOT ENTITY TEXTURE FEATURES
---------------------------------------------------------
The court are all one entity type -- `richs_races_wood_elves:wood_elf` -- separated only by a
custom name, so "a texture for the mage" needs some way to pick a texture per entity.

The obvious tool is Entity Texture Features, which is installed. It is also the wrong tool
here: ETF matches through OptiFine-style `.properties` files that are read entirely on the
CLIENT, so nothing in our headless validation can prove a rule ever fired. This project has
already shipped two silent no-ops that looked correct on disk (the culled canopy, the biome
band that could never be selected), and a client-only mechanism is exactly the shape of a
third.

The mod hands us something better. It is an MCreator mod whose renderer chooses between six
textures by reading a synched int, `DATA_SkinSwap`, persisted to entity NBT as `DataSkinSwap`
and set at spawn by `WoodElfOnInitialEntitySpawnProcedure`. `IsSkin1Procedure` through
`IsSkin6Procedure` compare it against 1..6 -- confirmed by decoding the `if_icmpne` operand in
each class rather than assumed:

    1  woodelf_female_1_texture.png
    2  woodelf_female_2_texture.png
    3  woodelf_female_3_texture.png
    4  woodelf_male_1_texture.png
    5  woodelf_male_2_texture.png     <- reserved for the Magister
    6  woodelf_male_3_texture.png     <- reserved for the Captain

So: RESERVE two of the six slots, override those two textures in our own resource pack, and
force every wild elf to roll only 1..4. The named pair get genuinely custom art, no wild elf
can ever wear it, and the whole mechanism is plain NBT that a server can verify.

The reservation is enforced by `kubejs/server_scripts/16_wood_elf_skins.js`, written here so
the reserved indices cannot drift away from this file.
"""
import argparse
import glob
import os
import zipfile

from PIL import Image

NS = 'richs_races_wood_elves'
TEX_DIR = os.path.join('kubejs', 'assets', NS, 'textures', 'entities')
SERVER = os.path.join('kubejs', 'server_scripts')

# Slot -> (source texture in the jar, output name). Only the two we reserve.
MAGISTER_SLOT = 5
CAPTAIN_SLOT = 6
SLOT_TEXTURE = {
    5: 'woodelf_male_2_texture.png',
    6: 'woodelf_male_3_texture.png',
}
WILD_SLOTS = [1, 2, 3, 4]


def base_image(name):
    """Pull a texture out of the mod jar so the recolour starts from the real art."""
    jars = glob.glob(os.path.join('mods', '*wood_elves*.jar'))
    if not jars:
        raise SystemExit('richs_races_wood_elves jar not found in mods/')
    with zipfile.ZipFile(jars[0]) as z:
        path = f'assets/{NS}/textures/entities/{name}'
        if path not in z.namelist():
            raise SystemExit(f'{path} not in {os.path.basename(jars[0])}')
        with z.open(path) as f:
            return Image.open(f).convert('RGBA').copy()


def recolour(img, ramp, keep_skin=True):
    """Map the image onto a colour ramp by luminance.

    Working from luminance rather than from hue keeps the mod's own shading, folds and outline
    exactly where the artist put them -- only the palette changes. A hue rotation would have
    smeared the darkest outline pixels into coloured noise.

    `keep_skin` leaves warm low-saturation pixels alone, which is what stops the face and hands
    from being dyed along with the robe.
    """
    out = img.copy()
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            sat = 0 if mx == 0 else (mx - mn) / mx
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

            # Skin and hair: warm, mid-bright, not very saturated. Left as drawn.
            if keep_skin and r > g >= b and sat < 0.45 and lum > 0.45:
                continue

            # Sample the ramp at this pixel's luminance.
            i = min(len(ramp) - 1, max(0, int(lum * (len(ramp) - 1))))
            cr, cg, cb = ramp[i]
            # Keep a little of the original so texture detail survives the remap.
            px[x, y] = (int(cr * 0.82 + r * 0.18),
                        int(cg * 0.82 + g * 0.18),
                        int(cb * 0.82 + b * 0.18), a)
    return out


def gild(img, colour, rows):
    """Lay a trim band across whole texture rows -- a belt, a hem, a collar.

    Applied only to pixels that already read as fabric (mid luminance), so the band follows the
    garment instead of painting a stripe straight across the face.
    """
    out = img.copy()
    px = out.load()
    w, h = out.size
    for y in rows:
        if not 0 <= y < h:
            continue
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            if 0.12 < lum < 0.80:
                px[x, y] = (int(colour[0] * 0.75 + r * 0.25),
                            int(colour[1] * 0.75 + g * 0.25),
                            int(colour[2] * 0.75 + b * 0.25), a)
    return out


# Deep indigo into starlit violet, with a cold highlight. He is the one who kept teaching after
# the lines died, so the palette is night rather than mourning.
MAGISTER_RAMP = [
    (14, 10, 30), (26, 18, 52), (42, 28, 78), (60, 40, 104),
    (84, 58, 132), (112, 84, 160), (146, 120, 190), (186, 168, 220),
]
MAGISTER_TRIM = (214, 176, 92)          # old gold

# Elven guard: living green under tarnished bronze. The armoury is locked and the plate has not
# been polished in a long time.
CAPTAIN_RAMP = [
    (12, 20, 16), (20, 34, 26), (30, 52, 38), (44, 74, 52),
    (66, 100, 70), (96, 130, 92), (134, 164, 122), (180, 200, 160),
]
CAPTAIN_TRIM = (156, 116, 62)           # tarnished bronze


def script():
    return f'''// Alfheim Reclaimed — reserve two wood elf skins for the named court
//
// GENERATED by tools/gen_court_skins.py — do not hand-edit.
//
// richs_races_wood_elves picks one of six textures from a synched int, persisted to NBT as
// `DataSkinSwap`, and `WoodElfOnInitialEntitySpawnProcedure` rolls it 1..6 at spawn. Slots
// {MAGISTER_SLOT} and {CAPTAIN_SLOT} carry OUR custom art for the Magister and the Captain, so a wild elf that
// rolled one of them would walk around wearing the Captain's plate.
//
// This forces every naturally spawned elf back into {WILD_SLOTS}. It runs on spawn rather than
// on a tick: the roll happens once, in finalizeSpawn, so once is enough.
//
// The court itself is NOT affected. Its members are placed by the amphitheatre structure with
// their DataSkinSwap already baked in and NoAI set, so they never pass through a spawn event.
// The NoAI test below is the guard for that, and it is deliberately belt-and-braces — hostile
// wood elves now spawn naturally in five biomes (see gen_alfheim_biomes.py), so this fires
// often and must never touch a court member.

const RESERVED = [{MAGISTER_SLOT}, {CAPTAIN_SLOT}]
const WILD = {WILD_SLOTS}

EntityEvents.spawned('{NS}:wood_elf', event => {{
    const e = event.entity
    if (!e) return
    try {{
        const nbt = e.nbt
        if (!nbt) return
        // A court member: placed, not spawned. Leave it exactly as the structure wrote it.
        if (nbt.getBoolean('NoAI')) return
        if (!RESERVED.includes(nbt.getInt('DataSkinSwap'))) return
        e.mergeNbt({{ DataSkinSwap: WILD[Math.floor(Math.random() * WILD.length)] }})
    }} catch (err) {{
        console.warn('[Alfheim Reclaimed] wood elf skin reservation failed: ' + err)
    }}
}})

console.info('[Alfheim Reclaimed] wood elf skins ' + RESERVED.join(' and ') +
             ' reserved for the Hollow Court')
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    if not a.dry_run:
        os.makedirs(TEX_DIR, exist_ok=True)
        os.makedirs(SERVER, exist_ok=True)

    jobs = [
        (MAGISTER_SLOT, 'Magister Velrous', MAGISTER_RAMP, MAGISTER_TRIM, range(20, 24)),
        (CAPTAIN_SLOT, 'Captain Orenvel', CAPTAIN_RAMP, CAPTAIN_TRIM, range(24, 28)),
    ]

    for slot, who, ramp, trim, rows in jobs:
        src = SLOT_TEXTURE[slot]
        img = base_image(src)
        img = recolour(img, ramp)
        img = gild(img, trim, rows)
        dst = os.path.join(TEX_DIR, src)
        if not a.dry_run:
            img.save(dst)
        print(f'  skin {slot}  {who:18} {img.size[0]}x{img.size[1]}  -> {dst}')

    sp = os.path.join(SERVER, '16_wood_elf_skins.js')
    if not a.dry_run:
        with open(sp, 'w', encoding='utf-8') as f:
            f.write(script())
    print(f'  reservation  wild elves forced to {WILD_SLOTS}  -> {sp}')
    print(f'\n  2 custom skins; slots {MAGISTER_SLOT} and {CAPTAIN_SLOT} reserved from '
          f'{len(WILD_SLOTS) + 2} total')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
