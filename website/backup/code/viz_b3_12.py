#!/usr/bin/env python3
"""viz_b3_12.py — 'Modular Kaleidoscope'
Residue grids mod small primes from the B3 Pythagorean tree.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
from matplotlib.patches import Circle
import os, gc

# B3 Berggren matrices
A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1, 2,2],[2, 1,2],[2, 2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_tree(max_depth=12):
    """Generate B3 tree, return list of (a, b, c)."""
    results = []
    stack = [(np.array([3, 4, 5]), 0)]
    while stack:
        triple, depth = stack.pop()
        t = np.abs(triple)
        results.append((int(t[0]), int(t[1]), int(t[2])))
        if depth < max_depth:
            for M in MATS:
                stack.append((M @ triple, depth + 1))
    return results

print("Generating tree to depth 12...")
triples = generate_tree(12)
print(f"Generated {len(triples)} triples")

OUT = "/home/raver1975/factor/images"
primes = [5, 7, 11, 13]
filenames = ["img_J01.png", "img_J02.png", "img_J03.png", "img_J04.png"]

plt.style.use('dark_background')

for pidx, p in enumerate(primes):
    # Count (a mod p, b mod p) occurrences
    grid = np.zeros((p, p), dtype=int)
    for a, b, c in triples:
        grid[a % p][b % p] += 1

    max_count = grid.max()
    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')

    # Draw faint grid lines
    for i in range(p + 1):
        ax.axhline(i - 0.5, color='gray', alpha=0.15, lw=0.5)
        ax.axvline(i - 0.5, color='gray', alpha=0.15, lw=0.5)

    # Draw circles at each cell
    cmap = plt.cm.hot
    norm = Normalize(vmin=0, vmax=max_count)
    for i in range(p):
        for j in range(p):
            count = grid[i][j]
            if count > 0:
                # Circle size proportional to count
                radius = 0.1 + 0.38 * (count / max_count)
                color = cmap(norm(count))
                circle = Circle((i, j), radius, facecolor=color, edgecolor='white',
                                linewidth=0.3, alpha=0.85)
                ax.add_patch(circle)
                # Add count text for larger circles
                if count > max_count * 0.3:
                    ax.text(i, j, str(count), ha='center', va='center',
                            fontsize=7, color='white', fontweight='bold', alpha=0.9)

    # Add a subtle radial glow at the center
    for r in np.linspace(0, p, 20):
        circle_bg = Circle((p/2 - 0.5, p/2 - 0.5), r, fill=False,
                           edgecolor='cyan', alpha=0.01, lw=0.5)
        ax.add_patch(circle_bg)

    ax.set_xlim(-0.7, p - 0.3)
    ax.set_ylim(-0.7, p - 0.3)
    ax.set_aspect('equal')
    ax.set_xlabel(f"a mod {p}", fontsize=12, color='white')
    ax.set_ylabel(f"b mod {p}", fontsize=12, color='white')
    ax.set_title(f"B3 Kaleidoscope mod {p}", fontsize=16, color='white', pad=15)
    ax.set_xticks(range(p))
    ax.set_yticks(range(p))
    ax.tick_params(colors='white', labelsize=9)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap='hot', norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.05)
    cbar.set_label('Count', color='white', fontsize=11)
    cbar.ax.tick_params(colors='white')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, filenames[pidx]), dpi=150, facecolor='#0a0a1a')
    plt.close()
    gc.collect()
    print(f"Saved {filenames[pidx]} (mod {p})")

print("Done — viz_b3_12.py")
