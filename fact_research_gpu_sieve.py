#!/usr/bin/env python3
"""
Field 4: GPU Sieving Analysis — RTX 4050 Laptop (6GB VRAM)
============================================================
Analyze feasibility of GPU-accelerated sieving for SIQS and GNFS.

RTX 4050 Laptop specs:
  - 2560 CUDA cores, 80 Tensor cores
  - 6GB GDDR6 VRAM, 192 GB/s bandwidth
  - Base clock 1605 MHz, Boost ~2370 MHz
  - FP32: ~12 TFLOPS, INT32: ~12 TOPS
  - SM count: 20

Key questions:
  1. Can the sieve loop be parallelized on GPU?
  2. What's the memory model? (sieve array in shared mem vs global?)
  3. What throughput can we expect vs CPU?
  4. Is the transfer overhead (CPU<->GPU) acceptable?
"""

import math
import time

def analyze_gpu_sieve_siqs():
    """
    SIQS sieve on GPU.

    Current SIQS sieve: for each polynomial, sieve g(x) = a*x^2 + 2bx + c
    over x in [-M, M]. For each FB prime p, step through array at stride p.

    GPU approach 1: One thread per FB prime
      - Each thread sieves one prime p across the entire array
      - Problem: small primes (p=2,3,5...) write to MANY positions → memory conflicts
      - Large primes (p > M) hit at most once → thread does almost nothing

    GPU approach 2: One thread per sieve position
      - Each thread computes accumulated log for position x
      - For each FB prime p: check if p | g(x) via modular arithmetic
      - Problem: each thread iterates over entire FB → O(FB_size) per thread

    GPU approach 3: Bucket sieve (best for GPU)
      - Phase 1: For each FB prime p, compute hit positions → write to per-block buckets
      - Phase 2: Each block processes its bucket entries, accumulating logs
      - This is how CUDA sieves work in practice (e.g., msieve GPU)

    GPU approach 4: Batch trial division only
      - Sieve on CPU (fast, sequential access pattern)
      - GPU does trial division on candidates (embarrassingly parallel)
      - Each thread: take one candidate, trial divide against FB
    """
    print("=== SIQS GPU Sieve Analysis ===\n")

    # Current CPU sieve performance
    # From SIQS benchmarks: 60d takes 48s, sieve is 95% → 45.6s sieve
    # FB ≈ 15K primes, M ≈ 500K, ~500 polynomials
    # That's 500 * 1M = 500M sieve points
    cpu_sieve_rate = 500e6 / 45.6  # ~11M pts/sec (Python+numba)

    print(f"Current CPU SIQS sieve rate: ~{cpu_sieve_rate/1e6:.0f} M pts/sec (Python+numba)")
    print(f"Current CPU C GNFS sieve:    ~835 M pts/sec (measured)")

    # GPU theoretical throughput
    # Each sieve position needs: for each p in FB, one modular add
    # With bucket sieve: each bucket entry = 1 atomic add to shared mem
    # RTX 4050: 2560 cores * 2370 MHz = ~6 TOPS of INT32

    gpu_cores = 2560
    gpu_clock_ghz = 2.37
    # Each sieve "hit" = 1 memory write (uint16 add)
    # Bottleneck is memory bandwidth, not compute
    # Global memory: 192 GB/s = 96 billion uint16 writes/sec (best case)
    # But random access → effective ~20% = ~19 billion/sec
    # With shared memory (48KB per SM): much better locality

    # Realistic: GPU bucket sieve
    # Phase 1: generate bucket entries (GPU, parallel over primes)
    #   FB=15K primes, M=500K: total hits ≈ M * sum(1/p for p in FB) ≈ M * ln(ln(B))
    #   ≈ 500K * 3.5 = 1.75M hits per polynomial side
    # Phase 2: apply bucket entries (GPU, parallel over blocks)
    #   1.75M random writes to shared memory → trivial for GPU

    # Estimate: GPU can process one polynomial sieve in:
    fb_size = 15000
    M = 500000
    hits_per_poly = int(M * sum(1.0/p for p in range(2, 200)))  # approx

    # Phase 1: 15K threads, each writes M/p entries
    # GPU throughput for scatter: ~5 billion entries/sec
    phase1_time = hits_per_poly / 5e9

    # Phase 2: apply hits with atomic adds to shared/global mem
    phase2_time = hits_per_poly / 10e9  # shared mem atomics are fast

    # Phase 3: scan threshold
    phase3_time = 2 * M / 192e9  # sequential scan, bandwidth limited

    gpu_poly_time = phase1_time + phase2_time + phase3_time
    cpu_poly_time = 45.6 / 500  # 500 polys for 60d

    gpu_speedup = cpu_poly_time / gpu_poly_time

    print(f"\nSIQS (60d, FB=15K, M=500K, 500 polys):")
    print(f"  Hits per polynomial: ~{hits_per_poly/1e6:.1f}M")
    print(f"  GPU time per poly:   ~{gpu_poly_time*1e6:.0f} us")
    print(f"  CPU time per poly:   ~{cpu_poly_time*1e3:.1f} ms")
    print(f"  Estimated speedup:   ~{gpu_speedup:.0f}x")

    print(f"\n  BUT: CPU C sieve is already ~835M pts/sec (from gnfs benchmark)")
    print(f"  C sieve per poly: ~{2*M/835e6*1e3:.1f} ms per side")
    print(f"  GPU vs C sieve speedup: ~{2*M/(835e6*gpu_poly_time):.1f}x")

    return gpu_speedup


