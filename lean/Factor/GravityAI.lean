import Mathlib

/-!
# Gravity-Powered AI: Iterative Research Engine

A formally verified research system that:
1. **Proposes hypotheses** as Lean theorem statements
2. **Runs experiments** via computational definitions and checks
3. **Validates data** through machine-verified proofs
4. **Brainstorms new hypotheses** derived from proven results
5. **Iterates forever** — each cycle's output feeds the next cycle's input

## Core Principle

Gravity is an **idempotent oracle**: O(O(x)) = O(x). This single equation
drives the entire research program. Every cycle explores a consequence.
-/

open Real Finset BigOperators Set Function

noncomputable section

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 0: Foundation — The Oracle Axiom
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle0

/-- An oracle is an idempotent endofunction. -/
structure Oracle (X : Type*) where
  op : X → X
  idem : ∀ x, op (op x) = op x

/-- The truth set: fixed points of the oracle. -/
def Oracle.truthSet {X : Type*} (O : Oracle X) : Set X :=
  {x | O.op x = x}

theorem Oracle.output_is_truth {X : Type*} (O : Oracle X) (x : X) :
    O.op x ∈ O.truthSet := O.idem x

theorem Oracle.is_retraction {X : Type*} (O : Oracle X) :
    (∀ x, O.op x ∈ O.truthSet) ∧ (∀ x ∈ O.truthSet, O.op x = x) :=
  ⟨fun x => O.idem x, fun x hx => hx⟩

theorem Oracle.truthSet_eq_range {X : Type*} (O : Oracle X) :
    O.truthSet = range O.op := by
  ext y; constructor
  · intro hy; exact ⟨y, hy⟩
  · rintro ⟨x, rfl⟩; exact O.idem x

theorem Oracle.iterate_eq {X : Type*} (O : Oracle X) (n : ℕ) (hn : 1 ≤ n) (x : X) :
    O.op^[n] x = O.op x := by
  induction n with
  | zero => omega
  | succ n ih =>
    rw [Function.iterate_succ_apply']
    by_cases h : n = 0
    · subst h; simp
    · rw [ih (by omega)]; exact O.idem x

theorem Oracle.one_query {X : Type*} (O : Oracle X) (x : X) :
    O.op x ∈ O.truthSet ∧ ∀ n, 1 ≤ n → O.op^[n] x = O.op x :=
  ⟨O.output_is_truth x, fun n hn => O.iterate_eq n hn x⟩

end Cycle0

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 1: Compression
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle1

theorem identity_no_compression {X : Type*} :
    (⟨id, fun _ => rfl⟩ : Oracle X).truthSet = Set.univ := by
  ext x; simp [Oracle.truthSet]

theorem constant_oracle_singleton {X : Type*} (c : X) :
    (⟨fun _ => c, fun _ => rfl⟩ : Oracle X).truthSet = {c} := by
  ext x; simp [Oracle.truthSet]

theorem Oracle.truth_set_le_input {X : Type*} [Fintype X] [DecidableEq X]
    (O : Oracle X) [DecidablePred (· ∈ O.truthSet)] :
    Fintype.card O.truthSet ≤ Fintype.card X :=
  Fintype.card_subtype_le _

end Cycle1

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 2: Light Cone Geometry
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle2

structure MinkowskiEvent where
  x : ℝ
  y : ℝ
  t : ℝ

def MinkowskiEvent.quadForm (e : MinkowskiEvent) : ℝ :=
  e.x ^ 2 + e.y ^ 2 - e.t ^ 2

def MinkowskiEvent.isNull (e : MinkowskiEvent) : Prop := e.quadForm = 0

theorem null_iff_pythagorean (e : MinkowskiEvent) :
    e.isNull ↔ e.x ^ 2 + e.y ^ 2 = e.t ^ 2 := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm]
  constructor <;> intro h <;> linarith

