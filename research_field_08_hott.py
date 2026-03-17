"""Field 8: Homotopy Type Theory - Computational Content of Number-Theoretic Proofs
Hypothesis: By the Curry-Howard correspondence, a proof that N is composite contains
a constructive witness (the factors). HoTT's univalence axiom might provide new
computational paths to extract this witness. Test: can we extract factors from the
proof structure of "N is not prime" more efficiently than direct search?
"""
import time, math, random

def fermat_witness_extraction(N):
    """Fermat's little theorem: if N is prime, a^{N-1} = 1 mod N for all a.
    A Fermat witness a where a^{N-1} != 1 mod N proves N is composite.
    Can we extract factors from the witness?
    """
    witnesses = []
    for a in range(2, min(N, 50)):
        if math.gcd(a, N) > 1:
            continue
        r = pow(a, N - 1, N)
        if r != 1:
            witnesses.append((a, r))
            # Try to extract factor from witness
            # r = a^{N-1} mod N, r != 1
            # So a^{N-1} - 1 = 0 mod (some factor of N but not all)
            # Try: gcd(a^{(N-1)/2} - 1, N)
            if (N - 1) % 2 == 0:
                half = pow(a, (N - 1) // 2, N)
                g = math.gcd(half - 1, N)
                if 1 < g < N:
                    return a, g, "Miller-Rabin style"
                g = math.gcd(half + 1, N)
                if 1 < g < N:
                    return a, g, "Miller-Rabin style"
    return None, None, "no extraction"

def proof_term_structure(N):
    """In HoTT, the type "N is composite" is Sigma(p q : N). p*q = N ∧ p>1 ∧ q>1.
    An inhabitant of this type IS the factorization.
    The computational content of any proof of "N is composite" must compute p,q.

    Test: does the proof of "not prime" via witness give computational content?
    """
    # Proof 1: Fermat witness (probabilistic)
    # Computational content: a^{N-1} mod N != 1
    # This PROVES compositeness but does NOT give factors!
    # The proof term is "there exists a Fermat witness" but it's not constructive for factors.

    # Proof 2: AKS (deterministic polynomial)
    # Proves "N is prime" or "N is composite" in poly time
    # But the "composite" branch doesn't give factors either!

    # Proof 3: Trial division (constructive)
    # The ONLY proof method that naturally gives factors
    sq = int(math.isqrt(N))
    for d in range(2, sq + 1):
        if N % d == 0:
            return d, N // d, "trial division (constructive proof)"

    return N, 1, "prime"

def univalence_test(N, p, q):
    """Univalence axiom: equivalent types are equal.
    Z/NZ ≅ Z/pZ × Z/qZ (by CRT when N=pq, gcd(p,q)=1).
    Univalence says these types are EQUAL, not just isomorphic.
    Can we use this to transport structure?

    Key insight: any property of Z/pZ × Z/qZ automatically holds for Z/NZ.
    But to USE univalence, we need the equivalence proof, which requires p,q.
    """
    # Transport test: in Z/pZ × Z/qZ, zero divisors are (0,x) and (x,0).
    # Transport to Z/NZ: zero divisors are multiples of p and q.
    # To find them: x*(N/x) = 0 mod N for any factor x. Circular.
    return "Univalence requires the equivalence proof, which IS the factorization."

def experiment():
    print("=== Field 8: HoTT - Computational Content of Proofs ===\n")

    random.seed(42)
    test_cases = [(3, 5), (7, 11), (13, 17), (23, 29), (37, 41),
                  (101, 103), (251, 257), (1009, 1013)]

    print("  Test 1: Can Fermat witnesses be 'extracted' into factors?")
    for p, q in test_cases[:5]:
        N = p * q
        a, factor, method = fermat_witness_extraction(N)
        if factor and factor > 1:
            print(f"    N={N}: witness a={a} -> factor {factor} via {method}")
        else:
            print(f"    N={N}: witnesses found but no factor extraction")

    print("\n  Test 2: Proof term analysis")
    for p, q in test_cases[:5]:
        N = p * q
        d, _, method = proof_term_structure(N)
        print(f"    N={N}: {method} -> factor {d}")

    print("\n  Test 3: Univalence axiom")
    for p, q in test_cases[:3]:
        N = p * q
        result = univalence_test(N, p, q)
        print(f"    N={N}: {result}")

    print("\n  Key HoTT insight:")
    print("  The type 'N is composite' = Sigma(p,q). p*q=N ∧ p>1 ∧ q>1")
    print("  ANY proof of this type MUST construct the witness (p,q).")
    print("  There is no shortcut: the computational content IS factoring.")
    print("  Fermat/Miller-Rabin prove compositeness but inhabit a WEAKER type")
    print("  ('there exists a witness a with a^{N-1}!=1') that doesn't contain factors.")
    print("  The Miller-Rabin extraction (gcd of half-order) sometimes works -")
    print("  this is essentially Shor's classical component.")

    print("\nVERDICT: HoTT correctly identifies that factoring proofs must be")
    print("constructive (they carry the witness). But this is a CHARACTERIZATION")
    print("of the problem, not a solution method. No new computational paths.")
    print("RESULT: REFUTED")

experiment()
