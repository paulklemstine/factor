"""Head-to-head: baseline vs Z/6+crossorbit on local RTX 4050."""
import ctypes, os, time, random, sys
import gmpy2
from gmpy2 import mpz, invert

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def ec_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        lam=3*x1*x1*int(invert(mpz(2*y1),mpz(p)))%p
    else:
        lam=(y2-y1)*int(invert(mpz(x2-x1),mpz(p)))%p
    x3=(lam*lam-x1-x2)%p; y3=(lam*(x1-x3)-y1)%p
    return (x3,y3)

def ec_mul(k,P):
    R=None;Q=P;k=int(k)
    while k>0:
        if k&1: R=ec_add(R,Q)
        Q=ec_add(Q,Q)
        k>>=1
    return R

G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
Gx = b"79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
Gy = b"483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"

def load_lib(path):
    lib = ctypes.CDLL(path)
    lib.ec_kang_gpu_solve.restype = ctypes.c_int
    lib.ec_kang_gpu_solve.argtypes = [ctypes.c_char_p]*5 + [ctypes.c_char_p, ctypes.c_size_t]
    return lib

def solve(lib, k_true, bits):
    P_pt = ec_mul(k_true, G)
    Px = format(P_pt[0], '064x').encode()
    Py = format(P_pt[1], '064x').encode()
    bound_hex = format(1 << bits, 'x').encode()
    buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    found = lib.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
    t = time.time() - t0
    if found:
        k_found = int(buf.value, 16)
        return t, k_found == k_true
    return t, False

random.seed(2026)

# Pre-generate test cases
print("Generating test points...", flush=True)
test_cases = {}
for bits in [32, 36, 40, 44, 48]:
    cases = []
    n_trials = 5 if bits <= 40 else 3
    for _ in range(n_trials):
        k = random.randint(1, (1 << bits) - 1)
        P_pt = ec_mul(k, G)
        cases.append((k, P_pt))
    test_cases[bits] = cases
    print("  %d-bit: %d cases ready" % (bits, len(cases)), flush=True)

print("\n" + "="*70, flush=True)
print("GPU Kangaroo: Baseline vs Z/6+crossorbit (RTX 4050 Laptop)", flush=True)
print("="*70, flush=True)

libs = [
    ("baseline", load_lib("./ec_kangaroo_gpu_baseline.so")),
    ("Z/6+cross", load_lib("./ec_kangaroo_gpu_z6.so")),
]

# Run each version on same test cases
all_results = {}
for label, lib in libs:
    print("\n--- %s ---" % label, flush=True)
    all_results[label] = {}
    for bits in [32, 36, 40, 44, 48]:
        times = []
        for trial, (k_true, P_pt) in enumerate(test_cases[bits]):
            Px = format(P_pt[0], '064x').encode()
            Py = format(P_pt[1], '064x').encode()
            bound_hex = format(1 << bits, 'x').encode()
            buf = ctypes.create_string_buffer(256)
            t0 = time.time()
            found = lib.ec_kang_gpu_solve(Gx, Gy, Px, Py, bound_hex, buf, 256)
            t = time.time() - t0
            if found:
                k_found = int(buf.value, 16)
                ok = "OK" if k_found == k_true else "WRONG"
            else:
                ok = "FAIL"
            times.append(t if ok == "OK" else None)
            print("  %s %db #%d: %.3fs %s" % (label, bits, trial, t, ok), flush=True)
        valid = [t for t in times if t is not None]
        avg = sum(valid) / len(valid) if valid else float('inf')
        all_results[label][bits] = avg
        print("  %s %db avg: %.3fs (%d/%d solved)" % (label, bits, avg, len(valid), len(times)), flush=True)

# Summary
print("\n" + "="*70, flush=True)
print("SUMMARY", flush=True)
print("="*70, flush=True)
print("%6s %12s %12s %10s" % ("Bits", "Baseline", "Z/6+cross", "Speedup"), flush=True)
print("-" * 45, flush=True)
for bits in [32, 36, 40, 44, 48]:
    ba = all_results["baseline"].get(bits, float('inf'))
    z6 = all_results["Z/6+cross"].get(bits, float('inf'))
    sp = ba / z6 if z6 > 0 and z6 != float('inf') else 0
    print("%6d %12.3fs %12.3fs %9.2fx" % (bits, ba, z6, sp), flush=True)
