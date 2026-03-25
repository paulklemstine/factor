import Mathlib

/-!
# The Integer Timeline of Gravity — Research Cycles 14–19+

## Research Team: Project CHRONOS (Continued)

### Agents
- **Agent Λ (Light)**: Proves both light and dark primes are infinite (Cycle 14)
- **Agent Γ (Gauss)**: Connects Gaussian integers to light/dark splitting (Cycle 15)
- **Agent Ω (Gravity)**: Formalizes gravitational clustering via highly composite numbers (Cycle 16)
- **Agent Σ (Information)**: Measures information content of light/dark sequences (Cycle 17)
- **Agent ζ (Zeta)**: States the Riemann hypothesis as expansion rate control (Cycle 18)
- **Agent ℚ (Reciprocity)**: Quadratic reciprocity as light-dark interaction law (Cycle 19)
- **Agent ∞ (Self-Reference)**: The universe computes itself (Cycle ∞)

### Lab Notebook — New Cycles
**Cycle 14**: Prove both light primes and dark primes are infinite (partial Dirichlet).
**Cycle 15**: Fermat's two-square theorem: light primes ARE sums of two squares.
**Cycle 16**: Highly composite numbers as gravitational galaxies.
**Cycle 17**: Information-theoretic content of light vs dark sequences.
**Cycle 18**: The Riemann hypothesis as a statement about expansion rate.
**Cycle 19**: Quadratic reciprocity as a light-dark interaction law.
**Cycle ∞**: Self-referential closure — the research oracle converges.
-/

open Nat Finset BigOperators Function Set

noncomputable section

-- Recall definitions from TimelineGravity.lean
/-- A prime is "light" if p ≡ 1 mod 4. -/
def isLightPrime' (p : ℕ) : Prop := p.Prime ∧ p % 4 = 1

/-- A prime is "dark" if p ≡ 3 mod 4. -/
def isDarkPrime' (p : ℕ) : Prop := p.Prime ∧ p % 4 = 3

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE 14: DIRICHLET'S THEOREM (PARTIAL) — EQUAL INFINITY OF LIGHT AND DARK
    ═══════════════════════════════════════════════════════════════════════════

    Both light primes (≡ 1 mod 4) and dark primes (≡ 3 mod 4) are infinite.
    This is a special case of Dirichlet's theorem on primes in arithmetic
    progressions. The dark case has an elementary proof; the light case
    uses the fact that prime divisors of n² + 1 must be ≡ 1 (mod 4).

    Metaphor: The universe has infinite photons AND infinite dark matter.
    Neither can be exhausted — the duality persists forever.
-/

/-
PROBLEM
Key lemma: if p is an odd prime dividing n² + 1, then p ≡ 1 mod 4.
    This is because -1 is a quadratic residue mod p iff p ≡ 1 mod 4.

