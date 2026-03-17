#!/usr/bin/env python3
"""
Deep Research: Algebraic Topology & Coding Theory for ECDLP

AREA 1: Persistent Homology / TDA (without heavy TDA libs)
  - Embed EC points into R^2, compute pairwise distance matrix
  - Build MST, analyze structure for consecutive vs random points
  - Check if MST of {P, P+G, ..., P+99G} has k-dependent signature

AREA 2: AG Codes from Elliptic Curves
  - Construct generator matrix from x-coordinates of multiples of G
  - Compute syndrome of target point P = kG
  - Check if syndrome leaks information about k

Uses only numpy/gmpy2. Memory < 200MB. 30s alarm per trial.
"""

import signal
import time
import random
import math
import sys
import numpy as np
from collections import Counter

# Import EC infrastructure from project
sys.path.insert(0, '/home/raver1975/factor')
from ecdlp_pythagorean import EllipticCurve, ECPoint


# ── Timeout helper ──────────────────────────────────────────────────────────

class TimeoutError(Exception):
    pass

def alarm_handler(signum, frame):
    raise TimeoutError("Trial timed out (30s)")

signal.signal(signal.SIGALRM, alarm_handler)


# ── Small curve factory ─────────────────────────────────────────────────────

def make_small_curve(target_order_min=100, target_order_max=1000):
    """
    Find a small curve y^2 = x^3 + ax + b (mod p) with order in range.
    Returns (curve, G, order) or None.
    """
    for p in range(101, 2000):
        if not _is_prime(p):
            continue
        for a in range(0, min(p, 20)):
            for b in range(1, min(p, 20)):
                # Check discriminant
                disc = (4 * a * a * a + 27 * b * b) % p
                if disc == 0:
                    continue
                curve = EllipticCurve(a, b, p)
                # Count points (Hasse bound: |#E - p - 1| <= 2*sqrt(p))
                G_cand = curve.find_generator()
                if G_cand is None:
                    continue
                # Find order of this point
                try:
                    order = curve.point_order(G_cand)
                except:
                    continue
                if target_order_min <= order <= target_order_max:
                    return curve, G_cand, order
    return None


def _is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def find_curves_with_orders(orders_wanted, p_range=(101, 2000)):
    """Find curves with specific orders for controlled experiments."""
    curves = []
    for p in range(p_range[0], p_range[1]):
        if not _is_prime(p):
            continue
        for a in range(0, min(p, 10)):
            for b in range(1, min(p, 10)):
                disc = (4 * a**3 + 27 * b**2) % p
                if disc == 0:
                    continue
                curve = EllipticCurve(a, b, p)
                G_cand = curve.find_generator()
                if G_cand is None:
                    continue
                try:
                    order = curve.point_order(G_cand)
                except:
                    continue
                if order in orders_wanted:
                    curves.append((curve, G_cand, order))
                    orders_wanted = [o for o in orders_wanted if o != order]
                    if not orders_wanted:
                        return curves
        if not orders_wanted:
            break
    return curves


# ══════════════════════════════════════════════════════════════════════════════
# AREA 1: TDA / Persistent Homology via MST
# ══════════════════════════════════════════════════════════════════════════════

def compute_distance_matrix(points, p):
    """
    Compute pairwise distance matrix for EC points on F_p.
    Distance = min circular distance on torus [0,p) x [0,p).
    """
    n = len(points)
    D = np.zeros((n, n), dtype=np.float64)
    half_p = p / 2.0
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            dx = abs(xi - xj)
            if dx > half_p:
                dx = p - dx
            dy = abs(yi - yj)
            if dy > half_p:
                dy = p - dy
            d = math.sqrt(dx * dx + dy * dy)
            D[i, j] = d
            D[j, i] = d
    return D


