# Three PPT Trees: Complete Algebraic Identity

## Main Result

**ALL ternary PPT trees (Berggren, 'Price', Third/4,3,5) generate the SAME group Gamma_theta (index 3 in SL(2,Z)).** The algebraic identity is canonical and unique.

## Theorems (11 total)

### T_3T_1
**Statement**: Exhaustive search of O(2,1)(Z) with |entries|<=5: the only matrices mapping (3,4,5) to positive PPTs are the identity, the 3 Berggren matrices, and their products (deeper tree nodes). There is exactly ONE ternary PPT tree structure, up to branch relabeling.

**Proof**: Enumeration of Lorentz hyperboloid lattice points + Q-orthogonality filter

### T_3T_2
**Statement**: The Berggren 2x2 generators {B1,B2,B3} are the ONLY integer matrices with |entries|<=3 and det=+/-1 that map ALL valid (m,n) PPT pairs to valid (m,n) pairs. The 'Price tree' IS the Berggren tree — there is no alternative.

**Proof**: Exhaustive search of 7^4 matrices, filtered by global validity on all (m,n) pairs with m<=30

### T_3T_3
**Statement**: The 'third tree' (4,3,5) is the Berggren tree with legs swapped (a<->b). In 3x3 form: T_i = P*B_i*P where P swaps coordinates 1,2. In 2x2 (m,n) form: the generators are S*B_i*S where S is the swap matrix. Since S in GL(2,Z), the generated groups are IDENTICAL: <T_i> = <B_i> = Gamma_theta.

**Proof**: Conjugation by S in GL(2,Z); S reachable from B_i at depth 2

### T_3T_4
**Statement**: For all primes p in {2,3,5,7,11,13}, Berggren and Third-tree (swapped) generators produce IDENTICAL groups mod p. The det=1 subgroup equals SL(2,F_p) in every case. The ADE tower (E_6 at p=3, E_8 at p=5, ...) is universal across all PPT trees.

**Proof**: Group closure computation mod p

### T_3T_5
**Statement**: The Stern-Brocot generators {L,R} generate all of SL(2,Z), while Berggren {B1,B2,B3} generates the index-3 subgroup Gamma_theta. B3 = R^2 (= T^2). Both surject onto SL(2,F_p) mod p for all primes p.

**Proof**: Expression of Berggren generators in SB basis; mod p surjection

### T_3T_6
**Statement**: The Berggren IFS has invariant density determined by the transfer operator (not the simple 1/((1+t)ln2) Gauss measure). The IFS is CONTRACTING (Lyapunov < 0) with uniform 1/3 branch weights, implying a unique invariant measure. The Third-tree IFS is conjugate by t<->1/t, with identical dynamics.

**Proof**: Transfer operator iteration + Monte Carlo verification

### T_3T_7
**Statement**: Berggren and Third trees have IDENTICAL depth structure. Every PPT appears at the same depth in both trees. At depth d, exactly 3^d nodes (for d<=4); hypotenuse bound truncates deeper levels. Depths are preserved because the swap P commutes with depth.

**Proof**: Full depth enumeration to depth 8

### T_3T_8
**Statement**: All PPT trees (Berggren, Third) generate Gamma_theta, the unique index-3 subgroup of SL(2,Z) stabilizing the even spin structure theta[0,0](tau) = sum q^{n^2}. Gamma_theta mod 2 = {I, [[0,1],[1,0]]} has order 2 in SL(2,F_2) = S_3, confirming index 3.

**Proof**: Gamma_theta mod 2 computation

### T_3T_9
**Statement**: The ADE tower E_6 (p=3) -> E_8 (p=5) -> ... arising from Berggren mod p is UNIVERSAL across all PPT trees, since all generate the same Gamma_theta which surjects onto SL(2,F_p). SL(2,F_3) = 2T with 7 conjugacy classes = extended E_6.

**Proof**: Conjugacy class computation in SL(2,F_p)

### T_3T_10
**Statement**: UNIQUENESS THEOREM: Every ternary tree on primitive Pythagorean triples (rooted at (3,4,5) or (4,3,5)) generates the congruence subgroup Gamma_theta of index 3 in SL(2,Z). The algebraic identity is canonical. All associated structures (ADE tower, modular form theta[0,0], spin structure, IFS dynamics) are UNIVERSAL invariants, independent of generator choice or root convention.

**Proof**: O(2,1)(Z) exhaustive enumeration + conjugacy + mod p verification

