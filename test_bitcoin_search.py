#!/usr/bin/env python3
"""
Bitcoin private key search.

Generates random Bitcoin addresses with full 256-bit private keys,
then attempts to find the private key by searching [0, 2^max_bits).
Any found key is verified by re-deriving the address.

This is an honest test: random 256-bit keys are almost never in the
searchable range, so most attempts will timeout. But if one is found,
it's a real result.

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
    ecdlp_pythagorean_kangaroo_c,
    secp256k1_curve,
)

KEYS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "found_keys.txt")

# secp256k1 order
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def sha256(data):
    return hashlib.sha256(data).digest()


def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()


def base58check_encode(payload):
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
    if compressed:
        prefix = b'\x02' if P.y % 2 == 0 else b'\x03'
        pubkey = prefix + P.x.to_bytes(32, 'big')
    else:
        pubkey = b'\x04' + P.x.to_bytes(32, 'big') + P.y.to_bytes(32, 'big')
    h160 = ripemd160(sha256(pubkey))
    return base58check_encode(b'\x00' + h160).decode()


def privkey_to_wif(k, compressed=True):
    raw = b'\x80' + k.to_bytes(32, 'big')
    if compressed:
        raw += b'\x01'
    return base58check_encode(raw).decode()


def log_found_key(k, address, wif, elapsed, attempt):
    with open(KEYS_FILE, 'a') as f:
        f.write(f"{'='*60}\n")
        f.write(f"Found: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Address:     {address}\n")
        f.write(f"Private Key: {k}\n")
        f.write(f"WIF:         {wif}\n")
        f.write(f"Hex:         {hex(k)}\n")
        f.write(f"Bits:        {k.bit_length()}\n")
        f.write(f"Time:        {elapsed:.2f}s\n")
        f.write(f"Attempt:     {attempt}\n")
        f.write(f"Verified:    YES (key -> address)\n")


def main():
    max_bits = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    max_attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    timeout = 60

    curve = secp256k1_curve()
    G = curve.G
    search_bound = 2**max_bits

    print(f"Bitcoin Address Private Key Search")
    print(f"Search range: [0, 2^{max_bits}) = {search_bound:,} keys")
    print(f"Keyspace: 2^256 ({2**256 // search_bound:.0e}x larger than search)")
    print(f"Timeout: {timeout}s per address")
    print(f"{'='*60}")

    found_count = 0
    attempt = 0

    class AlarmTimeout(Exception):
        pass

    def alarm_handler(signum, frame):
        raise AlarmTimeout()

    while max_attempts == 0 or attempt < max_attempts:
        attempt += 1

        # Generate a fully random 256-bit Bitcoin private key
        k = random.randint(1, N - 1)
        P = curve.scalar_mult(k, G)
        address = pubpoint_to_address(P)

        print(f"\nAttempt {attempt}:")
        print(f"  Address: {address}")
        print(f"  Pubkey:  02{hex(P.x)[2:][:16]}..." if P.y % 2 == 0
              else f"  Pubkey:  03{hex(P.x)[2:][:16]}...")
        print(f"  Searching [0, 2^{max_bits})...", end=" ", flush=True)

        t0 = time.time()
        old_handler = signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)

        try:
            result = ecdlp_pythagorean_kangaroo_c(curve, G, P, search_bound)
            elapsed = time.time() - t0
            signal.alarm(0)

            if result is not None:
                # Verify: does this key produce the target address?
                verify_P = curve.scalar_mult(result, G)
                verify_addr = pubpoint_to_address(verify_P)

                if verify_addr == address:
                    found_count += 1
                    wif = privkey_to_wif(result)
                    print(f"FOUND in {elapsed:.2f}s!")
                    print(f"  Private Key: {hex(result)}")
                    print(f"  WIF:         {wif}")
                    print(f"  Verified:    {verify_addr} == {address}")
                    log_found_key(result, address, wif, elapsed, attempt)
                    print(f"  Logged to {KEYS_FILE} (total: {found_count})")
                else:
                    print(f"key mismatch! {verify_addr} != {address}")
            else:
                print(f"not in range ({elapsed:.1f}s)")

        except AlarmTimeout:
            elapsed = time.time() - t0
            print(f"timeout ({elapsed:.0f}s)")

        except Exception as e:
            signal.alarm(0)
            print(f"error: {e}")

        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)

    print(f"\n{'='*60}")
    print(f"Searched {attempt} random addresses. Found {found_count} keys.")
    if found_count == 0:
        print(f"(Expected: random 256-bit keys are virtually never in [0, 2^{max_bits}))")


if __name__ == '__main__':
    main()
