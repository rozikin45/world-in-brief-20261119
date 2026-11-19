#!/usr/bin/env python3
"""Data-driven 3-lead / 9-brief edition. No article or headline is fabricated here.

This is a development renderer. main.py remains the standard-library entrypoint.
A partial selection can only be rendered explicitly to a non-publishable QA path.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

from PIL import Image
from render import Poster, font, ROOT, SCALE, SIZE, PAPER, INK, HERO, TEAL, WHITE, MUTED


def layout_boxes():
    width = (968 - 24) / 3
    columns = [28 + i * (width + 12) for i in range(3)]
    leads = [(x, 122, x + width, 398) for x in columns]
    briefs = [(x, 430 + row * 176, x + width, 596 + row * 176)
              for row in range(3) for x in columns]
    return leads + briefs


def validate_selection(document, allow_partial=False):
    stories = document.get("stories", [])
    if not allow_partial and len(stories) != 12:
        raise ValueError("The final edition needs exactly 12 verified story records")
    if not allow_partial and document.get("selection_status") != "final":
        raise ValueError("The publication selection must be explicitly final")
    if not (3 <= len(stories) <= 12):
        raise ValueError("A layout check needs 3 to 12 real source-linked stories")
    ids = [story.get("id") for story in stories]
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError("Story IDs must be present and unique")
    for story in stories:
        if not story.get("verified_claim") or not story.get("source_ids"):
            raise ValueError("Each story needs its verified claim and source references")
    leads = document.get("lead_ids", ["apec", "akvan", "gta"])
    if len(leads) != 3 or len(set(leads)) != 3 or not set(leads) <= set(ids):
        raise ValueError("Exactly three distinct selected lead IDs are required")
    return stories, leads


class DensePoster(Poster):
    def wrap(self, value, size, kind, width):
        lines = []
        current = ""
        for word in value.split():
            candidate = (current + " " + word).strip()
            box = self.draw.textbbox((0, 0), candidate, font=font(kind, size), anchor="lt")
            if (box[2] - box[0]) / SCALE <= width:
                current = candidate
            else:
                if not current:
                    return None
                lines.append(current)
                current = word
                box = self.draw.textbbox((0, 0), word, font=font(kind, size), anchor="lt")
                if (box[2] - box[0]) / SCALE > width:
                    return None
        if current:
            lines.append(current)
        return lines

    def block(self, value, x, y, *, size, floor, width, max_lines,
              leading, kind="regular", fill=INK, role="secondary"):
        for selected in range(size, floor - 1, -1):
            lines = self.wrap(value, selected, kind, width)
            if lines is not None and len(lines) <= max_lines:
                self.lines(lines, x, y, selected, leading, kind=kind,
                           fill=fill, width=width, role=role)
                return len(lines)
        raise ValueError("Editorial copy is too long for its region: " + value)

    def copy_for(self, story):
        headline = story.get("image_headline")
        if not headline:
            headline = " ".join(story.get("headline", []))
            if story.get("label"):
                headline = (headline + " " + story["label"]).strip()
        brief = story.get("image_brief") or " ".join(story.get("deck", []))
        if not headline or not brief:
            raise ValueError("Every selected story needs honest display copy")
        return headline, brief

    def symbol(self, story_id, x, y, color):
        if story_id == "akvan":
            self.cyclone_symbol(center=(x, y), radius=17)
        elif story_id == "gta":
            self.gamepad_symbol(x=x - 25, y=y - 15)
        else:
            for dx in [-13, 0, 13]:
                self.ellipse((x + dx - 4, y - 10, x + dx + 4, y - 2), fill=color)
                self.rect((x + dx - 5, y + 1, x + dx + 5, y + 13), fill=color)

    def lead(self, story, box, index):
        x0, y0, x1, y1 = box
        inverse = story["id"] == "akvan"
        background = TEAL if inverse else (HERO if index == 0 else PAPER)
        color = WHITE if inverse else INK
        self.rect(box, fill=background, outline=INK, width=3)
        category = story.get("category", "WORLD")
        self.text(f"{index + 1:02d} / {category}", x0 + 13, y0 + 15, 14,
                  kind="bold", fill=color, width=x1 - x0 - 86, floor=12)
        self.symbol(story["id"], x1 - 34, y0 + 27, color)
        title, brief = self.copy_for(story)
        self.block(title, x0 + 13, y0 + 61, size=35, floor=30,
                   width=x1 - x0 - 26, max_lines=3, leading=40,
                   kind="bold", fill=color, role="primary")
        self.block(brief, x0 + 14, y0 + 196, size=18, floor=17,
                   width=x1 - x0 - 28, max_lines=3, leading=22,
                   fill=color)

    def brief(self, story, box, index):
        x0, y0, x1, y1 = box
        self.rect(box, fill=PAPER, outline=INK, width=2)
        tag = story.get("location_short") or story.get("location") or story.get("category", "WORLD")
        self.text(f"{index + 4:02d} / {tag}", x0 + 12, y0 + 12, 14,
                  kind="bold", width=x1 - x0 - 24, floor=12)
        title, brief = self.copy_for(story)
        self.block(title, x0 + 12, y0 + 39, size=24, floor=22,
                   width=x1 - x0 - 24, max_lines=2, leading=28,
                   kind="bold", role="primary")
        self.block(brief, x0 + 13, y0 + 101, size=17, floor=16,
                   width=x1 - x0 - 26, max_lines=3, leading=19)

    def draw_document(self, document, allow_partial=False):
        stories, lead_ids = validate_selection(document, allow_partial)
        by_id = {story["id"]: story for story in stories}
        ordered = [by_id[story_id] for story_id in lead_ids]
        remaining = [story for story in stories if story["id"] not in lead_ids]
        stamp = datetime.fromisoformat(document["as_of_utc"].replace("Z", "+00:00"))
        self.text(stamp.strftime("%d %b %Y  /  %H:%M UTC").upper(),
                  28, 14, 25, kind="bold", width=790, role="primary")
        self.text("WORLD IN BRIEF", 26, 51, 55, kind="bold", width=785,
                  floor=51, role="primary")
        self.rect((842, 12, 996, 108), fill=INK)
        self.text(stamp.strftime("%d"), 919, 18, 55, kind="display",
                  fill=PAPER, anchor="mt", role="primary")
        self.text(stamp.strftime("%b %Y").upper(), 919, 83, 16,
                  kind="bold", fill=PAPER, anchor="mt")
        boxes = layout_boxes()
        for index, story in enumerate(ordered):
            self.lead(story, boxes[index], index)
        label = ("EARLY EDITION / 3 LEADS + 9 BRIEFS" if not allow_partial
                 else f"PRIVATE LAYOUT CHECK / {len(stories)} REAL STORIES, TARGET 12")
        self.text(label, 28, 410, 13, kind="bold", width=968)
        for index, story in enumerate(remaining):
            self.brief(story, boxes[index + 3], index)
        self.text("SOURCE-CHECKED SUMMARY / FULL REFERENCES IN REPOSITORY",
                  28, 968, 13, kind="bold", width=968)
        self.text(f"{len(stories)} STORIES. REPORTING CONTINUES.", 996, 1002,
                  13, kind="bold", fill=MUTED, anchor="rt", width=900)

    def save_to(self, destination, document, allow_partial):
        destination.parent.mkdir(parents=True, exist_ok=True)
        image = self.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        image.save(destination, format="PNG", optimize=True, compress_level=9)
        data = destination.read_bytes()
        if len(data) > 1_048_576:
            raise ValueError("Expanded artwork exceeds the 1 MiB cap")
        preview = (ROOT / "preview-300.png" if destination.resolve() == (ROOT / "entry.png").resolve()
                   else destination.with_name(destination.stem + "-300.png"))
        image.resize((300, 300), Image.Resampling.LANCZOS).save(preview, optimize=True)
        audit = {"size": list(image.size), "bytes": len(data),
                 "sha256": hashlib.sha256(data).hexdigest(),
                 "story_count": len(document["stories"]),
                 "partial_layout_check": allow_partial,
                 "as_of_utc": document["as_of_utc"], "text": self.text_audit}
        destination.with_suffix(".layout.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({k: audit[k] for k in
                          ["size", "bytes", "sha256", "story_count", "partial_layout_check"]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "news.json")
    parser.add_argument("--output", type=Path, default=ROOT / "entry.png")
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    if args.allow_partial and args.output.resolve() == (ROOT / "entry.png").resolve():
        raise ValueError("A partial layout may not overwrite the publishable entry.png")
    document = json.loads(args.input.read_text())
    poster = DensePoster()
    poster.draw_document(document, args.allow_partial)
    poster.save_to(args.output, document, args.allow_partial)


if __name__ == "__main__":
    main()
