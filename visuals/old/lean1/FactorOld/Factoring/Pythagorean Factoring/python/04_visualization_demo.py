#!/usr/bin/env python3
"""
=============================================================================
PYTHAGOREAN TRIPLE TREE FACTORING — INTERACTIVE VISUALIZATION DEMO
=============================================================================

A complete demonstration program showing:
1. How to factor any odd number using Pythagorean triples
2. The Berggren ternary tree and parent-child relationships  
3. The depth-factor theorem in action
4. ASCII tree visualization of the factoring process

Run: python3 04_visualization_demo.py [number_to_factor]
"""

import math
import sys
from typing import List, Tuple, Optional, Dict

# ==========================================================================
# CORE ALGORITHMS
# ==========================================================================

def factorize(n: int) -> List[int]:
    """Trial division factorization."""
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors


def triples_from_leg(n: int) -> List[Tuple[int, int, int]]:
    """Find all Pythagorean triples (n, b, c) with n² + b² = c²."""
    n_sq = n * n
    triples = []
    for d in range(1, int(math.isqrt(n_sq)) + 1):
        if n_sq % d != 0:
            continue
        e = n_sq // d
        if d >= e or (d + e) % 2 != 0:
            continue
        b = (e - d) // 2
        c = (e + d) // 2
        if b > 0:
            triples.append((n, b, c))
    return triples


def make_primitive(triple):
    """Reduce to primitive form."""
    a, b, c = triple
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
    result = (a // g, b // g, c // g)
    if result[0] % 2 == 0:
        result = (result[1], result[0], result[2])
    return result, g


# Berggren inverse matrices (verified correct)
def find_parent(triple):
    """Find the parent of a primitive Pythagorean triple in the Berggren tree."""
    a, b, c = triple
    if (a, b, c) == (3, 4, 5):
        return None, None
    
    candidates = {
        'A': ( a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c),
        'B': ( a + 2*b - 2*c,  2*a + b - 2*c, -2*a - 2*b + 3*c),
        'C': (-a - 2*b + 2*c,  2*a + b - 2*c, -2*a - 2*b + 3*c),
    }
    
    for label, (pa, pb, pc) in candidates.items():
        if pa > 0 and pb > 0 and pc > 0 and pc < c:
            if pa % 2 == 0 and pb % 2 == 1:
                pa, pb = pb, pa
            return label, (pa, pb, pc)
    
    return None, None


def climb_to_root(triple):
    """Climb from primitive triple to root (3,4,5), return path."""
    a, b, c = triple
    if a % 2 == 0:
        a, b = b, a
    current = (a, b, c)
    path = []
    ancestors = [current]
    
    for _ in range(100000):
        if current == (3, 4, 5):
            break
        label, parent = find_parent(current)
        if parent is None:
            break
        path.append(label)
        ancestors.append(parent)
        current = parent
    
    return path, ancestors


def berggren_children(triple):
    """Generate three children of a primitive Pythagorean triple."""
    a, b, c = triple
    
    A = [[ 1, -2,  2], [ 2, -1,  2], [ 2, -2,  3]]
    B = [[ 1,  2,  2], [ 2,  1,  2], [ 2,  2,  3]]
    C = [[-1,  2,  2], [-2,  1,  2], [-2,  2,  3]]
    
    def apply(M, v):
        result = tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))
        r = list(result)
        if r[0] % 2 == 0:
            r[0], r[1] = r[1], r[0]
        return tuple(abs(x) for x in r[:2]) + (abs(r[2]),)
    
    return {
        'A': apply(A, (a, b, c)),
        'B': apply(B, (a, b, c)),
        'C': apply(C, (a, b, c)),
    }


# ==========================================================================
# VISUALIZATION
# ==========================================================================

