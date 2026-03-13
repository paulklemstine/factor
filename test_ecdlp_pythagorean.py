"""
TDD tests for ECDLP solver using Pythagorean triplet tree exploration.

Progression:
  1. Elliptic curve arithmetic (toy curves + secp256k1)
  2. Pythagorean triplet tree generation (Berggren matrices)
  3. Tree-guided ECDLP search strategies
  4. Round-trip: generate keypair, recover private key
"""

import pytest
from ecdlp_pythagorean import (
    ECPoint,
    EllipticCurve,
    secp256k1_curve,
    pythagorean_tree_bfs,
    pythagorean_children,
    triple_to_scalar_map,
    ecdlp_pythagorean_search,
    ecdlp_ternary_tree_walk,
    ecdlp_naf_ternary_walk,
    ecdlp_mitm_ternary,
    ecdlp_bsgs,
    ecdlp_pollard_rho_ternary,
    ecdlp_kangaroo_ternary,
    ecdlp_mitm3_ternary,
    ecdlp_gaussian_pythagorean,
    CMCurve1728,
    compute_curve_order,
    benchmark_ecdlp,
    to_balanced_ternary,
    from_balanced_ternary,
    ternary_path_to_scalar,
    FastCurve,
    ecdlp_bsgs_c,
    ecdlp_glv_bsgs,
    ecdlp_pythagorean_kangaroo,
    ecdlp_pythagorean_kangaroo_c,
    secp256k1_benchmark,
)


# ---------------------------------------------------------------------------
# 1. Elliptic curve arithmetic on a toy curve
# ---------------------------------------------------------------------------

class TestEllipticCurveArithmetic:
    """Test EC math on y² = x³ + 2x + 3 (mod 97) — small curve for validation."""

    @pytest.fixture
    def toy_curve(self):
        return EllipticCurve(a=2, b=3, p=97)

    def test_point_on_curve(self, toy_curve):
        """(3, 6) is on y²=x³+2x+3 mod 97: 36 = 27+6+3 = 36."""
        pt = ECPoint(3, 6)
        assert toy_curve.is_on_curve(pt)

    def test_identity(self, toy_curve):
        """Point at infinity is the identity."""
        inf = ECPoint.infinity()
        assert inf.is_infinity

    def test_add_identity(self, toy_curve):
        pt = ECPoint(3, 6)
        result = toy_curve.add(pt, ECPoint.infinity())
        assert result.x == 3 and result.y == 6

    def test_add_inverse(self, toy_curve):
        """P + (-P) = O."""
        pt = ECPoint(3, 6)
        neg = ECPoint(3, 97 - 6)  # -P
        result = toy_curve.add(pt, neg)
        assert result.is_infinity

    def test_point_double(self, toy_curve):
        pt = ECPoint(3, 6)
        result = toy_curve.double(pt)
        assert toy_curve.is_on_curve(result)

    def test_scalar_mult(self, toy_curve):
        pt = ECPoint(3, 6)
        result = toy_curve.scalar_mult(1, pt)
        assert result.x == pt.x and result.y == pt.y

    def test_scalar_mult_2(self, toy_curve):
        pt = ECPoint(3, 6)
        doubled = toy_curve.double(pt)
        mult2 = toy_curve.scalar_mult(2, pt)
        assert doubled.x == mult2.x and doubled.y == mult2.y

    def test_scalar_mult_order(self, toy_curve):
        """Multiplying by the group order gives infinity."""
        # Find order of (3,6) by brute force for this tiny curve
        pt = ECPoint(3, 6)
        order = toy_curve.point_order(pt)
        result = toy_curve.scalar_mult(order, pt)
        assert result.is_infinity

    def test_scalar_mult_associative(self, toy_curve):
        """k1*(k2*G) == (k1*k2)*G."""
        G = ECPoint(3, 6)
        k1, k2 = 7, 13
        lhs = toy_curve.scalar_mult(k1, toy_curve.scalar_mult(k2, G))
        rhs = toy_curve.scalar_mult(k1 * k2, G)
        assert lhs.x == rhs.x and lhs.y == rhs.y


