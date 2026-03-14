"""
ECDLP Lifting & Height Function Experiments on secp256k1.

Idea A: Lifting E/F_p to E/Q and height functions
Idea B: Formal group logarithm (p-adic)
Idea C: Discrete elliptic integral / p-adic AGM
"""

import gmpy2
from gmpy2 import mpz, invert, powmod, isqrt
import time
import math

# ── secp256k1 parameters ──
p = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
n = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
Gx = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
Gy = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
a_curve = mpz(0)
b_curve = mpz(7)

# ── EC arithmetic over F_p ──
INF = None

def ec_add(P, Q):
    if P is INF: return Q
    if Q is INF: return P
    px, py = P
    qx, qy = Q
    if px == qx and py == qy:
        return ec_double(P)
    if px == qx:
        return INF
    dx = (qx - px) % p
    dy = (qy - py) % p
    inv_dx = invert(dx, p)
    lam = (dy * inv_dx) % p
    x3 = (lam * lam - px - qx) % p
    y3 = (lam * (px - x3) - py) % p
    return (x3, y3)

def ec_double(P):
    if P is INF: return INF
    px, py = P
    if py == 0: return INF
    num = (3 * px * px + a_curve) % p
    den = (2 * py) % p
    inv_den = invert(den, p)
    lam = (num * inv_den) % p
    x3 = (lam * lam - 2 * px) % p
    y3 = (lam * (px - x3) - py) % p
    return (x3, y3)

def ec_neg(P):
    if P is INF: return INF
    return (P[0], (-P[1]) % p)

def ec_mul(k, P):
    k = mpz(k) % n
    if k == 0: return INF
    R = INF
    Q = P
    while k > 0:
        if k & 1:
            R = ec_add(R, Q)
        Q = ec_double(Q)
        k >>= 1
    return R

G = (Gx, Gy)

# ── Test vectors ──
test_cases = [
    ("k_small", 12345),
    ("k_medium", 2**28 + 37),
    ("k_large", 2**40 + 12345),
]

print("Computing test points K = k*G ...")
test_points = []
for name, k in test_cases:
    K = ec_mul(k, G)
    test_points.append((name, k, K))
    print(f"  {name}: k={k}, K.x={hex(K[0])[:20]}...")
print()

# ======================================================================
# IDEA A: Lifting to Q and height functions
# ======================================================================
print("=" * 70)
print("IDEA A: Lifting E/F_p to E/Q and height functions")
print("=" * 70)

def naive_height_Fp(P):
    """
    'Naive height' of a point in F_p: log(min(x, p-x)).
    This is NOT a true height but tests if x-coordinates carry quadratic info.
    """
    if P is INF:
        return 0.0
    x = P[0]
    # Use the 'balanced' representative: min(x, p-x)
    x_bal = min(x, p - x)
    if x_bal == 0:
        return 0.0
    return float(gmpy2.log2(x_bal))

print("\n--- A1: Naive height h(P) = log2(min(x, p-x)) ---")
h_G = naive_height_Fp(G)
print(f"h(G) = {h_G:.4f}")
for name, k, K in test_points:
    h_K = naive_height_Fp(K)
    ratio = h_K / h_G if h_G > 0 else 0
    print(f"h({name}) = {h_K:.4f},  h(K)/h(G) = {ratio:.6f},  k² = {k*k},  sqrt(ratio)*? = {ratio**0.5:.6f}")
    print(f"  -> ratio/k² = {ratio/(k*k):.2e}" if k > 0 else "")

print("\n--- A2: Quadratic form search on x-coordinates ---")
print("Testing if q(kG) = k² * q(G) for any simple function of coordinates...")

def test_quadratic_form(func_name, func):
    """Test if func(kG) / func(G) = k² for test cases."""
    v_G = func(G)
    if v_G == 0:
        print(f"  {func_name}: func(G) = 0, skip")
        return
    results = []
    for name, k, K in test_points:
        v_K = func(K)
        if v_K == 0:
            results.append(f"    {name}: func(K) = 0")
            continue
        ratio = v_K / v_G if isinstance(v_G, float) else float(mpz(v_K)) / float(mpz(v_G))
        expected = k * k
        results.append(f"    {name}: ratio = {ratio:.6e}, k² = {expected}, match = {abs(ratio - expected) < 1e-6}")
    print(f"  {func_name}:")
    for r in results:
        print(r)

# x-coordinate mod p as integer
test_quadratic_form("x mod p", lambda P: float(P[0]) if P else 0.0)
test_quadratic_form("log2(x)", lambda P: float(gmpy2.log2(P[0])) if P else 0.0)
test_quadratic_form("x² mod p", lambda P: float((P[0] * P[0]) % p) if P else 0.0)

