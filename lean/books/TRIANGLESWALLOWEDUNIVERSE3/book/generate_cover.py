#!/usr/bin/env python3
"""
Generate a psychedelic, trippy casewrap cover for
'The Triangle That Swallowed the Universe'.

Creates a high-resolution PNG suitable for a casewrap hardcover.
Standard casewrap: front + spine + back + bleed.
For a 7.5" x 9.25" book with ~580 pages (spine ~1.5"), at 300 DPI.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

# Dimensions
DPI = 300
FRONT_W = int(7.5 * DPI)   # 2250
FRONT_H = int(9.25 * DPI)  # 2775
SPINE_W = int(1.5 * DPI)   # 450
BLEED = int(0.125 * DPI)   # 38
WRAP = int(0.75 * DPI)     # 225 - wrap around edges

TOTAL_W = WRAP + BLEED + FRONT_W + BLEED + SPINE_W + BLEED + FRONT_W + BLEED + WRAP
TOTAL_H = WRAP + BLEED + FRONT_H + BLEED + WRAP

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB (h in [0,360], s,v in [0,1])."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:    r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else:         r, g, b = c, 0, x
    return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

def create_psychedelic_background(img):
    """Create a trippy, swirling psychedelic background."""
    w, h = img.size
    pixels = img.load()
    
    random.seed(42)
    
    # Parameters for the pattern
    cx, cy = w / 2, h / 2
    
    for y in range(h):
        for x in range(w):
            # Normalized coordinates
            nx = (x - cx) / (w/2)
            ny = (y - cy) / (h/2)
            
            r = math.sqrt(nx*nx + ny*ny)
            theta = math.atan2(ny, nx)
            
            # Layer 1: Spiral pattern
            spiral = math.sin(8 * theta + 6 * r + math.sin(3*r)*2) * 0.5 + 0.5
            
            # Layer 2: Concentric waves
            waves = math.sin(r * 15 + math.sin(theta * 3) * 2) * 0.5 + 0.5
            
            # Layer 3: Fractal-like perturbation
            fx = math.sin(nx * 5 + math.cos(ny * 3)) * math.cos(ny * 7 + math.sin(nx * 4))
            fractal = fx * 0.5 + 0.5
            
            # Layer 4: Pythagorean motif - triangular wave pattern
            tri = abs(math.sin(nx * 3 + ny * 4)) * abs(math.cos(nx * 4 - ny * 3))
            
            # Combine layers
            combined = spiral * 0.3 + waves * 0.25 + fractal * 0.2 + tri * 0.25
            
            # Map to psychedelic color palette
            # Deep space blues -> electric purples -> hot pinks -> golden -> teal
            hue = (combined * 300 + r * 60 + theta * 20) % 360
            sat = 0.7 + 0.3 * math.sin(r * 4)
            val = 0.15 + 0.7 * combined + 0.15 * math.sin(theta * 5 + r * 3)
            
            # Darken edges for vignette
            vignette = 1.0 - 0.4 * min(1.0, r * 0.7)
            val *= vignette
            
            val = max(0, min(1, val))
            sat = max(0, min(1, sat))
            
            pixels[x, y] = hsv_to_rgb(hue, sat, val)
    
    return img

def add_golden_triangle_motif(img, draw):
    """Add a glowing Pythagorean triangle at the center of the front cover."""
    # Front cover center
    front_cx = WRAP + BLEED + SPINE_W + BLEED + FRONT_W + FRONT_W // 2
    front_cy = TOTAL_H // 2
    
    # 3-4-5 triangle scaled up
    scale = 120
    # Right angle at bottom-left
    ax, ay = front_cx - 4 * scale, front_cy + 3 * scale  # bottom left (right angle)
    bx, by = front_cx + 4 * scale, front_cy + 3 * scale  # bottom right
    cx, cy = front_cx - 4 * scale, front_cy - 3 * scale  # top

    # Glow effect - multiple layers
    for glow in range(20, 0, -1):
        alpha = int(255 * (1 - glow / 20) * 0.4)
        color = (255, 215, 80, alpha)
        width = glow * 3
        draw.line([(ax, ay), (bx, by)], fill=(255, 200, 50), width=width)
        draw.line([(bx, by), (cx, cy)], fill=(255, 200, 50), width=width)
        draw.line([(cx, cy), (ax, ay)], fill=(255, 200, 50), width=width)
    
    # Inner triangle - bright gold
    draw.line([(ax, ay), (bx, by)], fill=(255, 223, 100), width=6)
    draw.line([(bx, by), (cx, cy)], fill=(255, 223, 100), width=6)
    draw.line([(cx, cy), (ax, ay)], fill=(255, 223, 100), width=6)
    
    # Right angle marker
    marker_size = 40
    draw.line([(ax, ay - marker_size), (ax + marker_size, ay - marker_size)], 
              fill=(255, 223, 100), width=4)
    draw.line([(ax + marker_size, ay - marker_size), (ax + marker_size, ay)],
              fill=(255, 223, 100), width=4)
    
    # Labels: 3, 4, 5
    try:
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    except:
        font_label = ImageFont.load_default()
    
    # "3" on the left side (vertical leg)
    draw.text((ax - 90, (ay + cy) // 2 - 36), "3", fill=(255, 223, 100), font=font_label)
    # "4" on the bottom (horizontal leg)
    draw.text(((ax + bx) // 2 - 20, ay + 30), "4", fill=(255, 223, 100), font=font_label)
    # "5" on the hypotenuse
    mid_hx = (bx + cx) // 2
    mid_hy = (by + cy) // 2
    draw.text((mid_hx + 30, mid_hy - 36), "5", fill=(255, 223, 100), font=font_label)

    return img

def add_tree_branches(draw):
    """Add faint Berggren tree branching patterns radiating from the triangle."""
    front_cx = WRAP + BLEED + SPINE_W + BLEED + FRONT_W + FRONT_W // 2
    front_cy = TOTAL_H // 2
    
    random.seed(123)
    
    def draw_branch(x, y, angle, length, depth, opacity):
        if depth <= 0 or length < 10:
            return
        ex = x + length * math.cos(angle)
        ey = y + length * math.sin(angle)
        alpha = max(30, int(opacity))
        color = (180, 140, 255, alpha)
        draw.line([(int(x), int(y)), (int(ex), int(ey))], fill=(180, 140, 255), width=max(1, depth))
        
        # Three branches (ternary tree)
        for da in [-0.5, 0, 0.5]:
            new_angle = angle + da + random.uniform(-0.1, 0.1)
            draw_branch(ex, ey, new_angle, length * 0.65, depth - 1, opacity * 0.7)
    
    # Branches radiating outward
    for start_angle in [0, math.pi/3, 2*math.pi/3, math.pi, 4*math.pi/3, 5*math.pi/3]:
        draw_branch(front_cx, front_cy, start_angle, 200, 6, 200)

def add_light_cone_rays(draw):
    """Add subtle light cone / spacetime rays."""
    front_cx = WRAP + BLEED + SPINE_W + BLEED + FRONT_W + FRONT_W // 2
    front_cy = TOTAL_H // 2
    
    for i in range(36):
        angle = i * math.pi / 18
        length = 1200 + 300 * math.sin(angle * 3)
        ex = front_cx + length * math.cos(angle)
        ey = front_cy + length * math.sin(angle)
        
        # Gradient ray
        for j in range(50):
            t = j / 50
            px = int(front_cx + t * (ex - front_cx))
            py = int(front_cy + t * (ey - front_cy))
            alpha = int(80 * (1 - t))
            r = int(100 + 155 * t)
            g = int(50 + 100 * math.sin(angle + t * 2))
            b = int(200 - 100 * t)
            draw.ellipse([px-2, py-2, px+2, py+2], fill=(r % 256, g % 256, b % 256))


def add_text(img, draw):
    """Add title, author, and spine text."""
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 130)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 52)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 60)
        font_spine = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 50)
        font_spine_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_author = font_title
        font_spine = font_title
        font_spine_author = font_title
    
    # ── Front cover text ──
    front_left = WRAP + BLEED + SPINE_W + BLEED + FRONT_W
    front_right = front_left + FRONT_W
    front_cx = (front_left + front_right) // 2
    
    # Title - two lines
    title1 = "THE TRIANGLE"
    title2 = "THAT SWALLOWED"
    title3 = "THE UNIVERSE"
    
    # Shadow + text for title
    y_start = WRAP + BLEED + 280
    for line, y_off in [(title1, 0), (title2, 150), (title3, 300)]:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        tx = front_cx - tw // 2
        ty = y_start + y_off
        # Shadow
        draw.text((tx + 4, ty + 4), line, fill=(20, 10, 30), font=font_title)
        # Main text - golden
        draw.text((tx, ty), line, fill=(255, 223, 120), font=font_title)
    
    # Subtitle
    subtitle = "Pythagorean Triples, Berggren Trees,"
    subtitle2 = "and the Hidden Architecture of Number Theory"
    for line, y_off in [(subtitle, 620), (subtitle2, 690)]:
        bbox = draw.textbbox((0, 0), line, font=font_subtitle)
        tw = bbox[2] - bbox[0]
        tx = front_cx - tw // 2
        ty = y_start + y_off
        draw.text((tx, ty), line, fill=(200, 180, 255), font=font_subtitle)
    
    # Author
    author = "PAUL KLEMSTINE"
    bbox = draw.textbbox((0, 0), author, font=font_author)
    tw = bbox[2] - bbox[0]
    tx = front_cx - tw // 2
    ty = TOTAL_H - WRAP - BLEED - 300
    draw.text((tx + 3, ty + 3), author, fill=(20, 10, 30), font=font_author)
    draw.text((tx, ty), author, fill=(255, 223, 120), font=font_author)
    
    # ── Spine text ──
    spine_left = WRAP + BLEED + FRONT_W + BLEED
    spine_cx = spine_left + SPINE_W // 2
    
    # Spine title (rotated)
    spine_img = Image.new('RGBA', (TOTAL_H, SPINE_W), (0, 0, 0, 0))
    spine_draw = ImageDraw.Draw(spine_img)
    
    spine_title = "THE TRIANGLE THAT SWALLOWED THE UNIVERSE"
    bbox = spine_draw.textbbox((0, 0), spine_title, font=font_spine)
    tw = bbox[2] - bbox[0]
    tx = (TOTAL_H - tw) // 2
    ty = (SPINE_W - 50) // 2 - 25
    spine_draw.text((tx, ty), spine_title, fill=(255, 223, 120), font=font_spine)
    
    spine_author_text = "KLEMSTINE"
    bbox = spine_draw.textbbox((0, 0), spine_author_text, font=font_spine_author)
    tw2 = bbox[2] - bbox[0]
    spine_draw.text((TOTAL_H - tw2 - 100, ty + 60), spine_author_text, fill=(200, 180, 255), font=font_spine_author)
    
    # Rotate spine text
    spine_rotated = spine_img.rotate(90, expand=True)
    img.paste(spine_rotated, (spine_left, 0), spine_rotated)
    
    # ── Back cover ──
    back_left = WRAP + BLEED
    back_right = back_left + FRONT_W
    back_cx = (back_left + back_right) // 2
    
    # Back cover blurb
    blurb_lines = [
        "A right triangle with sides 3, 4, and 5.",
        "The most familiar shape in all of mathematics.",
        "",
        "But this humble triangle hides a secret:",
        "it is the root of an infinite tree,",
        "a node on Einstein's light cone,",
        "a key to cracking composite numbers,",
        "and a rung on an algebraic ladder",
        "that climbs through the complex numbers,",
        "the quaternions, and the octonions.",
        "",
        "With machine-verified proofs in Lean 4.",
    ]
    
    try:
        font_blurb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 42)
    except:
        font_blurb = ImageFont.load_default()
    
    y_blurb = TOTAL_H // 2 - len(blurb_lines) * 30
    for line in blurb_lines:
        if line == "":
            y_blurb += 30
            continue
        bbox = draw.textbbox((0, 0), line, font=font_blurb)
        tw = bbox[2] - bbox[0]
        tx = back_cx - tw // 2
        draw.text((tx, y_blurb), line, fill=(200, 190, 220), font=font_blurb)
        y_blurb += 56
    
    # "Soli Deo Gloria" on back
    try:
        font_sdg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 36)
    except:
        font_sdg = ImageFont.load_default()
    sdg = "Soli Deo Gloria"
    bbox = draw.textbbox((0, 0), sdg, font=font_sdg)
    tw = bbox[2] - bbox[0]
    draw.text((back_cx - tw // 2, TOTAL_H - WRAP - BLEED - 200), sdg, fill=(200, 180, 255), font=font_sdg)
    
    return img


def add_equation_watermark(draw):
    """Add faint a² + b² = c² watermark."""
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 200)
    except:
        return
    
    front_left = WRAP + BLEED + SPINE_W + BLEED + FRONT_W
    front_right = front_left + FRONT_W
    front_cx = (front_left + front_right) // 2
    
    eq = "a² + b² = c²"
    bbox = draw.textbbox((0, 0), eq, font=font)
    tw = bbox[2] - bbox[0]
    tx = front_cx - tw // 2
    ty = TOTAL_H // 2 + 250
    draw.text((tx, ty), eq, fill=(80, 60, 100), font=font)


def main():
    print(f"Creating cover: {TOTAL_W} x {TOTAL_H} pixels")
    print(f"  Front: {FRONT_W}x{FRONT_H}")
    print(f"  Spine: {SPINE_W}")
    print(f"  Bleed: {BLEED}")
    print(f"  Wrap: {WRAP}")
    
    # Create base image
    img = Image.new('RGB', (TOTAL_W, TOTAL_H), (10, 5, 20))
    
    # Generate psychedelic background  
    print("Generating psychedelic background...")
    img = create_psychedelic_background(img)
    
    draw = ImageDraw.Draw(img)
    
    # Add decorative elements
    print("Adding light cone rays...")
    add_light_cone_rays(draw)
    
    print("Adding tree branches...")
    add_tree_branches(draw)
    
    print("Adding equation watermark...")
    add_equation_watermark(draw)
    
    print("Adding golden triangle...")
    add_golden_triangle_motif(img, draw)
    
    print("Adding text...")
    add_text(img, draw)
    
    # Save
    output_path = "/workspace/request-project/book/casewrap_cover.png"
    img.save(output_path, 'PNG', dpi=(DPI, DPI))
    print(f"Cover saved to {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    import os
    main()