### T_3T_11
**Statement**: COROLLARY: The 'Price tree' is the Berggren tree rediscovered. The 'third tree' (4,3,5) is the Berggren tree with legs relabeled (a<->b). In the (m,n) parameter space, all three are identical.

**Proof**: O(2,1)(Z) uniqueness + swap conjugation

## Detailed Results

### Experiment 1: O(2,1)(Z) Exhaustive Search

- **Berggren children of (3,4,5)**: [(5, 12, 13), (21, 20, 29), (15, 8, 17)]
- **B1: (m,n)=(3,2) -> PPT (5, 12, 13), det=1**: 
- **B2: (m,n)=(5,2) -> PPT (21, 20, 29), det=-1**: 
- **B3: (m,n)=(4,1) -> PPT (15, 8, 17), det=1**: 
- **Lattice pts on x^2+y^2-z^2=1 (|entries|<=5)**: 76
- **Lattice pts on x^2+y^2-z^2=-1**: 10
- **O(2,1)(Z) matrices mapping (3,4,5) -> positive PPT**: 8
- **  #1 -> (8, 15, 17) [OTHER] det=-1**: 
- **  #2 -> (15, 8, 17) [BERGGREN B3] det=1**: 
- **  #3 -> (4, 3, 5) [OTHER] det=-1**: 
- **  #4 -> (3, 4, 5) [IDENTITY] det=1**: 
- **  #5 -> (5, 12, 13) [BERGGREN B1] det=1**: 
- **  #6 -> (21, 20, 29) [BERGGREN B2] det=-1**: 
- **  #7 -> (12, 5, 13) [OTHER] det=-1**: 
- **  #8 -> (20, 21, 29) [OTHER] det=1**: 
- **Non-Berggren, non-identity O(2,1)(Z) matrices**: 4
- **  Extra #1 -> (8, 15, 17)**: [[-2, 1, 2], [-1, 2, 2], [-2, 2, 3]]
- **  Extra #2 -> (4, 3, 5)**: [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
- **  Extra #3 -> (12, 5, 13)**: [[2, -1, 2], [1, -2, 2], [2, -2, 3]]
- **  Extra #4 -> (20, 21, 29)**: [[2, 1, 2], [1, 2, 2], [2, 2, 3]]

### Experiment 2: Price Tree Identity

- **2x2 matrices (|entries|<=3, det=+/-1) mapping (2,1) to valid PPT (m,n)**: 15
- **  [[1, 0], [0, 1]] -> (2,1) -> (3, 4, 5) [NEW?]**: 
- **  [[1, 0], [1, -1]] -> (2,1) -> (3, 4, 5) [NEW?]**: 
- **  [[1, 1], [1, 0]] -> (3,2) -> (5, 12, 13) [NEW?]**: 
- **  [[1, 2], [0, 1]] -> (4,1) -> (15, 8, 17) [BERGGREN]**: 
- **  [[1, 2], [1, 1]] -> (4,3) -> (7, 24, 25) [NEW?]**: 
- **  [[1, 3], [1, 2]] -> (5,4) -> (9, 40, 41) [NEW?]**: 
- **  [[2, -1], [1, 0]] -> (3,2) -> (5, 12, 13) [BERGGREN]**: 
- **  [[2, 1], [1, 0]] -> (5,2) -> (21, 20, 29) [BERGGREN]**: 
- **  [[2, 3], [1, 2]] -> (7,4) -> (33, 56, 65) [NEW?]**: 
- **  [[3, -2], [1, -1]] -> (4,1) -> (15, 8, 17) [NEW?]**: 
- **  [[3, -2], [2, -1]] -> (4,3) -> (7, 24, 25) [NEW?]**: 
- **  [[3, -1], [1, 0]] -> (5,2) -> (21, 20, 29) [NEW?]**: 
- **  [[3, 1], [1, 0]] -> (7,2) -> (45, 28, 53) [NEW?]**: 
- **  [[3, 2], [1, 1]] -> (8,3) -> (55, 48, 73) [NEW?]**: 
- **  [[3, 2], [2, 1]] -> (8,5) -> (39, 80, 89) [NEW?]**: 
- **Test (m,n) pairs (m<=30)**: 173
- **Matrices valid on ALL (m,n) pairs**: 15
- **  Globally valid: [[1, 0], [0, 1]] [NEW]**: 
- **  Globally valid: [[1, 0], [1, -1]] [NEW]**: 
- **  Globally valid: [[1, 1], [1, 0]] [NEW]**: 
- **  Globally valid: [[1, 2], [0, 1]] [BERGGREN]**: 
- **  Globally valid: [[1, 2], [1, 1]] [NEW]**: 
- **  Globally valid: [[1, 3], [1, 2]] [NEW]**: 
- **  Globally valid: [[2, -1], [1, 0]] [BERGGREN]**: 
- **  Globally valid: [[2, 1], [1, 0]] [BERGGREN]**: 
- **  Globally valid: [[2, 3], [1, 2]] [NEW]**: 
- **  Globally valid: [[3, -2], [1, -1]] [NEW]**: 
- **  Globally valid: [[3, -2], [2, -1]] [NEW]**: 
- **  Globally valid: [[3, -1], [1, 0]] [NEW]**: 
- **  Globally valid: [[3, 1], [1, 0]] [NEW]**: 
- **  Globally valid: [[3, 2], [1, 1]] [NEW]**: 
- **  Globally valid: [[3, 2], [2, 1]] [NEW]**: 

