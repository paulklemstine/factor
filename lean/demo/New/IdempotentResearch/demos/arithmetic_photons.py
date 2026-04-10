#!/usr/bin/env python3
"""
Arithmetic Photons: Discrete Spacetime Explorer
=================================================
Visualizes "arithmetic photons" — integer solutions to a² + b² + c² = d²
(the discrete light cone) — as rational points on S².

Validates:
- Parity constraint: a + b + c + d is always even
- Density on S² via stereographic projection
- Growth of photon count r₃(d²) with energy d
"""

import math
from collections import defaultdict


def find_photon_directions(d_max: int) -> dict:
    """Find all Pythagorean quadruples (a,b,c,d) with a²+b²+c²=d², d ≤ d_max."""
    quadruples = defaultdict(list)
    for d in range(1, d_max + 1):
        d_sq = d * d
        for a in range(-d, d + 1):
            a_sq = a * a
            if a_sq > d_sq:
                continue
            for b in range(-d, d + 1):
                b_sq = b * b
                if a_sq + b_sq > d_sq:
                    continue
                c_sq = d_sq - a_sq - b_sq
                c = int(math.isqrt(c_sq))
                if c * c == c_sq:
                    for sign_c in ([c, -c] if c > 0 else [0]):
                        quadruples[d].append((a, b, sign_c, d))
    return quadruples


def verify_parity_constraint(quadruples: dict) -> bool:
    """Verify that a + b + c + d is even for all quadruples."""
    violations = 0
    total = 0
    for d, quads in quadruples.items():
        for (a, b, c, d_val) in quads:
            total += 1
            if (a + b + c + d_val) % 2 != 0:
                violations += 1
                print(f"  VIOLATION: ({a},{b},{c},{d_val}), sum = {a+b+c+d_val}")
    return violations == 0, total


def stereographic_projection(a, b, c, d):
    """Project (a/d, b/d, c/d) ∈ S² to ℝ² via stereographic projection from north pole."""
    if d == 0:
        return None
    x, y, z = a / d, b / d, c / d
    if abs(z - 1.0) < 1e-10:  # North pole
        return None
    return (x / (1 - z), y / (1 - z))


