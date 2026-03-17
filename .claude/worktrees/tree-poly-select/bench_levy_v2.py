#!/usr/bin/env python3
"""
Lévy spread benchmark v2: Test the SHAPE of the distribution.

The C code scales jumps so mean ≈ sqrt(bound/2)/4.
What matters is the RATIO between max and min jump (the spread shape).
We test different shapes while keeping NUM_JUMPS=64.

Key insight: for 44b, mean_target ≈ 523K. For 48b, ≈ 8.4M.
The C code computes: scale = mean_target / raw_mean.
So we should make raw_mean small enough that scale >= 1.
After scaling, the spread ratio is preserved.
"""

import sys, os, time, random, re, subprocess, math, json

MAIN_DIR = "/home/raver1975/factor"
C_FILE = os.path.join(MAIN_DIR, "ec_kangaroo_shared.c")
SO_FILE = os.path.join(MAIN_DIR, "ec_kangaroo_shared.so")
NUM_JUMPS = 64

# Keep raw_mean around 100 so scale factor is always large
# This means the shape is preserved after scaling
BASE_MEAN = 100


def generate_table(spread_ratio, shape='exponential'):
    """Generate jump table with given spread ratio and shape.
    Raw mean is kept near BASE_MEAN so C scaling works correctly.
    """
    if shape == 'exponential':
        # Exponential: table[i] = a * r^i where r = spread^(1/63)
        # Mean of geometric series: a * (r^64 - 1) / (64 * (r - 1))
        r = spread_ratio ** (1.0 / 63)
        raw = [r ** i for i in range(NUM_JUMPS)]
    elif shape == 'quadratic':
        # More weight on small jumps
        raw = [1 + (spread_ratio - 1) * (i / 63) ** 2 for i in range(NUM_JUMPS)]
    elif shape == 'sqrt':
        # More weight on large jumps
        raw = [1 + (spread_ratio - 1) * (i / 63) ** 0.5 for i in range(NUM_JUMPS)]
    elif shape == 'linear':
        # Uniform spacing
        raw = [1 + (spread_ratio - 1) * i / 63 for i in range(NUM_JUMPS)]
    elif shape == 'bimodal':
        # Half small, half large
        raw = []
        for i in range(NUM_JUMPS):
            if i < 32:
                raw.append(1 + i * 2)
            else:
                raw.append(spread_ratio / 2 + (i - 32) * spread_ratio / 64)
    else:
        raise ValueError(f"Unknown shape: {shape}")

    # Normalize so mean ≈ BASE_MEAN
    cur_mean = sum(raw) / len(raw)
    factor = BASE_MEAN / cur_mean
    table = [max(1, round(v * factor)) for v in raw]

    # Ensure strictly non-decreasing
    for i in range(1, NUM_JUMPS):
        if table[i] <= table[i-1]:
            table[i] = table[i-1] + 1

    return table


def format_c_table(table):
    lines = []
    for i in range(0, len(table), 10):
        chunk = table[i:i+10]
        line = "    " + ", ".join(str(v) for v in chunk)
        if i + 10 < len(table):
            line += ","
        lines.append(line)
    return "static const unsigned long PYTH_HYPS[] = {\n" + "\n".join(lines) + "\n};"


def patch_and_compile(table):
    with open(C_FILE, 'r') as f:
        content = f.read()
    pattern = r'static const unsigned long PYTH_HYPS\[\] = \{[^}]+\};'
    new_decl = format_c_table(table)
    new_content = re.sub(pattern, new_decl, content, count=1)
    if new_content == content:
        print("ERROR: Could not find PYTH_HYPS")
        return False
    with open(C_FILE, 'w') as f:
        f.write(new_content)
    r = subprocess.run(
        f"gcc -O3 -march=native -shared -fPIC -o {SO_FILE} {C_FILE} -lgmp",
        shell=True, capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"COMPILE ERROR: {r.stderr}")
        return False
    return True


TRIAL_SCRIPT = '''
import sys, time, random
sys.path.insert(0, "{main_dir}")
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
'''.strip()


