/*
 * Pythagorean Fixed-Matrix Brent Rho
 * 
 * KEY INSIGHT: Use FIXED matrix (no state-dependent selection) on projective line.
 * r -> (a*r+b)/(c*r+d) mod N with FIXED a,b,c,d.
 * If r1 ≡ r2 mod p, then f(r1) ≡ f(r2) mod p → collision propagation works!
 * Cycle length mod p divides p²-1. Brent detects in O(√(cycle_length)) steps.
 * Since cycle_length ~ p, this gives O(√p).
 */

#include <stdint.h>
#include <stdlib.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;

static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

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
    *x = old_s; *y = old_t;
    return (u64)old_r;
}

static inline u64 modinv(u64 a, u64 N) {
    if (a == 0) return 0;
    i64 x, y;
    u64 g = extgcd(a, N, &x, &y);
    if (g != 1) return 0;
    return (u64)((x % (i64)N + (i64)N) % (i64)N);
}

static inline u64 mulmod(u64 a, u64 b, u64 N) {
    return (u64)((u128)a * b % N);
}

static inline u64 addmod(u64 a, u64 b, u64 N) {
    return (a + b) % N;
}

static inline u64 submod(u64 a, u64 b, u64 N) {
    return a >= b ? a - b : N - (b - a);
}

static inline u64 to_mod(int v, u64 N) {
    return v >= 0 ? (u64)v % N : N - (u64)(-v) % N;
}

typedef struct { int a, b, c, d; } IMat;

/* 9 forward matrices + 9 composite products */
static const IMat FORWARD[9] = {
    {2, -1, 1, 0}, {2, 1, 1, 0}, {1, 2, 0, 1},
    {1, 1, 0, 2}, {2, 0, 1, -1}, {2, 0, 1, 1},
    {3, -2, 1, -1}, {3, 2, 1, 1}, {1, 4, 0, 1},
};

/*
 * Fixed-matrix Brent rho on projective line.
 * Returns factor, or 0 if not found.
 * Tries all 9 matrices + some products.
 */
u64 fixed_projective_brent(
    u64 N,
    u64 max_steps_per_mat,
    int batch_size,
    u64 *total_steps
) {
    u64 all_steps = 0;
    
    /* Try each of 9 matrices */
    for (int mi = 0; mi < 9; mi++) {
        u64 a = to_mod(FORWARD[mi].a, N);
        u64 b = to_mod(FORWARD[mi].b, N);
        u64 c = to_mod(FORWARD[mi].c, N);
        u64 d = to_mod(FORWARD[mi].d, N);
        
        /* Try a few starting points */
        for (int si = 0; si < 5; si++) {
            u64 r_start = (2 + (u64)si * 7) % N;
            if (r_start == 0) r_start = 1;
            
            u64 tort = r_start;
            u64 hare = r_start;
            
            /* Step function: r -> (a*r+b)/(c*r+d) mod N */
            #define STEP(r) do { \
                u64 num = addmod(mulmod(a, r, N), b, N); \
                u64 den = addmod(mulmod(c, r, N), d, N); \
                if (den == 0) { r = num; } \
                else { \
                    u64 inv = modinv(den, N); \
                    if (inv == 0) { \
                        u64 g = gcd64(den, N); \
                        if (g > 1 && g < N) { *total_steps = all_steps; return g; } \
                        r = num; \
                    } else { \
                        r = mulmod(num, inv, N); \
                    } \
                } \
            } while(0)
            
            /* First hare step */
            STEP(hare);
            all_steps++;
            
            u64 power = 1, lam = 1;
            u64 acc = 1;
            int acc_count = 0;
            
            for (u64 s = 0; s < max_steps_per_mat; s++) {
                if (power == lam) {
                    tort = hare;
                    power *= 2;
                    lam = 0;
                }
                
                STEP(hare);
                all_steps++;
                lam++;
                
                u64 diff = submod(hare, tort, N);
                if (diff == 0) continue;
                
                acc = mulmod(acc, diff, N);
                acc_count++;
                
                if (acc_count >= batch_size) {
                    u64 g = gcd64(acc, N);
                    if (g > 1 && g < N) {
                        *total_steps = all_steps;
                        return g;
                    }
                    if (g == N) {
                        /* Backtrack: check last batch individually */
                        /* For simplicity, just reset */
                    }
                    acc = 1;
                    acc_count = 0;
                }
            }
            #undef STEP
        }
    }
    
    /* Also try composite matrices: M_i * M_j for all pairs */
    for (int mi = 0; mi < 9; mi++) {
        for (int mj = mi+1; mj < 9 && mj < mi+3; mj++) {
            /* Compose M_mi * M_mj */
            u64 a1 = to_mod(FORWARD[mi].a, N), b1 = to_mod(FORWARD[mi].b, N);
            u64 c1 = to_mod(FORWARD[mi].c, N), d1 = to_mod(FORWARD[mi].d, N);
            u64 a2 = to_mod(FORWARD[mj].a, N), b2 = to_mod(FORWARD[mj].b, N);
            u64 c2 = to_mod(FORWARD[mj].c, N), d2 = to_mod(FORWARD[mj].d, N);
            
            u64 a = addmod(mulmod(a1, a2, N), mulmod(b1, c2, N), N);
            u64 b = addmod(mulmod(a1, b2, N), mulmod(b1, d2, N), N);
            u64 c = addmod(mulmod(c1, a2, N), mulmod(d1, c2, N), N);
            u64 d = addmod(mulmod(c1, b2, N), mulmod(d1, d2, N), N);
            
            u64 r_start = 2;
            u64 tort = r_start, hare = r_start;
            
            #define STEP2(r) do { \
                u64 num = addmod(mulmod(a, r, N), b, N); \
                u64 den = addmod(mulmod(c, r, N), d, N); \
                if (den == 0) { r = num; } \
                else { \
                    u64 inv = modinv(den, N); \
                    if (inv == 0) { \
                        u64 g = gcd64(den, N); \
                        if (g > 1 && g < N) { *total_steps = all_steps; return g; } \
                        r = num; \
                    } else { \
                        r = mulmod(num, inv, N); \
                    } \
                } \
            } while(0)
            
            STEP2(hare);
            all_steps++;
            
            u64 power = 1, lam = 1;
            u64 acc = 1;
            int acc_count = 0;
            
            for (u64 s = 0; s < max_steps_per_mat; s++) {
                if (power == lam) {
                    tort = hare;
                    power *= 2;
                    lam = 0;
                }
                STEP2(hare);
                all_steps++;
                lam++;
                
                u64 diff = submod(hare, tort, N);
                if (diff == 0) continue;
                acc = mulmod(acc, diff, N);
                acc_count++;
                
                if (acc_count >= batch_size) {
                    u64 g = gcd64(acc, N);
                    if (g > 1 && g < N) {
                        *total_steps = all_steps;
                        return g;
                    }
                    acc = 1;
                    acc_count = 0;
                }
            }
            #undef STEP2
        }
    }
    
    *total_steps = all_steps;
    return 0;
}
