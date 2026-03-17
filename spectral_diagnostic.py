#!/usr/bin/env python3
"""Spectral gap diagnostic: enumerate orbit sizes of (2,1) under Pythagorean matrices mod small primes."""

# The 9 forward Berggren/Price/Firstov matrices on (m,n):
# Each is [[a,b],[c,d]] meaning (m',n') = (a*m+b*n, c*m+d*n)
MATRICES = [
    ((2, -1), (1, 0)),   # M0: Berggren U1
    ((2, 1), (1, 0)),    # M1: Berggren U2  
    ((1, 2), (0, 1)),    # M2: Berggren U3
    ((1, 0), (2, 1)),    # M3: Price
    ((0, 1), (1, 2)),    # M4: Price
    ((-1, 2), (0, 1)),   # M5: Firstov (needs 2n>m)
    ((1, -2), (0, 1)),   # M6: Firstov (needs m>2n)
    ((0, 1), (-1, 2)),   # M7: Firstov (needs 2n>m)
    ((2, -1), (0, 1)),   # M8: correction
]

def apply_mat(mat, m, n, p):
    """Apply matrix to (m,n) mod p."""
    (a, b), (c, d) = mat
    return (a * m + b * n) % p, (c * m + d * n) % p

def orbit_size_bfs(p):
    """BFS from (2,1) using all 9 matrices mod p. Return orbit size."""
    visited = set()
    queue = [(2 % p, 1 % p)]
    visited.add((2 % p, 1 % p))
    while queue:
        next_q = []
        for m, n in queue:
            for mat in MATRICES:
                m2, n2 = apply_mat(mat, m, n, p)
                if (m2, n2) not in visited:
                    visited.add((m2, n2))
                    next_q.append((m2, n2))
        queue = next_q
    return len(visited)

def orbit_size_single_matrix(mat_idx, p, max_steps=None):
    """Iterate single matrix from (2,1) mod p, return orbit period."""
    mat = MATRICES[mat_idx]
    if max_steps is None:
        max_steps = p * p + 10
    m0, n0 = 2 % p, 1 % p
    m, n = apply_mat(mat, m0, n0, p)
    steps = 1
    while (m, n) != (m0, n0) and steps < max_steps:
        m, n = apply_mat(mat, m, n, p)
        steps += 1
    if (m, n) == (m0, n0):
        return steps
    return -1  # didn't cycle

print("=" * 70)
print("SPECTRAL DIAGNOSTIC: Orbit sizes of (2,1) under Pythagorean matrices")
print("=" * 70)

# Test small primes
for p in [101, 1009, 10007]:
    orbit = orbit_size_bfs(p)
    print(f"\np = {p}:  orbit size (all 9 matrices BFS) = {orbit}  (p² = {p*p}, ratio = {orbit/(p*p):.4f})")
    
    # Single matrix orbits
    for mi in range(9):
        period = orbit_size_single_matrix(mi, p)
        print(f"  M{mi} period: {period:>8d}  (p-1={p-1}, p+1={p+1}, p²-1={p*p-1})")

# For 100003, BFS would be too slow (10^10 states), just do single-matrix periods
p = 100003
print(f"\np = {p}:  (BFS too slow, single-matrix periods only)")
print(f"  p-1 = {p-1},  p+1 = {p+1},  p²-1 = {p*p-1}")
for mi in range(9):
    period = orbit_size_single_matrix(mi, p, max_steps=2*p*p)
    pstr = f"{period:>12d}" if period > 0 else "   > 2p²"
    # Check divisibility
    divs = []
    if period > 0:
        if (p-1) % period == 0: divs.append("divides p-1")
        elif (p+1) % period == 0: divs.append("divides p+1")
        elif (p*p-1) % period == 0: divs.append("divides p²-1")
        elif period % (p-1) == 0: divs.append(f"= {period//(p-1)}*(p-1)")
        elif period % (p+1) == 0: divs.append(f"= {period//(p+1)}*(p+1)")
    print(f"  M{mi} period: {pstr}  {'  '.join(divs)}")

# Mixed walk: state-dependent matrix selection (Pollard-rho style)  
print(f"\n{'='*70}")
print("MIXED WALK (state-dependent matrix): orbit sizes")
print("=" * 70)

def mixed_walk_orbit(p, max_steps=None):
    """Walk where matrix choice depends on state: idx = (m*7 + n*13) % 9"""
    if max_steps is None:
        max_steps = 3 * p + 10
    m0, n0 = 2 % p, 1 % p
    m, n = m0, n0
    visited = set()
    visited.add((m, n))
    for step in range(1, max_steps):
        idx = (m * 7 + n * 13) % 9
        m, n = apply_mat(MATRICES[idx], m, n, p)
        if (m, n) in visited:
            return step, len(visited)
        visited.add((m, n))
    return -1, len(visited)

for p in [101, 1009, 10007, 100003]:
    cycle_at, unique = mixed_walk_orbit(p, max_steps=min(3*p, 500000))
    print(f"  p={p:>6d}: cycle detected at step {cycle_at:>8d}, unique states = {unique:>8d}, ratio unique/p = {unique/p:.3f}")