def print_banner():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     PYTHAGOREAN TRIPLE TREE FACTORING DEMONSTRATION        ║")
    print("║                                                            ║")
    print("║  Given n, construct (n, b, c) with n² + b² = c²           ║")
    print("║  Since (c-b)(c+b) = n², each triple reveals a             ║")
    print("║  factorization — and climbing the Berggren tree             ║")
    print("║  encodes the arithmetic structure of n.                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()


def visualize_factoring(n: int):
    """Complete factoring visualization for a number n."""
    
    factors = factorize(n)
    is_prime = len(factors) == 1
    
    print(f"━━━ ANALYZING n = {n} ━━━")
    print(f"    Prime factorization: {' × '.join(map(str, factors))}")
    print(f"    n² = {n*n}")
    print(f"    Is prime: {'YES' if is_prime else 'NO'}")
    print()
    
    # Find all triples
    triples = triples_from_leg(n)
    print(f"    Pythagorean triples with leg {n}: {len(triples)}")
    print()
    
    # Analyze each triple
    factors_found = set()
    
    for i, triple in enumerate(triples):
        a, b, c = triple
        d, e = c - b, c + b
        prim, g = make_primitive(triple)
        path, ancestors = climb_to_root(prim)
        
        # Try to extract factors
        gcd_d = math.gcd(d, n)
        gcd_e = math.gcd(e, n)
        
        factor_info = []
        if 1 < gcd_d < n:
            factors_found.add(gcd_d)
            factor_info.append(f"gcd({d},{n})={gcd_d}")
        if 1 < gcd_e < n:
            factors_found.add(gcd_e)
            factor_info.append(f"gcd({e},{n})={gcd_e}")
        if 1 < g < n:
            factors_found.add(g)
            factor_info.append(f"gcd_triple={g}")
        
        # Classify triple type
        if d == 1:
            ttype = "TRIVIAL"
        elif g > 1 and g < n:
            ttype = f"FACTOR-{g}"
        elif any(int(math.isqrt(d))**2 == d for _ in [1]):
            sqrt_d = int(math.isqrt(d))
            if sqrt_d * sqrt_d == d and sqrt_d > 1:
                ttype = f"CROSS-{sqrt_d}²"
            else:
                ttype = "OTHER"
        else:
            ttype = "OTHER"
        
        path_str = ''.join(path) if path else "(root)"
        if len(path_str) > 40:
            path_str = path_str[:37] + "..."
        
        print(f"    Triple #{i+1}: ({a}, {b}, {c})")
        print(f"      Type: {ttype}")
        print(f"      Factorization: {d} × {e} = {n*n}")
        print(f"      Primitive: {prim}, scale factor: {g}")
        print(f"      Berggren path: {path_str} (depth {len(path)})")
        if factor_info:
            print(f"      ⟹ FACTORS: {', '.join(factor_info)}")
        
        # Show ancestry
        if len(ancestors) > 1 and len(ancestors) <= 8:
            anc_str = " → ".join(str(a) for a in ancestors)
            print(f"      Ancestry: {anc_str}")
        elif len(ancestors) > 8:
            print(f"      Ancestry: {ancestors[0]} → {ancestors[1]} → ... → {ancestors[-1]}")
        
        print()
    
    # Summary
    if factors_found:
        print(f"    ╔══════════════════════════════════════════════╗")
        print(f"    ║ FACTORS DISCOVERED: {sorted(factors_found)}")
        print(f"    ║ Verification: {n} = {' × '.join(map(str, factors))}")
        print(f"    ╚══════════════════════════════════════════════╝")
    elif is_prime:
        print(f"    ╔══════════════════════════════════════════════╗")
        print(f"    ║ n = {n} is PRIME (exactly 1 triple)          ")
        print(f"    ╚══════════════════════════════════════════════╝")
    print()


def show_berggren_tree(depth=3):
    """Show the first few levels of the Berggren tree."""
    print("━━━ THE BERGGREN TERNARY TREE ━━━")
    print()
    print("    Every primitive Pythagorean triple appears exactly once.")
    print("    Root: (3, 4, 5)")
    print()
    
    def show_node(triple, prefix, label, d):
        a, b, c = triple
        # Verify it's a valid triple
        assert a*a + b*b == c*c, f"Invalid: {triple}"
        
        m = int(math.isqrt((c + a) // 2)) if a % 2 == 1 else int(math.isqrt((c + b) // 2))
        n_param = int(math.isqrt((c - a) // 2)) if a % 2 == 1 else int(math.isqrt((c - b) // 2))
        
        print(f"{prefix}[{label}] ({a}, {b}, {c})  m={m}, n={n_param}")
        
        if d < depth:
            children = berggren_children(triple)
            for i, (child_label, child) in enumerate(children.items()):
                is_last = (i == len(children) - 1)
                child_prefix = prefix + ("    " if is_last else "│   ")
                connector = "└── " if is_last else "├── "
                show_node(child, prefix + connector[:-4], child_label, d + 1)
    
    show_node((3, 4, 5), "    ", "ROOT", 0)
    print()


def show_depth_factor_theorem():
    """Demonstrate the depth-factor theorem."""
    print("━━━ THE DEPTH-FACTOR THEOREM ━━━")
    print()
    print("    For n = p × q (semiprime with p < q, both odd primes):")
    print("    • The FACTOR-p triple has Berggren depth (q-3)/2")
    print("    • The FACTOR-q triple has Berggren depth (p-3)/2")
    print("    • The tree depth reveals the complementary factor!")
    print()
    
    primes = [p for p in range(3, 100) if all(p % i for i in range(2, int(p**0.5)+1))]
    
    print(f"    {'p':>4s} {'q':>4s} {'n=p×q':>8s} │ {'depth_p':>7s} {'(q-3)/2':>8s} {'match':>5s} │ {'depth_q':>7s} {'(p-3)/2':>8s} {'match':>5s}")
    print(f"    {'─'*4} {'─'*4} {'─'*8} │ {'─'*7} {'─'*8} {'─'*5} │ {'─'*7} {'─'*8} {'─'*5}")
    
    for i, p in enumerate(primes[:12]):
        for q in primes[i+1:i+2]:
            n = p * q
            triples = triples_from_leg(n)
            
            depth_p = depth_q = None
            for triple in triples:
                prim, g = make_primitive(triple)
                if g == p:
                    path, _ = climb_to_root(prim)
                    depth_p = len(path)
                elif g == q:
                    path, _ = climb_to_root(prim)
                    depth_q = len(path)
            
            if depth_p is not None and depth_q is not None:
                pred_dp = (q - 3) // 2
                pred_dq = (p - 3) // 2
                mp = "✓" if depth_p == pred_dp else "✗"
                mq = "✓" if depth_q == pred_dq else "✗"
                print(f"    {p:4d} {q:4d} {n:8d} │ {depth_p:7d} {pred_dp:8d} {mp:>5s} │ {depth_q:7d} {pred_dq:8d} {mq:>5s}")
    print()


def show_primality_test():
    """Demonstrate the primality test via triple counting."""
    print("━━━ PRIMALITY TEST: Count Pythagorean Triples ━━━")
    print()
    print("    THEOREM: Odd n is prime ⟺ exactly 1 Pythagorean triple with leg n")
    print()
    
    for n in range(3, 60, 2):
        count = len(triples_from_leg(n))
        is_prime = all(n % i for i in range(2, int(n**0.5)+1))
        status = "PRIME" if is_prime else f"= {'×'.join(map(str, factorize(n)))}"
        bar = "█" * count
        print(f"    n={n:3d}: {count:2d} triple(s) {bar:30s} {status}")
    print()


def interactive_demo():
    """Run the full interactive demonstration."""
    print_banner()
    
    # 1. Show the Berggren tree
    show_berggren_tree(depth=2)
    
    # 2. Primality test
    show_primality_test()
    
    # 3. Depth-factor theorem
    show_depth_factor_theorem()
    
    # 4. Factor some numbers
    test_numbers = [15, 35, 77, 91, 143, 221, 1001, 10403]
    for n in test_numbers:
        visualize_factoring(n)
    
    # 5. Summary
    print("═" * 62)
    print("SUMMARY OF PROVEN THEOREMS (formalized in Lean 4)")
    print("═" * 62)
    print("""
    1. BIJECTION THEOREM:
       Pythagorean triples (n,b,c) ↔ same-parity divisor pairs of n²
       via d = c-b, e = c+b

    2. FACTORING THEOREM:
       Each non-trivial divisor pair yields gcd(d,n) as a factor of n

    3. COUNTING THEOREM:
       |T(n)| = (σ₀(n²) - 1) / 2 for odd n

    4. PRIMALITY THEOREM:
       n is odd prime ⟺ |T(n)| = 1

    5. PARAMETRIZATION THEOREM:
       Every primitive triple (a,b,c) = (m²-n², 2mn, m²+n²)
       for unique m > n with gcd(m,n)=1 and m-n odd

    6. DEPTH THEOREM:
       For prime p, the trivial triple has Berggren depth (p-3)/2
       via parameters m=(p+1)/2, n=(p-1)/2

    All theorems formally verified in Lean 4 with Mathlib.
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
            if n < 3 or n % 2 == 0:
                print("Please provide an odd number ≥ 3")
            else:
                print_banner()
                visualize_factoring(n)
        except ValueError:
            print("Please provide a valid integer")
    else:
        interactive_demo()
