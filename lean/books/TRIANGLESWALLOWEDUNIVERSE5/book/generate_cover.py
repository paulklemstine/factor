#!/usr/bin/env python3
"""Generate a psychedelic casewrap cover image for the book."""
import math
import struct
import zlib
import os

WIDTH = 3600   # ~6 inches at 600 DPI (front+back+spine)
HEIGHT = 2700  # ~9 inches at 600 DPI

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB. h in [0,360), s,v in [0,1]."""
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
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

def write_png(filename, width, height, pixels):
    """Write RGB pixel data as PNG."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter byte
        row_start = y * width * 3
        raw.extend(pixels[row_start:row_start + width * 3])
    
    compressed = zlib.compress(bytes(raw), 6)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')
    
    with open(filename, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

def generate_cover():
    pixels = bytearray(WIDTH * HEIGHT * 3)
    
    cx, cy = WIDTH / 2, HEIGHT / 2
    max_r = math.sqrt(cx*cx + cy*cy)
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = x - cx
            dy = y - cy
            r = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            # Create psychedelic spiral pattern
            t = r / max_r
            
            # Multiple overlapping spirals
            spiral1 = math.sin(angle * 5 + r * 0.02 + t * 15)
            spiral2 = math.cos(angle * 3 - r * 0.015 + t * 10)
            spiral3 = math.sin(angle * 7 + r * 0.025)
            
            # Mandala-like radial pattern
            mandala = math.sin(angle * 8) * math.cos(r * 0.03) * 0.5
            
            # Pythagorean-themed: concentric triangular waves
            tri_wave = abs(math.sin(angle * 3 + r * 0.01)) * math.cos(r * 0.02 - angle * 2)
            
            # Combine for hue
            hue = (angle * 180 / math.pi + 180 + r * 0.15 + spiral1 * 30 + spiral2 * 20 + mandala * 40) % 360
            
            # Saturation: high everywhere, slight variation
            sat = 0.7 + 0.3 * abs(math.sin(r * 0.008 + angle * 2))
            
            # Value: create depth with radial darkening and pattern
            val = 0.3 + 0.5 * (1 - t * 0.4) + 0.2 * tri_wave
            val = max(0.1, min(1.0, val))
            
            # Add a golden/dark border effect
            border_x = min(x, WIDTH - 1 - x) / (WIDTH * 0.05)
            border_y = min(y, HEIGHT - 1 - y) / (HEIGHT * 0.05)
            border = min(1.0, min(border_x, border_y))
            val *= border
            
            # Deep purple/indigo base with rainbow spirals
            hue = (hue + 240) % 360  # shift toward purple base
            
            # Add a bright center glow
            center_glow = max(0, 1 - r / (max_r * 0.3))
            if center_glow > 0:
                val = min(1.0, val + center_glow * 0.3)
                sat = max(0.4, sat - center_glow * 0.2)
            
            R, G, B = hsv_to_rgb(hue, sat, val)
            
            idx = (y * WIDTH + x) * 3
            pixels[idx] = R
            pixels[idx+1] = G
            pixels[idx+2] = B
    
    return pixels

print("Generating psychedelic cover image...")
pixels = generate_cover()
output_path = os.path.join(os.path.dirname(__file__), "cover_casewrap.png")
write_png(output_path, WIDTH, HEIGHT, pixels)
print(f"Cover saved to {output_path}")
# Also generate a smaller front-cover-only version for the title page
FRONT_W = 1800
write_png(os.path.join(os.path.dirname(__file__), "cover_front.png"), FRONT_W, HEIGHT, 
          bytearray(b''.join(pixels[(y*WIDTH + (WIDTH-FRONT_W)//2)*3:(y*WIDTH + (WIDTH-FRONT_W)//2 + FRONT_W)*3] for y in range(HEIGHT))))
print("Front cover saved.")
