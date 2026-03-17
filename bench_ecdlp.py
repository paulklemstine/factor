#!/usr/bin/env python3
"""ECDLP benchmark: shared kangaroo (6 workers) and single CPU at 36b, 40b, 44b."""
import time
import signal
import sys
import random

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, '.')

from ecdlp_pythagorean import (
    secp256k1_curve, ecdlp_shared_kangaroo,
    ecdlp_pythagorean_kangaroo_c
)

curve = secp256k1_curve()
G = curve.G

def make_ecdlp_instance(bits, seed):
    """Generate a random ECDLP instance: P = k*G where k < 2^bits."""
    rng = random.Random(seed)
    k = rng.randint(1, (1 << bits) - 1)
    P = curve.scalar_mult(k, G)
    return k, P

results = []

# Shared kangaroo (6 workers): 36b, 40b, 44b — 3 trials each
print("=" * 60)
print("ECDLP SHARED KANGAROO (6 workers)")
print("=" * 60)

for bits in [36, 40, 44]:
    times = []
    for trial in range(3):
        k, P = make_ecdlp_instance(bits, seed=bits*100 + trial)
        search_bound = 1 << bits
        print(f"  {bits}b trial {trial+1}...", end=" ", flush=True)
        signal.alarm(120)
        t0 = time.time()
        try:
            result = ecdlp_shared_kangaroo(curve, G, P, search_bound,
                                            num_workers=6, verbose=False)
            elapsed = time.time() - t0
            ok = (result == k)
            times.append(elapsed)
            print(f"{'OK' if ok else 'WRONG'} {elapsed:.2f}s", flush=True)
        except Exception as e:
            elapsed = time.time() - t0
            print(f"ERR {elapsed:.1f}s ({e})", flush=True)
    if times:
        avg = sum(times) / len(times)
        results.append(("Shared-6w", bits, avg, len(times)))
        print(f"  -> {bits}b avg: {avg:.2f}s ({len(times)} trials)", flush=True)

# Single CPU kangaroo: 36b, 40b, 44b — 3 trials each
print("\n" + "=" * 60)
print("ECDLP SINGLE CPU KANGAROO")
print("=" * 60)

for bits in [36, 40, 44]:
    times = []
    for trial in range(3):
        k, P = make_ecdlp_instance(bits, seed=bits*100 + trial)
        search_bound = 1 << bits
        print(f"  {bits}b trial {trial+1}...", end=" ", flush=True)
        signal.alarm(60)
        t0 = time.time()
        try:
            result = ecdlp_pythagorean_kangaroo_c(curve, G, P, search_bound,
                                                    verbose=False)
            elapsed = time.time() - t0
            ok = (result == k)
            times.append(elapsed)
            print(f"{'OK' if ok else 'WRONG'} {elapsed:.2f}s", flush=True)
        except Exception as e:
            elapsed = time.time() - t0
            print(f"ERR {elapsed:.1f}s ({e})", flush=True)
    if times:
        avg = sum(times) / len(times)
        results.append(("Single", bits, avg, len(times)))
        print(f"  -> {bits}b avg: {avg:.2f}s ({len(times)} trials)", flush=True)

# Scoreboard
print("\n" + "=" * 60)
print("ECDLP SCOREBOARD")
print("=" * 60)
print(f"{'Method':<12} {'Bits':>6} {'Avg Time':>10} {'Trials':>8}")
print("-" * 40)
for method, bits, avg, n_trials in results:
    print(f"{method:<12} {bits:>6}b {avg:>9.2f}s {n_trials:>8}")
