#!/usr/bin/env python3
"""
Demo: Strange Loops and Self-Reference
=========================================

Interactive demonstrations of strange loops, Gödel's incompleteness,
the bootstrap paradox, and self-referential structures.
"""

import itertools

def demo_mu_puzzle():
    """The MU Puzzle from GEB: can you get from MI to MU?"""
    print("=" * 60)
    print("Demo: The MU Puzzle (from Gödel, Escher, Bach)")
    print("=" * 60)
    print()
    print("Start: MI")
    print("Rules:")
    print("  1. If string ends in I, add U (xI → xIU)")
    print("  2. If string is Mx, you can get Mxx")
    print("  3. If string contains III, replace with U")
    print("  4. If string contains UU, drop it")
    print()

    # BFS from MI
    start = "MI"
    visited = {start}
    queue = [start]
    target = "MU"

    for depth in range(8):
        next_queue = []
        for s in queue:
            # Rule 1: xI → xIU
            if s.endswith("I"):
                new = s + "U"
                if new not in visited and len(new) <= 30:
                    visited.add(new)
                    next_queue.append(new)

            # Rule 2: Mx → Mxx
            if s.startswith("M"):
                suffix = s[1:]
                new = "M" + suffix + suffix
                if new not in visited and len(new) <= 30:
                    visited.add(new)
                    next_queue.append(new)

            # Rule 3: xIIIy → xUy
            for i in range(len(s) - 2):
                if s[i:i+3] == "III":
                    new = s[:i] + "U" + s[i+3:]
                    if new not in visited:
                        visited.add(new)
                        next_queue.append(new)

            # Rule 4: xUUy → xy
            for i in range(len(s) - 1):
                if s[i:i+2] == "UU":
                    new = s[:i] + s[i+2:]
                    if new not in visited:
                        visited.add(new)
                        next_queue.append(new)

        queue = next_queue
        print(f"  Depth {depth + 1}: {len(visited)} strings explored, {len(queue)} new")
        if target in visited:
            print(f"  Found {target}!")
            break

    if target not in visited:
        print(f"\n  MU not reachable! (I count mod 3 is invariant)")
        print(f"  MI has 1 I (≡ 1 mod 3)")
        print(f"  MU has 0 I's (≡ 0 mod 3)")
        print(f"  Rules preserve I-count mod 3, so MU is unreachable.")
        print(f"  This is a STRANGE LOOP: the system cannot reach its 'goal'")
        print(f"  because of an invariant invisible from inside.")
    print()

def demo_godel_sentence():
    """Simulate Gödel's self-referential sentence."""
    print("=" * 60)
    print("Demo: Gödel's Self-Referential Sentence")
    print("=" * 60)
    print()

    # Simple formal system: theorems are strings derivable from axioms
    axioms = {"A", "A→B", "B→C"}
    theorems = set(axioms)

    # Derive new theorems by modus ponens
    for _ in range(5):
        new = set()
        for t in theorems:
            if "→" in t:
                parts = t.split("→")
                if parts[0] in theorems:
                    new.add(parts[1])
        theorems |= new

    print(f"Axioms: {axioms}")
    print(f"Theorems: {theorems}")
    print()

    # The Gödel sentence: "This sentence is not a theorem"
    print("Gödel sentence G: 'G is not a theorem of this system'")
    print()
    print("If G is a theorem:")
    print("  → By soundness, G is true")
    print("  → 'G is not a theorem' is true")
    print("  → G is NOT a theorem  ← CONTRADICTION!")
    print()
    print("If G is NOT a theorem:")
    print("  → 'G is not a theorem' is true")
    print("  → G is TRUE but UNPROVABLE")
    print()
    print("Conclusion: G is true but unprovable — a STRANGE LOOP")
    print("between truth and provability!")
    print()