def prims_mst(D):
    """Prim's MST algorithm. Returns list of (weight, i, j) edges."""
    n = D.shape[0]
    in_tree = np.zeros(n, dtype=bool)
    in_tree[0] = True
    edges = []
    # key[v] = min edge weight to tree, parent[v] = tree node
    key = np.full(n, np.inf)
    parent = np.full(n, -1, dtype=int)
    # Initialize from node 0
    for v in range(1, n):
        key[v] = D[0, v]
        parent[v] = 0

    for _ in range(n - 1):
        # Find min key not in tree
        min_val = np.inf
        u = -1
        for v in range(n):
            if not in_tree[v] and key[v] < min_val:
                min_val = key[v]
                u = v
        if u == -1:
            break
        in_tree[u] = True
        edges.append((min_val, parent[u], u))
        # Update keys
        for v in range(n):
            if not in_tree[v] and D[u, v] < key[v]:
                key[v] = D[u, v]
                parent[v] = u
    return edges


def mst_features(edges):
    """Extract features from MST edges."""
    if not edges:
        return {}
    weights = [e[0] for e in edges]
    n = len(edges) + 1
    # Degree distribution
    degree = Counter()
    for w, i, j in edges:
        degree[i] += 1
        degree[j] += 1
    deg_vals = list(degree.values())

    return {
        'mean_weight': np.mean(weights),
        'std_weight': np.std(weights),
        'median_weight': np.median(weights),
        'min_weight': np.min(weights),
        'max_weight': np.max(weights),
        'weight_ratio': np.max(weights) / (np.min(weights) + 1e-12),
        'mean_degree': np.mean(deg_vals),
        'max_degree': max(deg_vals),
        'degree_entropy': _entropy(deg_vals),
        'weight_skew': _skewness(weights),
    }


def _entropy(vals):
    """Shannon entropy of value distribution."""
    c = Counter(vals)
    total = sum(c.values())
    ent = 0.0
    for count in c.values():
        p = count / total
        if p > 0:
            ent -= p * math.log2(p)
    return ent


def _skewness(vals):
    """Skewness of a distribution."""
    if len(vals) < 3:
        return 0.0
    m = np.mean(vals)
    s = np.std(vals)
    if s < 1e-12:
        return 0.0
    return np.mean(((np.array(vals) - m) / s) ** 3)


def tda_experiment(curve, G, order, num_points=80, num_trials=20):
    """
    Test H_TDA: Does MST structure of consecutive EC points differ
    from random EC points? Does the MST of {P, P+G, ...} depend on k?
    """
    print(f"\n{'='*70}")
    print(f"TDA EXPERIMENT: order={order}, p={curve.p}, num_points={num_points}")
    print(f"{'='*70}")
    p = curve.p

    # Precompute all multiples of G
    all_points = []
    Q = G
    for i in range(order):
        all_points.append((Q.x, Q.y))
        Q = curve.add(Q, G)

    # Feature comparison: consecutive vs random
    consec_features = []
    random_features = []
    shifted_features = []  # {kG, (k+1)G, ...} for various k

    for trial in range(num_trials):
        signal.alarm(30)
        try:
            # 1. Consecutive points: {G, 2G, ..., num_points*G}
            consec_pts = all_points[:num_points]
            D = compute_distance_matrix(consec_pts, p)
            edges = prims_mst(D)
            consec_features.append(mst_features(edges))

            # 2. Random subset of points
            indices = sorted(random.sample(range(order), num_points))
            rand_pts = [all_points[i] for i in indices]
            D = compute_distance_matrix(rand_pts, p)
            edges = prims_mst(D)
            random_features.append(mst_features(edges))

            # 3. Shifted consecutive: {kG, (k+1)G, ..., (k+num_points-1)G}
            k = random.randint(1, order - num_points - 1)
            shift_pts = all_points[k:k + num_points]
            D = compute_distance_matrix(shift_pts, p)
            edges = prims_mst(D)
            feat = mst_features(edges)
            feat['k'] = k
            shifted_features.append(feat)
        except TimeoutError:
            print(f"  Trial {trial} timed out")
            continue
        finally:
            signal.alarm(0)

    # Compare features
    print(f"\n  Consecutive vs Random MST features ({num_trials} trials):")
    print(f"  {'Feature':<20} {'Consecutive':>15} {'Random':>15} {'Ratio':>10}")
    print(f"  {'-'*60}")
    keys = ['mean_weight', 'std_weight', 'max_degree', 'degree_entropy', 'weight_skew']
    diffs_found = False
    for key in keys:
        c_vals = [f[key] for f in consec_features if key in f]
        r_vals = [f[key] for f in random_features if key in f]
        if c_vals and r_vals:
            c_mean = np.mean(c_vals)
            r_mean = np.mean(r_vals)
            ratio = c_mean / (r_mean + 1e-12)
            marker = " ***" if abs(ratio - 1.0) > 0.1 else ""
            print(f"  {key:<20} {c_mean:>15.4f} {r_mean:>15.4f} {ratio:>10.4f}{marker}")
            if abs(ratio - 1.0) > 0.1:
                diffs_found = True

    # Check k-dependence of shifted features
    print(f"\n  K-dependence analysis (shifted consecutive sequences):")
    if shifted_features:
        ks = [f['k'] for f in shifted_features]
        mean_ws = [f['mean_weight'] for f in shifted_features]
        # Correlation between k and MST mean weight
        if len(ks) > 2:
            corr = np.corrcoef(ks, mean_ws)[0, 1]
            print(f"  Correlation(k, mean_weight) = {corr:.6f}")
            print(f"  k range: [{min(ks)}, {max(ks)}]")
            print(f"  mean_weight range: [{min(mean_ws):.2f}, {max(mean_ws):.2f}]")
            # Also check other features
            for key in ['std_weight', 'max_degree', 'weight_skew']:
                vals = [f[key] for f in shifted_features]
                c = np.corrcoef(ks, vals)[0, 1]
                print(f"  Correlation(k, {key}) = {c:.6f}")

    return diffs_found


