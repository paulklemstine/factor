/*
 * gnfs_sieve_c.c — Fast GNFS line sieve in C
 *
 * For each b-line, sieves a in [-A, A] for both rational and algebraic sides.
 * Returns candidate (a, b) pairs that pass the combined log threshold.
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o gnfs_sieve_c.so gnfs_sieve_c.c -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* Inline GCD for coprimality check (small ints) */
static int gcd_int(int a, int b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { int t = b; b = a % b; a = t; }
    return a;
}

/* Sieve multiple b-lines. Returns total candidates.
 * Thresholds are b-adaptive:
 *   rat_thresh(b) = rat_frac * log(max(b*|m|, A)) * 128
 *   alg_thresh(b) = alg_frac * log(max(A, b)) * d + log(max(f0, f_d)) * 128
 */
int sieve_batch_c(
    int b_start,
    int b_end,                    /* sieve b from b_start to b_end inclusive */
    int A,                        /* sieve a in [-A, A], size = 2*A+1 */
    /* Rational FB */
    const int64_t *rat_primes,
    int n_rat,
    int64_t m,                    /* polynomial root mod n */
    /* Algebraic FB */
    const int64_t *alg_primes,
    const int64_t *alg_roots,     /* roots of f mod p */
    int n_alg,
    /* Threshold parameters (fixed-point: value * 1000) */
    int rat_frac_x1000,          /* e.g. 600 for 0.60 */
    int alg_frac_x1000,          /* e.g. 500 for 0.50 */
    int poly_degree,
    int64_t f0_abs,              /* |f_coeffs[0]| */
    int64_t fd_abs,              /* |f_coeffs[d]| (leading coefficient) */
    /* Output: pairs (a, b) */
    int *out_a,
    int *out_b,
    int max_cands
)
{
    int size = 2 * A + 1;
    int total = 0;
    double abs_m = (double)(m >= 0 ? m : -m);
    double rat_frac = rat_frac_x1000 / 1000.0;
    double alg_frac = alg_frac_x1000 / 1000.0;
    double log_f0 = (f0_abs > 0) ? log((double)f0_abs) : 0.0;
    double log_fd = (fd_abs > 0) ? log((double)fd_abs) : 0.0;
    /* Use the larger of f0 and fd for norm estimate */
    double log_leading_coeff = (log_fd > log_f0) ? log_fd : log_f0;

    /* Allocate sieve arrays (reused across b-lines) */
    uint16_t *rat_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    uint16_t *alg_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    if (!rat_log || !alg_log) {
        free(rat_log);
        free(alg_log);
        return 0;
    }

    /* Precompute log(p) * 128 for each FB prime */
    uint16_t *rat_lps = (uint16_t *)malloc(n_rat * sizeof(uint16_t));
    uint16_t *alg_lps = (uint16_t *)malloc(n_alg * sizeof(uint16_t));
    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    for (int b = b_start; b <= b_end && total < max_cands; b++) {
        memset(rat_log, 0, size * sizeof(uint16_t));
        memset(alg_log, 0, size * sizeof(uint16_t));

        /* Compute b-adaptive thresholds */
        double bm = (double)b * abs_m;
        double rat_typical = (bm > (double)A) ? bm : (double)A;
        uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

        /* Fix 2: a-dependent algebraic threshold.
         * Actual norm ≈ max(f0 * b^d, fd * a^d). Since a ranges over [-A, A],
         * use max(A, b) as the dominant base. */
        double abs_A = (double)A;
        double dom = (abs_A > (double)b) ? abs_A : (double)b;
        double alg_log_norm = (double)poly_degree * log(dom) + log_leading_coeff;
        uint16_t alg_thresh = (alg_log_norm > 1.0)
            ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

        /* Rational sieve */
        for (int i = 0; i < n_rat; i++) {
            int64_t p = rat_primes[i];
            uint16_t lp = rat_lps[i];
            int64_t bm_mod = ((int64_t)b % p) * (((m % p) + p) % p) % p;
            int64_t start = ((-bm_mod % p) + p) % p;
            start = (start + (int64_t)A) % p;
            for (int64_t idx = start; idx < size; idx += p)
                rat_log[idx] += lp;
        }

        /* Algebraic sieve */
        for (int i = 0; i < n_alg; i++) {
            int64_t p = alg_primes[i];
            uint16_t lp = alg_lps[i];
            int64_t r = alg_roots[i];
            int64_t br_mod = ((int64_t)b % p) * ((r % p + p) % p) % p;
            int64_t start = ((-br_mod % p) + p) % p;
            start = (start + (int64_t)A) % p;
            for (int64_t idx = start; idx < size; idx += p)
                alg_log[idx] += lp;
        }

        /* Collect candidates with coprimality pre-filter (Fix 1) */
        for (int idx = 0; idx < size && total < max_cands; idx++) {
            if (rat_log[idx] >= rat_thresh && alg_log[idx] >= alg_thresh) {
                int a = idx - A;
                if (a == 0) continue;
                /* Skip non-coprime (a, b) pairs — saves ~41% of verify work */
                if (gcd_int(a, b) != 1) continue;
                out_a[total] = a;
                out_b[total] = b;
                total++;
            }
        }
    }

    free(rat_log);
    free(alg_log);
    free(rat_lps);
    free(alg_lps);
    return total;
}


