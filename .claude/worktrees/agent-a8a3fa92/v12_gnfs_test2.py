#!/usr/bin/env python3
"""GNFS long-running factorization tests v2: 45d, 49d, 50d"""

import sys, time, gmpy2, traceback
sys.path.insert(0, '/home/raver1975/factor')
from gnfs_engine import gnfs_factor

results = []

# ============================================================
# Test 1: GNFS 45d (warm-up, should succeed quickly)
# ============================================================
p = gmpy2.next_prime(gmpy2.mpz(10)**21 + 42)
q = gmpy2.next_prime(gmpy2.mpz(10)**21 + 179)
N = p * q
nd = len(str(int(N)))
print(f"=== GNFS {nd}d TEST ===")
print(f"N = {N} ({nd}d)")
print(f"p = {p}, q = {q}")
sys.stdout.flush()

t0 = time.time()
try:
    result = gnfs_factor(N, verbose=True, time_limit=1800)
except Exception as e:
    result = None
    print(f"EXCEPTION: {e}")
    traceback.print_exc()
elapsed = time.time() - t0

if result and result != N and N % result == 0:
    print(f"\n*** {nd}d SUCCESS: {result} x {N//result} in {elapsed:.1f}s ***")
    results.append((f"{nd}d", True, elapsed, str(result), str(N//result)))
else:
    print(f"\n*** {nd}d FAILED after {elapsed:.1f}s ***")
    results.append((f"{nd}d", False, elapsed, None, None))
sys.stdout.flush()

# ============================================================
# Test 2: GNFS 49d (the one that was 93% before — should now succeed)
# ============================================================
p = gmpy2.next_prime(gmpy2.mpz(10)**24 + 42)
q = gmpy2.next_prime(gmpy2.mpz(10)**24 + 179)
N = p * q
nd = len(str(int(N)))
print(f"\n\n=== GNFS {nd}d TEST ===")
print(f"N = {N} ({nd}d)")
print(f"p = {p}, q = {q}")
sys.stdout.flush()

t0 = time.time()
try:
    result49 = gnfs_factor(N, verbose=True, time_limit=1800)
except Exception as e:
    result49 = None
    print(f"EXCEPTION: {e}")
    traceback.print_exc()
elapsed49 = time.time() - t0

if result49 and result49 != N and N % result49 == 0:
    print(f"\n*** {nd}d SUCCESS: {result49} x {N//result49} in {elapsed49:.1f}s ***")
    results.append((f"{nd}d", True, elapsed49, str(result49), str(N//result49)))
else:
    print(f"\n*** {nd}d FAILED after {elapsed49:.1f}s ***")
    results.append((f"{nd}d", False, elapsed49, None, None))
sys.stdout.flush()

# ============================================================
# Test 3: GNFS true 50d (if 49d succeeded)
# ============================================================
if result49 and result49 != N:
    p = gmpy2.next_prime(gmpy2.mpz(10)**24 + 42)
    q = gmpy2.next_prime(gmpy2.mpz(10)**25 + 179)
    N = p * q
    nd = len(str(int(N)))
    print(f"\n\n=== GNFS {nd}d TEST ===")
    print(f"N = {N} ({nd}d)")
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
        print(f"\n*** {nd}d SUCCESS: {result50} x {N//result50} in {elapsed50:.1f}s ***")
        results.append((f"{nd}d", True, elapsed50, str(result50), str(N//result50)))
    else:
        print(f"\n*** {nd}d FAILED after {elapsed50:.1f}s ***")
        results.append((f"{nd}d", False, elapsed50, None, None))
    sys.stdout.flush()

    # ============================================================
    # Test 4: GNFS 55d (if 50d succeeded)
    # ============================================================
    if result50 and result50 != N:
        p = gmpy2.next_prime(gmpy2.mpz(10)**26 + 42)
        q = gmpy2.next_prime(gmpy2.mpz(10)**27 + 179)
        N = p * q
        nd = len(str(int(N)))
        print(f"\n\n=== GNFS {nd}d TEST ===")
        print(f"N = {N} ({nd}d)")
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
            print(f"\n*** {nd}d SUCCESS: {result55} x {N//result55} in {elapsed55:.1f}s ***")
            results.append((f"{nd}d", True, elapsed55, str(result55), str(N//result55)))
        else:
            print(f"\n*** {nd}d FAILED after {elapsed55:.1f}s ***")
            results.append((f"{nd}d", False, elapsed55, None, None))
        sys.stdout.flush()
else:
    print("\n\nSkipping further tests (49d did not succeed)")
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
