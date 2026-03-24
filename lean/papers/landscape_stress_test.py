#!/usr/bin/env python3
"""
STRESS TEST: Landscape-guided factoring on larger semiprimes.
Tests scaling behavior and identifies the complexity boundary.
"""
import time
import numpy as np
from math import gcd, isqrt
from landscape_engine import (
    berggren_children, Landscape, stereo_param_from_triple
)

def beam_search_v2(N, beam_width=50, max_depth=500):
    """Optimized beam search with GCD checks."""
    # Estimate target parameter range
    sqrt_N = isqrt(N)
    
    # Multiple target angle estimates
    target_angles = []
    # For balanced factors (p ≈ q ≈ √N), odd leg ≈ N, angle ≈ 0
    target_angles.append(np.pi / (2 * sqrt_N))
    # For unbalanced factors, angle ≈ π/2
    target_angles.append(np.pi / 4)
    target_angles.append(np.pi / 6)
    
    beam = [((3, 4, 5), "")]
    
    for depth in range(max_depth):
        # Check current beam
        for (a, b, c), path in beam:
            for leg in [abs(a), abs(b)]:
                g = gcd(leg, N)
                if 1 < g < N:
                    return {
                        'success': True, 'factor': g, 'cofactor': N // g,
                        'depth': depth, 'nodes': depth * beam_width,
                        'path_len': len(path)
                    }
        
        # Expand
        candidates = []
        for (a, b, c), path in beam:
            children = berggren_children(a, b, c)
            for i, (ca, cb, cc) in enumerate(children):
                # Score: minimum angular distance to any target angle
                angle = np.arctan2(abs(cb), abs(ca))
                min_dist = min(abs(angle - ta) for ta in target_angles)
                
                # Also reward nodes whose legs share factors with N
                g1 = gcd(abs(ca), N)
                g2 = gcd(abs(cb), N)
                gcd_bonus = -100.0 if (g1 > 1 or g2 > 1) else 0.0
                
                score = min_dist + gcd_bonus
                branch = ['L', 'M', 'R'][i]
                candidates.append((score, (ca, cb, cc), path + branch))
        
        candidates.sort(key=lambda x: x[0])
        beam = [(c[1], c[2]) for c in candidates[:beam_width]]
    
    return {'success': False}

def run_stress_tests():
    """Test on increasingly large semiprimes."""
    print("╔" + "═"*68 + "╗")
    print("║  STRESS TEST: Landscape Factoring Scalability                      ║")
    print("╚" + "═"*68 + "╝")
    
    # Generate semiprimes of increasing size
    from sympy import nextprime, isprime
    
    test_cases = []
    
    # Small primes
    primes_small = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for i in range(len(primes_small) - 1):
        p, q = primes_small[i], primes_small[i+1]
        test_cases.append((p, q, p*q))
    
    # Medium primes
    medium = [101, 103, 127, 131, 151, 157, 199, 211, 251, 257, 307, 311, 
              401, 409, 503, 509, 601, 607, 701, 709, 809, 811, 907, 911]
    for i in range(0, len(medium)-1, 2):
        p, q = medium[i], medium[i+1]
        test_cases.append((p, q, p*q))
    
    # Larger primes
    large = [1009, 1013, 2003, 2011, 3001, 3011, 5003, 5009, 
             10007, 10009, 20011, 20021, 50021, 50023]
    for i in range(0, len(large)-1, 2):
        p, q = large[i], large[i+1]
        test_cases.append((p, q, p*q))
    
    # RSA-style (very unbalanced)
    unbalanced = [(3, 10007), (7, 50021), (11, 100003), (13, 200003)]
    for p, q in unbalanced:
        test_cases.append((p, q, p*q))
    
    print(f"\n{'Status':>6} {'N':>12} {'p':>7} {'q':>7} {'Depth':>6} {'Nodes':>8} {'Time':>8} {'bits':>5}")
    print("-" * 70)
    
    successes = 0
    total = 0
    
    for p, q, N in test_cases:
        total += 1
        t_start = time.time()
        result = beam_search_v2(N, beam_width=100, max_depth=1000)
        elapsed = time.time() - t_start
        
        bits = N.bit_length()
        
        if result.get('success'):
            successes += 1
            d = result['depth']
            n = result['nodes']
            print(f"  ✅   {N:>12} {p:>7} {q:>7} {d:>6} {n:>8} {elapsed:>7.3f}s {bits:>5}")
        else:
            print(f"  ❌   {N:>12} {p:>7} {q:>7}    —        — {elapsed:>7.3f}s {bits:>5}")
    
    print(f"\nSuccess rate: {successes}/{total} ({100*successes/total:.1f}%)")

if __name__ == "__main__":
    try:
        run_stress_tests()
    except ImportError:
        # If sympy not available, use simpler test set
        print("Running without sympy...")
        
        test_cases = [
            (3, 5, 15), (7, 11, 77), (13, 17, 221), (23, 29, 667),
            (41, 43, 1763), (71, 73, 5183), (97, 101, 9797),
            (127, 131, 16637), (199, 211, 41989), (307, 311, 95477),
            (503, 509, 256027), (701, 709, 497009), (907, 911, 826277),
            (1009, 1013, 1022117), (2003, 2011, 4028033),
            (3001, 3011, 9036011), (5003, 5009, 25060027),
            (10007, 10009, 100160063), (3, 10007, 30021),
            (7, 50021, 350147), (11, 100003, 1100033),
        ]
        
        print(f"\n{'Status':>6} {'N':>12} {'p':>7} {'q':>7} {'Depth':>6} {'Nodes':>8} {'Time':>8} {'bits':>5}")
        print("-" * 70)
        
        successes = 0
        for p, q, N in test_cases:
            t_start = time.time()
            result = beam_search_v2(N, beam_width=100, max_depth=1000)
            elapsed = time.time() - t_start
            bits = N.bit_length()
            if result.get('success'):
                successes += 1
                d = result['depth']
                n = result['nodes']
                print(f"  ✅   {N:>12} {p:>7} {q:>7} {d:>6} {n:>8} {elapsed:>7.3f}s {bits:>5}")
            else:
                print(f"  ❌   {N:>12} {p:>7} {q:>7}    —        — {elapsed:>7.3f}s {bits:>5}")
        
        print(f"\nSuccess rate: {successes}/{len(test_cases)}")
