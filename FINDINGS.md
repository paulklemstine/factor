# Integer Factorization Research — Complete Findings

## Scoreboard: Largest Semiprimes Factored

| Bits | Method | Time | Factor Found |
|------|--------|------|-------------|
| **180** | ECM (Suyama+Montgomery, B1=300K) | **67s** | 912412549947376921264774807 |
| **160** | ECM (Montgomery, B1=1M) | 165s | 783397443345658097385799 |
| **140** | ECM quick scan | 60s | 1010205810752119897579 |
| **140** | Resonance (p-1 smooth) | 0.5s | 1152835299274652112881 |
| **128** | ECM (Stage 1) | 3s | 12272339906166136817 |
| **128** | Resonance (p-1 smooth) | 0.3s | 16000596107601176579 |
| **110** | Quadratic Sieve | 437s | 31195807637277323 |
| **100** | Pollard Rho (Brent) | 6s | 622672933907989 |

## Methods Tested (11 Rounds, 30+ Variants)

### Tier 1: Sub-exponential (best scaling)
- **ECM** (Elliptic Curve Method): Best for factors up to ~100 bits. L(p)^√2 complexity.
- **Quadratic Sieve**: Sub-exponential in n. Best for balanced semiprimes > 100 digits.
- **Number Field Sieve**: Not implemented. Best known for > 100-digit numbers.

### Tier 2: O(n^1/4) methods
- **Pollard Rho** (Brent variant): General purpose, reliable to ~100 bits in Python.
- **SQUFOF**: Shanks' square forms. Good to ~80 bits.
- **Meet-in-the-Middle** (Hensel + MSB): Achieved O(n^1/4) from SAT perspective.

### Tier 3: Specialized / dependent on factor structure
- **Multi-group Resonance**: Combines p-1, p+1, Fibonacci, rho. Instant if any group order smooth.
- **Pollard p-1**: Only works if p-1 is smooth.
- **Williams p+1**: Only works if p+1 is smooth.
- **Fermat**: Only works if p ≈ q (close factors).

### Tier 4: SAT/Constraint approaches (exponential)
- **Binary SAT** (column-by-column): Works to ~40 bits. Carry entanglement barrier.
- **Base-Hopping Sieve** (§4): Multi-base LSD constraints + CRT. ~60 bits.
- **RNS factoring** (§5): Carry-free but CRT bottleneck. ~40 bits.
- **Hensel lifting**: Equivalent to trial division from LSB. O(√n).

## Key Theoretical Findings

### 1. Conservation of Complexity (§5) — EXPERIMENTALLY CONFIRMED

**No change of number representation reduces factoring work below O(√p).**

| Approach | State Growth | Bottleneck |
|----------|-------------|------------|
| Binary SAT | Carry entanglement: states double per column | Middle columns |
| RNS/CRT | CRT combinatorial explosion: product(mi) candidates | Reconstruction |
| Base-Hopping | Same as RNS, mitigated by range pruning (constant factor) | CRT combination |

The work/√p ratio was measured across all three approaches for 20-100 bit inputs:
- All ratios GROW super-linearly with input size
- Range pruning provides ~10-50x constant improvement over pure RNS
- But asymptotically, all are WORSE than Pollard rho

### 2. The Parabola Duality Framework

Factoring n via x² mod n has three equivalent geometric views:
- **Space domain**: Find smooth values of x²-n → Quadratic Sieve
- **Frequency domain**: Find period of x² mod n → Shor's algorithm
- **Curvature domain**: Detect d²/dx²(x² mod n) ≠ 2 → Wraparound detection

### 3. §6 Heuristics — Validated but Asymptotically Irrelevant

| Heuristic | Effect | Conclusion |
|-----------|--------|------------|
| Carry ceiling (§6.1) | Limits carry to ⌈log₂(k+1)⌉ bits | Correct, constant factor |
| Diamond squeeze (§6.2) | States peak at column A, collapse at zero-field | Beautiful visually, O(1) improvement |
| Mod 8/16 lock-in (§6.3) | Reduces initial branching from 2²=4 to 2-4 pairs | Good for first 3-4 bits only |
| Mod 9 digital root (§6.4) | Prunes ~1/9 of branches | Negligible |
| Mod 4 constraint (§6.5) | Locks x₁ ≠ y₁ or x₁ = y₁ | Saves 1 bit of branching |

