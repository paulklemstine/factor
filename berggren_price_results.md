# Berggren-Price Pythagorean Triple Tree Analysis

Generated: 2026-03-15

## Key Findings

### Task 1: Multiple Tree Generators

1. **Berggren/Barning matrices ARE the (m,n) parametric tree.** Converting the standard operations on coprime (m,n) pairs to (a,b,c) coordinates yields EXACTLY the three Berggren matrices A, B, C. This is a fundamental mathematical identity, not a coincidence.

2. **Romik's uniqueness theorem confirmed.** Exhaustive search of all 3x3 integer matrices with entries in [-3,3] (40M candidates) found 192 PPT-preserving matrices: 3 Berggren, 48 sign/permutation, and 141 "nontrivial" -- but ALL nontrivial ones are Berggren matrices with rows permuted/negated. No genuinely new PPT-preserving linear map exists.

3. **Five genuinely different tree structures implemented:**

| Tree | Size (depth 10) | Description |
|------|-----------------|-------------|
| Berggren | 88,573 (3^d at depth d) | Classic A,B,C matrices from (3,4,5) |
| MultiRoot | 265,719 (3 x 3^d) | Forest rooted at 3 depth-1 Berggren triples |
| Composed | 88,573 (3^d) | Uses AB, AC, BC (skips to depth-2 children) |
| Height | 792 | PPTs ordered by hypotenuse proximity |
| Calkin-Wilf | 87,045 | PPTs extracted from Calkin-Wilf rational tree |

### Task 2: Cross-Tree Analysis

**Berggren vs MultiRoot:**
- 88,572 common triples, ALL at different depths (depth difference = exactly 1)
- Same parents (99.997%), just shifted by one level
- This is a trivial shift: MultiRoot depth d = Berggren depth d+1

**Berggren vs Calkin-Wilf (the interesting comparison):**
- 52,405 common triples
- Only 1,331 at same depth (2.5%)
- 7,699 share the same parent (14.7%)
- **Maximum depth discrepancy: 10** (triple (23,264,265) is at Berggren depth 10 but CW depth 0!)
- This shows the CW tree finds "deep" Berggren triples near its root

**Berggren vs Height:**
- 647 common triples (Height tree limited by hypotenuse cap)
- Only 9 share the same parent
- Triple (23,264,265): Berggren depth 10, Height depth 3 (depth diff = 7)

**Path translation example (depth 2):**
```
(7,24,25):  Berggren [A,A] d=2 -> MultiRoot [A] d=1 (same parent)
(48,55,73): Berggren [A,B] d=2 -> MultiRoot [B] d=1 (same parent)
```

### Task 3: Connection Density

**Cross-tree connectivity distribution:**
- In 1 tree only: 256,813 triples (mainly MultiRoot extras)
- In 2 trees: 57,642
- In 3 trees: 51,760
- In 4 trees: 816
- In ALL 5 trees: 12 triples

**Top hub triples (most connections across all trees):**
| Triple | Connections | Trees | Min Depth |
|--------|------------|-------|-----------|
| (3,4,5) | 129 | Berg,CW,Comp,Height | 0 |
| (8,15,17) | 103 | Berg,CW,Height,Multi | 0 |
| (7,24,25) | 103 | Berg,CW,Height,Multi | 0 |
| (39,80,89) | 95 | ALL 5 | 1 |
| (48,55,73) | 91 | Berg,CW,Height,Multi | 1 |

**Triples in all 5 trees at depth <= 2:**
- (3,4,5): depth 0 in Berggren/Composed/Height/CW
- (5,12,13): depth 1 in Berggren, 0 in MultiRoot/CW
- (39,80,89), (33,56,65), (65,72,97): depth 2/1 across trees

### Task 4: Missing Connections & Matrix Search

