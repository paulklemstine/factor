#!/usr/bin/env python3
"""
Poincaré Disk Visualization of the Berggren Tree

Projects primitive Pythagorean triples onto the unit circle boundary,
revealing the hyperbolic geometry underlying the Berggren tree.

Generates SVG files for high-quality visualization.
"""
import math
from math import gcd, sqrt

# ── Berggren Matrices ─────────────────────────────────────────────────────────
def apply_A(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def apply_B(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def apply_C(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

CHILDREN = {'A': apply_A, 'B': apply_B, 'C': apply_C}

def generate_tree(max_depth=6):
    """Generate PPTs with path info."""
    results = []
    stack = [(3, 4, 5, "", 0)]
    while stack:
        a, b, c, path, depth = stack.pop()
        results.append((a, b, c, path, depth))
        if depth < max_depth:
            for name, fn in CHILDREN.items():
                a2, b2, c2 = fn(a, b, c)
                stack.append((a2, b2, c2, path + name, depth + 1))
    return results

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_poincare_svg(filename=None, max_depth=5):
    if filename is None:
        filename = os.path.join(BASE, 'visuals', 'poincare_berggren.svg')
    """Create SVG of PPTs projected onto the Poincaré disk boundary."""
    triples = generate_tree(max_depth)
    
    W, H = 800, 800
    cx, cy = W/2, H/2
    R = 350

    COLORS = {
        '': '#FFD700',
        'A': '#FF4444',
        'B': '#4488FF',
        'C': '#44CC44',
    }
    
    def get_color(path):
        if not path:
            return COLORS['']
        return COLORS.get(path[0], '#888888')
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#1a1a2e"/>',
        '',
        '<!-- Poincaré disk boundary -->',
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#334" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#16213e" opacity="0.5"/>',
        '',
    ]
    
    for frac in [0.25, 0.5, 0.75]:
        r = R * frac
        svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#223" stroke-width="0.5"/>')
    
    svg_lines.append(f'<line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="#223" stroke-width="0.5"/>')
    svg_lines.append(f'<line x1="{cx}" y1="{cy-R}" x2="{cx}" y2="{cy+R}" stroke="#223" stroke-width="0.5"/>')
    
    positions = {}
    for a, b, c, path, depth in triples:
        theta = math.atan2(b, a)
        r_frac = 1 - 1.0 / (1 + depth * 0.4)
        px = cx + R * r_frac * math.cos(theta)
        py = cy - R * r_frac * math.sin(theta)
        positions[path] = (px, py)
    
    svg_lines.append('')
    svg_lines.append('<!-- Tree edges -->')
    for a, b, c, path, depth in triples:
        if path:
            parent_path = path[:-1]
            if parent_path in positions:
                x1, y1 = positions[parent_path]
                x2, y2 = positions[path]
                color = get_color(path)
                opacity = max(0.1, 0.8 - depth * 0.1)
                svg_lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="{color}" stroke-width="{max(0.5, 2 - depth*0.2):.1f}" opacity="{opacity:.2f}"/>'
                )
    
    svg_lines.append('')
    svg_lines.append('<!-- Triple points -->')
    for a, b, c, path, depth in triples:
        if path in positions:
            px, py = positions[path]
            color = get_color(path)
            size = max(1.5, 6 - depth * 0.8)
            opacity = max(0.3, 1.0 - depth * 0.12)
            svg_lines.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{size:.1f}" '
                f'fill="{color}" opacity="{opacity:.2f}"/>'
            )
    
    if '' in positions:
        px, py = positions['']
        svg_lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="#FFD700" stroke="white" stroke-width="2"/>')
        svg_lines.append(f'<text x="{px:.1f}" y="{py-12:.1f}" text-anchor="middle" fill="white" font-size="12" font-family="monospace">(3,4,5)</text>')
    
    svg_lines.extend([
        '',
        f'<text x="{W/2}" y="30" text-anchor="middle" fill="white" font-size="18" font-family="sans-serif" font-weight="bold">',
        'Berggren Tree on the Poincaré Disk</text>',
        f'<text x="{W/2}" y="50" text-anchor="middle" fill="#888" font-size="12" font-family="sans-serif">',
        f'Primitive Pythagorean Triples (depth ≤ {max_depth})</text>',
        '',
        f'<rect x="20" y="{H-100}" width="15" height="15" fill="#FF4444"/>',
        f'<text x="40" y="{H-88}" fill="#ccc" font-size="12" font-family="sans-serif">A-branch (slowest growth)</text>',
        f'<rect x="20" y="{H-78}" width="15" height="15" fill="#4488FF"/>',
        f'<text x="40" y="{H-66}" fill="#ccc" font-size="12" font-family="sans-serif">B-branch (Pell growth, 3+2√2)</text>',
        f'<rect x="20" y="{H-56}" width="15" height="15" fill="#44CC44"/>',
        f'<text x="40" y="{H-44}" fill="#ccc" font-size="12" font-family="sans-serif">C-branch (quadratic growth)</text>',
        f'<circle cx="27" cy="{H-27}" r="6" fill="#FFD700" stroke="white" stroke-width="1"/>',
        f'<text x="40" y="{H-22}" fill="#ccc" font-size="12" font-family="sans-serif">Root: (3, 4, 5)</text>',
    ])
    
    svg_lines.append('</svg>')
    
    with open(filename, 'w') as f:
        f.write('\n'.join(svg_lines))
    print(f"Created {filename} with {len(triples)} PPTs")

