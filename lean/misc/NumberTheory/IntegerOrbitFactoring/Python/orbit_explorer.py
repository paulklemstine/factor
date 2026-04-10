#!/usr/bin/env python3
"""
Integer Orbit Factoring — Interactive Orbit Explorer

An interactive tool for exploring orbit structures of polynomial maps
over modular arithmetic. Supports:
- Custom polynomials f(x) = x^d + c mod n
- Orbit tracing and cycle detection
- Factor extraction via GCD
- Comparative orbit analysis across factor components
- Orbit graph export

Run: python3 orbit_explorer.py
"""

import math
from typing import List, Tuple, Dict, Set

# ═══════════════════════════════════════════════════════════════════════════════
# Orbit Graph Construction
# ═══════════════════════════════════════════════════════════════════════════════

def build_functional_graph(f, n: int) -> Dict[int, int]:
    """Build the complete functional graph of f on ℤ/nℤ."""
    return {x: f(x) % n for x in range(n)}

def find_all_cycles(graph: Dict[int, int]) -> List[List[int]]:
    """Find all cycles in the functional graph."""
    visited = set()
    cycles = []
    
    for start in graph:
        if start in visited:
            continue
        
        # Follow the chain until we hit a visited node or revisit current chain
        path = []
        path_set = set()
        x = start
        
        while x not in visited and x not in path_set:
            path.append(x)
            path_set.add(x)
            x = graph[x]
        
        if x in path_set and x not in visited:
            # Found a new cycle
            cycle_start = path.index(x)
            cycle = path[cycle_start:]
            cycles.append(cycle)
        
        visited.update(path_set)
    
    return cycles

def compute_tree_sizes(graph: Dict[int, int], cycles: List[List[int]]) -> Dict[int, int]:
    """Compute the size of the tree rooted at each cycle node."""
    cycle_nodes = set()
    for cycle in cycles:
        cycle_nodes.update(cycle)
    
    # Reverse graph
    reverse = {x: [] for x in graph}
    for x, y in graph.items():
        reverse[y].append(x)
    
    # BFS from cycle nodes
    tree_sizes = {}
    for node in cycle_nodes:
        size = 0
        stack = [node]
        visited = {node}
        while stack:
            current = stack.pop()
            size += 1
            for pred in reverse[current]:
                if pred not in visited and pred not in cycle_nodes:
                    visited.add(pred)
                    stack.append(pred)
        tree_sizes[node] = size
    
    return tree_sizes

def analyze_functional_graph(n: int, c: int = 1, degree: int = 2):
    """Complete analysis of the functional graph f(x) = x^d + c mod n."""
    f = lambda x: (pow(x, degree, n) + c) % n
    graph = build_functional_graph(f, n)
    cycles = find_all_cycles(graph)
    
    print(f"\n{'='*60}")
    print(f"Functional Graph Analysis")
    print(f"f(x) = x^{degree} + {c} mod {n}")
    print(f"{'='*60}")
    
    print(f"\n  Total nodes: {n}")
    print(f"  Number of cycles: {len(cycles)}")
    
    total_cycle_nodes = sum(len(c) for c in cycles)
    print(f"  Total cycle nodes: {total_cycle_nodes}")
    print(f"  Total tail nodes: {n - total_cycle_nodes}")
    
    for i, cycle in enumerate(cycles):
        print(f"\n  Cycle {i+1} (length {len(cycle)}):")
        if len(cycle) <= 20:
            print(f"    {' → '.join(str(x) for x in cycle)} ↩")
        else:
            print(f"    {' → '.join(str(x) for x in cycle[:10])} → ... ({len(cycle) - 10} more) ↩")
    
    return graph, cycles