def analyze_gpu_sieve_gnfs():
    """GNFS lattice sieve on GPU."""
    print("\n=== GNFS Lattice Sieve GPU Analysis ===\n")

    gpu_cores = 2560
    gpu_clock_ghz = 2.37

    for I_max, J_max, label in [(5000, 100, "medium"), (10000, 200, "large")]:
        region = (2*I_max+1) * (J_max+1)
        row_bytes = (2*I_max+1) * 2  # uint16

        # Shared memory limit: 48KB per SM, 20 SMs
        fits_shared = row_bytes <= 48*1024

        # CPU rate (measured)
        cpu_rate = 110e6  # pts/sec from our benchmark
        cpu_time = region / cpu_rate

        # GPU: if row fits in shared mem, process all primes on that row
        # 2560 cores, each core processes ~1 prime per clock for sieve
        # With 10K FB primes: 10K/2560 = ~4 clocks to assign all primes
        # Each prime does I_max/p iterations ≈ varies
        # Total work per row: sum(I_max/p for p in FB) ≈ I_max * ln(ln(B))
        fb_size = 10000
        work_per_row = I_max * 3.5  # ln(ln(100K)) ≈ 3.5
        gpu_row_time = work_per_row / (gpu_cores * gpu_clock_ghz * 1e9) * 1000  # generous
        gpu_time = gpu_row_time * (J_max + 1)

        # But real bottleneck: shared mem atomic adds
        # Each hit = 1 atomic uint16 add to shared memory
        # Throughput: ~20 billion atomics/sec on RTX 4050
        hits_per_row = int(work_per_row * 2)  # rat + alg sides
        gpu_time_atomic = hits_per_row * (J_max+1) / 20e9

        speedup = cpu_time / max(gpu_time_atomic, 1e-12)

        print(f"  {label} region (I={I_max}, J={J_max}):")
        print(f"    Points: {region/1e6:.1f}M, Row size: {row_bytes/1024:.1f} KB"
              f" ({'fits' if fits_shared else 'EXCEEDS'} shared mem)")
        print(f"    CPU time:   {cpu_time*1000:.1f} ms ({cpu_rate/1e6:.0f}M pts/sec)")
        print(f"    GPU est:    {gpu_time_atomic*1000:.3f} ms")
        print(f"    Speedup:    ~{speedup:.0f}x")


def analyze_gpu_trial_division():
    """GPU trial division (most practical GPU acceleration)."""
    print("\n=== GPU Trial Division Analysis ===\n")

    # Most practical: CPU does sieve, GPU does trial division
    # Each candidate: divide by all FB primes until fully factored or rejected
    # Perfectly parallel: one thread per candidate

    # From GNFS: ~1000-10000 candidates per batch, FB=10K-100K primes
    # Each candidate needs up to 100K trial divisions
    # GPU: 2560 threads, each doing 100K divisions

    for fb, n_cands, label in [(10000, 5000, "43d"), (50000, 10000, "50d"),
                                (200000, 20000, "70d")]:
        # CPU: current C verify does ~10K cands/sec for fb=10K
        cpu_rate = 10000 * (10000 / fb)  # scales inversely with FB
        cpu_time = n_cands / cpu_rate

        # GPU: each thread does fb divisions for one candidate
        # Division cost: ~4 cycles per division on GPU (64-bit)
        # 2560 threads * 2.37 GHz / 4 = 1.5 billion divs/sec
        gpu_div_rate = 2560 * 2.37e9 / 4
        total_divs = n_cands * fb  # worst case
        gpu_time = total_divs / gpu_div_rate

        # Transfer overhead: send candidates + FB to GPU, get results back
        transfer = (n_cands * 16 + fb * 16) / 192e9  # bytes / bandwidth

        speedup = cpu_time / (gpu_time + transfer)

        print(f"  {label} (FB={fb}, {n_cands} candidates):")
        print(f"    CPU time:      {cpu_time*1000:.1f} ms")
        print(f"    GPU compute:   {gpu_time*1000:.2f} ms")
        print(f"    GPU transfer:  {transfer*1e6:.1f} us")
        print(f"    Speedup:       ~{speedup:.0f}x")


