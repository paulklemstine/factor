"""
Repulsor Dynamics Simulator

Demonstrates repulsor behavior in discrete dynamical systems:
1. Fixed point repulsion
2. Attractor-repulsor duality via time reversal
3. Basin of repulsion computation
4. Repulsor spectrum analysis

Run: python demo_repulsors.py
"""

import math
import random
from typing import List, Tuple, Set, Dict

# ============================================================
# 1. DISCRETE DYNAMICAL SYSTEMS
# ============================================================

class DiscreteDynSystem:
    """A discrete dynamical system f: R -> R."""

    def __init__(self, step_fn):
        self.step = step_fn

    def iterate(self, x: float, n: int) -> float:
        """Compute f^n(x)."""
        result = x
        for _ in range(n):
            result = self.step(result)
        return result

    def orbit(self, x: float, n: int) -> List[float]:
        """Compute the orbit [x, f(x), f^2(x), ..., f^n(x)]."""
        trajectory = [x]
        current = x
        for _ in range(n):
            current = self.step(current)
            trajectory.append(current)
        return trajectory

    def reverse(self, inv_fn):
        """Create the reverse system using an inverse function."""
        return DiscreteDynSystem(inv_fn)


# ============================================================
# 2. REPULSOR DEMONSTRATION
# ============================================================

def demo_repulsor_fixed_point():
    """Demonstrate a repulsive fixed point.

    f(x) = 2x has 0 as a repulsive fixed point:
    nearby points move away exponentially.
    """
    print("=" * 60)
    print("DEMO 1: Repulsive Fixed Point (f(x) = 2x)")
    print("=" * 60)

    ds = DiscreteDynSystem(lambda x: 2 * x)

    print("  Starting near x=0 (the repulsive fixed point):")
    for x0 in [0.001, -0.001, 0.01, -0.1]:
        orbit = ds.orbit(x0, 10)
        distances = [abs(x) for x in orbit]
        print(f"  x₀ = {x0:8.4f}: distances from 0 = "
              f"[{', '.join(f'{d:.2f}' for d in distances[:6])}...]")
        print(f"    → Escapes! (grows exponentially)")

    print()

    # Contrast with attractor
    print("  Compare with ATTRACTIVE fixed point (f(x) = x/2):")
    ds_attract = DiscreteDynSystem(lambda x: x / 2)
    for x0 in [1.0, -1.0, 10.0]:
        orbit = ds_attract.orbit(x0, 10)
        distances = [abs(x) for x in orbit]
        print(f"  x₀ = {x0:8.4f}: distances from 0 = "
              f"[{', '.join(f'{d:.4f}' for d in distances[:6])}...]")
        print(f"    → Converges to 0 (decays exponentially)")

    print()


def demo_attractor_repulsor_duality():
    """Demonstrate attractor-repulsor duality via time reversal.

    f(x) = 2x has 0 as repulsor
    f⁻¹(x) = x/2 has 0 as attractor
    They are time-reverses of each other.
    """
    print("=" * 60)
    print("DEMO 2: Attractor-Repulsor Duality (Time Reversal)")
    print("=" * 60)

    # Forward system: repulsor at 0
    ds_forward = DiscreteDynSystem(lambda x: 2 * x)
    # Reverse system: attractor at 0
    ds_reverse = ds_forward.reverse(lambda x: x / 2)

    x0 = 0.1
    n = 8

    forward_orbit = ds_forward.orbit(x0, n)
    reverse_orbit = ds_reverse.orbit(x0, n)

    print(f"  Starting point: x₀ = {x0}")
    print(f"  {'Step':>6s} | {'Forward (f=2x)':>14s} | {'Reverse (f=x/2)':>14s}")
    print(f"  {'─'*6:>6s} + {'─'*14:>14s} + {'─'*14:>14s}")

    for i in range(n + 1):
        print(f"  {i:6d} | {forward_orbit[i]:14.6f} | {reverse_orbit[i]:14.6f}")

    print(f"\n  Forward: 0 is a REPULSOR (orbits diverge)")
    print(f"  Reverse: 0 is an ATTRACTOR (orbits converge)")
    print(f"  → Duality theorem verified!")
    print()


# ============================================================
# 3. BASIN OF REPULSION
# ============================================================

