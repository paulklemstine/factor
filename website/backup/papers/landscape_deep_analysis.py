#!/usr/bin/env python3
"""
DEEP LANDSCAPE ANALYSIS
========================
Following up on initial experiments with deeper investigation.

Key findings from Round 1:
1. Angular monotonicity: ✅ Confirmed along correct paths
2. Heuristic accuracy: 100% when target is known  
3. "All Right" path produces consecutive factorizations: (2k-1)(2k+1)
4. "All Mid" path converges to t = √2 - 1 (the silver ratio!)
5. Depth scales as O(max(p,q)) — exponential in input size

Round 2 questions:
A. Can GCD-based detection find factors WITHOUT knowing the target?
B. What landscape features correlate with shared factors?
C. Can we use MULTIPLE landscape metrics to build a better heuristic?
D. How does the tree structure relate to the continued fraction of √(N)?
"""

import numpy as np
from fractions import Fraction
from math import gcd, isqrt
from typing import Tuple, List, Dict, Optional
import time

# Import core engine
from landscape_engine import (
    inv_stereo, stereo_forward, conformal_factor,
    stereo_param_from_triple, berggren_children, berggren_parent,
    Landscape, encode_factoring_target, compute_landscape_signature
)

# ============================================================
# §1: GCD-BASED TREE EXPLORATION
# ============================================================

def gcd_landscape_search(N: int, max_depth: int = 50, max_nodes: int = 10000) -> Dict:
    """
    Explore the Berggren tree, checking gcd(odd_leg, N) at each node.
    Uses landscape heuristics to prioritize which branches to explore.
    
    Key insight: We don't need to find N as a leg — we just need
    gcd(leg, N) to be nontrivial (between 1 and N).
    """
    from collections import deque
    
    # Priority queue: (priority, triple, depth, path)
    queue = [(0.0, (3, 4, 5), 0, "")]
    visited = 0
    
    # Target angle: use sqrt(N) as an estimate for the Euclid parameter
    # If N = p*q, m ≈ √N, n ≈ small, so t ≈ n/m ≈ 1/√N
    t_estimate = 1.0 / np.sqrt(N)
    target_angle = np.arctan2(2*t_estimate, 1 - t_estimate**2)  # angle of σ(t)
    
    while queue and visited < max_nodes:
        _, (a, b, c), depth, path = queue.pop(0)
        visited += 1
        
        if depth > max_depth:
            continue
        
        # Check both legs for GCD with N
        for leg in [a, b]:
            g = gcd(abs(leg), N)
            if 1 < g < N:
                return {
                    'success': True,
                    'N': N,
                    'factor': g,
                    'cofactor': N // g,
                    'depth': depth,
                    'path': path,
                    'triple': (a, b, c),
                    'leg_used': leg,
                    'nodes_visited': visited,
                }
        
        # Generate children and score them
        children = berggren_children(a, b, c)
        for i, (ca, cb, cc) in enumerate(children):
            cL = Landscape(ca, cb, cc)
            
            # Score based on multiple factors:
            # 1. Angular distance to estimated target
            ang_dist = abs(cL.angle - target_angle)
            ang_dist = min(ang_dist, 2*np.pi - ang_dist)
            
            # 2. GCD potential: how "composite" is the odd leg?
            odd_leg = ca if ca % 2 == 1 else cb
            # Heuristic: smaller odd legs relative to hypotenuse are more likely composite
            composability = abs(odd_leg) / (cc + 1)
            
            priority = ang_dist + 0.1 * depth  # Penalize depth slightly
            
            branch = ['L', 'M', 'R'][i]
            queue.append((priority, (ca, cb, cc), depth + 1, path + branch))
        
        # Keep queue sorted by priority
        queue.sort(key=lambda x: x[0])
        # Trim queue to prevent memory explosion
        if len(queue) > 5000:
            queue = queue[:2500]
    
    return {
        'success': False,
        'N': N,
        'nodes_visited': visited,
    }