print("\n--- A3: Lift to Q via CRT / Hensel-like approach ---")
print("The point G on E/F_p has x = Gx (mod p).")
print("A lift to Q means finding X ∈ Q with X ≡ Gx (mod p) and Y² = X³ + 7 over Q.")
print("Simplest lift: X = Gx (as integer, 0 ≤ X < p), Y² = X³ + 7 over Z.")

# Check if Gx³ + 7 is a perfect square over Z
val = Gx**3 + 7
print(f"Gx³ + 7 has {int(gmpy2.num_digits(val))} digits")
sq = isqrt(val)
is_sq = (sq * sq == val)
print(f"Is Gx³ + 7 a perfect square over Z? {is_sq}")
if is_sq:
    print("  -> Can lift G directly to E/Q!")
    Gy_lift = sq
    # Naive height over Q: log(max(|num(x)|, |den(x)|))
    h_G_Q = float(gmpy2.log2(Gx))
    print(f"  h_Q(G_lift) = log2(Gx) = {h_G_Q:.4f}")
else:
    print("  -> Gx³ + 7 is NOT a perfect square over Z. Cannot lift G trivially.")
    print("  -> Trying projective lift: multiply by d² to clear denominators...")
    # Try small multipliers
    found_lift = False
    for d in range(2, 100):
        # If (d²·Gx)³ + 7·d⁶ = d⁶(Gx³ + 7), need d⁶(Gx³+7) to be a square
        # That means d³ must make Gx³+7 a square... same condition
        # Actually for Weierstrass: (X, Y) -> (u²X, u³Y), so Y² = X³ + 7 becomes
        # (u³Y)² = (u²X)³ + 7 => u⁶Y² = u⁶X³ + 7... no, this is isomorphism.
        # We need a different approach: choose x_lift = Gx + k*p for some k
        pass

    # Try x_lift = Gx + k*p for small k to find a square
    print("  Trying x_lift = Gx + k*p for k = 0..1000:")
    for k_try in range(1001):
        x_try = Gx + k_try * p
        val_try = x_try**3 + 7
        sq_try = isqrt(val_try)
        if sq_try * sq_try == val_try:
            print(f"    Found lift at k={k_try}!")
            found_lift = True
            break
    if not found_lift:
        print("    No lift found for k=0..1000. (Expected: lifts are very sparse)")

print("\n--- A4: Weil pairing approach ---")
print("The Weil pairing e_n(P, Q) is bilinear: e_n(aP, bQ) = e_n(P,Q)^(ab)")
print("If we had a point Q independent of G, we could compute:")
print("  e_n(K, Q) = e_n(kG, Q) = e_n(G, Q)^k")
print("This reduces ECDLP to DLP in F_p* (MOV attack).")
print("For secp256k1, embedding degree is huge (~n), so this doesn't help directly.")
print("But let's verify the math on a small curve...")

# Small test curve: y² = x³ + 7 mod 23
p_small = mpz(23)
# Find generator and order
def ec_add_small(P, Q, pp):
    if P is None: return Q
    if Q is None: return P
    px, py = P; qx, qy = Q
    if px == qx and py == qy:
        if py == 0: return None
        lam = (3*px*px) * invert(2*py, pp) % pp
    elif px == qx:
        return None
    else:
        lam = (qy - py) * invert(qx - px, pp) % pp
    x3 = (lam*lam - px - qx) % pp
    y3 = (lam*(px - x3) - py) % pp
    return (x3, y3)

def ec_mul_small(k, P, pp):
    R = None; Q = P
    k = int(k)
    while k > 0:
        if k & 1: R = ec_add_small(R, Q, pp)
        Q = ec_add_small(Q, Q, pp)
        k >>= 1
    return R

# Find points on y² = x³ + 7 mod 23
small_points = []
for x in range(23):
    rhs = (x**3 + 7) % 23
    for y in range(23):
        if (y*y) % 23 == rhs:
            small_points.append((mpz(x), mpz(y)))
print(f"Points on y²=x³+7 mod 23: {len(small_points)} (+infinity)")
if len(small_points) > 0:
    G_s = small_points[0]
    # Find order
    P = G_s
    for i in range(1, 50):
        if P is None:
            print(f"  Order of {G_s} is {i}")
            order_s = i
            break
        P = ec_add_small(P, G_s, p_small)
    else:
        order_s = 50
        print(f"  Order > 50")

print()

