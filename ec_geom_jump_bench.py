#!/usr/bin/env python3
"""
Benchmark: Geometric jump spacing vs Pythagorean/Levy jump table for kangaroo ECDLP.

Compares:
  - BASELINE: ec_kangaroo_c.so  (original PYTH_HYPS table)
  - GEOM:     ec_kangaroo_geom.so (geometric spacing: jumps[i] = round(r^i))

Tests at 36b, 40b, 44b with 5 trials each, 30s timeout per trial.
Reports wall times, success rate, and speedup.
"""

import ctypes, os, sys, time, signal, random

# ---------- Setup secp256k1 from ecdlp_pythagorean.py ----------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ecdlp_pythagorean import secp256k1_curve, FastCurve

curve = secp256k1_curve()
G = curve.G
ORDER = curve.n
P_HEX = hex(int(curve.p))[2:]
N_HEX = hex(ORDER)[2:]
GX_HEX = hex(G.x)[2:]
GY_HEX = hex(G.y)[2:]


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("timeout")


def solve_with_lib(lib, init_fn, solve_fn, Px_hex, Py_hex, bound_hex):
    """Call C kangaroo solver, return (found, k_hex, elapsed)."""
    init_fn(P_HEX.encode(), N_HEX.encode())
    result_buf = ctypes.create_string_buffer(256)
    t0 = time.time()
    ret = solve_fn(
        GX_HEX.encode(), GY_HEX.encode(),
        Px_hex.encode(), Py_hex.encode(),
        bound_hex.encode(),
        result_buf, ctypes.c_size_t(256)
    )
    elapsed = time.time() - t0
    if ret == 1:
        k = int(result_buf.value.decode(), 16)
        return True, k, elapsed
    return False, None, elapsed


