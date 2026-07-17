#!/usr/bin/env python3
"""Viz 6: Eigenvalue Landscape - 3D surface of spectral radius of product matrices."""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import product as iterproduct

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]], dtype=float)
B = np.array([[1,2,2],[2,1,2],[2,2,3]], dtype=float)
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]], dtype=float)
MATS = [A, B, C]
MAT_NAMES = ['A', 'B', 'C']

# --- Image 1: Spectral radius for all paths of depth 1-6 ---
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor('#0a0a1a')

for depth in range(1, 7):
    ax = axes[(depth-1)//3][(depth-1)%3]
    ax.set_facecolor('#0a0a1a')

    # Generate all matrix products of given depth
    paths = list(iterproduct(range(3), repeat=depth))
    spectral_radii = []
    traces = []
    dets = []

    for path in paths:
        M = np.eye(3)
        for idx in path:
            M = M @ MATS[idx]
        eigs = np.abs(np.linalg.eigvals(M))
        spectral_radii.append(np.max(eigs))
        traces.append(np.abs(np.trace(M)))
        dets.append(np.linalg.det(M))

    spectral_radii = np.array(spectral_radii)
    x = np.arange(len(paths))

    # Color by first matrix in path
    colors = [['#00ffff', '#ff00ff', '#ffd700'][p[0]] for p in paths]

    ax.bar(x, spectral_radii, color=colors, alpha=0.7, width=1.0, edgecolor='none')
    ax.set_title(f'Depth {depth} ({len(paths)} paths)', fontsize=12, color='white', fontweight='bold')
    ax.set_ylabel('Spectral Radius', fontsize=10, color='white')
    ax.tick_params(colors='white')
    ax.set_xticks([])
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.suptitle('Spectral Radius of B3 Product Matrices at Each Tree Depth',
             fontsize=18, color='cyan', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('/home/raver1975/factor/images/viz06_spectral_radius_bars.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: 3D surface of eigenvalue magnitudes ---
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor('#0a0a1a')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0a0a1a')

# Parameterize: interpolate between matrices A and B, then A and C
t1 = np.linspace(0, 1, 80)
t2 = np.linspace(0, 1, 80)
T1, T2 = np.meshgrid(t1, t2)

SR = np.zeros_like(T1)
for i in range(len(t1)):
    for j in range(len(t2)):
        # Convex combination: t1*A + (1-t1)*B, then multiply by t2*A + (1-t2)*C
        M1 = t1[i] * A + (1 - t1[i]) * B
        M2 = t2[j] * A + (1 - t2[j]) * C
        M = M1 @ M2
        SR[j, i] = np.max(np.abs(np.linalg.eigvals(M)))

surf = ax.plot_surface(T1, T2, SR, cmap='plasma', alpha=0.85,
                        edgecolor='none', antialiased=True)
ax.set_xlabel('t (A<->B)', fontsize=12, color='white', labelpad=10)
ax.set_ylabel('s (A<->C)', fontsize=12, color='white', labelpad=10)
ax.set_zlabel('Spectral Radius', fontsize=12, color='white', labelpad=10)
ax.set_title('Eigenvalue Landscape: Spectral Radius of Interpolated Products',
             fontsize=14, color='white', fontweight='bold', pad=20)
ax.tick_params(colors='white')
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
fig.colorbar(surf, ax=ax, shrink=0.5, label='Spectral Radius')
plt.savefig('/home/raver1975/factor/images/viz06_eigenvalue_3d.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 3: Trace spiral -- trace of M^k mapped to polar coordinates ---
# The trace encodes the full spectral information: tr(M^k) = sum of eigenvalue^k
# Plotting (k, log(|tr|)) in polar coords reveals the growth rate structure
fig, axes = plt.subplots(1, 2, figsize=(22, 10))
fig.patch.set_facecolor('#0a0a1a')

# Left: trace growth curves
ax = axes[0]
ax.set_facecolor('#0a0a1a')

max_k = 25
for label, mat_seq, color, ls in [
    ('A^k', [0], '#00ffff', '-'),
    ('B^k', [1], '#ff00ff', '-'),
    ('C^k', [2], '#ffd700', '-'),
    ('(AB)^k', [0,1], '#00ff88', '--'),
    ('(AC)^k', [0,2], '#ff8800', '--'),
    ('(BC)^k', [1,2], '#88aaff', '--'),
    ('(ABC)^k', [0,1,2], '#ff4488', ':'),
]:
    # Build the base product matrix
    M_base = np.eye(3)
    for idx in mat_seq:
        M_base = M_base @ MATS[idx]

    traces = []
    dets = []
    M = np.eye(3)
    for k in range(1, max_k + 1):
        M = M @ M_base
        traces.append(abs(np.trace(M)))
        dets.append(abs(np.linalg.det(M)))

    ks = np.arange(1, max_k + 1)
    ax.semilogy(ks, traces, color=color, linewidth=2.5, alpha=0.8, label=label, linestyle=ls)
    # Glow
    ax.fill_between(ks, [t*0.8 for t in traces], [t*1.2 for t in traces],
                    color=color, alpha=0.05)

ax.set_xlabel('Power k', fontsize=14, color='white')
ax.set_ylabel('|Trace(M^k)|', fontsize=14, color='white')
ax.set_title('Trace Growth: |tr(M^k)| vs k', fontsize=15, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white',
          loc='upper left', ncol=2)
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.08, color='white')

# Right: Lyapunov exponents (growth rate of eigenvalues)
ax = axes[1]
ax.set_facecolor('#0a0a1a')

# For each product, compute Lyapunov exponent = lim (1/k) * log(spectral_radius(M^k))
products = [
    ('A', [0]), ('B', [1]), ('C', [2]),
    ('AB', [0,1]), ('AC', [0,2]), ('BC', [1,2]),
    ('ABC', [0,1,2]), ('ACB', [0,2,1]), ('BAC', [1,0,2]),
    ('AAB', [0,0,1]), ('ABB', [0,1,1]), ('AAC', [0,0,2]),
    ('BCC', [1,2,2]), ('ACC', [0,2,2]), ('BBC', [1,1,2]),
]
lyap_labels = []
lyap_values = []
lyap_colors = []

color_map = {1: '#00ffff', 2: '#ff00ff', 3: '#ffd700'}
for name, seq in products:
    M_base = np.eye(3)
    for idx in seq:
        M_base = M_base @ MATS[idx]
    # Lyapunov = log of spectral radius of base product
    sr = np.max(np.abs(np.linalg.eigvals(M_base)))
    lyap = np.log(sr) / len(seq)  # per-step Lyapunov
    lyap_labels.append(name)
    lyap_values.append(lyap)
    lyap_colors.append(color_map.get(len(seq), '#888888'))

# Sort by Lyapunov exponent
order = np.argsort(lyap_values)[::-1]
lyap_labels = [lyap_labels[i] for i in order]
lyap_values = [lyap_values[i] for i in order]
lyap_colors = [lyap_colors[i] for i in order]

bars = ax.barh(range(len(lyap_labels)), lyap_values, color=lyap_colors, alpha=0.85,
               edgecolor='white', linewidth=0.3)
ax.set_yticks(range(len(lyap_labels)))
ax.set_yticklabels(lyap_labels, fontsize=11, color='white', fontfamily='monospace')
ax.set_xlabel('Lyapunov Exponent (per step)', fontsize=13, color='white')
ax.set_title('Per-Step Lyapunov Exponents\nlog(spectral_radius) / path_length',
             fontsize=15, color='white', fontweight='bold')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()
ax.grid(True, alpha=0.08, color='white', axis='x')

# Annotate values
for i, (v, lbl) in enumerate(zip(lyap_values, lyap_labels)):
    ax.text(v + 0.01, i, f'{v:.4f}', va='center', fontsize=9, color='white')

fig.suptitle('B3 Spectral Analysis: Trace Growth and Lyapunov Exponents',
             fontsize=18, color='cyan', fontweight='bold', y=1.02)
plt.tight_layout()

plt.savefig('/home/raver1975/factor/images/viz06_eigenvalue_complex.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_06: Eigenvalue landscape images saved.")
