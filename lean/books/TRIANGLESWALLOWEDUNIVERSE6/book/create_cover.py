#!/usr/bin/env python3
"""
Create a trippy, psychedelic casewrap cover image for the book.
Includes front cover, spine, and back cover with ISBN barcode.

Standard 8x10 book casewrap:
- Front cover: 8" x 10"
- Spine: ~1.2" (for ~480 pages at 0.0025" per page)
- Back cover: 8" x 10"
- Bleed: 0.125" on all outer edges
- Total: (8 + 1.2 + 8 + 0.25) x (10 + 0.25) = 17.45" x 10.25"
At 300 DPI: 5235 x 3075 pixels
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random
import colorsys
import os

# Dimensions
DPI = 300
BLEED = 0.125  # inches
SPINE_WIDTH = 1.2  # inches (for ~480 pages)
COVER_W = 8.0  # inches
COVER_H = 10.0  # inches

TOTAL_W = int((COVER_W + SPINE_WIDTH + COVER_W + 2 * BLEED) * DPI)
TOTAL_H = int((COVER_H + 2 * BLEED) * DPI)

# Key positions (in pixels)
BLEED_PX = int(BLEED * DPI)
COVER_W_PX = int(COVER_W * DPI)
SPINE_W_PX = int(SPINE_WIDTH * DPI)

# Back cover: from BLEED_PX to BLEED_PX + COVER_W_PX
BACK_LEFT = BLEED_PX
BACK_RIGHT = BLEED_PX + COVER_W_PX

# Spine: from BACK_RIGHT to BACK_RIGHT + SPINE_W_PX
SPINE_LEFT = BACK_RIGHT
SPINE_RIGHT = BACK_RIGHT + SPINE_W_PX

# Front cover: from SPINE_RIGHT to SPINE_RIGHT + COVER_W_PX
FRONT_LEFT = SPINE_RIGHT
FRONT_RIGHT = SPINE_RIGHT + COVER_W_PX


def create_psychedelic_background(width, height):
    """Create a trippy, psychedelic background with swirling colors."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    random.seed(42)  # Reproducible
    
    # Generate color centers
    centers = []
    for _ in range(12):
        cx = random.uniform(0, width)
        cy = random.uniform(0, height)
        hue = random.uniform(0, 1)
        freq = random.uniform(0.003, 0.008)
        phase = random.uniform(0, 2 * math.pi)
        centers.append((cx, cy, hue, freq, phase))
    
    for y in range(height):
        for x in range(width):
            # Combine multiple wave patterns
            h = 0
            s = 0.85
            v = 0.9
            
            total = 0
            for cx, cy, base_hue, freq, phase in centers:
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                wave = math.sin(dist * freq + phase)
                total += wave * base_hue
            
            # Swirl effect
            angle = math.atan2(y - height/2, x - width/2)
            dist_center = math.sqrt((x - width/2)**2 + (y - height/2)**2)
            swirl = math.sin(angle * 3 + dist_center * 0.005) * 0.3
            
            h = (total * 0.15 + swirl + x * 0.0003 + y * 0.0002) % 1.0
            
            # Mandala-like pattern
            mandala = math.sin(dist_center * 0.01) * math.cos(angle * 5) * 0.15
            h = (h + mandala) % 1.0
            
            # Vary saturation and brightness for depth
            v = 0.7 + 0.3 * math.sin(dist_center * 0.008 + angle * 2)
            s = 0.6 + 0.4 * math.cos(dist_center * 0.006 - angle)
            
            r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255))
    
    return img


def draw_triangle_pattern(draw, cx, cy, size, color, depth=3):
    """Draw a recursive triangle pattern (Sierpinski-like)."""
    if depth == 0 or size < 5:
        return
    
    h = size * math.sqrt(3) / 2
    points = [
        (cx, cy - h * 2/3),
        (cx - size/2, cy + h * 1/3),
        (cx + size/2, cy + h * 1/3),
    ]
    draw.polygon(points, outline=color, width=2)
    
    # Recursion on three sub-triangles
    new_size = size / 2
    new_h = new_size * math.sqrt(3) / 2
    draw_triangle_pattern(draw, cx, cy - h/3, new_size, color, depth-1)
    draw_triangle_pattern(draw, cx - size/4, cy + h/6, new_size, color, depth-1)
    draw_triangle_pattern(draw, cx + size/4, cy + h/6, new_size, color, depth-1)


def add_text_with_glow(draw, position, text, font, main_color, glow_color, glow_radius=3):
    """Add text with a glow effect."""
    x, y = position
    # Draw glow
    for dx in range(-glow_radius, glow_radius+1):
        for dy in range(-glow_radius, glow_radius+1):
            if dx*dx + dy*dy <= glow_radius*glow_radius:
                alpha = int(120 * (1 - math.sqrt(dx*dx + dy*dy) / glow_radius))
                draw.text((x+dx, y+dy), text, font=font, fill=glow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=main_color)


