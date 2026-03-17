#!/usr/bin/env python3
"""
v9 Track A: GPU Lite Cofactor Benchmark
========================================
Tests the lightweight GPU kernel (smooth flag + cofactor only, no exponent bits).
The key insight: GPU filters candidates, CPU only does full TD on the ~5% that pass.
"""
import ctypes
import os
import sys
import time
import random

sys.stdout.reconfigure(line_buffering=True)

print("=" * 60, flush=True)
print("GPU Lite Cofactor Benchmark", flush=True)
print("=" * 60, flush=True)

# Load library
so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpu_cofactor_lite.so')
if not os.path.exists(so_path):
    print(f"ERROR: {so_path} not found", flush=True)
    sys.exit(1)

lib = ctypes.CDLL(so_path)
lib.gpu_lite_init.restype = ctypes.c_int
lib.gpu_lite_set_fb.restype = ctypes.c_int
lib.gpu_lite_set_fb.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_int]
lib.gpu_lite_batch.restype = ctypes.c_int
lib.gpu_lite_batch.argtypes = [
    ctypes.POINTER(ctypes.c_uint64), ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int),
    ctypes.c_uint64
]
lib.gpu_lite_cleanup.restype = None

ret = lib.gpu_lite_init()
print(f"GPU init: {'OK' if ret == 0 else 'FAILED'}", flush=True)
if ret != 0:
    sys.exit(1)

# Generate factor base (primes)
def sieve_primes(limit):
    s = [True] * limit
    s[0] = s[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if s[i]:
            for j in range(i*i, limit, i):
                s[j] = False
    return [i for i in range(2, limit) if s[i]]

all_primes = sieve_primes(200000)
print(f"Generated {len(all_primes)} primes", flush=True)

NUM_CANDIDATES = 1 << 16  # 65536

for fb_size in [500, 2000, 5000]:
    fb = all_primes[:fb_size]
    lp_bound = fb[-1] * 100

    print(f"\n--- FB size = {fb_size}, LP bound = {lp_bound} ---", flush=True)

    # Upload FB
    fb_arr = (ctypes.c_uint32 * fb_size)(*fb)
    lib.gpu_lite_set_fb(fb_arr, fb_size)

    # Generate candidates
    random.seed(42)
    candidates = []
    for i in range(NUM_CANDIDATES):
        if random.random() < 0.3:
            v = 1
            for _ in range(8 + random.randint(0, 7)):
                v *= fb[random.randint(0, min(499, fb_size - 1))]
                if v > (1 << 60):
                    break
            candidates.append(max(v, 1))
        else:
            candidates.append(random.randint(1 << 59, (1 << 60) - 1))

    cands_arr = (ctypes.c_uint64 * NUM_CANDIDATES)(*candidates)
    cofactors_arr = (ctypes.c_uint64 * NUM_CANDIDATES)()
    smooth_arr = (ctypes.c_int * NUM_CANDIDATES)()

    # Warmup
    lib.gpu_lite_batch(cands_arr, NUM_CANDIDATES, cofactors_arr, smooth_arr,
                       ctypes.c_uint64(lp_bound))

    # Benchmark GPU
    t0 = time.time()
    for _ in range(5):
        lib.gpu_lite_batch(cands_arr, NUM_CANDIDATES, cofactors_arr, smooth_arr,
                           ctypes.c_uint64(lp_bound))
    gpu_ms = (time.time() - t0) * 1000 / 5

    gpu_full = sum(1 for i in range(NUM_CANDIDATES) if smooth_arr[i] == 1)
    gpu_partial = sum(1 for i in range(NUM_CANDIDATES) if smooth_arr[i] == 2)
    gpu_dlp = sum(1 for i in range(NUM_CANDIDATES) if smooth_arr[i] == 3)
    gpu_fail = NUM_CANDIDATES - gpu_full - gpu_partial - gpu_dlp

    print(f"  GPU: {gpu_ms:.1f} ms for {NUM_CANDIDATES} candidates", flush=True)
    print(f"  Results: {gpu_full} smooth, {gpu_partial} partial, {gpu_dlp} DLP, {gpu_fail} fail", flush=True)
    print(f"  Throughput: {NUM_CANDIDATES / (gpu_ms / 1000):.0f} candidates/sec", flush=True)

    # CPU reference
    t0 = time.time()
    cpu_full = 0
    cpu_partial = 0
    for val in candidates:
        v = val
        for p in fb:
            while v % p == 0:
                v //= p
            if v == 1:
                break
        if v == 1:
            cpu_full += 1
        elif v <= lp_bound:
            cpu_partial += 1
    cpu_ms = (time.time() - t0) * 1000

    print(f"  CPU: {cpu_ms:.1f} ms", flush=True)
    print(f"  Results: {cpu_full} smooth, {cpu_partial} partial", flush=True)
    print(f"  Speedup (filter only): {cpu_ms / gpu_ms:.1f}x", flush=True)

    # Verify: check a few
    mismatches = 0
    for i in range(min(1000, NUM_CANDIDATES)):
        v = candidates[i]
        for p in fb:
            while v % p == 0:
                v //= p
            if v == 1:
                break
        cpu_flag = 1 if v == 1 else (2 if v <= lp_bound else 0)
        gpu_flag = 1 if smooth_arr[i] == 1 else (2 if smooth_arr[i] >= 2 else 0)
        if (cpu_flag > 0) != (gpu_flag > 0):
            mismatches += 1

    print(f"  Verification: {mismatches}/1000 mismatches", flush=True)

    # Hybrid timing: GPU filter + CPU TD on smooth only
    # GPU marks ~30% as smooth/partial, CPU does full TD on those
    t0 = time.time()
    lib.gpu_lite_batch(cands_arr, NUM_CANDIDATES, cofactors_arr, smooth_arr,
                       ctypes.c_uint64(lp_bound))
    # CPU TD only on smooth/partial candidates
    hybrid_full = 0
    for i in range(NUM_CANDIDATES):
        if smooth_arr[i] > 0:
            v = candidates[i]
            for p in fb:
                while v % p == 0:
                    v //= p
                if v == 1:
                    break
            if v == 1:
                hybrid_full += 1
    hybrid_ms = (time.time() - t0) * 1000

    gpu_pass_rate = sum(1 for i in range(NUM_CANDIDATES) if smooth_arr[i] > 0) / NUM_CANDIDATES
    print(f"  Hybrid (GPU filter + CPU TD on {gpu_pass_rate*100:.1f}%): {hybrid_ms:.1f} ms", flush=True)
    print(f"  Hybrid speedup over pure CPU: {cpu_ms / hybrid_ms:.2f}x", flush=True)

lib.gpu_lite_cleanup()
print("\nDone.", flush=True)
