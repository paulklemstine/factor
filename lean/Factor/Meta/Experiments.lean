/-
# Computational Experiments

Testing the hypotheses about four-channel integer signatures.
-/

import RequestProject.Defs

/-! ## Experiment 1: Compute signatures for small integers -/

#eval Id.run do
  let mut results : Array String := #[]
  for n in List.range 30 do
    let n' := n + 1
    let s := signature n'
    results := results.push s!"n={n'}: ch2={s.ch2}, ch3={s.ch3}, ch4={s.ch4}"
  return results

/-! ## Experiment 2: Verify known formulas for primes -/

#eval Id.run do
  let primes := [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
  let mut results : Array String := #[]
  for p in primes do
    let s := signature p
    let mod4 := p % 4
    let expected_r4 : ℤ := 8 * (p + 1)
    let expected_r8 : ℤ := if p = 2 then r8 2 else 16 * (1 + (p : ℤ)^3)
    let r4_ok := s.ch3 == expected_r4
    let r8_ok := s.ch4 == expected_r8
    results := results.push s!"p={p} (mod4={mod4}): r₂={s.ch2}, r₄={s.ch3} (exp {expected_r4}, {if r4_ok then "✓" else "✗"}), r₈={s.ch4} (exp {expected_r8}, {if r8_ok then "✓" else "✗"})"
  return results

/-! ## Experiment 3: Channel Entropy — does Channel 4 dominate? -/

#eval Id.run do
  let test_values := [10, 50, 100, 500, 1000, 5000]
  let mut results : Array String := #[]
  for n in test_values do
    let s := signature n
    let total := s.ch2.natAbs + s.ch3.natAbs + s.ch4.natAbs
    let ratio : ℚ := if total = 0 then 0 else (s.ch4.natAbs : ℚ) / total
    results := results.push s!"n={n}: r₂={s.ch2}, r₄={s.ch3}, r₈={s.ch4}, ch4_fraction={ratio}"
  return results

/-! ## Experiment 4: Signature Distance for primes -/

#eval Id.run do
  let primes_1mod4 := [5, 13, 17, 29, 37, 41]
  let primes_3mod4 := [3, 7, 11, 19, 23, 31]
  let mut within_1 : Array String := #[]
  let mut across : Array String := #[]

  for i in List.range primes_1mod4.length do
    for j in List.range i do
      let p := primes_1mod4[i]!
      let q := primes_1mod4[j]!
      let d := sigDistSq (signature p) (signature q)
      within_1 := within_1.push s!"d²({p},{q})={d}"

  for p in (primes_1mod4.take 3) do
    for q in (primes_3mod4.take 3) do
      let d := sigDistSq (signature p) (signature q)
      across := across.push s!"d²({p},{q})={d}"

  return (within_1, across)

/-! ## Experiment 5: Twin primes — bounded signature distance? -/

#eval Id.run do
  let twin_primes : List (ℕ × ℕ) := [(3,5), (5,7), (11,13), (17,19), (29,31), (41,43),
                       (59,61), (71,73), (101,103), (107,109), (137,139),
                       (149,151), (179,181), (191,193), (197,199)]
  let mut results : Array String := #[]
  for (p, q) in twin_primes do
    let sp := signature p
    let sq := signature q
    let d := sigDistSq sp sq
    results := results.push s!"({p},{q}): d²={d}, Δr₂={sp.ch2 - sq.ch2}, Δr₄={sp.ch3 - sq.ch3}, Δr₈={sp.ch4 - sq.ch4}"
  return results

/-! ## Experiment 6: Highly composite numbers vs primes -/

#eval Id.run do
  let hc_numbers := [1, 2, 4, 6, 12, 24, 36, 48, 60, 120]
  let mut results : Array String := #[]
  for n in hc_numbers do
    let s := signature n
    results := results.push s!"HC({n}): r₂={s.ch2}, r₄={s.ch3}, r₈={s.ch4}"
  return results

/-! ## Experiment 7: The "dark matter" of Channel 2 -/

#eval Id.run do
  let mut dark : Array ℕ := #[]
  let mut count := 0
  for n in List.range 100 do
    let n' := n + 1
    let s := signature n'
    if s.ch2 == 0 then
      dark := dark.push n'
      count := count + 1
  return (s!"Dark matter count: {count}/100", dark)

/-! ## Experiment 8: Channel ratios r₈/r₄ -/

#eval Id.run do
  let mut results : Array String := #[]
  for n in [10, 20, 50, 100, 200, 500, 1000] do
    let s := signature n
    let ratio : ℚ := if s.ch3 == 0 then 0 else (s.ch4 : ℚ) / (s.ch3 : ℚ)
    results := results.push s!"n={n}: r₈/r₄={ratio}"
  return results

/-! ## Experiment 9: Product formula verification -/

#eval Id.run do
  let mut results : Array String := #[]
  for (p, q) in ([(5, 3), (5, 7), (13, 3), (13, 7), (17, 3), (17, 11)] : List (ℕ × ℕ)) do
    let n := p * q
    let s := signature n
    results := results.push s!"{p}×{q}={n}: r₂={s.ch2} (expect 0)"
  for (p, q) in ([(5, 3), (5, 7), (13, 3), (13, 7)] : List (ℕ × ℕ)) do
    let n := p * q * q
    let s := signature n
    results := results.push s!"{p}×{q}²={n}: r₂={s.ch2} (expect nonzero)"
  return results

/-! ## Experiment 10: Signature of powers of 2 -/

#eval Id.run do
  let mut results : Array String := #[]
  for k in List.range 12 do
    let n := 2^(k+1)
    let s := signature n
    results := results.push s!"2^{k+1}={n}: r₂={s.ch2}, r₄={s.ch3}, r₈={s.ch4}"
  return results

/-! ## Experiment 11: Eisenstein norm connection

For odd primes p, the ratio r₈(p)/r₄(p) should equal p² - p + 1,
which is the norm of p in ℤ[ω] (Eisenstein integers). -/

#eval Id.run do
  let primes := [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73]
  let mut results : Array String := #[]
  for p in primes do
    let s := signature p
    let ratio : ℚ := (s.ch4 : ℚ) / (s.ch3 : ℚ)
    let eisenstein_norm : ℚ := (p : ℚ)^2 - p + 1
    let match_ := ratio == eisenstein_norm
    results := results.push s!"p={p}: r₈/r₄={ratio}, p²-p+1={eisenstein_norm}, match={match_}"
  return results
