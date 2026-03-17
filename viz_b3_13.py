#!/usr/bin/env python3
"""viz_b3_13.py — 'Spiral Galaxy'
Pythagorean triples mapped to the complex plane.
Since a^2+b^2=c^2, z=(a+bi)/c lies ON the unit circle.
We exploit the angular distribution and use alternative mappings for interior views.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import os, gc

# B3 Berggren matrices
A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1, 2,2],[2, 1,2],[2, 2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_tree(max_depth=11):
    results = []
    stack = [(np.array([3, 4, 5]), 0, [])]
    while stack:
        triple, depth, path = stack.pop()
        t = np.abs(triple)
        results.append((int(t[0]), int(t[1]), int(t[2]), depth, list(path)))
        if depth < max_depth:
            for idx, M in enumerate(MATS):
                stack.append((M @ triple, depth + 1, path + [idx]))
    return results

print("Generating tree to depth 11...")
triples = generate_tree(11)
print(f"Generated {len(triples)} triples")

a_vals = np.array([t[0] for t in triples], dtype=float)
b_vals = np.array([t[1] for t in triples], dtype=float)
c_vals = np.array([t[2] for t in triples], dtype=float)
depths = np.array([t[3] for t in triples], dtype=float)

# angle on the unit circle: theta = arctan(b/a) = arctan2(b, a)
theta = np.arctan2(b_vals, a_vals)  # in [0, pi/2] for positive a,b

# Branch path encoding
def path_to_val(path, max_depth=11):
    if not path:
        return 0.5
    val = 0.0
    for i, p in enumerate(path):
        val += p * (3 ** -(i + 1))
    return val / 0.5  # normalize roughly to [0,1]

path_vals = np.array([min(1.0, path_to_val(t[4])) for t in triples])
sizes = np.clip(50 / (depths + 1)**1.3, 0.3, 50)

OUT = "/home/raver1975/factor/images"
plt.style.use('dark_background')

# ── Image 1: Spiral — map (theta, depth) in polar, creating a true spiral galaxy ──
fig, ax = plt.subplots(figsize=(13, 13), subplot_kw={'projection': 'polar'}, dpi=150)
ax.set_facecolor('#050510')
fig.patch.set_facecolor('#050510')

# Each depth level is a ring; angle = arctan(b/a) spreads in [0, pi/2]
# Mirror to fill full circle: use 4-fold symmetry (quadrants)
rng = np.random.default_rng(42)
jitter = rng.uniform(-0.12, 0.12, len(depths))

# Map theta from [0,pi/2] to [0,2pi] using the full angle info
# Add spiral twist: rotate each depth ring by golden angle
golden_angle = 2.3999632  # 137.508 degrees in radians
theta_spiral = theta * 4 + depths * golden_angle  # 4x stretch + spiral twist
r_spiral = depths + jitter

sc = ax.scatter(theta_spiral, r_spiral, c=path_vals, cmap='plasma',
                s=sizes, alpha=0.75, edgecolors='none')

# Concentric ring guides
ring_t = np.linspace(0, 2*np.pi, 500)
for d in range(12):
    ax.plot(ring_t, np.full_like(ring_t, d), color='white', alpha=0.03, lw=0.5)

ax.set_rticks([])
ax.grid(False)
ax.set_title("Spiral Galaxy — Golden-Angle Twist", fontsize=18, color='white', pad=20)
plt.colorbar(sc, ax=ax, shrink=0.55, label='Branch Path', pad=0.08)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_K01.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_K01.png")

# ── Image 2: Poincare disk — map each triple into the disk via z = r_d * e^{i*theta} ──
#    where r_d = 1 - 1/(depth+2), so deeper nodes approach the boundary
fig, ax = plt.subplots(figsize=(13, 13), dpi=150)
ax.set_facecolor('#050510')
fig.patch.set_facecolor('#050510')

r_poincare = 1.0 - 1.0 / (depths + 2)  # 0 -> 0.5, 1 -> 0.67, ... 11 -> 0.923
x_poinc = r_poincare * np.cos(theta * 4 + depths * golden_angle * 0.3)
y_poinc = r_poincare * np.sin(theta * 4 + depths * golden_angle * 0.3)

# Density heatmap
hb = ax.hist2d(x_poinc, y_poinc, bins=500, cmap='inferno',
               norm=LogNorm(vmin=1), range=[[-1.05, 1.05], [-1.05, 1.05]])
plt.colorbar(hb[3], ax=ax, shrink=0.65, label='Point Density', pad=0.03)

# Overlay shallow nodes as bright stars
for d in range(5):
    mask = depths == d
    ax.scatter(x_poinc[mask], y_poinc[mask], c='white', s=max(2, 30 - d*6),
               alpha=max(0.3, 1.0 - d*0.15), edgecolors='cyan',
               linewidth=0.3, zorder=5)

# Unit circle boundary with glow
circ_t = np.linspace(0, 2*np.pi, 1000)
for r_off, alpha_v, lw in [(0, 0.8, 1.5), (0.004, 0.3, 3), (0.01, 0.1, 5)]:
    ax.plot((1+r_off)*np.cos(circ_t), (1+r_off)*np.sin(circ_t),
            color='cyan', alpha=alpha_v, lw=lw)

ax.set_xlim(-1.15, 1.15)
ax.set_ylim(-1.15, 1.15)
ax.set_aspect('equal')
ax.set_title("Poincare Disk Model of the B3 Tree", fontsize=18, color='white', pad=15)
ax.set_xlabel("x", fontsize=12, color='white')
ax.set_ylabel("y", fontsize=12, color='white')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_K02.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_K02.png")

# ── Image 3: Angular spectrum — theta distribution per depth as heatmap + histogram ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), dpi=150,
                                gridspec_kw={'width_ratios': [2, 1]})
fig.patch.set_facecolor('#050510')

# Left: 2D histogram of (theta_degrees, depth)
theta_deg = np.degrees(theta)
ax1.set_facecolor('#050510')
hb = ax1.hist2d(theta_deg, depths, bins=[300, 12], cmap='plasma',
                norm=LogNorm(vmin=1), range=[[0, 90], [-0.5, 11.5]])
plt.colorbar(hb[3], ax=ax1, shrink=0.8, label='Count', pad=0.03)

# Highlight special angles
for angle, label, color in [(np.degrees(np.arctan(3/4)), '(3,4,5)', 'cyan'),
                              (np.degrees(np.arctan(5/12)), '(5,12,13)', 'gold'),
                              (45, '45 deg', 'white')]:
    ax1.axvline(angle, color=color, alpha=0.5, lw=1.5, linestyle='--')
    ax1.text(angle + 0.5, 10.5, label, fontsize=9, color=color, rotation=90, va='top')

ax1.set_xlabel(r"$\theta = \arctan(b/a)$ (degrees)", fontsize=13, color='white')
ax1.set_ylabel("Tree Depth", fontsize=13, color='white')
ax1.set_title("Angular Spectrum by Depth", fontsize=16, color='white')

# Right: stacked histogram of theta per depth
ax2.set_facecolor('#050510')
depth_groups = [theta_deg[depths == d] for d in range(12)]
colors_list = plt.cm.plasma(np.linspace(0.1, 0.9, 12))
ax2.hist(depth_groups, bins=90, stacked=True, color=colors_list,
         alpha=0.8, edgecolor='none', range=(0, 90))
ax2.set_xlabel(r"$\theta$ (degrees)", fontsize=12, color='white')
ax2.set_ylabel("Count (stacked)", fontsize=12, color='white')
ax2.set_title("Angle Distribution", fontsize=14, color='white')

plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_K03.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_K03.png")
print("Done — viz_b3_13.py")