def demo_quine():
    """Demonstrate a Quine (self-reproducing program)."""
    print("=" * 60)
    print("Demo: Quine (Self-Reproducing Program)")
    print("=" * 60)
    print()

    # A Python quine
    quine = 's = %r; print(s %% s)\n'
    print("A Quine is a program that outputs its own source code.")
    print("This is the programming analog of a fixed point of representation.")
    print()
    print(f"Quine template: s = %r; print(s %% s)")
    print()

    # Demonstrate the fixed-point property
    data = "HELLO"
    reflect = lambda x: x  # Identity = simplest Quine
    print(f"  Simple Quine (identity): reflect('{data}') = '{reflect(data)}'")
    print(f"  Is fixed point? {reflect(data) == data}")
    print()

    # More complex: a transform with a fixed point
    def complex_reflect(s):
        """Transform that has 'SELF' as a fixed point."""
        if s == "SELF":
            return "SELF"
        return "SELF"  # Everything maps to SELF eventually

    for test in ["START", "HELLO", "SELF", "WORLD"]:
        r = complex_reflect(test)
        rr = complex_reflect(r)
        print(f"  reflect('{test}') = '{r}', reflect²('{test}') = '{rr}'")
        print(f"  Fixed point reached? {r == rr}")
    print()

def demo_bootstrap_paradox():
    """The Bootstrap Paradox: periodic self-creation."""
    print("=" * 60)
    print("Demo: The Bootstrap Paradox (Periodic Timeline)")
    print("=" * 60)
    print()

    period = 5
    # Timeline: state at each time step
    states = ["A", "B", "C", "D", "E"]
    evolve = {"A": "B", "B": "C", "C": "D", "D": "E", "E": "A"}

    print(f"Period: {period}")
    print(f"Evolution: {evolve}")
    print()
    print("Timeline (wrapping around):")

    state = "A"
    for t in range(15):
        loop_marker = " ← NEW CYCLE" if t > 0 and t % period == 0 else ""
        print(f"  t={t:2d}: State {state}{loop_marker}")
        state = evolve[state]

    print()
    print("Each state 'creates' the next, and the last creates the first.")
    print("No external creator — the loop bootstraps itself!")
    print(f"Theorem: timeline(t + k*{period}) = timeline(t) for all k")
    print()

def demo_tangled_hierarchy():
    """Demonstrate a tangled hierarchy with multiple interlocking loops."""
    print("=" * 60)
    print("Demo: Tangled Hierarchy (Multiple Interlocking Loops)")
    print("=" * 60)
    print()

    n = 4
    # Two loops on 4 levels
    loop1 = [1, 2, 3, 0]  # Cycle: 0→1→2→3→0
    loop2 = [2, 3, 0, 1]  # Cycle: 0→2→0, 1→3→1

    print(f"Loop 1 (rotation):  {list(range(n))} → {loop1}")
    print(f"Loop 2 (swap pairs): {list(range(n))} → {loop2}")
    print()

    # Compose loops
    composed = [loop2[loop1[i]] for i in range(n)]
    print(f"Loop1 ∘ Loop2: {list(range(n))} → {composed}")

    # Find period of composition
    current = list(range(n))
    for period in range(1, 20):
        current = [composed[i] for i in current]
        if current == list(range(n)):
            print(f"Composition period: {period}")
            print(f"The loops are ENTANGLED — their composition creates a new loop!")
            break
    print()

    # Visualize the tangling
    print("Tangling pattern:")
    level = 0
    for step in range(12):
        loop_choice = step % 2
        next_level = loop1[level] if loop_choice == 0 else loop2[level]
        arrow = "→" if loop_choice == 0 else "⇒"
        print(f"  Step {step:2d}: Level {level} {arrow} Level {next_level} (Loop {loop_choice + 1})")
        level = next_level
    print()

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  STRANGE LOOPS AND SELF-REFERENCE — DEMOS              ║")
    print("╚" + "═" * 58 + "╝")
    print()

    demo_mu_puzzle()
    demo_godel_sentence()
    demo_quine()
    demo_bootstrap_paradox()
    demo_tangled_hierarchy()

    print("=" * 60)
    print("All demos complete.")
    print("=" * 60)