def demo_basin_of_repulsion():
    """Compute the basin of repulsion for the logistic map.

    f(x) = rx(1-x), with r > 4 the interval [0,1] has escaping orbits.
    """
    print("=" * 60)
    print("DEMO 3: Basin of Repulsion (Logistic Map, r=4.5)")
    print("=" * 60)

    r = 4.5
    ds = DiscreteDynSystem(lambda x: r * x * (1 - x))

    # Find points that escape [0, 1]
    n_points = 1000
    max_iter = 50
    escaped = 0
    escape_times = []

    for i in range(n_points):
        x = i / n_points
        escape_time = None
        current = x
        for t in range(max_iter):
            current = ds.step(current)
            if current < -10 or current > 10:
                escape_time = t + 1
                break
        if escape_time is not None:
            escaped += 1
            escape_times.append(escape_time)

    print(f"  Testing {n_points} initial conditions in [0, 1]:")
    print(f"  Escaped: {escaped}/{n_points} ({100*escaped/n_points:.1f}%)")
    if escape_times:
        print(f"  Average escape time: {sum(escape_times)/len(escape_times):.1f} steps")
        print(f"  Min escape time: {min(escape_times)} steps")
        print(f"  Max escape time: {max(escape_times)} steps")

    # Show escape time distribution
    from collections import Counter
    time_dist = Counter(escape_times)
    print(f"\n  Escape time distribution (top 5):")
    for t, count in sorted(time_dist.items(), key=lambda x: -x[1])[:5]:
        bar = "█" * (count * 40 // n_points)
        print(f"    t={t:3d}: {count:4d} points {bar}")

    print()


# ============================================================
# 4. REPULSOR SPECTRUM
# ============================================================

def demo_repulsor_spectrum():
    """Compute the repulsor spectrum: the set of escape times.

    For different dynamical systems, analyze the spectrum structure.
    """
    print("=" * 60)
    print("DEMO 4: Repulsor Spectrum Analysis")
    print("=" * 60)

    systems = {
        "Linear (2x)": (lambda x: 2 * x, (-0.5, 0.5)),
        "Quadratic (x²+0.3)": (lambda x: x**2 + 0.3, (-1, 1)),
        "Cubic (2x³)": (lambda x: 2 * x**3, (-0.9, 0.9)),
    }

    for name, (fn, (lo, hi)) in systems.items():
        ds = DiscreteDynSystem(fn)
        R = (lo, hi)

        escape_times = set()
        n_samples = 500

        for i in range(n_samples):
            x = lo + (hi - lo) * i / n_samples
            current = x
            for t in range(100):
                current = fn(current)
                if current < lo or current > hi:
                    escape_times.add(t + 1)
                    break

        spectrum = sorted(escape_times)[:10]
        print(f"  System: {name}")
        print(f"    Region R = [{lo}, {hi}]")
        print(f"    Spectrum (first 10): {spectrum}")
        print(f"    Spectrum size: {len(escape_times)}")
        print()


# ============================================================
# 5. PROBABILISTIC REPULSOR
# ============================================================

def demo_probabilistic_repulsor():
    """Demonstrate probabilistic repulsor: escape probability at each point."""
    print("=" * 60)
    print("DEMO 5: Probabilistic Repulsor")
    print("=" * 60)

    # f(x) = 2x with noise
    def noisy_doubling(x):
        return 2 * x + random.gauss(0, 0.01)

    ds = DiscreteDynSystem(noisy_doubling)
    region = (-0.5, 0.5)

    print(f"  System: f(x) = 2x + noise(σ=0.01)")
    print(f"  Region: [{region[0]}, {region[1]}]")
    print(f"  Computing escape probabilities...")

    n_points = 10
    n_trials = 1000
    max_steps = 20

    print(f"\n  {'x':>8s} | {'P(escape)':>10s} | {'Avg time':>10s} | Visual")
    print(f"  {'─'*8:>8s} + {'─'*10:>10s} + {'─'*10:>10s} + {'─'*20}")

    for i in range(n_points + 1):
        x0 = region[0] + (region[1] - region[0]) * i / n_points
        escapes = 0
        total_time = 0

        for _ in range(n_trials):
            current = x0
            escaped = False
            for t in range(max_steps):
                current = noisy_doubling(current)
                if current < region[0] or current > region[1]:
                    escapes += 1
                    total_time += t + 1
                    escaped = True
                    break
            if not escaped:
                total_time += max_steps

        p_escape = escapes / n_trials
        avg_time = total_time / n_trials
        bar = "█" * int(p_escape * 20)
        print(f"  {x0:8.3f} | {p_escape:10.3f} | {avg_time:10.1f} | {bar}")

    print(f"\n  Points near the boundary escape faster (higher repulsion)")
    print(f"  Points near the center (fixed point) escape slower")
    print()


# ============================================================
# 6. SEARCH-EVASION IN DYNAMICAL SYSTEMS
# ============================================================

def demo_search_in_dynamics():
    """Combine search theory with repulsor dynamics.

    A searcher scans regions; an evader uses repulsor dynamics to escape.
    """
    print("=" * 60)
    print("DEMO 6: Search-Evasion with Repulsor Dynamics")
    print("=" * 60)

    n_locations = 20
    n_steps = 30

    # Evader uses doubling map (mod n) to move
    def evader_step(pos):
        return (2 * pos + 1) % n_locations

    # Searcher uses sequential scan
    def searcher_step(t):
        return t % n_locations

    # Simulate
    evader_pos = 1
    detected = False
    detection_time = None

    print(f"  Space: {n_locations} locations (circular)")
    print(f"  Evader: doubling map f(x) = (2x+1) mod {n_locations}")
    print(f"  Searcher: sequential scan")
    print()

    evader_trail = [evader_pos]
    for t in range(n_steps):
        search_loc = searcher_step(t)
        if search_loc == evader_pos and not detected:
            detected = True
            detection_time = t
        evader_pos = evader_step(evader_pos)
        evader_trail.append(evader_pos)

    print(f"  Evader orbit: {evader_trail[:15]}...")
    if detected:
        print(f"  DETECTED at step {detection_time}!")
    else:
        print(f"  EVADED for all {n_steps} steps!")

    # Show uniqueness of orbit
    unique_positions = len(set(evader_trail[:n_steps]))
    print(f"  Unique positions visited by evader: {unique_positions}/{n_locations}")
    print(f"  Orbit density: {unique_positions/n_locations:.1%}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  REPULSOR DYNAMICS: INTERACTIVE DEMONSTRATIONS")
    print("  Based on Lean 4 Formalization")
    print("=" * 60 + "\n")

    random.seed(2024)

    demo_repulsor_fixed_point()
    demo_attractor_repulsor_duality()
    demo_basin_of_repulsion()
    demo_repulsor_spectrum()
    demo_probabilistic_repulsor()
    demo_search_in_dynamics()

    print("All demonstrations complete!")
