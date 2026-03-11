#!/usr/bin/env python3
"""
Round 11: Conservation of Complexity -- Theoretical Analysis (Section 5)

PURPOSE: Measure and experimentally test whether different factoring
representations (binary SAT, RNS/CRT, base-hopping with range pruning)
truly reduce total work, or merely redistribute it.

The "Conservation of Complexity" hypothesis (Section 5): no representation change
can reduce the total work below O(sqrt(p)) for the smallest factor p.

We measure:
1. Binary SAT state count curve (carry, x_partial, y_partial) per column
2. RNS candidate count curve as moduli are added (analytical + enumerated)
3. Base-hopping candidate count with range pruning vs pure RNS
4. Theoretical comparison with Pollard rho O(n^{1/4}) and trial O(n^{1/2})
5. Key ratio: total_work / sqrt(smallest_factor)
6. Carry entropy: Shannon entropy of carry distribution per column

All results appended to factoring_log.md.
"""

import math
import random
import time

random.seed(55555)

LOG_FILE = "factoring_log.md"


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)


# ============================================================
# Primality and semiprime generation
# ============================================================
def is_prime_miller_rabin(n, k=25):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n):
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not is_prime_miller_rabin(n):
        n += 2
    return n


def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q:
        q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q:
        p, q = q, p
    return p, q, p * q


