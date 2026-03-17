#!/usr/bin/env python3
"""
Fast benchmark: GPU kangaroo vs CPU shared-memory kangaroo.
Uses C libraries directly via ctypes to avoid Python EC overhead.
Tests at 48b, 52b, 56b with 3 trials each.
"""

import time
import signal
import sys
import os
import ctypes
import random

TIMEOUT = 120

def timeout_handler(signum, frame):
    raise TimeoutError("Trial timed out")

signal.signal(signal.SIGALRM, timeout_handler)

# secp256k1 constants
Gx_hex = b"79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
Gy_hex = b"483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"
N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def load_libs():
    base = "/home/raver1975/factor"
    gpu_lib = ctypes.CDLL(os.path.join(base, "ec_kangaroo_gpu.so"))
    # shared lib needs mmap setup — use the Python wrapper instead
    return gpu_lib

def compute_kG_via_gpu_lib(lib, k):
    """Use the GPU lib's host EC scalar mult to compute k*G, return (Px_hex, Py_hex)."""
    # We'll use the GPU solver with a known k — it should find it quickly
    # Actually, let's just compute k*G using Python gmpy2
    import gmpy2
    from gmpy2 import mpz

    p = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
    gx = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
    gy = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

    def ec_add(px, py, qx, qy):
        if px is None: return qx, qy
        if qx is None: return px, py
        if px == qx:
            if py == qy:
                if py == 0: return None, None
                lam = (3 * px * px) * gmpy2.invert(2 * py, p) % p
            else:
                return None, None
        else:
            lam = (qy - py) * gmpy2.invert(qx - px, p) % p
        rx = (lam * lam - px - qx) % p
        ry = (lam * (px - rx) - py) % p
        return rx, ry

    def ec_smul(k, gx, gy):
        rx, ry = None, None
        bx, by = gx, gy
        k = mpz(k)
        while k > 0:
            if k & 1:
                rx, ry = ec_add(rx, ry, bx, by)
            bx, by = ec_add(bx, by, bx, by)
            k >>= 1
        return rx, ry

    px, py = ec_smul(k, gx, gy)
    return format(int(px), 'x').encode(), format(int(py), 'x').encode()

def bench_gpu(lib, Px_hex, Py_hex, bound_hex):
    result_buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    signal.alarm(TIMEOUT)
    ret = lib.ec_kang_gpu_solve(Gx_hex, Gy_hex, Px_hex, Py_hex,
                                 bound_hex, result_buf, ctypes.c_size_t(256))
    signal.alarm(0)
    elapsed = time.time() - t0
    if ret == 1:
        k = int(result_buf.value.decode(), 16)
        return elapsed, k
    return elapsed, None

def bench_shared(Px_hex, Py_hex, bound_hex):
    """Run shared kangaroo via Python wrapper."""
    sys.path.insert(0, "/home/raver1975/factor")
    from ecdlp_pythagorean import (EllipticCurve, ECPoint, ecdlp_shared_kangaroo)

    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    curve = EllipticCurve(0, 7, p,
                          ECPoint(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
                                  0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8),
                          N_ORDER)
    G = curve.G
    Px = int(Px_hex, 16) if isinstance(Px_hex, str) else int(Px_hex.decode(), 16)
    Py = int(Py_hex, 16) if isinstance(Py_hex, str) else int(Py_hex.decode(), 16)
    P = ECPoint(Px, Py)
    bound = int(bound_hex, 16) if isinstance(bound_hex, str) else int(bound_hex.decode(), 16)

    t0 = time.time()
    signal.alarm(TIMEOUT)
    k = ecdlp_shared_kangaroo(curve, G, P, bound, num_workers=6, verbose=False)
    signal.alarm(0)
    elapsed = time.time() - t0
    return elapsed, k

def main():
    print("GPU vs CPU Shared-Memory Kangaroo Benchmark")
    print(f"Timeout per trial: {TIMEOUT}s\n")

    gpu_lib = load_libs()

    results = {}
    for bits in [48, 52, 56]:
        bound = 1 << bits
        bound_hex = format(bound, 'x').encode()

        print(f"{'='*60}")
        print(f"  {bits}-bit scalar (3 trials)")
        print(f"{'='*60}")

        gpu_times = []
        shared_times = []

        for trial in range(3):
            k = random.randint(1 << (bits - 1), (1 << bits) - 1)
            print(f"\n  Trial {trial+1}: k = {k} ({k.bit_length()}b)")

            Px_hex, Py_hex = compute_kG_via_gpu_lib(gpu_lib, k)

            # GPU
            try:
                elapsed, found_k = bench_gpu(gpu_lib, Px_hex, Py_hex, bound_hex)
                ok = found_k is not None and found_k == k
                print(f"    GPU:    {elapsed:7.2f}s  [{'OK' if ok else 'FAIL'}]")
                if ok: gpu_times.append(elapsed)
            except TimeoutError:
                signal.alarm(0)
                print(f"    GPU:    TIMEOUT (>{TIMEOUT}s)")

            # Shared (6 workers)
            try:
                elapsed, found_k = bench_shared(Px_hex, Py_hex, bound_hex)
                ok = found_k is not None and found_k == k
                print(f"    Shared: {elapsed:7.2f}s  [{'OK' if ok else 'FAIL'}]")
                if ok: shared_times.append(elapsed)
            except TimeoutError:
                signal.alarm(0)
                print(f"    Shared: TIMEOUT (>{TIMEOUT}s)")

        avg_gpu = sum(gpu_times) / len(gpu_times) if gpu_times else None
        avg_shared = sum(shared_times) / len(shared_times) if shared_times else None
        results[bits] = (avg_gpu, avg_shared)

        print(f"\n  Summary at {bits}b:")
        if avg_gpu: print(f"    GPU avg:    {avg_gpu:.2f}s  ({len(gpu_times)}/3)")
        else: print(f"    GPU avg:    N/A")
        if avg_shared: print(f"    Shared avg: {avg_shared:.2f}s  ({len(shared_times)}/3)")
        else: print(f"    Shared avg: N/A")
        if avg_gpu and avg_shared:
            ratio = avg_shared / avg_gpu
            print(f"    Speedup:    {ratio:.1f}x {'GPU' if ratio > 1 else 'Shared'} wins")

    print(f"\n{'='*60}")
    print("  FINAL RESULTS")
    print(f"{'='*60}")
    print(f"  {'Bits':>4s}  {'GPU avg':>10s}  {'Shared avg':>10s}  {'Speedup':>10s}")
    for bits in [48, 52, 56]:
        g, s = results[bits]
        gs = f"{g:.2f}s" if g else "N/A"
        ss = f"{s:.2f}s" if s else "N/A"
        sp = f"{s/g:.1f}x GPU" if g and s else "N/A"
        print(f"  {bits:>4d}  {gs:>10s}  {ss:>10s}  {sp:>10s}")

if __name__ == "__main__":
    main()
