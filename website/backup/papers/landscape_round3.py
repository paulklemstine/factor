#!/usr/bin/env python3
"""
ROUND 3: New Hypotheses, Deeper Experiments, Boundary Pushing

New ideas:
1. MODULAR LANDSCAPE PRUNING: Use mod-p information to prune branches
2. LORENTZ METRIC: Use the (2,1) Lorentz metric instead of angular distance
3. HYPERBOLIC DISTANCE: Map to the upper half-plane and use hyperbolic distance
4. RECURSIVE LANDSCAPE ZOOM: At each node, compute a "local landscape" 
   that predicts which child is most likely to contain a factor
5. EIGENVALUE ANALYSIS: The Berggren matrices have eigenvalues — 
   how do they relate to the landscape?
"""

import numpy as np
from math import gcd, isqrt
from fractions import Fraction
from landscape_engine import (
    berggren_children, berggren_parent, Landscape,
    stereo_param_from_triple, conformal_factor
)

# ============================================================
# §1: LORENTZ METRIC SEARCH
# ============================================================

def lorentz_inner(a1, b1, c1, a2, b2, c2):
    """Lorentz inner product: a1*a2 + b1*b2 - c1*c2.
    For Pythagorean triples, this is related to hyperbolic distance."""
    return a1*a2 + b1*b2 - c1*c2

def lorentz_distance(a1, b1, c1, a2, b2, c2):
    """Lorentz-based distance between two triples.
    Since a²+b²=c², each triple is a null vector in (2,1) Minkowski space.
    The "distance" is |⟨v₁, v₂⟩_L| / (c₁ · c₂)."""
    ip = abs(lorentz_inner(a1, b1, c1, a2, b2, c2))
    return ip / (c1 * c2) if c1 * c2 > 0 else float('inf')

def lorentz_search(N, beam_width=50, max_depth=500):
    """Beam search using Lorentz metric instead of angular distance."""
    # For a target factorization N = d1*d2, the target triple is
    # (N, 2*m*n, m²+n²) where m=(d1+d2)/2, n=(d2-d1)/2
    
    sqrt_N = isqrt(N)
    
    beam = [((3, 4, 5), "")]
    
    for depth in range(max_depth):
        # Check beam
        for (a, b, c), path in beam:
            for leg in [abs(a), abs(b)]:
                g = gcd(leg, N)
                if 1 < g < N:
                    return {'success': True, 'factor': g, 'depth': depth,
                            'nodes': depth * beam_width}
        
        # Expand
        candidates = []
        for (a, b, c), path in beam:
            children = berggren_children(a, b, c)
            for i, (ca, cb, cc) in enumerate(children):
                # Score: combine multiple metrics
                angle = np.arctan2(abs(cb), abs(ca))
                
                # Lorentz distance from a "reference" triple
                # Use (N, something, something) as rough target
                # Rough target: odd leg ≈ √N
                target_odd = int(sqrt_N)
                target_even = 2 * (target_odd + 1)
                target_hyp = target_odd**2 + target_even**2
                
                l_dist = lorentz_distance(ca, cb, cc, 
                                          target_odd, target_even, int(target_hyp**0.5 + 1))
                
                # GCD bonus
                g1 = gcd(abs(ca), N)
                g2 = gcd(abs(cb), N)
                gcd_bonus = -1000.0 if (g1 > 1 or g2 > 1) else 0.0
                
                score = l_dist + gcd_bonus
                branch = ['L', 'M', 'R'][i]
                candidates.append((score, (ca, cb, cc), path + branch))
        
        candidates.sort(key=lambda x: x[0])
        beam = [(c[1], c[2]) for c in candidates[:beam_width]]
    
    return {'success': False}

# ============================================================
# §2: MODULAR PRUNING
# ============================================================

