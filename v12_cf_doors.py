#!/usr/bin/env python3
"""v12_cf_doors.py — 15 Cross-Domain CF Experiments

Explores how Berggren tree / continued fraction discoveries apply to
cryptography, physics, mathematics, CS, and applications.
"""

import numpy as np
import time, os, sys, json, math, hashlib
from fractions import Fraction
from collections import Counter, defaultdict
from functools import reduce

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

IMG = '/home/raver1975/factor/images'
os.makedirs(IMG, exist_ok=True)

# ── Berggren matrices ──
B1 = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B2 = np.array([[1,2,2],[2,1,2],[2,2,3]])
B3 = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])

# 2x2 Berggren matrices for CF work
B1_2 = np.array([[1,2],[0,1]], dtype=object)  # unipotent
B2_2 = np.array([[2,1],[1,0]], dtype=object)  # = M(2), CF matrix
B3_2 = np.array([[-1,2],[0,1]], dtype=object) # anti-unipotent

results = {}

def cf_expand(x, maxterms=50):
    """Expand real x into CF partial quotients."""
    pqs = []
    for _ in range(maxterms):
        a = int(math.floor(x))
        pqs.append(a)
        frac = x - a
        if abs(frac) < 1e-12:
            break
        x = 1.0 / frac
    return pqs

def cf_from_fraction(p, q, maxterms=80):
    """Exact CF of p/q."""
    pqs = []
    for _ in range(maxterms):
        if q == 0:
            break
        a, r = divmod(p, q)
        pqs.append(int(a))
        p, q = q, r
    return pqs

def cf_convergents(pqs):
    """Return list of (p_k, q_k) convergents."""
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    convs = []
    for a in pqs:
        h0, h1 = h1, a*h1 + h0
        k0, k1 = k1, a*k1 + k0
        convs.append((h1, k1))
    return convs

def mat_cf(a):
    """CF matrix M(a) = [[a,1],[1,0]]."""
    return np.array([[a,1],[1,0]], dtype=object)

def matmul_int(A, B):
    """Integer matrix multiply for 2x2."""
    return np.array([
        [int(A[0,0]*B[0,0]+A[0,1]*B[1,0]), int(A[0,0]*B[0,1]+A[0,1]*B[1,1])],
        [int(A[1,0]*B[0,0]+A[1,1]*B[1,0]), int(A[1,0]*B[0,1]+A[1,1]*B[1,1])]
    ], dtype=object)

def matmul_mod(A, B, p):
    """2x2 matrix multiply mod p."""
    return np.array([
        [(A[0,0]*B[0,0]+A[0,1]*B[1,0])%p, (A[0,0]*B[0,1]+A[0,1]*B[1,1])%p],
        [(A[1,0]*B[0,0]+A[1,1]*B[1,0])%p, (A[1,0]*B[0,1]+A[1,1]*B[1,1])%p]
    ], dtype=object)

