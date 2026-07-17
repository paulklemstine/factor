#!/usr/bin/env python3
"""Viz 1: B3 Tree Fractal - Draw the Berggren tree to depth 8-10, color by (a mod p)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import deque

# Berggren matrices acting on (a, b, c) triples
A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]
MAT_NAMES = ['A', 'B', 'C']

def generate_tree(depth):
    """BFS generation of Pythagorean triples to given depth."""
    root = np.array([3, 4, 5])
    triples = []
    paths = []
    queue = deque()
    queue.append((root, 0, '', 0.5, 0))  # triple, depth, path, x, parent_idx
    triples.append(root)
    paths.append('')

    while queue:
        triple, d, path, x, pidx = queue.popleft()
        if d >= depth:
            continue
        for i, M in enumerate(MATS):
            child = M @ triple
            child = np.abs(child)  # ensure positive
            idx = len(triples)
            triples.append(child)
            paths.append(path + MAT_NAMES[i])
            queue.append((child, d+1, path + MAT_NAMES[i], x, idx))

    return np.array(triples), paths

def tree_layout(depth):
    """Compute tree layout positions using BFS."""
    root = np.array([3, 4, 5])
    positions = []
    triples_out = []
    depths_out = []
    branches = []  # 0=A, 1=B, 2=C for first move

    queue = deque()
    queue.append((root, 0, 0.5, 0.5, -1))  # triple, depth, x, width, first_branch

    while queue:
        triple, d, x, w, fb = queue.popleft()
        positions.append((x, -d))
        triples_out.append(triple)
        depths_out.append(d)
        branches.append(fb)

        if d >= depth:
            continue
        cw = w / 3.0
        for i, M in enumerate(MATS):
            child = M @ triple
            child = np.abs(child)
            cx = x - w/3 + i * w/3
            branch = i if fb == -1 else fb
            queue.append((child, d+1, cx, cw, branch))

    return np.array(triples_out), np.array(positions), np.array(depths_out), np.array(branches)

# Generate tree
DEPTH = 8
triples, positions, depths, branches = tree_layout(DEPTH)

primes_to_show = [3, 5, 7, 11]

fig, axes = plt.subplots(2, 2, figsize=(20, 16))
plt.style.use('dark_background')
fig.patch.set_facecolor('#0a0a1a')

for ax_idx, p in enumerate(primes_to_show):
    ax = axes[ax_idx // 2][ax_idx % 2]
    ax.set_facecolor('#0a0a1a')

    # Color by a mod p
    a_vals = triples[:, 0]
    colors = a_vals % p

    cmap = plt.cm.plasma
    norm = mcolors.Normalize(vmin=0, vmax=p-1)

    # Draw edges (parent to children)
    for i in range(len(positions)):
        d = depths[i]
        if d == 0:
            continue
        # Find parent: index (i-1)//3 approximately
        # Actually, BFS order: parent of node i is at index (i-1)//3
        pidx = (i - 1) // 3
        if pidx >= 0 and pidx < len(positions):
            ax.plot([positions[pidx][0], positions[i][0]],
                    [positions[pidx][1], positions[i][1]],
                    color=cmap(norm(colors[i])), alpha=0.15, linewidth=0.3)

    # Draw nodes
    sizes = np.maximum(1, 30 - depths * 3.5)
    sc = ax.scatter(positions[:, 0], positions[:, 1],
                    c=colors, cmap='plasma', s=sizes,
                    edgecolors='none', alpha=0.85, vmin=0, vmax=p-1)

    ax.set_title(f'Berggren Tree (depth {DEPTH}), colored by a mod {p}',
                 fontsize=14, color='white', fontweight='bold')
    ax.set_xlim(-0.1, 1.1)
    ax.axis('off')
    plt.colorbar(sc, ax=ax, label=f'a mod {p}', shrink=0.7)

fig.suptitle('B3 Pythagorean Triple Tree — Fractal Modular Structure',
             fontsize=20, color='cyan', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('/home/raver1975/factor/images/viz01_tree_fractal.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# Second image: color by branch (A/B/C) with glow effect
fig, ax = plt.subplots(figsize=(16, 12))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

branch_colors = {-1: '#ffffff', 0: '#00ffff', 1: '#ff00ff', 2: '#ffd700'}
branch_labels = {-1: 'Root', 0: 'Branch A', 1: 'Branch B', 2: 'Branch C'}

for b in [-1, 0, 1, 2]:
    mask = branches == b
    sizes = np.maximum(2, 40 - depths[mask] * 4)
    ax.scatter(positions[mask, 0], positions[mask, 1],
               c=branch_colors[b], s=sizes, alpha=0.8,
               edgecolors='none', label=branch_labels[b])
    # Glow layer
    ax.scatter(positions[mask, 0], positions[mask, 1],
               c=branch_colors[b], s=sizes*3, alpha=0.1, edgecolors='none')

# Draw edges
for i in range(1, len(positions)):
    pidx = (i - 1) // 3
    if pidx < len(positions):
        b = branches[i]
        ax.plot([positions[pidx][0], positions[i][0]],
                [positions[pidx][1], positions[i][1]],
                color=branch_colors.get(b, '#333'), alpha=0.1, linewidth=0.3)

ax.legend(fontsize=12, loc='lower right', facecolor='#1a1a2e', edgecolor='cyan')
ax.set_title(f'Berggren Tree to Depth {DEPTH} — Branch Coloring',
             fontsize=18, color='white', fontweight='bold')
ax.axis('off')
plt.savefig('/home/raver1975/factor/images/viz01_tree_branches.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_01: Tree fractal images saved.")
