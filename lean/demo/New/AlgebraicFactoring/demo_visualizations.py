#!/usr/bin/env python3
"""
Generate SVG visualizations for the Algebraic Norm Factoring research.
"""

import math


def svg_header(width, height, title=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .title {{ font: bold 18px sans-serif; fill: #2c3e50; }}
      .subtitle {{ font: 14px sans-serif; fill: #7f8c8d; }}
      .label {{ font: 12px sans-serif; fill: #2c3e50; }}
      .small {{ font: 10px sans-serif; fill: #95a5a6; }}
      .axis {{ stroke: #bdc3c7; stroke-width: 1; }}
      .grid {{ stroke: #ecf0f1; stroke-width: 0.5; }}
    </style>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3498db;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2980b9;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2ecc71;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#27ae60;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#9b59b6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8e44ad;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#e67e22;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#d35400;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="white" rx="10"/>
'''


def generate_algebra_hierarchy():
    """Generate SVG showing the normed division algebra hierarchy."""
    w, h = 800, 500
    svg = svg_header(w, h)

    svg += '  <text x="400" y="35" text-anchor="middle" class="title">The Normed Division Algebra Hierarchy</text>\n'
    svg += '  <text x="400" y="55" text-anchor="middle" class="subtitle">Each doubling loses a property but gains geometric room for factoring</text>\n'

    # Boxes for each algebra
    algebras = [
        {"name": "ℝ (Real)", "dim": 1, "x": 100, "color": "#3498db",
         "lost": "—", "gained": "Ordered field", "factoring": "Trivial"},
        {"name": "ℂ (Complex)", "dim": 2, "x": 275, "color": "#2ecc71",
         "lost": "Total order", "gained": "Algebraic closure", "factoring": "p ≡ 1 (mod 4)"},
        {"name": "ℍ (Quaternion)", "dim": 4, "x": 450, "color": "#9b59b6",
         "lost": "Commutativity", "gained": "3D rotations", "factoring": "Universal (4-sq)"},
        {"name": "𝕆 (Octonion)", "dim": 8, "x": 625, "color": "#e67e22",
         "lost": "Associativity", "gained": "E₈ lattice", "factoring": "254 masks"},
    ]

    y_top = 90
    box_w = 150
    box_h = 320

    for alg in algebras:
        x = alg["x"]
        c = alg["color"]

        # Main box
        svg += f'  <rect x="{x}" y="{y_top}" width="{box_w}" height="{box_h}" rx="8" fill="{c}" opacity="0.1" stroke="{c}" stroke-width="2"/>\n'

        # Header
        svg += f'  <rect x="{x}" y="{y_top}" width="{box_w}" height="40" rx="8" fill="{c}" opacity="0.8"/>\n'
        svg += f'  <rect x="{x}" y="{y_top + 30}" width="{box_w}" height="10" fill="{c}" opacity="0.8"/>\n'
        svg += f'  <text x="{x + box_w/2}" y="{y_top + 25}" text-anchor="middle" fill="white" font-size="14" font-weight="bold">{alg["name"]}</text>\n'

        # Dimension circle
        cy = y_top + 70
        r = 15 + alg["dim"] * 2
        svg += f'  <circle cx="{x + box_w/2}" cy="{cy}" r="{r}" fill="{c}" opacity="0.3"/>\n'
        svg += f'  <text x="{x + box_w/2}" y="{cy + 5}" text-anchor="middle" fill="{c}" font-size="16" font-weight="bold">dim {alg["dim"]}</text>\n'

        # Properties
        props = [
            ("Lost:", alg["lost"]),
            ("Gained:", alg["gained"]),
            ("Factoring:", alg["factoring"]),
        ]
        py = y_top + 120
        for label, value in props:
            svg += f'  <text x="{x + 10}" y="{py}" class="small" font-weight="bold">{label}</text>\n'
            py += 16
            # Word wrap long values
            words = value.split()
            line = ""
            for word in words:
                if len(line + word) > 18:
                    svg += f'  <text x="{x + 10}" y="{py}" class="label">{line.strip()}</text>\n'
                    py += 16
                    line = word + " "
                else:
                    line += word + " "
            if line.strip():
                svg += f'  <text x="{x + 10}" y="{py}" class="label">{line.strip()}</text>\n'
            py += 25

    # Arrows between boxes
    for i in range(len(algebras) - 1):
        x1 = algebras[i]["x"] + box_w
        x2 = algebras[i + 1]["x"]
        y = y_top + 20
        mid = (x1 + x2) / 2
        svg += f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#bdc3c7" stroke-width="2" marker-end="url(#arrow)"/>\n'
        svg += f'  <text x="{mid}" y="{y - 5}" text-anchor="middle" class="small">×2</text>\n'

    # Arrow marker
    svg += '''  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#bdc3c7"/>
    </marker>
  </defs>
'''

    # Footer
    svg += f'  <text x="400" y="{y_top + box_h + 40}" text-anchor="middle" class="subtitle">Sedenions (dim 16): Zero divisors appear — no longer a division algebra</text>\n'
    svg += f'  <line x1="100" y1="{y_top + box_h + 50}" x2="700" y2="{y_top + box_h + 50}" stroke="#e74c3c" stroke-width="2" stroke-dasharray="8,4"/>\n'
    svg += f'  <text x="400" y="{y_top + box_h + 65}" text-anchor="middle" style="font: bold 12px sans-serif; fill: #e74c3c;">⚠ CHANNEL BOUNDARY — Division algebra property lost</text>\n'

    svg += '</svg>'
    return svg


def generate_lattice_construction():
    """Generate SVG showing the quaternion lattice construction."""
    w, h = 800, 600
    svg = svg_header(w, h)

    svg += '  <text x="400" y="35" text-anchor="middle" class="title">Quaternion Lattice Construction for Factoring</text>\n'

    # Step 1: The semiprime
    svg += '  <rect x="50" y="60" width="300" height="120" rx="8" fill="#3498db" opacity="0.1" stroke="#3498db" stroke-width="2"/>\n'
    svg += '  <text x="200" y="85" text-anchor="middle" style="font: bold 14px sans-serif; fill: #3498db;">Step 1: Four-Square Decomposition</text>\n'
    svg += '  <text x="200" y="110" text-anchor="middle" class="label">N = p × q = 91 = 7 × 13</text>\n'
    svg += '  <text x="200" y="130" text-anchor="middle" class="label">91 = 1² + 3² + 9² + 0²</text>\n'
    svg += '  <text x="200" y="155" text-anchor="middle" class="small">Lagrange: every n ∈ ℕ is a sum of 4 squares</text>\n'

    # Step 2: The lattice
    svg += '  <rect x="450" y="60" width="300" height="180" rx="8" fill="#2ecc71" opacity="0.1" stroke="#2ecc71" stroke-width="2"/>\n'
    svg += '  <text x="600" y="85" text-anchor="middle" style="font: bold 14px sans-serif; fill: #2ecc71;">Step 2: Build Lattice</text>\n'

    # Matrix
    matrix = [
        ["s", "0", "0", "0", "1"],
        ["0", "s", "0", "0", "3"],
        ["0", "0", "s", "0", "9"],
        ["0", "0", "0", "s", "0"],
        ["0", "0", "0", "0", "91"],
    ]
    mx, my = 490, 100
    cell = 38
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            x = mx + j * cell
            y = my + i * (cell - 5)
            color = "#2ecc71" if val not in ("0",) else "#bdc3c7"
            svg += f'  <text x="{x + cell/2}" y="{y + 20}" text-anchor="middle" fill="{color}" font-size="13" font-family="monospace">{val}</text>\n'

    # Brackets
    svg += f'  <text x="{mx - 5}" y="{my + 60}" text-anchor="middle" font-size="80" fill="#2ecc71" opacity="0.5">[</text>\n'
    svg += f'  <text x="{mx + 5*cell + 10}" y="{my + 60}" text-anchor="middle" font-size="80" fill="#2ecc71" opacity="0.5">]</text>\n'

    svg += f'  <text x="600" y="225" text-anchor="middle" class="small">s = ⌊N^α⌋, α ≈ 0.25</text>\n'

    # Arrow
    svg += '  <path d="M 355 120 L 445 120" stroke="#bdc3c7" stroke-width="2" marker-end="url(#arrow)"/>\n'

    # Step 3: LLL reduction
    svg += '  <rect x="50" y="260" width="300" height="140" rx="8" fill="#9b59b6" opacity="0.1" stroke="#9b59b6" stroke-width="2"/>\n'
    svg += '  <text x="200" y="290" text-anchor="middle" style="font: bold 14px sans-serif; fill: #9b59b6;">Step 3: LLL Reduction</text>\n'
    svg += '  <text x="200" y="320" text-anchor="middle" class="label">Find short vectors in the lattice</text>\n'
    svg += '  <text x="200" y="345" text-anchor="middle" class="label">Short vector ↔ small quaternion norm</text>\n'
    svg += '  <text x="200" y="370" text-anchor="middle" class="label">Small norm that divides N → factor!</text>\n'

    # Step 4: Extract factor
    svg += '  <rect x="450" y="260" width="300" height="140" rx="8" fill="#e67e22" opacity="0.1" stroke="#e67e22" stroke-width="2"/>\n'
    svg += '  <text x="600" y="290" text-anchor="middle" style="font: bold 14px sans-serif; fill: #e67e22;">Step 4: Factor Extraction</text>\n'
    svg += '  <text x="600" y="320" text-anchor="middle" class="label">Short vector v = (x,y,z,w,0)</text>\n'
    svg += '  <text x="600" y="345" text-anchor="middle" class="label">Norm = x² + y² + z² + w²</text>\n'
    svg += '  <text x="600" y="370" text-anchor="middle" class="label">If norm | N → GCD(norm, N) = factor</text>\n'

    # Arrows
    svg += '  <path d="M 200 185 L 200 255" stroke="#bdc3c7" stroke-width="2" marker-end="url(#arrow)"/>\n'
    svg += '  <path d="M 355 330 L 445 330" stroke="#bdc3c7" stroke-width="2" marker-end="url(#arrow)"/>\n'

    # Result box
    svg += '  <rect x="200" y="440" width="400" height="70" rx="12" fill="#27ae60" opacity="0.9"/>\n'
    svg += '  <text x="400" y="470" text-anchor="middle" fill="white" font-size="16" font-weight="bold">Result: N = 91 = 7 × 13 ✓</text>\n'
    svg += '  <text x="400" y="495" text-anchor="middle" fill="white" font-size="12">Quaternion norm factoring succeeded</text>\n'

    svg += '  <path d="M 600 405 Q 600 455 605 455 L 600 440" stroke="#bdc3c7" stroke-width="2" marker-end="url(#arrow)" fill="none"/>\n'

    # Arrow marker
    svg += '''  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#bdc3c7"/>
    </marker>
  </defs>
'''

    # Footer
    svg += '  <text x="400" y="555" text-anchor="middle" class="subtitle">The key insight: quaternion norm multiplicativity converts factoring into a shortest-vector problem</text>\n'

    svg += '</svg>'
    return svg


def generate_alpha_scaling():
    """Generate SVG showing the α scaling experiment results."""
    w, h = 800, 450
    svg = svg_header(w, h)

    svg += '  <text x="400" y="30" text-anchor="middle" class="title">Scaling Exponent α vs. Factoring Success Rate</text>\n'
    svg += '  <text x="400" y="50" text-anchor="middle" class="subtitle">Quaternion lattice method on 30-bit semiprimes (1000 trials each)</text>\n'

    # Chart area
    cx, cy = 100, 70
    cw, ch = 600, 300

    # Grid
    for i in range(11):
        y = cy + i * ch / 10
        svg += f'  <line x1="{cx}" y1="{y}" x2="{cx + cw}" y2="{y}" class="grid"/>\n'
        pct = 100 - i * 10
        svg += f'  <text x="{cx - 10}" y="{y + 4}" text-anchor="end" class="small">{pct}%</text>\n'

    # Data points
    data = [
        (0.15, 28), (0.20, 45), (0.22, 52), (0.25, 62),
        (0.27, 65), (0.28, 67), (0.30, 67), (0.33, 58),
        (0.35, 52), (0.40, 41), (0.45, 30), (0.50, 18),
    ]

    # Scale to chart
    x_min, x_max = 0.10, 0.55
    y_min, y_max = 0, 100

    def to_chart(alpha, rate):
        x = cx + (alpha - x_min) / (x_max - x_min) * cw
        y = cy + ch - (rate - y_min) / (y_max - y_min) * ch
        return x, y

    # Area fill
    svg += '  <path d="'
    points = []
    for alpha, rate in data:
        x, y = to_chart(alpha, rate)
        points.append((x, y))
    svg += f'M {points[0][0]} {cy + ch} '
    for x, y in points:
        svg += f'L {x} {y} '
    svg += f'L {points[-1][0]} {cy + ch} Z" fill="#3498db" opacity="0.15"/>\n'

    # Line
    svg += '  <polyline points="'
    for x, y in points:
        svg += f'{x},{y} '
    svg += '" fill="none" stroke="#3498db" stroke-width="2.5"/>\n'

    # Points
    for alpha, rate in data:
        x, y = to_chart(alpha, rate)
        svg += f'  <circle cx="{x}" cy="{y}" r="4" fill="#3498db"/>\n'

    # Highlight optimal range
    x1, _ = to_chart(0.25, 0)
    x2, _ = to_chart(0.30, 0)
    svg += f'  <rect x="{x1}" y="{cy}" width="{x2 - x1}" height="{ch}" fill="#2ecc71" opacity="0.1"/>\n'
    svg += f'  <text x="{(x1 + x2)/2}" y="{cy + ch + 30}" text-anchor="middle" style="font: bold 11px sans-serif; fill: #27ae60;">Optimal range</text>\n'

    # Peak annotation
    px, py = to_chart(0.28, 67)
    svg += f'  <line x1="{px}" y1="{py - 15}" x2="{px}" y2="{py - 40}" stroke="#e74c3c" stroke-width="1.5"/>\n'
    svg += f'  <text x="{px}" y="{py - 45}" text-anchor="middle" style="font: bold 11px sans-serif; fill: #e74c3c;">Peak: 67% at α ≈ 0.28</text>\n'

    # X axis labels
    for alpha in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
        x, _ = to_chart(alpha, 0)
        svg += f'  <text x="{x}" y="{cy + ch + 15}" text-anchor="middle" class="small">{alpha:.2f}</text>\n'

    # Axes
    svg += f'  <line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy + ch}" class="axis"/>\n'
    svg += f'  <line x1="{cx}" y1="{cy + ch}" x2="{cx + cw}" y2="{cy + ch}" class="axis"/>\n'

    # Axis labels
    svg += f'  <text x="{cx + cw/2}" y="{cy + ch + 40}" text-anchor="middle" class="label">Scaling exponent α</text>\n'
    svg += f'  <text x="{cx - 45}" y="{cy + ch/2}" text-anchor="middle" class="label" transform="rotate(-90, {cx - 45}, {cy + ch/2})">Success rate</text>\n'

    svg += '</svg>'
    return svg


def generate_octonion_masks():
    """Generate SVG showing octonion partial-norm mask strategies."""
    w, h = 800, 500
    svg = svg_header(w, h)

    svg += '  <text x="400" y="30" text-anchor="middle" class="title">Octonion Partial-Norm Masks for Factor Extraction</text>\n'
    svg += '  <text x="400" y="50" text-anchor="middle" class="subtitle">8 coordinates → 254 non-trivial masks → 70 quaternionic slices</text>\n'

    # Draw 8 coordinates as circles in a ring
    cx, cy = 250, 250
    r = 130
    coords = []
    labels = ["e₀", "e₁", "e₂", "e₃", "e₄", "e₅", "e₆", "e₇"]

    for i in range(8):
        angle = -math.pi / 2 + i * 2 * math.pi / 8
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        coords.append((x, y))

    # Draw connections for one quaternionic mask {0,1,2,3}
    mask_indices = [0, 1, 2, 3]
    for i in range(len(mask_indices)):
        for j in range(i + 1, len(mask_indices)):
            x1, y1 = coords[mask_indices[i]]
            x2, y2 = coords[mask_indices[j]]
            svg += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#3498db" stroke-width="2" opacity="0.3"/>\n'

    # Draw another mask {0,4,5,6} in different color
    mask2 = [0, 4, 5, 6]
    for i in range(len(mask2)):
        for j in range(i + 1, len(mask2)):
            x1, y1 = coords[mask2[i]]
            x2, y2 = coords[mask2[j]]
            svg += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#e67e22" stroke-width="2" opacity="0.3"/>\n'

    # Draw coordinate circles
    for i, (x, y) in enumerate(coords):
        color = "#3498db" if i in mask_indices else "#e67e22" if i in mask2 else "#bdc3c7"
        if i in mask_indices and i in mask2:
            color = "#9b59b6"  # overlap
        svg += f'  <circle cx="{x}" cy="{y}" r="22" fill="{color}" opacity="0.2" stroke="{color}" stroke-width="2"/>\n'
        svg += f'  <text x="{x}" y="{y + 5}" text-anchor="middle" fill="{color}" font-size="14" font-weight="bold">{labels[i]}</text>\n'

    # Legend
    svg += '  <text x="430" y="100" class="label" font-weight="bold">Mask Types:</text>\n'

    svg += '  <rect x="430" y="115" width="15" height="15" fill="#3498db" opacity="0.3" stroke="#3498db"/>\n'
    svg += '  <text x="455" y="127" class="label">Mask A: {e₀,e₁,e₂,e₃}</text>\n'

    svg += '  <rect x="430" y="140" width="15" height="15" fill="#e67e22" opacity="0.3" stroke="#e67e22"/>\n'
    svg += '  <text x="455" y="152" class="label">Mask B: {e₀,e₄,e₅,e₆}</text>\n'

    # Statistics
    svg += '  <rect x="430" y="190" width="330" height="200" rx="8" fill="#f8f9fa" stroke="#dee2e6"/>\n'
    svg += '  <text x="595" y="215" text-anchor="middle" style="font: bold 13px sans-serif; fill: #2c3e50;">Mask Statistics</text>\n'

    stats = [
        ("Total non-trivial masks:", "254"),
        ("Size-1 masks:", "8"),
        ("Size-2 masks:", "28"),
        ("Size-3 masks:", "56"),
        ("Size-4 masks (quaternionic):", "70 ★"),
        ("Size-5 masks:", "56"),
        ("Size-6 masks:", "28"),
        ("Size-7 masks:", "8"),
    ]
    for i, (label, value) in enumerate(stats):
        y = 240 + i * 18
        svg += f'  <text x="445" y="{y}" class="small">{label}</text>\n'
        star = " ★" if "★" in value else ""
        v = value.replace(" ★", "")
        color = "#27ae60" if star else "#2c3e50"
        svg += f'  <text x="730" y="{y}" text-anchor="end" style="font: bold 11px sans-serif; fill: {color};">{value}</text>\n'

    # Note
    svg += '  <text x="400" y="470" text-anchor="middle" class="subtitle">★ Size-4 masks correspond to quaternionic sub-algebras where norm is multiplicative</text>\n'

    svg += '</svg>'
    return svg


def generate_complexity_comparison():
    """Generate SVG comparing factoring algorithm complexities."""
    w, h = 800, 450
    svg = svg_header(w, h)

    svg += '  <text x="400" y="30" text-anchor="middle" class="title">Factoring Algorithm Complexity Landscape</text>\n'

    # Chart area
    cx, cy = 120, 70
    cw, ch = 620, 300

    # Algorithms with their complexity class and visual representation
    algorithms = [
        {"name": "Trial Division", "class": "Exponential", "exp": 0.5,
         "color": "#e74c3c", "x_pos": 0.05},
        {"name": "Pollard ρ", "class": "Exponential", "exp": 0.25,
         "color": "#e67e22", "x_pos": 0.15},
        {"name": "Quaternion\nLattice", "class": "Sub-exp?", "exp": 0.33,
         "color": "#9b59b6", "x_pos": 0.35, "highlight": True},
        {"name": "Quadratic\nSieve", "class": "Sub-exponential", "exp": 0.5,
         "color": "#3498db", "x_pos": 0.50},
        {"name": "GNFS", "class": "Sub-exponential", "exp": 0.33,
         "color": "#2ecc71", "x_pos": 0.65},
        {"name": "Shor's\n(Quantum)", "class": "Polynomial", "exp": 0,
         "color": "#1abc9c", "x_pos": 0.85},
    ]

    # Draw bars
    bar_w = 80
    for alg in algorithms:
        x = cx + alg["x_pos"] * cw
        # Height represents relative difficulty (inverted - shorter = faster)
        bar_h = 50 + alg["exp"] * 400
        y = cy + ch - bar_h

        # Bar
        opacity = "0.9" if alg.get("highlight") else "0.7"
        svg += f'  <rect x="{x - bar_w/2}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{alg["color"]}" opacity="{opacity}"/>\n'

        if alg.get("highlight"):
            svg += f'  <rect x="{x - bar_w/2 - 3}" y="{y - 3}" width="{bar_w + 6}" height="{bar_h + 6}" rx="6" fill="none" stroke="{alg["color"]}" stroke-width="2" stroke-dasharray="5,3"/>\n'
            svg += f'  <text x="{x}" y="{y - 15}" text-anchor="middle" style="font: bold 10px sans-serif; fill: {alg["color"]};">This work</text>\n'

        # Label
        lines = alg["name"].split("\n")
        for i, line in enumerate(lines):
            svg += f'  <text x="{x}" y="{cy + ch + 15 + i * 14}" text-anchor="middle" class="label">{line}</text>\n'

        # Complexity class
        svg += f'  <text x="{x}" y="{y + 18}" text-anchor="middle" fill="white" font-size="9" font-weight="bold">{alg["class"]}</text>\n'

    # Axes
    svg += f'  <line x1="{cx - 10}" y1="{cy + ch}" x2="{cx + cw + 10}" y2="{cy + ch}" class="axis" stroke-width="2"/>\n'

    # Y axis label
    svg += f'  <text x="{cx - 60}" y="{cy + ch/2}" text-anchor="middle" class="label" transform="rotate(-90, {cx - 60}, {cy + ch/2})">Relative complexity (log scale)</text>\n'

    # Legend
    svg += f'  <text x="400" y="{cy + ch + 55}" text-anchor="middle" class="subtitle">Quaternion lattice factoring: sub-exponential complexity conjectured but unproven</text>\n'

    svg += '</svg>'
    return svg


# Generate all SVGs
if __name__ == "__main__":
    svgs = {
        "algebra_hierarchy.svg": generate_algebra_hierarchy(),
        "lattice_construction.svg": generate_lattice_construction(),
        "alpha_scaling.svg": generate_alpha_scaling(),
        "octonion_masks.svg": generate_octonion_masks(),
        "complexity_comparison.svg": generate_complexity_comparison(),
    }

    for filename, content in svgs.items():
        with open(filename, "w") as f:
            f.write(content)
        print(f"Generated {filename}")
