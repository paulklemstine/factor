#!/usr/bin/env python3
"""
CFRAC (Continued Fraction) Factoring Engine — Optimized v3
==========================================================
Uses the continued fraction expansion of sqrt(kN) to find smooth residues,
then GF(2) Gaussian elimination to combine them into x^2 = y^2 (mod N).

Key optimizations:
  1. C extension (cfrac_sieve_c.so) for CF recurrence + trial division inner loop
  2. Single Large Prime (SLP) variation with proper combining
  3. Double Large Prime (DLP) with graph-based cycle detection (union-find)
  4. Pollard rho for DLP cofactor splitting
  5. Knuth-Schroeppel multiplier selection
  6. Tuned parameter selection (alpha, LP bound)

Compile C extension:
  gcc -O3 -shared -fPIC -o cfrac_sieve_c.so cfrac_sieve_c.c -lgmp -lm
"""

import time
import math
import os
import ctypes
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre, iroot
from collections import defaultdict

# ---------------------------------------------------------------------------
# C extension loading
# ---------------------------------------------------------------------------

_c_lib = None

def _load_c_extension():
    global _c_lib
    if _c_lib is not None:
        return _c_lib
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cfrac_sieve_c.so')
    if os.path.exists(so_path):
        try:
            _c_lib = ctypes.CDLL(so_path)
            # Set up function signatures
            _c_lib.cfrac_init.argtypes = [ctypes.c_char_p]
            _c_lib.cfrac_init.restype = None
            _c_lib.cfrac_set_fb.argtypes = [
                ctypes.POINTER(ctypes.c_ulong), ctypes.c_int, ctypes.c_ulong
            ]
            _c_lib.cfrac_set_fb.restype = None
            _c_lib.cfrac_batch.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_int),   # out_step
                ctypes.POINTER(ctypes.c_int),   # out_sign
                ctypes.c_char_p, ctypes.c_int,  # out_cofactor_buf, size
                ctypes.POINTER(ctypes.c_int),   # out_exps
                ctypes.c_char_p, ctypes.c_int,  # out_pmod_buf, size
            ]
            _c_lib.cfrac_batch.restype = ctypes.c_int
            _c_lib.cfrac_get_step.argtypes = []
            _c_lib.cfrac_get_step.restype = ctypes.c_int
            _c_lib.cfrac_cleanup.argtypes = []
            _c_lib.cfrac_cleanup.restype = None
            return _c_lib
        except Exception as e:
            print(f"  Warning: C extension load failed: {e}")
            _c_lib = None
    return None

# ---------------------------------------------------------------------------
# Smoothness bound selection
# ---------------------------------------------------------------------------

def _smoothness_bound(N):
    """
    Choose smoothness bound B ~ L(N)^alpha.
    With C extension, we can handle larger FB since trial division is fast.
    """
    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    nd = len(str(N))
    # Lower alpha = smaller FB = fewer relations needed
    # With C extension doing fast trial division, we can afford slightly
    # larger FB for better smoothness yield. But the sweet spot is still
    # relatively low because LP combining is the main relation source.
    if nd <= 25:
        alpha = 0.36
    elif nd <= 35:
        alpha = 0.38
    elif nd <= 40:
        alpha = 0.40
    elif nd <= 45:
        alpha = 0.41
    elif nd <= 50:
        alpha = 0.42
    elif nd <= 55:
        alpha = 0.42
    elif nd <= 60:
        alpha = 0.42
    elif nd <= 65:
        alpha = 0.43
    elif nd <= 75:
        alpha = 0.44
    elif nd <= 85:
        alpha = 0.45
    elif nd <= 95:
        alpha = 0.46
    else:
        alpha = 0.47
    B = int(math.exp(alpha * L_exp))
    B = max(B, 50)
    B = min(B, 3_000_000)
    return B


def _build_factor_base(N, B):
    """Build factor base: {2} union {odd primes p <= B where Legendre(N,p) >= 0}."""
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


# ---------------------------------------------------------------------------
# Fast Pollard rho for DLP cofactor splitting
# ---------------------------------------------------------------------------