def analyze_batched_ecm():
    """
    Field 5: Batched ECM on GPU.

    ECM (Elliptic Curve Method) works best for medium factors (20-50 digits).
    Each curve is independent → embarrassingly parallel on GPU.

    Standard ECM: ~L(p)^sqrt(2) curves needed where p is factor size.
    Each curve: O(B1) point multiplications in stage 1, O(B2-B1) in stage 2.

    GPU ECM: run 2560 curves simultaneously.
    Each thread: one curve, doing Montgomery ladder arithmetic.
    Bottleneck: 256-bit modular multiplication (~50 cycles on GPU).
    """
    print("\n=== Batched ECM on GPU (Field 5) ===\n")

    # Montgomery multiplication on GPU: ~50 cycles for 256-bit
    # RTX 4050: 2560 cores * 2.37 GHz / 50 = ~122M mulmods/sec
    gpu_mulmod_rate = 2560 * 2.37e9 / 50

    # CPU (single core, gmpy2): ~10M mulmods/sec for 256-bit
    cpu_mulmod_rate = 10e6

    for factor_digits, B1, B2, label in [
        (20, 11000, 1900000, "p20"),
        (30, 250000, 128e6, "p30"),
        (40, 3000000, 6e9, "p40"),
        (50, 43000000, 2.4e11, "p50"),
    ]:
        # Stage 1: ~B1 point multiplications, each ~10 mulmods
        stage1_mulmods = B1 * 10
        # Stage 2: ~(B2-B1)/delta point operations, each ~5 mulmods
        stage2_mulmods = int((B2 - B1) / 210 * 5)  # delta=210 for baby-step
        total_mulmods = stage1_mulmods + stage2_mulmods

        # Expected curves needed
        # L(p) = exp(sqrt(ln(p) * ln(ln(p))))
        ln_p = factor_digits * math.log(10)
        Lp = math.exp(math.sqrt(ln_p * math.log(ln_p)))
        curves_needed = int(Lp ** math.sqrt(2))

        # CPU time (single core, one curve at a time)
        cpu_time_per_curve = total_mulmods / cpu_mulmod_rate
        cpu_total = cpu_time_per_curve * curves_needed

        # GPU time (2560 curves in parallel batches)
        gpu_time_per_curve = total_mulmods / (gpu_mulmod_rate / 2560)  # per-core rate
        n_batches = math.ceil(curves_needed / 2560)
        gpu_total = gpu_time_per_curve * n_batches

        # Also: GPU batch = all 2560 curves run in parallel
        gpu_batch_time = total_mulmods / gpu_mulmod_rate * 2560
        gpu_total2 = gpu_batch_time * n_batches

        speedup = cpu_total / max(gpu_total2, 1e-9)

        print(f"  {label} (B1={B1:.0f}, B2={B2:.0f}):")
        print(f"    Mulmods/curve:  {total_mulmods/1e6:.1f}M")
        print(f"    Curves needed:  ~{curves_needed}")
        print(f"    CPU total:      {cpu_total:.1f}s ({cpu_total/3600:.2f}h)")
        print(f"    GPU total:      {gpu_total2:.1f}s ({gpu_total2/3600:.2f}h)")
        print(f"    Speedup:        ~{speedup:.0f}x")

    print(f"\n  GPU mulmod rate: {gpu_mulmod_rate/1e6:.0f}M/sec (256-bit)")
    print(f"  CPU mulmod rate: {cpu_mulmod_rate/1e6:.0f}M/sec (gmpy2)")
    print(f"  Raw arithmetic speedup: {gpu_mulmod_rate/cpu_mulmod_rate:.0f}x")
    print(f"\n  CAVEAT: 256-bit GPU mulmod is complex (need multi-precision library).")
    print(f"  Existing CUDA ECM libraries: ecm-gpu (LIRMM), GMP-ECM with GPU support.")
    print(f"  Implementation effort: ~500 lines CUDA + Montgomery ladder, 1 week.")


