from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
from io import BytesIO
import base64
import random
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ---------- Fonts

def _try_font(paths: List[str], size: int) -> Optional[ImageFont.FreeTypeFont]:
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    return None

def load_font(size: int, weight: str = "regular") -> ImageFont.ImageFont:
    # Common system font candidates; add more if you have them
    CANDIDATES = {
        "regular": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/SFNS.ttf",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
        "bold": [
            "/System/Library/Fonts/SFNSBold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        "mono": [
            "/Library/Fonts/Menlo.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ],
    }
    font = _try_font(CANDIDATES.get(weight, CANDIDATES["regular"]), size)
    if font:
        return font
    # Fallback
    return ImageFont.load_default()


# ---------- Colors / themes

BRANDS: dict[str, Tuple[str, str, str]] = {
    # name: (start_hex, end_hex, accent_hex)
    "slate":   ("#1f2937", "#0b1220", "#93c5fd"),
    "indigo":  ("#3730a3", "#0f172a", "#a5b4fc"),
    "emerald": ("#065f46", "#052e2b", "#6ee7b7"),
    "rose":    ("#7f1d1d", "#111827", "#fda4af"),
    "amber":   ("#92400e", "#111827", "#fcd34d"),
}

def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


# ---------- Layout helpers

def draw_gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    a = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.linear_gradient("L").resize((w, h)).filter(ImageFilter.GaussianBlur(2))
    return Image.composite(top, a, mask)

def rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> List[str]:
    words = text.strip().split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

def draw_text_block(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, max_w: int, line_h: float, fill=(255,255,255)) -> int:
    lines = wrap(draw, text, font, max_w)
    for i, ln in enumerate(lines):
        draw.text((x, y + int(i * line_h)), ln, font=font, fill=fill)
    return y + int(len(lines) * line_h)

def stroke_text(draw, pos, text, font, fill, stroke_fill=(0,0,0), stroke_width=2):
    draw.text(pos, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


# ---------- Poster templates

@dataclass
class PosterSpec:
    title: str
    bullets: List[str]
    template: str  # "poster" | "split" | "quote" | "stat"
    brand: str
    width: int
    height: int
    seed: Optional[int] = None

def poster_bytes(spec: PosterSpec) -> bytes:
    r = random.Random(spec.seed or (hash(spec.title) & 0xFFFF))

    start, end, accent = BRANDS.get(spec.brand, BRANDS["slate"])
    bg = draw_gradient(spec.width, spec.height, start, end)
    draw = ImageDraw.Draw(bg)

    # Card inset for clean margins
    pad = int(0.06 * spec.width)
    card = (pad, pad, spec.width - pad, spec.height - pad)
    rounded_rect(draw, card, radius=int(0.06 * spec.width), fill=(0, 0, 0, 0))  # just masks corners visually

    # Typography
    title_font = load_font(int(spec.width * 0.075), "bold")
    body_font  = load_font(int(spec.width * 0.042), "regular")
    small_font = load_font(int(spec.width * 0.032), "regular")

    x0, y0 = card[0] + int(0.07 * spec.width), card[1] + int(0.08 * spec.height)
    max_w = card[2] - x0 - int(0.07 * spec.width)
    line_h_title = int(title_font.size * 1.18)
    line_h_body  = int(body_font.size * 1.38)

    # Template variants
    if spec.template == "quote":
        # Big quotation mark accent
        q = "“"
        stroke_text(draw, (x0, y0 - int(title_font.size * 0.4)), q, title_font, fill=hex_to_rgb(accent))
        y0 += int(title_font.size * 0.3)

    if spec.template == "split":
        # Title left, bullets right
        mid_x = spec.width // 2
        # left title
        y = y0
        y = draw_text_block(draw, x0, y, spec.title, title_font, max_w=mid_x - x0 - 20, line_h=line_h_title)
        # right bullets
        bx = mid_x + 20
        by = y0
        for b in spec.bullets[:6]:
            bullet = f"• {b}"
            by = draw_text_block(draw, bx, by, bullet, body_font, max_w=card[2] - bx, line_h=line_h_body)
        # accent bar
        draw.rectangle([mid_x - 4, y0, mid_x, by], fill=hex_to_rgb(accent))
    elif spec.template == "stat":
        # Title as number first token
        parts = spec.title.split(None, 1)
        num = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        big_font = load_font(int(spec.width * 0.18), "bold")
        stroke_text(draw, (x0, y0), num, big_font, fill=(255,255,255))
        y = y0 + int(big_font.size * 0.9)
        y = draw_text_block(draw, x0, y + 10, rest, title_font, max_w=max_w, line_h=line_h_title)
        y += 10
        for b in spec.bullets[:4]:
            y = draw_text_block(draw, x0, y, f"• {b}", body_font, max_w=max_w, line_h=line_h_body)
    else:
        # "poster" default: headline + up to 6 bullets
        y = draw_text_block(draw, x0, y0, spec.title, title_font, max_w=max_w, line_h=line_h_title)
        y += int(0.02 * spec.height)
        for b in spec.bullets[:6]:
            y = draw_text_block(draw, x0, y, f"• {b}", body_font, max_w=max_w, line_h=line_h_body)

    # Footer tag
    footer = "Influence OS — Prototype"
    fw = draw.textlength(footer, font=small_font)
    draw.text((spec.width - pad - fw, spec.height - pad - small_font.size - 6), footer, font=small_font, fill=(220, 225, 233))

    buf = BytesIO()
    bg.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---------- Public API used by router

def generate_image(
    title: str,
    bullets: Optional[List[str]] = None,
    template: str = "poster",
    brand: str = "slate",
    ratio: str = "square",
    width: int = 1080,
    seed: Optional[int] = None,
) -> str:
    """Return data URL (PNG)"""
    if ratio == "portrait":
        height = int(width * 1.25)  # 1080x1350-ish
    elif ratio == "landscape":
        height = int(width * 0.56)
    else:
        height = width

    img_bytes = poster_bytes(
        PosterSpec(
            title=title.strip(),
            bullets=[b.strip() for b in (bullets or []) if b.strip()],
            template=template,
            brand=brand,
            width=width,
            height=height,
            seed=seed,
        )
    )
    b64 = base64.b64encode(img_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"
