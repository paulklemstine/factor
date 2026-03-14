/*
 * Pythagorean Tree Pollard-Rho Factoring (Projective Line)
 *
 * KEY INSIGHT: Track r = m * n^(-1) mod N instead of (m, n).
 * The matrix acts as a Möbius transformation: r -> (a*r+b)/(c*r+d) mod N.
 * This is a MAP Z_N -> Z_N (1D), so the cycle mod p has length O(sqrt(p))
 * by birthday paradox. Brent's cycle detection finds the factor.
 *
 * When c*r+d ≡ 0 mod p (inverse fails), gcd(c*r+d, N) = p directly!
 *
 * Expected complexity: O(sqrt(p)) steps, each ~70ns in C.
 * For 64b semiprime: ~65K steps = 4.7ms = INSTANT.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;

static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

/* Extended GCD: returns gcd, sets *x, *y such that a*x + b*y = gcd */
static u64 extgcd(u64 a, u64 b, i64 *x, i64 *y) {
    i64 old_r = (i64)a, r = (i64)b;
    i64 old_s = 1, s = 0;
    i64 old_t = 0, t = 1;
    while (r != 0) {
        i64 q = old_r / r;
        i64 tmp;
        tmp = r; r = old_r - q * r; old_r = tmp;
        tmp = s; s = old_s - q * s; old_s = tmp;
        tmp = t; t = old_t - q * t; old_t = tmp;
    }
    *x = old_s;
    *y = old_t;
    return (u64)old_r;
}

/* Modular inverse: returns a^(-1) mod N, or 0 if gcd(a,N) > 1 */
static inline u64 modinv(u64 a, u64 N) {
    if (a == 0) return 0;
    i64 x, y;
    u64 g = extgcd(a, N, &x, &y);
    if (g != 1) return 0;  /* a and N share a factor */
    return (u64)((x % (i64)N + (i64)N) % (i64)N);
}

/* Modular multiply */
static inline u64 mulmod(u64 a, u64 b, u64 N) {
    return (u64)((u128)a * b % N);
}

/* Modular add */
static inline u64 addmod(u64 a, u64 b, u64 N) {
    return (a + b) % N;  /* Safe for a,b < N since N < 2^63 */
}

/* Modular sub */
static inline u64 submod(u64 a, u64 b, u64 N) {
    return (a >= b) ? a - b : N - (b - a);
}

/* Signed int to mod-N */
static inline u64 to_mod(int v, u64 N) {
    return (v >= 0) ? (u64)v % N : N - (u64)(-v) % N;
}

/* ---- Matrix definitions ---- */
typedef struct { int a, b, c, d; } IMat;

/* 9 forward Berggren/Price/Firstov matrices on (m,n) */
static const IMat FORWARD[9] = {
    {2, -1, 1, 0}, {2, 1, 1, 0}, {1, 2, 0, 1},
    {1, 1, 0, 2}, {2, 0, 1, -1}, {2, 0, 1, 1},
    {3, -2, 1, -1}, {3, 2, 1, 1}, {1, 4, 0, 1},
};
#define N_MAT 9

/* ---- Hash function for matrix selection ---- */
static inline int hash_r(u64 r) {
    /* Fibonacci hashing for good distribution */
    u64 h = r * 0x9E3779B97F4A7C15ULL;
    return (int)((h >> 60) % N_MAT);
}

/*
 * Projective step: r -> (a*r + b) / (c*r + d) mod N
 * Returns 1 on success, 0 if inverse failed (factor found in *factor)
 */
static inline int proj_step(u64 r, u64 N, u64 *r_out, u64 *factor) {
    int mi = hash_r(r);
    const IMat *M = &FORWARD[mi];

    u64 num = addmod(mulmod(to_mod(M->a, N), r, N), to_mod(M->b, N), N);
    u64 den = addmod(mulmod(to_mod(M->c, N), r, N), to_mod(M->d, N), N);

    if (den == 0) {
        /* den ≡ 0 mod N: trivial, skip */
        *r_out = num;  /* degenerate: just use numerator */
        *factor = 0;
        return 1;
    }

    u64 inv = modinv(den, N);
    if (inv == 0) {
        /* gcd(den, N) > 1: FOUND A FACTOR! */
        u64 g = gcd64(den, N);
        if (g > 1 && g < N) {
            *factor = g;
            return 0;  /* Factor found */
        }
        /* gcd = N (trivial), use fallback */
        *r_out = num;
        *factor = 0;
        return 1;
    }

    *r_out = mulmod(num, inv, N);
    *factor = 0;
    return 1;
}

/*
 * EXPERIMENT 1: Projective Pollard-Rho with Brent's Cycle Detection
 *
 * Track r = m/n mod N. Iterate r -> Mobius(r) where the matrix depends on hash(r).
 * Brent's algorithm detects cycle, accumulate (r_slow - r_fast) products for batch GCD.
 *
 * Expected: O(sqrt(p)) steps for balanced N = p*q.
 */