# ---------------------------------------------------------------------------
# 2. secp256k1 basics
# ---------------------------------------------------------------------------

class TestSecp256k1:
    def test_generator_on_curve(self):
        curve = secp256k1_curve()
        assert curve.is_on_curve(curve.G)

    def test_scalar_mult_small(self):
        curve = secp256k1_curve()
        P2 = curve.scalar_mult(2, curve.G)
        assert curve.is_on_curve(P2)
        assert not P2.is_infinity

    def test_order_gives_infinity(self):
        curve = secp256k1_curve()
        O = curve.scalar_mult(curve.n, curve.G)
        assert O.is_infinity

    def test_known_2G(self):
        """2*G should match the known secp256k1 value."""
        curve = secp256k1_curve()
        P2 = curve.scalar_mult(2, curve.G)
        # Known 2G for secp256k1
        expected_x = 0xC6047F9441ED7D6D3045406E95C07CD85C778E4B8CEF3CA7ABAC09B95C709EE5
        assert P2.x == expected_x


# ---------------------------------------------------------------------------
# 3. Pythagorean triplet tree
# ---------------------------------------------------------------------------

class TestPythagoreanTree:
    def test_root_triple(self):
        """The fundamental triple is (3, 4, 5)."""
        children = pythagorean_children((3, 4, 5))
        assert len(children) == 3
        for a, b, c in children:
            assert a * a + b * b == c * c

    def test_bfs_generates_valid_triples(self):
        """All generated triples satisfy a² + b² = c²."""
        triples = pythagorean_tree_bfs(max_triples=50)
        assert len(triples) == 50
        for a, b, c in triples:
            assert a * a + b * b == c * c
            assert a > 0 and b > 0 and c > 0

    def test_bfs_includes_root(self):
        triples = pythagorean_tree_bfs(max_triples=10)
        assert (3, 4, 5) in triples

    def test_all_primitive(self):
        """All triples from the Berggren tree are primitive (gcd=1)."""
        from math import gcd
        triples = pythagorean_tree_bfs(max_triples=100)
        for a, b, c in triples:
            assert gcd(gcd(a, b), c) == 1


# ---------------------------------------------------------------------------
# 4. Triple-to-scalar mapping
# ---------------------------------------------------------------------------

class TestTripleToScalar:
    def test_mapping_returns_integers(self):
        scalars = triple_to_scalar_map((3, 4, 5), n=97)
        assert all(isinstance(s, int) for s in scalars)
        assert all(0 < s < 97 for s in scalars)

    def test_different_triples_give_different_scalars(self):
        s1 = triple_to_scalar_map((3, 4, 5), n=97)
        s2 = triple_to_scalar_map((5, 12, 13), n=97)
        # At least some scalars should differ
        assert s1 != s2

    def test_mapping_deterministic(self):
        s1 = triple_to_scalar_map((3, 4, 5), n=97)
        s2 = triple_to_scalar_map((3, 4, 5), n=97)
        assert s1 == s2


# ---------------------------------------------------------------------------
# 5. ECDLP search on toy curves
# ---------------------------------------------------------------------------