def run_trial(bits, timeout=60):
    seed = random.randint(0, 2**32)
    script = TRIAL_SCRIPT.format(main_dir=MAIN_DIR, seed=seed, bits=bits)
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
        subprocess.run("pkill -f ec_kang_shared", shell=True, capture_output=True)
        time.sleep(0.5)
        return None
    except:
        return None


def bench(name, table, n_trials=3, test_bits=[44, 48]):
    actual_spread = table[-1] / max(table[0], 1)
    actual_mean = sum(table) / len(table)
    print(f"\n--- {name} ---")
    print(f"  Range: [{table[0]}..{table[-1]}], spread={actual_spread:.0f}x, mean={actual_mean:.0f}")

    if not patch_and_compile(table):
        return None

    results = {}
    for bits in test_bits:
        times = []
        for trial in range(n_trials):
            t = run_trial(bits, timeout=60)
            if t is not None:
                times.append(t)
                print(f"  {bits}b #{trial+1}: {t:.3f}s")
            else:
                print(f"  {bits}b #{trial+1}: TIMEOUT")
            sys.stdout.flush()
        avg = sum(times) / len(times) if times else None
        results[bits] = {'avg': avg, 'times': times, 'ok': len(times)}
        if avg:
            print(f"  {bits}b avg: {avg:.3f}s ({len(times)}/{n_trials})")
    return results


def main():
    with open(C_FILE, 'r') as f:
        original = f.read()

    all_results = {}

    try:
        # ============================================
        # Part 1: Spread ratio sweep (exponential shape)
        # ============================================
        print("=" * 60)
        print("PART 1: Spread ratio (exponential shape, mean~100)")
        print("=" * 60)

        for label, spread in [
            ("10x", 10),
            ("50x", 50),
            ("100x", 100),
            ("500x", 500),
            ("1000x", 1000),
            ("5000x", 5000),
            ("10000x", 10000),
            ("50000x", 50000),
        ]:
            table = generate_table(spread, 'exponential')
            r = bench(f"Exp spread={label}", table)
            all_results[f"exp_{label}"] = r

        # ============================================
        # Part 2: Shape comparison (fixed spread=1000x)
        # ============================================
        print("\n" + "=" * 60)
        print("PART 2: Shape comparison (spread=1000x)")
        print("=" * 60)

        for shape in ['exponential', 'quadratic', 'sqrt', 'linear', 'bimodal']:
            table = generate_table(1000, shape)
            r = bench(f"Shape={shape} 1000x", table)
            all_results[f"shape_{shape}"] = r

        # ============================================
        # Summary
        # ============================================
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"  {'Config':<35} {'44b avg':>10} {'48b avg':>10}")
        print("  " + "-" * 57)

        best_44 = (None, float('inf'))
        best_48 = (None, float('inf'))

        for name, r in all_results.items():
            if r is None:
                continue
            a44 = r.get(44, {}).get('avg')
            a48 = r.get(48, {}).get('avg')
            s44 = f"{a44:.3f}s" if a44 else "N/A"
            s48 = f"{a48:.3f}s" if a48 else "N/A"
            print(f"  {name:<35} {s44:>10} {s48:>10}")
            if a44 and a44 < best_44[1]:
                best_44 = (name, a44)
            if a48 and a48 < best_48[1]:
                best_48 = (name, a48)

        print()
        if best_44[0]:
            print(f"  BEST 44b: {best_44[0]} = {best_44[1]:.3f}s")
        if best_48[0]:
            print(f"  BEST 48b: {best_48[0]} = {best_48[1]:.3f}s")

        # Save JSON
        out = os.path.join(MAIN_DIR, "levy_spread_results.json")
        jr = {}
        for k, v in all_results.items():
            if v:
                jr[k] = {str(b): d for b, d in v.items()}
            else:
                jr[k] = None
        with open(out, 'w') as f:
            json.dump(jr, f, indent=2)
        print(f"\n  Saved to {out}")

    finally:
        with open(C_FILE, 'w') as f:
            f.write(original)
        subprocess.run(
            f"gcc -O3 -march=native -shared -fPIC -o {SO_FILE} {C_FILE} -lgmp",
            shell=True, capture_output=True
        )
        print("\n(Original restored)")


if __name__ == '__main__':
    main()
