#!/usr/bin/env python3
"""Viz 3: Modular Orbits - Show orbit structure of B3 tree mod p as directed graphs."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from collections import deque

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]
MAT_COLORS = ['#00ffff', '#ff00ff', '#ffd700']
MAT_NAMES = ['A', 'B', 'C']

# --- Image 1: a-value orbit graphs for 4 primes ---
primes = [5, 7, 11, 13]
fig, axes = plt.subplots(2, 2, figsize=(20, 20))
fig.patch.set_facecolor('#0a0a1a')

for idx, p in enumerate(primes):
    ax = axes[idx//2][idx%2]
    ax.set_facecolor('#0a0a1a')

    G = nx.MultiDiGraph()
    for a in range(p):
        G.add_node(a)

    # BFS from root (3,4,5) to discover all a-value transitions mod p
    root = np.array([3, 4, 5])
    seen_edges = set()
    queue = deque([(root, 0)])
    visited_triples = set()
    visited_triples.add(tuple(root % p))

    while queue:
        t, d = queue.popleft()
        if d >= 10:
            continue
        for mi, M in enumerate(MATS):
            child = np.abs(M @ t)
            a_from = int(t[0]) % p
            a_to = int(child[0]) % p
            edge_key = (a_from, a_to, mi)
            if edge_key not in seen_edges:
                G.add_edge(a_from, a_to, mat=mi)
                seen_edges.add(edge_key)
            tup = tuple(child % p)
            if tup not in visited_triples:
                visited_triples.add(tup)
                queue.append((child, d+1))

    # Layout
    pos = nx.circular_layout(G)

    # Draw edges by matrix type with different curvatures
    for mi in range(3):
        edges_mi = [(u, v) for u, v, d in G.edges(data=True) if d.get('mat') == mi]
        if edges_mi:
            nx.draw_networkx_edges(G, pos, edgelist=edges_mi, ax=ax,
                                   edge_color=MAT_COLORS[mi], alpha=0.6,
                                   width=2.0, arrows=True, arrowsize=18,
                                   connectionstyle=f'arc3,rad={0.08 + mi*0.18}',
                                   min_source_margin=15, min_target_margin=15)

    # Draw nodes
    node_colors = ['#1a1a4e'] * p
    # Highlight root residue
    root_res = 3 % p
    node_colors[root_res] = '#003355'
    node_sizes = [900 if n == root_res else 600 for n in range(p)]
    node_edge_colors = ['#00ff88' if n == root_res else 'cyan' for n in range(p)]

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, edgecolors=node_edge_colors, linewidths=2.5)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color='white', font_size=13, font_weight='bold')

    n_edges = len(seen_edges)
    ax.set_title(f'a-value Orbits mod {p}\n{p} nodes, {n_edges} edges',
                 fontsize=15, color='white', fontweight='bold')

# Legend
patches = [mpatches.Patch(color=MAT_COLORS[i], label=f'Matrix {MAT_NAMES[i]}') for i in range(3)]
patches.append(mpatches.Patch(color='#00ff88', label='Root residue (a=3 mod p)'))
fig.legend(handles=patches, loc='lower center', ncol=4, fontsize=13,
           facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')

fig.suptitle('B3 Modular Orbit Structure: a-value Transitions mod p',
             fontsize=20, color='cyan', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.05, 1, 0.96])
plt.savefig('/home/raver1975/factor/images/viz03_modular_orbits.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Full triple orbit graph for p=5 ---
p = 5
fig, ax = plt.subplots(figsize=(18, 18))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

G2 = nx.DiGraph()
# Find all Pythagorean triples mod p
pyth_triples = set()
for aa in range(p):
    for bb in range(p):
        cc_sq = (aa*aa + bb*bb) % p
        for cc in range(p):
            if (cc*cc) % p == cc_sq:
                pyth_triples.add((aa, bb, cc))

for t in pyth_triples:
    G2.add_node(t)
    for mi, M in enumerate(MATS):
        v = np.array(t)
        child = tuple(int(x) % p for x in M @ v)
        if child in pyth_triples:
            G2.add_edge(t, child)

pos2 = nx.spring_layout(G2, k=3.0, iterations=150, seed=42)

# Color nodes by hypotenuse residue
c_vals = [t[2] for t in G2.nodes()]
cmap = plt.cm.plasma
norm = plt.Normalize(0, p-1)
node_colors = [cmap(norm(c)) for c in c_vals]

# Highlight root (3,4,5) mod 5 = (3,4,0)
root_mod = (3 % p, 4 % p, 5 % p)
node_sizes = [400 if n == root_mod else 150 for n in G2.nodes()]
edge_widths = [3 if n == root_mod else 0.5 for n in G2.nodes()]

nx.draw_networkx_edges(G2, pos2, ax=ax, edge_color='#333366', alpha=0.25,
                       width=0.5, arrows=True, arrowsize=8)
nx.draw_networkx_nodes(G2, pos2, ax=ax, node_color=node_colors,
                       node_size=node_sizes, edgecolors='white', linewidths=edge_widths)

# Label a few nodes
labels = {}
for n in G2.nodes():
    if n == root_mod or G2.degree(n) > 4:
        labels[n] = f'{n}'
nx.draw_networkx_labels(G2, pos2, labels, ax=ax, font_color='white', font_size=7)

ax.set_title(f'Full Pythagorean Triple Orbits mod {p}\n{len(pyth_triples)} triples, {G2.number_of_edges()} edges',
             fontsize=16, color='white', fontweight='bold')
ax.axis('off')
plt.savefig('/home/raver1975/factor/images/viz03_full_orbit_mod5.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 3: Orbit cycle structure for p=7 and p=13 ---
fig, axes = plt.subplots(1, 2, figsize=(22, 10))
fig.patch.set_facecolor('#0a0a1a')

for ax_idx, p in enumerate([7, 13]):
    ax = axes[ax_idx]
    ax.set_facecolor('#0a0a1a')

    # Track full (a,b,c) mod p orbits under each matrix
    for mi, (M, color, name) in enumerate(zip(MATS, MAT_COLORS, MAT_NAMES)):
        # Find cycle lengths starting from various triples
        cycle_lengths = []
        for aa in range(p):
            for bb in range(p):
                cc_sq = (aa*aa + bb*bb) % p
                for cc in range(p):
                    if (cc*cc) % p == cc_sq:
                        # Apply M repeatedly until we return
                        start = np.array([aa, bb, cc])
                        current = start.copy()
                        for step in range(1, 2*p*p + 1):
                            current = np.array([int(x) % p for x in M @ current])
                            if np.array_equal(current, start):
                                cycle_lengths.append(step)
                                break

        if cycle_lengths:
            from collections import Counter
            counts = Counter(cycle_lengths)
            lengths = sorted(counts.keys())
            freqs = [counts[l] for l in lengths]
            ax.bar([l + mi*0.25 for l in lengths], freqs, width=0.22,
                   color=color, alpha=0.8, label=f'Matrix {name}', edgecolor='none')

    ax.set_xlabel('Cycle Length', fontsize=13, color='white')
    ax.set_ylabel('Number of Triples', fontsize=13, color='white')
    ax.set_title(f'Cycle Structure mod {p}', fontsize=15, color='white', fontweight='bold')
    ax.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.suptitle('B3 Cycle Structure: How Many Steps to Return mod p',
             fontsize=18, color='#ffd700', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz03_cycle_structure.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_03: Modular orbit images saved.")
