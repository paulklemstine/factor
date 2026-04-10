#!/usr/bin/env python3
"""
Berggren-Lorentz Factoring: Hypothesis Testing and Validation

This module systematically tests the hypotheses proposed in the research paper.
Each hypothesis is stated, tested computationally, and a verdict is rendered.
"""

import math
import time
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# Infrastructure
# ─────────────────────────────────────────────────────────────────────────────

def berggren_A(a, b, c): return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)
def berggren_B(a, b, c): return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)
def berggren_C(a, b, c): return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def inv_berggren(a, b, c):
    candidates = [
        ((a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c), 'A'),
        ((a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'B'),
        ((-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'C'),
    ]
    for (pa, pb, pc), name in candidates:
        if pa > 0 and pb > 0 and pc > 0 and pa**2 + pb**2 == pc**2:
            return (pa, pb, pc), name
    a, b = b, a
    for (pa, pb, pc), name in [
        ((a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c), 'A'),
        ((a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'B'),
        ((-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'C'),
    ]:
        if pa > 0 and pb > 0 and pc > 0 and pa**2 + pb**2 == pc**2:
            return (pa, pb, pc), name
    return None, None

def find_depth(a, b, c):
    if a % 2 == 0: a, b = b, a
    depth = 0
    path = []
    while (a, b, c) != (3, 4, 5) and (a, b, c) != (4, 3, 5):
        parent, name = inv_berggren(a, b, c)
        if parent is None:
            a, b = b, a
            parent, name = inv_berggren(a, b, c)
            if parent is None: break
        a, b, c = parent
        path.append(name)
        depth += 1
        if depth > 50000: break
    return depth, path

def euclid_triple(m, n):
    return (m**2 - n**2, 2*m*n, m**2 + n**2)

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 1: B-branch depth is Θ(log c)
# ═══════════════════════════════════════════════════════════════════════════

def test_H1():
    """
    H1: Along pure B-branch paths, depth = Θ(log c).
    Specifically, c_d ≈ (3+2√2)^d, so depth ≈ log(c) / log(3+2√2).
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H1: B-branch depth is Θ(log c)")
    print("═" * 70)

    lambda_B = 3 + 2 * math.sqrt(2)  # ≈ 5.828
    log_lambda = math.log2(lambda_B)   # ≈ 2.543

    current = (3, 4, 5)
    print(f"\nPredicted growth rate: λ_B = {lambda_B:.6f}")
    print(f"log₂(λ_B) = {log_lambda:.6f}")
    print(f"\n{'Depth':>6} {'Hypotenuse':>15} {'log₂(c)':>10} {'d·log₂(λ)':>11} {'Ratio':>8}")

    ratios = []
    for d in range(20):
        c = current[2]
        log_c = math.log2(c) if c > 1 else 0
        predicted = d * log_lambda + math.log2(5)
        ratio = log_c / predicted if predicted > 0 else 0
        ratios.append(ratio)
        if d <= 15:
            print(f"{d:6d} {c:15d} {log_c:10.4f} {predicted:11.4f} {ratio:8.4f}")
        current = berggren_B(*current)

    mean_ratio = sum(ratios[2:]) / len(ratios[2:])
    print(f"\nMean ratio (log₂(c) / predicted): {mean_ratio:.6f}")
    print(f"\n✅ VERDICT: VALIDATED" if abs(mean_ratio - 1.0) < 0.05 else
          f"\n⚠️  VERDICT: PARTIALLY VALIDATED (ratio = {mean_ratio:.4f})")
    return abs(mean_ratio - 1.0) < 0.05


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 2: A-branch depth is Θ(√c)
# ═══════════════════════════════════════════════════════════════════════════

def test_H2():
    """
    H2: Along pure A-branch paths, depth = Θ(√c).
    Specifically, for consecutive params (m, m-1), depth = m-2 and c ≈ 2m².
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H2: A-branch (consecutive params) depth is Θ(√c)")
    print("═" * 70)

    print(f"\n{'m':>6} {'Depth':>7} {'c':>12} {'√c':>10} {'Depth/√c':>10} {'Depth/(m-2)':>12}")

    ratios = []
    for m in range(3, 60):
        n = m - 1
        if math.gcd(m, n) != 1 or (m - n) % 2 == 0:
            continue
        a, b, c = euclid_triple(m, n)
        depth, _ = find_depth(a, b, c)
        sqrt_c = math.sqrt(c)
        ratio_sqrt = depth / sqrt_c if sqrt_c > 0 else 0
        ratio_m = depth / (m - 2) if m > 2 else 0
        ratios.append(ratio_sqrt)

        if m <= 25 or m % 10 == 0:
            print(f"{m:6d} {depth:7d} {c:12d} {sqrt_c:10.2f} {ratio_sqrt:10.4f} {ratio_m:12.4f}")

    mean_ratio = sum(ratios) / len(ratios) if ratios else 0
    print(f"\nMean Depth/√c ratio: {mean_ratio:.6f}")
    print(f"Expected: ≈ 1/√2 = {1/math.sqrt(2):.6f} (since c ≈ 2m² and depth ≈ m)")
    verdict = abs(mean_ratio - 1/math.sqrt(2)) < 0.15
    print(f"\n✅ VERDICT: VALIDATED" if verdict else
          f"\n⚠️  VERDICT: PARTIALLY VALIDATED")
    return verdict


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 3: Depth equals Euclidean algorithm steps (approx)
# ═══════════════════════════════════════════════════════════════════════════

def euclidean_steps(a, b):
    steps = 0
    while b > 0:
        a, b = b, a % b
        steps += 1
    return steps

def test_H3():
    """
    H3: Tree depth ≈ f(Euclidean algorithm steps for (m, n)).
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H3: Depth related to Euclidean algorithm steps")
    print("═" * 70)

    data = []
    for m in range(2, 60):
        for n in range(1, m):
            if math.gcd(m, n) != 1 or (m - n) % 2 == 0:
                continue
            a, b, c = euclid_triple(m, n)
            depth, _ = find_depth(a, b, c)
            euclid_s = euclidean_steps(m, n)
            data.append((m, n, depth, euclid_s))

    print(f"\n{'m':>4} {'n':>4} {'Depth':>7} {'Euclid Steps':>13} {'Ratio':>8}")
    for m, n, d, e in sorted(data, key=lambda x: x[0])[:20]:
        ratio = d / e if e > 0 else 0
        print(f"{m:4d} {n:4d} {d:7d} {e:13d} {ratio:8.4f}")

    # Correlation analysis
    depths = [d for _, _, d, _ in data]
    euclid = [e for _, _, _, e in data]
    n = len(data)
    mean_d = sum(depths) / n
    mean_e = sum(euclid) / n
    cov = sum((d - mean_d) * (e - mean_e) for d, e in zip(depths, euclid)) / n
    std_d = (sum((d - mean_d)**2 for d in depths) / n) ** 0.5
    std_e = (sum((e - mean_e)**2 for e in euclid) / n) ** 0.5
    correlation = cov / (std_d * std_e) if std_d * std_e > 0 else 0

    print(f"\nPearson correlation: {correlation:.6f}")
    print(f"Mean depth: {mean_d:.2f}, Mean Euclid steps: {mean_e:.2f}")
    print(f"Ratio of means: {mean_d/mean_e:.4f}")

    verdict = correlation > 0.7
    print(f"\n✅ VERDICT: {'VALIDATED' if verdict else 'PARTIALLY VALIDATED'} (correlation = {correlation:.4f})")
    return verdict


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 4: All semiprimes factorable via divisor pairs
# ═══════════════════════════════════════════════════════════════════════════

def test_H4():
    """
    H4: For every semiprime N = p·q with p,q odd primes, the non-trivial
    divisor pairs of N² yield triples that reveal p and q via GCD.
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H4: Divisor pairs always reveal factors of semiprimes")
    print("═" * 70)

    primes = [p for p in range(3, 200) if is_prime(p)]
    successes = 0
    failures = 0

    for i in range(len(primes)):
        for j in range(i + 1, len(primes)):
            p, q = primes[i], primes[j]
            N = p * q
            N_sq = N * N

            found = False
            for d in range(1, int(math.isqrt(N_sq)) + 1):
                if N_sq % d == 0:
                    e = N_sq // d
                    if d < e and d % 2 == e % 2:
                        b = (e - d) // 2
                        g = math.gcd(b, N)
                        if 1 < g < N:
                            found = True
                            break
                        g2 = math.gcd(e - d, N)
                        if 1 < g2 < N:
                            found = True
                            break

            if found:
                successes += 1
            else:
                failures += 1
                print(f"  ✗ FAILURE: N = {N} = {p} × {q}")

            if successes + failures >= 200:
                break
        if successes + failures >= 200:
            break

    print(f"\nTested: {successes + failures} semiprimes")
    print(f"Successes: {successes}, Failures: {failures}")
    verdict = failures == 0
    print(f"\n✅ VERDICT: {'VALIDATED' if verdict else 'FAILED'}")
    return verdict


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 5: B-branch recurrence c_{n+1} = 6c_n - c_{n-1}
# ═══════════════════════════════════════════════════════════════════════════

def test_H5():
    """
    H5: The pure B-branch hypotenuses satisfy c_{n+1} = 6c_n - c_{n-1}.
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H5: B-branch recurrence c_{n+1} = 6c_n - c_{n-1}")
    print("═" * 70)

    hyps = [5]
    current = (3, 4, 5)
    for _ in range(20):
        current = berggren_B(*current)
        hyps.append(current[2])

    print(f"\n{'n':>4} {'c_n':>20} {'6c_n - c_{n-1}':>20} {'c_{n+1}':>20} {'Match':>6}")
    all_match = True
    for i in range(1, len(hyps) - 1):
        predicted = 6 * hyps[i] - hyps[i-1]
        actual = hyps[i+1]
        match = predicted == actual
        all_match = all_match and match
        if i <= 12:
            print(f"{i:4d} {hyps[i]:20d} {predicted:20d} {actual:20d} {'✓' if match else '✗':>6}")

    print(f"\n✅ VERDICT: {'VALIDATED' if all_match else 'FAILED'}")
    return all_match


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 6: Lorentz form preservation
# ═══════════════════════════════════════════════════════════════════════════

def test_H6():
    """
    H6: All three Berggren matrices preserve Q(a,b,c) = a² + b² - c².
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H6: Lorentz form preservation Q(a,b,c) = a²+b²-c²")
    print("═" * 70)

    import random
    random.seed(42)

    all_pass = True
    for trial in range(1000):
        a = random.randint(-100, 100)
        b = random.randint(-100, 100)
        c = random.randint(-100, 100)
        Q = a**2 + b**2 - c**2

        for name, fn in [('A', berggren_A), ('B', berggren_B), ('C', berggren_C)]:
            na, nb, nc = fn(a, b, c)
            Q_new = na**2 + nb**2 - nc**2
            if Q != Q_new:
                print(f"  ✗ FAILURE: {name}({a},{b},{c}) → Q={Q} ≠ Q'={Q_new}")
                all_pass = False

    print(f"\n  Tested 1000 random triples × 3 matrices = 3000 cases")
    print(f"\n✅ VERDICT: {'VALIDATED' if all_pass else 'FAILED'}")
    return all_pass


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS 7: Primality detection via unique triple
# ═══════════════════════════════════════════════════════════════════════════

def test_H7():
    """
    H7: An odd prime p has exactly 1 same-parity divisor pair of p²
    (the trivial pair (1, p²)), while composites have more.
    """
    print("\n" + "═" * 70)
    print("HYPOTHESIS H7: Primes have exactly 1 divisor pair, composites > 1")
    print("═" * 70)

    all_pass = True
    for n in range(3, 200, 2):
        n_sq = n * n
        count = 0
        for d in range(1, int(math.isqrt(n_sq)) + 1):
            if n_sq % d == 0:
                e = n_sq // d
                if d < e and d % 2 == e % 2:
                    count += 1

        is_p = is_prime(n)
        expected = 1 if is_p else None  # composites should have > 1

        if is_p and count != 1:
            print(f"  ✗ Prime {n} has {count} pairs (expected 1)")
            all_pass = False
        elif not is_p and count <= 1:
            print(f"  ✗ Composite {n} has only {count} pair(s)")
            all_pass = False

        if n <= 25 or (is_p and n <= 50):
            status = "prime" if is_p else "composite"
            print(f"  n={n:4d} ({status:>9}): {count} divisor pair(s) {'✓' if (is_p and count == 1) or (not is_p and count > 1) else '✗'}")

    print(f"\n✅ VERDICT: {'VALIDATED' if all_pass else 'FAILED'}")
    return all_pass


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   BERGGREN-LORENTZ: SYSTEMATIC HYPOTHESIS TESTING                  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    results = {}
    results['H1'] = test_H1()
    results['H2'] = test_H2()
    results['H3'] = test_H3()
    results['H4'] = test_H4()
    results['H5'] = test_H5()
    results['H6'] = test_H6()
    results['H7'] = test_H7()

    print("\n" + "═" * 70)
    print("SUMMARY OF HYPOTHESIS TESTS")
    print("═" * 70)
    for h, result in results.items():
        status = "✅ VALIDATED" if result else "⚠️  NEEDS REFINEMENT"
        print(f"  {h}: {status}")

    validated = sum(1 for v in results.values() if v)
    print(f"\n  {validated}/{len(results)} hypotheses fully validated")
