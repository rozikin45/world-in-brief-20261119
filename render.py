#!/usr/bin/env python3
"""Build the original editorial artwork; Pillow is a development-only tool.

The competition runner is main.py and uses the Python standard library only.
All illustrations here are original geometric symbols, not documentary photos.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SCALE = 2
SIZE = 1024
PAPER = "#F5F0E6"
INK = "#151A1B"
RED = "#B93F31"
GOLD = "#E2BD71"
HERO = "#E8DDC2"
TEAL = "#285E5A"
WHITE = "#FFFFFF"
MUTED = "#4A5050"
FONTS = {
    "display": "NotoSerifDisplay-SemiCondensedExtraBold.ttf",
    "regular": "NotoSans-Regular.ttf",
    "bold": "NotoSans-SemiBold.ttf",
}


def px(value: float) -> int:
    return round(value * SCALE)


@lru_cache(maxsize=200)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ROOT / "fonts" / FONTS[kind]), px(size))


class Poster:
    def __init__(self) -> None:
        self.image = Image.new("RGB", (px(SIZE), px(SIZE)), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_audit: list[dict] = []

    def rect(self, box, fill=None, outline=None, width=1):
        self.draw.rectangle(tuple(px(n) for n in box), fill=fill,
                            outline=outline, width=px(width))

    def line(self, points, fill=INK, width=3):
        self.draw.line([(px(x), px(y)) for x, y in points], fill=fill,
                       width=px(width), joint="curve")

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.draw.ellipse(tuple(px(n) for n in box), fill=fill,
                          outline=outline, width=px(width))

    def polygon(self, points, fill, outline=None, width=1):
        self.draw.polygon([(px(x), px(y)) for x, y in points],
                          fill=fill, outline=outline, width=px(width))

    def text(self, value, x, y, size, *, kind="regular", fill=INK,
             width=None, floor=None, anchor="lt", role="secondary"):
        chosen = int(size)
        lowest = chosen if floor is None else floor
        while True:
            bbox = self.draw.textbbox((0, 0), value,
                                      font=font(kind, chosen), anchor="lt")
            actual_width = (bbox[2] - bbox[0]) / SCALE
            if width is None or actual_width <= width:
                break
            chosen -= 1
            if chosen < lowest:
                raise ValueError(f"Text cannot fit its region: {value!r}")
        position = (px(x), px(y))
        bbox = self.draw.textbbox(position, value, font=font(kind, chosen),
                                  anchor=anchor)
        if min(bbox[:2]) < 0 or bbox[2] > px(SIZE) or bbox[3] > px(SIZE):
            raise ValueError(f"Text leaves canvas: {value!r}: {bbox}")
        self.draw.text(position, value, font=font(kind, chosen), fill=fill,
                       anchor=anchor, stroke_width=0)
        self.text_audit.append({
            "text": value, "size": chosen, "role": role,
            "bbox": [round(v / SCALE, 2) for v in bbox],
        })
        return chosen

    def lines(self, values, x, y, size, leading, **kwargs):
        for index, value in enumerate(values):
            self.text(value, x, y + leading * index, size, **kwargs)

    def group_photo_symbol(self):
        """Symbolic viewfinder and labelled figures, not a documentary photo."""
        self.rect((600, 233, 943, 396), fill=PAPER, outline=INK, width=4)
        for center, name in [(657, "TRUMP"), (771, "XI"), (885, "PUTIN")]:
            self.ellipse((center - 22, 257, center + 22, 301), fill=INK)
            self.polygon([(center - 34, 319), (center - 15, 308),
                          (center + 15, 308), (center + 34, 319),
                          (center + 38, 358), (center - 38, 358)], fill=INK)
            self.text(name, center, 373, 18, kind="bold", anchor="mt",
                      width=104)
        self.rect((613, 247, 624, 255), fill=RED)

    def bridge_symbol(self, x=414, y=545):
        """Intact bridge plus stop sign: no assertion of new physical damage."""
        self.line([(x, y + 20), (x + 61, y + 20)], width=4)
        self.line([(x + 10, y + 20), (x + 10, y + 37)], width=4)
        self.line([(x + 48, y + 20), (x + 48, y + 37)], width=4)
        self.line([(x + 10, y + 19), (x + 28, y + 5),
                   (x + 48, y + 19)], width=3)
        self.ellipse((x + 43, y + 21, x + 66, y + 44),
                     fill=GOLD, outline=INK, width=3)
        self.line([(x + 48, y + 33), (x + 61, y + 33)], width=3)

    def cyclone_symbol(self, center=(934, 557), radius=24):
        """Abstract cyclone mark, not a track or a quantitative weather chart."""
        cx, cy = center
        for rotation in [0, math.pi]:
            points = []
            for i in range(65):
                angle = rotation + i / 64 * math.pi * 1.7
                r = radius * (1 - i / 80)
                points.append((cx + math.cos(angle) * r,
                               cy + math.sin(angle) * r))
            self.line(points, fill=WHITE, width=4)
        self.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=WHITE)

    def gamepad_symbol(self, x=900, y=813):
        self.polygon([(x + 7, y), (x + 37, y), (x + 48, y + 8),
                      (x + 55, y + 30), (x + 45, y + 35),
                      (x + 32, y + 22), (x + 17, y + 22),
                      (x + 8, y + 34), (x - 3, y + 30)],
                     fill=PAPER, outline=INK, width=3)
        self.line([(x + 9, y + 10), (x + 9, y + 21)], width=3)
        self.line([(x + 4, y + 15), (x + 15, y + 15)], width=3)
        self.ellipse((x + 35, y + 9, x + 40, y + 14), fill=RED)
        self.ellipse((x + 42, y + 16, x + 47, y + 21), fill=TEAL)

    def draw_all(self, document):
        stories = {s["id"]: s for s in document["stories"]}
        assert len(stories) == 5

        # Larger sans-serif anchors replace the denser six-story first draft.
        self.text("19 NOV 2026  /  04:00 UTC", 35, 27, 30, kind="bold",
                  width=775, role="primary")
        self.text("WORLD IN BRIEF", 33, 76, 68, kind="bold",
                  width=775, floor=64, role="primary")
        self.text("EARLY EDITION", 36, 151, 27,
                  kind="bold", width=775)
        self.rect((835, 27, 989, 175), fill=INK)
        self.text("19", 912, 37, 79, kind="display", fill=PAPER,
                  anchor="mt", role="primary")
        self.text("NOV 2026", 912, 132, 23, kind="bold", fill=PAPER,
                  anchor="mt", role="primary")

        self.rect((34, 190, 989, 422), fill=HERO, outline=INK, width=4)
        self.text("01 / DIPLOMACY · SHENZHEN", 54, 207, 18,
                  kind="bold", width=520)
        self.text(stories["apec"]["headline"][0], 53, 249, 47,
                  kind="bold", width=520, floor=44, role="primary")
        self.text(stories["apec"]["headline"][1], 51, 306, 75,
                  kind="bold", width=520, floor=70, role="primary")
        self.text("Leaders' group photo in Shenzhen", 55, 390, 23,
                  width=520)
        self.group_photo_symbol()

        self.rect((34, 444, 989, 697), fill=PAPER, outline=INK, width=4)
        self.rect((514, 446, 987, 695), fill=TEAL)
        self.line([(512, 444), (512, 697)], width=4)
        self.text("02 / RUSSIA–UKRAINE", 54, 463, 18,
                  kind="bold", width=355)
        self.bridge_symbol(x=414, y=457)
        self.lines(stories["crimea"]["headline"], 53, 508, 43, 51,
                   kind="bold", width=432, floor=39, role="primary")
        self.lines(stories["crimea"]["deck"], 55, 620, 25, 33,
                   width=432, floor=24)
        self.text("03 / BAY OF BENGAL", 534, 463, 18,
                  kind="bold", fill=WHITE, width=345)
        self.cyclone_symbol(center=(934, 475))
        self.lines(stories["akvan"]["headline"], 533, 508, 43, 51,
                   kind="bold", fill=WHITE, width=430, floor=39,
                   role="primary")
        self.lines(stories["akvan"]["deck"], 535, 620, 25, 33,
                   fill=WHITE, width=425, floor=24)

        self.rect((34, 719, 989, 963), fill=PAPER, outline=INK, width=4)
        self.line([(512, 719), (512, 963)], width=4)
        self.text("04 / AUSTRALIA", 53, 741, 36, kind="bold",
                  width=432, role="primary")
        self.text(stories["australia"]["headline"][0], 51, 790, 88,
                  kind="display", width=432, role="primary")
        self.text("JOBLESS · OCTOBER", 54, 891, 31, kind="bold",
                  width=432, role="primary")
        self.text("NEW ABS RELEASE", 55, 936, 20, kind="bold", width=432)

        self.text("05 / CULTURE", 534, 741, 29, kind="bold",
                  width=430, role="primary")
        self.text(stories["gta"]["headline"][0], 531, 795, 65,
                  kind="bold", width=350, role="primary")
        self.gamepad_symbol()
        self.text(stories["gta"]["label"], 534, 881, 35, kind="bold",
                  width=430, floor=33, role="primary")
        self.text("DIGITAL · REGION BY REGION", 535, 932, 26,
                  kind="bold", width=430, floor=25)

        self.text("REUTERS  /  CNBC  /  ABS  /  IMD  /  AP", 35, 981,
                  15, kind="bold", width=810)
        self.text("FIVE DEVELOPMENTS. REPORTING CONTINUES.", 989, 1006,
                  13, kind="bold", anchor="rt", width=900, fill=MUTED)

    def save(self):
        final = self.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        destination = ROOT / "entry.png"
        final.save(destination, format="PNG", optimize=True, compress_level=9)
        preview = final.resize((300, 300), Image.Resampling.LANCZOS)
        preview.save(ROOT / "preview-300.png", optimize=True, compress_level=9)
        blob = destination.read_bytes()
        assert len(blob) <= 1_048_576, "Image exceeds the bounty's byte cap"
        assert final.size == (1024, 1024)
        audit = {
            "size": list(final.size), "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "as_of_utc": "2026-11-19T04:00:00Z",
            "illustration_type": "original symbolic line art; no documentary photo",
            "text": self.text_audit,
        }
        (ROOT / "design" / "layout-audit.json").write_text(
            json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({k: audit[k] for k in ["size", "bytes", "sha256"]}))


def main():
    document = json.loads((ROOT / "news.json").read_text())
    (ROOT / "design").mkdir(exist_ok=True)
    poster = Poster()
    poster.draw_all(document)
    poster.save()


if __name__ == "__main__":
    main()
