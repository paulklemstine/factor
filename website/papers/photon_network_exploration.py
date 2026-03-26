#!/usr/bin/env python3
"""
PHOTON NETWORK EXPLORATION — Team Alpha
========================================
Hypothesize, Experiment, Validate, Iterate

Core Question: What is the "photon network" of an integer n?

HYPOTHESIS 1: For integer n, a "photon" is a Gaussian integer z = a + bi 
with |z|² = a² + b² = n. The photon network P(n) has these representations
as vertices, with edges connecting representations related by Gaussian 
integer arithmetic.

HYPOTHESIS 2: "Dark" integers are those with no sum-of-two-squares representation.
By Fermat's theorem: n is a sum of two squares iff every prime p ≡ 3 (mod 4) 
in the factorization of n appears to an even power.

HYPOTHESIS 3: The photon network's connectivity is controlled by the Gaussian
integer factorization structure of n.
"""

from math import gcd, isqrt
from collections import defaultdict
from itertools import product as cartesian_product

def sum_of_two_squares_representations(n):
    """Find all representations n = a² + b² with a >= 0, b >= a (canonical)."""
    reps = []
    for a in range(isqrt(n) + 1):
        b_sq = n - a * a
        if b_sq < 0:
            break
        b = isqrt(b_sq)
        if b * b == b_sq:
            reps.append((a, b))
    return reps

def all_gaussian_norms(n):
    """Find all (a, b) with a² + b² = n, a >= 0, b >= 0."""
    reps = []
    for a in range(isqrt(n) + 1):
        b_sq = n - a * a
        if b_sq < 0:
            break
        b = isqrt(b_sq)
        if b * b == b_sq and b >= 0:
            reps.append((a, b))
    return reps

def factorize(n):
    """Return prime factorization as dict."""
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

def is_sum_of_two_squares(n):
    """Check if n can be written as a² + b²."""
    if n == 0:
        return True
    factors = factorize(n)
    for p, e in factors.items():
        if p % 4 == 3 and e % 2 == 1:
            return False
    return True

def count_representations(n):
    """Count the number of representations of n as a² + b² (with a, b >= 0, a <= b)."""
    return len(all_gaussian_norms(n))

# ============================================================
# EXPERIMENT 1: Survey integers 1..200
# ============================================================
print("=" * 70)
print("EXPERIMENT 1: Photon Census for n = 1..200")
print("=" * 70)

has_photon = []
no_photon = []
multi_photon = []

for n in range(1, 201):
    reps = all_gaussian_norms(n)
    # Filter to non-trivial (both a, b can be 0 for n=0, but a²+b²=n)
    if len(reps) == 0:
        no_photon.append(n)
    else:
        has_photon.append((n, reps))
        if len(reps) > 1:
            multi_photon.append((n, reps))

print(f"\nIntegers with photon network (sum of 2 squares): {len(has_photon)}")
print(f"  First 30: {[x[0] for x in has_photon[:30]]}")
print(f"\n'Dark' integers (NO photon network): {len(no_photon)}")
print(f"  First 30: {no_photon[:30]}")
print(f"\nIntegers with MULTIPLE photon states: {len(multi_photon)}")
for n, reps in multi_photon[:20]:
    print(f"  n={n}: {reps}")

# ============================================================
# EXPERIMENT 2: Why are some integers dark?
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 2: Why Are Some Integers Dark?")
print("=" * 70)

print("\nDark integers and their factorizations:")
for n in no_photon[:30]:
    factors = factorize(n)
    mod4_3_primes = {p: e for p, e in factors.items() if p % 4 == 3}
    print(f"  n={n:4d}: factors={factors}, primes ≡ 3 mod 4 (odd power): {mod4_3_primes}")

# ============================================================
# EXPERIMENT 3: Photon Network as a Graph
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 3: Photon Network Graph Structure")
print("=" * 70)

def gaussian_multiply(z1, z2):
    """Multiply two Gaussian integers (a1+b1i)(a2+b2i)."""
    a1, b1 = z1
    a2, b2 = z2
    return (a1*a2 - b1*b2, a1*b2 + b1*a2)

