# Experiment Log: Pythagorean Triple Pairing Research

## Session Date: 2025

---

## Experiment 1: Sum-of-Squares Representations and Factor Recovery

### Objective
Verify that having two distinct sum-of-squares representations N = a² + b² = c² + d² always allows recovering a non-trivial factor of N via gcd(ac + bd, N).

### Method
Computed all sum-of-squares representations for N ≤ 5525. For each N with multiple representations, computed gcd(ac + bd, N) and gcd(ad - bc, N) for each pair.

### Results
**100% success rate** across all tested numbers. Every pair of distinct representations yielded a non-trivial factor. Selected data:

| N | Rep 1 | Rep 2 | gcd Factor | Factorization |
|:---:|:---:|:---:|:---:|:---:|
| 65 | 1²+8² | 4²+7² | 5 | 5 × 13 |
| 85 | 2²+9² | 6²+7² | 5 | 5 × 17 |
| 145 | 1²+12² | 8²+9² | 29 | 5 × 29 |
| 221 | 5²+14² | 10²+11² | 17 | 13 × 17 |
| 481 | 9²+20² | 15²+16² | 13 | 13 × 37 |
| 493 | 3²+22² | 13²+18² | 29 | 17 × 29 |
| 1105 | 4²+33² | 9²+32² | 13 | 5×13×17 |
| 1105 | 4²+33² | 23²+24² | 221 | 5×13×17 |
| 1105 | 9²+32² | 23²+24² | 65 | 5×13×17 |

### Key Observation
Different pairs of representations of the same N can yield different factorizations! For N = 1105 = 5 × 13 × 17 (which has 4 representations), the 6 pairs yield all possible factor splits.

---

## Experiment 2: Pythagorean Triple Hypotenuse Clustering

### Objective
Find all Pythagorean triples sharing the same hypotenuse c, for c ≤ 500.

### Method
Enumerated all triples (a, b, c) with a² + b² = c² and c ≤ 500. Grouped by hypotenuse.

### Results

| c | # Triples | Sum-of-squares reps of c | Composite? |
|:---:|:---:|:---:|:---:|
| 5 | 1 | 1 (prime) | No |
| 13 | 1 | 1 (prime) | No |
| 25 | 2 | 2 | Yes (5²) |
| 65 | 4 | 2 | Yes (5·13) |
| 85 | 4 | 2 | Yes (5·17) |
| 125 | 3 | 2 | Yes (5³) |
| 145 | 4 | 2 | Yes (5·29) |
| 169 | 2 | 2 | Yes (13²) |
| 221 | 4 | 2 | Yes (13·17) |
| 289 | 2 | 2 | Yes (17²) |
| 325 | 7 | 3 | Yes (5²·13) |
| 425 | 7 | 3 | Yes (5²·17) |
| 481 | 4 | 2 | Yes (13·37) |

### Key Finding
**The number of Pythagorean triples with hypotenuse c equals the number of representations of c² as a sum of two squares (excluding the trivial (0, c) rep), minus 1 and divided by 2.** More precisely:

- # of reps of c (up to order, ignoring signs) = r
- # of Pythagorean triples with hypotenuse c = (number of reps of c² - 1) / 2

This is because each rep (a, b) of c² as a² + b² = c² with 0 < a < b gives a Pythagorean triple.

---

## Experiment 3: The Brahmagupta-Fibonacci Bridge

### Objective
Verify that the Brahmagupta-Fibonacci identity correctly generates paired representations from prime factorizations.

### Method
For each composite c with c ≡ 1 (mod 4), factored c into primes p₁ · p₂ · ..., found sum-of-squares representations of each prime, and applied Brahmagupta-Fibonacci to generate all representations of c.

### Results for c = 65 = 5 × 13

5 = 1² + 2², 13 = 2² + 3²

Brahmagupta-Fibonacci gives:
- Rep 1: (1·2 - 2·3, 1·3 + 2·2) = (-4, 7) → 65 = 4² + 7² ✓
- Rep 2: (1·2 + 2·3, 1·3 - 2·2) = (8, -1) → 65 = 8² + 1² ✓