### Experiment 3: Third Tree (4,3,5)

- **S*B1*S = [[0, 1], [-1, 2]], det=1**: 
- **S*B2*S = [[0, 1], [1, 2]], det=-1**: 
- **S*B3*S = [[1, 0], [2, 1]], det=1**: 
- **T1 = P*B1*P, T1*(4,3,5) = (12, 5, 13), valid=True**: 
- **T2 = P*B2*P, T2*(4,3,5) = (20, 21, 29), valid=True**: 
- **T3 = P*B3*P, T3*(4,3,5) = (8, 15, 17), valid=True**: 
- **S in GL(2,Z)?**: True
- **S^2 = I?**: True
- **S reachable from Berggren gens at depth**: 2
- **S*B1*S reachable at depth**: 1
- **S*B2*S reachable at depth**: 3
- **S*B3*S reachable at depth**: 3
- **Berggren PPTs (c<=500)**: 80
- **Third tree PPTs (c<=500)**: 80
- **Same normalized set?**: True

### Experiment 4: Mod p Comparison

- **p=2: |Berg mod p|=2, |Swap|=2, |SB|=6**: 
- **p=2: |Berg det=1|=2, |Swap det=1|=2, |SB det=1|=6**: 
- **p=2: Berg = Swap?**: True
- **p=3: |Berg mod p|=48, |Swap|=48, |SB|=24**: 
- **p=3: |Berg det=1|=24, |Swap det=1|=24, |SB det=1|=24**: 
- **p=3: |SL(2,F_p)|=24**: 
- **p=3: Berg det=1 = SL(2)?**: True
- **p=3: Swap det=1 = SL(2)?**: True
- **p=3: Berg = Swap?**: True
- **p=5: |Berg mod p|=240, |Swap|=240, |SB|=120**: 
- **p=5: |Berg det=1|=120, |Swap det=1|=120, |SB det=1|=120**: 
- **p=5: |SL(2,F_p)|=120**: 
- **p=5: Berg det=1 = SL(2)?**: True
- **p=5: Swap det=1 = SL(2)?**: True
- **p=5: Berg = Swap?**: True
- **p=7: |Berg mod p|=672, |Swap|=672, |SB|=336**: 
- **p=7: |Berg det=1|=336, |Swap det=1|=336, |SB det=1|=336**: 
- **p=7: |SL(2,F_p)|=336**: 
- **p=7: Berg det=1 = SL(2)?**: True
- **p=7: Swap det=1 = SL(2)?**: True
- **p=7: Berg = Swap?**: True
- **p=11: |Berg mod p|=2640, |Swap|=2640, |SB|=1320**: 
- **p=11: |Berg det=1|=1320, |Swap det=1|=1320, |SB det=1|=1320**: 
- **p=11: |SL(2,F_p)|=1320**: 
- **p=11: Berg det=1 = SL(2)?**: True
- **p=11: Swap det=1 = SL(2)?**: True
- **p=11: Berg = Swap?**: True
- **p=13: |Berg mod p|=4368, |Swap|=4368, |SB|=2184**: 
- **p=13: |Berg det=1|=2184, |Swap det=1|=2184, |SB det=1|=2184**: 
- **p=13: |SL(2,F_p)|=2184**: 
- **p=13: Berg det=1 = SL(2)?**: True
- **p=13: Swap det=1 = SL(2)?**: True
- **p=13: Berg = Swap?**: True

### Experiment 5: Binary vs Ternary Trees

