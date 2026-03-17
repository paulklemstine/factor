#!/usr/bin/env python3
"""
v8_pvsnp.py — Five Novel Approaches to P vs NP via Factoring
=============================================================
Phase 4: Game-theoretic, Kolmogorov, compression, and time-space analyses.

Approach 1: Factoring as an Interactive Game (game tree complexity)
Approach 2: Kolmogorov Complexity of Factors (conditional descriptive complexity)
Approach 3: Algorithmic Information Distance (mutual information in factoring)
Approach 4: Factoring via Compression (compressibility vs difficulty correlation)
Approach 5: Time-Space Tradeoff Measurement (is T*S constant for factoring?)

RAM budget: <1.5 GB throughout.
"""

import sys, os, time, math, random, struct, zlib, bz2, lzma, json, hashlib
import collections, itertools, functools
from typing import List, Tuple, Dict, Optional
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, invert

# ─── Utility: generate semiprimes ────────────────────────────────────────────

def random_prime(bits):
    """Generate a random prime of exactly `bits` bits."""
    while True:
        p = gmpy2.mpz_random(gmpy2.random_state(random.getrandbits(64)), mpz(1) << bits)
        p |= (mpz(1) << (bits - 1)) | 1  # ensure top bit set and odd
        if is_prime(p):
            return p

def make_semiprime(total_bits, balance=0.5):
    """Make N=p*q with total_bits bits. balance=0.5 means equal-size factors."""
    p_bits = max(4, int(total_bits * balance))
    q_bits = total_bits - p_bits
    p = random_prime(p_bits)
    q = random_prime(q_bits)
    while p == q:
        q = random_prime(q_bits)
    return p * q, min(p, q), max(p, q)

