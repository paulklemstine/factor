/-
# Four-Channel Integer Signatures: Core Definitions

The "signature" of a positive integer n is the tuple (r₁(n), r₂(n), r₄(n), r₈(n))
where rₖ(n) counts the number of representations of n as a sum of k squares
(with signs and order).

Known closed forms:
  r₂(n) = 4 · Σ_{d|n} χ₋₄(d)         where χ₋₄ is the non-principal character mod 4
  r₄(n) = 8 · Σ_{d|n, 4∤d} d          (Jacobi's four-square theorem)
  r₈(n) = 16 · Σ_{d|n} (-1)^{n+d} d³  (Jacobi's eight-square theorem, up to sign convention)
-/

import Mathlib

open Finset BigOperators

/-! ## Channel 2: Representations as sums of 2 squares -/

/-- The non-principal Dirichlet character mod 4: χ₋₄(n) = 0 if n even, 1 if n≡1(4), -1 if n≡3(4). -/
def chi4 (n : ℤ) : ℤ :=
  if n % 2 = 0 then 0
  else if n % 4 = 1 then 1
  else -1

/-- r₂(n): number of representations of n as a sum of 2 squares (with signs and order).
    Formula: r₂(n) = 4 · Σ_{d|n} χ₋₄(d). -/
def r2 (n : ℕ) : ℤ :=
  4 * ∑ d ∈ (Nat.divisors n), chi4 (d : ℤ)

/-! ## Channel 3: Representations as sums of 4 squares -/

/-- r₄(n): number of representations of n as a sum of 4 squares.
    Jacobi's four-square theorem: r₄(n) = 8 · Σ_{d|n, 4∤d} d. -/
def r4 (n : ℕ) : ℤ :=
  8 * ∑ d ∈ (Nat.divisors n).filter (fun d => ¬(4 ∣ d)), (d : ℤ)

/-! ## Channel 4: Representations as sums of 8 squares -/

/-- r₈(n): number of representations of n as a sum of 8 squares.
    Formula: r₈(n) = 16 · Σ_{d|n} (-1)^{n+d} · d³. -/
def r8 (n : ℕ) : ℤ :=
  16 * ∑ d ∈ (Nat.divisors n), ((-1 : ℤ) ^ (n + d) * (d : ℤ) ^ 3)

/-! ## The Four-Channel Signature -/

/-- The four-channel signature of a positive integer. -/
structure IntSignature where
  ch1 : ℤ  -- Channel 1: trivially 1 for all n ≥ 1 (every n is a sum of 1 square... of itself, but we use r₁(n) = 2 if n is a perfect square, 0 otherwise, or just n itself)
  ch2 : ℤ  -- Channel 2: r₂(n)
  ch3 : ℤ  -- Channel 3: r₄(n)
  ch4 : ℤ  -- Channel 4: r₈(n)
  deriving Repr

/-- Compute the four-channel signature of n. -/
def signature (n : ℕ) : IntSignature where
  ch1 := n
  ch2 := r2 n
  ch3 := r4 n
  ch4 := r8 n

/-! ## Signature Distance -/

/-- Squared Euclidean distance between two signatures (using integer arithmetic). -/
def sigDistSq (s t : IntSignature) : ℤ :=
  (s.ch1 - t.ch1)^2 + (s.ch2 - t.ch2)^2 + (s.ch3 - t.ch3)^2 + (s.ch4 - t.ch4)^2

/-! ## Normalized Signature (for clustering) -/

/-- Normalized signature: each channel divided by n (as rationals). -/
structure NormSignature where
  ch1 : ℚ
  ch2 : ℚ
  ch3 : ℚ
  ch4 : ℚ
  deriving Repr

/-- Compute the normalized signature. -/
def normSignature (n : ℕ) (hn : n ≠ 0) : NormSignature :=
  let s := signature n
  { ch1 := (s.ch1 : ℚ) / n
    ch2 := (s.ch2 : ℚ) / n
    ch3 := (s.ch3 : ℚ) / n
    ch4 := (s.ch4 : ℚ) / n }
