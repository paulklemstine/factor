#!/usr/bin/env python3
"""
Lévy spread benchmark v3: Standalone test using subprocess.
Each config patches, compiles, tests in subprocess, restores.
Focus: fewer configs, more trials, proper analysis.
"""

import sys, os, time, random, re, subprocess, math, json

MAIN_DIR = "/home/raver1975/factor"
C_FILE = os.path.join(MAIN_DIR, "ec_kangaroo_shared.c")
SO_FILE = os.path.join(MAIN_DIR, "ec_kangaroo_shared.so")
NUM_JUMPS = 64


def make_exp_table(max_val, min_val=1):
    """Exponential table from min_val to max_val, 64 entries."""
    ratio = max_val / max(min_val, 1)
    base = ratio ** (1.0 / 63)
    table = [max(1, round(min_val * base ** i)) for i in range(NUM_JUMPS)]
    for i in range(1, NUM_JUMPS):
        if table[i] <= table[i-1]:
            table[i] = table[i-1] + 1
    return table


def make_table_for_bits(bits, spread_ratio, shape='exp'):
    """Make table whose effective mean matches sqrt(bound/2)/4 for given bits.

    The C code does: scale = mean_target / raw_mean, then jumps[i] = PYTH_HYPS[i] * scale
    To avoid distortion from integer truncation, we want scale ≈ 1.
    So raw_mean ≈ mean_target = sqrt(2^(bits-1)) / 4.
    """
    mean_target = int(math.isqrt(1 << (bits - 1))) // 4

    if shape == 'exp':
        # Exponential: geometric from min_val to max_val
        # With spread_ratio R: max = R * min
        # Mean of geometric = min * (R^(1/63)^64 - 1) / (64 * (R^(1/63) - 1))
        # For large R, mean ≈ max / (64 * ln(R^(1/63))) = max / (ln(R))
        # So max ≈ mean * ln(R), min = max / R

        # More precise: geometric mean = sqrt(min * max), arithmetic mean ≈ geometric for moderate spread
        # For exponential table: E[jump] = (max - min) / ln(max/min) for continuous approximation
        # Solve: mean_target = (max - min) / ln(spread_ratio)
        # With max = min * spread_ratio:
        # mean_target = min * (spread_ratio - 1) / ln(spread_ratio)
        # min = mean_target * ln(spread_ratio) / (spread_ratio - 1)

        if spread_ratio <= 1:
            spread_ratio = 2
        ln_r = math.log(spread_ratio)
        min_val = max(1, int(mean_target * ln_r / (spread_ratio - 1)))
        max_val = min_val * spread_ratio
        table = make_exp_table(int(max_val), min_val)
    else:
        raise ValueError(shape)

    # Verify
    actual_mean = sum(table) / len(table)
    actual_spread = table[-1] / max(table[0], 1)

    return table, actual_mean, actual_spread


def format_c_table(table):
    lines = []
    for i in range(0, len(table), 10):
        chunk = table[i:i+10]
        line = "    " + ", ".join(str(v) for v in chunk)
        if i + 10 < len(table):
            line += ","
        lines.append(line)
    return "static const unsigned long PYTH_HYPS[] = {\n" + "\n".join(lines) + "\n};"


def patch_compile_test(table, bits, seed, timeout=60):
    """Patch C file, compile, run one trial in subprocess, return time or None."""
    # Read original
    with open(C_FILE, 'r') as f:
        original = f.read()

    try:
        # Patch
        pattern = r'static const unsigned long PYTH_HYPS\[\] = \{[^}]+\};'
        new_decl = format_c_table(table)
        patched = re.sub(pattern, new_decl, original, count=1)
        with open(C_FILE, 'w') as f:
            f.write(patched)

        # Compile
        r = subprocess.run(
            f"gcc -O3 -march=native -shared -fPIC -o {SO_FILE} {C_FILE} -lgmp",
            shell=True, capture_output=True, text=True
        )
        if r.returncode != 0:
            return None

        # Run trial
        script = f'''
import sys, time, random
sys.path.insert(0, "{MAIN_DIR}")
from ecdlp_pythagorean import secp256k1_curve, ecdlp_shared_kangaroo
random.seed({seed})
curve = secp256k1_curve()
G = curve.G
bound = 1 << {bits}
k = random.randint(1, bound - 1)
P = curve.scalar_mult(k, G)
t0 = time.time()
result = ecdlp_shared_kangaroo(curve, G, P, bound, num_workers=6, verbose=False)
elapsed = time.time() - t0
if result == k:
    print(f"OK {{elapsed:.4f}}")
else:
    print(f"FAIL {{elapsed:.4f}}")
'''
        try:
            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True, text=True, timeout=timeout, cwd=MAIN_DIR
            )
            output = result.stdout.strip()
            if output.startswith("OK "):
                return float(output.split()[1])
            return None
        except subprocess.TimeoutExpired:
            subprocess.run("pkill -9 -f ec_kang_shared", shell=True, capture_output=True)
            time.sleep(0.5)
            return None
    finally:
        # Always restore
        with open(C_FILE, 'w') as f:
            f.write(original)