def make_structured_semiprime(total_bits, structure_type="close"):
    """Make a semiprime with specific structure."""
    half = total_bits // 2
    if structure_type == "close":
        # p and q are close together (Fermat-vulnerable)
        p = random_prime(half)
        q = next_prime(p + random.randint(1, int(p ** 0.25)))
        return p * q, p, q
    elif structure_type == "smooth_neighbor":
        # p-1 is smooth (Pollard p-1 vulnerable)
        while True:
            p = mpz(2)
            for _ in range(half // 3):
                p *= random.choice([2, 3, 5, 7, 11, 13])
            p += 1
            if is_prime(p) and p.bit_length() >= half - 2:
                break
        q = random_prime(half)
        return p * q, min(p, q), max(p, q)
    elif structure_type == "twin":
        # p and q are both part of twin prime pairs
        while True:
            p = random_prime(half)
            if is_prime(p + 2) or is_prime(p - 2):
                break
        while True:
            q = random_prime(half)
            if q != p and (is_prime(q + 2) or is_prime(q - 2)):
                break
        return p * q, min(p, q), max(p, q)
    else:  # random
        return make_semiprime(total_bits)


# ═══════════════════════════════════════════════════════════════════════════════
# APPROACH 1: Factoring as a 2-Player Game
# ═══════════════════════════════════════════════════════════════════════════════

def game_tree_analysis(bit_sizes=[16, 20, 24, 28, 32, 36, 40], trials=30):
    """
    Model factoring as an interactive game between Prover (knows p,q) and
    Verifier (knows only N). Measure the INFORMATION CONTENT of optimal
    verification strategies.

    Key insight: In a game tree, the Prover's optimal strategy reveals
    the minimum information needed. We measure:
    1. Binary search rounds (log2 of factor space)
    2. Modular hint rounds (Prover reveals p mod small primes)
    3. Bit-by-bit revelation with adaptive verification
    4. Game tree branching factor at each depth
    """
    print("=" * 72)
    print("APPROACH 1: Factoring as an Interactive Game")
    print("=" * 72)

    results = []

    for nbits in bit_sizes:
        round_counts = {"binary_search": [], "modular_hints": [],
                        "adaptive_bits": [], "gcd_game": []}

        for _ in range(trials):
            N, p, q = make_semiprime(nbits)

            # Strategy 1: Binary search on factor value
            # Verifier asks "is p > X?" — Prover answers truthfully
            lo, hi = mpz(2), isqrt(N)
            rounds_bs = 0
            while lo < hi:
                mid = (lo + hi) // 2
                if p > mid:
                    lo = mid + 1
                else:
                    hi = mid
                rounds_bs += 1
            round_counts["binary_search"].append(rounds_bs)

            # Strategy 2: Modular hints — Prover reveals p mod small primes
            # How many small primes needed to reconstruct p via CRT?
            rounds_mh = 0
            product = mpz(1)
            prime = mpz(2)
            while product < isqrt(N):
                product *= prime
                prime = next_prime(prime)
                rounds_mh += 1
            round_counts["modular_hints"].append(rounds_mh)

            # Strategy 3: Adaptive bit revelation
            # Prover reveals bits of p one at a time; Verifier checks consistency
            # After k bits revealed, Verifier knows p mod 2^k
            # Can Verifier prune early using N mod 2^k = (p mod 2^k)(q mod 2^k)?
            rounds_ab = 0
            known_p_mod = mpz(0)
            modulus = mpz(1)
            for bit_pos in range(nbits):
                bit_val = (p >> bit_pos) & 1
                known_p_mod += bit_val * modulus
                modulus *= 2
                rounds_ab += 1
                # Check: does known_p_mod divide N mod modulus?
                n_mod = N % modulus
                if known_p_mod > 0 and n_mod % known_p_mod == 0:
                    candidate_q_mod = n_mod // known_p_mod
                    if candidate_q_mod > 1:
                        # Could we reconstruct? Only if modulus > sqrt(N)
                        if modulus > isqrt(N):
                            break
            round_counts["adaptive_bits"].append(rounds_ab)

            # Strategy 4: GCD game — Prover suggests random multiples of p
            # Verifier computes gcd(hint, N)
            rounds_gcd = 0
            found = False
            while not found:
                # Prover sends k*p + noise (with decreasing noise)
                noise_bits = max(0, nbits // 2 - rounds_gcd * 2)
                hint = p * random.randint(1, 10) + random.randint(0, max(1, 1 << noise_bits))
                g = gcd(hint, N)
                rounds_gcd += 1
                if g > 1 and g < N:
                    found = True
                if rounds_gcd > 100:
                    break
            round_counts["gcd_game"].append(rounds_gcd)

        avg = {k: sum(v) / len(v) for k, v in round_counts.items()}
        theoretical_bs = nbits / 2  # log2(sqrt(N))

        results.append({
            "bits": nbits,
            "binary_search_rounds": avg["binary_search"],
            "modular_hint_rounds": avg["modular_hints"],
            "adaptive_bit_rounds": avg["adaptive_bits"],
            "gcd_game_rounds": avg["gcd_game"],
            "theoretical_bs": theoretical_bs,
            "bs_ratio": avg["binary_search"] / theoretical_bs,
            "info_content_bits": avg["adaptive_bits"],
        })

        print(f"  {nbits:3d}b: BS={avg['binary_search']:.1f} "
              f"(theory={theoretical_bs:.0f}) "
              f"ModHint={avg['modular_hints']:.1f} "
              f"AdaptBit={avg['adaptive_bits']:.1f} "
              f"GCD_game={avg['gcd_game']:.1f}")

    # Key analysis: does information content scale linearly with n?
    print("\n  KEY FINDING: Information content of optimal game strategy")
    for r in results:
        excess = r["info_content_bits"] - r["theoretical_bs"]
        print(f"    {r['bits']:3d}b: info={r['info_content_bits']:.1f} bits, "
              f"theory={r['theoretical_bs']:.0f}, excess={excess:+.1f}")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# APPROACH 2: Kolmogorov Complexity of Factors
# ═══════════════════════════════════════════════════════════════════════════════

def kolmogorov_analysis(bit_sizes=[32, 40, 48, 56, 64], trials=50):
    """
    Approximate K(p|N) using compression as a proxy.

    Key idea: K(p|N) measures the descriptive complexity of p given N.
    For random semiprimes, K(p|N) ≈ n/2 (p is random given N).
    For structured semiprimes, K(p|N) might be smaller.

    We estimate K(p) and K(p|N) by:
    1. Compressing p alone → proxy for K(p)
    2. Compressing p concatenated with N, minus K(N) → proxy for K(p|N)
    3. Comparing structured vs random semiprimes
    """
    print("\n" + "=" * 72)
    print("APPROACH 2: Kolmogorov Complexity of Factors")
    print("=" * 72)

    results = []

    for nbits in bit_sizes:
        records = {"random": [], "close": [], "smooth": [], "twin": []}

        for structure in records.keys():
            for _ in range(trials):
                if structure == "random":
                    N, p, q = make_semiprime(nbits)
                else:
                    try:
                        N, p, q = make_structured_semiprime(nbits, structure)
                    except Exception:
                        continue

                # Convert to byte strings
                p_bytes = int(p).to_bytes(max(1, (int(p).bit_length() + 7) // 8), 'big')
                q_bytes = int(q).to_bytes(max(1, (int(q).bit_length() + 7) // 8), 'big')
                n_bytes = int(N).to_bytes(max(1, (int(N).bit_length() + 7) // 8), 'big')

                # Compress individually
                kp = len(zlib.compress(p_bytes, 9))
                kq = len(zlib.compress(q_bytes, 9))
                kn = len(zlib.compress(n_bytes, 9))

                # Compress p|N (proxy for K(p,N))
                kpn = len(zlib.compress(p_bytes + n_bytes, 9))
                # K(p|N) ≈ K(p,N) - K(N)
                kp_given_n = max(0, kpn - kn)

                # Also try: compress (p XOR portion_of_N)
                # If p is "hidden" in N, XOR should compress well
                p_padded = p_bytes.ljust(len(n_bytes), b'\x00')
                xor_bytes = bytes(a ^ b for a, b in zip(p_padded, n_bytes))
                k_xor = len(zlib.compress(xor_bytes, 9))

                # Ratio: how much of p's complexity is "explained" by N?
                if kp > 0:
                    explained_ratio = 1.0 - (kp_given_n / kp)
                else:
                    explained_ratio = 0

                records[structure].append({
                    "kp": kp, "kn": kn, "kpn": kpn,
                    "kp_given_n": kp_given_n,
                    "k_xor": k_xor,
                    "explained_ratio": explained_ratio,
                    "raw_p_bytes": len(p_bytes),
                })

        result = {"bits": nbits}
        print(f"\n  {nbits}b semiprimes:")
        for structure, recs in records.items():
            if not recs:
                continue
            avg_kp = sum(r["kp"] for r in recs) / len(recs)
            avg_kp_given_n = sum(r["kp_given_n"] for r in recs) / len(recs)
            avg_explained = sum(r["explained_ratio"] for r in recs) / len(recs)
            avg_xor = sum(r["k_xor"] for r in recs) / len(recs)
            raw = sum(r["raw_p_bytes"] for r in recs) / len(recs)

            print(f"    {structure:8s}: K(p)={avg_kp:.1f}B  K(p|N)={avg_kp_given_n:.1f}B  "
                  f"explained={avg_explained:.3f}  K(p⊕N)={avg_xor:.1f}B  raw={raw:.0f}B")
            result[f"{structure}_kp"] = avg_kp
            result[f"{structure}_kp_given_n"] = avg_kp_given_n
            result[f"{structure}_explained"] = avg_explained
        results.append(result)

    # Key insight: if explained_ratio > 0 for structured primes but ≈ 0 for random,
    # it means structure leaks factor information through N
    print("\n  KEY FINDING: Does semiprime structure leak Kolmogorov information?")
    for r in results:
        rand_e = r.get("random_explained", 0)
        close_e = r.get("close_explained", 0)
        smooth_e = r.get("smooth_explained", 0)
        print(f"    {r['bits']:3d}b: random={rand_e:.3f}  close={close_e:.3f}  "
              f"smooth={smooth_e:.3f}  "
              f"gap={close_e - rand_e:+.3f}")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# APPROACH 3: Algorithmic Information Distance
# ═══════════════════════════════════════════════════════════════════════════════

def information_distance_analysis(bit_sizes=[32, 40, 48, 56, 64], trials=50):
    """
    Measure the Normalized Information Distance (NID) between p and N.

    NID(x,y) = max(K(x|y), K(y|x)) / max(K(x), K(y))

    For N=pq:
      K(N|p) = K(q) ≈ n/2  (given p, just need q — trivial division)
      K(p|N) ≈ n/2 (factoring is hard, p is ~random given N)

    So NID(p,N) ≈ (n/2) / n = 0.5

    But is this EXACTLY 0.5? Deviations could reveal structure.
    Also: how does NID vary across different semiprime structures?
    """
    print("\n" + "=" * 72)
    print("APPROACH 3: Algorithmic Information Distance")
    print("=" * 72)

    results = []

    for nbits in bit_sizes:
        nid_values = {"random": [], "close": [], "smooth": []}

        for structure in nid_values.keys():
            for _ in range(trials):
                if structure == "random":
                    N, p, q = make_semiprime(nbits)
                else:
                    try:
                        N, p, q = make_structured_semiprime(nbits, structure)
                    except Exception:
                        continue

                p_bytes = int(p).to_bytes(max(1, (int(p).bit_length() + 7) // 8), 'big')
                n_bytes = int(N).to_bytes(max(1, (int(N).bit_length() + 7) // 8), 'big')
                q_bytes = int(q).to_bytes(max(1, (int(q).bit_length() + 7) // 8), 'big')

                # Use multiple compressors and average (more robust estimate)
                nid_estimates = []
                for compress_fn in [
                    lambda x: zlib.compress(x, 9),
                    lambda x: bz2.compress(x, 9),
                    lambda x: lzma.compress(x),
                ]:
                    kp = len(compress_fn(p_bytes))
                    kn = len(compress_fn(n_bytes))
                    kpn = len(compress_fn(p_bytes + n_bytes))
                    knp = len(compress_fn(n_bytes + p_bytes))

                    # K(p|N) ≈ K(p,N) - K(N) = kpn - kn
                    kp_given_n = max(0, kpn - kn)
                    # K(N|p) ≈ K(N,p) - K(p) = knp - kp
                    kn_given_p = max(0, knp - kp)

                    # NID
                    numerator = max(kp_given_n, kn_given_p)
                    denominator = max(kp, kn)
                    if denominator > 0:
                        nid_estimates.append(numerator / denominator)

                if nid_estimates:
                    nid_values[structure].append(sum(nid_estimates) / len(nid_estimates))

                    # Also compute: K(N|p) using actual division
                    # Since q = N/p is trivially computable, K(N|p) ≈ K(q)
                    kq = len(zlib.compress(q_bytes, 9))
                    # This should be much less than kp_given_n if factoring is hard
                    # (asymmetry = hardness indicator)

        result = {"bits": nbits}
        print(f"\n  {nbits}b semiprimes — Normalized Information Distance:")
        for structure, nids in nid_values.items():
            if not nids:
                continue
            avg_nid = sum(nids) / len(nids)
            std_nid = (sum((x - avg_nid) ** 2 for x in nids) / len(nids)) ** 0.5
            # Theoretical NID for random semiprimes
            theory = 0.5
            print(f"    {structure:8s}: NID={avg_nid:.4f} ± {std_nid:.4f}  "
                  f"(theory=0.500, dev={avg_nid - theory:+.4f})")
            result[f"{structure}_nid"] = avg_nid
            result[f"{structure}_nid_std"] = std_nid
        results.append(result)

    # Key insight: if close primes have lower NID, it means the factors are
    # "more related" to N — which is exactly what makes them easier to find
    print("\n  KEY FINDING: NID deviation from 0.5 as difficulty indicator")
    for r in results:
        rand_nid = r.get("random_nid", 0.5)
        close_nid = r.get("close_nid", 0.5)
        print(f"    {r['bits']:3d}b: NID_random={rand_nid:.4f}  NID_close={close_nid:.4f}  "
              f"gap={close_nid - rand_nid:+.4f}")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# APPROACH 4: Factoring via Compression
# ═══════════════════════════════════════════════════════════════════════════════

def compression_factoring_analysis(bit_sizes=[24, 28, 32, 36, 40, 44, 48],
                                    trials=100, factor_trials=5):
    """
    Core hypothesis: if N = pq can be compressed below n bits, the
    compression implicitly encodes factor structure.

    Experiments:
    1. Compress many semiprimes — does compression ratio predict difficulty?
    2. Compress N in different bases — does any base reveal factor structure?
    3. Compress N's binary representation with context mixing — look for patterns
    4. Compare compression of N vs random numbers of same size
    """
    print("\n" + "=" * 72)
    print("APPROACH 4: Factoring via Compression")
    print("=" * 72)

    # Experiment 4a: Compression ratio vs factoring difficulty
    print("\n  Experiment 4a: Compression ratio vs actual factoring time")
    print("  " + "-" * 60)

    timing_results = []

    for nbits in bit_sizes:
        records = []
        for _ in range(trials):
            N, p, q = make_semiprime(nbits)
            n_bytes = int(N).to_bytes(max(1, (int(N).bit_length() + 7) // 8), 'big')

            # Compression ratios with multiple algorithms
            ratios = {}
            for name, fn in [("zlib", lambda x: zlib.compress(x, 9)),
                             ("bz2", lambda x: bz2.compress(x, 9)),
                             ("lzma", lambda x: lzma.compress(x))]:
                compressed = fn(n_bytes)
                ratios[name] = len(compressed) / len(n_bytes)

            # Measure actual factoring time (trial division + Pollard rho)
            if nbits <= 48:
                t0 = time.perf_counter()
                for _ in range(factor_trials):
                    _factor_timed(N)
                t1 = time.perf_counter()
                factor_time = (t1 - t0) / factor_trials
            else:
                factor_time = None

            records.append({
                "N": int(N), "p": int(p), "q": int(q),
                "ratios": ratios,
                "factor_time": factor_time,
                "balance": min(p.bit_length(), q.bit_length()) / max(p.bit_length(), q.bit_length()),
                "gap": abs(int(p) - int(q)),
            })

        avg_zlib = sum(r["ratios"]["zlib"] for r in records) / len(records)
        avg_bz2 = sum(r["ratios"]["bz2"] for r in records) / len(records)

        # Correlation between compression ratio and factor time
        if records[0]["factor_time"] is not None:
            times = [r["factor_time"] for r in records]
            zlips = [r["ratios"]["zlib"] for r in records]
            corr = _pearson(zlips, times)
            avg_time = sum(times) / len(times)
            print(f"    {nbits:3d}b: zlib_ratio={avg_zlib:.3f}  bz2_ratio={avg_bz2:.3f}  "
                  f"avg_time={avg_time:.6f}s  corr(zlib,time)={corr:+.3f}")
        else:
            print(f"    {nbits:3d}b: zlib_ratio={avg_zlib:.3f}  bz2_ratio={avg_bz2:.3f}")

        timing_results.append({
            "bits": nbits,
            "avg_zlib": avg_zlib,
            "avg_bz2": avg_bz2,
            "records": records,
        })

    # Experiment 4b: Base-dependent compression
    print("\n  Experiment 4b: Compression in different number bases")
    print("  " + "-" * 60)

    base_results = []
    for nbits in [40, 48, 56]:
        base_ratios = collections.defaultdict(list)
        for _ in range(trials):
            N, p, q = make_semiprime(nbits)
            for base in [2, 3, 6, 10, 16, 256]:
                rep = _to_base_bytes(int(N), base)
                ratio = len(zlib.compress(rep, 9)) / len(rep) if len(rep) > 0 else 1.0
                base_ratios[base].append(ratio)

        print(f"    {nbits}b: ", end="")
        row = {"bits": nbits}
        for base in [2, 3, 6, 10, 16, 256]:
            avg = sum(base_ratios[base]) / len(base_ratios[base])
            print(f"base{base}={avg:.3f} ", end="")
            row[f"base{base}"] = avg
        print()
        base_results.append(row)

    # Experiment 4c: Compression of semiprimes vs random numbers
    print("\n  Experiment 4c: Semiprimes vs random numbers (compression)")
    print("  " + "-" * 60)

    for nbits in [32, 48, 64]:
        semi_ratios = []
        rand_ratios = []
        prime_ratios = []
        for _ in range(200):
            N, _, _ = make_semiprime(nbits)
            n_bytes = int(N).to_bytes(max(1, (int(N).bit_length() + 7) // 8), 'big')
            semi_ratios.append(len(zlib.compress(n_bytes, 9)) / len(n_bytes))

            # Random number of same size
            R = random.getrandbits(nbits)
            r_bytes = R.to_bytes(max(1, nbits // 8), 'big')
            rand_ratios.append(len(zlib.compress(r_bytes, 9)) / len(r_bytes))

            # Prime of same size
            P = random_prime(nbits)
            p_bytes = int(P).to_bytes(max(1, (int(P).bit_length() + 7) // 8), 'big')
            prime_ratios.append(len(zlib.compress(p_bytes, 9)) / len(p_bytes))

        print(f"    {nbits:3d}b: semi={sum(semi_ratios)/len(semi_ratios):.4f}  "
              f"random={sum(rand_ratios)/len(rand_ratios):.4f}  "
              f"prime={sum(prime_ratios)/len(prime_ratios):.4f}  "
              f"semi-random={sum(semi_ratios)/len(semi_ratios) - sum(rand_ratios)/len(rand_ratios):+.4f}")

    return timing_results, base_results


# ═══════════════════════════════════════════════════════════════════════════════
# APPROACH 5: Time-Space Tradeoff for Factoring
# ═══════════════════════════════════════════════════════════════════════════════

def time_space_tradeoff(bit_sizes=[24, 28, 32, 36, 40], trials=10):
    """
    Measure factoring time as a function of available memory.

    Algorithms with different space requirements:
    1. Trial division: O(1) space, O(N^{1/2}) time
    2. Pollard rho: O(1) space, O(N^{1/4}) time (heuristic)
    3. Baby-step giant-step: O(N^{1/4}) space, O(N^{1/4}) time
    4. Pollard rho with limited cycle detection (tunable space)
    5. Hash-based rho with table size limit (tunable space)

    Key question: Is T * S = Theta(N^{1/2}) always? Or can we beat it?
    """
    print("\n" + "=" * 72)
    print("APPROACH 5: Time-Space Tradeoff for Factoring")
    print("=" * 72)

    results = []

    for nbits in bit_sizes:
        print(f"\n  {nbits}b semiprimes:")
        print(f"    {'Method':<25s} {'Time(s)':>10s} {'Space(entries)':>15s} {'T*S':>15s}")
        print("    " + "-" * 65)

        row = {"bits": nbits, "methods": []}

        for _ in range(trials):
            N, p, q = make_semiprime(nbits)

            # Method 1: Trial division (O(1) space)
            t0 = time.perf_counter()
            _trial_division(N)
            t_trial = time.perf_counter() - t0
            s_trial = 1

            # Method 2: Pollard rho (O(1) space)
            t0 = time.perf_counter()
            _pollard_rho(N)
            t_rho = time.perf_counter() - t0
            s_rho = 2  # only stores x, y

            # Method 3: BSGS-style (sqrt(sqrt(N)) space)
            space_limit = max(16, int(gmpy2.isqrt(gmpy2.isqrt(mpz(N)))))
            space_limit = min(space_limit, 1 << 18)  # cap at 256K entries for RAM
            t0 = time.perf_counter()
            _bsgs_factor(N, space_limit)
            t_bsgs = time.perf_counter() - t0
            s_bsgs = space_limit

            # Method 4: Rho with bounded cycle table
            for table_size in [16, 64, 256, 1024, 4096]:
                if table_size > space_limit:
                    break
                t0 = time.perf_counter()
                _bounded_rho(N, table_size)
                t_bounded = time.perf_counter() - t0

                row["methods"].append({
                    "name": f"bounded_rho_{table_size}",
                    "time": t_bounded, "space": table_size,
                    "ts_product": t_bounded * table_size,
                })

            row["methods"].append({"name": "trial_div", "time": t_trial, "space": s_trial, "ts_product": t_trial * s_trial})
            row["methods"].append({"name": "pollard_rho", "time": t_rho, "space": s_rho, "ts_product": t_rho * s_rho})
            row["methods"].append({"name": "bsgs", "time": t_bsgs, "space": s_bsgs, "ts_product": t_bsgs * s_bsgs})

        # Average across trials
        method_avgs = collections.defaultdict(lambda: {"times": [], "spaces": [], "ts": []})
        for m in row["methods"]:
            method_avgs[m["name"]]["times"].append(m["time"])
            method_avgs[m["name"]]["spaces"].append(m["space"])
            method_avgs[m["name"]]["ts"].append(m["ts_product"])

        ts_products = []
        for name, data in sorted(method_avgs.items()):
            avg_t = sum(data["times"]) / len(data["times"])
            avg_s = sum(data["spaces"]) / len(data["spaces"])
            avg_ts = sum(data["ts"]) / len(data["ts"])
            print(f"    {name:<25s} {avg_t:>10.6f} {avg_s:>15.0f} {avg_ts:>15.6f}")
            ts_products.append(avg_ts)

        results.append({
            "bits": nbits,
            "method_avgs": {k: {"time": sum(v["times"])/len(v["times"]),
                                "space": sum(v["spaces"])/len(v["spaces"]),
                                "ts": sum(v["ts"])/len(v["ts"])}
                           for k, v in method_avgs.items()},
        })

    # Analyze T*S scaling
    print("\n  KEY FINDING: T*S product scaling across bit sizes")
    print("  " + "-" * 60)
    for method_name in ["pollard_rho", "bsgs", "bounded_rho_256"]:
        ts_by_bits = []
        for r in results:
            if method_name in r["method_avgs"]:
                ts_by_bits.append((r["bits"], r["method_avgs"][method_name]["ts"]))
        if len(ts_by_bits) >= 2:
            # Fit log(T*S) vs bits to get scaling exponent
            xs = [b for b, _ in ts_by_bits]
            ys = [math.log2(max(ts, 1e-20)) for _, ts in ts_by_bits]
            if len(xs) >= 2:
                slope, intercept = _linear_fit(xs, ys)
                print(f"    {method_name}: log2(T*S) ≈ {slope:.3f} * bits + {intercept:.1f}")

    return results


# ─── Helper functions ─────────────────────────────────────────────────────────

def _factor_timed(N):
    """Quick factor using trial division then Pollard rho."""
    # Small primes
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N % p == 0:
            return p
    return _pollard_rho(N)


def _trial_division(N):
    """Trial division up to sqrt(N)."""
    if N % 2 == 0:
        return 2
    d = mpz(3)
    while d * d <= N:
        if N % d == 0:
            return d
        d += 2
    return N


def _pollard_rho(N, max_iter=1000000):
    """Pollard rho with Brent's improvement."""
    if N % 2 == 0:
        return 2
    x = mpz(random.randint(2, int(N) - 1))
    y = x
    c = mpz(random.randint(1, int(N) - 1))
    d = mpz(1)
    while d == 1:
        x = (x * x + c) % N
        y = (y * y + c) % N
        y = (y * y + c) % N
        d = gcd(abs(x - y), N)
        if d == N:
            # Retry with different c
            c = mpz(random.randint(1, int(N) - 1))
            x = mpz(random.randint(2, int(N) - 1))
            y = x
            d = mpz(1)
    return d


def _bsgs_factor(N, table_size):
    """Baby-step giant-step factoring (bounded space)."""
    if N % 2 == 0:
        return 2
    # Try to find factor by looking for x^2 ≡ y^2 (mod N) using hash table
    # Simplified: just search for small factors with a hash table
    table = {}
    step = max(1, int(isqrt(isqrt(N))))
    for i in range(min(table_size, step)):
        val = (2 + i)
        if N % val == 0:
            return val
        table[val * val % N] = val

    # Giant steps
    giant = mpz(step)
    for j in range(min(table_size, step)):
        target = (giant * (j + 1)) % N
        if target in table:
            g = gcd(target - table[target], N)
            if 1 < g < N:
                return g
        if N % (2 + table_size + j) == 0:
            return 2 + table_size + j

    # Fallback to rho
    return _pollard_rho(N, max_iter=10000)


def _bounded_rho(N, table_size):
    """Pollard rho with bounded distinguished-point table."""
    if N % 2 == 0:
        return 2
    x = mpz(random.randint(2, int(N) - 1))
    c = mpz(random.randint(1, int(N) - 1))
    table = {}
    for i in range(max(100000, table_size * 100)):
        x = (x * x + c) % N
        # Distinguished point: low bits are zero
        mask = table_size - 1 if (table_size & (table_size - 1)) == 0 else table_size
        key = int(x) % (table_size * 4)
        if key < table_size:
            if key in table:
                g = gcd(x - table[key], N)
                if 1 < g < N:
                    return g
                # Collision with same value, update
            table[key] = x
            if len(table) > table_size:
                # Evict oldest (approximate LRU by removing random)
                table.pop(next(iter(table)))
    return _pollard_rho(N, max_iter=10000)


def _to_base_bytes(n, base):
    """Convert n to a byte string in the given base."""
    if n == 0:
        return bytes([0])
    digits = []
    while n > 0:
        digits.append(n % base)
        n //= base
    # Pack digits as bytes (works for base <= 256)
    return bytes(digits)


def _pearson(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 2:
        return 0
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    if sx == 0 or sy == 0:
        return 0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


def _linear_fit(xs, ys):
    """Simple linear regression. Returns (slope, intercept)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    ss_xx = sum((x - mx) ** 2 for x in xs)
    ss_xy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if ss_xx == 0:
        return 0, my
    slope = ss_xy / ss_xx
    intercept = my - slope * mx
    return slope, intercept


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: Run all experiments and collect results
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 72)
    print("  P vs NP Phase 4: Five Novel Approaches via Factoring")
    print("  " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 72)

    all_results = {}

    t_total = time.perf_counter()

    # Approach 1: Game Tree
    t0 = time.perf_counter()
    all_results["game_tree"] = game_tree_analysis()
    print(f"\n  [Approach 1 completed in {time.perf_counter() - t0:.1f}s]\n")

    # Approach 2: Kolmogorov Complexity
    t0 = time.perf_counter()
    all_results["kolmogorov"] = kolmogorov_analysis()
    print(f"\n  [Approach 2 completed in {time.perf_counter() - t0:.1f}s]\n")

    # Approach 3: Information Distance
    t0 = time.perf_counter()
    all_results["info_distance"] = information_distance_analysis()
    print(f"\n  [Approach 3 completed in {time.perf_counter() - t0:.1f}s]\n")

    # Approach 4: Compression
    t0 = time.perf_counter()
    all_results["compression"] = compression_factoring_analysis()
    print(f"\n  [Approach 4 completed in {time.perf_counter() - t0:.1f}s]\n")

    # Approach 5: Time-Space Tradeoff
    t0 = time.perf_counter()
    all_results["time_space"] = time_space_tradeoff()
    print(f"\n  [Approach 5 completed in {time.perf_counter() - t0:.1f}s]\n")

    total_time = time.perf_counter() - t_total
    print("=" * 72)
    print(f"  All experiments completed in {total_time:.1f}s")
    print("=" * 72)

    return all_results


if __name__ == "__main__":
    results = main()