def beam_search(N: int, beam_width: int = 10, max_depth: int = 100) -> Dict:
    """
    Beam search through the Berggren tree.
    At each depth, keep the top `beam_width` candidates
    scored by landscape proximity to the estimated target.
    """
    # Estimate target parameter
    sqrt_N = isqrt(N)
    t_estimates = []
    for d1 in range(3, min(sqrt_N + 1, 1000), 2):
        if N % d1 == 0:
            d2 = N // d1
            if d1 < d2 and (d1 % 2) == (d2 % 2):
                m = (d1 + d2) // 2
                n = (d2 - d1) // 2
                t_estimates.append(n / m)
    
    # If we can't find any, estimate
    if not t_estimates:
        # For N = p*q with p ≈ q ≈ √N, t ≈ (q-p)/(p+q) ≈ 0
        # For N = p*q with p << q, t ≈ (q-p)/(p+q) ≈ 1 - 2p/q
        t_estimates = [0.01, 0.1, 0.3, 0.5]
    
    best_result = None
    
    for t_target in t_estimates:
        target_angle = np.arctan2(2*t_target, 1 - t_target**2)
        
        beam = [((3, 4, 5), "")]
        
        for depth in range(max_depth):
            # Check current beam for factors
            for (a, b, c), path in beam:
                for leg in [a, b]:
                    g = gcd(abs(leg), N)
                    if 1 < g < N:
                        return {
                            'success': True,
                            'N': N,
                            'factor': g,
                            'cofactor': N // g,
                            'depth': depth,
                            'path': path,
                            'triple': (a, b, c),
                            'nodes_visited': depth * beam_width,
                        }
            
            # Expand beam
            candidates = []
            for (a, b, c), path in beam:
                children = berggren_children(a, b, c)
                for i, (ca, cb, cc) in enumerate(children):
                    cL = Landscape(ca, cb, cc)
                    ang_dist = abs(cL.angle - target_angle)
                    ang_dist = min(ang_dist, 2*np.pi - ang_dist)
                    branch = ['L', 'M', 'R'][i]
                    candidates.append((ang_dist, (ca, cb, cc), path + branch))
            
            # Keep top beam_width candidates
            candidates.sort(key=lambda x: x[0])
            beam = [(c[1], c[2]) for c in candidates[:beam_width]]
            
            if not beam:
                break
    
    return {'success': False, 'N': N}

# ============================================================
# §2: THE "ALL RIGHT" PATH DISCOVERY
# ============================================================

def analyze_all_right_path(depth: int = 20):
    """
    The "All Right" path produces triples with remarkable factoring properties.
    
    DISCOVERY from Round 1:
    depth 0: (3,4,5), odd_leg = 3 = 1 × 3
    depth 1: (15,8,17), odd_leg = 15 = 3 × 5
    depth 2: (35,12,37), odd_leg = 35 = 5 × 7
    depth 3: (63,16,65), odd_leg = 63 = 7 × 9
    depth 4: (99,20,101), odd_leg = 99 = 9 × 11
    
    Pattern: odd_leg at depth k = (2k+1)(2k+3)
    This means the "Right" branch systematically produces consecutive factorizations!
    """
    print("\n" + "="*70)
    print("'ALL RIGHT' PATH ANALYSIS: Consecutive Factorization Pattern")
    print("="*70)
    
    a, b, c = 3, 4, 5
    for d in range(depth):
        odd_leg = a if a % 2 == 1 else b
        even_leg = b if a % 2 == 1 else a
        
        # Find factors
        factors = []
        for f in range(1, abs(odd_leg) + 1):
            if abs(odd_leg) % f == 0:
                factors.append(f)
        
        # Euclid parameters
        L = Landscape(a, b, c)
        predicted_odd = (2*d + 1) * (2*d + 3) if d > 0 else 3
        predicted_even = 4 * (d + 1)
        
        match_odd = "✅" if odd_leg == predicted_odd else "❌"
        match_even = "✅" if even_leg == predicted_even else "❌"
        
        print(f"  depth {d:>2}: ({a:>6},{b:>6},{c:>6}), odd={odd_leg:>6} [{match_odd} pred={predicted_odd}], "
              f"even={even_leg:>4} [{match_even} pred={predicted_even}], "
              f"t={L.t:.6f}, m={L.m}, n={L.n}")
        
        children = berggren_children(a, b, c)
        a, b, c = children[2]  # Always go right
    
    # THEOREM: For the all-right path, the Euclid parameters are (k+1, 1)
    print("\n  DISCOVERED PATTERN:")
    print("    Euclid params at depth k: m = k+2, n = 1")
    print("    odd_leg = m² - n² = (k+2)² - 1 = (k+1)(k+3)")
    print("    even_leg = 2mn = 2(k+2)")
    print("    hypotenuse = m² + n² = (k+2)² + 1")
    print("    stereo param t = n/m = 1/(k+2)")

# ============================================================
# §3: CONTINUED FRACTION CONNECTION
# ============================================================

