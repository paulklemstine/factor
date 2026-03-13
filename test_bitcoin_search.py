#!/usr/bin/env python3
"""
Bitcoin private key search test.

Generates real 256-bit secp256k1 private keys where the key is known to lie
in a specific bit range [2^(b-1), 2^b). This mirrors the Bitcoin Puzzle
Transaction challenge format. Uses our ECDLP Kangaroo solver to recover keys.

Logs found keys with round-trip verification to found_keys.txt.

Usage: python3 test_bitcoin_search.py [max_bits] [max_attempts]
  max_bits: maximum key bit-length (default: 48)
  max_attempts: stop after N attempts (default: unlimited)
"""

import hashlib
import os
import random
import signal
import sys
import time
from ecdlp_pythagorean import (
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


def privkey_to_pubpoint(k, curve, G):
    """Compute public key point from private key."""
    return curve.scalar_mult(k, G)


def pubpoint_to_address(P, compressed=True):
    """Derive Bitcoin P2PKH address from public key point."""
    if compressed:
        prefix = b'\x02' if P.y % 2 == 0 else b'\x03'
        pubkey = prefix + P.x.to_bytes(32, 'big')
    else:
        pubkey = b'\x04' + P.x.to_bytes(32, 'big') + P.y.to_bytes(32, 'big')
    h160 = ripemd160(sha256(pubkey))
    address = base58check_encode(b'\x00' + h160)
    return address.decode()


def privkey_to_address(k, curve, G, compressed=True):
    """Derive Bitcoin P2PKH address from private key k."""
    P = privkey_to_pubpoint(k, curve, G)
    return pubpoint_to_address(P, compressed), P


def privkey_to_wif(k, compressed=True):
    """Convert private key integer to WIF format."""
    raw = b'\x80' + k.to_bytes(32, 'big')
    if compressed:
        raw += b'\x01'
    return base58check_encode(raw).decode()


def round_trip_verify(found_key, expected_address, curve, G):
    """Verify that the found key generates the expected address."""
    addr, _ = privkey_to_address(found_key, curve, G)
    return addr == expected_address


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
        f.write(f"Verified:    YES (round-trip)\n")


def main():
    max_bits = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    max_attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    timeout = 60  # seconds per attempt

    curve = secp256k1_curve()
    G = curve.G
    n = curve.n

    print(f"Bitcoin Puzzle Key Search")
    print(f"Key range: up to {max_bits} bits")
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
        # Pick a random bit-length, weighted toward harder (larger) keys
        bits = random.randint(max(16, max_bits - 16), max_bits)
        # Generate a real full-range key in [2^(bits-1), 2^bits)
        k = random.randint(2**(bits-1), 2**bits - 1)

        address, P = privkey_to_address(k, curve, G)
        wif = privkey_to_wif(k)

        print(f"\nAttempt {attempt}: {bits}-bit key")
        print(f"  Address:    {address}")
        print(f"  WIF:        {wif}")
        print(f"  Key (hex):  {hex(k)}")
        print(f"  Searching range [2^{bits-1}, 2^{bits})...")

        # Search the exact bit-range [2^(bits-1), 2^bits)
        # Kangaroo searches [0, search_bound), so subtract the base and
        # adjust the target point: P' = P - 2^(bits-1)*G
        lo = 2**(bits-1)
        hi = 2**bits
        search_bound = hi - lo  # = 2^(bits-1)

        # Compute offset point: P' = P - lo*G
        loG = curve.scalar_mult(lo, G)
        # P' = P + (-loG)
        neg_loG_y = curve.p - loG.y
        from ecdlp_pythagorean import ECPoint
        neg_loG = ECPoint(loG.x, neg_loG_y)
        P_offset = curve.add(P, neg_loG)

        t0 = time.time()
        old_handler = signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)

        try:
            result = ecdlp_pythagorean_kangaroo_c(curve, G, P_offset, search_bound)
            elapsed = time.time() - t0
            signal.alarm(0)

            if result is not None:
                # Recover the full key: k = result + lo
                found_key = result + lo
                # Also try negation
                if not round_trip_verify(found_key, address, curve, G):
                    found_key = lo + (search_bound - result)
                    if not round_trip_verify(found_key, address, curve, G):
                        # Try raw result as-is
                        found_key = result
                        if not round_trip_verify(found_key, address, curve, G):
                            found_key = n - result
                            if not round_trip_verify(found_key, address, curve, G):
                                print(f"  WRONG KEY! result={result}, expected k={k}")
                                print(f"  Round-trip verification FAILED")
                                continue

                found_count += 1
                found_wif = privkey_to_wif(found_key)
                print(f"  FOUND in {elapsed:.2f}s! (round-trip VERIFIED)")
                print(f"  Recovered: {hex(found_key)}")
                print(f"  WIF:       {found_wif}")
                log_found_key(found_key, address, found_wif, bits, elapsed, attempt)
                print(f"  Logged to {KEYS_FILE} (total found: {found_count})")
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