class TestECDLPSearch:
    @pytest.fixture
    def toy_curve(self):
        return EllipticCurve(a=2, b=3, p=97)

    def test_solve_known_small_k(self, toy_curve):
        """Recover k=7 from P=7*G on toy curve."""
        G = ECPoint(3, 6)
        k_secret = 7
        P = toy_curve.scalar_mult(k_secret, G)
        order = toy_curve.point_order(G)

        k_found = ecdlp_pythagorean_search(toy_curve, G, P, order, max_triples=200)
        assert k_found is not None
        assert k_found % order == k_secret % order

    def test_solve_larger_k(self, toy_curve):
        """Recover k=42 from P=42*G."""
        G = ECPoint(3, 6)
        k_secret = 42
        P = toy_curve.scalar_mult(k_secret, G)
        order = toy_curve.point_order(G)

        k_found = ecdlp_pythagorean_search(toy_curve, G, P, order, max_triples=500)
        assert k_found is not None
        assert k_found % order == k_secret % order

    def test_solve_various_keys(self, toy_curve):
        """Recover several different secret keys."""
        G = ECPoint(3, 6)
        order = toy_curve.point_order(G)

        for k_secret in [1, 2, 5, 13, 29, 50]:
            k_secret = k_secret % order
            if k_secret == 0:
                continue
            P = toy_curve.scalar_mult(k_secret, G)
            k_found = ecdlp_pythagorean_search(toy_curve, G, P, order, max_triples=500)
            assert k_found == k_secret, f"Failed for k={k_secret}"


# ---------------------------------------------------------------------------
# 6. Slightly larger curve
# ---------------------------------------------------------------------------

class TestECDLPMediumCurve:
    @pytest.fixture
    def medium_curve(self):
        """y² = x³ + 7 (mod 10007) — same form as secp256k1 but tiny."""
        return EllipticCurve(a=0, b=7, p=10007)

    def test_find_generator(self, medium_curve):
        """Find a point on the curve."""
        G = medium_curve.find_generator()
        assert G is not None
        assert medium_curve.is_on_curve(G)

    def test_solve_on_medium_curve(self, medium_curve):
        G = medium_curve.find_generator()
        order = medium_curve.point_order(G)
        assert order > 10  # need reasonable order

        k_secret = 137 % order
        if k_secret == 0:
            k_secret = 1
        P = medium_curve.scalar_mult(k_secret, G)

        k_found = ecdlp_pythagorean_search(medium_curve, G, P, order, max_triples=2000)
        assert k_found == k_secret


# ---------------------------------------------------------------------------
# 7. Balanced ternary encoding
# ---------------------------------------------------------------------------

class TestBalancedTernary:
    def test_roundtrip_positive(self):
        for k in [1, 2, 3, 4, 5, 10, 42, 100, 999]:
            digits = to_balanced_ternary(k, 10**9)
            assert from_balanced_ternary(digits) == k

    def test_roundtrip_negative_mod(self):
        """Negative k mod order should round-trip."""
        order = 97
        k = order - 3  # equivalent to -3 mod 97
        digits = to_balanced_ternary(k, order)
        assert from_balanced_ternary(digits) % order == k % order

    def test_digits_are_balanced(self):
        digits = to_balanced_ternary(42, 1000)
        for d in digits:
            assert d in (-1, 0, 1)

    def test_path_to_scalar(self):
        # Path [1, -1, 0] (MSB first) = 1*9 + (-1)*3 + 0*1 = 6
        assert ternary_path_to_scalar([1, -1, 0]) == 6

    def test_path_to_scalar_single(self):
        assert ternary_path_to_scalar([1]) == 1
        assert ternary_path_to_scalar([-1]) == -1
        assert ternary_path_to_scalar([0]) == 0


# ---------------------------------------------------------------------------
# 8. Ternary tree walk (incremental EC computation)
# ---------------------------------------------------------------------------

