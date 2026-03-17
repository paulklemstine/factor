#!/usr/bin/env python3
"""
Benchmark: GPU kangaroo vs CPU shared-memory kangaroo (6 workers).
Tests at 48b, 52b, 56b with 3 trials each.
"""

import time
import signal
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ecdlp_pythagorean import (
    EllipticCurve, ECPoint,
    ecdlp_pythagorean_kangaroo_gpu,
    ecdlp_shared_kangaroo,
)

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

curve = EllipticCurve(a, b, p, ECPoint(Gx, Gy), n)
G = ECPoint(Gx, Gy)

TIMEOUT = 120  # seconds per trial

def make_test_point(bits):
    """Create a test point P = k*G with known k of given bit size."""
    k = random.randint(2**(bits-1), 2**bits - 1)
    P = curve.scalar_mult(k, G)
    return k, P

def run_trial(method_name, method_func, P, search_bound, timeout=TIMEOUT):
    """Run a single trial with timeout. Returns (time, success)."""
    t0 = time.time()
    try:
        signal.alarm(timeout)
        result = method_func(curve, G, P, search_bound, verbose=False)
        signal.alarm(0)
        elapsed = time.time() - t0
        return elapsed, result is not None
    except Exception as e:
        signal.alarm(0)
        elapsed = time.time() - t0
        return elapsed, False

def timeout_handler(signum, frame):
    raise TimeoutError("Trial timed out")

signal.signal(signal.SIGALRM, timeout_handler)

def bench_at_bits(bits, n_trials=3):
    """Run benchmark at a given bit size."""
    print(f"\n{'='*60}")
    print(f"  Benchmarking at {bits}-bit scalar ({n_trials} trials)")
    print(f"{'='*60}")

    search_bound = 2**bits

    gpu_times = []
    shared_times = []

    for trial in range(n_trials):
        k, P = make_test_point(bits)
        print(f"\n  Trial {trial+1}: k = {k} ({k.bit_length()}b)")

        # GPU kangaroo
        try:
            elapsed, ok = run_trial("GPU", ecdlp_pythagorean_kangaroo_gpu,
                                     P, search_bound)
            status = "OK" if ok else "FAIL"
            print(f"    GPU:    {elapsed:7.2f}s  [{status}]")
            if ok:
                gpu_times.append(elapsed)
        except TimeoutError:
            print(f"    GPU:    TIMEOUT (>{TIMEOUT}s)")

        # CPU shared (6 workers)
        def shared_wrapper(c, g, p, sb, verbose=False):
            return ecdlp_shared_kangaroo(c, g, p, sb, num_workers=6, verbose=verbose)
        try:
            elapsed, ok = run_trial("Shared", shared_wrapper, P, search_bound)
            status = "OK" if ok else "FAIL"
            print(f"    Shared: {elapsed:7.2f}s  [{status}]")
            if ok:
                shared_times.append(elapsed)
        except TimeoutError:
            print(f"    Shared: TIMEOUT (>{TIMEOUT}s)")

    print(f"\n  Summary at {bits}b:")
    if gpu_times:
        avg_gpu = sum(gpu_times) / len(gpu_times)
        print(f"    GPU avg:    {avg_gpu:.2f}s  ({len(gpu_times)}/{n_trials} succeeded)")
    else:
        avg_gpu = None
        print(f"    GPU avg:    N/A (0/{n_trials} succeeded)")

    if shared_times:
        avg_shared = sum(shared_times) / len(shared_times)
        print(f"    Shared avg: {avg_shared:.2f}s  ({len(shared_times)}/{n_trials} succeeded)")
    else:
        avg_shared = None
        print(f"    Shared avg: N/A (0/{n_trials} succeeded)")

    if avg_gpu and avg_shared:
        ratio = avg_shared / avg_gpu
        winner = "GPU" if ratio > 1 else "Shared"
        print(f"    Ratio:      {ratio:.2f}x ({winner} wins)")

    return avg_gpu, avg_shared

if __name__ == "__main__":
    print("GPU vs CPU Shared-Memory Kangaroo Benchmark")
    print(f"Timeout per trial: {TIMEOUT}s")

    results = {}
    for bits in [48, 52, 56]:
        avg_gpu, avg_shared = bench_at_bits(bits, n_trials=3)
        results[bits] = (avg_gpu, avg_shared)

    print(f"\n{'='*60}")
    print("  FINAL RESULTS")
    print(f"{'='*60}")
    print(f"  {'Bits':>4s}  {'GPU avg':>10s}  {'Shared avg':>10s}  {'Speedup':>10s}")
    for bits in [48, 52, 56]:
        g, s = results[bits]
        gs = f"{g:.2f}s" if g else "N/A"
        ss = f"{s:.2f}s" if s else "N/A"
        if g and s:
            ratio = s / g
            sp = f"{ratio:.2f}x GPU"
        else:
            sp = "N/A"
        print(f"  {bits:>4d}  {gs:>10s}  {ss:>10s}  {sp:>10s}")
