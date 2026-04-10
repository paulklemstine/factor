#!/usr/bin/env python3
"""
Lorentz-Berggren Visualization
================================
Generates publication-quality visualizations of the Berggren tree
in the Poincaré disk model, showing the hyperbolic tiling structure.

Outputs SVG files to the visuals/ directory.

Usage:
    python lorentz_visualization.py [--depth N]
"""

import numpy as np
from math import sqrt, atan2, pi, cos, sin, gcd
import argparse

# ─── Berggren Matrices ───────────────────────────────────────────────────────

A = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
C = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

ROOT = np.array([3, 4, 5])

BRANCH_COLORS = {
    'A': '#e74c3c',   # Red
    'B': '#2ecc71',   # Green
    'C': '#3498db',   # Blue
    'root': '#f39c12'  # Gold
}


def generate_tree_nodes(max_depth):
    """Generate all tree nodes with metadata."""
    from collections import deque
    nodes = []
    queue = deque([(ROOT, '', 0)])

    while queue:
        triple, path, depth = queue.popleft()
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        # Map to unit circle: (a/c, b/c)
        x, y = a / c, b / c
        theta = atan2(y, x)
        branch = path[0] if path else 'root'

        nodes.append({
            'a': a, 'b': b, 'c': c,
            'x': x, 'y': y, 'theta': theta,
            'path': path or 'root',
            'depth': depth,
            'branch': branch,
        })

        if depth < max_depth:
            for name, M in [('A', A), ('B', B), ('C', C)]:
                child = M @ triple
                if child[0] < 0:
                    child = -child
                queue.append((child, path + name, depth + 1))

    return nodes


def svg_poincare_disk(nodes, filename, size=800, title="Berggren Tree on the Poincaré Disk"):
    """Generate SVG of the Berggren tree mapped to the Poincaré disk."""
    cx, cy = size / 2, size / 2
    R = size / 2 - 60  # disk radius

    svg_parts = []
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size + 80}"
     viewBox="0 0 {size} {size + 80}">
<defs>
  <radialGradient id="diskBg" cx="50%" cy="50%" r="50%">
    <stop offset="0%" style="stop-color:#1a1a2e"/>
    <stop offset="100%" style="stop-color:#0d0d1a"/>
  </radialGradient>
  <filter id="glow">
    <feGaussianBlur stdDeviation="2" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<!-- Background -->
<rect width="{size}" height="{size + 80}" fill="#0a0a14"/>

<!-- Title -->
<text x="{cx}" y="30" text-anchor="middle" fill="#e0e0e0"
      font-family="Georgia, serif" font-size="18" font-weight="bold">{title}</text>

<!-- Poincaré disk boundary -->
<circle cx="{cx}" cy="{cy + 40}" r="{R}" fill="url(#diskBg)"
        stroke="#444" stroke-width="2"/>

<!-- Unit circle (light cone) -->
<circle cx="{cx}" cy="{cy + 40}" r="{R}" fill="none"
        stroke="#555" stroke-width="1" stroke-dasharray="4,4"/>