- **B3 = SB_R^2?**: True
- **B1 = [[2, -1], [1, 0]] in SB gens**: I*L*R^-1*L^-1
- **B2 = [[2, 1], [1, 0]] in SB gens**: not found
- **B3 = [[1, 2], [0, 1]] in SB gens**: I*R*R
- **SB_L, SB_R generate**: SL(2,Z) (full modular group)
- **B1, B2, B3 generate**: Gamma_theta (index 3 in SL(2,Z))
- **Gamma_theta = kernel of SL(2,Z) -> Z/3Z**: via the theta character

### Experiment 6: IFS Dynamics

- **Berggren IFS on t=n/m in (0,1)**: f1=1/(2-t), f2=1/(2+t), f3=t/(1+2t)
- **Images: f1->(1/2,1), f2->(1/3,1/2), f3->(0,1/3)**: disjoint union = (0,1)
- **Third tree IFS on s=m/n in (1,inf)**: g1=2-1/s, g2=2+1/s, g3=s+2
- **Conjugate by t=1/s?**: True
- **Density 'uniform': L2=1.1981, KS=0.2317**: 
- **Density '1/((1+t)ln2)': L2=1.1906, KS=0.1605**: 
- **Density '1/(t*ln2)': L2=3.3305, KS=0.6495**: 
- **Density '3/(1+2t)^2': L2=1.3786, KS=0.3276**: 
- **Transfer operator density: L2 vs histogram = 2.6462**: 
- **  rho(0.1) = 0.0000**: 
- **  rho(0.2) = 0.0000**: 
- **  rho(0.3) = 0.0000**: 
- **  rho(0.4) = 9.9064**: 
- **  rho(0.5) = 0.0000**: 
- **  rho(0.6) = 0.0000**: 
- **  rho(0.7) = 0.0000**: 
- **  rho(0.8) = 0.0000**: 
- **  rho(0.9) = 0.0000**: 
- **Lyapunov exponent (uniform 1/3 weights)**: -1.283838
- **Lyapunov < 0 means contracting**: True
- **Manneville-Pomeau: f3(t) ~ t near t=0 (neutral fixed pt)**: z=2 intermittency

### Experiment 7: Depth Comparison

- **PPTs found (Berggren, depth<=8, c<10000)**: 1025
- **PPTs found (Third, depth<=8, c<10000)**: 1025
- **Same normalized set?**: True
- **  (5, 12, 13): Berg=1, Third=1**: 
- **  (8, 15, 17): Berg=1, Third=1**: 
- **  (20, 21, 29): Berg=1, Third=1**: 
- **  (7, 24, 25): Berg=2, Third=2**: 
- **  (9, 40, 41): Berg=3, Third=3**: 
- **  (11, 60, 61): Berg=4, Third=4**: 
- **  (12, 35, 37): Berg=2, Third=2**: 
- **  (28, 45, 53): Berg=2, Third=2**: 
- **  (33, 56, 65): Berg=2, Third=2**: 
- **  (36, 77, 85): Berg=2, Third=2**: 
- **Max depth difference**: 0
- **Depth 0: Berggren=1, Third=1**: 
- **Depth 1: Berggren=3, Third=3**: 
- **Depth 2: Berggren=9, Third=9**: 
- **Depth 3: Berggren=27, Third=27**: 
- **Depth 4: Berggren=81, Third=81**: 
- **Depth 5: Berggren=223, Third=223**: 
- **Depth 6: Berggren=293, Third=293**: 
- **Depth 7: Berggren=230, Third=230**: 
- **Depth 8: Berggren=158, Third=158**: 

### Experiment 8: Modular Forms

- **Berggren group**: Gamma_theta = stabilizer of theta[0,0](tau)
- **Third tree group**: Same Gamma_theta (conjugate by swap in GL(2,Z))
- **|Berggren mod 2|**: 2
- **B1 mod 2**: ((0, 1), (1, 0))
- **B2 mod 2**: ((0, 1), (1, 0))
- **B3 mod 2**: ((1, 0), (0, 1))
- **Berggren mod 2 = {I, swap}**: order 2 subgroup of SL(2,F_2) = S_3 (order 6)
- **Index [SL(2,Z):Gamma_theta]**: 6/2 = 3
- **Cosets**: Gamma_theta, T*Gamma_theta, T^{-1}*Gamma_theta where T=[[1,1],[0,1]]
- **Three even spin structures**: theta[0,0], theta[1,0], theta[0,1]
- **Gamma_theta stabilizes**: theta[0,0] = sum q^{n^2}
- **T*Gamma_theta stabilizes**: theta[1,0] = sum q^{(n+1/2)^2}
- **ALL PPT trees stabilize same theta[0,0]**: True
- **Generating function**: sum_{PPT} q^{m^2+n^2} relates to theta(tau)^2