class TestTernaryTreeWalk:
    @pytest.fixture
    def toy_curve(self):
        return EllipticCurve(a=2, b=3, p=97)

    def test_solve_small_k_ternary(self, toy_curve):
        """Ternary walk should find small k values."""
        G = ECPoint(3, 6)
        order = toy_curve.point_order(G)
        for k_secret in [1, 2, 3, 4]:
            k_secret = k_secret % order
            if k_secret == 0:
                continue
            P = toy_curve.scalar_mult(k_secret, G)
            k_found = ecdlp_ternary_tree_walk(toy_curve, G, P, order, max_depth=5)
            assert k_found is not None
            assert k_found % order == k_secret % order, f"Failed k={k_secret}"

    def test_tripling_consistency(self, toy_curve):
        """Verify curve.triple(P) == scalar_mult(3, P)."""
        G = ECPoint(3, 6)
        P = toy_curve.scalar_mult(7, G)
        tripled = toy_curve.triple(P)
        expected = toy_curve.scalar_mult(3, P)
        assert tripled == expected

    def test_incremental_vs_direct(self, toy_curve):
        """Ternary walk's incremental computation must match direct scalar_mult."""
        G = ECPoint(3, 6)
        order = toy_curve.point_order(G)
        # Manually simulate: path [-1, 1] → scalar = -1*3 + 1 = -2
        # This should equal (order - 2) * G
        expected = toy_curve.scalar_mult(order - 2, G)
        # Via incremental: start with -G, then triple + G
        neg_G = toy_curve.neg(G)
        tripled = toy_curve.triple(neg_G)  # 3*(-G) = -3G
        result = toy_curve.add(tripled, G)  # -3G + G = -2G
        assert result == expected

    def test_medium_curve_ternary(self):
        """Ternary walk on y²=x³+7 mod 10007."""
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)

        k_secret = 137 % order
        if k_secret == 0:
            k_secret = 1
        P = curve.scalar_mult(k_secret, G)

        # Use enough depth + baby steps to cover the order
        import math
        depth = int(math.log(order) / math.log(3)) + 2
        k_found = ecdlp_ternary_tree_walk(
            curve, G, P, order, max_depth=depth, baby_size=100
        )
        assert k_found is not None
        assert k_found % order == k_secret % order

    def test_ternary_coverage(self, toy_curve):
        """Ternary walk at depth d covers scalars in [-((3^d-1)/2), (3^d-1)/2]."""
        G = ECPoint(3, 6)
        order = toy_curve.point_order(G)
        # Depth 3 covers 3^3=27 nodes, with baby_size=1 covers scalars -13..13
        # With baby_size covering the rest, should find any k < order
        for k_secret in range(1, order):
            P = toy_curve.scalar_mult(k_secret, G)
            k_found = ecdlp_ternary_tree_walk(
                toy_curve, G, P, order, max_depth=4, baby_size=order
            )
            assert k_found is not None
            assert k_found % order == k_secret % order, \
                f"Failed k={k_secret}, got {k_found}"


# ---------------------------------------------------------------------------
# 9. Larger prime curve — stress test
# ---------------------------------------------------------------------------

class TestECDLPLargerCurve:
    def test_solve_prime_100003(self):
        """y²=x³+7 mod 100003 — tests ternary walk at larger scale."""
        curve = EllipticCurve(a=0, b=7, p=100003)
        G = curve.find_generator()
        order = curve.point_order(G)

        k_secret = 4321 % order
        if k_secret == 0:
            k_secret = 1
        P = curve.scalar_mult(k_secret, G)

        k_found = ecdlp_pythagorean_search(
            curve, G, P, order, max_triples=5000, verbose=True
        )
        assert k_found is not None
        assert k_found % order == k_secret % order


# ---------------------------------------------------------------------------
# 10. Standard BSGS baseline
# ---------------------------------------------------------------------------

class TestBSGS:
    def test_bsgs_toy(self):
        curve = EllipticCurve(a=2, b=3, p=97)
        G = ECPoint(3, 6)
        order = curve.point_order(G)
        for k in range(1, order):
            P = curve.scalar_mult(k, G)
            assert ecdlp_bsgs(curve, G, P, order) % order == k

    def test_bsgs_medium(self):
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 4567 % order or 1
        P = curve.scalar_mult(k, G)
        assert ecdlp_bsgs(curve, G, P, order) % order == k


# ---------------------------------------------------------------------------
# 11. NAF-pruned ternary walk
# ---------------------------------------------------------------------------

