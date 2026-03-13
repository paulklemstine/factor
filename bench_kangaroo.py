#!/usr/bin/env python3
"""Benchmark C Kangaroo vs C BSGS on secp256k1."""
import sys, time, random
sys.path.insert(0, '.')
from ecdlp_pythagorean import secp256k1_curve, ecdlp_bsgs_c, ecdlp_pythagorean_kangaroo_c

curve = secp256k1_curve()
G = curve.G

print("=== secp256k1: C-Kangaroo vs C-BSGS ===")
print(f" {'Bits':>4s}  {'C-Kangaroo':>14s}  {'C-BSGS':>14s}")

for bits in range(20, 52, 4):
    bound = 1 << bits
    k = random.randint(1, bound - 1)
    P = curve.scalar_mult(k, G)

    # C Kangaroo
    t0 = time.time()
    r1 = ecdlp_pythagorean_kangaroo_c(curve, G, P, bound)
    t1 = time.time() - t0
    ok1 = "OK" if r1 == k else "FAIL"

    # C BSGS (skip if > 44 bits due to memory)
    if bits <= 44:
        t0 = time.time()
        r2 = ecdlp_bsgs_c(curve, G, P, bound)
        t2 = time.time() - t0
        ok2 = "OK" if r2 == k else "FAIL"
        bsgs_str = f"{t2:8.3f}s {ok2}"
    else:
        bsgs_str = "  (skipped)"

    print(f" {bits:4d}  {t1:8.3f}s {ok1:4s}  {bsgs_str}")
    sys.stdout.flush()

    if t1 > 120:
        print("  (time limit)")
        break
