/*
 * gnfs_lattice_sieve_c.c — Production-quality special-q lattice sieve for GNFS
 *
 * Implements the full lattice sieve pipeline in C:
 *   1. Gauss 2D lattice reduction for each special-q
 *   2. Line-by-line sieve within reduced lattice (cache-friendly)
 *   3. Integrated trial division + LP detection (special-q aware)
 *   4. GMP for norms that overflow __int128
 *
 * Key advantage over line sieve:
 *   Line sieve: sieves ALL (a,b), most produce non-smooth norms
 *   Lattice sieve: sieves ONLY (a,b) where algebraic norm is divisible by q
 *   → 10-50x higher yield per candidate
 *
 * Compile:
 *   gcc -O3 -march=native -shared -fPIC -o gnfs_lattice_sieve_c.so \
 *       gnfs_lattice_sieve_c.c -lgmp -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <gmp.h>

/* ======================================================================
 * Utility: GCD, modular inverse, primality
 * ====================================================================== */

static int64_t gcd64(int64_t a, int64_t b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { int64_t t = b; b = a % b; a = t; }
    return a;
}

/* Extended GCD for modular inverse mod p */
static int64_t mod_inverse(int64_t a, int64_t p) {
    int64_t g = p, x = 0, y = 1;
    int64_t a0 = ((a % p) + p) % p;
    int64_t g0 = a0;
    while (g0 != 0) {
        int64_t q = g / g0;
        int64_t tmp;
        tmp = g - q * g0; g = g0; g0 = tmp;
        tmp = x - q * y; x = y; y = tmp;
    }
    if (g != 1) return 0;
    return ((x % p) + p) % p;
}

/* Modular multiply for 64-bit values (uses __int128) */
typedef __int128 i128;
typedef unsigned __int128 u128;

static uint64_t mulmod64(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)(((u128)a * (u128)b) % (u128)m);
}

static uint64_t powmod64(uint64_t base, uint64_t exp, uint64_t m) {
    uint64_t result = 1;
    base %= m;
    while (exp > 0) {
        if (exp & 1) result = mulmod64(result, base, m);
        base = mulmod64(base, base, m);
        exp >>= 1;
    }
    return result;
}