PROVIDED SOLUTION
If p | n² + 1, then n² ≡ -1 mod p, meaning -1 is a quadratic residue mod p. For an odd prime p, -1 is a QR iff p ≡ 1 mod 4 (by Euler's criterion, (-1)^((p-1)/2) = 1 iff (p-1)/2 is even iff p ≡ 1 mod 4). Use ZMod.isSquare_neg_one_iff or work with Euler's criterion in Mathlib. The key Mathlib fact: legendreSym.at_neg_one says legendreSym p (-1) = χ₄(p), and if -1 is a QR mod p then legendreSym p (-1) = 1, so χ₄(p) = 1, which means p ≡ 1 mod 4. Alternatively, use the fact that the multiplicative order of -1 in (ZMod p)* divides (p-1), and -1 has order 2, so 2 | (p-1), and since p | n²+1 means n² ≡ -1 mod p, the order of n is 4, so 4 | (p-1), hence p ≡ 1 mod 4.
-/
theorem prime_div_sq_add_one_mod_four (p n : ℕ) (hp : p.Prime) (hp2 : p ≠ 2)
    (hdvd : p ∣ n ^ 2 + 1) : p % 4 = 1 := by
      haveI := Fact.mk hp; norm_num [ ← ZMod.natCast_eq_zero_iff ] at *;
      have := ZMod.exists_sq_eq_neg_one_iff ( p := p );
      exact this.mp ⟨ n, by linear_combination' -hdvd ⟩ |> fun h => by have := Nat.Prime.eq_two_or_odd hp; omega;

/-
PROBLEM
There are infinitely many dark primes (≡ 3 mod 4).
    Proof sketch: Given any N, consider M = 4·(N+1)! - 1.
    Then M ≡ 3 mod 4 and M > N. M must have a prime factor ≡ 3 mod 4
    (since a product of numbers all ≡ 1 mod 4 is itself ≡ 1 mod 4,
    so not all prime factors of M can be ≡ 1 mod 4). This prime factor
    exceeds N since it divides M > N.

PROVIDED SOLUTION
Given N, consider M = 4 * ∏(primes ≤ N that are ≡ 3 mod 4) - 1. But this is hard to formalize. Simpler: consider M = 4*(N+1)! - 1. Then M ≡ 3 mod 4 and M ≥ 3. M has at least one prime factor. If all prime factors of M were ≡ 1 mod 4 or equal to 2, then M mod 4 would be ≡ 0 or 1, contradiction since M ≡ 3 mod 4. So M has a prime factor p ≡ 3 mod 4. Since p | M = 4*(N+1)! - 1, if p ≤ N+1 then p | (N+1)! so p | 4*(N+1)!, and since p | M = 4*(N+1)!-1, we'd get p | 1, contradiction since p ≥ 3. So p > N+1 > N. Actually, this doesn't quite work because p could be 2. But p divides M which is odd (M = 4k-1), so p is odd. And p ≡ 3 mod 4. So p > N. Wait, we need p ≤ N+1 implies p | (N+1)!. Since p is prime and p ≤ N+1, we have p | (N+1)!. Then p | 4*(N+1)! and p | (4*(N+1)! - 1) gives p | 1, contradiction. So p > N+1 > N.
-/
theorem infinitely_many_dark_primes :
    ∀ N : ℕ, ∃ p, N < p ∧ isDarkPrime' p := by
      intro N;
      -- Consider the number $M = 4(N+1)! - 1$. This number is of the form $4k-1$ and is greater than $N$.
      set M := 4 * (N + 1)! - 1;
      have hM_form : M % 4 = 3 := by
        zify;
        rw [ Int.ofNat_sub ( Nat.one_le_iff_ne_zero.mpr <| by positivity ) ] ; norm_num [ Int.mul_emod, Int.sub_emod ];
      have hM_gt_N : M > N := by
        exact lt_tsub_iff_left.mpr ( by linarith [ Nat.self_le_factorial ( N + 1 ) ] );
      -- Since $M$ is of the form $4k-1$, it must have a prime divisor $p$ that is also of the form $4k-1$.
      obtain ⟨p, hp_prime, hp_div⟩ : ∃ p, Nat.Prime p ∧ p ∣ M ∧ p % 4 = 3 := by
        by_contra h_no_prime_divisor;
        -- If $M$ has no prime factors of the form $4k-1$, then all prime factors of $M$ must be of the form $4k+1$.
        have h_all_prime_factors_form : ∀ p : ℕ, Nat.Prime p → p ∣ M → p % 4 = 1 := by
          intro p pp dp; have := Nat.mod_lt p zero_lt_four; interval_cases h : p % 4 <;> simp_all +decide [ ← Nat.dvd_iff_mod_eq_zero, pp.dvd_iff_eq ] ;
          have := Nat.dvd_trans ( Nat.dvd_of_mod_eq_zero ( show p % 2 = 0 by norm_num [ ← Nat.mod_mod_of_dvd p ( by decide : 2 ∣ 4 ), h ] ) ) dp; omega;
        -- The product of numbers of the form $4k+1$ is again of the form $4k+1$.
        have h_prod_form : ∀ (n : ℕ), (∀ p : ℕ, Nat.Prime p → p ∣ n → p % 4 = 1) → n % 4 = 1 := by
          intros n hn; rw [ ← Nat.prod_primeFactorsList ( show n ≠ 0 from fun hk ↦ by subst hk; specialize hn 2 Nat.prime_two; simp_all +decide ) ] ; rw [ List.prod_nat_mod ] ; exact by rw [ List.prod_eq_one ] <;> intros <;> aesop;
        cases h_prod_form M h_all_prime_factors_form ▸ hM_form;
      exact ⟨ p, not_le.mp fun h => by have := Nat.dvd_sub ( dvd_mul_of_dvd_right ( Nat.dvd_factorial ( Nat.pos_of_ne_zero hp_prime.ne_zero ) ( by linarith : N + 1 ≥ p ) ) 4 ) hp_div.1; erw [ Nat.sub_sub_self ( Nat.one_le_iff_ne_zero.mpr <| by positivity ) ] at this; aesop, hp_prime, hp_div.2 ⟩

/-
PROBLEM
There are infinitely many light primes (≡ 1 mod 4).
    Proof sketch: Given any N, consider M = (2·(N+1)!)² + 1.
    Any odd prime factor of M must be ≡ 1 mod 4
    (by prime_div_sq_add_one_mod_four). Since M > N,
    at least one such prime exceeds N.

PROVIDED SOLUTION
Given N, consider M = (2*(N+1)!)^2 + 1. Then M ≥ 2. Let p be a prime factor of M. Then p | (2*(N+1)!)^2 + 1, so (2*(N+1)!)^2 ≡ -1 mod p. This means p is odd (since M is odd, being 1 + even²). By the lemma prime_div_sq_add_one_mod_four with n = 2*(N+1)!, p is ≡ 1 mod 4. So p is a light prime. If p ≤ N+1, then p | (N+1)!, so p | (2*(N+1)!)^2, and since p | M = (2*(N+1)!)^2 + 1, we'd get p | 1, contradiction since p ≥ 2. So p > N+1 > N. Thus p is a light prime bigger than N.
-/
theorem infinitely_many_light_primes :
    ∀ N : ℕ, ∃ p, N < p ∧ isLightPrime' p := by
      intro N;
      -- By Dirichlet's theorem on arithmetic progressions, there are infinitely many primes in the arithmetic progression $4k + 1$.
      have h_dirichlet : Set.Infinite {p : ℕ | Nat.Prime p ∧ p % 4 = 1} := by
        exact Nat.infinite_setOf_prime_modEq_one <| by decide;
      exact Exists.elim ( h_dirichlet.exists_gt N ) fun p hp => ⟨ p, hp.2, hp.1 ⟩

/-- Computational verification: light and dark counts. -/
def lightPrimeCount' (n : ℕ) : ℕ :=
  ((Finset.range (n + 1)).filter (fun p => p.Prime ∧ p % 4 = 1)).card

def darkPrimeCount' (n : ℕ) : ℕ :=
  ((Finset.range (n + 1)).filter (fun p => p.Prime ∧ p % 4 = 3)).card

/-- Both counts grow: 11 light and 13 dark primes up to 100. -/
theorem light_dark_count_100 :
    lightPrimeCount' 100 = 11 ∧ darkPrimeCount' 100 = 13 := by
  constructor <;> native_decide

/-- By 200: 21 light, 24 dark — dark still leads (Chebyshev bias). -/
theorem light_dark_count_200 :
    lightPrimeCount' 200 = 21 ∧ darkPrimeCount' 200 = 24 := by
  constructor <;> native_decide

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE 15: FERMAT'S TWO-SQUARE THEOREM — WHY LIGHT PRIMES SPLIT
    ═══════════════════════════════════════════════════════════════════════════

    Fermat's theorem: An odd prime p is a sum of two squares iff p ≡ 1 mod 4.
    Equivalently: light primes ARE exactly the primes that decompose as a² + b².

    In ℤ[i], this means light primes split: p = (a + bi)(a - bi).
    Dark primes remain inert — they don't factor in ℤ[i].

    Metaphor: Light primes carry internal structure (the a,b decomposition).
    Dark primes are structureless — they are the fabric of space itself.
-/

/-
PROBLEM
Fermat's two-square theorem (forward): light primes are sums of two squares.
    This is a deep result available in Mathlib as Nat.Prime.sq_add_sq.

PROVIDED SOLUTION
Use Mathlib's Nat.Prime.sq_add_sq. We have hmod : p % 4 = 1, so p % 4 ≠ 3. Apply @Nat.Prime.sq_add_sq with [Fact p.Prime] instance from hp.
-/
theorem light_prime_is_sum_of_squares (p : ℕ) (hp : p.Prime) (hmod : p % 4 = 1) :
    ∃ a b : ℕ, a ^ 2 + b ^ 2 = p := by
      convert @Nat.Prime.sq_add_sq p ( Fact.mk hp ) ( by aesop ) using 1

/-
PROBLEM
Conversely: dark primes are NOT sums of two squares.
    Proof: If p = a² + b² with p ≡ 3 mod 4, then a² + b² ≡ 3 mod 4.
    But squares mod 4 are 0 or 1, so a² + b² mod 4 ∈ {0, 1, 2}. Contradiction.

PROVIDED SOLUTION
If p = a² + b² and p ≡ 3 mod 4, then a² + b² ≡ 3 mod 4. But squares mod 4 are 0 or 1, so a² + b² mod 4 ∈ {0, 1, 2}. Contradiction. Use omega after reducing mod 4.
-/
theorem dark_prime_not_sum_of_squares (p : ℕ) (hp : p.Prime) (hmod : p % 4 = 3)
    (a b : ℕ) : a ^ 2 + b ^ 2 ≠ p := by
      exact ne_of_apply_ne ( · % 4 ) ( by norm_num [ Nat.add_mod, Nat.pow_mod, hmod ] ; have := Nat.mod_lt a zero_lt_four; have := Nat.mod_lt b zero_lt_four; interval_cases a % 4 <;> interval_cases b % 4 <;> trivial )

/-- The Gaussian norm: |a + bi|² = a² + b². -/
def gaussianNormSq (a b : ℤ) : ℤ := a ^ 2 + b ^ 2

/-- Gaussian norm is multiplicative: |zw|² = |z|²·|w|². -/
theorem gaussianNorm_mul (a b c d : ℤ) :
    gaussianNormSq (a * c - b * d) (a * d + b * c) =
    gaussianNormSq a b * gaussianNormSq c d := by
  unfold gaussianNormSq; ring

/-- A Gaussian integer decomposition of a light prime. -/
structure GaussianSplit (p : ℕ) where
  a : ℤ
  b : ℤ
  norm_eq : a ^ 2 + b ^ 2 = (p : ℤ)
  nontrivial_a : a ≠ 0
  nontrivial_b : b ≠ 0

/-- Concrete Gaussian split of 5 = (2 + i)(2 - i). -/
def split_5 : GaussianSplit 5 where
  a := 2; b := 1
  norm_eq := by norm_num
  nontrivial_a := by omega
  nontrivial_b := by omega

/-- Concrete Gaussian split of 13 = (3 + 2i)(3 - 2i). -/
def split_13 : GaussianSplit 13 where
  a := 3; b := 2
  norm_eq := by norm_num
  nontrivial_a := by omega
  nontrivial_b := by omega

/-- Concrete Gaussian split of 17 = (4 + i)(4 - i). -/
def split_17 : GaussianSplit 17 where
  a := 4; b := 1
  norm_eq := by norm_num
  nontrivial_a := by omega
  nontrivial_b := by omega

/-- Concrete Gaussian split of 29 = (5 + 2i)(5 - 2i). -/
def split_29 : GaussianSplit 29 where
  a := 5; b := 2
  norm_eq := by norm_num
  nontrivial_a := by omega
  nontrivial_b := by omega

/-- Concrete Gaussian split of 37 = (6 + i)(6 - i). -/
def split_37 : GaussianSplit 37 where
  a := 6; b := 1
  norm_eq := by norm_num
  nontrivial_a := by omega
  nontrivial_b := by omega

/-
PROBLEM
The number of essentially distinct representations is exactly 1
    for light primes (Fermat). Every photon has a unique internal structure.

PROVIDED SOLUTION
This is the uniqueness of sum-of-two-squares representation for primes. Since p is prime and p ≡ 1 mod 4, by Fermat/Thue, p = a² + b² uniquely (up to signs and order). The proof uses the fact that in ℤ[i], p factors as (a+bi)(a-bi) and since ℤ[i] is a PID/UFD, this factorization is unique up to units. The Gaussian integers units are {1, -1, i, -i}, which accounts for sign changes and swapping a,b. Given two representations s₁ and s₂ with s₁.a² + s₁.b² = p = s₂.a² + s₂.b², by the Gaussian integer UFD property, (s₁.a + s₁.b·i) and (s₂.a + s₂.b·i) differ by a unit in ℤ[i], giving the desired conclusion about natAbs.
-/
set_option maxHeartbeats 800000 in
theorem unique_photon_structure (p : ℕ) (hp : p.Prime) (hmod : p % 4 = 1)
    (s₁ s₂ : GaussianSplit p) :
    (s₁.a.natAbs = s₂.a.natAbs ∧ s₁.b.natAbs = s₂.b.natAbs) ∨
    (s₁.a.natAbs = s₂.b.natAbs ∧ s₁.b.natAbs = s₂.a.natAbs) := by
      obtain ⟨a₁, b₁, ha₁⟩ := s₁
      obtain ⟨a₂, b₂, ha₂⟩ := s₂
      have h_eq : a₁^2 + b₁^2 = a₂^2 + b₂^2 := by
        linarith
      have h_div : (a₁ * a₂ + b₁ * b₂) % p = 0 ∨ (a₁ * a₂ - b₁ * b₂) % p = 0 := by
        have h_div : (a₁ * a₂ + b₁ * b₂) * (a₁ * a₂ - b₁ * b₂) ≡ 0 [ZMOD p] := by
          exact Int.modEq_zero_iff_dvd.mpr ⟨ a₂ ^ 2 - b₁ ^ 2, by nlinarith ⟩ ;
        generalize_proofs at *; (
        exact Int.Prime.dvd_mul' hp ( Int.dvd_of_emod_eq_zero h_div ) |> Or.imp ( fun h => Int.emod_eq_zero_of_dvd h ) fun h => Int.emod_eq_zero_of_dvd h;)
      have h_cases : (a₁ * a₂ + b₁ * b₂) % p = 0 ∧ (a₁ * b₂ - a₂ * b₁) % p = 0 ∨ (a₁ * a₂ - b₁ * b₂) % p = 0 ∧ (a₁ * b₂ + a₂ * b₁) % p = 0 := by
        cases h_div <;> simp_all +decide [ ← Int.dvd_iff_emod_eq_zero, Int.natAbs_dvd ];
        · have h_div : (p : ℤ) ∣ (a₁ * b₂ - a₂ * b₁) ^ 2 := by
            convert dvd_sub ( dvd_mul_right ( p : ℤ ) ( a₂ ^ 2 + b₂ ^ 2 ) ) ( ‹ ( p : ℤ ) ∣ a₁ * a₂ + b₁ * b₂ ›.mul_left ( a₁ * a₂ + b₁ * b₂ ) ) using 1 ; ring;
            rw [ ← h_eq ] ; ring;
          exact Or.inl <| Int.Prime.dvd_pow' hp h_div;
        · have h_div : (p : ℤ) ∣ (a₁ * b₂ + a₂ * b₁) := by
            have h_eq : (a₁ * a₂ - b₁ * b₂) ^ 2 + (a₁ * b₂ + a₂ * b₁) ^ 2 = p * (a₂ ^ 2 + b₂ ^ 2) := by
              linear_combination' h_eq * ( a₂ ^ 2 + b₂ ^ 2 )
            exact Int.Prime.dvd_pow' hp <| show ( p : ℤ ) ∣ ( a₁ * b₂ + a₂ * b₁ ) ^ 2 by exact ⟨ ( a₂ ^ 2 + b₂ ^ 2 ) - ( a₁ * a₂ - b₁ * b₂ ) ^ 2 / p, by linarith [ Int.ediv_mul_cancel <| show ( p : ℤ ) ∣ ( a₁ * a₂ - b₁ * b₂ ) ^ 2 from dvd_pow ‹_› two_ne_zero ] ⟩ ;
          aesop
      have h_abs : Int.natAbs (a₁ * a₂ + b₁ * b₂) < p + p ∧ Int.natAbs (a₁ * a₂ - b₁ * b₂) < p + p ∧ Int.natAbs (a₁ * b₂ - a₂ * b₁) < p + p ∧ Int.natAbs (a₁ * b₂ + a₂ * b₁) < p + p := by
        have h_bounds : |a₁ * a₂ + b₁ * b₂| < 2 * p ∧ |a₁ * a₂ - b₁ * b₂| < 2 * p ∧ |a₁ * b₂ - a₂ * b₁| < 2 * p ∧ |a₁ * b₂ + a₂ * b₁| < 2 * p := by
          refine' ⟨ _, _, _, _ ⟩ <;> rw [ abs_lt ] <;> constructor <;> nlinarith [ sq_nonneg ( a₁ - a₂ ), sq_nonneg ( a₁ + a₂ ), sq_nonneg ( b₁ - b₂ ), sq_nonneg ( b₁ + b₂ ), hp.two_le ] ;
        exact ⟨ by linarith [ abs_lt.mp h_bounds.1 ], by linarith [ abs_lt.mp h_bounds.2.1 ], by linarith [ abs_lt.mp h_bounds.2.2.1 ], by linarith [ abs_lt.mp h_bounds.2.2.2 ] ⟩
      have h_cases : a₁ * a₂ + b₁ * b₂ = 0 ∨ a₁ * a₂ - b₁ * b₂ = 0 ∨ a₁ * b₂ - a₂ * b₁ = 0 ∨ a₁ * b₂ + a₂ * b₁ = 0 := by
        cases h_cases <;> simp_all +decide [ ← Int.dvd_iff_emod_eq_zero ];
        · cases' ‹_› with h₁ h₂;
          -- Since $p$ is prime and divides $a₁ * a₂ + b₁ * b₂$, and the absolute value of this sum is less than $2p$, the only possibilities are that the sum is $0$ or $p$. But if it were $p$, then $a₁ * a₂ + b₁ * b₂ = p$, which would imply that $a₁ * a₂$ and $b₁ * b₂$ are both less than $p$, leading to a contradiction.
          have h_sum_zero : a₁ * a₂ + b₁ * b₂ = 0 ∨ a₁ * a₂ + b₁ * b₂ = p ∨ a₁ * a₂ + b₁ * b₂ = -p := by
            obtain ⟨ k, hk ⟩ := h₁; simp_all +decide [ Int.natAbs_mul, Nat.prime_mul_iff ] ;
            have : k.natAbs ≤ 1 := Nat.le_of_lt_succ ( by nlinarith [ hp.two_le ] ) ; interval_cases _ : k.natAbs <;> simp_all +decide ;
            rw [ Int.natAbs_eq_iff ] at * ; aesop;
          rcases h_sum_zero with h | h | h <;> simp_all +decide [ sub_eq_iff_eq_add ];
          · have h_contra : (a₁ - a₂)^2 + (b₁ - b₂)^2 = 0 := by
              grind +locals;
            norm_num [ show a₁ = a₂ by nlinarith only [ h_contra ], show b₁ = b₂ by nlinarith only [ h_contra ] ] at *;
          · have h_contra : (a₁ + a₂)^2 + (b₁ + b₂)^2 = 0 := by
              grind;
            norm_num [ show a₁ = -a₂ by nlinarith only [ h_contra ], show b₁ = -b₂ by nlinarith only [ h_contra ] ] at *;
        · obtain ⟨ k₁, hk₁ ⟩ := ‹ ( p : ℤ ) ∣ a₁ * a₂ - b₁ * b₂ ∧ ( p : ℤ ) ∣ a₁ * b₂ + a₂ * b₁ ›.1; obtain ⟨ k₂, hk₂ ⟩ := ‹ ( p : ℤ ) ∣ a₁ * a₂ - b₁ * b₂ ∧ ( p : ℤ ) ∣ a₁ * b₂ + a₂ * b₁ ›.2; simp_all +decide [ sub_eq_iff_eq_add ] ;
          have h_contra : k₁ ^ 2 + k₂ ^ 2 = 1 := by
            have h_contra : (a₁ * a₂ - b₁ * b₂) ^ 2 + (a₁ * b₂ + a₂ * b₁) ^ 2 = p ^ 2 * (k₁ ^ 2 + k₂ ^ 2) := by
              rw [ hk₁, hk₂ ] ; ring;
            exact mul_left_cancel₀ ( pow_ne_zero 2 ( Nat.cast_ne_zero.mpr hp.ne_zero ) ) ( by nlinarith );
          have : k₁ ≤ 1 := Int.le_of_lt_add_one ( by nlinarith only [ h_contra ] ) ; ( have : k₁ ≥ -1 := Int.le_of_lt_add_one ( by nlinarith only [ h_contra ] ) ; interval_cases k₁ <;> ( have : k₂ ≤ 1 := Int.le_of_lt_add_one ( by nlinarith only [ h_contra ] ) ; ( have : k₂ ≥ -1 := Int.le_of_lt_add_one ( by nlinarith only [ h_contra ] ) ; interval_cases k₂ <;> simp_all +decide ; ) ) )
      have h_final : Int.natAbs a₁ = Int.natAbs a₂ ∧ Int.natAbs b₁ = Int.natAbs b₂ ∨ Int.natAbs a₁ = Int.natAbs b₂ ∧ Int.natAbs b₁ = Int.natAbs a₂ := by
        rcases h_cases with h | h | h | h <;> simp_all +decide [ sub_eq_iff_eq_add, add_eq_zero_iff_eq_neg ];
        · have h_abs : a₁^2 = b₂^2 ∧ b₁^2 = a₂^2 := by
            constructor <;> nlinarith [ sq_nonneg ( a₁ - a₂ ), sq_nonneg ( a₁ + a₂ ), sq_nonneg ( b₁ - b₂ ), sq_nonneg ( b₁ + b₂ ), mul_self_pos.2 ‹a₁ ≠ 0›, mul_self_pos.2 ‹b₁ ≠ 0›, mul_self_pos.2 ‹a₂ ≠ 0›, mul_self_pos.2 ‹b₂ ≠ 0› ] ;
          exact Or.inr ⟨ by simpa [ ← Int.natCast_inj ] using congr_arg Int.natAbs h_abs.1, by simpa [ ← Int.natCast_inj ] using congr_arg Int.natAbs h_abs.2 ⟩;
        · have h_final : a₁ ^ 2 = b₂ ^ 2 ∧ b₁ ^ 2 = a₂ ^ 2 := by
            constructor <;> nlinarith [ sq_nonneg ( a₁ - a₂ ), sq_nonneg ( a₁ + a₂ ), sq_nonneg ( b₁ - b₂ ), sq_nonneg ( b₁ + b₂ ) ];
          exact Or.inr ⟨ by simpa [ ← Int.natCast_inj ] using congr_arg Int.natAbs h_final.1, by simpa [ ← Int.natCast_inj ] using congr_arg Int.natAbs h_final.2 ⟩;
        · have h_cases : a₁ ^ 2 = a₂ ^ 2 ∧ b₁ ^ 2 = b₂ ^ 2 ∨ a₁ ^ 2 = b₂ ^ 2 ∧ b₁ ^ 2 = a₂ ^ 2 := by
            have h_cases : a₁ ^ 2 * b₂ ^ 2 = a₂ ^ 2 * b₁ ^ 2 := by
              linear_combination' h * h;
            cases le_or_gt ( a₁ ^ 2 ) ( a₂ ^ 2 ) <;> [ left; right ] <;> constructor <;> nlinarith [ show 0 < a₂ ^ 2 by positivity, show 0 < b₁ ^ 2 by positivity ] ;
          simp_all +decide [ ← Int.natCast_inj, Int.natAbs_pow ];
          exact Or.imp ( fun h => ⟨ by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith, by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith ⟩ ) ( fun h => ⟨ by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith, by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith ⟩ ) h_cases;
        · have h_abs : a₁ ^ 2 * b₂ ^ 2 = a₂ ^ 2 * b₁ ^ 2 := by
            linear_combination' h * h
          have h_abs_eq : a₁ ^ 2 = a₂ ^ 2 ∧ b₁ ^ 2 = b₂ ^ 2 ∨ a₁ ^ 2 = b₂ ^ 2 ∧ b₁ ^ 2 = a₂ ^ 2 := by
            exact Or.inl ⟨ by nlinarith, by nlinarith ⟩
          generalize_proofs at *; (
          simp_all +decide [ ← Int.natCast_inj, Int.natAbs_pow ];
          exact Or.imp ( fun h => ⟨ by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith, by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith ⟩ ) ( fun h => ⟨ by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith, by rw [ ← sq_eq_sq₀ ] <;> norm_num ; linarith ⟩ ) h_abs_eq;)
      exact h_final

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE 16: GRAVITATIONAL CLUSTERING — HIGHLY COMPOSITE GALAXIES
    ═══════════════════════════════════════════════════════════════════════════

    Highly composite numbers have more divisors than any smaller number.
    On the integer timeline, these are "gravitational galaxies" — massive
    concentrations that attract structure around them.

    HCNs: 1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720, ...
-/

/-- A number is highly composite if it has more divisors than all smaller numbers. -/
def IsHighlyComposite (n : ℕ) : Prop :=
  0 < n ∧ ∀ m, 0 < m → m < n → m.divisors.card < n.divisors.card

/-- 1 is highly composite (vacuously — the primordial singularity). -/
theorem hc_1 : IsHighlyComposite 1 := by
  constructor
  · omega
  · intro m hm hm1; omega

/-- 2 is highly composite: d(2) = 2 > d(1) = 1. -/
theorem hc_2 : IsHighlyComposite 2 := by
  refine ⟨by omega, ?_⟩
  intro m hm hm2
  interval_cases m <;> native_decide

/-- 4 is highly composite: d(4) = 3 > d(m) for m < 4. -/
theorem hc_4 : IsHighlyComposite 4 := by
  refine ⟨by omega, ?_⟩
  intro m hm hm4
  interval_cases m <;> native_decide

/-- 6 is highly composite: d(6) = 4 > d(m) for m < 6. -/
theorem hc_6 : IsHighlyComposite 6 := by
  refine ⟨by omega, ?_⟩
  intro m hm hm6
  interval_cases m <;> native_decide

/-- 12 is highly composite: d(12) = 6 > d(m) for m < 12. -/
theorem hc_12 : IsHighlyComposite 12 := by
  refine ⟨by omega, ?_⟩
  intro m hm hm12
  interval_cases m <;> native_decide

/-- 24 is highly composite: d(24) = 8 > d(m) for m < 24. -/
theorem hc_24 : IsHighlyComposite 24 := by
  refine ⟨by omega, ?_⟩
  intro m hm hm24
  interval_cases m <;> native_decide

/-- 3 is NOT highly composite: d(3) = 2 = d(2). -/
theorem not_hc_3 : ¬IsHighlyComposite 3 := by
  intro ⟨_, h⟩
  have h2 := h 2 (by omega) (by omega)
  revert h2; native_decide

/-- 5 is NOT highly composite: d(5) = 2 < d(4) = 3. -/
theorem not_hc_5 : ¬IsHighlyComposite 5 := by
  intro ⟨_, h⟩
  have h4 := h 4 (by omega) (by omega)
  revert h4; native_decide

/-- Gravitational weight (number of divisors). -/
def gravWeight (n : ℕ) : ℕ := n.divisors.card

/-- HCNs have strictly more gravitational mass than anything before them. -/
theorem hcn_maximal_gravity (n : ℕ) (hn : IsHighlyComposite n) :
    ∀ m, 0 < m → m < n → gravWeight m < gravWeight n :=
  hn.2

/-
PROBLEM
Highly composite numbers are always even (except 1).

PROVIDED SOLUTION
Proof: Assume n is odd and n > 1. Then n ≥ 3. Consider m = n - 1, which is even and satisfies 0 < m < n. Since n is highly composite, d(n) > d(n-1). But n is odd, so every divisor of n is odd. The number n-1 is even, so has divisors 1 and 2 at minimum. We can establish an injection from divisors of n to divisors of n-1 as follows: Actually, the easier approach: n is odd and n ≥ 3. If n is prime, then d(n) = 2. But n-1 ≥ 2 is even, so 1, 2, n-1 are divisors of n-1 (when n-1 ≥ 4, i.e. n ≥ 5, also (n-1)/2). For n = 3: d(3) = 2, d(2) = 2, so d(3) ≤ d(2), contradicting IsHighlyComposite. For n ≥ 5 prime: d(n) = 2 but d(n-1) ≥ 3 (since 1, 2, (n-1)/2 are distinct divisors when n ≥ 5), contradicting d(n) > d(n-1). For n ≥ 9 composite odd: d(n) ≥ 3, but we can show d(n-1) ≥ d(n). Actually the simplest approach: if n is odd and n > 1, map each divisor d of n to 2d. These are all divisors of 2n, and since n is odd, d and 2d are distinct. Together with the divisors of n themselves, 2n has at least 2·d(n) divisors: d(2n) ≥ 2·d(n) > d(n). Since 2n > n but we need a number LESS than n... Hmm. Instead: if n ≥ 3 is odd, consider n-1 which is even. We need d(n) > d(n-1). But we can show d(n) ≤ d(n-1) to get a contradiction. For n odd and n ≥ 3, n-1 is even, n-1 ≥ 2. Define f: divisors of n → divisors of n-1 by... this doesn't work directly. Better approach: Any odd number n has d(n) ≤ d(2(n-1)). But 2(n-1) could be ≥ n. Alternative: use that for n ≥ 3 odd, d(n-1) ≥ d(n). This is because n-1 is even and d(n-1) = d(n-1). Actually this isn't necessarily true (d(9)=3, d(8)=4: works. d(15)=4, d(14)=4: fails since d(15)=d(14)=4, so d(15) is NOT > d(14), meaning 15 isn't HCN. But what about d(25)=3, d(24)=8: d(25) < d(24), so 25 isn't HCN.) Actually the key insight is: for n odd and n > 1, n cannot be HCN because there exists some m < n with d(m) ≥ d(n). The simplest witness is a small even number. Specifically: for any odd n > 2, we have n ≥ 3. We claim d(n) ≤ n/2 + 1 (trivially), but actually we need something sharper. The simplest: for n ≥ 3 odd, we have d(n) ≤ (n+1)/2. And for the even number n-1 ≥ 2, d(n-1) ≥ 2. So we need d(n) > d(n-1). For n = 3: d(3)=2, d(2)=2, not strictly greater. For n = 5: d(5)=2, d(4)=3, 2 < 3, not strictly greater. For n ≥ 7 odd: we just need to find some even m < n with d(m) ≥ d(n). The key fact: d(2⌊n/2⌋) ≥ d(⌊n/2⌋) ≥ d(n) when n is odd... Actually this isn't obvious. Let me try a different angle. The theorem states that every HCN except 1 is even. We know the HCN sequence starts 1,2,4,6,12,24,... all even after 1. For the proof: suppose n > 1 is odd and HCN. Consider the largest power of 2 less than n, say 2^k < n. Then d(2^k) = k+1. Since n is odd, n < 2^(k+1), so k+1 > log2(n)/log2(2). Actually this is getting complicated. Let me try: for n ≥ 3 odd, let m be the largest even number ≤ n-1. Then m = n-1 and m < n. We need d(m) < d(n) for HCN. But d(n-1) ≥ d(n)? Not necessarily. Hmm. OK, let me try a cleaner argument: if n is odd and n ≥ 3, then 2 | (n-1) so n-1 has at least the divisors {1, 2, (n-1)/2, n-1} (when n ≥ 5), giving d(n-1) ≥ 4. Meanwhile n is odd. If n is prime, d(n) = 2 < 4 ≤ d(n-1). If n = p^a for odd prime p, d(n) = a+1 but n = p^a ≥ 3^a, and n-1 ≥ 3^a - 1. For n = 9 = 3², d(9) = 3, d(8) = 4, OK. For n = 27, d(27) = 4, d(26) = 4, so d(27) is not > d(26), fail. For composite odd n with multiple prime factors: d(n) ≥ 4 but d(n-1) ≥ 4 too. We'd need d(n-1) ≥ d(n). Actually, the REAL argument is: for odd n > 1, compare d(n) with d(2n). Since n is odd, gcd(2,n)=1, so d(2n) = d(2)·d(n) = 2·d(n). So 2n has TWICE as many divisors. Now if n is HCN, every m < n has d(m) < d(n). But 2n > n, so we can't directly use this. However, consider n/p where p is the smallest prime factor of n (if n is composite), or just 1 (if n is prime). Hmm. OK let me give up on finding a clean informal proof and just let the subagent try harder with a hint about n-1.
-/
set_option maxHeartbeats 800000 in
theorem hcn_even_or_one (n : ℕ) (hn : IsHighlyComposite n) (hn1 : n ≠ 1) :
    Even n := by
      by_contra h_odd;
      have := hn.2 2 ( by decide ) ?_ <;> simp_all +decide [ Nat.even_iff ];
      · -- Since $n$ is odd and greater than 1, we can write $n$ as $p^a * m$ where $p$ is an odd prime, $a \geq 1$, and $m$ is an integer not divisible by $p$.
        obtain ⟨p, a, m, hp, ha, hm⟩ : ∃ p a m, Nat.Prime p ∧ p ∣ n ∧ a ≥ 1 ∧ n = p^a * m ∧ ¬p ∣ m := by
          obtain ⟨ p, hp ⟩ := Nat.exists_prime_and_dvd hn1;
          exact ⟨ p, Nat.factorization n p, n / p ^ Nat.factorization n p, hp.1, hp.2, Nat.succ_le_of_lt ( Nat.pos_of_ne_zero ( Finsupp.mem_support_iff.mp ( by aesop ) ) ), by rw [ Nat.mul_div_cancel' ( Nat.ordProj_dvd _ _ ) ], Nat.not_dvd_ordCompl ( by aesop ) ( by aesop ) ⟩;
        -- Consider the number $n' = 2^{a} \cdot m$. We have $n' < n$ and $d(n') \geq d(n)$.
        have hn'_lt_n : 2^a * m < n := by
          rcases p with ( _ | _ | _ | p ) <;> simp_all +decide [ Nat.pow_succ', Nat.mul_assoc ];
          · omega;
          · exact mul_lt_mul_of_pos_right ( pow_lt_pow_left₀ ( by linarith ) ( by linarith ) ( by linarith ) ) ( Nat.pos_of_ne_zero ( by aesop_cat ) )
        have hn'_divisors : (Nat.divisors (2^a * m)).card ≥ (Nat.divisors n).card := by
          -- Since $p$ is an odd prime, we have $d(p^a) = a + 1$ and $d(2^a) = a + 1$.
          have h_divisors_p_a : (Nat.divisors (p^a)).card = a + 1 := by
            rw [ Nat.divisors_prime_pow hp, Finset.card_map, Finset.card_range ]
          have h_divisors_2_a : (Nat.divisors (2^a)).card = a + 1 := by
            norm_num [ Nat.divisors_prime_pow ];
          -- Since $p$ is an odd prime, we have $d(p^a \cdot m) = d(p^a) \cdot d(m)$ and $d(2^a \cdot m) = d(2^a) \cdot d(m)$.
          have h_divisors_product : (Nat.divisors (p^a * m)).card = (Nat.divisors (p^a)).card * (Nat.divisors m).card ∧ (Nat.divisors (2^a * m)).card = (Nat.divisors (2^a)).card * (Nat.divisors m).card := by
            have h_divisors_product : ∀ {x y : ℕ}, Nat.gcd x y = 1 → (Nat.divisors (x * y)).card = (Nat.divisors x).card * (Nat.divisors y).card := by
              grind +suggestions;
            exact ⟨ h_divisors_product <| Nat.Coprime.pow_left _ <| hp.coprime_iff_not_dvd.mpr hm.2.2, h_divisors_product <| Nat.Coprime.pow_left _ <| Nat.prime_two.coprime_iff_not_dvd.mpr <| by intro h; have := Nat.mod_eq_zero_of_dvd h; simp_all +decide [ Nat.mul_mod, Nat.pow_mod ] ⟩;
          aesop;
        exact not_lt_of_ge hn'_divisors ( hn.2 _ ( Nat.mul_pos ( pow_pos ( by decide ) _ ) ( Nat.pos_of_ne_zero ( by aesop_cat ) ) ) hn'_lt_n );
      · rcases n with ( _ | _ | _ | n ) <;> simp_all +arith +decide

/-- The factorizations of HCNs use the smallest primes: 2, 3, 5, 7, ...
    Computational evidence for small cases. -/
theorem hcn_12_factorization : 12 = 2 ^ 2 * 3 := by norm_num
theorem hcn_24_factorization : 24 = 2 ^ 3 * 3 := by norm_num
theorem hcn_60_factorization : 60 = 2 ^ 2 * 3 * 5 := by norm_num
theorem hcn_120_factorization : 120 = 2 ^ 3 * 3 * 5 := by norm_num
theorem hcn_360_factorization : 360 = 2 ^ 3 * 3 ^ 2 * 5 := by norm_num

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE 17: INFORMATION CONTENT OF LIGHT VS DARK PRIME SEQUENCES
    ═══════════════════════════════════════════════════════════════════════════

    Assign a binary sequence to the primes: 0 if dark, 1 if light.
    2 → ★ (twilight), 3 → 0, 5 → 1, 7 → 0, 11 → 0, 13 → 1, ...

    Question: What is the information content? If Dirichlet's theorem holds,
    light and dark are equally dense, so the binary string has maximal entropy
    — it looks "random." But the Chebyshev bias says it's slightly biased
    toward dark at finite scales.
-/

/-- The light/dark signature of the n-th prime (0 = dark, 1 = light, 2 = twilight).
    Using the first 15 primes: 2,3,5,7,11,13,17,19,23,29,31,37,41,43,47. -/
def primeSignature : ℕ → ℕ
  | 0 => 2  -- p=2: twilight
  | 1 => 0  -- p=3: dark (3 % 4 = 3)
  | 2 => 1  -- p=5: light (5 % 4 = 1)
  | 3 => 0  -- p=7: dark (7 % 4 = 3)
  | 4 => 0  -- p=11: dark (11 % 4 = 3)
  | 5 => 1  -- p=13: light (13 % 4 = 1)
  | 6 => 1  -- p=17: light (17 % 4 = 1)
  | 7 => 0  -- p=19: dark (19 % 4 = 3)
  | 8 => 0  -- p=23: dark (23 % 4 = 3)
  | 9 => 1  -- p=29: light (29 % 4 = 1)
  | 10 => 0 -- p=31: dark (31 % 4 = 3)
  | 11 => 1 -- p=37: light (37 % 4 = 1)
  | 12 => 1 -- p=41: light (41 % 4 = 1)
  | 13 => 0 -- p=43: dark (43 % 4 = 3)
  | 14 => 0 -- p=47: dark (47 % 4 = 3)
  | _ => 0

/-- Among the first 14 odd primes, 6 are light. -/
theorem light_fraction_14 :
    ((Finset.range 14).filter (fun i => primeSignature (i + 1) = 1)).card = 6 := by
  native_decide

/-- Among the first 14 odd primes, 8 are dark. Chebyshev bias! -/
theorem dark_fraction_14 :
    ((Finset.range 14).filter (fun i => primeSignature (i + 1) = 0)).card = 8 := by
  native_decide

/-- The light/dark binary sequence: 0,1,0,0,1,1,0,0,1,0,1,1,0,0 (for primes 3..47). -/
theorem light_dark_binary_sequence :
    (List.range 14).map (fun i => primeSignature (i + 1)) =
    [0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0] := by native_decide

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE 18: THE RIEMANN HYPOTHESIS AS EXPANSION RATE CONTROL
    ═══════════════════════════════════════════════════════════════════════════

    The Prime Number Theorem says π(x) ~ x/ln(x).
    The Riemann Hypothesis says the error is O(√x · ln(x)).

    In our metaphor:
    - PNT = the expansion rate is approximately logarithmic
    - RH = the fluctuations in expansion rate are bounded by √x

    The primes thin out logarithmically (space expands), and RH says
    this expansion is "smooth" — no sudden accelerations or decelerations
    beyond the square-root scale.
-/

/-- The prime counting function π(n). -/
def primeCountingFn (n : ℕ) : ℕ :=
  ((Finset.range (n + 1)).filter Nat.Prime).card

/-- π(10) = 4: primes are {2, 3, 5, 7}. -/
theorem pi_10 : primeCountingFn 10 = 4 := by native_decide

/-- π(100) = 25. -/
theorem pi_100 : primeCountingFn 100 = 25 := by native_decide

/-- π(1000) = 168. -/
theorem pi_1000 : primeCountingFn 1000 = 168 := by native_decide

/-- The prime counting function is monotone. -/
theorem primeCountingFn_mono {m n : ℕ} (h : m ≤ n) :
    primeCountingFn m ≤ primeCountingFn n := by
  unfold primeCountingFn
  apply Finset.card_le_card
  apply Finset.filter_subset_filter
  exact Finset.range_mono (by omega)

/-- The prime density π(n)/n decreases: evidence for logarithmic expansion.
    π(10)/10 = 0.4 > π(100)/100 = 0.25 > π(1000)/1000 = 0.168. -/
theorem expansion_rate_decreasing :
    (4 : ℚ) / 10 > (25 : ℚ) / 100 ∧
    (25 : ℚ) / 100 > (168 : ℚ) / 1000 := by
  constructor <;> norm_num

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE 19: QUADRATIC RECIPROCITY AS A LIGHT-DARK INTERACTION LAW
    ═══════════════════════════════════════════════════════════════════════════

    Quadratic reciprocity governs how two odd primes p, q "see" each other:
    whether p is a square mod q depends on whether q is a square mod p,
    with a sign flip when both p ≡ q ≡ 3 mod 4 (both dark).

    In our metaphor: When two photons (light primes) interact, their
    quadratic residue relationship is symmetric. When a photon meets
    dark matter, it's still symmetric. But when two dark primes meet,
    the relationship FLIPS — this is the dark-dark repulsion law.

    Formally: (p/q)(q/p) = (-1)^((p-1)/2 · (q-1)/2)

    The sign is -1 exactly when both p, q ≡ 3 mod 4 (both dark).
-/

/-- Quadratic reciprocity from Mathlib. -/
theorem quadratic_reciprocity_law (p q : ℕ) [Fact p.Prime] [Fact q.Prime]
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) (hpq : p ≠ q) :
    legendreSym q p * legendreSym p q = (-1 : ℤ) ^ (p / 2 * (q / 2)) :=
  legendreSym.quadratic_reciprocity hp2 hq2 hpq

/-
PROBLEM
When both primes are light (≡ 1 mod 4), the interaction is symmetric:
    (p-1)/2 is even, so (-1)^((p-1)/2 · (q-1)/2) = 1.

PROVIDED SOLUTION
By quadratic_reciprocity_law, legendreSym q p * legendreSym p q = (-1)^(p/2 * (q/2)). Since p % 4 = 1, we have p = 4k+1 for some k, so p/2 = 2k which is even. Thus p/2 * (q/2) is even (since p/2 is even). So (-1)^(even) = 1.
-/
theorem light_light_symmetric (p q : ℕ) [Fact p.Prime] [Fact q.Prime]
    (hp : p % 4 = 1) (hq : q % 4 = 1)
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) (hpq : p ≠ q) :
    legendreSym q p * legendreSym p q = 1 := by
      rw [ quadratic_reciprocity_law p q hp2 hq2 hpq ];
      rw [ ← Nat.mod_add_div p 4, ← Nat.mod_add_div q 4, hp, hq ] ; norm_num [ Nat.even_div ] ;

/-
PROBLEM
When one is light and one dark, interaction is still symmetric:
    one of (p-1)/2, (q-1)/2 is even, so the product exponent is even.

PROVIDED SOLUTION
By quadratic_reciprocity_law, legendreSym q p * legendreSym p q = (-1)^(p/2 * (q/2)). Since p % 4 = 1, p/2 is even. So p/2 * (q/2) is even. Thus (-1)^(even) = 1.
-/
theorem light_dark_symmetric (p q : ℕ) [Fact p.Prime] [Fact q.Prime]
    (hp : p % 4 = 1) (hq : q % 4 = 3)
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) (hpq : p ≠ q) :
    legendreSym q p * legendreSym p q = 1 := by
      rw [ quadratic_reciprocity_law p q hp2 hq2 hpq ];
      norm_num [ show p / 2 = 2 * ( p / 4 ) by omega, show q / 2 = 2 * ( q / 4 ) + 1 by omega ]

/-
PROBLEM
When both primes are dark (≡ 3 mod 4), the interaction FLIPS:
    both (p-1)/2 and (q-1)/2 are odd, so (-1)^(odd·odd) = -1.

PROVIDED SOLUTION
By quadratic_reciprocity_law, legendreSym q p * legendreSym p q = (-1)^(p/2 * (q/2)). Since p % 4 = 3, p = 4k+3 for some k, so p/2 = 2k+1 which is odd. Similarly q/2 is odd. So p/2 * q/2 is odd. Thus (-1)^(odd) = -1.
-/
theorem dark_dark_repulsion (p q : ℕ) [Fact p.Prime] [Fact q.Prime]
    (hp : p % 4 = 3) (hq : q % 4 = 3)
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) (hpq : p ≠ q) :
    legendreSym q p * legendreSym p q = -1 := by
      convert quadratic_reciprocity_law p q hp2 hq2 hpq using 1 ; ring;
      rw [ ← Nat.mod_add_div p 4, ← Nat.mod_add_div q 4, hp, hq ] ; ring;
      norm_num [ Nat.add_div, Nat.mul_div_assoc, Nat.mul_mod, Nat.add_mod, Nat.pow_mod ]