def _pollard_rho_small(n):
    """Pollard rho for splitting small composites. Returns a factor or 0."""
    if n < 4:
        return 0
    if n % 2 == 0:
        return 2
    for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
              61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113):
        if n % p == 0:
            return p
    n_mpz = mpz(n)
    for c in range(1, 20):
        x = mpz(2)
        y = mpz(2)
        d = mpz(1)
        product = mpz(1)
        count = 0
        while d == 1:
            x = (x * x + c) % n_mpz
            y = (y * y + c) % n_mpz
            y = (y * y + c) % n_mpz
            product = product * abs(x - y) % n_mpz
            count += 1
            if count % 40 == 0:
                d = gcd(product, n_mpz)
                product = mpz(1)
                if count > 6000:
                    break
        if d == 0 or d == 1:
            d = gcd(product, n_mpz)
        if 1 < d < n_mpz:
            return int(d)
    return 0


# ---------------------------------------------------------------------------
# DLP Graph — union-find with path-based cycle combining
# ---------------------------------------------------------------------------

class DLPGraph:
    """
    Graph-based DLP combining using union-find + spanning tree.
    Each DLP partial (cofactor = lp1 * lp2) is an edge.
    When adding an edge creates a cycle, combine all relations on the cycle path.

    IMPORTANT: We do NOT use path compression in find(), because we need the
    tree structure intact for path-to-root queries when combining cycles.
    """
    def __init__(self):
        self.parent = {}
        self.rank = {}
        self.edge_to_parent = {}  # node -> (p_mod, sign, exps) on edge to parent
        self.n_combined = 0
        self.n_edges = 0

    def _find(self, x):
        """Find root WITHOUT path compression (need tree structure)."""
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def _path_to_root(self, x):
        """Get path from x to root."""
        path = [x]
        while self.parent.get(x, x) != x:
            x = self.parent[x]
            path.append(x)
        return path

    def add_and_try_combine(self, lp1, lp2, p_mod, sign, exps, fb_size, mod_N):
        """Add edge and try to combine via cycle. Returns relation or None."""
        self.n_edges += 1
        r1 = self._find(lp1)
        r2 = self._find(lp2)

        if r1 == r2:
            # Cycle! Find paths and combine
            path1 = self._path_to_root(lp1)
            path2 = self._path_to_root(lp2)

            set1 = set(path1)
            lca = None
            lca_idx2 = 0
            for i, node in enumerate(path2):
                if node in set1:
                    lca = node
                    lca_idx2 = i
                    break

            if lca is None:
                return None

            lca_idx1 = path1.index(lca)

            # Collect relations on the cycle
            cycle_rels = []
            for node in path1[:lca_idx1]:
                if node in self.edge_to_parent:
                    cycle_rels.append(self.edge_to_parent[node])
            for node in path2[:lca_idx2]:
                if node in self.edge_to_parent:
                    cycle_rels.append(self.edge_to_parent[node])
            cycle_rels.append((p_mod, sign, exps))

            if len(cycle_rels) < 2:
                return None

            # Combine
            c_p = 1
            c_sign = 0
            c_exps = [0] * fb_size
            for rel_p, rel_s, rel_e in cycle_rels:
                c_p = (c_p * rel_p) % mod_N
                c_sign = (c_sign + rel_s) % 2
                for j in range(fb_size):
                    c_exps[j] += rel_e[j]

            # All LPs on cycle have even exponent (appear in exactly 2 edges)
            # Compute product of unique LPs for sqrt
            cycle_nodes = set()
            for node in path1[:lca_idx1]:
                cycle_nodes.add(node)
            for node in path2[:lca_idx2]:
                cycle_nodes.add(node)
            cycle_nodes.add(lp1)
            cycle_nodes.add(lp2)
            # Include lca if it has edges on the cycle
            lp_product = 1
            for lp in cycle_nodes:
                lp_product = (lp_product * lp) % mod_N

            self.n_combined += 1
            return (c_p, c_sign, c_exps, lp_product)
        else:
            # Union
            if self.rank.get(r1, 0) < self.rank.get(r2, 0):
                r1, r2 = r2, r1
                lp1, lp2 = lp2, lp1
            self.parent[r2] = r1
            if self.rank.get(r1, 0) == self.rank.get(r2, 0):
                self.rank[r1] = self.rank.get(r1, 0) + 1
            self.edge_to_parent[lp2] = (p_mod, sign, exps)
            return None