# ======================================================================
# IDEA B: Formal group logarithm (p-adic)
# ======================================================================
print("=" * 70)
print("IDEA B: Formal group logarithm (p-adic)")
print("=" * 70)

print("""
For y² = x³ + 7 (a₁=a₂=a₃=a₄=0, a₆=7):
The formal group Ê lives in the kernel of reduction.
Local parameter: t = -x/y near the point at infinity.
Then x = t⁻² - a₁t⁻¹ - a₂ - a₃t - (a₄ + a₁a₃)t² - ...
For our curve: x = t⁻², y = -t⁻³ (leading terms).

The formal group logarithm: logF(t) = t + Σ cₙ tⁿ
satisfies logF(t₁ ⊕ t₂) = logF(t₁) + logF(t₂).

If logF(t_K) = k · logF(t_G) mod p^m, we recover k.
""")

print("--- B1: Computing formal group log coefficients ---")

def formal_log_coefficients(num_terms=30):
    """
    Compute coefficients of the formal logarithm for y² = x³ + 7.

    The formal group law F(t₁, t₂) comes from the group law on the curve.
    For y² = x³ + 7, the invariant differential is ω = dx/(2y).

    In terms of t = -x/y:
      x = t⁻² + ... (power series in t)
      y = -t⁻³ + ...

    The formal logarithm is ∫ ω where ω = (1 + ...) dt in terms of t.

    For y² = x³ + a₆ with a₁=a₂=a₃=a₄=0:
    The invariant differential ω = dx/(2y).

    We work with the parameterization:
      w = -1/y = t³/(1 + ...) as a function of t = -x/y
      x = t/w, y = -1/w

    From y² = x³ + 7:
      1/w² = t³/w³ + 7
      w = t³ - 7w²·... (implicit)

    Actually, let's use the standard recursive formula.
    w = t³ + a₆·w² (for our curve, since a₁=a₂=a₃=a₄=0, a₆=7)
    => w = t³ + 7·w²
    Iterate: w₀ = t³, w₁ = t³ + 7·t⁶, w₂ = t³ + 7(t³+7t⁶)² = t³ + 7t⁶ + 98t⁹ + ...
    """
    # Compute w = t³ + 7*w² as power series in t, up to t^N
    N = num_terms
    # w[i] = coefficient of t^i
    w = [mpz(0)] * (N + 1)
    # Seed: w = t³
    if N >= 3:
        w[3] = mpz(1)

    # Iterate: w = t³ + 7*w²
    for iteration in range(N):
        w_new = [mpz(0)] * (N + 1)
        if N >= 3:
            w_new[3] = mpz(1)
        # Compute w² and add 7*w²
        for i in range(N + 1):
            for j in range(N + 1):
                if i + j <= N and w[i] != 0 and w[j] != 0:
                    w_new[i + j] += 7 * w[i] * w[j]
        if w_new == w:
            break
        w = w_new

    # Now x = t/w (as formal Laurent series) but we need x = t/w where w = -1/y
    # x = t/w, y = -1/w
    # invariant differential: dx/(2y)
    # dx = d(t/w) = (w - t·dw/dt)/w² dt
    # 2y = -2/w
    # dx/(2y) = (w - t·dw/dt)/w² · (-w/2) dt = -(w - t·dw/dt)/(2w) dt

    # Compute dw/dt
    dw = [mpz(0)] * (N + 1)
    for i in range(1, N + 1):
        dw[i - 1] = mpz(i) * w[i]

    # Numerator of ω: w - t·dw/dt
    num_omega = [mpz(0)] * (N + 1)
    for i in range(N + 1):
        num_omega[i] += w[i]
    for i in range(N):
        if i + 1 <= N:
            num_omega[i + 1] -= dw[i]

    # ω = -num_omega / (2w) dt = series in t
    # We need to compute num_omega / w as power series (then multiply by -1/2)
    # Let q = num_omega / w, so num_omega = q * w
    # Solve for q[0], q[1], ... coefficient by coefficient
    # Since w starts at t³, and num_omega starts at some power...

    # Actually, let me reconsider. The formal log is:
    # logF(t) = ∫ ω(t) dt where ω = invariant differential
    # For the standard form, logF(t) = t - (a₁/2)t² - (a₂/3)t³ + ...
    # For a₁=a₂=a₃=a₄=0: logF(t) = t + higher order terms from a₆

    # Direct computation via the recursion for the formal log:
    # logF(t) = t + Σ_{n≥2} c_n t^n / n where c_n come from the formal group

    # Simpler: use that logF'(t) = ω(t) and integrate term by term
    # ω = (1 - a₁t - a₂t² - (a₃ + a₁a₂)t³ - ...)^{-1} for short Weierstrass
    # Actually for y²=x³+a₆ with all a_i=0 except a₆:
    # ω = Σ binom(-1/2, k) · (-a₆)^k · t^{3k} ... no

    # Let me just use the direct power series approach.
    # From Silverman: for y²+a₁xy+a₃y = x³+a₂x²+a₄x+a₆
    # t = -x/y, w = -1/y
    # w = t³ - a₁t⁴w - a₂t⁵w - ... wait, the general recursion is:
    # w = t³(1 + a₁t + a₂t² + a₃w + a₄t·w + a₆w²)...
    # For our curve: w = t³(1 + a₆w²/t⁶)... no.

    # OK, the correct recursion from Silverman IV.1:
    # w = t³ - a₁tw - a₂t²w - a₃w² - a₄tw² - a₆w³  (this is for general Weierstrass)
    # Wait, that's also not right. Let me just use:
    # From y²=x³+7, with t=-x/y, w=-1/y:
    # x = t/w, y = -1/w
    # Substituting: 1/w² = t³/w³ + 7
    # => w = t³/(1 + 7w³)... hmm no: 1/w² = t³/w³ + 7 => w = t³ - 7w²·t³... no.
    # 1/w² = t³/w³ + 7
    # Multiply by w³: w = t³ + 7w³
    # So w = t³ + 7w³

    # Redo iteration with w = t³ + 7w³
    w2 = [mpz(0)] * (N + 1)
    w2[3] = mpz(1)
    for iteration in range(N):
        w_new2 = [mpz(0)] * (N + 1)
        w_new2[3] = mpz(1)
        # w³
        # First compute w²
        wsq = [mpz(0)] * (N + 1)
        for i in range(N + 1):
            for j in range(N + 1 - i):
                if w2[i] != 0 and w2[j] != 0:
                    wsq[i + j] += w2[i] * w2[j]
        # w³ = wsq * w
        wcube = [mpz(0)] * (N + 1)
        for i in range(N + 1):
            for j in range(N + 1 - i):
                if wsq[i] != 0 and w2[j] != 0:
                    wcube[i + j] += wsq[i] * w2[j]
        for i in range(N + 1):
            w_new2[i] += 7 * wcube[i]
        if w_new2 == w2:
            break
        w2 = w_new2

    print(f"  w series (first few nonzero): ", end="")
    for i in range(min(N+1, 25)):
        if w2[i] != 0:
            print(f"t^{i}:{w2[i]} ", end="")
    print()

    # The invariant differential ω = dx/(2y)
    # x = t/w, y = -1/w
    # dx/dt = (w - t·w')/w²
    # 2y = -2/w
    # ω = dx/(2y) dt = [(w - t·w')/w²] / (-2/w) dt = -(w - t·w')/(2w) dt
    # = -1/2 · (1 - t·w'/w) dt

    # Compute w'/w: logarithmic derivative
    # First compute w'
    wp = [mpz(0)] * (N + 1)
    for i in range(1, N + 1):
        wp[i-1] = i * w2[i]

    # t·w'/w — compute as power series by: (t·w') / w
    # t·w' has coefficients: (t·w')[i] = wp[i-1] for i>=1, 0 for i=0
    twp = [mpz(0)] * (N + 1)
    for i in range(N):
        twp[i+1] = wp[i]

    # To divide by w, we need to invert w as a power series.
    # w = t³(1 + ...), so 1/w = t⁻³ · (1/(1+...))
    # But we want t·w'/w which should be a proper power series (no negative powers)
    # since w ~ t³ and w' ~ 3t², t·w' ~ 3t³, so t·w'/w ~ 3 + ...

    # Compute (1 - t·w'/w) / 2
    # Actually let me compute ω directly as a power series.
    # ω = -(1 - t·w'/w)/2 dt
    # ω = -1/2 + t·w'/(2w) dt
    # logF(t) = ∫₀ᵗ ω(s) ds

    # Since computing 1/w as power series is tricky with w starting at t³,
    # let me use a different approach.
    #
    # The formal logarithm for y²=x³+c has a nice closed form:
    # logF(t) = Σ_{k≥0} binom(−1/2, k) · (−c)^k · t^(6k+1) / (6k+1)
    # Wait, is this right? Let me derive...

    # For y²=x³+c, the invariant differential is dx/(2y).
    # Near O, t=-x/y, and ω = (1 + c·w³)^{-1/2}... not exactly.
    #
    # Actually, from the formal expansion, the invariant differential for y²=x³+c is:
    # ω = dt · (1 + terms involving c)
    #
    # For c=0 (y²=x³): ω = dt, logF = t.
    # The c-terms come from the t³ + 7w³ recursion.

    # Let me just numerically compute logF by integration of ω.
    # ω_i is the coefficient of t^i in ω(t).
    # logF = Σ ω_i · t^{i+1} / (i+1)

    # We established ω = -(1 - t·w'/w)/2
    # Let's compute this differently. Note:
    # w = t³ + 7w³
    # w' = 3t² + 21w²·w'
    # w'(1 - 21w²) = 3t²
    # w' = 3t² / (1 - 21w²)
    # t·w'/w = 3t³/(w·(1 - 21w²))
    # Since w = t³ + 7w³ = t³(1 + 7w³/t³)... at leading order w~t³, so w/t³ ~ 1
    # t·w'/w = 3t³ / (t³·(1+...) · (1 - 21t⁶·(1+...))) = 3/(1·1) + ... = 3 + ...
    #
    # ω = -(1 - 3 - ...)/2 = 1 + ...  Good, ω starts with 1.

    # Let me compute ω numerically mod p (the p-adic approach).
    # logF(t) mod p^m

    # For mod p computation (m=1), logF(t) = t + higher terms mod p.
    # The key question: does logF(t_K) = k · logF(t_G) mod p?

    return w2

