#!/usr/bin/env python3 -u
"""
Benchmark different Levy spread configurations for ECDLP kangaroo.
Tests spread ratios, exponential bases, and distribution shapes.
Recompiles ec_kangaroo_c.c with different PYTH_HYPS tables.
"""
import ctypes, os, time, random, math, sys, subprocess
import gmpy2
from gmpy2 import mpz, invert

sys.stdout.reconfigure(line_buffering=True)

p_curve = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = b"79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
Gy = b"483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"
P_HEX = b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"
ORD_HEX = b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def ec_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p_curve==0: return None
        lam=3*x1*x1*int(invert(mpz(2*y1),mpz(p_curve)))%p_curve
    else:
        lam=(y2-y1)*int(invert(mpz(x2-x1),mpz(p_curve)))%p_curve
    x3=(lam*lam-x1-x2)%p_curve; y3=(lam*(x1-x3)-y1)%p_curve
    return(x3,y3)

def ec_mul(k, P):
    R=None; Q=P; k=int(k)
    while k>0:
        if k&1: R=ec_add(R,Q)
        Q=ec_add(Q,Q); k>>=1
    return R

NUM_JUMPS = 64
BASE_SRC = '/home/raver1975/factor/ec_kangaroo_c.c'
WORK_DIR = '/home/raver1975/factor'

def gen_exp_table(spread, n=NUM_JUMPS):
    base = spread ** (1.0/(n-1))
    return [max(1, int(round(base**i))) for i in range(n)]

def gen_custom_base(base, n=NUM_JUMPS):
    return [max(1, int(round(base**i))) for i in range(n)]

def gen_sqrt_table(spread, n=NUM_JUMPS):
    return [max(1, int(round(spread**((i/(n-1))**2)))) for i in range(n)]

def gen_heavy_small(spread, n=NUM_JUMPS):
    half = n//2; mid = int(math.sqrt(spread))
    t = [max(1, int(round(1+(mid-1)*i/(half-1)))) for i in range(half)]
    base = (spread/mid)**(1.0/(n-half-1))
    t += [max(1, int(round(mid*base**i))) for i in range(n-half)]
    return t

def format_c(table):
    lines = []
    for i in range(0, len(table), 10):
        lines.append("    " + ", ".join(str(v) for v in table[i:i+10]))
    return ",\n".join(lines)

def build(table, name):
    with open(BASE_SRC) as f:
        src = f.read()
    marker = "static const unsigned long PYTH_HYPS[] = {\n"
    end = "};\n"
    i1 = src.index(marker)
    i2 = src.index(end, i1 + len(marker)) + len(end)
    new = marker + format_c(table) + "\n" + end
    src = src[:i1] + new + src[i2:]
    tmp_c = os.path.join(WORK_DIR, f'_tmp_{name}.c')
    so_path = os.path.join(WORK_DIR, f'_tmp_{name}.so')
    with open(tmp_c, 'w') as f:
        f.write(src)
    r = subprocess.run(['gcc','-O3','-shared','-fPIC','-o',so_path,tmp_c,'-lgmp'],
                       capture_output=True, text=True)
    os.remove(tmp_c)
    if r.returncode != 0:
        print(f"  COMPILE FAIL: {r.stderr[:200]}")
        return None
    return so_path

def bench(so_path, bits, cases):
    lib = ctypes.CDLL(so_path)
    lib.ec_kang_init.argtypes = [ctypes.c_char_p]*2
    lib.ec_kang_init.restype = None
    lib.ec_kang_solve_ex.restype = ctypes.c_int
    lib.ec_kang_solve_ex.argtypes = [ctypes.c_char_p]*6+[ctypes.c_char_p, ctypes.c_size_t]
    lib.ec_kang_init(P_HEX, ORD_HEX)

    bound_hex = format(1<<bits, 'x').encode()
    times = []
    ok = 0
    for k_true, Ppt in cases:
        Px = format(Ppt[0], '064x').encode()
        Py = format(Ppt[1], '064x').encode()
        buf = ctypes.create_string_buffer(256)
        t0 = time.time()
        found = lib.ec_kang_solve_ex(Gx, Gy, Px, Py, bound_hex, None, buf, 256)
        t = time.time() - t0
        if found:
            ok += 1
            times.append(t)
        else:
            times.append(t * 2)  # penalty
    del lib
    return sum(times)/len(times), ok, len(cases), times