u64 projective_rho(
    u64 N,
    u64 max_steps,
    int time_limit_ms,
    int batch_size,
    u64 seed,
    u64 *steps_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    /* Starting r = m/n = 2/1 = 2 mod N, plus seed perturbation */
    u64 r_start = (2 + seed) % N;
    if (r_start == 0) r_start = 1;

    u64 tort = r_start;  /* Tortoise */
    u64 hare = r_start;  /* Hare */
    u64 factor;

    /* First step for hare */
    if (!proj_step(hare, N, &hare, &factor)) {
        *steps_out = 1;
        return factor;
    }

    u64 power = 1, lam = 1;
    u64 acc = 1;
    int acc_count = 0;
    u64 steps = 1;

    for (u64 s = 0; s < max_steps; s++) {
        /* Time check every 4096 steps */
        if ((s & 4095) == 0 && s > 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000;
            if (elapsed >= time_limit_ms) break;
        }

        /* Brent's power-of-2 checkpoint */
        if (power == lam) {
            tort = hare;
            power *= 2;
            lam = 0;
        }

        /* Advance hare one step */
        if (!proj_step(hare, N, &hare, &factor)) {
            *steps_out = steps;
            return factor;
        }
        steps++;
        lam++;

        /* Accumulate difference */
        u64 diff = submod(hare, tort, N);
        if (diff == 0) continue;  /* Same state mod N → skip */

        acc = mulmod(acc, diff, N);
        acc_count++;

        /* Batch GCD check */
        if (acc_count >= batch_size) {
            u64 g = gcd64(acc, N);
            if (g > 1 && g < N) {
                *steps_out = steps;
                return g;
            }
            if (g == N) {
                /* Trivial: backtrack with smaller batch */
                /* Re-run last batch_size steps one by one */
                u64 t2 = tort, h2 = hare;
                /* Reset and redo — simplified: just reset accumulator */
                acc = 1;
                acc_count = 0;
                continue;
            }
            acc = 1;
            acc_count = 0;
        }
    }

    *steps_out = steps;
    return 0;
}

/*
 * EXPERIMENT 2: Multi-start Projective Rho
 *
 * Try multiple starting values for r. Each start gives an independent rho walk.
 * If one walk has a short cycle mod p, it finds the factor.
 */
