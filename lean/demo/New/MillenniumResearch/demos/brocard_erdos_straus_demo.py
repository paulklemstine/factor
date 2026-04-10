#!/usr/bin/env python3
"""
Brocard's Problem and Erdos-Straus Conjecture Demo

Demonstrates computational verification of these number-theoretic conjectures,
corresponding to the formally verified results in Foundations.lean.
"""

import math


def is_perfect_square(n):
    """Check if n is a perfect square."""
    if n < 0:
        return False, 0
    s = int(math.isqrt(n))
    if s * s == n:
        return True, s
    return False, 0


def brocard_search(max_n=100):
    """Search for Brocard solutions: n! + 1 = m^2."""
    print("=" * 60)
    print("BROCARD'S PROBLEM: n! + 1 = m^2")
    print("(Formally verified solutions in Lean: brocard_4/5/7)")
    print("=" * 60)

    solutions = []
    print(f"\n  Searching n = 1 to {max_n}...\n")
    print(f"  {'n':>4s}  {'n!':>15s}  {'n!+1':>15s}  {'sqrt(n!+1)':>12s}  {'Solution?':>10s}")
    print("  " + "-" * 62)

    for n in range(1, max_n + 1):
        fact = math.factorial(n)
        val = fact + 1
        is_sq, m = is_perfect_square(val)

        if is_sq:
            solutions.append((n, m))
            print(f"  {n:4d}  {fact:15d}  {val:15d}  {m:12d}  {'*** YES ***':>10s}")
        elif n <= 10:
            sqrt_approx = math.isqrt(val)
            print(f"  {n:4d}  {fact:15d}  {val:15d}  ~{sqrt_approx:<11d}  {'no':>10s}")

    print(f"\n  Solutions found: {solutions}")
    print(f"  These match the formally verified results:")
    print(f"    brocard_4: 4! + 1 = 24 + 1 = 25 = 5^2  [verified in Lean]")
    print(f"    brocard_5: 5! + 1 = 120 + 1 = 121 = 11^2  [verified in Lean]")
    print(f"    brocard_7: 7! + 1 = 5040 + 1 = 5041 = 71^2  [verified in Lean]")
    print(f"\n  It is conjectured that no other solutions exist.")
    print(f"  This has been verified computationally up to n = 10^9.")


def erdos_straus_decomposition(n):
    """Find a decomposition 4/n = 1/x + 1/y + 1/z with x <= y <= z.
    Returns (x, y, z) or None."""
    if n <= 0:
        return None

    # Try all reasonable x values
    # 4/n = 1/x + 1/y + 1/z, so x >= n/4 (roughly)
    # and x <= n (since 1/x >= 1/n and we need three terms summing to 4/n)
    for x in range(1, 3 * n + 1):
        # Remaining: 4/n - 1/x = (4x - n) / (nx)
        num = 4 * x - n
        if num <= 0:
            continue
        den = n * x
        # Need 1/y + 1/z = num/den with y <= z
        # So y ranges from ceil(den/num) ... (since 1/y >= num/(2*den))
        # 1/y + 1/z = num/den => z = den*y / (num*y - den)
        for y in range(max(1, den // num), 2 * den // num + 2):
            numer_z = den * y
            denom_z = num * y - den
            if denom_z <= 0:
                continue
            if numer_z % denom_z == 0:
                z = numer_z // denom_z
                if y <= z:
                    # Verify: 4*x*y*z == n*(y*z + x*z + x*y)
                    if 4 * x * y * z == n * (y * z + x * z + x * y):
                        return (x, y, z)
    return None


def erdos_straus_demo(max_n=100):
    """Demonstrate the Erdos-Straus conjecture for small n."""
    print("\n" + "=" * 60)
    print("ERDOS-STRAUS CONJECTURE: 4/n = 1/x + 1/y + 1/z")
    print("(Formally verified cases in Lean: erdos_straus_2/3/5/7)")
    print("=" * 60)

    print(f"\n  Searching for decompositions for n = 2 to {max_n}...\n")
    print(f"  {'n':>4s}  {'x':>6s}  {'y':>6s}  {'z':>8s}  {'Verification':>15s}")
    print("  " + "-" * 45)

    failures = []
    for n in range(2, max_n + 1):
        result = erdos_straus_decomposition(n)
        if result is None:
            failures.append(n)
            if n <= 20:
                print(f"  {n:4d}  {'???':>6s}  {'???':>6s}  {'???':>8s}  {'NOT FOUND':>15s}")
        elif n <= 20 or n in [2, 3, 5, 7]:
            x, y, z = result
            # Verify
            lhs = 4 / n
            rhs = 1/x + 1/y + 1/z
            ok = abs(lhs - rhs) < 1e-10
            status = "OK" if ok else "FAIL"
            print(f"  {n:4d}  {x:6d}  {y:6d}  {z:8d}  {status:>15s}")

    if failures:
        print(f"\n  Failed for n = {failures}")
    else:
        print(f"\n  All n from 2 to {max_n} have decompositions!")

    print(f"\n  Formally verified in Lean:")
    print(f"    erdos_straus_2: 4/2 = 1/1 + 1/2 + 1/2")
    print(f"    erdos_straus_3: 4/3 = 1/1 + 1/4 + 1/12")
    print(f"    erdos_straus_5: 4/5 = 1/2 + 1/4 + 1/20")
    print(f"    erdos_straus_7: 4/7 = 1/2 + 1/15 + 1/210")


def main():
    print("=" * 60)
    print("  BROCARD & ERDOS-STRAUS DEMO")
    print("  Companion to formally verified results in Lean 4")
    print("=" * 60)

    brocard_search(30)
    erdos_straus_demo(100)


if __name__ == "__main__":
    main()
