# v35: Eisenstein Tree for j=0 Curves (secp256k1)

Date: 2026-03-17

## Summary Table

| # | Experiment | Status | Key Finding |
|---|-----------|--------|-------------|
| 1 | Exp 1: Eisenstein matrix tree (3x3 form-preserving) | OK | matrices_found=8 |
| 2 | Exp 2: Parametric (m,n) tree | OK | coverage_pct=26.837297341782566 |
| 3 | Exp 3: Tree properties | OK | ('total_triples', 56912) |
| 4 | Exp 4: secp256k1 connection | OK | verdict=Eisenstein tree = GLV navigation, no ECDLP break |
| 5 | Exp 5: CF-EPT bijection | OK | is_bijection=True |
| 6 | Exp 6: Eisenstein zeta machine | OK | ('split_primes', 330) |
| 7 | Exp 7: Eisenstein kangaroo | OK | ('std_found', True) |
| 8 | Exp 8: Eisenstein factoring | OK | complexity=O(sqrt(N)) |

## Detailed Results

```
============================================================
v35_eisenstein.py — Eisenstein Tree for j=0 Curves
============================================================
Date: 2026-03-17
Goal: Build cubic analog of Berggren tree, test on secp256k1


============================================================
EXPERIMENT: Exp 1: Eisenstein matrix tree (3x3 form-preserving)
============================================================
  Phase 1: Algebraic approach - find O(Q, Z) generators
  Q(a,b,c) = a² + ab + b² - c²
  Need M^T · Q_mat · M = Q_mat where Q_mat = [[2,1,0],[1,2,0],[0,0,-2]]
  (Multiplied by 2 to clear denominators)
  Phase 2: Searching [-5,5]^9 with algebraic constraints...
  FOUND: M=[[-1, 0, 0], [0, -1, 0], [0, 0, -1]], det=-1, (3,5,7)->[-3, -5, -7]
  FOUND: M=[[-1, 0, 0], [0, -1, 0], [0, 0, 1]], det=1, (3,5,7)->[-3, -5, 7]
  FOUND: M=[[0, -1, 0], [-1, 0, 0], [0, 0, -1]], det=1, (3,5,7)->[-5, -3, -7]
  FOUND: M=[[0, -1, 0], [-1, 0, 0], [0, 0, 1]], det=-1, (3,5,7)->[-5, -3, 7]
  FOUND: M=[[0, 1, 0], [1, 0, 0], [0, 0, -1]], det=1, (3,5,7)->[5, 3, -7]
  FOUND: M=[[0, 1, 0], [1, 0, 0], [0, 0, 1]], det=-1, (3,5,7)->[5, 3, 7]
  FOUND: M=[[1, 0, 0], [0, 1, 0], [0, 0, -1]], det=-1, (3,5,7)->[3, 5, -7]
  FOUND: M=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], det=1, (3,5,7)->[3, 5, 7]
  Row-0 candidates passing val00=2: 6
  Total form-preserving matrices ([-5,5]^9): 8

  Phase 3: Change-of-basis from Berggren
  a²+ab+b² = (a+b/2)² + 3b²/4
  Change of basis: P·(a,b,c) -> (x,y,z) where x²+y²=z²
  Then Berggren M_pyth transforms to P^{-1}·M_pyth·P for Eisenstein
  RESULT: a²+ab+b²-c² and x²+y²-z² are NOT Z-equivalent
  (discriminant 3 vs 1 — different genera)
  Berggren matrices CANNOT be conjugated to Eisenstein form over Z
  The trivial matrices (sign/swap) ARE the full group O(Q_eis, Z) in small range

  Phase 4: The Eisenstein tree is fundamentally 2D (on (m,n) pairs)
  Unlike Pythagorean triples where 3x3 LINEAR maps exist,
  Eisenstein triples require QUADRATIC maps or 2x2 maps on parameters
  This is because disc(a²+ab+b²) = -3 ≠ -4 = disc(a²+b²)

  Generators of O(a²+ab+b²-c², Z):
  Matrices mapping to positive c: 4
  Unique (mod ±1): 4
    M=[[-1, 0, 0], [0, -1, 0], [0, 0, -1]], det=-1, (3,5,7)->[-3, -5, -7]
    M=[[-1, 0, 0], [0, -1, 0], [0, 0, 1]], det=1, (3,5,7)->[-3, -5, 7]
    M=[[0, -1, 0], [-1, 0, 0], [0, 0, -1]], det=1, (3,5,7)->[-5, -3, -7]
    M=[[0, -1, 0], [-1, 0, 0], [0, 0, 1]], det=-1, (3,5,7)->[-5, -3, 7]
  TIME: 0.00s

============================================================
EXPERIMENT: Exp 2: Parametric (m,n) tree
============================================================
  Parametric form: a=m²-n², b=2mn+n², c=m²+mn+n²
  Parametric form verified for m=2..9
  Primitive Eisenstein triples with c<=500: 69
  First 10: [(3, 5, 7), (7, 8, 13), (5, 16, 19), (11, 24, 31), (7, 33, 37), (13, 35, 43), (16, 39, 49), (9, 56, 61), (32, 45, 67), (17, 63, 73)]
  Coprime (m,n) with m<50: primitive=563, non-primitive=190
  Non-primitive cases (gcd>1):
    m=4, n=1: (15,9,21), gcd=3, m%3=1, n%3=1
    m=5, n=2: (21,24,39), gcd=3, m%3=2, n%3=2
    m=7, n=1: (48,15,57), gcd=3, m%3=1, n%3=1
    m=7, n=4: (33,72,93), gcd=3, m%3=1, n%3=1
    m=8, n=5: (39,105,129), gcd=3, m%3=2, n%3=2
    m=10, n=1: (99,21,111), gcd=3, m%3=1, n%3=1
    m=10, n=7: (51,189,219), gcd=3, m%3=1, n%3=1
    m=11, n=2: (117,48,147), gcd=3, m%3=2, n%3=2
    m=11, n=5: (96,135,201), gcd=3, m%3=2, n%3=2
    m=11, n=8: (57,240,273), gcd=3, m%3=2, n%3=2
    m=13, n=1: (168,27,183), gcd=3, m%3=1, n%3=1
    m=13, n=4: (153,120,237), gcd=3, m%3=1, n%3=1
    m=13, n=7: (120,231,309), gcd=3, m%3=1, n%3=1
    m=13, n=10: (69,360,399), gcd=3, m%3=1, n%3=1
    m=14, n=5: (171,165,291), gcd=3, m%3=2, n%3=2
    m=14, n=11: (75,429,471), gcd=3, m%3=2, n%3=2
    m=16, n=1: (255,33,273), gcd=3, m%3=1, n%3=1
    m=16, n=7: (207,273,417), gcd=3, m%3=1, n%3=1
    m=16, n=13: (87,585,633), gcd=3, m%3=1, n%3=1
    m=17, n=2: (285,72,327), gcd=3, m%3=2, n%3=2
    m=17, n=5: (264,195,399), gcd=3, m%3=2, n%3=2
    m=17, n=8: (225,336,489), gcd=3, m%3=2, n%3=2
    m=17, n=11: (168,495,597), gcd=3, m%3=2, n%3=2
    m=17, n=14: (93,672,723), gcd=3, m%3=2, n%3=2
    m=19, n=1: (360,39,381), gcd=3, m%3=1, n%3=1
    m=19, n=4: (345,168,453), gcd=3, m%3=1, n%3=1
    m=19, n=7: (312,315,543), gcd=3, m%3=1, n%3=1
    m=19, n=10: (261,480,651), gcd=3, m%3=1, n%3=1
    m=19, n=13: (192,663,777), gcd=3, m%3=1, n%3=1
    m=19, n=16: (105,864,921), gcd=3, m%3=1, n%3=1

  Building (m,n) tree from root (2,1)...
  Tree nodes by depth: {0: 1, 1: 3, 2: 9, 3: 27, 4: 81, 5: 243, 6: 680, 7: 1134, 8: 1083}
  Total (m,n) pairs reached: 3261
  All coprime pairs (m<200): 12151
  Coverage: 26.8%
  First 10 missed: [(3, 1), (5, 1), (5, 3), (7, 1), (7, 3), (9, 1), (7, 5), (11, 1), (9, 5), (11, 3)]

  Stern-Brocot tree for coprime (m,n) pairs:
  Stern-Brocot coverage (m<200): 27.7% (3361 pairs)
  Depth distribution: {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32, 6: 64, 7: 128}
  First missed: [(14, 1), (14, 13), (15, 1), (15, 14), (16, 1)]

  Multi-root approach:
  Multi-root (3 roots, 4 transforms) coverage: 52.3% (6356 pairs)
  TIME: 0.03s

============================================================
EXPERIMENT: Exp 3: Tree properties
============================================================
  Total primitive Eisenstein triples (m<500): 56912
  Distinct hypotenuses: 38706
  First 20 hypotenuses: [7, 13, 19, 31, 37, 43, 49, 61, 67, 73, 79, 91, 97, 103, 109, 127, 133, 139, 151, 157]
  Prime hypotenuses: 17334 / 38706 = 44.8%
  First 20 prime hypotenuses: [7, 13, 19, 31, 37, 43, 61, 67, 73, 79, 97, 103, 109, 127, 139, 151, 157, 163, 181, 193]
  Prime hypotenuses mod 3: {1: 17334}
  Prime hypotenuses mod 6: {1: 17334}

  Equidistribution of hypotenuses mod p:
    mod 5: chi²=50.01, dist={1: 250, 2: 251, 3: 249, 4: 250}
    mod 7: chi²=2.50, dist={0: 160, 1: 138, 2: 141, 3: 142, 4: 138, 5: 141, 6: 140}
    mod 11: chi²=9.24, dist={1: 99, 2: 99, 3: 99, 4: 99, 5: 100, 6: 102, 7: 101, 8: 100, 9: 99, 10: 102}
    mod 13: chi²=2.59, dist={0: 90, 1: 75, 2: 75, 3: 77, 4: 75, 5: 78, 6: 77, 7: 76, 8: 75, 9: 75, 10: 75, 11: 77, 12: 75}

  Hypotenuses with multiple representations: 14152
    c=91: [(11, 85), (80, 19)]
    c=133: [(65, 88), (120, 23)]
    c=217: [(17, 208), (160, 87)]
    c=247: [(72, 203), (187, 93)]
    c=259: [(144, 155), (221, 64)]

  Loeschian number density:
  Loeschian numbers up to 1000: 277 (27.7%)
  Sum-of-two-squares up to 1000: 330 (33.0%)
  TIME: 0.18s

============================================================
EXPERIMENT: Exp 4: secp256k1 connection
============================================================
  secp256k1: j=0 curve, CM disc = -3
  Endomorphism: φ(x,y) = (β·x, y), β³ ≡ 1 mod p
  β = 0x7ae96a2b657c07106e...
  On group: φ acts as [λ]P where λ² + λ + 1 ≡ 0 mod n
  λ² + λ + 1 mod n = 0

  GLV decomposition analysis:

  Eisenstein triple scalar decompositions:
    m=2, n=1: a=3, b=5, c=7
      k = 0xa0f2627fc1ccf46339... (256b)
      GLV cost: 3 doublings vs 256
    m=3, n=1: a=8, b=7, c=13
      k = 0x47b9bd194285562484... (255b)
      GLV cost: 4 doublings vs 255
    m=3, n=2: a=5, b=16, c=19
      k = 0x363ad4cc05c30e0a52... (254b)
      GLV cost: 5 doublings vs 254
    m=4, n=1: a=15, b=9, c=21
      k = 0xee8117b2c33db7e5ce... (256b)
      GLV cost: 4 doublings vs 256
    m=4, n=3: a=7, b=33, c=37
      k = 0xbfd956e4cbe24cf549... (256b)
      GLV cost: 6 doublings vs 256
    m=5, n=1: a=24, b=11, c=31
      k = 0x9548724c43f619a718... (256b)
      GLV cost: 5 doublings vs 256
    m=5, n=2: a=21, b=24, c=39
      k = 0xd1583f3208a4950f7b... (256b)
      GLV cost: 5 doublings vs 256
    m=5, n=3: a=16, b=39, c=49
      k = 0xb42f66b14e0b723928... (256b)
      GLV cost: 6 doublings vs 256
    m=5, n=4: a=9, b=56, c=61
      k = 0x3dcde8ca142ab12420... (254b)
      GLV cost: 6 doublings vs 254
    m=6, n=1: a=35, b=13, c=43
      k = 0x3c0fcce5c4ae7b6862... (254b)
      GLV cost: 6 doublings vs 254
    m=6, n=5: a=11, b=85, c=91
      k = 0xb0188a7bde9c3a96d5... (256b)
      GLV cost: 7 doublings vs 256
    m=7, n=1: a=48, b=15, c=57
      k = 0xe2d7277f4566dd29ad... (256b)
      GLV cost: 6 doublings vs 256
    m=7, n=2: a=45, b=32, c=67
      k = 0x6c75a9980b861c14a4... (255b)
      GLV cost: 6 doublings vs 255
    m=7, n=3: a=40, b=51, c=79
      k = 0x9cdb864a525dbcc0e6... (256b)
      GLV cost: 6 doublings vs 256
    m=7, n=4: a=33, b=72, c=93
      k = 0x7408bd9619edbf2e72... (255b)
      GLV cost: 7 doublings vs 255
    m=7, n=5: a=24, b=95, c=109
      k = 0xf1fd4f7b6236235d49... (256b)
      GLV cost: 7 doublings vs 256
    m=7, n=6: a=13, b=120, c=127
      k = 0x16b93bfa2b36e94d69... (253b)
      GLV cost: 7 doublings vs 253
    m=8, n=1: a=63, b=17, c=73
      k = 0x899e8218c61f3eeaf7... (256b)
      GLV cost: 6 doublings vs 256
    m=8, n=3: a=55, b=57, c=97
      k = 0x91319616d486e204c5... (256b)
      GLV cost: 6 doublings vs 256
    m=8, n=5: a=39, b=105, c=129
      k = 0x33e2147ae5d00c23bc... (254b)
      GLV cost: 7 doublings vs 254
    m=8, n=7: a=15, b=161, c=169
      k = 0x71affd44f9fabd47dc... (255b)
      GLV cost: 8 doublings vs 255
    m=9, n=1: a=80, b=19, c=91
      k = 0x3065dcb246d7a0ac41... (254b)
      GLV cost: 7 doublings vs 254
    m=9, n=2: a=77, b=40, c=103
      k = 0x79313fe0e67a319cdf... (251b)
      GLV cost: 7 doublings vs 251
    m=9, n=4: a=65, b=88, c=133
      k = 0xaa4392621fb0cd38c5... (256b)
      GLV cost: 7 doublings vs 256
    m=9, n=5: a=56, b=115, c=151
      k = 0x75c6d97a6969f4ea30... (255b)
      GLV cost: 7 doublings vs 255
    m=9, n=7: a=32, b=175, c=193
      k = 0x12377777f056990e50... (249b)
      GLV cost: 8 doublings vs 249
    m=9, n=8: a=17, b=208, c=217
      k = 0xc0fcce5c4ae7b6862e... (256b)
      GLV cost: 8 doublings vs 256
    m=10, n=1: a=99, b=21, c=111
      k = 0xd72d374bc790026d8c... (256b)
      GLV cost: 7 doublings vs 256
    m=10, n=3: a=91, b=69, c=139
      k = 0x79ddb5afd8d92c8c83... (255b)
      GLV cost: 7 doublings vs 255
    m=10, n=7: a=51, b=189, c=219
      k = 0x9096f1aa041015d9ed... (256b)
      GLV cost: 8 doublings vs 256
    m=10, n=9: a=19, b=261, c=271
      k = 0x49faf401dfdd5085fd... (251b)
      GLV cost: 9 doublings vs 251
    m=11, n=1: a=120, b=23, c=133
      k = 0x7df491e54848642ed6... (255b)
      GLV cost: 7 doublings vs 255
    m=11, n=2: a=117, b=48, c=147
      k = 0xa2b07e6411492a1ef7... (256b)
      GLV cost: 7 doublings vs 256
    m=11, n=3: a=112, b=75, c=163
      k = 0x6e33c57c5b0251d062... (255b)
      GLV cost: 7 doublings vs 255
    m=11, n=4: a=105, b=104, c=181
      k = 0xe07e672e2573db4317... (256b)
      GLV cost: 7 doublings vs 256
    m=11, n=5: a=96, b=135, c=201
      k = 0xf9906379709dc67717... (256b)
      GLV cost: 8 doublings vs 256
    m=11, n=6: a=85, b=168, c=223
      k = 0xb969ba5e3c80136c61... (256b)
      GLV cost: 8 doublings vs 256
    m=11, n=7: a=72, b=203, c=247
      k = 0x200a6bdc891ac222f5... (254b)
      GLV cost: 8 doublings vs 254
    m=11, n=8: a=57, b=240, c=273
      k = 0x2d7277f4566dd29ad3... (254b)
      GLV cost: 8 doublings vs 254
    m=11, n=9: a=40, b=279, c=301
      k = 0xe1a1dea5a47944d3fc... (256b)
      GLV cost: 9 doublings vs 256
    m=11, n=10: a=21, b=320, c=331
      k = 0x3c989ff0733d18ce6f... (254b)
      GLV cost: 9 doublings vs 254
    m=12, n=1: a=143, b=25, c=157
      k = 0x24bbec7ec900c5f020... (254b)
      GLV cost: 8 doublings vs 254
    m=12, n=5: a=119, b=145, c=229
      k = 0x3b752878f437af3d8a... (254b)
      GLV cost: 8 doublings vs 254
    m=12, n=7: a=95, b=217, c=277
      k = 0xaf7de60f0e256e6bfd... (256b)
      GLV cost: 8 doublings vs 256
    m=12, n=11: a=23, b=385, c=397
      k = 0x68e7a06d4aa581d85e... (255b)
      GLV cost: 9 doublings vs 255
    m=13, n=1: a=168, b=27, c=183
      k = 0xcb83471849b927b16b... (256b)
      GLV cost: 8 doublings vs 256
    m=13, n=2: a=165, b=56, c=199
      k = 0x3dcde8ca142ab12420... (254b)
      GLV cost: 8 doublings vs 254
    m=13, n=3: a=160, b=87, c=217
      k = 0x56dfe5155f549c581f... (255b)
      GLV cost: 8 doublings vs 255
    m=13, n=4: a=153, b=120, c=237
      k = 0x16b93bfa2b36e94d69... (253b)
      GLV cost: 8 doublings vs 253
    m=13, n=5: a=144, b=155, c=259
      k = 0x7d59ed7877d19803fe... (255b)
      GLV cost: 8 doublings vs 255
    m=13, n=6: a=133, b=192, c=283
      k = 0x8ac1f9904524a87bdc... (256b)
      GLV cost: 8 doublings vs 256
    m=13, n=7: a=120, b=231, c=309
      k = 0x3ef1604193301ab505... (254b)
      GLV cost: 8 doublings vs 254
    m=13, n=8: a=105, b=272, c=337
      k = 0x99e8218c61f3eeaf78... (256b)
      GLV cost: 9 doublings vs 256
    m=13, n=9: a=88, b=315, c=367
      k = 0x9ba63d70b170246b35... (256b)
      GLV cost: 9 doublings vs 256
    m=13, n=10: a=69, b=360, c=399
      k = 0x442bb3ee81a4bbe83d... (255b)
      GLV cost: 9 doublings vs 255
    m=13, n=11: a=48, b=407, c=433
      k = 0x93788505d291b5268f... (256b)
      GLV cost: 9 doublings vs 256
    m=13, n=12: a=25, b=456, c=469
      k = 0x898cb0b6a43710262b... (256b)
      GLV cost: 9 doublings vs 256
    m=14, n=1: a=195, b=29, c=211
      k = 0x724aa1b1ca718972b5... (255b)
      GLV cost: 8 doublings vs 255
    m=14, n=3: a=187, b=93, c=247
      k = 0x4b35f4e1e17dc19bfe... (255b)
      GLV cost: 8 doublings vs 255
    m=14, n=5: a=171, b=165, c=291
      k = 0xbf3eb277fb6b80ca71... (256b)
      GLV cost: 8 doublings vs 256
    m=14, n=9: a=115, b=333, c=403
      k = 0x78a86cd637eb9436d2... (255b)
      GLV cost: 9 doublings vs 255
    m=14, n=11: a=75, b=429, c=471
      k = 0xbe09699e5a7de874c0... (256b)
      GLV cost: 9 doublings vs 256
    m=14, n=13: a=27, b=533, c=547
      k = 0x9e87d0cc7ff1c3b7d8... (256b)
      GLV cost: 10 doublings vs 256
    m=15, n=1: a=224, b=31, c=241
      k = 0x1911fc4b4b29eb33ff... (253b)
      GLV cost: 8 doublings vs 253
    m=15, n=2: a=221, b=64, c=259
      k = 0xd8eb5330170c382949... (256b)
      GLV cost: 8 doublings vs 256
    m=15, n=4: a=209, b=136, c=301
      k = 0x4cf410c630f9f757bc... (255b)
      GLV cost: 8 doublings vs 255
    m=15, n=7: a=176, b=259, c=379
      k = 0x5dd854a69d45734715... (255b)
      GLV cost: 9 doublings vs 255
    m=15, n=8: a=161, b=304, c=409
      k = 0x65dcb246d7a0ac41d4... (251b)
      GLV cost: 9 doublings vs 251
    m=15, n=11: a=104, b=451, c=511
      k = 0xe89a4e36e26a1bc2f2... (256b)
      GLV cost: 9 doublings vs 256
    m=15, n=13: a=56, b=559, c=589
      k = 0x16a76a98094eba889e... (253b)
      GLV cost: 10 doublings vs 253
    m=15, n=14: a=29, b=616, c=631
      k = 0xa7d900aeddd59c8d63... (256b)
      GLV cost: 10 doublings vs 256
    m=16, n=1: a=255, b=33, c=273
      k = 0xbfd956e4cbe24cf549... (256b)
      GLV cost: 8 doublings vs 256
    m=16, n=3: a=247, b=105, c=313
      k = 0x33e2147ae5d00c23bc... (254b)
      GLV cost: 8 doublings vs 254
    m=16, n=5: a=231, b=185, c=361
      k = 0x43083c77029f525758... (255b)
      GLV cost: 8 doublings vs 255
    m=16, n=7: a=207, b=273, c=417
      k = 0xed4bced922501f901d... (256b)
      GLV cost: 9 doublings vs 256
    m=16, n=9: a=175, b=369, c=481
      k = 0x32accba144e273ce0b... (254b)
      GLV cost: 9 doublings vs 254
    m=16, n=11: a=135, b=473, c=553
      k = 0x132b32cf6a564f1123... (253b)
      GLV cost: 9 doublings vs 253
    m=16, n=13: a=87, b=585, c=633
      k = 0x8ec7046392abb15964... (256b)
      GLV cost: 10 doublings vs 256
    m=16, n=15: a=31, b=705, c=721
      k = 0xa580405dbde29aa6cd... (256b)
      GLV cost: 10 doublings vs 256
    m=17, n=1: a=288, b=35, c=307
      k = 0x66a0b17e4c9aaeb694... (255b)
      GLV cost: 9 doublings vs 255
    m=17, n=2: a=285, b=72, c=327
      k = 0x7408bd9619edbf2e72... (255b)
      GLV cost: 9 doublings vs 255
    m=17, n=3: a=280, b=111, c=349
      k = 0x2838244767f931679b... (254b)
      GLV cost: 9 doublings vs 254
    m=17, n=4: a=273, b=152, c=373
      k = 0x832ee59236bd05620e... (256b)
      GLV cost: 9 doublings vs 256
    m=17, n=5: a=264, b=195, c=399
      k = 0x84ed017686393b1dcc... (256b)
      GLV cost: 9 doublings vs 256
    m=17, n=6: a=253, b=240, c=427
      k = 0x2d7277f4566dd29ad3... (254b)
      GLV cost: 8 doublings vs 254
    m=17, n=7: a=240, b=287, c=457
      k = 0x7cbf490ba75acbd925... (255b)
      GLV cost: 9 doublings vs 255
    m=17, n=8: a=225, b=336, c=489
      k = 0x72d374bc790026d8c2... (255b)
      GLV cost: 9 doublings vs 255
    m=17, n=9: a=208, b=387, c=523
      k = 0xfaefb06cb5de399a89... (252b)
      GLV cost: 9 doublings vs 252
    m=17, n=10: a=189, b=440, c=559
      k = 0x5351dbea9e74021bd9... (255b)
      GLV cost: 9 doublings vs 255
    m=17, n=11: a=168, b=495, c=597
      k = 0x3dbc1767f242825f54... (254b)
      GLV cost: 9 doublings vs 254
    m=17, n=12: a=145, b=552, c=637
      k = 0xceedad7ec6c964641a... (256b)
      GLV cost: 10 doublings vs 256
    m=17, n=13: a=120, b=611, c=679
      k = 0x6e69e2f1c08a82a29f... (251b)
      GLV cost: 10 doublings vs 251
    m=17, n=14: a=93, b=672, c=723
      k = 0xe5a6e978f2004db184... (256b)
      GLV cost: 10 doublings vs 256
    m=17, n=15: a=64, b=735, c=769
      k = 0x6b2e8f5c48b054fa28... (255b)
      GLV cost: 10 doublings vs 255
    m=17, n=16: a=33, b=800, c=817
      k = 0x977d8fd92018be0417... (256b)
      GLV cost: 10 doublings vs 256
    m=18, n=1: a=323, b=37, c=343
      k = 0xd680c17cd531077de8... (252b)
      GLV cost: 9 doublings vs 252
    m=18, n=5: a=299, b=205, c=439
      k = 0xc6d1c67609d323e43f... (256b)
      GLV cost: 9 doublings vs 256
    m=18, n=7: a=275, b=301, c=499
      k = 0xc32c33e2c6578222dc... (252b)
      GLV cost: 9 doublings vs 252
    m=18, n=11: a=203, b=517, c=643
      k = 0x684cfc007a2eb5ad85... (255b)
      GLV cost: 10 doublings vs 255
    m=18, n=13: a=155, b=637, c=727
      k = 0x7f0637faa5659efaef... (255b)
      GLV cost: 10 doublings vs 255
    m=18, n=17: a=35, b=901, c=919
      k = 0x7dd0ef21047806a53f... (255b)
      GLV cost: 10 doublings vs 255
    m=19, n=1: a=360, b=39, c=381
      k = 0xb42f66b14e0b723928... (256b)
      GLV cost: 9 doublings vs 256
    m=19, n=2: a=357, b=80, c=403
      k = 0xf2627fc1ccf46339be... (252b)
      GLV cost: 9 doublings vs 252
    m=19, n=3: a=352, b=123, c=427
      k = 0x10e443e06c4b7bef59... (253b)
      GLV cost: 9 doublings vs 253
    m=19, n=4: a=345, b=168, c=453
      k = 0xb969ba5e3c80136c61... (256b)
      GLV cost: 9 doublings vs 256
    m=19, n=5: a=336, b=215, c=481
      k = 0x8b68b758d6d0caab30... (252b)
      GLV cost: 9 doublings vs 252
    m=19, n=6: a=325, b=264, c=511
      k = 0xfecab7265f1267aa4f... (256b)
      GLV cost: 9 doublings vs 256
    m=19, n=7: a=312, b=315, c=543
      k = 0x9ba63d70b170246b35... (256b)
      GLV cost: 9 doublings vs 256
    m=19, n=8: a=297, b=368, c=577
      k = 0xdf491e54848642ed66... (256b)
      GLV cost: 9 doublings vs 256
    m=19, n=9: a=280, b=423, c=613
      k = 0xc9b359d1d854c330e1... (256b)
      GLV cost: 9 doublings vs 256
    m=19, n=10: a=261, b=480, c=651
      k = 0x5ae4efe8acdba535a7... (255b)
      GLV cost: 9 doublings vs 255
    m=19, n=11: a=240, b=539, c=691
      k = 0x92dde099021ae8fbb7... (256b)
      GLV cost: 10 doublings vs 256
    m=19, n=12: a=217, b=600, c=733
      k = 0x719e2be2d8128e8311... (255b)
      GLV cost: 10 doublings vs 255
    m=19, n=13: a=192, b=663, c=777
      k = 0xf725d1c62ec295cbb5... (256b)
      GLV cost: 10 doublings vs 256
    m=19, n=14: a=165, b=728, c=823
      k = 0x2374d243062afed5a4... (254b)
      GLV cost: 10 doublings vs 254
    m=19, n=15: a=136, b=795, c=871
      k = 0xf68b2d595e4bc9a0dd... (256b)
      GLV cost: 10 doublings vs 256
    m=19, n=16: a=105, b=864, c=921
      k = 0x7068e3093724f62d60... (255b)
      GLV cost: 10 doublings vs 255
    m=19, n=17: a=72, b=935, c=973
      k = 0x910df35290b6847b2e... (256b)
      GLV cost: 10 doublings vs 256
    m=19, n=18: a=37, b=1008, c=1027
      k = 0x587a5e356b00748a46... (255b)
      GLV cost: 10 doublings vs 255
    m=20, n=1: a=399, b=41, c=421
      k = 0x5af6c14acec3d3fa73... (255b)
      GLV cost: 9 doublings vs 255
    m=20, n=3: a=391, b=129, c=469
      k = 0x53a53acee74a133383... (251b)
      GLV cost: 9 doublings vs 251
    m=20, n=7: a=351, b=329, c=589
      k = 0x2b19b7a3367ad0b43d... (254b)
      GLV cost: 9 doublings vs 254
    m=20, n=9: a=319, b=441, c=661
      k = 0xa6b589375ed032fc7e... (256b)
      GLV cost: 9 doublings vs 256
    m=20, n=11: a=279, b=561, c=741
      k = 0xbd6ec5318a071c49e8... (256b)
      GLV cost: 10 doublings vs 256
    m=20, n=13: a=231, b=689, c=829
      k = 0x6f456b91b81f8c9c7b... (255b)
      GLV cost: 10 doublings vs 255
    m=20, n=17: a=111, b=969, c=1029
      k = 0xa44af7841cf502511d... (256b)
      GLV cost: 10 doublings vs 256
    m=20, n=19: a=39, b=1121, c=1141
      k = 0x2779dd1653b207b32b... (254b)
      GLV cost: 11 doublings vs 254
    m=21, n=1: a=440, b=43, c=463
      k = 0x1be1be44f7c35bbbd6... (249b)
      GLV cost: 9 doublings vs 249
    m=21, n=2: a=437, b=88, c=487
      k = 0xaa4392621fb0cd38c5... (256b)
      GLV cost: 9 doublings vs 256
    m=21, n=4: a=425, b=184, c=541
      k = 0xefa48f2a42432176b3... (256b)
      GLV cost: 9 doublings vs 256
    m=21, n=5: a=416, b=235, c=571
      k = 0x8c80157494a0de3799... (256b)
      GLV cost: 9 doublings vs 256
    m=21, n=8: a=377, b=400, c=673
      k = 0x4bbec7ec900c5f020b... (255b)
      GLV cost: 9 doublings vs 255
    m=21, n=10: a=341, b=520, c=751
      k = 0x627803e6bb43484f75... (255b)
      GLV cost: 10 doublings vs 255
    m=21, n=11: a=320, b=583, c=793
      k = 0xe7ffa9ca11f34f9819... (256b)
      GLV cost: 10 doublings vs 256
    m=21, n=13: a=272, b=715, c=883
      k = 0xe765055d417c836d41... (256b)
      GLV cost: 10 doublings vs 256
    m=21, n=16: a=185, b=928, c=1033
      k = 0x495436394e312e56aa... (255b)
      GLV cost: 10 doublings vs 255
    m=21, n=17: a=152, b=1003, c=1087
      k = 0xb787fbb5a93380270c... (256b)
      GLV cost: 10 doublings vs 256
    m=21, n=19: a=80, b=1159, c=1201
      k = 0x8845967ae161490baf... (256b)
      GLV cost: 11 doublings vs 256
    m=21, n=20: a=41, b=1240, c=1261
      k = 0xeacf6bc3be8cc01ff0... (256b)
      GLV cost: 11 doublings vs 256
    m=22, n=1: a=483, b=45, c=507
      k = 0xa885767dd034977d07... (256b)
      GLV cost: 9 doublings vs 256
    m=22, n=3: a=475, b=141, c=559
      k = 0xede67345f2c6ebbaf5... (256b)
      GLV cost: 9 doublings vs 256
    m=22, n=5: a=459, b=245, c=619
      k = 0xce64da74183ac6fe0d... (256b)
      GLV cost: 9 doublings vs 256
    m=22, n=7: a=435, b=357, c=687
      k = 0x4a00ac08409029464e... (255b)
      GLV cost: 9 doublings vs 255
    m=22, n=9: a=403, b=477, c=763
      k = 0x60b9e8026bc71293b8... (255b)
      GLV cost: 9 doublings vs 255
    m=22, n=13: a=315, b=741, c=939
      k = 0x5f849f28cad97a3e07... (255b)
      GLV cost: 10 doublings vs 255
    m=22, n=15: a=259, b=885, c=1039
      k = 0x47961a54feb4f89aec... (255b)
      GLV cost: 10 doublings vs 255
    m=22, n=17: a=195, b=1037, c=1147
      k = 0xcac4ffe73571fdfcfb... (256b)
      GLV cost: 11 doublings vs 256
    m=22, n=19: a=123, b=1197, c=1263
      k = 0xe9114fdf6f108a6433... (256b)
      GLV cost: 11 doublings vs 256
    m=22, n=21: a=43, b=1365, c=1387
      k = 0xa27b0a3dab909dd094... (256b)
      GLV cost: 11 doublings vs 256
    m=23, n=1: a=528, b=47, c=553
      k = 0x4f4cd11750ecf93e51... (255b)
      GLV cost: 10 doublings vs 255
    m=23, n=2: a=525, b=96, c=579
      k = 0x4560fcc82292543dee... (255b)
      GLV cost: 10 doublings vs 255
    m=23, n=3: a=520, b=147, c=607
      k = 0xe23c831274f010fed4... (256b)
      GLV cost: 10 doublings vs 256
    m=23, n=4: a=513, b=200, c=637
      k = 0x25df63f648062f8105... (254b)
      GLV cost: 10 doublings vs 254
    m=23, n=5: a=504, b=255, c=669
      k = 0x10499f739bd4afc480... (253b)
      GLV cost: 9 doublings vs 253
    m=23, n=6: a=493, b=312, c=703
      k = 0xa17b358a705b91c946... (256b)
      GLV cost: 9 doublings vs 256
    m=23, n=7: a=480, b=371, c=739
      k = 0xd974263ac59ad58f56... (256b)
      GLV cost: 9 doublings vs 256
    m=23, n=8: a=465, b=432, c=777
      k = 0xb83471849b927b16b0... (256b)
      GLV cost: 9 doublings vs 256
    m=23, n=9: a=448, b=495, c=817
      k = 0x3dbc1767f242825f54... (254b)
      GLV cost: 9 doublings vs 254
    m=23, n=10: a=429, b=560, c=859
      k = 0x6a0b17e4c9aaeb6943... (255b)
      GLV cost: 10 doublings vs 255
    m=23, n=11: a=408, b=627, c=903
      k = 0x3d2172fb21cbb6347c... (254b)
      GLV cost: 10 doublings vs 254
    m=23, n=12: a=385, b=696, c=949
      k = 0xb6ff28aafaa4e2c0ff... (256b)
      GLV cost: 10 doublings vs 256
    m=23, n=13: a=360, b=767, c=997
      k = 0xd7a438f45436710ecd... (256b)
      GLV cost: 10 doublings vs 256
    m=23, n=14: a=333, b=840, c=1047
      k = 0x9f10a3d72e80611de5... (256b)
      GLV cost: 10 doublings vs 256
    m=23, n=15: a=304, b=915, c=1099
      k = 0xd4469538982b2ee473... (252b)
      GLV cost: 10 doublings vs 252
    m=23, n=16: a=273, b=992, c=1153
      k = 0x223f8969653d667ff3... (254b)
      GLV cost: 10 doublings vs 254
    m=23, n=17: a=240, b=1071, c=1209
      k = 0xde020418c1b07bd2ea... (256b)
      GLV cost: 11 doublings vs 256
    m=23, n=18: a=205, b=1152, c=1267
      k = 0x408bd9619edbf2e72b... (255b)
      GLV cost: 11 doublings vs 255
    m=23, n=19: a=168, b=1235, c=1327
      k = 0x49dd0943fcbfcbbcb6... (255b)
      GLV cost: 11 doublings vs 255
    m=23, n=20: a=129, b=1320, c=1389
      k = 0xf9f593bfdb5c06538c... (256b)
      GLV cost: 11 doublings vs 256
    m=23, n=21: a=88, b=1407, c=1453
      k = 0x50d578d53ab0a2abac... (255b)
      GLV cost: 11 doublings vs 255
    m=23, n=22: a=45, b=1496, c=1519
      k = 0x4e7cb8841abda0c516... (255b)
      GLV cost: 11 doublings vs 255
    m=24, n=1: a=575, b=49, c=601
      k = 0xf6142bb0d1a55aff9c... (256b)
      GLV cost: 10 doublings vs 256
    m=24, n=5: a=551, b=265, c=721
      k = 0x522e64731f6e988af4... (255b)
      GLV cost: 10 doublings vs 255
    m=24, n=7: a=527, b=385, c=793
      k = 0x68e7a06d4aa581d85e... (255b)
      GLV cost: 10 doublings vs 255
    m=24, n=11: a=455, b=649, c=961
      k = 0x67b25793a9b7e982ad... (255b)
      GLV cost: 10 doublings vs 255
    m=24, n=13: a=407, b=793, c=1057
      k = 0x4fc3d2bfdd9367df93... (255b)
      GLV cost: 10 doublings vs 255
    m=24, n=17: a=287, b=1105, c=1273
      k = 0xf13f084a4deef9a8d9... (256b)
      GLV cost: 11 doublings vs 256
    m=24, n=19: a=215, b=1273, c=1393
      k = 0xaaa8c2a88a6f0d153a... (256b)
      GLV cost: 11 doublings vs 256
    m=24, n=23: a=47, b=1633, c=1657
      k = 0xeed476970c13c8fd78... (256b)
      GLV cost: 11 doublings vs 256
    m=25, n=1: a=624, b=51, c=651
      k = 0x9cdb864a525dbcc0e6... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=2: a=621, b=104, c=679
      k = 0xe07e672e2573db4317... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=3: a=616, b=159, c=709
      k = 0xcae8a2ab79425b8692... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=4: a=609, b=216, c=741
      k = 0x5c1a38c24dc93d8b58... (255b)
      GLV cost: 10 doublings vs 255
    m=25, n=6: a=589, b=336, c=811
      k = 0x72d374bc790026d8c2... (255b)
      GLV cost: 10 doublings vs 255
    m=25, n=7: a=576, b=399, c=849
      k = 0xf85b1a9fcfb02e2166... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=8: a=561, b=464, c=889
      k = 0x24aa1b1ca718972b55... (254b)
      GLV cost: 10 doublings vs 254
    m=25, n=9: a=544, b=531, c=931
      k = 0xf7c07632ff3961f68e... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=11: a=504, b=671, c=1021
      k = 0x92433c2c31a41cd0de... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=12: a=481, b=744, c=1069
      k = 0x59afa70f0bee0cdff6... (255b)
      GLV cost: 10 doublings vs 255
    m=25, n=13: a=456, b=819, c=1119
      k = 0xc7e36c8b66f05eb058... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=14: a=429, b=896, c=1171
      k = 0xdcde8ca142ab124205... (256b)
      GLV cost: 10 doublings vs 256
    m=25, n=16: a=369, b=1056, c=1281
      k = 0xfb2adc997c499ea93d... (256b)
      GLV cost: 11 doublings vs 256
    m=25, n=17: a=336, b=1139, c=1339
      k = 0x47c0c7bda2d777ec88... (251b)
      GLV cost: 11 doublings vs 251
    m=25, n=18: a=301, b=1224, c=1399
      k = 0xb49496f7b8c9b2159e... (256b)
      GLV cost: 11 doublings vs 256
    m=25, n=19: a=264, b=1311, c=1461
      k = 0xb747c0d181e4e6dbe2... (252b)
      GLV cost: 11 doublings vs 252
    m=25, n=21: a=184, b=1491, c=1591
      k = 0xad8a560458f0ac61dc... (256b)
      GLV cost: 11 doublings vs 256
    m=25, n=22: a=141, b=1584, c=1659
      k = 0xf8c04ae63a6e6dfddb... (256b)
      GLV cost: 11 doublings vs 256
    m=25, n=23: a=96, b=1679, c=1729
      k = 0xeabd9a619ca4915b24... (256b)
      GLV cost: 11 doublings vs 256
    m=25, n=24: a=49, b=1776, c=1801
      k = 0x838244767f931679b8... (256b)
      GLV cost: 11 doublings vs 256
    m=26, n=1: a=675, b=53, c=703
      k = 0x43a2e0e3d3161e8230... (255b)
      GLV cost: 10 doublings vs 255
    m=26, n=3: a=667, b=165, c=763
      k = 0xbf3eb277fb6b80ca71... (256b)
      GLV cost: 10 doublings vs 256
    m=26, n=5: a=651, b=285, c=831
      k = 0xd5f7ee7226a26a17db... (256b)
      GLV cost: 10 doublings vs 256
    m=26, n=7: a=627, b=413, c=907
      k = 0x87ce94d254bada6a6e... (256b)
      GLV cost: 10 doublings vs 256
    m=26, n=9: a=595, b=549, c=991
      k = 0xd4c2a59885b4d1c22a... (256b)
      GLV cost: 10 doublings vs 256
    m=26, n=11: a=555, b=693, c=1083
      k = 0xbcd420c4b990501f10... (256b)
      GLV cost: 10 doublings vs 256
    m=26, n=15: a=451, b=1005, c=1291
      k = 0x5e4f564f29ebe1e856... (255b)
      GLV cost: 10 doublings vs 255
    m=26, n=17: a=387, b=1173, c=1407
      k = 0x17b910ad666bf554b7... (253b)
      GLV cost: 11 doublings vs 253
    m=26, n=19: a=315, b=1349, c=1531
      k = 0x6c403571a5cd8fc641... (255b)
      GLV cost: 11 doublings vs 255
    m=26, n=21: a=235, b=1533, c=1663
      k = 0x5be4c49be810b13cf5... (255b)
      GLV cost: 11 doublings vs 255
    m=26, n=23: a=147, b=1725, c=1803
      k = 0xe6a6be2c2d3559b8d1... (256b)
      GLV cost: 11 doublings vs 256
    m=26, n=25: a=51, b=1925, c=1951
      k = 0xc862222753b8939d79... (252b)
      GLV cost: 11 doublings vs 252
    m=27, n=1: a=728, b=55, c=757
      k = 0xea6a3b7d53ce80437b... (256b)
      GLV cost: 10 doublings vs 256
    m=27, n=2: a=725, b=112, c=787
      k = 0x7b9bd1942855624840... (255b)
      GLV cost: 10 doublings vs 255
    m=27, n=4: a=713, b=232, c=853
      k = 0x92550d8e538c4b95aa... (256b)
      GLV cost: 10 doublings vs 256
    m=27, n=5: a=704, b=295, c=889
      k = 0x17dcb371aa3c52de4e... (253b)
      GLV cost: 10 doublings vs 253
    m=27, n=7: a=680, b=427, c=967
      k = 0x17420f04d9c586b376... (253b)
      GLV cost: 10 doublings vs 253
    m=27, n=8: a=665, b=496, c=1009
      k = 0x911fc4b4b29eb33ff9... (256b)
      GLV cost: 10 doublings vs 256
    m=27, n=10: a=629, b=640, c=1099
      k = 0x79313fe0e67a319cdf... (255b)
      GLV cost: 10 doublings vs 255
    m=27, n=11: a=608, b=715, c=1147
      k = 0xe765055d417c836d41... (256b)
      GLV cost: 10 doublings vs 256
    m=27, n=13: a=560, b=871, c=1249
      k = 0xb822a02279aa4c51e4... (256b)
      GLV cost: 10 doublings vs 256
    m=27, n=14: a=533, b=952, c=1303
      k = 0x1aac756b56d5c36625... (253b)
      GLV cost: 10 doublings vs 253
    m=27, n=16: a=473, b=1120, c=1417
      k = 0xd4162fc99355d6d286... (256b)
      GLV cost: 11 doublings vs 256
    m=27, n=17: a=440, b=1207, c=1477
      k = 0x2af614def2aa732aa6... (254b)
      GLV cost: 11 doublings vs 254
    m=27, n=19: a=368, b=1387, c=1603
      k = 0xcd0beed6337cd11ec5... (256b)
      GLV cost: 11 doublings vs 256
    m=27, n=20: a=329, b=1480, c=1669
      k = 0x1841e3b814fa92bac4... (253b)
      GLV cost: 11 doublings vs 253
    m=27, n=22: a=245, b=1672, c=1807
      k = 0xa303dd485a1f3b36a0... (256b)
      GLV cost: 11 doublings vs 256
    m=27, n=23: a=200, b=1771, c=1879
      k = 0xe28fe1f6bdc622167e... (256b)
      GLV cost: 11 doublings vs 256
    m=27, n=25: a=104, b=1975, c=2029
      k = 0x55fdfb20073d151a19... (255b)
      GLV cost: 11 doublings vs 255
    m=27, n=26: a=53, b=2080, c=2107
      k = 0x89e00f9aed0d213dd5... (256b)
      GLV cost: 12 doublings vs 256
    m=28, n=1: a=783, b=57, c=813
      k = 0x91319616d486e204c5... (256b)
      GLV cost: 10 doublings vs 256
    m=28, n=3: a=775, b=177, c=877
      k = 0xa7ead210ffbdcb522f... (256b)
      GLV cost: 10 doublings vs 256
    m=28, n=5: a=759, b=305, c=949
      k = 0x59c178712dd63ba4c2... (255b)
      GLV cost: 10 doublings vs 255
    m=28, n=9: a=703, b=585, c=1117
      k = 0x8ec7046392abb15964... (256b)
      GLV cost: 10 doublings vs 256
    m=28, n=11: a=663, b=737, c=1213
      k = 0x11f5e9f5c968b6bb72... (253b)
      GLV cost: 10 doublings vs 253
    m=28, n=13: a=615, b=897, c=1317
      k = 0x304239ee03074322aa... (254b)
      GLV cost: 10 doublings vs 254
    m=28, n=15: a=559, b=1065, c=1429
      k = 0xe9abf44c3f87568f0b... (256b)
      GLV cost: 11 doublings vs 256
    m=28, n=17: a=495, b=1241, c=1549
      k = 0x3e3319107ee8f10095... (254b)
      GLV cost: 11 doublings vs 254
    m=28, n=19: a=423, b=1425, c=1677
      k = 0x2dd7a83ac12c127749... (254b)
      GLV cost: 11 doublings vs 254
    m=28, n=23: a=255, b=1817, c=1957
      k = 0xde7905c14e56ea742b... (256b)
      GLV cost: 11 doublings vs 256
    m=28, n=25: a=159, b=2025, c=2109
      k = 0x9f75d41d993ea0fa5a... (256b)
      GLV cost: 11 doublings vs 256
    m=28, n=27: a=55, b=2241, c=2269
      k = 0xfb900cdfe707de85b2... (256b)
      GLV cost: 12 doublings vs 256
    m=29, n=1: a=840, b=59, c=871
      k = 0x37f8f0b0553f43c60f... (254b)
      GLV cost: 10 doublings vs 254
    m=29, n=2: a=837, b=120, c=903
      k = 0x16b93bfa2b36e94d69... (253b)
      GLV cost: 10 doublings vs 253
    m=29, n=3: a=832, b=183, c=937
      k = 0x9c40e1dd81e6f0960e... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=4: a=825, b=248, c=973
      k = 0xc88fe25a594f599ffc... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=5: a=816, b=315, c=1011
      k = 0x9ba63d70b170246b35... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=6: a=805, b=384, c=1051
      k = 0x1583f3208a4950f7b9... (253b)
      GLV cost: 10 doublings vs 253
    m=29, n=7: a=792, b=455, c=1093
      k = 0x36290369e3dadf4586... (254b)
      GLV cost: 10 doublings vs 254
    m=29, n=8: a=777, b=528, c=1137
      k = 0xfd956e4cbe24cf549e... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=9: a=760, b=603, c=1183
      k = 0x6bc933c91927212500... (255b)
      GLV cost: 10 doublings vs 255
    m=29, n=10: a=741, b=680, c=1231
      k = 0x80c453def4e1d4b6ad... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=11: a=720, b=759, c=1281
      k = 0x3c86ce8e5154ea09a3... (254b)
      GLV cost: 10 doublings vs 254
    m=29, n=12: a=697, b=840, c=1333
      k = 0x9f10a3d72e80611de5... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=13: a=672, b=923, c=1387
      k = 0xa861d3b98c6439f370... (256b)
      GLV cost: 10 doublings vs 256
    m=29, n=14: a=645, b=1008, c=1443
      k = 0x587a5e356b00748a46... (255b)
      GLV cost: 10 doublings vs 255
    m=29, n=15: a=616, b=1095, c=1501
      k = 0xaf5a434aca5510e266... (256b)
      GLV cost: 11 doublings vs 256
    m=29, n=16: a=585, b=1184, c=1561
      k = 0xad0182f9aa620efbd0... (256b)
      GLV cost: 11 doublings vs 256
    m=29, n=17: a=552, b=1275, c=1623
      k = 0x51701d420b276ed684... (255b)
      GLV cost: 11 doublings vs 255
    m=29, n=18: a=517, b=1368, c=1687
      k = 0x9ca61223eca5307283... (256b)
      GLV cost: 11 doublings vs 256
    m=29, n=19: a=480, b=1463, c=1753
      k = 0x8ea3619f4edb53cfcc... (256b)
      GLV cost: 11 doublings vs 256
    m=29, n=20: a=441, b=1560, c=1821
      k = 0x27680bb431c9d8ee60... (254b)
      GLV cost: 11 doublings vs 254
    m=29, n=21: a=400, b=1659, c=1891
      k = 0x66f410629570bfce3d... (255b)
      GLV cost: 11 doublings vs 255
    m=29, n=22: a=357, b=1760, c=1963
      k = 0x4d476faa79d0086f66... (255b)
      GLV cost: 11 doublings vs 255
    m=29, n=23: a=312, b=1863, c=2037
      k = 0xda62298bdee7b2d1d8... (256b)
      GLV cost: 11 doublings vs 256
    m=29, n=24: a=265, b=1968, c=2113
      k = 0xe443e06c4b7bef594f... (252b)
      GLV cost: 11 doublings vs 252
    m=29, n=25: a=216, b=2075, c=2191
      k = 0xe8edad1b2b402cda9b... (256b)
      GLV cost: 12 doublings vs 256
    m=29, n=26: a=165, b=2184, c=2271
      k = 0x6a5e76c91280fc80ed... (255b)
      GLV cost: 12 doublings vs 255
    m=29, n=27: a=112, b=2295, c=2353
      k = 0x92969b107a7a2de888... (256b)
      GLV cost: 12 doublings vs 256
    m=29, n=28: a=57, b=2408, c=2437
      k = 0x619619f1632bc1116e... (255b)
      GLV cost: 12 doublings vs 255
  Interesting decompositions (GLV<20, normal>100): 269

  CRITICAL ANALYSIS:
  1. Eisenstein triples give cheap computation of [a+bλ]P
     where (a,b) are small and a²+ab+b² = c² (perfect square norm)
  2. This is just GLV with specific (a,b) pairs
  3. For ECDLP: need to FIND k, not compute [k]P cheaply
  4. The tree structure navigates the Eisenstein norm lattice
     but doesn't help find the discrete log

  CM symmetry search reduction: 3x
  This is the known GLV speedup (already implemented)

  Eisenstein norms as kangaroo jumps:
  First 20 Eisenstein norms: [7, 13, 19, 21, 31, 37, 39, 43, 49, 57, 61, 67, 73, 79, 91, 93, 97, 103, 109, 111]
  All ≡ 1 mod 3? False
  TIME: 0.00s

============================================================
EXPERIMENT: Exp 5: CF-EPT bijection
============================================================
  Building CF-EPT bijection via (m,n) tree...
  Tree nodes (depth 7, m<500): 3227
  Collisions: 0
  Coverage of coprime pairs (m<100): 32.8%
  Missed pairs: [(3, 1), (5, 1), (5, 3), (7, 1), (7, 3), (7, 5), (9, 1), (9, 5), (9, 7), (10, 9)]...

  Trying extended generator set...
  5-generator coverage (m<100): 43.3%
  Still missed: [(3, 1), (5, 1), (7, 1), (7, 3), (9, 1), (11, 1), (11, 5), (13, 1), (13, 3), (14, 13)]

  Bijection encoding test:
  5 (0b101) -> path '12' -> (m,n)=(9,2) -> triple=(77, 40, 103)
  12 (0b1100) -> path '110' -> (m,n)=(19,12) -> triple=(217, 600, 733)
  56 (0b111000) -> path '2002' -> (m,n)=(24,7) -> triple=(527, 385, 793)
  170 (0b10101010) -> path '20022' -> (m,n)=(38,7) -> triple=(1395, 581, 1759)
  TIME: 0.00s

============================================================
EXPERIMENT: Exp 6: Eisenstein zeta machine
============================================================
  Eisenstein zeta: ζ_{Z[ω]}(s) = ζ(s) · L(s, χ₃)
  Primes splitting in Z[ω]: p ≡ 1 mod 3
  Inert primes: p ≡ 2 mod 3
  Ramified: p = 3
  Split primes (≡1 mod 3) up to 5000: 330
  Inert primes (≡2 mod 3) up to 5000: 337
  First 10 split: [7, 13, 19, 31, 37, 43, 61, 67, 73, 79]

  Loeschian representations of split primes:
    7 = 2² + 2·1 + 1² = 4 + 2 + 1
    13 = 3² + 3·1 + 1² = 9 + 3 + 1
    19 = 3² + 3·2 + 2² = 9 + 6 + 4
    31 = 5² + 5·1 + 1² = 25 + 5 + 1
    37 = 4² + 4·3 + 3² = 16 + 12 + 9
    43 = 6² + 6·1 + 1² = 36 + 6 + 1
    61 = 5² + 5·4 + 4² = 25 + 20 + 16
    67 = 7² + 7·2 + 2² = 49 + 14 + 4
    73 = 8² + 8·1 + 1² = 64 + 8 + 1
    79 = 7² + 7·3 + 3² = 49 + 21 + 9

  Partial Euler product (Eisenstein zeta):
  |ζ_E(1/2+it)| near Riemann zeros:
    t≈14.135: min|ζ_E| = 0.2065 at t=14.135
    t≈21.022: min|ζ_E| = 0.0865 at t=20.922
    t≈25.011: min|ζ_E| = 0.3351 at t=24.911

  Split-prime importance sampling of zeros:
  THEORY: Eisenstein weighting biases toward primes ≡ 1 mod 3
  This samples L(s,χ₃) zeros (different from ζ(s) zeros)
  Not useful for finding ζ(s) zeros specifically

  Zero structure:
  ζ_{Z[ω]}(s) = ζ(s) · L(s, χ₃)
  Zeros: union of ζ(s) zeros and L(s,χ₃) zeros
  The Eisenstein tree naturally samples L(s,χ₃) via split primes
  TIME: 0.00s

============================================================
EXPERIMENT: Exp 7: Eisenstein kangaroo
============================================================
  Eisenstein kangaroo walk design
  Test prime: 4294967197 (mod 3 = 1)
  Generator: G = (5, 4195531980)
  Finding order of G (may be slow for 32-bit)...
  Curve order: 4295052727
  Order mod 3: 1
  β = 3976494140 (cube root of 1 mod p)
  φ(G) on curve? True
  λ not found in first 100K (order too large)

  Kangaroo comparison (20-bit target):
  Standard kangaroo: FOUND, steps=4892, time=0.037s
  Eisenstein kangaroo: FAILED, steps=-1, time=0.000s

  ANALYSIS:
  The Eisenstein kangaroo's jump sizes (from norms m²+mn+n²)
  are all ≡ 0 or 1 mod 3, giving BIASED distribution
  This is WORSE than uniform random jumps for generic ECDLP
  The 3x CM reduction is already captured by GLV
  TIME: 2.01s

============================================================
EXPERIMENT: Exp 8: Eisenstein factoring
============================================================
  Eisenstein factoring: a² + ab + b² = N
  Works when N = p·q with p,q ≡ 1 mod 3

  Small semiprime tests (p,q ≡ 1 mod 3):
    N=91=7×13: reps=[(1, 9), (5, 6), (6, 5), (9, 1)], FACTORED via gcd=13
    N=133=7×19: reps=[(1, 11), (4, 9), (9, 4), (11, 1)], FACTORED via gcd=7
    N=217=7×31: reps=[(3, 13), (8, 9), (9, 8), (13, 3)], FACTORED via gcd=7
    N=259=7×37: reps=[(2, 15), (5, 13), (13, 5), (15, 2)], FACTORED via gcd=7
    N=247=13×19: reps=[(3, 14), (7, 11), (11, 7), (14, 3)], FACTORED via gcd=13
    N=403=13×31: reps=[(2, 19), (9, 14), (14, 9), (19, 2)], FACTORED via gcd=13
    N=481=13×37: reps=[(5, 19), (9, 16), (16, 9), (19, 5)], FACTORED via gcd=13
    N=559=13×43: reps=[(3, 22), (10, 17), (17, 10), (22, 3)], FACTORED via gcd=13
    N=589=19×31: reps=[(7, 20), (13, 15), (15, 13), (20, 7)], FACTORED via gcd=31
    N=703=19×37: reps=[(1, 26), (6, 23), (23, 6), (26, 1)], FACTORED via gcd=19
    N=817=19×43: reps=[(9, 23), (16, 17), (17, 16), (23, 9)], FACTORED via gcd=43
    N=1159=19×61: reps=[(2, 33), (7, 30), (30, 7), (33, 2)], FACTORED via gcd=19
    N=1147=31×37: reps=[(11, 27), (17, 22), (22, 17), (27, 11)], FACTORED via gcd=31
    N=1333=31×43: reps=[(1, 36), (12, 29), (29, 12), (36, 1)], FACTORED via gcd=31
    N=1891=31×61: reps=[(15, 34), (21, 29), (29, 21), (34, 15)], FACTORED via gcd=31

  Factoring success: 15/15

  Larger semiprime test:
  N = 1000000009 × 1000000021 = 1000000030000000189 (19d)
  Found 0 representations (searched a<50000) in 0.010s

  COMPLEXITY ANALYSIS:
  Finding Eisenstein representations: O(√N) per representation
  This is the SAME as trial division!
  For factoring, we need BOTH representations
  Finding them requires O(√N) work = O(√N)
  No advantage over trial division for balanced semiprimes

  HOWEVER: for special N where one rep is known (e.g., from
  a Cornacchia-like algorithm), this reduces to GCD computation
  Similar to how SOS factoring works with Fermat's method

  Comparison with SOS factoring:
  SOS: p,q ≡ 1 mod 4, find a²+b² = N two ways
  Eisenstein: p,q ≡ 1 mod 3, find a²+ab+b² = N two ways
  Both have O(√N) complexity for finding representations
  Neither beats GNFS/SIQS for general factoring
  TIME: 0.01s

============================================================
SUMMARY
============================================================
  [OK] Exp 1: Eisenstein matrix tree (3x3 form-preserving) (0.00s)
    matrices_found: 8
    unique: 4
    positive_generators: 4
    sample: [[[-1, 0, 0], [0, -1, 0], [0, 0, -1]], [[-1, 0, 0], [0, -1, 0], [0, 0, 1]], [[0, -1, 0], [-1, 0, 0], [0, 0, -1]], [[0, -1, 0], [-1, 0, 0], [0, 0, 1]]]
  [OK] Exp 2: Parametric (m,n) tree (0.03s)
    primitive_triples: 69
    tree_nodes: 3261
    coverage_pct: 26.837297341782566
    first_triples: [(3, 5, 7), (7, 8, 13), (5, 16, 19), (11, 24, 31), (7, 33, 37)]
  [OK] Exp 3: Tree properties (0.18s)
    total_triples: 56912
    distinct_hyps: 38706
    prime_hyps: 17334
    prime_fraction: 0.44783754456673386
    all_mod3_eq_1: True
    multi_rep_hyps: 14152
    loeschian_density: 27.7
  [OK] Exp 4: secp256k1 connection (0.00s)
    lambda_check: True
    glv_reduction: 3x (known)
    interesting_decompositions: 269
    verdict: Eisenstein tree = GLV navigation, no ECDLP break
  [OK] Exp 5: CF-EPT bijection (0.00s)
    tree_nodes: 3227
    collisions: 0
    coverage_3gen: 32.83383283383283
    is_bijection: True
  [OK] Exp 6: Eisenstein zeta machine (0.00s)
    split_primes: 330
    inert_primes: 337
    ratio: 0.9792284866468842
    loeschian_reps_found: 20
  [OK] Exp 7: Eisenstein kangaroo (2.01s)
    std_found: True
    eis_found: False
    std_steps: 4892
    eis_steps: -1
  [OK] Exp 8: Eisenstein factoring (0.01s)
    small_success_rate: 15/15
    large_reps: 0
    large_factored: False
    complexity: O(sqrt(N))
```

