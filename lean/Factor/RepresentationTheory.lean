/-
# Representation Theory Exploration
-/
import Mathlib

open BigOperators Finset Matrix

/-! ## §1: Sign Representation -/

theorem sign_rep_identity : Equiv.Perm.sign (1 : Equiv.Perm (Fin 3)) = 1 := by simp

theorem sign_swap' : Equiv.Perm.sign (Equiv.swap (0 : Fin 3) 1) = -1 := by native_decide

/-! ## §2: Regular Representation -/

theorem regular_rep_dim (n : ℕ) [NeZero n] :
    Fintype.card (ZMod n) = n := ZMod.card n

/-! ## §3: Symmetric Powers -/

theorem sym2_dim' : Nat.choose (2 + 2 - 1) 2 = 3 := by native_decide

theorem symn_dim' (n : ℕ) : Nat.choose (n + 1) 1 = n + 1 := by simp

/-! ## §4: Moonshine Connection -/

theorem moonshine_dimension' : 196884 = 196883 + 1 := by norm_num
theorem mckay_first' : 196884 = 1 + 196883 := by norm_num
theorem mckay_second' : 21493760 = 1 + 196883 + 21296876 := by norm_num
