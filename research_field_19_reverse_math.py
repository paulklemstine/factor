"""Field 19: Reverse Mathematics - What Axioms Are Needed for Factoring?
Hypothesis: Reverse mathematics classifies theorems by the axiom systems needed to
prove them (RCA_0, WKL_0, ACA_0, ATR_0, Pi^1_1-CA_0). The factoring theorem
("every composite N has a nontrivial factorization") requires certain axioms.
If factoring requires FEWER axioms than expected, there might be a simpler proof
(= faster algorithm) lurking. If it requires MORE, this explains the difficulty.
"""
import time, math, random

def axiom_analysis():
    """Classify factoring-related theorems in the 'Big Five' systems."""

    theorems = {
        "Every_composite_has_factor": {
            "statement": "∀N>1 composite, ∃p with 1<p<N and p|N",
            "system": "RCA_0 (base system)",
            "reason": "Bounded search: check d=2,...,sqrt(N). This is Sigma^0_1-induction.",
            "algorithmic": "Corresponds to trial division O(sqrt(N))",
        },
        "Fundamental_theorem_of_arithmetic": {
            "statement": "Every N>1 has a unique prime factorization",
            "system": "RCA_0 (with bounded Sigma^0_1 comprehension)",
            "reason": "Existence by repeated division, uniqueness by Euclid's lemma",
            "algorithmic": "Repeated trial division, O(sqrt(N) * log(N))",
        },
        "Infinitude_of_primes": {
            "statement": "There are infinitely many primes",
            "system": "RCA_0",
            "reason": "Euclid's proof is constructive and uses only bounded quantifiers",
            "algorithmic": "N/A (existence, not search)",
        },
        "Prime_number_theorem": {
            "statement": "pi(x) ~ x/ln(x)",
            "system": "ACA_0 (arithmetical comprehension)",
            "reason": "Requires reasoning about convergence of infinite sums",
            "algorithmic": "Provides smoothness probability estimates for sieve methods",
        },
        "Dirichlet_L_functions": {
            "statement": "L(s, chi) has analytic continuation and functional equation",
            "system": "ATR_0 or higher",
            "reason": "Requires transfinite induction for analytic continuation",
            "algorithmic": "Used in NFS (norm estimates, smoothness probabilities)",
        },
    }
    return theorems

def constructive_factoring_test():
    """In constructive mathematics (no LEM = law of excluded middle):
    Can we factor N without LEM?

    Key: "N is composite OR N is prime" requires LEM for unbounded N.
    But "given that N is composite, find a factor" is constructive
    (trial division terminates).

    The issue: RECOGNIZING that N is composite (primality testing)
    vs FINDING the factors (factoring).
    AKS is constructive for primality. Factoring by TD is constructive.
    But efficient factoring (SIQS, GNFS) uses non-constructive elements:
    - Randomized polynomial selection
    - Probabilistic smoothness testing
    - Non-constructive existence of smooth relations
    """
    return {
        "constructive_methods": ["trial_division", "Fermat_method", "AKS"],
        "non_constructive_elements": {
            "SIQS": "probabilistic poly selection, random sieve intervals",
            "ECM": "random curve selection (probability of success)",
            "GNFS": "existence of good polynomial (non-constructive choice)",
        },
        "key_insight": "Efficient factoring uses PROBABILISTIC methods, "
                       "which are non-constructive (existence of good random choices)"
    }

def computational_content_test(N):
    """Reverse mathematics test: what's the weakest system that proves
    'N has a factor <= sqrt(N)'?

    In RCA_0: we can define 'x divides y' (bounded), 'x is composite' (bounded search).
    The theorem 'if N composite then exists p <= sqrt(N) dividing N' is provable in RCA_0.

    Key question: can we prove factoring is HARD in any reverse math system?
    I.e., is there a theorem 'factoring requires exponential time' that itself
    requires strong axioms?
    """
    # This is a meta-question: the HARDNESS of factoring is an open problem.
    # Reverse mathematics can't settle P vs NP.
    # But it CAN tell us what axioms are needed to REASON about factoring complexity.

    results = {
        "factoring_exists": "RCA_0 (weakest system)",
        "factoring_unique": "RCA_0",
        "factoring_hard": "UNKNOWN (P vs NP is independent of standard axioms?)",
        "sieve_correctness": "ACA_0 (needs arithmetic comprehension for smoothness bounds)",
    }
    return results

def experiment():
    print("=== Field 19: Reverse Mathematics ===\n")

    print("  Test 1: Axiom classification of factoring theorems")
    theorems = axiom_analysis()
    for name, info in theorems.items():
        print(f"  {name}:")
        print(f"    Statement: {info['statement']}")
        print(f"    System: {info['system']}")
        print(f"    Algorithmic: {info['algorithmic']}")
        print()

    print("  Test 2: Constructive vs non-constructive factoring")
    cf = constructive_factoring_test()
    print(f"    Constructive methods: {cf['constructive_methods']}")
    for method, elements in cf['non_constructive_elements'].items():
        print(f"    {method} non-constructive: {elements}")
    print(f"    Key insight: {cf['key_insight']}")

    print("\n  Test 3: Computational content")
    cc = computational_content_test(0)  # N not needed for meta-analysis
    for question, answer in cc.items():
        print(f"    {question}: {answer}")

    print("\n  Test 4: Experimental - do 'constructive' methods scale differently?")
    random.seed(42)
    for bits in [16, 20, 24, 28, 32]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
               all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                break
        N = p * q

        # Constructive (trial division)
        t0 = time.time()
        for d in range(2, int(math.isqrt(N)) + 1):
            if N % d == 0:
                break
        t_constructive = time.time() - t0

        # Probabilistic (Pollard rho)
        t0 = time.time()
        x, y, d_rho = 2, 2, 1
        while d_rho == 1:
            x = (x * x + 1) % N
            y = (y * y + 1) % N
            y = (y * y + 1) % N
            d_rho = math.gcd(abs(x - y), N)
        t_probabilistic = time.time() - t0

        print(f"    {bits}b: constructive={t_constructive:.5f}s, probabilistic={t_probabilistic:.5f}s, ratio={t_constructive/max(t_probabilistic, 1e-10):.1f}x")

    print("\nVERDICT: Reverse mathematics shows factoring existence is provable in")
    print("the WEAKEST system (RCA_0). This means factoring is 'easy' from a")
    print("logical standpoint - it doesn't require strong axioms. But logical")
    print("strength != computational efficiency. The non-constructive elements")
    print("(randomization, probabilistic bounds) in efficient algorithms are USEFUL")
    print("but not NECESSARY. No new algorithmic insight from axiom analysis.")
    print("RESULT: REFUTED (interesting classification, no algorithmic content)")

experiment()
