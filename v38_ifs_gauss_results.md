# v38: Berggren-Gauss IFS — Full Analysis
# Date: 2026-03-17

## MAJOR DISCOVERY: Invariant Density is 1/(t(1-t)), NOT Cauchy

The Berggren expanding map T has invariant density **h(t) = C/(t(1-t))**.
This is an **infinite measure** (non-integrable at 0 and 1), making T an
**intermittent dynamical system** (Manneville-Pomeau type).

### Algebraic Proof

The Perron-Frobenius equation h(x) = Σ h(fi(x))·|fi'(x)| gives:

```
h(f1)·|f1'| = (2-x)²/(1-x) · 1/(2-x)² = 1/(1-x)
h(f2)·|f2'| = (2+x)²/(1+x) · 1/(2+x)² = 1/(1+x)
h(f3)·|f3'| = (1+2x)²/(x(1+x)) · 1/(1+2x)² = 1/(x(1+x)) = 1/x - 1/(1+x)

Sum = 1/(1-x) + 1/(1+x) + 1/x - 1/(1+x)
    = 1/(1-x) + 1/x
    = 1/(x(1-x)) = h(x)   QED
```

Numerical verification: ratio = 1.000000 at x = 0.1, 0.3, 0.5, 0.7, 0.9.
Cauchy density (4/pi)/(1+t²) fails the PF equation (ratios: 1.10, 0.94, 0.85, 0.97, 1.22).

## Experiment 1: Transfer Operator & Spectral Gap

Transfer operator L (Ulam, 300 bins):
- lambda_1 = 1.0024 (approx 1 as expected)
- lambda_2 = 0.9955
- Spectral ratio lambda_2/lambda_1 = 0.9932
- Gauss map: lambda_2/lambda_1 = 0.3036 (Wirsing constant)

**T138: The Berggren-Gauss map has spectral ratio approx 0.99, far larger than Gauss's 0.30.**
This is because of neutral fixed points at 0 and 1 (intermittency).
The essential spectrum touches 1, so the spectral gap -> 0 as resolution -> infinity.
Mixing is orders of magnitude slower than the Gauss map.

## Experiment 2: Thermodynamic Formalism P(beta)

| beta | P(beta)  | Theory            |
|------|----------|-------------------|
| 0.0  | 1.0986   | log 3 = 1.0986    |
| 0.5  | 0.4837   |                   |
| 1.0  | -0.0487  | approx 0 (Lyap)   |
| 1.5  | -0.4297  |                   |
| 2.0  | -0.6815  |                   |

- P(0) = log 3 (topological entropy of 3-shift)
- Pressure zero at beta_0 approx 0.94, confirming Hausdorff dim approx 1 (full interval)
- P(1) approx -0.05 (slightly negative because infinite invariant measure)

## Experiment 3: Dynamical Zeta Function

Individual fixed points:
- f1: t* = 0.998 (near neutral point 1), |f1'| = 0.996
- f2: t* = 0.414 (= sqrt(2)-1), |f2'| = 0.172
- f3: t* = 0.001 (near neutral point 0), |f3'| = 0.996

Z_1 = 2.164 (vs 3 for unweighted). Z_n/3^n decays geometrically.
Zeta function pole at z approx 1/Z_1 = 0.462 (vs 1/3 for standard 3-shift).

**T139: The dynamical zeta function zeta(z) has pole at z approx 0.46, shifted from 1/3
due to the near-identity contractivities at the neutral fixed points.**

## Experiment 4: Connection to Continued Fractions

### Branch-by-branch comparison with Gauss map G(x) = {1/x}

| Region     | T(x)        | G(x)      | Relationship     |
|------------|-------------|-----------|------------------|
| (1/2, 1)   | 2 - 1/x    | 1/x - 1  | T_1 = 1 - G     |
| [1/3, 1/2) | 1/x - 2    | 1/x - 2  | T_2 = G (SAME!)  |
| (0, 1/3)   | x/(1-2x)   | 1/x - d  | T_3 != G         |

**T140: The Berggren-Gauss map T uses the SAME partition as coarsened CF ({1},{2},{>=3})
but DIFFERENT maps on branches 1 and 3:**
- Branch 1: T_1 = 1 - G (reflection of Gauss)
- Branch 2: T_2 = G (identical to Gauss for CF digit 2)
- Branch 3: T_3 = x/(1-2x) (new Mobius transform, merges CF digits >=3)

The reflection T_1(1) = 1 creates the neutral fixed point at x=1.
The branch 3 map T_3(0) = 0 creates the neutral fixed point at x=0.

### Berggren addresses vs CF for small PPTs

| Address | (m,n) | t=n/m   | CF(t)       | T->root |
|---------|-------|---------|-------------|---------|
| 1       | (3,2) | 0.6667  | [1, 2]      | 12      |
| 2       | (5,2) | 0.4000  | [2, 2]      | 22      |
| 3       | (4,1) | 0.2500  | [4]         | 32      |
| 11      | (4,3) | 0.7500  | [1, 3]      | 111     |
| 33      | (6,1) | 0.1667  | [6]         | 332     |
| 333     | (8,1) | 0.1250  | [8]         | 3332    |

Note: Berggren address read backwards = path from root; T-iteration reads leaf->root.

## Experiment 5: Diophantine Approximation

Greedy Berggren vs CF convergents of tan(theta/2) for 50 random PPT angles:
- Berggren: 0 wins, CF: 50 wins

