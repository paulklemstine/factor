#!/usr/bin/env python3
"""
=============================================================================
EXPERIMENT 10: VISUAL EXPLORER — ASCII Art Berggren Tree & Hyperbolic Tiling
=============================================================================

Interactive visualization of:
1. The Berggren tree structure (ASCII art tree)
2. The "factoring radar" — angular positions of triples
3. The hyperbolic tiling (ASCII approximation)
4. The depth-factor landscape
"""

import math
import sys
from collections import Counter

def factorize(n):
    factors = []
    d = 2
    temp = abs(n)
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors

def triples_from_leg(n):
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
    a, b, c = triple
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
    result = (a // g, b // g, c // g)
    if result[0] % 2 == 0:
        result = (result[1], result[0], result[2])
    return result, g

# Berggren tree
A = [[ 1, -2,  2], [ 2, -1,  2], [ 2, -2,  3]]
B = [[ 1,  2,  2], [ 2,  1,  2], [ 2,  2,  3]]
C = [[-1,  2,  2], [-2,  1,  2], [-2,  2,  3]]

def mat_vec(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))

def normalize_triple(triple):
    a, b, c = [abs(x) for x in triple]
    if a % 2 == 0: a, b = b, a
    return (a, b, c)


# ==========================================================================
# 1. ASCII Art Berggren Tree
# ==========================================================================

def draw_tree(max_depth=3):
    """Draw the Berggren tree as ASCII art."""
    print("=" * 80)
    print("THE BERGGREN TREE OF ALL PRIMITIVE PYTHAGOREAN TRIPLES")
    print("=" * 80)
    
    def draw_subtree(triple, depth, prefix, is_last, label=""):
        a, b, c = triple
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        
        triple_str = f"({a},{b},{c})"
        if label:
            print(f"{prefix}{connector}[{label}] {triple_str}")
        else:
            print(f"{prefix}{triple_str}")
        
        if depth < max_depth:
            children = []
            for lbl, M in [("A", A), ("B", B), ("C", C)]:
                child = mat_vec(M, triple)
                child = normalize_triple(child)
                children.append((lbl, child))
            
            for i, (lbl, child) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                draw_subtree(child, depth + 1, prefix + extension, is_last_child, lbl)
    
    root = (3, 4, 5)
    draw_subtree(root, 0, "", True)
    
    count = sum(3**i for i in range(max_depth + 1))
    print(f"\n  Total nodes shown: {count} (depth ≤ {max_depth})")
    print(f"  At depth {max_depth+1}: {3**(max_depth+1)} more nodes")
    print(f"  The tree extends infinitely, containing ALL primitive Pythagorean triples")


# ==========================================================================
# 2. Factoring Radar
# ==========================================================================

def factoring_radar(n):
    """Display an ASCII 'radar' showing angular positions of triples."""
    print("\n" + "=" * 80)
    print(f"FACTORING RADAR FOR n = {n}")
    print("=" * 80)
    
    factors = factorize(n)
    exp_str = " × ".join(str(f) for f in factors)
    print(f"  n = {n} = {exp_str}")
    
    triples = triples_from_leg(n)
    if not triples:
        print("  No triples found")
        return
    
    # Compute angular positions
    positions = []
    for triple in triples:
        prim, g = make_primitive(triple)
        a, b, c = prim
        theta = math.atan2(b, a) * 180 / math.pi  # 0° to 90°
        
        d = triple[2] - triple[1]
        if d == 1:
            label = "T"  # Trivial
        elif g > 1 and g < n:
            label = f"F{g}"  # Factor
        else:
            label = "X"  # Cross or other
        
        positions.append((theta, label, prim, g))
    
    # ASCII radar display (0° to 90°)
    width = 60
    print(f"\n  0°{'─' * (width-8)}90°")
    
    # Place markers
    for theta, label, prim, g in sorted(positions):
        pos = int(theta / 90 * (width - 4))
        line = list(" " * width)
        for i, ch in enumerate(label):
            if pos + i < width:
                line[pos + i] = ch
        print(f"  {''.join(line)}  θ={theta:.1f}° g={g} {prim}")
    
    print(f"  0°{'─' * (width-8)}90°")
    print(f"\n  Legend: T=Trivial, F#=Factor-#, X=Cross/Other")


# ==========================================================================
# 3. Depth Landscape
# ==========================================================================