/*
 * ============================================================================
 * Trial division with __int128 for norms that overflow int64.
 * Handles algebraic norms up to ~1.7×10^38 (sufficient for degree 3 at 50d).
 * ============================================================================
 */

typedef __int128 i128;
typedef unsigned __int128 u128;

static int64_t gcd64(int64_t a, int64_t b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { int64_t t = b; b = a % b; a = t; }
    return a;
}

/* Modular multiplication for 64-bit values (for Miller-Rabin) */
static uint64_t mulmod64(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)(((u128)a * (u128)b) % (u128)m);
}

/* Modular exponentiation */
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

/* Deterministic Miller-Rabin for n < 3.3×10^24 */
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
    int nw = 12;
    for (int wi = 0; wi < nw; wi++) {
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

/* i128 limits for overflow detection */
static const i128 I128_MAX = ((i128)1 << 126) - 1 + ((i128)1 << 126);  /* 2^127 - 1 */
static const i128 I128_MIN = -((i128)1 << 126) - ((i128)1 << 126);     /* -2^127 */

/* Safe multiply with overflow check for i128 */
static inline i128 safe_mul_128(i128 a, i128 b, int *overflow) {
    if (a == 0 || b == 0) return 0;
    i128 result = a * b;
    /* Check: if a*b/b != a, overflow occurred */
    if (b != 0 && result / b != a) { *overflow = 1; }
    return result;
}

/* Compute algebraic norm using __int128.
 * norm = sum_{i=0}^{d} f[i] * (-a)^i * b^(d-i)
 * Returns absolute value. Sets *overflow=1 if result doesn't fit in i128.
 */
static i128 compute_alg_norm_128(int a, int b, const int64_t *f_coeffs, int d, int *overflow) {
    *overflow = 0;
    i128 result = 0;
    i128 neg_a_pow = 1;       /* (-a)^i */
    i128 b_pow = 1;
    for (int i = 0; i < d; i++) b_pow *= b;  /* b^d */

    for (int i = 0; i <= d; i++) {
        /* Check each term for overflow: f[i] * neg_a_pow * b_pow */
        i128 term = safe_mul_128((i128)f_coeffs[i], neg_a_pow, overflow);
        if (*overflow) return 0;
        term = safe_mul_128(term, b_pow, overflow);
        if (*overflow) return 0;

        /* Check addition overflow */
        if ((term > 0 && result > I128_MAX - term) ||
            (term < 0 && result < I128_MIN - term)) {
            *overflow = 1;
            return 0;
        }
        result += term;

        neg_a_pow *= (-a);
        if (i < d) {
            /* b_pow = b^(d-i-1), but avoid division — just divide by b */
            b_pow /= b;
        }
    }
    if (result < 0) result = -result;
    return result;
}

/*
 * Batch verify candidates with __int128 trial division.
 * Processes all (a,b) pairs from C sieve output.
 *
 * out_mask: 0=reject, 1=full smooth, 2=rat has LP, 3=alg has LP
 * Returns number of non-rejected candidates.
 */
int verify_candidates_c(
    const int *cand_a, const int *cand_b, int n_cands,
    int64_t m,
    const int64_t *f_coeffs, int degree,
    /* Rational FB */
    const int64_t *rat_primes, int n_rat,
    /* Algebraic FB */
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    /* LP bound */
    int64_t lp_bound,
    /* Output arrays (all preallocated by caller, size = n_cands) */
    int64_t *out_rat_exps,    /* flattened n_cands × n_rat */
    int64_t *out_alg_exps,    /* flattened n_cands × n_alg */
    int *out_signs,
    int *out_mask,
    int64_t *out_rat_lp,
    int64_t *out_alg_lp
)
{
    int count = 0;

    for (int ci = 0; ci < n_cands; ci++) {
        int a = cand_a[ci];
        int b = cand_b[ci];
        out_mask[ci] = 0;
        out_rat_lp[ci] = 0;
        out_alg_lp[ci] = 0;

        /* Clear exponent rows */
        int64_t *re = out_rat_exps + (int64_t)ci * n_rat;
        int64_t *ae = out_alg_exps + (int64_t)ci * n_alg;
        memset(re, 0, n_rat * sizeof(int64_t));
        memset(ae, 0, n_alg * sizeof(int64_t));

        /* GCD check: gcd(|a|, b) == 1 */
        if (gcd64((int64_t)(a < 0 ? -a : a), (int64_t)b) != 1)
            continue;

        /* === Rational side === */
        /* Rational norm: a + b*m */
        i128 raw_r = (i128)a + (i128)b * (i128)m;
        int sign = 0;
        if (raw_r < 0) { raw_r = -raw_r; sign = 1; }
        out_signs[ci] = sign;
        if (raw_r == 0) continue;

        /* Trial divide rational norm — use int64 fast path when possible */
        int rat_smooth;
        int64_t rat_lp = 0;
        if (raw_r <= (i128)0x7FFFFFFFFFFFFFFFLL) {
            /* Fast path: norm fits in int64 */
            int64_t rem64 = (int64_t)raw_r;
            for (int j = 0; j < n_rat; j++) {
                int64_t p = rat_primes[j];
                if (rem64 < p) break;
                if (rem64 % p == 0) {
                    do { rem64 /= p; re[j]++; } while (rem64 % p == 0);
                }
            }
            rat_smooth = (rem64 == 1);
            if (!rat_smooth) {
                if (rem64 > lp_bound || rem64 <= 1) continue;
                if (!is_prime64(rem64)) continue;
                rat_lp = rem64;
            }
        } else {
            /* Slow path: need i128 */
            i128 rem_r = raw_r;
            for (int j = 0; j < n_rat; j++) {
                int64_t p = rat_primes[j];
                if (rem_r < (i128)p) break;
                if (rem_r % p == 0) {
                    do { rem_r /= p; re[j]++; } while (rem_r % p == 0);
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

        /* === Algebraic side === */
        int overflow = 0;
        i128 val_a = compute_alg_norm_128(a, b, f_coeffs, degree, &overflow);
        if (overflow || val_a == 0) continue;

        /* Trial divide algebraic norm with root pre-check */
        i128 rem_a = val_a;
        for (int j = 0; j < n_alg; j++) {
            int64_t p = alg_primes[j];
            int64_t r = alg_roots[j];
            /* Pre-check: p | norm iff (a + b*r) ≡ 0 (mod p) */
            int64_t a_mod = ((int64_t)a % p + p) % p;
            int64_t b_mod = ((int64_t)b % p + p) % p;
            int64_t r_mod = (r % p + p) % p;
            int64_t check = (a_mod + (b_mod * r_mod) % p) % p;
            if (check == 0 && rem_a >= (i128)p) {
                while (rem_a % p == 0) {
                    rem_a /= p;
                    ae[j]++;
                }
            }
            if (rem_a == 1) break;  /* fully factored */
        }

        /* Check algebraic remainder */
        int alg_smooth = (rem_a == 1);
        int64_t alg_lp = 0;
        if (!alg_smooth) {
            if (rem_a > (i128)lp_bound || rem_a <= 1) continue;
            int64_t rem64 = (int64_t)rem_a;
            if (!is_prime64(rem64)) continue;
            alg_lp = rem64;
        }

        out_rat_lp[ci] = rat_lp;
        out_alg_lp[ci] = alg_lp;

        if (rat_smooth && alg_smooth)
            out_mask[ci] = 1;
        else if (!rat_smooth && alg_smooth)
            out_mask[ci] = 2;  /* rat has LP */
        else if (rat_smooth && !alg_smooth)
            out_mask[ci] = 3;  /* alg has LP */
        else
            out_mask[ci] = 4;  /* DLP: both sides have LP */

        count++;
    }
    return count;
}
