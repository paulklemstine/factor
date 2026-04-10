# Research Team: Berggren-Ramanujan Open Problems Initiative

## Team Structure

### Principal Investigators

**PI-1: Spectral Theory Lead**
- Focus: Eigenvalue bounds for quotient graphs G_p, Ramanujan certification
- Expertise: algebraic graph theory, representation theory
- Current hypothesis: The Ramanujan property for G_p is governed by the splitting behavior of √2 mod p. When p ≡ ±1 (mod 8), √2 splits in 𝔽_p, producing smaller orbits with better spectral gaps.
- Next experiment: Compute full spectra of G_p for p = 47, 53, 59, 61 using orbit enumeration + adjacency matrix eigendecomposition.

**PI-2: Number Theory Lead**
- Focus: Pell equation connections, quaternion algebras, density of Ramanujan primes
- Expertise: algebraic number theory, automorphic forms
- Current hypothesis: The Berggren group Γ ⊂ O(2,1;ℤ) ≅ PGL(2,ℤ[√2]) is commensurable with a congruence subgroup, and the Ramanujan property for G_p follows from the Ramanujan-Petersson conjecture for GL(2) automorphic forms over ℚ(√2).
- Next experiment: Determine the exact index [PGL(2,ℤ[√2]) : Γ] and check whether Γ is a congruence subgroup.

**PI-3: Combinatorics Lead**
- Focus: 5D completeness, forest structure, higher-dimensional generalizations
- Expertise: combinatorial group theory, tree enumeration
- Current hypothesis: The number of root quintuples needed for 5D completeness equals the number of orbits of primitive quintuples under the permutation group S₄ (permuting the first 4 coordinates).
- Next experiment: Enumerate all primitive quintuples with d ≤ 100 and check which are reachable from each root.

---

## Active Hypotheses

### H1: Density-Zero Conjecture
**Statement**: The set {p prime : G_p is Ramanujan} has natural density 0.

**Evidence for**:
- G₁₁ already fails the Ramanujan bound
- Generator orders grow with p (order 6 at p=5,7 → order 14 at p=13)
- Larger orbits → more opportunities for eigenvalues to exceed 2√5

**Evidence against**:
- LPS graphs are Ramanujan for ALL primes (if constructed correctly)
- Only 3 primes tested computationally so far

**Proposed experiment**: Compute spectra for p = 5, 7, 11, 13, 17, 19, 23, 29. If G₁₃ fails, the conjecture is strongly supported. If it succeeds, the pattern is more complex.

### H2: Universal Chebyshev Trace Formula
**Statement**: For any w ∈ ⟨B₁,B₂,B₃⟩ with |det(w)| = 1, the trace formula is:
tr(wⁿ) = det(w)ⁿ + 2Tₙ(c_w)
where c_w = (α_w + α_w⁻¹)/2 for the dominant eigenvalue α_w.

**Status**: Verified for B₂ (c=3), B₁B₂ (c=9), B₁B₃ (c=7). Need to verify for longer words.

**Proposed experiment**: Compute traces for B₁B₂B₃, B₁²B₂, B₂²B₃ and verify the Chebyshev formula.

### H3: Congruence Subgroup Property
**Statement**: The Berggren group Γ = ⟨B₁,B₂,B₃⟩ is a congruence subgroup of O(2,1;ℤ).

**Significance**: If true, the Ramanujan property for G_p would follow from the Jacquet-Langlands correspondence + Ramanujan conjecture for GL(2).

**Proposed experiment**: Compute the level of Γ (smallest N such that Γ ⊃ ker(O(2,1;ℤ) → O(2,1;ℤ/Nℤ))).

### H4: Optimal 5D Forest
**Statement**: The 5D tree requires exactly 3 roots: (1,0,0,0,1), (1,1,0,0,√2) [non-primitive], and (1,1,1,1,2).

**Status**: Speculative. Need systematic enumeration.

### H5: Quaternion Construction Existence
**Statement**: There exists a maximal order O in the quaternion algebra H(-1,-2|ℚ) and a finite set S ⊂ O of norm-1 elements such that the Cayley graph Cay(O/pO, S mod p) is Ramanujan for all primes p that do not ramify in H.

**Significance**: Would provide an LPS-type construction from Pythagorean arithmetic.

---

## Experimental Pipeline

### Phase 1: Computational Exploration (Current)
1. ✅ Lorentz preservation for p = 5,...,43
2. ✅ Generator orders mod small primes
3. ✅ Chebyshev formula for B₂, B₁B₂, B₁B₃
4. ⬜ Full spectrum computation for G₅, G₇, G₁₁, G₁₃
5. ⬜ Orbit enumeration for p ≤ 50
6. ⬜ 5D quintuple enumeration to depth 5

### Phase 2: Structural Analysis
1. ⬜ Index computation [PGL(2,ℤ[√2]) : Γ]
2. ⬜ Congruence subgroup test
3. ⬜ Quaternion algebra identification
4. ⬜ Representation theory of O(2,1;𝔽_p)

### Phase 3: Proof Development
1. ⬜ Formal proof of Chebyshev trace formula (general n)
2. ⬜ Formal proof of spectral gap positivity (general d)
3. ⬜ Formal proof of Lorentz preservation for general p
4. ⬜ Formal proof of 5D completeness obstruction

### Phase 4: Publication
1. ⬜ ArXiv preprint
2. ⬜ Lean formalization package
3. ⬜ Python visualization suite
4. ⬜ Peer review and revision

---

## Brainstorming: New Hypotheses from Recent Discoveries

### From the Pell-Chebyshev Connection:
- **H6**: The continued fraction expansion of √2 = [1; 2, 2, 2, ...] is related to the branching structure of the Berggren tree via the matrix identity B₂ⁿ = C_n where C_n encodes the n-th convergent of √2.

### From the -1 Eigenvalue Analysis:
- **H7**: The eigenvector (1,-1,0) of B₂ is the unique (up to scale) fixed point of the involution B₂ → QB₂Q, suggesting a natural Z/2 grading of the Berggren group.
- **H8**: The spectral gap of G_p is maximized when p ≡ 3 (mod 8) (when √2 ∉ 𝔽_p, forcing the eigenvalue pair to live in 𝔽_{p²}).

### From the Mixed Generator Analysis:
- **H9**: The Chebyshev parameter c_w for a word w of length ℓ satisfies c_w ≈ (3+2√2)^ℓ, growing exponentially with word length. This means trace formulas for longer words involve Chebyshev polynomials at rapidly growing arguments.
- **H10**: The set {c_w : w ∈ ⟨B₁,B₂,B₃⟩} is dense in [1,∞), providing a way to approximate any Chebyshev parameter.

### From the 5D Analysis:
- **H11**: In dimension 2n+1, the number of generators needed is n(n+1)/2 (= n choose 2 for parabolic-type + n for hyperbolic-type).
- **H12**: The parabolic/hyperbolic ratio (det=1 vs det=-1 generators) approaches 1/2 as dimension → ∞.

---

## Validation Protocol

For each hypothesis:
1. **Computational check**: Test against small examples using Python/SageMath
2. **Lean formalization**: State as a Lean theorem (possibly with sorry)
3. **Proof search**: Attempt formal proof using automated tools
4. **Peer discussion**: Present findings to team for critique
5. **Upgrade or reject**: Based on evidence, either strengthen the hypothesis or document counterexamples

---

## Meeting Schedule

- **Weekly**: Progress updates, hypothesis brainstorming
- **Monthly**: Full team review, priority reassessment
- **Quarterly**: External review, publication planning
