"""Generate the Guild Regalia: 63 Curio items, their icons, models, slot tags and registration.

The authority is `alfheim_reclaimed_design/curios/curio_suite_catalog.json`, which
`tools/build_curio_plan.py` validates. This generator adds no item and invents no id: it reads the
63 planned entries and gives each one a texture, a model, a display name, a slot tag and a KubeJS
registration. If the catalog changes, rerun this and the assets follow.

**Icons are derived, not drawn.** Each is a vanilla base recoloured to its owner's hue, with the
rank's own frame material — our own generated art — pressed into the silhouette. Three things
carry meaning and they are independent, so a 16x16 icon still reads at a glance:

    form  = family    ring / faceted drop / cord   (3 silhouettes)
    hue   = owner     6 classes + 9 professions    (15 hues)
    rank  = material  apprentice -> guild -> master (rising material, brightness, and a gleam)

**No mod jar is read.** `load_base(..., allow_mod=False)` is passed everywhere, so every source
pixel comes from the vanilla client jar or from `kubejs/assets/alfheim/`. `INSTRUCTIONS.md` §5
forbids redistributing third-party art, and a recoloured mod texture in our tree would be exactly
that. The 46 installed Curios the plan references are *anchors* — items the suite reacts to. Their
art is never copied.

**These items have no behaviour yet.** This pass registers them and puts them in the right slots.
Effects, recipes and the profession-proof capability are the next slices; see B-74.

    python tools/gen_curios.py
    python tools/gen_curios.py --list
    python tools/gen_curios.py --sheet    # contact sheet for a visual pass
"""
import argparse
import json
import os
import sys
import zipfile

from item_textures import CLIENT_JAR, load_base, mask_to, overlay, tint

NS = 'alfheim'
CATALOG = os.path.join('alfheim_reclaimed_design', 'curios', 'curio_suite_catalog.json')
TEX_OUT = os.path.join('kubejs', 'assets', NS, 'textures', 'item')
MODEL_OUT = os.path.join('kubejs', 'assets', NS, 'models', 'item')
SCRIPT_OUT = os.path.join('kubejs', 'startup_scripts', '18_curios.js')
TAG_OUT = os.path.join('kubejs', 'data', 'curios', 'tags', 'items')
MANIFEST_OUT = os.path.join('tools', 'curios_manifest.json')

# --- presentation -----------------------------------------------------------------------------
# The vanilla base that supplies each family's silhouette. Chosen by looking at the 1.20.1 art,
# not by name, and then by looking at the contact sheet: the first pick for the emblem was the
# nautilus shell, and against a signet's ring it was one more coloured circle. A silhouette only
# earns its place if it survives being 16 pixels wide next to its neighbours.
FORM = {
    'signet': 'ender_eye.png',      # an annulus: reads as a band seen face-on
    'emblem': 'amethyst_shard.png',  # a faceted drop: the one form that is not round
    'cuff': 'lead.png',             # a curved cord: reads as something that wraps a wrist
}

# One hue per owner. Classes and professions never share a silhouette, so the two sets only have
# to be internally separable; --sheet is how that gets checked rather than assumed.
HUE = {
    # six Mine and Slash base classes, by tradition
    'warrior': 100,    # Thornwarden   — thorn green
    'hunter': 42,      # Waywatcher    — amber
    'sorcerer': 278,   # Leyweaver     — violet
    'shaman': 158,     # Rootspeaker   — moss teal
    'warlock': 315,    # Duskkeeper    — dusk magenta
    'minstrel': 8,     # Dawnsinger    — dawn rose
    # nine native professions
    'mining': 218,
    'farming': 95,
    'fishing': 186,
    'husbandry': 54,
    'salvaging': 22,
    'gear_crafting': 246,
    'enchanting': 288,
    'cooking': 353,
    'alchemy': 132,
}

# Rank raises brightness, saturation and how much of the frame material shows through, and master
# also takes a gleam. Every overlay is clipped to the silhouette; nothing is allowed to spill.
RANK_STYLE = {
    'apprentice': {'sat': 0.80, 'val': 0.68, 'mat_alpha': 0.16, 'gleam': 0.0,
                   'rarity': 'uncommon', 'title': 'Apprentice'},
    'guild': {'sat': 1.10, 'val': 0.88, 'mat_alpha': 0.34, 'gleam': 0.0,
              'rarity': 'rare', 'title': 'Guild'},
    'master': {'sat': 1.25, 'val': 1.18, 'mat_alpha': 0.44, 'gleam': 0.34,
               'rarity': 'epic', 'title': 'Master'},
}