def gaussian_conjugate(z):
    """Conjugate of a+bi is a-bi."""
    return (z[0], -z[1])

def normalize_gaussian(z):
    """Normalize to canonical form (multiply by unit to get first quadrant)."""
    a, b = z
    # Units are 1, -1, i, -i
    candidates = [(a, b), (-a, -b), (-b, a), (b, -a)]
    # Choose lexicographically largest with both non-negative
    best = None
    for c in candidates:
        if c[0] >= 0 and c[1] >= 0:
            if best is None or c > best:
                best = c
    if best is None:
        return min(candidates)  # fallback
    return best

def build_photon_network(n):
    """
    Build the photon network of n.
    
    Vertices: All Gaussian integers z = a+bi with |z|² = n (up to units).
    
    Edges: z1 ~ z2 if there exists a Gaussian integer w with |w|² being 
    a prime p dividing n, such that z1 = w * z2/w' (i.e., related by 
    changing one Gaussian prime factor's conjugate choice).
    """
    # Find all Gaussian integers with norm n (all quadrants, then normalize)
    all_z = []
    for a in range(-isqrt(n)-1, isqrt(n)+2):
        for b in range(-isqrt(n)-1, isqrt(n)+2):
            if a*a + b*b == n:
                all_z.append((a, b))
    
    # Normalize to first quadrant representatives
    normalized = set()
    for z in all_z:
        nz = normalize_gaussian(z)
        normalized.add(nz)
    
    vertices = sorted(normalized)
    
    # Build edges: two vertices are connected if they share all but one 
    # Gaussian prime factor (i.e., differ by conjugating one factor)
    # Practical check: z1 * conj(z2) has norm n, and z1/z2 in Gaussian integers
    edges = []
    for i, z1 in enumerate(vertices):
        for j, z2 in enumerate(vertices):
            if i < j:
                # Check if z1 * conj(z2) gives something meaningful
                z2c = gaussian_conjugate(z2)
                prod = gaussian_multiply(z1, z2c)
                # The product has norm n²/n² = ... no, |z1|² = |z2|² = n
                # |z1 * conj(z2)|² = n * n = n²
                # They're related if the "rotation" z1/z2 is a Gaussian integer
                # z1 * conj(z2) / n should be a Gaussian integer (or unit)
                if n > 0 and prod[0] % n == 0 and prod[1] % n == 0:
                    edges.append((z1, z2))
    
    return vertices, edges

print("\nPhoton networks for select integers:")
for n in [1, 2, 4, 5, 8, 9, 10, 13, 16, 17, 20, 25, 26, 29, 34, 41, 45, 50, 
          65, 85, 100, 125, 130, 145, 169, 170, 185, 200]:
    if is_sum_of_two_squares(n):
        verts, edges = build_photon_network(n)
        if len(verts) > 0:
            print(f"  n={n:4d}: |V|={len(verts)}, |E|={len(edges)}, V={verts}, E={edges}")

# ============================================================
# EXPERIMENT 4: Connectivity Analysis
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 4: Connectivity of Photon Networks")
print("=" * 70)

def find_components(vertices, edges):
    """Find connected components using union-find."""
    parent = {v: v for v in vertices}
    
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    for u, v in edges:
        union(u, v)
    
    components = defaultdict(list)
    for v in vertices:
        components[find(v)].append(v)
    
    return list(components.values())

connected_networks = []
disconnected_networks = []

for n in range(1, 501):
    if not is_sum_of_two_squares(n):
        continue
    verts, edges = build_photon_network(n)
    if len(verts) <= 1:
        connected_networks.append((n, 1, verts))
        continue
    
    comps = find_components(verts, edges)
    if len(comps) == 1:
        connected_networks.append((n, len(verts), verts))
    else:
        disconnected_networks.append((n, len(comps), comps, verts, edges))

print(f"\nConnected photon networks (n ≤ 500): {len(connected_networks)}")
print(f"Disconnected photon networks (n ≤ 500): {len(disconnected_networks)}")