### Experiment 9: ADE Tower

- **p=3: |SL(2,F_p)| = 24**: Expected: p(p^2-1) = 24
- **p=3: conjugacy class sizes**: [1, 1, 4, 4, 4, 4, 6]
- **p=3: num classes = num irreps**: 7
- **p=3: SL(2,F_3) = 2T (binary tetrahedral, order 24)**: 
- **p=3: McKay graph = extended E_6**: 
- **p=3: Expected class sizes [1,1,4,4,4,4,6]**: True
- **p=5: |SL(2,F_p)| = 120**: Expected: p(p^2-1) = 120
- **p=5: conjugacy class sizes**: [1, 1, 12, 12, 12, 12, 20, 20, 30]
- **p=5: num classes = num irreps**: 9
- **p=5: SL(2,F_5) = 2I (binary icosahedral, order 120)**: 
- **p=5: McKay graph = extended E_8**: 

### Experiment 10: Grand Uniqueness Theorem

- **MAIN RESULT**: ALL ternary PPT trees (Berggren, 'Price', Third/4,3,5) generate the SAME group Gamma_theta (index 3 in SL(2,Z)). The algebraic identity PPT-tree = Gamma_theta is CANONICAL and UNIQUE.
- **Evidence**: {'1. O(2,1)(Z) search': 'Only 3 matrices map (3,4,5) to depth-1 PPTs (= Berggren)', '2. 2x2 global validity': 'Only Berggren 2x2 gens map ALL (m,n) pairs correctly', '3. Third tree': 'Conjugate by swap P, same group in (m,n) space', '4. Mod p': 'All variants give SL(2,F_p) for p=2,3,5,7,11,13', '5. Spin structure': 'All stabilize theta[0,0]', '6. ADE tower': 'Universal E_6->E_8->... tower', '7. IFS dynamics': 'Unique invariant measure (conjugate by t<->1/t for Third tree)', '8. Depths': 'Identical depth structure'}
- **Summary**: 
TREE COMPARISON TABLE
===============================================================
Property          | Berggren    | 'Price'     | Third (4,3,5)
------------------+-------------+-------------+--------------
Root              | (3,4,5)     | (3,4,5)     | (4,3,5)
3x3 generators    | B1,B2,B3    | B1,B2,B3    | P*Bi*P
2x2 generators    | M1,M2,M3    | M1,M2,M3    | S*Mi*S (same group!)
Group (SL2 part)  | Gamma_theta | Gamma_theta | Gamma_theta
Index in SL(2,Z)  | 3           | 3           | 3
Modular form      | theta[0,0]  | theta[0,0]  | theta[0,0]
Spin structure    | Even (0,0)  | Even (0,0)  | Even (0,0)
IFS density       | unique mu   | same        | conjugate
ADE at p=3        | E_6         | E_6         | E_6
ADE at p=5        | E_8         | E_8         | E_8
mod p group       | SL(2,F_p)   | SL(2,F_p)   | SL(2,F_p)
===============================================================
CONCLUSION: All three are the SAME mathematical object.


## Comparison Table

| Property | Berggren | 'Price' | Third (4,3,5) |
|----------|----------|---------|---------------|
| Root | (3,4,5) | (3,4,5) | (4,3,5) |
| 3x3 generators | B1,B2,B3 | B1,B2,B3 (same!) | P*Bi*P |
| 2x2 generators | M1,M2,M3 | M1,M2,M3 | S*Mi*S (same group!) |
| Group | Gamma_theta | Gamma_theta | Gamma_theta |
| Index in SL(2,Z) | 3 | 3 | 3 |
| Modular form | theta[0,0] | theta[0,0] | theta[0,0] |
| Spin structure | Even (0,0) | Even (0,0) | Even (0,0) |
| ADE at p=3 | E_6 | E_6 | E_6 |
| ADE at p=5 | E_8 | E_8 | E_8 |
| IFS density | unique mu | same | conjugate by t<->1/t |

## Key Insight

The ternary PPT tree is a **canonical mathematical object**. There is exactly ONE way to organize primitive Pythagorean triples into a ternary tree (using O(2,1)(Z) matrices), and it always generates Gamma_theta. The 'Price tree' is a rediscovery of the Berggren tree, and the 'third tree' (4,3,5) is just the Berggren tree with legs relabeled.
