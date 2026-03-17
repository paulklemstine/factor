"""
TDD tests for RSA round-trip factoring demo.

Tests progress from unit-level RSA math up to full round-trip:
  1. Key generation correctness
  2. Sign / verify with known key
  3. Factor the modulus using our engines
  4. Recover private key from factors
  5. Forge a valid signature with recovered key
"""

import pytest
import gmpy2
from gmpy2 import mpz

# Module under test
from rsa_demo import (
    generate_rsa_keypair,
    rsa_sign,
    rsa_verify,
    recover_private_key,
    rsa_crack,
)


# ---------------------------------------------------------------------------
# 1. Key generation
# ---------------------------------------------------------------------------

class TestKeyGeneration:
    def test_keypair_components(self):
        """Keypair contains n, e, d, p, q."""
        pub, priv = generate_rsa_keypair(bit_size=64)
        assert "n" in pub and "e" in pub
        assert "d" in priv and "p" in priv and "q" in priv and "n" in priv

    def test_n_equals_p_times_q(self):
        pub, priv = generate_rsa_keypair(bit_size=64)
        assert pub["n"] == priv["p"] * priv["q"]

    def test_p_and_q_are_prime(self):
        pub, priv = generate_rsa_keypair(bit_size=64)
        assert gmpy2.is_prime(priv["p"])
        assert gmpy2.is_prime(priv["q"])

    def test_p_and_q_are_distinct(self):
        pub, priv = generate_rsa_keypair(bit_size=64)
        assert priv["p"] != priv["q"]

    def test_d_is_inverse_of_e(self):
        """e * d ≡ 1 (mod lcm(p-1, q-1))."""
        pub, priv = generate_rsa_keypair(bit_size=64)
        phi = gmpy2.lcm(priv["p"] - 1, priv["q"] - 1)
        assert (pub["e"] * priv["d"]) % phi == 1

    def test_modulus_bit_size(self):
        """Modulus should be approximately the requested bit size."""
        pub, _ = generate_rsa_keypair(bit_size=128)
        n_bits = int(gmpy2.log2(mpz(pub["n"]))) + 1
        assert 120 <= n_bits <= 130  # allow some slack


# ---------------------------------------------------------------------------
# 2. Sign and verify
# ---------------------------------------------------------------------------

class TestSignVerify:
    @pytest.fixture
    def keys_48d(self):
        """~48 digit modulus (160 bits) — factorable by SIQS in ~2s."""
        return generate_rsa_keypair(bit_size=160)

    def test_sign_returns_integer(self, keys_48d):
        pub, priv = keys_48d
        sig = rsa_sign(b"Hello, RSA!", priv)
        assert isinstance(sig, int)

    def test_verify_valid_signature(self, keys_48d):
        pub, priv = keys_48d
        msg = b"Hello, RSA!"
        sig = rsa_sign(msg, priv)
        assert rsa_verify(msg, sig, pub) is True

    def test_verify_rejects_wrong_message(self, keys_48d):
        pub, priv = keys_48d
        sig = rsa_sign(b"Hello, RSA!", priv)
        assert rsa_verify(b"Wrong message", sig, pub) is False

    def test_verify_rejects_wrong_signature(self, keys_48d):
        pub, priv = keys_48d
        sig = rsa_sign(b"Hello, RSA!", priv)
        assert rsa_verify(b"Hello, RSA!", sig + 1, pub) is False


# ---------------------------------------------------------------------------
# 3. Private key recovery from factors
# ---------------------------------------------------------------------------

class TestKeyRecovery:
    def test_recover_from_known_factors(self):
        pub, priv = generate_rsa_keypair(bit_size=128)
        recovered_d = recover_private_key(pub["n"], pub["e"], priv["p"], priv["q"])
        # recovered d may differ numerically but must be functionally equivalent
        msg_int = 42
        assert pow(msg_int, recovered_d, pub["n"]) == pow(msg_int, priv["d"], pub["n"])

    def test_recovered_key_signs_validly(self):
        pub, priv = generate_rsa_keypair(bit_size=128)
        recovered_d = recover_private_key(pub["n"], pub["e"], priv["p"], priv["q"])
        forged_priv = {**priv, "d": recovered_d}
        msg = b"Recovered key test"
        sig = rsa_sign(msg, forged_priv)
        assert rsa_verify(msg, sig, pub) is True


# ---------------------------------------------------------------------------
# 4. Full round-trip: generate -> sign -> FACTOR -> recover -> forge
# ---------------------------------------------------------------------------

class TestFullRoundTrip:
    @pytest.mark.parametrize("bit_size,method", [
        (80, "siqs"),     # ~24 digits — trivial for SIQS
        (128, "siqs"),    # ~38 digits — easy for SIQS
        (160, "siqs"),    # ~48 digits — SIQS sweet spot (~2s)
    ])
    def test_crack_rsa(self, bit_size, method):
        """
        End-to-end: generate keypair, factor modulus, recover key, forge signature.
        """
        pub, priv = generate_rsa_keypair(bit_size=bit_size)
        msg = b"The magic words are squeamish ossifrage"

        # Sign with real key
        real_sig = rsa_sign(msg, priv)
        assert rsa_verify(msg, real_sig, pub)

        # Crack: factor n, recover d, forge signature
        cracked_priv = rsa_crack(pub, time_limit=30)

        assert cracked_priv is not None, f"Failed to factor {len(str(pub['n']))}d modulus"
        assert cracked_priv["p"] * cracked_priv["q"] == pub["n"]

        # Forge a signature with cracked key
        forged_sig = rsa_sign(msg, cracked_priv)
        assert rsa_verify(msg, forged_sig, pub), "Forged signature should verify!"

        # The forged signature should be identical to the real one
        assert forged_sig == real_sig, "Forged sig must match real sig (deterministic RSA)"


    def test_crack_displays_progress(self, capsys):
        """Crack should print progress info."""
        pub, _ = generate_rsa_keypair(bit_size=80)
        rsa_crack(pub, verbose=True, time_limit=30)
        captured = capsys.readouterr()
        assert "Factoring" in captured.out
        assert "Recovered" in captured.out
