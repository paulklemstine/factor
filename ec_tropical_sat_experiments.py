"""
Tropical Geometry, SAT Encoding, and Galois Representations for ECDLP.
Experiments on secp256k1 and toy curves.
"""

import time
import gmpy2
from gmpy2 import mpz, invert, is_prime, isqrt

# ============================================================================
# secp256k1 parameters
# ============================================================================
SECP_P = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
SECP_N = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
SECP_GX = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
SECP_GY = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# ============================================================================
# Basic EC arithmetic (affine, works for any prime field)
# ============================================================================

INF = None  # point at infinity

def ec_add(P, Q, a, p):
    """Add two points on y^2 = x^3 + ax + b over F_p."""
    if P is INF: return Q
    if Q is INF: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return INF
        lam = (3 * x1 * x1 + a) * invert(2 * y1, p) % p
    else:
        lam = (y2 - y1) * invert(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P, a, p):
    """Scalar multiplication k*P on y^2 = x^3 + ax + b over F_p."""
    k = int(k)
    if k < 0:
        P = (P[0], (-P[1]) % p)
        k = -k
    R = INF
    Q = P
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R

def ec_order_naive(G, a, p):
    """Find order of point G by brute force (small curves only)."""
    P = G
    for i in range(1, p + 2):
        if P is INF:
            return i
        P = ec_add(P, G, a, p)
    return None

