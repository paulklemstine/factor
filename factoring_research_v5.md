# Factoring Research v5: 20 Radically Different Moonshot Paradigms

**Started**: 2026-03-15 (session 5)
**Prior**: 210+ math fields exhausted (all converge to L[1/3]). v4 focused on engineering. This round: WILDLY different computational paradigms.
**Strategy**: Test whether non-standard computation models (analog, biological, swarm, topological) can break the discrete-algorithm barrier.

## Results Summary

| # | Paradigm | Factored | Max Bits | Avg Time | Verdict |
|---|----------|----------|----------|----------|---------|
| 1 | Analog ODE | 0/5 | 0b | 0.003s | DEAD -- gradient descent on continuous relaxation gets stuck in local minima. The xy=N surface has saddle points everywhere. |
| 2 | DNA Binding | 3/5 | 24b | 0.001s | DEAD -- "hybridization" is just random trial division with a fitness heuristic. No structural advantage. |
| 3 | Optical Interference | 3/5 | 24b | 0.001s | DEAD -- DFT trick is mathematically equivalent to trial division (geometric series = 0 unless d divides N). Fancy wrapper, same O(sqrt(N)). |
| 4 | Thermodynamic Annealing | 1/5 | 9b | 0.004s | DEAD -- energy landscape E=(N mod x)^2 is highly non-convex with no gradient signal. SA random walk is worse than systematic search. |
| 5 | Community Detection | 0/5 | 0b | 0.007s | DEAD -- factor base co-occurrence graph shows NO separation between p-associated and q-associated primes. Communities overlap completely. |
| 6 | Genetic Algorithm | 1/5 | 9b | 0.014s | DEAD -- crossover on bit strings of trial divisors is destructive. A single bit flip changes the divisor wildly. No building-block hypothesis holds. |
| 7 | Ant Colony | 2/5 | 17b | 0.012s | DEAD -- pheromone accumulation on bit positions has same problem as GA: bit independence assumption is wrong for factors. |
| 8 | Reservoir Computing | 0/5 | 0b | 0.030s | DEAD -- reservoir "predicts" smoothness at baseline accuracy (99%+ says "not smooth" always). Smooth numbers are too rare for the reservoir to learn anything. |
| 9 | Braid Period Finding | 1/5 | 9b | 0.010s | WEAK -- order-finding in Z/NZ does work (it's Shor's algorithm classically). But classical order-finding is O(N) worst case. No speedup without quantum. |
| 10 | Spiking Neural Net | 3/5 | 24b | 0.0004s | DEAD -- "spike timing = N mod d" is literally trial division. The biological metaphor adds nothing. |
| 11 | Rule 30 Rho | **4/5** | **31b** | 0.117s | INTERESTING -- Rule 30 CA as a rho walk generator works! Factored up to 31 bits. But it's just Pollard rho with a different pseudorandom function. Same O(N^{1/4}) complexity. No asymptotic improvement. |
| 12 | Fibonacci Sieve | **4/5** | **31b** | 0.008s | INTERESTING -- Fibonacci-spaced sieve points via golden ratio hit factors quickly for small N. But this is trial division along a quasi-random sequence. Three-distance theorem gives good coverage but same O(sqrt(N)). |
| 13 | Constellation Sieve | 0/5 | 0b | 0.002s | DEAD -- twin primes give FEWER smooth relations than the full prime set (15 vs 58 for 9b). Restricting factor base to constellations hurts, never helps. Primes are primes. |
| 14 | Collatz mod N | 2/5 | 17b | 0.0002s | WEAK -- Collatz-like maps on Z/NZ do produce GCD hits, but only for small N where cycles are short. For large N, cycle lengths grow with N. No advantage over rho. |
| 15 | DLog Factoring | 2/5 | 17b | 0.001s | KNOWN -- factoring-to-DLP reduction is well-known. Classical DLP in Z/NZ requires knowing phi(N), which requires factoring N. Circular. Only works with quantum period-finding (= Shor). |
| 16 | Isogeny Walk | 0/5 | 0b | 0.005s | DEAD -- simplified isogeny walk finds no structure. Real isogeny graphs over Z/NZ are ill-defined (need Z/pZ). Would need to factor N first to walk the isogeny graph, circular. |
| 17 | Hyperelliptic Jacobian | **3/5** | **31b** | 0.0004s | INTERESTING -- Euler criterion trick gcd(r^{(N-1)/2} +/- 1, N) finds factors! This is essentially a variant of ECM/Solovay-Strassen. Known technique, but confirms higher-genus curves could extend ECM-like methods. |
| 18 | Circuit SAT | **4/5** | **31b** | 0.0002s | DEAD -- reduced to trial division with LSB pruning (skip evens). The SAT encoding is sound but solving it classically is NP-hard. No unit propagation helps on multiplication circuits. |
| 19 | Tropical Factoring | 2/5 | 17b | 0.0002s | DEAD -- tropical valuations v_p(N) only reveal SMALL prime factors (literal trial division). For RSA semiprimes with large factors, all small-prime valuations are 0. No information. |
| 20 | ECC Decoding | 1/5 | 9b | 0.0005s | DEAD -- encoding N as a codeword provides no error-correction structure. Factors are not "nearby" in any code metric. The syndrome approach reduces to trial division by small primes. |

