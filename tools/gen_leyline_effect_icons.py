#!/usr/bin/env python3
"""Generate the seven 18x18 pixel-art icons used by the first leyline effect slice."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "kubejs" / "assets" / "alfheim" / "textures" / "mob_effect"
SIZE = 18


def canvas():
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def node(draw, outer, inner):
    draw.rectangle((7, 7, 10, 10), fill=outer)
    draw.rectangle((8, 8, 9, 9), fill=inner)
    draw.rectangle((8, 1, 9, 6), fill=outer)
    draw.rectangle((8, 11, 9, 16), fill=outer)
    draw.rectangle((1, 8, 6, 9), fill=outer)
    draw.rectangle((11, 8, 16, 9), fill=outer)
    draw.point((8, 0), fill=inner)
    draw.point((9, 17), fill=inner)
    draw.point((0, 8), fill=inner)
    draw.point((17, 9), fill=inner)


def presence():
    image, draw = canvas()
    node(draw, (48, 165, 203, 255), (204, 255, 255, 255))
    draw.line((4, 4, 6, 6), fill=(105, 230, 255, 210))
    draw.line((11, 6, 13, 4), fill=(105, 230, 255, 210))
    draw.line((4, 13, 6, 11), fill=(105, 230, 255, 210))
    draw.line((11, 11, 13, 13), fill=(105, 230, 255, 210))
    return image


def ember():
    image, draw = canvas()
    draw.polygon(((9, 1), (13, 6), (12, 10), (9, 16), (5, 12), (4, 8)), fill=(179, 47, 24, 255))
    draw.polygon(((9, 4), (11, 8), (9, 13), (6, 10), (7, 7)), fill=(255, 129, 39, 255))
    draw.polygon(((9, 7), (10, 10), (8, 12), (7, 10)), fill=(255, 228, 103, 255))
    return image


def tidal():
    image, draw = canvas()
    draw.polygon(((9, 1), (14, 8), (14, 12), (11, 15), (7, 16), (3, 13), (3, 10)), fill=(34, 105, 194, 255))
    draw.polygon(((3, 10), (6, 8), (9, 10), (12, 8), (15, 10), (15, 13), (12, 12), (9, 14), (6, 12), (3, 14)), fill=(89, 190, 255, 255))
    draw.line((7, 5, 9, 3), fill=(196, 243, 255, 255), width=1)
    return image


def rootguard():
    image, draw = canvas()
    draw.polygon(((9, 1), (15, 4), (14, 11), (9, 16), (4, 11), (3, 4)), fill=(45, 106, 57, 255))
    draw.polygon(((9, 3), (13, 5), (12, 10), (9, 13), (6, 10), (5, 5)), fill=(105, 177, 91, 255))
    draw.line((9, 5, 9, 13), fill=(209, 234, 145, 255), width=1)
    draw.line((9, 8, 6, 6), fill=(209, 234, 145, 255), width=1)
    draw.line((9, 10, 12, 7), fill=(209, 234, 145, 255), width=1)
    return image


def gale():
    image, draw = canvas()
    pale = (180, 255, 239, 255)
    mid = (70, 187, 181, 255)
    draw.arc((2, 2, 15, 12), 190, 350, fill=pale, width=2)
    draw.arc((3, 5, 14, 15), 10, 180, fill=mid, width=2)
    draw.line((2, 9, 11, 9), fill=pale, width=2)
    draw.polygon(((13, 7), (17, 9), (13, 11)), fill=pale)
    draw.line((5, 13, 12, 13), fill=(126, 229, 216, 255), width=1)
    return image


def dusk():
    image, draw = canvas()
    draw.ellipse((2, 2, 15, 15), outline=(104, 62, 163, 255), width=2)
    draw.ellipse((5, 5, 12, 12), outline=(181, 118, 239, 255), width=2)
    draw.polygon(((9, 4), (10, 8), (14, 9), (10, 10), (9, 14), (8, 10), (4, 9), (8, 8)), fill=(226, 184, 255, 255))
    draw.rectangle((8, 8, 9, 9), fill=(77, 37, 120, 255))
    return image


def dawn():
    image, draw = canvas()
    gold = (255, 214, 91, 255)
    pale = (255, 249, 184, 255)
    draw.polygon(((9, 1), (11, 6), (16, 4), (13, 8), (17, 9), (13, 10), (16, 14), (11, 12), (9, 17), (7, 12), (2, 14), (5, 10), (1, 9), (5, 8), (2, 4), (7, 6)), fill=gold)
    draw.rectangle((6, 6, 11, 11), fill=(240, 167, 55, 255))
    draw.rectangle((8, 8, 9, 9), fill=pale)
    return image


ICONS = {
    "leyline_presence": presence,
    "ember_current": ember,
    "tidal_recovery": tidal,
    "rootguard": rootguard,
    "gale_tempo": gale,
    "dusk_precision": dusk,
    "dawn_clarity": dawn,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for effect_id, factory in ICONS.items():
        path = OUT / f"{effect_id}.png"
        image = factory()
        if image.size != (SIZE, SIZE) or image.mode != "RGBA":
            raise ValueError(f"Invalid icon output for {effect_id}")
        image.save(path, format="PNG", optimize=True)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