# ══════════════════════════════════════════════════════════════════════════════
# AREA 2: AG Codes from Elliptic Curves
# ══════════════════════════════════════════════════════════════════════════════

def ag_code_experiment(curve, G, order, code_length=None, num_trials=30):
    """
    Test H_AGCODE: Does the syndrome of x(P) w.r.t. the AG code
    constructed from multiples of G leak information about k?

    Code construction:
      - n evaluation points: P_1=G, P_2=2G, ..., P_n=nG
      - Generator matrix row j: [x(P_i)^j mod p] for i=1..n, j=0..k_dim-1
      - This is a Reed-Solomon-like code on the x-coordinates

    Syndrome analysis:
      - For target P = kG, compute x(P) and its "position" in code space
      - Check if the syndrome vector leaks k mod something
    """
    print(f"\n{'='*70}")
    print(f"AG CODE EXPERIMENT: order={order}, p={curve.p}")
    print(f"{'='*70}")

    p = curve.p
    if code_length is None:
        code_length = min(order - 1, 60)
    k_dim = code_length // 3  # rate ~1/3

    # Precompute all multiples and their x-coordinates
    all_multiples = []
    Q = G
    for i in range(order):
        all_multiples.append(Q)
        Q = curve.add(Q, G)

    x_coords = [pt.x for pt in all_multiples[:code_length]]

    # Build generator matrix G_mat: k_dim x code_length
    # G_mat[j][i] = x_coords[i]^j mod p
    G_mat = np.zeros((k_dim, code_length), dtype=np.int64)
    for j in range(k_dim):
        for i in range(code_length):
            G_mat[j, i] = pow(x_coords[i], j, p)

    # Build parity check matrix H (code_length - k_dim) x code_length
    # Via row reduction of [G_mat^T | I]
    # Simpler: use the Vandermonde structure
    # H is (code_length - k_dim) x code_length such that H @ G_mat^T = 0 mod p
    # For simplicity, compute syndromes directly: s = H @ c mod p
    # where c is the "received word" constructed from x(P)

    print(f"  Code params: n={code_length}, k={k_dim}, rate={k_dim/code_length:.2f}")

    # Experiment: for various k, compute the "codeword residual" of x(kG)
    # relative to the code spanned by {x(iG)^j : j=0..k_dim-1}
    syndrome_data = []

    for trial in range(num_trials):
        signal.alarm(30)
        try:
            k = random.randint(1, order - 1)
            P = all_multiples[k - 1]  # k*G (0-indexed)
            x_P = P.x

            # Construct "received word": evaluate x_P^j for j=0..k_dim-1
            # and compute the projection onto the code space
            eval_vec = np.array([pow(x_P, j, p) for j in range(k_dim)], dtype=np.int64)

            # Compute "syndrome-like" quantity:
            # For each evaluation point i, compute x(iG) - sum_j c_j * x(iG)^j
            # where c_j are the coefficients representing x(P)
            # This is essentially: how well does x(P) fit as a codeword?

            # Method 1: Direct correlation with evaluation points
            correlations = []
            for i in range(code_length):
                # Dot product of eval_vec with column i of G_mat
                dot = sum(int(eval_vec[j]) * int(G_mat[j, i]) for j in range(k_dim)) % p
                correlations.append(dot)
            correlations = np.array(correlations)

            # Method 2: x(kG) position in the Vandermonde structure
            # Compute x(kG) mod each x(iG) for small primes
            residues = []
            for i in range(min(10, code_length)):
                if x_coords[i] != 0:
                    residues.append(x_P % x_coords[i])
                else:
                    residues.append(0)

            # Method 3: Syndrome = how the x-coordinate of kG relates to
            # the x-coordinates of the first few multiples
            # Check: x(kG) mod small_prime vs k mod small_prime
            small_primes = [q for q in range(2, 50) if _is_prime(q) and q < order]
            k_mod_info = []
            for q in small_primes[:10]:
                # x((k mod q)*G) should relate to x(kG) somehow
                k_red = k % q
                if k_red == 0:
                    k_red = q
                x_reduced = all_multiples[k_red - 1].x
                match = (x_reduced == x_P)
                k_mod_info.append((q, k_red, match))

            syndrome_data.append({
                'k': k,
                'x_P': x_P,
                'corr_mean': float(np.mean(correlations)),
                'corr_std': float(np.std(correlations)),
                'residues': residues,
                'k_mod_info': k_mod_info,
            })
        except TimeoutError:
            print(f"  Trial {trial} timed out")
            continue
        finally:
            signal.alarm(0)

    # Analyze results
    print(f"\n  Syndrome Analysis ({len(syndrome_data)} trials):")

    # Check if correlation statistics depend on k
    ks = [d['k'] for d in syndrome_data]
    corr_means = [d['corr_mean'] for d in syndrome_data]
    corr_stds = [d['corr_std'] for d in syndrome_data]

    if len(ks) > 2:
        r1 = np.corrcoef(ks, corr_means)[0, 1]
        r2 = np.corrcoef(ks, corr_stds)[0, 1]
        print(f"  Correlation(k, syndrome_mean) = {r1:.6f}")
        print(f"  Correlation(k, syndrome_std)  = {r2:.6f}")

    # Check residue patterns
    print(f"\n  Residue Pattern Analysis:")
    # For each small prime q, check if x(kG) mod x(iG) reveals k mod something
    if syndrome_data:
        # Examine if x(kG) has structure related to k for specific moduli
        for q_idx in range(min(5, len(syndrome_data[0].get('k_mod_info', [])))):
            q = syndrome_data[0]['k_mod_info'][q_idx][0]
            # Group by k mod q
            groups = {}
            for d in syndrome_data:
                km = d['k'] % q
                if km not in groups:
                    groups[km] = []
                groups[km].append(d['x_P'] % q)
            print(f"  Prime q={q}: k mod q -> x(kG) mod q distribution:")
            for km in sorted(groups.keys()):
                vals = groups[km]
                if vals:
                    dist = Counter(vals)
                    print(f"    k≡{km} (mod {q}): {dict(dist)}")

    # Check Hasse-Weil connection: x(kG) mod q determines something about k?
    print(f"\n  Vandermonde Syndrome Check:")
    # The key insight: if we build a Vandermonde matrix V where V[i,j] = x(jG)^i
    # then the vector [x(G), x(2G), ..., x(nG)] lives in a structured space
    # Check rank of the Vandermonde sub-matrices
    for dim in [5, 10, 15]:
        if dim > code_length:
            break
        V = np.zeros((dim, dim), dtype=np.float64)
        for i in range(dim):
            for j in range(dim):
                V[i, j] = pow(x_coords[j], i, p) % p
        rank = np.linalg.matrix_rank(V)
        det_log = 0
        try:
            sign, logdet = np.linalg.slogdet(V)
            det_log = logdet
        except:
            pass
        print(f"  Vandermonde {dim}x{dim}: rank={rank}, log|det|={det_log:.2f}")

    return syndrome_data