theorem light_cone_scaling (e : MinkowskiEvent) (s : ℝ) (h : e.isNull) :
    (⟨s * e.x, s * e.y, s * e.t⟩ : MinkowskiEvent).isNull := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm] at *
  nlinarith [sq_nonneg s]

theorem origin_is_null : (⟨0, 0, 0⟩ : MinkowskiEvent).isNull := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm]

theorem photon_345 : (⟨3, 4, 5⟩ : MinkowskiEvent).isNull := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm]; norm_num

theorem photon_51213 : (⟨5, 12, 13⟩ : MinkowskiEvent).isNull := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm]; norm_num

theorem parametric_photon (m n : ℝ) :
    (⟨m ^ 2 - n ^ 2, 2 * m * n, m ^ 2 + n ^ 2⟩ : MinkowskiEvent).isNull := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm]; ring

def minkowskiInner (e₁ e₂ : MinkowskiEvent) : ℝ :=
  e₁.x * e₂.x + e₁.y * e₂.y - e₁.t * e₂.t

theorem null_self_orthogonal (e : MinkowskiEvent) (h : e.isNull) :
    minkowskiInner e e = 0 := by
  simp [minkowskiInner, MinkowskiEvent.isNull, MinkowskiEvent.quadForm] at *
  nlinarith

theorem sum_null_iff_orthogonal (e₁ e₂ : MinkowskiEvent)
    (h₁ : e₁.isNull) (h₂ : e₂.isNull) :
    (⟨e₁.x + e₂.x, e₁.y + e₂.y, e₁.t + e₂.t⟩ : MinkowskiEvent).isNull ↔
    minkowskiInner e₁ e₂ = 0 := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm, minkowskiInner] at *
  constructor <;> intro h <;> nlinarith

end Cycle2

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 3: Entropic Gravity
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle3

structure BlackHole where
  mass : ℝ
  mass_pos : 0 < mass

def BlackHole.horizonArea (bh : BlackHole) : ℝ := 16 * π * bh.mass ^ 2
def BlackHole.entropy (bh : BlackHole) : ℝ := 4 * π * bh.mass ^ 2
def BlackHole.temperature (bh : BlackHole) : ℝ := 1 / (8 * π * bh.mass)

/-
PROVIDED SOLUTION
Unfold horizonArea to get 16 * π * bh.mass ^ 2. Use bh.mass_pos and pi_pos, then positivity or mul_pos.
-/
theorem BlackHole.horizonArea_pos (bh : BlackHole) :
    0 < bh.horizonArea := by
  exact mul_pos ( mul_pos ( by norm_num ) Real.pi_pos ) ( sq_pos_of_pos bh.mass_pos )

/-
PROVIDED SOLUTION
Unfold entropy to 4 * π * bh.mass ^ 2. Use bh.mass_pos and pi_pos, then mul_pos or positivity.
-/
theorem BlackHole.entropy_pos (bh : BlackHole) :
    0 < bh.entropy := by
  exact mul_pos ( mul_pos zero_lt_four Real.pi_pos ) ( sq_pos_of_pos bh.mass_pos )

/-
PROVIDED SOLUTION
Unfold temperature to 1 / (8 * π * bh.mass). Use div_pos one_pos and mul_pos with pi_pos and mass_pos.
-/
theorem BlackHole.temperature_pos (bh : BlackHole) :
    0 < bh.temperature := by
  exact one_div_pos.mpr ( mul_pos ( mul_pos ( by norm_num ) Real.pi_pos ) bh.mass_pos )

theorem BlackHole.entropy_eq_area_div_4 (bh : BlackHole) :
    bh.entropy = bh.horizonArea / 4 := by
  simp [entropy, horizonArea]; ring

