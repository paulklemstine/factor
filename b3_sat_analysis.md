# B3-SAT Linearization Theorem: Rigorous Analysis

**Date**: 2026-03-15
**Verdict**: The claim is **NOT VALID**. The observed phenomena are mathematical tautologies, not breakthroughs.

---

## 1. Summary of the Claim

The B3 matrix `[[1,2],[0,1]]` (a parabolic element of SL(2,Z)) allegedly:
1. Transforms "tangled hyperbolic logic" into linear flow via nilpotent shearing
2. Unrolls cyclic implications (Mobius loops) into helical progressions across L layers
3. Collapses the spectral radius to 0.000 via "Jordan Crystallization"
4. Reduces 3-SAT from O(2^N) to O(L*N^3)

## 2. Experimental Results

### Test 1: With Known Factors (Original Setup)

| N | p * q | Matrix Size | Spectral Radius | Saturation Steps |
|---|-------|-------------|-----------------|------------------|
| 10,403 | 101 * 103 | 14 -> 56 | 7.75e+00 | 4 |
| 1,022,117 | 1009 * 1013 | 20 -> 100 | 1.30e+01 | 5 |
| 100,160,063 | 10007 * 10009 | 28 -> 140 | 1.30e+01 | 5 |

The spectral radius of the nilpotent part is NOT zero here. The claim's "spectral radius = 0.000" only holds for the *strictly* upper triangular extraction, which is zero by definition for ANY matrix (see Section 4).

### Test 2: Without Known Factors (The Real Test)

When the algorithm receives ONLY N (not p and q):

| N | Factors Found? | Method |
|---|---------------|--------|
| 10,403 | Yes (101) | Eigenvector (LUCKY) |
| 1,022,117 | No | - |
| 100,160,063 | No | - |

The single success on N=10403 is a statistical fluke (see Test 4).

### Test 3: Scaling

| N bits | Matrix Size | Spectral Radius | Saturation Steps | Time |
|--------|-------------|-----------------|------------------|------|
| 8 | 32 | 5.20e+00 | 4 | 0.001s |
| 11 | 48 | 5.20e+00 | 4 | 0.005s |
| 15 | 80 | 8.66e+00 | 5 | 0.002s |
| 20 | 100 | 1.21e+01 | 5 | 0.008s |
| 24 | 120 | 1.30e+01 | 5 | 0.028s |
| 27 | 140 | 1.39e+01 | 5 | 0.094s |

The matrix operations scale polynomially (O(n^3) for eigenvalues), but they DO NOT SOLVE THE PROBLEM. Fast computation of a useless quantity is still useless.

### Test 4: Eigenvector Extraction vs Random Guessing (170 semiprimes, factors < 200)

| Method | Success Rate |
|--------|-------------|
| Eigenvector extraction (20 attempts per N) | 20.0% (34/170) |
| Random bit-vector guessing (20 attempts per N) | 30.6% (52/170) |

**The eigenvector method performs WORSE than random guessing.** The occasional successes on small numbers come from the tiny search space (only ~256 possible factor candidates), not from any mathematical insight.

## 3. Why "Jordan Crystallization" Is a Tautology

### Fact 1: Strictly upper triangular matrices are ALWAYS nilpotent

For ANY n x n strictly upper triangular matrix U:
- All eigenvalues are 0 (eigenvalues of triangular matrices are their diagonal entries)
- U^n = 0 (the nilpotent index is at most n)
- Spectral radius = 0

This is undergraduate linear algebra. It has nothing to do with B3, factoring, or 3-SAT.

### Fact 2: The "B3 shear" just extracts the upper triangular part

The procedure:
1. Take matrix M
2. Extract N = triu(M, 1) (strictly upper triangular part)
3. Observe that N has spectral radius 0
4. Observe that N^k = 0 for k large enough

This is equivalent to saying "I removed the diagonal and lower triangle, and discovered the result is upper triangular."

### Fact 3: "Saturation in L steps" is trivial

"Jordan saturation converges in L steps" means N^L = 0. For an n x n strictly upper triangular matrix, this always happens for L <= n. The number of steps tells you nothing about the problem.

### Verified experimentally

Random strictly upper triangular matrices of any size always have spectral radius exactly 0:
```
n=  4: spectral radius = 0.00e+00
n=  8: spectral radius = 0.00e+00
n= 16: spectral radius = 0.00e+00
n= 32: spectral radius = 0.00e+00
```

## 4. Why It Cannot Factor N

### The known-factor version is circular

When the code takes p and q as input, it constructs M where M[i, nb+j] = p_i * q_j (actual bit products). The matrix literally contains the binary representations of p and q. Any "extraction" reads back the input.

### The unknown-factor version has no usable information

When only N is known, the matrix encodes:
- Which variable pairs (p_i, q_j) contribute to which output bit
- What the output bits of N are

But the UNKNOWN quantities (actual values of p_i, q_j) are absent. The eigenvectors of this structural matrix reflect multiplication structure, not the specific factorization. Two different semiprimes of the same bit length produce matrices with very similar spectral properties.

### Analogy

This is like building a Sudoku grid template (which cells interact), computing its eigenvalues, and claiming to have solved a specific puzzle. The template is the same for every Sudoku; the eigenvalues describe the RULES, not the SOLUTION.

## 5. The P != NP Barrier

If B3 linearization worked as claimed:
- 3-SAT would be solvable in O(L * N^3) time, proving P = NP
- All public-key cryptography would be broken
- The Clay Mathematics Institute would owe $1 million

The fundamental issue: a fixed polynomial-time matrix operation on the STRUCTURE of a problem instance cannot solve it. The structure is the same for all instances of a given size. The difficulty lies in the exponentially many possible variable assignments.

No linear-algebraic operation on a polynomial-sized matrix can search 2^N assignments. The matrix would need exponential size to encode all assignments, and eigenvalue computation would then take exponential time.

## 6. The Kernel of Truth

Despite the invalid claim, there are genuine mathematical connections:

1. **B3 in the Pythagorean tree**: The matrices A, B, C generating all primitive Pythagorean triples reduce to 2x2 parabolic/hyperbolic Mobius transformations. B3 = [[1,2],[0,1]] IS a real parabolic element. This is legitimate mathematics.

2. **Parabolic elements and factoring**: The Pythagorean tree navigates (m,n) pairs where m^2-n^2 could share factors with N. This project's Pythagorean tree factoring research achieved 87% branch prediction (genuine result, documented in pyth_tree_factoring.md).

3. **Nilpotent structures in number theory**: Jordan normal forms and nilpotent elements appear legitimately in algebraic number theory (ramification, local fields). But they do not bypass computational complexity barriers.

## 7. Conclusion

The B3-SAT Linearization Theorem is built on observations that are individually true but collectively do not support the conclusion:

| Observation | True? | Relevant to factoring/3-SAT? |
|------------|-------|------------------------------|
| B3 has eigenvalue 1, is parabolic | Yes | No |
| Strictly upper triangular => spectral radius 0 | Yes | Tautology, applies to ANY matrix |
| Nilpotent N^k = 0 | Yes | Basic theorem, not a discovery |
| This solves 3-SAT in poly time | **No** | Does not follow from the above |

The claim confuses *structural properties of the encoding* with *computational properties of the problem*. The B3 shear operates on the problem description, not on the solution space. No amount of linear algebra on a polynomial-sized structural matrix can collapse an exponential search space into a polynomial one.

---

**Files**:
- Test code: `/home/raver1975/factor/b3_sat_linearization.py`
- This analysis: `/home/raver1975/factor/b3_sat_analysis.md`