def depth_landscape():
    """Visualize how Berggren depth varies across odd numbers."""
    print("\n" + "=" * 80)
    print("DEPTH LANDSCAPE: Berggren Depth vs Number")
    print("=" * 80)
    
    A_inv = [[ 1,  2, -2], [-2, -1,  2], [-2, -2,  3]]
    B_inv = [[ 1,  2, -2], [ 2,  1, -2], [-2, -2,  3]]
    C_inv = [[-1, -2,  2], [ 2,  1, -2], [-2, -2,  3]]
    
    def find_parent(triple):
        a, b, c = triple
        if (a, b, c) == (3, 4, 5):
            return None, None
        for label, M_inv in [('A', A_inv), ('B', B_inv), ('C', C_inv)]:
            result = mat_vec(M_inv, (a, b, c))
            pa, pb, pc = result
            if pa > 0 and pb > 0 and pc > 0 and pc < c:
                if pa % 2 == 0 and pb % 2 == 1:
                    pa, pb = pb, pa
                return label, (pa, pb, pc)
        return None, None
    
    def berggren_depth(triple):
        a, b, c = triple
        if a % 2 == 0: a, b = b, a
        current = (a, b, c)
        depth = 0
        for _ in range(100000):
            if current == (3, 4, 5): break
            label, parent = find_parent(current)
            if parent is None: break
            depth += 1
            current = parent
        return depth
    
    print("\n  For each odd n, showing depth of trivial triple (depth = (n-3)/2 for primes):")
    print(f"\n  {'n':>4s} | {'type':>8s} | {'trivial depth':>13s} | {'bar':>40s}")
    print("  " + "-" * 70)
    
    max_bar = 40
    
    for n in range(3, 60, 2):
        factors = factorize(n)
        is_p = len(factors) == 1
        
        # Trivial triple depth
        a, b, c = n, (n*n - 1) // 2, (n*n + 1) // 2
        prim, g = make_primitive((a, b, c))
        depth = berggren_depth(prim)
        
        ntype = "prime" if is_p else "×".join(str(f) for f in factors)
        bar_len = min(depth, max_bar)
        bar = "█" * bar_len + ("→" if depth > max_bar else "")
        
        marker = "★" if is_p else " "
        print(f"  {n:4d} | {ntype:>8s} | {depth:>13d} | {bar} {marker}")
    
    print(f"\n  ★ = prime (depth = (n-3)/2, always on the pure-A path)")
    print(f"  The prime depths form a PERFECT linear sequence!")


# ==========================================================================
# 4. The Factoring Race
# ==========================================================================

def factoring_race():
    """Race: factor numbers using Pythagorean triples vs trial division."""
    print("\n" + "=" * 80)
    print("THE FACTORING RACE: Pythagorean vs Trial Division")
    print("=" * 80)
    
    import time
    
    def pyth_factor(n):
        """Factor n using Pythagorean triple method."""
        if n % 2 == 0:
            return 2, n // 2
        n_sq = n * n
        for d in range(3, int(math.isqrt(n_sq)) + 1, 2):
            if n_sq % d == 0:
                e = n_sq // d
                if d < e and d % 2 == e % 2:
                    g = math.gcd(d, n)
                    if 1 < g < n:
                        return g, n // g
        return n, 1
    
    def trial_factor(n):
        """Factor n using trial division."""
        if n % 2 == 0:
            return 2, n // 2
        d = 3
        while d * d <= n:
            if n % d == 0:
                return d, n // d
            d += 2
        return n, 1
    
    test_numbers = [
        15, 77, 143, 221, 323, 1001, 10403, 
        99991 * 99989,  # ~10 billion
    ]
    
    print(f"\n  {'n':>15s} | {'Pyth result':>20s} | {'Pyth time':>12s} | {'Trial time':>12s} | {'speedup':>8s}")
    print("  " + "-" * 75)
    
    for n in test_numbers:
        if n > 10**12:
            print(f"  {n:>15d} | (skipped - too large for this demo)")
            continue
        
        t0 = time.time()
        p1, q1 = pyth_factor(n)
        t_pyth = time.time() - t0
        
        t0 = time.time()
        p2, q2 = trial_factor(n)
        t_trial = time.time() - t0
        
        speedup = t_trial / max(t_pyth, 1e-9) if t_pyth > 0 else "∞"
        if isinstance(speedup, float):
            speedup_str = f"{speedup:.2f}x"
        else:
            speedup_str = speedup
        
        print(f"  {n:>15d} | {p1:>9d} × {q1:<9d} | {t_pyth:>10.6f}s | {t_trial:>10.6f}s | {speedup_str:>8s}")
    
    print(f"\n  Both methods are O(√n) — the Pythagorean method iterates over divisors of n²")
    print(f"  while trial division iterates over potential factors up to √n.")
    print(f"  The geometric insight doesn't help with speed, but illuminates WHY factoring works.")


# ==========================================================================
# 5. The Triple Counter
# ==========================================================================

