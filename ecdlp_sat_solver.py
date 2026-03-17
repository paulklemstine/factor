#!/usr/bin/env python3
"""
SAT-based ECDLP Solver

Encodes elliptic curve discrete logarithm as Boolean satisfiability.
Special handling for congruent number curves E_n: y^2 = x^3 - n^2*x.

Two encoding strategies:
  1. Table-based: for small curves (order < 2^16), encode k*G as a lookup table
     mapping k bits -> (x,y) bits. Very compact, O(order * bits) clauses.
  2. Circuit-based: encode modular arithmetic + EC operations as Boolean circuits.
     Larger but tests how SAT handles the algebraic structure.

Uses PySAT (Glucose3/Cadical) as backend.
"""

import time
import signal
import random
import math
from collections import defaultdict

try:
    from pysat.solvers import Glucose3, Cadical103
    HAS_PYSAT = True
except ImportError:
    try:
        from pysat.solvers import Glucose3
        Cadical103 = None
        HAS_PYSAT = True
    except ImportError:
        HAS_PYSAT = False


# ---------------------------------------------------------------------------
# Variable allocator + CNF
# ---------------------------------------------------------------------------
class VarAlloc:
    def __init__(self):
        self.next_var = 1
    def fresh(self):
        v = self.next_var
        self.next_var += 1
        return v
    def fresh_vec(self, n):
        return [self.fresh() for _ in range(n)]


class CNF:
    def __init__(self, alloc=None):
        self.alloc = alloc or VarAlloc()
        self.clauses = []

    def add(self, clause):
        self.clauses.append(list(clause))

    def fresh(self):
        return self.alloc.fresh()

    def fresh_vec(self, n):
        return self.alloc.fresh_vec(n)

    def num_vars(self):
        return self.alloc.next_var - 1

    def num_clauses(self):
        return len(self.clauses)

    def const_true(self, v):
        self.add([v])

    def const_false(self, v):
        self.add([-v])

    def assign_bit_vec(self, vec, value):
        for i, v in enumerate(vec):
            if (value >> i) & 1:
                self.const_true(v)
            else:
                self.const_false(v)

    def gate_and(self, a, b):
        o = self.fresh()
        self.add([-a, -b, o])
        self.add([a, -o])
        self.add([b, -o])
        return o

    def gate_or(self, a, b):
        o = self.fresh()
        self.add([a, b, -o])
        self.add([-a, o])
        self.add([-b, o])
        return o

    def gate_xor(self, a, b):
        o = self.fresh()
        self.add([-a, -b, -o])
        self.add([a, b, -o])
        self.add([a, -b, o])
        self.add([-a, b, o])
        return o

    def gate_not(self, a):
        o = self.fresh()
        self.add([-a, -o])
        self.add([a, o])
        return o

    def gate_mux(self, sel, a, b):
        """sel ? a : b"""
        o = self.fresh()
        self.add([-sel, -a, o])
        self.add([-sel, a, -o])
        self.add([sel, -b, o])
        self.add([sel, b, -o])
        return o

    def gate_eq(self, a, b):
        x = self.gate_xor(a, b)
        return self.gate_not(x)

    def assert_eq(self, a, b):
        self.add([-a, b])
        self.add([a, -b])

    def vec_mux(self, sel, a_vec, b_vec):
        return [self.gate_mux(sel, a, b) for a, b in zip(a_vec, b_vec)]

    def vec_eq(self, a_vec, b_vec):
        for a, b in zip(a_vec, b_vec):
            self.assert_eq(a, b)