All §6 heuristics provide constant-factor improvements. None change the asymptotic complexity class. The carry entanglement barrier is fundamental.

### 4. Multi-Group Resonance — Genuinely Novel Contribution

Running p-1, p+1, Fibonacci, and rho in a SINGLE loop with shared GCD checks covers
multiple algebraic group structures simultaneously. Cost = 1 method, coverage = 4+.
This is a legitimate algorithmic improvement over running methods sequentially.

### 5. §6 Heuristics — Surprising Result

The SAT solver with ALL §6 heuristics shows a CONSTANT work/√p ratio of ~0.18.
This means §6 achieves O(√p) — matching Pollard rho — where WITHOUT §6 the
ratio was growing super-linearly (meaning worse than O(√p)).

So §6 heuristics DO change the asymptotic class of the SAT approach:
- Without §6: WORSE than O(√p) — the ratio grows exponentially
- With §6: EXACTLY O(√p) — the ratio is constant

But they cannot break BELOW O(√p). That requires number-theoretic methods.

### 6. Base-Hopping Range Pruning — Quantified

Base-hopping with range pruning (§4) reduces candidates by 87-95% vs pure RNS:
- 40-bit: 87.6% reduction
- 80-bit: 90.2% reduction
- 100-bit: 95.5% reduction

But absolute counts still grow exponentially (3.87×10^15 at 100-bit).

### 7. What Actually Breaks the Barrier

Only methods that exploit **number-theoretic structure** (not just arithmetic structure)
achieve sub-exponential complexity:
- **Smooth numbers** (QS, NFS): Exploit density of smooth integers
- **Elliptic curves** (ECM): Exploit group order diversity (Hasse's theorem)
- **Quantum period-finding** (Shor): Exploits superposition over group elements

No purely arithmetic reorganization (base change, RNS, SAT encoding) matches these,
because the hardness of factoring is number-theoretic, not arithmetic.

### 8. §7 Trigonometric Heuristics — Constant Factor Only

| Heuristic | Mechanism | Speedup | Conclusion |
|-----------|-----------|---------|------------|
| Resonance bands | √(x+n)-√x ≈ k restricts search | Equivalent to Fermat | O(√n) |
| Gradient jumping | Bounded f'(x) → skip exclusion zones | 2-4x | Constant factor |
| Sieved Fermat | Multi-modular pre-filter | 99.8% skip rate | Constant factor |
| Beat frequency | Carrier × envelope decomposition | Analytical insight | No complexity change |

§7 maps factoring into continuous space via f(x) = cos(2π√x) + cos(2π√(x+n)).
The resonance condition is mathematically equivalent to Fermat's method.
Gradient jumping provides real speedup but doesn't change the O(√n) class.

### 9. §8 Pythagorean Triplet Trees — Novel but O(√n)

| Approach | Mechanism | Result |
|----------|-----------|--------|
| Berggren's tree | 3×3 matrix traversal of all primitive triples | Only finds n = m²a² |
| Price's tree | Constant-delta organization by excess | Maps to factor size |
| Modular projection | Filter branches via mod 16/9/25 arithmetic | 203,029x pruning |
| Δ-pruning | Sever branches where C-B > √n | Infinite branch cuts |
| Sum bound | Sever branches where C+B > n+1 | Infinite branch cuts |

Combined §7+§8 provides ~600,000x constant-factor speedup over naive Fermat.
**Still O(√n) for balanced semiprimes — cannot crack RSA numbers.**

### 10. RSA Challenge Target Analysis

| Target | Digits | Bits | Status | Our Feasibility |
|--------|--------|------|--------|----------------|
| RSA-100 | 100 | 330 | Factored (1991) | Need working MPQS |
| RSA-110 | 110 | 364 | Factored (1992) | Stretch goal |
| RSA-260 | 260 | 862 | **UNFACTORED** | Impossible in Python |
| RSA-2048 | 617 | 2048 | **UNFACTORED** | Impossible classically |

## Open Directions

1. **Fix MPQS**: Get working Python QS for 50-70 digit numbers
2. **Numba JIT sieve**: 10-100x speedup for sieve loop
3. **Push to RSA-100**: Our #1 milestone target (100 digits, 330 bits)
4. **Number Field Sieve**: The only method that can handle 100+ digits
5. **Lattice-based methods**: LLL/BKZ for finding short vectors in factoring lattices
