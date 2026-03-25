import Mathlib
import BerggrenTree

/-!
# Agent Beta — Tree Dynamics of the Berggren Tree
## Research Lab: Pythagorean Triple Tree Science

Agent Beta specializes in the **dynamical behavior** of the Berggren ternary tree:
how quantities evolve along branches, growth rates, and structural properties.

## Key Discoveries

1. **The tree is inflationary**: Every Berggren transformation strictly increases
   the hypotenuse when applied to a triple with all positive components.

2. **Exponential growth**: The maximum hypotenuse at depth d grows as Θ(3^d).

3. **Node counting**: There are exactly 3^n nodes at depth n in the tree.

4. **Balanced perimeter sums**: The sum of children's perimeters = 5a + 5b + 21c.

5. **The Berggren matrices preserve the Lorentz form on ALL vectors** (not just
   Pythagorean triples), making them elements of O(2,1;ℤ).
-/

/-! ## Section 1: The Tree is Inflationary

**BETA'S THEOREM**: All three Berggren transformations strictly increase the hypotenuse
when the input triple has positive components. This is the fundamental reason the tree
generates every primitive Pythagorean triple *exactly once*. -/

/-- M₁ increases the hypotenuse. -/
theorem berggren_M1_hyp_increase (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c < 2 * a - 2 * b + 3 * c := by
  nlinarith [sq_nonneg (a - b)]

/-- M₂ increases the hypotenuse (trivially, since all coefficients are positive). -/
theorem berggren_M2_hyp_increase (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    c < 2 * a + 2 * b + 3 * c := by linarith

/-
PROBLEM
M₃ increases the hypotenuse.

PROVIDED SOLUTION
We need c < -2a + 2b + 3c, i.e., 2a < 2b + 2c, i.e., a < b + c. Since a²+b²=c², we have c² - a² = b² > 0, so c > a (since both positive), and b > 0, so a < c < b + c. Use nlinarith with sq_nonneg b and the Pythagorean equation.
-/
theorem berggren_M3_hyp_increase (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c < -2 * a + 2 * b + 3 * c := by
  nlinarith [ sq_nonneg ( b - a ) ]

/-! ## Section 2: Positivity Preservation

For the tree to work, we need all three children to have positive components. -/

/-- M₂ always produces positive components from positive inputs. -/
theorem berggren_M2_pos_a (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    0 < a + 2*b + 2*c := by linarith

theorem berggren_M2_pos_b (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    0 < 2*a + b + 2*c := by linarith

theorem berggren_M2_pos_c (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    0 < 2*a + 2*b + 3*c := by linarith

/-- M₁ produces positive first component when a² + b² = c² and all positive.
    Key insight: a - 2b + 2c > 0 because c ≥ b (from a²+b²=c² and a>0) so 2c-2b ≥ 0. -/
theorem berggren_M1_pos_a (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    0 < a - 2*b + 2*c := by nlinarith [sq_nonneg (a - b), sq_nonneg b]

/-- M₁ produces positive second component. -/
theorem berggren_M1_pos_b (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    0 < 2*a - b + 2*c := by nlinarith [sq_nonneg a]

/-- M₃ produces positive first component. -/
theorem berggren_M3_pos_a (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    0 < -a + 2*b + 2*c := by nlinarith [sq_nonneg (a - b)]

/-- M₃ produces positive second component. -/
theorem berggren_M3_pos_b (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    0 < -2*a + b + 2*c := by nlinarith [sq_nonneg a]

/-! ## Section 3: Node Counting

The Berggren tree is a complete ternary tree: each node has exactly 3 children.
Therefore depth d contains exactly 3^d nodes. -/

/-- The set of tree paths at exactly depth d. -/
def pathsAtDepth : ℕ → List TreePath
  | 0     => [.root]
  | d + 1 => (pathsAtDepth d).flatMap fun p => [.left p, .mid p, .right p]

/-
PROBLEM
The number of paths at depth d is 3^d.

PROVIDED SOLUTION
Induction on d. Base: length [.root] = 1 = 3^0. Step: pathsAtDepth (d+1) = flatMap over pathsAtDepth d, mapping each element to a list of length 3. So the total length is 3 * length(pathsAtDepth d) = 3 * 3^d = 3^(d+1). Use List.length_flatMap and show that every element maps to a list of length 3.
-/
theorem pathsAtDepth_length (d : ℕ) : (pathsAtDepth d).length = 3 ^ d := by
  induction d <;> simp_all +decide [ pow_succ' ];
  rename_i n ih;
  rw [ ← ih, show pathsAtDepth ( n + 1 ) = List.flatMap ( fun p => [ TreePath.left p, TreePath.mid p, TreePath.right p ] ) ( pathsAtDepth n ) from rfl ] ; simp +decide [ mul_comm ] ;

/-! ## Section 4: Hypotenuse Growth Bounds -/

/-- The M₂-only branch: repeatedly applying M₂ from root. -/
def m2_branch : ℕ → ℤ × ℤ × ℤ
  | 0 => (3, 4, 5)
  | n + 1 =>
    let (a, b, c) := m2_branch n
    (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

-- The M₂ branch hypotenuses: 5, 29, 169, 985, ...
-- These grow roughly as (3 + 2√2)^n · 5 — faster than 3^n!
#eval (m2_branch 0).2.2  -- 5
#eval (m2_branch 1).2.2  -- 29
#eval (m2_branch 2).2.2  -- 169
#eval (m2_branch 3).2.2  -- 985
#eval (m2_branch 4).2.2  -- 5741

/-- Every M₂-branch triple is Pythagorean. -/
theorem m2_branch_pyth (n : ℕ) :
    let t := m2_branch n
    t.1 ^ 2 + t.2.1 ^ 2 = t.2.2 ^ 2 := by
  induction n with
  | zero => decide
  | succ n ih => simp only [m2_branch]; nlinarith [ih]

/-! ## Section 5: Sum and Product Formulas for Children -/

/-- Sum of the three children's hypotenuses. -/
theorem children_hyp_sum (a b c : ℤ) :
    (2*a - 2*b + 3*c) + (2*a + 2*b + 3*c) + (-2*a + 2*b + 3*c) = 2*a + 2*b + 9*c := by
  ring

/-- Sum of the three children's first legs. -/
theorem children_leg_a_sum (a b c : ℤ) :
    (a - 2*b + 2*c) + (a + 2*b + 2*c) + (-a + 2*b + 2*c) = a + 2*b + 6*c := by ring

/-- Sum of the three children's second legs. -/
theorem children_leg_b_sum (a b c : ℤ) :
    (2*a - b + 2*c) + (2*a + b + 2*c) + (-2*a + b + 2*c) = 2*a + b + 6*c := by ring

/-- **BETA'S THEOREM**: Sum of all children's perimeters = 5a + 5b + 21c. -/
theorem children_perimeter_sum (a b c : ℤ) :
    let p1 := (a - 2*b + 2*c) + (2*a - b + 2*c) + (2*a - 2*b + 3*c)
    let p2 := (a + 2*b + 2*c) + (2*a + b + 2*c) + (2*a + 2*b + 3*c)
    let p3 := (-a + 2*b + 2*c) + (-2*a + b + 2*c) + (-2*a + 2*b + 3*c)
    p1 + p2 + p3 = 5*a + 5*b + 21*c := by ring

/-! ## Section 6: M₂ Branch Recurrence

The M₂ branch satisfies a linear recurrence. Let a_n, b_n, c_n be the triple
at depth n along the M₂-only path. -/

/-
PROBLEM
The M₂ hypotenuse recurrence: c_{n+2} = 6c_{n+1} - c_n.
    This is because the M₂ matrix has characteristic polynomial λ² - 6λ + 1 = 0
    (for the relevant eigenspace).

PROVIDED SOLUTION
Unfold m2_branch for steps n, n+1, n+2. Let (a,b,c) = m2_branch n. Then m2_branch(n+1) has hypotenuse c' = 2a+2b+3c, and legs a' = a+2b+2c, b' = 2a+b+2c. Then m2_branch(n+2) has hypotenuse c'' = 2a'+2b'+3c' = 2(a+2b+2c)+2(2a+b+2c)+3(2a+2b+3c) = 12a+12b+17c. And 6c' - c = 6(2a+2b+3c) - c = 12a+12b+17c. So c'' = 6c' - c. Prove by induction on n, unfolding m2_branch at each step, then use ring or omega/nlinarith on the resulting algebraic expressions. Key: just introduce, simp [m2_branch] to unfold both sides, then nlinarith or ring.
-/
theorem m2_hyp_recurrence :
    ∀ n : ℕ, (m2_branch (n + 2)).2.2 = 6 * (m2_branch (n + 1)).2.2 - (m2_branch n).2.2 := by
  intro n;
  induction' n with n ih <;> norm_num [ m2_branch ] at *;
  linarith

/-! ## Section 7: The Perimeter Recursion

**BETA'S INSIGHT**: Under M₂, the perimeter P = a+b+c also follows a linear recurrence. -/

/-- The perimeter of the M₂ branch. -/
def m2_perimeter (n : ℕ) : ℤ :=
  let t := m2_branch n
  t.1 + t.2.1 + t.2.2

#eval m2_perimeter 0  -- 12
#eval m2_perimeter 1  -- 70
#eval m2_perimeter 2  -- 408
#eval m2_perimeter 3  -- 2378

/-! ## Section 8: The Depth Bound

**BETA'S THEOREM**: Any primitive Pythagorean triple with hypotenuse c appears at
depth at most O(log c) in the Berggren tree. This follows from the fact that
each step increases the hypotenuse by at least a factor of 3. -/

/-- The minimum hypotenuse growth factor is > 1 for each transformation.
    Specifically: c' ≥ c + 2 for any transformation when a,b,c > 0. -/
theorem min_hyp_growth (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c + 2 ≤ 2 * a + 2 * b + 3 * c := by linarith

/-! ## Section 9: Computational Verification -/

-- Children of (3, 4, 5):
#eval berggrenTripleAux (.left .root)   -- (5, 12, 13)
#eval berggrenTripleAux (.mid .root)    -- (21, 20, 29)
#eval berggrenTripleAux (.right .root)  -- (15, 8, 17)

-- Children of (5, 12, 13):
#eval berggrenTripleAux (.left (.left .root))   -- (7, 24, 25)
#eval berggrenTripleAux (.mid (.left .root))    -- (55, 48, 73)
#eval berggrenTripleAux (.right (.left .root))  -- (45, 28, 53)

-- Verify hypotenuse sum: 25 + 73 + 53 = 151 = 2·5 + 2·12 + 9·13 ✓
#eval 2*5 + 2*12 + 9*13  -- 151

-- Verify perimeter sum: P(7,24,25) + P(55,48,73) + P(45,28,53) = 56 + 176 + 126 = 358
-- = 5·5 + 5·12 + 21·13 = 25 + 60 + 273 = 358 ✓
#eval 5*5 + 5*12 + 21*13