#!/usr/bin/env python3
"""Quick test: compare old GPU (NORM_INTERVAL=8) vs new (NORM_INTERVAL=2)."""
import ctypes, os, time, random
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

# Test at 36 bits with 5 trials
bits = 36
n = 5
cases = []
for i in range(n):
    k = random.randint(1, (1 << bits) - 1)
    P = ec_mul(k, G)
    cases.append((k, P))

bound_hex = format(1 << bits, 'x').encode()

def run_trials(lib, name, use_gpu=True):
    times = []
    for i, (k_true, P_pt) in enumerate(cases):
        Px = format(P_pt[0], '064x').encode()
        Py = format(P_pt[1], '064x').encode()
        buf = ctypes.create_string_buffer(256)
        t0 = time.time()
        if use_gpu:
            f = lib.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
        else:
            f = lib.ec_kang_solve_ex(Gx, Gy, Px, Py, bound_hex, None, buf, 256)
        t = time.time() - t0
        ok = f and int(buf.value, 16) == k_true
        times.append(t)
        print(f"  {name} #{i}: {t:.3f}s {'OK' if ok else 'FAIL'}")
    avg = sum(times) / len(times)
    print(f"  {name} avg: {avg:.3f}s\n")
    return avg

print(f"=== {bits}-bit ECDLP, {n} trials ===\n")

# GPU v2 (NORM_INTERVAL=2)
gpu_v2 = load_gpu("./ec_kangaroo_gpu_v2.so")
avg_v2 = run_trials(gpu_v2, "GPU-v2(NI=2)")

# GPU original (NORM_INTERVAL=8) - use baseline .so if available
if os.path.exists("./ec_kangaroo_gpu_baseline.so"):
    gpu_old = load_gpu("./ec_kangaroo_gpu_baseline.so")
    avg_old = run_trials(gpu_old, "GPU-old(NI=8)")
    print(f"Speedup v2 vs old: {avg_old/avg_v2:.2f}x")
elif os.path.exists("./ec_kangaroo_gpu.so"):
    # Current .so was built with NI=8 originally? Check by using the original
    # Actually the .so was just recompiled. Let's test CPU instead.
    pass

# CPU
cpu = load_cpu("./ec_kangaroo_c.so")
avg_cpu = run_trials(cpu, "CPU", use_gpu=False)
print(f"GPU-v2 vs CPU speedup: {avg_cpu/avg_v2:.2f}x")