# ---------------------------------------------------------------------------
# Trial division (Python fallback)
# ---------------------------------------------------------------------------

def _trial_divide_fast(r_abs, fb, fb_size, fb_mpz):
    """Trial divide r_abs by FB primes. Returns (exps, cofactor)."""
    exps = [0] * fb_size
    cof = mpz(r_abs)
    for i in range(fb_size):
        p = fb_mpz[i]
        if p * p > cof:
            break
        if gmpy2.is_divisible(cof, p):
            e = 0
            while gmpy2.is_divisible(cof, p):
                cof = cof // p
                e += 1
            exps[i] = e
            if cof == 1:
                return exps, 1
    cof_int = int(cof)
    if cof_int > 1 and cof_int <= fb[-1]:
        lo, hi = 0, fb_size - 1
        while lo <= hi:
            mid = (lo + hi) >> 1
            if fb[mid] == cof_int:
                exps[mid] += 1
                return exps, 1
            elif fb[mid] < cof_int:
                lo = mid + 1
            else:
                hi = mid - 1
    return exps, cof_int


# ---------------------------------------------------------------------------
# Core CFRAC with C extension
# ---------------------------------------------------------------------------

def cfrac_factor_c(N, verbose=True, time_limit=3600, original_N=None):
    """
    Factor N using CFRAC with C extension for the inner loop.
    Falls back to Python if C extension unavailable.
    """
    c_lib = _load_c_extension()
    if c_lib is None:
        return cfrac_factor(N, verbose=verbose, time_limit=time_limit, original_N=original_N)

    N = mpz(N)
    nd = len(str(N))
    if original_N is not None:
        orig_N = mpz(original_N)
    else:
        orig_N = N

    if N <= 1: return 0
    if N % 2 == 0: return 2
    if N % 3 == 0: return 3
    for exp in range(2, int(gmpy2.log2(N)) + 1):
        root, exact = iroot(N, exp)
        if exact: return int(root)
    if is_prime(N): return int(N)
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    t0 = time.time()

    B = _smoothness_bound(N)
    fb = _build_factor_base(N, B)
    fb_size = len(fb)
    needed = fb_size + 1 + max(40, fb_size // 5)

    lp_bound = B * B
    dlp_cofactor_bound = min(lp_bound * lp_bound, (1 << 62))

    if verbose:
        print(f"CFRAC(C): {nd}d ({int(gmpy2.log2(N))+1}b), B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}, LP<={lp_bound:,}")

    # Initialize C extension
    N_str = str(int(N)).encode('ascii')
    c_lib.cfrac_init(N_str)

    fb_arr = (ctypes.c_ulong * fb_size)(*fb)
    c_lib.cfrac_set_fb(fb_arr, fb_size, lp_bound)

    # Allocate output buffers
    batch_size = 50000
    max_results = 100000
    out_step = (ctypes.c_int * max_results)()
    out_sign = (ctypes.c_int * max_results)()
    # Cofactor buffer: each cofactor is at most ~20 digits + null
    cof_buf_size = max_results * 25
    out_cof_buf = ctypes.create_string_buffer(cof_buf_size)
    # Exponent buffer: fb_size ints per result
    out_exps = (ctypes.c_int * (max_results * fb_size))()
    # p_mod buffer: each p_mod is at most nd+5 digits + null
    pmod_buf_size = max_results * (nd + 10)
    out_pmod_buf = ctypes.create_string_buffer(pmod_buf_size)

    smooth = []
    partials = {}
    n_lp_combined = 0
    dlp_graph = DLPGraph()
    N_int = int(N)

    total_k = 0
    report_interval = 200000
    last_report_k = 0

    while len(smooth) < needed:
        if time.time() - t0 > time_limit:
            if verbose:
                print(f"\n  Time limit ({time_limit}s) at k={total_k:,}")
            break

        # Call C batch
        n_results = c_lib.cfrac_batch(
            batch_size, out_step, out_sign,
            out_cof_buf, cof_buf_size,
            out_exps, out_pmod_buf, pmod_buf_size
        )
        total_k += batch_size

        if n_results == 0:
            continue

        # Parse results — split null-terminated strings from buffers
        cof_raw = bytes(out_cof_buf)
        pmod_raw = bytes(out_pmod_buf)

        # Split by null bytes, take first n_results entries
        cof_parts = cof_raw.split(b'\x00')
        pmod_parts = pmod_raw.split(b'\x00')

        for ri in range(n_results):
            if len(smooth) >= needed:
                break

            step_idx = out_step[ri]
            sign = out_sign[ri]

            cof_str = cof_parts[ri].decode('ascii') if ri < len(cof_parts) else ''
            cofactor = int(cof_str) if cof_str else 0

            pmod_str = pmod_parts[ri].decode('ascii') if ri < len(pmod_parts) else ''
            p_mod_val = int(pmod_str) if pmod_str else 0

            # Extract exponent vector
            exps = [out_exps[ri * fb_size + j] for j in range(fb_size)]

            if cofactor == 1:
                # Fully smooth
                smooth.append((p_mod_val, sign, exps, 0))
            elif cofactor <= lp_bound:
                # SLP candidate
                if cofactor > 1 and cofactor < (1 << 62) and is_prime(mpz(cofactor)):
                    lp = cofactor
                    if lp in partials:
                        p2_mod, sign2, exps2 = partials.pop(lp)
                        c_p = (p_mod_val * p2_mod) % N_int
                        c_sign = (sign + sign2) % 2
                        c_exps = [exps[j] + exps2[j] for j in range(fb_size)]
                        smooth.append((c_p, c_sign, c_exps, lp))
                        n_lp_combined += 1
                    else:
                        partials[lp] = (p_mod_val, sign, exps)
            elif cofactor <= dlp_cofactor_bound and cofactor > 1 and cofactor < (1 << 62):
                # DLP candidate
                if not is_prime(mpz(cofactor)):
                    f1 = _pollard_rho_small(cofactor)
                    if f1 > 0 and f1 != cofactor:
                        f2 = cofactor // f1
                        if f1 > f2:
                            f1, f2 = f2, f1
                        if f1 <= lp_bound and f2 <= lp_bound:
                            result = dlp_graph.add_and_try_combine(
                                f1, f2, p_mod_val, sign, exps, fb_size, N_int)
                            if result:
                                smooth.append(result)

        # Progress report
        if verbose and total_k - last_report_k >= report_interval:
            last_report_k = total_k
            elapsed = time.time() - t0
            rate = total_k / elapsed if elapsed > 0 else 0
            if len(smooth) > 0:
                eta = elapsed * (needed - len(smooth)) / len(smooth)
            else:
                eta = 99999
            print(f"  k={total_k:>12,}  smooth={len(smooth):,}/{needed:,}  "
                  f"LP={n_lp_combined:,}  DLP={dlp_graph.n_combined:,}  "
                  f"partials={len(partials):,}  "
                  f"rate={rate:,.0f}/s  eta={min(eta,99999):.0f}s")
            if total_k >= 500000 and len(smooth) < needed * 0.002:
                if verbose:
                    print(f"  Early abort: yield too low ({len(smooth)}/{needed})")
                break

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"  Sieve done: {len(smooth):,} rels in {elapsed_sieve:.1f}s "
              f"({total_k:,} CF terms, {n_lp_combined} LP, {dlp_graph.n_combined} DLP)")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    # Run LA and factor extraction (shared code)
    return _la_and_extract(smooth, fb, fb_size, N, orig_N, t0, total_k, verbose)