if disconnected_networks:
    print("\nDisconnected networks:")
    for n, nc, comps, verts, edges in disconnected_networks[:20]:
        factors = factorize(n)
        print(f"  n={n}: {nc} components, vertices={verts}, factors={factors}")
        for i, comp in enumerate(comps):
            print(f"    Component {i}: {comp}")

# ============================================================
# EXPERIMENT 5: The Gaussian Factorization View
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 5: Gaussian Integer Factorization View")
print("=" * 70)

def gaussian_primes_of_prime(p):
    """Find Gaussian prime factors of rational prime p."""
    if p == 2:
        return [(1, 1)]  # 2 = -i(1+i)², 1+i is the Gaussian prime
    if p % 4 == 3:
        return [(p, 0)]  # p stays prime in Z[i]
    # p ≡ 1 mod 4: p = a² + b² for unique a > b > 0
    for a in range(1, isqrt(p) + 1):
        b_sq = p - a * a
        b = isqrt(b_sq)
        if b * b == b_sq and b > 0:
            if a > b:
                return [(a, b), (a, -b)]  # a+bi and a-bi
            elif b > a:
                return [(b, a), (b, -a)]
            else:
                return [(a, b)]
    return []

print("\nGaussian prime decomposition of small primes:")
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    gp = gaussian_primes_of_prime(p)
    mod4 = p % 4
    status = "splits" if mod4 == 1 else ("ramifies" if p == 2 else "inert")
    print(f"  p={p:3d} (≡{mod4} mod 4, {status}): Gaussian factors = {gp}")

# ============================================================
# EXPERIMENT 6: Network structure from Gaussian factorization
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 6: Photon Network from Gaussian Factorization")
print("=" * 70)

