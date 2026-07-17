# Experiment Log: Berggren Homing Missile Verification

## Session Summary
- **New theorems proved**: 45+
- **New Lean files**: 2 (HomingMissile.lean, MathExplorations.lean)
- **New sorry count in default build**: 0 (reduced from previous)
- **Non-standard axioms**: None

---

## New Experiments (This Session)

### HomingMissile.lean — Error Signal Analysis

| # | Theorem | Status | Proof Method |
|---|---------|--------|--------------|
| 1 | error_signal_algebra | ✅ | ring |
| 2 | error_signal_mod_p | ✅ | Algebraic expansion + divisibility |
| 3 | error_signal_factors | ✅ | ring |
| 4 | error_at_target | ✅ | ring |
| 5 | error_at_one | ✅ | ring |
| 6 | error_symmetry | ✅ | ring |
| 7 | error_at_neg_one | ✅ | ring |
| 8 | error_decomposition | ✅ | ring |
| 9 | linear_approx_error | ✅ | ring |
| 10 | quadratic_dominates | ✅ | abs manipulation + nlinarith |
| 11 | error_grows | ✅ | nlinarith |
| 12 | error_grows_neg | ✅ | nlinarith |
| 13 | linear_nav_exact | ✅ | omega |
| 14 | nav_overshoot_exact | ✅ | ring (over ℚ) |
| 15 | overshoot_bound | ✅ | nlinarith + sq_abs |
| 16 | error_zero_iff | ✅ | IsDomain + mul_eq_zero |
| 17 | multi_form_speedup | ✅ | Nat.div_le_self |
| 18 | total_steps_bound | ✅ | sqrt bound + omega |

### MathExplorations.lean — 20 Areas

| # | Area | Theorem | Status |
|---|------|---------|--------|
| 1 | Modular Arithmetic | prime_mod_four | ✅ |
| 2 | Modular Arithmetic | wilson_theorem' | ✅ |
| 3 | Pell Equations | pell_equation_small | ✅ |
| 4 | Pell Equations | pell_recurrence | ✅ |
| 5 | Gaussian Integers | gaussian_norm_mul | ✅ |
| 6 | Gaussian Integers | brahmagupta_fibonacci | ✅ |
| 7 | Analytic NT | bertrand_postulate' | ✅ |
| 8 | Analytic NT | primes_infinite' | ✅ |
| 9 | Diophantine | markov_generate | ✅ |
| 10 | Lattice Theory | lagrange_four_sq_* (×4) | ✅ |
| 11 | Graph Theory | ternary_tree_sum | ✅ |
| 12 | Info Theory | binary_entropy_bound | ✅ |
| 13 | Dynamical Systems | contracting_terminates | ✅ |
| 14 | Dynamical Systems | parent_hyp_less | ✅ |
| 15 | p-adic Numbers | legendre_formula_example | ✅ |
| 16 | p-adic Numbers | padic_val_mul' | ✅ |
| 17 | Elliptic Curves | congruent_5, congruent_6 | ✅ |
| 18 | Sieve Theory | smallest_factor_le_sqrt | ✅ |
| 19 | Additive Comb | sumset_singleton_card | ✅ |
| 20 | Geometric Algebra | pyth_on_lightcone | ✅ |
| 21 | Geometric Algebra | lorentz_add_left | ✅ |
| 22 | Algebraic Topology | euler_char_genus | ✅ |
| 23 | Operator Theory | cayley_hamilton_2x2_identity | ✅ |
| 24 | Finite Fields | Fp_card, fermat_little, Fp_star_cyclic | ✅ |
| 25 | Ramsey Theory | ramsey_lower (R(3,3) > 5) | ✅ |
| 26 | Tropical Geometry | trop_distrib | ✅ |
| 27 | Descriptive Set Theory | pyth_triples_finite | ✅ |
| 28 | New Theorem | error_nonneg_over_Z | ✅ |

### Failed Experiments
- ❌ Sauer-Shelah lemma — too deep for automated proving
- ❌ LYM inequality — requires chain counting infrastructure
- ❌ SES rank-nullity — not in default build, difficult

---

## Key Technical Insights (This Session)

1. **ZMod API quirks**: `ZMod.natCast_eq_zero_iff` replaces the old `ZMod.natCast_zmod_eq_zero_iff_dvd`. Must use `haveI : IsDomain (ZMod p)` for `mul_eq_zero` over ZMod.

2. **padicValNat needs Fact**: The `padicValNat.mul` lemma requires `[Fact (Nat.Prime p)]`, not just `Nat.Prime p` as a hypothesis. Use `haveI : Fact ... := ⟨hp⟩`.

3. **Nat.exists_prime_lt_and_le_two_mul** takes `n ≠ 0` not `1 ≤ n`, and returns `∃ p, Nat.Prime p ∧ n < p ∧ p ≤ 2 * n`.

4. **Integer division in proofs**: Working with `(p-1)/2` over ℤ requires careful handling of `Int.ediv`. The key identity `2 * ((p-1)/2) = p - 1` for odd p requires the oddness hypothesis.

5. **abs simplification**: For `|4 * δ ^ 2|`, need to decompose as `|4| * |δ^2|` then use `abs_of_nonneg (sq_nonneg δ)`.

---

## Research Directions Identified

### High Priority
1. **Error signal over 𝔽_p**: The 2-root property suggests connections to quadratic reciprocity
2. **Multi-polynomial sieve**: Formalize the constant-factor speedup more precisely
3. **Berggren-Markov connection**: Both trees share structural properties

### Medium Priority
4. **Tropical Berggren**: Can tropicalized matrices give shortest-path algorithms?
5. **p-adic factor estimation**: Use v_p(error) to bound factor size
6. **Spectral theory**: Eigenvalues of Berggren matrices and automorphic forms

### Exploratory
7. **Lattice reduction connection**: Is Berggren descent related to LLL?
8. **Quantum advantage**: Can Shor's algorithm be interpreted in Berggren coordinates?
9. **Higher-dimensional generalizations**: Extend to sum-of-k-squares