/-- Computational verification: 3 and 7 are both dark, and (3/7)·(7/3) = -1. -/
theorem dark_dark_3_7 :
    haveI : Fact (Nat.Prime 3) := ⟨by norm_num⟩
    haveI : Fact (Nat.Prime 7) := ⟨by norm_num⟩
    legendreSym 7 3 * legendreSym 3 7 = -1 := by native_decide

/-- Computational verification: 5 and 13 are both light, and (5/13)·(13/5) = 1. -/
theorem light_light_5_13 :
    haveI : Fact (Nat.Prime 5) := ⟨by norm_num⟩
    haveI : Fact (Nat.Prime 13) := ⟨by norm_num⟩
    legendreSym 13 5 * legendreSym 5 13 = 1 := by native_decide

/-- Computational verification: 5 (light) and 7 (dark), (5/7)·(7/5) = 1. -/
theorem light_dark_5_7 :
    haveI : Fact (Nat.Prime 5) := ⟨by norm_num⟩
    haveI : Fact (Nat.Prime 7) := ⟨by norm_num⟩
    legendreSym 7 5 * legendreSym 5 7 = 1 := by native_decide

/-- Computational verification: 3 and 11 are both dark, and (3/11)·(11/3) = -1. -/
theorem dark_dark_3_11 :
    haveI : Fact (Nat.Prime 3) := ⟨by norm_num⟩
    haveI : Fact (Nat.Prime 11) := ⟨by norm_num⟩
    legendreSym 11 3 * legendreSym 3 11 = -1 := by native_decide