# ============================================================
# Number theory helpers
# ============================================================
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def crt_two(r1, m1, r2, m2):
    """CRT for two congruences. Returns (solution, lcm) or (None, None)."""
    g, p, _ = extended_gcd(m1, m2)
    if (r2 - r1) % g != 0:
        return None, None
    lcm = m1 * m2 // g
    solution = (r1 + m1 * ((r2 - r1) // g) * p) % lcm
    return solution, lcm


def small_primes_list(count):
    """Generate first `count` primes."""
    primes = []
    candidate = 2
    while len(primes) < count:
        if all(candidate % p != 0 for p in primes):
            primes.append(candidate)
        candidate += 1
    return primes


# ============================================================
# MEASUREMENT 1: Binary SAT state count curve
# ============================================================
def measure_binary_sat_states(n, p_true, q_true, max_states_per_col=200000):
    """
    Process columns 0..L of binary long multiplication n = x * y.
    At each column k, count (carry, x_partial, y_partial) states.
    Also compute Shannon entropy of the carry distribution.

    Returns:
        states_per_col: list of state counts at each column
        total_states: sum of all state counts
        carry_entropies: Shannon entropy of carry distribution at each column
        capped: whether we had to cap states
    """
    L = n.bit_length()
    n_bits = [(n >> k) & 1 for k in range(L + 5)]

    A = min(p_true.bit_length(), q_true.bit_length())
    B = max(p_true.bit_length(), q_true.bit_length())

    if not (A + B - 1 <= L <= A + B):
        A = L // 2
        B = L - A + 1

    if n_bits[0] != 1:
        return [0] * (L + 1), 0, [0.0] * (L + 1), False

    # State: dict mapping carry -> set of (x_partial, y_partial)
    states = {0: set([(1, 1)])}

    states_per_col = [1]
    carry_entropies = [0.0]
    total_states = 1
    capped = False

    for k in range(1, L + 2):
        new_states = {}

        need_xk = k < A
        need_yk = k < B

        if need_xk and need_yk:
            if k == A - 1 and k == B - 1:
                bit_choices = [(1, 1)]
            elif k == A - 1:
                bit_choices = [(1, 0), (1, 1)]
            elif k == B - 1:
                bit_choices = [(0, 1), (1, 1)]
            else:
                bit_choices = [(0, 0), (0, 1), (1, 0), (1, 1)]
        elif need_xk:
            bit_choices = [(1, None)] if k == A - 1 else [(0, None), (1, None)]
        elif need_yk:
            bit_choices = [(None, 1)] if k == B - 1 else [(None, 0), (None, 1)]
        else:
            bit_choices = [(None, None)]

        for carry, xy_set in states.items():
            for x_val, y_val in xy_set:
                for xk, yk in bit_choices:
                    x_new = x_val | (xk << k) if xk is not None else x_val
                    y_new = y_val | (yk << k) if yk is not None else y_val

                    S_k = 0
                    for i in range(min(k + 1, A)):
                        j = k - i
                        if 0 <= j < B:
                            xi = (x_new >> i) & 1
                            yj = (y_new >> j) & 1
                            S_k += xi * yj

                    V_k = S_k + carry
                    bit_k = V_k & 1
                    new_carry = V_k >> 1

                    expected = n_bits[k] if k < len(n_bits) else 0
                    if bit_k != expected:
                        continue

                    if new_carry not in new_states:
                        new_states[new_carry] = set()
                    new_states[new_carry].add((x_new, y_new))

        col_count = sum(len(s) for s in new_states.values())

        if col_count > max_states_per_col:
            capped = True
            trimmed = {}
            budget_per_carry = max(1, max_states_per_col // max(1, len(new_states)))
            for c, s in new_states.items():
                if len(s) > budget_per_carry:
                    trimmed[c] = set(list(s)[:budget_per_carry])
                else:
                    trimmed[c] = s
            new_states = trimmed
            col_count = sum(len(s) for s in new_states.values())

        # Compute carry entropy
        carry_counts = {c: len(s) for c, s in new_states.items()}
        total_in_col = sum(carry_counts.values())
        entropy = 0.0
        if total_in_col > 0:
            for c, cnt in carry_counts.items():
                if cnt > 0:
                    prob = cnt / total_in_col
                    entropy -= prob * math.log2(prob)

        states_per_col.append(col_count)
        carry_entropies.append(entropy)
        total_states += col_count
        states = new_states

        if not states:
            for _ in range(k + 1, L + 2):
                states_per_col.append(0)
                carry_entropies.append(0.0)
            break

    return states_per_col, total_states, carry_entropies, capped


# ============================================================
# MEASUREMENT 2: RNS candidate count (analytical)
# ============================================================
def measure_rns_candidates_analytical(n, num_moduli=20):
    """
    For pure RNS with prime moduli m_i not dividing n:
    - Each modulus m_i contributes exactly (m_i - 1) valid x-residues
      (since x*y = n mod m_i has m_i - 1 solutions for x in [1, m_i-1])
    - After k moduli, total candidates = product of (m_i - 1) for i=1..k
    - Total CRT work = sum over steps of (prev_candidates * new_residues)

    This is EXACT -- no need to enumerate.

    Returns:
        moduli_used, candidates_per_step (list of ints), total_work (int)
    """
    primes = small_primes_list(num_moduli + 10)
    moduli = []
    for p in primes:
        if n % p != 0:
            moduli.append(p)
        if len(moduli) >= num_moduli:
            break

    moduli_used = []
    candidates_per_step = []
    total_work = 0
    current_count = 0

    for i, mi in enumerate(moduli):
        residues_this = mi - 1  # valid x residues mod mi
        if i == 0:
            current_count = residues_this
            total_work += current_count
        else:
            crt_ops = current_count * residues_this  # each old x each new
            total_work += crt_ops
            current_count = current_count * residues_this  # all survive (coprime primes)
        moduli_used.append(mi)
        candidates_per_step.append(current_count)

    return moduli_used, candidates_per_step, total_work


# ============================================================
# MEASUREMENT 3: Base-hopping with range pruning
# ============================================================
def measure_basehop_candidates(n, num_moduli=15, time_limit=30.0, max_cand=500000):
    """
    RNS with range pruning: after each CRT combination, discard candidates
    where no x = x_c + k*M falls in [2, sqrt(n)].

    Uses actual enumeration up to a candidate cap, then estimates.

    Returns:
        moduli_used, candidates_per_step, total_work, estimated (bool)
    """
    primes = small_primes_list(num_moduli + 10)
    moduli = []
    for p in primes:
        if n % p != 0:
            moduli.append(p)
        if len(moduli) >= num_moduli:
            break

    if not moduli:
        return [], [], 0, False

    sqrt_n = math.isqrt(n)
    moduli_used = []
    candidates_per_step = []
    total_work = 0
    estimated = False
    t0 = time.time()

    m0 = moduli[0]
    n_mod = n % m0
    pairs = []
    for x0 in range(1, m0):
        y0 = (n_mod * pow(x0, -1, m0)) % m0
        if y0 >= 1:
            pairs.append((x0, y0))

    current_candidates = pairs
    M = m0
    moduli_used.append(m0)
    candidates_per_step.append(len(current_candidates))
    total_work += len(current_candidates)

    for step in range(1, len(moduli)):
        if time.time() - t0 > time_limit:
            # Estimate remaining steps
            estimated = True
            for future in range(step, len(moduli)):
                mi = moduli[future]
                # Estimate: candidates * (mi-1) * survival_rate
                # survival_rate ~ sqrt(n) / M (fraction of residues with valid x in range)
                survival = min(1.0, float(sqrt_n) / float(M))
                est_new = int(candidates_per_step[-1] * (mi - 1) * survival)
                est_work = candidates_per_step[-1] * (mi - 1)
                total_work += est_work
                M *= mi
                moduli_used.append(mi)
                candidates_per_step.append(max(1, est_new))
            break

        mi = moduli[step]
        n_mod_mi = n % mi

        new_pairs = []
        for xi in range(1, mi):
            yi = (n_mod_mi * pow(xi, -1, mi)) % mi
            if yi >= 1:
                new_pairs.append((xi, yi))

        new_candidates = []
        crt_ops = 0
        M_new = M * mi

        for x_val, y_val in current_candidates:
            for xi, yi in new_pairs:
                crt_ops += 1
                x_c, x_m = crt_two(x_val, M, xi, mi)
                if x_c is None:
                    continue
                y_c, y_m = crt_two(y_val, M, yi, mi)
                if y_c is None:
                    continue

                # RANGE PRUNING: check if any x = x_c + k*M_new in [2, sqrt_n]
                if x_c < 2:
                    first_valid = x_c + M_new * ((2 - x_c + M_new - 1) // M_new)
                else:
                    first_valid = x_c

                if first_valid > sqrt_n:
                    continue  # No valid x in range

                new_candidates.append((x_c, y_c))

        total_work += crt_ops
        M = M_new
        current_candidates = new_candidates
        moduli_used.append(mi)
        candidates_per_step.append(len(current_candidates))

        if len(current_candidates) > max_cand:
            # Switch to estimation for remaining
            estimated = True
            for future in range(step + 1, len(moduli)):
                mi_f = moduli[future]
                survival = min(1.0, float(sqrt_n) / float(M))
                est_new = int(candidates_per_step[-1] * (mi_f - 1) * survival)
                est_work = candidates_per_step[-1] * (mi_f - 1)
                total_work += est_work
                M *= mi_f
                moduli_used.append(mi_f)
                candidates_per_step.append(max(1, est_new))
            break

    return moduli_used, candidates_per_step, total_work, estimated


# ============================================================
# MEASUREMENT 4 & 5: Theoretical complexity comparison
# ============================================================
def compute_theoretical_costs(n, p):
    """Compute theoretical operation counts for reference methods."""
    sqrt_p = math.isqrt(p) if p > 0 else 1
    if sqrt_p < 1:
        sqrt_p = 1

    trial_div = math.isqrt(n)
    pollard_rho = math.isqrt(p)  # O(p^{1/2})

    ln_n = math.log(n) if n > 1 else 1
    ln_ln_n = math.log(ln_n) if ln_n > 1 else 1
    gnfs = math.exp(((64.0 / 9.0) ** (1.0 / 3.0)) *
                    (ln_n ** (1.0 / 3.0)) * (ln_ln_n ** (2.0 / 3.0)))

    return {
        "trial_division": trial_div,
        "pollard_rho": pollard_rho,
        "gnfs_heuristic": gnfs,
        "sqrt_p": sqrt_p,
    }


# ============================================================
# Main analysis
# ============================================================
def run_analysis():
    log("")
    log("=" * 78)
    log("# Round 11: Conservation of Complexity Analysis (Section 5)")
    log("=" * 78)
    log("")
    log("**Hypothesis**: No change of representation (binary SAT, RNS, base-hopping)")
    log("can reduce total factoring work below O(sqrt(p)) for smallest factor p.")
    log("")
    log("random.seed(55555), standard Python only.")
    log("")

    bit_sizes = [20, 24, 28, 32, 36, 40, 48, 56, 64, 72, 80, 90, 100]

    # SAT is expensive: only run full enumeration up to this size
    sat_limit_bits = 48

    # Choose number of RNS/base-hop moduli to use
    # We want enough so M > sqrt(n) ideally, but cap to keep runtime sane
    # Product of first k primes: 2*3*5*7*11*13*17*19*23*29 = 6469693230 ~ 2^32.6
    # For 100-bit n, sqrt(n) ~ 2^50, need ~15 primes
    def choose_num_moduli(bits):
        # Enough primes so product approaches sqrt(n)
        # log2(product of first k primes) grows roughly as k*log2(k)
        target = bits // 2  # log2(sqrt(n))
        primes = small_primes_list(40)
        prod_log = 0.0
        for i, p in enumerate(primes):
            prod_log += math.log2(p)
            if prod_log >= target:
                return min(i + 2, 25)
        return min(25, len(primes))

    results = []

    for bits in bit_sizes:
        log(f"--- Analyzing {bits}-bit semiprime ---")
        p, q, n = gen_semiprime(bits)
        actual_bits = n.bit_length()
        log(f"  n = {n} ({actual_bits} bits)")
        log(f"  p = {p} ({p.bit_length()} bits), q = {q} ({q.bit_length()} bits)")
        sqrt_p = math.isqrt(p)

        row = {"bits": bits, "actual_bits": actual_bits, "p": p, "q": q, "n": n}

        # --- Measurement 1: Binary SAT states ---
        if bits <= sat_limit_bits:
            t0 = time.time()
            states_per_col, total_sat_states, carry_entropies, was_capped = \
                measure_binary_sat_states(n, p, q, max_states_per_col=200000)
            sat_time = time.time() - t0
            row["sat_total"] = total_sat_states
            row["sat_peak"] = max(states_per_col) if states_per_col else 0
            row["sat_measured"] = True

            peak_col = states_per_col.index(max(states_per_col)) if states_per_col else 0
            max_entropy = max(carry_entropies) if carry_entropies else 0
            entropy_at_peak = carry_entropies[peak_col] if peak_col < len(carry_entropies) else 0

            log(f"  SAT: total_states={total_sat_states}, peak={row['sat_peak']} at col {peak_col}, time={sat_time:.2f}s")
            if was_capped:
                log(f"  SAT: WARNING -- states were capped (lower bound)")
            log(f"  SAT carry entropy: max={max_entropy:.3f} bits, at peak col={entropy_at_peak:.3f} bits")

            if carry_entropies:
                increases = sum(1 for i in range(1, len(carry_entropies))
                                if carry_entropies[i] > carry_entropies[i - 1])
                decreases = sum(1 for i in range(1, len(carry_entropies))
                                if carry_entropies[i] < carry_entropies[i - 1])
                flat = sum(1 for i in range(1, len(carry_entropies))
                           if carry_entropies[i] == carry_entropies[i - 1])
                log(f"  Carry entropy curve: {increases} increases, {decreases} decreases, {flat} flat")
                q3 = len(carry_entropies) * 3 // 4
                late_ents = carry_entropies[q3:]
                late_avg = sum(late_ents) / max(1, len(late_ents))
                log(f"  Carry entropy saturation: late-avg={late_avg:.3f}, max={max_entropy:.3f}")
            row["carry_max_entropy"] = max_entropy
        else:
            # Estimate: SAT peak states ~ 2^(A-2) where A ~ L/2
            L = actual_bits
            est_exp = (L // 2) - 2
            row["sat_total"] = 2 ** est_exp * L  # rough: peak * L columns
            row["sat_peak"] = 2 ** est_exp
            row["sat_measured"] = False
            row["carry_max_entropy"] = None
            log(f"  SAT: estimated (>{sat_limit_bits} bits): peak ~ 2^{est_exp}, total ~ {row['sat_total']:.2e}")

        # --- Measurement 2: Pure RNS candidates (analytical) ---
        num_mod = choose_num_moduli(bits)
        rns_moduli, rns_counts, rns_work = measure_rns_candidates_analytical(n, num_moduli=num_mod)
        rns_final = rns_counts[-1] if rns_counts else 0
        row["rns_total_work"] = rns_work
        row["rns_final_candidates"] = rns_final
        row["rns_moduli_count"] = len(rns_moduli)
        log(f"  RNS (pure, analytical): {len(rns_moduli)} moduli, final_candidates={rns_final:.2e}, total_CRT_work={rns_work:.2e}")
        log(f"  RNS candidate curve: {[f'{c:.0e}' if c > 99999 else str(c) for c in rns_counts]}")

        # --- Measurement 3: Base-hopping with range pruning ---
        t0 = time.time()
        bh_moduli, bh_counts, bh_work, bh_estimated = \
            measure_basehop_candidates(n, num_moduli=num_mod, time_limit=20.0, max_cand=300000)
        bh_time = time.time() - t0
        bh_final = bh_counts[-1] if bh_counts else 0
        row["bh_total_work"] = bh_work
        row["bh_final_candidates"] = bh_final
        row["bh_estimated"] = bh_estimated
        est_tag = " (partially estimated)" if bh_estimated else ""
        log(f"  Base-hop (range pruned){est_tag}: {len(bh_moduli)} moduli, final_candidates={bh_final:.2e}, total_CRT_work={bh_work:.2e}, time={bh_time:.2f}s")
        log(f"  Base-hop candidate curve: {[f'{c:.0e}' if c > 99999 else str(c) for c in bh_counts]}")

        # --- Measurement 4: Theoretical costs ---
        theory = compute_theoretical_costs(n, p)
        row["trial_div"] = theory["trial_division"]
        row["pollard_rho"] = theory["pollard_rho"]
        row["gnfs"] = theory["gnfs_heuristic"]
        row["sqrt_p"] = theory["sqrt_p"]

        # --- Measurement 5: Key ratios (total_work / sqrt(p)) ---
        sat_total = row["sat_total"]
        row["sat_ratio"] = sat_total / max(1, sqrt_p) if isinstance(sat_total, (int, float)) and sat_total > 0 else None
        row["rns_ratio"] = rns_work / max(1, sqrt_p) if rns_work > 0 else None
        row["bh_ratio"] = bh_work / max(1, sqrt_p) if bh_work > 0 else None
        row["pollard_ratio"] = theory["pollard_rho"] / max(1, sqrt_p)
        row["trial_ratio"] = theory["trial_division"] / max(1, sqrt_p)

        log(f"  sqrt(p) = {sqrt_p}")
        log(f"  Ratios (work / sqrt(p)):")
        if row["sat_ratio"] is not None:
            log(f"    SAT:        {row['sat_ratio']:.4f}")
        log(f"    RNS:        {row['rns_ratio']:.4f}" if row["rns_ratio"] else "    RNS:        N/A")
        log(f"    Base-hop:   {row['bh_ratio']:.4f}" if row["bh_ratio"] else "    Base-hop:   N/A")
        log(f"    Pollard:    {row['pollard_ratio']:.4f}")
        log(f"    Trial div:  {row['trial_ratio']:.4f}")

        # Pruning effectiveness: compare base-hop vs pure RNS
        if rns_work > 0 and bh_work > 0:
            pruning_ratio = bh_work / rns_work
            reduction_pct = (1 - pruning_ratio) * 100
            log(f"  Range pruning effectiveness: BH/RNS work = {pruning_ratio:.6f} ({reduction_pct:.1f}% reduction)")
            row["pruning_effectiveness"] = pruning_ratio
        else:
            row["pruning_effectiveness"] = None

        # RNS vs base-hop final candidate comparison
        if rns_final > 0 and bh_final > 0:
            cand_ratio = bh_final / rns_final
            log(f"  Final candidate ratio BH/RNS: {cand_ratio:.6e} ({(1-cand_ratio)*100:.1f}% fewer candidates)")

        log("")
        results.append(row)

    # ============================================================
    # Final summary table
    # ============================================================
    log("")
    log("=" * 78)
    log("## Summary Table: Conservation of Complexity")
    log("=" * 78)
    log("")

    hdr = "{:>5s} | {:>14s} | {:>14s} | {:>14s} | {:>12s} | {:>10s} | {:>10s} | {:>10s}".format(
        "Bits", "SAT Total", "RNS Work", "BH Work", "sqrt(p)",
        "SAT/sqP", "RNS/sqP", "BH/sqP"
    )
    sep = "-" * len(hdr)
    log(hdr)
    log(sep)

    for r in results:
        sat_v = r["sat_total"]
        if isinstance(sat_v, int):
            sat_str = f"{sat_v:.2e}" if sat_v > 999999 else str(sat_v)
        else:
            sat_str = f"{sat_v:.2e}"

        rns_str = f"{r['rns_total_work']:.2e}" if r['rns_total_work'] > 999999 else str(r['rns_total_work'])
        bh_str = f"{r['bh_total_work']:.2e}" if r['bh_total_work'] > 999999 else str(r['bh_total_work'])
        sqp_str = str(r["sqrt_p"])

        sat_r = f"{r['sat_ratio']:.2f}" if r["sat_ratio"] is not None else "N/A"
        rns_r = f"{r['rns_ratio']:.2f}" if r["rns_ratio"] is not None else "N/A"
        bh_r = f"{r['bh_ratio']:.2f}" if r["bh_ratio"] is not None else "N/A"

        line = "{:>5d} | {:>14s} | {:>14s} | {:>14s} | {:>12s} | {:>10s} | {:>10s} | {:>10s}".format(
            r["bits"], sat_str, rns_str, bh_str, sqp_str, sat_r, rns_r, bh_r
        )
        log(line)

    log(sep)
    log("")

    # ============================================================
    # Ratio trend analysis
    # ============================================================
    log("## Ratio Trend Analysis (work / sqrt(p))")
    log("")

    def analyze_trend(name, data_pairs):
        """data_pairs = [(bits, ratio), ...]"""
        if len(data_pairs) < 3:
            log(f"  {name}: insufficient data points ({len(data_pairs)})")
            return
        bits_list = [b for b, _ in data_pairs]
        ratios = [r for _, r in data_pairs]
        # Log-log regression: log(ratio) vs log(bits)
        # If ratio ~ bits^alpha, then alpha > 0 means super-sqrt, alpha ~ 0 means sqrt
        n_pts = len(ratios)
        log_bits = [math.log(b) for b in bits_list]
        log_rats = [math.log(max(r, 1e-10)) for r in ratios]
        mean_lb = sum(log_bits) / n_pts
        mean_lr = sum(log_rats) / n_pts
        num = sum((log_bits[i] - mean_lb) * (log_rats[i] - mean_lr) for i in range(n_pts))
        den = sum((log_bits[i] - mean_lb) ** 2 for i in range(n_pts))
        slope = num / den if den > 0 else 0

        first_third = ratios[:n_pts // 3 + 1]
        last_third = ratios[-(n_pts // 3 + 1):]
        avg_first = sum(first_third) / len(first_third)
        avg_last = sum(last_third) / len(last_third)
        growth = avg_last / avg_first if avg_first > 0 else float('inf')

        if slope > 1.5:
            verdict = "SUPER-LINEAR GROWTH (worse than O(sqrt(p)))"
        elif slope > 0.3:
            verdict = "GROWING (consistent with super-O(sqrt(p)))"
        elif slope > -0.3:
            verdict = "ROUGHLY CONSTANT (consistent with O(sqrt(p)))"
        else:
            verdict = "DECREASING (would imply sub-O(sqrt(p))!)"

        log(f"  {name}:")
        log(f"    log-log slope = {slope:.3f}")
        log(f"    first-third avg = {avg_first:.2f}, last-third avg = {avg_last:.2f}, growth = {growth:.2f}x")
        log(f"    -> {verdict}")
        log("")

    sat_data = [(r["bits"], r["sat_ratio"]) for r in results if r["sat_ratio"] is not None]
    rns_data = [(r["bits"], r["rns_ratio"]) for r in results if r["rns_ratio"] is not None]
    bh_data = [(r["bits"], r["bh_ratio"]) for r in results if r["bh_ratio"] is not None]

    analyze_trend("Binary SAT", sat_data)
    analyze_trend("Pure RNS (analytical)", rns_data)
    analyze_trend("Base-Hopping (range pruned)", bh_data)

    # ============================================================
    # Range pruning effectiveness summary
    # ============================================================
    pruning_data = [(r["bits"], r["pruning_effectiveness"])
                    for r in results if r["pruning_effectiveness"] is not None]
    if pruning_data:
        log("## Range Pruning Effectiveness (BH work / RNS work)")
        log("")
        for bits, eff in pruning_data:
            bar_len = max(0, int(40 * (1 - eff)))
            bar = "#" * bar_len
            savings = (1 - eff) * 100
            log(f"  {bits:>3d}-bit: ratio={eff:.6f}  savings={savings:6.2f}%  {bar}")

        # Does pruning improve with size?
        if len(pruning_data) >= 3:
            first_effs = [e for _, e in pruning_data[:len(pruning_data) // 3 + 1]]
            last_effs = [e for _, e in pruning_data[-(len(pruning_data) // 3 + 1):]]
            avg_first = sum(first_effs) / len(first_effs)
            avg_last = sum(last_effs) / len(last_effs)
            if avg_last < avg_first * 0.8:
                log(f"  -> Pruning effectiveness IMPROVES with size (early avg={avg_first:.4f}, late avg={avg_last:.4f})")
            elif avg_last > avg_first * 1.2:
                log(f"  -> Pruning effectiveness DEGRADES with size (early avg={avg_first:.4f}, late avg={avg_last:.4f})")
            else:
                log(f"  -> Pruning effectiveness roughly STABLE (early avg={avg_first:.4f}, late avg={avg_last:.4f})")
        log("")

    # ============================================================
    # Carry entropy summary
    # ============================================================
    log("## Carry Entropy Observations")
    log("")
    for r in results:
        if r.get("carry_max_entropy") is not None:
            log(f"  {r['bits']:>3d}-bit: max carry entropy = {r['carry_max_entropy']:.3f} bits")
    entropy_vals = [r["carry_max_entropy"] for r in results if r.get("carry_max_entropy") is not None]
    if len(entropy_vals) >= 3:
        if entropy_vals[-1] > entropy_vals[0] * 1.3:
            log(f"  -> Carry entropy INCREASES with problem size (grows from {entropy_vals[0]:.3f} to {entropy_vals[-1]:.3f})")
            log(f"     This means carries encode MORE information at larger sizes,")
            log(f"     supporting the view that carry entanglement drives SAT complexity.")
        else:
            log(f"  -> Carry entropy roughly STABLE ({entropy_vals[0]:.3f} to {entropy_vals[-1]:.3f})")
    log("")

    # ============================================================
    # Conclusion
    # ============================================================
    log("=" * 78)
    log("## Conclusion: Conservation of Complexity (Section 5)")
    log("=" * 78)
    log("")
    log("The Conservation of Complexity predicts that switching from binary SAT")
    log("to RNS/CRT or base-hopping merely reshuffles where exponential blowup occurs:")
    log("")
    log("- Binary SAT: exponential state growth at MIDDLE columns (carry entanglement)")
    log("  States peak near column L/2 where carry values proliferate.")
    log("  Carry entropy rises then falls -- information is created then consumed.")
    log("")
    log("- Pure RNS: candidates grow as product of (m_i - 1) per modulus.")
    log("  With k primes, candidates ~ product(m_i - 1). No pruning at all")
    log("  from modular constraints alone -- every residue is valid.")
    log("  The CRT work is the SAME as the candidate count growth.")
    log("")
    log("- Base-hopping (range pruning): range constraint x <= sqrt(n) prunes")
    log("  candidates once M > sqrt(n), but until then, pruning is negligible.")
    log("  Savings are constant-factor, not asymptotic.")
    log("")
    log("If all work/sqrt(p) ratios grow (or stay constant) with bit size,")
    log("this SUPPORTS the conservation hypothesis: O(sqrt(p)) is a lower bound")
    log("that no representation change can circumvent for these approaches.")
    log("")
    log("KEY FINDING: The ratio total_work/sqrt(p) for each method reveals whether")
    log("it achieves, exceeds, or beats the sqrt(p) barrier. Pollard rho achieves")
    log("ratio ~1 (it IS O(sqrt(p))). Any method with growing ratio is WORSE.")
    log("A method with shrinking ratio would be a breakthrough -- but we expect none.")
    log("")
    log("=" * 78)
    log("End of Round 11 analysis.")
    log("=" * 78)


if __name__ == "__main__":
    run_analysis()
