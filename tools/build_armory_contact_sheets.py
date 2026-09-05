"""Build review sheets from the exported armory sprites.

The checkerboard exists only in these review images. Production item PNGs remain RGBA files
with literal alpha-zero backgrounds and are pasted over the checker for halo inspection.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'kubejs/assets/alfheim/textures/item/armory'
OUT = ROOT / 'alfheim_reclaimed_design/armory/visual_review'
CLASSES = {
    'warrior': ['blade', 'axe', 'spear', 'ward', 'helmet', 'chest', 'pants', 'boots'],
    'hunter': ['bow', 'crossbow', 'blade', 'charm', 'helmet', 'chest', 'pants', 'boots'],
    'sorcerer': ['focus', 'blade', 'spear', 'folio', 'helmet', 'chest', 'pants', 'boots'],
    'shaman': ['focus', 'spear', 'axe', 'ward', 'helmet', 'chest', 'pants', 'boots'],
    'warlock': ['focus', 'blade', 'bow', 'folio', 'helmet', 'chest', 'pants', 'boots'],
    'minstrel': ['focus', 'blade', 'crossbow', 'folio', 'helmet', 'chest', 'pants', 'boots'],
}


def font(size, bold=False):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    path = Path('C:/Windows/Fonts') / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def checker(size, step=12):
    im = Image.new('RGB', size, '#d6d8dc')
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                d.rectangle((x, y, x + step - 1, y + step - 1), fill='#8e949e')
    return im


def build_class(school, families):
    left, top, cell, gap = 138, 108, 96, 8
    width = left + len(families) * (cell + gap) + 18
    height = top + 10 * (cell + gap) + 18
    sheet = Image.new('RGB', (width, height), '#171b22')
    d = ImageDraw.Draw(sheet)
    d.text((18, 13), f'{school.title()} — all 80 exported sprites', font=font(28, True), fill='white')
    d.text((18, 51), 'Checkerboard is review-only; production PNG backgrounds are alpha 0.',
           font=font(17), fill='#c7ccd4')
    for col, family in enumerate(families):
        x = left + col * (cell + gap)
        d.text((x, 82), family.title(), font=font(15, True), fill='#e4e8ed')
    for era in range(1, 11):
        y = top + (era - 1) * (cell + gap)
        d.text((18, y + 35), f'Era {era:02}', font=font(18, True), fill='#e4e8ed')
        for col, family in enumerate(families):
            x = left + col * (cell + gap)
            bg = checker((cell, cell))
            sprite = Image.open(TEXTURES / school / family / f'era_{era:02}.png').convert('RGBA')
            sprite = sprite.resize((cell, cell), Image.Resampling.NEAREST)
            bg.paste(sprite, (0, 0), sprite)
            sheet.paste(bg, (x, y))
            d.rectangle((x, y, x + cell - 1, y + cell - 1), outline='#4e5662')
    path = OUT / f'{school}_armory_review.png'
    sheet.save(path)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [build_class(s, f) for s, f in CLASSES.items()]
    thumbs = []
    for path in paths:
        im = Image.open(path).convert('RGB')
        im.thumbnail((500, 610), Image.Resampling.LANCZOS)
        thumbs.append(im)
    overview = Image.new('RGB', (1040, 1910), '#0f1217')
    d = ImageDraw.Draw(overview)
    d.text((20, 12), 'Reclaimed Armory — six-class texture review', font=font(30, True), fill='white')
    d.text((20, 52), 'Each source sprite is composited over a review checkerboard to expose edge residue.',
           font=font(17), fill='#c7ccd4')
    for i, im in enumerate(thumbs):
        x = 20 + (i % 2) * 510
        y = 90 + (i // 2) * 605
        overview.paste(im, (x, y))
    overview.save(OUT / 'armory_overview.png')
    print(f'Built {len(paths)} class sheets and overview in {OUT}')


if __name__ == '__main__':
    main()