def load_lib(so_name, init_name, solve_name):
    """Load a .so and return (lib, init_fn, solve_fn)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), so_name)
    lib = ctypes.CDLL(path)
    init_fn = getattr(lib, init_name)
    solve_fn = getattr(lib, solve_name)
    return lib, init_fn, solve_fn


def generate_test_case(bits):
    """Generate a random ECDLP instance with secret k in [1, 2^bits)."""
    bound = 1 << bits
    k = random.randint(1, bound - 1)
    P = curve.scalar_mult(k, G)
    return k, P, bound


def run_benchmark():
    # Load both libraries
    lib_base, init_base, solve_base = load_lib(
        "ec_kangaroo_c.so", "ec_kang_init", "ec_kang_solve")
    lib_geom, init_geom, solve_geom = load_lib(
        "ec_kangaroo_geom.so", "ec_kang_geom_init", "ec_kang_geom_solve")

    bit_sizes = [36, 40, 44]
    n_trials = 5
    timeout_sec = 30

    print("=" * 78)
    print("Kangaroo ECDLP Benchmark: Pythagorean (baseline) vs Geometric jump table")
    print("=" * 78)
    print(f"Trials per config: {n_trials}, timeout: {timeout_sec}s")
    print()

    # Compute jump table means for reference
    pyth_hyps = [
        5, 109, 233, 373, 509, 685, 853, 1025, 1189, 1429,
        1649, 1825, 2045, 2273, 2533, 2749, 2953, 3233, 3485, 3697,
        4013, 4285, 4625, 4889, 5197, 5545, 5857, 6121, 6485, 6865,
        7309, 7625, 8005, 8465, 8845, 9529, 10069, 10537, 11065, 11597,
        12193, 12721, 13325, 13997, 14813, 15481, 16237, 16865, 17833, 18797,
        19501, 20813, 22229, 24217, 25805, 27449, 30005, 32657, 34285, 37013,
        42025, 47413, 53057, 67901
    ]
    geom_hyps = [
        1, 1, 2, 2, 3, 4, 5, 6, 8, 10,
        13, 17, 22, 28, 36, 47, 60, 78, 101, 130,
        169, 218, 282, 365, 472, 611, 790, 1022, 1322, 1710,
        2212, 2861, 3701, 4787, 6192, 8009, 10358, 13398, 17331, 22419,
        29000, 37515, 48531, 62779, 81200, 105031, 135849, 175714, 227259, 293915,
        380114, 491607, 635775, 822244, 1063487, 1375524, 1779111, 2300830, 2976153, 3849413,
        4978450, 6438281, 8325782, 10765769
    ]
    print(f"Pythagorean table: mean={sum(pyth_hyps)/len(pyth_hyps):.0f}, "
          f"min={min(pyth_hyps)}, max={max(pyth_hyps)}, ratio={max(pyth_hyps)/max(min(pyth_hyps),1):.0f}")
    print(f"Geometric table:   mean={sum(geom_hyps)/len(geom_hyps):.0f}, "
          f"min={min(geom_hyps)}, max={max(geom_hyps)}, ratio={max(geom_hyps)/max(min(geom_hyps),1):.0f}")
    print()

    # Pre-generate all test cases so both methods solve the same instances
    random.seed(42)
    test_cases = {}
    for bits in bit_sizes:
        test_cases[bits] = []
        for _ in range(n_trials):
            test_cases[bits].append(generate_test_case(bits))

    signal.signal(signal.SIGALRM, timeout_handler)

    results = {}  # {bits: {"base": [(time, ok)], "geom": [(time, ok)]}}

    for bits in bit_sizes:
        results[bits] = {"base": [], "geom": []}
        print(f"--- {bits}-bit search space ---")

        for trial in range(n_trials):
            k_true, P, bound = test_cases[bits][trial]
            Px_hex = hex(P.x)[2:]
            Py_hex = hex(P.y)[2:]
            bound_hex = hex(bound)[2:]

            # --- Baseline ---
            signal.alarm(timeout_sec)
            try:
                ok, k_found, elapsed = solve_with_lib(
                    lib_base, init_base, solve_base, Px_hex, Py_hex, bound_hex)
                if ok and k_found != k_true:
                    # Check negation
                    if k_found != (ORDER - k_true) % ORDER:
                        print(f"  WARNING: baseline trial {trial+1} found wrong k!")
                        ok = False
                results[bits]["base"].append((elapsed, ok))
                status = f"{elapsed:.3f}s" if ok else f"FAIL ({elapsed:.3f}s)"
            except TimeoutError:
                results[bits]["base"].append((timeout_sec, False))
                status = "TIMEOUT"
            finally:
                signal.alarm(0)

            # --- Geometric ---
            signal.alarm(timeout_sec)
            try:
                ok, k_found, elapsed = solve_with_lib(
                    lib_geom, init_geom, solve_geom, Px_hex, Py_hex, bound_hex)
                if ok and k_found != k_true:
                    if k_found != (ORDER - k_true) % ORDER:
                        print(f"  WARNING: geom trial {trial+1} found wrong k!")
                        ok = False
                results[bits]["geom"].append((elapsed, ok))
                status_g = f"{elapsed:.3f}s" if ok else f"FAIL ({elapsed:.3f}s)"
            except TimeoutError:
                results[bits]["geom"].append((timeout_sec, False))
                status_g = "TIMEOUT"
            finally:
                signal.alarm(0)

            print(f"  Trial {trial+1}: base={status:>10s}  geom={status_g:>10s}  (k={k_true})")

        print()

    # --- Summary ---
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"{'Bits':>6s} | {'Base avg':>10s} {'ok':>4s} | {'Geom avg':>10s} {'ok':>4s} | {'Speedup':>8s} | Winner")
    print("-" * 78)

    for bits in bit_sizes:
        base_times = [t for t, ok in results[bits]["base"] if ok]
        geom_times = [t for t, ok in results[bits]["geom"] if ok]
        base_ok = sum(1 for _, ok in results[bits]["base"] if ok)
        geom_ok = sum(1 for _, ok in results[bits]["geom"] if ok)

        base_avg = sum(base_times) / len(base_times) if base_times else float('inf')
        geom_avg = sum(geom_times) / len(geom_times) if geom_times else float('inf')

        if base_avg > 0 and geom_avg > 0:
            speedup = base_avg / geom_avg
            winner = "GEOM" if speedup > 1.05 else ("BASE" if speedup < 0.95 else "TIE")
            speedup_s = f"{speedup:.2f}x"
        else:
            speedup_s = "N/A"
            winner = "N/A"

        base_avg_s = f"{base_avg:.3f}s" if base_avg < float('inf') else "N/A"
        geom_avg_s = f"{geom_avg:.3f}s" if geom_avg < float('inf') else "N/A"

        print(f"{bits:>6d} | {base_avg_s:>10s} {base_ok:>2d}/{n_trials} | "
              f"{geom_avg_s:>10s} {geom_ok:>2d}/{n_trials} | {speedup_s:>8s} | {winner}")

    print()
    print("Speedup > 1.0 means geometric is faster.")


if __name__ == "__main__":
    run_benchmark()
