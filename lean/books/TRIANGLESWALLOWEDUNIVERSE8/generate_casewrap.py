#!/usr/bin/env python3
"""Generate a trippy, psychedelic casewrap PNG for the book cover."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math
import os

# Standard 6x9 book casewrap with bleed
# Front cover: 6" x 9", Back cover: 6" x 9", Spine depends on page count
# Assume ~400 pages, ~0.9" spine
# With 0.125" bleed on all sides
# Total width = back(6) + spine(0.9) + front(6) + bleeds(0.25*2 + 0.125*2) = 13.65"
# Total height = 9 + 0.25 = 9.25"
# At 300 DPI:
DPI = 300
SPINE_WIDTH = 0.9  # inches
BLEED = 0.125  # inches
COVER_W = 6.0  # inches
COVER_H = 9.0  # inches

TOTAL_W_IN = BLEED + COVER_W + SPINE_WIDTH + COVER_W + BLEED
TOTAL_H_IN = BLEED + COVER_H + BLEED

W = int(TOTAL_W_IN * DPI)
H = int(TOTAL_H_IN * DPI)

print(f"Casewrap dimensions: {W}x{H} pixels ({TOTAL_W_IN}x{TOTAL_H_IN} inches)")

# Create base image
img = np.zeros((H, W, 3), dtype=np.uint8)

# Generate psychedelic background using mathematical functions
for y in range(H):
    for x in range(W):
        # Normalized coordinates
        nx = x / W
        ny = y / H
        cx = nx - 0.5
        cy = ny - 0.5
        
        r = math.sqrt(cx*cx + cy*cy)
        theta = math.atan2(cy, cx)
        
        # Pythagorean-inspired patterns
        val1 = math.sin(nx * 30 + math.sin(ny * 15) * 3) * 0.5 + 0.5
        val2 = math.sin(ny * 25 + math.cos(nx * 20) * 2) * 0.5 + 0.5
        val3 = math.sin(r * 40 + theta * 5) * 0.5 + 0.5
        
        # Spiral pattern
        spiral = math.sin(r * 50 - theta * 8) * 0.5 + 0.5
        
        # Color channels - deep purples, electric blues, hot pinks, gold
        red = int(255 * (0.15 + 0.35 * val1 + 0.25 * spiral + 0.1 * val3))
        green = int(255 * (0.02 + 0.1 * val2 + 0.15 * val3 * spiral))
        blue = int(255 * (0.2 + 0.4 * val2 + 0.2 * val3 + 0.1 * spiral))
        
        img[y, x] = [min(255, red), min(255, green), min(255, blue)]

print("Base pattern generated, creating PIL image...")

pil_img = Image.fromarray(img)
draw = ImageDraw.Draw(pil_img)

# Add Pythagorean triangle motifs as overlay
def draw_glowing_triangle(draw, cx, cy, size, color, width=3):
    """Draw a right triangle (3-4-5 proportions)."""
    s = size
    # 3-4-5 triangle
    x1, y1 = cx - s*0.4, cy + s*0.3
    x2, y2 = cx - s*0.4, cy - s*0.3
    x3, y3 = cx + s*0.3, cy + s*0.3
    draw.line([(x1,y1),(x2,y2),(x3,y3),(x1,y1)], fill=color, width=width)

# Scatter triangles across the cover
np.random.seed(42)
colors = [(255,215,0), (255,100,200), (100,255,255), (200,150,255), (255,180,50)]
for _ in range(80):
    cx = np.random.randint(0, W)
    cy = np.random.randint(0, H)
    size = np.random.randint(20, 120)
    color = colors[np.random.randint(0, len(colors))]
    alpha_color = tuple(int(c * (0.3 + 0.7*np.random.random())) for c in color)
    draw_glowing_triangle(draw, cx, cy, size, alpha_color, width=np.random.randint(1,4))

# Draw concentric spirals with golden ratio
for i in range(500):
    t = i * 0.05
    r_spiral = t * 3
    x = int(W * 0.75 + r_spiral * math.cos(t))
    y = int(H * 0.5 + r_spiral * math.sin(t))
    if 0 <= x < W and 0 <= y < H:
        color = (
            int(128 + 127 * math.sin(t * 0.3)),
            int(50 + 50 * math.sin(t * 0.5 + 2)),
            int(128 + 127 * math.cos(t * 0.4))
        )
        draw.ellipse([x-2, y-2, x+2, y+2], fill=color)

# Add more spirals on back cover
for i in range(500):
    t = i * 0.05
    r_spiral = t * 2.5
    x = int(W * 0.25 + r_spiral * math.cos(t + 1))
    y = int(H * 0.5 + r_spiral * math.sin(t + 1))
    if 0 <= x < W and 0 <= y < H:
        color = (
            int(128 + 127 * math.sin(t * 0.4 + 1)),
            int(80 + 80 * math.sin(t * 0.3 + 3)),
            int(128 + 127 * math.cos(t * 0.5 + 2))
        )
        draw.ellipse([x-2, y-2, x+2, y+2], fill=color)

# --- TEXT on FRONT COVER ---
front_left = int((BLEED + COVER_W + SPINE_WIDTH) * DPI)
front_right = int((BLEED + COVER_W + SPINE_WIDTH + COVER_W) * DPI)
front_cx = (front_left + front_right) // 2
top_y = int(BLEED * DPI)

# Try to use a good font
try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 90)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 42)
    author_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 48)
    spine_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 36)
    back_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 30)
    isbn_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
except:
    title_font = ImageFont.load_default()
    subtitle_font = title_font
    author_font = title_font
    spine_font = title_font
    back_font = title_font
    isbn_font = title_font

# Semi-transparent overlay for text areas on front
overlay = Image.new('RGBA', pil_img.size, (0,0,0,0))
overlay_draw = ImageDraw.Draw(overlay)

# Dark band at top of front cover for title
overlay_draw.rectangle([front_left + 60, top_y + 100, front_right - 60, top_y + 650], fill=(0, 0, 0, 160))

# Convert to RGBA for compositing
pil_img = pil_img.convert('RGBA')
pil_img = Image.alpha_composite(pil_img, overlay)

# Now draw text on the composited image
draw = ImageDraw.Draw(pil_img)

# Title - front cover
title_lines = ["THE TRIANGLE", "THAT SWALLOWED", "THE UNIVERSE"]
y_pos = top_y + 140
for line in title_lines:
    bbox = draw.textbbox((0,0), line, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text((front_cx - tw//2, y_pos), line, fill=(255, 215, 0), font=title_font)
    y_pos += 110

# Subtitle
subtitle = "From Pythagoras to Einstein"
bbox = draw.textbbox((0,0), subtitle, font=subtitle_font)
tw = bbox[2] - bbox[0]
draw.text((front_cx - tw//2, y_pos + 30), subtitle, fill=(200, 180, 255), font=subtitle_font)

# Author - bottom of front cover
author = "Paul Klemstine"
bbox = draw.textbbox((0,0), author, font=author_font)
tw = bbox[2] - bbox[0]
draw.text((front_cx - tw//2, H - top_y - 200), author, fill=(255, 255, 255), font=author_font)

# --- SPINE TEXT ---
spine_left = int((BLEED + COVER_W) * DPI)
spine_right = int((BLEED + COVER_W + SPINE_WIDTH) * DPI)
spine_cx = (spine_left + spine_right) // 2

# Draw dark spine background
draw.rectangle([spine_left, 0, spine_right, H], fill=(20, 5, 30, 220))

# Spine text (rotated)
spine_text = "THE TRIANGLE THAT SWALLOWED THE UNIVERSE"
spine_author = "Klemstine"

# Create rotated text for spine
spine_txt_img = Image.new('RGBA', (H, int(SPINE_WIDTH * DPI)), (0,0,0,0))
spine_draw = ImageDraw.Draw(spine_txt_img)

bbox = spine_draw.textbbox((0,0), spine_text, font=spine_font)
tw = bbox[2] - bbox[0]
spine_draw.text(((H - tw)//2, 10), spine_text, fill=(255, 215, 0), font=spine_font)

bbox2 = spine_draw.textbbox((0,0), spine_author, font=spine_font)
tw2 = bbox2[2] - bbox2[0]
spine_draw.text(((H - tw2)//2, 55), spine_author, fill=(255, 255, 255), font=spine_font)

spine_txt_img = spine_txt_img.rotate(90, expand=True)
pil_img.paste(spine_txt_img, (spine_left, 0), spine_txt_img)

# --- BACK COVER ---
back_left = int(BLEED * DPI)
back_right = int((BLEED + COVER_W) * DPI)
back_cx = (back_left + back_right) // 2

# Semi-transparent overlay for back cover text area
overlay2 = Image.new('RGBA', pil_img.size, (0,0,0,0))
overlay2_draw = ImageDraw.Draw(overlay2)
overlay2_draw.rectangle([back_left + 60, top_y + 100, back_right - 60, top_y + 900], fill=(0, 0, 0, 140))
pil_img = Image.alpha_composite(pil_img, overlay2)
draw = ImageDraw.Draw(pil_img)

# Back cover blurb
blurb_lines = [
    "What if the world's oldest equation",
    "held the key to the world's hardest",
    "codes?",
    "",
    "From Babylonian rope-stretchers to",
    "Einstein's light cones, from quantum",
    "circuits to the deepest mysteries of",
    "prime numbers — this is the story of",
    "how a simple right triangle grew into",
    "a universe of mathematics.",
    "",
    "A journey through number theory,",
    "algebra, geometry, and physics that",
    "reveals the hidden connections binding",
    "the most ancient and modern ideas",
    "in mathematics.",
]

y_pos = top_y + 140
for line in blurb_lines:
    if line == "":
        y_pos += 20
        continue
    bbox = draw.textbbox((0,0), line, font=back_font)
    tw = bbox[2] - bbox[0]
    draw.text((back_cx - tw//2, y_pos), line, fill=(230, 220, 255), font=back_font)
    y_pos += 40

# ISBN barcode on back cover
isbn_barcode_path = "/workspace/request-project/ISBN/978-1-105-41110-6.png"
if os.path.exists(isbn_barcode_path):
    barcode_img = Image.open(isbn_barcode_path).convert('RGBA')
    # Scale barcode to fit nicely
    bc_w, bc_h = barcode_img.size
    target_w = int(COVER_W * 0.4 * DPI)
    scale = target_w / bc_w
    new_w = int(bc_w * scale)
    new_h = int(bc_h * scale)
    barcode_img = barcode_img.resize((new_w, new_h), Image.LANCZOS)
    
    # White background behind barcode
    bc_x = back_cx - new_w // 2
    bc_y = H - top_y - new_h - 150
    draw.rectangle([bc_x - 20, bc_y - 20, bc_x + new_w + 20, bc_y + new_h + 20], fill=(255, 255, 255, 255))
    pil_img.paste(barcode_img, (bc_x, bc_y), barcode_img)
    
    # ISBN text below barcode
    isbn_text = "ISBN 978-1-105-41110-6"
    bbox = draw.textbbox((0,0), isbn_text, font=isbn_font)
    tw = bbox[2] - bbox[0]
    draw.text((back_cx - tw//2, bc_y + new_h + 25), isbn_text, fill=(255, 255, 255), font=isbn_font)

# Add some more psychedelic elements - mandala pattern on front
front_center_y = int(H * 0.58)
for ring in range(8):
    r = 80 + ring * 40
    n_pts = 12 + ring * 4
    for i in range(n_pts):
        angle = 2 * math.pi * i / n_pts
        x = int(front_cx + r * math.cos(angle))
        y = int(front_center_y + r * math.sin(angle))
        color = (
            int(200 + 55 * math.sin(ring * 0.8)),
            int(100 + 100 * math.sin(ring * 0.5 + 1)),
            int(200 + 55 * math.cos(ring * 0.7))
        )
        # Small triangle at each point
        s = 8 + ring * 2
        pts = [(x, y-s), (x-s, y+s//2), (x+s, y+s//2)]
        draw.polygon(pts, fill=color + (180,), outline=(255,255,255,100))

# Convert to RGB for final save
final_img = pil_img.convert('RGB')
final_img.save('/workspace/request-project/casewrap.png', 'PNG', dpi=(300, 300))
print(f"Casewrap saved: {W}x{H} at 300 DPI")
