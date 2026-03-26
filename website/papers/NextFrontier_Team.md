# Research Team: Where Do We Go From Here?

## Project PHOTON-∞ — Beyond the Null Cone

### Mission Statement
Extend the arithmetic spacetime program from Pythagorean triples (2+1 dimensions) to Pythagorean quadruples (3+1 dimensions) and the "dark matter" of non-Pythagorean triples, using formal verification in Lean 4 with Mathlib.

---

## Team Roster

### Agent D (Dimensions) — *Pythagorean Quadruples Lead*
**Focus**: The (3+1)-dimensional null cone, SO(3,1;ℤ), and the infinite branching phenomenon.

**Key findings**:
- Formalized the full (3+1) Lorentz form Q₄(a,b,c,d) = a² + b² + c² - d²
- Proved the parametrization theorem: every quadruple arises from (m,n,p,q) parameters
- Verified all three spatial rotations preserve the Lorentz form (`native_decide`)
- **Discovered the infinite branching theorem**: unlike triples (ternary tree), quadruples form infinite forests — no finite set of matrices generates all primitive solutions from a single root

### Agent M (Mass) — *Dark Matter Lead*
**Focus**: Non-Pythagorean triples, mass shells, and the arithmetic equivalence principle.

**Key findings**:
- Proved that the Berggren matrices preserve Q for ALL values, not just Q = 0
- Formally verified mass conservation along dark matter tree paths (induction on DarkPath)
- Proved that every non-negative integer mass-squared is realized
- Computational census: photon fraction → 0 as N → ∞ (e.g., 52 photons among 171,648 triples at N=100)

### Agent C (Computation) — *Experimental Computation*
**Focus**: Computational exploration, census data, and pattern discovery.

**Key experiments**:
- Counted quadruples up to hypotenuse N: growth is Θ(N²) vs Θ(N) for triples
- Dark matter census: classified triples by causal type (null/timelike/spacelike)
- Generated dark matter trees from various seeds, verified mass conservation
- Tachyon tree exploration: (2,2,1) seed with mass² = -7

### Agent L (Lorentz) — *Group Theory*
**Focus**: SO(3,1;ℤ), the full integer Lorentz group in 4 dimensions.

**Key findings**:
- Formalized O(3,1;ℤ) membership predicate
- Proved identity, rot₁₂, rot₁₃, rot₂₃ are Lorentz transformations
- Proved Lorentz transformations preserve null vectors (the key invariance theorem)
- Embedded the (2+1) theory into (3+1) via tripleToQuad

### Agent O (Oracle) — *Interpretation & Synthesis*
**Focus**: Physical interpretation, oracle consultations, and philosophical implications.

**Key oracle pronouncements**:
1. Quadruples form forests, not trees — reflecting the 2D moduli space
2. The celestial sphere S² = ℂP¹ connects arithmetic photons to complex analysis
3. Dark matter has the SAME tree structure as light (arithmetic equivalence principle)
4. The Berggren matrices are mass-independent: universal tree generators

### Agent P (Publication) — *Writing & Documentation*
**Focus**: Research paper, Scientific American article, lab notes.

**Deliverables**:
- `NextFrontier_ResearchPaper.md` — Full research paper with formal results
- `NextFrontier_SciAm.md` — Popular science article
- `NextFrontier_LabNotebook.md` — Detailed experimental notes
- `PythagoreanQuadruples.lean` — 30+ verified theorems on quadruples
- `ArithmeticDarkMatter.lean` — 20+ verified theorems on dark matter

---

## Theorem Count Summary

| File | Theorems | Sorry-free |
|------|----------|------------|
| `PythagoreanQuadruples.lean` | 30+ | ✅ All proved |
| `ArithmeticDarkMatter.lean` | 20+ | ✅ All proved |

## Key Cross-References

- Extends `Research/QuaternaryPythagoreanTree.lean` (the (3+1) PHOTON-4 project)
- Builds on `Core/BerggrenTree.lean` (the original ternary tree)
- Connected to `Core/SL2Theory.lean` (group-theoretic foundations)
