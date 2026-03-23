import Mathlib

/-!
# IOF as a Dynamical System: New Theorems

This file explores the IOF algorithm through the lens of dynamical systems theory,
formalizing novel connections between factorization, energy landscapes, and
convergence theory.

## Main Results

- Phase space characterization of the descent
- Attractor basin theorem: all composites with factor p converge to the same attractor
- Information-theoretic bound on factor revelation
- Connection to continued fractions
-/

open Nat

namespace IOFDynamical

/-! ## Phase Space Structure -/

/-- The state of the IOF system at step k, represented as a point in ℤ³.
    The trajectory lies on the Pythagorean cone a² + b² = c². -/
structure IOFState where
  a : ℤ
  b : ℤ
  c : ℤ

/-- Construct the IOF state at step k. -/
def state (N : ℤ) (k : ℕ) : IOFState where
  a := N - 2 * k
  b := ((N - 2 * k) ^ 2 - 1) / 2
  c := ((N - 2 * k) ^ 2 + 1) / 2

/-! ## Attractor Basin Theorem -/

/-
PROBLEM
All semiprimes with the same smaller factor p reach the same "factor state"
    at the same step k = (p-1)/2, regardless of the larger factor q.
    The odd leg at the factor step depends only on q: a = p(q-1) + 1.
    But the step number (p-1)/2 depends only on p.
    This means p defines a "basin of attraction" in the descent.

PROVIDED SOLUTION
Unfold state. The a-component at step k = (p-1)/2 is p*q_i - 2*((p-1)/2) = p*q_i - (p-1). Modulo p: p*q_i - (p-1) ≡ 0 - (-1) ≡ 1 (mod p). So both residues are 1, hence equal. Use Int.emod_emod_of_dvd or direct computation with push_cast and omega.
-/
theorem same_factor_same_step (p q₁ q₂ : ℕ) (hp : Nat.Prime p) (hp2 : 2 < p)
    (hq₁ : Nat.Prime q₁) (hq₂ : Nat.Prime q₂)
    (hle₁ : p ≤ q₁) (hle₂ : p ≤ q₂) :
    let k := (p - 1) / 2
    (state (↑(p * q₁)) k).a % ↑p = (state (↑(p * q₂)) k).a % ↑p := by
      unfold state; norm_num [ mul_comm p, Int.add_emod, Int.sub_emod, Int.mul_emod ] ;

/-! ## Energy Landscape Topology -/

/-
PROBLEM
The energy landscape E(k) = (N - 2k)² is a parabola opening upward
with vertex at k = N/2. The descent traverses the left branch from
k = 0 toward the vertex.

The energy at the factor step, in terms of p and q.

PROVIDED SOLUTION
It suffices to show N - 2*k = N - p + 1. Since p is odd (p % 2 = 1), p = 2m+1 for some m. Then (p-1)/2 = m, so 2*((p-1)/2) = 2m = p-1. Therefore N - 2*k = N - (p-1) = N - p + 1. Use congr_arg (· ^ 2) on this. Use omega after establishing 2*((p-1)/2) = p - 1 from hp_odd.
-/
theorem energy_at_factor (p q : ℕ) (hp : 2 < p) (hq : 2 < q) (hp_odd : p % 2 = 1) :
    let N : ℤ := ↑(p * q)
    let k := (p - 1) / 2
    (N - 2 * ↑k) ^ 2 = (↑(p * q) - ↑p + 1) ^ 2 := by
      grind +ring

/-! ## Convergence Rate -/

/-- The "velocity" of the descent in energy space at step k.
    v(k) = E(k) - E(k+1) = 4(N - 2k - 1).
    The velocity decreases linearly, meaning the system decelerates. -/
def velocity (N : ℤ) (k : ℕ) : ℤ := 4 * (N - 2 * k - 1)

/-
PROBLEM
Velocity is positive whenever we haven't passed the midpoint.

PROVIDED SOLUTION
velocity N k = 4*(N - 2k - 1). Since 2k+1 < N (as naturals), casting to integers gives (N : ℤ) - 2*(k : ℤ) - 1 > 0. Unfold velocity, push_cast, omega or linarith.
-/
theorem velocity_positive (N : ℕ) (k : ℕ) (hk : 2 * k + 1 < N) :
    0 < velocity (↑N) k := by
      exact mul_pos zero_lt_four ( by linarith )

/-
PROBLEM
Velocity decreases by exactly 8 at each step (constant deceleration).

PROVIDED SOLUTION
Unfold velocity. v(k) - v(k+1) = 4*(N-2k-1) - 4*(N-2*(k+1)-1) = 4*(N-2k-1) - 4*(N-2k-3) = 4*2 = 8. Use ring after unfolding.
-/
theorem constant_deceleration (N : ℤ) (k : ℕ) :
    velocity N k - velocity N (k + 1) = 8 := by
      unfold velocity; ring;
      push_cast; ring;

/-! ## Parallel Descent Theorem -/

/-
PROBLEM
Running descents from different starting configurations simultaneously.
For the standard descent, the time is (p-1)/2.
Key insight: we can run multiple descents with different step sizes.

Multi-stride correctness: stepping by s instead of 1 finds the factor
    if and only if the factor step is a multiple of s (modulo stride).

PROVIDED SOLUTION
We need ∃ i with j*s ≤ i ∧ i < (j+1)*s ∧ i = k. Since j*s ≤ k and k < (j+1)*s, just use ⟨k, hjs, hjsn, rfl⟩.
-/
theorem multi_stride_gcd (N p : ℕ) (s : ℕ) (hs : 0 < s)
    (hp : Nat.Prime p) (hdvd : p ∣ N) (hp2 : p ≠ 2)
    (k : ℕ) (hk : k = (p - 1) / 2)
    (j : ℕ) (hjs : j * s ≤ k) (hjsn : k < (j + 1) * s) :
    ∃ i, j * s ≤ i ∧ i < (j + 1) * s ∧ i = k := by
      aesop

/-! ## Information-Theoretic Bound -/

/-
PROBLEM
Each step of the IOF descent reveals at most O(log N) bits of information
    about the factors (through the GCD computation). Since the factors
    contain O(log N) bits total, we need at least Ω(1) steps to find them.
    The actual number of steps (p-1)/2 ≈ √N/2 is much larger, suggesting
    the descent is informationally inefficient.

    This theorem states the trivial lower bound: at least 1 step is needed
    for N > 3.

PROVIDED SOLUTION
p is prime and p > 2, so p ≥ 3. Then (p-1)/2 ≥ 1 > 0. Use omega.
-/
theorem at_least_one_step (N p q : ℕ) (hp : Nat.Prime p) (hq : Nat.Prime q)
    (hN : N = p * q) (hp2 : 2 < p) (hle : p ≤ q) :
    0 < (p - 1) / 2 := by
      grind

end IOFDynamical