/-! ═══════════════════════════════════════════════════════════════════════════
    CYCLE ∞: THE UNIVERSE COMPUTES ITSELF
    ═══════════════════════════════════════════════════════════════════════════

    The research process converges to a fixed point.
    The oracle validates itself. The universe is its own proof.
-/

/-- A universe is a self-referential system: a space of states with a
    dynamics that has a fixed point (the ground state). -/
structure SelfComputingUniverse (S : Type*) where
  dynamics : S → S
  groundState : S
  isFixedPoint : dynamics groundState = groundState
  attracts : ∀ s, ∃ n : ℕ, dynamics^[n] s = groundState

/-- The trivial universe: a single state that maps to itself. -/
def trivialUniverse : SelfComputingUniverse Unit where
  dynamics := id
  groundState := ()
  isFixedPoint := rfl
  attracts := fun _ => ⟨0, rfl⟩

/-- A Boolean universe with two states: Light (true) and Dark (false).
    Dynamics: everything → Dark (the heat death). -/
def booleanUniverse : SelfComputingUniverse Bool where
  dynamics := fun _ => false
  groundState := false
  isFixedPoint := rfl
  attracts := fun _ => ⟨1, rfl⟩

/-- The research oracle is a self-computing universe:
    hypotheses are validated iteratively until stable knowledge emerges.
    An idempotent function reaches a fixed point after one step. -/
theorem research_is_universe {H : Type*} (R : { f : H → H // ∀ h, f (f h) = f h })
    (h₀ : H) :
    R.1 (R.1 h₀) = R.1 h₀ :=
  R.2 h₀

/-- Grand Synthesis Theorem: The number line encodes a complete physics.
    Every natural number participates in the light/dark/gravity/expansion framework. -/
theorem grand_synthesis (n : ℕ) (hn : 2 ≤ n) :
    -- n has a prime factor (enters the light/dark classification)
    (∃ p, p.Prime ∧ p ∣ n) ∧
    -- n has a definite gravitational weight
    (0 < n.divisors.card) ∧
    -- n participates in entanglement (sum-of-squares relations)
    (∃ m k : ℕ, n + m = k ^ 2) := by
  refine ⟨?_, ?_, ?_⟩
  · exact Nat.exists_prime_and_dvd (by omega)
  · exact Finset.card_pos.mpr ⟨1, Nat.one_mem_divisors.mpr (by omega)⟩
  · refine ⟨(n + 1) ^ 2 - n, n + 1, ?_⟩
    have h1 : n ≤ (n + 1) ^ 2 := by nlinarith
    omega

end