def bench_config(name, table, n_trials=3, test_bits=[44, 48]):
    actual_mean = sum(table) / len(table)
    actual_spread = table[-1] / max(table[0], 1)
    print(f"\n--- {name} ---")
    print(f"  Range: [{table[0]}..{table[-1]}], spread={actual_spread:.0f}x, mean={actual_mean:.0f}")

    results = {}
    for bits in test_bits:
        times = []
        for trial in range(n_trials):
            seed = random.randint(0, 2**32)
            t = patch_compile_test(table, bits, seed, timeout=55)
            if t is not None:
                times.append(t)
                print(f"  {bits}b #{trial+1}: {t:.3f}s", flush=True)
            else:
                print(f"  {bits}b #{trial+1}: TIMEOUT", flush=True)
        avg = sum(times) / len(times) if times else None
        results[bits] = {'avg': avg, 'times': times, 'ok': len(times)}
        if avg:
            print(f"  {bits}b avg: {avg:.3f}s ({len(times)}/{n_trials})")
    return results


def main():
    # First restore and compile original
    subprocess.run(f"cd {MAIN_DIR} && git checkout ec_kangaroo_shared.c", shell=True, capture_output=True)
    subprocess.run(
        f"gcc -O3 -march=native -shared -fPIC -o {SO_FILE} {C_FILE} -lgmp",
        shell=True, capture_output=True
    )

    all_results = {}

    # ===========================================
    # Baseline: current table
    # ===========================================
    print("=" * 60)
    print("BASELINE: Current 1e7 table")
    print("=" * 60)

    current = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        12, 16, 21, 27, 35, 46, 59, 77, 99, 129,
        166, 215, 278, 359, 464, 599, 774, 1000, 1291, 1668,
        2154, 2782, 3593, 4641, 5994, 7742, 9999, 12915, 16681, 21544,
        27825, 35938, 46415, 59948, 77426, 100000, 129154, 166810, 215443, 278255,
        359381, 464158, 599484, 774263, 1000000, 1291549, 1668100, 2154434, 2782559, 3593813,
        4641588, 5994842, 7742636, 10000000]
    r = bench_config("Current 1e7", current)
    all_results["baseline"] = r

    # ===========================================
    # Spread ratio sweep at 44b and 48b
    # For each bit size, build table matched to that size's mean_target
    # ===========================================
    print("\n" + "=" * 60)
    print("SPREAD RATIO SWEEP")
    print("=" * 60)

    for spread in [10, 50, 100, 500, 1000, 5000, 10000, 100000]:
        # Build table for 44b mean_target
        table_44, mean_44, sp_44 = make_table_for_bits(44, spread)
        # Build table for 48b mean_target
        table_48, mean_48, sp_48 = make_table_for_bits(48, spread)

        label = f"spread_{spread}x"
        print(f"\n=== Spread {spread}x ===")

        # Test at 44b with 44b-matched table
        print(f"  44b-matched table: mean={mean_44:.0f}, range=[{table_44[0]}..{table_44[-1]}]")
        times_44 = []
        for trial in range(3):
            seed = random.randint(0, 2**32)
            t = patch_compile_test(table_44, 44, seed, timeout=55)
            if t is not None:
                times_44.append(t)
                print(f"  44b #{trial+1}: {t:.3f}s", flush=True)
            else:
                print(f"  44b #{trial+1}: TIMEOUT", flush=True)

        # Test at 48b with 48b-matched table
        print(f"  48b-matched table: mean={mean_48:.0f}, range=[{table_48[0]}..{table_48[-1]}]")
        times_48 = []
        for trial in range(3):
            seed = random.randint(0, 2**32)
            t = patch_compile_test(table_48, 48, seed, timeout=55)
            if t is not None:
                times_48.append(t)
                print(f"  48b #{trial+1}: {t:.3f}s", flush=True)
            else:
                print(f"  48b #{trial+1}: TIMEOUT", flush=True)

        all_results[label] = {
            44: {'avg': sum(times_44)/len(times_44) if times_44 else None,
                 'times': times_44, 'ok': len(times_44)},
            48: {'avg': sum(times_48)/len(times_48) if times_48 else None,
                 'times': times_48, 'ok': len(times_48)},
        }

        for bits, times in [(44, times_44), (48, times_48)]:
            if times:
                print(f"  {bits}b avg: {sum(times)/len(times):.3f}s ({len(times)}/3)")
            else:
                print(f"  {bits}b: ALL FAILED")

    # ===========================================
    # Summary
    # ===========================================
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  {'Config':<25} {'44b avg':>10} {'48b avg':>10}")
    print("  " + "-" * 47)

    best_44 = (None, float('inf'))
    best_48 = (None, float('inf'))

    for name, r in all_results.items():
        if r is None:
            continue
        a44 = r.get(44, {}).get('avg')
        a48 = r.get(48, {}).get('avg')
        s44 = f"{a44:.3f}s" if a44 else "N/A"
        s48 = f"{a48:.3f}s" if a48 else "N/A"
        print(f"  {name:<25} {s44:>10} {s48:>10}")
        if a44 and a44 < best_44[1]:
            best_44 = (name, a44)
        if a48 and a48 < best_48[1]:
            best_48 = (name, a48)

    print()
    if best_44[0]:
        print(f"  BEST 44b: {best_44[0]} = {best_44[1]:.3f}s")
    if best_48[0]:
        print(f"  BEST 48b: {best_48[0]} = {best_48[1]:.3f}s")

    # Restore and compile original
    subprocess.run(f"cd {MAIN_DIR} && git checkout ec_kangaroo_shared.c", shell=True, capture_output=True)
    subprocess.run(
        f"gcc -O3 -march=native -shared -fPIC -o {SO_FILE} {C_FILE} -lgmp",
        shell=True, capture_output=True
    )
    print("\n(Original restored)")


if __name__ == '__main__':
    main()