# ---------------------------------------------------------------------------
# Core CFRAC (Python fallback)
# ---------------------------------------------------------------------------

def cfrac_factor(N, verbose=True, time_limit=3600, original_N=None):
    """Factor N using CFRAC — pure Python version."""
    N = mpz(N)
    nd = len(str(N))
    if original_N is not None:
        orig_N = mpz(original_N)
    else:
        orig_N = N

    if N <= 1: return 0
    if N % 2 == 0: return 2
    if N % 3 == 0: return 3
    for exp in range(2, int(gmpy2.log2(N)) + 1):
        root, exact = iroot(N, exp)
        if exact: return int(root)
    if is_prime(N): return int(N)
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    t0 = time.time()

    B = _smoothness_bound(N)
    fb = _build_factor_base(N, B)
    fb_size = len(fb)
    needed = fb_size + 1 + max(40, fb_size // 5)
    lp_bound = B * B
    dlp_cofactor_bound = min(lp_bound * lp_bound, 1 << 62)

    if verbose:
        print(f"CFRAC: {nd}d ({int(gmpy2.log2(N))+1}b), B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}, LP<={lp_bound:,}")

    fb_set = set(fb)
    fb_mpz = [mpz(p) for p in fb]

    a0 = isqrt(N)
    m_k = mpz(0)
    d_k = mpz(1)
    a_k = a0
    p_prev2_mod = mpz(1)
    p_prev1_mod = a0 % N

    smooth = []
    partials = {}
    n_lp_combined = 0
    dlp_graph = DLPGraph()
    N_int = int(N)

    k = 0
    report_interval = 100000
    last_report_k = 0

    while len(smooth) < needed:
        if k % 10000 == 0 and k > 0:
            if time.time() - t0 > time_limit:
                if verbose:
                    print(f"\n  Time limit ({time_limit}s) at k={k:,}")
                break

        m_next = d_k * a_k - m_k
        d_next = (N - m_next * m_next) // d_k
        if d_next == 0:
            break
        a_next = (a0 + m_next) // d_next
        p_new_mod = (a_next * p_prev1_mod + p_prev2_mod) % N

        r_abs = int(d_next)
        sign = 1 if (k % 2 == 0) else 0

        if r_abs > 0:
            exps, cofactor = _trial_divide_fast(r_abs, fb, fb_size, fb_mpz)

            if cofactor == 1:
                smooth.append((int(p_prev1_mod), sign, exps, 0))
            elif cofactor <= lp_bound:
                if cofactor < (1 << 62) and is_prime(mpz(cofactor)):
                    lp = cofactor
                    if lp in partials:
                        p2_mod, sign2, exps2 = partials.pop(lp)
                        c_p = (int(p_prev1_mod) * p2_mod) % N_int
                        c_sign = (sign + sign2) % 2
                        c_exps = [exps[j] + exps2[j] for j in range(fb_size)]
                        smooth.append((c_p, c_sign, c_exps, lp))
                        n_lp_combined += 1
                    else:
                        partials[lp] = (int(p_prev1_mod), sign, exps)
            elif cofactor <= dlp_cofactor_bound and cofactor > 1 and cofactor < (1 << 62):
                if not is_prime(mpz(cofactor)):
                    f1 = _pollard_rho_small(cofactor)
                    if f1 > 0 and f1 != cofactor:
                        f2 = cofactor // f1
                        if f1 > f2:
                            f1, f2 = f2, f1
                        if f1 <= lp_bound and f2 <= lp_bound:
                            result = dlp_graph.add_and_try_combine(
                                f1, f2, int(p_prev1_mod), sign, exps, fb_size, N_int)
                            if result:
                                smooth.append(result)

        m_k = m_next
        d_k = d_next
        a_k = a_next
        p_prev2_mod = p_prev1_mod
        p_prev1_mod = p_new_mod
        k += 1

        if verbose and k - last_report_k >= report_interval:
            last_report_k = k
            elapsed = time.time() - t0
            rate = k / elapsed if elapsed > 0 else 0
            if len(smooth) > 0:
                eta = elapsed * (needed - len(smooth)) / len(smooth)
            else:
                eta = 99999
            print(f"  k={k:>12,}  smooth={len(smooth):,}/{needed:,}  "
                  f"LP={n_lp_combined:,}  DLP={dlp_graph.n_combined:,}  "
                  f"partials={len(partials):,}  "
                  f"rate={rate:,.0f}/s  eta={min(eta,99999):.0f}s")
            if k >= 500000 and len(smooth) < needed * 0.002:
                if verbose:
                    print(f"  Early abort: yield too low ({len(smooth)}/{needed})")
                break

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"  Sieve done: {len(smooth):,} rels in {elapsed_sieve:.1f}s "
              f"({k:,} CF terms, {n_lp_combined} LP, {dlp_graph.n_combined} DLP)")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    return _la_and_extract(smooth, fb, fb_size, N, orig_N, t0, k, verbose)


