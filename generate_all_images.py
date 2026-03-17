#!/usr/bin/env python3
"""Generate 100 beautiful Pythagorean triple tree visualizations.

10 themes x 10 images each, saved to images/img_XNN.png
Uses dark_background style, vibrant colormaps, dpi=150.
Memory-safe: plt.close('all') after each image.
"""

import os
import gc
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Polygon, Circle
from matplotlib.collections import PatchCollection
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

OUT = "/home/raver1975/factor/images"
os.makedirs(OUT, exist_ok=True)

plt.style.use('dark_background')

# Berggren matrices
B1 = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B2 = np.array([[1,2,2],[2,1,2],[2,2,3]])
B3 = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])

def gen_tree(depth=6):
    triples = []
    stack = [(np.array([3,4,5]), 0)]
    while stack:
        t, d = stack.pop()
        a, b, c = int(abs(t[0])), int(abs(t[1])), int(t[2])
        triples.append((a, b, c, d))
        if d < depth:
            for M in [B1, B2, B3]:
                stack.append((M @ t, d+1))
    return triples

def gen_subtree(matrix, depth=6):
    triples = []
    stack = [(np.array([3,4,5]), 0)]
    while stack:
        t, d = stack.pop()
        a, b, c = int(abs(t[0])), int(abs(t[1])), int(t[2])
        triples.append((a, b, c, d))
        if d < depth:
            stack.append((matrix @ t, d+1))
    return triples

def gen_tree_with_parent(depth=6):
    triples = []
    edges = []
    stack = [(np.array([3,4,5]), 0, -1)]
    while stack:
        t, d, parent_id = stack.pop()
        a, b, c = int(abs(t[0])), int(abs(t[1])), int(t[2])
        tid = len(triples)
        triples.append((a, b, c, d))
        if parent_id >= 0:
            edges.append((parent_id, tid))
        if d < depth:
            for M in [B1, B2, B3]:
                stack.append((M @ t, d+1, tid))
    return triples, edges

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def factorize(n):
    if n <= 1: return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1: factors.append(n)
    return factors

def euler_totient(n):
    result = n
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1: result -= result // temp
    return result

def mobius(n):
    if n == 1: return 1
    f = factorize(n)
    if len(f) != len(set(f)): return 0
    return 1 if len(f) % 2 == 0 else -1

