#!/usr/bin/env python3
"""Generate a psychedelic casewrap cover for the book."""

import math
from PIL import Image, ImageDraw, ImageFont

# Full casewrap dimensions (front + spine + back) at 300 DPI
# Assuming 8.5 x 11 inch trim, ~1 inch spine, 0.125 inch bleed on all sides
W_FRONT = 2550  # 8.5 * 300
W_SPINE = 300  # ~1 inch spine
W_BACK = 2550
H = 3300  # 11 * 300
BLEED = 38  # 0.125 * 300

TOTAL_W = W_BACK + W_SPINE + W_FRONT + 2 * BLEED
TOTAL_H = H + 2 * BLEED

img = Image.new("RGB", (TOTAL_W, TOTAL_H), (0, 0, 0))
draw = ImageDraw.Draw(img)


# Helper: psychedelic color from angle
def psychedelic_color(t, intensity=1.0):
    r = int(127.5 * (1 + math.sin(t)) * intensity)
    g = int(127.5 * (1 + math.sin(t + 2.094)) * intensity)
    b = int(127.5 * (1 + math.sin(t + 4.189)) * intensity)
    return (min(255, r), min(255, g), min(255, b))


cx = TOTAL_W // 2
cy = TOTAL_H // 2

# Layer 1: Radial psychedelic gradient with interference patterns
# Use step-based approach for speed
print("Generating background...")
for y in range(0, TOTAL_H, 2):
    for x in range(0, TOTAL_W, 2):
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)

        # Multiple interfering wave patterns
        wave1 = math.sin(dist * 0.02 + angle * 3)
        wave2 = math.sin(dist * 0.015 - angle * 5)
        wave3 = math.sin(dist * 0.008 + angle * 7)
        wave4 = math.cos(dist * 0.025 + angle * 2)

        t = wave1 + wave2 * 0.7 + wave3 * 0.5 + wave4 * 0.3

        # Deep space background fade
        fade = max(0.15, 1.0 - dist / (TOTAL_W * 0.6))

        r = int(min(255, max(0, 127.5 * (1 + math.sin(t * 2.5)) * fade)))
        g = int(min(255, max(0, 127.5 * (1 + math.sin(t * 2.5 + 2.5)) * fade * 0.8)))
        b = int(min(255, max(0, 127.5 * (1 + math.sin(t * 2.5 + 4.5)) * fade)))

        color = (r, g, b)
        img.putpixel((x, y), color)
        if x + 1 < TOTAL_W:
            img.putpixel((x + 1, y), color)
        if y + 1 < TOTAL_H:
            img.putpixel((x, y + 1), color)
            if x + 1 < TOTAL_W:
                img.putpixel((x + 1, y + 1), color)

print("Background done. Adding overlays...")

# Layer 2: Pythagorean triangles radiating from center (front cover area)
front_cx = BLEED + W_BACK + W_SPINE + W_FRONT // 2
front_cy = TOTAL_H // 2

for i in range(12):
    angle = i * math.pi / 6
    scale = 200 + i * 40

    x0 = int(front_cx + scale * math.cos(angle))
    y0 = int(front_cy + scale * math.sin(angle))
    x1 = int(front_cx + scale * 1.5 * math.cos(angle + 0.3))
    y1 = int(front_cy + scale * 1.5 * math.sin(angle + 0.3))
    x2 = int(front_cx + scale * 1.2 * math.cos(angle - 0.2))
    y2 = int(front_cy + scale * 1.2 * math.sin(angle - 0.2))

    color = psychedelic_color(angle * 3 + i * 0.5, 0.9)
    draw.polygon([(x0, y0), (x1, y1), (x2, y2)], outline=color, width=3)


# Layer 3: Ternary tree branching pattern
def draw_tree_branch(draw, x, y, length, angle, depth, max_depth):
    if depth > max_depth or length < 5:
        return
    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)
    color = psychedelic_color(depth * 1.5 + angle, 0.7)
    draw.line(
        [(int(x), int(y)), (int(x2), int(y2))], fill=color, width=max(1, 4 - depth)
    )

    for da in [-0.5, 0, 0.5]:
        draw_tree_branch(draw, x2, y2, length * 0.65, angle + da, depth + 1, max_depth)


draw_tree_branch(draw, front_cx, front_cy + 600, 250, -math.pi / 2, 0, 6)

# Layer 4: Concentric light cone rings
for r in range(50, 1200, 80):
    color = psychedelic_color(r * 0.05, 0.4)
    bbox = [front_cx - r, front_cy - r, front_cx + r, front_cy + r]
    draw.ellipse(bbox, outline=color, width=2)

# Fonts
try:
    font_large = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 120
    )
    font_title = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 90
    )
    font_subtitle = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 48
    )
    font_author = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 56
    )
    font_spine = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 36
    )
    font_back = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36
    )
    font_small = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 28
    )
except:
    font_large = ImageFont.load_default()
    font_title = font_large
    font_subtitle = font_large
    font_author = font_large
    font_spine = font_large
    font_back = font_large
    font_small = font_large