def matpow_mod(M, n, p):
    """Matrix power mod p."""
    result = np.array([[1,0],[0,1]], dtype=object)
    base = M.copy() % p
    while n > 0:
        if n % 2 == 1:
            result = matmul_mod(result, base, p)
        base = matmul_mod(base, base, p)
        n //= 2
    return result

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 1: Wiener attack via Berggren paths
# ═══════════════════════════════════════════════════════════════════
def exp01_wiener_berggren():
    """Compare standard Wiener CF attack vs Berggren-path convergents on RSA keys with small d."""
    print("=== Exp 1: Wiener attack via Berggren paths ===")
    t0 = time.time()

    import random
    random.seed(42)

    def generate_weak_rsa(bits=64):
        """Generate RSA key with small d for Wiener attack."""
        while True:
            # Small primes for testing
            p = random.randint(2**(bits//2-1), 2**(bits//2))
            if not is_prime(p): continue
            q = random.randint(2**(bits//2-1), 2**(bits//2))
            if not is_prime(q) or p == q: continue
            N = p * q
            phi = (p-1)*(q-1)
            # Small d
            d = random.randint(3, int(N**0.25)//3)
            if d % 2 == 0: d += 1
            if gcd(d, phi) != 1: continue
            # Compute e
            e = pow(d, -1, phi)
            return N, e, d, p, q

    def wiener_attack(e, N):
        """Standard Wiener: CF of e/N."""
        pqs = cf_from_fraction(e, N, maxterms=200)
        convs = cf_convergents(pqs)
        for k, d_cand in convs:
            if k == 0: continue
            if d_cand == 0: continue
            # Check: (ed - 1) / k should be integer = phi(N)
            if (e * d_cand - 1) % k != 0: continue
            phi_cand = (e * d_cand - 1) // k
            # phi = N - p - q + 1, so p+q = N - phi + 1
            s = N - phi_cand + 1
            # p,q are roots of x^2 - s*x + N = 0
            disc = s*s - 4*N
            if disc < 0: continue
            sqrt_disc = int(math.isqrt(disc))
            if sqrt_disc * sqrt_disc != disc: continue
            p_cand = (s + sqrt_disc) // 2
            q_cand = (s - sqrt_disc) // 2
            if p_cand * q_cand == N:
                return d_cand, p_cand, q_cand
        return None, None, None

    def berggren_convergents(e, N, max_depth=200):
        """Generate convergents by multiplying B2 matrices (= M(2) path)
        and also mixed B1/B2/B3 paths, then check as Wiener candidates."""
        found = []
        # Pure B2 path (= CF [2;2,2,...] = convergents of 1+sqrt(2))
        M = np.array([[1,0],[0,1]], dtype=object)
        for i in range(max_depth):
            M = matmul_int(M, B2_2)
            k, d_cand = int(M[0,0]), int(M[0,1])
            if d_cand > 0 and k > 0:
                found.append((k, d_cand))

        # Mixed paths: try all 3-step combinations
        matrices = [B1_2, B2_2, B3_2]
        labels = ['B1','B2','B3']
        for i in range(3):
            for j in range(3):
                M = matmul_int(matrices[i], matrices[j])
                for step in range(min(max_depth, 30)):
                    M2 = matmul_int(M, matrices[step % 3])
                    k, d_cand = abs(int(M2[0,0])), abs(int(M2[0,1]))
                    if d_cand > 0 and k > 0:
                        found.append((k, d_cand))
                    M = M2
        return found

    # Test on 50 weak RSA keys
    n_keys = 50
    wiener_success = 0
    berggren_success = 0
    berggren_extra = 0  # found by Berggren but NOT by standard Wiener

    for trial in range(n_keys):
        result = generate_weak_rsa(bits=64)
        if result is None: continue
        N, e, d_true, p_true, q_true = result

        # Standard Wiener
        d_w, p_w, q_w = wiener_attack(e, N)
        w_ok = (d_w == d_true)
        if w_ok: wiener_success += 1

        # Berggren convergents as Wiener candidates
        b_convs = berggren_convergents(e, N)
        b_ok = False
        for k, d_cand in b_convs:
            if d_cand == 0 or k == 0: continue
            if (e * d_cand - 1) % k != 0: continue
            phi_cand = (e * d_cand - 1) // k
            s = N - phi_cand + 1
            disc = s*s - 4*N
            if disc < 0: continue
            sqrt_disc = int(math.isqrt(disc))
            if sqrt_disc * sqrt_disc == disc:
                p_cand = (s + sqrt_disc) // 2
                q_cand = (s - sqrt_disc) // 2
                if p_cand * q_cand == N:
                    b_ok = True
                    break
        if b_ok: berggren_success += 1
        if b_ok and not w_ok: berggren_extra += 1

    elapsed = time.time() - t0
    results['exp01'] = {
        'wiener_success': wiener_success,
        'berggren_success': berggren_success,
        'berggren_extra': berggren_extra,
        'n_keys': n_keys,
        'time': elapsed
    }
    print(f"  Wiener: {wiener_success}/{n_keys}, Berggren: {berggren_success}/{n_keys}, Extra: {berggren_extra}")
    return results['exp01']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 2: CF-based key exchange
# ═══════════════════════════════════════════════════════════════════
def exp02_cf_key_exchange():
    """Analyze security of Berggren-matrix-product key exchange."""
    print("=== Exp 2: CF-based key exchange ===")
    t0 = time.time()

    # Protocol: public prime p, public generators B1,B2,B3 mod p
    # Alice picks path w_A = sequence of {1,2,3}, computes M_A = product of B_{w_A[i]} mod p
    # Bob picks path w_B, computes M_B mod p
    # Shared secret = M_A * M_B (but this is commutative only if paths commute)
    # Actually: use M_A * M_B vs M_B * M_A -- NOT commutative in general
    # So we need a different protocol.

    # Better: Diffie-Hellman analog
    # Public: prime p, matrix G in SL(2,F_p)
    # Alice: picks integer a, sends G^a mod p
    # Bob: picks integer b, sends G^b mod p
    # Shared: G^(ab) mod p
    # Security = DLP in SL(2,F_p) = matrix discrete log

    primes = [101, 503, 1009, 5003, 10007]
    security_data = []

    for p in primes:
        G = B2_2 % p  # Use B2 as generator

        # Compute order of G mod p
        M = np.array([[1,0],[0,1]], dtype=object)
        order = 0
        for k in range(1, 2*p*(p+1)+1):
            M = matmul_mod(M, G, p)
            if M[0,0] == 1 and M[0,1] == 0 and M[1,0] == 0 and M[1,1] == 1:
                order = k
                break
            if k > 50000:
                order = -1
                break

        # Baby-step giant-step cost to break DLP in <G>
        bsgs_cost = int(math.isqrt(order)) + 1 if order > 0 else -1

        # Key size = log2(p) bits for each matrix entry (4 entries)
        key_size_bits = 4 * math.ceil(math.log2(p)) if p > 1 else 0

        # Security level = log2(bsgs_cost)
        sec_level = math.log2(bsgs_cost) if bsgs_cost > 0 else -1

        security_data.append({
            'p': p,
            'order': order,
            'bsgs_cost': bsgs_cost,
            'key_size_bits': key_size_bits,
            'security_bits': round(sec_level, 1)
        })

    # Compare to standard DH in Z/pZ*
    # Standard DH: order ~ p-1, BSGS cost ~ sqrt(p), key = log2(p) bits, security = log2(p)/2
    comparison = []
    for sd in security_data:
        p = sd['p']
        std_sec = math.log2(p) / 2
        comparison.append({
            'p': p,
            'berggren_sec': sd['security_bits'],
            'standard_dh_sec': round(std_sec, 1),
            'ratio': round(sd['security_bits'] / std_sec, 2) if std_sec > 0 else 0
        })

    elapsed = time.time() - t0
    results['exp02'] = {
        'security_data': security_data,
        'comparison': comparison,
        'time': elapsed
    }
    print(f"  Security ratios: {[c['ratio'] for c in comparison]}")
    return results['exp02']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 3: Lattice reduction via Berggren
# ═══════════════════════════════════════════════════════════════════
def exp03_lattice_berggren():
    """Apply Berggren pre-reduction before LLL on random lattices."""
    print("=== Exp 3: Lattice reduction via Berggren ===")
    t0 = time.time()

    np.random.seed(42)

    def gram_schmidt_quality(basis):
        """Compute orthogonality defect = prod(||b_i||) / det(B)."""
        n = basis.shape[0]
        norms_prod = np.prod([np.linalg.norm(basis[i]) for i in range(n)])
        det_abs = abs(np.linalg.det(basis.astype(float)))
        if det_abs < 1e-10:
            return float('inf')
        return norms_prod / det_abs

    def berggren_prereduction_2d(basis):
        """Apply Berggren matrices as 2D lattice transforms on pairs of rows."""
        n = basis.shape[0]
        improved = basis.copy().astype(float)
        # Apply B2_2-like reduction on consecutive row pairs
        for i in range(0, n-1, 2):
            v1 = improved[i]
            v2 = improved[i+1]
            # Try B2-like: replace (v1,v2) with (2v1+v2, v1)
            cand1 = 2*v1 + v2
            cand2 = v1.copy()
            if np.linalg.norm(cand1) < np.linalg.norm(v1) + np.linalg.norm(v2):
                improved[i] = cand1
                improved[i+1] = cand2
            # Try size reduction: v2 = v2 - round(v2.v1/v1.v1)*v1
            dot = np.dot(v2, v1)
            norm_sq = np.dot(v1, v1)
            if norm_sq > 0:
                mu = round(dot / norm_sq)
                improved[i+1] = v2 - mu * v1
        return improved

    dims = [4, 6, 8, 10, 14, 20]
    n_trials = 20
    quality_results = []

    for dim in dims:
        orig_quals = []
        berg_quals = []
        for _ in range(n_trials):
            # Random lattice basis
            basis = np.random.randint(-50, 50, (dim, dim)).astype(float)
            while abs(np.linalg.det(basis)) < 1:
                basis = np.random.randint(-50, 50, (dim, dim)).astype(float)

            q_orig = gram_schmidt_quality(basis)

            # Berggren pre-reduction
            reduced = berggren_prereduction_2d(basis)
            q_berg = gram_schmidt_quality(reduced)

            orig_quals.append(q_orig)
            berg_quals.append(q_berg)

        mean_orig = np.mean(orig_quals)
        mean_berg = np.mean(berg_quals)
        improvement = mean_orig / mean_berg if mean_berg > 0 else 0
        quality_results.append({
            'dim': dim,
            'mean_orig': round(mean_orig, 2),
            'mean_berggren': round(mean_berg, 2),
            'improvement': round(improvement, 3)
        })

    elapsed = time.time() - t0
    results['exp03'] = {
        'quality_results': quality_results,
        'time': elapsed
    }
    print(f"  Improvements by dim: {[(q['dim'], q['improvement']) for q in quality_results]}")
    return results['exp03']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 4: KAM stability from Zaremba (HIGH PRIORITY)
# ═══════════════════════════════════════════════════════════════════
def exp04_kam_stability():
    """Map B2 frequencies to dynamical systems. Are B2-path frequencies KAM-stable?"""
    print("=== Exp 4: KAM stability from Zaremba ===")
    t0 = time.time()

    # B2 eigenvalue: 3+2sqrt(2), its CF = [5;1,4,1,4,...] period 2
    # B2 path ratios converge to 1+sqrt(2) = [2;2,2,...] (all PQ=2, bounded)
    # Zaremba (T102): B2 paths have PQ <= 5
    # KAM theorem: orbit with frequency omega is stable iff CF(omega) has bounded PQ

    # Generate B2-path frequencies (ratio c_k/c_{k-1} for Pythagorean triples)
    def b2_path_frequencies(depth=30):
        """Generate frequencies from B2 path."""
        # B2 on (3,4,5): iteratively apply B2
        triple = np.array([3, 4, 5])
        freqs = []
        prev_c = 5
        for _ in range(depth):
            triple = B2 @ triple
            c = triple[2]
            if prev_c > 0:
                freqs.append(c / prev_c)
            prev_c = c
        return freqs

    freqs = b2_path_frequencies(30)

    # Check: all B2 frequencies converge to 3+2sqrt(2)
    target = 3 + 2*math.sqrt(2)
    convergence = [abs(f - target) for f in freqs]

    # Standard map: x_{n+1} = x_n + y_{n+1}, y_{n+1} = y_n + K*sin(2*pi*x_n)
    # KAM: for small K, orbits with "good" frequency are stable
    # Good = bounded partial quotients in CF

    def standard_map_lyapunov(omega, K, n_iter=5000):
        """Compute Lyapunov exponent for orbit starting near frequency omega."""
        x, y = 0.1, omega
        lyap_sum = 0.0
        for _ in range(n_iter):
            # Jacobian
            J11 = 1.0
            J12 = 1.0
            J21 = 2*math.pi*K*math.cos(2*math.pi*x)
            J22 = 1.0 + 2*math.pi*K*math.cos(2*math.pi*x)
            lyap_sum += math.log(max(abs(J22), 1e-15))
            y = y + K * math.sin(2*math.pi*x)
            x = x + y
            x = x % 1.0
        return lyap_sum / n_iter

    # Test frequencies: B2-path freqs (mod 1), golden ratio, random
    K_values = [0.1, 0.3, 0.5, 0.8, 0.97, 1.5]

    # B2 frequency mod 1
    b2_freq = (1 + math.sqrt(2)) % 1  # fractional part
    golden = (math.sqrt(5) - 1) / 2  # golden ratio (most irrational)
    liouville_approx = 0.1100010000000000000001  # very well-approximable (unbounded PQ)
    random_freqs = [0.31415926, 0.27182818, 0.69314718]

    test_freqs = {
        'B2 (1+sqrt2)': b2_freq,
        'Golden (phi)': golden,
        'Liouville-like': liouville_approx,
        'pi/10': 0.31415926,
        'e/10': 0.27182818,
        'ln2': 0.69314718,
    }

    # Check PQ bounds
    pq_bounds = {}
    for name, freq in test_freqs.items():
        pqs = cf_expand(freq, 30)
        pq_bounds[name] = {
            'max_pq': max(pqs[1:]) if len(pqs) > 1 else 0,
            'mean_pq': np.mean(pqs[1:]) if len(pqs) > 1 else 0,
            'pqs': pqs[:10]
        }

    kam_data = {}
    for name, freq in test_freqs.items():
        lyaps = []
        for K in K_values:
            lyap = standard_map_lyapunov(freq, K)
            lyaps.append(round(lyap, 4))
        kam_data[name] = lyaps

    # KAM stability = Lyapunov exponent near 0 (stable) vs positive (chaotic)
    # B2 and golden should be most stable (bounded PQ)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    for name, lyaps in kam_data.items():
        ax.plot(K_values, lyaps, 'o-', label=name, markersize=5)
    ax.set_xlabel('Perturbation K')
    ax.set_ylabel('Lyapunov Exponent')
    ax.set_title('KAM Stability: Lyapunov vs K\n(lower = more stable)')
    ax.legend(fontsize=8)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    names = list(pq_bounds.keys())
    max_pqs = [pq_bounds[n]['max_pq'] for n in names]
    mean_pqs = [pq_bounds[n]['mean_pq'] for n in names]
    x_pos = range(len(names))
    ax.bar([x-0.15 for x in x_pos], max_pqs, 0.3, label='Max PQ', color='steelblue')
    ax.bar([x+0.15 for x in x_pos], mean_pqs, 0.3, label='Mean PQ', color='coral')
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels([n.split('(')[0].strip() for n in names], rotation=30, ha='right', fontsize=8)
    ax.set_ylabel('Partial Quotient')
    ax.set_title('CF Partial Quotient Bounds\n(lower = more KAM-stable)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_04_kam.png', dpi=150)
    plt.close()

    # Determine if B2 frequencies are KAM-stable
    # Compare: at K=0.97 (near KAM breakdown), is B2 more stable than Liouville?
    b2_lyap_097 = kam_data['B2 (1+sqrt2)'][K_values.index(0.97)]
    liou_lyap_097 = kam_data['Liouville-like'][K_values.index(0.97)]
    golden_lyap_097 = kam_data['Golden (phi)'][K_values.index(0.97)]

    elapsed = time.time() - t0
    results['exp04'] = {
        'kam_data': kam_data,
        'pq_bounds': {k: {'max_pq': v['max_pq'], 'mean_pq': round(v['mean_pq'],2), 'pqs_head': v['pqs']} for k,v in pq_bounds.items()},
        'K_values': K_values,
        'b2_lyap_at_097': b2_lyap_097,
        'golden_lyap_at_097': golden_lyap_097,
        'liouville_lyap_at_097': liou_lyap_097,
        'b2_more_stable_than_liouville': b2_lyap_097 < liou_lyap_097,
        'time': elapsed
    }
    print(f"  B2 Lyap@0.97={b2_lyap_097}, Golden={golden_lyap_097}, Liouville={liou_lyap_097}")
    print(f"  B2 more stable than Liouville: {b2_lyap_097 < liou_lyap_097}")
    return results['exp04']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 5: Quantum chaos eigenvalues
# ═══════════════════════════════════════════════════════════════════
def exp05_quantum_chaos():
    """Eigenvalue spacing for Berggren graph mod p. Compare to quantum chaos predictions."""
    print("=== Exp 5: Quantum chaos eigenvalues ===")
    t0 = time.time()

    primes_test = [101, 503, 1009]
    spacing_data = {}

    for p in primes_test:
        # Build adjacency matrix of Berggren graph mod p
        # Nodes: primitive Pythagorean triples mod p (pairs (m,n) with m>n, gcd=1, m-n odd)
        # Too large for full matrix. Instead: use the 2x2 action on (Z/pZ)^2
        # Adjacency: v -> B1*v, B2*v, B3*v mod p (3-regular directed graph)

        # Work with projective line P^1(F_p) = {0,1,...,p-1,infty}
        # B2_2 acts as Mobius transform: z -> (2z+1)/(z) = 2 + 1/z
        # Use matrix action on (Z/pZ)^2 \ {0}

        # For manageable size, use P^1(F_p): p+1 points
        n_nodes = p + 1
        adj = np.zeros((n_nodes, n_nodes), dtype=float)

        # Map: (a:b) -> index. a=1,b=0..p-1 gives 0..p-1. a=0,b=1 gives p (infinity).
        def proj_index(a, b, p):
            a, b = a % p, b % p
            if a == 0 and b == 0:
                return -1  # zero vector, skip
            if a == 0:
                return p  # infinity
            # Normalize: a=1
            a_inv = pow(int(a), p-2, p)
            return (b * a_inv) % p

        matrices_2 = [
            np.array([[1,2],[0,1]], dtype=object),
            np.array([[2,1],[1,0]], dtype=object),
            np.array([[-1,2],[0,1]], dtype=object)
        ]

        for M in matrices_2:
            for idx in range(n_nodes):
                if idx < p:
                    vec = (1, idx)
                else:
                    vec = (0, 1)
                # Apply M
                new_a = (int(M[0,0]) * vec[0] + int(M[0,1]) * vec[1]) % p
                new_b = (int(M[1,0]) * vec[0] + int(M[1,1]) * vec[1]) % p
                j = proj_index(new_a, new_b, p)
                if j >= 0:
                    adj[idx, j] += 1

        # Symmetrize for eigenvalue analysis
        adj_sym = (adj + adj.T) / 2

        # Compute eigenvalues
        eigs = np.linalg.eigvalsh(adj_sym)
        eigs = np.sort(eigs)

        # Nearest-neighbor spacing distribution
        spacings = np.diff(eigs)
        # Normalize: mean spacing = 1
        mean_sp = np.mean(spacings)
        if mean_sp > 0:
            spacings_norm = spacings / mean_sp
        else:
            spacings_norm = spacings

        # Compare to:
        # Poisson: P(s) = exp(-s) -- integrable systems
        # GOE (Wigner surmise): P(s) = (pi*s/2)*exp(-pi*s^2/4) -- chaotic systems

        # Compute KL divergence to both
        hist, bin_edges = np.histogram(spacings_norm[spacings_norm < 4], bins=30, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        poisson_pred = np.exp(-bin_centers)
        goe_pred = (np.pi * bin_centers / 2) * np.exp(-np.pi * bin_centers**2 / 4)

        # L2 distance
        l2_poisson = np.sum((hist - poisson_pred)**2)
        l2_goe = np.sum((hist - goe_pred)**2)

        spacing_data[p] = {
            'n_eigs': len(eigs),
            'l2_poisson': round(float(l2_poisson), 4),
            'l2_goe': round(float(l2_goe), 4),
            'closer_to': 'Poisson' if l2_poisson < l2_goe else 'GOE',
            'mean_spacing': round(float(mean_sp), 4),
            'spacings_std': round(float(np.std(spacings_norm)), 4)
        }

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, p in enumerate(primes_test):
        ax = axes[idx]
        # Recompute for plot
        n_nodes = p + 1
        adj = np.zeros((n_nodes, n_nodes), dtype=float)
        for M in matrices_2:
            for i in range(n_nodes):
                vec = (1, i) if i < p else (0, 1)
                new_a = (int(M[0,0]) * vec[0] + int(M[0,1]) * vec[1]) % p
                new_b = (int(M[1,0]) * vec[0] + int(M[1,1]) * vec[1]) % p
                j = proj_index(new_a, new_b, p)
                if j >= 0: adj[i, j] += 1
        adj_sym = (adj + adj.T) / 2
        eigs = np.sort(np.linalg.eigvalsh(adj_sym))
        sp = np.diff(eigs)
        mean_s = np.mean(sp)
        sp_n = sp / mean_s if mean_s > 0 else sp

        ax.hist(sp_n[sp_n < 4], bins=25, density=True, alpha=0.7, color='steelblue', label='Data')
        s_range = np.linspace(0.01, 4, 100)
        ax.plot(s_range, np.exp(-s_range), 'r--', label='Poisson', linewidth=2)
        ax.plot(s_range, (np.pi*s_range/2)*np.exp(-np.pi*s_range**2/4), 'g--', label='GOE', linewidth=2)
        ax.set_title(f'p={p}: {spacing_data[p]["closer_to"]}')
        ax.set_xlabel('Normalized spacing s')
        ax.set_ylabel('P(s)')
        ax.legend(fontsize=8)
        ax.set_xlim(0, 4)

    plt.suptitle('Berggren Graph Eigenvalue Spacing vs Quantum Chaos', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_05_quantum.png', dpi=150)
    plt.close()

    elapsed = time.time() - t0
    results['exp05'] = {
        'spacing_data': spacing_data,
        'time': elapsed
    }
    print(f"  Results: {spacing_data}")
    return results['exp05']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 6: Penrose-Pythagorean tiling
# ═══════════════════════════════════════════════════════════════════
def exp06_penrose_tiling():
    """Construct quasi-periodic tiling using Berggren eigenvalues as inflation factors."""
    print("=== Exp 6: Penrose-Pythagorean tiling ===")
    t0 = time.time()

    # B2 eigenvalues: 3+2sqrt(2) and 3-2sqrt(2) (product=1, sum=6)
    # Golden ratio phi = (1+sqrt(5))/2 ~ 1.618 used in Penrose
    # B2 eigenvalue: 1+sqrt(2) ~ 2.414 (for 2x2 B2)

    lam1 = 1 + math.sqrt(2)  # ~ 2.414 (B2_2 dominant eigenvalue)
    lam2 = 1 - math.sqrt(2)  # ~ -0.414 (B2_2 minor eigenvalue)
    phi = (1 + math.sqrt(5)) / 2  # golden ratio

    # 1D quasi-crystal: cut-and-project from 2D lattice
    # Use lam1 as slope instead of phi
    def cut_and_project_1d(slope, window_width=1.0, n_points=200):
        """Generate 1D quasicrystal via cut-and-project."""
        points = []
        for n in range(-n_points, n_points+1):
            for m in range(-n_points, n_points+1):
                # Physical space projection
                x_phys = n + m * slope
                # Internal space projection
                x_int = n * slope - m  # perpendicular
                if abs(x_int) < window_width:
                    points.append(x_phys)
        points.sort()
        return np.array(points)

    # Generate for both slopes
    pts_berggren = cut_and_project_1d(lam1, window_width=1.0, n_points=50)
    pts_penrose = cut_and_project_1d(phi, window_width=1.0, n_points=50)

    # Analyze gap distribution
    gaps_b = np.diff(pts_berggren)
    gaps_p = np.diff(pts_penrose)

    # Filter near-zero gaps
    gaps_b = gaps_b[gaps_b > 0.01]
    gaps_p = gaps_p[gaps_p > 0.01]

    # Count distinct gap sizes (within tolerance)
    def count_gap_types(gaps, tol=0.01):
        if len(gaps) == 0:
            return 0, []
        sorted_gaps = np.sort(gaps)
        types = [sorted_gaps[0]]
        for g in sorted_gaps[1:]:
            if abs(g - types[-1]) > tol:
                types.append(g)
        return len(types), types

    n_types_b, types_b = count_gap_types(gaps_b)
    n_types_p, types_p = count_gap_types(gaps_p)

    # Three-gap theorem: for any irrational slope, at most 3 distinct gap sizes
    # Check if Berggren slope gives exactly 3

    # Diffraction pattern (Fourier transform of point set)
    def diffraction(points, k_max=20, n_k=1000):
        """Compute diffraction intensity."""
        k_vals = np.linspace(-k_max, k_max, n_k)
        intensity = np.zeros(n_k)
        pts_centered = points - np.mean(points)
        for i, k in enumerate(k_vals):
            phase = np.exp(2j * np.pi * k * pts_centered)
            intensity[i] = abs(np.sum(phase))**2 / len(pts_centered)
        return k_vals, intensity

    # Compute for a subset
    sel_b = pts_berggren[(pts_berggren > -20) & (pts_berggren < 20)]
    sel_p = pts_penrose[(pts_penrose > -20) & (pts_penrose < 20)]

    k_b, int_b = diffraction(sel_b, k_max=15, n_k=500)
    k_p, int_p = diffraction(sel_p, k_max=15, n_k=500)

    # Symmetry: check if diffraction has n-fold rotational symmetry analog
    # For 1D: check if peak positions are at m + n*slope (dense set)
    peaks_b = k_b[int_b > np.max(int_b) * 0.1]
    peaks_p = k_p[int_p > np.max(int_p) * 0.1]

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Gap distribution
    ax = axes[0, 0]
    if len(gaps_b) > 0:
        ax.hist(gaps_b, bins=50, alpha=0.7, label=f'Berggren (1+sqrt2)', color='steelblue', density=True)
    if len(gaps_p) > 0:
        ax.hist(gaps_p, bins=50, alpha=0.7, label=f'Penrose (phi)', color='coral', density=True)
    ax.set_xlabel('Gap size')
    ax.set_ylabel('Density')
    ax.set_title(f'Gap Distribution: Berggren {n_types_b} types, Penrose {n_types_p} types')
    ax.legend()

    # Point sets
    ax = axes[0, 1]
    sel_range = (-10, 10)
    b_sel = pts_berggren[(pts_berggren > sel_range[0]) & (pts_berggren < sel_range[1])]
    p_sel = pts_penrose[(pts_penrose > sel_range[0]) & (pts_penrose < sel_range[1])]
    ax.eventplot([b_sel], lineoffsets=[1], linelengths=[0.3], colors=['steelblue'], label='Berggren')
    ax.eventplot([p_sel], lineoffsets=[0.5], linelengths=[0.3], colors=['coral'], label='Penrose')
    ax.set_xlabel('Position')
    ax.set_title('1D Quasicrystals')
    ax.legend()
    ax.set_yticks([0.5, 1.0])
    ax.set_yticklabels(['Penrose', 'Berggren'])

    # Diffraction
    ax = axes[1, 0]
    ax.plot(k_b, int_b, color='steelblue', alpha=0.8, label='Berggren')
    ax.set_xlabel('k')
    ax.set_ylabel('Intensity')
    ax.set_title('Diffraction: Berggren Quasicrystal')
    ax.set_xlim(-15, 15)

    ax = axes[1, 1]
    ax.plot(k_p, int_p, color='coral', alpha=0.8, label='Penrose')
    ax.set_xlabel('k')
    ax.set_ylabel('Intensity')
    ax.set_title('Diffraction: Penrose Quasicrystal')
    ax.set_xlim(-15, 15)

    plt.suptitle('Penrose-Pythagorean Tiling Comparison', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_06_tiling.png', dpi=150)
    plt.close()

    # Is the Berggren tiling aperiodic?
    # Yes: any cut-and-project with irrational slope is aperiodic
    # Symmetry group: the module Z[1+sqrt(2)] = Z + Z*sqrt(2)
    # This is the ring of integers in Q(sqrt(2))

    elapsed = time.time() - t0
    results['exp06'] = {
        'berggren_gap_types': n_types_b,
        'penrose_gap_types': n_types_p,
        'berggren_gaps': [round(float(g), 4) for g in types_b[:5]],
        'penrose_gaps': [round(float(g), 4) for g in types_p[:5]],
        'berggren_n_peaks': len(peaks_b),
        'penrose_n_peaks': len(peaks_p),
        'aperiodic': True,
        'symmetry_module': 'Z[sqrt(2)]',
        'time': elapsed
    }
    print(f"  Berggren gaps: {n_types_b} types, Penrose: {n_types_p} types")
    print(f"  Both aperiodic. Berggren symmetry module: Z[sqrt(2)]")
    return results['exp06']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 7: Gauss-Kuzmin on Berggren tree (HIGH PRIORITY)
# ═══════════════════════════════════════════════════════════════════
def exp07_gauss_kuzmin():
    """CF PQ distribution for tree-generated ratios vs Gauss-Kuzmin."""
    print("=== Exp 7: Gauss-Kuzmin on Berggren tree ===")
    t0 = time.time()

    # Gauss-Kuzmin: P(a=k) = log2(1 + 1/(k(k+2)))
    def gauss_kuzmin(k):
        return math.log2(1 + 1/(k*(k+2)))

    # Generate tree triples at depth d and compute c_k / c_{k-1} ratios
    def generate_tree_ratios(max_depth=14):
        """BFS through Berggren tree, collect consecutive hypotenuse ratios."""
        all_pqs = []  # all partial quotients from tree ratios

        queue = [(np.array([3, 4, 5]), 0)]
        path_ratios = {}  # path -> list of ratios

        # Also track by branch type
        b1_pqs, b2_pqs, b3_pqs, mixed_pqs = [], [], [], []

        # Generate all paths up to depth
        from itertools import product as iprod
        for depth in range(1, min(max_depth+1, 13)):
            for path in iprod([0,1,2], repeat=depth):
                triple = np.array([3, 4, 5])
                matrices = [B1, B2, B3]
                prev_c = 5
                ratios = []
                for step in path:
                    triple = matrices[step] @ triple
                    triple = np.abs(triple)  # ensure positive
                    c = triple[2]
                    if prev_c > 0 and c > 0:
                        ratio = c / prev_c
                        ratios.append(ratio)
                    prev_c = c

                # Get CF of each ratio
                for r in ratios:
                    if r > 0:
                        pqs = cf_expand(r, 20)
                        if len(pqs) > 1:
                            all_pqs.extend(pqs[1:])  # skip a_0

                            # Categorize by branch type
                            if all(s == 0 for s in path):
                                b1_pqs.extend(pqs[1:])
                            elif all(s == 1 for s in path):
                                b2_pqs.extend(pqs[1:])
                            elif all(s == 2 for s in path):
                                b3_pqs.extend(pqs[1:])
                            else:
                                mixed_pqs.extend(pqs[1:])

                if len(all_pqs) > 100000:
                    break
            if len(all_pqs) > 100000:
                break

        return all_pqs, b1_pqs, b2_pqs, b3_pqs, mixed_pqs

    all_pqs, b1_pqs, b2_pqs, b3_pqs, mixed_pqs = generate_tree_ratios(12)

    # Compute empirical distribution
    max_k = 20

    def pq_distribution(pqs, max_k=20):
        if not pqs:
            return {}
        counts = Counter(pqs)
        total = sum(counts[k] for k in range(1, max_k+1))
        if total == 0:
            return {}
        return {k: counts.get(k, 0) / total for k in range(1, max_k+1)}

    dist_all = pq_distribution(all_pqs)
    dist_b1 = pq_distribution(b1_pqs)
    dist_b2 = pq_distribution(b2_pqs)
    dist_b3 = pq_distribution(b3_pqs)
    dist_mixed = pq_distribution(mixed_pqs)

    # Gauss-Kuzmin reference
    gk_dist = {k: gauss_kuzmin(k) for k in range(1, max_k+1)}

    # KL divergence from Gauss-Kuzmin
    def kl_divergence(empirical, reference):
        kl = 0
        for k in range(1, max_k+1):
            p = empirical.get(k, 1e-10)
            q = reference.get(k, 1e-10)
            if p > 0 and q > 0:
                kl += p * math.log(p / q)
        return kl

    kl_all = kl_divergence(dist_all, gk_dist) if dist_all else float('inf')
    kl_b1 = kl_divergence(dist_b1, gk_dist) if dist_b1 else float('inf')
    kl_b2 = kl_divergence(dist_b2, gk_dist) if dist_b2 else float('inf')
    kl_b3 = kl_divergence(dist_b3, gk_dist) if dist_b3 else float('inf')
    kl_mixed = kl_divergence(dist_mixed, gk_dist) if dist_mixed else float('inf')

    # Also generate random reals for comparison
    import random
    random.seed(42)
    random_pqs = []
    for _ in range(5000):
        x = random.random()
        if x > 0:
            pqs = cf_expand(x, 20)
            if len(pqs) > 1:
                random_pqs.extend(pqs[1:])
    dist_random = pq_distribution(random_pqs)
    kl_random = kl_divergence(dist_random, gk_dist)

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ks = list(range(1, max_k+1))
    gk_vals = [gk_dist[k] for k in ks]

    ax = axes[0, 0]
    if dist_all:
        ax.bar([k-0.2 for k in ks], [dist_all.get(k, 0) for k in ks], 0.4, label='Tree (all)', color='steelblue', alpha=0.8)
    ax.bar([k+0.2 for k in ks], gk_vals, 0.4, label='Gauss-Kuzmin', color='coral', alpha=0.8)
    ax.set_xlabel('Partial Quotient k')
    ax.set_ylabel('P(a=k)')
    ax.set_title(f'All Tree Ratios vs Gauss-Kuzmin (KL={kl_all:.4f})')
    ax.legend()
    ax.set_xlim(0, max_k+1)

    ax = axes[0, 1]
    if dist_b2:
        ax.bar([k-0.2 for k in ks], [dist_b2.get(k, 0) for k in ks], 0.4, label='B2 pure', color='green', alpha=0.8)
    ax.bar([k+0.2 for k in ks], gk_vals, 0.4, label='Gauss-Kuzmin', color='coral', alpha=0.8)
    ax.set_xlabel('Partial Quotient k')
    ax.set_ylabel('P(a=k)')
    ax.set_title(f'B2 Pure Paths (KL={kl_b2:.4f})')
    ax.legend()
    ax.set_xlim(0, max_k+1)

    ax = axes[1, 0]
    categories = ['All Tree', 'B1 pure', 'B2 pure', 'B3 pure', 'Mixed', 'Random']
    kl_vals = [kl_all, kl_b1, kl_b2, kl_b3, kl_mixed, kl_random]
    colors = ['steelblue', 'orange', 'green', 'purple', 'brown', 'gray']
    valid = [(c, k, col) for c, k, col in zip(categories, kl_vals, colors) if k != float('inf')]
    if valid:
        ax.bar([v[0] for v in valid], [v[1] for v in valid], color=[v[2] for v in valid], alpha=0.8)
        ax.set_ylabel('KL Divergence from Gauss-Kuzmin')
        ax.set_title('Deviation from Gauss-Kuzmin by Path Type')
        ax.axhline(y=0.01, color='red', linestyle='--', alpha=0.5, label='Threshold (0.01)')
        ax.legend()
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

    ax = axes[1, 1]
    # B2 pure should be very different: all PQ=2 (CF of 1+sqrt(2) = [2;2,2,...])
    if dist_b2:
        ax.bar(ks, [dist_b2.get(k, 0) for k in ks], color='green', alpha=0.8)
    ax.set_xlabel('Partial Quotient k')
    ax.set_ylabel('P(a=k)')
    ax.set_title('B2 Pure: Concentrated at k=2\n(CF of 1+sqrt(2) = [2;2,2,...])')

    plt.suptitle('Gauss-Kuzmin Distribution on Berggren Tree', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_07_gauss_kuzmin.png', dpi=150)
    plt.close()

    # Determine if tree distribution differs from GK
    differs = kl_all > 0.05  # significant deviation

    elapsed = time.time() - t0
    results['exp07'] = {
        'n_pqs': len(all_pqs),
        'n_b1': len(b1_pqs),
        'n_b2': len(b2_pqs),
        'n_b3': len(b3_pqs),
        'n_mixed': len(mixed_pqs),
        'kl_all': round(kl_all, 6),
        'kl_b1': round(kl_b1, 6) if kl_b1 != float('inf') else 'N/A',
        'kl_b2': round(kl_b2, 6) if kl_b2 != float('inf') else 'N/A',
        'kl_b3': round(kl_b3, 6) if kl_b3 != float('inf') else 'N/A',
        'kl_mixed': round(kl_mixed, 6) if kl_mixed != float('inf') else 'N/A',
        'kl_random': round(kl_random, 6),
        'differs_from_gk': differs,
        'dist_all_head': {k: round(dist_all.get(k,0), 4) for k in range(1,8)} if dist_all else {},
        'gk_head': {k: round(gk_dist[k], 4) for k in range(1,8)},
        'time': elapsed
    }
    print(f"  KL divergences: all={kl_all:.4f}, B2={kl_b2:.4f}, random={kl_random:.4f}")
    print(f"  Differs from Gauss-Kuzmin: {differs}")
    return results['exp07']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 8: CF universality (HIGH PRIORITY)
# ═══════════════════════════════════════════════════════════════════
def exp08_cf_universality():
    """Can every eventually periodic CF be realized as a path in extended Berggren tree?"""
    print("=== Exp 8: CF universality ===")
    t0 = time.time()

    # The extended Berggren group = <B1, B2, B3, B1^-1, B2^-1, B3^-1>
    # B2 = M(2) = [[2,1],[1,0]], and M(a) = [[a,1],[1,0]]
    # M(a) = product of B2 and B1/B3 matrices?

    # Key insight: SL(2,Z) is generated by S=[[0,-1],[1,0]] and T=[[1,1],[0,1]]
    # B1_2 = T^2 (double translation)
    # B2_2 = M(2) = T*S*T (not quite standard)
    # The extended group <B1_2, B2_2, B3_2, inverses> - is it SL(2,Z)?

    # Check: can we express S and T using B1_2, B2_2, B3_2?
    S = np.array([[0,-1],[1,0]], dtype=object)
    T = np.array([[1,1],[0,1]], dtype=object)
    I = np.array([[1,0],[0,1]], dtype=object)

    B1_inv = np.array([[1,-2],[0,1]], dtype=object)
    B2_inv = np.array([[0,1],[1,-2]], dtype=object)  # M(2)^-1 = [[0,1],[1,-2]]
    B3_inv = np.array([[-1,-2],[0,1]], dtype=object)

    # T = [[1,1],[0,1]]. B1_2 = T^2 = [[1,2],[0,1]].
    # So T is NOT in <B1,B2,B3> directly (need sqrt of B1).
    # But T^2 = B1_2. Can we get T from B2 and B1?

    # B2_2 * B1_inv = [[2,1],[1,0]] * [[1,-2],[0,1]] = [[2,-3],[1,-2]]
    test1 = matmul_int(B2_2, B1_inv)
    # = [[2,-3],[1,-2]], det = -4+3 = -1. This is in GL(2,Z) but not SL(2,Z).

    # Actually B3_2 = [[-1,2],[0,1]] has det = -1. So extended group includes GL(2,Z) elements.

    # SL(2,Z) is generated by T and S. T^2 = B1_2.
    # Can we get S? S = [[0,-1],[1,0]], det = 1.
    # Try: B2_2 = [[2,1],[1,0]]. B2_2 * S = [[2*0+1*1, 2*(-1)+1*0],[1*0+0*1, 1*(-1)+0*0]] = [[1,-2],[0,-1]]
    # Hmm, let me just do BFS to find S and T

    generators = {
        'B1': B1_2, 'B2': B2_2, 'B3': B3_2,
        'B1i': B1_inv, 'B2i': B2_inv, 'B3i': B3_inv
    }

    # BFS: find T and S as products of generators
    def mat_key(M):
        return (int(M[0,0]), int(M[0,1]), int(M[1,0]), int(M[1,1]))

    visited = {mat_key(I): ''}
    frontier = [(I, '')]
    target_T = mat_key(T)
    target_S = mat_key(S)
    found_T = None
    found_S = None

    for depth in range(1, 8):
        new_frontier = []
        for M, path in frontier:
            for name, G in generators.items():
                M2 = matmul_int(M, G)
                k = mat_key(M2)
                if k not in visited:
                    visited[k] = path + '.' + name if path else name
                    new_frontier.append((M2, visited[k]))
                    if k == target_T and found_T is None:
                        found_T = visited[k]
                    if k == target_S and found_S is None:
                        found_S = visited[k]
        frontier = new_frontier
        if found_T and found_S:
            break
        if len(visited) > 500000:
            break

    # Also check: can we express M(a) for a=1..10?
    cf_matrices_found = {}
    for a in range(1, 11):
        target = mat_key(mat_cf(a))
        if target in visited:
            cf_matrices_found[a] = visited[target]
        else:
            cf_matrices_found[a] = 'NOT FOUND'

    # Test: periodic CFs [a;a,a,...] for a=1..5
    # These correspond to sqrt(a^2+4)/2 type numbers
    periodic_cf_reachable = {}
    for a in range(1, 6):
        # CF [a;a,a,...] = M(a)^k. If M(a) is reachable, then all powers are.
        if a in cf_matrices_found and cf_matrices_found[a] != 'NOT FOUND':
            periodic_cf_reachable[a] = True
        else:
            periodic_cf_reachable[a] = False

    # The key theorem: if S and T are expressible, then SL(2,Z) = <S,T> is contained
    # in <B1,B2,B3,inverses>. Since every CF matrix M(a) is in SL(2,Z),
    # every periodic CF corresponds to a periodic path in the extended tree.

    # BUT: M(a) for odd a has det = -1 (wait, no: det(M(a)) = -1 for all a)
    # Actually det([[a,1],[1,0]]) = -1. So M(a) is in GL(2,Z), not SL(2,Z).
    # M(a)*M(b) has det = 1. So even-length CFs are in SL(2,Z).

    # Extended group has B3 with det=-1, so it generates GL(2,Z).

    generates_gl2z = found_T is not None  # If we can get T, we can get all of GL(2,Z)

    elapsed = time.time() - t0
    results['exp08'] = {
        'found_T': found_T,
        'found_S': found_S,
        'cf_matrices': cf_matrices_found,
        'periodic_reachable': periodic_cf_reachable,
        'generates_gl2z': generates_gl2z,
        'visited_count': len(visited),
        'time': elapsed
    }
    print(f"  T found: {found_T}")
    print(f"  S found: {found_S}")
    print(f"  CF matrices: {cf_matrices_found}")
    print(f"  Generates GL(2,Z): {generates_gl2z}")
    return results['exp08']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 9: Minkowski ?-function on tree
# ═══════════════════════════════════════════════════════════════════
def exp09_minkowski():
    """Apply Minkowski ? function to tree ratios. Check for dyadic structure."""
    print("=== Exp 9: Minkowski ?-function on tree ===")
    t0 = time.time()

    def minkowski_question(x, max_iter=100):
        """Compute Minkowski ?(x) for x in [0,1]."""
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        # CF expansion then binary decode
        pqs = cf_expand(x, max_iter)
        result = 0.0
        sign = 1
        power = 1.0
        for a in pqs:
            power /= 2**a
            result += sign * power
            sign = -sign
        return result

    # Generate tree ratios at various depths
    # Use min(a,b)/max(a,b) to get value in [0,1]
    from itertools import product as iprod

    b2_ratios = []
    b1_ratios = []
    b3_ratios = []
    mixed_ratios = []

    for depth in range(1, 10):
        for path in iprod([0,1,2], repeat=depth):
            triple = np.array([3, 4, 5])
            matrices_3 = [B1, B2, B3]
            for step in path:
                triple = matrices_3[step] @ triple
            triple = np.abs(triple)
            a, b, c = triple
            if max(a,b) > 0:
                ratio = min(a,b) / max(a,b)
                if all(s == 1 for s in path):
                    b2_ratios.append(ratio)
                elif all(s == 0 for s in path):
                    b1_ratios.append(ratio)
                elif all(s == 2 for s in path):
                    b3_ratios.append(ratio)
                else:
                    mixed_ratios.append(ratio)
            if len(mixed_ratios) > 5000:
                break
        if len(mixed_ratios) > 5000:
            break

    # Apply ? to all ratios
    def check_dyadic(values, label):
        """Check if ?(x) values are dyadic rationals (k/2^n)."""
        q_vals = [minkowski_question(x) for x in values[:200]]
        n_dyadic = 0
        for q in q_vals:
            # Check if q = k/2^n for small n
            for n in range(1, 30):
                k = round(q * 2**n)
                if abs(q - k / 2**n) < 1e-10:
                    n_dyadic += 1
                    break
        return q_vals, n_dyadic, n_dyadic / len(q_vals) if q_vals else 0

    q_b2, nd_b2, rate_b2 = check_dyadic(b2_ratios, 'B2')
    q_b1, nd_b1, rate_b1 = check_dyadic(b1_ratios, 'B1')
    q_b3, nd_b3, rate_b3 = check_dyadic(b3_ratios, 'B3')
    q_mixed, nd_mixed, rate_mixed = check_dyadic(mixed_ratios, 'Mixed')

    # Random comparison
    import random
    random.seed(42)
    rand_vals = [random.random() for _ in range(200)]
    q_rand, nd_rand, rate_rand = check_dyadic(rand_vals, 'Random')

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    ax = axes[0]
    if b2_ratios:
        ax.scatter(b2_ratios[:100], q_b2[:100], s=10, alpha=0.7, label='B2', color='green')
    if b1_ratios:
        ax.scatter(b1_ratios[:100], q_b1[:100], s=10, alpha=0.7, label='B1', color='orange')
    ax.plot([0,1], [0,1], 'k--', alpha=0.3, label='y=x')
    ax.set_xlabel('x = min(a,b)/max(a,b)')
    ax.set_ylabel('?(x)')
    ax.set_title('Minkowski ? on Tree Ratios')
    ax.legend(fontsize=8)

    ax = axes[1]
    categories = ['B1', 'B2', 'B3', 'Mixed', 'Random']
    rates = [rate_b1, rate_b2, rate_b3, rate_mixed, rate_rand]
    colors = ['orange', 'green', 'purple', 'brown', 'gray']
    ax.bar(categories, rates, color=colors, alpha=0.8)
    ax.set_ylabel('Fraction Dyadic')
    ax.set_title('Dyadic Rational Rate of ?(ratio)')
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.3)

    ax = axes[2]
    if q_b2:
        ax.hist(q_b2, bins=30, alpha=0.7, label='B2', color='green', density=True)
    if q_mixed:
        ax.hist(q_mixed[:200], bins=30, alpha=0.5, label='Mixed', color='brown', density=True)
    ax.set_xlabel('?(x)')
    ax.set_ylabel('Density')
    ax.set_title('Distribution of ?(tree ratios)')
    ax.legend()

    plt.suptitle('Minkowski Question-Mark Function on Berggren Tree', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_09_minkowski.png', dpi=150)
    plt.close()

    elapsed = time.time() - t0
    results['exp09'] = {
        'n_b2': len(b2_ratios),
        'n_b1': len(b1_ratios),
        'n_b3': len(b3_ratios),
        'dyadic_rate_b2': round(rate_b2, 4),
        'dyadic_rate_b1': round(rate_b1, 4),
        'dyadic_rate_b3': round(rate_b3, 4),
        'dyadic_rate_mixed': round(rate_mixed, 4),
        'dyadic_rate_random': round(rate_rand, 4),
        'time': elapsed
    }
    print(f"  Dyadic rates: B1={rate_b1:.3f}, B2={rate_b2:.3f}, B3={rate_b3:.3f}, Mixed={rate_mixed:.3f}, Random={rate_rand:.3f}")
    return results['exp09']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 10: Stern-Brocot mediant as factoring tool
# ═══════════════════════════════════════════════════════════════════
def exp10_stern_brocot():
    """Compare Stern-Brocot vs Berggren for rational approximations to sqrt(N)."""
    print("=== Exp 10: Stern-Brocot mediant as factoring tool ===")
    t0 = time.time()

    import random
    random.seed(42)

    # Test numbers
    test_ns = []
    for _ in range(20):
        p = random.randint(10**6, 10**7)
        while not is_prime(p): p += 1
        q = random.randint(10**6, 10**7)
        while not is_prime(q): q += 1
        test_ns.append(p * q)

    def stern_brocot_approx(target, max_depth=100):
        """Find best rational approximations to target via Stern-Brocot tree."""
        a_num, a_den = 0, 1  # left = 0/1
        b_num, b_den = 1, 0  # right = 1/0 = infinity
        approxs = []
        for _ in range(max_depth):
            m_num = a_num + b_num
            m_den = a_den + b_den
            approxs.append((m_num, m_den))
            if m_den > 10**8:
                break
            val = m_num / m_den if m_den > 0 else float('inf')
            if val < target:
                a_num, a_den = m_num, m_den
            elif val > target:
                b_num, b_den = m_num, m_den
            else:
                break
        return approxs

    def cf_approx(target, max_terms=100):
        """CF convergents of target."""
        pqs = cf_expand(target, max_terms)
        return cf_convergents(pqs)

    def berggren_approx(target, max_depth=100):
        """Berggren tree: traverse toward target using (m,n) -> a/b ~ target."""
        triple = np.array([3, 4, 5])
        approxs = []
        matrices_3 = [B1, B2, B3]
        for _ in range(max_depth):
            best_dist = float('inf')
            best_m = None
            best_triple = None
            for i, M in enumerate(matrices_3):
                t = M @ triple
                t = np.abs(t)
                a, b, c = t
                if b > 0:
                    ratio = a / b
                    dist = abs(ratio - target)
                    if dist < best_dist:
                        best_dist = dist
                        best_m = i
                        best_triple = t
            if best_triple is None:
                break
            triple = best_triple
            a, b, c = triple
            approxs.append((int(a), int(b)))
            if best_dist < 1e-15:
                break
        return approxs

    # Compare smoothness of |p^2 - N*q^2| for each method
    def smooth_bound(n_digits):
        return 10**(n_digits // 4)

    def is_bsmooth(val, B):
        if val == 0: return True
        val = abs(val)
        for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
            if p > B: break
            while val % p == 0:
                val //= p
        return val == 1

    sb_smooth_count = 0
    cf_smooth_count = 0
    berg_smooth_count = 0
    sb_total = 0
    cf_total = 0
    berg_total = 0

    for N in test_ns:
        sqrtN = math.sqrt(N)
        B = smooth_bound(len(str(N)))

        # Stern-Brocot
        sb_approxs = stern_brocot_approx(sqrtN, 80)
        for p, q in sb_approxs:
            if q > 0:
                residue = abs(p*p - N*q*q)
                if residue > 0:
                    sb_total += 1
                    if is_bsmooth(residue, B):
                        sb_smooth_count += 1

        # CF
        cf_approxs = cf_approx(sqrtN, 80)
        for p, q in cf_approxs:
            if q > 0:
                residue = abs(p*p - N*q*q)
                if residue > 0:
                    cf_total += 1
                    if is_bsmooth(residue, B):
                        cf_smooth_count += 1

        # Berggren
        berg_approxs = berggren_approx(sqrtN, 80)
        for p, q in berg_approxs:
            if q > 0:
                residue = abs(p*p - N*q*q)
                if residue > 0:
                    berg_total += 1
                    if is_bsmooth(residue, B):
                        berg_smooth_count += 1

    sb_rate = sb_smooth_count / sb_total if sb_total > 0 else 0
    cf_rate = cf_smooth_count / cf_total if cf_total > 0 else 0
    berg_rate = berg_smooth_count / berg_total if berg_total > 0 else 0

    elapsed = time.time() - t0
    results['exp10'] = {
        'sb_smooth': sb_smooth_count, 'sb_total': sb_total, 'sb_rate': round(sb_rate, 4),
        'cf_smooth': cf_smooth_count, 'cf_total': cf_total, 'cf_rate': round(cf_rate, 4),
        'berg_smooth': berg_smooth_count, 'berg_total': berg_total, 'berg_rate': round(berg_rate, 4),
        'time': elapsed
    }
    print(f"  SB: {sb_smooth_count}/{sb_total} ({sb_rate:.3f}), CF: {cf_smooth_count}/{cf_total} ({cf_rate:.3f}), Berg: {berg_smooth_count}/{berg_total} ({berg_rate:.3f})")
    return results['exp10']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 11: Parallel GCD from tree (HIGH PRIORITY)
# ═══════════════════════════════════════════════════════════════════
def exp11_parallel_gcd():
    """Design and benchmark a 3-way parallel GCD using Berggren-like reductions."""
    print("=== Exp 11: Parallel GCD from tree ===")
    t0 = time.time()

    import random
    random.seed(42)

    def standard_gcd(a, b):
        """Standard Euclidean GCD, count steps."""
        steps = 0
        while b:
            a, b = b, a % b
            steps += 1
        return a, steps

    def binary_gcd(a, b):
        """Binary GCD (Stein's algorithm), count steps."""
        if a == 0: return b, 0
        if b == 0: return a, 0
        steps = 0
        shift = 0
        while ((a | b) & 1) == 0:
            a >>= 1
            b >>= 1
            shift += 1
            steps += 1
        while (a & 1) == 0:
            a >>= 1
            steps += 1
        while b != 0:
            while (b & 1) == 0:
                b >>= 1
                steps += 1
            if a > b:
                a, b = b, a
            b -= a
            steps += 1
        return a << shift, steps

    def berggren_gcd(a, b):
        """3-way GCD: at each step try 3 reductions inspired by B1,B2,B3.
        B1-like: subtract, B2-like: standard mod, B3-like: subtract with swap.
        Pick whichever gives smallest remainder."""
        steps = 0
        while b != 0:
            if a < b:
                a, b = b, a
            # Three candidates:
            # R1: standard mod (Euclidean)
            r1 = a % b
            # R2: a - 2*b (B1 = double subtraction, if positive)
            r2 = a - 2*b if a >= 2*b else a % b
            # R3: (a + b) % max(a,b) -- mix
            r3 = (a - b) if a > b else 0

            # Pick smallest positive remainder
            candidates = [(r1, 'R1'), (r2, 'R2'), (r3, 'R3')]
            candidates = [(r, name) for r, name in candidates if r >= 0]
            if not candidates:
                break
            best = min(candidates, key=lambda x: x[0] if x[0] > 0 else float('inf'))
            if best[0] == 0:
                # Try to find zero
                for r, name in candidates:
                    if r == 0:
                        b = 0
                        break
                break
            a, b = b, best[0]
            steps += 1
        return a, steps

    # Benchmark
    bit_sizes = [64, 128, 256, 512]
    n_pairs = 1000

    bench_results = []
    for bits in bit_sizes:
        pairs = [(random.randint(2**(bits-1), 2**bits), random.randint(2**(bits-1), 2**bits)) for _ in range(n_pairs)]

        # Standard Euclidean
        t1 = time.time()
        std_steps = 0
        for a, b in pairs:
            _, s = standard_gcd(a, b)
            std_steps += s
        t_std = time.time() - t1

        # Binary GCD
        t1 = time.time()
        bin_steps = 0
        for a, b in pairs:
            _, s = binary_gcd(a, b)
            bin_steps += s
        t_bin = time.time() - t1

        # Berggren 3-way
        t1 = time.time()
        berg_steps = 0
        for a, b in pairs:
            _, s = berggren_gcd(a, b)
            berg_steps += s
        t_berg = time.time() - t1

        # Verify correctness
        correct = True
        for a, b in pairs[:100]:
            g1, _ = standard_gcd(a, b)
            g2, _ = berggren_gcd(a, b)
            if g1 != g2:
                correct = False
                break

        bench_results.append({
            'bits': bits,
            'std_time': round(t_std, 4),
            'bin_time': round(t_bin, 4),
            'berg_time': round(t_berg, 4),
            'std_steps_avg': round(std_steps / n_pairs, 1),
            'bin_steps_avg': round(bin_steps / n_pairs, 1),
            'berg_steps_avg': round(berg_steps / n_pairs, 1),
            'berg_vs_std_ratio': round(t_berg / t_std, 3) if t_std > 0 else 0,
            'correct': correct
        })

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    bits_list = [r['bits'] for r in bench_results]
    ax.plot(bits_list, [r['std_steps_avg'] for r in bench_results], 'o-', label='Euclidean', color='steelblue')
    ax.plot(bits_list, [r['bin_steps_avg'] for r in bench_results], 's-', label='Binary', color='coral')
    ax.plot(bits_list, [r['berg_steps_avg'] for r in bench_results], '^-', label='Berggren 3-way', color='green')
    ax.set_xlabel('Bit size')
    ax.set_ylabel('Average steps')
    ax.set_title('GCD Steps by Algorithm')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(bits_list, [r['std_time'] for r in bench_results], 'o-', label='Euclidean', color='steelblue')
    ax.plot(bits_list, [r['bin_time'] for r in bench_results], 's-', label='Binary', color='coral')
    ax.plot(bits_list, [r['berg_time'] for r in bench_results], '^-', label='Berggren 3-way', color='green')
    ax.set_xlabel('Bit size')
    ax.set_ylabel('Time (s) for 1000 pairs')
    ax.set_title('GCD Wall Time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.suptitle('Parallel GCD via Berggren Reductions', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_11_gcd.png', dpi=150)
    plt.close()

    elapsed = time.time() - t0
    results['exp11'] = {
        'bench_results': bench_results,
        'time': elapsed
    }
    print(f"  Results: {[(r['bits'], r['berg_vs_std_ratio']) for r in bench_results]}")
    return results['exp11']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 12: CF neural network layer
# ═══════════════════════════════════════════════════════════════════
def exp12_cf_nn_layer():
    """CF 'bottleneck' layer vs ReLU for function approximation."""
    print("=== Exp 12: CF neural network layer ===")
    t0 = time.time()

    # CF layer: input x -> CF expand to k terms -> reconstruct
    # This forces a rational approximation bottleneck

    def cf_layer(x_arr, k_terms=5):
        """CF bottleneck: expand each x to k CF terms, reconstruct."""
        out = np.zeros_like(x_arr)
        for i, x in enumerate(x_arr):
            if abs(x) < 1e-15:
                out[i] = 0
                continue
            sign = 1 if x >= 0 else -1
            x_abs = abs(x)
            pqs = cf_expand(x_abs, k_terms)
            # Reconstruct from truncated CF
            if not pqs:
                out[i] = 0
                continue
            # Backward reconstruction
            val = pqs[-1]
            for a in reversed(pqs[:-1]):
                if val != 0:
                    val = a + 1.0/val
                else:
                    val = a
            out[i] = sign * val
        return out

    def relu_layer(x_arr, weights, biases):
        """Standard dense + ReLU."""
        return np.maximum(0, x_arr.reshape(-1, 1) @ weights.reshape(1, -1) + biases)

    # Target: approximate sin(x) on [0, 2*pi]
    x_train = np.linspace(0.1, 2*np.pi - 0.1, 200)
    y_true = np.sin(x_train)

    # CF approximation with different k
    cf_errors = {}
    for k in [2, 3, 4, 5, 7, 10]:
        # CF layer: sin(x) ~ CF_k(x) doesn't make sense directly
        # Better: approximate sin(x) as rational function via CF
        # Use CF of y_true values
        y_cf = cf_layer(y_true, k_terms=k)
        mse = np.mean((y_true - y_cf)**2)
        cf_errors[k] = mse

    # ReLU approximation: use k neurons (same parameter count as k CF terms)
    relu_errors = {}
    np.random.seed(42)
    for k in [2, 3, 4, 5, 7, 10]:
        # Simple: k piecewise linear segments
        # Optimal for sin: place breakpoints at extrema
        breakpoints = np.linspace(0.1, 2*np.pi - 0.1, k+1)
        y_relu = np.interp(x_train, breakpoints, np.sin(breakpoints))
        mse = np.mean((y_true - y_relu)**2)
        relu_errors[k] = mse

    # Also: CF of x as preprocessing, then linear fit
    # sin(x) ~ a * CF_k(x) + b
    cf_preprocess_errors = {}
    for k in [2, 3, 4, 5, 7, 10]:
        x_cf = cf_layer(x_train / (2*np.pi), k_terms=k) * 2 * np.pi
        # Linear regression
        A = np.column_stack([x_cf, np.ones(len(x_cf))])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(A, y_true, rcond=None)
            y_pred = A @ coeffs
            mse = np.mean((y_true - y_pred)**2)
        except:
            mse = float('inf')
        cf_preprocess_errors[k] = mse

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    ks = sorted(cf_errors.keys())

    ax = axes[0]
    ax.semilogy(ks, [cf_errors[k] for k in ks], 'o-', label='CF reconstruct', color='steelblue')
    ax.semilogy(ks, [relu_errors[k] for k in ks], 's-', label='ReLU (piecewise)', color='coral')
    ax.semilogy(ks, [cf_preprocess_errors[k] for k in ks], '^-', label='CF preprocess+linear', color='green')
    ax.set_xlabel('Parameters k')
    ax.set_ylabel('MSE')
    ax.set_title('sin(x) Approximation Error')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    k_show = 5
    y_cf_show = cf_layer(y_true, k_terms=k_show)
    breakpoints = np.linspace(0.1, 2*np.pi - 0.1, k_show+1)
    y_relu_show = np.interp(x_train, breakpoints, np.sin(breakpoints))
    ax.plot(x_train, y_true, 'k-', label='sin(x)', linewidth=2)
    ax.plot(x_train, y_cf_show, '--', label=f'CF k={k_show}', color='steelblue')
    ax.plot(x_train, y_relu_show, '--', label=f'ReLU k={k_show}', color='coral')
    ax.set_xlabel('x')
    ax.set_title(f'Approximations at k={k_show}')
    ax.legend(fontsize=8)

    ax = axes[2]
    # Error distribution
    err_cf = np.abs(y_true - y_cf_show)
    err_relu = np.abs(y_true - y_relu_show)
    ax.plot(x_train, err_cf, label='CF error', color='steelblue', alpha=0.8)
    ax.plot(x_train, err_relu, label='ReLU error', color='coral', alpha=0.8)
    ax.set_xlabel('x')
    ax.set_ylabel('|error|')
    ax.set_title('Pointwise Error')
    ax.legend(fontsize=8)

    plt.suptitle('CF Neural Network Layer vs ReLU', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_12_nn.png', dpi=150)
    plt.close()

    elapsed = time.time() - t0
    results['exp12'] = {
        'cf_errors': {k: round(v, 8) for k, v in cf_errors.items()},
        'relu_errors': {k: round(v, 8) for k, v in relu_errors.items()},
        'cf_preprocess_errors': {k: round(v, 8) for k, v in cf_preprocess_errors.items()},
        'time': elapsed
    }
    print(f"  CF MSE: {cf_errors}")
    print(f"  ReLU MSE: {relu_errors}")
    return results['exp12']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 13: CF streaming compression
# ═══════════════════════════════════════════════════════════════════
def exp13_cf_compression():
    """CF-based streaming compression vs delta encoding."""
    print("=== Exp 13: CF streaming compression ===")
    t0 = time.time()

    np.random.seed(42)

    def cf_encode(values, max_pq=50):
        """Encode sequence as CF partial quotients.
        For each value, store (continuation_flag, partial_quotient)."""
        encoded = []
        for v in values:
            if abs(v) < 1e-15:
                encoded.append((0, 0))
                continue
            pqs = cf_expand(abs(v), 10)
            sign = 1 if v >= 0 else -1
            for i, a in enumerate(pqs):
                a_clipped = min(a, max_pq)
                cont = 1 if i < len(pqs) - 1 else 0
                encoded.append((cont, sign * a_clipped))
                sign = 1  # sign only on first
        return encoded

    def cf_bits(encoded, max_pq=50):
        """Bits needed: 1 bit for continuation, ceil(log2(max_pq+1)) for PQ, 1 for sign."""
        pq_bits = math.ceil(math.log2(max_pq + 1))
        return len(encoded) * (1 + pq_bits + 1)

    def delta_encode(values):
        """Delta encoding."""
        if len(values) == 0:
            return []
        deltas = [values[0]]
        for i in range(1, len(values)):
            deltas.append(values[i] - values[i-1])
        return deltas

    def delta_bits(deltas):
        """Estimate bits for delta-encoded values using variable-length encoding."""
        total = 0
        for d in deltas:
            if d == 0:
                total += 1
            else:
                total += 1 + math.ceil(math.log2(abs(d) + 1)) + 1  # sign + magnitude
        return total

    def raw_bits(values, precision=32):
        return len(values) * precision

    # Test signals
    n_points = 500
    t_vals = np.linspace(0, 10, n_points)

    signals = {
        'Random walk': np.cumsum(np.random.randn(n_points)),
        'Sine wave': np.sin(2 * np.pi * t_vals / 3),
        'Brownian': np.cumsum(np.random.randn(n_points)) / np.sqrt(n_points),
        'ECG-like': np.sin(2*np.pi*t_vals) + 0.5*np.sin(6*np.pi*t_vals) + 0.2*np.random.randn(n_points),
        'Constant': np.ones(n_points) * 3.14159,
    }

    compression_results = {}
    for name, signal in signals.items():
        # Normalize to [0, 10] range
        sig = signal.copy()
        sig_range = sig.max() - sig.min()
        if sig_range > 0:
            sig = (sig - sig.min()) / sig_range * 10

        # Raw bits
        raw = raw_bits(sig, precision=32)

        # CF encoding
        cf_enc = cf_encode(sig)
        cf_b = cf_bits(cf_enc)

        # Delta encoding
        delta = delta_encode(sig)
        delta_b = delta_bits(delta)

        compression_results[name] = {
            'raw_bits': raw,
            'cf_bits': cf_b,
            'delta_bits': delta_b,
            'cf_ratio': round(raw / cf_b, 3) if cf_b > 0 else 0,
            'delta_ratio': round(raw / delta_b, 3) if delta_b > 0 else 0,
        }

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    names = list(compression_results.keys())
    cf_ratios = [compression_results[n]['cf_ratio'] for n in names]
    delta_ratios = [compression_results[n]['delta_ratio'] for n in names]

    x_pos = np.arange(len(names))
    ax.bar(x_pos - 0.15, cf_ratios, 0.3, label='CF compression', color='steelblue')
    ax.bar(x_pos + 0.15, delta_ratios, 0.3, label='Delta compression', color='coral')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, rotation=20, ha='right')
    ax.set_ylabel('Compression Ratio (higher = better)')
    ax.set_title('CF Streaming Compression vs Delta Encoding')
    ax.legend()
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_13_compression.png', dpi=150)
    plt.close()

    elapsed = time.time() - t0
    results['exp13'] = {
        'compression_results': compression_results,
        'time': elapsed
    }
    print(f"  Results: {compression_results}")
    return results['exp13']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 14: CF for GPS coordinates
# ═══════════════════════════════════════════════════════════════════
def exp14_cf_gps():
    """CF compression of GPS lat/lon pairs vs raw float and fixed-point."""
    print("=== Exp 14: CF for GPS coordinates ===")
    t0 = time.time()

    import random
    random.seed(42)

    # Generate 10000 random GPS coordinates
    n_coords = 10000
    lats = [random.uniform(-90, 90) for _ in range(n_coords)]
    lons = [random.uniform(-180, 180) for _ in range(n_coords)]

    # Method 1: Raw float64 — 64 bits per value
    raw_bits_total = n_coords * 2 * 64

    # Method 2: Fixed-point (6 decimal places = microdegreee, enough for ~11cm precision)
    # Lat: [-90, 90] -> 180 * 10^6 values -> ~28 bits
    # Lon: [-180, 180] -> 360 * 10^6 values -> ~29 bits
    fp_bits = n_coords * (28 + 29)

    # Method 3: CF encoding
    # Encode each coordinate as CF partial quotients
    # For GPS: value is in degrees, multiply by 10^6 to get integer, then CF of p/q
    cf_total_bits = 0
    cf_terms_total = 0
    cf_terms_per_coord = []

    for lat, lon in zip(lats, lons):
        for val in [lat, lon]:
            # Convert to rational: val * 10^6 / 10^6
            p = int(round(val * 1000000))
            q = 1000000
            g = gcd(abs(p), q)
            p //= g
            q //= g
            pqs = cf_from_fraction(abs(p), q, 30)
            n_terms = len(pqs)
            cf_terms_total += n_terms
            cf_terms_per_coord.append(n_terms)
            # Bits: sign (1) + each PQ needs log2(pq+1) bits
            bits = 1  # sign
            for a in pqs:
                bits += max(1, math.ceil(math.log2(abs(a) + 2)))
            cf_total_bits += bits

    # Compression ratios
    cf_ratio = raw_bits_total / cf_total_bits if cf_total_bits > 0 else 0
    fp_ratio = raw_bits_total / fp_bits if fp_bits > 0 else 0

    # Verify lossless: reconstruct from CF and check error
    max_errors = []
    for i in range(min(100, n_coords)):
        for val in [lats[i], lons[i]]:
            p = int(round(val * 1000000))
            q = 1000000
            g = gcd(abs(p), q)
            pn, qn = p // g, q // g
            pqs = cf_from_fraction(abs(pn), qn, 30)
            convs = cf_convergents(pqs)
            if convs:
                recon = convs[-1][0] / convs[-1][1] if convs[-1][1] != 0 else 0
                if pn < 0: recon = -recon
                error = abs(recon * g - p) / 1000000
                max_errors.append(error)

    max_error = max(max_errors) if max_errors else 0
    mean_cf_terms = np.mean(cf_terms_per_coord)

    elapsed = time.time() - t0
    results['exp14'] = {
        'raw_bits': raw_bits_total,
        'fp_bits': fp_bits,
        'cf_bits': cf_total_bits,
        'cf_ratio': round(cf_ratio, 3),
        'fp_ratio': round(fp_ratio, 3),
        'mean_cf_terms': round(mean_cf_terms, 2),
        'max_recon_error': max_error,
        'time': elapsed
    }
    print(f"  CF ratio: {cf_ratio:.3f}x, FP ratio: {fp_ratio:.3f}x, Mean CF terms: {mean_cf_terms:.1f}")
    return results['exp14']

# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 15: Medical signal compression
# ═══════════════════════════════════════════════════════════════════
def exp15_medical_signal():
    """CF compression of quasi-periodic signals vs wavelet."""
    print("=== Exp 15: Medical signal compression ===")
    t0 = time.time()

    np.random.seed(42)

    # Synthetic ECG: P-QRS-T complex
    t_ecg = np.linspace(0, 4, 2000)  # 4 seconds at 500Hz

    def ecg_beat(t, offset=0, hr=72):
        """Single ECG beat template."""
        period = 60.0 / hr
        t_rel = (t - offset) % period
        t_n = t_rel / period  # normalized 0-1

        # P wave
        p = 0.15 * np.exp(-((t_n - 0.1)**2) / (2 * 0.01**2))
        # QRS complex
        q = -0.1 * np.exp(-((t_n - 0.25)**2) / (2 * 0.003**2))
        r = 1.0 * np.exp(-((t_n - 0.27)**2) / (2 * 0.005**2))
        s = -0.15 * np.exp(-((t_n - 0.30)**2) / (2 * 0.004**2))
        # T wave
        tw = 0.3 * np.exp(-((t_n - 0.55)**2) / (2 * 0.03**2))

        return p + q + r + s + tw

    ecg = np.array([ecg_beat(t) for t in t_ecg]) + 0.02 * np.random.randn(len(t_ecg))

    # Method 1: CF compression
    # Segment into windows, CF-encode each window
    window = 50
    n_windows = len(ecg) // window

    cf_total_bits = 0
    cf_reconstructed = np.zeros_like(ecg)

    for w in range(n_windows):
        segment = ecg[w*window:(w+1)*window]
        # Normalize segment
        seg_min, seg_max = segment.min(), segment.max()
        seg_range = seg_max - seg_min
        if seg_range < 1e-10:
            seg_range = 1.0
        seg_norm = (segment - seg_min) / seg_range

        # CF encode: store as rational approximations
        bits_header = 32 + 32  # min and range as float32
        bits_data = 0
        recon = np.zeros(window)
        for i, v in enumerate(seg_norm):
            # CF with limited terms
            k_terms = 4
            pqs = cf_expand(max(v, 1e-10), k_terms)
            # Reconstruct
            val = pqs[-1] if pqs else 0
            for a in reversed(pqs[:-1]):
                if val != 0:
                    val = a + 1.0/val
                else:
                    val = a
            recon[i] = val
            # Bits per value: sum of log2(pq+1) for each term
            for a in pqs:
                bits_data += max(1, math.ceil(math.log2(abs(a) + 2)))

        cf_total_bits += bits_header + bits_data
        cf_reconstructed[w*window:(w+1)*window] = recon * seg_range + seg_min

    cf_mse = np.mean((ecg[:n_windows*window] - cf_reconstructed[:n_windows*window])**2)

    # Method 2: Simple wavelet-like compression (Haar)
    def haar_compress(signal, keep_ratio=0.3):
        """Simple Haar wavelet compression."""
        n = len(signal)
        # Pad to power of 2
        n_pad = 2**math.ceil(math.log2(n))
        padded = np.zeros(n_pad)
        padded[:n] = signal

        # Haar transform
        coeffs = padded.copy()
        length = n_pad
        while length > 1:
            half = length // 2
            temp = np.zeros(length)
            for i in range(half):
                temp[i] = (coeffs[2*i] + coeffs[2*i+1]) / 2
                temp[half+i] = (coeffs[2*i] - coeffs[2*i+1]) / 2
            coeffs[:length] = temp
            length = half

        # Keep only top keep_ratio fraction of coefficients
        n_keep = max(1, int(n_pad * keep_ratio))
        indices = np.argsort(np.abs(coeffs))[::-1][:n_keep]
        compressed = np.zeros(n_pad)
        compressed[indices] = coeffs[indices]

        # Inverse Haar
        length = 2
        while length <= n_pad:
            half = length // 2
            temp = np.zeros(length)
            for i in range(half):
                temp[2*i] = compressed[i] + compressed[half+i]
                temp[2*i+1] = compressed[i] - compressed[half+i]
            compressed[:length] = temp
            length *= 2

        recon = compressed[:n]
        bits = n_keep * 32 + n_keep * math.ceil(math.log2(n_pad + 1))  # value + index
        return recon, bits

    # Find Haar ratio that gives similar MSE to CF
    haar_recon, haar_bits = haar_compress(ecg, keep_ratio=0.3)
    haar_mse = np.mean((ecg - haar_recon)**2)

    # Raw bits
    raw_bits_ecg = len(ecg) * 32

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    ax.plot(t_ecg[:500], ecg[:500], 'k-', linewidth=0.8, label='Original')
    ax.plot(t_ecg[:500], cf_reconstructed[:500], 'b--', linewidth=0.8, label='CF', alpha=0.8)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title('ECG: CF Reconstruction')
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(t_ecg[:500], ecg[:500], 'k-', linewidth=0.8, label='Original')
    ax.plot(t_ecg[:500], haar_recon[:500], 'r--', linewidth=0.8, label='Haar', alpha=0.8)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title('ECG: Haar Wavelet Reconstruction')
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    methods = ['Raw', 'CF', 'Haar']
    bits_vals = [raw_bits_ecg, cf_total_bits, haar_bits]
    ax.bar(methods, [b/1000 for b in bits_vals], color=['gray', 'steelblue', 'coral'], alpha=0.8)
    ax.set_ylabel('Kilobits')
    ax.set_title('Storage Size')

    ax = axes[1, 1]
    ax.bar(['CF', 'Haar'], [cf_mse, haar_mse], color=['steelblue', 'coral'], alpha=0.8)
    ax.set_ylabel('MSE')
    ax.set_title('Reconstruction Error')
    ax.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))

    plt.suptitle('Medical Signal Compression: CF vs Wavelet', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{IMG}/cf_doors_15_medical.png', dpi=150)
    plt.close()

    elapsed = time.time() - t0
    results['exp15'] = {
        'raw_bits': raw_bits_ecg,
        'cf_bits': cf_total_bits,
        'haar_bits': haar_bits,
        'cf_mse': round(float(cf_mse), 8),
        'haar_mse': round(float(haar_mse), 8),
        'cf_ratio': round(raw_bits_ecg / cf_total_bits, 3) if cf_total_bits > 0 else 0,
        'haar_ratio': round(raw_bits_ecg / haar_bits, 3) if haar_bits > 0 else 0,
        'time': elapsed
    }
    print(f"  CF: {cf_total_bits/1000:.1f}kb MSE={cf_mse:.6f}, Haar: {haar_bits/1000:.1f}kb MSE={haar_mse:.6f}")
    return results['exp15']


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 70)
    print("v12 CF Cross-Domain Experiments — 15 experiments")
    print("=" * 70)

    T0 = time.time()

    # Run all experiments
    exp01_wiener_berggren()
    exp02_cf_key_exchange()
    exp03_lattice_berggren()
    exp04_kam_stability()       # HIGH PRIORITY
    exp05_quantum_chaos()
    exp06_penrose_tiling()
    exp07_gauss_kuzmin()        # HIGH PRIORITY
    exp08_cf_universality()     # HIGH PRIORITY
    exp09_minkowski()
    exp10_stern_brocot()
    exp11_parallel_gcd()        # HIGH PRIORITY
    exp12_cf_nn_layer()
    exp13_cf_compression()
    exp14_cf_gps()
    exp15_medical_signal()

    total_time = time.time() - T0
    print(f"\n{'='*70}")
    print(f"Total time: {total_time:.1f}s")
    print(f"{'='*70}")

    # Save results JSON
    with open('/home/raver1975/factor/v12_cf_doors_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\nResults saved to v12_cf_doors_results.json")
    print("Plots saved to images/cf_doors_*.png")