# ---------------------------------------------------------------------------
# Modular Arithmetic (circuit-based for Phase 2+)
# ---------------------------------------------------------------------------
class ModArith:
    def __init__(self, cnf, p):
        self.cnf = cnf
        self.p = p
        self.nbits = p.bit_length()

    def const(self, value):
        value = value % self.p
        vec = self.cnf.fresh_vec(self.nbits)
        self.cnf.assign_bit_vec(vec, value)
        return vec

    def fresh_element(self):
        return self.cnf.fresh_vec(self.nbits)

    def _ripple_add(self, a, b, n):
        carry = None
        s = []
        for i in range(n):
            if carry is None:
                si = self.cnf.gate_xor(a[i], b[i])
                carry = self.cnf.gate_and(a[i], b[i])
            else:
                ab = self.cnf.gate_xor(a[i], b[i])
                si = self.cnf.gate_xor(ab, carry)
                c1 = self.cnf.gate_and(a[i], b[i])
                c2 = self.cnf.gate_and(ab, carry)
                carry = self.cnf.gate_or(c1, c2)
            s.append(si)
        return s, carry

    def _sub_if_ge(self, val, sub_val_int, n):
        sub_bits = [(sub_val_int >> i) & 1 for i in range(n)]
        not_sub = []
        for i in range(n):
            v = self.cnf.fresh()
            if sub_bits[i]:
                self.cnf.const_false(v)
            else:
                self.cnf.const_true(v)
            not_sub.append(v)

        carry_in = self.cnf.fresh()
        self.cnf.const_true(carry_in)
        carry = carry_in
        diff = []
        for i in range(n):
            ab = self.cnf.gate_xor(val[i], not_sub[i])
            si = self.cnf.gate_xor(ab, carry)
            c1 = self.cnf.gate_and(val[i], not_sub[i])
            c2 = self.cnf.gate_and(ab, carry)
            carry = self.cnf.gate_or(c1, c2)
            diff.append(si)

        result = self.cnf.vec_mux(carry, diff, val)
        return result

    def add(self, a, b):
        n = self.nbits
        a_ext = a + [self.cnf.fresh()]
        b_ext = b + [self.cnf.fresh()]
        self.cnf.const_false(a_ext[-1])
        self.cnf.const_false(b_ext[-1])
        s_ext, _ = self._ripple_add(a_ext, b_ext, n + 1)
        result = self._sub_if_ge(s_ext[:n+1], self.p, n + 1)
        return result[:n]

    def sub(self, a, b):
        n = self.nbits
        not_b = [self.cnf.gate_not(bi) for bi in b]
        carry_in = self.cnf.fresh()
        self.cnf.const_true(carry_in)
        carry = carry_in
        diff = []
        for i in range(n):
            ab = self.cnf.gate_xor(a[i], not_b[i])
            si = self.cnf.gate_xor(ab, carry)
            c1 = self.cnf.gate_and(a[i], not_b[i])
            c2 = self.cnf.gate_and(ab, carry)
            carry = self.cnf.gate_or(c1, c2)
            diff.append(si)

        # Create p as raw bits (NOT self.const(p) which reduces mod p to 0!)
        p_bits = self.cnf.fresh_vec(n)
        for i in range(n):
            if (self.p >> i) & 1:
                self.cnf.const_true(p_bits[i])
            else:
                self.cnf.const_false(p_bits[i])

        borrow = self.cnf.gate_not(carry)
        correction = [self.cnf.gate_and(borrow, pi) for pi in p_bits]
        result, _ = self._ripple_add(diff, correction, n)
        return result

    def _mul_circuit(self, a, b):
        n = self.nbits
        product = [self.cnf.fresh() for _ in range(2 * n)]
        for i in range(2 * n):
            self.cnf.const_false(product[i])

        for i in range(n):
            partial = [self.cnf.gate_and(a[j], b[i]) for j in range(n)]
            shifted = [self.cnf.fresh() for _ in range(2 * n)]
            for k in range(2 * n):
                if k < i or k >= i + n:
                    self.cnf.const_false(shifted[k])
                else:
                    self.cnf.assert_eq(shifted[k], partial[k - i])
            product, _ = self._ripple_add(product, shifted, 2 * n)

        result = product
        nbits_result = 2 * n
        for shift in range(n - 1, -1, -1):
            multiple = self.p << shift
            if multiple >= (1 << nbits_result):
                continue
            result = self._sub_if_ge(result, multiple, nbits_result)
        return result[:n]

    def mul(self, a, b):
        return self._mul_circuit(a, b)

    def square(self, a):
        return self.mul(a, a)


