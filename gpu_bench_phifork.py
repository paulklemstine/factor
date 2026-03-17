"""Head-to-head: baseline vs Z/6+crossorbit+φ-fork on RTX 4050."""
import ctypes, os, time, sys
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

def load(path):
    lib=ctypes.CDLL(path)
    lib.ec_kang_gpu_solve.restype=ctypes.c_int
    lib.ec_kang_gpu_solve.argtypes=[ctypes.c_char_p]*5+[ctypes.c_char_p,ctypes.c_size_t]
    return lib

base = load("/tmp/baseline_orig.so")
z6 = load("./ec_kangaroo_gpu_z6.so")

vectors = [
    (32, 2718281828),
    (36, 51234567890),
    (36, 31415926535),
    (40, 712345678901),
    (40, 271828182845),
]

print("="*65, flush=True)
print("Baseline vs Z/6+crossorbit+phi-fork (RTX 4050)", flush=True)
print("="*65, flush=True)
print("%6s %15s %10s %10s %9s" % ("Bits", "k", "Baseline", "Z6+fork", "Speedup"), flush=True)
print("-"*55, flush=True)

for bits, k_true in vectors:
    P = ec_mul(k_true, G)
    Px = format(P[0], '064x').encode()
    Py = format(P[1], '064x').encode()
    bound = format(1 << bits, 'x').encode()

    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    f = base.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound, buf, 256)
    tb = time.time() - t0
    ok_b = "OK" if f and int(buf.value,16) == k_true else "FAIL"

    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    f = z6.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound, buf, 256)
    tz = time.time() - t0
    ok_z = "OK" if f and int(buf.value,16) == k_true else "FAIL"

    sp = tb/tz if tz > 0 else 0
    print("%6d %15d %9.3fs %9.3fs %8.2fx  %s/%s" % (bits, k_true, tb, tz, sp, ok_b, ok_z), flush=True)
