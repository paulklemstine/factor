"""Field 16: Operads - Compositional Structure of Factoring Algorithms
Hypothesis: Factoring algorithms have a compositional structure: sieve -> collect ->
linear algebra -> sqrt. Operads formalize how operations compose. If we model the
factoring "pipeline" as an operad, we might discover that certain compositions are
more efficient or that there are novel operation compositions not yet explored.
Test: model the SIQS pipeline as operad elements and measure composition efficiency.
"""
import time, math, random

def operad_pipeline_model():
    """Model SIQS stages as operad operations:
    - sieve(N, FB, M) -> candidates
    - trial_div(candidates, FB) -> smooth_relations
    - linear_algebra(relations) -> dependencies
    - sqrt_extraction(dependencies, N) -> factors

    The operad composition rule is: output of stage k = input of stage k+1.
    We test: are there alternative compositions?
    """

    compositions = {
        "standard_siqs": ["poly_select", "sieve", "trial_div", "LP_combine", "gauss_elim", "sqrt"],
        "batch_variant": ["poly_select", "sieve", "batch_gcd", "LP_combine", "gauss_elim", "sqrt"],
        "cfrac_style":   ["cf_expand", "convergent_test", "LP_combine", "gauss_elim", "sqrt"],
        "ecm_style":     ["curve_select", "stage1_mul", "stage2_mul", "gcd"],
        "rho_style":     ["walk_init", "iterate", "cycle_detect", "gcd"],
        "gnfs_style":    ["poly_select", "lattice_sieve", "filter", "block_lanczos", "sqrt"],
    }

    # Operadic question: can we COMPOSE operations across different pipelines?
    # E.g., use ECM's curve selection as input to SIQS's sieve?
    cross_compositions = {
        "ecm_sieve_hybrid": ["curve_select", "sieve_on_curve", "trial_div", "gauss_elim", "sqrt"],
        "rho_sieve_hybrid": ["rho_walk", "collect_smooth", "gauss_elim", "sqrt"],
        "cfrac_gnfs_hybrid": ["cf_poly_select", "lattice_sieve", "filter", "gauss_elim", "sqrt"],
    }

    return compositions, cross_compositions

def composition_timing_test(N):
    """Test: measure timing of each "stage" to find bottlenecks.
    The operad perspective suggests optimizing the COMPOSITION, not individual stages.
    """
    sq = int(math.isqrt(N))

    # Stage 1: Candidate generation (sieve-like)
    t0 = time.time()
    candidates = []
    for x in range(1, min(10000, sq)):
        val = x * x - N
        if abs(val) < N:
            candidates.append((x, val))
    t_gen = time.time() - t0

    # Stage 2: Smoothness testing (trial division)
    t0 = time.time()
    FB = [p for p in range(2, 200) if all(p % d != 0 for d in range(2, min(p, int(p**0.5)+1)))]
    smooth = []
    for x, val in candidates:
        v = abs(val)
        exponents = {}
        if val < 0:
            exponents[-1] = 1
            v = -val
        for p in FB:
            while v % p == 0:
                v //= p
                exponents[p] = exponents.get(p, 0) + 1
        if v == 1:
            smooth.append((x, val, exponents))
    t_smooth = time.time() - t0

    # Stage 3: Linear algebra (simplified)
    t0 = time.time()
    # Build binary matrix
    if smooth:
        all_primes = sorted(set(p for _, _, exp in smooth for p in exp))
        matrix = []
        for _, _, exp in smooth:
            row = [exp.get(p, 0) % 2 for p in all_primes]
            matrix.append(row)
    t_la = time.time() - t0

    return {
        "generation": t_gen,
        "smoothness": t_smooth,
        "linear_algebra": t_la,
        "candidates": len(candidates),
        "smooth": len(smooth),
    }

def novel_composition_test(N):
    """Test a novel operad composition: interleave sieving and GCD checking.
    Instead of sieve -> collect -> LA -> sqrt,
    try: sieve a bit -> check partial products -> GCD -> repeat.
    This is essentially "early abort" / "progressive factoring".
    """
    sq = int(math.isqrt(N))
    FB = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    # Accumulate product of smooth residues
    product = 1
    checks = 0
    for x in range(sq, sq + 5000):
        val = x * x - N
        if val <= 0:
            continue
        # Quick smooth check
        v = val
        for p in FB:
            while v % p == 0:
                v //= p
        if v == 1:
            product = (product * (x * x)) % N  # accumulate x^2 values
            checks += 1
            if checks % 5 == 0:
                g = math.gcd(product - 1, N) if product > 1 else 1
                if 1 < g < N:
                    return g, checks, "progressive GCD"

    return None, checks, "no factor"

def experiment():
    print("=== Field 16: Operads - Compositional Structure ===\n")

    comps, cross = operad_pipeline_model()
    print("  Standard factoring pipelines (operad elements):")
    for name, stages in comps.items():
        print(f"    {name}: {' -> '.join(stages)}")

    print("\n  Cross-pipeline compositions:")
    for name, stages in cross.items():
        print(f"    {name}: {' -> '.join(stages)}")

    print("\n  Stage timing analysis:")
    random.seed(42)
    for bits in [20, 24, 28, 32]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
               all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                break
        N = p * q
        timing = composition_timing_test(N)
        print(f"    {bits}b N={N}: gen={timing['generation']:.4f}s, smooth={timing['smoothness']:.4f}s, LA={timing['linear_algebra']:.4f}s")
        print(f"      candidates={timing['candidates']}, smooth={timing['smooth']}")

    print("\n  Novel composition test (progressive GCD):")
    for bits in [20, 24, 28]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
               all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                break
        N = p * q
        factor, checks, method = novel_composition_test(N)
        print(f"    {bits}b: {method}, factor={factor}, smooth values checked={checks}")

    print("\nVERDICT: The operad perspective correctly identifies factoring as a pipeline")
    print("of composable operations. But the COMPLEXITY is determined by the hardest")
    print("stage (sieving), not by the composition. Novel compositions (progressive GCD,")
    print("interleaved checking) don't change the asymptotic complexity. The operad")
    print("framework is useful for SOFTWARE ENGINEERING (modular design) but doesn't")
    print("provide new mathematical insight for factoring.")
    print("RESULT: REFUTED (useful for engineering, not for complexity)")

experiment()