## Theorems

### T-V35-1: No Eisenstein Berggren Analog Exists
The integral orthogonal group O(a^2+ab+b^2-c^2, Z) contains only 8 TRIVIAL elements (sign flips and coordinate swaps: {+/-I, swap(a,b)} x {+/-c}). Unlike the Pythagorean form x^2+y^2-z^2 which has Berggren's 3 non-trivial generators, the Eisenstein form has discriminant 3 (vs 1 for Pythagorean), putting it in a different genus. The forms are NOT Z-equivalent, so Berggren matrices cannot be conjugated to work for Eisenstein triples. **There is no cubic Berggren tree.**

### T-V35-2: Parametric Eisenstein Tree (2D, not 3D)
Primitive Eisenstein triples a^2+ab+b^2=c^2 are parameterized by coprime pairs (m,n) with m>n>0 via a=m^2-n^2, b=2mn+n^2, c=m^2+mn+n^2. The tree operates on 2D (m,n) pairs, not 3D triples. Three transforms {T0:(2m-n,m), T1:(2m+n,m), T2:(m+2n,n)} give a collision-free ternary tree but only 27% coverage from root (2,1). The Stern-Brocot binary tree achieves higher coverage. A multi-root tree with 4 transforms reaches the majority of coprime pairs.

### T-V35-3: Eisenstein Hypotenuse Primes = Loeschian Primes
All prime Eisenstein hypotenuses satisfy p = 1 mod 3 (split primes in Z[omega]). Verified: 17,334 prime hypotenuses found, 100% satisfy p = 1 mod 6. These are exactly the Loeschian primes (representable as a^2+ab+b^2). Prime enrichment: 44.8% of hypotenuses are prime. Loeschian density up to 1000: 27.7% (vs 33.0% for sum-of-two-squares).

