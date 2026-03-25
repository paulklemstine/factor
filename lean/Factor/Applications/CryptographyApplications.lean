import Mathlib

/-!
# Cryptography and Coding Theory Applications

Real-world applications connecting number theory to:
- RSA cryptosystem correctness
- Diffie-Hellman key exchange
- Error-correcting codes
- Lattice cryptography foundations
-/

open Finset BigOperators

section RSA

theorem rsa_key_ex1 : (3 * 3 : ℤ) % 8 = 1 := by norm_num
theorem rsa_correct_15 : ∀ m : ZMod 15, m ^ 9 = m := by decide
theorem rsa_key_ex2 : (3 * 27 : ℤ) % 40 = 1 := by norm_num
theorem euler_thm_15 : ∀ a : (ZMod 15)ˣ, (a : ZMod 15) ^ Nat.totient 15 = 1 := by decide

end RSA

section DiffieHellman

/-
DH correctness: (g^a)^b = (g^b)^a
-/
theorem dh_correct {G : Type*} [CommMonoid G] (g : G) (a b : ℕ) :
    (g ^ a) ^ b = (g ^ b) ^ a := by
  rw [ ← pow_mul, ← pow_mul, mul_comm ]

/-
3 generates (ℤ/7ℤ)*
-/
theorem primitive_root_3_7 :
    ∀ a : (ZMod 7)ˣ, ∃ k : ℕ, (3 : ZMod 7) ^ k = (a : ZMod 7) := by
  intro a;
  -- Since 3 generates (ℤ/7ℤ)*, we can find k such that 3^k ≡ a (mod 7).
  have h_order : ∀ a : ZMod 7, a ≠ 0 → ∃ k : ℕ, k < 6 ∧ (3 ^ k : ZMod 7) = a := by
    native_decide;
  exact Exists.elim ( h_order a ( by fin_cases a <;> trivial ) ) fun k hk => ⟨ k, hk.2 ⟩

end DiffieHellman

section ErrorCorrecting

/-- Hamming distance on Fin n → Bool -/
def hammingDistance {n : ℕ} (x y : Fin n → Bool) : ℕ :=
  (Finset.univ.filter (fun i => x i ≠ y i)).card

theorem hamming_self_zero {n : ℕ} (x : Fin n → Bool) :
    hammingDistance x x = 0 := by
  -- The Hamming distance between a string and itself is zero because there are no differing positions.
  simp [hammingDistance]

theorem hamming_symmetric {n : ℕ} (x y : Fin n → Bool) :
    hammingDistance x y = hammingDistance y x := by
  -- The Hamming distance is symmetric because the set of positions where x and y differ is the same as the set of positions where y and x differ.
  simp [hammingDistance];
  -- Since equality is symmetric, the sets {i | ¬x i = y i} and {i | ¬y i = x i} are identical.
  simp [eq_comm]

/-
PROVIDED SOLUTION
If x_i ≠ z_i, then either x_i ≠ y_i or y_i ≠ z_i (since equality is transitive). So the filter set for d(x,z) is a subset of the union of filter sets for d(x,y) and d(y,z). Use Finset.card_filter_le_card_filter + Finset.card_union_le.
-/
theorem hamming_tri {n : ℕ} (x y z : Fin n → Bool) :
    hammingDistance x z ≤ hammingDistance x y + hammingDistance y z := by
  unfold hammingDistance; rw [ ← Finset.card_union_add_card_inter ] ;
  exact le_add_right ( Finset.card_le_card fun i hi => by by_cases hi' : x i = y i <;> by_cases hi'' : y i = z i <;> aesop )

/-
Repetition code distance
-/
theorem rep_code_distance :
    hammingDistance (fun _ : Fin 3 => false) (fun _ : Fin 3 => true) = 3 := by
  native_decide +revert

end ErrorCorrecting

section LatticeCrypto

theorem std_lattice_det_eq (n : ℕ) :
    Matrix.det (1 : Matrix (Fin n) (Fin n) ℤ) = 1 := by
  -- The determinant of the identity matrix is 1 by definition.
  apply Matrix.det_one

end LatticeCrypto

section HashFunctions

theorem birthday_bound_val : 2 ^ 64 * 2 ^ 64 = 2 ^ 128 := by norm_num

theorem iter_inj {α : Type*} (f : α → α) (hf : Function.Injective f) (n : ℕ) :
    Function.Injective (f^[n]) := by
  -- Since $f$ is injective, the composition of $f$ with itself $n$ times is also injective.
  apply Function.Injective.iterate hf n

end HashFunctions