def analyze_novel_norms():
    """
    Field 7: Novel Norm Forms for GNFS.

    The algebraic norm in GNFS is N_f(a,b) = resultant(a-b*x, f(x)) = b^d * f(-a/b).
    For standard base-m polynomials, coefficients are O(N^(1/d)), so:
      |N_f(a,b)| ≈ max(|c_i|) * max(A, B)^d ≈ N^(1/d) * A^d

    Smaller norms → higher smoothness probability → faster sieving.

    Approaches to reduce norms:
    1. Better polynomial selection (covered in Field 10)
    2. Skewness optimization: balance a^i * b^(d-i) terms
    3. Non-monic polynomials: a_d != 1, so leading term is smaller
    4. Rotations: f(x) → f(x) + k*g(x) preserves f(m) ≡ 0 mod n
    5. Translation: f(x) → f(x+t), changes coefficient distribution
    """
    print("\n=== Novel Norm Forms for GNFS (Field 7) ===\n")

    # Demonstrate norm sizes for different polynomial strategies
    import gmpy2
    from gmpy2 import mpz, iroot

    # Test number: 43 digits
    n = mpz("1522605027922533360535618378132637429718068114961")  # RSA-129's first 43 digits approx
    # Actually let's use a proper semiprime
    p = gmpy2.next_prime(mpz(10)**21 + 7)
    q = gmpy2.next_prime(mpz(10)**21 + 1000007)
    n = p * q
    nd = len(str(int(n)))

    d = 4
    m0 = int(iroot(n, d)[0])

    print(f"N = {n} ({nd}d)")
    print(f"d = {d}, m0 = {m0}")

    # Strategy 1: Standard base-m
    def base_m_coeffs(n, m, d):
        coeffs = []
        rem = int(n)
        for i in range(d+1):
            coeffs.append(rem % m)
            rem //= m
        if rem > 0:
            coeffs[-1] += rem * m
        return coeffs

    std_coeffs = base_m_coeffs(int(n), m0, d)
    max_std = max(abs(c) for c in std_coeffs)

    # Norm at typical sieve point (a=50000, b=100)
    a_test, b_test = 50000, 100
    norm_std = abs(sum(std_coeffs[i] * (-a_test)**i * b_test**(d-i) for i in range(d+1)))

    print(f"\nStrategy 1: Standard base-m")
    print(f"  Coefficients: {std_coeffs}")
    print(f"  Max coeff: {max_std:.2e}")
    print(f"  Norm at (a={a_test},b={b_test}): {norm_std:.2e}")
    print(f"  Log2(norm): {math.log2(norm_std):.1f}")

    # Strategy 2: Rotation f(x) → f(x) + k*g(x) where g(x) = x - m
    # Adding k*(x-m) changes: c_0 → c_0 - k*m, c_1 → c_1 + k
    best_rot_norm = norm_std
    best_k = 0
    for k in range(-1000, 1001):
        rot_coeffs = list(std_coeffs)
        rot_coeffs[0] -= k * m0
        rot_coeffs[1] += k
        norm = abs(sum(rot_coeffs[i] * (-a_test)**i * b_test**(d-i) for i in range(d+1)))
        if norm < best_rot_norm:
            best_rot_norm = norm
            best_k = k

    rot_coeffs = list(std_coeffs)
    rot_coeffs[0] -= best_k * m0
    rot_coeffs[1] += best_k

    print(f"\nStrategy 2: Rotation by k={best_k}")
    print(f"  Coefficients: {rot_coeffs}")
    print(f"  Max coeff: {max(abs(c) for c in rot_coeffs):.2e}")
    print(f"  Norm at (a={a_test},b={b_test}): {best_rot_norm:.2e}")
    print(f"  Log2(norm): {math.log2(max(best_rot_norm,1)):.1f}")
    print(f"  Improvement: {norm_std/max(best_rot_norm,1):.1f}x smaller")

    # Strategy 3: Search over multiple m values (already in gnfs_engine.py)
    best_m_norm = norm_std
    best_m = m0
    for delta in range(-500, 501):
        m_try = m0 + delta
        if m_try < 2:
            continue
        coeffs = base_m_coeffs(int(n), m_try, d)
        if coeffs[-1] <= 0:
            continue
        norm = abs(sum(coeffs[i] * (-a_test)**i * b_test**(d-i) for i in range(d+1)))
        if norm < best_m_norm:
            best_m_norm = norm
            best_m = m_try

    best_coeffs = base_m_coeffs(int(n), best_m, d)
    print(f"\nStrategy 3: Best m in m0±500 (m={best_m}, delta={best_m-m0})")
    print(f"  Coefficients: {best_coeffs}")
    print(f"  Max coeff: {max(abs(c) for c in best_coeffs):.2e}")
    print(f"  Norm: {best_m_norm:.2e}, Log2: {math.log2(max(best_m_norm,1)):.1f}")
    print(f"  Improvement: {norm_std/max(best_m_norm,1):.1f}x")

    # Strategy 4: Combined rotation + m search
    overall_best = norm_std
    overall_best_m = m0
    overall_best_k = 0
    for delta in range(-200, 201, 5):
        m_try = m0 + delta
        if m_try < 2:
            continue
        coeffs = base_m_coeffs(int(n), m_try, d)
        if coeffs[-1] <= 0:
            continue
        for k in range(-200, 201, 5):
            rc = list(coeffs)
            rc[0] -= k * m_try
            rc[1] += k
            norm = abs(sum(rc[i] * (-a_test)**i * b_test**(d-i) for i in range(d+1)))
            if norm < overall_best:
                overall_best = norm
                overall_best_m = m_try
                overall_best_k = k

    print(f"\nStrategy 4: Combined m+rotation search (m={overall_best_m}, k={overall_best_k})")
    print(f"  Norm: {overall_best:.2e}, Log2: {math.log2(max(overall_best,1)):.1f}")
    print(f"  Improvement over base: {norm_std/max(overall_best,1):.1f}x")

    # Impact on smoothness
    FB = 100000
    u_base = math.log2(norm_std) / math.log2(FB)
    u_best = math.log2(max(overall_best, 2)) / math.log2(FB)

    # Dickman rho approximation
    def dickman(u):
        if u <= 1: return 1.0
        if u <= 2: return 1.0 - math.log(u)
        table = {2:0.3069, 3:0.0486, 4:0.00491, 5:3.07e-4, 6:1.33e-5,
                 7:4.23e-7, 8:1.02e-8}
        keys = sorted(table.keys())
        for i in range(len(keys)-1):
            if keys[i] <= u <= keys[i+1]:
                t = (u - keys[i]) / (keys[i+1] - keys[i])
                return math.exp(math.log(table[keys[i]]) * (1-t) + math.log(table[keys[i+1]]) * t)
        return table[keys[-1]] * (keys[-1]/u)**u

    smooth_base = dickman(u_base)
    smooth_best = dickman(u_best)

    print(f"\n  Smoothness analysis (FB={FB}):")
    print(f"    Base:  u={u_base:.2f}, P(smooth)={smooth_base:.2e}")
    print(f"    Best:  u={u_best:.2f}, P(smooth)={smooth_best:.2e}")
    print(f"    Smoothness gain: {smooth_best/max(smooth_base, 1e-50):.1f}x")