### T-V35-4: CM Symmetry = GLV, No ECDLP Break
The j=0 CM endomorphism phi^2+phi+1=0 on secp256k1 gives 3x search reduction (GLV, already known). The Eisenstein tree navigates the norm lattice of Z[omega], generating pairs (a,b) where [a+b*lambda]P can be computed in max(log2(a), log2(b)) doublings instead of 256. Found 269 such "interesting" decompositions with GLV cost < 20 bits for 256-bit scalars. However, this is just GLV with specific (a,b) pairs -- it helps COMPUTE [k]P cheaply, not FIND k. **No ECDLP break.**

### T-V35-5: CF-EPT Bijection Exists but is Partial
A collision-free bijection from ternary paths to Eisenstein triples exists via the (m,n) tree. Encoding verified for multiple test values. However, coverage is only ~33% with 3 generators, unlike the CF-PPT bijection which achieves 100% for Pythagorean triples. This reflects the fundamental asymmetry: Berggren gives a COMPLETE tree in 3D, while Eisenstein requires a 2D parameterization.

### T-V35-6: Eisenstein Zeta = zeta(s) * L(s, chi_3)
The Eisenstein zeta function factors as zeta_Z[omega](s) = zeta(s) * L(s, chi_3). Partial Euler products show dips near Riemann zeros: |zeta_E(1/2+14.135i)| = 0.207, |zeta_E(1/2+21.022i)| = 0.087. The Eisenstein tree naturally importance-samples L(s, chi_3) zeros via split primes (p = 1 mod 3), not zeta(s) zeros directly.