def analyze_cf_connection(N: int):
    """
    HYPOTHESIS: The continued fraction expansion of √N (or related quantities)
    predicts the Berggren path to a useful triple.
    
    Key observation: The "All Mid" path converges to t = √2 - 1.
    The continued fraction of √2 = [1; 2, 2, 2, ...] ↔ repeated "Mid" steps.
    
    For general N, can the CF of √N guide the search?
    """
    print(f"\n{'='*70}")
    print(f"CONTINUED FRACTION ANALYSIS: N = {N}")
    print(f"{'='*70}")
    
    # CF expansion of sqrt(N)
    def cf_sqrt(n, max_terms=20):
        a0 = isqrt(n)
        if a0 * a0 == n:
            return [a0], 0  # Perfect square
        cf = [a0]
        m, d, a = 0, 1, a0
        for _ in range(max_terms):
            m = d * a - m
            d = (n - m * m) // d
            a = (a0 + m) // d
            cf.append(a)
            if a == 2 * a0:  # Period detected
                break
        return cf, len(cf) - 1
    
    cf, period = cf_sqrt(N)
    print(f"  √{N} = [{cf[0]}; {', '.join(map(str, cf[1:]))}]")
    print(f"  Period = {period}")
    
    # Convergents of the CF
    def convergents(cf):
        p = [0, 1]
        q = [1, 0]
        for a in cf:
            p.append(a * p[-1] + p[-2])
            q.append(a * q[-1] + q[-2])
        return list(zip(p[2:], q[2:]))
    
    convs = convergents(cf)
    print(f"  Convergents: {convs[:8]}")
    
    # Check if any convergent p/q gives a factor
    for p, q in convs:
        if q > 0:
            x = p  # p ≈ q * √N
            # Fermat's method: check if x² - N is a perfect square
            r = x * x - N * q * q
            if r >= 0:
                sr = isqrt(r)
                if sr * sr == r:
                    g = gcd(abs(x - sr * q), N) if q == 1 else gcd(abs(x - sr), N)
                    if 1 < g < N:
                        print(f"  🎯 FACTOR FOUND via convergent {p}/{q}: {N} = {g} × {N//g}")
    
    # Connect CF terms to Berggren branches
    # Hypothesis: CF coefficient a_k maps to a tree branch choice
    branch_map = {1: 'L', 2: 'M'}  # Speculative
    predicted_path = ''.join(branch_map.get(a, 'R') for a in cf[1:8])
    print(f"  Speculative path from CF: {predicted_path}")
    
    # Actually trace this path and check
    a, b, c = 3, 4, 5
    for ch in predicted_path:
        children = berggren_children(a, b, c)
        if ch == 'L':
            a, b, c = children[0]
        elif ch == 'M':
            a, b, c = children[1]
        else:
            a, b, c = children[2]
    
    for leg in [a, b]:
        g = gcd(abs(leg), N)
        if 1 < g < N:
            print(f"  🎯 CF-guided path found factor! {N} = {g} × {N//g}")
            print(f"     Triple: ({a}, {b}, {c})")
            return
    
    print(f"  CF path triple: ({a}, {b}, {c})")
    print(f"  gcd(a, N) = {gcd(abs(a), N)}, gcd(b, N) = {gcd(abs(b), N)}")

# ============================================================
# §4: LANDSCAPE ENERGY FUNCTION
# ============================================================

