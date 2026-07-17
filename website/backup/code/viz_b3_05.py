#!/usr/bin/env python3
"""Viz 5: Coprimality Heatmap - GCD matrix for first 200 hypotenuses."""
import numpy as np
import matplotlib.pyplot as plt
from math import gcd
from collections import deque

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_triples_bfs(depth):
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
    return triples

triples = generate_triples_bfs(7)  # 3^7 = 2187, more than enough
N = min(200, len(triples))
hyps = [int(t[2]) for t in triples[:N]]

# --- Image 1: GCD heatmap ---
gcd_matrix = np.zeros((N, N), dtype=int)
for i in range(N):
    for j in range(N):
        gcd_matrix[i, j] = gcd(hyps[i], hyps[j])

fig, ax = plt.subplots(figsize=(14, 12))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

# Log scale for visibility
log_gcd = np.log2(gcd_matrix.astype(float) + 1)
im = ax.imshow(log_gcd, cmap='inferno', interpolation='nearest')
ax.set_title(f'GCD(c_i, c_j) Heatmap — First {N} Hypotenuses',
             fontsize=16, color='white', fontweight='bold')
ax.set_xlabel('Triple index j', fontsize=13, color='white')
ax.set_ylabel('Triple index i', fontsize=13, color='white')
ax.tick_params(colors='white')
cbar = plt.colorbar(im, ax=ax, label='log2(GCD + 1)')
cbar.ax.yaxis.label.set_color('white')
cbar.ax.tick_params(colors='white')

plt.savefig('/home/raver1975/factor/images/viz05_coprimality_heatmap.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Coprimality fraction by BFS distance ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
fig.patch.set_facecolor('#0a0a1a')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Binary coprimality matrix
coprime_matrix = np.zeros((N, N), dtype=int)
for i in range(N):
    for j in range(N):
        coprime_matrix[i, j] = 1 if gcd(hyps[i], hyps[j]) == 1 else 0

im2 = ax1.imshow(coprime_matrix, cmap='RdYlGn', interpolation='nearest', vmin=0, vmax=1)
ax1.set_title(f'Coprimality Matrix (green=coprime)', fontsize=14, color='white', fontweight='bold')
ax1.set_xlabel('Triple index', fontsize=12, color='white')
ax1.set_ylabel('Triple index', fontsize=12, color='white')

# Coprimality fraction vs index distance
distances = range(1, N)
coprime_fracs = []
for d in distances:
    count = 0
    total = 0
    for i in range(N - d):
        total += 1
        if gcd(hyps[i], hyps[i+d]) == 1:
            count += 1
    coprime_fracs.append(count / total if total > 0 else 0)

ax2.plot(distances, coprime_fracs, color='#00ffff', linewidth=1.5, alpha=0.8)
ax2.axhline(y=6/np.pi**2, color='#ff00ff', linestyle='--', alpha=0.7,
            label=f'6/pi^2 = {6/np.pi**2:.4f} (random)')
ax2.fill_between(distances, coprime_fracs, alpha=0.15, color='cyan')
ax2.set_xlabel('BFS Index Distance', fontsize=12, color='white')
ax2.set_ylabel('Coprimality Fraction', fontsize=12, color='white')
ax2.set_title('Coprimality vs BFS Distance', fontsize=14, color='white', fontweight='bold')
ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')

fig.suptitle('B3 Hypotenuse Coprimality Structure',
             fontsize=18, color='#ffd700', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz05_coprimality_analysis.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_05: Coprimality heatmap images saved.")
