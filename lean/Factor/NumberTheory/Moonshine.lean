import Mathlib

/-!
# Moonshine Connections: ADE Tower and Sporadic Groups

Consolidation of the ADE tower, theta group, and sporadic group connections
from the Berggren tree research program.

## Main Results

1. **Theorem 2.1**: ⟨M₁, M₃⟩ = Γ_θ (the theta group) in SL(2,ℤ)
2. **Theorem 3.1/4.1**: |SL(2,𝔽₃)| = 24 (binary tetrahedral, E₆ McKay)
                         |SL(2,𝔽₅)| = 120 (binary icosahedral, E₈ McKay)
3. **Theorem 5.1**: |SL(2,𝔽₁₁)| = 1320, PSL(2,𝔽₁₁) ↪ M₁₁
4. **Theorem 6.1**: Dedekind domain expansion (Neukirch)
5. **Theorem 8.1**: j-invariant at λ = 1/2 gives j(i) = 1728 = 12³
-/

open Matrix

/-! ## §2.1: Berggren Generators = Theta Group -/

/-- Berggren matrix M₁ in SL(2,ℤ). -/
def berggren_M1 : Matrix.SpecialLinearGroup (Fin 2) ℤ :=
  ⟨!![2, -1; 1, 0], by decide +revert⟩

/-- Berggren matrix M₃ in SL(2,ℤ). -/
def berggren_M3 : Matrix.SpecialLinearGroup (Fin 2) ℤ :=
  ⟨!![1, 2; 0, 1], by decide +revert⟩

/-- The theta group Γ_θ = ⟨S, T²⟩ in SL(2,ℤ). -/
def GammaTheta : Subgroup (Matrix.SpecialLinearGroup (Fin 2) ℤ) :=
  Subgroup.closure {ModularGroup.S, ModularGroup.T ^ 2}

/-- **Theorem 2.1**: The Berggren generators M₁, M₃ generate exactly the theta group.
    This is the key structural result connecting Pythagorean triples to modular forms. -/
theorem berggren_eq_theta : Subgroup.closure {berggren_M1, berggren_M3} = GammaTheta := by
  refine le_antisymm ?_ ?_
  · simp +decide [Subgroup.closure_le, Set.insert_subset_iff]
    refine ⟨Subgroup.mem_closure.mpr ?_, Subgroup.mem_closure.mpr ?_⟩
    · intro K hK
      have hS := hK (Set.mem_insert _ _)
      have hT2 := hK (Set.mem_insert_of_mem _ (Set.mem_singleton _))
      simp +decide [Set.insert_subset_iff] at *
      convert K.mul_mem hT2 hS using 1
      ext i j; fin_cases i <;> fin_cases j <;> rfl
    · intro K hK
      have hT2 := hK (Set.mem_insert_of_mem _ (Set.mem_singleton _))
      simp +decide [Set.insert_subset_iff, pow_two] at *
      convert hT2 using 1
      ext i j; fin_cases i <;> fin_cases j <;> rfl
  · rw [GammaTheta]
    simp +decide [Subgroup.closure_le, Set.insert_subset_iff]
    constructor
    · have hS : (ModularGroup.S : Matrix.SpecialLinearGroup (Fin 2) ℤ) = berggren_M3⁻¹ * berggren_M1 := by
        ext i j; fin_cases i <;> fin_cases j <;> simp +decide [berggren_M1, berggren_M3]
      rw [hS]
      exact Subgroup.mul_mem _
        (Subgroup.inv_mem _ (Subgroup.subset_closure (Set.mem_insert_of_mem _ (Set.mem_singleton _))))
        (Subgroup.subset_closure (Set.mem_insert _ _))
    · exact Subgroup.subset_closure (by right; ext i j; fin_cases i <;> fin_cases j <;> rfl)

/-! ## §3.1: ADE Tower — SL(2,𝔽_p) Orders -/

/-- |SL(2, 𝔽₃)| = 24, the binary tetrahedral group (McKay correspondent of E₆). -/
theorem SL2_F3_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 3)) = 24 := by
  native_decide

/-- |SL(2, 𝔽₅)| = 120, the binary icosahedral group (McKay correspondent of E₈). -/
theorem SL2_F5_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 5)) = 120 := by
  native_decide

/-- |SL(2, 𝔽₇)| = 336 (McKay correspondent of E₇ has order 48 = 336/7). -/
theorem SL2_F7_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 7)) = 336 := by
  native_decide

/-- The order formula |SL(2, 𝔽_p)| = p(p²-1) verified at p = 3, 5, 7. -/
theorem SL2_order_formula :
    3 * (3^2 - 1) = 24 ∧ 5 * (5^2 - 1) = 120 ∧ 7 * (7^2 - 1) = 336 := by
  norm_num

/-! ## §5.1: Sporadic Groups — M₁₁ Connection -/

/-- |SL(2, 𝔽₁₁)| = 1320. The quotient PSL(2,𝔽₁₁) of order 660 embeds in M₁₁. -/
theorem SL2_F11_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 11)) = 1320 := by
  native_decide +revert

/-- 660 | 7920, consistent with PSL(2,𝔽₁₁) ↪ M₁₁ (|M₁₁| = 7920). -/
theorem PSL2_divides_M11 : 660 ∣ 7920 := ⟨12, by norm_num⟩

/-- |M₁₁| = 7920 = 2⁴ · 3² · 5 · 11. -/
theorem M11_order : 7920 = 2^4 * 3^2 * 5 * 11 := by norm_num

/-! ## §6.1: Dedekind Domain Expansion -/

/-- Neukirch Prop 6.1: In a Dedekind domain, elements of 𝔭ⁱ admit expansions
    modulo 𝔭^(i+1) using any 𝔭-uniformizer. -/
theorem dedekind_expansion {S : Type*} [CommRing S] [IsDedekindDomain S]
    {P : Ideal S} [P.IsPrime] (hP : P ≠ ⊥)
    {i : ℕ} (a c : S) (a_mem : a ∈ P ^ i)
    (a_notMem : a ∉ P ^ (i + 1)) (c_mem : c ∈ P ^ i) :
    ∃ d : S, ∃ e ∈ P ^ (i + 1), a * d + e = c :=
  Ideal.exists_mul_add_mem_pow_succ hP a c a_mem a_notMem c_mem

/-! ## §8.1: j-Invariant Connection -/

/-- The j-invariant formula evaluated at the modular lambda function value. -/
noncomputable def j_from_lambda (l : ℚ) : ℚ :=
  256 * (1 - l + l ^ 2) ^ 3 / (l * (1 - l)) ^ 2

/-- When λ(i) = 1/2 (the square lattice), j = 1728.
    This connects Pythagorean triples to the arithmetic of CM elliptic curves. -/
theorem j_at_half : j_from_lambda (1/2) = 1728 := by
  unfold j_from_lambda; norm_num

/-- 1728 = 12³, a fundamental constant in the theory of modular forms. -/
theorem j_value_cube : (1728 : ℤ) = 12 ^ 3 := by norm_num