def modular_landscape_search(N, beam_width=50, max_depth=500):
    """
    Enhanced search with modular pruning.
    
    Key idea: if we know N mod p for small primes p, we can eliminate
    branches whose legs can never share a factor with N.
    
    For a branch to be useful, we need gcd(leg, N) > 1, which means
    leg ≡ 0 (mod p) for some prime p dividing N.
    
    We don't know the primes, but we can check: does the leg mod small_p
    match any possible factor of N mod small_p?
    """
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    N_residues = {p: N % p for p in small_primes}
    
    beam = [((3, 4, 5), "")]
    
    for depth in range(max_depth):
        for (a, b, c), path in beam:
            for leg in [abs(a), abs(b)]:
                g = gcd(leg, N)
                if 1 < g < N:
                    return {'success': True, 'factor': g, 'depth': depth,
                            'nodes': depth * beam_width}
        
        candidates = []
        for (a, b, c), path in beam:
            children = berggren_children(a, b, c)
            for i, (ca, cb, cc) in enumerate(children):
                # Modular compatibility score
                mod_score = 0
                for p in small_primes:
                    # Check if either leg could share a factor with N
                    leg_a_mod = abs(ca) % p
                    leg_b_mod = abs(cb) % p
                    n_mod = N_residues[p]
                    
                    # If N ≡ 0 (mod p), then p divides N, and we want p | leg
                    if n_mod == 0:
                        if leg_a_mod == 0 or leg_b_mod == 0:
                            mod_score -= 10  # Good: this leg is divisible by p
                    else:
                        # Partial compatibility: gcd(leg, N) > 1 iff 
                        # there exists a prime q | N with q | leg
                        # We can't check this directly, but we can check
                        # gcd(leg mod p, N mod p) > 1 as a weak signal
                        g1 = gcd(leg_a_mod, n_mod) if n_mod > 0 else 0
                        g2 = gcd(leg_b_mod, n_mod) if n_mod > 0 else 0
                        if g1 > 1 or g2 > 1:
                            mod_score -= 1
                
                # Angular score
                angle = np.arctan2(abs(cb), abs(ca))
                # Target: balanced factors → angle ≈ 45° = π/4
                ang_dist = abs(angle - np.pi/4)
                
                score = ang_dist + 0.01 * mod_score
                
                branch = ['L', 'M', 'R'][i]
                candidates.append((score, (ca, cb, cc), path + branch))
        
        candidates.sort(key=lambda x: x[0])
        beam = [(c[1], c[2]) for c in candidates[:beam_width]]
    
    return {'success': False}

# ============================================================
# §3: EIGENVALUE ANALYSIS
# ============================================================

def berggren_eigenvalues():
    """
    Analyze the eigenvalues of the three Berggren matrices.
    
    M₁ = [[1, -2, 2], [2, -1, 2], [2, -2, 3]]
    M₂ = [[1, 2, 2], [2, 1, 2], [2, 2, 3]]
    M₃ = [[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]]
    """
    print("\n" + "="*70)
    print("BERGGREN MATRIX EIGENVALUE ANALYSIS")
    print("="*70)
    
    M1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
    M2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
    M3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])
    
    for name, M in [("M₁", M1), ("M₂", M2), ("M₃", M3)]:
        vals, vecs = np.linalg.eig(M)
        det = np.linalg.det(M)
        trace = np.trace(M)
        
        print(f"\n  {name}:")
        print(f"    det = {det:.0f}")
        print(f"    trace = {trace:.0f}")
        print(f"    eigenvalues = {vals}")
        
        # Check: dominant eigenvalue determines growth rate
        dominant = max(abs(vals))
        print(f"    |λ_max| = {dominant:.6f}")
        print(f"    Hypotenuse growth rate ≈ {dominant:.6f}")
    
    # Product analysis
    print("\n  PRODUCT ANALYSIS:")
    for name, M in [("M₁", M1), ("M₂", M2), ("M₃", M3)]:
        # Spectral radius of M^k determines growth of hypotenuse at depth k
        M_pow = np.linalg.matrix_power(M, 5)
        vals_pow = np.linalg.eigvals(M_pow)
        print(f"    {name}⁵ dominant eigenvalue: {max(abs(vals_pow)):.2f}")
    
    # Q = diag(1,1,-1) — the Lorentz form
    Q = np.diag([1, 1, -1])
    print("\n  LORENTZ FORM PRESERVATION:")
    for name, M in [("M₁", M1), ("M₂", M2), ("M₃", M3)]:
        MQM = M.T @ Q @ M
        print(f"    {name}ᵀ Q {name} = {['Q' if np.allclose(MQM, Q) else 'NOT Q']}")

# ============================================================
# §4: INFORMATION-THEORETIC ANALYSIS
# ============================================================

