/-
# Computational Explorations: The Integer Decoder

Compute four-channel signatures for small integers to observe patterns
and verify the theoretical framework.
-/

import Mathlib

open Finset

/-! ## Efficient computation of representation counts and signatures -/

/-- Count divisors of n that are ≡ r (mod 4) -/
def countDivisorsMod4 (n : ℕ) (r : ℕ) : ℕ :=
  ((Nat.divisors n).filter (fun d => d % 4 = r)).card

/-- d₁(n) - d₃(n): the Channel 2 signal -/
def complexSignal (n : ℕ) : Int :=
  ↑(countDivisorsMod4 n 1) - ↑(countDivisorsMod4 n 3)

/-- Jacobi sum for Channel 3: Σ_{d|n, 4∤d} d -/
def jacobiSumC (n : ℕ) : ℕ :=
  ((Nat.divisors n).filter (fun d => d % 4 ≠ 0)).sum id

/-- Channel 4 signal: Σ_{d|n} (-1)^{n+d} d³ -/
def octonionicSignal (n : ℕ) : Int :=
  (Nat.divisors n).sum fun d =>
    if (n + d) % 2 = 0 then (↑d : Int) ^ 3 else -(↑d : Int) ^ 3

/-- Full four-channel signature as a string -/
def signatureStr (n : ℕ) : String :=
  let isSq := Nat.sqrt n ^ 2 == n
  let ch2 := complexSignal n
  let ch3 := jacobiSumC n
  let ch4 := octonionicSignal n
  s!"n={n}: sq={isSq} ch2={ch2} ch3={ch3} ch4={ch4}"

/-- Predicted r₂(n) = 4 * complexSignal(n) -/
def predicted_r₂ (n : ℕ) : Int := 4 * complexSignal n

/-- Predicted r₄(n) = 8 * jacobiSumC(n) -/
def predicted_r₄ (n : ℕ) : ℕ := 8 * jacobiSumC n

/-- Predicted r₈(n) = 16 * octonionicSignal(n) -/
def predicted_r₈ (n : ℕ) : Int := 16 * octonionicSignal n

/-! ## Computational experiments -/

-- Experiment 1: Four-channel signatures of small integers (1 to 30)
#eval (List.range 30).map (fun i => signatureStr (i + 1))

-- Experiment 2: Which integers ≤ 50 are sums of two squares? (Channel 2 positive)
#eval (List.range 50).filterMap fun i =>
  let n := i + 1
  if complexSignal n > 0 then some (n, predicted_r₂ n) else none

-- Experiment 3: Jacobi's formula - r₄(n) values for n = 1..20
#eval (List.range 20).map fun i => (i + 1, predicted_r₄ (i + 1))

-- Experiment 4: Signatures of primes — how Channel 2 distinguishes p mod 4
#eval [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47].map fun p =>
  (p, p % 4, complexSignal p, jacobiSumC p)

-- Experiment 5: Channel 2 sequence — the oscillation of the complex signal
#eval (List.range 50).map fun i => (i + 1, complexSignal (i + 1))

-- Experiment 6: Information content across channels for n = 1..30
#eval (List.range 30).map fun i =>
  let n := i + 1
  let ch2 := (predicted_r₂ n).natAbs
  let ch3 := predicted_r₄ n
  let ch4 := (predicted_r₈ n).natAbs
  (n, ch2, ch3, ch4)

-- Experiment 7: Highly composite numbers have large Channel 3 signals
#eval [1, 2, 4, 6, 12, 24, 36, 48, 60, 120].map fun n =>
  (n, jacobiSumC n, predicted_r₄ n)

-- Experiment 8: Perfect squares — the only integers heard by Channel 1
#eval (List.range 100).filterMap fun i =>
  let n := i + 1
  if Nat.sqrt n ^ 2 = n then some (n, signatureStr n) else none

-- Experiment 9: Verify Channel 3 always positive (Lagrange's theorem, computationally)
#eval (List.range 200).all fun i => jacobiSumC (i + 1) ≥ 1

-- Experiment 10: The ratio r₄(p)/r₂(p) for primes p ≡ 1 (mod 4) — should be (p+1)/2
#eval [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97].map fun p =>
  let r2 := predicted_r₂ p
  let r4 := (predicted_r₄ p : Int)
  (p, r2, r4, if r2 ≠ 0 then r4 / r2 else 0)