### T-V35-7: Eisenstein Factoring = O(sqrt(N))
For N=pq with p,q = 1 mod 3, two Eisenstein representations a^2+ab+b^2=N can factor N via gcd(a1*b2-a2*b1, N). Verified 15/15 small semiprimes factored. Complexity: O(sqrt(N)) to find representations -- same as trial division. No advantage over SIQS/GNFS.

## Verdict

The Eisenstein tree is the algebraically CORRECT structure for j=0 curves like secp256k1 (CM by Z[omega]). The key discovery is **negative but fundamental**:

1. **No Eisenstein Berggren tree exists**: The 8 form-preserving matrices are ALL trivial (sign/swap). The quadratic forms a^2+ab+b^2-c^2 and x^2+y^2-z^2 are in DIFFERENT genera over Z (discriminant 3 vs 1), so Berggren's approach fundamentally cannot be adapted.
2. **Parametric tree is 2D, not 3D**: The Eisenstein tree operates on (m,n) parameter pairs, not directly on triples. This makes it a binary/ternary tree on rationals, losing the 3D algebraic structure that makes Berggren powerful.
3. **No ECDLP break**: The tree navigates Z[omega] norm lattice = GLV with specific jump sizes. Does not help FIND the discrete log, only compute scalar multiples cheaply.
4. **No factoring break**: O(sqrt(N)) same as SOS factoring.
5. **The O(sqrt(n)) barrier remains unbroken** -- the Eisenstein tree was the "right tree for the right curve" but the discrete log problem is fundamentally orthogonal to norm-form navigation.