## Classification

### Tier 1: Genuinely Interesting (worth deeper investigation)
- **#11 Rule 30 Rho**: A new pseudorandom function for Pollard rho. While asymptotically the same, the mixing properties of Rule 30 (proven CSPRNG-like by Wolfram) might give better constants. Could test on 50-60 bit semiprimes vs standard rho.
- **#12 Fibonacci Sieve**: Golden-ratio spacing gives provably optimal equidistribution (3-distance theorem). Could improve the constant factor in sieve initialization or polynomial selection.
- **#17 Hyperelliptic Jacobian**: Euler criterion variant is a legitimate factoring technique. Higher-genus curves (genus 2-3) have larger group orders (~N^g), potentially fewer curves needed than ECM.

### Tier 2: Known Reduction, No New Insight
- **#9 Braid Period Finding** = Shor's algorithm without a quantum computer
- **#15 DLog Factoring** = factoring <-> DLP equivalence (well-known)
- **#18 Circuit SAT** = factoring -> SAT (well-known, basis of SAT-based factoring papers)

### Tier 3: Dead on Arrival (fundamental barriers)
- **#1 Analog ODE**: Continuous relaxation of xy=N has no useful gradient information
- **#2-3 DNA/Optical**: Fancy metaphors for trial division
- **#4 Thermodynamic**: Energy landscape has no gradient signal toward factors
- **#5 Community Detection**: Factor base graph shows no community structure aligned with factors
- **#6-7 GA/Ant Colony**: Bit-level crossover/pheromone is destructive for integer structure
- **#8 Reservoir Computing**: Smoothness is too rare to learn
- **#10 Spiking NN**: Literal trial division in disguise
- **#13 Constellation Sieve**: Restricting FB to twin primes hurts smoothness
- **#14 Collatz mod N**: Cycle lengths grow with N, no advantage
- **#16 Isogeny Walk**: Isogeny graph over Z/NZ is ill-defined
- **#19 Tropical**: Valuations only find small prime factors
- **#20 ECC Decoding**: No code structure to exploit

## Key Insight

**Every "alternative computation" paradigm, when reduced to its mathematical core, is one of:**
1. Trial division (testing N mod d for sequential/random d)
2. Pollard rho (pseudorandom walk with cycle detection)
3. Order/period finding (requires quantum for speedup)
4. Smooth number sieving (the L[1/3] family)

The computation model (analog, biological, swarm, neural) is irrelevant -- what matters is the MATHEMATICAL OPERATION being computed. No amount of metaphor-changing escapes the underlying complexity class.

**The only paths to faster factoring remain:**
- Better constants in L[1/3] algorithms (engineering, not theory)
- Quantum period-finding (Shor's algorithm)
- A genuinely new mathematical structure (not found in 210+ fields)

## Files
- `/home/raver1975/factor/v5_moonshots.py` -- all 20 experiments (590 lines)
- This file -- results and analysis

---

## Session 5 Running Status

### Implementation Agents (in worktrees)
- GNFS coprimality + threshold + overflow fixes — in progress
- SIQS C trial division integration — in progress

### Research Agents (completed)
- 20 moonshot paradigms: ALL reduce to known families (Rule 30 rho, Fibonacci sieve interesting but same complexity)
- P vs NP phase 3: 5 approaches analyzed, Dickman barrier and oracle separation are genuine insights
- Breakthrough explorer: investigating B3 lattice 8.2x, batch-GCD 6-9x, cross-poly LP 3.3x

### Meta-conclusion (230+ fields total)
**The computation model is irrelevant. All classical factoring paradigms map to:**
1. Trial division: O(sqrt(N))
2. Birthday/rho: O(N^{1/4})  
3. Group order/period: L[1/2] (p-1, p+1, ECM)
4. Congruence of squares: L[1/2] (QS) or L[1/3] (GNFS)
5. Quantum period-finding: O(poly(log N)) (Shor)

No paradigm shift escapes without quantum resources or new mathematics.
The only path forward is engineering within L[1/3].

### Key Breakthrough Hints Under Investigation
1. B3 lattice sieve: 8.2x hit rate
2. Bernstein batch-GCD: 6-9x smoothness testing  
3. Cross-poly LP resonance: 3.3x yield
4. disc = 16·N·n₀⁴ fast switching identity
5. B3-MPQS extraction regression (needs fix)

Combined potential: ~200x if all verified and integrated.

### Breakthrough Verification — COMPLETE

| Claim | Result |
|-------|--------|
| B3 lattice sieve 8.2x | 2.3x verified (not 8.2x) |
| Bernstein batch-GCD 6-9x | Not implemented anywhere |
| **Cross-poly LP resonance 3.3x** | **CONFIRMED at 3.298x** |
| **disc = 16·N·n₀⁴ identity** | **CONFIRMED 100% (19701/19701)** |
| B3-MPQS extraction bug | No bug — CFRAC engine works correctly |

**Actionable**: The LP resonance (3.3x) should be integrated into SIQS/B3-MPQS.
The discriminant identity enables fast polynomial switching.
Combined: ~7.5x improvement on relation generation if both exploited.

Batch-GCD needs to be implemented from scratch (Bernstein's product tree).
B3 lattice sieve gives 2.3x (not 8.2x) — worth having but not transformative.