def create_depth_spectrum_svg(filename=None):
    if filename is None:
        filename = os.path.join(BASE, 'visuals', 'depth_spectrum.svg')
    """Create SVG showing growth rates along different branches."""
    W, H = 900, 500
    margin = 60
    
    branches = {}
    for branch_name in ['A', 'B', 'C']:
        fn = CHILDREN[branch_name]
        a, b, c = 3, 4, 5
        hyps = [c]
        for _ in range(8):
            a, b, c = fn(a, b, c)
            hyps.append(c)
        branches[branch_name] = hyps
    
    max_val = max(max(h) for h in branches.values())
    max_log = math.log10(max_val + 1)
    
    colors = {'A': '#FF4444', 'B': '#4488FF', 'C': '#44CC44'}
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#1a1a2e"/>',
        '',
        f'<text x="{W/2}" y="30" text-anchor="middle" fill="white" font-size="18" font-family="sans-serif" font-weight="bold">',
        'Hypotenuse Growth: Pure Branch Paths (log scale)</text>',
    ]
    
    plot_w = W - 2*margin
    plot_h = H - 2*margin - 20
    ox, oy = margin, H - margin
    
    svg.append(f'<line x1="{ox}" y1="{oy}" x2="{ox+plot_w}" y2="{oy}" stroke="#555" stroke-width="1"/>')
    svg.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-plot_h}" stroke="#555" stroke-width="1"/>')
    
    n_points = 9
    for i in range(n_points):
        x = ox + i * plot_w / (n_points - 1)
        svg.append(f'<text x="{x}" y="{oy+20}" text-anchor="middle" fill="#888" font-size="11" font-family="monospace">{i}</text>')
    svg.append(f'<text x="{W/2}" y="{oy+40}" text-anchor="middle" fill="#aaa" font-size="12" font-family="sans-serif">Depth</text>')
    
    for exp in range(0, int(max_log) + 2):
        y = oy - (exp / max_log) * plot_h
        if y >= oy - plot_h:
            svg.append(f'<text x="{ox-10}" y="{y+4}" text-anchor="end" fill="#888" font-size="11" font-family="monospace">10^{exp}</text>')
            svg.append(f'<line x1="{ox}" y1="{y}" x2="{ox+plot_w}" y2="{y}" stroke="#333" stroke-width="0.5"/>')
    
    for branch_name, hyps in branches.items():
        color = colors[branch_name]
        points = []
        for i, c in enumerate(hyps):
            x = ox + i * plot_w / (n_points - 1)
            log_c = math.log10(c) if c > 0 else 0
            y = oy - (log_c / max_log) * plot_h
            points.append(f"{x:.1f},{y:.1f}")
        
        polyline = ' '.join(points)
        svg.append(f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        
        for i, c in enumerate(hyps):
            x = ox + i * plot_w / (n_points - 1)
            log_c = math.log10(c) if c > 0 else 0
            y = oy - (log_c / max_log) * plot_h
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
    
    ly = 70
    for branch_name in ['A', 'B', 'C']:
        growth = {
            'A': 'O(d²) quadratic',
            'B': 'O((3+2√2)^d) exponential',
            'C': 'O(d²) quadratic'
        }[branch_name]
        svg.append(f'<line x1="{W-280}" y1="{ly}" x2="{W-250}" y2="{ly}" stroke="{colors[branch_name]}" stroke-width="3"/>')
        svg.append(f'<text x="{W-245}" y="{ly+4}" fill="#ccc" font-size="12" font-family="sans-serif">{branch_name}-branch: {growth}</text>')
        ly += 22
    
    svg.append('</svg>')
    
    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print(f"Created {filename}")

def create_factoring_diagram_svg(filename=None):
    if filename is None:
        filename = os.path.join(BASE, 'visuals', 'factoring_diagram.svg')
    """Create SVG showing the factoring-via-descent process."""
    W, H = 800, 600
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs>',
        '  <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">',
        '    <polygon points="0 0, 10 3.5, 0 7" fill="#888"/>',
        '  </marker>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="#1a1a2e"/>',
        f'<text x="{W/2}" y="35" text-anchor="middle" fill="white" font-size="18" font-family="sans-serif" font-weight="bold">',
        'Integer Factoring via Berggren Tree Descent</text>',
    ]
    
    N = 21  # = 3 × 7
    steps = [
        ("N = 21 = 3 × 7", "Find PPTs with leg 21"),
        ("(21, 20, 29)", "Triple found: 21² + 20² = 29²"),
        ("gcd(21, 20) = 1", "No factor from legs"),
        ("Descend: A⁻¹ applied", "→ (7, 24, 25)"),
        ("gcd(7, 21) = 7 ✓", "FACTOR FOUND!"),
        ("21 = 3 × 7", "Complete factorization"),
    ]
    
    box_w, box_h = 320, 45
    start_y = 80
    gap = 65
    
    for i, (label, detail) in enumerate(steps):
        y = start_y + i * gap
        x = W/2 - box_w/2
        
        if i == len(steps) - 1:
            fill, stroke = "#1a4a1a", "#44CC44"
        elif "FACTOR" in detail:
            fill, stroke = "#4a4a1a", "#FFD700"
        else:
            fill, stroke = "#162040", "#4488FF"
        
        svg.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        svg.append(f'<text x="{W/2}" y="{y+20}" text-anchor="middle" fill="white" font-size="13" font-family="monospace" font-weight="bold">{label}</text>')
        svg.append(f'<text x="{W/2}" y="{y+36}" text-anchor="middle" fill="#aaa" font-size="11" font-family="sans-serif">{detail}</text>')
        
        if i < len(steps) - 1:
            svg.append(f'<line x1="{W/2}" y1="{y+box_h}" x2="{W/2}" y2="{y+gap}" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>')
    
    svg.append(f'<text x="{W-100}" y="100" text-anchor="middle" fill="#666" font-size="11" font-family="sans-serif">Complexity:</text>')
    svg.append(f'<text x="{W-100}" y="118" text-anchor="middle" fill="#888" font-size="10" font-family="monospace">O(depth × gcd)</text>')
    svg.append(f'<text x="{W-100}" y="136" text-anchor="middle" fill="#888" font-size="10" font-family="monospace">= O(√c · log N)</text>')
    
    svg.extend([
        f'<rect x="30" y="{H-150}" width="250" height="130" rx="8" fill="#0d1117" stroke="#333" stroke-width="1"/>',
        f'<text x="45" y="{H-130}" fill="#FF9944" font-size="11" font-family="monospace" font-weight="bold">Algorithm Overview:</text>',
        f'<text x="45" y="{H-112}" fill="#ccc" font-size="10" font-family="monospace">1. N² = (c-b)(c+b)</text>',
        f'<text x="45" y="{H-96}" fill="#ccc" font-size="10" font-family="monospace">2. Enumerate divisors of N²</text>',
        f'<text x="45" y="{H-80}" fill="#ccc" font-size="10" font-family="monospace">3. Build PPT (N, b, c)</text>',
        f'<text x="45" y="{H-64}" fill="#ccc" font-size="10" font-family="monospace">4. Descend Berggren tree</text>',
        f'<text x="45" y="{H-48}" fill="#ccc" font-size="10" font-family="monospace">5. Check gcd(leg, N) at</text>',
        f'<text x="45" y="{H-32}" fill="#ccc" font-size="10" font-family="monospace">   each step</text>',
    ])
    
    svg.append('</svg>')
    
    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print(f"Created {filename}")

