/*
 * mpqs_sieve_c.c — Fast MPQS sieve + trial division in C
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o mpqs_sieve_c.so mpqs_sieve_c.c -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef __int128 i128;
typedef unsigned __int128 u128;

/* ============================================================================
 * Sieve one polynomial: fill sieve array with log(p) contributions
 * Uses uint16_t for sieve values to avoid overflow at large N.
 * Log scale: log2(p) * 16 (max ~800 for sum, fits uint16 easily).
 * ============================================================================ */
void sieve_poly(
    uint16_t *sieve,         /* sieve array [sz] — caller zeroes it */
    int sz,                  /* sieve size = 2*M */
    const int *fb_primes,    /* factor base primes [n_fb] */
    const int *fb_offsets1,  /* sieve offset 1 for each prime [n_fb], -1 = skip */
    const int *fb_offsets2,  /* sieve offset 2 for each prime [n_fb], -1 = skip */
    const uint16_t *fb_logp, /* log2(p)*16 for each prime [n_fb] */
    int n_fb                 /* number of FB primes */
)
{
    for (int i = 0; i < n_fb; i++) {
        int p = fb_primes[i];
        uint16_t lp = fb_logp[i];
        if (p < 32) continue;  /* skip small primes (handled by correction) */

        int o1 = fb_offsets1[i];
        if (o1 >= 0) {
            for (int j = o1; j < sz; j += p)
                sieve[j] += lp;
        }
        int o2 = fb_offsets2[i];
        if (o2 >= 0 && o2 != o1) {
            for (int j = o2; j < sz; j += p)
                sieve[j] += lp;
        }
    }
}

/* ============================================================================
 * Find sieve survivors (indices where sieve[i] >= threshold)
 * Returns count, fills out_indices.
 * ============================================================================ */
int find_survivors(
    const uint16_t *sieve,
    int sz,
    int threshold,
    int *out_indices,    /* output: survivor indices [max_out] */
    int max_out
)
{
    int count = 0;
    uint16_t thresh16 = (uint16_t)threshold;
    for (int i = 0; i < sz && count < max_out; i++) {
        if (sieve[i] >= thresh16) {
            out_indices[count++] = i;
        }
    }
    return count;
}

/* ============================================================================
 * Modular arithmetic helpers
 * ============================================================================ */

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

/* ============================================================================
 * Trial division routines
 * ============================================================================ */

/* Trial divide int64 value by factor base. Returns cofactor. */
static int64_t trial_divide_64(
    int64_t val,
    const int *fb_primes,
    int n_fb,
    int *exponents
)
{
    int64_t v = (val < 0) ? -val : val;

    /* Powers of 2 — use bit tricks */
    if (v > 0 && (v & 1) == 0) {
        int e = __builtin_ctzll((uint64_t)v);
        exponents[0] = e;
        v >>= e;
    }

    /* Remaining primes */
    for (int i = 1; i < n_fb; i++) {
        int64_t p = fb_primes[i];
        if (p * p > v) break;
        if (v % p == 0) {
            int e = 0;
            do {
                v /= p;
                e++;
            } while (v % p == 0);
            exponents[i] = e;
        }
    }

    return v;
}

/* Trial divide i128 value by factor base. Returns cofactor. */
static i128 trial_divide_128(
    i128 val,
    const int *fb_primes,
    int n_fb,
    int *exponents
)
{
    i128 v = (val < 0) ? -val : val;

    /* Powers of 2 */
    if (v > 0 && ((int64_t)v & 1) == 0) {
        while ((v & 1) == 0) {
            v >>= 1;
            exponents[0]++;
        }
    }

    /* Remaining primes */
    for (int i = 1; i < n_fb; i++) {
        i128 p = (i128)fb_primes[i];
        if (p * p > v) break;
        if (v % p == 0) {
            int e = 0;
            do {
                v /= p;
                e++;
            } while (v % p == 0);
            exponents[i] = e;
        }
    }

    return v;
}

/* ============================================================================
 * Batch trial division.
 * g(x) encoded as (hi64, lo64) pairs -> reconstructed as i128.
 * Returns number of smooth/partial-smooth candidates.
 * ============================================================================ */
int trial_divide_batch(
    const int64_t *gx_hi,
    const int64_t *gx_lo,
    int n_cand,
    const int *fb_primes,
    int n_fb,
    int64_t lp_bound,
    /* Output arrays */
    int *out_exponents,       /* flat [n_cand][n_fb] */
    int64_t *out_cofactors,
    int *out_signs,
    int *out_status,          /* 0=reject, 1=full smooth, 2=partial (LP) */
    int *out_n_smooth
)
{
    int n_good = 0;

    for (int ci = 0; ci < n_cand; ci++) {
        int *exps = out_exponents + (int64_t)ci * n_fb;
        memset(exps, 0, n_fb * sizeof(int));
        out_status[ci] = 0;
        out_cofactors[ci] = 0;
        out_signs[ci] = 0;

        /* Reconstruct g(x) as i128 */
        i128 gx = ((i128)gx_hi[ci] << 64) | (u128)(uint64_t)gx_lo[ci];

        if (gx == 0) continue;

        int sign = 0;
        i128 v;
        if (gx < 0) {
            sign = 1;
            v = -gx;
        } else {
            v = gx;
        }
        out_signs[ci] = sign;

        /* Choose fast or slow path */
        i128 cofactor;
        if (v <= (i128)0x7FFFFFFFFFFFFFFFLL) {
            cofactor = (i128)trial_divide_64((int64_t)v, fb_primes, n_fb, exps);
        } else {
            cofactor = trial_divide_128(v, fb_primes, n_fb, exps);
        }

        if (cofactor == 1) {
            out_status[ci] = 1;
            out_cofactors[ci] = 1;
            n_good++;
        } else if (cofactor <= (i128)lp_bound && cofactor > 1) {
            int64_t cof64 = (int64_t)cofactor;
            /* Check if in FB */
            int found = 0;
            {
                int lo = 0, hi = n_fb - 1;
                while (lo <= hi) {
                    int mid = (lo + hi) >> 1;
                    if (fb_primes[mid] == cof64) {
                        exps[mid]++;
                        out_cofactors[ci] = 1;
                        out_status[ci] = 1;
                        n_good++;
                        found = 1;
                        break;
                    } else if (fb_primes[mid] < cof64) lo = mid + 1;
                    else hi = mid - 1;
                }
            }
            if (!found && is_prime64(cof64)) {
                out_cofactors[ci] = cof64;
                out_status[ci] = 2;
                n_good++;
            }
        }
    }

    *out_n_smooth = n_good;
    return n_good;
}