# ---------------------------------------------------------------------------
# Plain EC arithmetic (for verification and table generation)
# ---------------------------------------------------------------------------
class EC:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a % p
        self.b = b % p

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def add(self, P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P
        x2, y2 = Q
        p = self.p
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, p - 2, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def mul(self, k, P):
        R = None
        Q = P
        while k > 0:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def order(self, P):
        Q = P
        for i in range(1, self.p + 2):
            if Q is None:
                return i
            Q = self.add(Q, P)
        return None

    def find_generator(self, min_order=4):
        p = self.p
        for x in range(p):
            rhs = (x * x * x + self.a * x + self.b) % p
            if rhs == 0:
                continue
            if pow(rhs, (p - 1) // 2, p) != 1:
                continue
            y = self._sqrt_mod(rhs, p)
            if y is None:
                continue
            P = (x, y)
            if self.on_curve(P):
                o = self.order(P)
                if o is not None and o >= min_order:
                    return P, o
        return None, None

    def _sqrt_mod(self, a, p):
        if a == 0: return 0
        if pow(a, (p - 1) // 2, p) != 1: return None
        if p % 4 == 3: return pow(a, (p + 1) // 4, p)
        q, s = p - 1, 0
        while q % 2 == 0: q //= 2; s += 1
        z = 2
        while pow(z, (p - 1) // 2, p) != p - 1: z += 1
        m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
        while True:
            if t == 1: return r
            i, tmp = 1, (t * t) % p
            while tmp != 1: tmp = (tmp * tmp) % p; i += 1
            b = pow(c, 1 << (m - i - 1), p)
            m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p

    def count_points(self):
        count = 1
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            if rhs == 0: count += 1
            elif pow(rhs, (self.p - 1) // 2, self.p) == 1: count += 2
        return count


# ---------------------------------------------------------------------------
# Strategy 1: Table-based encoding (fast, compact)
# ---------------------------------------------------------------------------
class TableEncoder:
    """
    Encodes ECDLP as: given the table {i -> i*G} for i=0..2^k-1,
    find k_bits such that table[k] == P.

    For each output bit of x and y, builds a Boolean function of k_bits.
    Uses Tseitin encoding of the truth table.
    """

    @staticmethod
    def encode(ec, G, P, k_bits_count, order):
        """
        Returns (cnf, k_vars, stats).
        """
        cnf = CNF()
        k_vars = cnf.fresh_vec(k_bits_count)
        nbits = ec.p.bit_length()

        # Precompute table: i -> i*G
        max_k = 1 << k_bits_count
        table_x = []  # table_x[i] = x-coordinate of i*G
        table_y = []
        table_inf = []  # True if i*G = O

        for i in range(max_k):
            kG = ec.mul(i % order if order else i, G)
            if kG is None:
                table_x.append(0)
                table_y.append(0)
                table_inf.append(True)
            else:
                table_x.append(kG[0])
                table_y.append(kG[1])
                table_inf.append(False)

        # Target point
        if P is None:
            target_x, target_y, target_inf = 0, 0, True
        else:
            target_x, target_y, target_inf = P[0], P[1], False

        # For each bit position of x-coordinate, build a constraint
        # that the output bit equals the truth table evaluated at k_vars
        for bit in range(nbits):
            target_bit = (target_x >> bit) & 1
            # Find which k values produce a different bit than target
            # For those k values, we need to exclude them
            # This is: for all k where table_x[k].bit != target_bit,
            #   NOT(k_vars == k)
            # Which is equivalent to a set of clauses

            # Approach: for each k where bit differs, add blocking clause
            for k_val in range(max_k):
                if table_inf[k_val]:
                    tbl_bit = 0  # doesn't matter, will be handled by inf constraint
                else:
                    tbl_bit = (table_x[k_val] >> bit) & 1
                if tbl_bit != target_bit:
                    # Block this k_val: at least one k_var bit must differ
                    clause = []
                    for j in range(k_bits_count):
                        if (k_val >> j) & 1:
                            clause.append(-k_vars[j])
                        else:
                            clause.append(k_vars[j])
                    cnf.add(clause)

        # Same for y-coordinate
        for bit in range(nbits):
            target_bit = (target_y >> bit) & 1
            for k_val in range(max_k):
                if table_inf[k_val]:
                    tbl_bit = 0
                else:
                    tbl_bit = (table_y[k_val] >> bit) & 1
                if tbl_bit != target_bit:
                    clause = []
                    for j in range(k_bits_count):
                        if (k_val >> j) & 1:
                            clause.append(-k_vars[j])
                        else:
                            clause.append(k_vars[j])
                    cnf.add(clause)

        # Handle infinity: if target is not infinity, block all k producing O
        if not target_inf:
            for k_val in range(max_k):
                if table_inf[k_val]:
                    clause = []
                    for j in range(k_bits_count):
                        if (k_val >> j) & 1:
                            clause.append(-k_vars[j])
                        else:
                            clause.append(k_vars[j])
                    cnf.add(clause)
        else:
            # Target IS infinity: block all k NOT producing O
            for k_val in range(max_k):
                if not table_inf[k_val]:
                    clause = []
                    for j in range(k_bits_count):
                        if (k_val >> j) & 1:
                            clause.append(-k_vars[j])
                        else:
                            clause.append(k_vars[j])
                    cnf.add(clause)

        return cnf, k_vars


# ---------------------------------------------------------------------------
# Strategy 2: Circuit-based encoding (full algebraic structure)
# ---------------------------------------------------------------------------
class CircuitEncoder:
    """
    Encodes ECDLP as a Boolean circuit: k*G computed via double-and-add.
    Uses precomputed doubling of G (since G is constant) to reduce circuit size.
    Only the conditional additions need symbolic encoding.
    """

    @staticmethod
    def encode(ec_plain, mod_arith, G, P, k_bits_count):
        """
        Optimized encoding: precompute 2^i * G, encode only conditional additions.

        k*G = k_0 * G + k_1 * 2G + k_2 * 4G + ...

        Each term is either O or 2^i*G depending on k_i.
        We sum them using a chain of additions.
        """
        cnf = mod_arith.cnf
        k_vars = cnf.fresh_vec(k_bits_count)
        p = mod_arith.p
        nbits = mod_arith.nbits

        # Precompute 2^i * G
        powers = []
        Q = G
        for i in range(k_bits_count):
            powers.append(Q)
            Q = ec_plain.add(Q, Q)

        # Build running sum: R = sum of k_i * powers[i]
        # Start with either powers[0] or O depending on k_0

        # Helper to create a conditional point: k_i ? P_i : O
        # Since O has special handling, we encode the running sum step by step.
        # R_0 = k_0 ? powers[0] : O
        # R_i = R_{i-1} + (k_i ? powers[i] : O) for i > 0

        # For each step, we need point_add(R, Q) where Q is either constant or O.
        # When Q = O, result is R unchanged.
        # When Q = powers[i], result is R + powers[i].

        # So: R_new = k_i ? (R + powers[i]) : R
        # We precompute R + powers[i] using circuit, then MUX.

        # But we STILL need to handle R being O (point at infinity).
        # Track with an is_inf flag.

        # Actually, for a compact encoding with constant G:
        # The addition R + powers[i] where powers[i] is constant
        # can use a simplified circuit where one operand is known.

        # For now, use the witness-based approach for addition with one constant point.

        def ec_add_with_constant(R_x, R_y, R_inf, Qx, Qy):
            """Add symbolic point R to constant point Q=(Qx,Qy).
            Returns (new_x, new_y, new_inf).
            Q is never O in our usage.
            """
            mod = mod_arith

            # Case 1: R is O -> result is Q
            # Case 2: R.x == Qx and R.y == Qy -> doubling
            # Case 3: R.x == Qx and R.y != Qy -> result is O
            # Case 4: R.x != Qx -> standard addition

            Qx_const = mod.const(Qx)
            Qy_const = mod.const(Qy)

            # Standard addition: lambda = (Qy - R.y) / (Qx - R.x)
            dy = mod.sub(Qy_const, R_y)
            dx = mod.sub(Qx_const, R_x)

            # lambda_add is a witness: lambda * dx = dy
            lambda_add = mod.fresh_element()
            lam_dx = mod.mul(lambda_add, dx)

            lam_sq = mod.square(lambda_add)
            rx_add = mod.sub(mod.sub(lam_sq, R_x), Qx_const)
            ry_add = mod.sub(mod.mul(lambda_add, mod.sub(R_x, rx_add)), R_y)

            # Doubling: lambda = (3*Qx^2 + a) / (2*Qy)
            # Since Q is constant, we can precompute the numerator and denominator
            numer_val = (3 * Qx * Qx + ec_plain.a) % p
            denom_val = (2 * Qy) % p
            if denom_val == 0:
                # 2-torsion point, doubling gives O
                lambda_dbl_val = 0  # unused
                dbl_is_inf = True
            else:
                lambda_dbl_val = (numer_val * pow(denom_val, p - 2, p)) % p
                dbl_is_inf = False

            if not dbl_is_inf:
                rx_dbl_val = (lambda_dbl_val * lambda_dbl_val - 2 * Qx) % p
                ry_dbl_val = (lambda_dbl_val * (Qx - rx_dbl_val) - Qy) % p
                rx_dbl = mod.const(rx_dbl_val)
                ry_dbl = mod.const(ry_dbl_val)
            else:
                rx_dbl = mod.const(0)
                ry_dbl = mod.const(0)

            # Detect cases
            # x_eq: R.x == Qx
            x_eq_bits = [cnf.gate_eq(R_x[i], Qx_const[i]) for i in range(nbits)]
            x_eq = x_eq_bits[0]
            for i in range(1, len(x_eq_bits)):
                x_eq = cnf.gate_and(x_eq, x_eq_bits[i])

            y_eq_bits = [cnf.gate_eq(R_y[i], Qy_const[i]) for i in range(nbits)]
            y_eq = y_eq_bits[0]
            for i in range(1, len(y_eq_bits)):
                y_eq = cnf.gate_and(y_eq, y_eq_bits[i])

            is_double = cnf.gate_and(x_eq, y_eq)
            not_y_eq = cnf.gate_not(y_eq)
            is_inverse = cnf.gate_and(x_eq, not_y_eq)

            # Constrain addition witness: if NOT x_eq, lambda*dx == dy
            for i in range(nbits):
                diff = cnf.gate_xor(lam_dx[i], dy[i])
                cnf.add([x_eq, R_inf, -diff])  # x_eq OR R_inf -> unconstrained

            # Select result
            rx = rx_add
            ry = ry_add
            r_inf_new = cnf.fresh()
            cnf.const_false(r_inf_new)

            # If doubling case
            rx = cnf.vec_mux(is_double, rx_dbl, rx)
            ry = cnf.vec_mux(is_double, ry_dbl, ry)
            if dbl_is_inf:
                r_inf_new = cnf.gate_or(r_inf_new, is_double)

            # If inverse case -> O
            zero_vec = mod.const(0)
            rx = cnf.vec_mux(is_inverse, zero_vec, rx)
            ry = cnf.vec_mux(is_inverse, zero_vec, ry)
            r_inf_new = cnf.gate_or(r_inf_new, is_inverse)

            # If R was O -> result is Q
            rx = cnf.vec_mux(R_inf, Qx_const, rx)
            ry = cnf.vec_mux(R_inf, Qy_const, ry)
            r_inf_final = cnf.gate_mux(R_inf, cnf.fresh(), r_inf_new)
            # When R_inf=1, result is Q which is not O, so r_inf_final=0
            r_inf_false = cnf.fresh()
            cnf.const_false(r_inf_false)
            r_inf_final = cnf.gate_mux(R_inf, r_inf_false, r_inf_new)

            return rx, ry, r_inf_final

        # Build the scalar multiplication chain
        # Initialize: R = k_0 ? powers[0] : O
        p0 = powers[0]
        R_x = cnf.vec_mux(k_vars[0], mod_arith.const(p0[0]), mod_arith.const(0))
        R_y = cnf.vec_mux(k_vars[0], mod_arith.const(p0[1]), mod_arith.const(0))
        R_inf = cnf.gate_not(k_vars[0])  # if k_0=0, R=O

        for i in range(1, k_bits_count):
            Qi = powers[i]
            if Qi is None:
                # powers[i] is O (shouldn't happen for small k_bits)
                continue

            # Compute R + Qi
            add_x, add_y, add_inf = ec_add_with_constant(R_x, R_y, R_inf, Qi[0], Qi[1])

            # MUX: if k_i, use R+Qi; else use R
            R_x = cnf.vec_mux(k_vars[i], add_x, R_x)
            R_y = cnf.vec_mux(k_vars[i], add_y, R_y)
            R_inf = cnf.gate_mux(k_vars[i], add_inf, R_inf)

        # Constrain output: R == P
        P_x = mod_arith.const(P[0])
        P_y = mod_arith.const(P[1])
        cnf.const_false(R_inf)
        cnf.vec_eq(R_x, P_x)
        cnf.vec_eq(R_y, P_y)

        return cnf, k_vars


# ---------------------------------------------------------------------------
# Utility: find curves
# ---------------------------------------------------------------------------
def random_prime(nbits):
    while True:
        n = random.randint(1 << (nbits - 1), (1 << nbits) - 1)
        n |= 1
        if is_prime(n):
            return n

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
        if n == p: return True
        if n % p == 0: return False
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for a in [2, 3, 5, 7, 11]:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def find_curve(nbits, congruent=False, n_val=None):
    """Find a curve over F_p with a generator of reasonable order."""
    for attempt in range(200):
        p = random_prime(nbits)
        if p < 5: continue

        if congruent:
            nv = n_val if n_val is not None else random.randint(1, max(1, p // 2))
            a = (-nv * nv) % p
            b = 0
        else:
            a = random.randint(1, p - 1)
            b = random.randint(1, p - 1)

        disc = (4 * a * a * a + 27 * b * b) % p
        if disc == 0: continue

        ec = EC(p, a, b)
        G, order = ec.find_generator(min_order=4)
        if G is not None:
            return p, a, b, ec, G, order

    raise RuntimeError(f"Could not find curve after 200 attempts (nbits={nbits}, congruent={congruent})")


# ---------------------------------------------------------------------------
# Comparison methods
# ---------------------------------------------------------------------------
def brute_force_dlog(ec, G, P, max_k):
    Q = None
    for k in range(max_k + 1):
        if Q == P: return k
        Q = ec.add(Q, G)
    return None

def bsgs_dlog(ec, G, P, order):
    m = int(math.isqrt(order)) + 1
    table = {}
    Q = None
    for j in range(m):
        key = (Q[0], Q[1]) if Q is not None else 'inf'
        table[key] = j
        Q = ec.add(Q, G)

    neg_mG = ec.mul(order - m, G)
    Q = P
    for i in range(m):
        key = (Q[0], Q[1]) if Q is not None else 'inf'
        if key in table:
            return (i * m + table[key]) % order
        Q = ec.add(Q, neg_mG)
    return None


# ---------------------------------------------------------------------------
# SAT Solver wrapper
# ---------------------------------------------------------------------------
def solve_sat(cnf, k_vars, timeout=60):
    """Solve CNF and extract k value. Returns (k, solve_time, result_str)."""
    if not HAS_PYSAT:
        return None, 0, 'NO_SOLVER'

    solver = Glucose3()
    for clause in cnf.clauses:
        solver.add_clause(clause)

    timed_out = [False]
    def handler(signum, frame):
        timed_out[0] = True
        raise TimeoutError()

    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        t0 = time.time()
        sat = solver.solve()
        solve_time = time.time() - t0

        if sat:
            model = set(solver.get_model())
            k = 0
            for i, v in enumerate(k_vars):
                if v in model:
                    k |= (1 << i)
            solver.delete()
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            return k, solve_time, 'SAT'
        else:
            solver.delete()
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            return None, solve_time, 'UNSAT'

    except TimeoutError:
        solve_time = time.time() - t0
        solver.delete()
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
        return None, solve_time, 'TIMEOUT'

    except Exception as e:
        solver.delete()
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
        return None, 0, f'ERROR: {e}'


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
def run_instance(nbits, k_bits, congruent=False, n_val=None,
                 method='table', verbose=True):
    """Run a single ECDLP SAT instance."""
    try:
        p, a, b, ec, G, order = find_curve(nbits, congruent=congruent, n_val=n_val)
    except RuntimeError as e:
        if verbose:
            print(f"\n--- {method}: {nbits}b field, {k_bits}b scalar ---")
            print(f"  SKIP: {e}")
        raise

    k_actual = random.randint(1, min(order - 1, (1 << k_bits) - 1))
    P = ec.mul(k_actual, G)

    curve_type = f"E_{n_val} (congruent)" if congruent else "generic"
    if verbose:
        print(f"\n--- {method}: {nbits}b field, {k_bits}b scalar, {curve_type} ---")
        print(f"  p={p}, order={order}, G={G}, k={k_actual}, P={P}")

    stats = {'p': p, 'nbits': nbits, 'k_bits': k_bits, 'order': order,
             'k_actual': k_actual, 'congruent': congruent, 'method': method}

    # Encode
    t0 = time.time()
    if method == 'table':
        cnf, k_vars = TableEncoder.encode(ec, G, P, k_bits, order)
    elif method == 'circuit':
        cnf_obj = CNF()
        mod = ModArith(cnf_obj, p)
        cnf, k_vars = CircuitEncoder.encode(ec, mod, G, P, k_bits)
    else:
        raise ValueError(f"Unknown method: {method}")

    stats['encode_time'] = time.time() - t0
    stats['num_vars'] = cnf.num_vars()
    stats['num_clauses'] = cnf.num_clauses()

    # Solve
    k_found, solve_time, result_str = solve_sat(cnf, k_vars, timeout=60)
    stats['solve_time'] = solve_time
    stats['result'] = result_str
    stats['k_found'] = k_found

    # Verify
    if k_found is not None:
        P_check = ec.mul(k_found, G)
        correct = (P_check == P)
        if not correct and order:
            correct = (k_found % order == k_actual % order)
        stats['correct'] = correct
    else:
        stats['correct'] = False

    # Brute force
    t0 = time.time()
    brute_force_dlog(ec, G, P, 1 << k_bits)
    stats['bf_time'] = time.time() - t0

    # BSGS
    t0 = time.time()
    bsgs_dlog(ec, G, P, order)
    stats['bsgs_time'] = time.time() - t0

    if verbose:
        print(f"  Encoding: {stats['num_vars']} vars, {stats['num_clauses']} clauses, {stats['encode_time']:.4f}s")
        print(f"  SAT: {result_str}, {solve_time:.4f}s, k_found={k_found}, correct={stats['correct']}")
        print(f"  BF: {stats['bf_time']:.5f}s, BSGS: {stats['bsgs_time']:.6f}s")

    return stats


def run_benchmark():
    """Full benchmark suite."""
    print("=" * 72)
    print("ECDLP SAT Solver Benchmark")
    print("=" * 72)

    all_results = defaultdict(list)

    # ---- Phase 1: Table-based encoding, varying sizes ----
    print("\n### Phase 1: Table-based encoding ###")
    for trial in range(5):
        for k_bits in [4, 8, 12]:
            nbits = max(6, k_bits + 2)
            s = run_instance(nbits, k_bits, method='table')
            all_results[f"table_{nbits}b_k{k_bits}"].append(s)

    # ---- Phase 2: Circuit-based encoding (small only) ----
    print("\n### Phase 2: Circuit-based encoding ###")
    for trial in range(5):
        for k_bits in [4]:
            s = run_instance(6, k_bits, method='circuit')
            all_results[f"circuit_6b_k{k_bits}"].append(s)

    # ---- Phase 3: Table - congruent vs generic ----
    print("\n### Phase 3: Congruent vs Generic (table) ###")
    for trial in range(5):
        for k_bits in [4, 8, 12]:
            nbits = max(6, k_bits + 2)
            sg = run_instance(nbits, k_bits, congruent=False, method='table')
            all_results[f"cmp_generic_k{k_bits}"].append(sg)
            sc = run_instance(nbits, k_bits, congruent=True, n_val=2, method='table')
            all_results[f"cmp_congruent_k{k_bits}"].append(sc)

    # ---- Phase 4: Circuit - congruent vs generic ----
    print("\n### Phase 4: Congruent vs Generic (circuit) ###")
    for trial in range(3):
        try:
            sg = run_instance(8, 4, congruent=False, method='circuit')
            all_results["cmp_circuit_generic"].append(sg)
        except Exception as e:
            print(f"  SKIP generic circuit: {e}")
        try:
            sc = run_instance(8, 4, congruent=True, n_val=3, method='circuit')
            all_results["cmp_circuit_congruent"].append(sc)
        except Exception as e:
            print(f"  SKIP congruent circuit: {e}")

    # ---- Phase 5: Scaling test (table) ----
    print("\n### Phase 5: Scaling test (table) ###")
    for k_bits in [4, 8, 12, 16]:
        nbits = max(6, k_bits + 2)
        s = run_instance(nbits, k_bits, method='table')
        all_results[f"scale_table_k{k_bits}"].append(s)

    # ---- Phase 6: Scaling test (circuit) ----
    print("\n### Phase 6: Scaling test (circuit) ###")
    for k_bits in [4, 6]:
        nbits = max(6, k_bits + 2)
        s = run_instance(nbits, k_bits, method='circuit')
        all_results[f"scale_circuit_k{k_bits}"].append(s)

    # ---- Summary ----
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    fmt = "{:<28} {:>8} {:>10} {:>8} {:>8} {:>8} {:>8} {:>4}"
    print(fmt.format("Config", "Vars", "Clauses", "Encode", "Solve", "BF", "BSGS", "OK"))
    print("-" * 72)

    for key in sorted(all_results.keys()):
        stats_list = all_results[key]
        n = len(stats_list)
        avg = lambda f: sum(s[f] for s in stats_list) / n
        n_ok = sum(1 for s in stats_list if s.get('correct'))
        print(fmt.format(
            key,
            f"{avg('num_vars'):.0f}",
            f"{avg('num_clauses'):.0f}",
            f"{avg('encode_time'):.4f}s",
            f"{avg('solve_time'):.4f}s",
            f"{avg('bf_time'):.5f}s",
            f"{avg('bsgs_time'):.6f}s",
            f"{n_ok}/{n}"
        ))

    # ---- Congruent Number Curve Analysis ----
    print("\n### Congruent Number Curve Analysis ###")
    for k_bits in [4, 8, 12]:
        gk = f"cmp_generic_k{k_bits}"
        ck = f"cmp_congruent_k{k_bits}"
        if gk in all_results and ck in all_results:
            g, c = all_results[gk], all_results[ck]
            gc = sum(s['num_clauses'] for s in g) / len(g)
            cc = sum(s['num_clauses'] for s in c) / len(c)
            gs = sum(s['solve_time'] for s in g) / len(g)
            cs = sum(s['solve_time'] for s in c) / len(c)
            ratio = cc / gc if gc > 0 else 0
            print(f"  k={k_bits}b (table): generic={gc:.0f} clauses/{gs:.4f}s, "
                  f"congruent={cc:.0f} clauses/{cs:.4f}s, ratio={ratio:.3f}")

    for tag in [("cmp_circuit_generic", "cmp_circuit_congruent")]:
        gk, ck = tag
        if gk in all_results and ck in all_results:
            g, c = all_results[gk], all_results[ck]
            gc = sum(s['num_clauses'] for s in g) / len(g)
            cc = sum(s['num_clauses'] for s in c) / len(c)
            gs = sum(s['solve_time'] for s in g) / len(g)
            cs = sum(s['solve_time'] for s in c) / len(c)
            gv = sum(s['num_vars'] for s in g) / len(g)
            cv = sum(s['num_vars'] for s in c) / len(c)
            print(f"  Circuit: generic={gv:.0f}v/{gc:.0f}c/{gs:.4f}s, "
                  f"congruent={cv:.0f}v/{cc:.0f}c/{cs:.4f}s")

    # ---- Scaling Analysis ----
    print("\n### Scaling Analysis ###")
    print("  Table-based:")
    for k_bits in [4, 8, 12, 16]:
        key = f"scale_table_k{k_bits}"
        if key in all_results:
            s = all_results[key][0]
            print(f"    k={k_bits}b: {s['num_vars']}v, {s['num_clauses']}c, "
                  f"encode={s['encode_time']:.4f}s, solve={s['solve_time']:.4f}s")

    print("  Circuit-based:")
    for k_bits in [4, 6, 8]:
        key = f"scale_circuit_k{k_bits}"
        if key in all_results:
            s = all_results[key][0]
            print(f"    k={k_bits}b: {s['num_vars']}v, {s['num_clauses']}c, "
                  f"encode={s['encode_time']:.4f}s, solve={s['solve_time']:.4f}s")


if __name__ == "__main__":
    run_benchmark()
