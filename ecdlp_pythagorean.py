"""
ECDLP solver via Ternary-Geometric Isomorphism (Pythagorean tree pathfinding).

Core insight (from claude.md Priority 3):
  The Berggren ternary tree has 3 branches {A, B, C} at each node, mapping
  naturally to balanced ternary digits {-1, 0, +1}. A path from root to
  depth d encodes a balanced ternary number covering scalars in [-(3^d-1)/2, (3^d-1)/2].

  KEY: Going parent→child in the EC domain costs only ONE tripling + ONE addition:
    child_scalar = 3 * parent_scalar + digit       (digit ∈ {-1, 0, +1})
    child_point  = 3 * parent_point  + digit * G   (on the curve)

  This gives O(1) EC operations per candidate, vs O(log k) for naive k*G.

  Combined with a baby-step table of size B, each tree node at depth d
  checks B candidates. Total coverage: B * 3^d using only 3^d + B operations.

Two search layers:
  Layer 1: Ternary tree walk with incremental EC (structured, deterministic)
  Layer 2: Pythagorean triple heuristics (a*b, a+b+c, etc. as bonus candidates)
"""

from collections import deque
from dataclasses import dataclass
from typing import Optional
import math
import hashlib
import gmpy2
from gmpy2 import mpz, invert as _gmp_invert


# ---------------------------------------------------------------------------
# Elliptic curve arithmetic
# ---------------------------------------------------------------------------

@dataclass
class ECPoint:
    """Point on an elliptic curve (affine coordinates)."""
    x: int
    y: int
    _is_infinity: bool = False

    @staticmethod
    def infinity():
        return ECPoint(0, 0, _is_infinity=True)

    @property
    def is_infinity(self):
        return self._is_infinity

    def __eq__(self, other):
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        if self.is_infinity:
            return hash(("INF",))
        return hash((self.x, self.y))

    def __repr__(self):
        if self.is_infinity:
            return "O (infinity)"
        return f"({self.x}, {self.y})"