# Central equation on front cover
eq_text = "a\u00b2 + b\u00b2 = c\u00b2"
bbox_eq = draw.textbbox((0, 0), eq_text, font=font_large)
tw = bbox_eq[2] - bbox_eq[0]
for offset in range(8, 0, -1):
    glow_alpha = int(255 * (1 - offset / 8))
    glow_color = (glow_alpha, glow_alpha // 2, glow_alpha)
    draw.text(
        (front_cx - tw // 2 - offset, front_cy - 60 - offset),
        eq_text,
        fill=glow_color,
        font=font_large,
    )
    draw.text(
        (front_cx - tw // 2 + offset, front_cy - 60 + offset),
        eq_text,
        fill=glow_color,
        font=font_large,
    )
draw.text(
    (front_cx - tw // 2, front_cy - 60), eq_text, fill=(255, 255, 255), font=font_large
)

# Title
title1 = "THE TRIANGLE THAT"
title2 = "SWALLOWED THE UNIVERSE"
for t, yoff in [(title1, -500), (title2, -390)]:
    bb = draw.textbbox((0, 0), t, font=font_title)
    tw = bb[2] - bb[0]
    for off in range(5, 0, -1):
        draw.text(
            (front_cx - tw // 2 + off, front_cy + yoff + off),
            t,
            fill=(100, 80, 0),
            font=font_title,
        )
    draw.text(
        (front_cx - tw // 2, front_cy + yoff), t, fill=(255, 215, 100), font=font_title
    )

# Subtitle
sub = "Pythagorean Triples, Berggren Trees,"
sub2 = "and the Hidden Geometry of Everything"
for t, yoff in [(sub, 200), (sub2, 270)]:
    bb = draw.textbbox((0, 0), t, font=font_subtitle)
    tw = bb[2] - bb[0]
    draw.text(
        (front_cx - tw // 2, front_cy + yoff),
        t,
        fill=(200, 220, 255),
        font=font_subtitle,
    )

# Author
author = "Paul Klemstine"
bb = draw.textbbox((0, 0), author, font=font_author)
tw = bb[2] - bb[0]
draw.text(
    (front_cx - tw // 2, TOTAL_H - 400), author, fill=(255, 215, 100), font=font_author
)

# === SPINE ===
spine_cx = BLEED + W_BACK + W_SPINE // 2
spine_img = Image.new("RGB", (TOTAL_H, W_SPINE), (20, 10, 30))
spine_draw = ImageDraw.Draw(spine_img)
spine_text = "THE TRIANGLE THAT SWALLOWED THE UNIVERSE"
bb = spine_draw.textbbox((0, 0), spine_text, font=font_spine)
tw = bb[2] - bb[0]
spine_draw.text(
    (TOTAL_H // 2 - tw // 2, W_SPINE // 2 - 20),
    spine_text,
    fill=(255, 215, 100),
    font=font_spine,
)
author_spine = "Paul Klemstine"
bb2 = spine_draw.textbbox((0, 0), author_spine, font=font_small)
tw2 = bb2[2] - bb2[0]
spine_draw.text(
    (TOTAL_H - tw2 - 100, W_SPINE // 2 - 16),
    author_spine,
    fill=(200, 200, 200),
    font=font_small,
)
spine_rotated = spine_img.rotate(90, expand=True)
img.paste(spine_rotated, (BLEED + W_BACK, 0))

# === BACK COVER ===
back_cx = BLEED + W_BACK // 2
back_top = 300

blurb_lines = [
    "What if the world\u2019s oldest equation\u2014",
    "a\u00b2 + b\u00b2 = c\u00b2\u2014contained the seeds of",
    "an infinite tree, a spacetime geometry,",
    "a factoring algorithm, and a tower of",
    "algebras reaching into eight dimensions?",
    "",
    "From ancient Babylonian clay tablets to",
    "quantum computing, from Einstein\u2019s light",
    "cones to Fermat\u2019s Last Theorem, this book",
    "reveals the astonishing hidden life of the",
    "Pythagorean equation\u2014with full formal",
    "proofs verified in the Lean 4 theorem prover.",
]

y_pos = back_top
for line in blurb_lines:
    if line:
        bb = draw.textbbox((0, 0), line, font=font_back)
        tw = bb[2] - bb[0]
        draw.text(
            (back_cx - tw // 2, y_pos), line, fill=(220, 220, 240), font=font_back
        )
    y_pos += 50

# ISBN text
isbn_text = "ISBN 978-1-105-41110-6"
bb = draw.textbbox((0, 0), isbn_text, font=font_small)
tw = bb[2] - bb[0]
# draw.text((back_cx - tw//2, TOTAL_H - 650), isbn_text, fill=(200, 200, 200), font=font_small)

# ISBN barcode
try:
    barcode = Image.open("/workspace/request-project/ISBN/978-1-105-41110-6.png")
    bc_w = 600
    bc_h = int(barcode.height * bc_w / barcode.width)
    barcode = barcode.resize((bc_w, bc_h), Image.LANCZOS)
    bx = back_cx - bc_w // 2
    by = TOTAL_H - 550
    draw.rectangle(
        [bx - 20, by - 20, bx + bc_w + 20, by + bc_h + 20], fill=(255, 255, 255)
    )
    # img.paste(barcode, (bx, by))
    print("Barcode placed successfully")
except Exception as e:
    print(f"Barcode paste failed: {e}")

img.save("cover_casewrap.png", "PNG", dpi=(300, 300))
print(f"Cover saved: {TOTAL_W}x{TOTAL_H} pixels")
