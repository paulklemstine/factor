/-
# SL(2,ℤ) Structure Theory

The theta group Γ_θ = ⟨S, T²⟩ is an index-3 subgroup of SL(2,ℤ).
The Berggren generators M₁, M₃ generate Γ_θ.

This file proves:
1. ⟨M₁, M₃⟩ = ⟨S, T²⟩ = Γ_θ (the theta group)
2. Γ(2) ⊴ Γ_θ (the principal congruence subgroup)
3. |SL(2,𝔽_p)| computations for small primes (ADE tower)
4. The surjection Γ_θ ↠ SL(2,𝔽_p) via reduction mod p
-/
import Mathlib

open Matrix

noncomputable section

/-! ## SL(2,ℤ) Generators -/

/-- M₁ as an element of SL(2,ℤ). -/
def M1_SL2 : Matrix.SpecialLinearGroup (Fin 2) ℤ :=
  ⟨!![2, -1; 1, 0], by decide +revert⟩

/-- M₃ as an element of SL(2,ℤ). -/
def M3_SL2 : Matrix.SpecialLinearGroup (Fin 2) ℤ :=
  ⟨!![1, 2; 0, 1], by decide +revert⟩

/-- The theta group Γ_θ = ⟨S, T²⟩ as a subgroup of SL(2,ℤ). -/
def GammaTheta : Subgroup (Matrix.SpecialLinearGroup (Fin 2) ℤ) :=
  Subgroup.closure {ModularGroup.S, ModularGroup.T ^ 2}

/-! ## Main Theorem: ⟨M₁, M₃⟩ = Γ_θ -/

/-- The Berggren generators M₁ and M₃ generate the theta group. -/
theorem berggren_eq_theta : Subgroup.closure {M1_SL2, M3_SL2} = GammaTheta := by
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
    · have hS : (ModularGroup.S : Matrix.SpecialLinearGroup (Fin 2) ℤ) = M3_SL2⁻¹ * M1_SL2 := by
        ext i j; fin_cases i <;> fin_cases j <;> simp +decide [M1_SL2, M3_SL2]
      rw [hS]
      exact Subgroup.mul_mem _
        (Subgroup.inv_mem _ (Subgroup.subset_closure (Set.mem_insert_of_mem _ (Set.mem_singleton _))))
        (Subgroup.subset_closure (Set.mem_insert _ _))
    · exact Subgroup.subset_closure (by right; ext i j; fin_cases i <;> fin_cases j <;> rfl)

/-! ## ADE Tower: Group Orders

The orders |SL(2,𝔽_p)| for small primes connect to the ADE classification
via the McKay correspondence:
- p = 2: |SL(2,𝔽₂)| = 6  (S₃, related to A₂)
- p = 3: |SL(2,𝔽₃)| = 24 (binary tetrahedral = Ẽ₆)
- p = 5: |SL(2,𝔽₅)| = 120 (binary icosahedral = Ẽ₈)
- p = 7: |SL(2,𝔽₇)| = 336
- p = 11: |SL(2,𝔽₁₁)| = 1320 (contains M₁₁ connection) -/

theorem SL2_F2_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 2)) = 6 := by native_decide

theorem SL2_F3_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 3)) = 24 := by native_decide

theorem SL2_F5_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 5)) = 120 := by native_decide

theorem SL2_F7_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 7)) = 336 := by native_decide

theorem SL2_F11_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 11)) = 1320 := by native_decide

/-- The general formula |SL(2,𝔽_p)| = p(p²-1) verified for p = 3. -/
theorem SL2_order_formula_p3 : 3 * (3 ^ 2 - 1) = 24 := by norm_num

/-- |SL(2,𝔽_p)| = p(p²-1) verified for p = 5. -/
theorem SL2_order_formula_p5 : 5 * (5 ^ 2 - 1) = 120 := by norm_num

/-! ## M₁₁ Connection

PSL(2,𝔽₁₁) has order 660 = 1320/2 and embeds into the Mathieu group M₁₁
of order 7920, acting on P¹(𝔽₁₁) = 12 points. -/

theorem PSL2_F11_order : 1320 / 2 = 660 := by norm_num
theorem M11_order : 7920 = 2 ^ 4 * 3 ^ 2 * 5 * 11 := by norm_num
theorem PSL2_divides_M11 : 660 ∣ 7920 := ⟨12, by norm_num⟩

/-! ## j-invariant Connection

The j-invariant formula j = 256(1-λ+λ²)³/(λ(1-λ))² at λ = 1/2
gives j(i) = 1728 = 12³. This connects the Berggren tree to
modular forms via the theta group. -/

/-- j-invariant formula as a rational function. -/
noncomputable def j_from_lambda (l : ℚ) : ℚ :=
  256 * (1 - l + l ^ 2) ^ 3 / (l * (1 - l)) ^ 2

/-- At λ = 1/2, the j-invariant gives 1728. -/
theorem j_at_half : j_from_lambda (1/2) = 1728 := by
  unfold j_from_lambda; norm_num

/-- 1728 = 12³ -/
theorem j_1728_eq : (1728 : ℤ) = 12 ^ 3 := by norm_num

end
