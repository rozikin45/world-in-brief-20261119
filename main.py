#!/usr/bin/env python3
"""Emit the committed, original news artwork using only Python's standard library."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def validate_png(data: bytes) -> tuple[int, int]:
    """Check format, intake caps and chunk integrity before writing any output."""
    if len(data) > 1_048_576:
        raise ValueError("entry.png exceeds 1 MiB")
    if len(data) < 33 or not data.startswith(PNG_MAGIC):
        raise ValueError("entry.png is not a PNG")
    if data[12:16] != b"IHDR" or struct.unpack(">I", data[8:12])[0] != 13:
        raise ValueError("PNG has no initial IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if not (1 <= width <= 1024 and 1 <= height <= 1024):
        raise ValueError("entry.png exceeds the dimension cap")
    offset = 8
    saw_pixels = False
    saw_end = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("PNG chunk header is truncated")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError("PNG chunk payload is truncated")
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            raise ValueError("PNG chunk CRC mismatch")
        saw_pixels |= kind == b"IDAT" and length > 0
        offset = end
        if kind == b"IEND":
            if length != 0 or offset != len(data):
                raise ValueError("PNG has an invalid ending or trailing bytes")
            saw_end = True
            break
    if not saw_pixels or not saw_end:
        raise ValueError("PNG is missing pixel data or its final chunk")
    return width, height


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("/output"))
    args = parser.parse_args()
    data = (ROOT / "entry.png").read_bytes()
    width, height = validate_png(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / "entry.png"
    destination.write_bytes(data)
    print(json.dumps({"file": str(destination), "width": width,
                      "height": height, "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
