"""
RSA Round-Trip Factoring Demo.

Demonstrates: generate keypair -> sign -> factor modulus -> recover private key -> forge signature.

Uses our SIQS/GNFS engines to break deliberately small RSA keys.
"""

import hashlib
import gmpy2
from gmpy2 import mpz, invert, is_prime

from siqs_engine import siqs_factor


def generate_rsa_keypair(bit_size=160, e=65537):
    """
    Generate an RSA keypair with a modulus of approximately `bit_size` bits.

    Each prime is ~bit_size/2 bits, so the modulus is ~bit_size bits.
    Returns (public_key, private_key) dicts.
    """
    half = bit_size // 2
    rand_state = gmpy2.random_state()

    while True:
        p = gmpy2.next_prime(gmpy2.mpz_urandomb(rand_state, half) | (mpz(1) << (half - 1)))
        q = gmpy2.next_prime(gmpy2.mpz_urandomb(rand_state, half) | (mpz(1) << (half - 1)))
        if p == q:
            continue
        n = p * q
        phi = gmpy2.lcm(p - 1, q - 1)
        if gmpy2.gcd(e, phi) != 1:
            continue
        d = int(invert(e, phi))
        break

    pub = {"n": int(n), "e": e}
    priv = {"n": int(n), "e": e, "d": d, "p": int(p), "q": int(q)}
    return pub, priv


def _hash_message(message: bytes, n: int) -> int:
    """Hash message to an integer < n using SHA-256 (textbook RSA for demo)."""
    h = hashlib.sha256(message).digest()
    return int.from_bytes(h, "big") % n


def rsa_sign(message: bytes, private_key: dict) -> int:
    """Sign a message: signature = hash(msg)^d mod n."""
    h = _hash_message(message, private_key["n"])
    return int(pow(mpz(h), mpz(private_key["d"]), mpz(private_key["n"])))


def rsa_verify(message: bytes, signature: int, public_key: dict) -> bool:
    """Verify: hash(msg) == signature^e mod n."""
    h = _hash_message(message, public_key["n"])
    recovered = int(pow(mpz(signature), mpz(public_key["e"]), mpz(public_key["n"])))
    return recovered == h


def recover_private_key(n: int, e: int, p: int, q: int) -> int:
    """Given factors p, q of n, recover the RSA private exponent d."""
    phi = gmpy2.lcm(mpz(p - 1), mpz(q - 1))
    return int(invert(mpz(e), phi))


def rsa_crack(public_key: dict, verbose=True, time_limit=30):
    """
    Crack an RSA public key by factoring n.

    Uses SIQS (our engine) to find a factor, then recovers the private key.
    Returns a private_key dict, or None on failure.
    """
    n = public_key["n"]
    e = public_key["e"]
    nd = len(str(n))

    if verbose:
        print(f"Factoring {nd}-digit RSA modulus...")

    p = siqs_factor(n, verbose=verbose, time_limit=time_limit)
    if p is None or p == n or p == 1:
        if verbose:
            print("Factoring failed.")
        return None

    p = int(p)
    q = n // p
    assert p * q == n, "Factor verification failed"

    # Ensure p < q by convention
    if p > q:
        p, q = q, p

    d = recover_private_key(n, e, p, q)

    if verbose:
        print(f"Recovered private key! p={p}, q={q}")
        print(f"  d = {d}")

    return {"n": n, "e": e, "d": d, "p": p, "q": q}


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("=" * 60)
    print("RSA Round-Trip Factoring Demo")
    print("=" * 60)

    for bits in [80, 128, 160, 192]:
        print(f"\n--- {bits}-bit RSA key (~{bits * 3 // 10}d modulus) ---")

        pub, priv = generate_rsa_keypair(bit_size=bits)
        nd = len(str(pub["n"]))
        print(f"Generated {nd}-digit modulus: n = {pub['n']}")

        msg = b"The magic words are squeamish ossifrage"
        sig = rsa_sign(msg, priv)
        assert rsa_verify(msg, sig, pub)
        print(f"Signed and verified message with real key.")

        t0 = time.time()
        cracked = rsa_crack(pub, verbose=True, time_limit=60)
        elapsed = time.time() - t0

        if cracked:
            forged_sig = rsa_sign(msg, cracked)
            ok = rsa_verify(msg, forged_sig, pub)
            match = forged_sig == sig
            print(f"Forged signature valid: {ok}, matches original: {match}")
            print(f"Cracked in {elapsed:.1f}s")
        else:
            print(f"Failed to crack in {elapsed:.1f}s")

    print("\n" + "=" * 60)
    print("Demo complete.")