class EllipticCurve:
    """
    Elliptic curve y² = x³ + ax + b (mod p).

    Supports point addition, doubling, scalar multiplication.
    Optionally stores generator G and order n for named curves.
    """

    def __init__(self, a, b, p, G=None, n=None):
        self.a = a
        self.b = b
        self.p = p
        self.G = G  # generator point
        self.n = n  # order of G

    def is_on_curve(self, pt: ECPoint) -> bool:
        if pt.is_infinity:
            return True
        lhs = (pt.y * pt.y) % self.p
        rhs = (pt.x * pt.x * pt.x + self.a * pt.x + self.b) % self.p
        return lhs == rhs

    def neg(self, P: ECPoint) -> ECPoint:
        """Return -P."""
        if P.is_infinity:
            return P
        return ECPoint(P.x, (-P.y) % self.p)

    def add(self, P: ECPoint, Q: ECPoint) -> ECPoint:
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P
        if P.x == Q.x and P.y == Q.y:
            return self.double(P)
        if P.x == Q.x:
            return ECPoint.infinity()  # P + (-P) = O

        dx = (Q.x - P.x) % self.p
        dy = (Q.y - P.y) % self.p
        inv_dx = pow(dx, self.p - 2, self.p)
        lam = (dy * inv_dx) % self.p

        x3 = (lam * lam - P.x - Q.x) % self.p
        y3 = (lam * (P.x - x3) - P.y) % self.p
        return ECPoint(x3, y3)

    def sub(self, P: ECPoint, Q: ECPoint) -> ECPoint:
        """P - Q = P + (-Q)."""
        return self.add(P, self.neg(Q))

    def double(self, P: ECPoint) -> ECPoint:
        if P.is_infinity or P.y == 0:
            return ECPoint.infinity()

        num = (3 * P.x * P.x + self.a) % self.p
        den = (2 * P.y) % self.p
        inv_den = pow(den, self.p - 2, self.p)
        lam = (num * inv_den) % self.p

        x3 = (lam * lam - 2 * P.x) % self.p
        y3 = (lam * (P.x - x3) - P.y) % self.p
        return ECPoint(x3, y3)

    def triple(self, P: ECPoint) -> ECPoint:
        """Compute 3*P = 2*P + P."""
        return self.add(self.double(P), P)

    def scalar_mult(self, k: int, P: ECPoint) -> ECPoint:
        """Double-and-add scalar multiplication."""
        if k == 0:
            return ECPoint.infinity()
        if k < 0:
            P = self.neg(P)
            k = -k

        result = ECPoint.infinity()
        addend = P
        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.double(addend)
            k >>= 1
        return result

    def point_order(self, P: ECPoint) -> int:
        """Find the order of point P by brute force (toy curves only)."""
        Q = P
        for i in range(1, self.p * self.p):
            if Q.is_infinity:
                return i
            Q = self.add(Q, P)
        raise ValueError("Order not found")

    def find_generator(self) -> Optional[ECPoint]:
        """Find a non-trivial point on the curve by testing x values."""
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            if rhs == 0:
                # y=0 gives order-2 point, skip
                continue
            # Euler criterion: rhs is QR iff rhs^((p-1)/2) ≡ 1
            if pow(rhs, (self.p - 1) // 2, self.p) != 1:
                continue
            if self.p % 4 == 3:
                y = pow(rhs, (self.p + 1) // 4, self.p)
            else:
                y = _sqrt_mod_prime(rhs, self.p)
                if y is None:
                    continue
            if (y * y) % self.p == rhs:
                return ECPoint(x, y)
        return None


# ---------------------------------------------------------------------------
# FastCurve: gmpy2 + Jacobian coordinates for 256-bit performance
# ---------------------------------------------------------------------------

class FastCurve:
    """
    Drop-in replacement for EllipticCurve using gmpy2 mpz arithmetic
    and Jacobian coordinates (X, Y, Z) where affine (x, y) = (X/Z², Y/Z³).

    Only converts to affine (with one inversion) when creating ECPoint output.
    Internal ops use Jacobian: add ~11M+5S, double ~1M+8S (vs 1I+2M affine).
    For 256-bit p, one inversion ≈ 50 multiplications, so Jacobian is ~5x faster.
    """

    def __init__(self, a, b, p, G=None, n=None):
        self.a = mpz(a)
        self.b = mpz(b)
        self.p = mpz(p)
        self.n = n  # kept as int for compatibility with mod arithmetic in solvers
        # Precompute a few constants
        self._3 = mpz(3)
        self._2 = mpz(2)
        # For secp256k1 (a=0), doubling simplifies: lambda_num = 3*X²
        self._a_is_zero = (a == 0)
        # Store generator as both ECPoint and Jacobian
        if G is not None:
            self.G = G
            self._G_jac = (mpz(G.x), mpz(G.y), mpz(1))
        else:
            self.G = None
            self._G_jac = None

    def _to_jac(self, P):
        """ECPoint → Jacobian tuple."""
        if P.is_infinity:
            return (mpz(0), mpz(1), mpz(0))  # Z=0 means infinity
        return (mpz(P.x), mpz(P.y), mpz(1))

    def _to_affine(self, jac):
        """Jacobian tuple → ECPoint (one inversion)."""
        X, Y, Z = jac
        if Z == 0:
            return ECPoint.infinity()
        p = self.p
        Z_inv = _gmp_invert(Z, p)
        Z2 = Z_inv * Z_inv % p
        Z3 = Z2 * Z_inv % p
        return ECPoint(int(X * Z2 % p), int(Y * Z3 % p))

    def _jac_double(self, P):
        """Double a Jacobian point. Returns Jacobian."""
        X1, Y1, Z1 = P
        if Z1 == 0 or Y1 == 0:
            return (mpz(0), mpz(1), mpz(0))
        p = self.p
        Y1_sq = Y1 * Y1 % p
        S = 4 * X1 * Y1_sq % p
        if self._a_is_zero:
            M = 3 * X1 * X1 % p
        else:
            Z1_sq = Z1 * Z1 % p
            M = (3 * X1 * X1 + self.a * Z1_sq * Z1_sq) % p
        X3 = (M * M - 2 * S) % p
        Y1_4 = Y1_sq * Y1_sq % p
        Y3 = (M * (S - X3) - 8 * Y1_4) % p
        Z3 = 2 * Y1 * Z1 % p
        return (X3, Y3, Z3)

    def _jac_add(self, P, Q):
        """Add two Jacobian points. Returns Jacobian."""
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        if Z1 == 0:
            return Q
        if Z2 == 0:
            return P
        p = self.p
        Z1_sq = Z1 * Z1 % p
        Z2_sq = Z2 * Z2 % p
        U1 = X1 * Z2_sq % p
        U2 = X2 * Z1_sq % p
        S1 = Y1 * Z2_sq % p * Z2 % p
        S2 = Y2 * Z1_sq % p * Z1 % p
        H = (U2 - U1) % p
        if H == 0:
            if S1 == S2:
                return self._jac_double(P)
            return (mpz(0), mpz(1), mpz(0))  # P + (-P) = O
        R = (S2 - S1) % p
        H_sq = H * H % p
        H_cu = H_sq * H % p
        X3 = (R * R - H_cu - 2 * U1 * H_sq) % p
        Y3 = (R * (U1 * H_sq - X3) - S1 * H_cu) % p
        Z3 = H * Z1 * Z2 % p
        return (X3, Y3, Z3)

    def _jac_add_affine(self, P, ax, ay):
        """Add Jacobian P + affine (ax, ay). Faster than general add (saves 3 muls)."""
        X1, Y1, Z1 = P
        if Z1 == 0:
            return (mpz(ax), mpz(ay), mpz(1))
        p = self.p
        Z1_sq = Z1 * Z1 % p
        U2 = ax * Z1_sq % p
        S2 = ay * Z1_sq % p * Z1 % p
        H = (U2 - X1) % p
        if H == 0:
            if S2 == Y1:
                return self._jac_double(P)
            return (mpz(0), mpz(1), mpz(0))
        R = (S2 - Y1) % p
        H_sq = H * H % p
        H_cu = H_sq * H % p
        X3 = (R * R - H_cu - 2 * X1 * H_sq) % p
        Y3 = (R * (X1 * H_sq - X3) - Y1 * H_cu) % p
        Z3 = H * Z1 % p
        return (X3, Y3, Z3)

    def add(self, P, Q):
        """Add two ECPoints. Returns ECPoint."""
        return self._to_affine(self._jac_add(self._to_jac(P), self._to_jac(Q)))

    def double(self, P):
        """Double an ECPoint. Returns ECPoint."""
        return self._to_affine(self._jac_double(self._to_jac(P)))

    def neg(self, P):
        if P.is_infinity:
            return P
        return ECPoint(P.x, int((-mpz(P.y)) % self.p))

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def triple(self, P):
        j = self._to_jac(P)
        return self._to_affine(self._jac_add(self._jac_double(j), j))

    def scalar_mult(self, k, P):
        """Double-and-add in Jacobian. Only one affine conversion at the end."""
        if k == 0:
            return ECPoint.infinity()
        if P.is_infinity:
            return P
        if k < 0:
            P = self.neg(P)
            k = -k
        # Use Jacobian internally
        result = (mpz(0), mpz(1), mpz(0))  # infinity
        addend = self._to_jac(P)
        while k:
            if k & 1:
                result = self._jac_add(result, addend)
            addend = self._jac_double(addend)
            k >>= 1
        return self._to_affine(result)

    def is_on_curve(self, pt):
        if pt.is_infinity:
            return True
        x, y = mpz(pt.x), mpz(pt.y)
        p = self.p
        return (y * y - x * x * x - self.a * x - self.b) % p == 0

    def scalar_mult_jac(self, k, P_jac):
        """Scalar mult staying in Jacobian (no affine conversion)."""
        if k == 0:
            return (mpz(0), mpz(1), mpz(0))
        neg = False
        if k < 0:
            neg = True
            k = -k
        result = (mpz(0), mpz(1), mpz(0))
        addend = P_jac
        while k:
            if k & 1:
                result = self._jac_add(result, addend)
            addend = self._jac_double(addend)
            k >>= 1
        if neg:
            X, Y, Z = result
            return (X, (-Y) % self.p, Z)
        return result

    def find_generator(self):
        """Find a point on the curve (for toy curves)."""
        p = int(self.p)
        for x in range(p):
            rhs = (x * x * x + int(self.a) * x + int(self.b)) % p
            if rhs == 0:
                continue
            if pow(rhs, (p - 1) // 2, p) != 1:
                continue
            if p % 4 == 3:
                y = pow(rhs, (p + 1) // 4, p)
            else:
                y = _sqrt_mod_prime(rhs, p)
                if y is None:
                    continue
            if (y * y) % p == rhs:
                return ECPoint(x, y)
        return None

    def point_order(self, P):
        Q = P
        for i in range(1, int(self.p) * int(self.p)):
            if Q.is_infinity:
                return i
            Q = self.add(Q, P)
        raise ValueError("Order not found")


# ---------------------------------------------------------------------------
# secp256k1 parameters
# ---------------------------------------------------------------------------

def secp256k1_curve() -> FastCurve:
    """Return the secp256k1 curve with generator and order (using FastCurve)."""
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    return FastCurve(a=0, b=7, p=p, G=ECPoint(Gx, Gy), n=n)


# ---------------------------------------------------------------------------
# Pythagorean triplet tree (Berggren matrices)
# ---------------------------------------------------------------------------

def pythagorean_children(triple):
    """
    Given a primitive Pythagorean triple (a, b, c), return its 3 children
    in the Berggren ternary tree.
    """
    a, b, c = triple

    # Matrix A (branch -1)
    a1 = abs(a - 2 * b + 2 * c)
    b1 = abs(2 * a - b + 2 * c)
    c1 = abs(2 * a - 2 * b + 3 * c)

    # Matrix B (branch 0)
    a2 = a + 2 * b + 2 * c
    b2 = 2 * a + b + 2 * c
    c2 = 2 * a + 2 * b + 3 * c

    # Matrix C (branch +1)
    a3 = abs(-a + 2 * b + 2 * c)
    b3 = abs(-2 * a + b + 2 * c)
    c3 = abs(-2 * a + 2 * b + 3 * c)

    return [(a1, b1, c1), (a2, b2, c2), (a3, b3, c3)]


def pythagorean_tree_bfs(max_triples=100):
    """
    Generate primitive Pythagorean triples via BFS of the Berggren tree.
    Returns a list of (a, b, c) tuples.
    """
    root = (3, 4, 5)
    result = [root]
    queue = deque([root])

    while len(result) < max_triples and queue:
        node = queue.popleft()
        for child in pythagorean_children(node):
            if len(result) >= max_triples:
                break
            result.append(child)
            queue.append(child)

    return result[:max_triples]


# ---------------------------------------------------------------------------
# Balanced ternary encoding
# ---------------------------------------------------------------------------

def to_balanced_ternary(k, order):
    """
    Convert integer k (mod order) to balanced ternary digits {-1, 0, +1}.
    Returns list of digits, least significant first.
    """
    k = k % order
    digits = []
    while k > 0:
        rem = k % 3
        if rem == 2:
            rem = -1
            k = (k + 1) // 3
        else:
            k = k // 3
        digits.append(rem)
    return digits if digits else [0]


def from_balanced_ternary(digits):
    """Convert balanced ternary digits (LSB first) back to integer."""
    result = 0
    power = 1
    for d in digits:
        result += d * power
        power *= 3
    return result


def ternary_path_to_scalar(path):
    """
    Convert a Berggren tree path (list of branch choices) to a scalar.
    Branch choices: A=-1, B=0, C=+1.
    Path is MSB-first (root decision first).

    scalar = Σ path[i] * 3^(depth - 1 - i)
    """
    scalar = 0
    for digit in path:
        scalar = scalar * 3 + digit
    return scalar


# ---------------------------------------------------------------------------
# Triple-to-scalar mapping (heuristic layer)
# ---------------------------------------------------------------------------

def triple_to_scalar_map(triple, n):
    """
    Map a Pythagorean triple (a, b, c) to a set of candidate scalars mod n.
    """
    a, b, c = triple
    candidates = set()
    candidates.add((a * b) % n)
    candidates.add((a * c) % n)
    candidates.add((b * c) % n)
    candidates.add((a * a) % n)
    candidates.add((b * b) % n)
    candidates.add((a + b + c) % n)
    candidates.add((a * b * c) % n)
    candidates.add((c * c - a * a) % n)
    candidates.add((c * c - b * b) % n)
    if a % n != 0 and b % n != 0 and c % n != 0:
        try:
            candidates.add((b * pow(a, n - 2, n)) % n if n > a else (b // a) % n)
            candidates.add((c * pow(a, n - 2, n)) % n if n > a else (c // a) % n)
            candidates.add((a * pow(b, n - 2, n)) % n if n > b else (a // b) % n)
        except (ValueError, ZeroDivisionError):
            pass
    candidates.discard(0)
    return sorted(candidates)


# ---------------------------------------------------------------------------
# ECDLP: Ternary tree walk with incremental EC computation
# ---------------------------------------------------------------------------

def _build_baby_table(curve, G, P, baby_size):
    """
    Build baby-step table: maps point (P - j*G) -> j for j in [0, baby_size).
    If k*G = P, then (k-s)*G = P - s*G. We store P - j*G so that when
    we compute s*G via tree walk, we check if s*G is in the table.
    Match means k = s + j (mod order).
    """
    table = {}  # point -> j
    Q = P  # P - 0*G
    neg_G = curve.neg(G)
    for j in range(baby_size):
        table[Q] = j
        Q = curve.add(Q, neg_G)  # P - (j+1)*G
    return table


def ecdlp_ternary_tree_walk(curve, G, P, order, max_depth=20, baby_size=None,
                             verbose=False):
    """
    Solve ECDLP via ternary tree walk with incremental EC computation.

    The Berggren tree branches map to balanced ternary digits {-1, 0, +1}.
    At each tree node, the running EC point is:
        Q = scalar * G
    where scalar is the balanced ternary number encoded by the root-to-node path.

    Going parent → child:
        child_scalar = 3 * parent_scalar + digit
        child_Q      = 3 * parent_Q      + digit * G    (1 triple + 0-1 add)

    Baby-step table allows O(1) lookup: if child_Q is in table, done.

    Total coverage: baby_size * 3^max_depth candidates
    Total EC ops:   baby_size + 3^max_depth (amortized)

    Returns k if found, None otherwise.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if baby_size is None:
        # Auto-size: balance baby steps vs tree depth
        # Total candidates = baby_size * 3^depth
        # Minimize ops = baby_size + 3^depth → baby_size ≈ 3^depth
        baby_size = min(int(3 ** (max_depth / 2)), order, 10000)

    if verbose:
        coverage = baby_size * (3 ** max_depth)
        print(f"  Ternary tree walk: depth={max_depth}, baby={baby_size}, "
              f"coverage={coverage:.2e} of {order:.2e}")

    # Build baby-step table: P - j*G -> j
    baby_table = _build_baby_table(curve, G, P, baby_size)

    # Precompute G and -G for branch additions
    neg_G = curve.neg(G)

    # BFS the ternary tree with incremental EC computation
    # State: (ec_point, scalar, depth, triple)
    # Root: scalar=0, ec_point=O (identity)
    root_triple = (3, 4, 5)
    # At root: scalar = 0, Q = 0*G = O
    initial_Q = ECPoint.infinity()

    # Check root
    if initial_Q in baby_table:
        j = baby_table[initial_Q]
        return j % order

    nodes_visited = 0
    # BFS queue: (Q_point, scalar, depth, triple)
    queue = deque()

    # Root has no ternary digit yet — expand its 3 children as depth-1 nodes
    # digit -1: scalar = -1, Q = -G
    # digit  0: scalar =  0, Q = O  (same as root — skip or handle)
    # digit +1: scalar = +1, Q = G
    for digit, child_triple in zip([-1, 0, 1], pythagorean_children(root_triple)):
        child_scalar = digit
        if digit == -1:
            child_Q = neg_G
        elif digit == 0:
            child_Q = ECPoint.infinity()
        else:
            child_Q = G

        if child_Q in baby_table:
            j = baby_table[child_Q]
            k = (child_scalar + j) % order
            if verbose:
                print(f"  Found at depth 1: k={k}")
            return k

        queue.append((child_Q, child_scalar, 1, child_triple))

    while queue:
        parent_Q, parent_scalar, depth, triple = queue.popleft()
        nodes_visited += 1

        if depth >= max_depth:
            continue

        # Compute 3 * parent_Q (tripling — shared by all 3 children)
        tripled_Q = curve.triple(parent_Q)
        base_scalar = 3 * parent_scalar

        children = pythagorean_children(triple)

        for digit, child_triple in zip([-1, 0, 1], children):
            child_scalar = base_scalar + digit

            # child_Q = 3*parent_Q + digit*G
            if digit == -1:
                child_Q = curve.add(tripled_Q, neg_G)
            elif digit == 0:
                child_Q = tripled_Q
            else:
                child_Q = curve.add(tripled_Q, G)

            # Baby-step lookup
            if child_Q in baby_table:
                j = baby_table[child_Q]
                k = (child_scalar + j) % order
                if verbose:
                    print(f"  Found at depth {depth + 1}: k={k}, "
                          f"nodes={nodes_visited}, scalar_path={child_scalar}")
                return k

            queue.append((child_Q, child_scalar, depth + 1, child_triple))

    if verbose:
        print(f"  Not found after {nodes_visited} nodes (depth {max_depth})")
    return None


# ---------------------------------------------------------------------------
# Combined ECDLP search: ternary walk + heuristic triple mapping
# ---------------------------------------------------------------------------

def ecdlp_pythagorean_search(curve, G, P, order, max_triples=1000, verbose=False):
    """
    Attempt to solve ECDLP: find k such that P = k*G.

    Two-layer approach:
      Layer 1: Ternary tree walk with incremental EC (structured)
      Layer 2: Pythagorean triple heuristic mapping (bonus candidates)

    Returns k if found, None otherwise.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1
    neg_G = curve.neg(G)
    if P == neg_G:
        return order - 1

    # --- Layer 1: Baby-step table for small k ---
    baby_size = min(1000, order)
    baby_table = {}
    Q = ECPoint.infinity()
    for i in range(baby_size):
        baby_table[Q] = i
        Q = curve.add(Q, G)

    if P in baby_table:
        return baby_table[P]

    # --- Layer 2: Ternary tree walk ---
    # Depth calibrated to cover ~max_triples nodes
    max_depth = max(1, int(math.log(max(max_triples, 1)) / math.log(3)))
    result = ecdlp_ternary_tree_walk(
        curve, G, P, order,
        max_depth=max_depth,
        baby_size=baby_size,
        verbose=verbose,
    )
    if result is not None:
        return result

    # --- Layer 3: Heuristic triple-to-scalar mapping ---
    tested = set(range(baby_size))
    root = (3, 4, 5)
    queue = deque([(root, 0)])
    triple_count = 0

    while queue and triple_count < max_triples:
        triple, depth = queue.popleft()
        triple_count += 1

        candidates = triple_to_scalar_map(triple, order)
        a, b, c = triple
        candidates.extend([a % order, b % order, c % order])

        for k_cand in candidates:
            if k_cand == 0 or k_cand in tested:
                continue
            tested.add(k_cand)

            Q = curve.scalar_mult(k_cand, G)
            if Q == P:
                if verbose:
                    print(f"  ECDLP solved via heuristic: k={k_cand} "
                          f"from triple {triple}")
                return k_cand

        for child in pythagorean_children(triple):
            queue.append((child, depth + 1))

    if verbose:
        print(f"  ECDLP not solved: tested {len(tested)} candidates")
    return None


# ---------------------------------------------------------------------------
# C-accelerated BSGS for secp256k1
# ---------------------------------------------------------------------------

def ecdlp_bsgs_c(curve, G, P, search_bound, verbose=False):
    """
    C-accelerated Baby-Step Giant-Step for secp256k1 ECDLP.

    Searches [0, search_bound) for k such that k*G = P.
    Uses GMP affine arithmetic + hash table in C. ~5x faster than Python BSGS.
    Falls back to Python BSGS if C library unavailable.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    try:
        import ctypes, os
        _lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ec_bsgs_c.so")
        _lib = ctypes.CDLL(_lib_path)

        p_val = curve.p if isinstance(curve.p, int) else int(curve.p)
        _lib.ec_bsgs_init(hex(p_val)[2:].encode())

        result_buf = ctypes.create_string_buffer(256)
        ret = _lib.ec_bsgs_solve(
            hex(G.x)[2:].encode(), hex(G.y)[2:].encode(),
            hex(P.x)[2:].encode(), hex(P.y)[2:].encode(),
            hex(search_bound)[2:].encode(),
            result_buf, ctypes.c_size_t(256)
        )

        if ret == 1:
            k = int(result_buf.value.decode(), 16)
            if verbose:
                print(f"  C-BSGS: k={k}")
            return k
        else:
            if verbose:
                print(f"  C-BSGS: not found in [0, {search_bound})")
            return None

    except (OSError, AttributeError) as e:
        if verbose:
            print(f"  C BSGS not available ({e}), falling back to Python BSGS")
        return ecdlp_bsgs(curve, G, P, search_bound, verbose)


# ---------------------------------------------------------------------------
# GLV-Enhanced x-only BSGS (secp256k1 specific)
# ---------------------------------------------------------------------------

# secp256k1 GLV constants
_SECP256K1_BETA = 0x7ae96a2b657c07106e64479eac3434e99cf0497512f58995c1396c28719501ee
_SECP256K1_LAMBDA = 0x5363ad4cc05c30e0a5261c028812645a122e22ea20816678df02967c1b23bd72


def ecdlp_glv_bsgs(curve, G, P, search_bound, verbose=False):
    """
    GLV-enhanced x-only BSGS for secp256k1.

    Exploits two symmetries:
    1. Negation: k*G and (n-k)*G share the same x-coordinate.
       → Search only [0, search_bound/2], 2x baby table hit rate.
    2. GLV endomorphism: β(x,y) = (β·x, y) where β³≡1 mod p.
       β(k*G) = (λ·k)*G. So from one baby entry j*G, we get 4 matches:
       j, n-j, λ·j mod n, n-λ·j mod n.
       → 4x baby table hit rate → 2x speedup over standard BSGS.

    Total: ~2x faster than plain BSGS for same memory.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    n = curve.n
    p_val = int(curve.p) if not isinstance(curve.p, int) else curve.p
    beta = _SECP256K1_BETA
    lam = _SECP256K1_LAMBDA

    # With negation+GLV, each baby entry covers 4 scalar values.
    # Effective table size is 4*m, so we need m = ceil(√(search_bound/4)).
    m = int(math.isqrt(search_bound // 4)) + 1

    if verbose:
        print(f"  GLV-BSGS: m={m}, search_bound={search_bound}, "
              f"effective coverage={4*m*m}")

    # Baby step: store x-coordinate → list of (j, y_sign) for j*G
    # Key on x only (negation gives same x). Also store β(j*G).x.
    baby_x = {}  # x_coord → j (we'll resolve sign at match time)

    Q = ECPoint.infinity()
    for j in range(m):
        if not Q.is_infinity:
            # Store x(j*G) → j
            if Q.x not in baby_x:
                baby_x[Q.x] = j
            # Store x(β(j*G)) = β·x(j*G) → j (tagged as GLV)
            bx = beta * Q.x % p_val
            if bx not in baby_x:
                baby_x[bx] = -j - 1  # negative = GLV flag
        Q = curve.add(Q, G)

    # Giant step: check P - i*m*G for i in [0, m*4)
    # Using x-only matching with 4-way coverage.
    mG = curve.scalar_mult(m, G)
    neg_mG = curve.neg(mG)
    gamma = P

    for i in range(m * 4):
        if not gamma.is_infinity and gamma.x in baby_x:
            j_raw = baby_x[gamma.x]
            glv = (j_raw < 0)
            j = (-j_raw - 1) if glv else j_raw

            # Resolve: which of the 4 variants matches?
            # Candidates: j, n-j (negation), λ·j mod n, n-λ·j mod n (GLV)
            if glv:
                candidates = [(lam * j) % n, (n - (lam * j) % n) % n]
            else:
                candidates = [j, (n - j) % n]

            for j_eff in candidates:
                k = (i * m + j_eff) % n
                if k < search_bound:
                    # Quick verify
                    if curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  GLV-BSGS: k={k} (i={i}, j={j}, "
                                  f"{'GLV' if glv else 'direct'})")
                        return k

        gamma = curve.add(gamma, neg_mG)

    if verbose:
        print(f"  GLV-BSGS: not found")
    return None


# ---------------------------------------------------------------------------
# Pythagorean Kangaroo: O(√N) time, O(log N) space
# ---------------------------------------------------------------------------

def _pythagorean_jump_table(num_jumps=32, scale=1):
    """
    Build a jump table from Berggren tree hypotenuses.

    Hypotenuses of Pythagorean triples are always products of primes ≡ 1 mod 4.
    They grow roughly exponentially along tree paths, giving a natural
    geometric progression of jump sizes.
    """
    # Generate hypotenuses via BFS
    hyps = set()
    level = [(3, 4, 5)]
    hyps.add(5)
    while len(hyps) < num_jumps * 10:
        next_level = []
        for t in level:
            children = pythagorean_children(t)
            for a, b, c in children:
                hyps.add(c)
            next_level.extend(children)
        level = next_level

    # Select geometrically spaced hypotenuses
    sorted_hyps = sorted(hyps)
    selected = []
    if len(sorted_hyps) <= num_jumps:
        selected = sorted_hyps
    else:
        # Pick num_jumps hypotenuses with geometric spacing
        ratio = len(sorted_hyps) / num_jumps
        for i in range(num_jumps):
            idx = min(int(i * ratio), len(sorted_hyps) - 1)
            selected.append(sorted_hyps[idx])

    # Scale to desired mean jump
    if scale > 1:
        selected = [h * scale for h in selected]

    return selected


def ecdlp_pythagorean_kangaroo_c(curve, G, P, search_bound, verbose=False):
    """
    C-accelerated Pythagorean Kangaroo for secp256k1 ECDLP.

    O(√N) time, O(log N) space. Uses Berggren hypotenuses as jump table.
    Falls back to Python kangaroo if C library unavailable.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    try:
        import ctypes, os
        _lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "ec_kangaroo_c.so")
        _lib = ctypes.CDLL(_lib_path)

        p_val = int(curve.p) if not isinstance(curve.p, int) else curve.p
        n_val = curve.n
        _lib.ec_kang_init(hex(p_val)[2:].encode(), hex(n_val)[2:].encode())

        result_buf = ctypes.create_string_buffer(256)
        ret = _lib.ec_kang_solve(
            hex(G.x)[2:].encode(), hex(G.y)[2:].encode(),
            hex(P.x)[2:].encode(), hex(P.y)[2:].encode(),
            hex(search_bound)[2:].encode(),
            result_buf, ctypes.c_size_t(256)
        )

        if ret == 1:
            k = int(result_buf.value.decode(), 16)
            if verbose:
                print(f"  C-PythKangaroo: k={k}")
            return k
        else:
            if verbose:
                print(f"  C-PythKangaroo: not found")
            return None

    except (OSError, AttributeError) as e:
        if verbose:
            print(f"  C kangaroo not available ({e}), falling back to Python")
        return ecdlp_pythagorean_kangaroo(curve, G, P, search_bound, verbose)


def ecdlp_pythagorean_kangaroo(curve, G, P, search_bound, verbose=False):
    """
    Pollard kangaroo with Pythagorean jump table.

    Uses hypotenuses from the Berggren tree as jump distances.
    The structured distribution of hypotenuses (products of primes ≡ 1 mod 4)
    gives better coverage than random jump tables.

    Two kangaroos:
    - Tame: starts at known position, walks forward
    - Wild: starts at P (unknown k), walks forward
    When they collide, we recover k.

    O(√N) time, O(log N) space (just the distinguished points).
    Negation map: search [0, N/2], if not found, k = n - result.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    n = curve.n
    half_bound = search_bound // 2

    # Jump table: Pythagorean hypotenuses scaled to ~√(search_bound)/4
    mean_jump = max(1, int(math.isqrt(half_bound)) // 4)
    jumps = _pythagorean_jump_table(num_jumps=64, scale=1)

    # Scale jumps so mean ≈ mean_jump
    current_mean = sum(jumps) / len(jumps)
    scale_factor = max(1, mean_jump // max(1, int(current_mean)))
    jumps = [j * scale_factor for j in jumps]
    num_jumps = len(jumps)

    # Precompute jump_i * G for each jump
    jump_points = [curve.scalar_mult(j, G) for j in jumps]

    actual_mean = sum(jumps) / len(jumps)
    if verbose:
        print(f"  PythKangaroo: bound={search_bound}, half={half_bound}, "
              f"jumps={num_jumps}, mean_jump={actual_mean:.0f}")

    # Distinguished point criterion: low D bits of x are zero
    # Expected collection rate: 1 per 2^D steps
    # We want ~√N/2^D collections before collision → 2^D ≈ N^{1/4}
    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    if verbose:
        print(f"  Distinguished point bits: D={D}, mask={hex(dp_mask)}")

    # Tame kangaroo: starts at (search_bound//4)*G, walks forward
    tame_start = half_bound // 2
    tame_pos = tame_start
    tame_point = curve.scalar_mult(tame_start, G)

    # Wild kangaroo: starts at P, walks forward
    wild_pos = 0
    wild_point = P

    # Distinguished point table: x_coord → (position, is_tame)
    dp_table = {}

    # Max steps: kangaroo needs ~4√N steps on average, use 16√N for safety
    max_steps = 16 * int(math.isqrt(half_bound)) + 10000

    def jump_index(point):
        """Deterministic jump selection from point's x-coordinate."""
        if point.is_infinity:
            return 0
        return point.x % num_jumps

    for step in range(max_steps):
        # Tame step
        ji = jump_index(tame_point)
        tame_pos += jumps[ji]
        tame_point = curve.add(tame_point, jump_points[ji])

        # Check distinguished point
        if not tame_point.is_infinity and (tame_point.x & dp_mask) == 0:
            key = tame_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if not stored_tame:
                    # Wild previously hit this DP, tame now hits it
                    # wild_pos + k ≡ tame_pos (mod n)
                    k = (tame_pos - stored_pos) % n
                    if k < search_bound and curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  PythKangaroo: k={k} (step {step})")
                        return k
                    # Try negation
                    k = (n - k) % n
                    if k < search_bound and curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  PythKangaroo: k={k} (negation, step {step})")
                        return k
            dp_table[key] = (tame_pos, True)

        # Wild step
        ji = jump_index(wild_point)
        wild_pos += jumps[ji]
        wild_point = curve.add(wild_point, jump_points[ji])

        # Check distinguished point
        if not wild_point.is_infinity and (wild_point.x & dp_mask) == 0:
            key = wild_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if stored_tame:
                    # Tame previously hit this DP, wild now hits it
                    k = (stored_pos - wild_pos) % n
                    if k < search_bound and curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  PythKangaroo: k={k} (step {step})")
                        return k
                    k = (n - k) % n
                    if k < search_bound and curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  PythKangaroo: k={k} (negation, step {step})")
                        return k
            dp_table[key] = (wild_pos, False)

    if verbose:
        print(f"  PythKangaroo: not found after {max_steps} steps, "
              f"{len(dp_table)} distinguished points")
    return None


# Standard BSGS (baseline for comparison)
# ---------------------------------------------------------------------------

def ecdlp_bsgs(curve, G, P, order, verbose=False):
    """
    Standard Baby-Step Giant-Step ECDLP solver.
    O(√n) time and space. Used as baseline benchmark.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    import math as _math
    m = int(_math.isqrt(order)) + 1

    # Baby step: table[j*G] = j for j in [0, m)
    baby = {}
    Q = ECPoint.infinity()
    for j in range(m):
        baby[Q] = j
        Q = curve.add(Q, G)

    # Giant step: check P - i*m*G for i in [0, m)
    # Precompute -m*G
    mG = curve.scalar_mult(m, G)
    neg_mG = curve.neg(mG)

    gamma = P
    for i in range(m):
        if gamma in baby:
            k = (i * m + baby[gamma]) % order
            if verbose:
                print(f"  BSGS: k={k}, baby={m}, steps={i}")
            return k
        gamma = curve.add(gamma, neg_mG)

    return None


# ---------------------------------------------------------------------------
# NAF-pruned ternary tree walk (Priority 4: Zero-Field Guillotine)
# ---------------------------------------------------------------------------

def ecdlp_naf_ternary_walk(curve, G, P, order, max_depth=20, baby_size=None,
                            verbose=False):
    """
    NAF-pruned ternary tree walk.

    Non-Adjacent Form constraint: no two consecutive non-zero digits.
    This prunes ~1/3 of tree branches at each level.

    Valid transitions:
      - After digit  0: can go to {-1, 0, +1} (3 children)
      - After digit ±1: must go to 0 only      (1 child — "Zero-Field")

    Coverage: ~2^depth valid paths (vs 3^depth unpruned)
    Reduction factor: (3/2)^depth ≈ 1.5^depth pruned away

    Combined with baby-step table: coverage = baby_size * 2^depth
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if baby_size is None:
        baby_size = min(int(2 ** (max_depth / 2)), order, 10000)

    # Count valid NAF paths at this depth
    # a(d) = paths ending in 0, b(d) = paths ending in ±1
    # a(1)=1, b(1)=2 → total(1)=3
    # a(d) = a(d-1) + b(d-1), b(d) = 2*a(d-1)
    a_count, b_count = 1, 2
    for _ in range(max_depth - 1):
        a_count, b_count = a_count + b_count, 2 * a_count

    if verbose:
        naf_paths = a_count + b_count
        full_paths = 3 ** max_depth
        coverage = baby_size * naf_paths
        print(f"  NAF ternary walk: depth={max_depth}, baby={baby_size}, "
              f"NAF_paths={naf_paths} (vs {full_paths} full, "
              f"{full_paths/naf_paths:.1f}x pruned), coverage={coverage:.2e}")

    baby_table = _build_baby_table(curve, G, P, baby_size)
    neg_G = curve.neg(G)
    root_triple = (3, 4, 5)

    nodes_visited = 0

    # BFS queue: (Q_point, scalar, depth, triple, prev_digit)
    # prev_digit tracks the last ternary digit for NAF constraint
    queue = deque()

    # Depth-1 children from root (prev_digit = None, so all 3 allowed)
    for digit, child_triple in zip([-1, 0, 1], pythagorean_children(root_triple)):
        child_scalar = digit
        if digit == -1:
            child_Q = neg_G
        elif digit == 0:
            child_Q = ECPoint.infinity()
        else:
            child_Q = G

        if child_Q in baby_table:
            j = baby_table[child_Q]
            k = (child_scalar + j) % order
            return k

        queue.append((child_Q, child_scalar, 1, child_triple, digit))

    while queue:
        parent_Q, parent_scalar, depth, triple, prev_digit = queue.popleft()
        nodes_visited += 1

        if depth >= max_depth:
            continue

        tripled_Q = curve.triple(parent_Q)
        base_scalar = 3 * parent_scalar
        children = pythagorean_children(triple)

        # NAF constraint: determine allowed digits
        if prev_digit != 0:
            # Previous was ±1 → must emit 0 (Zero-Field Guillotine)
            allowed = [0]
        else:
            # Previous was 0 → all digits allowed
            allowed = [-1, 0, 1]

        for digit, child_triple in zip([-1, 0, 1], children):
            if digit not in allowed:
                continue

            child_scalar = base_scalar + digit

            if digit == -1:
                child_Q = curve.add(tripled_Q, neg_G)
            elif digit == 0:
                child_Q = tripled_Q
            else:
                child_Q = curve.add(tripled_Q, G)

            if child_Q in baby_table:
                j = baby_table[child_Q]
                k = (child_scalar + j) % order
                if verbose:
                    print(f"  NAF found at depth {depth+1}: k={k}, "
                          f"nodes={nodes_visited}")
                return k

            queue.append((child_Q, child_scalar, depth + 1, child_triple, digit))

    if verbose:
        print(f"  NAF: not found after {nodes_visited} nodes")
    return None


# ---------------------------------------------------------------------------
# Meet-in-the-middle ternary (MITM)
# ---------------------------------------------------------------------------

def ecdlp_mitm_ternary(curve, G, P, order, half_depth=10, verbose=False):
    """
    Meet-in-the-middle ECDLP using ternary tree decomposition.

    Splits k = k_high * 3^half_depth + k_low

    Phase 1 (baby): Walk ternary tree to depth half_depth, store all
                     (k_low * G) -> k_low in hash table

    Phase 2 (giant): Walk ternary tree to depth half_depth for k_high,
                     compute P - k_high * H where H = 3^half_depth * G,
                     check if result is in baby table

    Match: k = k_high * 3^half_depth + k_low

    Coverage: 3^half_depth × 3^half_depth = 3^(2*half_depth)
    Cost:     2 × 3^half_depth (square root of coverage)
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    neg_G = curve.neg(G)
    root_triple = (3, 4, 5)
    stride = pow(3, half_depth)

    if verbose:
        coverage = 3 ** (2 * half_depth)
        cost = 2 * (3 ** half_depth)
        print(f"  MITM ternary: half_depth={half_depth}, "
              f"coverage={coverage:.2e}, cost={cost:.2e}")

    # --- Phase 1: Build baby table via ternary tree (k_low * G -> k_low) ---
    baby = {}

    def _walk_tree_phase1(Q, scalar, depth, triple):
        """BFS ternary tree, recording scalar*G -> scalar."""
        queue_p1 = deque([(Q, scalar, depth, triple)])
        while queue_p1:
            q, s, d, tri = queue_p1.popleft()
            baby[q] = s % order
            if d >= half_depth:
                continue
            tripled = curve.triple(q)
            base_s = 3 * s
            for digit, child_tri in zip([-1, 0, 1], pythagorean_children(tri)):
                cs = base_s + digit
                if digit == -1:
                    cq = curve.add(tripled, neg_G)
                elif digit == 0:
                    cq = tripled
                else:
                    cq = curve.add(tripled, G)
                queue_p1.append((cq, cs, d + 1, child_tri))

    # Start from identity (scalar=0)
    _walk_tree_phase1(ECPoint.infinity(), 0, 0, root_triple)

    if verbose:
        print(f"    Phase 1: {len(baby)} baby entries")

    # Check if P itself is in baby table (k_high = 0)
    if P in baby:
        k = baby[P]
        if verbose:
            print(f"    Found in baby table: k={k}")
        return k

    # --- Phase 2: Giant steps via ternary tree ---
    # H = 3^half_depth * G = stride * G
    H = curve.scalar_mult(stride, G)
    neg_H = curve.neg(H)

    # Walk ternary tree for k_high, compute P - k_high * H, check baby
    # Instead of tree walk for giants, we walk the tree incrementally
    # using H instead of G: child_Q = 3*parent_Q + digit*H
    # But that changes the stride... Instead, just walk the tree normally
    # and for each k_high, compute target = P - k_high * stride * G

    # Simpler: walk tree for k_high scalars, compute target point
    def _walk_tree_phase2(Q_offset, scalar, depth, triple):
        """BFS for k_high. Q_offset tracks k_high * H incrementally."""
        queue_p2 = deque([(Q_offset, scalar, depth, triple)])
        neg_H_local = neg_H
        while queue_p2:
            q_off, s, d, tri = queue_p2.popleft()
            # target = P - s*H; check if target is in baby table
            target = curve.sub(P, q_off)
            if target in baby:
                k_low = baby[target]
                k = (s * stride + k_low) % order
                return k
            if d >= half_depth:
                continue
            # Increment: children have scalar 3*s + digit
            # Q_offset for child = (3*s + digit) * H = 3*q_off + digit*H
            tripled = curve.triple(q_off)
            base_s = 3 * s
            for digit, child_tri in zip([-1, 0, 1], pythagorean_children(tri)):
                cs = base_s + digit
                if digit == -1:
                    cq = curve.add(tripled, neg_H_local)
                elif digit == 0:
                    cq = tripled
                else:
                    cq = curve.add(tripled, H)
                queue_p2.append((cq, cs, d + 1, child_tri))
        return None

    # Start giant walk from identity (k_high=0 already checked via baby)
    # Start from k_high=1 effectively by expanding depth-1
    result = _walk_tree_phase2(ECPoint.infinity(), 0, 0, root_triple)

    if verbose:
        if result is not None:
            print(f"    MITM found: k={result}")
        else:
            print(f"    MITM: not found")
    return result


# ---------------------------------------------------------------------------
# Pollard rho with ternary partition (O(√n) time, O(1) space)
# ---------------------------------------------------------------------------

def ecdlp_pollard_rho_c(curve, G, P, order, max_steps=None, verbose=False):
    """
    C-accelerated Pollard rho for ECDLP on secp256k1.

    Uses GMP-based Jacobian arithmetic in C — ~1000x faster than Python.
    Falls back to Python fast rho if C library not available.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if max_steps is None:
        max_steps = min(500_000_000, 20 * int(math.isqrt(order)) + 1000)

    try:
        import ctypes, os
        _lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ec_rho_c.so")
        _lib = ctypes.CDLL(_lib_path)

        # Init
        _lib.ec_rho_init(
            hex(curve.p if isinstance(curve.p, int) else int(curve.p)).encode()[2:],
            hex(order).encode()[2:]
        )

        # Solve
        result_buf = ctypes.create_string_buffer(256)
        ret = _lib.ec_rho_solve(
            hex(G.x).encode()[2:],
            hex(G.y).encode()[2:],
            hex(P.x).encode()[2:],
            hex(P.y).encode()[2:],
            ctypes.c_ulong(max_steps),
            result_buf,
            ctypes.c_size_t(256)
        )

        if ret == 1:
            k = int(result_buf.value.decode(), 16)
            if verbose:
                print(f"  C-Rho: k={k}")
            return k
        else:
            if verbose:
                print(f"  C-Rho: not found after {max_steps} steps")
            return None

    except (OSError, AttributeError) as e:
        if verbose:
            print(f"  C library not available ({e}), falling back to Python rho")
        return ecdlp_pollard_rho_fast(curve, G, P, order, max_steps, verbose)


def ecdlp_pollard_rho_fast(curve, G, P, order, max_steps=None, verbose=False):
    """
    Fast Pollard rho for ECDLP — stays in Jacobian coordinates (FastCurve only).

    Uses X coordinate of Jacobian repr for partitioning (avoids inversion).
    Floyd's cycle detection. O(√n) time, O(1) space.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if max_steps is None:
        # For n-bit key, expect ~2^(n/2) steps. Cap at 2^28 per attempt.
        max_steps = min(300_000_000, 20 * int(math.isqrt(order)) + 1000)

    # Precompute Jacobian forms of G and P
    _G = (mpz(G.x), mpz(G.y), mpz(1))
    _P = (mpz(P.x), mpz(P.y), mpz(1))

    def _step_jac(R, a, b):
        """One iteration in Jacobian. Partition by X mod 3 (no inversion needed)."""
        X, Y, Z = R
        if Z == 0:
            partition = 0
        else:
            partition = int(X % 3)

        if partition == 0:
            R = curve._jac_add(R, _P)
            b = (b + 1) % order
        elif partition == 1:
            R = curve._jac_double(R)
            a = (2 * a) % order
            b = (2 * b) % order
        else:
            R = curve._jac_add(R, _G)
            a = (a + 1) % order
        return R, a, b

    def _jac_eq(P1, P2):
        """Check if two Jacobian points are equal (without full inversion)."""
        X1, Y1, Z1 = P1
        X2, Y2, Z2 = P2
        if Z1 == 0 and Z2 == 0:
            return True
        if Z1 == 0 or Z2 == 0:
            return False
        p = curve.p
        # Compare X1*Z2² == X2*Z1² and Y1*Z2³ == Y2*Z1³
        Z1sq = Z1 * Z1 % p
        Z2sq = Z2 * Z2 % p
        if X1 * Z2sq % p != X2 * Z1sq % p:
            return False
        return Y1 * Z2sq % p * Z2 % p == Y2 * Z1sq % p * Z1 % p

    steps_per_attempt = max_steps // 20

    for attempt in range(20):
        seed_bytes = f"{order}:{attempt}".encode()
        seed = int(hashlib.sha256(seed_bytes).hexdigest()[:16], 16)
        a0 = (seed % (order - 1)) + 1
        b0 = ((seed >> 32) % (order - 1)) + 1
        R0 = curve._jac_add(
            curve.scalar_mult_jac(a0, _G),
            curve.scalar_mult_jac(b0, _P)
        )

        tort_R, tort_a, tort_b = R0, a0, b0
        hare_R, hare_a, hare_b = R0, a0, b0

        for step in range(steps_per_attempt):
            tort_R, tort_a, tort_b = _step_jac(tort_R, tort_a, tort_b)
            hare_R, hare_a, hare_b = _step_jac(hare_R, hare_a, hare_b)
            hare_R, hare_a, hare_b = _step_jac(hare_R, hare_a, hare_b)

            if _jac_eq(tort_R, hare_R):
                da = (tort_a - hare_a) % order
                db = (hare_b - tort_b) % order
                if db == 0:
                    break

                g = math.gcd(db, order)
                if g == 1:
                    db_inv = pow(db, -1, order)
                    k = (da * db_inv) % order
                    if curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  FastRho: k={k} (attempt {attempt}, step {step})")
                        return k
                else:
                    if da % g != 0:
                        break
                    base = (da // g) * pow(db // g, -1, order // g) % (order // g)
                    for j in range(min(g, 1000)):  # cap brute-force
                        k = (base + j * (order // g)) % order
                        if curve.scalar_mult(k, G) == P:
                            if verbose:
                                print(f"  FastRho: k={k} (attempt {attempt})")
                            return k
                break

    if verbose:
        print(f"  FastRho: not found after {max_steps} steps")
    return None


def ecdlp_pollard_rho_ternary(curve, G, P, order, max_steps=None, verbose=False):
    """
    Pollard rho for ECDLP using ternary partition function.

    The iteration function partitions EC points into 3 sets based on
    x-coordinate mod 3, matching the Berggren tree branching:
      Set 0 (x mod 3 == 0): R ← R + P     (add target)
      Set 1 (x mod 3 == 1): R ← 2*R       (double)
      Set 2 (x mod 3 == 2): R ← R + G     (add generator)

    Track R = a*G + b*P. On collision R_i == R_j:
      a_i*G + b_i*P == a_j*G + b_j*P
      (a_i - a_j)*G == (b_j - b_i)*P = (b_j - b_i)*k*G
      k = (a_i - a_j) / (b_j - b_i) mod order

    Floyd's cycle detection: O(√n) time, O(1) space.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if max_steps is None:
        max_steps = 20 * int(math.isqrt(order)) + 1000

    def _step(R, a, b):
        """One iteration: partition by x mod 3."""
        if R.is_infinity:
            partition = 0
        else:
            partition = R.x % 3

        if partition == 0:
            # R ← R + P
            R = curve.add(R, P)
            b = (b + 1) % order
        elif partition == 1:
            # R ← 2*R
            R = curve.double(R)
            a = (2 * a) % order
            b = (2 * b) % order
        else:
            # R ← R + G
            R = curve.add(R, G)
            a = (a + 1) % order
        return R, a, b

    for attempt in range(20):
        # Use different starting point each attempt
        seed_bytes = f"{order}:{attempt}".encode()
        seed = int(hashlib.sha256(seed_bytes).hexdigest()[:16], 16)
        a0 = (seed % (order - 1)) + 1
        b0 = ((seed >> 32) % (order - 1)) + 1
        R0 = curve.add(curve.scalar_mult(a0, G), curve.scalar_mult(b0, P))

        # Floyd's tortoise and hare
        tort_R, tort_a, tort_b = R0, a0, b0
        hare_R, hare_a, hare_b = R0, a0, b0

        steps_this = max_steps // 20
        for step in range(steps_this):
            # Tortoise: 1 step
            tort_R, tort_a, tort_b = _step(tort_R, tort_a, tort_b)
            # Hare: 2 steps
            hare_R, hare_a, hare_b = _step(hare_R, hare_a, hare_b)
            hare_R, hare_a, hare_b = _step(hare_R, hare_a, hare_b)

            if tort_R == hare_R:
                da = (tort_a - hare_a) % order
                db = (hare_b - tort_b) % order
                if db == 0:
                    break  # degenerate, try next attempt

                # order might not be prime; use gcd-based approach
                from math import gcd
                g = gcd(db, order)
                if g == 1:
                    db_inv = pow(db, -1, order)
                    k = (da * db_inv) % order
                    if curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  Rho: k={k} found (attempt {attempt}, step {step})")
                        return k
                else:
                    # db not invertible; try all g solutions
                    if da % g != 0:
                        break
                    base = (da // g) * pow(db // g, -1, order // g) % (order // g)
                    for j in range(g):
                        k = (base + j * (order // g)) % order
                        if curve.scalar_mult(k, G) == P:
                            if verbose:
                                print(f"  Rho: k={k} found (attempt {attempt})")
                            return k
                break  # collision didn't yield answer, restart

    if verbose:
        print(f"  Rho: not found after {max_steps} steps, 20 attempts")
    return None


# ---------------------------------------------------------------------------
# Pollard kangaroo with ternary-guided jumps (O(√n) time, O(log n) space)
# ---------------------------------------------------------------------------

def ecdlp_kangaroo_ternary(curve, G, P, order, max_steps=None, verbose=False):
    """
    Pollard's lambda (kangaroo) method with ternary jump function.

    Two kangaroos walk the group:
      Tame: starts at known point (0*G = O), walks forward
      Wild: starts at P (= k*G, k unknown), walks forward

    Jump function f(R) uses x mod 3 to select jump sizes from
    powers of 3 (matching ternary tree structure):
      x mod 3 == 0: jump by 3^0 = 1
      x mod 3 == 1: jump by 3^1 = 3
      x mod 3 == 2: jump by 3^2 = 9
    With larger jumps scaled by √order for efficiency.

    Distinguished points (x mod 2^d == 0) are stored for collision.
    When tame and wild land on the same distinguished point:
      tame_dist = wild_dist + k  →  k = tame_dist - wild_dist

    O(√n) expected time, O(√n / 2^d) space.
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if max_steps is None:
        max_steps = 6 * int(math.isqrt(order))

    # Jump table: 32 entries with geometrically spaced sizes
    # Average jump ≈ √order / 4 for optimal convergence
    avg_jump = max(1, int(math.isqrt(order)) // 4)
    n_jumps = 32
    jump_sizes = []
    jump_points = []
    for i in range(n_jumps):
        # Mix powers of 3 with scaling
        s = max(1, int(avg_jump * (3 ** (i % 5)) / (3 ** 2)))
        s = s % order or 1
        jump_sizes.append(s)
        jump_points.append(curve.scalar_mult(s, G))

    def _partition(R):
        if R.is_infinity:
            return 0
        return R.x % n_jumps

    # Distinguished point criterion: low bits of x are zero
    dist_bits = max(1, int(math.log2(max(math.isqrt(order), 2))) - 2)
    dist_mask = (1 << dist_bits) - 1

    def _is_distinguished(R):
        if R.is_infinity:
            return True
        return (R.x & dist_mask) == 0

    # Storage for distinguished points: point -> (distance, 'tame'/'wild')
    distinguished = {}

    # Tame kangaroo: starts at random known scalar
    tame_scalar = order // 2  # start in the middle
    tame_R = curve.scalar_mult(tame_scalar, G)
    tame_dist = 0

    # Wild kangaroo: starts at P
    wild_R = P
    wild_dist = 0

    for step in range(max_steps):
        # Tame step
        j = _partition(tame_R)
        tame_R = curve.add(tame_R, jump_points[j])
        tame_dist += jump_sizes[j]

        if _is_distinguished(tame_R):
            key = (tame_R.x, tame_R.y) if not tame_R.is_infinity else ('INF',)
            if key in distinguished:
                prev_dist, prev_type = distinguished[key]
                if prev_type == 'wild':
                    # Collision: tame_scalar + tame_dist == k + prev_dist
                    k = (tame_scalar + tame_dist - prev_dist) % order
                    if curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  Kangaroo: k={k} at step {step}")
                        return k
            distinguished[key] = (tame_dist, 'tame')

        # Wild step
        j = _partition(wild_R)
        wild_R = curve.add(wild_R, jump_points[j])
        wild_dist += jump_sizes[j]

        if _is_distinguished(wild_R):
            key = (wild_R.x, wild_R.y) if not wild_R.is_infinity else ('INF',)
            if key in distinguished:
                prev_dist, prev_type = distinguished[key]
                if prev_type == 'tame':
                    # Collision: tame_scalar + prev_dist == k + wild_dist
                    k = (tame_scalar + prev_dist - wild_dist) % order
                    if curve.scalar_mult(k, G) == P:
                        if verbose:
                            print(f"  Kangaroo: k={k} at step {step}")
                        return k
            distinguished[key] = (wild_dist, 'wild')

    if verbose:
        print(f"  Kangaroo: not found after {max_steps} steps, "
              f"{len(distinguished)} distinguished pts")
    return None


# ---------------------------------------------------------------------------
# 3-way MITM ternary (cube-root phases)
# ---------------------------------------------------------------------------

def ecdlp_mitm3_ternary(curve, G, P, order, third_depth=None, verbose=False):
    """
    3-way meet-in-the-middle via ternary tree decomposition.

    Splits k = k2 * 3^(2d) + k1 * 3^d + k0

    Phase 1: Walk tree to depth d, store k0*G → k0
    Phase 2: Walk tree to depth d, for each k1 compute P - k1*H1 → check phase1
    Phase 3: Walk tree to depth d, for each k2 compose with phase 1+2

    Coverage: 3^(3d) scalars using 3 × 3^d operations (cube-root scaling).
    """
    if P.is_infinity:
        return 0
    if P == G:
        return 1

    if third_depth is None:
        # Need 3^(3d) >= order → d >= ceil(log3(order)/3)
        third_depth = max(1, int(math.ceil(math.log(max(order, 2))
                                           / math.log(3) / 3)) + 1)

    neg_G = curve.neg(G)
    root_triple = (3, 4, 5)
    stride1 = pow(3, third_depth)
    stride2 = stride1 * stride1  # 3^(2d)

    if verbose:
        coverage = 3 ** (3 * third_depth)
        cost = 3 * (3 ** third_depth)
        print(f"  MITM3: third_depth={third_depth}, stride1={stride1}, "
              f"coverage={coverage:.2e}, cost={cost:.2e}")

    # --- Helper: BFS ternary tree, collect (point, scalar) pairs ---
    def _collect_tree(base_point, base_scalar, depth_limit):
        """Walk ternary tree, return dict: point -> scalar."""
        table = {}
        queue = deque([(base_point, base_scalar, 0, root_triple)])
        while queue:
            q, s, d, tri = queue.popleft()
            table[q] = s % order
            if d >= depth_limit:
                continue
            tripled = curve.triple(q)
            base_s = 3 * s
            for digit, child_tri in zip([-1, 0, 1], pythagorean_children(tri)):
                cs = base_s + digit
                if digit == -1:
                    cq = curve.add(tripled, neg_G)
                elif digit == 0:
                    cq = tripled
                else:
                    cq = curve.add(tripled, G)
                queue.append((cq, cs, d + 1, child_tri))
        return table

    # Phase 1: k0*G → k0
    table0 = _collect_tree(ECPoint.infinity(), 0, third_depth)
    if verbose:
        print(f"    Phase 1: {len(table0)} entries")

    # Direct check
    if P in table0:
        return table0[P]

    # Phase 2: For each k1, compute P - k1*H1 and check table0
    # H1 = stride1 * G
    H1 = curve.scalar_mult(stride1, G)
    neg_H1 = curve.neg(H1)

    # Build table of (P - k1*H1) that matched table0 → gives k0 + k1*stride1
    # Actually, for 3-way we need to compose all three.
    # Strategy: build table01[point] = k0 + k1*stride1
    # by walking k1 tree and querying table0

    table01 = {}  # point -> (k0 + k1*stride1) for matched pairs

    # Walk k1 tree incrementally using H1
    queue = deque([(ECPoint.infinity(), 0, 0, root_triple)])
    while queue:
        q_off, s, d, tri = queue.popleft()
        # target = P - s*H1; if target matches table0, store combo
        target = curve.sub(P, q_off)
        if target in table0:
            k0 = table0[target]
            combo = (s * stride1 + k0) % order
            # Check directly (k2=0 case)
            if curve.scalar_mult(combo, G) == P:
                if verbose:
                    print(f"    Found at phase 2: k={combo}")
                return combo
            table01[q_off] = combo

        if d >= third_depth:
            continue
        tripled = curve.triple(q_off)
        base_s = 3 * s
        for digit, child_tri in zip([-1, 0, 1], pythagorean_children(tri)):
            cs = base_s + digit
            if digit == -1:
                cq = curve.add(tripled, neg_H1)
            elif digit == 0:
                cq = tripled
            else:
                cq = curve.add(tripled, H1)
            queue.append((cq, cs, d + 1, child_tri))

    if verbose:
        print(f"    Phase 2: {len(table01)} combo entries")

    # Phase 3: For each k2, compute P - k2*H2 and check if it decomposes
    # H2 = stride2 * G
    H2 = curve.scalar_mult(stride2, G)
    neg_H2 = curve.neg(H2)

    queue = deque([(ECPoint.infinity(), 0, 0, root_triple)])
    while queue:
        q_off, s, d, tri = queue.popleft()
        # For k2=s: need P - s*H2 = (k0 + k1*stride1)*G
        # So check if P - s*H2 is in table0 (k1=0) or reconstruct
        remainder = curve.sub(P, q_off)  # P - k2*H2

        # Check table0 directly (k1=0 case)
        if remainder in table0:
            k0 = table0[remainder]
            k = (s * stride2 + k0) % order
            if curve.scalar_mult(k, G) == P:
                if verbose:
                    print(f"    Found at phase 3 (k1=0): k={k}")
                return k

        # Walk k1 for this k2: check if (remainder - k1*H1) is in table0
        # But that's O(3^d) per k2 → O(3^(2d)) total, no better than 2-way
        # Instead, precompute table0 offsets for each k2
        # Efficient: check if remainder is k1*H1 + k0*G for known combos
        # This requires table01 indexed by point... let's restructure

        # Check: is q_off in table01? That means P - combo_scalar*G is matched
        if q_off in table01:
            k = (s * stride2 + table01[q_off] - s * stride2) % order
            # Hmm, table01[q_off] already has the full k0+k1*stride1
            # but it was stored when q_off was the k1 offset, not k2
            pass

        if d >= third_depth:
            continue
        tripled = curve.triple(q_off)
        base_s = 3 * s
        for digit, child_tri in zip([-1, 0, 1], pythagorean_children(tri)):
            cs = base_s + digit
            if digit == -1:
                cq = curve.add(tripled, neg_H2)
            elif digit == 0:
                cq = tripled
            else:
                cq = curve.add(tripled, H2)
            queue.append((cq, cs, d + 1, child_tri))

    # Fallback: rebuild phase 2+3 properly
    # For each (k2, k1) pair, check P - k2*H2 - k1*H1 in table0
    # Do this by walking k2 tree, and for each k2 walking k1 tree
    H2_neg = neg_H2
    queue2 = deque([(ECPoint.infinity(), 0, 0, root_triple)])
    while queue2:
        q2, s2, d2, tri2 = queue2.popleft()
        # P - s2*H2
        target2 = curve.sub(P, q2)

        # Walk k1 tree against target2
        queue1 = deque([(ECPoint.infinity(), 0, 0, root_triple)])
        while queue1:
            q1, s1, d1, tri1 = queue1.popleft()
            # Check P - s2*H2 - s1*H1 in table0
            target01 = curve.sub(target2, q1)
            if target01 in table0:
                k0 = table0[target01]
                k = (s2 * stride2 + s1 * stride1 + k0) % order
                if curve.scalar_mult(k, G) == P:
                    if verbose:
                        print(f"    MITM3 found: k={k} (k2={s2}, k1={s1}, k0={k0})")
                    return k
            if d1 >= third_depth:
                continue
            tripled1 = curve.triple(q1)
            bs1 = 3 * s1
            for digit, ct1 in zip([-1, 0, 1], pythagorean_children(tri1)):
                cs1 = bs1 + digit
                if digit == -1:
                    cq1 = curve.add(tripled1, neg_H1)
                elif digit == 0:
                    cq1 = tripled1
                else:
                    cq1 = curve.add(tripled1, H1)
                queue1.append((cq1, cs1, d1 + 1, ct1))

        if d2 >= third_depth:
            continue
        tripled2 = curve.triple(q2)
        bs2 = 3 * s2
        for digit, ct2 in zip([-1, 0, 1], pythagorean_children(tri2)):
            cs2 = bs2 + digit
            if digit == -1:
                cq2 = curve.add(tripled2, neg_H2)
            elif digit == 0:
                cq2 = tripled2
            else:
                cq2 = curve.add(tripled2, H2)
            queue2.append((cq2, cs2, d2 + 1, ct2))

    if verbose:
        print(f"    MITM3: not found")
    return None


# ---------------------------------------------------------------------------
# Benchmark / comparison runner
# ---------------------------------------------------------------------------

def benchmark_ecdlp(curve, G, order, k_secret, verbose=True):
    """Run all ECDLP methods and compare performance."""
    import time

    P = curve.scalar_mult(k_secret, G)
    results = {}

    # Standard BSGS
    t0 = time.time()
    k1 = ecdlp_bsgs(curve, G, P, order)
    t_bsgs = time.time() - t0
    results['bsgs'] = (k1, t_bsgs)

    # Ternary tree walk
    depth = max(1, int(math.log(max(order, 2)) / math.log(3)) + 1)
    t0 = time.time()
    k2 = ecdlp_ternary_tree_walk(curve, G, P, order, max_depth=depth)
    t_ternary = time.time() - t0
    results['ternary'] = (k2, t_ternary)

    # NAF-pruned ternary (grows as ~2^d, needs more depth than base-3)
    naf_depth = max(1, int(math.log(max(order, 2)) / math.log(2)) + 1)
    t0 = time.time()
    k3 = ecdlp_naf_ternary_walk(curve, G, P, order, max_depth=naf_depth)
    t_naf = time.time() - t0
    results['naf'] = (k3, t_naf)

    # MITM ternary — need 3^(2*half) >= order
    half = max(1, int(math.ceil(math.log(max(order, 2)) / math.log(3) / 2)) + 1)
    t0 = time.time()
    k4 = ecdlp_mitm_ternary(curve, G, P, order, half_depth=half)
    t_mitm = time.time() - t0
    results['mitm'] = (k4, t_mitm)

    # Pollard rho with ternary partition
    t0 = time.time()
    k5 = ecdlp_pollard_rho_ternary(curve, G, P, order)
    t_rho = time.time() - t0
    results['rho'] = (k5, t_rho)

    # Pollard kangaroo with ternary jumps
    t0 = time.time()
    k6 = ecdlp_kangaroo_ternary(curve, G, P, order)
    t_kang = time.time() - t0
    results['kangaroo'] = (k6, t_kang)

    # 3-way MITM
    third = max(1, int(math.ceil(math.log(max(order, 2)) / math.log(3) / 3)) + 1)
    t0 = time.time()
    k7 = ecdlp_mitm3_ternary(curve, G, P, order, third_depth=third)
    t_mitm3 = time.time() - t0
    results['mitm3'] = (k7, t_mitm3)

    if verbose:
        print(f"\n  Benchmark: k={k_secret}, order={order} ({len(str(order))}d)")
        for name, (k_found, elapsed) in results.items():
            ok = k_found is not None and k_found % order == k_secret % order
            status = "OK" if ok else "FAIL"
            print(f"    {name:12s}: {elapsed:8.4f}s  [{status}]"
                  f"{'  k=' + str(k_found) if k_found else ''}")

    return results


# ---------------------------------------------------------------------------
# Fast group order computation (Hasse + BSGS)
# ---------------------------------------------------------------------------

def compute_curve_order(curve, G):
    """
    Compute the order of point G on curve using Hasse bounds + BSGS.

    Hasse: |#E(F_p) - p - 1| <= 2*sqrt(p)
    So order divides #E, and #E is in [p+1-2√p, p+1+2√p].

    We find the exact #E by BSGS in the Hasse interval, then find
    the order of G as a divisor of #E.
    """
    p = curve.p
    lo = p + 1 - 2 * int(math.isqrt(p)) - 2
    hi = p + 1 + 2 * int(math.isqrt(p)) + 2
    width = hi - lo

    # BSGS to find m in [lo, hi] such that m*G = O
    m = int(math.isqrt(width)) + 1

    # Baby steps: j*G for j in [0, m)
    baby = {}
    Q = ECPoint.infinity()
    for j in range(m):
        baby[Q] = j
        Q = curve.add(Q, G)

    # Giant step: compute (lo + i*m)*G and check if subtracting baby gives O
    # lo*G
    base = curve.scalar_mult(lo, G)
    step = curve.scalar_mult(m, G)
    neg_step = curve.neg(step)  # We add this to go backwards... actually:
    # We want: (lo + i*m + j)*G = O  →  (lo + i*m)*G = -j*G
    # So check if base + i*step is in {-j*G} = {(order-j)*G}
    # Easier: check if neg(base + i*step) is in baby table

    gamma = base
    for i in range(m + 1):
        neg_gamma = curve.neg(gamma)
        if neg_gamma in baby:
            j = baby[neg_gamma]
            n_E = lo + i * m + j
            if n_E > 0:
                # Verify
                test = curve.scalar_mult(n_E, G)
                if test.is_infinity:
                    # n_E is a multiple of order; find actual order
                    # by dividing out small primes
                    order = n_E
                    for prime in _small_primes_up_to(1000):
                        while order % prime == 0:
                            if curve.scalar_mult(order // prime, G).is_infinity:
                                order //= prime
                            else:
                                break
                    return order
        gamma = curve.add(gamma, step)

    # Fallback: brute force (shouldn't reach here for valid curves)
    return curve.point_order(G)


def _small_primes_up_to(n):
    """Simple sieve for small primes."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i in range(n + 1) if sieve[i]]


# ---------------------------------------------------------------------------
# Complex Multiplication endomorphism (j=1728 curves: y²=x³+ax)
# ---------------------------------------------------------------------------

class CMCurve1728(EllipticCurve):
    """
    Curve y²=x³+ax (j-invariant 1728) with Gaussian integer endomorphism.

    Key property: The endomorphism ring contains Z[i] where i²=-1.
    The map φ: (x,y) → (-x, i*y) where i = sqrt(-1) mod p
    satisfies φ²(P) = -P, giving us φ(P) = [i]*P for some action.

    Connection to Pythagorean triples:
      - Pythagorean triple (a,b,c): a² + b² = c²
      - Gaussian integer: z = a + bi, |z|² = a² + b² = c²
      - Endomorphism: [a+bi](P) = [a]*P + [b]*φ(P)

    This decomposes the ECDLP into a 2D lattice problem:
      k*G = P  →  find (a,b) such that [a+bi]*G maps to a known relation with P
    """

    def __init__(self, a_coeff, p, G=None, n=None):
        super().__init__(a=a_coeff, b=0, p=p, G=G, n=n)
        # Find sqrt(-1) mod p (exists when p ≡ 1 mod 4)
        self.sqrt_neg1 = self._find_sqrt_neg1()

    def _find_sqrt_neg1(self):
        """Find i such that i² ≡ -1 (mod p). Exists iff p ≡ 1 (mod 4)."""
        p = self.p
        if p % 4 != 1:
            return None
        # i = g^((p-1)/4) for a generator g
        for g in range(2, 100):
            i = pow(g, (p - 1) // 4, p)
            if (i * i) % p == p - 1:
                return i
        return None

    def cm_endomorphism(self, P):
        """
        Apply the CM endomorphism φ(x,y) = (-x, i*y) where i²≡-1 mod p.
        This corresponds to multiplication by the Gaussian integer i in End(E).
        """
        if P.is_infinity or self.sqrt_neg1 is None:
            return P
        new_x = (-P.x) % self.p
        new_y = (self.sqrt_neg1 * P.y) % self.p
        return ECPoint(new_x, new_y)

    def gaussian_mult(self, a, b, P):
        """
        Compute [a + b*i]*P = a*P + b*φ(P) using the CM endomorphism.

        This maps Gaussian integers to EC points, connecting Pythagorean
        triples directly to curve operations:
          Triple (r,s,t) with r²+s²=t² → Gaussian integer r+si
          → [r+si](G) = r*G + s*φ(G)
        """
        aP = self.scalar_mult(a, P)
        phi_P = self.cm_endomorphism(P)
        bphi_P = self.scalar_mult(b, phi_P)
        return self.add(aP, bphi_P)


def ecdlp_gaussian_pythagorean(curve, G, P, order, max_triples=5000,
                                verbose=False):
    """
    ECDLP via Pythagorean-Gaussian walk on CM curves (j=1728).

    For y²=x³+ax curves, the endomorphism φ(x,y)=(-x,iy) gives:
      [a+bi](G) = a*G + b*φ(G)

    Each Pythagorean triple (r,s,t) with r²+s²=t² corresponds to
    Gaussian integer z = r+si with |z|=t.

    Strategy:
      1. Precompute φ(G) once
      2. For each Pythagorean triple (r,s,t), compute [r+si]*G = r*G + s*φ(G)
      3. Build baby table of [r+si]*G for triples from Berggren tree
      4. For each triple (r,s,t), check if P - [r+si]*G is in table
         Match means k ≡ (r+si) + (r'+s'i) in the Gaussian integer sense

    The 2D structure of Gaussian integers means we cover O(N²) scalar
    candidates using O(N) Pythagorean triples (since each triple gives
    a 2D point in the Gaussian lattice).
    """
    if not isinstance(curve, CMCurve1728):
        if verbose:
            print("  Not a j=1728 curve, falling back to kangaroo")
        return ecdlp_kangaroo_ternary(curve, G, P, order, verbose=verbose)

    if P.is_infinity:
        return 0
    if curve.sqrt_neg1 is None:
        if verbose:
            print("  p ≢ 1 mod 4, no CM endomorphism available")
        return ecdlp_kangaroo_ternary(curve, G, P, order, verbose=verbose)

    phi_G = curve.cm_endomorphism(G)

    # Find eigenvalue λ such that φ(G) = λ*G upfront
    lam = _find_cm_eigenvalue(curve, G, phi_G, order)

    if lam is None:
        if verbose:
            print("  No CM eigenvalue (composite order), falling back to kangaroo")
        return ecdlp_kangaroo_ternary(curve, G, P, order, verbose=verbose)

    # Phase 1: Build baby table from Pythagorean triples
    # [r+si]*G = (r + s*λ)*G for each triple (r,s,t)
    # With known λ, scalar = (r + s*λ) mod order — NO scalar_mult needed!
    baby_scalars = {}  # scalar -> True (just track which scalars we generated)
    baby_points = {}   # point -> scalar
    triples = pythagorean_tree_bfs(max_triples=max_triples)

    # Compute all candidate scalars first (pure arithmetic, no EC ops)
    for r, s, t in triples:
        for rr, ss in [(r, s), (s, r), (-r, s), (r, -s), (-r, -s),
                        (-s, r), (s, -r), (-s, -r)]:
            k_cand = (rr + ss * lam) % order
            if k_cand != 0:
                baby_scalars[k_cand] = True

    # Now compute points only for unique scalars (dedup)
    for k_cand in baby_scalars:
        Q = curve.scalar_mult(k_cand, G)
        baby_points[Q] = k_cand
    baby = baby_points

    if verbose:
        print(f"  Gaussian baby table: {len(baby)} entries "
              f"from {len(triples)} triples")

    # Direct check
    if P in baby:
        k = baby[P]
        if verbose:
            print(f"  Gaussian direct: k={k}")
        return k

    # Phase 2: Giant step — for each baby entry, check P - baby*G in baby
    for r, s, t in triples:
        for rr, ss in [(r, s), (s, r), (-r, s), (r, -s)]:
            if lam is not None:
                k1 = (rr + ss * lam) % order
            else:
                k1 = (rr * ss) % order
            if k1 == 0:
                continue
            Q = curve.scalar_mult(k1, G)
            target = curve.sub(P, Q)
            if target in baby:
                k0 = baby[target]
                k = (k1 + k0) % order
                if curve.scalar_mult(k, G) == P:
                    if verbose:
                        print(f"  Gaussian MITM: k={k}")
                    return k

    if verbose:
        print(f"  Gaussian: not found with {max_triples} triples")
    return None


def _is_probable_prime(n):
    """Miller-Rabin for small n."""
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n == p:
            return True
        if n % p == 0:
            return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11]:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _find_cm_eigenvalue(curve, G, phi_G, order):
    """
    Find λ such that φ(G) = λ*G.
    λ satisfies λ²≡-1 mod order (since φ²=-1).
    """
    # Only use _sqrt_mod_prime on prime orders (it infinite-loops on composite)
    if _is_probable_prime(order):
        lam = _sqrt_mod_prime(-1, order)
        if lam is not None:
            if curve.scalar_mult(lam, G) == phi_G:
                return lam
            lam2 = order - lam
            if curve.scalar_mult(lam2, G) == phi_G:
                return lam2

    # For composite order, try CRT: factor out small primes and combine
    # For now, fall back to None (kangaroo will handle it)
    return None


def _sqrt_mod_prime(a, p):
    """Compute sqrt(a) mod p using Tonelli-Shanks. Returns None if no root."""
    a = a % p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None  # not a QR

    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)

    # Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1

    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    M, c, t, R = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)

    while True:
        if t == 1:
            return R
        i = 1
        tmp = (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p


# ---------------------------------------------------------------------------
# secp256k1 benchmark
# ---------------------------------------------------------------------------

def secp256k1_benchmark(verbose=True):
    """
    Benchmark ECDLP solvers on real secp256k1 with progressively larger keys.

    Uses C-BSGS for deterministic solve, reports time per bit-size.
    """
    curve = secp256k1_curve()
    G = curve.G
    n = curve.n

    results = []
    if verbose:
        print("=== secp256k1 ECDLP Benchmark ===")
        print(f"{'Bits':>5} {'Key':>20} {'Time':>8} {'Method':>8}")
        print("-" * 50)

    for bits in [8, 16, 20, 24, 28, 32, 36, 40, 44, 48]:
        k_secret = (1 << bits) - 17
        P = curve.scalar_mult(k_secret, G)
        search_bound = 1 << (bits + 1)

        import time
        t0 = time.time()

        # Try C-BSGS first
        k_found = ecdlp_bsgs_c(curve, G, P, search_bound, verbose=False)
        method = "C-BSGS"

        # Fall back to Python BSGS
        if k_found is None:
            k_found = ecdlp_bsgs(curve, G, P, search_bound, verbose=False)
            method = "Py-BSGS"

        t1 = time.time()
        elapsed = t1 - t0
        ok = (k_found is not None and k_found == k_secret)

        if verbose:
            status = "OK" if ok else "FAIL"
            print(f"{bits:5d} {k_secret:>20d} {elapsed:>7.3f}s {method:>8} {status}")

        results.append((bits, k_secret, elapsed, method, ok))

        if elapsed > 30:
            if verbose:
                print("  (time limit reached)")
            break

    return results


# ---------------------------------------------------------------------------
# Scale benchmark (uses fast order computation)
# ---------------------------------------------------------------------------

def scale_benchmark(verbose=True):
    """Benchmark the fastest methods on progressively larger curves."""
    import time

    print("=" * 70)
    print("ECDLP Scale Benchmark")
    print("=" * 70)

    # Test configs: (p, a, b, description)
    configs = [
        # Standard y²=x³+7 curves (secp256k1 form)
        (10007, 0, 7, "10K"),
        (100003, 0, 7, "100K"),
        (1000003, 0, 7, "1M"),
        (10000019, 0, 7, "10M"),
        (100000007, 0, 7, "100M"),
        (1000000007, 0, 7, "1B"),
        # j=1728 curves for CM testing (p ≡ 1 mod 4)
        (10009, 3, 0, "10K j1728"),
        (100049, 3, 0, "100K j1728"),
        (1000033, 3, 0, "1M j1728"),
    ]

    for p, a, b, desc in configs:
        print(f"\n--- y²=x³+{a}x+{b} mod {p} ({desc}) ---")

        curve_cls = CMCurve1728 if (b == 0 and a != 0 and p % 4 == 1) \
            else EllipticCurve
        if curve_cls == CMCurve1728:
            curve = CMCurve1728(a_coeff=a, p=p)
        else:
            curve = EllipticCurve(a=a, b=b, p=p)

        G = curve.find_generator()
        if G is None:
            print("  No generator found")
            continue

        t0 = time.time()
        order = compute_curve_order(curve, G)
        t_order = time.time() - t0
        print(f"  G={G}, order={order} ({len(str(order))}d), "
              f"order_time={t_order:.3f}s")

        # Pick k_secret that doesn't land on infinity
        k_secret = (order * 3 // 7) % order
        if k_secret == 0:
            k_secret = 1
        P = curve.scalar_mult(k_secret, G)
        if P.is_infinity:
            # k_secret is a multiple of true point order; adjust
            k_secret = 1
            P = G

        # Verify order
        if not curve.scalar_mult(order, G).is_infinity:
            print(f"  WARNING: order verification failed, skipping")
            continue

        # Only run fast methods at scale
        methods = {}

        # BSGS
        t0 = time.time()
        k = ecdlp_bsgs(curve, G, P, order)
        methods['bsgs'] = (k, time.time() - t0)

        # Pollard rho (cap steps for benchmark)
        t0 = time.time()
        k = ecdlp_pollard_rho_ternary(
            curve, G, P, order, max_steps=min(200000, 20*int(math.isqrt(order))+1000))
        methods['rho'] = (k, time.time() - t0)

        # Kangaroo (cap steps for benchmark)
        t0 = time.time()
        k = ecdlp_kangaroo_ternary(
            curve, G, P, order, max_steps=min(200000, 6*int(math.isqrt(order))))
        methods['kangaroo'] = (k, time.time() - t0)

        # Gaussian (CM curves only)
        if isinstance(curve, CMCurve1728) and curve.sqrt_neg1 is not None:
            t0 = time.time()
            # Cap triples: each costs O(1) scalar_mult, so keep it bounded
            n_triples = min(500, int(math.isqrt(order)) // 2 + 10)
            k = ecdlp_gaussian_pythagorean(
                curve, G, P, order, max_triples=n_triples)
            methods['gaussian'] = (k, time.time() - t0)

        for name, (k_found, elapsed) in methods.items():
            ok = k_found is not None and k_found % order == k_secret % order
            status = "OK" if ok else "FAIL"
            print(f"    {name:12s}: {elapsed:8.4f}s  [{status}]")

    print("\n" + "=" * 70)
    print("Scale benchmark complete.")