# ---------------------------------------------------------------------------
# Linear Algebra + Factor Extraction (shared)
# ---------------------------------------------------------------------------

def _la_and_extract(smooth, fb, fb_size, N, orig_N, t0, k, verbose):
    """GF(2) Gaussian elimination + factor extraction."""
    la_t0 = time.time()
    nrows = len(smooth)
    ncols = fb_size + 1

    if verbose:
        print(f"  LA: {nrows} x {ncols} matrix...")

    # Build GF(2) matrix
    mat = [0] * nrows
    for i in range(nrows):
        _, s, exps, _ = smooth[i]
        row = s
        for j in range(fb_size):
            if exps[j] & 1:
                row |= (1 << (j + 1))
        mat[i] = row

    # Gaussian elimination
    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows

    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        piv_row = mat[piv]
        piv_combo = combo[piv]
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= piv_row
                combo[row] ^= piv_combo

    # Extract null space
    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []
            bits = combo[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if indices:
                null_vecs.append(indices)

    la_time = time.time() - la_t0
    if verbose:
        print(f"  LA: {la_time:.1f}s, {len(null_vecs)} null vecs")

    # Factor extraction
    orig_nd = len(str(orig_N))
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        for idx in indices:
            p_mod, s, exps, lp_val = smooth[idx]
            x_val = x_val * mpz(p_mod) % N
            total_sign += s
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % N

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        y_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        for diff in (x_val - y_val, x_val + y_val):
            g = gcd(diff % N, N)
            if g <= 1 or g >= N:
                continue
            g2 = gcd(g, orig_N)
            if 1 < g2 < orig_N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g2} ({orig_nd}d, {total_t:.1f}s, "
                          f"k={k:,}, {len(smooth)} rels) ***")
                return int(g2)
            cof = N // g
            g3 = gcd(cof, orig_N)
            if 1 < g3 < orig_N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g3} ({orig_nd}d, {total_t:.1f}s, "
                          f"k={k:,}, {len(smooth)} rels) ***")
                return int(g3)

    if verbose:
        print(f"  Tried {len(null_vecs)} null vecs, no factor found.")
    return 0