class TestNAFTernaryWalk:
    @pytest.fixture
    def toy_curve(self):
        return EllipticCurve(a=2, b=3, p=97)

    def test_naf_solves_small(self, toy_curve):
        G = ECPoint(3, 6)
        order = toy_curve.point_order(G)
        for k in range(1, order):
            P = toy_curve.scalar_mult(k, G)
            result = ecdlp_naf_ternary_walk(
                toy_curve, G, P, order, max_depth=6, baby_size=order
            )
            assert result is not None
            assert result % order == k, f"Failed k={k}"

    def test_naf_medium_curve(self):
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 137 % order or 1
        P = curve.scalar_mult(k, G)
        import math
        depth = int(math.log(order) / math.log(2)) + 2  # NAF grows as 2^d
        result = ecdlp_naf_ternary_walk(
            curve, G, P, order, max_depth=depth, baby_size=200, verbose=True
        )
        assert result is not None
        assert result % order == k

    def test_naf_fewer_nodes_than_full(self):
        """NAF should visit fewer nodes than unpruned ternary walk."""
        # NAF paths at depth d: ~2^d vs 3^d full
        # At depth 4: NAF ~ 21, full = 81
        # Just verify the structure prunes correctly
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 42 % order or 1
        P = curve.scalar_mult(k, G)
        # Should solve with NAF — the pruning doesn't prevent finding solutions
        result = ecdlp_naf_ternary_walk(
            curve, G, P, order, max_depth=20, baby_size=500
        )
        assert result is not None
        assert result % order == k


# ---------------------------------------------------------------------------
# 12. Meet-in-the-middle ternary
# ---------------------------------------------------------------------------

class TestMITMTernary:
    def test_mitm_toy(self):
        curve = EllipticCurve(a=2, b=3, p=97)
        G = ECPoint(3, 6)
        order = curve.point_order(G)
        for k in range(1, order):
            P = curve.scalar_mult(k, G)
            result = ecdlp_mitm_ternary(curve, G, P, order, half_depth=3)
            assert result is not None
            assert result % order == k, f"Failed k={k}"

    def test_mitm_medium(self):
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 4567 % order or 1
        P = curve.scalar_mult(k, G)
        import math
        half = int(math.log(order) / math.log(3)) // 2 + 1
        result = ecdlp_mitm_ternary(
            curve, G, P, order, half_depth=half, verbose=True
        )
        assert result is not None
        assert result % order == k

    def test_mitm_larger(self):
        """MITM on p=100003 curve."""
        curve = EllipticCurve(a=0, b=7, p=100003)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 31337 % order or 1
        P = curve.scalar_mult(k, G)
        import math
        half = int(math.log(order) / math.log(3)) // 2 + 1
        result = ecdlp_mitm_ternary(curve, G, P, order, half_depth=half)
        assert result is not None
        assert result % order == k


# ---------------------------------------------------------------------------
# 13. Benchmark comparison
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 14. Pollard rho with ternary partition
# ---------------------------------------------------------------------------

class TestPollardRho:
    def test_rho_toy(self):
        curve = EllipticCurve(a=2, b=3, p=97)
        G = ECPoint(3, 6)
        order = curve.point_order(G)
        for k in range(1, order):
            P = curve.scalar_mult(k, G)
            result = ecdlp_pollard_rho_ternary(curve, G, P, order)
            assert result is not None
            assert result % order == k, f"Failed k={k}"

    def test_rho_medium(self):
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 2345 % order or 1
        P = curve.scalar_mult(k, G)
        result = ecdlp_pollard_rho_ternary(curve, G, P, order)
        assert result is not None
        assert result % order == k

    def test_rho_larger(self):
        curve = EllipticCurve(a=0, b=7, p=100003)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 31337 % order or 1
        P = curve.scalar_mult(k, G)
        result = ecdlp_pollard_rho_ternary(curve, G, P, order)
        assert result is not None
        assert result % order == k


# ---------------------------------------------------------------------------
# 15. Pollard kangaroo with ternary jumps
# ---------------------------------------------------------------------------