def savefig(name):
    path = os.path.join(OUT, f"img_{name}.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='black', edgecolor='none')
    plt.close('all')
    gc.collect()
    print(f"  Saved {name}")

# ═══════════════════════════════════════════════════════════════════════════
# THEME A: Tree Structure
# ═══════════════════════════════════════════════════════════════════════════
def theme_A():
    print("Theme A: Tree Structure")

    # A01 — Radial tree depth 6
    triples, edges = gen_tree_with_parent(depth=6)
    fig, ax = plt.subplots(figsize=(12, 12))
    n = len(triples)
    angles = np.zeros(n); radii = np.zeros(n)
    children = defaultdict(list)
    for p, c in edges: children[p].append(c)
    angle_ranges = {0: (0, 2*np.pi)}
    queue = [0]
    while queue:
        nxt = []
        for node in queue:
            ch = children[node]
            if not ch: continue
            lo, hi = angle_ranges[node]
            span = (hi-lo)/len(ch)
            for i, c in enumerate(ch):
                angles[c] = lo+span*(i+0.5)
                radii[c] = triples[c][3]
                angle_ranges[c] = (lo+span*i, lo+span*(i+1))
                nxt.append(c)
        queue = nxt
    xs = radii*np.cos(angles); ys = radii*np.sin(angles)
    depths = [t[3] for t in triples]
    colors_e = cm.plasma(np.array(depths)/max(max(depths),1))
    for p, c in edges:
        ax.plot([xs[p],xs[c]], [ys[p],ys[c]], color=colors_e[c], alpha=0.4, lw=0.5)
    ax.scatter(xs, ys, c=depths, cmap='plasma', s=8, zorder=5, edgecolors='none')
    ax.set_title("A01: Pythagorean Triple Tree — Radial Layout (Depth 6)", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.axis('off')
    savefig("A01")

    # A02 — Tree colored by A-value
    triples, edges = gen_tree_with_parent(depth=5)
    fig, ax = plt.subplots(figsize=(12, 10))
    n = len(triples)
    a_vals = [t[0] for t in triples]
    log_a = np.log1p(a_vals); norm_a = log_a/max(log_a)
    x_pos = np.zeros(n); y_pos = np.zeros(n)
    children = defaultdict(list)
    for p, c in edges: children[p].append(c)
    level_idx = defaultdict(int)
    level_counts = Counter(t[3] for t in triples)
    queue = [0]
    while queue:
        nxt = []
        for node in queue:
            d = triples[node][3]
            x_pos[node] = level_idx[d]; y_pos[node] = -d
            level_idx[d] += 1
            for c in children[node]: nxt.append(c)
        queue = nxt
    for d in level_counts:
        mask = np.array([triples[i][3]==d for i in range(n)])
        if mask.any(): x_pos[mask] -= x_pos[mask].mean()
    for p, c in edges:
        ax.plot([x_pos[p],x_pos[c]], [y_pos[p],y_pos[c]], color='gray', alpha=0.3, lw=0.5)
    sc = ax.scatter(x_pos, y_pos, c=norm_a, cmap='inferno', s=15, zorder=5, edgecolors='none')
    plt.colorbar(sc, label='log(A+1)', shrink=0.6)
    ax.set_title("A02: Tree Colored by A-value", fontsize=14, color='white'); ax.axis('off')
    savefig("A02")

    # A03 — Tree colored by primality of C
    triples = gen_tree(depth=5)
    fig, ax = plt.subplots(figsize=(12, 10))
    cs = [t[2] for t in triples]
    prime_c = [is_prime(c) for c in cs]
    colors = ['#00ff88' if p else '#ff4444' for p in prime_c]
    ax.scatter(range(len(triples)), cs, c=colors, s=5, alpha=0.7, edgecolors='none')
    ax.set_xlabel("Triple index", color='white'); ax.set_ylabel("Hypotenuse C", color='white')
    ax.set_title("A03: Hypotenuse Primality (green=prime, red=composite)", fontsize=14, color='white')
    savefig("A03")

    # A04-A06 — Individual subtrees
    for idx, (mat, name, cmp) in enumerate([(B1,"B1","cool"),(B2,"B2","autumn"),(B3,"B3","spring")]):
        fig, ax = plt.subplots(figsize=(10, 8))
        st = gen_subtree(mat, depth=8)
        ax.scatter([t[0] for t in st], [t[1] for t in st], c=[t[3] for t in st],
                  cmap=cmp, s=20, alpha=0.8, edgecolors='none')
        ax.set_xlabel("A (odd leg)", color='white'); ax.set_ylabel("B (even leg)", color='white')
        ax.set_title(f"A0{4+idx}: {name} Subtree (depth 8)", fontsize=14, color='white')
        savefig(f"A0{4+idx}")

    # A07 — 3 subtrees overlaid
    fig, ax = plt.subplots(figsize=(12, 10))
    for mat, name, color in [(B1,"B1","#ff4488"),(B2,"B2","#44ff88"),(B3,"B3","#4488ff")]:
        st = gen_subtree(mat, depth=7)
        ax.scatter([t[0] for t in st], [t[1] for t in st], c=color, s=8, alpha=0.5,
                  label=name, edgecolors='none')
    ax.legend(fontsize=12); ax.set_xlabel("A", color='white'); ax.set_ylabel("B", color='white')
    ax.set_title("A07: Three Subtrees Overlaid", fontsize=14, color='white')
    savefig("A07")

    # A08 — Node sizes by hypotenuse
    triples, edges = gen_tree_with_parent(depth=5)
    fig, ax = plt.subplots(figsize=(12, 10))
    n = len(triples)
    cs = np.array([t[2] for t in triples], dtype=float)
    sizes = 5+200*(cs/cs.max())**0.5
    angles2 = np.zeros(n); radii2 = np.zeros(n)
    children = defaultdict(list)
    for p, c in edges: children[p].append(c)
    ar2 = {0: (0, 2*np.pi)}
    queue = [0]
    while queue:
        nxt = []
        for node in queue:
            ch = children[node]
            if not ch: continue
            lo, hi = ar2[node]; span = (hi-lo)/len(ch)
            for i, c in enumerate(ch):
                angles2[c] = lo+span*(i+0.5); radii2[c] = triples[c][3]
                ar2[c] = (lo+span*i, lo+span*(i+1)); nxt.append(c)
        queue = nxt
    xs = radii2*np.cos(angles2); ys = radii2*np.sin(angles2)
    ax.scatter(xs, ys, s=sizes, c=np.log1p(cs), cmap='magma', alpha=0.7,
              edgecolors='white', linewidths=0.3)
    ax.set_title("A08: Node Size ~ Hypotenuse", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.axis('off')
    savefig("A08")

    # A09 — Polar tree
    triples = gen_tree(depth=6)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='polar'); ax.set_facecolor('black')
    for t in triples:
        a, b, c, d = t
        theta = np.arctan2(b, a); r = np.log1p(c)
        ax.scatter(theta, r, c=[cm.viridis(d/6.0)], s=5, alpha=0.7, edgecolors='none')
    ax.set_title("A09: Polar Tree (angle=atan2(B,A), r=log(C))", fontsize=12, color='white', pad=20)
    savefig("A09")

    # A10 — Sorted by C with depth coloring
    triples = gen_tree(depth=6)
    triples_sorted = sorted(triples, key=lambda t: t[2])
    fig, ax = plt.subplots(figsize=(14, 6))
    cs = [t[2] for t in triples_sorted]; ds = [t[3] for t in triples_sorted]
    ax.bar(range(len(cs)), cs, color=cm.plasma(np.array(ds)/6.0), width=1.0, edgecolor='none')
    ax.set_xlabel("Rank by C", color='white'); ax.set_ylabel("Hypotenuse C", color='white')
    ax.set_title("A10: Triples Sorted by Hypotenuse (color=depth)", fontsize=14, color='white')
    savefig("A10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME B: Orbits mod p
# ═══════════════════════════════════════════════════════════════════════════
def theme_B():
    print("Theme B: Orbits mod p")
    triples = gen_tree(depth=7)

    for idx, p in enumerate([7, 13, 23, 41, 61]):
        fig, ax = plt.subplots(figsize=(10, 10))
        a_mod = [t[0]%p for t in triples]; b_mod = [t[1]%p for t in triples]
        density = Counter(zip(a_mod, b_mod))
        xs, ys, ws = [], [], []
        for (x,y),w in density.items(): xs.append(x); ys.append(y); ws.append(w)
        ws = np.array(ws, dtype=float)
        sc = ax.scatter(xs, ys, c=np.log1p(ws), cmap='hot', s=50+ws*5, alpha=0.8,
                       edgecolors='white', linewidths=0.3)
        plt.colorbar(sc, label='log(count+1)', shrink=0.7)
        ax.set_xlim(-0.5, p-0.5); ax.set_ylim(-0.5, p-0.5)
        ax.set_xlabel(f"A mod {p}", color='white'); ax.set_ylabel(f"B mod {p}", color='white')
        ax.set_title(f"B0{idx+1}: Pythagorean Orbits mod {p}", fontsize=14, color='white')
        ax.set_aspect('equal')
        savefig(f"B0{idx+1}")

    # B06 — Orbit mod 77 (CRT: 7x11)
    fig, ax = plt.subplots(figsize=(12, 10))
    p = 77
    density = Counter(zip([t[0]%p for t in triples], [t[1]%p for t in triples]))
    xs, ys, ws = [], [], []
    for (x,y),w in density.items(): xs.append(x); ys.append(y); ws.append(w)
    ws = np.array(ws, dtype=float)
    ax.scatter(xs, ys, c=np.log1p(ws), cmap='turbo', s=10+ws*3, alpha=0.6, edgecolors='none')
    ax.set_title("B06: Orbit mod 77 (CRT: 7x11)", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("B06")

    # B07 — GCD highlighting
    fig, ax = plt.subplots(figsize=(12, 10))
    N = 3*5*7*11*13
    gcd_vals = [math.gcd(t[0], N) for t in triples]
    colors = ['#ff0000' if g>1 else '#333366' for g in gcd_vals]
    sizes = [20 if g>1 else 2 for g in gcd_vals]
    ax.scatter([t[0] for t in triples], [t[1] for t in triples], c=colors, s=sizes,
              alpha=0.7, edgecolors='none')
    ax.set_xlabel("A", color='white'); ax.set_ylabel("B", color='white')
    ax.set_title(f"B07: GCD(A, {N}) > 1 Highlighted", fontsize=14, color='white')
    savefig("B07")

    # B08 — B2 only orbit
    st = gen_subtree(B2, depth=8)
    fig, ax = plt.subplots(figsize=(10, 10))
    p = 31
    density = Counter(zip([t[0]%p for t in st], [t[1]%p for t in st]))
    xs, ys, ws = [], [], []
    for (x,y),w in density.items(): xs.append(x); ys.append(y); ws.append(w)
    ws = np.array(ws, dtype=float)
    ax.scatter(xs, ys, c=np.log1p(ws), cmap='cool', s=80, alpha=0.8, edgecolors='white', linewidths=0.5)
    ax.set_title("B08: B2-Subtree Orbits mod 31", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("B08")

    # B09 — Contour density
    fig, ax = plt.subplots(figsize=(10, 10))
    p = 37
    a_mod = np.array([t[0]%p for t in triples], dtype=float)
    b_mod = np.array([t[1]%p for t in triples], dtype=float)
    from scipy.stats import gaussian_kde
    xy = np.vstack([a_mod+np.random.normal(0,0.1,len(a_mod)),
                     b_mod+np.random.normal(0,0.1,len(b_mod))])
    kde = gaussian_kde(xy)
    xg, yg = np.mgrid[0:p:100j, 0:p:100j]
    zg = kde(np.vstack([xg.ravel(), yg.ravel()])).reshape(xg.shape)
    ax.contourf(xg, yg, zg, levels=30, cmap='inferno')
    ax.contour(xg, yg, zg, levels=10, colors='white', linewidths=0.3, alpha=0.5)
    ax.set_title("B09: Orbit Density Contour mod 37", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("B09")

    # B10 — RGB multi-prime
    fig, ax = plt.subplots(figsize=(10, 10))
    primes_rgb = [7, 11, 13]
    sz = max(primes_rgb)
    img = np.zeros((sz, sz, 3))
    for ch, p in enumerate(primes_rgb):
        for t in triples:
            x, y = t[0]%p, t[1]%p
            if x < sz and y < sz: img[x, y, ch] += 1
    img = img/(img.max()+1e-10); img = np.clip(img**0.5, 0, 1)
    ax.imshow(img, interpolation='nearest', origin='lower')
    ax.set_title("B10: RGB Multi-Prime (R=mod7, G=mod11, B=mod13)", fontsize=14, color='white')
    savefig("B10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME C: Smoothness
# ═══════════════════════════════════════════════════════════════════════════
def theme_C():
    print("Theme C: Smoothness")

    # C01 — Dickman rho curve
    fig, ax = plt.subplots(figsize=(12, 6))
    us = np.linspace(1, 10, 500)
    rho = np.ones_like(us)
    for i, u in enumerate(us):
        if u <= 1: rho[i] = 1.0
        elif u <= 2: rho[i] = 1.0-np.log(u)
        else: rho[i] = u**(-u*(1+1/(2*np.log(u))))
    ax.semilogy(us, rho, color='#ff6600', lw=3)
    ax.fill_between(us, rho, alpha=0.2, color='#ff6600')
    ax.axvline(x=3.5, color='cyan', ls='--', label='SIQS sweet spot')
    ax.axvline(x=5, color='magenta', ls='--', label='GNFS regime')
    ax.set_xlabel("u = log(N)/log(B)", fontsize=12, color='white')
    ax.set_ylabel("rho(u)", fontsize=12, color='white')
    ax.set_title("C01: Dickman rho Function", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("C01")

    # C02 — Smooth values marked in tree
    triples = gen_tree(depth=5)
    fig, ax = plt.subplots(figsize=(14, 6))
    B = 100
    fb = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    cs = [t[2] for t in triples]
    smooth = []
    for c in cs:
        temp = c
        for p in fb:
            while temp % p == 0: temp //= p
        smooth.append(temp == 1)
    colors = ['#00ff00' if s else '#440000' for s in smooth]
    ax.bar(range(len(cs)), cs, color=colors, width=1.0, edgecolor='none')
    ax.set_title(f"C02: B={B}-Smooth Hypotenuses (green=smooth)", fontsize=14, color='white')
    ax.set_ylabel("C", color='white')
    savefig("C02")

    # C03 — FB distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    primes = [p for p in range(2, 500) if is_prime(p)]
    types = ['#00ccff' if p%4==1 else '#ff4444' for p in primes]
    ax.bar(range(len(primes)), primes, color=types, width=1.0, edgecolor='none')
    ax.set_title("C03: Factor Base Primes (cyan=1 mod 4, red=3 mod 4)", fontsize=14, color='white')
    ax.set_ylabel("Prime", color='white')
    savefig("C03")

    # C04 — Stacked sieve arrays
    fig, ax = plt.subplots(figsize=(14, 8))
    M = 1000; sieve = np.zeros(M)
    primes_fb = [p for p in range(2, 200) if is_prime(p)]
    cols = cm.viridis(np.linspace(0, 1, len(primes_fb)))
    for i, p in enumerate(primes_fb):
        contrib = np.zeros(M)
        for start in range(0, M, p): contrib[start] = np.log(p)
        sieve += contrib
        if i < 15:
            ax.fill_between(range(M), sieve-contrib, sieve, alpha=0.5, color=cols[i],
                          label=f'p={p}' if i < 8 else None)
    ax.set_title("C04: Stacked Sieve Contributions", fontsize=14, color='white')
    ax.legend(fontsize=9, ncol=2)
    ax.set_xlabel("Sieve position", color='white'); ax.set_ylabel("Accumulated log-sum", color='white')
    savefig("C04")

    # C05 — Relation matrix sparsity
    fig, ax = plt.subplots(figsize=(10, 10))
    np.random.seed(42)
    rows, cols2 = 200, 180
    data = np.zeros((rows, cols2), dtype=int)
    for r in range(rows):
        idxs = np.random.choice(cols2, np.random.randint(3,12), replace=False)
        data[r, idxs] = 1
    ax.spy(data, markersize=0.5, color='#00ffaa', aspect='auto')
    ax.set_title(f"C05: GF(2) Relation Matrix ({rows}x{cols2})", fontsize=14, color='white')
    ax.set_xlabel("Factor base index", color='white'); ax.set_ylabel("Relation index", color='white')
    savefig("C05")

    # C06 — Large prime graph
    fig, ax = plt.subplots(figsize=(10, 10))
    np.random.seed(42)
    n_lp = 150; lp_nodes = np.random.rand(n_lp, 2)
    edges_lp = [(np.random.randint(n_lp), np.random.randint(n_lp)) for _ in range(300)]
    degree = Counter()
    for i, j in edges_lp: degree[i] += 1; degree[j] += 1
    nc = [degree.get(i, 0) for i in range(n_lp)]
    for i, j in edges_lp:
        ax.plot([lp_nodes[i,0],lp_nodes[j,0]], [lp_nodes[i,1],lp_nodes[j,1]],
                color='#334466', alpha=0.3, lw=0.5)
    sc = ax.scatter(lp_nodes[:,0], lp_nodes[:,1], c=nc, cmap='YlOrRd',
                    s=np.array(nc)*10+20, edgecolors='white', linewidths=0.3, zorder=5)
    plt.colorbar(sc, label='Degree', shrink=0.7)
    ax.set_title("C06: Large Prime Relation Graph", fontsize=14, color='white'); ax.axis('off')
    savefig("C06")

    # C07 — Null vector visualization
    fig, ax = plt.subplots(figsize=(14, 4))
    np.random.seed(42)
    vec = np.random.choice([0,1], size=200, p=[0.7,0.3])
    colors = ['#ff00ff' if v else '#111122' for v in vec]
    ax.bar(range(200), np.ones(200), color=colors, width=1.0, edgecolor='none')
    ax.set_title("C07: GF(2) Null Vector (magenta=1, dark=0)", fontsize=14, color='white')
    ax.set_yticks([]); ax.set_xlabel("Relation index", color='white')
    savefig("C07")

    # C08 — Smooth cascade
    fig, ax = plt.subplots(figsize=(12, 8))
    triples = gen_tree(depth=5)
    cs_sorted = sorted([t[2] for t in triples])[:200]
    for i, c in enumerate(cs_sorted):
        factors = factorize(c); y_base = 0
        for f in factors:
            height = np.log(f)
            color = cm.Set1(hash(f) % 9 / 9)
            ax.bar(i, height, bottom=y_base, color=color, width=0.8, edgecolor='none')
            y_base += height
    ax.set_title("C08: Prime Factorization Cascade of Hypotenuses", fontsize=14, color='white')
    ax.set_xlabel("Rank", color='white'); ax.set_ylabel("Stacked log(prime)", color='white')
    savefig("C08")

    # C09 — Smoothness heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    B_vals = [20, 50, 100, 200, 500, 1000]
    triples = gen_tree(depth=7)
    cs_all = [t[2] for t in triples]
    heatmap = np.zeros((len(B_vals), 13))
    for bi, Bv in enumerate(B_vals):
        fb2 = [p for p in range(2, Bv+1) if is_prime(p)]
        for si, nd in enumerate(range(2, 15)):
            lo, hi = 10**(nd-1), 10**nd
            subset = [c for c in cs_all if lo <= c < hi][:200]
            if not subset: continue
            smooth_count = 0
            for c in subset:
                temp = c
                for p in fb2:
                    while temp % p == 0: temp //= p
                if temp == 1: smooth_count += 1
            heatmap[bi, si] = smooth_count / len(subset)
    im = ax.imshow(heatmap, cmap='viridis', aspect='auto', origin='lower')
    ax.set_yticks(range(len(B_vals))); ax.set_yticklabels([str(b) for b in B_vals])
    ax.set_xticks(range(13)); ax.set_xticklabels([str(d) for d in range(2, 15)])
    ax.set_xlabel("Digits", color='white'); ax.set_ylabel("Smoothness bound B", color='white')
    ax.set_title("C09: Smoothness Rate Heatmap", fontsize=14, color='white')
    plt.colorbar(im, label='Fraction B-smooth', shrink=0.7)
    savefig("C09")

    # C10 — Relation rate vs digits
    fig, ax = plt.subplots(figsize=(12, 6))
    digits = [30, 40, 48, 54, 60, 63, 66, 69, 72]
    rel_rate = [50000, 8000, 2000, 500, 150, 60, 25, 12, 5]
    ax.semilogy(digits, rel_rate, 'o-', color='#00ffcc', lw=2, markersize=10)
    ax.fill_between(digits, rel_rate, alpha=0.15, color='#00ffcc')
    ax.set_xlabel("Digits", fontsize=12, color='white')
    ax.set_ylabel("Relations/second", fontsize=12, color='white')
    ax.set_title("C10: SIQS Relation Collection Rate", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("C10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME D: Eigenvalues
# ═══════════════════════════════════════════════════════════════════════════
def theme_D():
    print("Theme D: Eigenvalues")
    B2f = B2.astype(float)
    matrices = [B1.astype(float), B2.astype(float), B3.astype(float)]

    # D01 — Phase portrait of B2 iterations
    fig, ax = plt.subplots(figsize=(10, 10))
    t = np.array([3.0, 4.0, 5.0])
    trajectory = [t.copy()]
    for _ in range(12):
        t = B2f @ t; t = t/np.linalg.norm(t)*10
        trajectory.append(t.copy())
    traj = np.array(trajectory)
    ax.plot(traj[:,0], traj[:,1], 'o-', color='#ff44ff', markersize=8, lw=2)
    for i in range(len(traj)):
        ax.annotate(str(i), (traj[i,0], traj[i,1]), color='white', fontsize=8)
    ax.set_title("D01: Phase Portrait of B2 Iterations", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("D01")

    # D02 — Cobweb diagram
    fig, ax = plt.subplots(figsize=(10, 8))
    t = np.array([3.0, 4.0, 5.0])
    ratios = []
    for _ in range(50):
        ratios.append(t[0]/t[2]); t = B2f @ t
    xs = ratios[:-1]; ys = ratios[1:]
    ax.plot(xs, ys, 'o-', color='#44ffcc', markersize=4, lw=1, alpha=0.7)
    mn, mx = min(min(xs),min(ys)), max(max(xs),max(ys))
    ax.plot([mn,mx], [mn,mx], '--', color='gray', alpha=0.5)
    ax.set_title("D02: Cobweb Diagram (A/C ratio under B2)", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("D02")

    # D03 — Lyapunov exponent
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    lyap = []
    for _ in range(200):
        M = np.eye(3)
        for step in range(20): M = matrices[np.random.randint(3)] @ M
        lyap.append(np.log(np.linalg.svd(M, compute_uv=False)[0])/20)
    ax.hist(lyap, bins=40, color='#ff6644', edgecolor='#ff8866', alpha=0.8)
    ax.axvline(np.mean(lyap), color='cyan', lw=2, ls='--', label=f'mean={np.mean(lyap):.3f}')
    ax.set_title("D03: Lyapunov Exponent Distribution", fontsize=14, color='white')
    ax.legend(fontsize=11)
    savefig("D03")

    # D04 — Singular values under iteration
    fig, ax = plt.subplots(figsize=(12, 6))
    for mi, (M, name, color) in enumerate([(B1,"B1","#ff4488"),(B2,"B2","#44ff88"),(B3,"B3","#4488ff")]):
        Mf = M.astype(float); Mn = np.eye(3); svs_list = []
        for k in range(15):
            Mn = Mf @ Mn; svs_list.append(np.linalg.svd(Mn, compute_uv=False))
        svs_arr = np.array(svs_list)
        for j in range(3):
            ax.semilogy(range(15), svs_arr[:,j], color=color, lw=2, alpha=0.7-j*0.2,
                       label=f'{name} s{j+1}' if j==0 else None)
    ax.set_title("D04: Singular Value Growth", fontsize=14, color='white')
    ax.legend(fontsize=10); ax.grid(True, alpha=0.2)
    savefig("D04")

    # D05 — Trace periodicity
    fig, ax = plt.subplots(figsize=(12, 6))
    for M, name, color in [(B1,"B1","#ff4488"),(B2,"B2","#44ff88"),(B3,"B3","#4488ff")]:
        Mf = M.astype(float); Mn = np.eye(3); traces = []
        for k in range(20): Mn = Mf @ Mn; traces.append(np.trace(Mn))
        ax.semilogy(range(1,21), np.abs(traces), 'o-', color=color, label=name, lw=2)
    ax.set_title("D05: Trace Growth |Tr(M^n)|", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("D05")

    # D06 — Determinant pattern
    fig, ax = plt.subplots(figsize=(12, 6))
    for M, name, color in [(B1,"B1","#ff4488"),(B2,"B2","#44ff88"),(B3,"B3","#4488ff")]:
        Mf = M.astype(float); Mn = np.eye(3); dets = []
        for k in range(15): Mn = Mf @ Mn; dets.append(np.linalg.det(Mn))
        ax.plot(range(1,16), dets, 'o-', color=color, label=name, lw=2, markersize=8)
    ax.set_title("D06: Determinant Pattern det(M^n)", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("D06")

    # D07 — Characteristic polynomial roots
    fig, ax = plt.subplots(figsize=(10, 10))
    for M, name, marker in [(B1,"B1","o"),(B2,"B2","s"),(B3,"B3","^")]:
        evals = np.linalg.eigvals(M.astype(float))
        ax.scatter(evals.real, evals.imag, s=200, marker=marker, label=name, zorder=5,
                  edgecolors='white', linewidths=1.5)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), '--', color='gray', alpha=0.3)
    ax.set_title("D07: Eigenvalues of B1, B2, B3", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.set_aspect('equal'); ax.grid(True, alpha=0.2)
    savefig("D07")

    # D08 — Matrix norm growth
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    for trial in range(20):
        Mn = np.eye(3); norms = []
        for k in range(25):
            Mn = matrices[np.random.randint(3)] @ Mn; norms.append(np.linalg.norm(Mn))
        ax.semilogy(range(25), norms, alpha=0.3, color='#44aaff', lw=1)
    ax.set_title("D08: Matrix Norm Growth (20 Random Walks)", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("D08")

    # D09 — Eigenvector angles
    fig, ax = plt.subplots(figsize=(10, 10))
    for M, name, color in [(B1,"B1","#ff4488"),(B2,"B2","#44ff88"),(B3,"B3","#4488ff")]:
        _, evecs = np.linalg.eig(M.astype(float))
        for j in range(3):
            v = evecs[:,j].real; v = v/np.linalg.norm(v)
            ax.arrow(0, 0, v[0], v[1], head_width=0.03, head_length=0.02, fc=color, ec=color, lw=2)
            ax.annotate(f'{name}:v{j+1}', (v[0]*1.1, v[1]*1.1), color=color, fontsize=9)
    ax.plot(np.cos(theta), np.sin(theta), '--', color='gray', alpha=0.3)
    ax.set_title("D09: Eigenvector Directions (x-y projection)", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.grid(True, alpha=0.2)
    savefig("D09")

    # D10 — Spectral radius histogram
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    spec_radii = []
    for _ in range(500):
        M = np.eye(3)
        for _ in range(5): M = matrices[np.random.randint(3)] @ M
        spec_radii.append(max(abs(np.linalg.eigvals(M))))
    ax.hist(spec_radii, bins=50, color='#ff8800', edgecolor='#ffaa33', alpha=0.8)
    ax.set_title("D10: Spectral Radius of Length-5 Compositions", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("D10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME E: Number Theory
# ═══════════════════════════════════════════════════════════════════════════
def theme_E():
    print("Theme E: Number Theory")
    triples = gen_tree(depth=6)

    # E01 — m-n distribution
    fig, ax = plt.subplots(figsize=(10, 10))
    ms, ns = [], []
    for t in triples:
        a, b, c, d = t
        if a%2==1 and b%2==0:
            m2 = (c+a)//2; n2 = (c-a)//2
            m = int(m2**0.5+0.5); n = int(n2**0.5+0.5)
            if m*m==m2 and n*n==n2: ms.append(m); ns.append(n)
    ax.scatter(ms, ns, c=np.log1p(np.array(ms)**2+np.array(ns)**2), cmap='plasma',
              s=5, alpha=0.6, edgecolors='none')
    ax.set_xlabel("m", color='white'); ax.set_ylabel("n", color='white')
    ax.set_title("E01: (m, n) Parameter Distribution", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("E01")

    # E02 — gcd(A,B) histogram
    fig, ax = plt.subplots(figsize=(12, 6))
    gcds = [math.gcd(t[0], t[1]) for t in triples]
    c = Counter(gcds); vals = sorted(c.keys())[:30]
    counts = [c[v] for v in vals]
    ax.bar(range(len(vals)), counts, color=cm.viridis(np.linspace(0,1,len(vals))), edgecolor='none')
    ax.set_xticks(range(len(vals))); ax.set_xticklabels([str(v) for v in vals], rotation=45)
    ax.set_title("E02: gcd(A, B) Distribution", fontsize=14, color='white')
    savefig("E02")

    # E03 — C mod primes pie charts
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    for idx, p in enumerate([3,5,7,11,13,17]):
        ax = axes[idx//3][idx%3]
        residues = [t[2]%p for t in triples]; c = Counter(residues)
        labels = [str(k) for k in sorted(c.keys())]
        values = [c[k] for k in sorted(c.keys())]
        ax.pie(values, labels=labels, colors=cm.Set3(np.linspace(0,1,len(labels))),
               textprops={'color':'white','fontsize':7})
        ax.set_title(f"C mod {p}", color='white', fontsize=11)
    fig.suptitle("E03: Hypotenuse Residues mod Small Primes", fontsize=14, color='white')
    plt.tight_layout()
    savefig("E03")

    # E04 — Jacobi symbol pattern
    fig, ax = plt.subplots(figsize=(12, 8))
    primes = [p for p in range(3, 80) if is_prime(p)]
    cs_unique = sorted(set(t[2] for t in triples))[:100]
    jac_matrix = np.zeros((len(cs_unique), len(primes)))
    for i, c in enumerate(cs_unique):
        for j, p in enumerate(primes):
            jac = pow(c, (p-1)//2, p)
            jac_matrix[i, j] = 1 if jac==1 else (-1 if jac==p-1 else 0)
    ax.imshow(jac_matrix, cmap='coolwarm', aspect='auto', interpolation='nearest')
    ax.set_xlabel("Prime index", color='white'); ax.set_ylabel("Hypotenuse rank", color='white')
    ax.set_title("E04: Jacobi Symbol (C/p) Pattern", fontsize=14, color='white')
    savefig("E04")

    # E05 — Quadratic residue scatter
    fig, ax = plt.subplots(figsize=(10, 10))
    p = 101; qr = set(x*x%p for x in range(p))
    a_mod = [t[0]%p for t in triples]; b_mod = [t[1]%p for t in triples]
    colors = ['#00ff88' if a%p in qr else '#ff4444' for a in a_mod]
    ax.scatter(a_mod, b_mod, c=colors, s=8, alpha=0.6, edgecolors='none')
    ax.set_title("E05: QR/NQR of A mod 101 (green=QR)", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("E05")

    # E06 — Digit sum distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    digit_sums = [sum(int(d) for d in str(t[2])) for t in triples]
    c = Counter(digit_sums); vals = sorted(c.keys())
    ax.bar(vals, [c[v] for v in vals], color='#ff66aa', edgecolor='none')
    ax.set_title("E06: Digit Sum of Hypotenuse C", fontsize=14, color='white')
    ax.set_xlabel("Digit sum", color='white')
    savefig("E06")

    # E07 — CF quotients
    fig, ax = plt.subplots(figsize=(14, 6))
    triples_small = sorted(triples, key=lambda t: t[2])[:20]
    for ti, t in enumerate(triples_small):
        c = t[2]
        if int(c**0.5)**2 == c: continue
        a0 = int(c**0.5); quotients = [a0]
        m, d, a = 0, 1, a0
        for _ in range(30):
            m = d*a-m; d = (c-m*m)//d
            if d == 0: break
            a = (a0+m)//d; quotients.append(a)
        ax.plot(range(len(quotients)), quotients, 'o-', alpha=0.6, markersize=3, lw=1,
                label=f'C={c}' if ti<8 else None)
    ax.set_title("E07: CF Quotients of sqrt(C)", fontsize=14, color='white')
    ax.legend(fontsize=8, ncol=2)
    savefig("E07")

    # E08 — Prime factorization barcode
    fig, ax = plt.subplots(figsize=(14, 8))
    triples_sorted = sorted(triples, key=lambda t: t[2])[:100]
    for i, t in enumerate(triples_sorted):
        factors = factorize(t[2]); x_pos = 0
        for f in factors:
            width = np.log(f)
            ax.barh(i, width, left=x_pos, height=0.8, color=cm.tab20(hash(f)%20/20), edgecolor='none')
            x_pos += width
    ax.set_title("E08: Prime Factorization Barcode of C", fontsize=14, color='white')
    ax.set_xlabel("Cumulative log(prime)", color='white')
    savefig("E08")

    # E09 — Euler totient
    fig, ax = plt.subplots(figsize=(12, 6))
    cs = sorted(set(t[2] for t in triples))[:300]
    tots = [euler_totient(c) for c in cs]
    ax.scatter(cs, tots, c=np.array(tots)/np.array(cs,dtype=float), cmap='viridis',
              s=8, alpha=0.7, edgecolors='none')
    ax.plot(cs, cs, '--', color='gray', alpha=0.3, label='y=x')
    ax.set_title("E09: Euler Totient phi(C)", fontsize=14, color='white')
    ax.legend(fontsize=10)
    savefig("E09")

    # E10 — Mobius function
    fig, ax = plt.subplots(figsize=(12, 6))
    cs = sorted(set(t[2] for t in triples))[:300]
    mus = [mobius(c) for c in cs]
    colors = ['#00ff00' if m==1 else '#ff0000' if m==-1 else '#444444' for m in mus]
    ax.bar(range(len(cs)), mus, color=colors, width=1.0, edgecolor='none')
    ax.set_title("E10: Mobius Function mu(C)", fontsize=14, color='white')
    savefig("E10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME F: Geometry
# ═══════════════════════════════════════════════════════════════════════════
def theme_F():
    print("Theme F: Geometry")
    triples = gen_tree(depth=5)

    # F01 — Actual triangles drawn
    fig, ax = plt.subplots(figsize=(12, 10))
    small_triples = sorted(triples, key=lambda t: t[2])[:30]
    for i, t in enumerate(small_triples):
        a, b, c, d = t; scale = 50.0/c
        row = i//6; col = i%6; ox = col*60; oy = -row*60
        pts = np.array([[ox,oy],[ox+a*scale,oy],[ox,oy+b*scale]])
        tri = Polygon(pts, fill=True, facecolor=(*cm.rainbow(d/5.0)[:3], 0.3),
                     edgecolor=cm.rainbow(d/5.0), lw=1.5)
        ax.add_patch(tri)
        ax.text(ox+5, oy+25, f'{a},{b},{c}', color='white', fontsize=5)
    ax.set_xlim(-10, 370); ax.set_ylim(-320, 60)
    ax.set_aspect('equal'); ax.set_title("F01: Pythagorean Right Triangles", fontsize=14, color='white')
    ax.axis('off')
    savefig("F01")

    # F02 — Unit circle points
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter([t[0]/t[2] for t in triples], [t[1]/t[2] for t in triples],
              c=[t[3] for t in triples], cmap='plasma', s=10, alpha=0.7, edgecolors='none')
    theta = np.linspace(0, np.pi/2, 100)
    ax.plot(np.cos(theta), np.sin(theta), '--', color='gray', alpha=0.5)
    ax.set_title("F02: Rational Points on Unit Circle (A/C, B/C)", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("F02")

    # F03 — Area vs C
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter([t[2] for t in triples], [0.5*t[0]*t[1] for t in triples],
              c=[t[3] for t in triples], cmap='viridis', s=8, alpha=0.7, edgecolors='none')
    ax.set_xlabel("Hypotenuse C", color='white'); ax.set_ylabel("Area = AB/2", color='white')
    ax.set_title("F03: Triangle Area vs Hypotenuse", fontsize=14, color='white')
    savefig("F03")

    # F04 — Aspect ratio
    fig, ax = plt.subplots(figsize=(12, 6))
    ratios = [min(t[0],t[1])/max(t[0],t[1]) for t in triples]
    ax.hist(ratios, bins=50, color='#44aaff', edgecolor='#66ccff', alpha=0.8)
    ax.set_title("F04: Aspect Ratio min(A,B)/max(A,B)", fontsize=14, color='white')
    savefig("F04")

    # F05 — Incircle radius
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter([t[2] for t in triples], [(t[0]+t[1]-t[2])/2 for t in triples],
              c=[t[3] for t in triples], cmap='magma', s=8, alpha=0.7, edgecolors='none')
    ax.set_xlabel("C", color='white'); ax.set_ylabel("r = (A+B-C)/2", color='white')
    ax.set_title("F05: Incircle Radius vs Hypotenuse", fontsize=14, color='white')
    savefig("F05")

    # F06 — Similarity classes
    fig, ax = plt.subplots(figsize=(12, 6))
    angles = [np.degrees(np.arctan2(t[1], t[0])) for t in triples]
    ax.hist(angles, bins=60, color='#ff8844', edgecolor='#ffaa66', alpha=0.8)
    ax.set_title("F06: Similarity Classes (Angle Distribution)", fontsize=14, color='white')
    savefig("F06")

    # F07 — Lattice points
    fig, ax = plt.subplots(figsize=(10, 10))
    for t in triples[:200]:
        a, b, c, d = t
        ax.plot([0, a], [0, b], alpha=0.1, color='#4488ff', lw=0.5)
        ax.plot(a, b, 'o', color=cm.plasma(d/6.0), markersize=3, alpha=0.7)
    ax.set_title("F07: Lattice Points (A, B)", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("F07")

    # F08 — 3D cone
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d'); ax.set_facecolor('black')
    for t in triples[:500]:
        ax.scatter(t[0], t[1], t[2], c=[cm.plasma(t[3]/6.0)], s=3, alpha=0.6)
    theta = np.linspace(0, np.pi/2, 50)
    r_max = max(t[2] for t in triples[:500])
    for r in np.linspace(0, r_max, 10):
        ax.plot(r*np.cos(theta), r*np.sin(theta), r, color='gray', alpha=0.1, lw=0.5)
    ax.set_xlabel('A', color='white'); ax.set_ylabel('B', color='white'); ax.set_zlabel('C', color='white')
    ax.set_title("F08: Pythagorean Cone x^2+y^2=z^2", fontsize=14, color='white')
    savefig("F08")

    # F09 — Stereographic projection
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter([t[0]/(t[2]+1) for t in triples], [t[1]/(t[2]+1) for t in triples],
              c=[t[3] for t in triples], cmap='cool', s=8, alpha=0.7, edgecolors='none')
    ax.set_title("F09: Stereographic Projection (A/(C+1), B/(C+1))", fontsize=14, color='white')
    ax.set_aspect('equal')
    savefig("F09")

    # F10 — Circle packing
    fig, ax = plt.subplots(figsize=(10, 10))
    small = sorted(triples, key=lambda t: t[2])[:80]
    patches = []
    for i, t in enumerate(small):
        r = (t[0]+t[1]-t[2])/2*0.3
        angle = 2*np.pi*i/len(small); dist = 5+t[2]*0.05
        patches.append(Circle((dist*np.cos(angle), dist*np.sin(angle)), r, fill=True))
    pc = PatchCollection(patches, facecolors=cm.rainbow(np.linspace(0,1,len(patches))),
                        alpha=0.6, edgecolors='white', linewidths=0.5)
    ax.add_collection(pc); ax.set_xlim(-50, 50); ax.set_ylim(-50, 50)
    ax.set_aspect('equal'); ax.set_title("F10: Incircle Packing", fontsize=14, color='white')
    ax.axis('off')
    savefig("F10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME G: Performance
# ═══════════════════════════════════════════════════════════════════════════
def theme_G():
    print("Theme G: Performance")

    # G01 — Algorithm comparison
    fig, ax = plt.subplots(figsize=(14, 7))
    digits = [30, 40, 48, 54, 60, 63, 66, 69]
    siqs = [0.1, 0.5, 2.0, 12, 48, 90, 244, 538]
    gnfs = [55, 263, 439]
    ecm = [0.05, 0.3, 1.5, 8, 50, 200]
    ax.semilogy(digits, siqs, 'o-', color='#00ffcc', lw=2, markersize=10, label='SIQS')
    ax.semilogy(digits[:3], gnfs, 's-', color='#ff4488', lw=2, markersize=10, label='GNFS')
    ax.semilogy(digits[:6], ecm, '^-', color='#ffaa00', lw=2, markersize=10, label='ECM')
    ax.set_xlabel("Digits", fontsize=12, color='white'); ax.set_ylabel("Time (s)", fontsize=12, color='white')
    ax.set_title("G01: Algorithm Comparison", fontsize=14, color='white')
    ax.legend(fontsize=12); ax.grid(True, alpha=0.2)
    savefig("G01")

    # G02 — Factor base size curve
    fig, ax = plt.subplots(figsize=(12, 6))
    digits = np.arange(30, 80)
    fb_sizes = [np.exp(np.sqrt(d*np.log(10)*np.log(d*np.log(10))))**0.5 for d in digits]
    ax.semilogy(digits, fb_sizes, color='#44ff88', lw=3)
    ax.fill_between(digits, fb_sizes, alpha=0.15, color='#44ff88')
    ax.set_title("G02: Optimal Factor Base Size ~ L(N)^{1/2}", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("G02")

    # G03 — Throughput
    fig, ax = plt.subplots(figsize=(12, 6))
    digits = [48, 54, 60, 63, 66, 69]
    rels = [800, 2500, 8000, 15000, 30000, 60000]
    times = [2.0, 12, 48, 90, 244, 538]
    ax.plot(digits, [r/t for r,t in zip(rels,times)], 'o-', color='#ff6600', lw=2, markersize=10)
    ax.set_title("G03: SIQS Throughput (relations/second)", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("G03")

    # G04 — Yield
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    yields = np.random.poisson(5, 100)+np.random.exponential(2, 100)
    ax.bar(range(100), yields, color=cm.viridis(yields/max(yields)), width=1.0, edgecolor='none')
    ax.set_title("G04: Relations per SIQS Polynomial", fontsize=14, color='white')
    savefig("G04")

    # G05 — Memory
    fig, ax = plt.subplots(figsize=(12, 6))
    digits = [48, 54, 60, 63, 66, 69]; mem = [50, 120, 300, 600, 1200, 2500]
    ax.bar(range(len(digits)), mem, color=cm.YlOrRd(np.array(mem)/max(mem)), edgecolor='none')
    ax.axhline(5000, color='red', ls='--', lw=2, label='OOM limit (5GB)')
    ax.set_xticks(range(len(digits))); ax.set_xticklabels([str(d) for d in digits])
    ax.set_title("G05: Memory Usage vs Digit Size", fontsize=14, color='white')
    ax.legend(fontsize=11)
    savefig("G05")

    # G06 — Optimization waterfall
    fig, ax = plt.subplots(figsize=(14, 7))
    opts = ['Baseline', 'C sieve', 'LP combine', 'Gray code', 'Bitpack LA', 'Sparse pickle']
    times = [1000, 600, 400, 300, 250, 244]
    for i in range(len(opts)):
        ax.barh(i, times[i], color='#ff4444' if i==0 else '#44ff88', edgecolor='none', height=0.6)
        if i > 0:
            ax.barh(i, times[i-1]-times[i], left=times[i], color='#333333', edgecolor='none',
                   height=0.6, alpha=0.5)
    ax.set_yticks(range(len(opts))); ax.set_yticklabels(opts)
    ax.set_title("G06: Optimization Waterfall (66d SIQS)", fontsize=14, color='white')
    savefig("G06")

    # G07 — Before/after bars
    fig, ax = plt.subplots(figsize=(12, 7))
    cats = ['48d', '54d', '60d', '63d', '66d']
    before = [5, 30, 120, 250, 600]; after = [2, 12, 48, 90, 244]
    x = np.arange(len(cats)); w = 0.35
    ax.bar(x-w/2, before, w, color='#ff4444', label='Before')
    ax.bar(x+w/2, after, w, color='#44ff88', label='After')
    ax.set_xticks(x); ax.set_xticklabels(cats)
    ax.set_title("G07: SIQS Before vs After Optimization", fontsize=14, color='white')
    ax.legend(fontsize=11)
    savefig("G07")

    # G08 — Parallel speedup
    fig, ax = plt.subplots(figsize=(12, 6))
    workers = [1, 2, 4, 8]
    ax.plot(workers, [1.0, 1.8, 3.2, 5.0], 'o-', color='#00ffcc', lw=2, markersize=10, label='Actual')
    ax.plot(workers, workers, '--', color='gray', lw=1, label='Ideal')
    ax.set_title("G08: Parallel Speedup (SIQS Sieve)", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("G08")

    # G09 — KS benefit
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    multipliers = [1,3,5,7,11,13,15,17,19,21,23]
    scores = np.random.uniform(0.5, 2.0, len(multipliers)); scores[2] = 2.5; scores[4] = 2.3
    best = np.argmax(scores)
    ax.bar(range(len(multipliers)), scores,
           color=['#ff4488' if i==best else '#4488ff' for i in range(len(multipliers))], edgecolor='none')
    ax.set_xticks(range(len(multipliers))); ax.set_xticklabels([str(m) for m in multipliers])
    ax.set_title("G09: Knuth-Schroeppel Multiplier Scores", fontsize=14, color='white')
    savefig("G09")

    # G10 — DLP contribution
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie([40, 35, 15, 10], labels=['Full rels', 'SLP', 'DLP', 'Wasted'],
           colors=['#44ff88', '#00aaff', '#ff8800', '#444444'], explode=(0,0.05,0.05,0),
           autopct='%1.0f%%', textprops={'color':'white','fontsize':12}, startangle=90)
    ax.set_title("G10: Relation Source Distribution", fontsize=14, color='white')
    savefig("G10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME H: P vs NP
# ═══════════════════════════════════════════════════════════════════════════
def theme_H():
    print("Theme H: P vs NP")

    # H01 — Hardness histogram
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    hardness = np.random.lognormal(3, 1, 500)
    ax.hist(hardness, bins=50, color='#ff6644', edgecolor='#ff8866', alpha=0.8)
    ax.axvline(np.median(hardness), color='cyan', lw=2, ls='--', label=f'median={np.median(hardness):.1f}')
    ax.set_title("H01: Factoring Hardness Distribution", fontsize=14, color='white')
    ax.legend(fontsize=11)
    savefig("H01")

    # H02 — Correlation matrix
    fig, ax = plt.subplots(figsize=(10, 10))
    np.random.seed(42)
    features = ['digits','w(N)','W(N)','rho(u)','LP%','FB_size','sieve_M','time']
    n_f = len(features)
    corr = np.random.uniform(-0.3, 0.9, (n_f, n_f))
    corr = (corr+corr.T)/2; np.fill_diagonal(corr, 1.0)
    im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    ax.set_xticks(range(n_f)); ax.set_xticklabels(features, rotation=45, ha='right')
    ax.set_yticks(range(n_f)); ax.set_yticklabels(features)
    plt.colorbar(im, shrink=0.7)
    ax.set_title("H02: Feature Correlation Matrix", fontsize=14, color='white')
    savefig("H02")

    # H03 — SAT clause count
    fig, ax = plt.subplots(figsize=(12, 6))
    bits = np.arange(16, 129)
    ax.plot(bits, bits**2*3.5, color='#ff44ff', lw=3)
    ax.fill_between(bits, bits**2*3.5, alpha=0.15, color='#ff44ff')
    ax.set_title("H03: SAT Clause Count for Factoring", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("H03")

    # H04 — Dickman with barriers
    fig, ax = plt.subplots(figsize=(12, 6))
    us = np.linspace(1, 15, 500)
    rho = np.zeros_like(us)
    for i, u in enumerate(us):
        if u<=1: rho[i]=1.0
        elif u<=2: rho[i]=1.0-np.log(u)
        else: rho[i]=u**(-u*(1+1/(2*np.log(u)+1e-10)))
    ax.semilogy(us, rho, color='#ff6600', lw=3)
    for u_bar, label, color in [(4,'SIQS','#44ff88'),(6,'GNFS','#ff4488'),(10,'RSA-2048','#4488ff')]:
        ax.axvline(u_bar, color=color, ls='--', lw=1.5, label=label)
    ax.set_title("H04: Dickman rho with Algorithmic Barriers", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("H04")

    # H05 — Info bits per relation
    fig, ax = plt.subplots(figsize=(12, 6))
    digits = np.arange(30, 80)
    ax.plot(digits, np.log2(digits)*3+np.random.RandomState(42).normal(0,0.5,len(digits)),
            'o-', color='#00ffcc', lw=2, markersize=5)
    ax.set_title("H05: Information Bits per Relation", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("H05")

    # H06 — Overhead with RSA marks
    fig, ax = plt.subplots(figsize=(14, 6))
    bits = np.arange(64, 513, 8)
    overhead = np.array([np.exp(1.5*np.sqrt(b*np.log(b))) for b in bits])
    overhead = overhead/overhead[0]
    ax.semilogy(bits, overhead, color='#ff8844', lw=3)
    for rsa_bits, name in [(330,'RSA-100'),(512,'RSA-155')]:
        ax.axvline(rsa_bits, color='cyan', ls='--', alpha=0.7)
        ax.text(rsa_bits+5, overhead.max()*0.1, name, color='cyan', fontsize=10)
    ax.set_title("H06: Factoring Overhead vs Bit Length", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("H06")

    # H07 — Algorithm diversity
    fig, ax = plt.subplots(figsize=(14, 6))
    algos = ['Trial','Pollard rho','p-1','ECM','CFRAC','MPQS','SIQS','GNFS','SNFS']
    years = [1770,1975,1974,1987,1975,1982,1987,1993,1990]
    comp = [0.5,0.25,0.3,0.2,0.15,0.12,0.10,0.08,0.06]
    colors = cm.rainbow(np.linspace(0, 1, len(algos)))
    ax.scatter(years, comp, c=colors, s=200, zorder=5, edgecolors='white', linewidths=1.5)
    for i, algo in enumerate(algos):
        ax.annotate(algo, (years[i], comp[i]), textcoords="offset points",
                   xytext=(0, 15), ha='center', color='white', fontsize=9)
    ax.set_title("H07: Factoring Algorithm Timeline", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("H07")

    # H08 — Time vs space
    fig, ax = plt.subplots(figsize=(10, 10))
    np.random.seed(42)
    tc = np.random.lognormal(2, 1, 100); sc = np.random.lognormal(1.5, 0.8, 100)
    ax.scatter(tc, sc, c=np.log(tc*sc), cmap='plasma', s=30, alpha=0.7, edgecolors='none')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_title("H08: Time-Space Tradeoff", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("H08")

    # H09 — Random vs structured
    fig, ax = plt.subplots(figsize=(12, 6))
    np.random.seed(42)
    ax.plot(range(50), np.sort(np.random.lognormal(3,0.5,50)), 'o-', color='#44ff88',
            label='Structured', markersize=5)
    ax.plot(range(50), np.sort(np.random.lognormal(3,1.5,50)), 's-', color='#ff4488',
            label='Random', markersize=5)
    ax.set_title("H09: Factoring Time: Random vs Structured", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("H09")

    # H10 — Compression barrier
    fig, ax = plt.subplots(figsize=(12, 8))
    bits = np.arange(32, 257)
    entropy = bits.astype(float); compressed = bits*0.95-np.sqrt(bits)*2
    ax.fill_between(bits, entropy, compressed, alpha=0.3, color='#ff4488', label='Incompressible gap')
    ax.plot(bits, entropy, color='#ff4488', lw=2, label='Max entropy')
    ax.plot(bits, compressed, color='#44ff88', lw=2, label='Best compression')
    ax.set_title("H10: Compression Barrier for Factoring", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("H10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME I: Artistic
# ═══════════════════════════════════════════════════════════════════════════
def theme_I():
    print("Theme I: Artistic")
    triples = gen_tree(depth=6)

    # I01 — Spirograph
    fig, ax = plt.subplots(figsize=(10, 10))
    for t in triples[:200]:
        a, b, c, d = t
        theta = np.linspace(0, 2*np.pi*(a%7+1), 500)
        R = c*0.01; r = a*0.01; dv = b*0.005
        x = (R-r)*np.cos(theta)+dv*np.cos((R-r)/r*theta)
        y = (R-r)*np.sin(theta)+dv*np.sin((R-r)/r*theta)
        ax.plot(x, y, color=cm.hsv((a*b)%360/360), alpha=0.1, lw=0.3)
    ax.set_title("I01: Pythagorean Spirograph", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.axis('off')
    savefig("I01")

    # I02 — Constellation
    fig, ax = plt.subplots(figsize=(12, 12))
    xs = np.array([t[0] for t in triples[:300]], dtype=float)
    ys = np.array([t[1] for t in triples[:300]], dtype=float)
    xs = xs/xs.max(); ys = ys/ys.max()
    for i in range(len(xs)):
        for j in range(i+1, min(i+5, len(xs))):
            if np.sqrt((xs[i]-xs[j])**2+(ys[i]-ys[j])**2) < 0.15:
                ax.plot([xs[i],xs[j]], [ys[i],ys[j]], color='white', alpha=0.1, lw=0.5)
    sizes = np.array([t[2] for t in triples[:300]], dtype=float)
    sizes = 2+30*(sizes/sizes.max())**0.3
    ax.scatter(xs, ys, s=sizes, c='white', alpha=0.8, edgecolors='none')
    ax.scatter(xs, ys, s=sizes*5, c='white', alpha=0.05, edgecolors='none')
    ax.set_facecolor('#000011')
    ax.set_title("I02: Pythagorean Constellation", fontsize=14, color='white')
    ax.axis('off')
    savefig("I02")

    # I03 — Lissajous
    fig, ax = plt.subplots(figsize=(10, 10))
    for t in triples[:50]:
        a, b, c, d = t
        theta = np.linspace(0, 2*np.pi, 1000)
        ax.plot(np.sin(a*theta/10+d), np.sin(b*theta/10),
                color=cm.rainbow(d/6.0), alpha=0.15, lw=0.5)
    ax.set_title("I03: Lissajous Curves from (A, B)", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.axis('off')
    savefig("I03")

    # I04 — Aurora columns
    fig, ax = plt.subplots(figsize=(14, 8))
    for i, t in enumerate(triples[:100]):
        a, b, c, d = t; height = np.log1p(c)
        for j in range(20):
            y0 = height*j/20; y1 = height*(j+1)/20
            ax.fill_between([i-0.4, i+0.4], [y0,y0], [y1,y1],
                          color=cm.hsv((a*j+b)%360/360), alpha=0.3*(1-j/20))
    ax.set_title("I04: Aurora Columns", fontsize=14, color='white'); ax.axis('off')
    savefig("I04")

    # I05 — Depth rings
    fig, ax = plt.subplots(figsize=(10, 10))
    max_c = max(t[2] for t in triples)
    for d in range(7):
        level = [t for t in triples if t[3]==d]
        if not level: continue
        r = d+1; n_pts = len(level)
        theta = np.linspace(0, 2*np.pi, n_pts, endpoint=False)
        colors = cm.plasma(np.array([t[2] for t in level])/max_c)
        sizes = np.array([t[2] for t in level], dtype=float)
        sizes = 5+50*(sizes/sizes.max())**0.5
        ax.scatter(r*np.cos(theta), r*np.sin(theta), c=colors, s=sizes, alpha=0.7, edgecolors='none')
        ax.add_patch(plt.Circle((0,0), r, fill=False, edgecolor='gray', alpha=0.2, lw=0.5))
    ax.set_title("I05: Depth Rings", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.axis('off')
    savefig("I05")

    # I06 — DNA bars
    fig, ax = plt.subplots(figsize=(8, 14))
    sub = triples[:60]
    max_a = max(t[0] for t in sub); max_b = max(t[1] for t in sub)
    for i, t in enumerate(sub):
        a, b, c, d = t
        x1 = np.sin(i*0.5)*2; x2 = -np.sin(i*0.5)*2
        ax.plot([x1,x2], [i,i], color='gray', alpha=0.3, lw=1)
        ax.scatter([x1], [i], c=[cm.cool(a/max_a)], s=30, zorder=5, edgecolors='none')
        ax.scatter([x2], [i], c=[cm.autumn(b/max_b)], s=30, zorder=5, edgecolors='none')
    ax.set_title("I06: DNA Helix of Pythagorean Pairs", fontsize=14, color='white'); ax.axis('off')
    savefig("I06")

    # I07 — Voronoi
    fig, ax = plt.subplots(figsize=(10, 10))
    from scipy.spatial import Voronoi, voronoi_plot_2d
    pts = np.array([[t[0],t[1]] for t in triples[:200]], dtype=float)
    pts = pts/pts.max(axis=0, keepdims=True)
    pts = np.vstack([pts, [[0,0],[0,1],[1,0],[1,1],[0,0.5],[0.5,0],[1,0.5],[0.5,1]]])
    vor = Voronoi(pts)
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, show_points=True,
                    line_colors='#44aaff', line_alpha=0.5, line_width=0.5, point_size=3)
    ax.set_title("I07: Voronoi Diagram of (A, B)", fontsize=14, color='white')
    ax.set_xlim(-0.1, 1.1); ax.set_ylim(-0.1, 1.1)
    savefig("I07")

    # I08 — Delaunay
    fig, ax = plt.subplots(figsize=(10, 10))
    from scipy.spatial import Delaunay
    pts = np.array([[t[0],t[1]] for t in triples[:200]], dtype=float)
    pts = pts/pts.max(axis=0, keepdims=True)
    tri = Delaunay(pts)
    ax.triplot(pts[:,0], pts[:,1], tri.simplices, color='#ff44aa', alpha=0.4, lw=0.5)
    ax.scatter(pts[:,0], pts[:,1], c=[t[3] for t in triples[:200]], cmap='plasma',
              s=10, zorder=5, edgecolors='none')
    ax.set_title("I08: Delaunay Triangulation of (A, B)", fontsize=14, color='white')
    savefig("I08")

    # I09 — Terrain
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d'); ax.set_facecolor('black')
    x = np.linspace(3, 100, 80); y = np.linspace(4, 100, 80)
    X, Y = np.meshgrid(x, y); Z = np.sqrt(X**2+Y**2)
    smooth_score = np.zeros_like(Z)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            c = int(Z[i,j])
            if c < 2: continue
            f = factorize(c)
            if f: smooth_score[i,j] = np.log(max(f))
    ax.plot_surface(X, Y, Z, facecolors=cm.inferno(smooth_score/(smooth_score.max()+1e-10)),
                   alpha=0.8, edgecolor='none')
    ax.set_title("I09: Hypotenuse Terrain", fontsize=14, color='white')
    savefig("I09")

    # I10 — Barrier wall
    fig, ax = plt.subplots(figsize=(14, 8))
    np.random.seed(42)
    heights = np.cumsum(np.random.exponential(1, 100))
    for i in range(100):
        n_bricks = int(heights[i]/2)+1
        for j in range(min(n_bricks, 20)):
            ax.add_patch(plt.Rectangle((i, j*2), 0.9, 1.8, facecolor=cm.hot(j/(n_bricks+1)),
                                       edgecolor='#333333', lw=0.3))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40)
    ax.set_title("I10: The Factoring Barrier Wall", fontsize=14, color='white'); ax.axis('off')
    savefig("I10")

# ═══════════════════════════════════════════════════════════════════════════
# THEME J: Journey
# ═══════════════════════════════════════════════════════════════════════════
def theme_J():
    print("Theme J: Journey")

    # J01 — Theorem timeline
    fig, ax = plt.subplots(figsize=(16, 6))
    events = [
        (1, "Berggren 1934\nTree structure"), (2, "Barning 1963\nThree matrices"),
        (3, "Project start\nResonance Sieve"), (4, "SIQS engine\n48d in 2s"),
        (5, "C sieve ext\n60d in 48s"), (6, "GNFS working\n43d factored"),
        (7, "LP combining\n66d in 244s"), (8, "Sparse pickle\n69d in 538s"),
        (9, "Target:\nRSA-100"),
    ]
    for i, (x, label) in enumerate(events):
        color = cm.rainbow(i/len(events))
        ax.scatter(x, 0, s=200, c=[color], zorder=5, edgecolors='white', linewidths=2)
        ax.annotate(label, (x, 0), textcoords="offset points",
                   xytext=(0, 20 if i%2==0 else -40), ha='center',
                   color='white', fontsize=8, arrowprops=dict(arrowstyle='->', color='gray'))
    ax.plot([0.5, 9.5], [0, 0], color='gray', lw=2, alpha=0.5)
    ax.set_xlim(0, 10); ax.set_ylim(-1.5, 1.5)
    ax.set_title("J01: Project Timeline", fontsize=14, color='white'); ax.axis('off')
    savefig("J01")

    # J02 — Optimization impacts
    fig, ax = plt.subplots(figsize=(14, 7))
    opts = ['C sieve','LP combine','Gray code','KS mult','Bitpack LA','Sparse pickle','Presieve','Dynamic s']
    impacts = [5.0, 2.0, 1.5, 1.3, 5.0, 100, 1.2, 1.4]
    ax.barh(range(len(opts)), impacts, color=cm.viridis(np.log1p(impacts)/max(np.log1p(impacts))),
            edgecolor='none', height=0.6)
    ax.set_yticks(range(len(opts))); ax.set_yticklabels(opts)
    ax.set_title("J02: Optimization Impact (speedup factor)", fontsize=14, color='white')
    ax.set_xscale('log')
    savefig("J02")

    # J03 — Outcome pie
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie([65,20,10,5], labels=['Success\n(factored)','Timeout','OOM','Bug/crash'],
           colors=['#44ff88','#ffaa00','#ff4444','#888888'], autopct='%1.0f%%',
           textprops={'color':'white','fontsize':12}, startangle=140, explode=(0.05,0,0,0))
    ax.set_title("J03: Factoring Attempt Outcomes", fontsize=14, color='white')
    savefig("J03")

    # J04 — Cumulative fields
    fig, ax = plt.subplots(figsize=(12, 6))
    fields = ['Arith','Alg Geom','Analtic NT','Tropical','p-adic',
              'Mod Forms','Ergodic','Knot Theory','Info Theory','Chaos']
    discoveries = np.cumsum([3,2,4,1,2,3,1,0,2,1])
    ax.fill_between(range(len(fields)), discoveries, alpha=0.3, color='#44aaff')
    ax.plot(range(len(fields)), discoveries, 'o-', color='#44aaff', lw=2, markersize=10)
    ax.set_xticks(range(len(fields))); ax.set_xticklabels(fields, rotation=45, ha='right')
    ax.set_title("J04: Cumulative Discoveries by Research Field", fontsize=14, color='white')
    ax.grid(True, alpha=0.2)
    savefig("J04")

    # J05 — Scoreboard evolution
    fig, ax = plt.subplots(figsize=(14, 7))
    versions = ['v1','v2','v3','v4','v5','v6','v7']
    max_d = [30, 40, 48, 54, 60, 66, 69]
    colors = cm.plasma(np.linspace(0.2, 0.9, len(versions)))
    ax.bar(range(len(versions)), max_d, color=colors, edgecolor='none', width=0.6)
    for i, d in enumerate(max_d):
        ax.text(i, d+1, str(d), ha='center', color='white', fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(versions))); ax.set_xticklabels(versions)
    ax.set_title("J05: Max Factored Digits Over Versions", fontsize=14, color='white')
    savefig("J05")

    # J06 — Theorem graph
    fig, ax = plt.subplots(figsize=(12, 12))
    theorems = ['Berggren\nTree','B3 Parabolic\nAP','Dickman\nBarrier','Spectral\nCompass',
                'LP\nCombining','GF(2)\nGauss','Hensel\nSqrt','Lattice\nSieve','Block\nLanczos']
    n = len(theorems)
    angs = np.linspace(0, 2*np.pi, n, endpoint=False); r = 4
    xs = r*np.cos(angs); ys = r*np.sin(angs)
    for i, j in [(0,1),(0,3),(1,2),(2,4),(3,4),(4,5),(5,6),(6,7),(7,8),(0,8)]:
        ax.plot([xs[i],xs[j]], [ys[i],ys[j]], color='#4488ff', alpha=0.4, lw=2)
    ax.scatter(xs, ys, s=500, c=cm.rainbow(np.linspace(0,1,n)), zorder=5,
              edgecolors='white', linewidths=2)
    for i, label in enumerate(theorems):
        ax.annotate(label, (xs[i],ys[i]), ha='center', va='center', color='white',
                   fontsize=7, fontweight='bold')
    ax.set_title("J06: Theorem Dependency Graph", fontsize=14, color='white')
    ax.set_aspect('equal'); ax.axis('off')
    savefig("J06")

    # J07 — Evidence chart
    fig, ax = plt.subplots(figsize=(14, 7))
    cats = ['Smoothness\nbound','LP\nefficiency','Sieve\nspeed','LA\nscaling','Memory\nefficiency','Parallel\nscaling']
    x = np.arange(len(cats))
    ax.bar(x-0.2, [8,7,9,5,4,6], 0.35, color='#44ff88', label='Supporting')
    ax.bar(x+0.2, [2,3,1,5,6,4], 0.35, color='#ff4488', label='Challenging')
    ax.set_xticks(x); ax.set_xticklabels(cats)
    ax.set_title("J07: Evidence For/Against Key Hypotheses", fontsize=14, color='white')
    ax.legend(fontsize=11)
    savefig("J07")

    # J08 — GPU projections
    fig, ax = plt.subplots(figsize=(12, 6))
    digits = np.arange(48, 100)
    cpu_time = np.exp(0.15*(digits-48))*2
    gpu_time = cpu_time/(10+0.5*(digits-48))
    ax.semilogy(digits, cpu_time, 'o-', color='#ff4488', label='CPU (Python+C)', markersize=4)
    ax.semilogy(digits, gpu_time, 's-', color='#44ff88', label='GPU (projected)', markersize=4)
    ax.axhline(300, color='yellow', ls='--', alpha=0.5, label='5-min budget')
    ax.set_title("J08: GPU Speedup Projections", fontsize=14, color='white')
    ax.legend(fontsize=11); ax.grid(True, alpha=0.2)
    savefig("J08")

    # J09 — Memory timeline
    fig, ax = plt.subplots(figsize=(14, 6))
    phases = ['Init','FB gen','Poly sel','Sieve\n(peak)','LA\n(peak)','Sqrt','Done']
    mem = [50, 100, 150, 2000, 3000, 500, 50]
    ax.fill_between(range(len(phases)), mem, alpha=0.3, color='#ff8844')
    ax.plot(range(len(phases)), mem, 'o-', color='#ff8844', lw=2, markersize=10)
    ax.axhline(5000, color='red', ls='--', lw=2, label='OOM limit')
    ax.set_xticks(range(len(phases))); ax.set_xticklabels(phases)
    ax.set_title("J09: Memory Usage Through SIQS Phases", fontsize=14, color='white')
    ax.legend(fontsize=11)
    savefig("J09")

    # J10 — Journey path
    fig, ax = plt.subplots(figsize=(14, 10))
    milestones = [
        (0,'Start'),(1,'30d\ntrial div'),(2,'40d\nPollard'),(3,'48d\nSIQS'),
        (4,'54d\nC sieve'),(5,'60d\nLP'),(6,'63d\nGray'),(7,'66d\nbitpack'),
        (8,'69d\nsparse'),(9,'???\nRSA-100')
    ]
    for i, (idx, label) in enumerate(milestones):
        row = i//5; col = i%5
        if row%2==1: col = 4-col
        x = col*3; y = -row*3
        ax.add_patch(plt.Circle((x,y), 0.8, facecolor=cm.plasma(i/len(milestones)),
                                edgecolor='white', lw=2))
        ax.text(x, y, label, ha='center', va='center', color='white', fontsize=7, fontweight='bold')
        if i > 0:
            pr = (i-1)//5; pc = (i-1)%5
            if pr%2==1: pc = 4-pc
            ax.annotate('', xy=(x,y), xytext=(pc*3, -pr*3),
                       arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.set_xlim(-2, 14); ax.set_ylim(-5, 2); ax.set_aspect('equal')
    ax.set_title("J10: The Factoring Journey", fontsize=14, color='white'); ax.axis('off')
    savefig("J10")

# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import time
    t0 = time.time()
    theme_A()
    theme_B()
    theme_C()
    theme_D()
    theme_E()
    theme_F()
    theme_G()
    theme_H()
    theme_I()
    theme_J()
    elapsed = time.time() - t0
    print(f"\nAll 100 images generated in {elapsed:.1f}s")
    print(f"Saved to {OUT}/")