# ---------------------------------------------------------------------------
# Multiplier selection
# ---------------------------------------------------------------------------

def _select_top_multipliers(N, count=8):
    """Return top multipliers ranked by Knuth-Schroeppel score."""
    candidates = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21,
                  23, 26, 29, 30, 31, 33, 34, 37, 38, 41, 42, 43,
                  46, 47, 51, 53, 55, 57, 58, 59, 61, 62, 65, 66, 67]
    scored = []
    for k in candidates:
        kN = N * k
        sq = isqrt(kN)
        if sq * sq == kN:
            continue
        score = -math.log(k) / 2.0
        kN_mod8 = int(kN % 8)
        if kN_mod8 == 1:
            score += 2.0 * math.log(2.0)
        elif kN_mod8 == 5:
            score += math.log(2.0)
        elif kN_mod8 == 0:
            score += math.log(2.0) * 0.5
        p = mpz(3)
        for _ in range(80):
            pf = float(p)
            leg = legendre(kN, p)
            if leg == 1:
                score += 2.0 * math.log(pf) / (pf - 1.0)
            elif leg == 0:
                score += math.log(pf) / pf
            p = next_prime(p)
        scored.append((score, k))
    scored.sort(reverse=True)
    return [k for _, k in scored[:count]]


# ---------------------------------------------------------------------------
# Multiplier-enhanced entry point
# ---------------------------------------------------------------------------

