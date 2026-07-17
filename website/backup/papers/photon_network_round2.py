#!/usr/bin/env python3
"""
PHOTON NETWORK EXPLORATION — Round 2: Deep Dive into Network Structure
======================================================================

Key findings from Round 1:
- ~57-72% of integers are "dark" (no sum-of-two-squares representation)
- Darkness criterion: has prime factor ≡ 3 (mod 4) to an odd power
- The number of representations follows prod(ei+1) for split primes
- Networks appear mostly disconnected under the Gaussian quotient edge rule

Round 2 explores:
1. Better edge relations that capture the Gaussian factorization hypercube
2. The precise structure of photon networks for products of split primes
3. Why some networks are connected and others disconnected
4. The graph-theoretic properties (diameter, degree distribution)
"""

from math import gcd, isqrt, sqrt, log
from collections import defaultdict
from itertools import product as cartesian_product

def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def gaussian_multiply(z1, z2):
    return (z1[0]*z2[0] - z1[1]*z2[1], z1[0]*z2[1] + z1[1]*z2[0])

def gaussian_norm_sq(z):
    return z[0]**2 + z[1]**2

def find_gaussian_prime(p):
    """For prime p ≡ 1 mod 4, find a+bi with a²+b²=p, a > b > 0."""
    if p == 2:
        return (1, 1)
    for a in range(1, isqrt(p)+1):
        b_sq = p - a*a
        b = isqrt(b_sq)
        if b*b == b_sq and b > 0 and a >= b:
            return (a, b)
    return None

def all_sum2sq(n):
    """All (a,b) with a²+b²=n, a≥0, b≥0."""
    reps = []
    for a in range(isqrt(n)+1):
        b_sq = n - a*a
        if b_sq < 0:
            break
        b = isqrt(b_sq)
        if b*b == b_sq:
            reps.append((a, b))
    return reps

# ============================================================
# DEEP DIVE 1: The Hypercube Structure
# ============================================================
print("=" * 70)
print("DEEP DIVE 1: The Gaussian Factorization Hypercube")
print("=" * 70)