def main():
    print(f"Creating cover: {TOTAL_W}x{TOTAL_H} pixels")
    
    # Create psychedelic background
    print("Generating psychedelic background...")
    img = create_psychedelic_background(TOTAL_W, TOTAL_H)
    draw = ImageDraw.Draw(img)
    
    # Add geometric triangle patterns
    print("Adding geometric patterns...")
    
    # Front cover triangles
    front_cx = FRONT_LEFT + COVER_W_PX // 2
    front_cy = TOTAL_H // 2
    
    # Draw concentric triangles
    for i in range(8):
        size = 400 + i * 180
        hue = (i * 0.12) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
        color = (int(r*255), int(g*255), int(b*255))
        h = size * math.sqrt(3) / 2
        angle_offset = i * 0.15
        points = []
        for k in range(3):
            a = angle_offset + k * 2 * math.pi / 3 - math.pi / 2
            px = front_cx + size * math.cos(a)
            py = front_cy + size * math.sin(a)
            points.append((px, py))
        draw.polygon(points, outline=color, width=3)
    
    # Sierpinski triangle on front
    for depth in range(1, 5):
        hue = 0.15 * depth
        r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 0.5, 1.0)
        color = (int(r*255), int(g*255), int(b*255))
        draw_triangle_pattern(draw, front_cx, front_cy, 600, color, depth)
    
    # Sacred geometry circles
    for i in range(6):
        angle = i * math.pi / 3
        cx = front_cx + 500 * math.cos(angle)
        cy = front_cy + 500 * math.sin(angle)
        for r in range(3):
            radius = 80 + r * 40
            hue = (i * 0.1 + r * 0.05) % 1.0
            rv, gv, bv = colorsys.hsv_to_rgb(hue, 0.6, 0.9)
            color = (int(rv*255), int(gv*255), int(bv*255))
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], 
                        outline=color, width=2)
    
    # Add light rays emanating from center
    for i in range(36):
        angle = i * math.pi / 18
        hue = (i * 0.028) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.4, 1.0)
        color = (int(r*255), int(g*255), int(b*255), 80)
        x1 = front_cx + 200 * math.cos(angle)
        y1 = front_cy + 200 * math.sin(angle)
        x2 = front_cx + 1200 * math.cos(angle)
        y2 = front_cy + 1200 * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=(int(r*255), int(g*255), int(b*255)), width=1)
    
    # === FRONT COVER TEXT ===
    print("Adding front cover text...")
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 120)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 48)
        author_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 60)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36)
        spine_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 48)
        spine_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36)
        isbn_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = title_font
        author_font = title_font
        small_font = title_font
        spine_font = title_font
        spine_author = title_font
        isbn_font = title_font
    
    # Title - centered on front cover
    title_lines = ["THE TRIANGLE", "THAT SWALLOWED", "THE UNIVERSE"]
    title_y = int(0.12 * TOTAL_H)
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = front_cx - tw // 2
        add_text_with_glow(draw, (tx, title_y), line, title_font,
                          (255, 255, 255), (100, 50, 150), glow_radius=4)
        title_y += 140
    
    # Subtitle
    subtitle_lines = [
        "How Pythagorean Triples Connect",
        "Number Theory, the Lorentz Group,",
        "and the Art of Breaking Numbers Apart"
    ]
    sub_y = TOTAL_H - int(0.32 * TOTAL_H)
    for line in subtitle_lines:
        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        tw = bbox[2] - bbox[0]
        tx = front_cx - tw // 2
        draw.text((tx, sub_y), line, font=subtitle_font, fill=(255, 240, 200))
        sub_y += 60
    
    # Author
    author_text = "PAUL KLEMSTINE"
    bbox = draw.textbbox((0, 0), author_text, font=author_font)
    tw = bbox[2] - bbox[0]
    tx = front_cx - tw // 2
    author_y = TOTAL_H - int(0.12 * TOTAL_H)
    add_text_with_glow(draw, (tx, author_y), author_text, author_font,
                      (255, 255, 255), (80, 40, 120), glow_radius=3)
    
    # Lean 4 badge
    badge_text = "With Machine-Verified Proofs in Lean 4"
    bbox = draw.textbbox((0, 0), badge_text, font=small_font)
    tw = bbox[2] - bbox[0]
    tx = front_cx - tw // 2
    draw.text((tx, author_y + 80), badge_text, font=small_font, fill=(200, 220, 255))
    
    # === SPINE ===
    print("Adding spine text...")
    # Spine text (rotated)
    spine_text_img = Image.new('RGBA', (TOTAL_H, SPINE_W_PX), (0, 0, 0, 0))
    spine_draw = ImageDraw.Draw(spine_text_img)
    
    spine_title = "THE TRIANGLE THAT SWALLOWED THE UNIVERSE"
    bbox = spine_draw.textbbox((0, 0), spine_title, font=spine_font)
    tw = bbox[2] - bbox[0]
    tx = TOTAL_H // 2 - tw // 2
    ty = SPINE_W_PX // 2 - 40
    spine_draw.text((tx, ty - 20), spine_title, font=spine_font, fill=(255, 255, 255))
    
    spine_auth = "Paul Klemstine"
    bbox = spine_draw.textbbox((0, 0), spine_auth, font=spine_author)
    tw = bbox[2] - bbox[0]
    tx = TOTAL_H // 2 - tw // 2
    spine_draw.text((tx, ty + 50), spine_auth, font=spine_author, fill=(220, 220, 255))
    
    # Rotate spine text
    spine_rotated = spine_text_img.rotate(90, expand=True)
    # Paste onto main image
    img.paste(spine_rotated, (SPINE_LEFT, 0), spine_rotated)
    
    # === BACK COVER ===
    print("Adding back cover...")
    back_cx = BACK_LEFT + COVER_W_PX // 2
    
    # Semi-transparent overlay for readability
    overlay = Image.new('RGBA', (COVER_W_PX - 200, int(TOTAL_H * 0.5)), (0, 0, 0, 140))
    img_rgba = img.convert('RGBA')
    img_rgba.paste(overlay, (BACK_LEFT + 100, int(TOTAL_H * 0.15)), overlay)
    img = img_rgba.convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Back cover blurb
    blurb_lines = [
        "A single equation—a² + b² = c²—connects",
        "ancient rope-stretchers to Einstein's spacetime,",
        "Berggren's infinite tree to quantum algorithms,",
        "and the humblest right triangle to the deepest",
        "structures in mathematics.",
        "",
        "This book reveals how Pythagorean triples form",
        "a ternary tree rooted at (3, 4, 5), how that tree",
        "hides inside the integer Lorentz group, and how",
        "it opens unexpected pathways to factoring large",
        "numbers—with machine-verified Lean 4 proofs.",
    ]
    
    blurb_y = int(TOTAL_H * 0.18)
    for line in blurb_lines:
        if line == "":
            blurb_y += 20
            continue
        bbox = draw.textbbox((0, 0), line, font=small_font)
        tw = bbox[2] - bbox[0]
        tx = back_cx - tw // 2
        draw.text((tx, blurb_y), line, font=small_font, fill=(240, 240, 240))
        blurb_y += 45
    
    # Equation centerpiece on back
    eq_text = "a² + b² = c²"
    try:
        eq_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 72)
    except:
        eq_font = title_font
    bbox = draw.textbbox((0, 0), eq_text, font=eq_font)
    tw = bbox[2] - bbox[0]
    eq_y = blurb_y + 40
    tx = back_cx - tw // 2
    add_text_with_glow(draw, (tx, eq_y), eq_text, eq_font,
                      (255, 220, 100), (150, 100, 0), glow_radius=4)
    
    # ISBN barcode on back cover
    isbn_barcode_path = '/workspace/request-project/ISBN/978-1-105-41110-6.png'
    if os.path.exists(isbn_barcode_path):
        barcode = Image.open(isbn_barcode_path)
        # Scale barcode to fit
        bc_width = int(COVER_W_PX * 0.4)
        bc_height = int(bc_width * barcode.height / barcode.width)
        barcode = barcode.resize((bc_width, bc_height), Image.LANCZOS)
        
        # White background behind barcode
        bc_bg = Image.new('RGB', (bc_width + 40, bc_height + 60), (255, 255, 255))
        bc_bg.paste(barcode, (20, 20))
        
        bc_x = back_cx - (bc_width + 40) // 2
        bc_y = TOTAL_H - bc_height - 200
        img.paste(bc_bg, (bc_x, bc_y))
        
        # ISBN text below barcode
        isbn_text = "ISBN 978-1-105-41110-6"
        bbox = draw.textbbox((0, 0), isbn_text, font=isbn_font)
        tw = bbox[2] - bbox[0]
        tx = back_cx - tw // 2
        draw.text((tx, bc_y + bc_height + 70), isbn_text, font=isbn_font, fill=(255, 255, 255))
    
    # Add decorative triangles on back cover too
    for i in range(5):
        angle = i * 2 * math.pi / 5 + math.pi/10
        cx = back_cx + 700 * math.cos(angle)
        cy = TOTAL_H // 2 + 700 * math.sin(angle)
        size = 120
        h = size * math.sqrt(3) / 2
        points = [
            (cx, cy - h * 2/3),
            (cx - size/2, cy + h * 1/3),
            (cx + size/2, cy + h * 1/3),
        ]
        hue = (i * 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.9)
        draw.polygon(points, outline=(int(r*255), int(g*255), int(b*255)), width=2)
    
    # Save
    out_path = '/workspace/request-project/book/casewrap_cover.png'
    img.save(out_path, 'PNG', dpi=(DPI, DPI))
    print(f"Saved cover to {out_path}")
    print(f"Size: {TOTAL_W}x{TOTAL_H} pixels at {DPI} DPI")


if __name__ == '__main__':
    main()