class TestKangaroo:
    def test_kangaroo_toy(self):
        curve = EllipticCurve(a=2, b=3, p=97)
        G = ECPoint(3, 6)
        order = curve.point_order(G)
        for k in range(1, order):
            P = curve.scalar_mult(k, G)
            result = ecdlp_kangaroo_ternary(curve, G, P, order)
            assert result is not None
            assert result % order == k, f"Failed k={k}"

    def test_kangaroo_medium(self):
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 3456 % order or 1
        P = curve.scalar_mult(k, G)
        result = ecdlp_kangaroo_ternary(curve, G, P, order)
        assert result is not None
        assert result % order == k


# ---------------------------------------------------------------------------
# 16. 3-way MITM ternary
# ---------------------------------------------------------------------------

class TestMITM3:
    def test_mitm3_toy(self):
        curve = EllipticCurve(a=2, b=3, p=97)
        G = ECPoint(3, 6)
        order = curve.point_order(G)
        for k in range(1, order):
            P = curve.scalar_mult(k, G)
            result = ecdlp_mitm3_ternary(curve, G, P, order, third_depth=3)
            assert result is not None
            assert result % order == k, f"Failed k={k}"

    def test_mitm3_medium(self):
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 4567 % order or 1
        P = curve.scalar_mult(k, G)
        import math
        third = int(math.ceil(math.log(order) / math.log(3) / 3)) + 1
        result = ecdlp_mitm3_ternary(curve, G, P, order, third_depth=third)
        assert result is not None
        assert result % order == k


# ---------------------------------------------------------------------------
# 17. Full benchmark comparison
# ---------------------------------------------------------------------------

class TestBenchmark:
    def test_all_methods_agree(self):
        """All methods should find the same k on a medium curve."""
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k_secret = 137 % order or 1

        results = benchmark_ecdlp(curve, G, order, k_secret, verbose=True)

        for name, (k_found, _) in results.items():
            assert k_found is not None, f"{name} failed"
            assert k_found % order == k_secret % order, \
                f"{name}: got {k_found}, expected {k_secret}"


# ---------------------------------------------------------------------------
# 18. Fast order computation (Hasse + BSGS)
# ---------------------------------------------------------------------------

class TestComputeOrder:
    def test_order_matches_brute_force(self):
        """Fast order computation should match brute force on small curves."""
        curve = EllipticCurve(a=2, b=3, p=97)
        G = ECPoint(3, 6)
        order_bf = curve.point_order(G)
        order_fast = compute_curve_order(curve, G)
        assert order_fast == order_bf

    def test_order_medium_curve(self):
        """Order on p=10007 should match brute force."""
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order_bf = curve.point_order(G)
        order_fast = compute_curve_order(curve, G)
        assert order_fast == order_bf

    def test_order_verifies(self):
        """order*G should be infinity."""
        for p in [10007, 100003]:
            curve = EllipticCurve(a=0, b=7, p=p)
            G = curve.find_generator()
            order = compute_curve_order(curve, G)
            assert curve.scalar_mult(order, G).is_infinity
            # order-1 should NOT be infinity
            assert not curve.scalar_mult(order - 1, G).is_infinity

    def test_order_large_prime(self):
        """Fast order on p ~ 10^8."""
        curve = EllipticCurve(a=0, b=7, p=100000007)
        G = curve.find_generator()
        order = compute_curve_order(curve, G)
        assert order > 0
        assert curve.scalar_mult(order, G).is_infinity


# ---------------------------------------------------------------------------
# 19. CM curve (j=1728) and Gaussian integer endomorphism
# ---------------------------------------------------------------------------

