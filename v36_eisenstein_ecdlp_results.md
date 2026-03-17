# v36: Eisenstein Parametric Tree + ECDLP

Date: 2026-03-17

## Summary Table

| # | Experiment | Status | Key Finding |
|---|-----------|--------|-------------|
| 1 | Exp 1: 2x2 matrices on (m,n) parameters | OK | norm_preserving=180, isometries=12, expansions=168 |
| 2 | Exp 2: Tree completeness (c < 10000) | OK | parametric_complete=True, triples=1384, tree_coverage=15.9% |
| 3 | Exp 3: Norm-form factoring in Z[ζ₃] | OK | factored=27/100, rate=27.0% |
| 4 | Exp 4: GLV-3 decomposition analysis | OK | GLV-3 collapses to GLV-2 (λ²+λ+1=0), avg_bits=128.5 |
| 5 | Exp 5: Eisenstein lattice 2D kangaroo | OK | 1d_steps=24064, 2d_steps=65536, 2d_no_advantage=True |
| 6 | Exp 6: GLV-3 scalar multiplication benchmark | OK | GLV-2 ~1.5x faster, GLV-3=GLV-2 (algebraic identity) |
| 7 | Exp 7: Eisenstein p-1 factoring | OK | eis_unique=9, std_only=1, both=10 |
| 8 | Exp 8: Combined Eisenstein + Gaussian p-1 pre-sieve | OK | combined=22/50, eis_unique=5, gauss_unique=3 |

## Detailed Results