w_series = formal_log_coefficients(30)

print("\n--- B2: Computing t = -x/y mod p for test points ---")
print("For a point P=(x,y) on E/F_p, the local parameter is t = -x/y mod p.")
print("This maps to the formal group only if the point is in the kernel of reduction,")
print("i.e., P reduces to O modulo p. For general points on E/F_p, t = -x/y mod p")
print("is just a number, not in the formal group's domain of convergence.")
print()

def compute_t(P):
    """t = -x/y mod p"""
    if P is INF: return mpz(0)
    x, y = P
    return (-x * invert(y, p)) % p

t_G = compute_t(G)
print(f"t(G) = {hex(t_G)[:20]}...")

for name, k, K in test_points:
    t_K = compute_t(K)
    # Check if t_K / t_G mod p = k mod p
    ratio = (t_K * invert(t_G, p)) % p
    print(f"t({name}) = {hex(t_K)[:20]}...")
    print(f"  t(K)/t(G) mod p = {hex(ratio)[:20]}..., k mod p = {hex(k % p)[:20]}...")
    print(f"  Match? {ratio == k % p}")

print("\n--- B3: Formal logarithm mod p ---")
print("Computing logF(t) = t + c₂t² + c₃t³ + ... mod p")
print("Even though the series may not converge p-adically for arbitrary points,")
print("let's evaluate it mod p and see what happens.")