def triple_counter():
    """Visualize how |T(n)| grows with the complexity of n."""
    print("\n" + "=" * 80)
    print("THE TRIPLE COUNTER: How Factoring Complexity Grows")
    print("=" * 80)
    
    print("\n  Number of Pythagorean triples |T(n)| for different types of n:")
    print(f"\n  {'n':>6s} | {'factorization':>18s} | {'|T(n)|':>7s} | {'histogram':>40s}")
    print("  " + "-" * 75)
    
    interesting = [
        3, 5, 7, 9, 15, 21, 25, 27, 35, 45, 63, 75, 
        105, 135, 189, 225, 315, 945,  # highly composite odd numbers
    ]
    
    max_bar = 35
    
    for n in interesting:
        factors = factorize(n)
        exp = Counter(factors)
        exp_str = "×".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(exp.items()))
        
        sigma0_n2 = 1
        for p, a in exp.items():
            sigma0_n2 *= (2*a + 1)
        t_n = (sigma0_n2 - 1) // 2
        
        bar_len = min(t_n, max_bar)
        bar = "█" * bar_len + (f"→{t_n}" if t_n > max_bar else "")
        
        print(f"  {n:5d} | {exp_str:>18s} | {t_n:7d} | {bar}")
    
    print(f"\n  Formula: |T(n)| = (∏(2aᵢ+1) - 1) / 2 for n = ∏pᵢ^aᵢ")
    print(f"  Each prime factor MULTIPLIES the number of triples!")
    print(f"  945 = 3³×5×7 has {(7*3*3-1)//2} triples — rich factoring information")


# ==========================================================================
# 6. The Gaussian Integer Gallery
# ==========================================================================

def gaussian_gallery():
    """Visualize primitive triples as Gaussian integer squares."""
    print("\n" + "=" * 80)
    print("THE GAUSSIAN INTEGER GALLERY: z² = Pythagorean Triple")
    print("=" * 80)
    
    print("""
    Each dot below represents a Gaussian integer z = m + ni
    whose square z² gives a primitive Pythagorean triple.
    
    The position shows (m, n) on the integer lattice:
    """)
    
    # Create a grid
    size = 14
    grid = [[' ' for _ in range(size + 1)] for _ in range(size + 1)]
    
    # Mark valid Gaussian integers
    for m in range(1, size + 1):
        for n_p in range(0, m):
            if math.gcd(m, n_p) == 1 and (m - n_p) % 2 == 1:
                if n_p <= size:
                    grid[size - n_p][m] = '●'
    
    # Print grid
    print(f"  n")
    for row_idx, row in enumerate(grid):
        n_val = size - row_idx
        if n_val >= 0:
            print(f"  {n_val:2d} {''.join(row)}")
    print(f"     {''.join(f'{i:1d}' if i < 10 else ' ' for i in range(size + 1))}  m")
    print(f"     {''.join(' ' if i < 10 else f'{i//10}' for i in range(size + 1))}")
    
    print(f"\n  Each ● at position (m,n) gives the primitive triple:")
    print(f"  (m²−n², 2mn, m²+n²)")
    print(f"  Conditions: gcd(m,n) = 1, m−n odd, m > n ≥ 0")
    
    # Show some examples
    print(f"\n  Examples:")
    for m in range(2, 8):
        for n_p in range(1, m):
            if math.gcd(m, n_p) == 1 and (m - n_p) % 2 == 1:
                a = m*m - n_p*n_p
                b = 2*m*n_p
                c = m*m + n_p*n_p
                print(f"    z = {m}+{n_p}i → z² = {a}+{b}i → triple ({a},{b},{c})")


# ==========================================================================
# MAIN
# ==========================================================================

if __name__ == "__main__":
    print("╔" + "═" * 78 + "╗")
    print("║  PYTHAGOREAN FACTORING: VISUAL EXPLORER                                     ║")
    print("╚" + "═" * 78 + "╝")
    
    if len(sys.argv) > 1 and sys.argv[1] == "tree":
        depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        draw_tree(depth)
    elif len(sys.argv) > 1 and sys.argv[1] == "radar":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 105
        factoring_radar(n)
    elif len(sys.argv) > 1 and sys.argv[1] == "race":
        factoring_race()
    else:
        # Run everything
        draw_tree(2)
        
        for n in [15, 77, 105]:
            factoring_radar(n)
        
        depth_landscape()
        triple_counter()
        gaussian_gallery()
        factoring_race()
        
        print("\n" + "=" * 80)
        print("VISUAL EXPLORATION COMPLETE")
        print("=" * 80)
        print("\nUsage:")
        print("  python3 10_visual_explorer.py              # Run all visualizations")
        print("  python3 10_visual_explorer.py tree [depth]  # Show Berggren tree")
        print("  python3 10_visual_explorer.py radar [n]     # Factoring radar for n")
        print("  python3 10_visual_explorer.py race          # Factoring race")
