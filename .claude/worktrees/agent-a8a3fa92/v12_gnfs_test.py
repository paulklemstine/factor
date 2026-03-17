#!/usr/bin/env python3
"""GNFS long-running factorization tests: 45d, 50d, 55d"""

import sys, time, gmpy2, traceback
sys.path.insert(0, '/home/raver1975/factor')
from gnfs_engine import gnfs_factor

results = []

# ============================================================
# Test 1: GNFS 45d (warm-up)
# ============================================================
p = gmpy2.next_prime(gmpy2.mpz(10)**21 + 42)
q = gmpy2.next_prime(gmpy2.mpz(10)**21 + 179)
N = p * q
print(f"=== GNFS 45d TEST ===")
print(f"N = {N} ({len(str(N))}d)")
print(f"p = {p}, q = {q}")
sys.stdout.flush()

t0 = time.time()
try:
    result45 = gnfs_factor(N, verbose=True, time_limit=1800)
except Exception as e:
    result45 = None
    print(f"EXCEPTION: {e}")
    traceback.print_exc()
elapsed45 = time.time() - t0

if result45 and result45 != N and N % result45 == 0:
    print(f"\n*** 45d SUCCESS: {result45} x {N//result45} in {elapsed45:.1f}s ***")
    results.append(("45d", True, elapsed45, str(result45), str(N//result45)))
else:
    print(f"\n*** 45d FAILED after {elapsed45:.1f}s ***")
    results.append(("45d", False, elapsed45, None, None))
sys.stdout.flush()

# ============================================================
# Test 2: GNFS 50d (the real target)
# ============================================================
p = gmpy2.next_prime(gmpy2.mpz(10)**24 + 42)
q = gmpy2.next_prime(gmpy2.mpz(10)**24 + 179)
N = p * q
print(f"\n\n=== GNFS 50d TEST ===")
print(f"N = {N} ({len(str(N))}d)")
print(f"p = {p}, q = {q}")
sys.stdout.flush()

t0 = time.time()
try:
    result50 = gnfs_factor(N, verbose=True, time_limit=1800)
except Exception as e:
    result50 = None
    print(f"EXCEPTION: {e}")
    traceback.print_exc()
elapsed50 = time.time() - t0

if result50 and result50 != N and N % result50 == 0:
    print(f"\n*** 50d SUCCESS: {result50} x {N//result50} in {elapsed50:.1f}s ***")
    results.append(("50d", True, elapsed50, str(result50), str(N//result50)))
else:
    print(f"\n*** 50d FAILED after {elapsed50:.1f}s ***")
    results.append(("50d", False, elapsed50, None, None))
sys.stdout.flush()

# ============================================================
# Test 3: GNFS 55d (only if 50d succeeded)
# ============================================================
if result50 and result50 != N:
    p = gmpy2.next_prime(gmpy2.mpz(10)**26 + 42)
    q = gmpy2.next_prime(gmpy2.mpz(10)**27 + 179)
    N = p * q
    print(f"\n\n=== GNFS 55d TEST ===")
    print(f"N = {N} ({len(str(N))}d)")
    print(f"p = {p}, q = {q}")
    sys.stdout.flush()

    t0 = time.time()
    try:
        result55 = gnfs_factor(N, verbose=True, time_limit=1800)
    except Exception as e:
        result55 = None
        print(f"EXCEPTION: {e}")
        traceback.print_exc()
    elapsed55 = time.time() - t0

    if result55 and result55 != N and N % result55 == 0:
        print(f"\n*** 55d SUCCESS: {result55} x {N//result55} in {elapsed55:.1f}s ***")
        results.append(("55d", True, elapsed55, str(result55), str(N//result55)))
    else:
        print(f"\n*** 55d FAILED after {elapsed55:.1f}s ***")
        results.append(("55d", False, elapsed55, None, None))
    sys.stdout.flush()
else:
    print("\n\nSkipping 55d test (50d did not succeed)")
    sys.stdout.flush()

# ============================================================
# Summary
# ============================================================
print("\n\n" + "="*60)
print("FINAL RESULTS SUMMARY")
print("="*60)
for name, success, elapsed, p_str, q_str in results:
    status = "SUCCESS" if success else "FAILED"
    if success:
        print(f"  {name}: {status} in {elapsed:.1f}s  ({p_str} x {q_str})")
    else:
        print(f"  {name}: {status} after {elapsed:.1f}s")
print("="*60)
sys.stdout.flush()