/-
PROVIDED SOLUTION
Unfold entropy. The goal becomes 4*π*M1^2 + 4*π*M2^2 ≤ 4*π*(M1+M2)^2. Factor out 4π and expand. The difference is 8*π*M1*M2 ≥ 0, which follows from mass_pos.
-/
theorem BlackHole.second_law (bh₁ bh₂ : BlackHole) :
    bh₁.entropy + bh₂.entropy ≤
    (⟨bh₁.mass + bh₂.mass, by linarith [bh₁.mass_pos, bh₂.mass_pos]⟩ : BlackHole).entropy := by
  unfold BlackHole.entropy; ring_nf; norm_num;
  exact mul_nonneg ( mul_nonneg Real.pi_pos.le bh₁.mass_pos.le ) bh₂.mass_pos.le

/-
PROVIDED SOLUTION
Temperature is 1/(8πM). If M1 < M2 then 8πM1 < 8πM2 (by mul_lt_mul_of_pos_left), so 1/(8πM2) < 1/(8πM1). Use one_div_lt_one_div_of_lt or div_lt_div_of_pos_left.
-/
theorem BlackHole.smaller_is_hotter (bh₁ bh₂ : BlackHole)
    (h : bh₁.mass < bh₂.mass) :
    bh₂.temperature < bh₁.temperature := by
  exact one_div_lt_one_div_of_lt ( mul_pos ( mul_pos ( by norm_num ) Real.pi_pos ) bh₁.mass_pos ) ( mul_lt_mul_of_pos_left h ( by positivity ) )

/-
PROVIDED SOLUTION
Entropy is 4*π*M^2. If M1 ≤ M2 then M1^2 ≤ M2^2 (since both positive), so 4π*M1^2 ≤ 4π*M2^2. Use mul_le_mul_of_nonneg_left.
-/
theorem BlackHole.larger_more_entropy (bh₁ bh₂ : BlackHole)
    (h : bh₁.mass ≤ bh₂.mass) :
    bh₁.entropy ≤ bh₂.entropy := by
  exact mul_le_mul_of_nonneg_left ( pow_le_pow_left₀ ( le_of_lt bh₁.mass_pos ) h 2 ) ( by positivity )

theorem redshift_positive (M r : ℝ) (hr : 0 < r) (hMr : 2 * M < r) :
    0 < 1 - 2 * M / r := by
  rw [sub_pos, div_lt_one hr]; linarith

end Cycle3

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 4: Oracle Algebra
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle4

def Oracle.commutes {X : Type*} (O₁ O₂ : Oracle X) : Prop :=
  ∀ x, O₁.op (O₂.op x) = O₂.op (O₁.op x)

/-
PROVIDED SOLUTION
Goal: O1(O2(O1(O2(x)))) = O1(O2(x)). Use hcomm to rewrite the inner O1(O2(x)) to O2(O1(x)), getting O1(O2(O2(O1(x)))). Then use O2.idem on O2(O2(O1(x))) to get O2(O1(x)). Then use hcomm backwards on O1(O2(O1(x))) to get back O1(O2(x)). Actually simpler: use conv to rewrite the 2nd-innermost application.
-/
theorem Oracle.comp_of_commuting {X : Type*} (O₁ O₂ : Oracle X)
    (hcomm : O₁.commutes O₂) :
    ∀ x, O₁.op (O₂.op (O₁.op (O₂.op x))) = O₁.op (O₂.op x) := by
  intro x;
  rw [ ← hcomm, O₂.idem, hcomm ];
  rw [ ← hcomm, O₁.idem ]

def Oracle.setoid {X : Type*} (O : Oracle X) : Setoid X where
  r x y := O.op x = O.op y
  iseqv := ⟨fun _ => rfl, fun h => h.symm, fun h1 h2 => h1.trans h2⟩

def OracleEquiv {X : Type*} (O₁ O₂ : Oracle X) : Prop :=
  O₁.truthSet = O₂.truthSet

end Cycle4

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 5: Geodesic Gradient Descent — Gravity for AI
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle5

