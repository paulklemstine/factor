/*
 * pollard_rho_c.c — Fast Pollard rho for DLP cofactor splitting
 *
 * Brent's cycle detection with batch GCD, using __int128 for
 * overflow-safe modular multiplication of 64-bit values.
 *
 * Compile: gcc -O3 -shared -fPIC -o pollard_rho_c.so pollard_rho_c.c
 */

#include <stdint.h>
#include <stdlib.h>

typedef unsigned __int128 u128;

static inline uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)(((u128)a * (u128)b) % (u128)m);
}

static inline uint64_t addmod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t r = a + b;
    if (r >= m || r < a) r -= m;  /* handle overflow */
    return r;
}

static uint64_t gcd64(uint64_t a, uint64_t b) {
    while (b) {
        uint64_t t = b;
        b = a % b;
        a = t;
    }
    return a;
}

static inline uint64_t absdiff(uint64_t a, uint64_t b) {
    return a > b ? a - b : b - a;
}

/*
 * Brent's rho with batch GCD.
 * Returns a non-trivial factor of n, or 0 if not found.
 * n must be > 1, odd, and composite.
 */
static uint64_t rho_brent(uint64_t n, uint64_t c, int limit) {
    uint64_t y = 2, x = 2, ys = 2, q = 1, g = 1;
    int r = 1, k, iters = 0;

    while (g == 1 && iters < limit) {
        x = y;
        for (int i = 0; i < r && iters < limit; i++) {
            y = addmod(mulmod(y, y, n), c, n);
            iters++;
        }
        k = 0;
        while (k < r && g == 1 && iters < limit) {
            ys = y;
            int batch = r - k;
            if (batch > 128) batch = 128;
            q = 1;
            for (int i = 0; i < batch && iters < limit; i++) {
                y = addmod(mulmod(y, y, n), c, n);
                uint64_t diff = absdiff(x, y);
                if (diff == 0) continue;
                q = mulmod(q, diff, n);
                iters++;
            }
            if (q == 0) { g = n; break; }
            g = gcd64(q, n);
            k += batch;
        }
        r *= 2;
    }

    if (g == n) {
        /* Backtrack from ys */
        g = 1;
        while (g == 1) {
            ys = addmod(mulmod(ys, ys, n), c, n);
            g = gcd64(absdiff(x, ys), n);
        }
    }

    if (g > 1 && g < n) return g;
    return 0;
}

/*
 * Split a composite n into a non-trivial factor.
 * Tries multiple c values. Returns factor or 0.
 *
 * limit: max iterations per c value (recommend 3000-5000)
 */
uint64_t pollard_rho_split(uint64_t n, int limit) {
    if (n <= 1) return 0;
    if ((n & 1) == 0) return 2;
    if (n % 3 == 0) return 3;

    static const uint64_t c_vals[] = {1, 3, 5, 7, 11, 13, 17, 19};
    int n_c = sizeof(c_vals) / sizeof(c_vals[0]);

    for (int i = 0; i < n_c; i++) {
        uint64_t f = rho_brent(n, c_vals[i], limit);
        if (f > 1) return f;
    }
    return 0;
}

/*
 * Batch split: process multiple cofactors at once.
 * cofactors[i] -> results[i] (factor or 0)
 * Returns number of successful splits.
 */
int batch_pollard_rho(uint64_t *cofactors, uint64_t *results,
                      int count, int limit) {
    int successes = 0;
    for (int i = 0; i < count; i++) {
        results[i] = pollard_rho_split(cofactors[i], limit);
        if (results[i] > 0) successes++;
    }
    return successes;
}
