#!/usr/bin/env python3
"""Crop padding around the supervisor window in report screenshots.

macOS screencapture -R uses the same point units as AppleScript geometry; on
Retina displays the PNG is 2× wider/taller.  When capture_report_screenshots.sh
adds PAD_X / PAD_Y (points) around the window, remove 2× that margin here.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("crop_screenshot.py: install Pillow (pip install pillow)", file=sys.stderr)
    sys.exit(1)


def crop_margins(path: Path, margin_x: int, margin_y: int, inplace: bool = True) -> tuple[int, int]:
    im = Image.open(path)
    w, h = im.size
    if 2 * margin_x >= w or 2 * margin_y >= h:
        raise SystemExit(f"{path}: margins {margin_x}x{margin_y} too large for {w}x{h}")
    cropped = im.crop((margin_x, margin_y, w - margin_x, h - margin_y))
    out = path if inplace else path.with_name(path.stem + "-cropped" + path.suffix)
    cropped.save(out, optimize=True)
    return cropped.size


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("images", nargs="+", type=Path, help="PNG files to crop in place")
    p.add_argument(
        "--pad-x",
        type=int,
        default=80,
        help="horizontal padding used at capture time, in points (default: 80)",
    )
    p.add_argument(
        "--pad-y",
        type=int,
        default=40,
        help="vertical padding used at capture time, in points (default: 40)",
    )
    p.add_argument(
        "--scale",
        type=int,
        default=2,
        help="display scale factor (default: 2 for Retina)",
    )
    args = p.parse_args()
    mx = args.pad_x * args.scale
    my = args.pad_y * args.scale
    for path in args.images:
        if not path.is_file():
            print(f"skip missing: {path}", file=sys.stderr)
            continue
        nw, nh = crop_margins(path, mx, my)
        print(f"{path.name}: -> {nw}x{nh}")


if __name__ == "__main__":
    main()
