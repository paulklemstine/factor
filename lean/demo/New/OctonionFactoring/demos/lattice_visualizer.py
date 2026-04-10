#!/usr/bin/env python3
"""
Lattice Visualization Generator

Generates SVG visualizations for the quaternion factoring paper:
1. Division algebra hierarchy
2. Lattice L₃(N) vectors
3. Dimensional advantage chart
4. Pell obstacle visualization
5. Factoring pipeline diagram
6. Fano plane (octonion multiplication)
"""

import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'visuals')


def svg_header(width, height, title=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" 
     width="{width}" height="{height}">
  <defs>
    <style>
      text {{ font-family: 'Georgia', 'Times New Roman', serif; }}
      .title {{ font-size: 18px; font-weight: bold; fill: #1a1a2e; }}
      .subtitle {{ font-size: 13px; fill: #444; }}
      .label {{ font-size: 12px; fill: #333; }}
      .small {{ font-size: 10px; fill: #666; }}
      .math {{ font-family: 'Times New Roman', serif; font-style: italic; }}
      .axis {{ stroke: #333; stroke-width: 1.5; fill: none; }}
      .grid {{ stroke: #ddd; stroke-width: 0.5; fill: none; }}
      .highlight {{ fill: #e94560; }}
      .accent1 {{ fill: #0f3460; }}
      .accent2 {{ fill: #16213e; }}
      .accent3 {{ fill: #533483; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
  <!-- {title} -->
'''


def svg_footer():
    return '</svg>\n'


# ============================================================
# 1. Division Algebra Hierarchy
# ============================================================

def generate_division_algebra_hierarchy():
    w, h = 700, 500
    svg = svg_header(w, h, "Division Algebra Hierarchy")
    
    svg += '  <rect width="700" height="500" fill="#fafbfc" rx="10"/>\n'
    svg += '  <text x="350" y="35" text-anchor="middle" class="title">Division Algebra Hierarchy</text>\n'
    svg += '  <text x="350" y="55" text-anchor="middle" class="subtitle">Normed Division Algebras over ℝ (Hurwitz Theorem)</text>\n'
    
    # Four levels
    levels = [
        (1, "ℝ", "Real Numbers", "dim 1", "#4CAF50", "Trial Division", "N^1"),
        (2, "ℂ ≅ ℤ[i]", "Gaussian Integers", "dim 2", "#2196F3", "Fermat's Method", "N^{1/2}"),
        (4, "ℍ ≅ ℤ[i,j,k]", "Quaternions", "dim 4", "#FF9800", "This Paper", "N^{1/4}"),
        (8, "𝕆", "Octonions", "dim 8", "#E91E63", "Open Question", "N^{1/8}"),
    ]
    
    for idx, (dim, symbol, name, dim_label, color, method, bound) in enumerate(levels):
        y = 90 + idx * 100
        bw = 560
        bh = 80
        x = 70
        
        # Box
        svg += f'  <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" '
        svg += f'fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width="2"/>\n'
        
        # Symbol
        svg += f'  <text x="{x + 30}" y="{y + 35}" font-size="24" font-weight="bold" fill="{color}">{symbol}</text>\n'
        
        # Name and details
        svg += f'  <text x="{x + 180}" y="{y + 28}" font-size="14" font-weight="bold" fill="#333">{name}</text>\n'
        svg += f'  <text x="{x + 180}" y="{y + 48}" font-size="11" fill="#666">{dim_label} · Associative: {"Yes" if dim <= 4 else "No"} · Commutative: {"Yes" if dim <= 2 else "No"}</text>\n'
        
        # Method
        svg += f'  <text x="{x + 420}" y="{y + 28}" font-size="12" fill="{color}" font-weight="bold">{method}</text>\n'
        svg += f'  <text x="{x + 420}" y="{y + 48}" font-size="11" fill="#666">Bound: {bound}</text>\n'
        
        # Connecting arrow
        if idx < 3:
            svg += f'  <line x1="350" y1="{y + bh}" x2="350" y2="{y + 100}" '
            svg += f'stroke="#999" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrowhead)"/>\n'
            svg += f'  <text x="365" y="{y + bh + 13}" font-size="9" fill="#999">extends</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# 2. Lattice Vectors Visualization
# ============================================================

def generate_lattice_visualization():
    w, h = 600, 600
    svg = svg_header(w, h, "Lattice L₃(N) Visualization")
    
    svg += '  <rect width="600" height="600" fill="#fafbfc" rx="10"/>\n'
    svg += '  <text x="300" y="30" text-anchor="middle" class="title">Lattice L₃(N=15) Short Vectors</text>\n'
    svg += '  <text x="300" y="50" text-anchor="middle" class="subtitle">Projection to (x,y) plane · Color = z value</text>\n'
    
    N = 15
    cx, cy = 300, 320
    scale = 25
    
    # Grid
    for i in range(-10, 11):
        x = cx + i * scale
        svg += f'  <line x1="{x}" y1="70" x2="{x}" y2="570" class="grid"/>\n'
        y_pos = cy + i * scale
        svg += f'  <line x1="50" y1="{y_pos}" x2="550" y2="{y_pos}" class="grid"/>\n'
    
    # Axes
    svg += f'  <line x1="50" y1="{cy}" x2="550" y2="{cy}" class="axis" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <line x1="{cx}" y1="570" x2="{cx}" y2="70" class="axis" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <text x="555" y="{cy - 5}" class="label">x</text>\n'
    svg += f'  <text x="{cx + 8}" y="75" class="label">y</text>\n'
    
    # Find and plot lattice vectors
    vectors = []
    bound = 8
    for x in range(-bound, bound+1):
        for y in range(-bound, bound+1):
            for z in range(-bound, bound+1):
                if (x*x + y*y + z*z) % N == 0 and (x or y or z):
                    vectors.append((x, y, z))
    
    # Color by z value
    colors = {-3: "#1a237e", -2: "#283593", -1: "#3949ab", 0: "#e53935",
              1: "#43a047", 2: "#2e7d32", 3: "#1b5e20"}
    
    for x, y, z in vectors:
        px = cx + x * scale
        py = cy - y * scale  # flip y
        
        if 55 < px < 545 and 75 < py < 565:
            z_clamp = max(-3, min(3, z))
            color = colors.get(z_clamp, "#888")
            r = 4 if z == 0 else 3
            opacity = "0.9" if z == 0 else "0.5"
            
            svg += f'  <circle cx="{px}" cy="{py}" r="{r}" fill="{color}" opacity="{opacity}"/>\n'
    
    # Origin
    svg += f'  <circle cx="{cx}" cy="{cy}" r="5" fill="#e53935" stroke="white" stroke-width="1.5"/>\n'
    
    # Legend
    svg += '  <text x="60" y="590" font-size="10" fill="#666">Red: z=0 · Green: z&gt;0 · Blue: z&lt;0 · Size indicates proximity to z=0 plane</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# 3. Dimensional Advantage Chart
# ============================================================

def generate_dimensional_chart():
    w, h = 650, 450
    svg = svg_header(w, h, "Dimensional Advantage")
    
    svg += '  <rect width="650" height="450" fill="#fafbfc" rx="10"/>\n'
    svg += '  <text x="325" y="30" text-anchor="middle" class="title">Minkowski Bound: N^(1/d) by Dimension</text>\n'
    svg += '  <text x="325" y="50" text-anchor="middle" class="subtitle">Shorter vectors in higher dimensions enable better factoring</text>\n'
    
    # Chart area
    chart_x, chart_y = 80, 70
    chart_w, chart_h = 500, 320
    
    # Axes
    svg += f'  <line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}" class="axis"/>\n'
    svg += f'  <line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x}" y2="{chart_y}" class="axis"/>\n'
    
    svg += f'  <text x="{chart_x + chart_w/2}" y="{chart_y + chart_h + 35}" text-anchor="middle" class="label">N (log scale)</text>\n'
    svg += f'  <text x="{chart_x - 45}" y="{chart_y + chart_h/2}" text-anchor="middle" class="label" transform="rotate(-90 {chart_x - 45} {chart_y + chart_h/2})">Minkowski Bound</text>\n'
    
    # Plot N^(1/d) for d = 1, 2, 3, 4, 8
    dims = [(1, "#e53935", "d=1 (N)"), (2, "#FF9800", "d=2 (√N)"), 
            (3, "#4CAF50", "d=3 (∛N)"), (4, "#2196F3", "d=4 (⁴√N)"),
            (8, "#9C27B0", "d=8 (⁸√N)")]
    
    N_values = [10, 100, 1000, 10000, 100000, 1000000]
    log_max = math.log10(1000000)
    log_min = math.log10(10)
    val_max = 1000000
    val_min = 1
    
    for d, color, label in dims:
        points = []
        for N in N_values:
            x = chart_x + (math.log10(N) - log_min) / (log_max - log_min) * chart_w
            val = N ** (1.0/d)
            y = chart_y + chart_h - (math.log10(max(1, val)) / math.log10(val_max)) * chart_h
            y = max(chart_y, min(chart_y + chart_h, y))
            points.append(f"{x:.1f},{y:.1f}")
        
        svg += f'  <polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.5"/>\n'
    
    # Legend
    legend_x, legend_y = chart_x + chart_w + 15, chart_y + 20
    for i, (d, color, label) in enumerate(dims):
        y = legend_y + i * 22
        svg += f'  <line x1="{legend_x}" y1="{y}" x2="{legend_x + 20}" y2="{y}" stroke="{color}" stroke-width="2.5"/>\n'
        svg += f'  <text x="{legend_x + 25}" y="{y + 4}" font-size="11" fill="#333">{label}</text>\n'
    
    # N tick labels
    for N in N_values:
        x = chart_x + (math.log10(N) - log_min) / (log_max - log_min) * chart_w
        svg += f'  <text x="{x}" y="{chart_y + chart_h + 18}" text-anchor="middle" font-size="10" fill="#666">{N:,}</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# 4. Pell Obstacle Visualization
# ============================================================

def generate_pell_obstacle():
    w, h = 600, 500
    svg = svg_header(w, h, "Pell Obstacle")
    
    svg += '  <rect width="600" height="500" fill="#fafbfc" rx="10"/>\n'
    svg += '  <text x="300" y="30" text-anchor="middle" class="title">The Pell Obstacle</text>\n'
    svg += '  <text x="300" y="50" text-anchor="middle" class="subtitle">λ² − n·μ² = 1: Solutions depend critically on n</text>\n'
    
    cx, cy = 300, 280
    scale = 22
    
    # Grid
    for i in range(-12, 13):
        x = cx + i * scale
        if 40 < x < 560:
            svg += f'  <line x1="{x}" y1="70" x2="{x}" y2="470" class="grid"/>\n'
        y = cy + i * scale
        if 70 < y < 470:
            svg += f'  <line x1="40" y1="{y}" x2="560" y2="{y}" class="grid"/>\n'
    
    # Axes
    svg += f'  <line x1="40" y1="{cy}" x2="560" y2="{cy}" class="axis" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <line x1="{cx}" y1="470" x2="{cx}" y2="70" class="axis" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <text x="565" y="{cy - 5}" class="label">λ</text>\n'
    svg += f'  <text x="{cx + 8}" y="75" class="label">μ</text>\n'
    
    # Draw hyperbolas λ² - μ² = 1 (n=1, Pell obstacle)
    # λ = ±cosh(t), μ = sinh(t)
    svg += '  <!-- Hyperbola λ² - μ² = 1 -->\n'
    pts_right = []
    pts_left = []
    for i in range(-40, 41):
        t = i * 0.08
        l_val = math.cosh(t)
        m_val = math.sinh(t)
        px = cx + l_val * scale
        py = cy - m_val * scale
        if 40 < px < 560 and 70 < py < 470:
            pts_right.append(f"{px:.1f},{py:.1f}")
        px2 = cx - l_val * scale
        if 40 < px2 < 560 and 70 < py < 470:
            pts_left.append(f"{px2:.1f},{py:.1f}")
    
    if pts_right:
        svg += f'  <polyline points="{" ".join(pts_right)}" fill="none" stroke="#e53935" stroke-width="2" stroke-dasharray="6,3"/>\n'
    if pts_left:
        svg += f'  <polyline points="{" ".join(pts_left)}" fill="none" stroke="#e53935" stroke-width="2" stroke-dasharray="6,3"/>\n'
    
    # Mark the only integer solutions: (1,0) and (-1,0)
    for l_val in [1, -1]:
        px = cx + l_val * scale
        py = cy
        svg += f'  <circle cx="{px}" cy="{py}" r="6" fill="#e53935" stroke="white" stroke-width="2"/>\n'
        svg += f'  <text x="{px}" y="{py - 12}" text-anchor="middle" font-size="11" font-weight="bold" fill="#e53935">({l_val}, 0)</text>\n'
    
    # Draw hyperbola λ² - 2μ² = 1 (n=2, infinitely many solutions)
    pts_right2 = []
    for i in range(-60, 61):
        t = i * 0.06
        # parametrize: λ = cosh(t*arccosh(3)), μ = sinh(t*arccosh(3))/√2
        # simpler: just check integer points
        pass
    
    # Mark n=2 integer solutions
    n2_solutions = [(1,0), (-1,0), (3,2), (3,-2), (-3,2), (-3,-2),
                    (17,12), (17,-12), (-17,12), (-17,-12)]
    for l_val, m_val in n2_solutions:
        px = cx + l_val * scale
        py = cy - m_val * scale
        if 45 < px < 555 and 75 < py < 465:
            svg += f'  <circle cx="{px}" cy="{py}" r="5" fill="#2196F3" stroke="white" stroke-width="1.5"/>\n'
    
    # Legend
    svg += '  <circle cx="60" cy="485" r="5" fill="#e53935"/>\n'
    svg += '  <text x="72" y="489" font-size="11" fill="#333">n=1 (Pell Obstacle): only (±1, 0)</text>\n'
    svg += '  <circle cx="310" cy="485" r="5" fill="#2196F3"/>\n'
    svg += '  <text x="322" y="489" font-size="11" fill="#333">n=2: infinitely many solutions</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# 5. Factoring Pipeline Diagram
# ============================================================

def generate_pipeline_diagram():
    w, h = 800, 350
    svg = svg_header(w, h, "Quaternion Factoring Pipeline")
    
    svg += '  <rect width="800" height="350" fill="#fafbfc" rx="10"/>\n'
    svg += '  <text x="400" y="30" text-anchor="middle" class="title">Quaternion Factoring Pipeline</text>\n'
    
    steps = [
        ("Input", "N = p·q", "#e53935", "Composite\ninteger"),
        ("Decompose", "4-Square", "#FF9800", "N = Σaᵢ²\n(Lagrange)"),
        ("Construct", "Lattice", "#4CAF50", "L₄(N) ⊂ ℤ⁴"),
        ("Reduce", "LLL/BKZ", "#2196F3", "Short vectors\n‖v‖ ≈ N^{1/4}"),
        ("Extract", "GCD", "#9C27B0", "p = gcd(·,N)"),
        ("Output", "p, q", "#e53935", "Factored!"),
    ]
    
    bw, bh = 100, 70
    spacing = 120
    start_x = 40
    y = 100
    
    for i, (title, main, color, detail) in enumerate(steps):
        x = start_x + i * spacing
        
        # Box with gradient effect
        svg += f'  <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" '
        svg += f'fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="2"/>\n'
        
        # Step number
        svg += f'  <circle cx="{x + 15}" cy="{y - 8}" r="12" fill="{color}"/>\n'
        svg += f'  <text x="{x + 15}" y="{y - 4}" text-anchor="middle" font-size="11" fill="white" font-weight="bold">{i+1}</text>\n'
        
        # Title
        svg += f'  <text x="{x + bw/2}" y="{y + 22}" text-anchor="middle" font-size="13" font-weight="bold" fill="{color}">{title}</text>\n'
        svg += f'  <text x="{x + bw/2}" y="{y + 40}" text-anchor="middle" font-size="12" fill="#333">{main}</text>\n'
        
        # Detail below
        lines = detail.split('\n')
        for j, line in enumerate(lines):
            svg += f'  <text x="{x + bw/2}" y="{y + bh + 20 + j*15}" text-anchor="middle" font-size="10" fill="#666">{line}</text>\n'
        
        # Arrow
        if i < len(steps) - 1:
            ax = x + bw + 5
            svg += f'  <line x1="{ax}" y1="{y + bh/2}" x2="{ax + spacing - bw - 10}" y2="{y + bh/2}" '
            svg += f'stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>\n'
    
    # Bottom annotation
    svg += '  <text x="400" y="280" text-anchor="middle" font-size="12" fill="#666">Key Insight: Higher dimension d → shorter vectors N^(1/d) → easier factor extraction</text>\n'
    
    # Complexity comparison
    svg += '  <rect x="80" y="300" width="640" height="35" rx="5" fill="#f5f5f5" stroke="#ddd"/>\n'
    svg += '  <text x="400" y="322" text-anchor="middle" font-size="11" fill="#333">'
    svg += 'Trial Division: O(N^{1/2}) → Quaternion Lattice (d=4): O(N^{1/4}) → Octonion Lattice (d=8): O(N^{1/8})?</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# 6. Fano Plane (Octonion Multiplication)
# ============================================================

def generate_fano_plane():
    w, h = 550, 550
    svg = svg_header(w, h, "Fano Plane - Octonion Multiplication")
    
    svg += '  <rect width="550" height="550" fill="#fafbfc" rx="10"/>\n'
    svg += '  <text x="275" y="30" text-anchor="middle" class="title">The Fano Plane</text>\n'
    svg += '  <text x="275" y="50" text-anchor="middle" class="subtitle">Octonion Multiplication Table: eᵢ · eⱼ = ±eₖ</text>\n'
    
    cx, cy = 275, 290
    R = 150  # outer radius
    r_inner = R * 0.5  # inner triangle radius
    
    # 7 points arranged: 3 on outer triangle, 3 on inner triangle, 1 at center
    # Using standard Fano plane layout
    angles_outer = [90, 210, 330]  # top, bottom-left, bottom-right
    angles_inner = [270, 30, 150]  # bottom, top-right, top-left
    
    points = {}
    
    # Outer triangle vertices (e₁, e₂, e₄)
    labels_outer = ['e₁', 'e₂', 'e₄']
    for i, (ang, label) in enumerate(zip(angles_outer, labels_outer)):
        rad = math.radians(ang)
        x = cx + R * math.cos(rad)
        y = cy - R * math.sin(rad)
        points[label] = (x, y)
    
    # Inner triangle vertices (e₃, e₅, e₆)
    labels_inner = ['e₆', 'e₃', 'e₅']
    for i, (ang, label) in enumerate(zip(angles_inner, labels_inner)):
        rad = math.radians(ang)
        x = cx + r_inner * math.cos(rad)
        y = cy - r_inner * math.sin(rad)
        points[label] = (x, y)
    
    # Center (e₇)
    points['e₇'] = (cx, cy)
    
    # Lines of the Fano plane (each line has 3 points, product of first two = third)
    lines = [
        ('e₁', 'e₂', 'e₄', '#e53935'),   # outer edge
        ('e₂', 'e₄', 'e₁', '#FF9800'),   # outer edge (cyclic)
        ('e₁', 'e₃', 'e₇', '#4CAF50'),   # through center
        ('e₂', 'e₅', 'e₇', '#2196F3'),   # through center
        ('e₄', 'e₆', 'e₇', '#9C27B0'),   # through center
        ('e₁', 'e₅', 'e₆', '#795548'),   # inner-outer
        ('e₂', 'e₃', 'e₆', '#607D8B'),   # inner-outer
    ]
    
    # Draw outer triangle
    outer_pts = [points[l] for l in labels_outer]
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in outer_pts)
    svg += f'  <polygon points="{pts_str}" fill="none" stroke="#ccc" stroke-width="1.5"/>\n'
    
    # Draw inner triangle
    inner_pts = [points[l] for l in labels_inner]
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in inner_pts)
    svg += f'  <polygon points="{pts_str}" fill="none" stroke="#ccc" stroke-width="1.5"/>\n'
    
    # Draw lines through center
    for label in labels_outer:
        p1 = points[label]
        p2 = points['e₇']
        svg += f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
        svg += f'stroke="#ddd" stroke-width="1.5"/>\n'
    
    # Draw inscribed circle
    svg += f'  <circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="#ddd" stroke-width="1"/>\n'
    
    # Draw points
    colors = {
        'e₁': '#e53935', 'e₂': '#FF9800', 'e₃': '#4CAF50', 'e₄': '#2196F3',
        'e₅': '#9C27B0', 'e₆': '#795548', 'e₇': '#333333'
    }
    
    for label, (x, y) in points.items():
        color = colors[label]
        svg += f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="18" fill="{color}" stroke="white" stroke-width="2.5"/>\n'
        svg += f'  <text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" font-size="13" fill="white" font-weight="bold">{label}</text>\n'
    
    # Caption
    svg += '  <text x="275" y="480" text-anchor="middle" font-size="11" fill="#666">'
    svg += 'Each line through 3 points defines a multiplication rule: eᵢ · eⱼ = eₖ</text>\n'
    svg += '  <text x="275" y="500" text-anchor="middle" font-size="11" fill="#666">'
    svg += 'Reversing direction negates: eⱼ · eᵢ = -eₖ</text>\n'
    svg += '  <text x="275" y="525" text-anchor="middle" font-size="11" fill="#999">'
    svg += 'The Fano plane encodes octonion non-associativity: 7 lines, 7 points</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    generators = [
        ("division_algebra_hierarchy.svg", generate_division_algebra_hierarchy),
        ("lattice_vectors.svg", generate_lattice_visualization),
        ("dimensional_advantage.svg", generate_dimensional_chart),
        ("pell_obstacle.svg", generate_pell_obstacle),
        ("factoring_pipeline.svg", generate_pipeline_diagram),
        ("fano_plane.svg", generate_fano_plane),
    ]
    
    for filename, generator in generators:
        filepath = os.path.join(OUTPUT_DIR, filename)
        svg_content = generator()
        with open(filepath, 'w') as f:
            f.write(svg_content)
        print(f"  Generated: {filepath}")
    
    print(f"\n  All {len(generators)} SVG visualizations generated in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
