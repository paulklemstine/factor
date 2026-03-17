"""Average over many random trials to get statistically meaningful comparison."""
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

def load(path):
    lib=ctypes.CDLL(path)
    lib.ec_kang_gpu_solve.restype=ctypes.c_int
    lib.ec_kang_gpu_solve.argtypes=[ctypes.c_char_p]*5+[ctypes.c_char_p,ctypes.c_size_t]
    return lib

base = load("/tmp/baseline_orig.so")
z6 = load("./ec_kangaroo_gpu_z6.so")

random.seed(12345)

# Pre-generate all test points
bits = 36
n_trials = 10
print("Generating %d test cases at %d bits..." % (n_trials, bits), flush=True)
cases = []
for i in range(n_trials):
    k = random.randint(1, (1 << bits) - 1)
    P = ec_mul(k, G)
    cases.append((k, P))
    print("  case %d: k=%d" % (i, k), flush=True)

bound_hex = format(1 << bits, 'x').encode()

print("\nRunning baseline...", flush=True)
base_times = []
for i, (k_true, P_pt) in enumerate(cases):
    Px = format(P_pt[0], '064x').encode()
    Py = format(P_pt[1], '064x').encode()
    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    f = base.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
    t = time.time() - t0
    ok = f and int(buf.value,16) == k_true
    base_times.append(t)
    print("  #%d: %.3fs %s" % (i, t, "OK" if ok else "FAIL"), flush=True)

print("\nRunning Z6+fork...", flush=True)
z6_times = []
for i, (k_true, P_pt) in enumerate(cases):
    Px = format(P_pt[0], '064x').encode()
    Py = format(P_pt[1], '064x').encode()
    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    f = z6.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
    t = time.time() - t0
    ok = f and int(buf.value,16) == k_true
    z6_times.append(t)
    print("  #%d: %.3fs %s" % (i, t, "OK" if ok else "FAIL"), flush=True)

base_avg = sum(base_times) / len(base_times)
z6_avg = sum(z6_times) / len(z6_times)
# Also compute median
base_med = sorted(base_times)[len(base_times)//2]
z6_med = sorted(z6_times)[len(z6_times)//2]

print("\n=== RESULTS (%d-bit, %d trials) ===" % (bits, n_trials), flush=True)
print("Baseline: avg=%.3fs  median=%.3fs" % (base_avg, base_med), flush=True)
print("Z6+fork:  avg=%.3fs  median=%.3fs" % (z6_avg, z6_med), flush=True)
print("Speedup:  avg=%.2fx  median=%.2fx" % (base_avg/z6_avg, base_med/z6_med), flush=True)