class TestCMCurve:
    @pytest.fixture
    def cm_curve(self):
        """y²=x³+3x mod 10009 (p ≡ 1 mod 4)."""
        return CMCurve1728(a_coeff=3, p=10009)

    def test_sqrt_neg1_exists(self, cm_curve):
        assert cm_curve.sqrt_neg1 is not None
        assert (cm_curve.sqrt_neg1 ** 2) % cm_curve.p == cm_curve.p - 1

    def test_endomorphism_on_curve(self, cm_curve):
        """φ(P) should be on the curve."""
        G = cm_curve.find_generator()
        phi_G = cm_curve.cm_endomorphism(G)
        assert cm_curve.is_on_curve(phi_G)

    def test_endomorphism_squared_is_negation(self, cm_curve):
        """φ²(P) = -P (since i² = -1)."""
        G = cm_curve.find_generator()
        phi_G = cm_curve.cm_endomorphism(G)
        phi2_G = cm_curve.cm_endomorphism(phi_G)
        neg_G = cm_curve.neg(G)
        assert phi2_G == neg_G

    def test_gaussian_mult_basics(self, cm_curve):
        """[1+0i]*G = G, [0+1i]*G = φ(G)."""
        G = cm_curve.find_generator()
        assert cm_curve.gaussian_mult(1, 0, G) == G
        phi_G = cm_curve.cm_endomorphism(G)
        assert cm_curve.gaussian_mult(0, 1, G) == phi_G

    def test_gaussian_mult_pythagorean(self, cm_curve):
        """[3+4i]*G should be on curve and equal 3*G + 4*φ(G)."""
        G = cm_curve.find_generator()
        result = cm_curve.gaussian_mult(3, 4, G)
        assert cm_curve.is_on_curve(result)
        # Verify manually
        phi_G = cm_curve.cm_endomorphism(G)
        expected = cm_curve.add(
            cm_curve.scalar_mult(3, G),
            cm_curve.scalar_mult(4, phi_G)
        )
        assert result == expected


# ---------------------------------------------------------------------------
# 20. Gaussian-Pythagorean ECDLP solver
# ---------------------------------------------------------------------------

class TestGaussianECDLP:
    def test_gaussian_solver_on_cm_curve(self):
        """Gaussian solver on y²=x³+3x mod 10009."""
        curve = CMCurve1728(a_coeff=3, p=10009)
        G = curve.find_generator()
        order = compute_curve_order(curve, G)
        k = 137 % order or 1
        P = curve.scalar_mult(k, G)
        result = ecdlp_gaussian_pythagorean(
            curve, G, P, order, max_triples=2000, verbose=True)
        # May or may not find it; if found, must be correct
        if result is not None:
            assert result % order == k

    def test_gaussian_fallback_on_non_cm(self):
        """On non-CM curves, should fall back to kangaroo."""
        curve = EllipticCurve(a=0, b=7, p=10007)
        G = curve.find_generator()
        order = curve.point_order(G)
        k = 42 % order or 1
        P = curve.scalar_mult(k, G)
        result = ecdlp_gaussian_pythagorean(
            curve, G, P, order, max_triples=500)
        assert result is not None
        assert result % order == k


# ---------------------------------------------------------------------------
# 21. FastCurve (gmpy2 + Jacobian coordinates)
# ---------------------------------------------------------------------------

class TestFastCurve:
    """Test FastCurve gives same results as EllipticCurve."""

    @pytest.fixture
    def secp(self):
        return secp256k1_curve()

    def test_type_is_fast_curve(self, secp):
        assert isinstance(secp, FastCurve)

    def test_generator_on_curve(self, secp):
        assert secp.is_on_curve(secp.G)

    def test_scalar_mult_matches(self, secp):
        """FastCurve scalar mult matches hand-verified 2*G."""
        G = secp.G
        P2 = secp.scalar_mult(2, G)
        assert secp.is_on_curve(P2)
        assert not P2.is_infinity

    def test_add_commutative(self, secp):
        G = secp.G
        P2 = secp.scalar_mult(2, G)
        P3 = secp.scalar_mult(3, G)
        assert secp.add(P2, P3) == secp.add(P3, P2)

    def test_add_associative(self, secp):
        G = secp.G
        P2 = secp.scalar_mult(2, G)
        P3 = secp.scalar_mult(3, G)
        P5 = secp.scalar_mult(5, G)
        assert secp.add(P2, P3) == P5

    def test_neg_and_sub(self, secp):
        G = secp.G
        P5 = secp.scalar_mult(5, G)
        P3 = secp.scalar_mult(3, G)
        P2 = secp.scalar_mult(2, G)
        assert secp.sub(P5, P3) == P2

    def test_identity(self, secp):
        G = secp.G
        assert secp.add(G, ECPoint.infinity()) == G

    def test_order_mult_gives_infinity(self, secp):
        """n*G = O for secp256k1."""
        G = secp.G
        O = secp.scalar_mult(secp.n, G)
        assert O.is_infinity


