#!/usr/bin/env python3
"""
Generate a psychedelic, trippy casewrap cover for
'The Triangle That Swallowed the Universe' by Paul Klemstine.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

# ── Dimensions ─────────────────────────────────────────────
DPI = 300
TRIM_W = 6.125   # inches
TRIM_H = 9.25
SPINE_W = 1.065  # 426 pages
BLEED = 0.125

TOTAL_W = TRIM_W * 2 + SPINE_W + 2 * BLEED  # ~13.565 in
TOTAL_H = TRIM_H + 2 * BLEED                 # 9.5 in

PX_W = int(TOTAL_W * DPI)  # 4069
PX_H = int(TOTAL_H * DPI)  # 2850

# Zone boundaries (in pixels from left)
BLEED_PX = int(BLEED * DPI)
BACK_W = int(TRIM_W * DPI)
SPINE_PX = int(SPINE_W * DPI)
FRONT_W = int(TRIM_W * DPI)

BACK_START = BLEED_PX
BACK_END = BLEED_PX + BACK_W
SPINE_START = BACK_END
SPINE_END = SPINE_START + SPINE_PX
FRONT_START = SPINE_END
FRONT_END = FRONT_START + FRONT_W

random.seed(42)


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB (h in [0,360], s,v in [0,1])."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def generate_psychedelic_background(img, draw):
    """Create a trippy, swirling psychedelic background."""
    cx, cy = PX_W // 2, PX_H // 2
    
    pixels = img.load()
    
    for y in range(PX_H):
        for x in range(PX_W):
            # Normalized coordinates
            nx = (x - cx) / (PX_W * 0.5)
            ny = (y - cy) / (PX_H * 0.5)
            
            # Distance and angle from center
            dist = math.sqrt(nx * nx + ny * ny)
            angle = math.atan2(ny, nx)
            
            # Psychedelic spiral pattern
            spiral = angle * 3 + dist * 8
            wave1 = math.sin(spiral) * 0.5 + 0.5
            wave2 = math.sin(dist * 12 - angle * 5) * 0.5 + 0.5
            wave3 = math.sin(nx * 6 + ny * 4) * 0.5 + 0.5
            
            # Hue cycling with multiple frequencies
            hue = (spiral * 30 + wave2 * 60 + wave3 * 40) % 360
            
            # Deep rich colors - dark purples, magentas, deep blues, teals
            # Shift the palette toward jewel tones
            hue = (hue + 240) % 360  # Start from blue/purple range
            
            sat = 0.7 + 0.3 * wave1
            val = 0.15 + 0.35 * wave2 * wave3 + 0.1 * wave1
            
            # Darken edges for vignette
            edge_fade = max(0, 1 - dist * 0.6)
            val *= (0.5 + 0.5 * edge_fade)
            
            pixels[x, y] = hsv_to_rgb(hue, sat, min(1.0, val))
    
    return img


def draw_pythagorean_tree_fractal(draw, x, y, size, angle, depth, alpha_base=180):
    """Draw a fractal Pythagorean tree pattern."""
    if depth <= 0 or size < 3:
        return
    
    # Compute square corners
    dx = size * math.cos(angle)
    dy = size * math.sin(angle)
    
    # Four corners of the square
    px = [-dy, dx - dy, dx, 0]
    py = [dx, dx + dy, dy, 0]
    
    corners = [(int(x + px[i]), int(y + py[i])) for i in range(4)]
    
    # Color based on depth
    hue = (depth * 45 + 180) % 360
    alpha = max(30, alpha_base - depth * 20)
    color = hsv_to_rgb(hue, 0.8, 0.7)
    color_with_alpha = (*color, alpha)
    
    draw.polygon(corners, outline=color_with_alpha)
    
    # Branch left
    new_size_l = size * 0.65
    new_angle_l = angle + 0.5
    nx_l = x + px[1]
    ny_l = y + py[1]
    draw_pythagorean_tree_fractal(draw, nx_l, ny_l, new_size_l, new_angle_l, depth - 1, alpha)
    
    # Branch right
    new_size_r = size * 0.75
    new_angle_r = angle - 0.35
    nx_r = x + px[1] + new_size_l * math.cos(new_angle_l) * 0.8
    ny_r = y + py[1] + new_size_l * math.sin(new_angle_l) * 0.8
    draw_pythagorean_tree_fractal(draw, nx_r, ny_r, new_size_r, new_angle_r, depth - 1, alpha)


def draw_triangles_pattern(draw, overlay):
    """Draw scattered Pythagorean triangles across the cover."""
    overlay_draw = ImageDraw.Draw(overlay)
    
    triangles = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (20, 21, 29), (9, 40, 41), (12, 35, 37), (11, 60, 61),
    ]
    
    for i in range(60):
        x = random.randint(0, PX_W)
        y = random.randint(0, PX_H)
        scale = random.uniform(3, 15)
        angle = random.uniform(0, 2 * math.pi)
        
        a, b, c = random.choice(triangles)
        
        # Triangle vertices
        p1 = (x, y)
        p2 = (int(x + a * scale * math.cos(angle)), int(y + a * scale * math.sin(angle)))
        p3 = (int(x + b * scale * math.cos(angle + math.pi/2)), int(y + b * scale * math.sin(angle + math.pi/2)))
        
        hue = random.randint(0, 360)
        alpha = random.randint(15, 50)
        color = hsv_to_rgb(hue, 0.9, 0.8)
        
        overlay_draw.polygon([p1, p2, p3], outline=(*color, alpha + 30), fill=(*color, alpha))


def draw_concentric_spirals(overlay):
    """Draw mathematical spirals."""
    draw = ImageDraw.Draw(overlay)
    
    # Golden spiral on front cover center
    cx = FRONT_START + FRONT_W // 2
    cy = PX_H // 2
    
    for t_i in range(2000):
        t = t_i * 0.02
        r = 3 * math.exp(0.15 * t)
        if r > 800:
            break
        x = int(cx + r * math.cos(t))
        y = int(cy + r * math.sin(t))
        
        hue = (t * 25 + 300) % 360
        color = hsv_to_rgb(hue, 0.7, 0.9)
        alpha = max(20, 120 - int(t * 3))
        
        size = max(1, int(2 + t * 0.1))
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(*color, alpha))


def draw_light_cones(overlay):
    """Draw light cone patterns (Minkowski-style)."""
    draw = ImageDraw.Draw(overlay)
    
    # Several light cone sources
    sources = [
        (FRONT_START + FRONT_W // 2, PX_H // 2 - 200),
        (BACK_START + BACK_W // 2, PX_H // 2),
        (SPINE_START + SPINE_PX // 2, PX_H // 3),
    ]
    
    for cx, cy in sources:
        for angle_deg in range(0, 360, 3):
            angle = math.radians(angle_deg)
            for r in range(50, 600, 8):
                x = int(cx + r * math.cos(angle))
                y = int(cy + r * math.sin(angle) * 0.6)
                
                if 0 <= x < PX_W and 0 <= y < PX_H:
                    hue = (angle_deg + r * 0.3 + 200) % 360
                    alpha = max(5, 40 - r // 20)
                    color = hsv_to_rgb(hue, 0.8, 0.7)
                    draw.point((x, y), fill=(*color, alpha))


def add_text(img):
    """Add title, author, spine text, and ISBN to the cover."""
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 72)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 32)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 40)
        font_spine = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 34)
        font_spine_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 28)
        font_back_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_author = font_title
        font_spine = font_title
        font_spine_author = font_title
        font_back_text = font_title
        font_small = font_title
    
    # ── FRONT COVER ────────────────────────────────────────
    front_cx = FRONT_START + FRONT_W // 2
    
    # Title - multi-line
    title_y = PX_H // 6
    
    # Draw title with glow effect
    title_lines = ["THE TRIANGLE", "THAT SWALLOWED", "THE UNIVERSE"]
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        tx = front_cx - tw // 2
        ty = title_y + i * 90
        
        # Glow
        for offset in range(5, 0, -1):
            glow_alpha = 60 - offset * 10
            glow_color = (255, 200, 100, max(10, glow_alpha))
            draw.text((tx - offset, ty), line, font=font_title, fill=glow_color)
            draw.text((tx + offset, ty), line, font=font_title, fill=glow_color)
            draw.text((tx, ty - offset), line, font=font_title, fill=glow_color)
            draw.text((tx, ty + offset), line, font=font_title, fill=glow_color)
        
        # Main text
        draw.text((tx, ty), line, font=font_title, fill=(255, 240, 220, 255))
    
    # Subtitle
    subtitle = "Pythagorean Triples, Lorentz Symmetry,"
    subtitle2 = "and the Hidden Architecture of Number Theory"
    
    for j, sub in enumerate([subtitle, subtitle2]):
        bbox = draw.textbbox((0, 0), sub, font=font_subtitle)
        tw = bbox[2] - bbox[0]
        tx = front_cx - tw // 2
        ty = title_y + 310 + j * 45
        draw.text((tx, ty), sub, font=font_subtitle, fill=(220, 200, 255, 230))
    
    # Author
    author = "PAUL KLEMSTINE"
    bbox = draw.textbbox((0, 0), author, font=font_author)
    tw = bbox[2] - bbox[0]
    tx = front_cx - tw // 2
    ty = PX_H - PX_H // 5
    draw.text((tx, ty), author, font=font_author, fill=(255, 240, 220, 255))
    
    # Draw a large decorative right triangle on front cover
    tri_cx = front_cx
    tri_cy = PX_H // 2 + 100
    tri_scale = 180
    
    # 3-4-5 triangle
    p1 = (tri_cx - 3 * tri_scale // 2, tri_cy + 4 * tri_scale // 2)
    p2 = (tri_cx + 3 * tri_scale // 2, tri_cy + 4 * tri_scale // 2)
    p3 = (tri_cx + 3 * tri_scale // 2, tri_cy - 4 * tri_scale // 2 + 200)
    
    # Glowing triangle
    for offset in range(8, 0, -1):
        alpha = 30 + (8 - offset) * 15
        color = (200, 150, 255, alpha)
        draw.polygon([p1, p2, p3], outline=color)
    
    # Right angle mark
    mark_size = 30
    draw.line([
        (p2[0] - mark_size, p2[1]),
        (p2[0] - mark_size, p2[1] - mark_size),
        (p2[0], p2[1] - mark_size)
    ], fill=(200, 150, 255, 150), width=2)
    
    # Labels
    draw.text((tri_cx - 30, p1[1] + 15), "a", font=font_subtitle, fill=(200, 220, 255, 200))
    draw.text((p2[0] + 15, tri_cy + 50), "b", font=font_subtitle, fill=(200, 220, 255, 200))
    draw.text((tri_cx - 100, tri_cy - 30), "c", font=font_subtitle, fill=(200, 220, 255, 200))
    
    # Equation
    eq = "a² + b² = c²"
    bbox = draw.textbbox((0, 0), eq, font=font_author)
    tw = bbox[2] - bbox[0]
    draw.text((front_cx - tw // 2, PX_H - PX_H // 3.5), eq, font=font_author, fill=(255, 220, 150, 230))
    
    # ── SPINE ──────────────────────────────────────────────
    spine_cx = SPINE_START + SPINE_PX // 2
    
    # Spine title (rotated - we'll draw it character by character vertically)
    spine_title = "THE TRIANGLE THAT SWALLOWED THE UNIVERSE"
    spine_author = "KLEMSTINE"
    
    # Create a rotated text image for spine
    # Title
    spine_text_img = Image.new('RGBA', (PX_H - 200, SPINE_PX - 40), (0, 0, 0, 0))
    spine_draw = ImageDraw.Draw(spine_text_img)
    
    bbox = spine_draw.textbbox((0, 0), spine_title, font=font_spine)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (PX_H - 200 - tw) // 2 - 200
    ty = (SPINE_PX - 40 - th) // 2
    spine_draw.text((tx, ty), spine_title, font=font_spine, fill=(255, 240, 220, 255))
    
    # Author on spine
    bbox2 = spine_draw.textbbox((0, 0), spine_author, font=font_spine_author)
    tw2 = bbox2[2] - bbox2[0]
    spine_draw.text((PX_H - 200 - tw2 - 50, ty + 3), spine_author, font=font_spine_author, fill=(220, 200, 240, 230))
    
    # Rotate 90 degrees clockwise (text reads top-to-bottom)
    spine_text_rot = spine_text_img.rotate(90, expand=True)
    
    # Paste onto main image
    paste_x = spine_cx - spine_text_rot.width // 2
    paste_y = 100
    img.paste(spine_text_rot, (paste_x, paste_y), spine_text_rot)
    
    # ── BACK COVER ─────────────────────────────────────────
    back_cx = BACK_START + BACK_W // 2
    
    # Back cover blurb
    blurb_lines = [
        "A 3-4-5 triangle. The oldest theorem in mathematics.",
        "But what if this humble shape conceals an infinite",
        "tree, a light cone from Einstein's spacetime,",
        "a factoring machine for breaking codes,",
        "and a ladder of algebras that climbs",
        "from the real numbers to the octonions?",
        "",
        "In this groundbreaking work, Paul Klemstine",
        "reveals the astonishing hidden architecture",
        "connecting Pythagorean triples to Lorentz symmetry,",
        "lattice reduction, quantum computing, tropical",
        "geometry, and Fermat's Last Theorem.",
        "",
        "From Plimpton 322 to the Berggren tree,",
        "from Euclid's algorithm to Shor's quantum circuit,",
        "the simplest equation in mathematics has never",
        "looked so deep — or so beautiful.",
    ]
    
    blurb_y = PX_H // 6
    for i, line in enumerate(blurb_lines):
        if line == "":
            blurb_y += 10
            continue
        bbox = draw.textbbox((0, 0), line, font=font_back_text)
        tw = bbox[2] - bbox[0]
        tx = back_cx - tw // 2
        draw.text((tx, blurb_y + i * 38), line, font=font_back_text, fill=(220, 210, 230, 230))
    
    # ISBN text
    isbn_text = "ISBN 978-1-105-41110-6"
    bbox = draw.textbbox((0, 0), isbn_text, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text((back_cx - tw // 2, PX_H - 550), isbn_text, font=font_small, fill=(200, 200, 210, 220))
    
    # ISBN barcode
    try:
        barcode = Image.open("/workspace/request-project/ISBN/978-1-105-41110-6.png")
        # Scale barcode to fit
        bc_w = 400
        bc_h = int(barcode.height * bc_w / barcode.width)
        barcode = barcode.resize((bc_w, bc_h), Image.LANCZOS)
        
        # Create white background for barcode
        bc_bg = Image.new('RGBA', (bc_w + 30, bc_h + 30), (255, 255, 255, 240))
        bc_bg.paste(barcode, (15, 15))
        
        bx = back_cx - bc_bg.width // 2
        by = PX_H - 500
        img.paste(bc_bg, (bx, by), bc_bg)
    except Exception as e:
        print(f"Warning: Could not load ISBN barcode: {e}")
    
    return img


def main():
    print("Generating psychedelic casewrap cover...")
    
    # Create base image with psychedelic background
    img = Image.new('RGB', (PX_W, PX_H), (10, 5, 20))
    draw = ImageDraw.Draw(img)
    
    print("  Generating psychedelic background...")
    img = generate_psychedelic_background(img, draw)
    
    # Convert to RGBA for overlays
    img = img.convert('RGBA')
    
    # Create overlay for translucent elements
    overlay = Image.new('RGBA', (PX_W, PX_H), (0, 0, 0, 0))
    
    print("  Adding triangle patterns...")
    draw_triangles_pattern(draw, overlay)
    img = Image.alpha_composite(img, overlay)
    
    overlay2 = Image.new('RGBA', (PX_W, PX_H), (0, 0, 0, 0))
    print("  Adding spiral patterns...")
    draw_concentric_spirals(overlay2)
    img = Image.alpha_composite(img, overlay2)
    
    overlay3 = Image.new('RGBA', (PX_W, PX_H), (0, 0, 0, 0))
    print("  Adding light cone patterns...")
    draw_light_cones(overlay3)
    img = Image.alpha_composite(img, overlay3)
    
    print("  Adding text and ISBN...")
    img = add_text(img)
    
    # Final composite
    final = img.convert('RGB')
    
    # Save
    output_path = "/workspace/request-project/book/casewrap_cover.png"
    final.save(output_path, 'PNG', dpi=(300, 300))
    print(f"Casewrap cover saved to {output_path}")
    print(f"Dimensions: {PX_W} x {PX_H} pixels ({TOTAL_W:.3f} x {TOTAL_H:.3f} inches at {DPI} DPI)")


if __name__ == "__main__":
    main()