# Some bases are pale, so their own saturation is too low for an absolute hue to show. The floor, not the
# multiplier, is what makes an owner's colour legible; at 0.45 every piece came out tan.
SAT_FLOOR = 0.68

GLEAM = 'nether_star.png'
ROMAN = {2: 'II', 5: 'V', 8: 'VIII'}


def plan(catalog):
    """Expand the catalog's 63 entries into everything the assets need.

    Nothing here decides *which* items exist — that is the catalog's job. This only attaches the
    display name, tooltip and style each planned id is going to be drawn and registered with.
    """
    ranks = {r['id']: r for r in catalog['ranks']}
    rows = []
    for item in catalog['planned_items']:
        owner, kind, family, rank = item['owner'], item['kind'], item['family'], item['rank']
        style = RANK_STYLE[rank]
        if kind == 'class':
            src = catalog['classes'][owner]
            noun = f"{src['tradition']} Signet" if family == 'signet' else src['emblem']
            lore = src['tradition']
        else:
            src = catalog['professions'][owner]
            noun = src['cuff']
            lore = src['title']
        rows.append({
            'id': item['id'].split(':', 1)[1],
            'kind': kind, 'owner': owner, 'family': family, 'rank': rank,
            'slot': item['slot'], 'era': item['era'],
            'name': f"{style['title']} {noun}",
            'tooltip': f"{lore} · Era {ROMAN[item['era']]} regalia",
            'frame': ranks[rank]['frame'],
            'hue': HUE[owner],
            'style': style,
        })
    return rows


def draw(jar, row):
    """Vanilla silhouette, owner hue, rank material pressed into the form, gleam at master."""
    st = row['style']
    form = load_base(jar, FORM[row['family']], allow_mod=False)
    if row['family'] == 'signet':
        # Cut out the eye's iris to turn the existing rim into a real ring. This is an alpha
        # opening, not painted background; clipping all overlays below keeps it open.
        from PIL import ImageDraw
        ImageDraw.Draw(form).ellipse((6, 6, 9, 9), fill=(0, 0, 0, 0))
    icon = tint(form, row['hue'], st['sat'], st['val'], sat_floor=SAT_FLOOR)

    # The rank's own frame material, tinted toward the owner and clipped to the silhouette so it
    # reads as the piece's surface rather than as a sticker floating over it.
    material = load_base(jar, row['frame'] + '.png', allow_mod=False)
    material = tint(material, row['hue'], 0.85, 1.05, sat_floor=0.45)
    icon = overlay(icon, mask_to(material, form), st['mat_alpha'])

    if st['gleam']:
        # Masked, unlike the first attempt. An unmasked nether_star at this alpha replaced the
        # piece with a four-point cross; clipped to the form it reads as sheen on the metal.
        gleam = tint(load_base(jar, GLEAM, allow_mod=False), 48, 0.45, 1.20, sat_floor=0.25)
        icon = overlay(icon, mask_to(gleam, form), st['gleam'])
    return icon