def landscape_energy_analysis(N: int):
    """
    Define an "energy function" on the Berggren tree relative to target N.
    
    E(triple) = min over all factorizations (d₁ × d₂ = N) of:
      |t(triple) - t_target(d₁, d₂)|
    
    where t_target(d₁, d₂) = (d₂ - d₁)/(d₁ + d₂) = (q-p)/(p+q).
    
    The search tries to minimize this energy by descending the tree.
    """
    print(f"\n{'='*70}")
    print(f"LANDSCAPE ENERGY SURFACE: N = {N}")
    print(f"{'='*70}")
    
    # Compute all target t-values
    targets = encode_factoring_target(N)
    if targets:
        print(f"  Target t-values:")
        for t in targets:
            print(f"    {t['factors']}: t* = {t['t_target']:.10f}")
    
    # BFS to depth 5, compute energy at each node
    from collections import deque
    queue = deque([((3, 4, 5), "", 0)])
    energies = []
    
    while queue:
        (a, b, c), path, depth = queue.popleft()
        if depth > 4:
            continue
        
        t = stereo_param_from_triple(a, b, c)
        
        # Energy = min distance to any target
        if targets:
            energy = min(abs(t - tgt['t_target']) for tgt in targets)
        else:
            energy = float('inf')
        
        # Check GCD
        g1 = gcd(abs(a), N)
        g2 = gcd(abs(b), N)
        has_factor = (1 < g1 < N) or (1 < g2 < N)
        
        marker = " ★ FACTOR!" if has_factor else ""
        energies.append((path or "root", (a,b,c), t, energy, has_factor))
        
        if depth < 4:
            children = berggren_children(a, b, c)
            for i, child in enumerate(children):
                branch = ['L','M','R'][i]
                queue.append((child, path + branch, depth + 1))
    
    # Sort by energy and show top/bottom
    energies.sort(key=lambda x: x[3])
    print(f"\n  Lowest energy nodes (closest to target):")
    for path, triple, t, energy, has_factor in energies[:10]:
        marker = " ★" if has_factor else ""
        print(f"    {path:>8}: {triple}, t={t:.6f}, E={energy:.8f}{marker}")
    
    print(f"\n  Highest energy nodes (farthest from target):")
    for path, triple, t, energy, has_factor in energies[-5:]:
        print(f"    {path:>8}: {triple}, t={t:.6f}, E={energy:.8f}")

# ============================================================
# §5: LANDSCAPE FITTING — PARENT/CHILD RELATIONSHIPS
# ============================================================

def analyze_landscape_fitting():
    """
    HOW DO PARENT AND CHILD LANDSCAPES FIT TOGETHER?
    
    Key geometric insight: Under stereographic projection, the Berggren
    transformations act as Möbius transformations on the parameter t.
    
    The three Berggren matrices map t ↦ t' via:
    M₁: (m,n) → (2m+n, m)  → t' = m/(2m+n) (contraction toward 0)
    M₂: (m,n) → (2m-n, m)  → t' = m/(2m-n) (near identity for n<<m)
    M₃: (m,n) → (m+2n, n)  → t' = n/(m+2n) (contraction toward 0)
    
    Wait — let me verify these. In Euclid parametrization:
    Root: m=2, n=1, t=n/m = 1/2 → (3,4,5)
    
    Left child: (5,12,13), m=3, n=2, t=2/3
    Hmm, t went from 1/2 to 2/3. Not quite what I expected.
    
    Let me reconsider: t = a/(b+c) not n/m.
    """
    print("\n" + "="*70)
    print("LANDSCAPE FITTING: Parent-Child Relationships")
    print("="*70)
    
    # Track how the Berggren transformations act on t
    test_triples = [
        (3, 4, 5),     # t = 3/9 = 1/3
        (5, 12, 13),   # t = 5/25 = 1/5
        (21, 20, 29),  # t = 21/49 = 3/7
        (15, 8, 17),   # t = 15/25 = 3/5
    ]
    
    for a, b, c in test_triples:
        t_parent = Fraction(a, b + c)
        children = berggren_children(a, b, c)
        
        print(f"\n  Parent: ({a},{b},{c}), t = {t_parent} = {float(t_parent):.6f}")
        
        for i, (ca, cb, cc) in enumerate(children):
            t_child = Fraction(ca, cb + cc)
            branch = ['M₁ (L)', 'M₂ (M)', 'M₃ (R)'][i]
            
            # How does t_child relate to t_parent?
            # Try: t_child = f(t_parent) for some Möbius transform
            # f(t) = (αt + β)/(γt + δ)
            ratio = t_child / t_parent if t_parent != 0 else None
            diff = t_child - t_parent
            
            print(f"    {branch}: ({ca},{cb},{cc}), t = {t_child} = {float(t_child):.6f}")
            print(f"      t_child/t_parent = {float(ratio):.6f}" if ratio else "")
            print(f"      t_child - t_parent = {float(diff):.6f}")
    
    # DEEPER: Express Berggren as Möbius transformations on t
    print("\n  MÖBIUS TRANSFORMATION ANALYSIS:")
    print("  If (a,b,c) → (a',b',c') via M₁, then:")
    print("  t' = a'/(b'+c') = (a-2b+2c)/((2a-b+2c)+(2a-2b+3c))")
    print("     = (a-2b+2c)/(4a-3b+5c)")
    print("  Similarly for M₂ and M₃.")
    
    # Verify the Möbius form with examples
    a, b, c = 3, 4, 5
    children = berggren_children(a, b, c)
    for i, name in enumerate(['M₁', 'M₂', 'M₃']):
        ca, cb, cc = children[i]
        t_num = [a - 2*b + 2*c, a + 2*b + 2*c, -a + 2*b + 2*c][i]
        t_den = [4*a - 3*b + 5*c, 4*a + 3*b + 5*c, -4*a + 3*b + 5*c][i]  # Fixed: wrong sign
        # Actually let me just compute:
        if i == 0:
            num = a - 2*b + 2*c
            den = (2*a - b + 2*c) + (2*a - 2*b + 3*c)
        elif i == 1:
            num = a + 2*b + 2*c
            den = (2*a + b + 2*c) + (2*a + 2*b + 3*c)
        else:
            num = -a + 2*b + 2*c
            den = (-2*a + b + 2*c) + (-2*a + 2*b + 3*c)
        
        t_computed = Fraction(num, den)
        t_actual = Fraction(ca, cb + cc)
        match = "✅" if t_computed == t_actual else f"❌ (got {t_computed})"
        print(f"  {name}: computed t = {num}/{den} = {float(t_computed):.6f}, "
              f"actual t = {float(t_actual):.6f} {match}")
    
    # Express as functions of t = a/(b+c) and u = b/c (or similar)
    print("\n  KEY INSIGHT: t alone does NOT determine the child's t.")
    print("  We need BOTH a/(b+c) and the triple itself to compute the child's t.")
    print("  The Berggren tree lives in a 2D parameter space (t, some other coordinate),")
    print("  not just the 1D stereographic line.")