# ═══════════════════════════════════════════════════════════════════════════════
# Comparative Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def compare_orbits_across_factors(n: int, c: int = 1, x0: int = 2):
    """
    Compare the orbit mod n with orbits mod each prime factor.
    Shows how collisions in factor components precede those in n.
    """
    # Simple trial division for small n
    factors = []
    temp = n
    for p in range(2, int(temp**0.5) + 1):
        while temp % p == 0:
            if p not in factors:
                factors.append(p)
            temp //= p
    if temp > 1:
        factors.append(temp)
    
    print(f"\n{'='*60}")
    print(f"Comparative Orbit Analysis")
    print(f"n = {n}, factors: {' × '.join(map(str, factors))}")
    print(f"f(x) = x² + {c}, x₀ = {x0}")
    print(f"{'='*60}")
    
    # Trace orbits
    max_steps = min(n + 1, 200)
    
    # Orbit mod n
    orbit_n = [x0 % n]
    x = x0 % n
    for _ in range(max_steps):
        x = (x * x + c) % n
        orbit_n.append(x)
    
    # Orbits mod each factor
    orbits_p = {}
    for p in factors:
        orbit_p = [x0 % p]
        x = x0 % p
        for _ in range(max_steps):
            x = (x * x + c) % p
            orbit_p.append(x)
        orbits_p[p] = orbit_p
    
    # Find first collision in each
    def first_collision(orbit):
        seen = {}
        for i, v in enumerate(orbit):
            if v in seen:
                return (seen[v], i)
            seen[v] = i
        return None
    
    col_n = first_collision(orbit_n)
    print(f"\n  First collision mod {n}: ", end="")
    if col_n:
        print(f"x_{col_n[0]} = x_{col_n[1]} = {orbit_n[col_n[0]]} (at step {col_n[1]})")
    else:
        print("none found")
    
    for p in factors:
        col_p = first_collision(orbits_p[p])
        print(f"  First collision mod {p}: ", end="")
        if col_p:
            print(f"x_{col_p[0]} = x_{col_p[1]} = {orbits_p[p][col_p[0]]} (at step {col_p[1]})")
            print(f"    √{p} ≈ {p**0.5:.2f}, √(π{p}/2) ≈ {(math.pi*p/2)**0.5:.2f}")
        else:
            print("none found")
    
    # Show parallel orbit values
    print(f"\n  Step-by-step orbit comparison:")
    show_steps = min(25, max_steps)
    header = f"  {'Step':>4} | {'mod '+str(n):>10}"
    for p in factors:
        header += f" | {'mod '+str(p):>8}"
    header += " | GCD info"
    print(header)
    print("  " + "-" * (len(header) - 2))
    
    for i in range(show_steps):
        row = f"  {i:>4} | {orbit_n[i]:>10}"
        for p in factors:
            row += f" | {orbits_p[p][i]:>8}"
        
        # Check if any factor collision just happened
        gcd_info = ""
        if i > 0:
            for p in factors:
                if orbits_p[p][i] == orbits_p[p][0] and i > 1:
                    gcd_info += f" [cycle mod {p}]"
        
        row += f" | {gcd_info}"
        print(row)

# ═══════════════════════════════════════════════════════════════════════════════
# Orbit Density Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def orbit_density_analysis(n: int, num_trials: int = 100):
    """
    Analyze the distribution of orbit points across residue classes.
    Tests the Orbit Density Theorem prediction.
    """
    print(f"\n{'='*60}")
    print(f"Orbit Density Analysis for n = {n}")
    print(f"({num_trials} random orbits)")
    print(f"{'='*60}")
    
    # Count how often each residue class is visited
    visit_counts = [0] * n
    total_visits = 0
    
    import random
    for _ in range(num_trials):
        c = random.randint(1, n - 1)
        x0 = random.randint(0, n - 1)
        
        x = x0
        seen = set()
        while x not in seen:
            seen.add(x)
            visit_counts[x] += 1
            total_visits += 1
            x = (x * x + c) % n
    
    # Display distribution
    expected = total_visits / n
    print(f"\n  Total orbit points sampled: {total_visits}")
    print(f"  Expected count per residue: {expected:.1f}")
    
    counts = sorted(visit_counts)
    print(f"  Min visits: {counts[0]}")
    print(f"  Max visits: {counts[-1]}")
    print(f"  Median visits: {counts[n//2]}")
    
    # Chi-squared test
    chi2 = sum((v - expected)**2 / expected for v in visit_counts if expected > 0)
    print(f"  χ² statistic: {chi2:.1f} (df={n-1})")
    print(f"  χ²/df = {chi2/(n-1):.3f} (≈1 if uniform)")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         INTEGER ORBIT EXPLORER — Interactive Tool           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Exploration 1: Functional graph of small modulus
    analyze_functional_graph(31, c=1, degree=2)
    
    # Exploration 2: Compare orbits across factors
    compare_orbits_across_factors(77, c=1, x0=2)   # 7 × 11
    compare_orbits_across_factors(221, c=1, x0=2)  # 13 × 17
    
    # Exploration 3: Orbit density
    orbit_density_analysis(37, num_trials=500)
    
    print("\n" + "═" * 60)
    print("Exploration complete!")

if __name__ == "__main__":
    main()