''')

    # Draw edges (parent → child connections)
    node_by_path = {n['path']: n for n in nodes}
    for n in nodes:
        if n['path'] != 'root':
            parent_path = n['path'][:-1] if len(n['path']) > 1 else 'root'
            if parent_path in node_by_path:
                pn = node_by_path[parent_path]
                # Use stereographic-like compression for depth
                pr = 1 - 1 / (1 + pn['depth'] * 0.3)
                cr = 1 - 1 / (1 + n['depth'] * 0.3)
                px = cx + pr * R * cos(pn['theta'])
                py = cy + 40 - pr * R * sin(pn['theta'])
                nx = cx + cr * R * cos(n['theta'])
                ny = cy + 40 - cr * R * sin(n['theta'])
                color = BRANCH_COLORS.get(n['branch'], '#888')
                opacity = max(0.1, 0.6 - n['depth'] * 0.08)
                svg_parts.append(
                    f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
                    f'stroke="{color}" stroke-width="{max(0.5, 2 - n["depth"]*0.3):.1f}" '
                    f'opacity="{opacity:.2f}"/>')

    # Draw nodes
    for n in nodes:
        r_factor = 1 - 1 / (1 + n['depth'] * 0.3)
        px = cx + r_factor * R * cos(n['theta'])
        py = cy + 40 - r_factor * R * sin(n['theta'])
        color = BRANCH_COLORS.get(n['branch'], '#f39c12')
        node_r = max(2, 6 - n['depth'] * 0.5)
        opacity = max(0.3, 1.0 - n['depth'] * 0.1)

        svg_parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r:.1f}" '
            f'fill="{color}" opacity="{opacity:.2f}" filter="url(#glow)"/>')

        # Label for shallow nodes
        if n['depth'] <= 2:
            label = f"({n['a']},{n['b']},{n['c']})"
            svg_parts.append(
                f'<text x="{px + node_r + 3:.1f}" y="{py + 3:.1f}" '
                f'fill="#ccc" font-family="monospace" font-size="9" opacity="0.8">'
                f'{label}</text>')

    # Legend
    legend_y = size + 50
    for i, (name, color) in enumerate(BRANCH_COLORS.items()):
        lx = 50 + i * 160
        svg_parts.append(f'<circle cx="{lx}" cy="{legend_y}" r="5" fill="{color}"/>')
        label = {'A': 'A-branch (slow)', 'B': 'B-branch (fast)',
                 'C': 'C-branch (mirror)', 'root': 'Root (3,4,5)'}[name]
        svg_parts.append(
            f'<text x="{lx + 10}" y="{legend_y + 4}" fill="#aaa" '
            f'font-family="sans-serif" font-size="11">{label}</text>')

    svg_parts.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg_parts))
    print(f"  Saved: {filename}")


def svg_ternary_tree(nodes, filename, size=1000):
    """Generate SVG of the Berggren tree as a proper ternary tree layout."""
    max_depth = max(n['depth'] for n in nodes)

    svg_parts = []
    height = 120 * (max_depth + 1) + 80
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{height}"
     viewBox="0 0 {size} {height}">
<rect width="{size}" height="{height}" fill="#fafaf5"/>
<text x="{size/2}" y="30" text-anchor="middle" fill="#333"
      font-family="Georgia, serif" font-size="18" font-weight="bold">
  Berggren Ternary Tree of Pythagorean Triples</text>
''')

    # Compute positions using tree layout
    positions = {}

    def layout(path, x, y, spread):
        positions[path] = (x, y)
        if len(path.replace('root', '')) < max_depth:
            base = path if path != 'root' else ''
            child_spread = spread / 3.2
            layout(base + 'A' if base else 'A', x - spread, y + 100, child_spread)
            layout(base + 'B' if base else 'B', x, y + 100, child_spread)
            layout(base + 'C' if base else 'C', x + spread, y + 100, child_spread)

    layout('root', size / 2, 60, size / 4)

    node_by_path = {n['path']: n for n in nodes}

    # Draw edges
    for path, (x, y) in positions.items():
        if path != 'root':
            parent = path[:-1] if len(path) > 1 else 'root'
            if parent in positions:
                px, py = positions[parent]
                branch = path[0]
                color = BRANCH_COLORS.get(branch, '#888')
                svg_parts.append(
                    f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                    f'stroke="{color}" stroke-width="1.5" opacity="0.5"/>')

    # Draw nodes
    for path, (x, y) in positions.items():
        if path in node_by_path:
            n = node_by_path[path]
            branch = n['branch']
            color = BRANCH_COLORS.get(branch, '#f39c12')
            r = max(3, 20 - n['depth'] * 3)

            svg_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                f'fill="{color}" stroke="#333" stroke-width="0.5"/>')

            if n['depth'] <= max_depth:
                label = f"({n['a']},{n['b']},{n['c']})"
                font_size = max(7, 11 - n['depth'])
                svg_parts.append(
                    f'<text x="{x:.1f}" y="{y + r + font_size + 2:.1f}" text-anchor="middle" '
                    f'fill="#444" font-family="monospace" font-size="{font_size}">{label}</text>')

    svg_parts.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg_parts))
    print(f"  Saved: {filename}")