def build_gaussian_hypercube(n):
    """
    Build the photon network as a labeled hypercube.
    
    For n = 2^a0 * p1^a1 * ... * pk^ak * q1^b1 * ...
    where pi ≡ 1 mod 4, qj ≡ 3 mod 4 (bj even):
    
    In Z[i], pi = πi * π̄i where πi = ai + bi*i.
    The factor pi^ei contributes ei+1 choices: 
    use j copies of πi and (ei-j) copies of π̄i, for j=0,...,ei.
    
    Vertex set: product of {0,...,e1} × {0,...,e2} × ...
    Edge set: vertices differing in exactly one coordinate by exactly 1.
    
    This is a GRID GRAPH (Hamming graph / rook's graph on a product of paths).
    """
    factors = factorize(n)
    
    # Check if n is sum of 2 squares
    for p, e in factors.items():
        if p % 4 == 3 and e % 2 == 1:
            return None, None, None, "DARK"
    
    split_primes = sorted([(p, e) for p, e in factors.items() if p % 4 == 1])
    
    if not split_primes:
        # No split primes: only one representation (up to signs)
        return [((),)], [], {(): None}, "TRIVIAL"
    
    # Find Gaussian primes for each split prime
    gaussian_primes = {}
    for p, e in split_primes:
        gp = find_gaussian_prime(p)
        gaussian_primes[p] = gp
    
    # Build vertex set
    ranges = [range(e+1) for p, e in split_primes]
    vertices = list(cartesian_product(*ranges))
    
    # Build edge set (grid graph: differ in one coordinate by 1)
    edges = []
    for v in vertices:
        for dim in range(len(split_primes)):
            # Try incrementing this coordinate by 1
            if v[dim] < split_primes[dim][1]:
                w = list(v)
                w[dim] = v[dim] + 1
                w = tuple(w)
                edges.append((v, w))
    
    # Compute the Gaussian integer for each vertex
    vertex_to_gaussian = {}
    for v in vertices:
        z = (1, 0)
        # Multiply by appropriate Gaussian primes
        for dim, (p, e) in enumerate(split_primes):
            k = v[dim]  # number of π copies (vs π̄)
            gp = gaussian_primes[p]
            gp_conj = (gp[0], -gp[1])
            for _ in range(k):
                z = gaussian_multiply(z, gp)
            for _ in range(e - k):
                z = gaussian_multiply(z, gp_conj)
        
        # Handle prime 2 (ramifies as -i(1+i)²)
        if 2 in factors:
            a = factors[2]
            power_of_1pi = (1, 1)  # 1+i
            for _ in range(a):
                z = gaussian_multiply(z, power_of_1pi)
        
        # Handle inert primes (ℤ-multiples)
        for p, e in factors.items():
            if p % 4 == 3:
                factor = p ** (e // 2)
                z = (z[0] * factor, z[1] * factor)
        
        vertex_to_gaussian[v] = z
    
    return vertices, edges, vertex_to_gaussian, split_primes

print("\nHypercube structure of photon networks:\n")
for n in [5, 13, 17, 25, 29, 37, 41, 50, 65, 85, 125, 130, 145, 
          169, 170, 185, 221, 250, 289, 325, 425, 650, 845, 1105, 
          1625, 2210, 5525]:
    result = build_gaussian_hypercube(n)
    if result[3] == "DARK":
        continue
    vertices, edges, v2g, info = result
    if info == "TRIVIAL":
        print(f"  n={n:5d}: TRIVIAL (no split primes)")
        continue
    
    # Determine graph type
    dims = [e for _, e in info]
    total_v = len(vertices)
    total_e = len(edges)
    
    # Is it connected?
    # A grid graph P_{d1+1} × P_{d2+1} × ... is ALWAYS connected
    graph_type = " × ".join([f"P_{d+1}" for d in dims])
    
    print(f"  n={n:5d}: Grid graph {graph_type}, "
          f"|V|={total_v}, |E|={total_e}, "
          f"split_primes={info}")
    
    if total_v <= 12:
        for v in vertices:
            z = v2g[v]
            norm = z[0]**2 + z[1]**2
            print(f"    {v} → z = {z[0]}+{z[1]}i, |z|² = {norm}")

# ============================================================
# DEEP DIVE 2: Connectivity Theorem
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 2: Connectivity Theorem")
print("=" * 70)

print("""
THEOREM: The photon network of n is ALWAYS connected (when it exists).

PROOF SKETCH:
The photon network of n is isomorphic to the grid graph
  P_{e1+1} × P_{e2+1} × ... × P_{ek+1}
where n = p1^e1 * p2^e2 * ... * pk^ek (only primes ≡ 1 mod 4).

Grid graphs (Cartesian products of paths) are always connected 
because you can walk from any vertex to any other by changing 
one coordinate at a time.

From vertex (j1,...,jk) to (j1',...,jk'), you change coordinates
one by one: first walk j1→j1', then j2→j2', etc.
Each step changes one Gaussian prime factor from π to π̄ (or vice versa).
""")

# Verify computationally
print("Verification: checking connectivity for all n ≤ 1000...")
all_connected = True
for n in range(1, 1001):
    factors = factorize(n)
    is_dark = any(p % 4 == 3 and e % 2 == 1 for p, e in factors.items())
    if is_dark:
        continue
    
    result = build_gaussian_hypercube(n)
    if result[3] == "DARK" or result[3] == "TRIVIAL":
        continue
    
    vertices, edges, _, _ = result
    if len(vertices) <= 1:
        continue
    
    # Check connectivity via BFS
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    
    visited = set()
    queue = [vertices[0]]
    visited.add(vertices[0])
    while queue:
        curr = queue.pop(0)
        for nb in adj[curr]:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    
    if len(visited) != len(vertices):
        print(f"  DISCONNECTED at n={n}!")
        all_connected = False

if all_connected:
    print("  ✓ ALL photon networks are connected for n ≤ 1000")

# ============================================================
# DEEP DIVE 3: Graph-Theoretic Properties
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 3: Graph-Theoretic Properties of Photon Networks")
print("=" * 70)

print("\nProperties of photon networks for selected n:")
print(f"{'n':>6} {'type':>20} {'|V|':>5} {'|E|':>5} {'diam':>5} {'max_deg':>8} {'chromatic':>9}")

for n in [5, 13, 25, 50, 65, 85, 125, 169, 325, 625, 845, 1105, 1625, 5525]:
    result = build_gaussian_hypercube(n)
    if result[3] == "DARK" or result[3] == "TRIVIAL":
        continue
    vertices, edges, _, info = result
    
    dims = [e for _, e in info]
    graph_type = "×".join([f"P{d+1}" for d in dims])
    
    # Compute diameter (sum of (di))
    diameter = sum(dims)
    
    # Max degree (sum of min(ji, di-ji) possible moves... actually each vertex has
    # degree = sum of (1 if dim[i]>0 and ji>0) + (1 if dim[i]>0 and ji<dim[i]))
    # For a grid graph, max degree = 2 * k (number of dimensions with size > 1)
    # But for paths P2, each internal vertex has degree 2, boundary has degree 1
    # Max degree in grid = sum of (2 if dim[i]>=2, 1 if dim[i]==1)
    # Actually: degree of (j1,...,jk) = sum over i of (1 if ji>0) + (1 if ji<di)
    max_deg = sum(min(2, d) for d in dims)
    
    # Chromatic number of grid graph = 2 (bipartite)
    chromatic = 2 if all(d >= 1 for d in dims) else 1
    
    print(f"{n:>6} {graph_type:>20} {len(vertices):>5} {len(edges):>5} {diameter:>5} {max_deg:>8} {chromatic:>9}")

# ============================================================
# DEEP DIVE 4: Dark Photon Analysis 
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 4: Dark Photon Taxonomy")
print("=" * 70)

print("\nClassification of dark integers by their 'darkness source':")
print("\nSingle dark prime (one prime ≡ 3 mod 4 to odd power):")
single_dark = []
multi_dark = []
for n in range(1, 201):
    factors = factorize(n)
    dark_primes = [(p, e) for p, e in factors.items() if p % 4 == 3 and e % 2 == 1]
    if len(dark_primes) == 1:
        single_dark.append((n, dark_primes[0]))
    elif len(dark_primes) > 1:
        multi_dark.append((n, dark_primes))

print(f"  Count (n≤200): {len(single_dark)}")
print(f"  Examples: {[(n, dp) for n, dp in single_dark[:15]]}")
print(f"\nMultiple dark primes:")  
print(f"  Count (n≤200): {len(multi_dark)}")
print(f"  Examples: {[(n, dps) for n, dps in multi_dark[:15]]}")

# ============================================================
# DEEP DIVE 5: Photon Network Diameter Distribution
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 5: What Controls the Diameter?")
print("=" * 70)

print("\nDiameter = sum of exponents of primes ≡ 1 mod 4 in factorization of n")
print("\nExamples:")
for n in [5, 25, 125, 625, 65, 325, 1625, 85, 425, 1105, 5525]:
    factors = factorize(n)
    split = [(p, e) for p, e in factors.items() if p % 4 == 1]
    if split:
        diam = sum(e for _, e in split)
        nv = 1
        for _, e in split:
            nv *= (e + 1)
        print(f"  n={n:5d}: split primes {split}, diameter={diam}, "
              f"|V|={nv}, shape={'×'.join([f'P{e+1}' for _,e in split])}")

# ============================================================
# DEEP DIVE 6: Pythagorean Triple Network (Hypotenuse View)
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 6: Pythagorean Triple Networks")
print("=" * 70)

print("""
For an integer c, the PYTHAGOREAN PHOTON NETWORK is:
- Vertices: all (a,b) with a²+b²=c², a>0, b>0
- Edges: Gaussian prime factor swap (conjugation)

This is the photon network of n=c², restricted to non-axis representations.
""")

for c in [5, 10, 13, 15, 17, 20, 25, 29, 30, 35, 37, 39, 41, 45, 50, 
          51, 53, 55, 60, 65, 75, 85, 100, 125]:
    c_sq = c * c
    reps = all_sum2sq(c_sq)
    # Filter to a > 0, b > 0
    nontriv = [(a, b) for a, b in reps if a > 0 and b > 0]
    if nontriv:
        factors_c = factorize(c)
        factors_csq = factorize(c_sq)
        split_c = [(p, e) for p, e in factors_c.items() if p % 4 == 1]
        diam_csq = sum(2*e for _, e in split_c)  # doubled exponents in c²
        nv_csq = 1
        for _, e in split_c:
            nv_csq *= (2*e + 1)
        print(f"  c={c:4d}: {len(nontriv)} Pyth triples, "
              f"full network |V|={nv_csq} (diam={diam_csq}), "
              f"split_primes_of_c={split_c}")
        if len(nontriv) <= 8:
            for a, b in nontriv:
                g = gcd(a, gcd(b, c))
                print(f"    ({a}, {b}, {c})  gcd={g}  {'primitive' if g==1 else ''}")

# ============================================================
# DEEP DIVE 7: The "Brightness" Spectrum
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 7: Brightness Spectrum")
print("=" * 70)

print("""
Define the BRIGHTNESS of n as the number of non-trivial photon states:
  brightness(n) = #{(a,b) : a²+b²=n, a>0, b>0}
  = (r₂(n) - #axis_reps) / 4  [accounting for sign/swap symmetries]

Dark integers have brightness 0.
""")

brightness_table = {}
for n in range(1, 501):
    reps = all_sum2sq(n)
    nontriv = [(a,b) for a,b in reps if a > 0 and b > 0 and a < b]
    brightness_table[n] = len(nontriv)

print("Brightness distribution for n ≤ 500:")
from collections import Counter
bright_dist = Counter(brightness_table.values())
for k in sorted(bright_dist.keys()):
    examples = [n for n in range(1, 501) if brightness_table[n] == k][:10]
    print(f"  brightness {k}: {bright_dist[k]} integers, examples: {examples}")

# ============================================================
# DEEP DIVE 8: The 1105 Network — First n with 4 distinct split primes
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 8: The 1105 Network — Richest Small Photon Network")
print("=" * 70)

n = 1105
factors = factorize(n)
print(f"\nn = 1105 = {factors}")
print(f"  = 5 × 13 × 17")
print(f"  All primes ≡ 1 mod 4!")
print(f"  Split primes: 5=(2+i)(2-i), 13=(3+2i)(3-2i), 17=(4+i)(4-i)")

reps = all_sum2sq(n)
print(f"\n  All representations {n} = a² + b²:")
for a, b in reps:
    print(f"    {a}² + {b}² = {a**2 + b**2}  ← ({a}, {b})")

result = build_gaussian_hypercube(n)
vertices, edges, v2g, info = result
print(f"\n  Hypercube: {len(vertices)} vertices, {len(edges)} edges")
print(f"  Grid graph: P2 × P2 × P2 = 3-dimensional cube!")
print(f"  Diameter: {sum(e for _,e in info)}")

print("\n  Vertex labels (hypercube coordinates → Gaussian integers):")
for v in sorted(vertices):
    z = v2g[v]
    norm = z[0]**2 + z[1]**2
    print(f"    {v} → z = {z[0]} + {z[1]}i, |z|² = {norm}")

print("\n  Edge list:")
for u, v in edges:
    zu, zv = v2g[u], v2g[v]
    print(f"    {u}--{v}  ({zu[0]}+{zu[1]}i ↔ {zv[0]}+{zv[1]}i)")

# ============================================================
# DEEP DIVE 9: Isolated (Degree-0) Vertices?
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 9: Can Vertices Be Isolated?")
print("=" * 70)

print("""
In the grid graph model, a vertex is isolated iff all dimensions have size 1.
This means all split prime exponents are 0 — but then n has no split primes.

THEOREM: Every vertex in a non-trivial photon network has degree ≥ 1.
(Because if n has at least one split prime p^e with e ≥ 1, every vertex 
can change at least one coordinate.)

So there are NO "dark photons within a bright network" — all photon states 
within a connected network are reachable.
""")

# ============================================================
# DEEP DIVE 10: Sum-of-Two-Squares: The Photon Lattice
# ============================================================
print("\n" + "=" * 70)
print("DEEP DIVE 10: The Photon Lattice")
print("=" * 70)

print("""
KEY INSIGHT: The integers that ARE sums of two squares form a multiplicative 
set (closed under multiplication), because the Brahmagupta-Fibonacci identity
shows that (a₁²+b₁²)(a₂²+b₂²) = c²+d².

But they do NOT form an additive set: 1 + 3 = 4 (light + dark = light),
and 1 + 2 = 3 (light + light = dark).

The "photon-representable" integers S = {n : n = a² + b²} satisfy:
  - S is closed under multiplication ✓
  - S is NOT closed under addition ✗
  - S contains all primes ≡ 1 mod 4 ✓
  - S contains 2 = 1² + 1² ✓
  - S does NOT contain any prime ≡ 3 mod 4 ✓
  - n ∈ S iff all primes ≡ 3 mod 4 in factorization of n appear to even power ✓
""")

# Verify multiplicative closure
print("Verification: S is closed under multiplication (n,m ≤ 100):")
violations = 0
for n in range(1, 101):
    if not any(True for a in range(isqrt(n)+1) if (n-a*a) >= 0 and isqrt(n-a*a)**2 == n-a*a):
        continue
    for m in range(1, 101):
        if not any(True for a in range(isqrt(m)+1) if (m-a*a) >= 0 and isqrt(m-a*a)**2 == m-a*a):
            continue
        nm = n * m
        is_s = any(True for a in range(isqrt(nm)+1) if (nm-a*a) >= 0 and isqrt(nm-a*a)**2 == nm-a*a)
        if not is_s:
            print(f"  VIOLATION: {n} × {m} = {nm} not in S!")
            violations += 1
if violations == 0:
    print("  ✓ Multiplicative closure verified for all pairs n,m ≤ 100")

print("\n\nDONE — Round 2 Complete")