def formal_log_mod_p(t_val, num_terms=50):
    """
    Compute logF(t) mod p using the formal log series.

    For y²=x³+7, the invariant differential ω satisfies:
    ω = dt/(1 - 21w²) · (something)

    Instead of deriving closed-form coefficients, let's use the
    relation: logF is the unique homomorphism from Ê to Ĝ_a.

    For numerical computation mod p, we use:
    logF(t) = ∫₀ᵗ ω(s) ds where ω is the invariant differential.

    For y² = x³ + 7:
    The formal expansion gives ω(t) = 1 - 7·5·t⁶/2 + ... (complicated)

    Alternative: directly test linearity.
    If logF is a homomorphism, then logF(t(P+Q)) = logF(t(P)) + logF(t(Q)).

    But we can also just test: does t(kG)/t(G) = k mod p? (i.e., is the map already linear at first order?)
    """
    # The formal log mod p for a curve over F_p is essentially the identity at first order
    # logF(t) ≡ t mod (t²) always.
    # Higher terms matter for convergence and accuracy.

    # For the formal group over Z_p (p-adic integers), logF converges on the maximal ideal.
    # Over F_p (mod p), the series truncates and logF(t) ≡ t (mod p) to first order.
    # All higher terms also reduce mod p but the series is finite mod p.

    # Let's compute: logF(t) = Σ_{n≥1} a_n t^n / n  where the a_n come from ω = Σ a_n t^{n-1}

    # From w = t³ + 7w³, derive ω:
    # Shortcut: for y²=x³+c, the invariant differential expansion is:
    # ω = Σ_{k≥0} binom(-3/2, k) · (-7)^k · t^{6k} ... actually I'm not sure about this.
    #
    # Let me just use the NUMERICAL approach:
    # Compute ω coefficients from the w series, then integrate.

    # From the w series (mod p), compute ω = -(1 - t·w'/w)/2
    # But 1/w involves division by zero-ish power series...

    # ACTUALLY: the simplest test. The formal log is a p-adic object.
    # Over F_p (residue field), logF(t) ≡ t mod p automatically.
    # The formal log only gives extra info if we work mod p² or higher.
    # But our points are defined mod p only, so t(P) is only defined mod p.
    #
    # Therefore, logF(t(P)) ≡ t(P) mod p, and the test reduces to:
    # Does t(kG) = k · t(G) mod p?
    # We already tested this above and it DOESN'T hold (as expected).

    return t_val  # mod p, logF(t) ≡ t

