#!/usr/bin/env python3
"""
Bitcoin private key search test.

Generates random secp256k1 key pairs, derives the Bitcoin address,
then uses our ECDLP Pythagorean Kangaroo solver to recover the key.
Times out after 60 seconds per attempt. Keeps trying until successful.

Usage: python3 test_bitcoin_search.py [max_bits]
  max_bits: maximum key size in bits (default: 48)
"""

import hashlib
import random
import sys
import time
from ecdlp_pythagorean import (
    ecdlp_pythagorean_kangaroo_c,
    secp256k1_curve,
)


def sha256(data):
    return hashlib.sha256(data).digest()


def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()


def base58check_encode(payload):
    """Encode bytes as Base58Check (Bitcoin address format)."""
    ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    checksum = sha256(sha256(payload))[:4]
    data = payload + checksum
    # Count leading zero bytes
    leading_zeros = 0
    for b in data:
        if b == 0:
            leading_zeros += 1
        else:
            break
    # Convert to base58
    n = int.from_bytes(data, 'big')
    result = []
    while n > 0:
        n, r = divmod(n, 58)
        result.append(ALPHABET[r:r+1])
    result.reverse()
    return b'1' * leading_zeros + b''.join(result)


def privkey_to_address(k, curve, G, compressed=True):
    """Derive Bitcoin P2PKH address from private key k."""
    P = curve.scalar_mult(k, G)
    if compressed:
        prefix = b'\x02' if P.y % 2 == 0 else b'\x03'
        pubkey = prefix + P.x.to_bytes(32, 'big')
    else:
        pubkey = b'\x04' + P.x.to_bytes(32, 'big') + P.y.to_bytes(32, 'big')
    h160 = ripemd160(sha256(pubkey))
    # Version byte 0x00 for mainnet
    address = base58check_encode(b'\x00' + h160)
    return address.decode(), P


def privkey_to_wif(k, compressed=True):
    """Convert private key integer to WIF format."""
    raw = b'\x80' + k.to_bytes(32, 'big')
    if compressed:
        raw += b'\x01'
    return base58check_encode(raw).decode()


def main():
    max_bits = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    timeout = 60  # seconds per attempt

    curve = secp256k1_curve()
    G = curve.G
    n = curve.n

    print(f"Bitcoin Private Key Search Test")
    print(f"Max search range: {max_bits} bits ({2**max_bits:,} keys)")
    print(f"Timeout: {timeout}s per attempt")
    print(f"{'='*60}")

    attempt = 0
    while True:
        attempt += 1
        # Generate a random key in [1, 2^max_bits)
        bits = random.randint(16, max_bits)
        k = random.randint(2**(bits-1), 2**bits - 1)
        address, P = privkey_to_address(k, curve, G)
        wif = privkey_to_wif(k)

        print(f"\nAttempt {attempt}: {bits}-bit key")
        print(f"  Address: {address}")
        print(f"  Key:     {k} ({bits}b)")

        # Try to find the key
        search_bound = 2**max_bits
        t0 = time.time()

        # Use signal for timeout on Unix
        import signal

        class TimeoutError(Exception):
            pass

        def handler(signum, frame):
            raise TimeoutError()

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)

        try:
            result = ecdlp_pythagorean_kangaroo_c(curve, G, P, search_bound)
            elapsed = time.time() - t0
            signal.alarm(0)

            if result == k:
                print(f"  FOUND in {elapsed:.2f}s!")
                print(f"\n{'='*60}")
                print(f"SUCCESS! Found key for Bitcoin address:")
                print(f"  Address:     {address}")
                print(f"  Private Key: {k}")
                print(f"  WIF:         {wif}")
                print(f"  Hex:         {hex(k)}")
                print(f"  Bits:        {bits}")
                print(f"  Time:        {elapsed:.2f}s")
                print(f"  Attempt:     {attempt}")
                print(f"{'='*60}")
                break
            elif result is not None:
                # Found a different key? Check negation
                if result == n - k:
                    print(f"  FOUND (negation) in {elapsed:.2f}s!")
                    print(f"  Result: {result}")
                    break
                else:
                    print(f"  Wrong key! Got {result}, expected {k}")
            else:
                print(f"  Not found in {elapsed:.2f}s (within step limit)")

        except TimeoutError:
            elapsed = time.time() - t0
            print(f"  Timeout after {elapsed:.1f}s")

        except Exception as e:
            signal.alarm(0)
            print(f"  Error: {e}")

        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)


if __name__ == '__main__':
    main()
