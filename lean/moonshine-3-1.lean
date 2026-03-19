import Mathlib

set_option maxRecDepth 2000

/-!
# Theorem 3.1: ADE Tower from PPTs

This file verifies the core computational claims of Theorem 3.1 from the paper:

(i) **p = 3, E₆**: SL(2, 𝔽₃) has order 24 (= |binary tetrahedral group|).
(ii) **p = 5, E₈**: SL(2, 𝔽₅) has order 120 (= |binary icosahedral group|).

These orders follow from the general formula |SL(2, 𝔽_p)| = p(p² − 1):
  - p = 3: 3 · (9 − 1) = 24
  - p = 5: 5 · (25 − 1) = 120
-/

/-- SL(2, 𝔽₃) has order 24, identifying it as the binary tetrahedral group T̃
    (the McKay correspondent of E₆). -/
theorem SL2_F3_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 3)) = 24 := by
  decide

/-- SL(2, 𝔽₅) has order 120, identifying it as the binary icosahedral group Ĩ
    (the McKay correspondent of E₈). -/
theorem SL2_F5_card :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 5)) = 120 := by
  decide