def vanillaStep (eta grad theta : ℝ) : ℝ := theta - eta * grad
def naturalStep (eta grad g theta : ℝ) : ℝ := theta - eta * (grad / g)

/-- Natural gradient is covariant: scaling gradient by alpha and metric by alpha
    rescales the step by 1. (The correct covariance uses alpha in both.) -/
theorem natural_gradient_invariant (eta grad g alpha : ℝ)
    (halpha : alpha ≠ 0) (_hg : g ≠ 0) (theta : ℝ) :
    naturalStep eta (alpha * grad) (alpha * g) theta =
    naturalStep eta grad g theta := by
  simp [naturalStep, mul_div_mul_left _ _ halpha]

theorem geodesic_oracle_at_critical (eta g theta : ℝ) :
    naturalStep eta 0 g (naturalStep eta 0 g theta) = naturalStep eta 0 g theta := by
  simp [naturalStep]

end Cycle5

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 6: Holographic Neural Networks
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle6

structure TwoLayerNet (input hidden output : ℕ) where
  layer1 : Fin input → Fin hidden
  layer2 : Fin hidden → Fin output

def TwoLayerNet.forward {i h o : ℕ} (net : TwoLayerNet i h o) : Fin i → Fin o :=
  net.layer2 ∘ net.layer1

/-
PROVIDED SOLUTION
The range of net.forward = range (net.layer2 ∘ net.layer1) ⊆ range net.layer2. So card(range net.forward) ≤ card(range net.layer2) ≤ card(Fin h) = h. Use Set.range_comp_subset_range and Fintype.card_le_of_surjective or Set.Finite.toFinset_mono.
-/
theorem bottleneck_compression {i h o : ℕ} (net : TwoLayerNet i h o) :
    Fintype.card (range net.forward) ≤ h := by
  rw [ Fintype.card_ofFinset ];
  refine' le_trans ( Finset.card_le_card ( show Finset.image ( net.forward ∘ PLift.down ) Finset.univ ⊆ Finset.image ( net.layer2 ∘ PLift.down ) Finset.univ from _ ) ) _;
  · intro x hx; aesop;
  · exact Finset.card_image_le.trans ( by simpa )

end Cycle6

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 7: The Numbers-Light-Gravity Triangle
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle7

