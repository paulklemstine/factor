#!/usr/bin/env python3
"""Viz 10: Galois Period Bifurcation - ord(B3 mod p) vs p, colored by Legendre symbol (2/p)."""
import numpy as np
import matplotlib.pyplot as plt

def matrix_mod(M, p):
    return M % p

def matrix_mul_mod(A, B, p):
    n = A.shape[0]
    C = np.zeros_like(A)
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += int(A[i, k]) * int(B[k, j])
            C[i, j] = s % p
    return C

def matrix_order(M, p):
    """Find order of matrix M in GL(n, F_p)."""
    n = M.shape[0]
    I = np.eye(n, dtype=int) % p
    current = M.copy() % p
    for k in range(1, 4 * p * p + 2):
        if np.array_equal(current, I):
            return k
        current = matrix_mul_mod(current, M, p)
    return -1  # didn't find order

def legendre_symbol(a, p):
    """Compute (a/p) Legendre symbol."""
    if a % p == 0:
        return 0
    val = pow(a, (p - 1) // 2, p)
    return val if val <= 1 else val - p

# Berggren matrices
MA = np.array([[1,-2,2],[2,-1,2],[2,-2,3]], dtype=int)
MB = np.array([[1,2,2],[2,1,2],[2,2,3]], dtype=int)
MC = np.array([[-1,2,2],[-2,1,2],[-2,2,3]], dtype=int)

# Compute for odd primes up to 200
primes = []
for n in range(3, 200, 2):
    if all(n % i != 0 for i in range(2, int(n**0.5) + 1)):
        primes.append(n)

print(f"Computing orders for {len(primes)} primes...")

results = {name: {'p': [], 'ord': [], 'leg': []} for name in ['A', 'B', 'C']}

for p in primes:
    leg = legendre_symbol(2, p)
    for name, M in [('A', MA), ('B', MB), ('C', MC)]:
        Mmod = M.copy()
        # Make all entries positive mod p
        Mmod = Mmod % p
        o = matrix_order(Mmod, p)
        results[name]['p'].append(p)
        results[name]['ord'].append(o)
        results[name]['leg'].append(leg)

print("Orders computed.")

# --- Image 1: Bifurcation diagram ---
fig, axes = plt.subplots(3, 1, figsize=(18, 16), sharex=True)
fig.patch.set_facecolor('#0a0a1a')

colors_leg = {1: '#00ffff', -1: '#ff00ff', 0: '#ffd700'}
labels_leg = {1: '(2/p) = +1', -1: '(2/p) = -1', 0: '(2/p) = 0'}

for idx, (name, M) in enumerate([('A', MA), ('B', MB), ('C', MC)]):
    ax = axes[idx]
    ax.set_facecolor('#0a0a1a')

    ps = np.array(results[name]['p'])
    ords = np.array(results[name]['ord'])
    legs = np.array(results[name]['leg'])

    for leg_val in [1, -1]:
        mask = legs == leg_val
        ax.scatter(ps[mask], ords[mask], c=colors_leg[leg_val], s=60, alpha=0.85,
                   edgecolors='white', linewidths=0.3, label=labels_leg[leg_val], zorder=5)
        # Glow
        ax.scatter(ps[mask], ords[mask], c=colors_leg[leg_val], s=200, alpha=0.1,
                   edgecolors='none')

    # Reference lines: p-1, p+1, 2(p+1), 2(p-1)
    p_range = np.linspace(3, max(primes), 200)
    ax.plot(p_range, p_range - 1, '--', color='#00ff88', alpha=0.3, linewidth=1, label='p-1')
    ax.plot(p_range, p_range + 1, '--', color='#ff8800', alpha=0.3, linewidth=1, label='p+1')
    ax.plot(p_range, 2*(p_range + 1), ':', color='#ff8800', alpha=0.2, linewidth=1, label='2(p+1)')
    ax.plot(p_range, 2*(p_range - 1), ':', color='#00ff88', alpha=0.2, linewidth=1, label='2(p-1)')

    ax.set_ylabel(f'ord(M_{name} mod p)', fontsize=13, color='white')
    ax.set_title(f'Matrix {name} Order Bifurcation', fontsize=14, color='white', fontweight='bold')
    ax.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white',
              loc='upper left', ncol=3)
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.08, color='white')

axes[2].set_xlabel('Prime p', fontsize=14, color='white')

fig.suptitle('Galois Period Bifurcation: ord(Berggren mod p) by Legendre Symbol (2/p)',
             fontsize=18, color='#ffd700', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('/home/raver1975/factor/images/viz10_galois_bifurcation.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Order ratios ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#0a0a1a')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Left: ord/p ratio
for name, color in [('A', '#00ffff'), ('B', '#ff00ff'), ('C', '#ffd700')]:
    ps = np.array(results[name]['p'], dtype=float)
    ords = np.array(results[name]['ord'], dtype=float)
    ratio = ords / ps
    ax1.scatter(ps, ratio, c=color, s=30, alpha=0.7, label=f'ord({name})/p', edgecolors='none')

ax1.axhline(y=1, color='#666', linestyle='--', alpha=0.5)
ax1.axhline(y=2, color='#666', linestyle=':', alpha=0.3)
ax1.set_xlabel('Prime p', fontsize=13, color='white')
ax1.set_ylabel('ord(M mod p) / p', fontsize=13, color='white')
ax1.set_title('Normalized Order (ord/p)', fontsize=14, color='white', fontweight='bold')
ax1.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')
ax1.grid(True, alpha=0.1, color='white')

# Right: histogram of orders
for name, color in [('A', '#00ffff'), ('B', '#ff00ff'), ('C', '#ffd700')]:
    ords = np.array(results[name]['ord'], dtype=float)
    ps = np.array(results[name]['p'], dtype=float)
    ratio = ords / ps
    ax2.hist(ratio, bins=30, alpha=0.5, color=color, label=f'M_{name}', edgecolor='none')

ax2.set_xlabel('ord(M mod p) / p', fontsize=13, color='white')
ax2.set_ylabel('Count', fontsize=13, color='white')
ax2.set_title('Distribution of Normalized Orders', fontsize=14, color='white', fontweight='bold')
ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')

fig.suptitle('B3 Galois Period Analysis',
             fontsize=18, color='cyan', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz10_order_ratios.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_10: Galois period bifurcation images saved.")