/* Deterministic Miller-Rabin for n < 3.3e24 */
static int is_prime64(int64_t n) {
    if (n < 2) return 0;
    if (n < 4) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    if (n < 25) return 1;
    uint64_t un = (uint64_t)n;
    uint64_t d = un - 1;
    int r = 0;
    while ((d & 1) == 0) { d >>= 1; r++; }
    static const uint64_t witnesses[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    for (int wi = 0; wi < 12; wi++) {
        uint64_t a = witnesses[wi];
        if (a >= un) continue;
        uint64_t x = powmod64(a, d, un);
        if (x == 1 || x == un - 1) continue;
        int composite = 1;
        for (int i = 0; i < r - 1; i++) {
            x = mulmod64(x, x, un);
            if (x == un - 1) { composite = 0; break; }
        }
        if (composite) return 0;
    }
    return 1;
}

/* ======================================================================
 * Gauss 2D lattice reduction
 * ====================================================================== */

void gauss_reduce_c(int64_t *ux, int64_t *uy, int64_t *vx, int64_t *vy) {
    while (1) {
        /* Use double for norm comparison to avoid i64 overflow on large q */
        double nu = (double)(*ux) * (double)(*ux) + (double)(*uy) * (double)(*uy);
        double nv = (double)(*vx) * (double)(*vx) + (double)(*vy) * (double)(*vy);
        if (nv < nu) {
            int64_t t;
            t = *ux; *ux = *vx; *vx = t;
            t = *uy; *uy = *vy; *vy = t;
            double tn = nu; nu = nv; nv = tn;
        }
        if (nu < 1e-9) break;
        double dot = (double)(*ux) * (double)(*vx) + (double)(*uy) * (double)(*vy);
        int64_t mu;
        if (dot >= 0)
            mu = (int64_t)((dot + nu / 2.0) / nu);
        else
            mu = -(int64_t)((-dot + nu / 2.0) / nu);
        if (mu == 0) break;
        *vx -= mu * (*ux);
        *vy -= mu * (*uy);
    }
}

/* ======================================================================
 * Norm computation with GMP (arbitrary precision)
 *
 * Algebraic norm = |sum_{i=0}^{d} f[i] * (-a)^i * b^(d-i)|
 * Rational norm  = |a + b * m|
 * ====================================================================== */

/* Compute algebraic norm into mpz_t result.
 * f_coeffs[0..d], degree d, coordinates (a, b).
 * Result is |norm|. */
static void compute_alg_norm_gmp(mpz_t result, int64_t a, int64_t b,
                                  const int64_t *f_coeffs, int d) {
    mpz_t term, neg_a_pow, b_pow, coeff_z;
    mpz_inits(term, neg_a_pow, b_pow, coeff_z, NULL);

    mpz_set_ui(result, 0);
    mpz_set_si(neg_a_pow, 1);       /* (-a)^0 = 1 */
    mpz_set_si(b_pow, 1);
    for (int i = 0; i < d; i++)
        mpz_mul_si(b_pow, b_pow, b);  /* b^d */

    for (int i = 0; i <= d; i++) {
        /* term = f[i] * (-a)^i * b^(d-i) */
        mpz_set_si(coeff_z, f_coeffs[i]);
        mpz_mul(term, coeff_z, neg_a_pow);
        mpz_mul(term, term, b_pow);
        mpz_add(result, result, term);

        mpz_mul_si(neg_a_pow, neg_a_pow, -a);
        if (i < d && b != 0)
            mpz_divexact_ui(b_pow, b_pow, (unsigned long)(b > 0 ? b : -b));
    }
    mpz_abs(result, result);

    mpz_clears(term, neg_a_pow, b_pow, coeff_z, NULL);
}

/* Try to compute algebraic norm using __int128 (fast path).
 * Returns 1 on success, 0 on overflow. */
static int compute_alg_norm_128(i128 *out, int64_t a, int64_t b,
                                 const int64_t *f_coeffs, int d) {
    i128 result = 0;
    i128 neg_a_pow = 1;
    i128 b_pow = 1;
    for (int i = 0; i < d; i++) b_pow *= (i128)b;

    for (int i = 0; i <= d; i++) {
        i128 term = (i128)f_coeffs[i] * neg_a_pow;
        /* Check overflow of term * b_pow:
         * if |term| > 2^62 and |b_pow| > 2^62, overflow possible */
        i128 abs_term = term >= 0 ? term : -term;
        i128 abs_bpow = b_pow >= 0 ? b_pow : -b_pow;
        if (abs_term > 0 && abs_bpow > ((i128)1 << 126) / abs_term)
            return 0;  /* overflow */
        term *= b_pow;
        result += term;

        neg_a_pow *= (i128)(-a);
        if (i < d && b != 0)
            b_pow /= (i128)b;
    }
    *out = result >= 0 ? result : -result;
    return 1;
}

/* ======================================================================
 * Precomputation for per-prime sieve constants
 * ====================================================================== */

typedef struct {
    int64_t *rat_R2_R1inv;   /* rational: -(R2 * R1^{-1}) mod p, for sieve start */
    int     *rat_valid;       /* 1 if R1 != 0 for this prime */
    int64_t *alg_V_Uinv;     /* algebraic: -(V * U^{-1}) mod p */
    int     *alg_valid;
    uint16_t *rat_logp;       /* log2(p) * 128 for each rational prime */
    uint16_t *alg_logp;       /* log2(p) * 128 for each algebraic prime */
} sieve_precomp_t;

static sieve_precomp_t* precompute_sieve_constants(
    int64_t e1x, int64_t e1y, int64_t e2x, int64_t e2y,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    int64_t q)
{
    sieve_precomp_t *pc = (sieve_precomp_t *)calloc(1, sizeof(sieve_precomp_t));
    if (!pc) return NULL;

    pc->rat_R2_R1inv = (int64_t *)calloc(n_rat, sizeof(int64_t));
    pc->rat_valid    = (int *)calloc(n_rat, sizeof(int));
    pc->alg_V_Uinv  = (int64_t *)calloc(n_alg, sizeof(int64_t));
    pc->alg_valid    = (int *)calloc(n_alg, sizeof(int));
    pc->rat_logp     = (uint16_t *)calloc(n_rat, sizeof(uint16_t));
    pc->alg_logp     = (uint16_t *)calloc(n_alg, sizeof(uint16_t));

    if (!pc->rat_R2_R1inv || !pc->rat_valid || !pc->alg_V_Uinv ||
        !pc->alg_valid || !pc->rat_logp || !pc->alg_logp) {
        free(pc->rat_R2_R1inv); free(pc->rat_valid);
        free(pc->alg_V_Uinv); free(pc->alg_valid);
        free(pc->rat_logp); free(pc->alg_logp);
        free(pc);
        return NULL;
    }

    /* Rational side: for each prime p,
     * R1 = (e1x + e1y * m) mod p
     * R2 = (e2x + e2y * m) mod p
     * Sieve start for row j: i_start = (-j * R2 * R1^{-1}) mod p */
    for (int i = 0; i < n_rat; i++) {
        int64_t p = rat_primes[i];
        pc->rat_logp[i] = (uint16_t)(log((double)p) * 128.0 + 0.5);

        /* Careful modular arithmetic to avoid overflow */
        int64_t e1xp = ((e1x % p) + p) % p;
        int64_t e1yp = ((e1y % p) + p) % p;
        int64_t mp   = ((m % p) + p) % p;
        int64_t R1 = (e1xp + (e1yp * mp) % p) % p;

        int64_t e2xp = ((e2x % p) + p) % p;
        int64_t e2yp = ((e2y % p) + p) % p;
        int64_t R2 = (e2xp + (e2yp * mp) % p) % p;

        if (R1 != 0) {
            int64_t R1inv = mod_inverse(R1, p);
            pc->rat_R2_R1inv[i] = (R2 * R1inv) % p;
            pc->rat_valid[i] = 1;
        }
    }

    /* Algebraic side: for each prime p with root r,
     * U = (e1x + e1y * r) mod p
     * V = (e2x + e2y * r) mod p
     * Skip if p == q (special-q itself; handled separately) */
    for (int i = 0; i < n_alg; i++) {
        int64_t p = alg_primes[i];
        pc->alg_logp[i] = (uint16_t)(log((double)p) * 128.0 + 0.5);

        if (p == q) {
            pc->alg_valid[i] = 0;  /* skip special-q prime in sieve */
            continue;
        }

        int64_t rp = alg_roots[i];
        int64_t e1xp = ((e1x % p) + p) % p;
        int64_t e1yp = ((e1y % p) + p) % p;
        int64_t rpp  = ((rp % p) + p) % p;
        int64_t U = (e1xp + (e1yp * rpp) % p) % p;

        int64_t e2xp = ((e2x % p) + p) % p;
        int64_t e2yp = ((e2y % p) + p) % p;
        int64_t V = (e2xp + (e2yp * rpp) % p) % p;

        if (U != 0) {
            int64_t Uinv = mod_inverse(U, p);
            pc->alg_V_Uinv[i] = (V * Uinv) % p;
            pc->alg_valid[i] = 1;
        }
    }

    return pc;
}

static void free_precomp(sieve_precomp_t *pc) {
    if (!pc) return;
    free(pc->rat_R2_R1inv);
    free(pc->rat_valid);
    free(pc->alg_V_Uinv);
    free(pc->alg_valid);
    free(pc->rat_logp);
    free(pc->alg_logp);
    free(pc);
}

/* ======================================================================
 * Core lattice sieve: sieve one special-q with integrated verify
 *
 * This is the hot loop. For each row j:
 *   1. Clear sieve arrays
 *   2. Sieve rational + algebraic sides (stride p per FB prime)
 *   3. Threshold filter
 *   4. Convert (i,j) -> (a,b) = i*e1 + j*e2
 *   5. Trial divide both norms with LP detection
 *   6. Special-q handling: divide q from algebraic norm
 *
 * Memory: 2 * (2*I+1) * 2 bytes per row = ~256KB for I=32K
 * ====================================================================== */

/*
 * Output relation structure (flat arrays for ctypes compatibility)
 */
typedef struct {
    int *out_a;
    int *out_b;
    int64_t *out_rat_exps;    /* flattened: n_rels * n_rat */
    int64_t *out_alg_exps;    /* flattened: n_rels * n_alg */
    int *out_signs;
    int *out_mask;            /* 0=reject, 1=full, 2=rat LP, 3=alg LP, 4=DLP */
    int64_t *out_rat_lp;
    int64_t *out_alg_lp;
    int64_t *out_sq;          /* special-q for each relation */
    int max_rels;
} rel_output_t;

/*
 * lattice_sieve_and_verify_q: Sieve + verify one special-q.
 *
 * Returns number of verified relations found.
 */
static int lattice_sieve_and_verify_q(
    int64_t e1x, int64_t e1y, int64_t e2x, int64_t e2y,
    int I_max, int J_max,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    const int64_t *f_coeffs, int degree,
    int64_t q,
    double rat_frac, double alg_frac,
    int64_t lp_bound,
    const sieve_precomp_t *pc,
    rel_output_t *out,
    int out_offset)
{
    int size = 2 * I_max + 1;
    int total = 0;
    int remaining = out->max_rels - out_offset;
    if (remaining <= 0) return 0;

    /* Sieve arrays — one row at a time */
    uint16_t *rat_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    uint16_t *alg_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    if (!rat_log || !alg_log) {
        free(rat_log); free(alg_log);
        return 0;
    }

    /* Per-row candidate buffer */
    int max_row_cands = 10000;
    int *row_cand_idx = (int *)malloc(max_row_cands * sizeof(int));
    if (!row_cand_idx) {
        free(rat_log); free(alg_log);
        return 0;
    }

    /* Norm estimate constants for thresholds */
    double e1_m = (double)e1x + (double)e1y * (double)m;
    double e2_m = (double)e2x + (double)e2y * (double)m;
    double log_q = log((double)q);

    /* GMP temporaries for norm computation (allocated once, reused) */
    mpz_t gmp_norm, gmp_rem, gmp_p;
    mpz_inits(gmp_norm, gmp_rem, gmp_p, NULL);

    for (int j = 0; j <= J_max && total < remaining; j++) {
        memset(rat_log, 0, size * sizeof(uint16_t));
        memset(alg_log, 0, size * sizeof(uint16_t));

        /* === Rational sieve for row j === */
        for (int pi = 0; pi < n_rat; pi++) {
            if (!pc->rat_valid[pi]) continue;
            int64_t p = rat_primes[pi];
            uint16_t lp = pc->rat_logp[pi];
            int64_t start = ((-(int64_t)j * pc->rat_R2_R1inv[pi]) % p + p) % p;
            start = (start + I_max) % p;
            for (int64_t idx = start; idx < size; idx += p)
                rat_log[idx] += lp;
        }

        /* === Algebraic sieve for row j === */
        for (int pi = 0; pi < n_alg; pi++) {
            if (!pc->alg_valid[pi]) continue;
            int64_t p = alg_primes[pi];
            uint16_t lp = pc->alg_logp[pi];
            int64_t start = ((-(int64_t)j * pc->alg_V_Uinv[pi]) % p + p) % p;
            start = (start + I_max) % p;
            for (int64_t idx = start; idx < size; idx += p)
                alg_log[idx] += lp;
        }

        /* === Adaptive thresholds === */
        /* Rational: log(|a + b*m|) where (a,b) at edge of sieve region */
        double rat_typical = fabs((double)I_max * e1_m + (double)j * e2_m);
        if (rat_typical < fabs(e1_m)) rat_typical = fabs(e1_m);
        if (rat_typical < 2.0) rat_typical = 2.0;
        uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

        /* Algebraic: norm / q (since q divides norm by construction) */
        double a_est = (double)I_max * fabs((double)e1x) + (double)j * fabs((double)e2x);
        double b_est = fmax(1.0, (double)I_max * fabs((double)e1y) + (double)j * fabs((double)e2y));
        double alg_log_norm = (double)degree * log(fmax(a_est, b_est));
        if (alg_log_norm > log_q)
            alg_log_norm -= log_q;  /* subtract q from norm estimate */
        uint16_t alg_thresh = (alg_log_norm > 1.0)
            ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

        /* === Collect candidate positions === */
        int n_row_cands = 0;
        for (int idx = 0; idx < size && n_row_cands < max_row_cands; idx++) {
            if (rat_log[idx] >= rat_thresh && alg_log[idx] >= alg_thresh) {
                int i_val = idx - I_max;
                if (i_val == 0 && j == 0) continue;
                row_cand_idx[n_row_cands++] = idx;
            }
        }

        /* === Verify each candidate === */
        for (int ci = 0; ci < n_row_cands && total < remaining; ci++) {
            int idx = row_cand_idx[ci];
            int i_val = idx - I_max;

            /* Convert lattice (i,j) -> original (a,b) */
            int64_t a64 = (int64_t)i_val * e1x + (int64_t)j * e2x;
            int64_t b64 = (int64_t)i_val * e1y + (int64_t)j * e2y;

            /* Filter: b > 0, a != 0, gcd(|a|,b) = 1 */
            if (b64 <= 0 || a64 == 0) continue;
            if (gcd64(a64 < 0 ? -a64 : a64, b64) != 1) continue;

            /* Truncate to int for output (line sieve compat) */
            if (a64 > 2147483647LL || a64 < -2147483647LL) continue;
            if (b64 > 2147483647LL) continue;
            int a_int = (int)a64;
            int b_int = (int)b64;

            int oi = out_offset + total;  /* output index */

            /* Clear output exponent arrays */
            int64_t *re = out->out_rat_exps + (int64_t)oi * n_rat;
            int64_t *ae = out->out_alg_exps + (int64_t)oi * n_alg;
            memset(re, 0, n_rat * sizeof(int64_t));
            memset(ae, 0, n_alg * sizeof(int64_t));
            out->out_mask[oi] = 0;
            out->out_rat_lp[oi] = 0;
            out->out_alg_lp[oi] = 0;

            /* ============ Rational side ============ */
            /* Rational norm: |a + b*m| */
            i128 raw_r = (i128)a64 + (i128)b64 * (i128)m;
            int sign = 0;
            if (raw_r < 0) { raw_r = -raw_r; sign = 1; }
            out->out_signs[oi] = sign;
            if (raw_r == 0) continue;

            /* Trial divide rational norm */
            int rat_smooth;
            int64_t rat_lp = 0;

            if (raw_r <= (i128)0x7FFFFFFFFFFFFFFFLL) {
                /* Fast path: int64 */
                int64_t rem64 = (int64_t)raw_r;
                for (int pi = 0; pi < n_rat; pi++) {
                    int64_t p = rat_primes[pi];
                    if (rem64 < p) break;
                    /* Use sieve start position for fast divisibility check */
                    if ((int64_t)idx % p == ((-(int64_t)j * pc->rat_R2_R1inv[pi]) % p + p) % p
                        ? (((int64_t)idx % p) == (((-(int64_t)j * pc->rat_R2_R1inv[pi]) % p + p) % p + I_max) % p)
                        : 0) {
                        /* Sieve-informed check is complex for lattice; just trial divide */
                    }
                    /* Direct trial division (reliable) */
                    if (rem64 % p == 0) {
                        do { rem64 /= p; re[pi]++; } while (rem64 % p == 0);
                    }
                }
                rat_smooth = (rem64 == 1);
                if (!rat_smooth) {
                    if (rem64 > lp_bound || rem64 <= 1) continue;
                    if (!is_prime64(rem64)) continue;
                    rat_lp = rem64;
                }
            } else {
                /* Slow path: __int128 */
                i128 rem_r = raw_r;
                for (int pi = 0; pi < n_rat; pi++) {
                    int64_t p = rat_primes[pi];
                    if (rem_r < (i128)p) break;
                    if (rem_r % p == 0) {
                        do { rem_r /= p; re[pi]++; } while (rem_r % p == 0);
                    }
                }
                rat_smooth = (rem_r == 1);
                if (!rat_smooth) {
                    if (rem_r > (i128)lp_bound || rem_r <= 1) continue;
                    int64_t rem64 = (int64_t)rem_r;
                    if (!is_prime64(rem64)) continue;
                    rat_lp = rem64;
                }
            }

            /* ============ Algebraic side ============ */
            /* Try __int128 fast path first, fall back to GMP */
            i128 alg_norm_128 = 0;

            if (compute_alg_norm_128(&alg_norm_128, a64, b64, f_coeffs, degree)) {
                /* __int128 path */
                if (alg_norm_128 == 0) continue;

                /* Divide out special-q */
                if (alg_norm_128 % (i128)q != 0) continue;  /* q must divide norm */
                int sq_exp = 0;
                while (alg_norm_128 % (i128)q == 0) {
                    alg_norm_128 /= (i128)q;
                    sq_exp++;
                }

                /* Trial divide cofactor */
                i128 rem_a = alg_norm_128;
                for (int pi = 0; pi < n_alg; pi++) {
                    int64_t p = alg_primes[pi];
                    if (p == q) continue;  /* skip special-q */
                    if (rem_a < (i128)p) break;
                    int64_t rp = alg_roots[pi];
                    /* Pre-check: p | norm iff (a + b*r) = 0 mod p */
                    int64_t a_mod = ((a64 % p) + p) % p;
                    int64_t b_mod = ((b64 % p) + p) % p;
                    int64_t r_mod = ((rp % p) + p) % p;
                    int64_t check = (a_mod + (b_mod * r_mod) % p) % p;
                    if (check == 0) {
                        while (rem_a % p == 0) {
                            rem_a /= p;
                            ae[pi]++;
                        }
                    }
                    if (rem_a == 1) break;
                }

                int alg_smooth = (rem_a == 1);
                int64_t alg_lp = 0;
                if (!alg_smooth) {
                    if (rem_a > (i128)lp_bound || rem_a <= 1) continue;
                    int64_t rem64 = (int64_t)rem_a;
                    if (!is_prime64(rem64)) continue;
                    alg_lp = rem64;
                }

                /* Success! Record relation */
                out->out_a[oi] = a_int;
                out->out_b[oi] = b_int;
                out->out_rat_lp[oi] = rat_lp;
                out->out_alg_lp[oi] = alg_lp;
                out->out_sq[oi] = q;

                if (rat_lp == 0 && alg_lp == 0)
                    out->out_mask[oi] = 1;
                else if (rat_lp != 0 && alg_lp == 0)
                    out->out_mask[oi] = 2;
                else if (rat_lp == 0 && alg_lp != 0)
                    out->out_mask[oi] = 3;
                else
                    out->out_mask[oi] = 4;

                total++;
            } else {
                /* GMP path: norm overflows __int128 */
                compute_alg_norm_gmp(gmp_norm, a64, b64, f_coeffs, degree);
                if (mpz_sgn(gmp_norm) == 0) continue;

                /* Divide out special-q */
                mpz_set_si(gmp_p, q);
                if (!mpz_divisible_p(gmp_norm, gmp_p)) continue;
                int sq_exp = 0;
                while (mpz_divisible_p(gmp_norm, gmp_p)) {
                    mpz_divexact(gmp_norm, gmp_norm, gmp_p);
                    sq_exp++;
                }

                /* Trial divide cofactor using GMP */
                mpz_set(gmp_rem, gmp_norm);
                for (int pi = 0; pi < n_alg; pi++) {
                    int64_t p = alg_primes[pi];
                    if (p == q) continue;
                    int64_t rp = alg_roots[pi];
                    /* Pre-check */
                    int64_t a_mod = ((a64 % p) + p) % p;
                    int64_t b_mod = ((b64 % p) + p) % p;
                    int64_t r_mod = ((rp % p) + p) % p;
                    int64_t check = (a_mod + (b_mod * r_mod) % p) % p;
                    if (check == 0) {
                        mpz_set_si(gmp_p, p);
                        while (mpz_divisible_p(gmp_rem, gmp_p)) {
                            mpz_divexact(gmp_rem, gmp_rem, gmp_p);
                            ae[pi]++;
                        }
                    }
                    if (mpz_cmp_ui(gmp_rem, 1) == 0) break;
                }

                int alg_smooth = (mpz_cmp_ui(gmp_rem, 1) == 0);
                int64_t alg_lp = 0;
                if (!alg_smooth) {
                    if (mpz_cmp_si(gmp_rem, lp_bound) > 0) continue;
                    if (mpz_cmp_ui(gmp_rem, 1) <= 0) continue;
                    if (!mpz_fits_slong_p(gmp_rem)) continue;
                    int64_t rem64 = (int64_t)mpz_get_si(gmp_rem);
                    if (!is_prime64(rem64)) continue;
                    alg_lp = rem64;
                }

                out->out_a[oi] = a_int;
                out->out_b[oi] = b_int;
                out->out_rat_lp[oi] = rat_lp;
                out->out_alg_lp[oi] = alg_lp;
                out->out_sq[oi] = q;

                if (rat_lp == 0 && alg_lp == 0)
                    out->out_mask[oi] = 1;
                else if (rat_lp != 0 && alg_lp == 0)
                    out->out_mask[oi] = 2;
                else if (rat_lp == 0 && alg_lp != 0)
                    out->out_mask[oi] = 3;
                else
                    out->out_mask[oi] = 4;

                total++;
            }
        }
    }

    mpz_clears(gmp_norm, gmp_rem, gmp_p, NULL);
    free(rat_log);
    free(alg_log);
    free(row_cand_idx);
    return total;
}


/* ======================================================================
 * Public API: lattice_sieve_batch
 *
 * Process multiple special-q primes. For each (q, root):
 *   1. Construct lattice basis
 *   2. Gauss-reduce
 *   3. Compute adaptive sieve region
 *   4. Sieve + verify (integrated)
 *   5. Output verified relations
 *
 * Compatible with the existing Python caller in gnfs_engine.py.
 * ====================================================================== */

int lattice_sieve_batch(
    const int64_t *q_primes, const int64_t *q_roots, int n_q,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    double rat_frac, double alg_frac,
    int poly_degree,
    int sieve_radius, int sieve_height,
    int *out_a, int *out_b, int64_t *out_q,
    int max_cands)
{
    /* This is the "sieve-only" batch entry point used by the old Python path.
     * It performs sieve + coprimality filter but NOT trial division.
     * Verification is done by the caller using verify_candidates_c.
     * Kept for backward compatibility. */

    int total = 0;
    int batch_max = max_cands > 50000 ? 50000 : max_cands;
    int *tmp_i = (int *)malloc(batch_max * sizeof(int));
    int *tmp_j = (int *)malloc(batch_max * sizeof(int));
    if (!tmp_i || !tmp_j) { free(tmp_i); free(tmp_j); return 0; }

    /* Sieve arrays (allocated once, reused) */
    int max_size = 2 * sieve_radius + 1;
    uint16_t *rat_log = (uint16_t *)malloc(max_size * sizeof(uint16_t));
    uint16_t *alg_log = (uint16_t *)malloc(max_size * sizeof(uint16_t));
    uint16_t *rat_lps = (uint16_t *)malloc(n_rat * sizeof(uint16_t));
    uint16_t *alg_lps = (uint16_t *)malloc(n_alg * sizeof(uint16_t));
    if (!rat_log || !alg_log || !rat_lps || !alg_lps) {
        free(tmp_i); free(tmp_j);
        free(rat_log); free(alg_log);
        free(rat_lps); free(alg_lps);
        return 0;
    }

    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    for (int qi = 0; qi < n_q && total < max_cands; qi++) {
        int64_t q = q_primes[qi];
        int64_t r = q_roots[qi];

        /* Gauss reduce */
        int64_t ux = q, uy = 0;
        int64_t vx = ((-r) % q + q) % q, vy = 1;
        gauss_reduce_c(&ux, &uy, &vx, &vy);

        /* Adaptive sieve region */
        double len_e1 = sqrt((double)ux * (double)ux + (double)uy * (double)uy);
        double len_e2 = sqrt((double)vx * (double)vx + (double)vy * (double)vy);
        int I_max = (int)(50000.0 / fmax(len_e1, 1.0));
        if (I_max < 50) I_max = 50;
        if (I_max > sieve_radius) I_max = sieve_radius;
        int J_max = (int)(200.0 / fmax(len_e2, 1.0));
        if (J_max < 2) J_max = 2;
        if (J_max > sieve_height) J_max = sieve_height;

        int size = 2 * I_max + 1;

        /* Precompute per-prime lattice projections */
        int64_t *rat_R2R1inv = (int64_t *)calloc(n_rat, sizeof(int64_t));
        int *rat_valid = (int *)calloc(n_rat, sizeof(int));
        int64_t *alg_VUinv = (int64_t *)calloc(n_alg, sizeof(int64_t));
        int *alg_valid = (int *)calloc(n_alg, sizeof(int));

        if (!rat_R2R1inv || !rat_valid || !alg_VUinv || !alg_valid) {
            free(rat_R2R1inv); free(rat_valid);
            free(alg_VUinv); free(alg_valid);
            continue;
        }

        for (int i = 0; i < n_rat; i++) {
            int64_t p = rat_primes[i];
            int64_t e1xp = ((ux % p) + p) % p;
            int64_t e1yp = ((uy % p) + p) % p;
            int64_t mp = ((m % p) + p) % p;
            int64_t R1 = (e1xp + (e1yp * mp) % p) % p;
            int64_t e2xp = ((vx % p) + p) % p;
            int64_t e2yp = ((vy % p) + p) % p;
            int64_t R2 = (e2xp + (e2yp * mp) % p) % p;
            if (R1 != 0) {
                int64_t R1inv = mod_inverse(R1, p);
                rat_R2R1inv[i] = (R2 * R1inv) % p;
                rat_valid[i] = 1;
            }
        }

        for (int i = 0; i < n_alg; i++) {
            int64_t p = alg_primes[i];
            if (p == q) { alg_valid[i] = 0; continue; }
            int64_t rp = alg_roots[i];
            int64_t e1xp = ((ux % p) + p) % p;
            int64_t e1yp = ((uy % p) + p) % p;
            int64_t rpp = ((rp % p) + p) % p;
            int64_t U = (e1xp + (e1yp * rpp) % p) % p;
            int64_t e2xp = ((vx % p) + p) % p;
            int64_t e2yp = ((vy % p) + p) % p;
            int64_t V = (e2xp + (e2yp * rpp) % p) % p;
            if (U != 0) {
                int64_t Uinv = mod_inverse(U, p);
                alg_VUinv[i] = (V * Uinv) % p;
                alg_valid[i] = 1;
            }
        }

        /* Norm estimates for thresholds */
        double e1_m = (double)ux + (double)uy * (double)m;
        double e2_m = (double)vx + (double)vy * (double)m;
        double log_q = log((double)q);

        int n_this_q = 0;
        for (int j = 0; j <= J_max && total < max_cands; j++) {
            if (size > max_size) break;
            memset(rat_log, 0, size * sizeof(uint16_t));
            memset(alg_log, 0, size * sizeof(uint16_t));

            for (int pi = 0; pi < n_rat; pi++) {
                if (!rat_valid[pi]) continue;
                int64_t p = rat_primes[pi];
                uint16_t lp = rat_lps[pi];
                int64_t start = ((-(int64_t)j * rat_R2R1inv[pi]) % p + p) % p;
                start = (start + I_max) % p;
                for (int64_t idx = start; idx < size; idx += p)
                    rat_log[idx] += lp;
            }

            for (int pi = 0; pi < n_alg; pi++) {
                if (!alg_valid[pi]) continue;
                int64_t p = alg_primes[pi];
                uint16_t lp = alg_lps[pi];
                int64_t start = ((-(int64_t)j * alg_VUinv[pi]) % p + p) % p;
                start = (start + I_max) % p;
                for (int64_t idx = start; idx < size; idx += p)
                    alg_log[idx] += lp;
            }

            double rat_typical = fabs((double)I_max * e1_m + (double)j * e2_m);
            if (rat_typical < fabs(e1_m)) rat_typical = fabs(e1_m);
            if (rat_typical < 2.0) rat_typical = 2.0;
            uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

            double a_est = (double)I_max * fabs((double)ux) + (double)j * fabs((double)vx);
            double b_est = fmax(1.0, (double)I_max * fabs((double)uy) + (double)j * fabs((double)vy));
            double alg_log_norm = (double)poly_degree * log(fmax(a_est, b_est));
            if (alg_log_norm > log_q)
                alg_log_norm -= log_q;
            uint16_t alg_thresh = (alg_log_norm > 1.0)
                ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

            for (int idx = 0; idx < size && total < max_cands; idx++) {
                if (rat_log[idx] >= rat_thresh && alg_log[idx] >= alg_thresh) {
                    int i_val = idx - I_max;
                    if (i_val == 0 && j == 0) continue;
                    int64_t a = (int64_t)i_val * ux + (int64_t)j * vx;
                    int64_t b = (int64_t)i_val * uy + (int64_t)j * vy;
                    if (b <= 0 || a == 0) continue;
                    if (gcd64(a < 0 ? -a : a, b) != 1) continue;
                    if (a > 2147483647LL || a < -2147483647LL || b > 2147483647LL) continue;
                    out_a[total] = (int)a;
                    out_b[total] = (int)b;
                    out_q[total] = q;
                    total++;
                    n_this_q++;
                }
            }
        }

        free(rat_R2R1inv); free(rat_valid);
        free(alg_VUinv); free(alg_valid);
    }

    free(tmp_i); free(tmp_j);
    free(rat_log); free(alg_log);
    free(rat_lps); free(alg_lps);
    return total;
}


/* ======================================================================
 * New API: lattice_sieve_verify_batch
 *
 * Full sieve + verify pipeline. Returns verified relations with
 * exponent vectors, LP values, and special-q info.
 *
 * This is the primary entry point for the lattice sieve path.
 * ====================================================================== */

int lattice_sieve_verify_batch(
    const int64_t *q_primes, const int64_t *q_roots, int n_q,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    const int64_t *f_coeffs, int poly_degree,
    double rat_frac, double alg_frac,
    int sieve_radius, int sieve_height,
    int64_t lp_bound,
    /* Output arrays (all preallocated by caller) */
    int *out_a, int *out_b,
    int64_t *out_rat_exps,    /* flattened: max_rels * n_rat */
    int64_t *out_alg_exps,    /* flattened: max_rels * n_alg */
    int *out_signs,
    int *out_mask,
    int64_t *out_rat_lp,
    int64_t *out_alg_lp,
    int64_t *out_sq,          /* which special-q produced each relation */
    int max_rels)
{
    int total = 0;

    rel_output_t out_struct;
    out_struct.out_a = out_a;
    out_struct.out_b = out_b;
    out_struct.out_rat_exps = out_rat_exps;
    out_struct.out_alg_exps = out_alg_exps;
    out_struct.out_signs = out_signs;
    out_struct.out_mask = out_mask;
    out_struct.out_rat_lp = out_rat_lp;
    out_struct.out_alg_lp = out_alg_lp;
    out_struct.out_sq = out_sq;
    out_struct.max_rels = max_rels;

    for (int qi = 0; qi < n_q && total < max_rels; qi++) {
        int64_t q = q_primes[qi];
        int64_t r = q_roots[qi];

        /* Construct lattice: L = {(a,b) : a + b*r = 0 (mod q)}
         * Basis: v1 = (q, 0), v2 = (-r mod q, 1) */
        int64_t ux = q, uy = 0;
        int64_t vx = ((-r) % q + q) % q, vy = 1;
        gauss_reduce_c(&ux, &uy, &vx, &vy);

        /* Adaptive sieve region based on reduced basis vector lengths.
         * After Gauss reduction, |e1| ~ |e2| ~ sqrt(q).
         * We want the sieve region to cover enough (a,b) space for good yield
         * while keeping norms manageable.
         *
         * Standard: I ~ 2^16, J ~ I/2 for square sieve regions.
         * But we scale inversely with vector length to keep norms bounded. */
        double len_e1 = sqrt((double)ux * (double)ux + (double)uy * (double)uy);
        double len_e2 = sqrt((double)vx * (double)vx + (double)vy * (double)vy);

        /* Scale sieve region: want total covered area ~ constant
         * Area ~ I_max * J_max * det(lattice) = I_max * J_max * q
         * For fixed yield, want I*J*q ~ target. */
        int I_max = (int)(50000.0 / fmax(len_e1, 1.0));
        if (I_max < 50) I_max = 50;
        if (I_max > sieve_radius) I_max = sieve_radius;

        int J_max = (int)(200.0 / fmax(len_e2, 1.0));
        if (J_max < 2) J_max = 2;
        if (J_max > sieve_height) J_max = sieve_height;

        /* Precompute per-prime sieve constants for this (q, r) */
        sieve_precomp_t *pc = precompute_sieve_constants(
            ux, uy, vx, vy,
            rat_primes, n_rat, m,
            alg_primes, alg_roots, n_alg,
            q);
        if (!pc) continue;

        int n_found = lattice_sieve_and_verify_q(
            ux, uy, vx, vy,
            I_max, J_max,
            rat_primes, n_rat, m,
            alg_primes, alg_roots, n_alg,
            f_coeffs, poly_degree,
            q,
            rat_frac, alg_frac,
            lp_bound,
            pc,
            &out_struct,
            total);

        total += n_found;
        free_precomp(pc);
    }

    return total;
}


/* ======================================================================
 * Convenience: single special-q sieve (no verify)
 * Kept for backward compatibility with the old Python path.
 * ====================================================================== */

int lattice_sieve_q(
    int64_t e1x, int64_t e1y, int64_t e2x, int64_t e2y,
    int I_max, int J_max,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    double rat_frac, double alg_frac,
    int64_t q, int poly_degree,
    int *out_i, int *out_j, int max_cands)
{
    int size = 2 * I_max + 1;
    int total = 0;

    uint16_t *rat_lps = (uint16_t *)malloc(n_rat * sizeof(uint16_t));
    uint16_t *alg_lps = (uint16_t *)malloc(n_alg * sizeof(uint16_t));
    if (!rat_lps || !alg_lps) { free(rat_lps); free(alg_lps); return 0; }

    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    /* Precompute per-prime constants */
    int64_t *rat_R2R1inv = (int64_t *)calloc(n_rat, sizeof(int64_t));
    int *rat_valid = (int *)calloc(n_rat, sizeof(int));
    int64_t *alg_VUinv = (int64_t *)calloc(n_alg, sizeof(int64_t));
    int *alg_valid = (int *)calloc(n_alg, sizeof(int));

    if (!rat_R2R1inv || !rat_valid || !alg_VUinv || !alg_valid) goto cleanup_q;

    for (int i = 0; i < n_rat; i++) {
        int64_t p = rat_primes[i];
        int64_t e1xp = ((e1x % p) + p) % p;
        int64_t e1yp = ((e1y % p) + p) % p;
        int64_t mp = ((m % p) + p) % p;
        int64_t R1 = (e1xp + (e1yp * mp) % p) % p;
        int64_t e2xp = ((e2x % p) + p) % p;
        int64_t e2yp = ((e2y % p) + p) % p;
        int64_t R2 = (e2xp + (e2yp * mp) % p) % p;
        if (R1 != 0) {
            int64_t R1inv = mod_inverse(R1, p);
            rat_R2R1inv[i] = (R2 * R1inv) % p;
            rat_valid[i] = 1;
        }
    }

    for (int i = 0; i < n_alg; i++) {
        int64_t p = alg_primes[i];
        if (p == q) { alg_valid[i] = 0; continue; }
        int64_t rp = alg_roots[i];
        int64_t e1xp = ((e1x % p) + p) % p;
        int64_t e1yp = ((e1y % p) + p) % p;
        int64_t rpp = ((rp % p) + p) % p;
        int64_t U = (e1xp + (e1yp * rpp) % p) % p;
        int64_t e2xp = ((e2x % p) + p) % p;
        int64_t e2yp = ((e2y % p) + p) % p;
        int64_t V = (e2xp + (e2yp * rpp) % p) % p;
        if (U != 0) {
            int64_t Uinv = mod_inverse(U, p);
            alg_VUinv[i] = (V * Uinv) % p;
            alg_valid[i] = 1;
        }
    }

    {
        uint16_t *sieve_rat = (uint16_t *)malloc(size * sizeof(uint16_t));
        uint16_t *sieve_alg = (uint16_t *)malloc(size * sizeof(uint16_t));
        if (!sieve_rat || !sieve_alg) {
            free(sieve_rat); free(sieve_alg);
            goto cleanup_q;
        }

        double e1_m = (double)e1x + (double)e1y * (double)m;
        double e2_m = (double)e2x + (double)e2y * (double)m;
        double log_q = log((double)q);

        for (int j = 0; j <= J_max && total < max_cands; j++) {
            memset(sieve_rat, 0, size * sizeof(uint16_t));
            memset(sieve_alg, 0, size * sizeof(uint16_t));

            for (int pi = 0; pi < n_rat; pi++) {
                if (!rat_valid[pi]) continue;
                int64_t p = rat_primes[pi];
                uint16_t lp = rat_lps[pi];
                int64_t start = ((-(int64_t)j * rat_R2R1inv[pi]) % p + p) % p;
                start = (start + I_max) % p;
                for (int64_t idx = start; idx < size; idx += p)
                    sieve_rat[idx] += lp;
            }

            for (int pi = 0; pi < n_alg; pi++) {
                if (!alg_valid[pi]) continue;
                int64_t p = alg_primes[pi];
                uint16_t lp = alg_lps[pi];
                int64_t start = ((-(int64_t)j * alg_VUinv[pi]) % p + p) % p;
                start = (start + I_max) % p;
                for (int64_t idx = start; idx < size; idx += p)
                    sieve_alg[idx] += lp;
            }

            double rat_typical = fabs((double)I_max * e1_m + (double)j * e2_m);
            if (rat_typical < fabs(e1_m)) rat_typical = fabs(e1_m);
            if (rat_typical < 2.0) rat_typical = 2.0;
            uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

            double a_est = (double)I_max * fabs((double)e1x) + (double)j * fabs((double)e2x);
            double b_est = fmax(1.0, (double)I_max * fabs((double)e1y) + (double)j * fabs((double)e2y));
            double alg_log_norm = (double)poly_degree * log(fmax(a_est, b_est));
            if (alg_log_norm > log_q)
                alg_log_norm -= log_q;
            uint16_t alg_thresh = (alg_log_norm > 1.0)
                ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

            for (int idx = 0; idx < size && total < max_cands; idx++) {
                if (sieve_rat[idx] >= rat_thresh && sieve_alg[idx] >= alg_thresh) {
                    int i_val = idx - I_max;
                    if (i_val == 0 && j == 0) continue;
                    out_i[total] = i_val;
                    out_j[total] = j;
                    total++;
                }
            }
        }

        free(sieve_rat);
        free(sieve_alg);
    }

cleanup_q:
    free(rat_lps); free(alg_lps);
    free(rat_R2R1inv); free(rat_valid);
    free(alg_VUinv); free(alg_valid);
    return total;
}