def cfrac_factor_with_multiplier(N, verbose=True, time_limit=3600):
    """Try CFRAC with Knuth-Schroeppel multipliers sequentially."""
    N = mpz(N)

    if N <= 1: return 0
    if N % 2 == 0: return 2
    if N % 3 == 0: return 3
    for exp in range(2, int(gmpy2.log2(N)) + 1):
        root, exact = iroot(N, exp)
        if exact: return int(root)
    if is_prime(N): return int(N)
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    # Check if C extension is available
    c_available = _load_c_extension() is not None
    factor_fn = cfrac_factor_c if c_available else cfrac_factor

    top_ks = _select_top_multipliers(N, count=12)
    # Always try k=1 first — it produces the most fully-smooth relations
    # and factor extraction is most reliable when gcd is against N directly
    if 1 in top_ks:
        top_ks.remove(1)
    top_ks.insert(0, 1)

    if verbose:
        mode = "C" if c_available else "Python"
        print(f"CFRAC multipliers ({mode}): k={top_ks}")

    t_start = time.time()
    for ki, k in enumerate(top_ks):
        remaining = time_limit - (time.time() - t_start)
        if remaining < 5:
            break
        if ki == 0:
            alloc = remaining * 0.7
        else:
            alloc = remaining / max(1, len(top_ks) - ki)

        kN = N * k
        sq_kN = isqrt(kN)
        if sq_kN * sq_kN == kN:
            continue

        if verbose and ki > 0:
            print(f"\n  Trying k={k} ({remaining:.0f}s remaining)...")
        elif verbose:
            print(f"CFRAC multiplier: k={k}")

        result = factor_fn(int(kN), verbose=verbose, time_limit=alloc,
                           original_N=int(N))
        if result and result > 1 and int(N) % result == 0:
            return result

    return 0


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def factor(N, verbose=True, time_limit=3600):
    """Main entry point: multiplier-enhanced CFRAC."""
    return cfrac_factor_with_multiplier(N, verbose=verbose, time_limit=time_limit)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("CFRAC Engine -- Self-Test")
    print("=" * 70)

    semiprimes = [
        ("20d", mpz("1000000007") * mpz("1000000009"), 30),
        ("30d", mpz("1000000007") * mpz("100000000000000003"), 30),
        ("35d", mpz("10000000000000061") * mpz("1000000000000000003"), 60),
        ("40d", mpz("10000000000000000051") * mpz("10000000000000000087"), 120),
        ("45d", mpz("100000000000000000267") * mpz("10000000000000000000000069"), 300),
        ("50d", mpz("100000000000000000151") * mpz("1000000000000000000117"), 600),
    ]

    results = []
    for label, n, limit in semiprimes:
        nd = len(str(n))
        print(f"\n{'='*70}")
        print(f"Test: {label} ({nd} actual digits)")
        print(f"N = {n}")
        t0 = time.time()
        f = factor(int(n), verbose=True, time_limit=limit)
        elapsed = time.time() - t0
        if f and f > 1 and int(n) % f == 0:
            print(f"  SUCCESS: {f} x {n // f}  ({elapsed:.1f}s)")
            results.append((label, nd, elapsed, True))
        else:
            print(f"  FAILED ({elapsed:.1f}s)")
            results.append((label, nd, elapsed, False))

    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  {'Label':>6}  {'Digits':>6}  {'Time':>8}  {'Result':>8}")
    for label, nd, t, ok in results:
        print(f"  {label:>6}  {nd:>5}d  {t:>7.1f}s  {'OK' if ok else 'FAIL':>8}")
