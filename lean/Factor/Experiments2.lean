/-
# Computational Experiments: Round 2

Deeper investigations following the initial findings.
-/

import RequestProject.Defs

/-! ## Experiment 12: Dark matter fraction at larger scales

The Landau-Ramanujan theorem predicts: #{n ≤ N : r₂(n) > 0} ~ C·N/√(log N).
Let's check this for increasing N. -/

#eval Id.run do
  let mut results : Array String := #[]
  for N in [50, 100, 200, 500, 1000] do
    let mut visible := 0
    for n in List.range N do
      let s := signature (n + 1)
      if s.ch2 != 0 then visible := visible + 1
    let fraction : ℚ := (visible : ℚ) / (N : ℚ)
    results := results.push s!"N={N}: visible={visible}/{N}, fraction={fraction}"
  return results

/-! ## Experiment 13: Multiplicativity test for r₄

r₄ is "almost multiplicative": r₄(mn) = r₄(m)·r₄(n) when gcd(m,n) = 1?
Not exactly — r₄(n)/8 = σ₁*(n) which IS multiplicative.
Let's test: r₄(m)·r₄(n) vs r₄(mn) for coprime m, n. -/

#eval Id.run do
  let mut results : Array String := #[]
  -- Coprime pairs
  for (m, n) in ([(3,5), (3,7), (5,7), (4,9), (7,11), (8,15)] : List (ℕ × ℕ)) do
    let rm := r4 m
    let rn := r4 n
    let rmn := r4 (m * n)
    -- If r₄/8 is multiplicative, then r₄(mn) = r₄(m)·r₄(n)/8
    let predicted := rm * rn / 8
    results := results.push s!"r₄({m})·r₄({n})/8 = {rm}·{rn}/8 = {predicted}, r₄({m*n}) = {rmn}, match={predicted == rmn}"
  return results

/-! ## Experiment 14: Multiplicativity test for r₈

r₈(n)/16 involves σ₃ with sign adjustments. Is r₈ multiplicative (up to scaling)?
Test with coprime pairs. -/

#eval Id.run do
  let mut results : Array String := #[]
  for (m, n) in ([(3,5), (3,7), (5,7), (7,11), (3,11)] : List (ℕ × ℕ)) do
    let rm := r8 m
    let rn := r8 n
    let rmn := r8 (m * n)
    let predicted := rm * rn / 16
    results := results.push s!"r₈({m})·r₈({n})/16 = {predicted}, r₈({m*n}) = {rmn}, match={predicted == rmn}"
  return results

/-! ## Experiment 15: The signature of perfect numbers

Perfect numbers n satisfy σ₁(n) = 2n. Since r₄ involves σ₁,
perfect numbers should have distinctive Channel 3 signatures. -/

#eval Id.run do
  let perfect := [6, 28, 496]
  let mut results : Array String := #[]
  for n in perfect do
    let s := signature n
    -- For perfect numbers: σ₁(n) = 2n, so the "ideal" r₄ would be related to 16n
    results := results.push s!"Perfect({n}): r₂={s.ch2}, r₄={s.ch3}, r₈={s.ch4}, r₄/(8·2n)={s.ch3}/({8 * 2 * n})"
  return results

/-! ## Experiment 16: The signature of Fibonacci numbers

Do Fibonacci numbers have distinctive signatures? -/

def fib : ℕ → ℕ
  | 0 => 0
  | 1 => 1
  | n + 2 => fib (n + 1) + fib n

#eval Id.run do
  let mut results : Array String := #[]
  for k in List.range 15 do
    let n := fib (k + 2)  -- start from fib(2) = 1
    if n > 0 then
      let s := signature n
      results := results.push s!"fib({k+2})={n}: r₂={s.ch2}, r₄={s.ch3}"
  return results

/-! ## Experiment 17: Representation entropy per channel

Compute average log(r_k(n)) for n ≤ N as a proxy for channel entropy. -/

-- Simple integer log2 approximation
def ilog2 (n : ℕ) : ℕ :=
  if n ≤ 1 then 0
  else 1 + ilog2 (n / 2)

#eval Id.run do
  let N := 200
  let mut sum_log_r2 := 0
  let mut sum_log_r4 := 0
  let mut sum_log_r8 := 0
  let mut count_r2 := 0
  for n in List.range N do
    let s := signature (n + 1)
    if s.ch2 != 0 then
      sum_log_r2 := sum_log_r2 + ilog2 s.ch2.natAbs
      count_r2 := count_r2 + 1
    sum_log_r4 := sum_log_r4 + ilog2 s.ch3.natAbs
    sum_log_r8 := sum_log_r8 + ilog2 s.ch4.natAbs
  let avg_r2 : ℚ := if count_r2 = 0 then 0 else (sum_log_r2 : ℚ) / count_r2
  let avg_r4 : ℚ := (sum_log_r4 : ℚ) / N
  let avg_r8 : ℚ := (sum_log_r8 : ℚ) / N
  return s!"N={N}: avg_log2(r₂|visible)={avg_r2}, avg_log2(r₄)={avg_r4}, avg_log2(r₈)={avg_r8}, r₂_visible={count_r2}/{N}"

/-! ## Experiment 18: The "quantum interference" of Channel 3

For r₄(m+n) vs r₄(m) and r₄(n): is there a pattern in the "interference term"
  I(m,n) = r₄(m+n) - r₄(m) - r₄(n)?
-/

#eval Id.run do
  let mut results : Array String := #[]
  for m in [3, 5, 7, 10, 12] do
    for n in [2, 4, 6, 8] do
      let rm := r4 m
      let rn := r4 n
      let rmn := r4 (m + n)
      let interference := rmn - rm - rn
      results := results.push s!"I({m},{n}) = r₄({m+n}) - r₄({m}) - r₄({n}) = {rmn} - {rm} - {rn} = {interference}"
  return results

/-! ## Experiment 19: Channel 2 as parity detector

For which n does the "parity" (r₂(n) = 0 vs r₂(n) > 0) agree with
a simple function of the prime factorization? Count violations. -/

-- Naive primality test
def isPrime (n : ℕ) : Bool :=
  if n < 2 then false
  else Id.run do
    let mut result := true
    for d in List.range (n - 2) do
      let d' := d + 2
      if d' * d' > n then return result
      if n % d' == 0 then result := false
    return result

-- Check if n has a prime factor ≡ 3 (mod 4) to an odd power
def hasBadFactor (n : ℕ) : Bool :=
  if n == 0 then true
  else Id.run do
    let mut m := n
    for p in List.range (n - 2) do
      let p' := p + 2
      if p' * p' > m then
        -- m is either 1 or a prime
        if m > 1 && m % 4 == 3 then return true
        return false
      if isPrime p' && p' % 4 == 3 then
        let mut count := 0
        while m % p' == 0 do
          m := m / p'
          count := count + 1
        if count % 2 == 1 then return true
    if m > 1 && m % 4 == 3 then return true
    return false

#eval Id.run do
  let mut mismatches := 0
  let mut total := 0
  for n in List.range 200 do
    let n' := n + 1
    let s := signature n'
    let dark := s.ch2 == 0
    let predicted_dark := hasBadFactor n'
    if dark != predicted_dark then
      mismatches := mismatches + 1
    total := total + 1
  return s!"Mismatches between r₂=0 and bad-factor prediction: {mismatches}/{total}"