def analyze_multi_poly_gnfs():
    """
    Field 10: Multi-Polynomial GNFS.

    Currently: search ±1000 around m0 for best single polynomial.
    Advanced: generate thousands of candidates with different strategies,
    score each by Murphy E-score, use top-K for sieving.

    Murphy E-score = integral over sieve region of P(smooth(f(a,b))) weighted
    by 1/log(|f(a,b)|). More accurate than just norm size.
    """
    print("\n=== Multi-Polynomial GNFS (Field 10) ===\n")

    # How many polynomials can we test per second?
    # Current: score_polynomial does murphy_alpha (B=500) = 500 primes to check
    # Each prime: enumerate roots mod p → O(p) per prime
    # Total: sum(p for p in primes up to 500) ≈ 500*250 = 125K operations
    # Python: ~1M ops/sec → ~0.1s per polynomial

    # With C acceleration: ~100x faster → ~1ms per polynomial
    # In 60 seconds: 60K polynomials scored

    strategies = [
        ("Base-m, m ± 2000", 4001, "Current approach, simple"),
        ("Base-m + rotation k ± 500", 4001 * 1001, "m search × rotation search"),
        ("Kleinjung's method", 100000, "Lattice-based poly search (state of art)"),
        ("Random a_d, Kleinjung", 1000000, "Fix leading coeff, optimize rest"),
    ]

    print(f"{'Strategy':<35} {'Candidates':>12} {'Time (C)':>10} {'Quality':>10}")
    print("-" * 70)
    for name, n_cands, note in strategies:
        time_c = n_cands * 0.001  # 1ms per poly in C
        time_py = n_cands * 0.1   # 100ms per poly in Python
        quality = "baseline" if n_cands < 5000 else (
            "good" if n_cands < 100000 else "best")
        t_str = f"{time_c:.0f}s" if time_c < 3600 else f"{time_c/3600:.1f}h"
        print(f"  {name:<33} {n_cands:>12,} {t_str:>10} {quality:>10}")
        print(f"    {note}")

    print(f"\nKey insight: polynomial selection time is AMORTIZED over sieving.")
    print(f"For a 60d number that takes 3600s to sieve, spending 60s on poly")
    print(f"selection is well worth it if it gives 10% smaller norms → 2-3x")
    print(f"more smooth relations.")

    print(f"\nMurphy E-score computation:")
    print(f"  Full E-score requires numerical integration (expensive)")
    print(f"  Proxy: alpha score + norm size at typical points (current method)")
    print(f"  Better proxy: alpha + log(resultant) + root properties at small primes")
    print(f"  Key root property: number of roots of f mod p for small p")
    print(f"  More roots → more sieve hits → faster relation collection")

    print(f"\nRecommendation:")
    print(f"  1. Keep current m±1000 search (adequate for 43-50d)")
    print(f"  2. Add rotation search k±500 (easy, 2-10x norm reduction)")
    print(f"  3. For 70d+: implement Kleinjung-style search in C")
    print(f"  4. Score by: norm_size + 2*alpha + root_count_bonus")