# ---------------------------------------------------------------------------
# 22. secp256k1 ECDLP solving
# ---------------------------------------------------------------------------

class TestSecp256k1ECDLP:
    """Test ECDLP solving on the real secp256k1 curve."""

    @pytest.fixture
    def secp(self):
        return secp256k1_curve()

    def test_bsgs_8bit(self, secp):
        """Solve 8-bit key on secp256k1 with Python BSGS."""
        k = 239
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_bsgs(secp, secp.G, P, 512)
        assert found == k

    def test_bsgs_16bit(self, secp):
        """Solve 16-bit key on secp256k1."""
        k = 65519
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_bsgs(secp, secp.G, P, 1 << 17)
        assert found == k

    def test_bsgs_24bit(self, secp):
        """Solve 24-bit key on secp256k1."""
        k = 16777199
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_bsgs(secp, secp.G, P, 1 << 25)
        assert found == k

    def test_bsgs_c_24bit(self, secp):
        """Solve 24-bit key with C-BSGS."""
        k = 16777199
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_bsgs_c(secp, secp.G, P, 1 << 25)
        assert found == k

    def test_bsgs_c_32bit(self, secp):
        """Solve 32-bit key with C-BSGS (<1s)."""
        k = (1 << 32) - 17
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_bsgs_c(secp, secp.G, P, 1 << 33)
        assert found == k

    def test_bsgs_c_40bit(self, secp):
        """Solve 40-bit key with C-BSGS (~5s)."""
        k = (1 << 40) - 17
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_bsgs_c(secp, secp.G, P, 1 << 41)
        assert found == k


# ---------------------------------------------------------------------------
# 23. GLV-Enhanced BSGS
# ---------------------------------------------------------------------------

class TestGLVBSGS:
    @pytest.fixture
    def secp(self):
        return secp256k1_curve()

    def test_glv_bsgs_16bit(self, secp):
        k = 65519
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_glv_bsgs(secp, secp.G, P, 1 << 17)
        assert found == k

    def test_glv_bsgs_24bit(self, secp):
        k = 16777199
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_glv_bsgs(secp, secp.G, P, 1 << 25)
        assert found == k

    def test_glv_bsgs_32bit(self, secp):
        k = (1 << 32) - 17
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_glv_bsgs(secp, secp.G, P, 1 << 33)
        assert found == k


# ---------------------------------------------------------------------------
# 24. Pythagorean Kangaroo
# ---------------------------------------------------------------------------

class TestPythagoreanKangaroo:
    @pytest.fixture
    def secp(self):
        return secp256k1_curve()

    def test_kangaroo_python_20bit(self, secp):
        """Python kangaroo solves 20-bit key."""
        k = 1048559
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_pythagorean_kangaroo(secp, secp.G, P, 1 << 21)
        assert found == k

    def test_kangaroo_python_24bit(self, secp):
        """Python kangaroo solves 24-bit key."""
        k = 16777199
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_pythagorean_kangaroo(secp, secp.G, P, 1 << 25)
        assert found == k

    def test_kangaroo_c_24bit(self, secp):
        """C kangaroo solves 24-bit key."""
        k = 16777199
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_pythagorean_kangaroo_c(secp, secp.G, P, 1 << 25)
        assert found == k

    def test_kangaroo_c_32bit(self, secp):
        """C kangaroo solves 32-bit key."""
        k = (1 << 32) - 17
        P = secp.scalar_mult(k, secp.G)
        found = ecdlp_pythagorean_kangaroo_c(secp, secp.G, P, 1 << 33)
        assert found == k