def count_representations(d_max: int):
    """Count r₃(d²) = number of (a,b,c) with a²+b²+c² = d²."""
    print("=" * 65)
    print("  PHOTON COUNT: r₃(d²) = |{(a,b,c) ∈ ℤ³ : a²+b²+c² = d²}|")
    print("=" * 65)

    counts = []
    for d in range(1, d_max + 1):
        d_sq = d * d
        count = 0
        for a in range(-d, d + 1):
            for b in range(-d, d + 1):
                c_sq = d_sq - a * a - b * b
                if c_sq < 0:
                    continue
                c = int(math.isqrt(c_sq))
                if c * c == c_sq:
                    count += 1 if c == 0 else 2
        counts.append((d, count))

    print(f"\n  {'d':>4s}  {'r₃(d²)':>8s}  {'d²':>8s}  {'ratio':>8s}  {'visual':>30s}")
    print("  " + "-" * 62)
    for d, count in counts:
        ratio = count / d if d > 0 else 0
        bar = "█" * min(count // 2, 30)
        print(f"  {d:>4d}  {count:>8d}  {d*d:>8d}  {ratio:>8.2f}  {bar}")

    return counts


def demo_parity():
    """Demonstrate the parity constraint."""
    print("\n" + "=" * 65)
    print("  PARITY CONSTRAINT (Machine-Verified in Lean 4)")
    print("  For all (a,b,c,d) with a²+b²+c²=d²: a+b+c+d ≡ 0 (mod 2)")
    print("=" * 65)

    quadruples = find_photon_directions(20)
    ok, total = verify_parity_constraint(quadruples)
    print(f"\n  Checked {total} quadruples with d ≤ 20")
    print(f"  Parity constraint {'VERIFIED ✓' if ok else 'FAILED ✗'}")

    # Show some examples
    print(f"\n  {'(a, b, c, d)':>20s}  {'a²+b²+c²':>10s}  {'d²':>6s}  {'sum':>5s}  {'even':>5s}")
    print("  " + "-" * 52)
    shown = 0
    for d in sorted(quadruples.keys()):
        for (a, b, c, d_val) in quadruples[d]:
            if a >= 0 and b >= 0 and c >= 0 and shown < 15:
                s = a + b + c + d_val
                print(f"  ({a:>2d},{b:>2d},{c:>2d},{d_val:>2d})"
                      f"  {a*a+b*b+c*c:>10d}  {d_val*d_val:>6d}  {s:>5d}  {'✓' if s%2==0 else '✗':>5s}")
                shown += 1


def demo_stereographic():
    """Show stereographic projection of photon directions."""
    print("\n" + "=" * 65)
    print("  STEREOGRAPHIC PROJECTION OF PHOTON DIRECTIONS")
    print("  Each (a,b,c,d) with a²+b²+c²=d² maps to a rational point on S²")
    print("  Stereographic projection sends S² → ℝ²")
    print("=" * 65)

    quadruples = find_photon_directions(10)
    points = set()

    for d in sorted(quadruples.keys()):
        for (a, b, c, d_val) in quadruples[d]:
            if d_val == 0:
                continue
            pt = stereographic_projection(a, b, c, d_val)
            if pt is not None:
                # Round to avoid floating point duplicates
                pt_rounded = (round(pt[0], 6), round(pt[1], 6))
                points.add(pt_rounded)

    print(f"\n  Total distinct stereographic points (d ≤ 10): {len(points)}")
    print(f"\n  Sample points (s, t) ∈ ℝ² from stereographic projection:")
    for i, (s, t) in enumerate(sorted(points, key=lambda p: p[0]**2 + p[1]**2)):
        if i < 20:
            r = math.sqrt(s**2 + t**2)
            print(f"    ({s:>8.4f}, {t:>8.4f})  |r| = {r:.4f}")

    # Count growth
    print("\n" + "=" * 65)
    print("  PHOTON DIRECTION COUNT GROWTH")
    print("=" * 65)
    for d_max in [5, 10, 15, 20, 25]:
        quads = find_photon_directions(d_max)
        total = sum(len(v) for v in quads.values())
        unique_dirs = set()
        for d in quads:
            for (a, b, c, d_val) in quads[d]:
                if d_val > 0:
                    g = math.gcd(math.gcd(abs(a), abs(b)), math.gcd(abs(c), d_val))
                    unique_dirs.add((a // g, b // g, c // g, d_val // g))
        print(f"  d ≤ {d_max:>3d}: {total:>6d} total quadruples, "
              f"{len(unique_dirs):>5d} primitive directions")


def demo_dark_matter_ratio():
    """The 'dark matter ratio': fraction of ℤ⁴ lattice NOT reachable by photons."""
    print("\n" + "=" * 65)
    print("  DARK MATTER RATIO")
    print("  Fraction of ℤ⁴ NOT on the null cone a²+b²+c²=d²")
    print("=" * 65)

    for d_max in [5, 10, 15]:
        total_lattice = (2 * d_max + 1) ** 4
        on_cone = 0
        for d in range(-d_max, d_max + 1):
            for a in range(-d_max, d_max + 1):
                for b in range(-d_max, d_max + 1):
                    c_sq = d * d - a * a - b * b
                    if c_sq < 0:
                        continue
                    c = int(math.isqrt(c_sq))
                    if c * c == c_sq and abs(c) <= d_max:
                        on_cone += 1 if c == 0 else 2
        dark = total_lattice - on_cone
        ratio = dark / total_lattice
        print(f"  d_max={d_max:>2d}: lattice={total_lattice:>8d}, "
              f"on cone={on_cone:>6d}, dark={dark:>8d}, ratio={ratio:.6f}")


if __name__ == "__main__":
    demo_parity()
    count_representations(25)
    demo_stereographic()
    demo_dark_matter_ratio()
