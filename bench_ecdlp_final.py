#!/usr/bin/env python3
"""Final ECDLP benchmark: GPU vs CPU at 28-48 bits."""
import ctypes, os, time, random, sys
import gmpy2
from gmpy2 import mpz, invert

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
def ec_add(P,Q):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        lam=3*x1*x1*int(invert(mpz(2*y1),mpz(p)))%p
    else:
        lam=(y2-y1)*int(invert(mpz(x2-x1),mpz(p)))%p
    x3=(lam*lam-x1-x2)%p;y3=(lam*(x1-x3)-y1)%p
    return(x3,y3)
def ec_mul(k,P):
    R=None;Q=P;k=int(k)
    while k>0:
        if k&1:R=ec_add(R,Q)
        Q=ec_add(Q,Q)
        k>>=1
    return R

G=(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
   0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
Gx=b"79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
Gy=b"483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"
P_HEX=b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"
ORD_HEX=b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"

def load_gpu(path):
    lib=ctypes.CDLL(path)
    lib.ec_kang_gpu_solve.restype=ctypes.c_int
    lib.ec_kang_gpu_solve.argtypes=[ctypes.c_char_p]*5+[ctypes.c_char_p,ctypes.c_size_t]
    return lib

def load_cpu(path):
    lib=ctypes.CDLL(path)
    lib.ec_kang_init.argtypes=[ctypes.c_char_p,ctypes.c_char_p]
    lib.ec_kang_init.restype=None
    lib.ec_kang_solve_ex.restype=ctypes.c_int
    lib.ec_kang_solve_ex.argtypes=[ctypes.c_char_p]*6+[ctypes.c_char_p,ctypes.c_size_t]
    lib.ec_kang_init(P_HEX, ORD_HEX)
    return lib

random.seed(42)

gpu = load_gpu("./ec_kangaroo_gpu.so")
cpu = load_cpu("./ec_kangaroo_c.so")

n_trials = 3

print("=" * 60)
print("ECDLP Kangaroo Benchmark: GPU vs CPU (secp256k1)")
print("=" * 60)

results = {}

for bits in [28, 32, 36, 40, 44, 48]:
    print(f"\n--- {bits}-bit ---")
    cases = [(random.randint(1, (1<<bits)-1), None) for _ in range(n_trials)]
    # precompute points
    cases = [(k, ec_mul(k, G)) for k, _ in cases]
    bound_hex = format(1 << bits, 'x').encode()

    gpu_times = []
    cpu_times = []

    for i, (k_true, Ppt) in enumerate(cases):
        Px = format(Ppt[0], '064x').encode()
        Py = format(Ppt[1], '064x').encode()
        buf = ctypes.create_string_buffer(256)

        # GPU
        t0 = time.time()
        f = gpu.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
        tg = time.time() - t0
        ok_g = f and int(buf.value, 16) == k_true
        gpu_times.append(tg if ok_g else None)

        # CPU
        buf2 = ctypes.create_string_buffer(256)
        t0 = time.time()
        f2 = cpu.ec_kang_solve_ex(Gx, Gy, Px, Py, bound_hex, None, buf2, 256)
        tc = time.time() - t0
        ok_c = f2 and int(buf2.value, 16) == k_true
        cpu_times.append(tc if ok_c else None)

        print(f"  #{i}: GPU={tg:.3f}s({'OK' if ok_g else 'FAIL'}) CPU={tc:.3f}s({'OK' if ok_c else 'FAIL'})")

    # Compute averages (skip failures)
    gpu_ok = [t for t in gpu_times if t is not None]
    cpu_ok = [t for t in cpu_times if t is not None]
    gpu_avg = sum(gpu_ok)/len(gpu_ok) if gpu_ok else None
    cpu_avg = sum(cpu_ok)/len(cpu_ok) if cpu_ok else None
    results[bits] = (gpu_avg, cpu_avg)

    if gpu_avg and cpu_avg:
        print(f"  GPU avg: {gpu_avg:.3f}s, CPU avg: {cpu_avg:.3f}s, speedup: {cpu_avg/gpu_avg:.2f}x")

    # Skip larger sizes if too slow
    if (gpu_avg and gpu_avg > 60) or (cpu_avg and cpu_avg > 60):
        print("  Too slow, stopping")
        break

print("\n" + "=" * 60)
print(f"{'Bits':>6} {'GPU (s)':>10} {'CPU (s)':>10} {'GPU speedup':>12}")
print("-" * 42)
for bits, (ga, ca) in sorted(results.items()):
    gs = f"{ga:.3f}" if ga else "N/A"
    cs = f"{ca:.3f}" if ca else "N/A"
    sp = f"{ca/ga:.2f}x" if ga and ca else "N/A"
    print(f"{bits:>6} {gs:>10} {cs:>10} {sp:>12}")
