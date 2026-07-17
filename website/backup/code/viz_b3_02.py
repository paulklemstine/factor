#!/usr/bin/env python3
"""Viz 2: Angular Rose - Polar histogram of arctan(a/b) showing non-uniform density."""
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_triples(depth):
    root = np.array([3, 4, 5])
    triples = [root]
    queue = deque([(root, 0)])
    while queue:
        t, d = queue.popleft()
        if d >= depth:
            continue
        for M in MATS:
            child = np.abs(M @ t)
            triples.append(child)
            queue.append((child, d+1))
    return np.array(triples)

# Generate deep tree
triples = generate_triples(12)
a, b, c = triples[:, 0], triples[:, 1], triples[:, 2]
angles = np.arctan2(a.astype(float), b.astype(float))

# --- Image 1: Polar histogram (rose diagram) ---
fig, axes = plt.subplots(1, 2, figsize=(20, 9), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('#0a0a1a')

for ax_idx, nbins in enumerate([72, 360]):
    ax = axes[ax_idx]
    ax.set_facecolor('#0a0a1a')

    counts, bin_edges = np.histogram(angles, bins=nbins, range=(0, np.pi/2))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Normalize
    counts_norm = counts / counts.max()

    # Color by density
    colors = plt.cm.magma(counts_norm)

    bars = ax.bar(bin_centers, counts_norm, width=(np.pi/2)/nbins,
                  color=colors, alpha=0.85, edgecolor='none')

    # Add glow for peaks
    peak_mask = counts_norm > 0.7
    if peak_mask.any():
        ax.bar(bin_centers[peak_mask], counts_norm[peak_mask],
               width=(np.pi/2)/nbins * 2, color='cyan', alpha=0.15, edgecolor='none')

    ax.set_thetamin(0)
    ax.set_thetamax(90)
    ax.set_theta_offset(0)
    ax.set_title(f'Angular Distribution ({nbins} bins, {len(triples)} triples)',
                 fontsize=13, color='white', fontweight='bold', pad=20)
    ax.tick_params(colors='white')

    # Mark pi/4
    ax.axvline(x=np.pi/4, color='cyan', linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(np.pi/4, ax.get_ylim()[1]*1.05, r'$\pi/4$', color='cyan',
            fontsize=12, ha='center')

fig.suptitle('B3 Angular Rose: arctan(a/b) for Primitive Pythagorean Triples',
             fontsize=18, color='#ff00ff', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz02_angular_rose.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Density heatmap by depth ---
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

# Regenerate with depth tracking
root = np.array([3, 4, 5])
depth_angles = {d: [] for d in range(13)}
queue = deque([(root, 0)])
depth_angles[0].append(np.arctan2(3, 4))
while queue:
    t, d = queue.popleft()
    if d >= 12:
        continue
    for M in MATS:
        child = np.abs(M @ t)
        ang = np.arctan2(float(child[0]), float(child[1]))
        depth_angles[d+1].append(ang)
        queue.append((child, d+1))

# Build heatmap
nbins = 90
heatmap = np.zeros((13, nbins))
for d in range(13):
    if depth_angles[d]:
        counts, _ = np.histogram(depth_angles[d], bins=nbins, range=(0, np.pi/2))
        if counts.max() > 0:
            heatmap[d] = counts / counts.max()

im = ax.imshow(heatmap, aspect='auto', cmap='inferno',
               extent=[0, 90, 12.5, -0.5], interpolation='bilinear')
ax.set_xlabel('Angle (degrees)', fontsize=14, color='white')
ax.set_ylabel('Tree Depth', fontsize=14, color='white')
ax.set_title('Angular Density by Tree Depth', fontsize=16, color='white', fontweight='bold')
ax.axvline(x=45, color='cyan', linewidth=1.5, linestyle='--', alpha=0.7, label=r'$45\degree$')
ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='cyan')
ax.tick_params(colors='white')
plt.colorbar(im, ax=ax, label='Normalized density')
plt.savefig('/home/raver1975/factor/images/viz02_angle_depth_heatmap.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_02: Angular rose images saved.")
