#!/usr/bin/env python3
"""Generate the original placeholder wallpaper + avatar shipped with this repo.

No character art is included. The output is an abstract 'blue hour' scene so the
theme can be previewed and built without redistributing anyone else's artwork.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
W, H = 1920, 1080
random.seed(20261025)
np.random.seed(20261025)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient():
    stops = [
        (0.00, (3, 7, 10)),
        (0.32, (7, 23, 30)),
        (0.55, (11, 44, 55)),
        (0.68, (15, 66, 76)),
        (0.82, (9, 32, 40)),
        (1.00, (4, 9, 11)),
    ]
    img = Image.new("RGB", (1, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            a, ca = stops[i]
            b, cb = stops[i + 1]
            if a <= t <= b:
                px[0, y] = lerp(ca, cb, (t - a) / (b - a))
                break
    return img.resize((W, H), Image.BILINEAR)


def glow_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # teal light behind the "character" side
    for r in range(900, 0, -30):
        a = int(2.2 * (900 - r) / 900 * 40)
        d.ellipse((1240 - r, 340 - r * .72, 1240 + r, 340 + r * .72),
                  fill=(45, 190, 160, max(0, a)))
    # warm city glow on the left
    for r in range(700, 0, -25):
        a = int(1.4 * (700 - r) / 700 * 34)
        d.ellipse((430 - r, 760 - r * .55, 430 + r, 760 + r * .55),
                  fill=(210, 140, 70, max(0, a)))
    return layer.filter(ImageFilter.GaussianBlur(70))


def bokeh_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    palette = [(160, 232, 255), (214, 255, 143), (255, 216, 160), (180, 166, 255), (190, 255, 230)]
    for _ in range(64):
        x = random.uniform(-40, W + 40)
        y = random.uniform(120, H - 40)
        r = random.uniform(2.5, 34)
        c = random.choice(palette)
        a = int(random.uniform(20, 95) * (0.5 if y < 380 else 1.0))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*c, a))
    soft = layer.filter(ImageFilter.GaussianBlur(7))
    sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sharp)
    for _ in range(26):
        x = random.uniform(0, W)
        y = random.uniform(H * .35, H * .98)
        r = random.uniform(1.2, 4.2)
        c = random.choice(palette)
        ds.ellipse((x - r, y - r, x + r, y + r), fill=(*c, random.randint(40, 120)))
    return Image.alpha_composite(soft, sharp)


def skyline(base: Image.Image):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = -20
    while x < W + 20:
        w = random.randint(24, 92)
        h = random.randint(60, 240)
        top = H - h
        d.rectangle((x, top, x + w, H), fill=(2, 6, 8, 220))
        # a few lit windows
        for _ in range(random.randint(0, 4)):
            wx = random.randint(x + 4, max(x + 5, x + w - 6))
            wy = random.randint(top + 8, min(H - 6, top + h - 8))
            d.rectangle((wx, wy, wx + 2, wy + 3), fill=(180, 235, 210, random.randint(30, 90)))
        x += w + random.randint(2, 14)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    return Image.alpha_composite(base.convert("RGBA"), layer)


def beam(base: Image.Image):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    poly = [(980, -50), (1310, -50), (760, H + 50), (560, H + 50)]
    d.polygon(poly, fill=(150, 255, 215, 16))
    layer = layer.filter(ImageFilter.GaussianBlur(45))
    return Image.alpha_composite(base.convert("RGBA"), layer)


def vignette(base: Image.Image):
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-W * .25, -H * .35, W * 1.25, H * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(180))
    dark = Image.new("RGBA", (W, H), (0, 3, 4, 200))
    out = Image.composite(base.convert("RGBA"), Image.alpha_composite(base.convert("RGBA"), dark), mask)
    return out


def grain(base: Image.Image):
    arr = np.array(base).astype(np.int16)
    noise = np.random.normal(0, 4.2, (H, W, 1)).repeat(3, axis=2)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")



def moon_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = 1370, 300
    for r in range(420, 30, -12):
        a = int(1.4 * (420 - r) / 420 * 18)
        d.ellipse((cx - r, cy - r * .78, cx + r, cy + r * .78), fill=(180, 255, 235, max(0, a)))
    d.ellipse((cx - 92, cy - 92, cx + 92, cy + 92), fill=(210, 255, 240, 46))
    d.ellipse((cx - 78, cy - 78, cx + 78, cy + 78), fill=(225, 255, 245, 54))
    return layer.filter(ImageFilter.GaussianBlur(18))

def wallpaper():
    img = gradient()
    img = Image.alpha_composite(img.convert("RGBA"), glow_layer())
    img = Image.alpha_composite(img, moon_layer())
    img = Image.alpha_composite(img, bokeh_layer())
    img = skyline(img)
    img = beam(img)
    img = vignette(img).convert("RGB")
    img = grain(img)
    out = ASSETS / "wall.placeholder.jpg"
    img.save(out, quality=90, optimize=True, progressive=True)
    print("wrote", out, img.size)


def avatar():
    size = 256
    img = Image.new("RGB", (size, size), "#06100d")
    px = img.load()
    for y in range(size):
        for x in range(size):
            dx = (x - size * .5) / (size * .5)
            dy = (y - size * .5) / (size * .5)
            d = min(1.0, math.sqrt(dx * dx + dy * dy))
            t = 1 - d
            px[x, y] = (
                int(8 + 22 * t),
                int(18 + 52 * t),
                int(15 + 40 * t),
            )
    d = ImageDraw.Draw(img)
    d.ellipse((10, 10, size - 10, size - 10), outline=(111, 227, 161, 160), width=2)
    d.ellipse((20, 20, size - 20, size - 20), outline=(214, 255, 143, 40), width=1)
    font_path = "/System/Library/Fonts/Hiragino Sans GB.ttc"
    try:
        font = ImageFont.truetype(font_path, 124, index=0)
        small = ImageFont.truetype(font_path, 18, index=0)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    text = "昴"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] - 10), text,
           font=font, fill=(214, 255, 143))
    # small drum-stick ticks
    d.line((48, 196, 84, 182), fill=(111, 227, 161), width=3)
    d.line((208, 196, 172, 182), fill=(111, 227, 161), width=3)
    d.text((size / 2, 222), "SUBARU", font=small, fill=(111, 227, 161), anchor="mm")
    out = ASSETS / "avatar.placeholder.jpg"
    img.save(out, quality=92, optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    wallpaper()
    avatar()
