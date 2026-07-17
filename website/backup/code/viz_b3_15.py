#!/usr/bin/env python3
"""viz_b3_15.py — 'Tree of Life'
Draw the actual B3 ternary tree structure with radial layout.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import deque
import os, gc

# B3 Berggren matrices
A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1, 2,2],[2, 1,2],[2, 2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]
MAT_NAMES = ['A', 'B', 'C']

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def digital_root(n):
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n

class TreeNode:
    def __init__(self, triple, depth, node_id, parent_id=None, branch=None):
        self.triple = triple
        self.a, self.b, self.c = abs(int(triple[0])), abs(int(triple[1])), abs(int(triple[2]))
        self.depth = depth
        self.node_id = node_id
        self.parent_id = parent_id
        self.branch = branch  # 'A', 'B', or 'C'
        self.children = []

def build_tree(max_depth=7):
    """Build tree and return nodes dict."""
    nodes = {}
    nid = 0
    root = TreeNode(np.array([3, 4, 5]), 0, nid)
    nodes[nid] = root
    queue = deque([(root, np.array([3, 4, 5]))])

    while queue:
        parent, triple = queue.popleft()
        if parent.depth >= max_depth:
            continue
        for idx, M in enumerate(MATS):
            nid += 1
            child_triple = M @ triple
            child = TreeNode(child_triple, parent.depth + 1, nid,
                             parent.node_id, MAT_NAMES[idx])
            nodes[nid] = child
            parent.children.append(nid)
            queue.append((child, child_triple))

    return nodes

def radial_layout(nodes, max_depth):
    """Compute radial layout positions."""
    positions = {}
    # Root at center
    positions[0] = (0.0, 0.0)

    # BFS assign angles
    # Each depth level gets a ring; children equally spaced within parent's arc
    def assign_positions(node_id, angle_start, angle_end, depth):
        node = nodes[node_id]
        if depth == 0:
            positions[node_id] = (0.0, 0.0)
        else:
            angle = (angle_start + angle_end) / 2
            radius = depth * 1.5
            positions[node_id] = (radius * np.cos(angle), radius * np.sin(angle))

        children = node.children
        if children:
            arc = angle_end - angle_start
            child_arc = arc / len(children)
            for i, cid in enumerate(children):
                c_start = angle_start + i * child_arc
                c_end = c_start + child_arc
                assign_positions(cid, c_start, c_end, depth + 1)

    assign_positions(0, 0, 2 * np.pi, 0)
    return positions

print("Building tree to depth 7...")
nodes = build_tree(7)
print(f"Total nodes: {len(nodes)}")
positions = radial_layout(nodes, 7)

OUT = "/home/raver1975/factor/images"
plt.style.use('dark_background')

# ── Helper: draw tree ──
def draw_tree(ax, nodes, positions, node_colors, node_sizes, title, cmap_name, clabel):
    ax.set_facecolor('#050510')

    # Draw edges with glow
    for nid, node in nodes.items():
        if node.parent_id is not None:
            x0, y0 = positions[node.parent_id]
            x1, y1 = positions[nid]
            # Glowing edge: multiple overlaid lines
            for lw, alpha in [(3.0, 0.03), (1.5, 0.06), (0.5, 0.15)]:
                ax.plot([x0, x1], [y0, y1], color='white', lw=lw, alpha=alpha,
                        solid_capstyle='round')

    # Draw nodes
    xs = [positions[nid][0] for nid in sorted(nodes.keys())]
    ys = [positions[nid][1] for nid in sorted(nodes.keys())]
    colors = [node_colors[nid] for nid in sorted(nodes.keys())]
    sizes_arr = [node_sizes[nid] for nid in sorted(nodes.keys())]

    sc = ax.scatter(xs, ys, c=colors, cmap=cmap_name, s=sizes_arr,
                    alpha=0.85, edgecolors='white', linewidth=0.2, zorder=5)

    ax.set_aspect('equal')
    ax.set_title(title, fontsize=16, color='white', pad=15)
    ax.axis('off')
    return sc, clabel


# ── Image 1: Color by hypotenuse size ──
fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
fig.patch.set_facecolor('#050510')

hyp_colors = {nid: np.log(node.c + 1) for nid, node in nodes.items()}
node_sizes_hyp = {nid: max(1, 30 - node.depth * 3.5) for nid, node in nodes.items()}

sc, clbl = draw_tree(ax, nodes, positions, hyp_colors, node_sizes_hyp,
                      "Tree of Life — Hypotenuse Magnitude", 'plasma', 'log(c)')
plt.colorbar(sc, ax=ax, shrink=0.5, label='log(c)', pad=0.02)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_M01.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_M01.png")

# ── Image 2: Color by primality of c ──
fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
fig.patch.set_facecolor('#050510')

prime_colors = {nid: (1.0 if is_prime(node.c) else 0.0) for nid, node in nodes.items()}
node_sizes_prime = {}
for nid, node in nodes.items():
    base = max(1, 30 - node.depth * 3.5)
    node_sizes_prime[nid] = base * (2.5 if is_prime(node.c) else 1.0)

sc, clbl = draw_tree(ax, nodes, positions, prime_colors, node_sizes_prime,
                      "Tree of Life — Prime Hypotenuses", 'coolwarm', 'Prime?')
# Custom legend instead of colorbar
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#b40426',
           markersize=10, label='c is prime', linestyle='None'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#3b4cc0',
           markersize=7, label='c is composite', linestyle='None')
]
ax.legend(handles=legend_elements, fontsize=12, loc='upper left',
          framealpha=0.3, facecolor='#050510')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_M02.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_M02.png")

# ── Image 3: Color by digital root of c ──
fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
fig.patch.set_facecolor('#050510')

dr_colors = {nid: digital_root(node.c) for nid, node in nodes.items()}
node_sizes_dr = {nid: max(1, 30 - node.depth * 3.5) for nid, node in nodes.items()}

sc, clbl = draw_tree(ax, nodes, positions, dr_colors, node_sizes_dr,
                      "Tree of Life — Digital Root of Hypotenuse", 'twilight_shifted', 'Digital root')
cbar = plt.colorbar(sc, ax=ax, shrink=0.5, label='Digital root of c', pad=0.02)
cbar.set_ticks(range(1, 10))
plt.tight_layout()
plt.savefig(os.path.join(OUT, "img_M03.png"), dpi=150, facecolor='#050510')
plt.close(); gc.collect()
print("Saved img_M03.png")
print("Done — viz_b3_15.py")
