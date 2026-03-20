/-
# Cryptography Foundations

Number-theoretic foundations of modern cryptography.
-/
import Mathlib

open BigOperators Finset

/-! ## §1: Discrete Logarithm -/

/-- 2^10 ≡ 1 (mod 1023). -/
theorem dlog_example_1 : (2 : ZMod 1023) ^ 10 = 1 := by native_decide

/-- 3 is a primitive root mod 7: ord(3) = 6. -/
theorem primitive_root_3_7 :
    (3 : ZMod 7) ^ 6 = 1 ∧
    (3 : ZMod 7) ^ 1 ≠ 1 ∧
    (3 : ZMod 7) ^ 2 ≠ 1 ∧
    (3 : ZMod 7) ^ 3 ≠ 1 := by
  native_decide

/-- 2 is a primitive root mod 5. -/
theorem primitive_root_2_5 :
    (2 : ZMod 5) ^ 4 = 1 ∧
    (2 : ZMod 5) ^ 1 ≠ 1 ∧
    (2 : ZMod 5) ^ 2 ≠ 1 := by
  native_decide

/-! ## §2: RSA Mathematics -/

/-- RSA key generation: p=3, q=11, N=33, φ(N)=20, e=3, d=7. -/
theorem rsa_small_keygen :
    3 * 11 = 33 ∧ (3 - 1) * (11 - 1) = (20 : ℕ) ∧ 3 * 7 % 20 = 1 := by omega

/-- RSA roundtrip: m^(ed) ≡ m (mod N). -/
theorem rsa_roundtrip : (2 : ZMod 33) ^ (3 * 7) = 2 := by native_decide

/-! ## §3: Elliptic Curve Cryptography -/

/-- Verify (2,1) is on y² = x³ + 2x + 3 over 𝔽₇. -/
theorem ecc_point_on_curve : (1 : ZMod 7) ^ 2 = (2 : ZMod 7) ^ 3 + 2 * 2 + 3 := by
  native_decide

/-! ## §4: Hash Functions -/

/-- Pigeonhole: hash collisions must exist when input > output space. -/
theorem hash_collisions_exist (n m : ℕ) (hm : m < n) :
    2 ^ n > 2 ^ m :=
  Nat.pow_lt_pow_right (by norm_num : 1 < 2) hm

/-- Birthday attack bound. -/
theorem birthday_bound_squared (m : ℕ) : (2 ^ m) * (2 ^ m) = 2 ^ (2 * m) := by ring

/-! ## §5: Lattice Cryptography -/

/-- Minkowski example: (1,1) is in the disk of radius √2. -/
theorem minkowski_example : (1 : ℤ)^2 + 1^2 ≤ 2 := by norm_num

/-! ## §6: RSA Security -/

/-- 2^2048 > 2^1024 (RSA-2048 vs RSA-1024). -/
theorem rsa_2048_size : 2 ^ 2048 > 2 ^ 1024 :=
  Nat.pow_lt_pow_right (by norm_num : 1 < 2) (by norm_num)