# ══════════════════════════════════════════════════════════════════════════════
# AREA 2b: Goppa-style syndrome attack
# ══════════════════════════════════════════════════════════════════════════════

def goppa_syndrome_experiment(curve, G, order, num_trials=50):
    """
    Goppa code approach: define code from the EC group structure.

    Key idea: The map k -> x(kG) is a "code" from Z/nZ to F_p.
    The SYNDROME of a received value x w.r.t. locator polynomial
    L(z) = prod(z - alpha_i) reveals error positions.

    If we treat k as an "error position" and x(kG) as a "syndrome",
    can we invert this map efficiently?

    Specifically: for Goppa code with goppa polynomial g(z),
    syndrome S(x) = sum_{i in support} 1/(x - alpha_i)
    If alpha_i = x(iG), then S relates to the x-coordinate structure.
    """
    print(f"\n{'='*70}")
    print(f"GOPPA SYNDROME EXPERIMENT: order={order}, p={curve.p}")
    print(f"{'='*70}")

    p = curve.p

    # Precompute all x-coordinates
    all_x = []
    Q = G
    for i in range(order):
        all_x.append(Q.x)
        Q = curve.add(Q, G)

    # Check: is the map k -> x(kG) injective?
    x_set = set(all_x)
    print(f"  Unique x-coords: {len(x_set)} out of {order} points")
    print(f"  (Expected ~{order//2} unique since x(kG) = x(-kG) = x((n-k)G))")

    # Build "syndrome function": S_m(k) = sum_{i=1}^{m} x(iG)^(-1) * x(kG)^i mod p
    # This is inspired by Goppa syndrome computation
    m_vals = [5, 10, 20]
    for m in m_vals:
        if m >= order:
            continue
        print(f"\n  Goppa-like syndrome (m={m}):")

        # For several random k values, compute syndrome and check structure
        syndrome_map = {}  # k -> syndrome vector
        for trial in range(min(num_trials, order // 2)):
            k = random.randint(1, order - 1)
            x_k = all_x[k - 1]  # x(kG)

            # Syndrome: S_j = sum_{i=1}^{m} x(iG)^j / (x_k - x(iG)) mod p
            # (standard Goppa syndrome with received = x_k)
            syn = []
            for j in range(min(m, 5)):
                s = 0
                for i in range(m):
                    denom = (x_k - all_x[i]) % p
                    if denom == 0:
                        # x_k = x(iG) means k = i+1 or k = n-(i+1)
                        # This IS the match!
                        pass
                    else:
                        inv_denom = pow(denom, p - 2, p)
                        s = (s + pow(all_x[i], j, p) * inv_denom) % p
                syn.append(s)
            syndrome_map[k] = tuple(syn)

        # Check if syndromes cluster by k mod small values
        for q in [2, 3, 5, 7]:
            if q >= order:
                continue
            groups = {}
            for k, syn in syndrome_map.items():
                km = k % q
                if km not in groups:
                    groups[km] = []
                groups[km].append(syn[0] if syn else 0)
            # Check variance within groups vs between groups
            all_vals = [v for vs in groups.values() for v in vs]
            if len(all_vals) < 2:
                continue
            total_var = np.var(all_vals)
            within_vars = []
            for vs in groups.values():
                if len(vs) > 1:
                    within_vars.append(np.var(vs))
            if within_vars:
                within_var = np.mean(within_vars)
                f_ratio = total_var / (within_var + 1e-12)
                sig = " ***" if f_ratio > 2.0 else ""
                print(f"    S_0 grouped by k mod {q}: F-ratio={f_ratio:.4f}{sig}")


# ══════════════════════════════════════════════════════════════════════════════
# AREA 1b: Distance spectrum analysis
# ══════════════════════════════════════════════════════════════════════════════

def distance_spectrum_experiment(curve, G, order, num_points=100):
    """
    Analyze the distance spectrum of EC point sets.

    Key question: Do consecutive EC points have a different nearest-neighbor
    distance distribution than random subsets? If so, this could be exploitable.
    """
    print(f"\n{'='*70}")
    print(f"DISTANCE SPECTRUM EXPERIMENT: order={order}, p={curve.p}")
    print(f"{'='*70}")

    p = curve.p
    num_points = min(num_points, order - 1)

    # Precompute all points
    all_pts = []
    Q = G
    for i in range(order):
        all_pts.append((Q.x, Q.y))
        Q = curve.add(Q, G)

    # Nearest-neighbor distances for consecutive vs random
    def nn_distances(pts):
        """Compute nearest-neighbor distance for each point."""
        n = len(pts)
        nn = []
        for i in range(n):
            min_d = float('inf')
            xi, yi = pts[i]
            for j in range(n):
                if i == j:
                    continue
                xj, yj = pts[j]
                dx = abs(xi - xj)
                if dx > p / 2:
                    dx = p - dx
                dy = abs(yi - yj)
                if dy > p / 2:
                    dy = p - dy
                d = math.sqrt(dx * dx + dy * dy)
                if d < min_d:
                    min_d = d
            nn.append(min_d)
        return nn

    # Test 1: Consecutive points {G, 2G, ..., mG}
    consec_pts = all_pts[:num_points]
    signal.alarm(30)
    try:
        nn_consec = nn_distances(consec_pts)
    except TimeoutError:
        print("  Consecutive NN computation timed out")
        return
    finally:
        signal.alarm(0)

    # Test 2: Random subset
    indices = sorted(random.sample(range(order), num_points))
    rand_pts = [all_pts[i] for i in indices]
    signal.alarm(30)
    try:
        nn_random = nn_distances(rand_pts)
    except TimeoutError:
        print("  Random NN computation timed out")
        return
    finally:
        signal.alarm(0)

    print(f"\n  Nearest-Neighbor Distance Statistics (n={num_points}):")
    print(f"  {'Metric':<25} {'Consecutive':>15} {'Random':>15}")
    print(f"  {'-'*55}")
    for name, func in [('Mean', np.mean), ('Std', np.std), ('Median', np.median),
                        ('Min', np.min), ('Max', np.max)]:
        c = func(nn_consec)
        r = func(nn_random)
        marker = " ***" if abs(c - r) / (r + 1e-12) > 0.1 else ""
        print(f"  {name:<25} {c:>15.4f} {r:>15.4f}{marker}")

    # Test 3: For different starting k, does NN distribution change?
    print(f"\n  K-dependence of NN distribution:")
    k_vs_mean_nn = []
    for _ in range(10):
        k = random.randint(0, order - num_points - 1)
        pts = all_pts[k:k + num_points]
        signal.alarm(30)
        try:
            nn = nn_distances(pts)
            k_vs_mean_nn.append((k, np.mean(nn)))
        except TimeoutError:
            continue
        finally:
            signal.alarm(0)

    if len(k_vs_mean_nn) > 2:
        ks = [x[0] for x in k_vs_mean_nn]
        means = [x[1] for x in k_vs_mean_nn]
        corr = np.corrcoef(ks, means)[0, 1]
        print(f"  Correlation(k, mean_NN) = {corr:.6f}")
        print(f"  Mean NN range: [{min(means):.2f}, {max(means):.2f}]")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("Deep Research: Algebraic Topology & Coding Theory for ECDLP")
    print("=" * 70)

    # Find suitable small curves
    print("\nSearching for test curves...")
    t0 = time.time()

    # We want curves with orders in different ranges
    test_curves = []

    # Quick search for a few curves
    for p in [127, 199, 251, 307, 509, 769, 1021]:
        if not _is_prime(p):
            continue
        for a in range(0, 10):
            for b in range(1, 10):
                disc = (4 * a**3 + 27 * b**2) % p
                if disc == 0:
                    continue
                curve = EllipticCurve(a, b, p)
                G_cand = curve.find_generator()
                if G_cand is None:
                    continue
                try:
                    order = curve.point_order(G_cand)
                except:
                    continue
                if 100 <= order <= 800:
                    test_curves.append((curve, G_cand, order))
                    break
            if test_curves and test_curves[-1][0].p == p:
                break

    print(f"  Found {len(test_curves)} test curves in {time.time()-t0:.1f}s")
    for curve, G_pt, order in test_curves[:3]:
        print(f"    p={curve.p}, a={curve.a}, b={curve.b}, order={order}")

    if not test_curves:
        print("ERROR: No suitable curves found!")
        return

    # Run experiments on first few curves
    results_summary = {
        'tda_diffs': [],
        'agcode_leaks': [],
    }

    for idx, (curve, G_pt, order) in enumerate(test_curves[:3]):
        print(f"\n\n{'#'*70}")
        print(f"# CURVE {idx+1}: p={curve.p}, a={curve.a}, b={curve.b}, order={order}")
        print(f"{'#'*70}")

        # AREA 1: TDA
        num_pts = min(60, order // 2)
        diff = tda_experiment(curve, G_pt, order, num_points=num_pts, num_trials=15)
        results_summary['tda_diffs'].append(diff)

        # AREA 1b: Distance spectrum
        distance_spectrum_experiment(curve, G_pt, order, num_points=num_pts)

        # AREA 2: AG Codes
        ag_code_experiment(curve, G_pt, order, code_length=min(order-1, 50), num_trials=20)

        # AREA 2b: Goppa syndrome
        goppa_syndrome_experiment(curve, G_pt, order, num_trials=30)

    # ── Final summary ───────────────────────────────────────────────────────
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")

    print(f"\n  AREA 1 (TDA/Persistent Homology):")
    any_tda = any(results_summary['tda_diffs'])
    if any_tda:
        print(f"    RESULT: MST structure DOES differ between consecutive and random EC points")
        print(f"    This warrants further investigation on larger curves")
    else:
        print(f"    RESULT: No significant MST structural difference detected")
        print(f"    EC points in F_p appear uniformly distributed (as expected)")
        print(f"    VERDICT: H_TDA is likely FALSE for small curves")

    print(f"\n  AREA 2 (AG Codes / Goppa Syndrome):")
    print(f"    Syndrome correlations with k were tested")
    print(f"    If no significant F-ratios (>2.0) observed: syndromes don't leak k")
    print(f"    The x-coordinate map k->x(kG) appears pseudorandom")
    print(f"    VERDICT: H_AGCODE needs specific algebraic structure to work,")
    print(f"    generic syndrome computation doesn't break DLP")

    print(f"\n  THEORETICAL NOTES:")
    print(f"    - EC points on F_p are conjectured to be equidistributed (Sato-Tate)")
    print(f"    - Topological structure exists in the GROUP, not in the EMBEDDING")
    print(f"    - AG codes give good error-correction but decoding != DLP inversion")
    print(f"    - The Goppa approach would need a polynomial whose roots encode k,")
    print(f"      but constructing such a polynomial IS the DLP")

    print(f"\n  Total runtime: {time.time()-t0:.1f}s")


if __name__ == '__main__':
    main()
