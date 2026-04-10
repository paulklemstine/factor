#!/usr/bin/env python3
"""
Idempotent Proof Complexity Demo

Demonstrates:
1. Idempotent operations and their algebraic properties
2. Resolution proof system and width bounds
3. Connection between idempotency and CSP tractability
4. Absorption property
"""

from math import gcd
from functools import reduce

def lcm(a, b):
    return abs(a * b) // gcd(a, b) if a and b else 0

def demo_idempotent_operations():
    """Demonstrate all idempotent operations from our Lean formalization."""
    print("=" * 60)
    print("IDEMPOTENT OPERATIONS: f(x, x) = x")
    print("=" * 60)

    operations = [
        ("min", min),
        ("max", max),
        ("gcd", gcd),
        ("lcm", lcm),
        ("AND", lambda a, b: a and b),
        ("OR", lambda a, b: a or b),
    ]

    test_values = [
        (3, 3), (7, 7), (12, 12), (1, 1), (0, 0),
    ]

    for name, op in operations:
        print(f"\n  {name}:")
        all_pass = True
        for a, b in test_values:
            if name in ("AND", "OR"):
                a_bool, b_bool = bool(a), bool(b)
                result = op(a_bool, b_bool)
                expected = a_bool
                ok = result == expected
            else:
                result = op(a, b)
                expected = a
                ok = result == expected

            if not ok:
                all_pass = False

        vals = [v[0] for v in test_values[:4]]
        results = [op(v, v) for v in vals] if name not in ("AND", "OR") else [op(bool(v), bool(v)) for v in vals]
        print(f"    {name}(x, x) = x for x ∈ {vals}")
        print(f"    Results: {results}  {'✓ All idempotent!' if all_pass else '✗ FAILED'}")

def demo_non_idempotent():
    """Show operations that are NOT idempotent."""
    print("\n" + "=" * 60)
    print("NON-IDEMPOTENT OPERATIONS: f(x, x) ≠ x")
    print("=" * 60)

    operations = [
        ("addition (+)", lambda a, b: a + b),
        ("multiplication (×)", lambda a, b: a * b),
        ("XOR (⊕)", lambda a, b: a ^ b),
    ]

    for name, op in operations:
        print(f"\n  {name}:")
        for x in [1, 2, 3, 5]:
            result = op(x, x)
            print(f"    {name.split('(')[0].strip()}({x}, {x}) = {result} {'= x ✓' if result == x else '≠ ' + str(x) + ' ✗'}")

    print("\n  These operations can COUNT (1+1=2, 2+2=4, ...)")
    print("  Idempotent operations CANNOT count — this is the key insight!")

def demo_resolution():
    """Demonstrate resolution proof system and width bounds."""
    print("\n" + "=" * 60)
    print("RESOLUTION PROOF SYSTEM")
    print("=" * 60)

    print("\nResolution rule: from (A ∨ x) and (B ∨ ¬x), derive (A ∨ B)")
    print()

    # Example: prove unsatisfiability of (x ∨ y) ∧ (x ∨ ¬y) ∧ (¬x ∨ y) ∧ (¬x ∨ ¬y)

    clauses = [
        ({1, 2}, "x ∨ y"),
        ({1, -2}, "x ∨ ¬y"),
        ({-1, 2}, "¬x ∨ y"),
        ({-1, -2}, "¬x ∨ ¬y"),
    ]

    print("  Clauses:")
    for c, name in clauses:
        print(f"    {name}  (literals: {c})")

    print("\n  Resolution proof:")

    # Resolve clause 0 and 1 on y
    r1 = (clauses[0][0] - {2}) | (clauses[1][0] - {-2})
    print(f"    Step 1: Resolve '{clauses[0][1]}' and '{clauses[1][1]}' on y → {r1} = {{x}}")
    print(f"            Width: |{clauses[0][0]}| + |{clauses[1][0]}| - 1 = {len(clauses[0][0]) + len(clauses[1][0]) - 1}")

    # Resolve clause 2 and 3 on y
    r2 = (clauses[2][0] - {2}) | (clauses[3][0] - {-2})
    print(f"    Step 2: Resolve '{clauses[2][1]}' and '{clauses[3][1]}' on y → {r2} = {{¬x}}")

    # Resolve r1 and r2 on x
    r3 = (r1 - {1}) | (r2 - {-1})
    print(f"    Step 3: Resolve {{x}} and {{¬x}} on x → {r3} = ∅ (contradiction!)")
    print()
    print("  ✓ Formula is UNSATISFIABLE (derived empty clause)")
    print()
    print("  Key property: Resolution is IDEMPOTENT")
    print("  Using a clause twice ≡ using it once (weakening is free)")

def demo_absorption():
    """Demonstrate the absorption property and its relationship to idempotency."""
    print("\n" + "=" * 60)
    print("ABSORPTION PROPERTY: f(x, f(x, y)) = f(x, y)")
    print("=" * 60)

    print("\n  Testing min:")
    for x in [3, 5, 1]:
        for y in [2, 7, 1]:
            inner = min(x, y)
            outer = min(x, inner)
            ok = outer == inner
            print(f"    min({x}, min({x}, {y})) = min({x}, {inner}) = {outer} {'= f(x,y) ✓' if ok else '✗'}")

    print("\n  Testing max:")
    for x in [3, 5, 1]:
        for y in [2, 7, 1]:
            inner = max(x, y)
            outer = max(x, inner)
            ok = outer == inner
            print(f"    max({x}, max({x}, {y})) = max({x}, {inner}) = {outer} {'= f(x,y) ✓' if ok else '✗'}")

    print("\n  Absorption is a WEAKER property than lattice absorption.")
    print("  Our Lean proof showed: absorption + commutativity does NOT imply idempotency!")
    print("  But: absorption DOES imply f(x, f(x,x)) = f(x,x) (self-fixed property)")

def demo_csp_connection():
    """Demonstrate the CSP-idempotency connection."""
    print("\n" + "=" * 60)
    print("CSP AND IDEMPOTENT POLYMORPHISMS")
    print("=" * 60)

    print("\n  The CSP Dichotomy Theorem (Bulatov/Zhuk):")
    print("  Every finite-domain CSP is either in P or NP-complete.")
    print()
    print("  The key: IDEMPOTENT POLYMORPHISMS determine tractability!")
    print()

    # Example: 2-SAT has the polymorphism "majority"
    print("  Example: 2-SAT")
    print("  Polymorphism: majority(x, y, z) = the value appearing ≥ 2 times")

    def majority(x, y, z):
        return 1 if (x + y + z) >= 2 else 0

    print("  Idempotency check: majority(x, x, x) = x?")
    for x in [0, 1]:
        result = majority(x, x, x)
        print(f"    majority({x}, {x}, {x}) = {result} {'✓' if result == x else '✗'}")

    print()
    print("  Because 2-SAT has an idempotent polymorphism (majority),")
    print("  it is solvable in polynomial time!")
    print()
    print("  Compare: 3-SAT has NO such polymorphism → NP-complete")

if __name__ == "__main__":
    demo_idempotent_operations()
    demo_non_idempotent()
    demo_resolution()
    demo_absorption()
    demo_csp_connection()

    print("\n" + "=" * 60)
    print("All idempotent proof complexity demos completed!")
    print("=" * 60)
