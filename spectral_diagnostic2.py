#!/usr/bin/env python3
"""Spectral diagnostic v2: memory-efficient. Only BFS for p=101, periods + mixed walk for larger."""

MATRICES = [
    ((2, -1), (1, 0)),   # M0
    ((2, 1), (1, 0)),    # M1
    ((1, 2), (0, 1)),    # M2
    ((1, 0), (2, 1)),    # M3
    ((0, 1), (1, 2)),    # M4
    ((-1, 2), (0, 1)),   # M5
    ((1, -2), (0, 1)),   # M6
    ((0, 1), (-1, 2)),   # M7
    ((2, -1), (0, 1)),   # M8
]

def apply_mat(mat, m, n, p):
    (a, b), (c, d) = mat
    return (a * m + b * n) % p, (c * m + d * n) % p

def orbit_bfs(p):
    """BFS orbit size — only for small p."""
    visited = set()
    queue = [(2 % p, 1 % p)]
    visited.add(queue[0])
    while queue:
        nxt = []
        for m, n in queue:
            for mat in MATRICES:
                s = apply_mat(mat, m, n, p)
                if s not in visited:
                    visited.add(s)
                    nxt.append(s)
        queue = nxt
    return len(visited)

def single_period(mi, p, max_steps):
    """Period of (2,1) under matrix mi mod p."""
    mat = MATRICES[mi]
    m0, n0 = 2 % p, 1 % p
    m, n = apply_mat(mat, m0, n0, p)
    for s in range(1, max_steps):
        if (m, n) == (m0, n0):
            return s + 1  # +1 because we started from step 1
        m, n = apply_mat(mat, m, n, p)
    return -1

def mixed_walk_cycle(p, max_steps):
    """State-dependent matrix walk cycle length via Brent's algorithm."""
    def step(m, n):
        idx = ((m * 2654435761) ^ (n * 40503)) % 9
        return apply_mat(MATRICES[idx], m, n, p)
    
    # Brent's cycle detection
    power = lam = 1
    tort_m, tort_n = 2 % p, 1 % p
    hare_m, hare_n = step(tort_m, tort_n)
    
    while (tort_m, tort_n) != (hare_m, hare_n):
        if power == lam:
            tort_m, tort_n = hare_m, hare_n
            power *= 2
            lam = 0
        hare_m, hare_n = step(hare_m, hare_n)
        lam += 1
        if lam > max_steps:
            return -1, -1
    
    # Find mu (start of cycle)
    tort_m, tort_n = 2 % p, 1 % p
    hare_m, hare_n = 2 % p, 1 % p
    for _ in range(lam):
        hare_m, hare_n = step(hare_m, hare_n)
    mu = 0
    while (tort_m, tort_n) != (hare_m, hare_n):
        tort_m, tort_n = step(tort_m, tort_n)
        hare_m, hare_n = step(hare_m, hare_n)
        mu += 1
    return lam, mu

print("=" * 70)
print("SPECTRAL DIAGNOSTIC v2")
print("=" * 70)

# BFS only for p=101
p = 101
orbit = orbit_bfs(p)
print(f"\np={p}: BFS orbit = {orbit}  (p²={p*p}, ratio={orbit/(p*p):.4f})")

# Single-matrix periods for several primes
print("\n--- Single-matrix periods ---")
for p in [101, 1009, 10007, 100003]:
    print(f"\np={p}:  p-1={p-1}  p+1={p+1}  p²-1={p*p-1}")
    for mi in range(9):
        per = single_period(mi, p, min(2_000_000, p*p))
        if per > 0:
            divs = []
            if (p-1) % per == 0: divs.append(f"| p-1")
            if (p+1) % per == 0: divs.append(f"| p+1")
            if (p*p-1) % per == 0: divs.append(f"| p²-1")
            print(f"  M{mi}: {per:>10d}  {'  '.join(divs)}")
        else:
            print(f"  M{mi}: > {min(2_000_000, p*p)}")

# Mixed walk (Pollard-rho style) cycle detection
print(f"\n{'='*70}")
print("MIXED WALK cycle detection (Brent's algorithm)")
print("=" * 70)
for p in [101, 1009, 10007, 100003, 1000003]:
    lam, mu = mixed_walk_cycle(p, min(5_000_000, 10*p))
    ratio = lam / p if lam > 0 else -1
    print(f"  p={p:>8d}: lambda={lam:>10d}  mu={mu:>8d}  lambda/p={ratio:.3f}")

# Key test: does mixed walk achieve O(p) cycle length?
# If lambda ~ p, then rho cycle detection gives O(sqrt(p)) factor detection
print(f"\n{'='*70}")
print("CRITICAL: Birthday collision estimate")
print("=" * 70)
print("If lambda ~ O(p), Pollard-rho gives O(sqrt(lambda)) = O(sqrt(p)) detection")
print("For balanced 64b semiprime, p~2^32: sqrt(p)~65K steps = INSTANT at 50M steps/s")
print("For balanced 96b semiprime, p~2^48: sqrt(p)~16M steps = 0.3s at 50M steps/s")
