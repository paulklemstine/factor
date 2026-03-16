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
 * For values > 127 bits, uses (extra_hi, hi, lo) with 3rd array.
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

/* ============================================================================
 * Extended batch trial division for values up to 192 bits.
 * g(x) encoded as (hi64, mid64, lo64) triples.
 * ============================================================================ */
int trial_divide_batch_wide(
    const int64_t *gx_hi,     /* bits [128..191] */
    const int64_t *gx_mid,    /* bits [64..127]  */
    const int64_t *gx_lo,     /* bits [0..63]    */
    int n_cand,
    const int *fb_primes,
    int n_fb,
    int64_t lp_bound,
    int *out_exponents,
    int64_t *out_cofactors,
    int *out_signs,
    int *out_status,
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

        /* Reconstruct as unsigned 192-bit value using two i128s */
        /* We handle sign separately. Reconstruct absolute value. */
        u128 lo128 = ((u128)(uint64_t)gx_mid[ci] << 64) | (u128)(uint64_t)gx_lo[ci];
        int64_t hi_word = gx_hi[ci];
        int sign = 0;

        /* Check sign: if hi_word < 0 or (hi_word == 0 && mid < 0 in 2s complement)
         * For simplicity, the Python caller should pass absolute value + sign. */
        if (hi_word < 0) {
            /* Negate the 192-bit value: ~lo128 + 1, carry into hi */
            sign = 1;
            u128 neg_lo = ~lo128 + 1;
            int carry = (neg_lo == 0) ? 1 : 0;
            lo128 = neg_lo;
            hi_word = ~hi_word + carry;
        }
        out_signs[ci] = sign;

        /* Trial divide: start with hi:lo as a wide number.
         * First reduce: divide by small primes until it fits in 128 bits. */
        uint64_t hi = (uint64_t)hi_word;

        /* Powers of 2 first */
        if (hi == 0 && lo128 == 0) continue;
        if ((lo128 & 1) == 0) {
            /* Count trailing zeros in lo128 */
            while ((lo128 & 1) == 0 && (hi || lo128)) {
                lo128 >>= 1;
                if (hi & 1) lo128 |= ((u128)1 << 127);
                hi >>= 1;
                exps[0]++;
            }
        }

        /* Divide by FB primes until hi == 0 (value fits in 128 bits) */
        for (int i = 1; i < n_fb && hi > 0; i++) {
            uint64_t p = (uint64_t)fb_primes[i];
            /* 192-bit mod p: ((hi * 2^128 + lo128) mod p) */
            /* = ((hi mod p) * (2^128 mod p) + lo128 mod p) mod p */
            /* 2^128 mod p = (2^64 mod p)^2 mod p */
            uint64_t r128 = 1;
            {
                uint64_t tmp = 1;
                for (int b = 0; b < 128; b++) {
                    if (b == 64) r128 = tmp;
                    tmp = mulmod64(tmp, 2, p);
                }
                r128 = tmp;  /* 2^128 mod p */
            }
            uint64_t rem = (mulmod64(hi % p, r128, p) + (uint64_t)(lo128 % p)) % p;
            if (rem == 0) {
                /* Divide: full 192-bit / p */
                do {
                    /* long division: [hi : lo128] / p */
                    u128 full_hi = (u128)hi;
                    u128 q_hi = full_hi / p;
                    u128 r_hi = full_hi % p;
                    u128 mid_val = (r_hi << 64) | (lo128 >> 64);
                    u128 q_mid = mid_val / p;
                    u128 r_mid = mid_val % p;
                    u128 lo_val = (r_mid << 64) | (lo128 & 0xFFFFFFFFFFFFFFFFULL);
                    u128 q_lo = lo_val / p;

                    hi = (uint64_t)q_hi;
                    lo128 = (q_mid << 64) | (u128)(uint64_t)q_lo;
                    exps[i]++;

                    /* Check if still divisible */
                    if (hi == 0) {
                        /* Now fits in 128 bits, use fast path below */
                        break;
                    }
                    rem = (mulmod64(hi % p, r128, p) + (uint64_t)(lo128 % p)) % p;
                } while (rem == 0);
            }
        }

        /* Now value should fit in i128 (hi == 0) */
        if (hi != 0) {
            /* Still > 128 bits after FB trial division — skip */
            continue;
        }

        /* Continue with standard 128-bit trial division for remaining primes */
        i128 v = (i128)lo128;
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
            int found = 0;
            {
                int lo2 = 0, hi2 = n_fb - 1;
                while (lo2 <= hi2) {
                    int mid = (lo2 + hi2) >> 1;
                    if (fb_primes[mid] == cof64) {
                        exps[mid]++;
                        out_cofactors[ci] = 1;
                        out_status[ci] = 1;
                        n_good++;
                        found = 1;
                        break;
                    } else if (fb_primes[mid] < cof64) lo2 = mid + 1;
                    else hi2 = mid - 1;
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

/* ============================================================================
 * Incremental offset update for Gray code poly switching.
 * Updates off1/off2 arrays in-place: off[i] = (off[i] +/- delta[i]) % p[i]
 * Skips entries where off[i] < 0 or is_a_prime[i] != 0.
 * direction: +1 = add, -1 = subtract
 * ============================================================================ */
void update_offsets(
    int *off1,
    int *off2,
    const int *delta,
    const int *fb_primes,
    const int *is_a_prime,
    int n_fb,
    int direction
)
{
    if (direction > 0) {
        for (int i = 0; i < n_fb; i++) {
            if (is_a_prime[i]) continue;
            int p = fb_primes[i];
            int d = delta[i];
            if (off1[i] >= 0) {
                off1[i] += d;
                if (off1[i] >= p) off1[i] -= p;
            }
            if (off2[i] >= 0) {
                off2[i] += d;
                if (off2[i] >= p) off2[i] -= p;
            }
        }
    } else {
        for (int i = 0; i < n_fb; i++) {
            if (is_a_prime[i]) continue;
            int p = fb_primes[i];
            int d = delta[i];
            if (off1[i] >= 0) {
                off1[i] -= d;
                if (off1[i] < 0) off1[i] += p;
            }
            if (off2[i] >= 0) {
                off2[i] -= d;
                if (off2[i] < 0) off2[i] += p;
            }
        }
    }
}
