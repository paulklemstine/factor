#!/usr/bin/env python3
"""Generate a trippy, psychedelic casewrap cover for the book.
Full casewrap = back cover + spine + front cover, all in one PNG.
Standard 6x9 trim, ~500 page book.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

# --- Dimensions (300 DPI) ---
DPI = 300
TRIM_W = int(6 * DPI)      # 1800 px
TRIM_H = int(9 * DPI)      # 2700 px
SPINE_W = int(1.1 * DPI)   # ~330 px for ~500 pages
BLEED = int(0.125 * DPI)   # 37 px bleed on each edge
WRAP = int(0.75 * DPI)     # 225 px wrap-around

TOTAL_W = 2 * TRIM_W + SPINE_W + 2 * BLEED
TOTAL_H = TRIM_H + 2 * BLEED

# Back cover occupies: [BLEED, BLEED + TRIM_W]
# Spine: [BLEED + TRIM_W, BLEED + TRIM_W + SPINE_W]
# Front cover: [BLEED + TRIM_W + SPINE_W, BLEED + 2*TRIM_W + SPINE_W]

BACK_L = BLEED
BACK_R = BLEED + TRIM_W
SPINE_L = BACK_R
SPINE_R = SPINE_L + SPINE_W
FRONT_L = SPINE_R
FRONT_R = FRONT_L + TRIM_W

def psychedelic_background(w, h):
    """Generate a trippy, psychedelic background using interference patterns."""
    img = np.zeros((h, w, 3), dtype=np.float64)
    # Create coordinate grids
    y, x = np.mgrid[0:h, 0:w].astype(np.float64)
    cx, cy = w / 2, h / 2
    
    # Normalize
    xn = (x - cx) / w
    yn = (y - cy) / h
    
    # Polar coords
    r = np.sqrt(xn**2 + yn**2)
    theta = np.arctan2(yn, xn)
    
    # Layer 1: Spiral interference (deep purple to electric blue)
    wave1 = np.sin(r * 40 + theta * 5) * 0.5 + 0.5
    # Layer 2: Concentric rings (gold to magenta)
    wave2 = np.sin(r * 25 - theta * 3) * 0.5 + 0.5
    # Layer 3: Diagonal waves (teal to orange)
    wave3 = np.sin(xn * 30 + yn * 20) * 0.5 + 0.5
    # Layer 4: Mandala-like pattern
    wave4 = np.sin(theta * 8 + r * 15) * 0.5 + 0.5
    # Layer 5: Pythagorean triple inspired: a²+b²=c² contours
    wave5 = np.sin(xn**2 * 50 + yn**2 * 50) * 0.5 + 0.5
    
    # Color mixing - rich psychedelic palette
    # Deep indigo/violet base
    img[:,:,0] = 0.15 + 0.35 * wave1 + 0.25 * wave4 + 0.15 * wave5  # R
    img[:,:,1] = 0.05 + 0.15 * wave2 + 0.30 * wave3 + 0.10 * wave5  # G  
    img[:,:,2] = 0.30 + 0.30 * wave1 + 0.20 * wave2 + 0.15 * wave4  # B
    
    # Add golden highlights
    gold_mask = wave5 * wave4
    img[:,:,0] += 0.25 * gold_mask
    img[:,:,1] += 0.18 * gold_mask
    img[:,:,2] -= 0.05 * gold_mask
    
    # Electric neon accents
    neon = np.sin(r * 60) * np.sin(theta * 12)
    neon = np.clip(neon, 0, 1) * 0.3
    img[:,:,0] += neon * 0.8  # hot pink
    img[:,:,1] += neon * 0.1
    img[:,:,2] += neon * 0.5
    
    # Fractal-like triangle patterns
    tri_pattern = np.sin(np.abs(xn + yn) * 40) * np.sin(np.abs(xn - yn) * 40)
    tri_pattern = np.clip(tri_pattern, 0, 1) * 0.15
    img[:,:,0] += tri_pattern * 1.0
    img[:,:,1] += tri_pattern * 0.7
    img[:,:,2] += tri_pattern * 0.2
    
    img = np.clip(img, 0, 1)
    return (img * 255).astype(np.uint8)

def draw_pythagorean_triangles(draw, cx, cy, scale, color, alpha_img):
    """Draw recursive Pythagorean tree triangles."""
    triangles = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (20, 21, 29), (9, 40, 41), (12, 35, 37), (11, 60, 61),
    ]
    for i, (a, b, c) in enumerate(triangles):
        angle = i * math.pi / 4
        r = scale * (0.3 + 0.1 * i)
        ox = cx + r * math.cos(angle)
        oy = cy + r * math.sin(angle)
        s = scale * 0.08
        pts = [
            (ox, oy),
            (ox + a * s / c, oy + b * s / c),
            (ox + a * s / c, oy),
        ]
        draw.polygon(pts, outline=color, width=2)

def add_text(img, draw):
    """Add title, author, spine text."""
    # Try to find a nice font
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break
    
    font_path_italic = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
    if not os.path.exists(font_path_italic):
        font_path_italic = font_path
    
    # Front cover text
    front_cx = FRONT_L + TRIM_W // 2
    
    # Title - large
    title_font = ImageFont.truetype(font_path, 100) if font_path else ImageFont.load_default()
    subtitle_font = ImageFont.truetype(font_path, 50) if font_path else ImageFont.load_default()
    author_font = ImageFont.truetype(font_path, 55) if font_path else ImageFont.load_default()
    small_font = ImageFont.truetype(font_path_italic, 36) if font_path else ImageFont.load_default()
    
    # Semi-transparent overlay box for readability on front cover
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Dark semi-transparent panel behind title area on front cover
    overlay_draw.rounded_rectangle(
        [FRONT_L + 100, 300, FRONT_R - 100, 1500],
        radius=40, fill=(10, 5, 30, 160)
    )
    # Dark panel behind author
    overlay_draw.rounded_rectangle(
        [FRONT_L + 200, TRIM_H - 500, FRONT_R - 200, TRIM_H - 200],
        radius=30, fill=(10, 5, 30, 160)
    )
    
    # Spine overlay
    overlay_draw.rectangle(
        [SPINE_L, 0, SPINE_R, TOTAL_H],
        fill=(10, 5, 30, 180)
    )
    
    # Back cover overlay for text areas
    overlay_draw.rounded_rectangle(
        [BACK_L + 100, TRIM_H - 700, BACK_R - 100, TRIM_H - 100],
        radius=30, fill=(10, 5, 30, 180)
    )
    
    img_rgba = img.convert('RGBA')
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    draw = ImageDraw.Draw(img_rgba)
    
    # === FRONT COVER ===
    # Title
    title_lines = ["The Triangle", "That Swallowed", "the Universe"]
    y_start = 450
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = front_cx - tw // 2
        # Gold text with glow effect
        # Glow
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((x + dx, y_start + i * 130 + dy), line, font=title_font, fill=(255, 200, 50, 80))
        draw.text((x, y_start + i * 130), line, font=title_font, fill=(255, 220, 100, 255))
    
    # Subtitle
    subtitle = "Pythagorean Triples, Lorentz Symmetry,"
    subtitle2 = "and the Hidden Geometry of Numbers"
    for j, st in enumerate([subtitle, subtitle2]):
        bbox = draw.textbbox((0, 0), st, font=subtitle_font)
        tw = bbox[2] - bbox[0]
        x = front_cx - tw // 2
        draw.text((x, 900 + j * 65), st, font=subtitle_font, fill=(200, 180, 255, 230))
    
    # a² + b² = c² equation prominently
    eq_font = ImageFont.truetype(font_path_italic, 70) if font_path else ImageFont.load_default()
    eq = "a² + b² = c²"
    bbox = draw.textbbox((0, 0), eq, font=eq_font)
    tw = bbox[2] - bbox[0]
    draw.text((front_cx - tw // 2, 1150), eq, font=eq_font, fill=(255, 180, 80, 240))
    
    # Author
    author = "Paul Klemstine"
    bbox = draw.textbbox((0, 0), author, font=author_font)
    tw = bbox[2] - bbox[0]
    draw.text((front_cx - tw // 2, TRIM_H - 420), author, font=author_font, fill=(255, 255, 255, 240))
    
    # === SPINE ===
    # Spine text (rotated)
    spine_cx = SPINE_L + SPINE_W // 2
    spine_font = ImageFont.truetype(font_path, 36) if font_path else ImageFont.load_default()
    spine_author_font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    
    # Title on spine (rotated 90° CCW - reads bottom to top)
    spine_title = "The Triangle That Swallowed the Universe"
    title_img = Image.new('RGBA', (1800, 60), (0, 0, 0, 0))
    title_draw = ImageDraw.Draw(title_img)
    title_draw.text((10, 5), spine_title, font=spine_font, fill=(255, 220, 100, 255))
    title_img = title_img.rotate(90, expand=True)
    # Center on spine
    img_rgba.paste(title_img, (spine_cx - 30, TOTAL_H // 2 - 900), title_img)
    
    # Author on spine
    spine_author = "Klemstine"
    auth_img = Image.new('RGBA', (500, 50), (0, 0, 0, 0))
    auth_draw = ImageDraw.Draw(auth_img)
    auth_draw.text((10, 5), spine_author, font=spine_author_font, fill=(200, 200, 255, 230))
    auth_img = auth_img.rotate(90, expand=True)
    img_rgba.paste(auth_img, (spine_cx - 25, TOTAL_H - 600), auth_img)
    
    draw = ImageDraw.Draw(img_rgba)
    
    # === BACK COVER ===
    back_cx = BACK_L + TRIM_W // 2
    
    # Back cover blurb
    blurb_font = ImageFont.truetype(font_path_italic, 32) if font_path else ImageFont.load_default()
    blurb_lines = [
        "From a rope stretched on the Nile to",
        "Einstein's spacetime, one equation",
        "connects them all: a² + b² = c².",
        "",
        "Discover the infinite tree of right triangles,",
        "the hidden Lorentz symmetry of number theory,",
        "and the deep geometry of factoring.",
    ]
    y_blurb = TRIM_H - 650
    for line in blurb_lines:
        if line:
            bbox = draw.textbbox((0, 0), line, font=blurb_font)
            tw = bbox[2] - bbox[0]
            draw.text((back_cx - tw // 2, y_blurb), line, font=blurb_font, fill=(220, 210, 240, 220))
        y_blurb += 42
    
    # ISBN barcode on back cover
    try:
        isbn_img = Image.open("/workspace/request-project/ISBN/978-1-105-41110-6.png").convert("RGBA")
        # Scale barcode to fit nicely
        isbn_w = 500
        ratio = isbn_w / isbn_img.width
        isbn_h = int(isbn_img.height * ratio)
        isbn_img = isbn_img.resize((isbn_w, isbn_h), Image.LANCZOS)
        
        # White background behind barcode
        barcode_bg = Image.new('RGBA', (isbn_w + 40, isbn_h + 40), (255, 255, 255, 240))
        barcode_bg.paste(isbn_img, (20, 20), isbn_img if isbn_img.mode == 'RGBA' else None)
        
        # Place on back cover, bottom right area
        bx = BACK_L + TRIM_W - isbn_w - 200
        by = TRIM_H - isbn_h - 200
        img_rgba.paste(barcode_bg, (bx, by), barcode_bg)
    except Exception as e:
        print(f"Warning: Could not place ISBN barcode: {e}")
    
    return img_rgba.convert('RGB')

# Generate
print("Generating psychedelic background...")
bg = psychedelic_background(TOTAL_W, TOTAL_H)
img = Image.fromarray(bg)

# Apply some post-processing for extra trippiness
# Slight blur for smoother gradients
img_smooth = img.filter(ImageFilter.GaussianBlur(radius=2))
# Blend sharp and smooth
img = Image.blend(img, img_smooth, 0.3)

# Draw decorative elements
draw = ImageDraw.Draw(img)

# Draw some geometric Pythagorean-inspired patterns
front_cx = FRONT_L + TRIM_W // 2
# Decorative triangles scattered on front cover
for i in range(12):
    angle = i * math.pi / 6
    r = 600 + 100 * (i % 3)
    cx = front_cx + r * math.cos(angle)
    cy = TRIM_H // 2 + r * math.sin(angle)
    s = 30 + 10 * (i % 4)
    pts = [
        (cx, cy - s),
        (cx - s * 0.866, cy + s * 0.5),
        (cx + s * 0.866, cy + s * 0.5),
    ]
    color = (
        int(200 + 55 * math.sin(i)),
        int(150 + 100 * math.sin(i + 2)),
        int(200 + 55 * math.cos(i)),
    )
    draw.polygon(pts, outline=color, width=3)

# Add text and ISBN
print("Adding text and ISBN...")
final = add_text(img, draw)

# Save
output_path = "/workspace/request-project/casewrap_cover.png"
final.save(output_path, dpi=(300, 300))
print(f"Saved casewrap to {output_path}")
print(f"Dimensions: {final.size[0]}x{final.size[1]} px ({final.size[0]/300:.2f}x{final.size[1]/300:.2f} inches)")