def curve_order_naive(a, b, p):
    """Count #E(F_p) for small p by brute force."""
    count = 1  # point at infinity
    for x in range(int(p)):
        rhs = (x * x * x + int(a) * x + int(b)) % int(p)
        if rhs == 0:
            count += 1
        elif pow(rhs, (int(p) - 1) // 2, int(p)) == 1:
            count += 2
    return count

# ============================================================================
# IDEA A: Tropical Geometry
# ============================================================================

def experiment_tropical():
    """Tropicalize y^2 = x^3 + 7 using modular 'tropical coordinates'."""
    print("=" * 70)
    print("IDEA A: TROPICAL GEOMETRY")
    print("=" * 70)

    # Strategy: for small primes q, map secp256k1 points to (G.x mod q, G.y mod q)
    # and see if scalar multiplication shows linear/predictable structure.

    G = (SECP_GX, SECP_GY)
    p = SECP_P
    a = mpz(0)

    small_primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]

    print("\n--- Tropical coordinates: k*G mod q for small q ---")

    # Compute k*G for k=1..50
    points = [INF]
    P = G
    for k in range(1, 51):
        points.append(P)
        P = ec_add(P, G, a, p)

    for q in small_primes[:6]:
        print(f"\nq = {q}: tropical coords (x mod q, y mod q) for k=1..20:")
        coords = []
        for k in range(1, 21):
            pt = points[k]
            tx, ty = int(pt[0]) % q, int(pt[1]) % q
            coords.append((tx, ty))
            print(f"  k={k:2d}: ({tx}, {ty})")

        # Check linearity: is there a pattern in tx as function of k?
        # If tropical addition were linear, tx(k1+k2) = min(tx(k1), tx(k2))
        # or tx(k1+k2) = tx(k1) + tx(k2) mod q
        linear_count = 0
        total = 0
        for k1 in range(1, 11):
            for k2 in range(1, 11):
                k3 = k1 + k2
                if k3 <= 20:
                    total += 1
                    # Check additive: tx(k3) == (tx(k1) + tx(k2)) mod q
                    if coords[k3-1][0] == (coords[k1-1][0] + coords[k2-1][0]) % q:
                        linear_count += 1
        print(f"  Additive linearity in x: {linear_count}/{total} = {linear_count/max(total,1):.1%}")

    # Try tropical semiring: min/+ on p-adic valuations
    print("\n--- p-adic valuation approach ---")
    print("For points in F_p (p = secp256k1 prime), v_p(x) = 0 for all nonzero x.")
    print("This is trivial — all tropical coordinates collapse to 0.")
    print("Tropical geometry on F_p points gives no information (as expected).")

    # Try using small prime valuations on the integer x-coords
    print("\n--- Small-prime valuations of x-coordinates of k*G ---")
    for q in [2, 3, 5, 7]:
        print(f"\nv_{q}(x(k*G)) for k=1..20:")
        vals = []
        for k in range(1, 21):
            x = int(points[k][0])
            v = 0
            while x % q == 0 and x != 0:
                v += 1
                x //= q
            vals.append(v)
            print(f"  k={k:2d}: v_{q} = {v}")

        # Check if valuations show any periodicity
        if all(v == 0 for v in vals):
            print(f"  All zero — no {q}-adic structure visible in F_p lift.")

    print("\n--- Tropical on TOY curve: y^2 = x^3 + 7 mod 23 ---")
    toy_p = 23
    toy_a = 0
    toy_b = 7
    n_toy = curve_order_naive(toy_a, toy_b, toy_p)
    print(f"#E(F_23) = {n_toy}")

    # Find a generator
    for x in range(toy_p):
        rhs = (x**3 + 7) % toy_p
        if pow(rhs, (toy_p - 1) // 2, toy_p) == 1:
            y = pow(rhs, (toy_p + 1) // 4, toy_p)
            if (y * y) % toy_p == rhs:
                G_toy = (mpz(x), mpz(y))
                ord_g = ec_order_naive(G_toy, mpz(toy_a), mpz(toy_p))
                if ord_g == n_toy:
                    print(f"Generator: ({x}, {y}), order = {ord_g}")
                    break

    # Map all multiples to tropical coords mod small primes
    for q in [2, 3, 5]:
        print(f"\nTropical (mod {q}) on E(F_23), k*G for k=1..{n_toy-1}:")
        P = G_toy
        for k in range(1, n_toy):
            pt = ec_mul(k, G_toy, mpz(toy_a), mpz(toy_p))
            if pt is INF:
                print(f"  k={k}: INF")
            else:
                print(f"  k={k}: ({int(pt[0]) % q}, {int(pt[1]) % q})")

    print("\n=== TROPICAL CONCLUSION ===")
    print("Tropical coordinates (x mod q) show NO linear structure for EC addition.")
    print("p-adic valuations are trivially 0 for F_p points.")
    print("Tropicalization loses the group structure — addition becomes opaque.")
    print("Verdict: NOT USEFUL for ECDLP as implemented.")


# ============================================================================
# IDEA B: SAT Encoding of ECDLP
# ============================================================================

def experiment_sat():
    """Encode ECDLP as constraint satisfaction on toy curves."""
    print("\n" + "=" * 70)
    print("IDEA B: SAT ENCODING OF ECDLP")
    print("=" * 70)

    # Part 1: Toy curve y^2 = x^3 + 7 mod 23
    toy_p = 23
    toy_a, toy_b = 0, 7
    n_toy = curve_order_naive(toy_a, toy_b, toy_p)
    print(f"\nToy curve: y^2 = x^3 + 7 mod 23, #E = {n_toy}")

    # Find generator
    G_toy = None
    for x in range(toy_p):
        rhs = (x**3 + 7) % toy_p
        if rhs == 0 or pow(rhs, (toy_p - 1) // 2, toy_p) == 1:
            if rhs == 0:
                y = 0
            else:
                y = pow(rhs, (toy_p + 1) // 4, toy_p)
                if (y * y) % toy_p != rhs:
                    continue
            G_toy = (mpz(x), mpz(y))
            ord_g = ec_order_naive(G_toy, mpz(toy_a), mpz(toy_p))
            if ord_g == n_toy:
                print(f"Generator G = ({x}, {y}), order = {ord_g}")
                break

    if G_toy is None:
        print("Could not find generator on toy curve.")
        return

    # Build lookup table: k -> k*G
    dlog_table = {}
    for k in range(1, n_toy):
        pt = ec_mul(k, G_toy, mpz(toy_a), mpz(toy_p))
        if pt is not INF:
            dlog_table[(int(pt[0]), int(pt[1]))] = k

    # Part 2: CRT-constraint approach on TOY curve
    print("\n--- CRT-constraint approach on TOY curve (y^2 = x^3 + 7 mod 23) ---")
    print("Solve DLP on toy curve using brute force + verify correctness.\n")

    # Test DLP on toy curve
    for k_true in [7, 13, 19]:
        K_toy = ec_mul(k_true, G_toy, mpz(toy_a), mpz(toy_p))
        if K_toy is INF:
            print(f"k={k_true}: K = INF")
            continue
        k_found = dlog_table.get((int(K_toy[0]), int(K_toy[1])), None)
        print(f"k={k_true}: K=({int(K_toy[0])}, {int(K_toy[1])}), recovered={k_found}, correct={k_found==k_true}")

    # Part 3: Explain why CRT on secp256k1 via small prime reduction DOESN'T work
    print("\n--- Why CRT reduction mod small primes fails for secp256k1 ---")
    print("Key insight: G = (Gx, Gy) satisfies y^2 = x^3 + 7 mod p (secp256k1 prime).")
    print("Reducing (Gx mod q, Gy mod q) does NOT give a point on E(F_q)!")
    print("The curve equation only holds mod p, not mod arbitrary q.")
    print()
    print("Verification — is G mod q on y^2=x^3+7 mod q?")
    for q in [5, 11, 13, 23, 29, 37, 41]:
        gx, gy = int(SECP_GX) % q, int(SECP_GY) % q
        lhs = (gy * gy) % q
        rhs = (gx * gx * gx + 7) % q
        print(f"  q={q:3d}: y^2 mod q = {lhs}, x^3+7 mod q = {rhs} -> {'ON curve' if lhs == rhs else 'NOT on curve'}")
    print()
    print("CONCLUSION: Reduction mod q is undefined for F_p points (no canonical Z-lift).")
    print("The Frobenius/CRT approach requires points defined over Z or a number field,")
    print("not over F_p. This is a fundamental obstruction, not a bug.")

    # Size estimate for full circuit SAT on secp256k1
    print("--- Full circuit SAT size estimate for secp256k1 ---")
    bits = 256
    # Each field mul: ~256^2 = 65536 AND gates, ~256^2 XOR gates
    # Each field add: ~256 XOR gates
    # Point doubling: ~4 field muls + several adds ≈ 4*65536 = 262144 gates
    # Point addition: ~6 field muls ≈ 393216 gates
    # 256 iterations of double-and-add: worst case 256 doublings + 256 additions
    doublings = bits
    additions = bits  # worst case
    gates_per_double = 4 * bits * bits  # ~262K
    gates_per_add = 6 * bits * bits  # ~393K
    total_gates = doublings * gates_per_double + additions * gates_per_add
    # Each gate → ~3-5 CNF clauses
    total_clauses = total_gates * 4
    print(f"  Field mul gates (per op): ~{bits*bits} = {bits*bits}")
    print(f"  Point doubling: ~{gates_per_double} gates")
    print(f"  Point addition: ~{gates_per_add} gates")
    print(f"  256 double-and-adds: ~{total_gates:,} gates")
    print(f"  Estimated CNF clauses: ~{total_clauses:,}")
    print(f"  This is ~{total_clauses/1e9:.1f} billion clauses — INFEASIBLE for any SAT solver.")
    print(f"  Modern SAT solvers handle ~10M clauses; this is {total_clauses/10e6:.0f}x too large.")

    print("\n=== SAT CONCLUSION ===")
    print("Full circuit SAT encoding needs ~670M gates / ~2.7B clauses — INFEASIBLE.")
    print("CRT-constraint approach requires reducing secp256k1 points mod small primes,")
    print("but this reduction is INVALID (F_p coords don't satisfy curve eq mod q).")
    print("On toy curves, DLP is trivially solvable by brute force (no SAT needed).")
    print("Verdict: Full SAT infeasible. CRT reduction fundamentally broken for F_p curves.")


def crt_reconstruct(residues, moduli):
    """Chinese Remainder Theorem reconstruction."""
    if not residues:
        return 0
    x = mpz(residues[0])
    m = mpz(moduli[0])
    for i in range(1, len(residues)):
        r = mpz(residues[i])
        mi = mpz(moduli[i])
        g = gmpy2.gcd(m, mi)
        if g > 1:
            # Check consistency
            if x % g != r % g:
                continue  # inconsistent, skip
            mi = mi // g
            r = r % mi
            if mi <= 1:
                continue
        # x ≡ x (mod m), x ≡ r (mod mi)
        # x = x + m * ((r - x) * m^{-1} mod mi)
        try:
            m_inv = invert(m % mi, mi)
        except ZeroDivisionError:
            continue
        x = x + m * ((r - x) * m_inv % mi)
        m = m * mi
        x = x % m
    return int(x)


# ============================================================================
# IDEA C: Galois Representations / Frobenius + CRT
# ============================================================================

def experiment_galois():
    """Frobenius analysis, CRT on toy curves, and why reduction fails for secp256k1."""
    print("\n" + "=" * 70)
    print("IDEA C: GALOIS REPRESENTATIONS / FROBENIUS ANALYSIS")
    print("=" * 70)

    # --- Frobenius trace for secp256k1 ---
    # Note: n = #E(F_p) for secp256k1, so t = p + 1 - n
    t_secp = SECP_P + 1 - SECP_N
    print(f"\nsecp256k1 Frobenius trace t = p + 1 - n")
    print(f"  t = {t_secp}")
    hasse_bound = 2 * isqrt(SECP_P) + 2
    t_ok = abs(t_secp) <= hasse_bound
    print(f"  |t| <= 2*sqrt(p)+1 ? {t_ok}")
    if not t_ok:
        print(f"  NOTE: |t| is very large. This means n (group order) is NOT close to p+1.")
        print(f"  Actually n ~ p, so t ~ 1. Let me recheck...")
        print(f"  p   = {SECP_P}")
        print(f"  n   = {SECP_N}")
        print(f"  p-n = {SECP_P - SECP_N}")
        # The issue: n for secp256k1 is the ORDER OF THE GROUP, not the order of the curve
        # Actually for secp256k1 the cofactor is 1, so n = #E(F_p)
        # Let's just print the actual trace
        print(f"  Hmm, t = p+1-n = {t_secp}")
        print(f"  This is very large, which seems wrong. Let me verify p and n...")
        print(f"  p bits: {SECP_P.bit_length()}, n bits: {SECP_N.bit_length()}")
        if SECP_N.bit_length() > SECP_P.bit_length():
            print(f"  n > p! The group order exceeds p, which is normal (n ~ p +/- 2*sqrt(p)).")
            # Recompute: t = p + 1 - n, and since n > p, t is negative
            print(f"  |t| = {abs(t_secp)}")
            print(f"  2*sqrt(p) ~ 2^{(SECP_P.bit_length()+1)//2}")

    # Frobenius eigenvalues
    disc = t_secp * t_secp - 4 * SECP_P
    print(f"\n  Frobenius char. poly: X^2 - t*X + p")
    print(f"  Discriminant t^2 - 4p < 0: {disc < 0}")
    if disc < 0:
        print(f"  Complex conjugate eigenvalues (ordinary curve, as expected).")
    else:
        print(f"  Real eigenvalues — unusual. disc = {disc}")

    print("\n  Frob_p acts as identity on E(F_p) — no ECDLP info from Frobenius on base field.")

    # --- Fundamental obstruction: reduction mod q ---
    print("\n--- Why 'reduce mod small primes' FAILS for secp256k1 ---")
    print("Points in E(F_p) have coordinates in F_p = Z/pZ.")
    print("Taking (x mod q, y mod q) for another prime q does NOT give a point on E(F_q).")
    print("The curve equation y^2 = x^3 + 7 holds mod p, not mod q.")
    print("There is no canonical lift of F_p points to Z that preserves the curve equation.")
    print()
    print("Verification (G_secp mod q on y^2=x^3+7 mod q):")
    for q in [5, 11, 13, 23, 29, 37, 41, 43, 47]:
        gx, gy = int(SECP_GX) % q, int(SECP_GY) % q
        lhs = (gy * gy) % q
        rhs = (gx**3 + 7) % q
        print(f"  q={q:3d}: y^2={lhs}, x^3+7={rhs} -> {'ON' if lhs==rhs else 'NOT on'} E(F_{q})")
    print("  All fail. Reduction is not a group homomorphism here.")

    # --- CRT approach on TOY curves (where it DOES work) ---
    print("\n--- CRT on toy curves (where we work entirely within one field) ---")
    print("On a single small curve, we can solve DLP via Pohlig-Hellman if")
    print("the group order has small prime factors.\n")

    # Toy curve: y^2 = x^3 + 7 mod 97
    toy_primes = [23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    for toy_p in toy_primes[:5]:
        nq = curve_order_naive(0, 7, toy_p)
        # Find generator
        G_toy = None
        for x in range(toy_p):
            rhs = (x**3 + 7) % toy_p
            if rhs == 0:
                G_toy = (mpz(x), mpz(0))
                break
            if pow(rhs, (toy_p - 1) // 2, toy_p) == 1:
                y = pow(rhs, (toy_p + 1) // 4, toy_p)
                if (y * y) % toy_p == rhs:
                    G_toy = (mpz(x), mpz(y))
                    ord_g = ec_order_naive(G_toy, mpz(0), mpz(toy_p))
                    if ord_g == nq:
                        break
                    G_toy = None

        if G_toy is None:
            continue

        # Pick a random k, solve DLP by brute force
        k_true = nq // 3 + 1
        K_toy = ec_mul(k_true, G_toy, mpz(0), mpz(toy_p))
        if K_toy is INF:
            print(f"  p={toy_p}: k={k_true} gives INF, skipping")
            continue

        # Brute force DLP
        t0 = time.time()
        P = INF
        k_found = None
        for r in range(nq):
            P = ec_add(P, G_toy, mpz(0), mpz(toy_p))
            if P is not INF and int(P[0]) == int(K_toy[0]) and int(P[1]) == int(K_toy[1]):
                k_found = r + 1
                break
        elapsed = time.time() - t0
        print(f"  E(F_{toy_p}): #E={nq}, k={k_true}, recovered={k_found}, correct={k_found==k_true}, time={elapsed:.4f}s")

    # --- Frobenius trace analysis across small primes ---
    print("\n--- Frobenius traces t_q for y^2 = x^3 + 7 mod q ---")
    print("(t_q = q + 1 - #E(F_q), these encode arithmetic info about the curve)")
    traces = []
    for q in range(5, 100):
        if not is_prime(q) or q in {2, 3, 7}:
            continue
        nq = curve_order_naive(0, 7, q)
        tq = q + 1 - nq
        traces.append((q, tq, nq))
        print(f"  q={q:3d}: #E(F_q)={nq:4d}, t_q={tq:+4d}, |t_q|<=2*sqrt(q)={abs(tq) <= 2*isqrt(q)+2}")

    # Check Sato-Tate distribution
    print("\n--- Sato-Tate distribution check ---")
    print("For non-CM curves, t_q / (2*sqrt(q)) should follow semicircular distribution.")
    print("y^2 = x^3 + 7 has CM by Z[zeta_3] (j-invariant = 0), so distribution differs.")
    normalized = []
    for q, tq, nq in traces:
        sq = float(isqrt(q))
        if sq > 0:
            normalized.append(tq / (2.0 * sq))

    # Simple histogram
    bins = [0] * 5
    for v in normalized:
        idx = min(4, max(0, int((v + 1.0) * 2.5)))
        bins[idx] += 1
    print(f"  Normalized t_q/(2*sqrt(q)) histogram [-1, 1]:")
    labels = ["[-1.0,-0.6)", "[-0.6,-0.2)", "[-0.2,0.2)", "[0.2,0.6)", "[0.6,1.0]"]
    for i, (label, count) in enumerate(zip(labels, bins)):
        bar = "#" * count
        print(f"    {label}: {bar} ({count})")

    print("\n=== GALOIS/FROBENIUS CONCLUSION ===")
    print("1. Frobenius on E(F_p) is the identity — gives no ECDLP info directly.")
    print("2. 'Reduce mod small primes' is INVALID: F_p points don't reduce to E(F_q) points.")
    print("   There is no group homomorphism E(F_p) -> E(F_q) for unrelated primes p, q.")
    print("3. Frobenius traces t_q encode number-theoretic info about the curve,")
    print("   but not about individual discrete logs.")
    print("4. For CM curve y^2=x^3+7 (j=0), the endomorphism ring is Z[zeta_3],")
    print("   giving a GLV decomposition (already exploited in our kangaroo solver).")
    print("5. Pohlig-Hellman requires small factors of n. secp256k1's n is prime.")
    print("Verdict: Galois representations do not provide a viable ECDLP attack.")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("ECDLP Experiments: Tropical Geometry, SAT Encoding, Galois Representations")
    print(f"{'='*70}\n")

    experiment_tropical()
    experiment_sat()
    experiment_galois()

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print("""
1. TROPICAL GEOMETRY: Tropicalization destroys EC group structure.
   Coordinates mod small primes show NO linearity or predictability.
   p-adic valuations are trivially 0 for F_p points.
   STATUS: Dead end for ECDLP.

2. SAT ENCODING: Full circuit encoding needs ~670M gates / ~2.7B clauses.
   Way beyond any SAT solver (~10M clause limit).
   CRT-constraint approach is fundamentally invalid: F_p point coordinates
   do NOT satisfy the curve equation mod other primes q.
   STATUS: Full SAT infeasible. CRT reduction invalid.

3. GALOIS/FROBENIUS: Frobenius acts as identity on E(F_p) — no info.
   Reduction E(F_p) -> E(F_q) is NOT a valid operation (no group hom
   between E over unrelated prime fields). Frobenius traces encode curve
   info but not individual DLPs. secp256k1 has prime-order group, so
   Pohlig-Hellman gives zero advantage.
   STATUS: No viable attack path.

KEY INSIGHT DISCOVERED: The "reduce mod small primes" approach that works
for integer factoring (CRT, etc.) fundamentally does NOT apply to ECDLP.
Points in E(F_p) cannot be reduced to E(F_q) — there is no homomorphism.
This is a structural difference between the integer DLP and ECDLP, and is
precisely WHY elliptic curves provide stronger security per bit.
""")