def svg_depth_spectrum(filename, size=900):
    """Generate SVG showing depth vs hypotenuse for different branches."""
    svg_parts = []
    height = 500
    margin = 60

    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{height}"
     viewBox="0 0 {size} {height}">
<rect width="{size}" height="{height}" fill="#fafaf5"/>
<text x="{size/2}" y="25" text-anchor="middle" fill="#333"
      font-family="Georgia, serif" font-size="16" font-weight="bold">
  Depth Spectrum: Hypotenuse Growth by Branch</text>
''')

    plot_w = size - 2 * margin
    plot_h = height - 2 * margin - 20

    # Generate data
    max_d = 8
    branches = {'A': A, 'B': B, 'C': C}
    data = {}
    for name, M in branches.items():
        v = ROOT.copy()
        hyps = []
        for d in range(max_d + 1):
            hyps.append(int(v[2]))
            v = M @ v
            if v[0] < 0:
                v = -v
        data[name] = hyps

    # Use log scale for y-axis
    all_hyps = [h for hyps in data.values() for h in hyps]
    max_log = np.log10(max(all_hyps))
    min_log = np.log10(min(all_hyps))

    # Axes
    svg_parts.append(
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{margin+plot_h}" '
        f'stroke="#333" stroke-width="1"/>')
    svg_parts.append(
        f'<line x1="{margin}" y1="{margin+plot_h}" x2="{margin+plot_w}" y2="{margin+plot_h}" '
        f'stroke="#333" stroke-width="1"/>')

    # Axis labels
    svg_parts.append(
        f'<text x="{size/2}" y="{height-10}" text-anchor="middle" fill="#555" '
        f'font-family="sans-serif" font-size="12">Depth in Berggren Tree</text>')
    svg_parts.append(
        f'<text x="15" y="{height/2}" text-anchor="middle" fill="#555" '
        f'font-family="sans-serif" font-size="12" '
        f'transform="rotate(-90 15 {height/2})">log₁₀(hypotenuse)</text>')

    # Grid and tick marks
    for d in range(max_d + 1):
        x = margin + d * plot_w / max_d
        svg_parts.append(
            f'<line x1="{x}" y1="{margin+plot_h}" x2="{x}" y2="{margin+plot_h+5}" stroke="#333"/>')
        svg_parts.append(
            f'<text x="{x}" y="{margin+plot_h+18}" text-anchor="middle" fill="#555" '
            f'font-size="10">{d}</text>')

    for log_val in range(int(min_log), int(max_log) + 2):
        y = margin + plot_h - (log_val - min_log) / (max_log - min_log + 1) * plot_h
        svg_parts.append(
            f'<line x1="{margin-5}" y1="{y}" x2="{margin+plot_w}" y2="{y}" '
            f'stroke="#eee" stroke-width="0.5"/>')
        svg_parts.append(
            f'<text x="{margin-8}" y="{y+4}" text-anchor="end" fill="#555" font-size="10">'
            f'10^{log_val}</text>')

    # Plot curves
    for name, hyps in data.items():
        color = BRANCH_COLORS[name]
        points = []
        for d, h in enumerate(hyps):
            x = margin + d * plot_w / max_d
            log_h = np.log10(h)
            y = margin + plot_h - (log_h - min_log) / (max_log - min_log + 1) * plot_h
            points.append(f"{x:.1f},{y:.1f}")

        svg_parts.append(
            f'<polyline points="{" ".join(points)}" fill="none" '
            f'stroke="{color}" stroke-width="2.5"/>')

        # Data points
        for d, h in enumerate(hyps):
            x = margin + d * plot_w / max_d
            log_h = np.log10(h)
            y = margin + plot_h - (log_h - min_log) / (max_log - min_log + 1) * plot_h
            svg_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" stroke="white" stroke-width="1"/>')

    # Legend
    for i, (name, label) in enumerate([('A', 'A-branch (quadratic growth)'),
                                        ('B', 'B-branch (exponential growth)'),
                                        ('C', 'C-branch (quadratic growth)')]):
        lx = margin + 20
        ly = margin + 20 + i * 20
        svg_parts.append(f'<rect x="{lx}" y="{ly-5}" width="12" height="3" fill="{BRANCH_COLORS[name]}"/>')
        svg_parts.append(
            f'<text x="{lx+18}" y="{ly}" fill="#444" font-family="sans-serif" font-size="11">{label}</text>')

    svg_parts.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg_parts))
    print(f"  Saved: {filename}")


def svg_factoring_diagram(N, filename, size=900):
    """Generate SVG showing the factoring process for a specific number."""
    from math import isqrt

    # Find triples
    triples = []
    N2 = N * N
    for d in range(1, isqrt(N2) + 1):
        if N2 % d == 0:
            e = N2 // d
            if d < e and (d + e) % 2 == 0:
                b_val = (e - d) // 2
                c_val = (e + d) // 2
                if b_val > 0 and c_val > 0:
                    triples.append((N, b_val, c_val))

    height = 120 + len(triples) * 90
    svg_parts = []
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{height}"
     viewBox="0 0 {size} {height}">
<rect width="{size}" height="{height}" fill="#fafaf5"/>
<text x="{size/2}" y="30" text-anchor="middle" fill="#333"
      font-family="Georgia, serif" font-size="16" font-weight="bold">
  Factoring N = {N} via Pythagorean Triples</text>
<text x="{size/2}" y="50" text-anchor="middle" fill="#666"
      font-family="Georgia, serif" font-size="12">
  (c - b)(c + b) = N*N = {N*N}    |    gcd extraction reveals factors</text>
''')

    y_offset = 80
    for i, (a, b, c) in enumerate(triples[:6]):
        y = y_offset + i * 90
        cm_b = c - b
        cp_b = c + b
        g1 = gcd(a, cm_b)
        g2 = gcd(a, cp_b)

        # Box
        svg_parts.append(
            f'<rect x="30" y="{y}" width="{size-60}" height="75" rx="8" '
            f'fill="white" stroke="#ddd" stroke-width="1"/>')

        # Triple info
        svg_parts.append(
            f'<text x="50" y="{y+20}" fill="#333" font-family="monospace" font-size="13">'
            f'Triple #{i+1}: ({a}, {b}, {c})</text>')

        # Identity
        svg_parts.append(
            f'<text x="50" y="{y+40}" fill="#555" font-family="monospace" font-size="11">'
            f'(c−b)(c+b) = {cm_b} × {cp_b} = {cm_b * cp_b}</text>')

        # GCD results
        factor_found = False
        gcd_text = f'gcd({a}, {cm_b}) = {g1}'
        if 1 < g1 < N:
            gcd_text += f'  →  {N} = {g1} × {N//g1}  ★'
            factor_found = True
        gcd_text += f'    gcd({a}, {cp_b}) = {g2}'
        if 1 < g2 < N:
            gcd_text += f'  →  {N} = {g2} × {N//g2}  ★'
            factor_found = True

        color = '#27ae60' if factor_found else '#888'
        svg_parts.append(
            f'<text x="50" y="{y+60}" fill="{color}" font-family="monospace" font-size="11">'
            f'{gcd_text}</text>')

    svg_parts.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg_parts))
    print(f"  Saved: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Lorentz-Berggren Visualization")
    parser.add_argument('--depth', type=int, default=4, help='Tree depth for visualizations')
    args = parser.parse_args()

    print("Generating visualizations...")
    nodes = generate_tree_nodes(args.depth)

    svg_poincare_disk(nodes, '../visuals/poincare_disk.svg')
    svg_ternary_tree(nodes, '../visuals/berggren_ternary_tree.svg')
    svg_depth_spectrum('../visuals/depth_spectrum.svg')
    svg_factoring_diagram(667, '../visuals/factoring_667.svg')
    svg_factoring_diagram(2021, '../visuals/factoring_2021.svg')

    print("\nAll visualizations generated!")


if __name__ == '__main__':
    main()