theorem numbers_to_light (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (⟨(a : ℝ), (b : ℝ), (c : ℝ)⟩ : MinkowskiEvent).isNull := by
  rw [null_iff_pythagorean]; push_cast; exact_mod_cast h

theorem numbers_to_gravity : ∀ n : ℤ, ⌊(n : ℝ)⌋ = n :=
  fun n => Int.floor_intCast n

theorem photon_multiplication (a1 b1 a2 b2 : ℤ) :
    (a1 ^ 2 + b1 ^ 2) * (a2 ^ 2 + b2 ^ 2) =
    (a1 * a2 - b1 * b2) ^ 2 + (a1 * b2 + b1 * a2) ^ 2 := by ring

theorem light_cone_closed_mul (a1 b1 c1 a2 b2 c2 : ℤ)
    (h1 : a1 ^ 2 + b1 ^ 2 = c1 ^ 2) (h2 : a2 ^ 2 + b2 ^ 2 = c2 ^ 2) :
    (a1 * a2 - b1 * b2) ^ 2 + (a1 * b2 + b1 * a2) ^ 2 = (c1 * c2) ^ 2 := by
  nlinarith [photon_multiplication a1 b1 a2 b2]

end Cycle7

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 8: Information Bounds
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle8

def bekensteinBound (R E : ℝ) : ℝ := 2 * π * R * E

theorem bekenstein_nonneg (R E : ℝ) (hR : 0 ≤ R) (hE : 0 ≤ E) :
    0 ≤ bekensteinBound R E := by
  unfold bekensteinBound; positivity

theorem bekenstein_radius_scaling (R E : ℝ) :
    bekensteinBound (2 * R) E = 2 * bekensteinBound R E := by
  unfold bekensteinBound; ring

def holographicBound (A : ℝ) : ℝ := A / 4

theorem holographic_sphere (R : ℝ) :
    holographicBound (4 * π * R ^ 2) = π * R ^ 2 := by
  unfold holographicBound; ring

/-
PROVIDED SOLUTION
We need π*R^2 < (4/3)*π*R^3 when R > 3. Divide both sides by π*R^2 (positive) to get 1 < (4/3)*R, i.e., R > 3/4, which holds since R > 3. Use nlinarith with pi_pos and sq_nonneg.
-/
theorem holographic_beats_volume (R : ℝ) (hR : 3 < R) :
    π * R ^ 2 < (4 / 3) * π * R ^ 3 := by
  nlinarith [ Real.pi_pos, mul_le_mul_of_nonneg_left hR.le Real.pi_pos.le, pow_pos ( sub_pos.mpr hR ) 2 ]

end Cycle8

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 9: Fixed Point Theory — Strange Loop
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle9

theorem universe_fixed_point {X : Type*} (O : Oracle X) (U : X)
    (hU : U ∈ O.truthSet) : O.op U = U := hU

theorem strange_loop {X : Type*} (O : Oracle X) :
    ∀ x ∈ O.truthSet, O.op x = x := fun _ hx => hx

theorem oracle_determined_by_truth {X : Type*} (O1 O2 : Oracle X)
    (h : O1.truthSet = O2.truthSet) :
    ∀ x ∈ O1.truthSet, O2.op (O1.op x) = O1.op x := by
  intro x _
  have : O1.op x ∈ O1.truthSet := O1.output_is_truth x
  rw [h] at this; exact this

def oracleLE {X : Type*} (O1 O2 : Oracle X) : Prop :=
  O1.truthSet ⊆ O2.truthSet

theorem identity_oracle_top {X : Type*} (O : Oracle X) :
    oracleLE O ⟨id, fun _ => rfl⟩ := by
  intro x _; simp [Oracle.truthSet]

theorem double_oracle_same_truth {X : Type*} (O : Oracle X) :
    (⟨O.op ∘ O.op, fun x => by
      show O.op (O.op (O.op (O.op x))) = O.op (O.op x)
      rw [O.idem, O.idem]⟩ : Oracle X).truthSet = O.truthSet := by
  ext x
  simp only [Oracle.truthSet, Set.mem_setOf_eq, comp]
  constructor
  · intro h
    -- h : O.op (O.op x) = x
    have h2 := O.idem x
    -- O.op (O.op x) = O.op x, and O.op (O.op x) = x
    rw [h] at h2; exact h2.symm
  · intro h
    -- h : O.op x = x
    rw [h, h]

end Cycle9

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 10: Gravitational Factoring
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle10

def isSumOfTwoSquares (n : ℕ) : Prop := ∃ a b : ℕ, a ^ 2 + b ^ 2 = n

theorem zero_sos : isSumOfTwoSquares 0 := ⟨0, 0, by norm_num⟩
theorem one_sos : isSumOfTwoSquares 1 := ⟨0, 1, by norm_num⟩
theorem two_sos : isSumOfTwoSquares 2 := ⟨1, 1, by norm_num⟩
theorem five_sos : isSumOfTwoSquares 5 := ⟨1, 2, by norm_num⟩
theorem twentyfive_sos : isSumOfTwoSquares 25 := ⟨3, 4, by norm_num⟩

/-
PROVIDED SOLUTION
Use Brahmagupta-Fibonacci identity: (a1^2+b1^2)(a2^2+b2^2) = (a1*a2-b1*b2)^2 + (a1*b2+b1*a2)^2. The witnesses are |a1*a2 - b1*b2| and a1*b2 + b1*a2. Use Nat subtraction with cases on whether a1*a2 ≤ b1*b2, then verify by zify and ring.
-/
theorem sos_mul (m n : ℕ) (hm : isSumOfTwoSquares m) (hn : isSumOfTwoSquares n) :
    isSumOfTwoSquares (m * n) := by
      -- By the identity $(a^2 + b^2)(c^2 + d^2) = (ac - bd)^2 + (ad + bc)^2$, we can conclude that $m * n$ is a sum of two squares.
      obtain ⟨a, b, hab⟩ := hm
      obtain ⟨c, d, hcd⟩ := hn
      use Int.natAbs (a * c - b * d), Int.natAbs (a * d + b * c);
      norm_num [ ← @Nat.cast_inj ℤ ] ; nlinarith

theorem square_sos (n : ℕ) : isSumOfTwoSquares (n ^ 2) := ⟨0, n, by ring⟩

theorem degenerate_light_cone (n : ℕ) :
    (⟨0, (n : ℝ), (n : ℝ)⟩ : MinkowskiEvent).isNull := by
  simp [MinkowskiEvent.isNull, MinkowskiEvent.quadForm]

end Cycle10

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 11: Discrete Ricci Flow
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle11

structure WeightedGraph (n : ℕ) where
  weight : Fin n → Fin n → ℝ
  weight_nonneg : ∀ i j, 0 ≤ weight i j
  weight_symm : ∀ i j, weight i j = weight j i

def WeightedGraph.degree {n : ℕ} (G : WeightedGraph n) (i : Fin n) : ℝ :=
  ∑ j, G.weight i j

theorem WeightedGraph.degree_nonneg {n : ℕ} (G : WeightedGraph n) (i : Fin n) :
    0 ≤ G.degree i :=
  Finset.sum_nonneg (fun j _ => G.weight_nonneg i j)

theorem WeightedGraph.totalWeight_eq_sum_degree {n : ℕ} (G : WeightedGraph n) :
    ∑ i, ∑ j, G.weight i j = ∑ i, G.degree i := by
  simp [WeightedGraph.degree]

end Cycle11

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 12: Oracle Metrics
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle12

def compressionDistortion {n : ℕ} (O : Oracle (Fin n)) (d : Fin n → Fin n → ℝ) : ℝ :=
  (∑ i : Fin n, d i (O.op i)) / n

theorem zero_distortion_on_truth {n : ℕ} (O : Oracle (Fin n))
    (d : Fin n → Fin n → ℝ) (hd : ∀ x, d x x = 0)
    (x : Fin n) (hx : x ∈ O.truthSet) :
    d x (O.op x) = 0 := by rw [hx]; exact hd x

theorem identity_zero_distortion {n : ℕ} (d : Fin n → Fin n → ℝ)
    (hd : ∀ x, d x x = 0) :
    compressionDistortion ⟨id, fun _ => rfl⟩ d = 0 := by
  simp [compressionDistortion, hd]

end Cycle12

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 13: Gravitational Lensing
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle13

def deflectionAngle (M b : ℝ) : ℝ := 4 * M / b

theorem deflection_pos (M b : ℝ) (hM : 0 < M) (hb : 0 < b) :
    0 < deflectionAngle M b := by unfold deflectionAngle; positivity

def einsteinRingRadius (M D : ℝ) : ℝ := Real.sqrt (4 * M / D)

theorem einstein_ring_monotone (M1 M2 D : ℝ)
    (hD : 0 < D) (hM : M1 ≤ M2) :
    einsteinRingRadius M1 D ≤ einsteinRingRadius M2 D := by
  unfold einsteinRingRadius
  apply Real.sqrt_le_sqrt
  apply div_le_div_of_nonneg_right _ (le_of_lt hD)
  linarith

end Cycle13

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 14: The Oracle Spectrum
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle14

theorem idempotent_eigenvalue {K : Type*} [Field K] {V : Type*}
    [AddCommGroup V] [Module K V]
    (P : V →ₗ[K] V) (hP : P ∘ₗ P = P)
    (v : V) (mu : K) (hv : v ≠ 0) (heig : P v = mu • v) :
    mu = 0 ∨ mu = 1 := by
  have h1 : P (P v) = P v := by rw [← LinearMap.comp_apply, hP]
  rw [heig, LinearMap.map_smul, heig] at h1
  have h2 : (mu * mu - mu) • v = 0 := by
    rw [sub_smul, mul_smul]; exact sub_eq_zero.mpr h1
  have h3 : mu * mu - mu = 0 := (smul_eq_zero.mp h2).resolve_right hv
  have h4 : mu * (mu - 1) = 0 := by rwa [mul_sub, mul_one]
  exact (mul_eq_zero.mp h4).imp id sub_eq_zero.mp

theorem idempotent_kernel_part {K : Type*} [Field K] {V : Type*}
    [AddCommGroup V] [Module K V]
    (P : V →ₗ[K] V) (hP : P ∘ₗ P = P) (v : V) :
    P (v - P v) = 0 := by
  rw [map_sub, ← LinearMap.comp_apply, hP]; simp

theorem idempotent_image_fixed {K : Type*} [Field K] {V : Type*}
    [AddCommGroup V] [Module K V]
    (P : V →ₗ[K] V) (hP : P ∘ₗ P = P) (v : V) :
    P (P v) = P v := by rw [← LinearMap.comp_apply, hP]

theorem measurement_binary {K : Type*} [Field K] {V : Type*}
    [AddCommGroup V] [Module K V]
    (P : V →ₗ[K] V) (hP : P ∘ₗ P = P) (v : V) (hv : v ≠ 0) (mu : K)
    (heig : P v = mu • v) :
    (mu = 0 ∧ P v = 0) ∨ (mu = 1 ∧ P v = v) := by
  rcases idempotent_eigenvalue P hP v mu hv heig with h | h
  · left; exact ⟨h, by rw [heig, h, zero_smul]⟩
  · right; exact ⟨h, by rw [heig, h, one_smul]⟩

end Cycle14

/-! ═══════════════════════════════════════════════════════════════════════════
    RESEARCH CYCLE 15: Iterate Forever — The Meta-Oracle
    ═══════════════════════════════════════════════════════════════════════════ -/

section Cycle15

theorem meta_oracle_stable {X : Type*} (O : Oracle X) :
    ∀ x, O.op (O.op (O.op x)) = O.op x := by
  intro x; rw [O.idem (O.op x)]; exact O.idem x

theorem research_converges {X : Type*} (O : Oracle X) (n : ℕ) (hn : 1 ≤ n) :
    ∀ x, O.op^[n] x = O.op x := O.iterate_eq n hn

theorem gravity_ai_axiom {X : Type*} (O : Oracle X) :
    (⟨O.op ∘ O.op, fun x => by
      show O.op (O.op (O.op (O.op x))) = O.op (O.op x)
      rw [O.idem, O.idem]⟩ : Oracle X).truthSet = O.truthSet := by
  ext x; simp only [Oracle.truthSet, Set.mem_setOf_eq, comp]
  constructor
  · intro h; have := O.idem x; rw [h] at this; exact this.symm
  · intro h; rw [h, h]

/-- **The Grand Theorem**: Every oracle is a gravitational truth-finder. -/
theorem grand_unification {X : Type*} (O : Oracle X) :
    (∀ x, O.op x ∈ range O.op) ∧
    (∀ x, O.op (O.op x) = O.op x) ∧
    (∀ x ∈ O.truthSet, O.op x = x) ∧
    (∀ n, 1 ≤ n → ∀ x, O.op^[n] x = O.op x) :=
  ⟨fun x => ⟨x, rfl⟩, O.idem, fun _ h => h, fun n hn x => O.iterate_eq n hn x⟩

end Cycle15

end