def js_escape(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true', help='print the roster and exit')
    ap.add_argument('--sheet', action='store_true', help='also write a contact sheet for review')
    a = ap.parse_args()

    catalog = json.load(open(CATALOG, encoding='utf-8'))
    rows = plan(catalog)

    expected = catalog['counts']['planned_items']
    if len(rows) != expected:
        print(f'catalog disagrees with itself: {len(rows)} entries, counts says {expected}')
        return 2

    if a.list:
        for r in rows:
            print(f"  era {r['era']:>2}  {r['slot']:9} {r['id']:44} {r['name']}")
        print(f'\n{len(rows)} curios')
        return 0

    if not os.path.exists(CLIENT_JAR):
        print(f'client jar not found: {CLIENT_JAR}')
        return 2

    jar = zipfile.ZipFile(CLIENT_JAR)
    lines = [
        '// Alfheim Reclaimed — the Guild Regalia',
        '//',
        '// GENERATED by tools/gen_curios.py from',
        '// alfheim_reclaimed_design/curios/curio_suite_catalog.json — do not hand-edit.',
        '//',
        '// Registration and slot eligibility only. These pieces carry no effect yet: the plan',
        '// binds every effect to a native action the owning system has already accepted, and',
        '// that event work is the next slice (B-74). Slots come from data/curios/tags/items/.',
        '',
        "StartupEvents.registry('item', event => {",
    ]

    tags = {}
    manifest_rows = []
    for r in rows:
        icon = draw(jar, r)
        tex = os.path.join(TEX_OUT, *r['id'].split('/')) + '.png'
        os.makedirs(os.path.dirname(tex), exist_ok=True)
        icon.save(tex)

        write_json(os.path.join(MODEL_OUT, *r['id'].split('/')) + '.json',
                   {'parent': 'minecraft:item/generated',
                    'textures': {'layer0': f"{NS}:item/{r['id']}"}})

        lines.append(
            f"    event.create('{NS}:{r['id']}')"
            f".displayName('{js_escape(r['name'])}')"
            f".tooltip('{js_escape(r['tooltip'])}')"
            f".rarity('{r['style']['rarity']}')"
            f".unstackable()")

        tags.setdefault(r['slot'], []).append(f"{NS}:{r['id']}")
        manifest_rows.append({k: r[k] for k in
                              ('id', 'kind', 'owner', 'family', 'rank', 'slot', 'era', 'name')})

    lines += ['})', '']
    os.makedirs(os.path.dirname(SCRIPT_OUT), exist_ok=True)
    with open(SCRIPT_OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

    # Curios reads slot eligibility from item tags in its own namespace. `replace: false` is the
    # default, but stating it keeps this file from ever silently emptying a slot another mod fills.
    for slot, ids in sorted(tags.items()):
        write_json(os.path.join(TAG_OUT, f'{slot}.json'), {'replace': False, 'values': sorted(ids)})

    write_json(MANIFEST_OUT, {
        'status': 'registered and slotted; no effect, no recipe',
        'source_catalog': CATALOG.replace('\\', '/'),
        'counts': {
            'items': len(rows),
            'class_items': sum(1 for r in rows if r['kind'] == 'class'),
            'profession_items': sum(1 for r in rows if r['kind'] == 'profession'),
            'textures': len(rows), 'models': len(rows),
            'slot_tags': len(tags),
            'by_slot': {s: len(v) for s, v in sorted(tags.items())},
        },
        'forms': FORM, 'hues': HUE,
        'items': manifest_rows,
    })

    if a.sheet:
        sheet_path = contact_sheet(rows)
        print(f'  contact sheet -> {sheet_path}')

    jar.close()
    print(f'{len(rows)} curios -> {TEX_OUT}, {MODEL_OUT}, {SCRIPT_OUT}, {TAG_OUT}')
    for slot, ids in sorted(tags.items()):
        print(f'  {slot:10} {len(ids):2} items')
    return 0


def contact_sheet(rows, path=os.path.join('tools', 'curios_review.png')):
    """Full owner labels, grouped families, and exact 4x nearest-neighbour scaling."""
    from PIL import Image, ImageDraw
    groups = [('Class signets / ring', 'signet'), ('Class emblems / necklace or charm', 'emblem'),
              ('Profession cuffs / bracelet', 'cuff')]
    rank_order = ['apprentice', 'guild', 'master']
    sheet = Image.new('RGBA', (900, 930), (31, 33, 40, 255))
    d = ImageDraw.Draw(sheet)
    d.text((20, 14), 'GUILD REGALIA / 63 items / existing textures + PIL', fill='#e5e7ed')
    d.text((20, 32), 'Left to right: Apprentice / Guild / Master. Art and registration build; effects pending.', fill='#aeb5c7')
    y = 66
    for title, family in groups:
        d.text((20, y), title, fill='#e5d4a3')
        y += 26
        owners = sorted({r['owner'] for r in rows if r['family'] == family})
        for i, owner in enumerate(owners):
            x, top = 20 + (i % 3) * 294, y + (i // 3) * 108
            d.text((x, top), owner.replace('_', ' ').title(), fill='#e5e7ed')
            for j, rank in enumerate(rank_order):
                row = next(r for r in rows if r['family'] == family and r['owner'] == owner and r['rank'] == rank)
                icon_path = os.path.join(TEX_OUT, *row['id'].split('/')) + '.png'
                with Image.open(icon_path) as source:
                    im = source.convert('RGBA').resize((64, 64), Image.Resampling.NEAREST)
                ix, iy = x + j * 88, top + 18
                for cy in range(0, 64, 8):
                    for cx in range(0, 64, 8):
                        shade = '#30333d' if (cx + cy) % 16 else '#3c404b'
                        d.rectangle((ix + cx, iy + cy, ix + cx + 7, iy + cy + 7), fill=shade)
                sheet.alpha_composite(im, (ix, iy))
                d.text((ix, iy + 66), rank.title(), fill='#aeb5c7')
        y += ((len(owners) + 2) // 3) * 108 + 12
    sheet = sheet.crop((0, 0, sheet.width, y))
    sheet.save(path)
    return path


if __name__ == '__main__':
    sys.exit(main())
