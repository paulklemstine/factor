#!/usr/bin/env python3
"""Viz 9: Depth vs Prime Density - Scatter plot showing exponential decay of prime legs."""
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from sympy import isprime

A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B = np.array([[1,2,2],[2,1,2],[2,2,3]])
C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
MATS = [A, B, C]

def generate_with_depth(max_depth):
    root = np.array([3, 4, 5])
    results = [(root, 0)]
    queue = deque([(root, 0)])
    while queue:
        t, d = queue.popleft()
        if d >= max_depth:
            continue
        for M in MATS:
            child = np.abs(M @ t)
            results.append((child, d + 1))
            queue.append((child, d + 1))
    return results

print("Generating tree...")
data = generate_with_depth(11)
print(f"  {len(data)} triples generated")

# Count primes by depth
depth_stats = {}
for triple, d in data:
    a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
    if d not in depth_stats:
        depth_stats[d] = {'total': 0, 'prime_a': 0, 'prime_b': 0, 'prime_c': 0,
                          'any_prime': 0}
    depth_stats[d]['total'] += 1
    pa = isprime(a)
    pb = isprime(b)
    pc = isprime(c)
    if pa:
        depth_stats[d]['prime_a'] += 1
    if pb:
        depth_stats[d]['prime_b'] += 1
    if pc:
        depth_stats[d]['prime_c'] += 1
    if pa or pb or pc:
        depth_stats[d]['any_prime'] += 1

print("Prime counting done.")

# --- Image 1: Prime fraction by depth ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.patch.set_facecolor('#0a0a1a')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

ds = sorted(depth_stats.keys())
frac_a = [depth_stats[d]['prime_a'] / depth_stats[d]['total'] for d in ds]
frac_b = [depth_stats[d]['prime_b'] / depth_stats[d]['total'] for d in ds]
frac_c = [depth_stats[d]['prime_c'] / depth_stats[d]['total'] for d in ds]
frac_any = [depth_stats[d]['any_prime'] / depth_stats[d]['total'] for d in ds]

ax1.semilogy(ds, frac_a, 'o-', color='#00ffff', linewidth=2.5, markersize=10,
             label='P(a prime)', markeredgecolor='white', markeredgewidth=0.5)
ax1.semilogy(ds, frac_b, 's-', color='#ff00ff', linewidth=2.5, markersize=10,
             label='P(b prime)', markeredgecolor='white', markeredgewidth=0.5)
ax1.semilogy(ds, frac_c, '^-', color='#ffd700', linewidth=2.5, markersize=10,
             label='P(c prime)', markeredgecolor='white', markeredgewidth=0.5)
ax1.semilogy(ds, frac_any, 'D-', color='#00ff88', linewidth=2.5, markersize=10,
             label='P(any prime)', markeredgecolor='white', markeredgewidth=0.5)

# Fit exponential decay to frac_any
from numpy.polynomial.polynomial import polyfit
log_frac = np.log(np.array(frac_any) + 1e-10)
coeffs = np.polyfit(ds, log_frac, 1)
fit_y = np.exp(np.polyval(coeffs, ds))
ax1.semilogy(ds, fit_y, '--', color='#ff4444', linewidth=1.5, alpha=0.7,
             label=f'Fit: exp({coeffs[0]:.3f}*d)')

ax1.set_xlabel('Tree Depth', fontsize=14, color='white')
ax1.set_ylabel('Fraction Prime (log scale)', fontsize=14, color='white')
ax1.set_title('Prime Leg Fraction vs Depth', fontsize=16, color='white', fontweight='bold')
ax1.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')
ax1.grid(True, alpha=0.1, color='white')

# Right: absolute counts
counts_a = [depth_stats[d]['prime_a'] for d in ds]
counts_b = [depth_stats[d]['prime_b'] for d in ds]
counts_c = [depth_stats[d]['prime_c'] for d in ds]
totals = [depth_stats[d]['total'] for d in ds]

width = 0.25
x = np.array(ds)
ax2.bar(x - width, counts_a, width, color='#00ffff', alpha=0.7, label='Prime a', edgecolor='none')
ax2.bar(x, counts_b, width, color='#ff00ff', alpha=0.7, label='Prime b', edgecolor='none')
ax2.bar(x + width, counts_c, width, color='#ffd700', alpha=0.7, label='Prime c', edgecolor='none')

# Overlay total as line
ax2_twin = ax2.twinx()
ax2_twin.plot(ds, totals, 'o--', color='#888888', linewidth=1.5, markersize=5, label='Total triples')
ax2_twin.set_ylabel('Total Triples at Depth', fontsize=12, color='#888888')
ax2_twin.tick_params(colors='#888888')
ax2_twin.spines['right'].set_color('#444')

ax2.set_xlabel('Tree Depth', fontsize=14, color='white')
ax2.set_ylabel('Count of Prime Legs', fontsize=14, color='white')
ax2.set_title('Prime Leg Counts by Depth', fontsize=16, color='white', fontweight='bold')
ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white', loc='upper left')

fig.suptitle('B3 Pythagorean Tree: Prime Density Exponential Decay',
             fontsize=18, color='cyan', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/raver1975/factor/images/viz09_prime_density.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

# --- Image 2: Prime hypotenuses highlighted on tree ---
fig, ax = plt.subplots(figsize=(14, 10))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

# Scatter: depth vs log(c), highlight primes
all_d = np.array([d for _, d in data])
all_c = np.array([int(t[2]) for t, _ in data], dtype=float)
is_prime_c = np.array([isprime(int(t[2])) for t, _ in data])

ax.scatter(all_d[~is_prime_c] + np.random.uniform(-0.2, 0.2, (~is_prime_c).sum()),
           np.log10(all_c[~is_prime_c]),
           c='#334466', s=3, alpha=0.3, label='Composite c')
ax.scatter(all_d[is_prime_c] + np.random.uniform(-0.2, 0.2, is_prime_c.sum()),
           np.log10(all_c[is_prime_c]),
           c='#ff0044', s=30, alpha=0.8, label='Prime c', edgecolors='white', linewidths=0.3)
# Glow
ax.scatter(all_d[is_prime_c] + np.random.uniform(-0.2, 0.2, is_prime_c.sum()),
           np.log10(all_c[is_prime_c]),
           c='#ff0044', s=120, alpha=0.1, edgecolors='none')

ax.set_xlabel('Tree Depth', fontsize=14, color='white')
ax.set_ylabel('log10(c)', fontsize=14, color='white')
ax.set_title('Prime Hypotenuses in the B3 Tree', fontsize=16, color='white', fontweight='bold')
ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='cyan', labelcolor='white')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.1, color='white')

plt.savefig('/home/raver1975/factor/images/viz09_prime_hypotenuses.png', dpi=150,
            facecolor='#0a0a1a', bbox_inches='tight')
plt.close()

print("viz_b3_09: Prime density images saved.")
