#!/usr/bin/env python3
"""
Benchmark: GPU vs CPU ECDLP kangaroo solvers.
Tests at 28, 32, 36, 40, 44, 48 bits with 3 trials each.
"""
import ctypes, os, time, random, sys
import gmpy2
from gmpy2 import mpz, invert

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def ec_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = 3 * x1 * x1 * int(invert(mpz(2 * y1), mpz(p))) % p
    else:
        lam = (y2 - y1) * int(invert(mpz(x2 - x1), mpz(p))) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P):
    R = None; Q = P; k = int(k)
    while k > 0:
        if k & 1: R = ec_add(R, Q)
        Q = ec_add(Q, Q)
        k >>= 1
    return R

G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
Gx = b"79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
Gy = b"483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"
P_HEX = b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"
ORD_HEX = b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"

def load_gpu():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ec_kangaroo_gpu.so")
    if not os.path.exists(path):
        print(f"GPU .so not found: {path}")
        return None
    lib = ctypes.CDLL(path)
    lib.ec_kang_gpu_solve.restype = ctypes.c_int
    lib.ec_kang_gpu_solve.argtypes = [ctypes.c_char_p] * 5 + [ctypes.c_char_p, ctypes.c_size_t]
    return lib

def load_cpu():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ec_kangaroo_c.so")
    if not os.path.exists(path):
        print(f"CPU .so not found: {path}")
        return None
    lib = ctypes.CDLL(path)
    lib.ec_kang_init.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.ec_kang_init.restype = None
    lib.ec_kang_solve_ex.restype = ctypes.c_int
    lib.ec_kang_solve_ex.argtypes = [ctypes.c_char_p] * 6 + [ctypes.c_char_p, ctypes.c_size_t]
    lib.ec_kang_init(P_HEX, ORD_HEX)
    return lib

def solve_gpu(lib, k_true, bits):
    P = ec_mul(k_true, G)
    Px = format(P[0], '064x').encode()
    Py = format(P[1], '064x').encode()
    bound_hex = format(1 << bits, 'x').encode()
    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    found = lib.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
    elapsed = time.time() - t0
    if found:
        k_found = int(buf.value, 16)
        ok = (k_found == k_true)
    else:
        ok = False
        k_found = None
    return elapsed, ok, k_found

def solve_cpu(lib, k_true, bits):
    P = ec_mul(k_true, G)
    Px = format(P[0], '064x').encode()
    Py = format(P[1], '064x').encode()
    bound_hex = format(1 << bits, 'x').encode()
    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    found = lib.ec_kang_solve_ex(Gx, Gy, Px, Py, bound_hex, None, buf, 256)
    elapsed = time.time() - t0
    if found:
        k_found = int(buf.value, 16)
        ok = (k_found == k_true)
    else:
        ok = False
        k_found = None
    return elapsed, ok, k_found

def main():
    random.seed(42)

    gpu_lib = load_gpu()
    cpu_lib = load_cpu()

    if not gpu_lib and not cpu_lib:
        print("Neither GPU nor CPU library found!")
        return

    bit_sizes = [28, 32, 36, 40, 44]
    n_trials = 3
    max_time = 120  # skip larger if any trial exceeds this

    print("=" * 70)
    print("ECDLP Kangaroo Benchmark: GPU vs CPU (secp256k1)")
    print("=" * 70)
    print(f"Trials per size: {n_trials}")
    print()

    results = {}

    for bits in bit_sizes:
        print(f"--- {bits}-bit keys ---")
        # Pre-generate test cases
        cases = []
        for i in range(n_trials):
            k = random.randint(1, (1 << bits) - 1)
            cases.append(k)

        gpu_times = []
        cpu_times = []

        if gpu_lib:
            skip_gpu = False
            for i, k in enumerate(cases):
                if skip_gpu:
                    break
                t, ok, _ = solve_gpu(gpu_lib, k, bits)
                status = "OK" if ok else "FAIL"
                print(f"  GPU trial {i}: {t:.3f}s {status}")
                if ok:
                    gpu_times.append(t)
                if t > max_time:
                    print(f"  GPU too slow, skipping larger sizes")
                    skip_gpu = True

        if cpu_lib:
            skip_cpu = False
            for i, k in enumerate(cases):
                if skip_cpu:
                    break
                t, ok, _ = solve_cpu(cpu_lib, k, bits)
                status = "OK" if ok else "FAIL"
                print(f"  CPU trial {i}: {t:.3f}s {status}")
                if ok:
                    cpu_times.append(t)
                if t > max_time:
                    print(f"  CPU too slow, skipping larger sizes")
                    skip_cpu = True

        gpu_avg = sum(gpu_times) / len(gpu_times) if gpu_times else None
        cpu_avg = sum(cpu_times) / len(cpu_times) if cpu_times else None

        results[bits] = (gpu_avg, cpu_avg)

        if gpu_avg and cpu_avg:
            speedup = cpu_avg / gpu_avg
            print(f"  => GPU avg: {gpu_avg:.3f}s, CPU avg: {cpu_avg:.3f}s, GPU speedup: {speedup:.2f}x")
        elif gpu_avg:
            print(f"  => GPU avg: {gpu_avg:.3f}s")
        elif cpu_avg:
            print(f"  => CPU avg: {cpu_avg:.3f}s")
        print()

    # Summary table
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Bits':>6} {'GPU (s)':>10} {'CPU (s)':>10} {'Speedup':>10}")
    print("-" * 40)
    for bits in bit_sizes:
        gpu_avg, cpu_avg = results.get(bits, (None, None))
        gpu_str = f"{gpu_avg:.3f}" if gpu_avg else "N/A"
        cpu_str = f"{cpu_avg:.3f}" if cpu_avg else "N/A"
        if gpu_avg and cpu_avg:
            speedup = f"{cpu_avg/gpu_avg:.2f}x"
        else:
            speedup = "N/A"
        print(f"{bits:>6} {gpu_str:>10} {cpu_str:>10} {speedup:>10}")

if __name__ == "__main__":
    main()