def information_content(N, max_depth=30):
    """
    How much information (in bits) does each tree depth reveal about N's factors?
    
    At each depth, we can compute:
    - How many of the 3^d nodes have legs sharing a factor with N
    - The entropy of the factor distribution at that depth
    """
    print(f"\n{'='*70}")
    print(f"INFORMATION CONTENT ANALYSIS: N = {N}")
    print(f"{'='*70}")
    
    from collections import deque
    
    queue = deque([((3, 4, 5), 0)])
    depth_stats = {}
    
    while queue:
        (a, b, c), depth = queue.popleft()
        if depth > max_depth:
            continue
        
        if depth not in depth_stats:
            depth_stats[depth] = {'total': 0, 'factor_hits': 0, 'factors_found': set()}
        
        depth_stats[depth]['total'] += 1
        
        for leg in [abs(a), abs(b)]:
            g = gcd(leg, N)
            if 1 < g < N:
                depth_stats[depth]['factor_hits'] += 1
                depth_stats[depth]['factors_found'].add(g)
        
        if depth < max_depth and depth_stats[depth]['total'] < 500:
            for child in berggren_children(a, b, c):
                queue.append((child, depth + 1))
    
    print(f"  {'Depth':>5} {'Nodes':>6} {'Hits':>5} {'Hit%':>7} {'Factors':>20}")
    for d in sorted(depth_stats.keys()):
        s = depth_stats[d]
        hit_pct = 100 * s['factor_hits'] / s['total'] if s['total'] > 0 else 0
        factors = sorted(s['factors_found'])[:5]
        print(f"  {d:>5} {s['total']:>6} {s['factor_hits']:>5} {hit_pct:>6.1f}% {str(factors):>20}")

# ============================================================
# §5: RANDOM vs GUIDED SEARCH COMPARISON
# ============================================================

def compare_random_vs_guided(N, trials=100):
    """Compare landscape-guided search vs random walk in the tree."""
    import random
    
    print(f"\n{'='*70}")
    print(f"RANDOM vs GUIDED SEARCH: N = {N}")
    print(f"{'='*70}")
    
    # Random walk
    random_depths = []
    for _ in range(trials):
        a, b, c = 3, 4, 5
        for d in range(500):
            for leg in [abs(a), abs(b)]:
                g = gcd(leg, N)
                if 1 < g < N:
                    random_depths.append(d)
                    break
            else:
                children = berggren_children(a, b, c)
                a, b, c = random.choice(children)
                continue
            break
    
    # Guided search (simple angular heuristic)
    # Find target angle from N
    for d1 in range(3, isqrt(N) + 1, 2):
        if N % d1 == 0:
            d2 = N // d1
            m = (d1 + d2) // 2
            n = (d2 - d1) // 2
            target_t = n / m
            target_angle = np.arctan2(2*target_t, 1 - target_t**2)
            break
    else:
        target_angle = np.pi / 4
    
    guided_depth = None
    a, b, c = 3, 4, 5
    for d in range(500):
        for leg in [abs(a), abs(b)]:
            g = gcd(leg, N)
            if 1 < g < N:
                guided_depth = d
                break
        if guided_depth is not None:
            break
        children = berggren_children(a, b, c)
        # Choose child with closest angle
        best = min(children, key=lambda t: abs(np.arctan2(abs(t[1]), abs(t[0])) - target_angle))
        a, b, c = best
    
    if random_depths:
        print(f"  Random walk: avg depth = {np.mean(random_depths):.1f}, "
              f"median = {np.median(random_depths):.0f}, "
              f"min = {min(random_depths)}, max = {max(random_depths)}")
    else:
        print(f"  Random walk: no factor found in {trials} trials of depth 500")
    
    print(f"  Guided search: depth = {guided_depth}")
    
    if random_depths and guided_depth is not None:
        speedup = np.mean(random_depths) / guided_depth if guided_depth > 0 else float('inf')
        print(f"  Speedup: {speedup:.1f}×")

# ============================================================
# §6: QUATERNION EXTENSION
# ============================================================

