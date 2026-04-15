#!/usr/bin/env python3
"""Create a psychedelic, trippy casewrap cover for the book.
   Full casewrap with front cover, spine, back cover, and ISBN barcode."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
import os
import colorsys

# --- BOOK DIMENSIONS ---
TRIM_W = 6.0     # inches (cover width)
TRIM_H = 9.0     # inches (cover height)
SPINE_W = 1.25   # inches (~547 pages)
BLEED = 0.125    # inches
WRAP = 0.625     # inches
DPI = 300

total_w = 2 * TRIM_W + SPINE_W + 2 * BLEED + 2 * WRAP
total_h = TRIM_H + 2 * BLEED + 2 * WRAP
pw = int(total_w * DPI)
ph = int(total_h * DPI)

print(f"Cover: {total_w:.2f}\" x {total_h:.2f}\" ({pw}x{ph}px)")

# --- CREATE BASE ---
img = Image.new('RGB', (pw, ph), (5, 2, 15))
draw = ImageDraw.Draw(img)
random.seed(42)

# --- HELPER FUNCTIONS ---
def hsv_color(h, s=0.9, v=0.95):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def blend(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

# --- BACKGROUND: Deep space nebula with swirling psychedelic patterns ---
print("Drawing background...")
for y in range(ph):
    for x in range(0, pw, 1):
        cx, cy = pw / 2, ph / 2
        dx, dy = (x - cx) / pw, (y - cy) / ph
        dist = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)
        
        # Multi-layered spiral pattern
        spiral1 = angle / (2 * math.pi) + dist * 4
        spiral2 = angle / (2 * math.pi) - dist * 3 + 0.5
        wave = 0.3 * math.sin(dist * 25 + angle * 3)
        ripple = 0.15 * math.cos(x / 50 + y / 70)
        
        t = spiral1 + wave + ripple
        
        # Deep cosmic color palette: purples, deep blues, magentas, teals
        h = (t * 0.15 + 0.7) % 1.0
        s = 0.75 + 0.2 * math.sin(dist * 12)
        v = 0.08 + 0.18 * max(0, 1 - dist * 1.5)
        
        # Add nebula clouds
        cloud = (math.sin(x / 100 + y / 80) * 
                 math.cos(x / 60 - y / 90) * 
                 math.sin(x / 40 + y / 50))
        v += 0.08 * max(0, cloud)
        
        # Brighter near edges for psychedelic border
        edge_dist = min(x, y, pw - x, ph - y) / (DPI * 0.5)
        if edge_dist < 1:
            v += 0.05 * (1 - edge_dist)
            s = min(1.0, s + 0.1 * (1 - edge_dist))
        
        v = max(0.03, min(0.5, v))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        img.putpixel((x, y), (int(r * 255), int(g * 255), int(b * 255)))

print("Background done")

# --- SACRED GEOMETRY PATTERNS ---
print("Drawing sacred geometry...")

# Key positions
front_left = int((WRAP + BLEED + SPINE_W + TRIM_W) * DPI)
front_right = int((WRAP + BLEED + SPINE_W + 2 * TRIM_W) * DPI)
front_cx = (front_left + front_right) // 2
front_top = int((WRAP + BLEED) * DPI)
front_bottom = int((WRAP + BLEED + TRIM_H) * DPI)
front_cy = (front_top + front_bottom) // 2

back_left = int(WRAP * DPI)
back_right = int((WRAP + BLEED + TRIM_W) * DPI)
back_cx = (back_left + back_right) // 2
back_cy = front_cy

spine_left = int((WRAP + BLEED + TRIM_W) * DPI)
spine_right = int((WRAP + BLEED + TRIM_W + SPINE_W) * DPI)
spine_cx = (spine_left + spine_right) // 2

# Mandala on front cover: concentric rings of triangles
for ring in range(3, 30):
    n = ring * 4 + 3
    radius = ring * 20 + 30
    for j in range(n):
        angle = j * 2 * math.pi / n + ring * 0.15
        cx = front_cx + int(radius * math.cos(angle))
        cy = front_cy + 80 + int(radius * math.sin(angle))
        size = max(4, 25 - ring * 0.7)
        hue = (ring * 0.04 + j * 0.01 + 0.6) % 1.0
        
        pts = []
        for k in range(3):
            a = angle + k * 2 * math.pi / 3 + ring * 0.05
            pts.append((int(cx + size * math.cos(a)), int(cy + size * math.sin(a))))
        
        color = hsv_color(hue, 0.85, 0.6 + 0.3 * math.sin(ring * 0.3))
        draw.polygon(pts, outline=color, width=1)

# Glowing concentric circles at center
for r in range(250, 5, -3):
    hue = (r / 250.0) * 0.4 + 0.55
    alpha = max(30, int(200 * (1 - r / 250.0)))
    color = hsv_color(hue, 0.7, 0.5 * (1 - r / 500.0) + 0.1)
    draw.ellipse([front_cx - r, front_cy + 80 - r, 
                  front_cx + r, front_cy + 80 + r],
                 outline=color, width=1)

# The sacred 3-4-5 triangle at center
scale = 50
tri_cx, tri_cy = front_cx, front_cy + 80
pts_345 = [
    (tri_cx - int(1.5 * scale), tri_cy + int(2 * scale)),
    (tri_cx + int(2.5 * scale), tri_cy + int(2 * scale)),
    (tri_cx - int(1.5 * scale), tri_cy - int(1 * scale)),
]
# Multi-color glow
for w in range(12, 0, -1):
    hue = 0.08 + w * 0.04
    color = hsv_color(hue, 0.9, 0.4 + w * 0.05)
    draw.polygon(pts_345, outline=color, width=w)

# Right angle mark
draw.rectangle([pts_345[0][0], pts_345[0][1] - 18,
                pts_345[0][0] + 18, pts_345[0][1]], 
               outline=hsv_color(0.15, 0.9, 0.9), width=2)

# 3, 4, 5 labels
try:
    label_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 18)
except:
    label_font = ImageFont.load_default()

draw.text((tri_cx - int(1.5*scale) - 25, tri_cy + int(0.3*scale)), "3", 
          font=label_font, fill=hsv_color(0.1, 0.9, 0.95))
draw.text((tri_cx + int(0.3*scale), tri_cy + int(2*scale) + 5), "4", 
          font=label_font, fill=hsv_color(0.1, 0.9, 0.95))
draw.text((tri_cx + int(0.8*scale), tri_cy + int(0.3*scale)), "5", 
          font=label_font, fill=hsv_color(0.1, 0.9, 0.95))

# Fractal Pythagorean tree on back cover
def draw_ptree(draw, x, y, size, angle, depth, hue_base):
    if depth <= 0 or size < 2:
        return
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    dx1, dy1 = size * cos_a, size * sin_a
    dx2, dy2 = -size * sin_a, size * cos_a
    
    corners = [
        (x, y), (x + dx1, y + dy1),
        (x + dx1 + dx2, y + dy2 + dy1), (x + dx2, y + dy2)
    ]
    
    hue = (hue_base + depth * 0.06) % 1.0
    color = hsv_color(hue, 0.8, 0.3 + depth * 0.07)
    draw.polygon([(int(cx), int(cy)) for cx, cy in corners], outline=color, width=max(1, depth // 3))
    
    top_left, top_right = corners[3], corners[2]
    draw_ptree(draw, top_left[0], top_left[1], size * 0.65, angle + 0.55, depth - 1, hue_base + 0.08)
    draw_ptree(draw, top_right[0] - size * 0.55 * cos_a, top_right[1] - size * 0.55 * sin_a,
               size * 0.55, angle - 0.45, depth - 1, hue_base + 0.2)

# Trees on back cover
draw_ptree(draw, back_cx - 100, back_cy + 300, 50, -math.pi/2, 9, 0.0)
draw_ptree(draw, back_cx + 100, back_cy + 250, 40, -math.pi/2, 8, 0.4)

# Smaller trees scattered
draw_ptree(draw, front_cx - 350, front_cy + 500, 25, -math.pi/2, 7, 0.2)
draw_ptree(draw, front_cx + 400, front_cy + 450, 30, -math.pi/2, 7, 0.6)

# Stars scattered across
for _ in range(200):
    sx = random.randint(0, pw)
    sy = random.randint(0, ph)
    brightness = random.randint(100, 255)
    size = random.randint(1, 3)
    draw.ellipse([sx, sy, sx + size, sy + size], fill=(brightness, brightness, brightness + 20))

print("Sacred geometry done")

# --- TEXT ---
print("Adding text...")

font_paths = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf',
]
font_paths_regular = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
]

font_title = font_author = font_sub = font_small = font_spine = None

for fp in font_paths:
    if os.path.exists(fp):
        font_title = ImageFont.truetype(fp, 68)
        font_author = ImageFont.truetype(fp, 40)
        font_sub = ImageFont.truetype(fp, 26)
        font_small = ImageFont.truetype(fp, 18)
        font_spine = ImageFont.truetype(fp, 20)
        break

if font_title is None:
    font_title = ImageFont.load_default()
    font_author = font_sub = font_small = font_spine = font_title

font_sub_it = None
for fp in font_paths_regular:
    if os.path.exists(fp):
        font_sub_it = ImageFont.truetype(fp, 24)
        break
if font_sub_it is None:
    font_sub_it = font_sub

front_w = front_right - front_left

# Title with glow
title_lines = ["THE TRIANGLE", "THAT SWALLOWED", "THE UNIVERSE"]
y_pos = front_top + 80
for line in title_lines:
    bbox = draw.textbbox((0, 0), line, font=font_title)
    tw = bbox[2] - bbox[0]
    x_pos = front_left + (front_w - tw) // 2
    
    # Outer glow
    for offset in range(6, 0, -1):
        gc = hsv_color(0.7 + offset * 0.03, 0.6, 0.3 + offset * 0.05)
        draw.text((x_pos + offset, y_pos + offset), line, font=font_title, fill=gc)
        draw.text((x_pos - offset, y_pos + offset), line, font=font_title, fill=gc)
        draw.text((x_pos + offset, y_pos - offset), line, font=font_title, fill=gc)
        draw.text((x_pos - offset, y_pos - offset), line, font=font_title, fill=gc)
    
    # Main text
    draw.text((x_pos, y_pos), line, font=font_title, fill=(255, 255, 255))
    y_pos += 78

# Subtitle
subtitles = [
    "How Pythagorean Triples Connect",
    "Number Theory, Spacetime,",
    "and the Art of Factoring"
]
y_pos += 30
for st in subtitles:
    bbox = draw.textbbox((0, 0), st, font=font_sub_it)
    tw = bbox[2] - bbox[0]
    x_pos = front_left + (front_w - tw) // 2
    draw.text((x_pos, y_pos), st, font=font_sub_it, fill=(180, 200, 240))
    y_pos += 32

# Decorative line
line_y = y_pos + 15
draw.line([(front_cx - 200, line_y), (front_cx + 200, line_y)], 
          fill=hsv_color(0.6, 0.5, 0.5), width=2)

# "With formal proofs verified in Lean 4"
lean_text = "With formal proofs verified in Lean 4"
bbox = draw.textbbox((0, 0), lean_text, font=font_small)
tw = bbox[2] - bbox[0]
draw.text((front_left + (front_w - tw) // 2, line_y + 15), 
          lean_text, font=font_small, fill=(140, 160, 200))

# Author name
author = "Paul Klemstine"
bbox = draw.textbbox((0, 0), author, font=font_author)
tw = bbox[2] - bbox[0]
draw.text((front_left + (front_w - tw) // 2, front_bottom - 180), 
          author, font=font_author, fill=(255, 255, 255))

# --- SPINE ---
# Vertical fold lines (subtle)
draw.line([(spine_left, 0), (spine_left, ph)], fill=(40, 35, 60), width=2)
draw.line([(spine_right, 0), (spine_right, ph)], fill=(40, 35, 60), width=2)

# Spine text (rotated)
spine_h = spine_right - spine_left
spine_w = front_bottom - front_top

spine_text_img = Image.new('RGBA', (spine_w, spine_h), (0, 0, 0, 0))
sd = ImageDraw.Draw(spine_text_img)

# Spine title
spine_title = "THE TRIANGLE THAT SWALLOWED THE UNIVERSE"
bbox = sd.textbbox((0, 0), spine_title, font=font_spine)
tw = bbox[2] - bbox[0]
sd.text(((spine_w - tw) // 2, (spine_h - 22) // 2 - 2), 
        spine_title, font=font_spine, fill=(220, 220, 240))

# Spine author (at bottom)
spine_author_text = "KLEMSTINE"
bbox = sd.textbbox((0, 0), spine_author_text, font=font_small)
tw = bbox[2] - bbox[0]
sd.text((spine_w - tw - 30, (spine_h - 20) // 2 - 2), 
        spine_author_text, font=font_small, fill=(180, 180, 200))

# Rotate 90 degrees
rotated = spine_text_img.rotate(90, expand=True)
paste_x = spine_left + (spine_right - spine_left - rotated.width) // 2
paste_y = front_top
img.paste(rotated, (paste_x, paste_y), rotated)

# --- BACK COVER ---
back_w = back_right - back_left

# Blurb text
blurb = [
    "What do an Egyptian rope-stretcher, a Babylonian",
    "clay tablet, and Einstein's spacetime share?",
    "",
    "The humble equation  a\u00b2 + b\u00b2 = c\u00b2  conceals",
    "a universe of structure: infinite trees, Lorentz",
    "symmetries, doubling algebras, and a surprising",
    "connection to integer factoring.",
    "",
    "From ancient geometry to quantum computing,",
    "this book reveals the hidden architecture",
    "of the world's most famous equation---with",
    "every theorem formally verified in Lean 4.",
]

y_pos = back_cy - 350
for line in blurb:
    if line == "":
        y_pos += 12
        continue
    bbox = draw.textbbox((0, 0), line, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text((back_left + (back_w - tw) // 2, y_pos), 
              line, font=font_small, fill=(190, 200, 220))
    y_pos += 26

# ISBN barcode
isbn_path = '/workspace/request-project/ISBN/978-1-105-41110-6.png'
if os.path.exists(isbn_path):
    isbn_img = Image.open(isbn_path).convert('RGB')
    target_w = int(2.0 * DPI)
    ratio = target_w / isbn_img.width
    target_h = int(isbn_img.height * ratio)
    isbn_img = isbn_img.resize((target_w, target_h), Image.LANCZOS)
    
    # White background
    bg = Image.new('RGB', (target_w + 40, target_h + 40), (255, 255, 255))
    bg.paste(isbn_img, (20, 20))
    
    paste_x = back_cx - (target_w + 40) // 2
    paste_y = int((WRAP + BLEED + TRIM_H - 1.8) * DPI)
    img.paste(bg, (paste_x, paste_y))
    
    isbn_label = "ISBN 978-1-105-41110-6"
    bbox = draw.textbbox((0, 0), isbn_label, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text((back_cx - tw // 2, paste_y + target_h + 48), 
              isbn_label, font=font_small, fill=(180, 180, 200))

print("Text done")

# --- FINAL SAVE ---
output = '/workspace/request-project/book/casewrap_cover.png'
img.save(output, 'PNG', dpi=(DPI, DPI))
print(f"\nSaved: {output}")
print(f"Size: {img.width}x{img.height} px, {os.path.getsize(output) / 1024 / 1024:.1f} MB")
