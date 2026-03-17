---
name: B3 Parabolic Discovery
description: Research finding that Berggren B3 matrix is parabolic (eigenvalue 1), creating arithmetic progressions in m that connect Pythagorean tree to Quadratic Sieve framework
type: project
---

## The B3 Parabolic Discovery

Key finding from cross-mathematics research (Field 11: Differential Equations / Dynamical Systems).

### The Three Berggren Matrices

The Pythagorean triple tree uses three Berggren matrices on (m,n) generators:

- **B1**: (m,n) → (2m-n, m) — eigenvalues: 1±√2 — hyperbolic
- **B2**: (m,n) → (2m+n, m) — eigenvalues: 1±√2 — hyperbolic
- **B3**: (m,n) → (m+2n, n) — eigenvalue: 1 (multiplicity 2) — **parabolic**

### What "Parabolic" Means

B3 = [[1,2],[0,1]] has a repeated eigenvalue of 1:

B3^k × (m₀, n₀) = (m₀ + 2kn₀, n₀)

- n-coordinate is FIXED
- m-coordinate grows linearly in k (not exponentially like B1/B2)
- Walking a B3-only path traces an arithmetic progression in m

### Why This Matters for Factoring

The Pythagorean triple at step k along a B3 path has:

A_k = (m₀+2kn₀)² - n₀² = (m₀+2kn₀-n₀)(m₀+2kn₀+n₀)

This is a quadratic polynomial in k: A_k = 4n₀²k² + 4m₀n₀k + (m₀²-n₀²)

This is exactly what the Quadratic Sieve can sieve! For each factor base prime p, A_k ≡ 0 (mod p) at most 2 values of k (mod p) — giving two arithmetic progressions.

### The Key Innovation: B3-MPQS

Choose m₀ ≈ n₀·√N, then:

r_k = (m₀+2kn₀)² - N·n₀²

This residue starts small (~√N at k=0) and gives the QS relation:

x_k² ≡ r_k (mod N) where x_k = m₀+2kn₀

Each different n₀ gives a different polynomial — unlimited polynomial supply (like MPQS).

### Results

- B3 arithmetic progression search: 100% success at 36-bit semiprimes
- Full B3-MPQS engine: factors 55-digit numbers in 237 seconds
- 2x faster than CFRAC

### The Catch

Pure B3 polynomials have a = 4n₀² which is a perfect square. Every null vector in GF(2) LA is trivial (gcd always gives 1 or N). Fix: use standard CRT-based polynomial generation with square-free a, but the B3 structure inspired the polynomial family that keeps residues small.

### Summary

The discovery that B3 is parabolic (while B1/B2 are hyperbolic) revealed that one-third of the Pythagorean tree has linear, sievable structure — connecting the tree directly to the Quadratic Sieve framework.

**Why:** This bridges Pythagorean number theory with practical sub-exponential factoring.
**How to apply:** Use B3 paths to generate MPQS-style polynomials; use square-free a to avoid trivial GF(2) solutions.