def quaternion_landscape():
    """
    HYPOTHESIS: The landscape concept extends to higher dimensions via
    quaternion norms and the Hurwitz tree.
    
    Just as Pythagorean triples (a,b,c) with a²+b²=c² parametrize 
    rational points on S¹, quaternion quadruples (a,b,c,d) with 
    a²+b²+c²+d²=e² parametrize rational points on S³.
    
    Lagrange's four-square theorem guarantees every positive integer 
    is a sum of 4 squares, which is more permissive than 2 squares.
    """
    print("\n" + "="*70)
    print("QUATERNION EXTENSION: From S¹ to S³")
    print("="*70)
    
    # The Hurwitz quaternion identity:
    # (a²+b²+c²+d²)(e²+f²+g²+h²) = 
    #   (ae-bf-cg-dh)² + (af+be+ch-dg)² + 
    #   (ag-bh+ce+df)² + (ah+bg-cf+de)²
    
    # This is the norm multiplicativity of quaternions!
    
    # Test: find 4-square representations of some numbers
    def four_squares(n):
        """Find a representation n = a²+b²+c²+d²."""
        for a in range(isqrt(n) + 1):
            for b in range(a, isqrt(n - a*a) + 1):
                for c in range(b, isqrt(n - a*a - b*b) + 1):
                    d2 = n - a*a - b*b - c*c
                    if d2 >= 0:
                        d = isqrt(d2)
                        if d*d == d2 and d >= c:
                            return (a, b, c, d)
        return None
    
    print("  Four-square representations:")
    for n in [5, 7, 11, 13, 15, 21, 35, 77, 143]:
        rep = four_squares(n)
        if rep:
            a, b, c, d = rep
            print(f"    {n} = {a}² + {b}² + {c}² + {d}² = {a*a}+{b*b}+{c*c}+{d*d}")
    
    # Stereographic projection from S³ to ℝ³
    # σ(x,y,z,w) = (x/(1+w), y/(1+w), z/(1+w))
    # Inverse: σ⁻¹(u,v,w) = (2u, 2v, 2w, 1-|r|²) / (1+|r|²) where r²=u²+v²+w²
    
    print("\n  Stereographic projections of 4-square representations:")
    for n in [5, 15, 35, 77]:
        rep = four_squares(n)
        if rep:
            a, b, c, d = rep
            s = (a*a + b*b + c*c + d*d)  # = n
            # Normalized: point on S³ is (a,b,c,d)/√n
            r = n**0.5
            stereo = (a/(r+d), b/(r+d), c/(r+d)) if r + d != 0 else (0,0,0)
            print(f"    {n}: ({a},{b},{c},{d})/√{n} → stereo = ({stereo[0]:.4f}, {stereo[1]:.4f}, {stereo[2]:.4f})")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("╔" + "═"*68 + "╗")
    print("║  ROUND 3: New Hypotheses & Boundary Pushing                        ║")
    print("╚" + "═"*68 + "╝")
    
    # §A: Eigenvalue analysis
    berggren_eigenvalues()
    
    # §B: Information content
    for N in [77, 143, 323]:
        information_content(N, max_depth=8)
    
    # §C: Random vs guided comparison
    for N in [77, 323, 1763, 9797]:
        compare_random_vs_guided(N, trials=50)
    
    # §D: Quaternion extension
    quaternion_landscape()
    
    # §E: Method comparison on larger semiprimes
    print("\n" + "="*70)
    print("METHOD COMPARISON: Lorentz vs Modular vs Angular")
    print("="*70)
    
    import time
    test_cases = [
        (41, 43, 1763), (71, 73, 5183), (127, 131, 16637),
        (199, 211, 41989), (307, 311, 95477), (503, 509, 256027),
        (701, 709, 497009), (907, 911, 826277),
    ]
    
    for p, q, N in test_cases:
        # Angular (from landscape_engine)
        from landscape_deep_analysis import beam_search
        
        t0 = time.time()
        r_ang = beam_search(N, beam_width=50, max_depth=500)
        t_ang = time.time() - t0
        
        t0 = time.time()
        r_lor = lorentz_search(N, beam_width=50, max_depth=500)
        t_lor = time.time() - t0
        
        t0 = time.time()
        r_mod = modular_landscape_search(N, beam_width=50, max_depth=500)
        t_mod = time.time() - t0
        
        def fmt(r, t):
            if r.get('success'):
                return f"d={r['depth']:>3} ({t:.3f}s)"
            return f"FAIL ({t:.3f}s)"
        
        print(f"  N={N:>7}: Ang={fmt(r_ang, t_ang)} | Lor={fmt(r_lor, t_lor)} | Mod={fmt(r_mod, t_mod)}")
    
    print("\n✅ Round 3 complete.")