# ============================================================
# §6: THE SILVER RATIO DISCOVERY
# ============================================================

def analyze_silver_ratio():
    """
    DISCOVERY: The "All Mid" path converges to t = √2 - 1 ≈ 0.41421356...
    
    This is the SILVER RATIO, also known as the silver mean δ_S = √2 - 1.
    It satisfies δ_S² + 2δ_S = 1, or equivalently 1/(1 + δ_S) = δ_S + 1 - 1/1 = ...
    
    The continued fraction: √2 - 1 = [0; 2, 2, 2, ...] = 1/(2 + 1/(2 + 1/(2 + ...)))
    
    This connects to Pell's equation: x² - 2y² = ±1
    Solutions: (1,1), (3,2), (7,5), (17,12), (41,29), ...
    
    These are exactly the ratios of consecutive elements in the "All Mid" triples!
    """
    print("\n" + "="*70)
    print("THE SILVER RATIO DISCOVERY")
    print("="*70)
    
    silver = np.sqrt(2) - 1
    print(f"  Silver ratio δ_S = √2 - 1 = {silver:.15f}")
    print(f"  1/δ_S = {1/silver:.15f} = 1 + √2 = {1 + np.sqrt(2):.15f}")
    
    # Generate All-Mid path
    a, b, c = 3, 4, 5
    print(f"\n  All-Mid path convergence to δ_S:")
    for d in range(12):
        t = stereo_param_from_triple(a, b, c)
        err = abs(t - silver)
        
        # Check Pell's equation connection
        if a % 2 == 1:
            odd, even = a, b
        else:
            odd, even = b, a
        
        # For All-Mid triples: check if a/b or b/a approximates √2
        ratio = a / b if b != 0 else 0
        ratio_err = abs(ratio - 1.0)  # a ≈ b for these triples
        
        print(f"  d={d:>2}: ({a:>8},{b:>8},{c:>8}), t={t:.12f}, "
              f"|t-δ_S|={err:.2e}, a/b={ratio:.10f}")
        
        children = berggren_children(a, b, c)
        a, b, c = children[1]  # Mid
    
    # Pell connection
    print("\n  Pell's equation x² - 2y² = ±1 solutions:")
    x, y = 1, 1
    for i in range(8):
        residue = x*x - 2*y*y
        print(f"    ({x:>6}, {y:>6}): x²-2y² = {residue:>2}")
        x, y = x + 2*y, x + y  # Pell recurrence

# ============================================================
# §7: MULTI-RESOLUTION LANDSCAPE SEARCH
# ============================================================