def main():
    random.seed(42)

    # Precompute test cases
    print("Precomputing test points...")
    cases = {}
    for bits in [36, 40]:
        cc = []
        for _ in range(3):
            k = random.randint(1, (1<<bits)-1)
            P = ec_mul(k, G)
            cc.append((k, P))
            print(f"  {bits}b case: k={k}")
        cases[bits] = cc
    print("Done.\n")

    all_results = {}

    # ============================================================
    # Exp 1: Spread ratio
    # ============================================================
    print("=" * 70)
    print("EXP 1: SPREAD RATIO")
    print("=" * 70)
    for spread_exp in [5, 6, 7, 8]:
        spread = 10**spread_exp
        table = gen_exp_table(spread)
        base = spread**(1.0/63)
        name = f"spread{spread_exp}"
        print(f"\n  10^{spread_exp} (base={base:.4f}): [{table[0]}..{table[-1]}], mean={sum(table)//len(table)}")
        so = build(table, name)
        if not so: continue
        for bits in [36, 40]:
            mean, ok, tot, _ = bench(so, bits, cases[bits])
            print(f"    {bits}b: mean={mean:.3f}s, ok={ok}/{tot}")
            all_results[(f"spread_1e{spread_exp}", bits)] = mean
        os.remove(so)

    # ============================================================
    # Exp 2: Exponential base
    # ============================================================
    print("\n" + "=" * 70)
    print("EXP 2: EXPONENTIAL BASE")
    print("=" * 70)
    for base_val in [1.10, 1.15, 1.20, 1.28, 1.35, 1.45]:
        table = gen_custom_base(base_val)
        name = f"base{int(base_val*100)}"
        print(f"\n  base={base_val:.2f}: [{table[0]}..{table[-1]}], spread={table[-1]}, mean={sum(table)//len(table)}")
        so = build(table, name)
        if not so: continue
        for bits in [36, 40]:
            mean, ok, tot, _ = bench(so, bits, cases[bits])
            print(f"    {bits}b: mean={mean:.3f}s, ok={ok}/{tot}")
            all_results[(f"base_{base_val:.2f}", bits)] = mean
        os.remove(so)

    # ============================================================
    # Exp 3: Distribution shape
    # ============================================================
    print("\n" + "=" * 70)
    print("EXP 3: DISTRIBUTION SHAPE (spread=10^7)")
    print("=" * 70)
    spread = 1e7
    shapes = [
        ("exponential", gen_exp_table(spread)),
        ("sqrt_heavy", gen_sqrt_table(spread)),
        ("heavy_small", gen_heavy_small(spread)),
    ]
    for shape_name, table in shapes:
        name = f"shape_{shape_name}"
        print(f"\n  {shape_name}: [{table[0]}..{table[-1]}], mean={sum(table)//len(table)}")
        print(f"    first10: {table[:10]}")
        print(f"    last10:  {table[-10:]}")
        so = build(table, name)
        if not so: continue
        for bits in [36, 40]:
            mean, ok, tot, _ = bench(so, bits, cases[bits])
            print(f"    {bits}b: mean={mean:.3f}s, ok={ok}/{tot}")
            all_results[(f"shape_{shape_name}", bits)] = mean
        os.remove(so)

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 70)
    print("FULL RESULTS TABLE")
    print("=" * 70)
    print(f"  {'Config':25s} | {'36b mean':>10s} | {'40b mean':>10s}")
    print("  " + "-"*55)

    configs_seen = set()
    for (cfg, bits), mean in sorted(all_results.items()):
        if cfg not in configs_seen:
            configs_seen.add(cfg)
            m36 = all_results.get((cfg, 36), None)
            m40 = all_results.get((cfg, 40), None)
            s36 = f"{m36:.3f}s" if m36 else "N/A"
            s40 = f"{m40:.3f}s" if m40 else "N/A"
            print(f"  {cfg:25s} | {s36:>10s} | {s40:>10s}")

    # Best config
    best_40 = min(((k, v) for k, v in all_results.items() if k[1] == 40), key=lambda x: x[1], default=None)
    if best_40:
        print(f"\n  BEST at 40b: {best_40[0][0]} = {best_40[1]:.3f}s")

if __name__ == "__main__":
    main()
