/-
  Verification of Theorem 4.1 (ADE Tower from PPTs)

  The theorem states:
  (i)  SL(2, 𝔽₃) has order 24  (binary tetrahedral group ↔ E₆)
  (ii) SL(2, 𝔽₅) has order 120 (binary icosahedral group ↔ E₈)

  We verify the group-order computations, which are the core
  checkable claims.  The McKay correspondence itself (associating
  Dynkin diagrams to finite subgroups of SL(2,ℂ)) is beyond
  current Mathlib coverage.
-/
import Mathlib

open Matrix

/-- Part (i): |SL(2, 𝔽₃)| = 24 -/
theorem thm41_sl2_F3_card :
    Fintype.card (SpecialLinearGroup (Fin 2) (ZMod 3)) = 24 := by
  native_decide

/-- Part (ii): |SL(2, 𝔽₅)| = 120 -/
theorem thm41_sl2_F5_card :
    Fintype.card (SpecialLinearGroup (Fin 2) (ZMod 5)) = 120 := by
  native_decide

/-- The order formula |SL(2, 𝔽_p)| = p(p²-1) for p=3 gives 3·(9-1) = 24. -/
theorem thm41_order_formula_p3 : 3 * (3 ^ 2 - 1) = 24 := by norm_num

/-- The order formula |SL(2, 𝔽_p)| = p(p²-1) for p=5 gives 5·(25-1) = 120. -/
theorem thm41_order_formula_p5 : 5 * (5 ^ 2 - 1) = 120 := by norm_num