**T141: CF convergents exploit the full infinite-digit structure and win
overwhelmingly for angle approximation. The 3-branch Berggren coarsening
loses too much information for Diophantine purposes.**

## Experiment 6: Natural Extension

The natural extension (t,s) -> (T(t), f_{branch}(s)) collapses because
of the neutral fixed points: orbits get trapped near (0,0) or (1,1).
This is inherent to the infinite-measure dynamics -- the natural extension
also has an infinite invariant measure on [0,1]^2.

**T142: The natural extension of the Berggren-Gauss map has an infinite
invariant measure, consistent with the 1/(t(1-t)) density on each factor.**

## Experiment 7: Coding and Entropy

Full shift check: IFS tiles (0,1) without gaps. No forbidden words.

Empirical symbol frequencies (from T orbit, 2M iterates):
- B1: 0.347 (trapped near 1 -> emits many B1 symbols)
- B2: 0.020 (rare -- only narrow band [1/3, 1/2))
- B3: 0.633 (trapped near 0 -> emits many B3 symbols)

Theoretical (Cauchy): B1=0.41, B2=0.18, B3=0.41 -- does NOT match orbit.
This confirms Cauchy is NOT the dynamical invariant measure.

Under the true invariant h(t)=1/(t(1-t)) [infinite measure], the
symbol "probabilities" are not well-defined (infinite total mass).
Instead, the relative frequencies depend on the starting point and
observation time due to intermittency.

Lyapunov exponent: lambda approx 0 (near zero due to long laminar phases).
Shannon entropy H_1(Cauchy) = 1.50 bits, h_top = log_2(3) = 1.58 bits.

**T143: The entropy structure reflects intermittency. The Lyapunov exponent
is near zero because orbits spend long stretches near the neutral fixed
points where |T'| approx 1. This is the hallmark of infinite-measure dynamics.**

## Experiment 8: Arithmetic Coding Compression

Using Cauchy-weighted random branching (the natural tree walk):
- B1: 0.415, B2: 0.178, B3: 0.407
- Shannon entropy: 1.50 bits/symbol
- Uniform (log_2(3)): 1.58 bits/symbol
- **Compression: 5.5% vs uniform (Shannon bound)**

**T144: Arithmetic coding on Berggren addresses (Cauchy-weighted walk)
achieves 5.5% compression. This is modest because the distribution
B1:41%/B2:18%/B3:41% is nearly symmetric.**

======================================================================
## SUMMARY OF THEOREMS

### T138: Spectral Gap and Intermittency
The Berggren-Gauss map has neutral (indifferent) fixed points at x=0 and x=1.
T_1'(1) = 1, T_3'(0) = 1 (quadratic tangency: T_1(1-e) approx 1-e^2).
This creates Manneville-Pomeau intermittency (exponent alpha=2).
Spectral ratio lambda_2/lambda_1 approx 0.993 (vs Gauss map 0.304).

### T139: Dynamical Zeta Function
Z_1 = 2.164. Zeta pole at z approx 0.462 (shifted from 1/3 by neutral points).
Z_n/3^n -> 0 geometrically (neutral-point orbits dominate Z_n).

### T140: Twisted Gauss Map (EXACT CHARACTERIZATION)
Same partition as coarsened CF ({1},{2},{>=3}), but different maps:
  T_1 = 1 - G (reflected Gauss), T_2 = G (identical), T_3 = x/(1-2x) (new).
Branch 2 is the ONLY shared branch with the Gauss CF map.

### T141: Diophantine Approximation
CF convergents dominate Berggren greedy for angle approximation (50/50 wins).
The 3-symbol coarsening loses critical Diophantine information.

### T142: Natural Extension
Has infinite invariant measure, consistent with h(t) = 1/(t(1-t)) density.

### T143: Entropy and Lyapunov
Lyapunov exponent approx 0 due to intermittent trapping at neutral points.
True measure entropy undefined (infinite measure system).
h_top = log_2(3) = 1.58 bits (topological, well-defined).

### T144: Compression via Berggren Addresses
5.5% compression (Shannon bound for Cauchy-weighted branching).

## MASTER THEOREM: Invariant Density (NEW DISCOVERY)

**The invariant density of the Berggren-Gauss expanding map T is
h(t) = C/(t(1-t)), NOT the Cauchy distribution.**

Proved algebraically via Perron-Frobenius:
h(f_1)|f_1'| + h(f_2)|f_2'| + h(f_3)|f_3'| = 1/(1-x) + 1/(1+x) + 1/x - 1/(1+x) = 1/(x(1-x)).

This is an INFINITE (sigma-finite) measure -- integral_0^1 dt/(t(1-t)) diverges.
This confirms the Berggren-Gauss map is an **intermittent dynamical system**
(Manneville-Pomeau type with quadratic neutral fixed points at 0 and 1).

The previously claimed Cauchy measure applies to the **random walk** on the
Berggren tree (equal 1/3 probability at each branch), not to the deterministic
dynamics of the expanding map T.

## KEY INSIGHT: Berggren = Intermittent Twisted Gauss

The Berggren tree generates a Mobius IFS whose expanding map T is:
1. In the same algebraic family as the Gauss CF map
2. Uses the same partition of (0,1) as coarsened CF
3. BUT has reflected/merged branch maps creating neutral fixed points
4. Making it an INTERMITTENT system with INFINITE invariant measure
5. The Cauchy connection is to the random walk, not the dynamics

This is the mathematical analog of: the Berggren tree is to the Stern-Brocot
tree as the Manneville-Pomeau map is to the doubling map -- same topology,
but fundamentally different ergodic properties.
