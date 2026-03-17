#!/usr/bin/env python3
"""viz_b3_11.py — 'Mandala of Triples'
Polar-coordinate mandalas from the B3 Pythagorean tree.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
import os, gc

# B3 Berggren matrices
A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1, 2,2],[2, 1,2],[2, 2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_tree(max_depth=10):
    """Generate B3 tree, return list of (a, b, c, depth, branch_path)."""
    results = []
    stack = [(np.array([3, 4, 5]), 0, [])]
    while stack:
        triple, depth, path = stack.pop()
        t = np.abs(triple)
        a, b, c = int(t[0]), int(t[1]), int(t[2])
        results.append((a, b, c, depth, list(path)))
        if depth < max_depth:
            for idx, M in enumerate(MATS):
                child = M @ triple
                stack.append((np.abs(child), depth + 1, path + [idx]))
    return results

print("Generating tree to depth 10...")
triples = generate_tree(10)
print(f"Generated {len(triples)} triples")

# Extract data
depths = np.array([t[3] for t in triples])
a_vals = np.array([t[0] for t in triples], dtype=float)
b_vals = np.array([t[1] for t in triples], dtype=float)
c_vals = np.array([t[2] for t in triples], dtype=float)

# Encode branch path as base-3 number (normalized to [0,1])
def path_to_val(path, max_depth=10):
    if not path:
        return 0.5
    val = 0.0
    for i, p in enumerate(path):
        val += p * (3 ** -(i + 1))
    return val / (1.0 - 3**(-max_depth))

path_vals = np.array([path_to_val(t[4]) for t in triples])

# Marker sizes: larger at shallow depth, smaller deeper
sizes = np.clip(80 / (depths + 1)**1.5, 0.3, 80)

OUT = "/home/raver1975/factor/images"
plt.style.use('dark_background')

# ── Image 1: angle = fractional part of log(c) * golden_ratio * 2pi, radius = depth ──
# Using golden-angle spacing to spread points around the full circle
golden_angle = 2 * np.pi * (1 - 1 / ((1 + np.sqrt(5)) / 2))  # ~137.5 degrees
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': 'polar'}, dpi=150)
# Use log(c) * golden ratio to scatter angles uniformly
theta1 = (np.log(c_vals) * golden_angle * 7) % (2 * np.pi)
r1 = depths.astype(float) + np.random.default_rng(42).uniform(-0.15, 0.15, len(depths))
sc = ax.scatter(theta1, r1, c=path_vals, cmap='twilight_shifted', s=sizes,
                alpha=0.7, edgecolors='none')
ax.set_facecolor('#0a0a1a')
fig.patch.set_facecolor('#0a0a1a')
ax.set_title("Mandala of Triples — Golden Angle Phyllotaxis", fontsize=16, color='white', pad=20)
ax.set_rticks([])
ax.grid(True, alpha=0.1, color='white')
plt.colorbar(sc, ax=ax, shrink=0.6, label='Branch Path (base-3)', pad=0.08)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_I01.png"), dpi=150, facecolor='#0a0a1a')
plt.close(); gc.collect()
print("Saved img_I01.png")

# ── Image 2: angle = arctan(b/a), radius = log(c) ──
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': 'polar'}, dpi=150)
theta2 = np.arctan2(b_vals, a_vals)
r2 = np.log(c_vals + 1)
sc = ax.scatter(theta2, r2, c=path_vals, cmap='twilight_shifted', s=sizes,
                alpha=0.7, edgecolors='none')
ax.set_facecolor('#0a0a1a')
fig.patch.set_facecolor('#0a0a1a')
ax.set_title("Mandala of Triples — Angle of Legs", fontsize=16, color='white', pad=20)
ax.set_rticks([])
ax.grid(True, alpha=0.1, color='white')
plt.colorbar(sc, ax=ax, shrink=0.6, label='Branch Path (base-3)', pad=0.08)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_I02.png"), dpi=150, facecolor='#0a0a1a')
plt.close(); gc.collect()
print("Saved img_I02.png")

# ── Image 3: Full mandala — 3-fold symmetry from A/B/C branches ──
fig, ax = plt.subplots(figsize=(14, 14), subplot_kw={'projection': 'polar'}, dpi=150)

# Separate by first branch taken from root
branch_colors = {0: 'magenta', 1: 'cyan', 2: 'gold'}
for first_branch in [0, 1, 2]:
    mask = np.array([len(t[4]) > 0 and t[4][0] == first_branch for t in triples])
    if not mask.any():
        continue
    # Rotate each branch by 120 degrees to create mandala symmetry
    rotation = first_branch * 2 * np.pi / 3
    theta_m = theta2[mask] + rotation
    r_m = r2[mask]
    d_m = depths[mask]
    s_m = sizes[mask]
    ax.scatter(theta_m, r_m, c=d_m.astype(float), cmap='inferno',
               s=s_m * 0.7, alpha=0.55, edgecolors='none')

# Root node as bright star
ax.scatter([0], [np.log(6)], c='white', s=200, marker='*', zorder=10,
           edgecolors='gold', linewidth=1)

# Subtle ring guides
ring_theta = np.linspace(0, 2*np.pi, 500)
for rd in np.linspace(r2.min(), r2.max(), 12):
    ax.plot(ring_theta, np.full_like(ring_theta, rd), color='white', alpha=0.03, lw=0.5)

# Radial spokes at 120-degree intervals
for angle in [0, 2*np.pi/3, 4*np.pi/3]:
    ax.plot([angle, angle], [0, r2.max()], color='white', alpha=0.08, lw=0.5)

ax.set_facecolor('#050510')
fig.patch.set_facecolor('#050510')
ax.set_title("Mandala Overlay — Three-fold Branch Symmetry", fontsize=16, color='white', pad=20)
ax.set_rticks([])
ax.grid(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_I03.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_I03.png")
print("Done — viz_b3_11.py")