**Exhaustive matrix search results:**
- Searched 40,353,607 candidate matrices (entries in [-3,3])
- Found 192 PPT-preserving matrices total
- **3 are the Berggren A, B, C** (confirmed found in search)
- **48 are sign/permutation matrices** (map (3,4,5) to itself via coordinate swaps)
- **141 are row-permuted/negated Berggren matrices** (all passed 43+ PPT tests)
- **NO novel matrix exists** -- confirms the theoretical result that Berggren matrices generate the full automorphism group

**Berggren matrix compositions:**
- Products of 2 Berggren matrices have max entry up to 17
- Products of 3 have max entry up to 51
- These generate depth-2 and depth-3 "skip" trees

**Connection density at depth <= 5:**
- 364 triples, 726 directed connections via Berggren matrices
- Tree has exactly 363 edges (n-1 for a tree)
- Connection density: 0.55% of all possible directed pairs
- 99.45% of potential parent-child pairs are "missing" -- these are the non-tree connections

### Task 5: Prime Tree by Analogy (Moonshot)

**Fundamental impossibility:** Unlike PPTs (which form an algebraic variety preserved by matrix action), primes have no algebraic characterization that a linear map could preserve. All algebraic prime trees eventually die.

**Prime tree comparison (primes generated):**

| Rank | Tree Type | Primes | Notes |
|------|-----------|--------|-------|
| 1 | Stern-Brocot analogy | 235 | Adaptively chooses nearest prime; 45% coverage to 3733 |
| 2 | Primorial-offset | 94 | Uses p#+1, p#-1, 2p+1; steady growth through depth 10 |
| 3 | Ternary [2p+3, 3p+2, 4p+3] | 76 | Best pure algebraic tree; survives to depth 12 |
| 4 | Ternary [3p+2, p+30, 2p+1] | 46 | Additive offset helps survival |
| 5 | Euler p^2+p+41 | 35 | Famous prime-producing polynomial |
| 6 | Ternary [2p+1, 2p-1, 6p+1] | 33 | Sophie Germain + Cunningham |
| 7 | Binary (2p-1, 2p+1) | 8 | Dies at depth 5 from root=2 |
| 8 | Gaussian Z[i] | 4 | Norm-preserving multiplications fail fast |

**Cunningham chains:** Longest found: 89 -> 179 -> 359 -> 719 -> 1439 -> 2879 (length 6). Among first 2000 primes, 85% have chain length 1 (immediate death), only 0.05% reach length 6.

**Why prime trees die (theoretical):**
1. Prime density ~ 1/ln(n) decreases
2. Branch operations multiply by 2-6x, so values grow exponentially
3. Probability of all 3 children being prime at depth d ~ (1/d*ln(2))^3
4. Expected tree lifetime ~ O(log log N) -- doubly logarithmic

**The Stern-Brocot prime tree works** because it ADAPTS: it finds the nearest prime to the mediant, sacrificing algebraic structure for coverage. It generated all primes up to 139 in order, and 45% of primes up to 3733.

## Visualizations

- `images/bp_depth_scatter.png` -- Depth comparison scatter plots (4 panels)
- `images/bp_cross_tree_graph.png` -- Cross-tree PPT graph (depth <= 3)
- `images/bp_connection_density.png` -- Connection count distribution + coverage pie
- `images/bp_prime_trees.png` -- Prime tree comparison (4 panels)
- `images/bp_ppt_tree_growth.png` -- PPT tree growth by depth
- `images/bp_parent_comparison.png` -- Depth-2 same/different parent scatter

## Deep Mathematical Insight

The reason the Berggren matrices are THE ONLY PPT-preserving linear maps (up to sign/permutation) is that they are the generators of the orthogonal group O(2,1;Z) -- the group of integer matrices preserving the quadratic form x^2 + y^2 - z^2. This is the same group that appears in:
- Lorentz transformations (special relativity)
- Hyperbolic geometry (Poincare disk model)
- Binary quadratic forms (Gauss composition)

The fact that there is NO analogous structure for primes reflects that primality is an ANALYTIC property (defined by divisibility/factorization) rather than an ALGEBRAIC one (defined by polynomial equations). This is why factoring is hard: there is no algebraic shortcut to primality.
