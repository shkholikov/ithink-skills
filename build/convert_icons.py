#!/usr/bin/env python3
"""One-time build step: Cisco CMYK JPEGs -> trimmed transparent RGBA PNGs.

Not shipped in the skill. Run once on a machine with Pillow; commit the
results into the skill's assets/icons/ directory.

Background removal uses a flood fill seeded from the image border, so white
*inside* an icon (a server bezel, a printer tray) is preserved. A global
white->alpha replacement would punch holes in those.
"""

import json
import re
import sys
from collections import deque
from pathlib import Path

from PIL import Image

# A pixel counts as background if every channel is at least this bright.
WHITE_CUTOFF = 235
# Icons are tiny; upscale so they survive being drawn at 80px in a diagram.
TARGET_MAX_EDGE = 256
# Palette size after quantization. 64 is indistinguishable from truecolour on
# this icon set and keeps the base64 payload small.
PALETTE_COLORS = 64


def load_rgb(path: Path) -> Image.Image:
    """CMYK JPEGs from this set decode with inverted channels in some tools;
    Pillow handles the conversion correctly, so just normalise to RGB."""
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def background_mask(img: Image.Image) -> set:
    """Flood fill inward from every border pixel, crossing only near-white."""
    width, height = img.size
    px = img.load()

    def is_white(x: int, y: int) -> bool:
        r, g, b = px[x, y]
        return r >= WHITE_CUTOFF and g >= WHITE_CUTOFF and b >= WHITE_CUTOFF

    seen = set()
    queue = deque()

    for x in range(width):
        for y in (0, height - 1):
            if is_white(x, y) and (x, y) not in seen:
                seen.add((x, y))
                queue.append((x, y))
    for y in range(height):
        for x in (0, width - 1):
            if is_white(x, y) and (x, y) not in seen:
                seen.add((x, y))
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen:
                if is_white(nx, ny):
                    seen.add((nx, ny))
                    queue.append((nx, ny))
    return seen


def convert(src: Path) -> Image.Image | None:
    img = load_rgb(src)
    bg = background_mask(img)

    rgba = img.convert("RGBA")
    px = rgba.load()
    for x, y in bg:
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, 0)

    bbox = rgba.getbbox()
    if bbox is None:
        return None
    rgba = rgba.crop(bbox)

    longest = max(rgba.size)
    if longest < TARGET_MAX_EDGE:
        scale = TARGET_MAX_EDGE / longest
        new_size = (round(rgba.width * scale), round(rgba.height * scale))
        rgba = rgba.resize(new_size, Image.LANCZOS)

    # These are flat-colour line drawings; the LANCZOS upscale invents
    # thousands of near-duplicate shades that PNG cannot compress. Quantizing
    # back to a palette cuts file size ~85% with no visible loss, which matters
    # because every icon is base64-embedded into the .drawio output.
    return rgba.quantize(colors=PALETTE_COLORS, method=Image.FASTOCTREE)


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def main() -> int:
    src_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    index = {}
    skipped = []

    for src in sorted(src_dir.glob("*.jpg")):
        slug = slugify(src.stem)
        img = convert(src)
        if img is None:
            skipped.append(src.name)
            continue
        dest = out_dir / f"{slug}.png"
        img.save(dest, "PNG", optimize=True)
        index[slug] = {
            "file": dest.name,
            "source": src.name,
            "w": img.width,
            "h": img.height,
        }

    (out_dir.parent / "icons.json").write_text(
        json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    )

    print(f"converted {len(index)} icons -> {out_dir}")
    if skipped:
        print(f"skipped {len(skipped)} blank: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