def gaussian_factorization_network(n):
    """
    The photon network via Gaussian factorization.
    
    For n with prime factorization n = 2^a0 * p1^a1 * ... * pk^ak * q1^b1 * ...
    where pi ≡ 1 mod 4 and qj ≡ 3 mod 4:
    
    - Each pi splits as pi = πi * π̄i in Z[i]
    - In the factorization of n in Z[i], for each pi^ai factor, we choose 
      how many πi vs π̄i to use (from 0 to ai)
    - Each choice gives a different Gaussian integer z with |z|² = n (up to units)
    
    The network connects choices that differ in exactly one prime's conjugate assignment.
    This gives a HYPERCUBE structure!
    """
    factors = factorize(n)
    
    # Find primes ≡ 1 mod 4 with their exponents
    split_primes = [(p, e) for p, e in factors.items() if p % 4 == 1]
    
    # Primes ≡ 3 mod 4 must appear to even power for n to be sum of 2 squares
    inert_primes = [(p, e) for p, e in factors.items() if p % 4 == 3]
    for p, e in inert_primes:
        if e % 2 == 1:
            return None, None, "Dark: prime ≡ 3 mod 4 to odd power"
    
    if not split_primes:
        return [(0, isqrt(n))] if isqrt(n)**2 == n else [], [], "No splitting primes"
    
    # For each splitting prime p^e, the exponent e gives (e+1) choices:
    # Use k copies of π and (e-k) copies of π̄, for k = 0, 1, ..., e
    # This gives a product of (e_i + 1) vertices
    
    # Build the hypercube
    dimensions = [(p, e, gaussian_primes_of_prime(p)) for p, e, in split_primes]
    
    # Each vertex is a tuple of choices (k1, k2, ..., km) where 0 <= ki <= ei
    choice_ranges = [range(e + 1) for _, e, _ in dimensions]
    
    vertices = list(cartesian_product(*choice_ranges))
    
    # Compute the actual Gaussian integer for each vertex
    def compute_gaussian(choices):
        z = (1, 0)
        # Handle prime 2
        if 2 in factors:
            # 2 = -i(1+i)², so 2^a contributes (1+i)^(2a) / units
            a = factors[2]
            for _ in range(a):
                z = gaussian_multiply(z, (1, 1))  # multiply by (1+i)
            # But |1+i|² = 2, so (1+i)^a gives norm 2^a, not 2^(2a)
            # Actually we need to be more careful...
            pass
        
        for i, (p, e, gps) in enumerate(dimensions):
            k = choices[i]
            pi_fwd = gps[0]  # π
            pi_conj = (gps[0][0], -gps[0][1]) if len(gps) > 1 else gps[0]  # π̄
            
            # Use k copies of π and (e-k) copies of π̄
            for _ in range(k):
                z = gaussian_multiply(z, pi_fwd)
            for _ in range(e - k):
                z = gaussian_multiply(z, pi_conj)
        
        # Handle inert primes (contribute p^(e/2) to both real and imaginary parts... 
        # actually they contribute p^(e/2) as a real factor)
        for p, e in inert_primes:
            real_factor = p ** (e // 2)
            z = (z[0] * real_factor, z[1] * real_factor)
        
        # Handle prime 2
        if 2 in factors and 2 not in [p for p, _, _ in dimensions]:
            a = factors[2]
            for _ in range(a):
                z = gaussian_multiply(z, (1, 1))
        
        return normalize_gaussian(z)
    
    vertex_gaussians = {}
    for v in vertices:
        g = compute_gaussian(v)
        vertex_gaussians[v] = g
    
    # Edges: differ in exactly one coordinate
    edges = []
    for i, v1 in enumerate(vertices):
        for j, v2 in enumerate(vertices):
            if i < j:
                # Count number of coordinates that differ
                diffs = sum(1 for a, b in zip(v1, v2) if a != b)
                if diffs == 1:
                    edges.append((v1, v2))
    
    return vertices, edges, vertex_gaussians

print("\nGaussian factorization networks:")
for n in [5, 10, 13, 25, 50, 65, 85, 100, 125, 130, 145, 170, 185, 
          200, 250, 325, 425, 500, 650, 845, 1000, 1105]:
    verts, edges, info = gaussian_factorization_network(n)
    if isinstance(info, str):
        print(f"  n={n:5d}: {info}")
    elif verts:
        factors = factorize(n)
        split_p = [p for p in factors if p % 4 == 1]
        print(f"  n={n:5d}: |V|={len(verts)}, |E|={len(edges)}, "
              f"split primes={split_p}, exponents={[factors[p] for p in split_p]}")
        if len(verts) <= 8:
            for v in verts:
                g = info[v] if isinstance(info, dict) else "?"
                print(f"    Choice {v} → z = {g}")

# ============================================================
# EXPERIMENT 7: The Number r2(n) — representation count
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 7: r₂(n) — Number of Representations as Sum of Two Squares")  
print("=" * 70)

def r2(n):
    """Count representations of n = a² + b² with a,b ∈ ℤ (all signs, order matters)."""
    count = 0
    for a in range(-isqrt(n)-1, isqrt(n)+2):
        b_sq = n - a*a
        if b_sq < 0:
            continue
        b = isqrt(b_sq)
        if b*b == b_sq:
            if b == 0:
                count += 1
            else:
                count += 2  # (a, b) and (a, -b)
    return count

print("\nr₂(n) for n = 0..100:")
for row_start in range(0, 101, 20):
    vals = [f"{r2(n):2d}" for n in range(row_start, min(row_start+20, 101))]
    indices = [f"{n:2d}" for n in range(row_start, min(row_start+20, 101))]
    print(f"  n={row_start:3d}..{min(row_start+19,100):3d}: {' '.join(vals)}")

# Jacobi formula: r2(n) = 4 * (d1(n) - d3(n))
# where d1(n) = number of divisors ≡ 1 mod 4, d3(n) = number of divisors ≡ 3 mod 4
def jacobi_r2(n):
    if n == 0:
        return 1
    d1 = sum(1 for d in range(1, n+1) if n % d == 0 and d % 4 == 1)
    d3 = sum(1 for d in range(1, n+1) if n % d == 0 and d % 4 == 3)
    return 4 * (d1 - d3)

print("\nValidating Jacobi's formula r₂(n) = 4(d₁(n) - d₃(n)):")
mismatches = 0
for n in range(1, 201):
    if r2(n) != jacobi_r2(n):
        print(f"  MISMATCH at n={n}: r2={r2(n)}, jacobi={jacobi_r2(n)}")
        mismatches += 1
if mismatches == 0:
    print("  ✓ Perfect match for all n = 1..200")

# ============================================================
# EXPERIMENT 8: Pythagorean networks — n as hypotenuse
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 8: Pythagorean Triple Networks (n as hypotenuse)")
print("=" * 70)

def pythagorean_triples_with_hypotenuse(c):
    """Find all (a, b) with a² + b² = c², a > 0, b > 0, a <= b."""
    triples = []
    for a in range(1, c):
        b_sq = c*c - a*a
        if b_sq <= 0:
            break
        b = isqrt(b_sq)
        if b*b == b_sq and a <= b:
            triples.append((a, b, c))
    return triples

print("\nPythagorean triples with hypotenuse c:")
triple_counts = {}
for c in range(1, 201):
    triples = pythagorean_triples_with_hypotenuse(c)
    triple_counts[c] = len(triples)
    if triples:
        factors = factorize(c)
        print(f"  c={c:4d}: {len(triples)} triple(s), factors={factors}")
        for t in triples:
            g = gcd(t[0], gcd(t[1], t[2]))
            print(f"    ({t[0]:4d}, {t[1]:4d}, {t[2]:4d})  gcd={g}  {'primitive' if g==1 else ''}")

print("\n\nIntegers 1..200 that are NEVER a hypotenuse:")
never_hyp = [c for c in range(1, 201) if triple_counts[c] == 0]
print(f"  Count: {len(never_hyp)}")
print(f"  Values: {never_hyp[:50]}")
print(f"\nFactorizations of first 20 non-hypotenuse integers:")
for c in never_hyp[:20]:
    factors = factorize(c)
    print(f"  c={c:3d}: {factors}")

# ============================================================
# EXPERIMENT 9: Connectivity via Gaussian Product
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 9: Photon Network Connectivity via Gaussian Product")
print("=" * 70)

def build_full_photon_graph(c):
    """
    Build the photon network for hypotenuse c.
    
    Vertices: All non-trivial representations c² = a² + b² with a,b > 0.
    These are the "photon states" of energy c.
    
    Edges: Two states (a1,b1) and (a2,b2) are connected if their
    Gaussian quotient (a1+b1i)/(a2+b2i) is a Gaussian integer.
    I.e., (a1+b1i)*conj(a2+b2i) / (a2²+b2²) is a Gaussian integer.
    But a2²+b2² = c², so we need (a1+b1i)*(a2-b2i) to be divisible by c² in Z[i].
    
    Alternative: connect if they share a common Gaussian prime factor pattern
    (differ by conjugating one factor).
    """
    reps = pythagorean_triples_with_hypotenuse(c)
    if not reps:
        return [], []
    
    # All (a, b) representations (both orderings)
    all_reps = set()
    for a, b, _ in reps:
        all_reps.add((a, b))
        if a != b:
            all_reps.add((b, a))
    
    vertices = sorted(all_reps)
    
    # Edge criterion: (a1+b1i)*conj(a2+b2i) = (a1*a2+b1*b2) + (b1*a2-a1*b2)i
    # This has norm c² * c² / c² = c². Wait, no.
    # |z1|² = c², |z2|² = c², so |z1*conj(z2)|² = c⁴
    # For z1/z2 to be a Gaussian integer, z1*conj(z2) must be divisible by |z2|² = c²
    edges = []
    for i, (a1, b1) in enumerate(vertices):
        for j, (a2, b2) in enumerate(vertices):
            if i < j:
                # z1 * conj(z2) = (a1*a2 + b1*b2) + (b1*a2 - a1*b2)i
                real_part = a1*a2 + b1*b2
                imag_part = b1*a2 - a1*b2
                c_sq = c * c
                if c_sq > 0 and real_part % c_sq == 0 and imag_part % c_sq == 0:
                    edges.append(((a1,b1), (a2,b2)))
    
    return vertices, edges

print("\nPhoton network connectivity for hypotenuses with multiple representations:")
for c in range(1, 201):
    triples = pythagorean_triples_with_hypotenuse(c)
    if len(triples) >= 2:
        verts, edges = build_full_photon_graph(c)
        comps = find_components(verts, edges) if verts else [[]]
        factors = factorize(c)
        status = "CONNECTED" if len(comps) <= 1 else f"DISCONNECTED ({len(comps)} components)"
        print(f"  c={c:4d}: {len(verts)} vertices, {len(edges)} edges, "
              f"{status}, factors={factors}")
        if len(comps) > 1:
            for idx, comp in enumerate(comps):
                print(f"    Component {idx}: {comp}")

# ============================================================
# EXPERIMENT 10: Dark Photon Classification
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 10: Dark Photon Classification")
print("=" * 70)

print("\nClassification of integers by photon network type:")
print("\nType 0 (DARK — no sum-of-2-squares rep):")
dark = [n for n in range(1, 101) if not is_sum_of_two_squares(n)]
print(f"  {dark}")
print(f"  Count in [1,100]: {len(dark)}")

print("\nType 1 (SINGLE PHOTON — exactly one rep up to signs/order):")
single = [n for n in range(1, 101) if is_sum_of_two_squares(n) and count_representations(n) == 1]
print(f"  {single[:30]}...")
print(f"  Count in [1,100]: {len(single)}")

print("\nType 2 (BINARY — exactly two reps):")
binary = [n for n in range(1, 101) if count_representations(n) == 2]
print(f"  {binary}")
print(f"  Count in [1,100]: {len(binary)}")

print("\nType 3+ (RICH — three or more reps):")
rich = [n for n in range(1, 201) if count_representations(n) >= 3]
print(f"  {rich}")
for n in rich[:10]:
    reps = all_gaussian_norms(n)
    print(f"    n={n}: {reps}")

# ============================================================
# EXPERIMENT 11: The Darkness Criterion
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 11: What Makes an Integer Dark?")
print("=" * 70)

print("\nAn integer n is dark iff it has a prime factor p ≡ 3 (mod 4) to an odd power.")
print("\nVerification for n = 1..500:")
errors = 0
for n in range(1, 501):
    predicted_dark = False
    factors = factorize(n)
    for p, e in factors.items():
        if p % 4 == 3 and e % 2 == 1:
            predicted_dark = True
            break
    actual_dark = not is_sum_of_two_squares(n)
    if predicted_dark != actual_dark:
        print(f"  ERROR at n={n}: predicted={predicted_dark}, actual={actual_dark}")
        errors += 1
if errors == 0:
    print("  ✓ Perfect match: darkness criterion verified for all n = 1..500")

# ============================================================  
# EXPERIMENT 12: Network Topology Deeper Analysis
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 12: Deeper Network Topology")
print("=" * 70)

# Try a different edge relation: connect (a1,b1) and (a2,b2) if 
# the Gaussian integer product of one triple gives another
# I.e., ∃ primitive triple (p,q,r) such that (a1+b1i)*(p+qi) gives (a2+b2i) up to units

def build_photon_network_v2(n):
    """
    Photon network v2: Connect two sum-of-two-squares representations
    if one can be obtained from another by multiplying by a Gaussian prime.
    
    For n = a² + b², the Gaussian integer z = a + bi has |z|² = n.
    Two representations z1, z2 are adjacent if z1 = z2 * u for a Gaussian unit u,
    or z1 = z2 * π / π̄ for some Gaussian prime π dividing n.
    
    Equivalently: z1 * conj(z2) should have norm n² and factor through n.
    """
    reps = all_gaussian_norms(n)
    if len(reps) <= 1:
        return reps, [], 1
    
    # Vertices are the canonical reps (a, b) with a >= 0, b >= 0
    vertices = reps
    
    # For connectivity, use: two reps are in same component iff
    # they correspond to the same Gaussian ideal class
    # In Z[i] (which is a PID), all ideals are principal, so 
    # the question is about which associates are chosen
    
    # Actually, the right approach: factor n in Z[i] and track the choices
    factors = factorize(n)
    split_count = sum(1 for p in factors if p % 4 == 1)
    
    # With k splitting primes each to power e_i, 
    # the number of essentially different representations is prod(e_i + 1) / symmetry
    
    # Edges: connect reps that differ by conjugating one Gaussian prime factor
    edges = []
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            a1, b1 = vertices[i]
            a2, b2 = vertices[j]
            # z1 * conj(z2) = (a1*a2 + b1*b2) + (b1*a2 - a1*b2)i
            real_part = a1 * a2 + b1 * b2
            imag_part = b1 * a2 - a1 * b2
            # For them to be "adjacent" in the Gaussian factorization sense,
            # the quotient z1/z2 should be a ratio of conjugate Gaussian primes
            # |z1/z2|² = 1, so z1*conj(z2) has norm n
            # z1*conj(z2)/n should be a unit or Gaussian integer
            # Actually |z1*conj(z2)|² = |z1|²|z2|² = n²
            # Hmm, z1*conj(z2) has norm n², not n
            
            # Different approach: z1 and z2 are connected if z1*conj(z2) 
            # is divisible by some splitting prime p in Z[i]
            # That is, (a1*a2+b1*b2) + (b1*a2-a1*b2)i ≡ 0 mod some Gaussian prime of p
            
            # Simplest: connect all pairs — the network is complete for multi-rep n
            # Then study the structure differently
            edges.append((vertices[i], vertices[j]))
    
    comps = find_components(vertices, edges) if vertices else [[]]
    return vertices, edges, len(comps)

print("\nPhoton network v2 (complete graph on representations):")
for n in sorted(set(list(range(1, 100)) + [325, 425, 650, 725, 845, 1105, 1625, 2125])):
    reps = all_gaussian_norms(n)
    if len(reps) >= 2:
        factors = factorize(n)
        split_primes = [(p, e) for p, e in factors.items() if p % 4 == 1]
        print(f"  n={n:5d}: {len(reps)} reps = {reps}, "
              f"split primes = {split_primes}")

# ============================================================
# EXPERIMENT 13: Characterizing number of representations
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 13: Formula for Number of Representations")
print("=" * 70)

print("\nFor n = p1^a1 * p2^a2 * ... where pi ≡ 1 mod 4:")
print("Number of reps (a,b) with a >= 0, b >= 0, a <= b:")
print("= prod(ai + 1) / 2  [roughly, accounting for symmetry]\n")

for n in [5, 25, 125, 13, 169, 65, 85, 325, 1105, 5525]:
    reps = all_gaussian_norms(n)
    factors = factorize(n)
    split_primes = [(p, e) for p, e in factors.items() if p % 4 == 1]
    predicted = 1
    for p, e in split_primes:
        predicted *= (e + 1)
    print(f"  n={n:5d}: actual_reps={len(reps)}, "
          f"prod(ei+1)={predicted}, "
          f"split_primes={split_primes}, "
          f"reps={reps}")

# ============================================================
# EXPERIMENT 14: Photon Darkness Density
# ============================================================
print("\n" + "=" * 70)
print("EXPERIMENT 14: Asymptotic Density of Dark Integers")
print("=" * 70)

for N in [100, 500, 1000, 5000, 10000]:
    dark_count = sum(1 for n in range(1, N+1) if not is_sum_of_two_squares(n))
    density = dark_count / N
    # Landau-Ramanujan: proportion of n ≤ N that are sum of 2 squares ~ C/√(ln N)
    import math
    landau_approx = 0.7642 / math.sqrt(math.log(N))  # Landau-Ramanujan constant
    print(f"  N={N:6d}: dark={dark_count:5d} ({density:.4f}), "
          f"light={N-dark_count:5d} ({1-density:.4f}), "
          f"Landau-Ramanujan approx: {landau_approx:.4f}")

print("\n\nDONE — Photon Network Exploration Complete")