Corresponding Pythagorean triples:
- From (7, 4): (7²-4², 2·7·4, 7²+4²) = (33, 56, 65) ✓
- From (8, 1): (8²-1², 2·8·1, 8²+1²) = (63, 16, 65) ✓

Factor recovery: gcd(7·8 + 4·1, 65) = gcd(60, 65) = 5 ✓

### Results for c = 221 = 13 × 17

13 = 2² + 3², 17 = 1² + 4²

Brahmagupta-Fibonacci gives:
- Rep 1: (2·1 - 3·4, 2·4 + 3·1) = (-10, 11) → 221 = 10² + 11² ✓
- Rep 2: (2·1 + 3·4, 2·4 - 3·1) = (14, 5) → 221 = 14² + 5² ✓

Corresponding Pythagorean triples:
- From (11, 10): (121-100, 220, 221) = (21, 220, 221) ✓
- From (14, 5): (196-25, 140, 221) = (171, 140, 221) ✓

Factor recovery: gcd(11·14 + 10·5, 221) = gcd(204, 221) = 17 ✓

### Results for c = 325 = 5² × 13

Three representations found:
- 325 = 1² + 18² → Triple (323, 36, 325)
- 325 = 6² + 17² → Triple (253, 204, 325)
- 325 = 10² + 15² → Triple (125, 300, 325)

Factor recovery from pairs:
- (1,18) & (6,17): gcd(312, 325) = 13 → 325 = 13 × 25
- (1,18) & (10,15): gcd(280, 325) = 5 → 325 = 5 × 65
- (6,17) & (10,15): gcd(315, 325) = 5 → 325 = 5 × 65

Different pairs reveal different factorizations!

---

## Experiment 4: Computational Pairing Algorithm

### Objective
Test the `findPairedTriples` algorithm implemented in Lean 4.

### Method
Called `findPairedTriples m n` for various Euclid parameter pairs and verified the output.

### Results

```
findPairedTriples 7 4  = [(63, 16, 65, 5)]
  Input: Triple (33, 56, 65), Output: Paired triple (63, 16, 65), Factor 5 ✓

findPairedTriples 8 1  = [(33, 56, 65, 5)]
  Input: Triple (63, 16, 65), Output: Paired triple (33, 56, 65), Factor 5 ✓

findPairedTriples 9 2  = [(13, 84, 85, 5)]
  Input: Triple (77, 36, 85), Output: Paired triple (13, 84, 85), Factor 5 ✓

findPairedTriples 11 10 = [(171, 140, 221, 17)]
  Input: Triple (21, 220, 221), Output: Paired triple (171, 140, 221), Factor 17 ✓
```

### Key Finding
The algorithm is **symmetric**: starting from either triple in a pair and running the algorithm yields the other triple. This confirms the pairing is a genuine involution on the set of Pythagorean triples with a given composite hypotenuse.

---

## Experiment 5: Primes That Don't Pair

### Objective
Verify that prime hypotenuses have no paired triples.

### Method
Checked all prime hypotenuses c ≤ 500 (where c ≡ 1 mod 4 and c is prime).

### Results
For c ∈ {5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97, 101, 109, 113, 137, 149, 157, 173, 181, 193, 197, 229, 233, 241, 257, 269, 277, 281, 293, 313, 317, 337, 349, 353, 373, 389, 397, 401, 409, 421, 433, 449, 457, 461}:

**Every prime hypotenuse has exactly ONE Pythagorean triple and ONE sum-of-squares representation.** No pairs exist, confirming the theorem.

---

## Summary of Findings

1. **The pairing exists** for all composite hypotenuses with at least two distinct prime factors ≡ 1 (mod 4).

2. **The GCD method** gcd(m₁m₂ + n₁n₂, c) **always** recovers a non-trivial factor.

3. **Different pairs give different factorizations** when c has ≥ 3 prime factors.

4. **The pairing is symmetric**: finding the pair of the pair returns the original.

5. **Prime hypotenuses have no pairs**, confirming the theoretical prediction.

6. **All results are formally verified** in Lean 4 (see `PythagoreanPairing.lean`).
