#!/usr/bin/env python3
"""Viz 8: Digital Root Mandala - Arrange triples by digital root patterns in a circular mandala."""
import numpy as np
import matplotlib.pyplot as plt
from collections import deque, Counter

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def digital_root(n):
    n = abs(int(n))
    if n == 0:
        return 0
    return 1 + (n - 1) % 9

def generate_triples(depth):
    root = np.array([3, 4, 5])
    triples = [root]
    depths = [0]
    queue = deque([(root, 0)])
    while queue:
        t, d = queue.popleft()
        if d >= depth:
            continue
        for M in MATS:
            child = np.abs(M @ t)
            triples.append(child)
            depths.append(d + 1)
            queue.append((child, d + 1))
    return np.array(triples), np.array(depths)

triples, depths = generate_triples(10)

# Compute digital root patterns (dr(a), dr(b), dr(c))
dr_a = np.array([digital_root(t[0]) for t in triples])
dr_b = np.array([digital_root(t[1]) for t in triples])
dr_c = np.array([digital_root(t[2]) for t in triples])
patterns = [(da, db, dc) for da, db, dc in zip(dr_a, dr_b, dr_c)]
pattern_counts = Counter(patterns)

# --- Image 1: Mandala ---
fig, ax = plt.subplots(figsize=(16, 16), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

# Place triples in concentric rings by depth
max_depth = depths.max()
cmap = plt.cm.twilight_shifted

for d in range(max_depth + 1):
    mask = depths == d
    idx = np.where(mask)[0]
    n_at_depth = len(idx)
    if n_at_depth == 0:
        continue

    # Angle by digital root of a (1-9 -> 0 to 2pi)
    theta_vals = (dr_a[mask] - 1) / 9.0 * 2 * np.pi
    # Add jitter based on b's digital root
    theta_vals += (dr_b[mask] - 1) / 9.0 * (2 * np.pi / 9) * 0.8
    # Further jitter
    theta_vals += np.random.uniform(-0.03, 0.03, n_at_depth)

    r_vals = np.full(n_at_depth, d + 0.5)
    r_vals += np.random.uniform(-0.15, 0.15, n_at_depth)

    # Color by digital root of c
    colors = cmap((dr_c[mask] - 1) / 8.0)

    sizes = np.maximum(2, 25 - d * 2)

    ax.scatter(theta_vals, r_vals, c=colors, s=sizes, alpha=0.7, edgecolors='none')
    # Glow ring
    ax.scatter(theta_vals, r_vals, c=colors, s=sizes * 4, alpha=0.05, edgecolors='none')

# Add radial lines for digital root sectors
for dr in range(1, 10):
    angle = (dr - 1) / 9.0 * 2 * np.pi
    ax.plot([angle, angle], [0, max_depth + 1], color='#444466', linewidth=0.5, alpha=0.5)
    ax.text(angle, max_depth + 1.5, f'dr={dr}', fontsize=9, color='#888',
            ha='center', va='center')

# Concentric depth rings
for d in range(max_depth + 1):
    circle = plt.Circle((0, 0), d + 0.5, transform=ax.transData + ax.transAxes,
                         fill=False, color='#333355', linewidth=0.3)

ax.set_title('Digital Root Mandala\nAngle = dr(a), Ring = Depth, Color = dr(c)',
             fontsize=16, color='white', fontweight='bold', pad=30)
ax.set_rticks([])
ax.set_thetagrids([])
ax.grid(False)

plt.savefig('/home/raver1975/factor/images/viz08_digital_mandala.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Pattern frequency chart ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#0a0a1a')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Top 30 patterns
top = pattern_counts.most_common(30)
labels = [f'({p[0]},{p[1]},{p[2]})' for p, _ in top]
counts = [c for _, c in top]

colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(labels)))
bars = ax1.barh(range(len(labels)), counts, color=colors, edgecolor='none', alpha=0.85)
ax1.set_yticks(range(len(labels)))
ax1.set_yticklabels(labels, fontsize=9, color='white')
ax1.set_xlabel('Count', fontsize=12, color='white')
ax1.set_title('Top 30 Digital Root Patterns (dr_a, dr_b, dr_c)',
              fontsize=13, color='white', fontweight='bold')
ax1.invert_yaxis()

# Digital root distribution for each component
for comp, name, color in [(dr_a, 'a', '#00ffff'), (dr_b, 'b', '#ff00ff'), (dr_c, 'c', '#ffd700')]:
    dr_counts = Counter(comp)
    vals = range(1, 10)
    freqs = [dr_counts.get(v, 0) / len(comp) for v in vals]
    ax2.plot(list(vals), freqs, 'o-', color=color, linewidth=2, markersize=8, label=f'dr({name})')

ax2.axhline(y=1/9, color='#666', linestyle='--', alpha=0.5, label='Uniform (1/9)')
ax2.set_xlabel('Digital Root', fontsize=12, color='white')
ax2.set_ylabel('Frequency', fontsize=12, color='white')
ax2.set_title('Digital Root Frequency by Component',
              fontsize=13, color='white', fontweight='bold')
ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')
ax2.set_xticks(range(1, 10))

fig.suptitle('B3 Pythagorean Triple Digital Root Analysis',
             fontsize=18, color='#ffd700', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz08_digital_root_analysis.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_08: Digital root mandala images saved.")
