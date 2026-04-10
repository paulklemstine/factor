#!/usr/bin/env python3
"""
Berggren Tree Visualization
============================

Generates SVG visualizations of the Berggren tree in multiple representations:
1. Standard tree layout
2. Poincaré disk model (hyperbolic)
3. Hypotenuse growth chart
"""

import math
from typing import List, Tuple

# Berggren matrices
def apply_B1(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def apply_B2(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def apply_B3(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)


def generate_tree(depth: int) -> dict:
    """Generate the Berggren tree to a given depth."""
    root = (3, 4, 5)
    tree = {'triple': root, 'children': [], 'depth': 0, 'path': ''}

    def expand(node, d):
        if d >= depth:
            return
        a, b, c = node['triple']
        children = [
            ('L', apply_B1(a, b, c)),
            ('M', apply_B2(a, b, c)),
            ('R', apply_B3(a, b, c)),
        ]
        for name, triple in children:
            child = {
                'triple': triple,
                'children': [],
                'depth': d + 1,
                'path': node['path'] + name,
            }
            node['children'].append(child)
            expand(child, d + 1)

    expand(tree, 0)
    return tree


def tree_to_svg(depth: int = 3) -> str:
    """Generate an SVG of the Berggren tree structure."""
    tree = generate_tree(depth)

    width = 1200
    height = 200 + depth * 180
    node_radius = 28

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .node {{ fill: #1a1a2e; stroke: #16213e; stroke-width: 2; }}
      .node-root {{ fill: #e94560; stroke: #0f3460; stroke-width: 3; }}
      .node-L {{ fill: #0f3460; stroke: #16213e; stroke-width: 2; }}
      .node-M {{ fill: #533483; stroke: #16213e; stroke-width: 2; }}
      .node-R {{ fill: #e94560; stroke: #16213e; stroke-width: 2; }}
      .label {{ fill: white; font-family: 'Courier New', monospace; font-size: 10px; text-anchor: middle; dominant-baseline: central; }}
      .edge {{ stroke: #16213e; stroke-width: 2; fill: none; }}
      .title {{ fill: #1a1a2e; font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; text-anchor: middle; }}
      .subtitle {{ fill: #533483; font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }}
      .path-label {{ fill: #533483; font-family: 'Courier New', monospace; font-size: 9px; text-anchor: middle; }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" fill="#f0f0f5"/>
  <text x="{width//2}" y="30" class="title">The Berggren Tree of Pythagorean Triples</text>
  <text x="{width//2}" y="55" class="subtitle">Every primitive Pythagorean triple appears exactly once</text>
''')

    # Position nodes
    positions = {}

    def position_nodes(node, x, y, x_span):
        positions[node['path'] or 'root'] = (x, y)
        n_children = len(node['children'])
        if n_children == 0:
            return
        child_span = x_span / n_children
        start_x = x - x_span / 2 + child_span / 2
        for i, child in enumerate(node['children']):
            cx = start_x + i * child_span
            cy = y + 160
            position_nodes(child, cx, cy, child_span)

    position_nodes(tree, width // 2, 90, width - 100)

    # Draw edges
    def draw_edges(node):
        parent_pos = positions[node['path'] or 'root']
        for child in node['children']:
            child_pos = positions[child['path']]
            svg_parts.append(
                f'  <line x1="{parent_pos[0]}" y1="{parent_pos[1] + node_radius}" '
                f'x2="{child_pos[0]}" y2="{child_pos[1] - node_radius}" class="edge"/>')
            # Direction label on edge
            mx = (parent_pos[0] + child_pos[0]) / 2
            my = (parent_pos[1] + child_pos[1]) / 2
            direction = child['path'][-1]
            svg_parts.append(
                f'  <text x="{mx + 12}" y="{my}" class="path-label">{direction}</text>')
            draw_edges(child)

    draw_edges(tree)

    # Draw nodes
    def draw_nodes(node):
        pos = positions[node['path'] or 'root']
        a, b, c = node['triple']

        if node['path'] == '':
            cls = 'node-root'
        elif node['path'][-1] == 'L':
            cls = 'node-L'
        elif node['path'][-1] == 'M':
            cls = 'node-M'
        else:
            cls = 'node-R'

        svg_parts.append(
            f'  <circle cx="{pos[0]}" cy="{pos[1]}" r="{node_radius}" class="{cls}"/>')
        svg_parts.append(
            f'  <text x="{pos[0]}" y="{pos[1]}" class="label">({a},{b},{c})</text>')

        for child in node['children']:
            draw_nodes(child)

    draw_nodes(tree)

    # Legend
    ly = height - 40
    svg_parts.append(f'  <rect x="20" y="{ly-15}" width="20" height="20" rx="10" class="node-root"/>')
    svg_parts.append(f'  <text x="50" y="{ly}" class="subtitle">Root</text>')
    svg_parts.append(f'  <rect x="120" y="{ly-15}" width="20" height="20" rx="10" class="node-L"/>')
    svg_parts.append(f'  <text x="150" y="{ly}" class="subtitle">B₁ (L, det=+1)</text>')
    svg_parts.append(f'  <rect x="290" y="{ly-15}" width="20" height="20" rx="10" class="node-M"/>')
    svg_parts.append(f'  <text x="320" y="{ly}" class="subtitle">B₂ (M, det=−1)</text>')
    svg_parts.append(f'  <rect x="470" y="{ly-15}" width="20" height="20" rx="10" class="node-R"/>')
    svg_parts.append(f'  <text x="500" y="{ly}" class="subtitle">B₃ (R, det=+1)</text>')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def poincare_disk_svg(depth: int = 4) -> str:
    """Generate a Poincaré disk model visualization of the Berggren tree."""
    tree = generate_tree(depth)

    size = 800
    cx, cy = size // 2, size // 2
    radius = 350

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <style>
      .disk-boundary {{ fill: #fafafa; stroke: #333; stroke-width: 2; }}
      .hyp-point {{ stroke: #333; stroke-width: 1; }}
      .hyp-edge {{ stroke: #999; stroke-width: 1; stroke-opacity: 0.5; }}
      .hyp-label {{ fill: #333; font-family: 'Courier New', monospace; font-size: 8px; text-anchor: middle; dominant-baseline: central; }}
      .disk-title {{ fill: #333; font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; text-anchor: middle; }}
    </style>
    <radialGradient id="diskGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#fff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e8e8f0;stop-opacity:1" />
    </radialGradient>
  </defs>
  <rect width="{size}" height="{size}" fill="#f5f5fa"/>
  <text x="{cx}" y="30" class="disk-title">Berggren Tree in the Poincaré Disk</text>
  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="url(#diskGrad)" stroke="#333" stroke-width="2"/>
''')

    # Map triples to Poincaré disk coordinates
    # Use (a/c, b/c) projected onto the disk
    def triple_to_disk(a, b, c):
        """Map a Pythagorean triple to the Poincaré disk."""
        # Normalize to unit circle (a/c, b/c)
        x, y = a / c, b / c
        # Apply a contraction to keep points inside the disk
        r = math.sqrt(x*x + y*y)
        if r > 0.99:
            scale = 0.99 / r
            x, y = x * scale, y * scale
        return cx + x * radius, cy - y * radius

    # Collect all nodes with positions
    nodes = []
    def collect_nodes(node):
        a, b, c = node['triple']
        px, py = triple_to_disk(a, b, c)
        nodes.append((node, px, py))
        for child in node['children']:
            collect_nodes(child)
    collect_nodes(tree)

    # Draw edges
    for node, px, py in nodes:
        for child in node['children']:
            ca, cb, cc = child['triple']
            cpx, cpy = triple_to_disk(ca, cb, cc)
            svg_parts.append(
                f'  <line x1="{px:.1f}" y1="{py:.1f}" x2="{cpx:.1f}" y2="{cpy:.1f}" class="hyp-edge"/>')

    # Draw nodes
    colors = {'': '#e94560', 'L': '#0f3460', 'M': '#533483', 'R': '#e94560'}
    for node, px, py in nodes:
        a, b, c = node['triple']
        d = node['depth']
        r = max(3, 8 - d)
        path = node['path']
        color = colors.get(path[-1] if path else '', '#e94560')
        svg_parts.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{color}" class="hyp-point"/>')
        if d <= 2:
            svg_parts.append(
                f'  <text x="{px:.1f}" y="{py + r + 10:.1f}" class="hyp-label">({a},{b},{c})</text>')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def lorentz_boost_svg() -> str:
    """Generate an SVG showing the B₂ boost powers."""
    width, height = 800, 500

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .axis {{ stroke: #333; stroke-width: 2; }}
      .axis-label {{ fill: #333; font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }}
      .boost-point {{ fill: #e94560; stroke: #333; stroke-width: 1; }}
      .boost-label {{ fill: #333; font-family: 'Courier New', monospace; font-size: 11px; text-anchor: start; }}
      .boost-line {{ stroke: #e94560; stroke-width: 2; stroke-dasharray: 5,3; }}
      .chart-title {{ fill: #333; font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; text-anchor: middle; }}
      .null-cone {{ stroke: #0f3460; stroke-width: 1.5; stroke-dasharray: 8,4; fill: none; }}
      .hyperboloid {{ stroke: #533483; stroke-width: 2; fill: none; }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" fill="#fafafa"/>
  <text x="{width//2}" y="30" class="chart-title">Integer Lorentz Boosts: Powers of B₂</text>
''')

    # Draw axes
    ox, oy = 100, height - 80  # origin
    ax_len = 600
    ay_len = 350

    svg_parts.append(f'  <line x1="{ox}" y1="{oy}" x2="{ox + ax_len}" y2="{oy}" class="axis"/>')
    svg_parts.append(f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - ay_len}" class="axis"/>')
    svg_parts.append(f'  <text x="{ox + ax_len//2}" y="{oy + 40}" class="axis-label">Rapidity φ = acosh(cosh_val)</text>')
    svg_parts.append(f'  <text x="{ox - 40}" y="{oy - ay_len//2}" class="axis-label" transform="rotate(-90,{ox-40},{oy - ay_len//2})">cosh(φ) value</text>')

    # B₂ powers: cosh values
    cosh_values = [1, 3, 17, 99, 577, 3363]
    rapidities = [0] + [math.acosh(v) for v in cosh_values[1:]]

    max_rapidity = rapidities[-1]
    max_cosh = cosh_values[-1]

    # Scale
    def to_screen(rap, cosh_val):
        x = ox + (rap / max_rapidity) * ax_len
        y = oy - (math.log(cosh_val + 1) / math.log(max_cosh + 1)) * ay_len
        return x, y

    # Draw points and connecting lines
    for i in range(len(cosh_values)):
        x, y = to_screen(rapidities[i], cosh_values[i])
        r = 6
        svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="boost-point"/>')
        svg_parts.append(
            f'  <text x="{x + 10:.1f}" y="{y - 5:.1f}" class="boost-label">'
            f'B₂^{i}: cosh={cosh_values[i]}</text>')

        if i > 0:
            px, py = to_screen(rapidities[i-1], cosh_values[i-1])
            svg_parts.append(
                f'  <line x1="{px:.1f}" y1="{py:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="boost-line"/>')

    # Note
    svg_parts.append(f'  <text x="{width//2}" y="{height - 20}" class="axis-label" style="font-size:12px; fill:#666;">'
                     f'Rapidity grows linearly; cosh grows exponentially (~3^k)</text>')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def factoring_identity_svg() -> str:
    """Generate an SVG illustrating the factoring identity."""
    width, height = 700, 400

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .box {{ fill: #f0f0ff; stroke: #333; stroke-width: 2; rx: 10; }}
      .box-highlight {{ fill: #e8f5e9; stroke: #2e7d32; stroke-width: 2; rx: 10; }}
      .formula {{ fill: #333; font-family: 'Times New Roman', serif; font-size: 18px; text-anchor: middle; dominant-baseline: central; }}
      .formula-large {{ fill: #1a1a2e; font-family: 'Times New Roman', serif; font-size: 24px; font-weight: bold; text-anchor: middle; dominant-baseline: central; }}
      .arrow {{ stroke: #333; stroke-width: 2; fill: #333; }}
      .fig-title {{ fill: #1a1a2e; font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; text-anchor: middle; }}
      .annotation {{ fill: #666; font-family: Arial, sans-serif; font-size: 13px; text-anchor: middle; font-style: italic; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
    </marker>
  </defs>
  <rect width="{width}" height="{height}" fill="#fafafa"/>
  <text x="{width//2}" y="35" class="fig-title">The Factoring Identity: From Pythagorean Triples to Factors</text>
''')

    # Pythagorean triple box
    svg_parts.append(f'  <rect x="50" y="70" width="250" height="60" class="box"/>')
    svg_parts.append(f'  <text x="175" y="90" class="formula">Pythagorean Triple</text>')
    svg_parts.append(f'  <text x="175" y="115" class="formula-large">a² + b² = c²</text>')

    # Arrow down
    svg_parts.append(f'  <line x1="175" y1="130" x2="175" y2="165" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>')

    # Difference of squares
    svg_parts.append(f'  <rect x="50" y="170" width="250" height="60" class="box"/>')
    svg_parts.append(f'  <text x="175" y="190" class="formula">Difference of Squares</text>')
    svg_parts.append(f'  <text x="175" y="215" class="formula-large">(c−b)(c+b) = a²</text>')

    # Arrow right
    svg_parts.append(f'  <line x1="300" y1="200" x2="380" y2="200" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>')

    # GCD extraction
    svg_parts.append(f'  <rect x="390" y="170" width="260" height="60" class="box-highlight"/>')
    svg_parts.append(f'  <text x="520" y="190" class="formula">Factor Extraction</text>')
    svg_parts.append(f'  <text x="520" y="215" class="formula-large">gcd(c−b, N) → factor</text>')

    # Example
    svg_parts.append(f'  <rect x="50" y="270" width="600" height="80" class="box" style="fill:#fff8e1;stroke:#f57f17;"/>')
    svg_parts.append(f'  <text x="350" y="295" class="formula" style="fill:#e65100;">Example: N = 65 = 5 × 13</text>')
    svg_parts.append(f'  <text x="350" y="320" class="formula">Triple (5, 12, 13): (13−12)(13+12) = 1×25 = 5² → gcd(25, 65) = 5 ✓</text>')

    # Annotation
    svg_parts.append(f'  <text x="{width//2}" y="{height - 20}" class="annotation">'
                     f'The Berggren tree descent finds triples where legs share factors with the target number N</text>')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


if __name__ == "__main__":
    # Generate all SVGs
    import os

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'visuals')
    os.makedirs(output_dir, exist_ok=True)

    print("Generating SVG visualizations...")

    # 1. Tree structure
    svg = tree_to_svg(depth=3)
    path = os.path.join(output_dir, 'berggren_tree.svg')
    with open(path, 'w') as f:
        f.write(svg)
    print(f"  ✓ {path}")

    # 2. Poincaré disk
    svg = poincare_disk_svg(depth=4)
    path = os.path.join(output_dir, 'poincare_disk.svg')
    with open(path, 'w') as f:
        f.write(svg)
    print(f"  ✓ {path}")

    # 3. Lorentz boosts
    svg = lorentz_boost_svg()
    path = os.path.join(output_dir, 'lorentz_boosts.svg')
    with open(path, 'w') as f:
        f.write(svg)
    print(f"  ✓ {path}")

    # 4. Factoring identity
    svg = factoring_identity_svg()
    path = os.path.join(output_dir, 'factoring_identity.svg')
    with open(path, 'w') as f:
        f.write(svg)
    print(f"  ✓ {path}")

    print("\nAll visualizations generated!")