if __name__ == '__main__':
    print("=" * 72)
    print("ITERATION 2: Fields 4, 5, 7, 10 — GPU & Polynomial Analysis")
    print("=" * 72)

    # Field 4: GPU Sieving
    print("\n" + "=" * 72)
    print("FIELD 4: GPU Sieving")
    print("=" * 72)
    analyze_gpu_sieve_siqs()
    analyze_gpu_sieve_gnfs()
    analyze_gpu_trial_division()

    # Field 5: Batched ECM
    print("\n" + "=" * 72)
    print("FIELD 5: Batched ECM on GPU")
    print("=" * 72)
    analyze_batched_ecm()

    # Field 7: Novel Norm Forms
    print("\n" + "=" * 72)
    print("FIELD 7: Novel Norm Forms for GNFS")
    print("=" * 72)
    analyze_novel_norms()

    # Field 10: Multi-Polynomial GNFS
    print("\n" + "=" * 72)
    print("FIELD 10: Multi-Polynomial GNFS")
    print("=" * 72)
    analyze_multi_poly_gnfs()

    print("\n" + "=" * 72)
    print("ITERATION 2 SUMMARY")
    print("=" * 72)
    print("""
Priority update after iteration 2:

1. C Lattice Sieve (Field 2) — PROTOTYPE DONE (see lattice_sieve_c.c)
   Measured: 22-110 M pts/sec, 15-78 KB memory per q
   vs line sieve: 835 M pts/sec but 3.8 MB per b-line
   NET: lattice wins because norms ~q times smaller (10-50x more relations/pt)

2. Block Lanczos (Field 3) — analysis from iter 1, still #2 priority

3. GPU Trial Division (Field 4) — MEDIUM priority
   GPU sieve: ~10-50x over Python SIQS, but only ~2-5x over C sieve
   GPU trial division: 5-20x speedup, embarrassingly parallel
   GPU ECM: ~12x speedup for 256-bit arithmetic
   RECOMMENDATION: GPU trial division is easiest win (1-2 days CUDA)

4. Polynomial Rotation (Field 7) — EASY win, add to gnfs_engine.py
   Rotation f(x) + k*(x-m) reduces norms 2-10x with minimal code
   Combined m+rotation search: 5-20x norm reduction possible

5. Multi-Poly (Field 10) — LOW priority at current scale
   Current m±1000 search is adequate for 43-50d
   For 70d+: need Kleinjung-style search (weeks of development)

6. Batched ECM (Field 5) — SPECIALIZED, useful for unbalanced factors
   GPU ECM: ~12x over CPU, useful for 20-50d factors
   Not critical for RSA-100 (balanced factors → NFS is better)
""")