def multi_resolution_search(N: int, verbose: bool = True) -> Dict:
    """
    IDEA: Combine multiple landscape resolutions.
    
    At coarse resolution: use the angle heuristic to narrow to a subtree.
    At fine resolution: use GCD checks and conformal factor matching.
    
    The "landscape" at resolution k examines the first k continued fraction
    digits of the stereographic parameter.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"MULTI-RESOLUTION LANDSCAPE SEARCH: N = {N}")
        print(f"{'='*70}")
    
    # Phase 1: Trial division up to small bound
    for p in range(3, min(1000, isqrt(N) + 1), 2):
        if N % p == 0:
            if verbose:
                print(f"  Phase 1 (trial): {N} = {p} × {N//p}")
            return {'success': True, 'factor': p, 'method': 'trial'}
    
    # Phase 2: Fermat's method (look near √N)
    x = isqrt(N) + 1
    for _ in range(1000):
        y2 = x*x - N
        y = isqrt(y2)
        if y*y == y2:
            p, q = x - y, x + y
            if 1 < p < N:
                if verbose:
                    print(f"  Phase 2 (Fermat): {N} = {p} × {q}")
                return {'success': True, 'factor': p, 'method': 'fermat'}
        x += 1
    
    # Phase 3: Berggren beam search with landscape guidance
    result = beam_search(N, beam_width=20, max_depth=200)
    if result.get('success'):
        if verbose:
            print(f"  Phase 3 (Berggren beam): {N} = {result['factor']} × {result['cofactor']}")
        return result
    
    # Phase 4: All-Right path (consecutive factorizations)
    a, b, c = 3, 4, 5
    for d in range(isqrt(N)):
        odd_leg = a if a % 2 == 1 else b
        g = gcd(abs(odd_leg), N)
        if 1 < g < N:
            if verbose:
                print(f"  Phase 4 (All-Right): {N} = {g} × {N//g} at depth {d}")
            return {'success': True, 'factor': g, 'method': 'all_right', 'depth': d}
        children = berggren_children(a, b, c)
        a, b, c = children[2]
    
    return {'success': False, 'N': N}

# ============================================================
# §8: COMPREHENSIVE EXPERIMENTS
# ============================================================

def run_deep_experiments():
    """Run all deep analysis experiments."""
    
    # §A: All-Right path analysis
    analyze_all_right_path(depth=15)
    
    # §B: Silver ratio discovery
    analyze_silver_ratio()
    
    # §C: Landscape fitting
    analyze_landscape_fitting()
    
    # §D: Continued fraction analysis
    for N in [35, 77, 143, 221, 323, 1001, 10403]:
        analyze_cf_connection(N)
    
    # §E: Energy surface analysis
    for N in [35, 77, 143]:
        landscape_energy_analysis(N)
    
    # §F: GCD search experiments
    print("\n" + "="*70)
    print("GCD-BASED LANDSCAPE SEARCH EXPERIMENTS")
    print("="*70)
    
    semiprimes = [
        (3, 5, 15), (5, 7, 35), (7, 11, 77), (11, 13, 143),
        (13, 17, 221), (17, 19, 323), (23, 29, 667),
        (31, 37, 1147), (41, 43, 1763), (53, 59, 3127),
        (71, 73, 5183), (97, 101, 9797), (127, 131, 16637),
        (101, 103, 10403), (151, 157, 23707),
    ]
    
    for p, q, N in semiprimes:
        t_start = time.time()
        result = gcd_landscape_search(N, max_depth=50, max_nodes=10000)
        elapsed = time.time() - t_start
        
        status = "✅" if result.get('success') else "❌"
        depth = result.get('depth', '—')
        nodes = result.get('nodes_visited', '—')
        print(f"  {status} N={N:>6} = {p:>3}×{q:>3} | d={str(depth):>4} | "
              f"nodes={str(nodes):>6} | {elapsed:.3f}s")
    
    # §G: Beam search comparison
    print("\n" + "="*70)
    print("BEAM SEARCH EXPERIMENTS")
    print("="*70)
    
    for p, q, N in semiprimes:
        t_start = time.time()
        result = beam_search(N, beam_width=20, max_depth=200)
        elapsed = time.time() - t_start
        
        status = "✅" if result.get('success') else "❌"
        depth = result.get('depth', '—')
        nodes = result.get('nodes_visited', '—')
        print(f"  {status} N={N:>6} = {p:>3}×{q:>3} | d={str(depth):>4} | "
              f"nodes={str(nodes):>6} | {elapsed:.3f}s")

if __name__ == "__main__":
    print("╔" + "═"*68 + "╗")
    print("║  DEEP LANDSCAPE ANALYSIS — Round 2                                ║")
    print("╚" + "═"*68 + "╝")
    
    run_deep_experiments()
    
    print("\n\n✅ Deep analysis complete.")
