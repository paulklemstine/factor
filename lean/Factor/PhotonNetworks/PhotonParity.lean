/-
# Photon Parity: Discrete Invariant of Primitive Pythagorean Triples

For a primitive Pythagorean triple (a, b, c):
- Exactly one of a, b is even
- c is always odd

This parity structure is a discrete invariant — a "polarization" of the photon.

## Key Results
1. If a² + b² = c² and gcd(a,b) = 1, then a and b have different parities
2. The hypotenuse c is always odd
3. The parametrization: a = m² - n², b = 2mn, c = m² + n² for coprime m > n
-/
import Mathlib

/-
PROBLEM
In a Pythagorean triple, a and b cannot both be odd if a² + b² = c²

PROVIDED SOLUTION
If a and b are both odd, then a² ≡ 1 and b² ≡ 1 (mod 4), so a²+b² ≡ 2 (mod 4). But c² is either 0 or 1 (mod 4). Contradiction. Use Int.even_or_odd and modular arithmetic via omega or decide.
-/
theorem pyth_not_both_odd (a b c : ℤ) (h : a^2 + b^2 = c^2)
    (ha : ¬ 2 ∣ a) (hb : ¬ 2 ∣ b) : False := by
  simp_all +decide [ ← even_iff_two_dvd, parity_simps ];
  exact absurd ( congr_arg ( · % 4 ) h ) ( by obtain ⟨ k, rfl ⟩ := ha; obtain ⟨ l, rfl ⟩ := hb; rcases Int.even_or_odd' c with ⟨ m, rfl | rfl ⟩ <;> ring_nf <;> norm_num )

/-
PROBLEM
The hypotenuse of a primitive Pythagorean triple is odd

PROVIDED SOLUTION
If a,b coprime and a²+b²=c², then a,b can't both be even (coprime). They can't both be odd (by pyth_not_both_odd over ℤ, cast). So one is even, one odd. Then a²+b² is odd, so c² is odd, so c is odd.
-/
theorem pyth_hypotenuse_odd (a b c : ℕ) (h : a^2 + b^2 = c^2)
    (hcop : Nat.Coprime a b) : ¬ 2 ∣ c := by
  contrapose! hcop; have := congr_arg ( · % 4 ) h; rcases Nat.even_or_odd' a with ⟨ b₁, rfl | rfl ⟩ <;> rcases Nat.even_or_odd' b with ⟨ b₂, rfl | rfl ⟩ <;> rcases Nat.even_or_odd' c with ⟨ b₃, rfl | rfl ⟩ <;> ring_nf at * <;> norm_num [ Nat.add_mod, Nat.mul_mod ] at *;
  · norm_num [ Nat.gcd_mul_right, Nat.gcd_mul_left ];
  · grind +ring;
  · grind +ring

/-
PROBLEM
In a primitive Pythagorean triple, exactly one leg is even

PROVIDED SOLUTION
Since a,b are coprime, they can't both be even. By pyth_not_both_odd (cast to ℤ), they can't both be odd. So exactly one is even. Use Nat.even_or_odd for each and eliminate cases.
-/
theorem pyth_one_leg_even (a b c : ℕ) (h : a^2 + b^2 = c^2)
    (hcop : Nat.Coprime a b) (ha : 0 < a) (hb : 0 < b) :
    (2 ∣ a ∧ ¬ 2 ∣ b) ∨ (¬ 2 ∣ a ∧ 2 ∣ b) := by
  by_cases ha : 2 ∣ a <;> by_cases hb : 2 ∣ b <;> simp_all +decide [ Nat.dvd_iff_mod_eq_zero ];
  · have := Nat.dvd_gcd ( Nat.dvd_of_mod_eq_zero ha ) ( Nat.dvd_of_mod_eq_zero hb ) ; aesop;
  · exact absurd ( congr_arg ( · % 4 ) h ) ( by rw [ ← Nat.mod_add_div a 2, ← Nat.mod_add_div b 2, ha, hb ] ; ring_nf; norm_num [ Nat.add_mod, Nat.mul_mod, Nat.pow_mod ] ; have := Nat.mod_lt c zero_lt_four ; interval_cases c % 4 <;> trivial )

/-
PROBLEM
The parametrization generates Pythagorean triples (over ℤ)

PROVIDED SOLUTION
Pure ring identity: (m²-n²)² + (2mn)² = m⁴ - 2m²n² + n⁴ + 4m²n² = m⁴ + 2m²n² + n⁴ = (m²+n²)².
-/
theorem pyth_parametrization (m n : ℤ) :
    (m^2 - n^2)^2 + (2*m*n)^2 = (m^2 + n^2)^2 := by
  ring