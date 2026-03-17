#!/usr/bin/env python3
"""Viz 7: Factor Tree Overlay - For RSA-like N, show tree paths where gcd(leg, N) > 1."""
import numpy as np
import matplotlib.pyplot as plt
from math import gcd
from collections import deque

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]
MAT_NAMES = ['A', 'B', 'C']

def tree_with_layout(depth):
    root = np.array([3, 4, 5])
    nodes = [(root, 0, 0.5, '', -1)]  # triple, depth, x, path, parent_idx
    queue = deque([(0, 0.5, 0.5)])  # node_idx, x, width

    while queue:
        pidx, x, w = queue.popleft()
        t, d, _, path, _ = nodes[pidx]
        if d >= depth:
            continue
        cw = w / 3.0
        for i, M in enumerate(MATS):
            child = np.abs(M @ t)
            cx = x - w/3 + i * w/3
            cidx = len(nodes)
            nodes.append((child, d+1, cx, path + MAT_NAMES[i], pidx))
            queue.append((cidx, cx, cw))
    return nodes

# Semi-prime targets
targets = [
    (143, "11 x 13"),
    (323, "17 x 19"),
    (1073, "29 x 37"),
    (10403, "101 x 103"),
]

DEPTH = 8
nodes = tree_with_layout(DEPTH)

fig, axes = plt.subplots(2, 2, figsize=(22, 16))
fig.patch.set_facecolor('#0a0a1a')

for ax_idx, (N, label) in enumerate(targets):
    ax = axes[ax_idx // 2][ax_idx % 2]
    ax.set_facecolor('#0a0a1a')

    # Classify each node
    xs, ys = [], []
    hit_xs, hit_ys = [], []
    hit_labels = []
    norm_sizes = []
    hit_sizes = []

    for idx, (triple, d, x, path, pidx) in enumerate(nodes):
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        g_a = gcd(a, N)
        g_b = gcd(b, N)
        g_c = gcd(c, N)

        if g_a > 1 and g_a < N:
            hit_xs.append(x)
            hit_ys.append(-d)
            hit_sizes.append(max(5, 50 - d*4))
            hit_labels.append(f'a={a}\ngcd={g_a}')
        elif g_b > 1 and g_b < N:
            hit_xs.append(x)
            hit_ys.append(-d)
            hit_sizes.append(max(5, 50 - d*4))
            hit_labels.append(f'b={b}\ngcd={g_b}')
        else:
            xs.append(x)
            ys.append(-d)
            norm_sizes.append(max(1, 15 - d*1.5))

    # Draw edges faintly
    for idx in range(1, len(nodes)):
        _, d, x, _, pidx = nodes[idx]
        _, _, px, _, _ = nodes[pidx]
        ax.plot([px, x], [-nodes[pidx][1], -d], color='#222244', linewidth=0.2, alpha=0.3)

    # Normal nodes
    ax.scatter(xs, ys, c='#334466', s=norm_sizes, alpha=0.4, edgecolors='none')

    # Hit nodes - bright glow
    if hit_xs:
        ax.scatter(hit_xs, hit_ys, c='#ff0044', s=[s*4 for s in hit_sizes],
                   alpha=0.15, edgecolors='none')  # glow
        ax.scatter(hit_xs, hit_ys, c='#ff0044', s=hit_sizes,
                   alpha=0.9, edgecolors='white', linewidths=0.5, zorder=5)

        # Annotate first few hits
        for i in range(min(5, len(hit_xs))):
            ax.annotate(hit_labels[i], (hit_xs[i], hit_ys[i]),
                       fontsize=7, color='#ff8888', ha='center', va='bottom',
                       xytext=(0, 8), textcoords='offset points')

    total_hits = len(hit_xs)
    total_nodes = len(nodes)
    ax.set_title(f'N = {N} ({label})\n{total_hits}/{total_nodes} nodes share factor with N',
                 fontsize=13, color='white', fontweight='bold')
    ax.axis('off')

fig.suptitle('B3 Factoring Paths: Tree Nodes Where gcd(leg, N) > 1',
             fontsize=20, color='#ff0044', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('/home/raver1975/factor/images/viz07_factor_overlay.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Hit density by depth ---
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

for N, label in targets:
    depth_hits = {}
    depth_total = {}
    for triple, d, x, path, pidx in nodes:
        depth_total[d] = depth_total.get(d, 0) + 1
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        if (gcd(a, N) > 1 and gcd(a, N) < N) or (gcd(b, N) > 1 and gcd(b, N) < N):
            depth_hits[d] = depth_hits.get(d, 0) + 1

    ds = sorted(depth_total.keys())
    fracs = [depth_hits.get(d, 0) / depth_total[d] for d in ds]
    ax.plot(ds, fracs, 'o-', linewidth=2, markersize=6, alpha=0.8, label=f'N={N} ({label})')

ax.set_xlabel('Tree Depth', fontsize=14, color='white')
ax.set_ylabel('Fraction of Nodes Hitting a Factor', fontsize=14, color='white')
ax.set_title('Factor Hit Rate by Depth in B3 Tree', fontsize=16, color='white', fontweight='bold')
ax.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.1, color='white')

plt.savefig('/home/raver1975/factor/images/viz07_factor_density.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_07: Factor tree overlay images saved.")