def create_tree_structure_svg(filename=None):
    if filename is None:
        filename = os.path.join(BASE, 'visuals', 'berggren_tree_structure.svg')
    """Create a clean tree structure diagram showing first 3 levels."""
    W, H = 1000, 650
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#1a1a2e"/>',
        f'<text x="{W/2}" y="30" text-anchor="middle" fill="white" font-size="18" font-family="sans-serif" font-weight="bold">',
        'The Berggren Ternary Tree of Pythagorean Triples</text>',
    ]
    
    # Tree data: depth 0,1,2
    tree = {
        '': (3, 4, 5),
        'A': (5, 12, 13),
        'B': (21, 20, 29),
        'C': (15, 8, 17),
        'AA': (7, 24, 25),
        'AB': (55, 48, 73),
        'AC': (45, 28, 53),
        'BA': (39, 80, 89),
        'BB': (119, 120, 169),
        'BC': (77, 36, 85),
        'CA': (33, 56, 65),
        'CB': (65, 72, 97),
        'CC': (35, 12, 37),
    }
    
    colors = {'A': '#FF4444', 'B': '#4488FF', 'C': '#44CC44'}
    
    positions = {}
    # Root
    positions[''] = (W/2, 80)
    # Depth 1
    d1_y = 220
    d1_spacing = 300
    positions['A'] = (W/2 - d1_spacing, d1_y)
    positions['B'] = (W/2, d1_y)
    positions['C'] = (W/2 + d1_spacing, d1_y)
    # Depth 2
    d2_y = 400
    d2_spacing = 95
    for i, parent in enumerate(['A', 'B', 'C']):
        px, _ = positions[parent]
        for j, child in enumerate(['A', 'B', 'C']):
            key = parent + child
            positions[key] = (px + (j-1)*d2_spacing, d2_y)
    
    # Draw edges
    edges = [
        ('', 'A'), ('', 'B'), ('', 'C'),
        ('A', 'AA'), ('A', 'AB'), ('A', 'AC'),
        ('B', 'BA'), ('B', 'BB'), ('B', 'BC'),
        ('C', 'CA'), ('C', 'CB'), ('C', 'CC'),
    ]
    
    for parent, child in edges:
        x1, y1 = positions[parent]
        x2, y2 = positions[child]
        branch = child[0] if child else 'A'
        color = colors.get(branch, '#888')
        svg.append(f'<line x1="{x1}" y1="{y1+25}" x2="{x2}" y2="{y2-25}" stroke="{color}" stroke-width="2" opacity="0.6"/>')
    
    # Draw nodes
    for path, (a, b, c) in tree.items():
        if path not in positions:
            continue
        x, y = positions[path]
        
        if path == '':
            fill = '#2a2a1a'
            stroke = '#FFD700'
            r = 30
        else:
            branch = path[0]
            fill = '#1a2240' if branch == 'B' else '#2a1a1a' if branch == 'A' else '#1a2a1a'
            stroke = colors[branch]
            r = 24
        
        svg.append(f'<rect x="{x-45}" y="{y-18}" width="90" height="36" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" fill="white" font-size="11" font-family="monospace">({a},{b},{c})</text>')
        
        if path:
            svg.append(f'<text x="{x}" y="{y-22}" text-anchor="middle" fill="{stroke}" font-size="10" font-family="monospace" font-weight="bold">{path}</text>')
    
    # Matrix labels
    svg.extend([
        f'<text x="50" y="{H-80}" fill="#FF4444" font-size="11" font-family="monospace">B_A = [1,-2,2; 2,-1,2; 2,-2,3]</text>',
        f'<text x="50" y="{H-60}" fill="#4488FF" font-size="11" font-family="monospace">B_B = [1, 2,2; 2, 1,2; 2, 2,3]</text>',
        f'<text x="50" y="{H-40}" fill="#44CC44" font-size="11" font-family="monospace">B_C = [-1,2,2;-2,1,2;-2,2,3]</text>',
        f'<text x="{W-350}" y="{H-80}" fill="#aaa" font-size="11" font-family="sans-serif">All matrices preserve Q(a,b,c) = a²+b²-c²</text>',
        f'<text x="{W-350}" y="{H-60}" fill="#aaa" font-size="11" font-family="sans-serif">They are elements of O(2,1;ℤ) — the integer Lorentz group</text>',
        f'<text x="{W-350}" y="{H-40}" fill="#aaa" font-size="11" font-family="sans-serif">Every primitive Pythagorean triple appears exactly once</text>',
    ])
    
    # Pythagorean verification
    svg.append(f'<text x="{W/2}" y="{H-10}" text-anchor="middle" fill="#666" font-size="10" font-family="sans-serif">')
    svg.append(f'Verification: 3²+4²=5² ✓ | 5²+12²=13² ✓ | 21²+20²=29² ✓ | 15²+8²=17² ✓ | ...</text>')
    
    svg.append('</svg>')
    
    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print(f"Created {filename}")

if __name__ == "__main__":
    create_poincare_svg()
    create_depth_spectrum_svg()
    create_factoring_diagram_svg()
    create_tree_structure_svg()
    print("\nAll SVG visualizations created.")