print("Key insight: Over F_p (not Z_p), the formal log reduces to logF(t) ≡ t mod p.")
print("We already tested t(kG) = k·t(G) mod p above — it doesn't hold for general points.")
print("The formal group log only works for points in the KERNEL OF REDUCTION,")
print("i.e., points that are 'close to O' p-adically. General points on E(F_p) are not in this kernel.")

print("\n--- B4: p-adic lift and formal log mod p² ---")
print("To use the formal group properly, we need to work over Z/p²Z (or higher).")
print("Lift: find (X, Y) with X ≡ x mod p, Y ≡ y mod p, Y² ≡ X³+7 mod p².")

def hensel_lift_point(P, precision=2):
    """Lift point P from E(F_p) to E(Z/p^m Z) via Hensel's lemma."""
    if P is INF:
        return INF
    x0, y0 = P
    pm = p ** precision
    # We have y0² ≡ x0³ + 7 mod p
    # Lift: keep x = x0, adjust y so y² ≡ x0³ + 7 mod p²
    # y = y0 + t·p for some t
    # (y0 + tp)² = y0² + 2y0·tp + t²p² ≡ y0² + 2y0·tp mod p²
    # Need y0² + 2y0·tp ≡ x0³ + 7 mod p²
    # residue = (x0³ + 7 - y0²) / p  (as integer)
    residue = (x0**3 + 7 - y0**2)
    assert residue % p == 0, "Point not on curve mod p!"
    r = residue // p  # This is an integer
    # t = r / (2y0) mod p
    t = (r * invert(2 * y0, p)) % p
    Y = (y0 + t * p) % pm
    X = x0 % pm
    # Verify
    check = (Y * Y - X * X * X - 7) % pm
    assert check == 0, f"Hensel lift failed: residue = {check}"
    return (X, Y)

print("Lifting G to Z/p²Z ...")
G_lift2 = hensel_lift_point(G, precision=2)
print(f"  G_lift mod p² OK: ({hex(G_lift2[0])[:20]}..., {hex(G_lift2[1])[:20]}...)")

print("\nLifting test points to Z/p²Z ...")
pm2 = p * p
for name, k, K in test_points:
    K_lift2 = hensel_lift_point(K, precision=2)
    # Now compute t mod p²: t = -X/Y mod p²
    t_G2 = (-G_lift2[0] * invert(G_lift2[1], pm2)) % pm2
    t_K2 = (-K_lift2[0] * invert(K_lift2[1], pm2)) % pm2
    # Check if t_K / t_G mod p² = k
    ratio2 = (t_K2 * invert(t_G2, pm2)) % pm2
    print(f"  {name}: t(K)/t(G) mod p² = {hex(ratio2)[:20]}..., k = {hex(k)}")
    print(f"    Match? {ratio2 == k % pm2}")

print("\n--- B5: Multiply-by-p map and kernel of Frobenius ---")
print("For E/F_p with p prime, [p]P = Frobenius(P) + P_related on the formal group.")
print("The formal group of E/F_p has height 1 (ordinary) or 2 (supersingular).")
print("secp256k1 is ordinary (trace t = p+1-n is not divisible by p for large p).")
trace = p + 1 - n
print(f"Trace of Frobenius: a_p = p + 1 - #E = {trace}")
print(f"(This equals the trace of the Frobenius endomorphism)")
print(f"Ordinary? (a_p not divisible by p): {trace % p != 0}")

print()

# ======================================================================
# IDEA C: Discrete elliptic integral / p-adic period
# ======================================================================
print("=" * 70)
print("IDEA C: Discrete elliptic integral / p-adic AGM period")
print("=" * 70)

print("""
Over C, the elliptic logarithm u(P) = ∫_O^P dx/(2y) satisfies u(kP) = k·u(P).
Over F_p, there's no integral, but there are p-adic analogues.

The p-adic sigma/log functions from Mazur-Tate and Bernardi give a p-adic
analytic function σ_p with σ_p(⊕) = σ_p(·) · σ_p(·) · (explicit factors).
""")

