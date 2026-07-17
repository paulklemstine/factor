#!/usr/bin/env python3
"""Viz 4: Hypotenuse Spiral - Plot hypotenuses on logarithmic spiral, color by branch."""
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_with_branches(depth):
    root = np.array([3, 4, 5])
    results = [(root, -1, 0)]  # triple, first_branch, depth
    queue = deque([(root, 0, -1)])
    while queue:
        t, d, fb = queue.popleft()
        if d >= depth:
            continue
        for i, M in enumerate(MATS):
            child = np.abs(M @ t)
            branch = i if fb == -1 else fb
            results.append((child, branch, d+1))
            queue.append((child, d+1, branch))
    return results

data = generate_with_branches(10)
hyps = np.array([d[0][2] for d in data], dtype=float)
branches = np.array([d[1] for d in data])
ddepths = np.array([d[2] for d in data])

# --- Image 1: Logarithmic spiral ---
fig, ax = plt.subplots(figsize=(16, 16), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

# Sort by hypotenuse for spiral ordering
order = np.argsort(hyps)
sorted_hyps = hyps[order]
sorted_branches = branches[order]

# Map to polar coordinates
theta = np.linspace(0, 12*np.pi, len(sorted_hyps))
r = np.log(sorted_hyps + 1)

branch_colors_map = {-1: '#ffffff', 0: '#00ffff', 1: '#ff00ff', 2: '#ffd700'}
colors = [branch_colors_map[b] for b in sorted_branches]

ax.scatter(theta, r, c=colors, s=3, alpha=0.7, edgecolors='none')

# Add glow trail
for b, col in [(0, '#00ffff'), (1, '#ff00ff'), (2, '#ffd700')]:
    mask = sorted_branches == b
    ax.scatter(theta[mask], r[mask], c=col, s=15, alpha=0.08, edgecolors='none')

ax.set_title('Hypotenuse Logarithmic Spiral\nColor by First Branch (A/B/C)',
             fontsize=16, color='white', fontweight='bold', pad=20)
ax.tick_params(colors='#666')
plt.savefig('/home/raver1975/factor/images/viz04_hypotenuse_spiral.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Hypotenuse growth by depth ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.patch.set_facecolor('#0a0a1a')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Left: log(c) vs depth
for b, col, name in [(0, '#00ffff', 'A'), (1, '#ff00ff', 'B'), (2, '#ffd700', 'C')]:
    mask = branches == b
    ax1.scatter(ddepths[mask] + np.random.uniform(-0.15, 0.15, mask.sum()),
                np.log10(hyps[mask]), c=col, s=8, alpha=0.3, label=f'Branch {name}')

ax1.set_xlabel('Tree Depth', fontsize=13, color='white')
ax1.set_ylabel('log10(hypotenuse)', fontsize=13, color='white')
ax1.set_title('Hypotenuse Growth by Depth', fontsize=15, color='white', fontweight='bold')
ax1.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')

# Right: distribution of hypotenuses at fixed depth
for d in [5, 7, 9]:
    mask = ddepths == d
    if mask.sum() > 0:
        log_h = np.log10(hyps[mask])
        ax2.hist(log_h, bins=40, alpha=0.5, label=f'Depth {d}',
                 edgecolor='none', density=True)

ax2.set_xlabel('log10(hypotenuse)', fontsize=13, color='white')
ax2.set_ylabel('Density', fontsize=13, color='white')
ax2.set_title('Hypotenuse Distribution at Fixed Depths', fontsize=15, color='white', fontweight='bold')
ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')

fig.suptitle('B3 Pythagorean Tree: Hypotenuse Growth Patterns',
             fontsize=18, color='cyan', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz04_hypotenuse_growth.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_04: Hypotenuse spiral images saved.")