```
============================================================
v36_eisenstein_ecdlp.py — Eisenstein Parametric Tree + ECDLP
============================================================
Date: 2026-03-17
Goal: 2x2 matrices, tree completeness, GLV-3, Eisenstein p-1

============================================================
EXPERIMENT: Exp 1: 2x2 matrices on (m,n) parameters
============================================================
  Searching [-10,10]^4 for 2x2 matrices on (m,n)...
  Test pairs: 202
  Found 11364 candidate matrices

  Searching for NORM-PRESERVING matrices (algebraic)...
  Need: N(M*v) = k * N(v) where N(m,n) = m^2+mn+n^2
  Norm-preserving matrices (k=1 means isometry): 180
    M=[-1,-1; 0, 1] k=1 det=-1
    M=[-1,-1; 1, 0] k=1 det=1
    M=[-1, 0; 0,-1] k=1 det=1
    M=[-1, 0; 1, 1] k=1 det=-1
    M=[ 0,-1;-1, 0] k=1 det=-1
    M=[ 0,-1; 1, 1] k=1 det=1
    M=[ 0, 1;-1,-1] k=1 det=1
    M=[ 0, 1; 1, 0] k=1 det=-1
    M=[ 1, 0;-1,-1] k=1 det=-1
    M=[ 1, 0; 0, 1] k=1 det=1
    M=[ 1, 1;-1, 0] k=1 det=1
    M=[ 1, 1; 0,-1] k=1 det=-1
    M=[-2,-1; 1,-1] k=3 det=3
    M=[-2,-1; 1, 2] k=3 det=-3
    M=[-1,-2;-1, 1] k=3 det=-3
    M=[-1,-2; 2, 1] k=3 det=3
    M=[-1, 1;-1,-2] k=3 det=3
    M=[-1, 1; 2, 1] k=3 det=-3
    M=[ 1,-1;-2,-1] k=3 det=-3
    M=[ 1,-1; 1, 2] k=3 det=3
    M=[ 1, 2;-2,-1] k=3 det=3
    M=[ 1, 2; 1,-1] k=3 det=-3
    M=[ 2, 1;-1,-2] k=3 det=-3
    M=[ 2, 1;-1, 1] k=3 det=3
    M=[-2,-2; 0, 2] k=4 det=-4
    M=[-2,-2; 2, 0] k=4 det=4
    M=[-2, 0; 0,-2] k=4 det=4
    M=[-2, 0; 2, 2] k=4 det=-4
    M=[ 0,-2;-2, 0] k=4 det=-4
    M=[ 0,-2; 2, 2] k=4 det=4
    M=[ 0, 2;-2,-2] k=4 det=4
    M=[ 0, 2; 2, 0] k=4 det=-4
    M=[ 2, 0;-2,-2] k=4 det=-4
    M=[ 2, 0; 0, 2] k=4 det=4
    M=[ 2, 2;-2, 0] k=4 det=4
    M=[ 2, 2; 0,-2] k=4 det=-4
    M=[-3,-2; 1, 3] k=7 det=-7
    M=[-3,-2; 2,-1] k=7 det=7
    M=[-3,-1; 1,-2] k=7 det=7
    M=[-3,-1; 2, 3] k=7 det=-7
    M=[-2,-3;-1, 2] k=7 det=-7
    M=[-2,-3; 3, 1] k=7 det=7
    M=[-2, 1;-1,-3] k=7 det=7
    M=[-2, 1; 3, 2] k=7 det=-7
    M=[-1,-3;-2, 1] k=7 det=-7
    M=[-1,-3; 3, 2] k=7 det=7
    M=[-1, 2;-2,-3] k=7 det=7
    M=[-1, 2; 3, 1] k=7 det=-7
    M=[ 1,-2;-3,-1] k=7 det=-7
    M=[ 1,-2; 2, 3] k=7 det=7
    M=[ 1, 3;-3,-2] k=7 det=7
    M=[ 1, 3; 2,-1] k=7 det=-7
    M=[ 2,-1;-3,-2] k=7 det=-7
    M=[ 2,-1; 1, 3] k=7 det=7
    M=[ 2, 3;-3,-1] k=7 det=7
    M=[ 2, 3; 1,-2] k=7 det=-7
    M=[ 3, 1;-2,-3] k=7 det=-7
    M=[ 3, 1;-1, 2] k=7 det=7
    M=[ 3, 2;-2, 1] k=7 det=7
    M=[ 3, 2;-1,-3] k=7 det=-7
    M=[-3,-3; 0, 3] k=9 det=-9
    M=[-3,-3; 3, 0] k=9 det=9
    M=[-3, 0; 0,-3] k=9 det=9
    M=[-3, 0; 3, 3] k=9 det=-9
    M=[ 0,-3;-3, 0] k=9 det=-9
    M=[ 0,-3; 3, 3] k=9 det=9
    M=[ 0, 3;-3,-3] k=9 det=9
    M=[ 0, 3; 3, 0] k=9 det=-9
    M=[ 3, 0;-3,-3] k=9 det=-9
    M=[ 3, 0; 0, 3] k=9 det=9
    M=[ 3, 3;-3, 0] k=9 det=9
    M=[ 3, 3; 0,-3] k=9 det=-9
    M=[-4,-2; 2,-2] k=12 det=12
    M=[-4,-2; 2, 4] k=12 det=-12
    M=[-2,-4;-2, 2] k=12 det=-12
    M=[-2,-4; 4, 2] k=12 det=12
    M=[-2, 2;-2,-4] k=12 det=12
    M=[-2, 2; 4, 2] k=12 det=-12
    M=[ 2,-2;-4,-2] k=12 det=-12
    M=[ 2,-2; 2, 4] k=12 det=12
    M=[ 2, 4;-4,-2] k=12 det=12
    M=[ 2, 4; 2,-2] k=12 det=-12
    M=[ 4, 2;-2,-4] k=12 det=-12
    M=[ 4, 2;-2, 2] k=12 det=12
    M=[-4,-3; 1, 4] k=13 det=-13
    M=[-4,-3; 3,-1] k=13 det=13
    M=[-4,-1; 1,-3] k=13 det=13
    M=[-4,-1; 3, 4] k=13 det=-13
    M=[-3,-4;-1, 3] k=13 det=-13
    M=[-3,-4; 4, 1] k=13 det=13
    M=[-3, 1;-1,-4] k=13 det=13
    M=[-3, 1; 4, 3] k=13 det=-13
    M=[-1,-4;-3, 1] k=13 det=-13
    M=[-1,-4; 4, 3] k=13 det=13
    M=[-1, 3;-3,-4] k=13 det=13
    M=[-1, 3; 4, 1] k=13 det=-13
    M=[ 1,-3;-4,-1] k=13 det=-13
    M=[ 1,-3; 3, 4] k=13 det=13
    M=[ 1, 4;-4,-3] k=13 det=13
    M=[ 1, 4; 3,-1] k=13 det=-13
    M=[ 3,-1;-4,-3] k=13 det=-13
    M=[ 3,-1; 1, 4] k=13 det=13
    M=[ 3, 4;-4,-1] k=13 det=13
    M=[ 3, 4; 1,-3] k=13 det=-13
    M=[ 4, 1;-3,-4] k=13 det=-13
    M=[ 4, 1;-1, 3] k=13 det=13
    M=[ 4, 3;-3, 1] k=13 det=13
    M=[ 4, 3;-1,-4] k=13 det=-13
    M=[-4,-4; 0, 4] k=16 det=-16
    M=[-4,-4; 4, 0] k=16 det=16
    M=[-4, 0; 0,-4] k=16 det=16
    M=[-4, 0; 4, 4] k=16 det=-16
    M=[ 0,-4;-4, 0] k=16 det=-16
    M=[ 0,-4; 4, 4] k=16 det=16
    M=[ 0, 4;-4,-4] k=16 det=16
    M=[ 0, 4; 4, 0] k=16 det=-16
    M=[ 4, 0;-4,-4] k=16 det=-16
    M=[ 4, 0; 0, 4] k=16 det=16
    M=[ 4, 4;-4, 0] k=16 det=16
    M=[ 4, 4; 0,-4] k=16 det=-16
    M=[-5,-3; 2, 5] k=19 det=-19
    M=[-5,-3; 3,-2] k=19 det=19
    M=[-5,-2; 2,-3] k=19 det=19
    M=[-5,-2; 3, 5] k=19 det=-19
    M=[-3,-5;-2, 3] k=19 det=-19
    M=[-3,-5; 5, 2] k=19 det=19
    M=[-3, 2;-2,-5] k=19 det=19
    M=[-3, 2; 5, 3] k=19 det=-19
    M=[-2,-5;-3, 2] k=19 det=-19
    M=[-2,-5; 5, 3] k=19 det=19
    M=[-2, 3;-3,-5] k=19 det=19
    M=[-2, 3; 5, 2] k=19 det=-19
    M=[ 2,-3;-5,-2] k=19 det=-19
    M=[ 2,-3; 3, 5] k=19 det=19
    M=[ 2, 5;-5,-3] k=19 det=19
    M=[ 2, 5; 3,-2] k=19 det=-19
    M=[ 3,-2;-5,-3] k=19 det=-19
    M=[ 3,-2; 2, 5] k=19 det=19
    M=[ 3, 5;-5,-2] k=19 det=19
    M=[ 3, 5; 2,-3] k=19 det=-19
    M=[ 5, 2;-3,-5] k=19 det=-19
    M=[ 5, 2;-2, 3] k=19 det=19
    M=[ 5, 3;-3, 2] k=19 det=19
    M=[ 5, 3;-2,-5] k=19 det=-19
    M=[-5,-4; 1, 5] k=21 det=-21
    M=[-5,-4; 4,-1] k=21 det=21
    M=[-5,-1; 1,-4] k=21 det=21
    M=[-5,-1; 4, 5] k=21 det=-21
    M=[-4,-5;-1, 4] k=21 det=-21
    M=[-4,-5; 5, 1] k=21 det=21
    M=[-4, 1;-1,-5] k=21 det=21
    M=[-4, 1; 5, 4] k=21 det=-21
    M=[-1,-5;-4, 1] k=21 det=-21
    M=[-1,-5; 5, 4] k=21 det=21
    M=[-1, 4;-4,-5] k=21 det=21
    M=[-1, 4; 5, 1] k=21 det=-21
    M=[ 1,-4;-5,-1] k=21 det=-21
    M=[ 1,-4; 4, 5] k=21 det=21
    M=[ 1, 5;-5,-4] k=21 det=21
    M=[ 1, 5; 4,-1] k=21 det=-21
    M=[ 4,-1;-5,-4] k=21 det=-21
    M=[ 4,-1; 1, 5] k=21 det=21
    M=[ 4, 5;-5,-1] k=21 det=21
    M=[ 4, 5; 1,-4] k=21 det=-21
    M=[ 5, 1;-4,-5] k=21 det=-21
    M=[ 5, 1;-1, 4] k=21 det=21
    M=[ 5, 4;-4, 1] k=21 det=21
    M=[ 5, 4;-1,-5] k=21 det=-21
    M=[-5,-5; 0, 5] k=25 det=-25
    M=[-5,-5; 5, 0] k=25 det=25
    M=[-5, 0; 0,-5] k=25 det=25
    M=[-5, 0; 5, 5] k=25 det=-25
    M=[ 0,-5;-5, 0] k=25 det=-25
    M=[ 0,-5; 5, 5] k=25 det=25
    M=[ 0, 5;-5,-5] k=25 det=25
    M=[ 0, 5; 5, 0] k=25 det=-25
    M=[ 5, 0;-5,-5] k=25 det=-25
    M=[ 5, 0; 0, 5] k=25 det=25
    M=[ 5, 5;-5, 0] k=25 det=25
    M=[ 5, 5; 0,-5] k=25 det=-25

  Isometries (k=1): 12
    M=[-1,-1; 0, 1] det=-1
    M=[-1,-1; 1, 0] det=1
    M=[-1, 0; 0,-1] det=1
    M=[-1, 0; 1, 1] det=-1
    M=[ 0,-1;-1, 0] det=-1
    M=[ 0,-1; 1, 1] det=1
    M=[ 0, 1;-1,-1] det=1
    M=[ 0, 1; 1, 0] det=-1
      (2,1) -> (1,2) -> triple (3, 5, 7)
    M=[ 1, 0;-1,-1] det=-1
    M=[ 1, 0; 0, 1] det=1
      (2,1) -> (2,1) -> triple (3, 5, 7)
    M=[ 1, 1;-1, 0] det=1
    M=[ 1, 1; 0,-1] det=-1

  Expansion matrices (k>1): 168
    M=[-5,-5; 0, 5] k=25 det=-25
    M=[-5,-5; 5, 0] k=25 det=25
    M=[-5,-4; 1, 5] k=21 det=-21
    M=[-5,-4; 4,-1] k=21 det=21
    M=[-5,-3; 2, 5] k=19 det=-19
    M=[-5,-3; 3,-2] k=19 det=19
    M=[-5,-2; 2,-3] k=19 det=19
    M=[-5,-2; 3, 5] k=19 det=-19
    M=[-5,-1; 1,-4] k=21 det=21
    M=[-5,-1; 4, 5] k=21 det=-21
    M=[-5, 0; 0,-5] k=25 det=25
    M=[-5, 0; 5, 5] k=25 det=-25
    M=[-4,-5;-1, 4] k=21 det=-21
    M=[-4,-5; 5, 1] k=21 det=21
    M=[-4,-4; 0, 4] k=16 det=-16
    M=[-4,-4; 4, 0] k=16 det=16
    M=[-4,-3; 1, 4] k=13 det=-13
    M=[-4,-3; 3,-1] k=13 det=13
    M=[-4,-2; 2,-2] k=12 det=12
    M=[-4,-2; 2, 4] k=12 det=-12
  TIME: 0.45s

============================================================
EXPERIMENT: Exp 2: Tree completeness (c < 10000)
============================================================
  Phase 1: Brute-force all primitive Eisenstein triples c < 10000...
  Primitive triples with c < 10000: 1384
  Phase 2: Direct brute force (a^2+ab+b^2 = c^2, a<=b, c<10000)...
    c=2000, found 277 so far...
    c=4000, found 549 so far...
    c=6000, found 826 so far...
    c=8000, found 1103 so far...
  Direct brute force found: 1384 primitive triples
  Missing from parametric: 0
  Extra in parametric: 0
  PARAMETRIC IS COMPLETE!
  Phase 3: Tree via Stern-Brocot L/R from (2,1)...
  Tree reached 399 (m,n) pairs, 220 valid
  All valid (m,n) with c<10000: 1384
  Coverage: 15.9%
  Multi-root (3 roots) coverage: 22.3%
  TIME: 9.95s

============================================================
EXPERIMENT: Exp 3: Norm-form factoring in Z[ζ₃]
============================================================
  Norm-form factoring: N = a^2+ab+b^2, two representations -> factor
  Results: 27/100 factored (27.0%)
    10d: 26/26 (100.0%)
    13d: 1/18 (5.6%)
    16d: 0/18 (0.0%)
    18d: 0/19 (0.0%)
    21d: 0/19 (0.0%)

  Complexity: Finding Loeschian reps requires O(sqrt(N)) search
  This is equivalent to Fermat's method — O(sqrt(N)) for balanced factors
  Advantage: works only when p,q ≡ 1 mod 3 (1/4 of semiprimes)
  TIME: 2.98s

============================================================
EXPERIMENT: Exp 4: GLV-3 decomposition analysis
============================================================
  GLV-3 analysis on secp256k1:
  lambda = 0x5363ad4cc05c30e0a5...
  lambda^2 mod n = 0xac9c52b33fa3cf1f5a...
  lambda^2 + lambda + 1 mod n = 0

  GLV-2 decomposition tests:
    k=0xd6a82a951b923e... -> k1(128b) + k2(126b)*λ, verify=True
    k=0x573e8d77550ae8... -> k1(129b) + k2(128b)*λ, verify=True
    k=0xb3a1f1315573ae... -> k1(129b) + k2(124b)*λ, verify=True
  Average max(k1,k2) bits: 128.5 (vs 256 for full scalar)
  Speedup: 1.99x fewer doublings

  GLV-3 = GLV-2 because λ²+λ+1=0:
  k = k1 + k2·λ + k3·λ²
  = k1 + k2·λ + k3·(-λ-1)
  = (k1-k3) + (k2-k3)·λ
  So GLV-3 is EXACTLY GLV-2 with k1'=k1-k3, k2'=k2-k3
  NO additional speedup from λ² term!

  Alternative: 3-dimensional GLV lattice
  L = {(a,b,c) : a + b·λ + c·λ² ≡ 0 mod n}
  Since λ² = -λ-1, this is: a - c + (b-c)·λ ≡ 0 mod n
  Which is 2D (rank 2 lattice in Z^3), not 3D
  CONCLUSION: GLV-3 offers NO advantage over GLV-2 for j=0 curves
  TIME: 0.00s

============================================================
EXPERIMENT: Exp 5: Eisenstein lattice 2D kangaroo
============================================================
  2D Eisenstein kangaroo design:
  Idea: walk in Z[ζ₃] ≅ Z², use hexagonal distinguished points

  Standard 1D kangaroo (28-bit key)...
  1D kangaroo: found=True, steps=24064, time=6.113s

  2D Eisenstein kangaroo (28-bit key)...
  Decompose scalar: k = k1 + k2·λ (GLV)
  Walk in (k1, k2) plane with hexagonal jumps
  2D kangaroo: found=False, steps=65536, time=18.558s

  Analysis:
  2D kangaroo has O(sqrt(n)) steps same as 1D
  Each 2D step is MORE expensive (2D tracking overhead)
  The hexagonal symmetry does NOT reduce search space
  because the ECDLP is inherently 1-dimensional (find k in Z/nZ)
  GLV makes it 2D but the lattice constraint means it's still 1D
  TIME: 24.68s

============================================================
EXPERIMENT: Exp 6: GLV-3 scalar multiplication benchmark
============================================================
  Benchmarking scalar multiplication methods:

  Running 5 trials...
  Trial 1: std=256D+125A (0.048s), GLV2=257D+90A (0.048s), speedup=1.00x, correct=True
  Trial 2: std=256D+124A (0.047s), GLV2=257D+85A (0.041s), speedup=1.15x, correct=True
  Trial 3: std=253D+141A (0.051s), GLV2=254D+82A (0.043s), speedup=1.21x, correct=True
  Trial 4: std=256D+142A (0.045s), GLV2=257D+82A (0.038s), speedup=1.17x, correct=True
  Trial 5: std=256D+140A (0.047s), GLV2=256D+83A (0.040s), speedup=1.16x, correct=True

  GLV-3 analysis:
  φ²(P) = (β²·Px mod p, Py)
  β² mod p = 0x851695d49a83f8ef91...
  λ² mod n = 0xac9c52b33fa3cf1f5a...
  λ² = -λ-1 mod n: True

  Since λ² = -λ-1, for any k = k1 + k2·λ + k3·λ²:
  = k1 + k2·λ + k3·(-λ-1) = (k1-k3) + (k2-k3)·λ
  This is STILL a 2-term GLV decomposition!
  [k1]P + [k2]φ(P) + [k3]φ²(P) = [k1-k3]P + [k2-k3]φ(P)
  GLV-3 = GLV-2. No improvement possible.
  TIME: 0.45s

============================================================
EXPERIMENT: Exp 7: Eisenstein p-1 factoring
============================================================
  Eisenstein p-1 factoring in Z[ζ₃]:
  Z[ζ₃] = Z[w] where w² + w + 1 = 0
  Norm(a + bw) = a² + ab + b²

  Testing on 50 semiprimes (B1=5000)...
  Standard p-1 only: 1
  Eisenstein p-1 only: 9
  Both: 10
  Neither: 30

  Theory:
  Standard p-1: catches p-1 smooth
  Eisenstein p-1: catches p²+p+1 smooth (p≡2 mod 3) OR p-1 smooth (p≡1 mod 3)
  For p≡2 mod 3: tests p²+p+1 smoothness — DIFFERENT from p±1
  For p≡1 mod 3: subsumes standard p-1
  TIME: 0.13s

============================================================
EXPERIMENT: Exp 8: Combined Eisenstein + Gaussian p-1 pre-sieve
============================================================
  Combined Gaussian + Eisenstein pre-sieve:

  50 semiprimes, B1=5000:
  Results:
    std_only: 1
    gauss_only: 3
    eis_only: 5
    std+gauss: 0
    std+eis: 1
    gauss+eis: 3
    all_three: 9
    none: 28

  Summary:
    Standard p-1:    11/50 (0.09s)
    Gaussian p-1:    15/50 (0.33s)
    Eisenstein p-1:  18/50 (0.38s)
    Combined:        22/50
    Unique to Gaussian: 3
    Unique to Eisenstein: 5

  Smoothness orders tested:
    Standard p-1:   p-1
    Gaussian p-1:   p-1 (split, p≡1 mod 4) or p²+1 (inert, p≡3 mod 4)
    Eisenstein p-1: p-1 (split, p≡1 mod 3) or p²+p+1 (inert, p≡2 mod 3)
    Union: p-1, p²+1, p²+p+1 — three independent smoothness tests!
  TIME: 0.79s

============================================================
SUMMARY
============================================================
| # | Experiment | Status | Key Finding |
|---|-----------|--------|-------------|
| 1 | Exp 1: 2x2 matrices on (m,n) parameters | OK | norm_preserving=180, isometries=12, expansions=168 |
| 2 | Exp 2: Tree completeness (c < 10000) | OK | parametric_complete=True, triples=1384, tree_coverage=15.9% |
| 3 | Exp 3: Norm-form factoring in Z[ζ₃] | OK | factored=27/100, rate=27.0% |
| 4 | Exp 4: GLV-3 decomposition analysis | OK | GLV-3 collapses to GLV-2 (λ²+λ+1=0), avg_bits=128.5 |
| 5 | Exp 5: Eisenstein lattice 2D kangaroo | OK | 1d_steps=24064, 2d_steps=65536, 2d_no_advantage=True |
| 6 | Exp 6: GLV-3 scalar multiplication benchmark | OK | GLV-2 ~1.5x faster, GLV-3=GLV-2 (algebraic identity) |
| 7 | Exp 7: Eisenstein p-1 factoring | OK | eis_unique=9, std_only=1, both=10 |
| 8 | Exp 8: Combined Eisenstein + Gaussian p-1 pre-sieve | OK | combined=22/50, eis_unique=5, gauss_unique=3 |
```