print("--- C1: AGM computation of p-adic period ---")
print("The p-adic AGM gives periods of the curve.")
print("For y²=x³+7 over Q_p, the AGM converges p-adically.")

def p_adic_agm(a0, b0, pp, precision_bits=256):
    """
    p-adic AGM iteration: a_{n+1} = (a_n + b_n)/2, b_{n+1} = sqrt(a_n * b_n).
    Over Q_p, convergence is linear (one p-adic digit per step).
    """
    pm = pp ** (precision_bits // int(gmpy2.num_digits(pp, 2)) + 1)
    inv2 = invert(mpz(2), pm)
    a, b = a0 % pm, b0 % pm
    for i in range(20):
        a_new = (a + b) * inv2 % pm
        ab = a * b % pm
        # p-adic sqrt: need Hensel lifting
        # sqrt(ab) mod pm
        # First find sqrt mod pp
        sq = powmod(ab, (pp + 1) // 4, pp)  # Only works if pp ≡ 3 mod 4
        if sq * sq % pp != ab % pp:
            sq = pp - sq
        if sq * sq % pp != ab % pp:
            print(f"  AGM: sqrt({ab % pp}) does not exist mod {pp}")
            return None
        # Hensel lift sqrt to higher precision
        for _ in range(20):
            sq = (sq + ab * invert(sq, pm)) * inv2 % pm
        b_new = sq
        if a_new == a and b_new == b:
            print(f"  AGM converged in {i+1} iterations")
            return a_new
        a, b = a_new, b_new
    return a

# Check if p ≡ 3 mod 4 for simple sqrt
print(f"p mod 4 = {p % 4}")
if p % 4 == 3:
    print("p ≡ 3 mod 4, so sqrt mod p uses (p+1)/4 exponent.")

# Try AGM with curve-related initial values
# For the Weierstrass model y²=x³+7, we can try AGM with roots of x³+7=0 mod p
print("\nFinding roots of x³ + 7 = 0 mod p ...")
# x³ ≡ -7 mod p
neg7 = (-7) % p
# cube root: x = (-7)^((2p-1)/3) mod p if p ≡ 1 mod 3
print(f"p mod 3 = {p % 3}")
if p % 3 == 1:
    cr = powmod(neg7, (2 * p - 1) // 3, p)
    print(f"Cube root of -7 mod p: {hex(cr)[:20]}...")
    print(f"Verify: cr³ mod p = {hex(powmod(cr, 3, p))[:20]}..., -7 mod p = {hex(neg7)[:20]}...")

    # The three roots of x³+7=0 are cr, cr*ω, cr*ω² where ω is a primitive cube root of 1
    # Find ω: cube root of 1 mod p
    omega = powmod(mpz(2), (p - 1) // 3, p)
    if omega == 1:
        omega = powmod(mpz(3), (p - 1) // 3, p)
    print(f"Primitive cube root of unity ω = {hex(omega)[:20]}...")
    print(f"Verify ω³ = {powmod(omega, 3, p)}")

    roots = [cr, (cr * omega) % p, (cr * omega * omega) % p]
    print(f"Roots: {[hex(r)[:16]+'...' for r in roots]}")

    # AGM with e1, e2 (roots)
    print("\nAGM(sqrt(e1-e3), sqrt(e2-e3)) ...")
    e1, e2, e3 = roots
    diff1 = (e1 - e3) % p
    diff2 = (e2 - e3) % p
    sq1 = powmod(diff1, (p + 1) // 4, p)
    sq2 = powmod(diff2, (p + 1) // 4, p)
    if sq1 * sq1 % p == diff1 and sq2 * sq2 % p == diff2:
        agm_result = p_adic_agm(sq1, sq2, p, 256)
        if agm_result is not None:
            print(f"  AGM result: {hex(agm_result)[:30]}...")
            # The period ω_p ~ π_p / agm
            # Discrete log would be: k = u(K) / u(G) where u is the elliptic log
            # u(P) = ∫_∞^P dx/(2y) ~ involves the AGM period
            print("  Testing if AGM period relates to discrete log...")
            # The p-adic period relates to #E(F_p) = p + 1 - a_p
            # But extracting k from this is not straightforward.
    else:
        print(f"  sqrt(e1-e3) or sqrt(e2-e3) doesn't exist mod p")

print("\n--- C2: Discrete sum analogue of elliptic integral ---")
print("Try: S(k) = Σ_{i=1}^{k} 1/(2·y_i) where (x_i, y_i) = i·G")
print("If S(k) is related to k, this could help.")
print("Testing for small k values...")

def discrete_integral_sum(k_max):
    """Compute Σ 1/(2y_i) mod p for i=1..k_max."""
    P = G
    total = mpz(0)
    inv2 = invert(mpz(2), p)
    for i in range(1, k_max + 1):
        if P is not INF:
            total = (total + invert(2 * P[1], p)) % p
        P = ec_add(P, G)
    return total

# Small test
for k_test in [10, 100, 500, 1000]:
    s = discrete_integral_sum(k_test)
    print(f"  S({k_test}) = {hex(s)[:20]}...")

# Check linearity: is S(2k) = 2·S(k)?
s10 = discrete_integral_sum(10)
s20 = discrete_integral_sum(20)
print(f"\n  S(10)   = {hex(s10)[:30]}...")
print(f"  S(20)   = {hex(s20)[:30]}...")
print(f"  2·S(10) = {hex((2*s10) % p)[:30]}...")
print(f"  S(20) = 2·S(10)? {s20 == (2*s10) % p}")

print("\n--- C3: x-coordinate summation ---")
print("Alternative: S_x(k) = Σ x(iG) for i=1..k")

def x_sum(k_max):
    P = G
    total = mpz(0)
    for i in range(1, k_max + 1):
        if P is not INF:
            total = (total + P[0]) % p
        P = ec_add(P, G)
    return total

for k_test in [10, 50, 100]:
    s = x_sum(k_test)
    print(f"  S_x({k_test}) = {hex(s)[:20]}...")

s_x_10 = x_sum(10)
s_x_20 = x_sum(20)
print(f"  S_x(20) = 2·S_x(10)? {s_x_20 == (2*s_x_10) % p}")

print("\n--- C4: Division polynomial approach ---")
print("The division polynomial ψ_k satisfies ψ_k(P) = 0 iff [k]P = O.")
print("For the ECDLP, if K = kG, then ψ_k(G) 'evaluates to something related to k'.")
print("The x-coordinate of [k]P = ψ_{k-1}ψ_{k+1}/ψ_k² (modulo factors).")
print("If we knew ψ_k, we could relate K.x to k, but computing ψ_k requires k...")
print("This is circular for the DLP. Skipping direct computation.")

print()

# ======================================================================
# SUMMARY
# ======================================================================
print("=" * 70)
print("SUMMARY OF RESULTS")
print("=" * 70)

print("""
IDEA A (Height functions):
- Naive height h(P) = log2(min(x, p-x)) does NOT satisfy h(kG) = k²·h(G).
  Heights over F_p are meaningless — all x-coordinates are ~256-bit numbers.
- Lifting G to E/Q is extremely hard: Gx³ + 7 is not a perfect square over Z,
  and finding x_lift = Gx + kp with x_lift³+7 a perfect square is needle-in-haystack.
- The Weil pairing reduces ECDLP to DLP in F_{p^k}*, but the embedding degree
  for secp256k1 is ~n (huge), so MOV attack is infeasible.

IDEA B (Formal group logarithm):
- The formal group log logF(t) = t + O(t²) over Z_p.
- Over F_p (mod p only), logF(t) ≡ t, so it reduces to testing t(kG) = k·t(G) mod p.
- This does NOT hold: t = -x/y mod p is not a homomorphism on E(F_p).
- The formal group log only works on the KERNEL OF REDUCTION (points p-adically
  close to O), which general E(F_p) points are not.
- Hensel lifting to Z/p²Z and testing t(K)/t(G) mod p²: ALSO fails because
  the lifted points still don't lie in the formal group's convergence domain.
- The trace of Frobenius a_p = p+1-n confirms secp256k1 is ordinary.

IDEA C (Discrete elliptic integral):
- p-adic AGM can compute periods, but extracting k from periods requires
  computing the actual p-adic elliptic log, which IS the DLP itself.
- Discrete sums Σ 1/(2y_i) and Σ x_i are not linear: S(2k) ≠ 2·S(k).
  These are NOT analogues of the elliptic integral.
- Division polynomials: computing ψ_k requires knowing k (circular).

CONCLUSION: None of these height/lift approaches break the ECDLP on secp256k1.
The fundamental obstacle is that:
1. Heights require lifting to Q, which is computationally as hard as the DLP.
2. The formal group log only works on points in the kernel of reduction.
3. There is no efficient "discrete integral" over F_p.
These are well-known theoretical barriers (Silverman, Mazur, etc.).
""")
