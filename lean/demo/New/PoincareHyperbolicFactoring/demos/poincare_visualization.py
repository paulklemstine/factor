"""
Poincaré Disk Visualization of the Berggren Tree

Maps the Berggren tree of Pythagorean triples onto the Poincaré disk model
of the hyperbolic plane, generating an SVG visualization.

Each Pythagorean triple (a, b, c) on the light cone x² + y² = z² is
projected to the Poincaré disk via the map (a, b, c) ↦ (a/(c+1), b/(c+1)),
preserving the hyperbolic geometry.
"""

import numpy as np
from math import sqrt, atan2, pi

# Berggren matrices
B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)
B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]], dtype=np.int64)
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]], dtype=np.int64)

ROOT = np.array([3, 4, 5], dtype=np.int64)


def to_poincare(triple):
    """Project a Pythagorean triple to the Poincaré disk.
    Uses stereographic projection from the hyperboloid model."""
    a, b, c = float(triple[0]), float(triple[1]), float(triple[2])
    # Normalize to hyperboloid: divide by c to get point on x²+y²-z²=0, z=1
    # Then project to disk: (x, y) / (1 + z) for hyperboloid model
    # For light cone points, we use (a/c, b/c) scaled to fit in disk
    scale = 1.0 / (c + sqrt(a*a + b*b))
    return (a * scale, b * scale)


def generate_tree_data(depth=5):
    """Generate Berggren tree data with Poincaré disk coordinates."""
    nodes = []
    edges = []

    def _recurse(triple, d, path, parent_idx):
        idx = len(nodes)
        px, py = to_poincare(triple)
        nodes.append({
            'triple': tuple(triple),
            'depth': d,
            'path': path,
            'x': px,
            'y': py,
            'idx': idx,
        })
        if parent_idx >= 0:
            edges.append((parent_idx, idx, path[-1] if path else ''))

        if d >= depth:
            return
        for mat, direction in [(B1, 'L'), (B2, 'M'), (B3, 'R')]:
            child = mat @ triple
            _recurse(child, d + 1, path + direction, idx)

    _recurse(ROOT, 0, '', -1)
    return nodes, edges


def generate_svg(depth=5, width=800, height=800):
    """Generate an SVG visualization of the Berggren tree in the Poincaré disk."""
    nodes, edges = generate_tree_data(depth)

    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2 - 40

    colors = {
        'L': '#4ecdc4',
        'M': '#ff6b6b',
        'R': '#a29bfe',
        '': '#ffffff',
    }

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     font-family="'Segoe UI', Arial, sans-serif">
  <defs>
    <radialGradient id="diskBg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#1a1a3e"/>
      <stop offset="90%" style="stop-color:#0a0a2e"/>
      <stop offset="100%" style="stop-color:#050520"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{width}" height="{height}" fill="#0a0a2e"/>

  <!-- Poincaré disk boundary -->
  <circle cx="{cx}" cy="{cy}" r="{radius+2}" fill="none" stroke="#444" stroke-width="2"/>
  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="url(#diskBg)"/>

  <!-- Title -->
  <text x="{width/2}" y="25" text-anchor="middle" fill="#fff" font-size="18" font-weight="bold">
    Berggren Tree in the Poincaré Disk (depth {depth})
  </text>
''')

    # Draw edges
    svg_parts.append('  <!-- Edges -->\n')
    for parent_idx, child_idx, direction in edges:
        p = nodes[parent_idx]
        c = nodes[child_idx]
        px_svg = cx + p['x'] * radius
        py_svg = cy + p['y'] * radius
        cx_svg = cx + c['x'] * radius
        cy_svg = cy + c['y'] * radius
        color = colors.get(direction, '#666')
        opacity = max(0.1, 0.8 - c['depth'] * 0.12)
        width_line = max(0.3, 2.0 - c['depth'] * 0.3)
        svg_parts.append(
            f'  <line x1="{px_svg:.1f}" y1="{py_svg:.1f}" '
            f'x2="{cx_svg:.1f}" y2="{cy_svg:.1f}" '
            f'stroke="{color}" stroke-width="{width_line:.1f}" opacity="{opacity:.2f}"/>\n'
        )

    # Draw nodes
    svg_parts.append('  <!-- Nodes -->\n')
    for node in nodes:
        x = cx + node['x'] * radius
        y = cy + node['y'] * radius
        d = node['depth']
        r_node = max(1.5, 6 - d * 0.8)

        if d == 0:
            color = '#ffffff'
        else:
            last_dir = node['path'][-1]
            color = colors.get(last_dir, '#888')

        opacity = max(0.3, 1.0 - d * 0.12)
        svg_parts.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r_node:.1f}" '
            f'fill="{color}" opacity="{opacity:.2f}"'
        )
        if d <= 1:
            svg_parts.append(' filter="url(#glow)"')
        svg_parts.append('/>\n')

        # Labels for first 2 levels
        if d <= 1:
            a, b, c = node['triple']
            label = f"({a},{b},{c})"
            font_size = 11 if d == 0 else 9
            svg_parts.append(
                f'  <text x="{x+r_node+3:.1f}" y="{y+4:.1f}" '
                f'fill="{color}" font-size="{font_size}" opacity="0.9">{label}</text>\n'
            )

    # Legend
    svg_parts.append(f'''
  <!-- Legend -->
  <rect x="10" y="{height-90}" width="200" height="80" rx="8" fill="#151540" stroke="#333" opacity="0.9"/>
  <rect x="25" y="{height-75}" width="10" height="10" rx="2" fill="#4ecdc4"/>
  <text x="42" y="{height-66}" fill="#4ecdc4" font-size="11">B₁ branch (det = +1)</text>
  <rect x="25" y="{height-55}" width="10" height="10" rx="2" fill="#ff6b6b"/>
  <text x="42" y="{height-46}" fill="#ff6b6b" font-size="11">B₂ branch (det = -1)</text>
  <rect x="25" y="{height-35}" width="10" height="10" rx="2" fill="#a29bfe"/>
  <text x="42" y="{height-26}" fill="#a29bfe" font-size="11">B₃ branch (det = +1)</text>
''')

    svg_parts.append('</svg>')
    return ''.join(svg_parts)


if __name__ == '__main__':
    # Generate visualizations at different depths
    for depth in [3, 5, 7]:
        svg = generate_svg(depth=depth)
        filename = f'berggren_poincare_depth{depth}.svg'
        filepath = f'/workspace/request-project/visuals/{filename}'
        with open(filepath, 'w') as f:
            f.write(svg)
        print(f"Generated {filename}")

    print("\nDone! SVG files written to visuals/")
