import Mathlib

/-!
# Photon Research Round 4: Berggren Trees, Möbius Actions, and Photon Statistics

## Research Team: Photon Collective — Round 4

This round investigates the open questions from the research paper:
1. **The Berggren tree as a quantum circuit** (Open Question 6)
2. **Photon factorization and the Möbius group** (Open Question 2)
3. **Asymptotic photon counting** (Open Question 4)
4. **Spin networks on the light cone** (Open Question 3)
-/

open Finset BigOperators

/-! ## Part I: Berggren Matrix Theory -/

/-- A Pythagorean triple (integer version) -/
def IsPythTriple' (a b c : ℤ) : Prop := a ^ 2 + b ^ 2 = c ^ 2

/-- Berggren matrix A action on a triple -/
def berggrenA (a b c : ℤ) : ℤ × ℤ × ℤ :=
  (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

/-- Berggren matrix B action on a triple -/
def berggrenB (a b c : ℤ) : ℤ × ℤ × ℤ :=
  (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

/-- Berggren matrix C action on a triple -/
def berggrenC (a b c : ℤ) : ℤ × ℤ × ℤ :=
  (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

/-- Berggren matrix A preserves the Pythagorean property -/
theorem berggrenA_preserves_pyth (a b c : ℤ) (h : IsPythTriple' a b c) :
    let t := berggrenA a b c
    IsPythTriple' t.1 t.2.1 t.2.2 := by
  simp only [berggrenA, IsPythTriple'] at *; nlinarith [h]

/-- Berggren matrix B preserves the Pythagorean property -/
theorem berggrenB_preserves_pyth (a b c : ℤ) (h : IsPythTriple' a b c) :
    let t := berggrenB a b c
    IsPythTriple' t.1 t.2.1 t.2.2 := by
  simp only [berggrenB, IsPythTriple'] at *; nlinarith [h]

/-- Berggren matrix C preserves the Pythagorean property -/
theorem berggrenC_preserves_pyth (a b c : ℤ) (h : IsPythTriple' a b c) :
    let t := berggrenC a b c
    IsPythTriple' t.1 t.2.1 t.2.2 := by
  simp only [berggrenC, IsPythTriple'] at *; nlinarith [h]

/-- (3,4,5) is the root of the Berggren tree -/
theorem base_triple_pyth : IsPythTriple' 3 4 5 := by
  unfold IsPythTriple'; ring

/-- Berggren A applied to (3,4,5) gives (5,12,13) -/
theorem berggrenA_base : berggrenA 3 4 5 = (5, 12, 13) := by native_decide

/-- Berggren B applied to (3,4,5) gives (21,20,29) -/
theorem berggrenB_base : berggrenB 3 4 5 = (21, 20, 29) := by native_decide

/-- Berggren C applied to (3,4,5) gives (15,8,17) -/
theorem berggrenC_base : berggrenC 3 4 5 = (15, 8, 17) := by native_decide

/-- Berggren A increases the hypotenuse for positive triples -/
theorem berggrenA_hypotenuse_grows (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : IsPythTriple' a b c) :
    c < (berggrenA a b c).2.2 := by
  simp only [berggrenA, IsPythTriple'] at *; nlinarith [sq_nonneg a, sq_nonneg b, sq_nonneg c]

/-- Berggren B increases the hypotenuse for positive triples -/
theorem berggrenB_hypotenuse_grows (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : IsPythTriple' a b c) :
    c < (berggrenB a b c).2.2 := by
  simp only [berggrenB, IsPythTriple'] at *; nlinarith

/-- The Berggren matrices preserve the Minkowski form Q = a² + b² - c².
    This means they are discrete Lorentz transformations. -/
theorem berggren_preserves_minkowski_form (a b c : ℤ) :
    let tA := berggrenA a b c
    let tB := berggrenB a b c
    let tC := berggrenC a b c
    (tA.1^2 + tA.2.1^2 - tA.2.2^2 = a^2 + b^2 - c^2) ∧
    (tB.1^2 + tB.2.1^2 - tB.2.2^2 = a^2 + b^2 - c^2) ∧
    (tC.1^2 + tC.2.1^2 - tC.2.2^2 = a^2 + b^2 - c^2) := by
  simp only [berggrenA, berggrenB, berggrenC]
  constructor <;> [skip; constructor] <;> ring

/-- Depth-2: Berggren A applied twice to (3,4,5) -/
theorem berggrenA_depth2 : berggrenA 5 12 13 = (7, 24, 25) := by native_decide

/-- (7,24,25) is Pythagorean -/
theorem triple_7_24_25 : IsPythTriple' 7 24 25 := by unfold IsPythTriple'; ring

/-- Depth-2: Berggren B applied to the A-child of (3,4,5) -/
theorem berggrenB_of_A : berggrenB 5 12 13 = (55, 48, 73) := by native_decide

/-- (55,48,73) is Pythagorean -/
theorem triple_55_48_73 : IsPythTriple' 55 48 73 := by unfold IsPythTriple'; ring

/-! ## Part II: Photon Direction Algebra -/

/-- The Gaussian product of two photon triples -/
def gaussianProd' (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) : ℤ × ℤ × ℤ :=
  (a₁ * a₂ - b₁ * b₂, a₁ * b₂ + b₁ * a₂, c₁ * c₂)

/-- Gaussian product preserves the Pythagorean property -/
theorem gaussianProd'_preserves_pyth (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ)
    (h₁ : IsPythTriple' a₁ b₁ c₁) (h₂ : IsPythTriple' a₂ b₂ c₂) :
    let t := gaussianProd' a₁ b₁ c₁ a₂ b₂ c₂
    IsPythTriple' t.1 t.2.1 t.2.2 := by
  simp only [gaussianProd', IsPythTriple'] at *
  nlinarith [sq_nonneg (a₁ * a₂), sq_nonneg (b₁ * b₂),
             sq_nonneg (a₁ * b₂), sq_nonneg (b₁ * a₂)]

/-- Gaussian product is associative -/
theorem gaussianProd'_assoc (a₁ b₁ c₁ a₂ b₂ c₂ a₃ b₃ c₃ : ℤ) :
    let t₁₂ := gaussianProd' a₁ b₁ c₁ a₂ b₂ c₂
    let t₁₂_₃ := gaussianProd' t₁₂.1 t₁₂.2.1 t₁₂.2.2 a₃ b₃ c₃
    let t₂₃ := gaussianProd' a₂ b₂ c₂ a₃ b₃ c₃
    let t₁_₂₃ := gaussianProd' a₁ b₁ c₁ t₂₃.1 t₂₃.2.1 t₂₃.2.2
    t₁₂_₃ = t₁_₂₃ := by
  simp only [gaussianProd']; ext <;> ring

/-- Gaussian product is commutative -/
theorem gaussianProd'_comm (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) :
    gaussianProd' a₁ b₁ c₁ a₂ b₂ c₂ = gaussianProd' a₂ b₂ c₂ a₁ b₁ c₁ := by
  simp only [gaussianProd']; ext <;> ring

/-- Direction is invariant under scaling -/
theorem direction_ratio_scaling (a b k : ℤ) (ha : (a : ℚ) ≠ 0) (hk : (k : ℚ) ≠ 0) :
    (k * b : ℚ) / (k * a) = (b : ℚ) / a := by field_simp

/-- The "slope" of a Gaussian product follows the tangent addition formula -/
theorem gaussian_slope_composition (a₁ b₁ a₂ b₂ : ℤ)
    (ha₁ : (a₁ : ℚ) ≠ 0) (ha₂ : (a₂ : ℚ) ≠ 0)
    (hden : (a₁ : ℚ) * a₂ - b₁ * b₂ ≠ 0)
    (hden2 : 1 - (b₁ : ℚ) / a₁ * (b₂ / a₂) ≠ 0) :
    ((a₁ * b₂ + b₁ * a₂ : ℤ) : ℚ) / (a₁ * a₂ - b₁ * b₂) =
    ((b₁ : ℚ) / a₁ + b₂ / a₂) / (1 - b₁ / a₁ * (b₂ / a₂)) := by
  field_simp
  push_cast; ring

/-! ## Part III: Photon Counting and Statistics -/

/-- A prime is "bright" if it's ≡ 1 (mod 4) — it generates a photon -/
def isBrightPrime (p : ℕ) : Prop := Nat.Prime p ∧ p % 4 = 1

/-- A prime is "dark" if it's ≡ 3 (mod 4) — it has no photon representation -/
def isDarkPrime (p : ℕ) : Prop := Nat.Prime p ∧ p % 4 = 3

/-- 2 is the unique "diagonal" prime — neither bright nor dark -/
theorem two_is_diagonal : Nat.Prime 2 ∧ 2 % 4 ≠ 1 ∧ 2 % 4 ≠ 3 := by
  refine ⟨by decide, by omega, by omega⟩

/-- 5 is the smallest bright prime -/
theorem five_is_bright : isBrightPrime 5 := ⟨by decide, by omega⟩

/-- 3 is the smallest dark prime -/
theorem three_is_dark : isDarkPrime 3 := ⟨by decide, by omega⟩

/-- The first few bright primes -/
theorem bright_primes_small :
    isBrightPrime 5 ∧ isBrightPrime 13 ∧ isBrightPrime 17 ∧ isBrightPrime 29 := by
  exact ⟨⟨by decide, by omega⟩, ⟨by decide, by omega⟩, ⟨by decide, by omega⟩, ⟨by decide, by omega⟩⟩

/-- Every Pythagorean triple with c ≤ N has a, b ≤ N -/
theorem pyth_legs_bounded {N : ℕ} (a b c : ℕ) (h : a^2 + b^2 = c^2) (hc : c ≤ N) :
    a ≤ N ∧ b ≤ N := by
  constructor <;> nlinarith [sq_nonneg b, sq_nonneg a]

/-- The hypotenuse of a Pythagorean triple is at least as large as each leg -/
theorem hypotenuse_ge_legs (a b c : ℕ) (h : a^2 + b^2 = c^2) :
    a ≤ c ∧ b ≤ c := by
  constructor <;> nlinarith [sq_nonneg b, sq_nonneg a]

/-! ## Part IV: Spin Network Foundations -/

/-- A photon state is a point on the integer light cone -/
structure PhotonState' where
  px : ℤ
  py : ℤ
  energy : ℤ
  on_cone : px ^ 2 + py ^ 2 = energy ^ 2

/-- Photon fusion via Gaussian product -/
def PhotonState'.fuse (p q : PhotonState') : PhotonState' where
  px := p.px * q.px - p.py * q.py
  py := p.px * q.py + p.py * q.px
  energy := p.energy * q.energy
  on_cone := by
    have hp := p.on_cone; have hq := q.on_cone
    nlinarith [sq_nonneg (p.px * q.px), sq_nonneg (p.py * q.py),
               sq_nonneg (p.px * q.py), sq_nonneg (p.py * q.px)]

/-- The vacuum photon (1, 0, 1) -/
def vacuumPhoton : PhotonState' := ⟨1, 0, 1, by ring⟩

/-- Fusion with vacuum is identity (left) -/
theorem fuse_vacuum_left (p : PhotonState') :
    (vacuumPhoton.fuse p).px = p.px ∧
    (vacuumPhoton.fuse p).py = p.py ∧
    (vacuumPhoton.fuse p).energy = p.energy := by
  simp [PhotonState'.fuse, vacuumPhoton]

/-- Fusion with vacuum is identity (right) -/
theorem fuse_vacuum_right (p : PhotonState') :
    (p.fuse vacuumPhoton).px = p.px ∧
    (p.fuse vacuumPhoton).py = p.py ∧
    (p.fuse vacuumPhoton).energy = p.energy := by
  simp [PhotonState'.fuse, vacuumPhoton]

/-- Conjugate photon -/
def PhotonState'.conjugate (p : PhotonState') : PhotonState' where
  px := p.px
  py := -p.py
  energy := p.energy
  on_cone := by nlinarith [p.on_cone]

/-- Fusing with conjugate kills the transverse momentum -/
theorem fuse_conjugate_py (p : PhotonState') :
    (p.fuse p.conjugate).py = 0 := by
  simp [PhotonState'.fuse, PhotonState'.conjugate]; ring

/-- Fusing with conjugate gives squared energy -/
theorem fuse_conjugate_energy (p : PhotonState') :
    (p.fuse p.conjugate).energy = p.energy ^ 2 := by
  simp [PhotonState'.fuse, PhotonState'.conjugate]; ring

/-- Photon fusion is commutative -/
theorem fuse_comm (p q : PhotonState') :
    (p.fuse q).px = (q.fuse p).px ∧
    (p.fuse q).py = (q.fuse p).py ∧
    (p.fuse q).energy = (q.fuse p).energy := by
  simp [PhotonState'.fuse]; constructor <;> [skip; constructor] <;> ring

/-- Photon fusion is associative -/
theorem fuse_assoc (p q r : PhotonState') :
    ((p.fuse q).fuse r).px = (p.fuse (q.fuse r)).px ∧
    ((p.fuse q).fuse r).py = (p.fuse (q.fuse r)).py ∧
    ((p.fuse q).fuse r).energy = (p.fuse (q.fuse r)).energy := by
  simp [PhotonState'.fuse]; constructor <;> [skip; constructor] <;> ring

/-! ## Part V: Berggren Tree Generation -/

/-- The depth-1 Berggren tree from (3,4,5) produces three valid triples -/
theorem berggren_depth1_valid :
    IsPythTriple' 5 12 13 ∧ IsPythTriple' 21 20 29 ∧ IsPythTriple' 15 8 17 := by
  unfold IsPythTriple'; constructor <;> [skip; constructor] <;> ring

/-- The (3,4,5) photon -/
def photon345 : PhotonState' := ⟨3, 4, 5, by ring⟩

/-- Self-fusion of (3,4,5) gives (-7, 24, 25) -/
theorem self_fuse_345 :
    (photon345.fuse photon345).px = -7 ∧
    (photon345.fuse photon345).py = 24 ∧
    (photon345.fuse photon345).energy = 25 := by
  simp [PhotonState'.fuse, photon345]

/-- The (5,12,13) photon -/
def photon51213 : PhotonState' := ⟨5, 12, 13, by ring⟩

/-- Fusing (3,4,5) with (5,12,13) -/
theorem fuse_345_51213 :
    (photon345.fuse photon51213).px = -33 ∧
    (photon345.fuse photon51213).py = 56 ∧
    (photon345.fuse photon51213).energy = 65 := by
  simp [PhotonState'.fuse, photon345, photon51213]

/-! ## Part VI: Light Cone Group Properties -/

/-- The Gaussian norm of a photon state is the energy squared -/
theorem photon_norm_is_energy_sq (p : PhotonState') :
    p.px ^ 2 + p.py ^ 2 = p.energy ^ 2 := p.on_cone

/-- Energy is preserved under conjugation -/
theorem conjugate_energy (p : PhotonState') :
    p.conjugate.energy = p.energy := rfl

/-- Double conjugation is identity -/
theorem double_conjugate (p : PhotonState') :
    p.conjugate.conjugate.px = p.px ∧
    p.conjugate.conjugate.py = p.py ∧
    p.conjugate.conjugate.energy = p.energy := by
  simp [PhotonState'.conjugate]

/-! ## Part VII: Photon Entanglement -/

/-- A photon is "pure real" if py = 0 -/
def PhotonState'.isPureReal (p : PhotonState') : Prop := p.py = 0

/-- Fusing a photon with its conjugate always produces a pure real photon -/
theorem fuse_conjugate_is_pure_real (p : PhotonState') :
    (p.fuse p.conjugate).isPureReal := by
  simp [PhotonState'.isPureReal, PhotonState'.fuse, PhotonState'.conjugate]; ring

/-- Two photons with opposite momenta fuse to give energy² -/
theorem opposite_photon_fuse (p : PhotonState') :
    let neg_p : PhotonState' := ⟨-p.px, -p.py, p.energy, by nlinarith [p.on_cone]⟩
    (p.fuse neg_p).energy = p.energy ^ 2 := by
  simp [PhotonState'.fuse]; ring

/-! ## Part VIII: Photon Winding Numbers and Angular Momentum -/

/-- The quadrant of a photon (sign of px and py) -/
def photonQuadrant (p : PhotonState') : ℤ × ℤ :=
  (if p.px > 0 then 1 else if p.px < 0 then -1 else 0,
   if p.py > 0 then 1 else if p.py < 0 then -1 else 0)

/-- A photon with positive px and py is in the first quadrant -/
theorem first_quadrant_345 : photonQuadrant photon345 = (1, 1) := by
  simp [photonQuadrant, photon345]

/-- The "angular momentum" proxy L = px * py for a photon -/
def angularMomentumProxy (p : PhotonState') : ℤ := p.px * p.py

/-- Angular momentum of (3,4,5) is 12 -/
theorem angular_momentum_345 : angularMomentumProxy photon345 = 12 := by
  simp [angularMomentumProxy, photon345]

/-- Under fusion, the angular momentum proxy satisfies a product rule -/
theorem angular_momentum_fuse (p q : PhotonState') :
    angularMomentumProxy (p.fuse q) =
    (p.px * q.px - p.py * q.py) * (p.px * q.py + p.py * q.px) := by
  simp [angularMomentumProxy, PhotonState'.fuse]

/-! ## Part IX: Scaling Photons and Energy Levels -/

/-- Scaling a photon by k gives another valid photon -/
def PhotonState'.scale (p : PhotonState') (k : ℤ) : PhotonState' where
  px := k * p.px
  py := k * p.py
  energy := k * p.energy
  on_cone := by nlinarith [p.on_cone, sq_nonneg k]

/-- Scaling preserves direction ratio -/
theorem scale_preserves_direction (p : PhotonState') (k : ℤ) (hk : (k : ℚ) ≠ 0) (hp : (p.px : ℚ) ≠ 0) :
    ((p.scale k).py : ℚ) / (p.scale k).px = (p.py : ℚ) / p.px := by
  simp [PhotonState'.scale]; field_simp

/-- Scaling by 1 is identity -/
theorem scale_one (p : PhotonState') :
    (p.scale 1).px = p.px ∧ (p.scale 1).py = p.py ∧ (p.scale 1).energy = p.energy := by
  simp [PhotonState'.scale]

/-- Scaling composes multiplicatively -/
theorem scale_compose (p : PhotonState') (j k : ℤ) :
    ((p.scale j).scale k).px = (p.scale (k * j)).px ∧
    ((p.scale j).scale k).py = (p.scale (k * j)).py ∧
    ((p.scale j).scale k).energy = (p.scale (k * j)).energy := by
  simp [PhotonState'.scale]; constructor <;> [skip; constructor] <;> ring
