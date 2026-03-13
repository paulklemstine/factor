#!/usr/bin/env python3
"""
Bitcoin private key search test.

Generates random Bitcoin addresses (with public keys in a solvable range),
then attempts to find the private key using our ECDLP Kangaroo solver.
Verifies any found key by re-deriving the address and checking it matches.

Logs found keys to found_keys.txt.

Usage: python3 test_bitcoin_search.py [max_bits] [max_attempts]
  max_bits: search range in bits (default: 48)
  max_attempts: stop after N attempts (default: unlimited)
"""

import hashlib
import os
import random
import signal
import sys
import time
from ecdlp_pythagorean import (
    ECPoint,
    ecdlp_pythagorean_kangaroo_c,
    secp256k1_curve,
)

KEYS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "found_keys.txt")


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
    leading_zeros = 0
    for b in data:
        if b == 0:
            leading_zeros += 1
        else:
            break
    n = int.from_bytes(data, 'big')
    result = []
    while n > 0:
        n, r = divmod(n, 58)
        result.append(ALPHABET[r:r+1])
    result.reverse()
    return b'1' * leading_zeros + b''.join(result)


def pubpoint_to_address(P, compressed=True):
    """Derive Bitcoin P2PKH address from a public key point."""
    if compressed:
        prefix = b'\x02' if P.y % 2 == 0 else b'\x03'
        pubkey = prefix + P.x.to_bytes(32, 'big')
    else:
        pubkey = b'\x04' + P.x.to_bytes(32, 'big') + P.y.to_bytes(32, 'big')
    h160 = ripemd160(sha256(pubkey))
    address = base58check_encode(b'\x00' + h160)
    return address.decode()


def privkey_to_wif(k, compressed=True):
    """Convert private key integer to WIF format."""
    raw = b'\x80' + k.to_bytes(32, 'big')
    if compressed:
        raw += b'\x01'
    return base58check_encode(raw).decode()


def log_found_key(k, address, wif, bits, elapsed, attempt):
    """Append found key to found_keys.txt."""
    with open(KEYS_FILE, 'a') as f:
        f.write(f"{'='*60}\n")
        f.write(f"Found: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Address:     {address}\n")
        f.write(f"Private Key: {k}\n")
        f.write(f"WIF:         {wif}\n")
        f.write(f"Hex:         {hex(k)}\n")
        f.write(f"Bits:        {bits}\n")
        f.write(f"Time:        {elapsed:.2f}s\n")
        f.write(f"Attempt:     {attempt}\n")
        f.write(f"Verified:    YES (key -> address round-trip)\n")


def generate_target_address(curve, G, max_bits):
    """
    Generate a random Bitcoin address whose private key is in a solvable range.
    Returns (address, public_key_point, bit_length).
    The private key is NOT returned — it's the unknown we're searching for.
    """
    bits = random.randint(max(16, max_bits - 16), max_bits)
    # Generate a random key in [2^(bits-1), 2^bits) — but we don't keep it
    secret = random.randint(2**(bits-1), 2**bits - 1)
    P = curve.scalar_mult(secret, G)
    address = pubpoint_to_address(P)
    return address, P, bits


def main():
    max_bits = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    max_attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    timeout = 60  # seconds per attempt

    curve = secp256k1_curve()
    G = curve.G

    print(f"Bitcoin Address -> Private Key Search")
    print(f"Search range: up to {max_bits} bits ({2**max_bits:,} keys)")
    print(f"Timeout: {timeout}s per attempt")
    print(f"Keys logged to: {KEYS_FILE}")
    print(f"{'='*60}")

    found_count = 0
    attempt = 0

    class AlarmTimeout(Exception):
        pass

    def alarm_handler(signum, frame):
        raise AlarmTimeout()

    while max_attempts == 0 or attempt < max_attempts:
        attempt += 1

        # Step 1: Pick a random Bitcoin address (public key known, private key unknown)
        target_addr, P, bits = generate_target_address(curve, G, max_bits)

        print(f"\nAttempt {attempt}: target {bits}-bit address")
        print(f"  Address: {target_addr}")
        print(f"  Pubkey:  ({hex(P.x)[:20]}..., {hex(P.y)[:20]}...)")
        print(f"  Searching [2^{bits-1}, 2^{bits})...")

        # Step 2: Search for the private key
        # Offset the point so kangaroo searches [0, 2^(bits-1))
        lo = 2**(bits-1)
        search_bound = lo  # range width = 2^(bits-1)

        loG = curve.scalar_mult(lo, G)
        neg_loG = ECPoint(loG.x, curve.p - loG.y)
        P_offset = curve.add(P, neg_loG)

        t0 = time.time()
        old_handler = signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)

        try:
            result = ecdlp_pythagorean_kangaroo_c(curve, G, P_offset, search_bound)
            elapsed = time.time() - t0
            signal.alarm(0)

            if result is not None:
                # Step 3: Recover full key and VERIFY by re-deriving address
                found_key = result + lo

                # Verify: does this key produce the target address?
                verify_P = curve.scalar_mult(found_key, G)
                verify_addr = pubpoint_to_address(verify_P)

                if verify_addr != target_addr:
                    # Try other recovery: lo + (search_bound - result)
                    found_key = lo + (search_bound - result)
                    verify_P = curve.scalar_mult(found_key, G)
                    verify_addr = pubpoint_to_address(verify_P)

                if verify_addr == target_addr:
                    found_count += 1
                    wif = privkey_to_wif(found_key)
                    print(f"  FOUND in {elapsed:.2f}s!")
                    print(f"  Private Key: {hex(found_key)}")
                    print(f"  WIF:         {wif}")
                    print(f"  Verify addr: {verify_addr}")
                    print(f"  VERIFIED: address matches!")
                    log_found_key(found_key, target_addr, wif, bits, elapsed, attempt)
                    print(f"  Logged to {KEYS_FILE} (total found: {found_count})")
                else:
                    print(f"  Found key {hex(found_key)} but address mismatch!")
                    print(f"  Expected: {target_addr}")
                    print(f"  Got:      {verify_addr}")
            else:
                print(f"  Not found in {elapsed:.2f}s (step limit reached)")

        except AlarmTimeout:
            elapsed = time.time() - t0
            print(f"  Timeout after {elapsed:.1f}s")

        except Exception as e:
            signal.alarm(0)
            import traceback
            traceback.print_exc()
            print(f"  Error: {e}")

        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)

    print(f"\n{'='*60}")
    print(f"Done. Found {found_count} keys in {attempt} attempts.")


if __name__ == '__main__':
    main()
