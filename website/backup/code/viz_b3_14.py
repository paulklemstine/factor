#!/usr/bin/env python3
"""viz_b3_14.py — 'Fibonacci Web'
Explore golden-ratio and Fibonacci structure in Pythagorean triple ratios.
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

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI

# Fibonacci numbers up to a reasonable bound
def fibonacci_set(bound=10**9):
    fibs = []
    a, b = 1, 1
    while a <= bound:
        fibs.append(a)
        a, b = b, a + b
    return np.array(fibs)

FIBS = fibonacci_set()

def fib_distance(n):
    """Minimum distance from n to any Fibonacci number, normalized by n."""
    if n <= 0:
        return 1.0
    dists = np.abs(FIBS - n)
    return float(dists.min()) / max(n, 1)

def generate_tree(max_depth=12):
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

print("Generating tree to depth 12...")
triples = generate_tree(12)
print(f"Generated {len(triples)} triples")

a_arr = np.array([t[0] for t in triples], dtype=float)
b_arr = np.array([t[1] for t in triples], dtype=float)
c_arr = np.array([t[2] for t in triples], dtype=float)
depths = np.array([t[3] for t in triples], dtype=float)

# Ratios
ratio_ab = a_arr / b_arr
ratio_bc = b_arr / c_arr

OUT = "/home/raver1975/factor/images"
plt.style.use('dark_background')

# ── Image 1: (log(a), log(b)) scatter colored by Fibonacci proximity of c ──
# This gives genuine 2D spread since a and b grow at different rates per branch
fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
ax.set_facecolor('#050510')
fig.patch.set_facecolor('#050510')

log_a = np.log10(a_arr + 1)
log_b = np.log10(b_arr + 1)

# Compute Fibonacci proximity score for c (use vectorized approach)
print("Computing Fibonacci distances...")
# Sample to keep computation reasonable
if len(triples) > 100000:
    rng = np.random.default_rng(42)
    idx_sample = rng.choice(len(triples), 100000, replace=False)
else:
    idx_sample = np.arange(len(triples))

log_a_s = log_a[idx_sample]
log_b_s = log_b[idx_sample]
c_s = c_arr[idx_sample]
depths_s = depths[idx_sample]

# For each c, find distance to nearest Fibonacci
fib_dists = np.array([fib_distance(int(c)) for c in c_s])
# Invert: closer to Fibonacci = brighter
fib_score = 1.0 - np.clip(fib_dists * 20, 0, 1)  # scale so dist < 0.05 is "hot"

sizes_s = np.clip(30 / (depths_s + 1)**1.1, 0.3, 30)

# Background: all points in cool blue by depth
sc1 = ax.scatter(log_a_s, log_b_s, c=depths_s, cmap='cool', s=sizes_s * 0.4,
                 alpha=0.25, edgecolors='none', zorder=1)

# Overlay: Fibonacci-hot points
hot_mask = fib_score > 0.3
if hot_mask.any():
    sc2 = ax.scatter(log_a_s[hot_mask], log_b_s[hot_mask], c=fib_score[hot_mask],
                     cmap='hot', s=sizes_s[hot_mask] * 4, alpha=0.85,
                     edgecolors='gold', linewidth=0.2, zorder=3)
    plt.colorbar(sc2, ax=ax, shrink=0.6, label='Fibonacci proximity of c', pad=0.03)

# Golden ratio lines: log(b) = log(a) + log(phi), i.e., b = a*phi
x_range = np.linspace(log_a_s.min(), log_a_s.max(), 100)
for ratio, label, color, ls in [(PHI, r'b = a$\phi$', 'gold', '--'),
                                  (INV_PHI, r'b = a/$\phi$', 'orange', '--'),
                                  (1.0, 'b = a', 'white', ':')]:
    ax.plot(x_range, x_range + np.log10(ratio), color=color, alpha=0.6,
            lw=1.5, linestyle=ls, label=label)

ax.legend(fontsize=11, loc='upper left', framealpha=0.3, facecolor='#0a0a1a')
ax.set_xlabel("log10(a)", fontsize=13, color='white')
ax.set_ylabel("log10(b)", fontsize=13, color='white')
ax.set_title("Fibonacci Web — Leg Space of B3 Triples", fontsize=18, color='white', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_L01.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_L01.png")

# ── Image 2: Dual histogram of a/b and b/c with golden ratio markers ──
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), dpi=150)
fig.patch.set_facecolor('#050510')

# Top: a/b distribution
clip_ab = ratio_ab[ratio_ab < 8]
ax1.set_facecolor('#050510')
n1, bins1, patches1 = ax1.hist(clip_ab, bins=200, color='#4444ff', alpha=0.7,
                                edgecolor='none', density=True)
bin_centers = 0.5 * (bins1[:-1] + bins1[1:])
for i, (bc, patch) in enumerate(zip(bin_centers, patches1)):
    dist_to_phi = min(abs(bc - PHI), abs(bc - INV_PHI), abs(bc - PHI**2))
    warmth = max(0, 1 - dist_to_phi * 2)
    color = plt.cm.hot(warmth * 0.8 + 0.1)
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

for val, label, color in [(PHI, r'$\phi$', 'gold'), (INV_PHI, r'$1/\phi$', 'orange'),
                           (1.0, '1', 'white'), (PHI**2, r'$\phi^2$', '#FFD700')]:
    ax1.axvline(val, color=color, alpha=0.8, lw=2, linestyle='--')
    ax1.text(val, ax1.get_ylim()[1]*0.9, f' {label}', fontsize=12,
             color=color, fontweight='bold')

ax1.set_xlabel("a / b", fontsize=12, color='white')
ax1.set_ylabel("Density", fontsize=12, color='white')
ax1.set_title("Distribution of Leg Ratios a/b", fontsize=14, color='white')

# Bottom: b/c distribution
ax2.set_facecolor('#050510')
n2, bins2, patches2 = ax2.hist(ratio_bc, bins=200, color='#ff4444', alpha=0.7,
                                edgecolor='none', density=True)
bin_centers2 = 0.5 * (bins2[:-1] + bins2[1:])
for i, (bc, patch) in enumerate(zip(bin_centers2, patches2)):
    dist_to_phi = min(abs(bc - INV_PHI), abs(bc - 1/PHI**2))
    warmth = max(0, 1 - dist_to_phi * 4)
    color = plt.cm.inferno(warmth * 0.7 + 0.2)
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

for val, label, color in [(INV_PHI, r'$1/\phi$', 'orange'),
                           (np.sqrt(2)/2, r'$\sqrt{2}/2$', 'cyan'),
                           (1/PHI**2, r'$1/\phi^2$', '#FFD700')]:
    if ratio_bc.min() <= val <= ratio_bc.max():
        ax2.axvline(val, color=color, alpha=0.8, lw=2, linestyle='--')
        ax2.text(val, ax2.get_ylim()[1]*0.9, f' {label}', fontsize=12,
                 color=color, fontweight='bold')

ax2.set_xlabel("b / c", fontsize=12, color='white')
ax2.set_ylabel("Density", fontsize=12, color='white')
ax2.set_title("Distribution of Normalized Leg b/c", fontsize=14, color='white')

plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_L02.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_L02.png")
print("Done — viz_b3_14.py")