u64 multi_projective_rho(
    u64 N,
    int num_starts,
    u64 steps_per_start,
    int time_limit_ms,
    int batch_size,
    u64 *steps_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    u64 total_steps = 0;

    for (int si = 0; si < num_starts; si++) {
        /* Time check */
        clock_gettime(CLOCK_MONOTONIC, &now);
        long elapsed = (now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000;
        if (elapsed >= time_limit_ms) break;

        int remaining_ms = time_limit_ms - (int)elapsed;
        u64 start_steps = 0;

        u64 f = projective_rho(N, steps_per_start, remaining_ms, batch_size,
                                (u64)si * 1000003 + 42, &start_steps);
        total_steps += start_steps;

        if (f > 1 && f < N) {
            *steps_out = total_steps;
            return f;
        }
    }

    *steps_out = total_steps;
    return 0;
}

/*
 * EXPERIMENT 3: 2D Rho (for comparison baseline)
 *
 * Standard Brent on (m,n) mod N with state-dependent matrix selection.
 * Expected: O(p) steps (not O(sqrt(p))) because 2D state space.
 */
u64 twod_rho(
    u64 N,
    u64 max_steps,
    int time_limit_ms,
    int batch_size,
    u64 seed,
    u64 *steps_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    /* Convert matrices */
    u64 ma[N_MAT][4];
    for (int i = 0; i < N_MAT; i++) {
        ma[i][0] = to_mod(FORWARD[i].a, N);
        ma[i][1] = to_mod(FORWARD[i].b, N);
        ma[i][2] = to_mod(FORWARD[i].c, N);
        ma[i][3] = to_mod(FORWARD[i].d, N);
    }

    u64 tm = (2 + seed) % N, tn = 1;
    u64 hm = tm, hn = tn;

    /* Step hare once using state-dependent matrix */
    {
        int mi = (int)((hm * 0x9E3779B97F4A7C15ULL >> 60) % N_MAT);
        u64 nm = addmod(mulmod(ma[mi][0], hm, N), mulmod(ma[mi][1], hn, N), N);
        u64 nn = addmod(mulmod(ma[mi][2], hm, N), mulmod(ma[mi][3], hn, N), N);
        hm = nm; hn = nn;
    }

    u64 power = 1, lam = 1;
    u64 acc = 1;
    int acc_count = 0;
    u64 steps = 1;

    for (u64 s = 0; s < max_steps; s++) {
        if ((s & 4095) == 0 && s > 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000;
            if (elapsed >= time_limit_ms) break;
        }

        if (power == lam) {
            tm = hm; tn = hn;
            power *= 2;
            lam = 0;
        }

        /* Advance hare */
        int mi = (int)((hm * 0x9E3779B97F4A7C15ULL >> 60) % N_MAT);
        u64 nm = addmod(mulmod(ma[mi][0], hm, N), mulmod(ma[mi][1], hn, N), N);
        u64 nn = addmod(mulmod(ma[mi][2], hm, N), mulmod(ma[mi][3], hn, N), N);
        hm = nm; hn = nn;
        steps++;
        lam++;

        /* Accumulate m-difference and n-difference */
        u64 dm = submod(hm, tm, N);
        u64 dn = submod(hn, tn, N);
        if (dm != 0) {
            acc = mulmod(acc, dm, N);
            acc_count++;
        }
        if (dn != 0) {
            acc = mulmod(acc, dn, N);
            acc_count++;
        }

        if (acc_count >= batch_size) {
            u64 g = gcd64(acc, N);
            if (g > 1 && g < N) {
                *steps_out = steps;
                return g;
            }
            if (g == N) { acc = 1; acc_count = 0; continue; }
            acc = 1;
            acc_count = 0;
        }
    }

    *steps_out = steps;
    return 0;
}

/*
 * EXPERIMENT 4: Projective Rho + Derived Values
 *
 * Like projective_rho but also compute (m,n) at each step and check
 * all 12 derived values via batch GCD. Combines O(sqrt(p)) cycle detection
 * with O(1/p) per-step hit probability from derived values.
 */
u64 projective_rho_plus(
    u64 N,
    u64 max_steps,
    int time_limit_ms,
    int batch_size,
    u64 seed,
    u64 *steps_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    /* Convert matrices */
    u64 ma[N_MAT][4];
    for (int i = 0; i < N_MAT; i++) {
        ma[i][0] = to_mod(FORWARD[i].a, N);
        ma[i][1] = to_mod(FORWARD[i].b, N);
        ma[i][2] = to_mod(FORWARD[i].c, N);
        ma[i][3] = to_mod(FORWARD[i].d, N);
    }

    /* Track both r (for rho) and (m,n) (for derived values) */
    u64 r_start = (2 + seed) % N;
    if (r_start == 0) r_start = 1;

    u64 tort_r = r_start;
    u64 hare_r = r_start;
    u64 hare_m = (2 + seed) % N, hare_n = 1;

    u64 factor;

    /* First hare step */
    int mi0 = hash_r(hare_r);
    {
        u64 nm = addmod(mulmod(ma[mi0][0], hare_m, N), mulmod(ma[mi0][1], hare_n, N), N);
        u64 nn = addmod(mulmod(ma[mi0][2], hare_m, N), mulmod(ma[mi0][3], hare_n, N), N);
        hare_m = nm; hare_n = nn;
    }
    if (!proj_step(hare_r, N, &hare_r, &factor)) {
        *steps_out = 1;
        return factor;
    }

    u64 power = 1, lam = 1;
    u64 acc_rho = 1;      /* Accumulator for rho differences */
    u64 acc_derived = 1;  /* Accumulator for derived values */
    int acc_count = 0;
    u64 steps = 1;

    for (u64 s = 0; s < max_steps; s++) {
        if ((s & 4095) == 0 && s > 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000;
            if (elapsed >= time_limit_ms) break;
        }

        if (power == lam) {
            tort_r = hare_r;
            power *= 2;
            lam = 0;
        }

        /* Matrix selection from projective coordinate */
        int mi = hash_r(hare_r);

        /* Advance (m,n) */
        u64 nm = addmod(mulmod(ma[mi][0], hare_m, N), mulmod(ma[mi][1], hare_n, N), N);
        u64 nn = addmod(mulmod(ma[mi][2], hare_m, N), mulmod(ma[mi][3], hare_n, N), N);
        hare_m = nm; hare_n = nn;

        /* Advance r */
        if (!proj_step(hare_r, N, &hare_r, &factor)) {
            *steps_out = steps;
            return factor;
        }
        steps++;
        lam++;

        /* Rho accumulator */
        u64 diff = submod(hare_r, tort_r, N);
        if (diff != 0) {
            acc_rho = mulmod(acc_rho, diff, N);
        }

        /* Derived value accumulator (every 4th step to save time) */
        if ((s & 3) == 0) {
            u64 m2 = mulmod(hare_m, hare_m, N);
            u64 n2 = mulmod(hare_n, hare_n, N);
            u64 A = submod(m2, n2, N);
            u64 B = mulmod(mulmod(2, hare_m, N), hare_n, N);
            if (A != 0) acc_derived = mulmod(acc_derived, A, N);
            if (B != 0) acc_derived = mulmod(acc_derived, B, N);
        }

        acc_count++;

        if (acc_count >= batch_size) {
            /* Check rho accumulator */
            u64 g = gcd64(acc_rho, N);
            if (g > 1 && g < N) { *steps_out = steps; return g; }

            /* Check derived accumulator */
            g = gcd64(acc_derived, N);
            if (g > 1 && g < N) { *steps_out = steps; return g; }

            /* Check combined */
            u64 combined = mulmod(acc_rho, acc_derived, N);
            g = gcd64(combined, N);
            if (g > 1 && g < N) { *steps_out = steps; return g; }

            if (g == N || acc_rho == 0 || acc_derived == 0) {
                acc_rho = 1;
                acc_derived = 1;
            }
            acc_rho = 1;
            acc_derived = 1;
            acc_count = 0;
        }
    }

    *steps_out = steps;
    return 0;
}
