/*
 * Pythagorean Tree Beam Search — Full C implementation
 *
 * Entire beam search loop in C including hash-based dedup.
 * Python calls beam_search_full() and gets back the factor.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

typedef long long i64;
typedef unsigned long long u64;

/* ===== GCD ===== */
static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

/* ===== Hash table for (A,B,C) dedup ===== */
/* Open-addressing with linear probing. Stores 64-bit hashes. */

typedef struct {
    u64 *table;
    int capacity;
    int count;
    int mask;
} HashSet;

static void hs_init(HashSet *hs, int capacity) {
    /* Round up to power of 2 */
    int cap = 1;
    while (cap < capacity) cap <<= 1;
    hs->table = (u64 *)calloc(cap, sizeof(u64));
    hs->capacity = cap;
    hs->count = 0;
    hs->mask = cap - 1;
}

static void hs_free(HashSet *hs) {
    free(hs->table);
}

static u64 hash_triple(i64 a, i64 b, i64 c) {
    /* FNV-1a style hash */
    u64 h = 14695981039346656037ULL;
    h ^= (u64)a; h *= 1099511628211ULL;
    h ^= (u64)b; h *= 1099511628211ULL;
    h ^= (u64)c; h *= 1099511628211ULL;
    /* Ensure non-zero (0 = empty slot) */
    return h | 1;
}

/* Returns 1 if already present or table full, 0 if newly inserted */
static int hs_insert(HashSet *hs, u64 h) {
    /* Refuse insert if load factor > 75% */
    if (hs->count >= (hs->capacity * 3 / 4)) return 1;
    int idx = (int)(h & hs->mask);
    int probes = 0;
    while (probes < 64) {  /* max 64 probes to avoid infinite loop */
        u64 existing = hs->table[idx];
        if (existing == 0) {
            hs->table[idx] = h;
            hs->count++;
            return 0; /* new */
        }
        if (existing == h) return 1; /* duplicate */
        idx = (idx + 1) & hs->mask;
        probes++;
    }
    return 1; /* treat as duplicate if too many probes */
}

/* ===== Beam entry ===== */
typedef struct {
    i64 A, B, C;
    u64 scent_fp; /* fixed-point scent * 1e15 */
} BeamEntry;

static int cmp_beam(const void *a, const void *b) {
    u64 sa = ((const BeamEntry *)a)->scent_fp;
    u64 sb = ((const BeamEntry *)b)->scent_fp;
    if (sa < sb) return -1;
    if (sa > sb) return 1;
    return 0;
}

/* ===== Scent + GCD check ===== */
/* Returns factor if found (>1), else 0. Sets *scent_out. */
static u64 check_scent(i64 A, i64 B, i64 C, u64 N, u64 *scent_out) {
    if (A <= 0 || B <= 0 || C <= 0) { *scent_out = (u64)1e15; return 0; }

    i64 diff = C - B;
    if (diff < 1) diff = 1;
    i64 summ = C + B;

    double best = 1.0;
    i64 bases[5] = {diff, summ, A, C, B};

    for (int i = 0; i < 5; i++) {
        i64 base = bases[i];
        if (base <= 0) continue;
        u64 ubase = (u64)base;
        u64 g = gcd64(ubase, N);
        if (g > 1 && g < N) {
            *scent_out = 0;
            return g;
        }
        u64 r = N % ubase;
        double s;
        if (r < ubase - r)
            s = (double)r / (double)ubase;
        else
            s = (double)(ubase - r) / (double)ubase;
        if (s < best) best = s;
    }

    *scent_out = (u64)(best * 1e15);
    return 0;
}

/* ===== LCG random ===== */
static u64 rng_state = 12345678901234567ULL;

static u64 rng_next(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return rng_state;
}

static void rng_seed(u64 s) {
    rng_state = s | 1;
}

/* ===== Main beam search ===== */

/*
 * beam_search_full: Complete diversified beam search in C.
 *
 * N: semiprime to factor
 * matrices: n_mat x 9 ints (3x3 row-major)
 * n_mat: number of matrices
 * beam_width: max beam size
 * max_steps: max iterations
 * time_limit_ms: time limit in milliseconds
 * n_clusters: diversity clusters
 * diversity_frac: fraction of beam reserved for random diversity (0-100 = percent)
 * restart_patience: steps stuck before restart
 * seed: random seed
 *
 * Returns: factor if found, else 0
 * *steps_out: steps completed
 * *nodes_out: total nodes visited
 */
u64 beam_search_full(
    u64 N,
    const int *matrices,
    int n_mat,
    int beam_width,
    int max_steps,
    int time_limit_ms,
    int n_clusters,
    int diversity_frac,   /* percent: 0-100 */
    int restart_patience,
    u64 seed,
    int *steps_out,
    int *nodes_out
) {
    rng_seed(seed);
    struct timespec ts_start, ts_now;
    clock_gettime(CLOCK_MONOTONIC, &ts_start);

    double log2_N = log2((double)N);
    double log2_sqrt_N = log2_N / 2.0;

    int cluster_capacity = beam_width / n_clusters;
    if (cluster_capacity < 3) cluster_capacity = 3;
    int forced_random_count = beam_width * diversity_frac / 100;
    int greedy_count = beam_width - forced_random_count;

    /* Hash table: size based on time budget.
     * At ~2M nodes/sec, 60s = 120M nodes. Use 2x for headroom.
     * Cap at 256M entries (2GB). Use time_limit to estimate. */
    int expected_nodes = (int)((double)time_limit_ms / 1000.0 * 3000000.0);
    int ht_cap = expected_nodes * 2;
    if (ht_cap < 1024) ht_cap = 1024;
    if (ht_cap > 256 * 1024 * 1024) ht_cap = 256 * 1024 * 1024;
    HashSet visited;
    hs_init(&visited, ht_cap);

    /* Beam and candidate buffers */
    int max_cands = beam_width * n_mat + 256;
    BeamEntry *beam = (BeamEntry *)malloc(beam_width * sizeof(BeamEntry));
    BeamEntry *candidates = (BeamEntry *)malloc(max_cands * sizeof(BeamEntry));
    int *cluster_counts = (int *)calloc(n_clusters * 5, sizeof(int));

    /* Init beam from root + random walks */
    int beam_size = 0;
    i64 root_A = 3, root_B = 4, root_C = 5;
    int init_depths[] = {0, 2, 4, 6, 8, 10, 12, 15, 18, 20, 25, 30};
    int n_init = sizeof(init_depths) / sizeof(init_depths[0]);

    i64 best_ever_A = root_A, best_ever_B = root_B, best_ever_C = root_C;
    u64 best_ever_scent = (u64)1e15;
    int total_nodes = 0;

    for (int di = 0; di < n_init && beam_size < beam_width; di++) {
        for (int rep = 0; rep < 3 && beam_size < beam_width; rep++) {
            i64 cA = root_A, cB = root_B, cC = root_C;
            for (int d = 0; d < init_depths[di]; d++) {
                int mi = (int)(rng_next() % 6);  /* forward only */
                const int *M = matrices + mi * 9;
                i64 nA = M[0]*cA + M[1]*cB + M[2]*cC;
                i64 nB = M[3]*cA + M[4]*cB + M[5]*cC;
                i64 nC = M[6]*cA + M[7]*cB + M[8]*cC;
                if (nA > 0 && nB > 0 && nC > 0) { cA = nA; cB = nB; cC = nC; }
            }

            u64 h = hash_triple(cA, cB, cC);
            if (hs_insert(&visited, h)) continue;
            total_nodes++;

            u64 scent;
            u64 factor = check_scent(cA, cB, cC, N, &scent);
            if (factor > 1 && factor < N) {
                *steps_out = 0; *nodes_out = total_nodes;
                free(beam); free(candidates); free(cluster_counts);
                hs_free(&visited);
                return factor;
            }

            beam[beam_size].A = cA;
            beam[beam_size].B = cB;
            beam[beam_size].C = cC;
            beam[beam_size].scent_fp = scent;
            beam_size++;

            if (scent < best_ever_scent) {
                best_ever_scent = scent;
                best_ever_A = cA; best_ever_B = cB; best_ever_C = cC;
            }
        }
    }

    qsort(beam, beam_size, sizeof(BeamEntry), cmp_beam);

    u64 prev_best = (u64)1e15;
    int stuck_count = 0;

    for (int step = 0; step < max_steps; step++) {
        /* Time check every 100 steps */
        if ((step & 0x3F) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &ts_now);
            long elapsed_ms = (ts_now.tv_sec - ts_start.tv_sec) * 1000 +
                              (ts_now.tv_nsec - ts_start.tv_nsec) / 1000000;
            if (elapsed_ms >= time_limit_ms) {
                *steps_out = step; *nodes_out = total_nodes;
                break;
            }
        }

        /* Expand beam */
        int n_cands = 0;
        for (int bi = 0; bi < beam_size; bi++) {
            i64 bA = beam[bi].A, bB = beam[bi].B, bC = beam[bi].C;

            for (int mi = 0; mi < n_mat; mi++) {
                const int *M = matrices + mi * 9;
                i64 nA = M[0]*bA + M[1]*bB + M[2]*bC;
                i64 nB = M[3]*bA + M[4]*bB + M[5]*bC;
                i64 nC = M[6]*bA + M[7]*bB + M[8]*bC;

                if (nA <= 0 || nB <= 0 || nC <= 0) continue;

                u64 h = hash_triple(nA, nB, nC);
                if (hs_insert(&visited, h)) continue;
                total_nodes++;

                u64 scent;
                u64 factor = check_scent(nA, nB, nC, N, &scent);
                if (factor > 1 && factor < N) {
                    *steps_out = step; *nodes_out = total_nodes;
                    free(beam); free(candidates); free(cluster_counts);
                    hs_free(&visited);
                    return factor;
                }

                if (scent < best_ever_scent) {
                    best_ever_scent = scent;
                    best_ever_A = nA; best_ever_B = nB; best_ever_C = nC;
                }

                if (n_cands < max_cands) {
                    candidates[n_cands].A = nA;
                    candidates[n_cands].B = nB;
                    candidates[n_cands].C = nC;
                    candidates[n_cands].scent_fp = scent;
                    n_cands++;
                }
            }
        }

        if (n_cands == 0) break;

        /* Sort candidates by scent */
        qsort(candidates, n_cands, sizeof(BeamEntry), cmp_beam);

        /* Diversified selection */
        memset(cluster_counts, 0, n_clusters * 5 * sizeof(int));
        int greedy_n = 0;
        int overflow_start = -1;

        beam_size = 0;
        for (int i = 0; i < n_cands && greedy_n < greedy_count; i++) {
            i64 cval = candidates[i].C;
            int cid = 0;
            if (cval > 0) {
                double lc = log2((double)cval);
                cid = (int)(lc / (log2_sqrt_N > 0 ? log2_sqrt_N : 1) * n_clusters);
                if (cid < 0) cid = 0;
                if (cid >= n_clusters * 4) cid = n_clusters * 4 - 1;
            }

            if (cluster_counts[cid] < cluster_capacity) {
                beam[beam_size++] = candidates[i];
                cluster_counts[cid]++;
                greedy_n++;
            }
            /* overflow candidates stay in candidates array for random sampling */
        }

        /* Forced random diversity: sample from remaining candidates */
        if (n_cands > greedy_n && forced_random_count > 0) {
            int avail = n_cands - greedy_n;
            int to_add = forced_random_count < avail ? forced_random_count : avail;
            /* Simple: just take evenly spaced from the overflow */
            int stride = avail / (to_add + 1);
            if (stride < 1) stride = 1;
            int added = 0;
            for (int i = greedy_n; i < n_cands && added < to_add && beam_size < beam_width; i += stride) {
                /* Check if already in beam (simplified: skip if scent matches) */
                beam[beam_size++] = candidates[i];
                added++;
            }
        }

        qsort(beam, beam_size, sizeof(BeamEntry), cmp_beam);
        if (beam_size > beam_width) beam_size = beam_width;

        /* Restart detection */
        u64 cur_best = beam_size > 0 ? beam[0].scent_fp : (u64)1e15;
        if (cur_best < 1000000000ULL && /* < 0.001 */
            (cur_best > prev_best ? cur_best - prev_best : prev_best - cur_best) < 100) {
            stuck_count++;
            if (stuck_count >= restart_patience) {
                /* Restart from best-ever neighborhood */
                int inject = beam_width / 2;
                for (int r = 0; r < inject; r++) {
                    i64 cA = best_ever_A, cB = best_ever_B, cC = best_ever_C;
                    int walk = 3 + (int)(rng_next() % 13);
                    for (int w = 0; w < walk; w++) {
                        int mi = (int)(rng_next() % n_mat);
                        const int *M = matrices + mi * 9;
                        i64 nA = M[0]*cA + M[1]*cB + M[2]*cC;
                        i64 nB = M[3]*cA + M[4]*cB + M[5]*cC;
                        i64 nC = M[6]*cA + M[7]*cB + M[8]*cC;
                        if (nA > 0 && nB > 0 && nC > 0) { cA = nA; cB = nB; cC = nC; }
                    }
                    u64 h = hash_triple(cA, cB, cC);
                    if (hs_insert(&visited, h)) continue;
                    total_nodes++;

                    u64 scent;
                    u64 factor = check_scent(cA, cB, cC, N, &scent);
                    if (factor > 1 && factor < N) {
                        *steps_out = step; *nodes_out = total_nodes;
                        free(beam); free(candidates); free(cluster_counts);
                        hs_free(&visited);
                        return factor;
                    }
                    if (beam_size < beam_width) {
                        beam[beam_size].A = cA;
                        beam[beam_size].B = cB;
                        beam[beam_size].C = cC;
                        beam[beam_size].scent_fp = scent;
                        beam_size++;
                    }
                }

                /* Also inject random deep nodes */
                for (int r = 0; r < beam_width / 4; r++) {
                    i64 cA = root_A, cB = root_B, cC = root_C;
                    int depth = 10 + (int)(rng_next() % 26);
                    for (int d = 0; d < depth; d++) {
                        int mi = (int)(rng_next() % n_mat);
                        const int *M = matrices + mi * 9;
                        i64 nA = M[0]*cA + M[1]*cB + M[2]*cC;
                        i64 nB = M[3]*cA + M[4]*cB + M[5]*cC;
                        i64 nC = M[6]*cA + M[7]*cB + M[8]*cC;
                        if (nA > 0 && nB > 0 && nC > 0) { cA = nA; cB = nB; cC = nC; }
                    }
                    u64 h = hash_triple(cA, cB, cC);
                    if (hs_insert(&visited, h)) continue;
                    total_nodes++;

                    u64 scent;
                    u64 factor = check_scent(cA, cB, cC, N, &scent);
                    if (factor > 1 && factor < N) {
                        *steps_out = step; *nodes_out = total_nodes;
                        free(beam); free(candidates); free(cluster_counts);
                        hs_free(&visited);
                        return factor;
                    }
                    if (beam_size < beam_width) {
                        beam[beam_size].A = cA;
                        beam[beam_size].B = cB;
                        beam[beam_size].C = cC;
                        beam[beam_size].scent_fp = scent;
                        beam_size++;
                    }
                }

                qsort(beam, beam_size, sizeof(BeamEntry), cmp_beam);
                if (beam_size > beam_width) beam_size = beam_width;
                stuck_count = 0;
            }
        } else {
            if (stuck_count > 0) stuck_count--;
        }
        prev_best = cur_best;
    }

    *steps_out = max_steps;
    *nodes_out = total_nodes;
    free(beam); free(candidates); free(cluster_counts);
    hs_free(&visited);
    return 0;
}

/*
 * Forward-only beam search — NO hash table dedup.
 * Uses only the first n_forward matrices (forward moves).
 * Beam can only move deeper in tree, so no oscillation.
 * Much lower memory usage, no hash table capacity limit.
 */
u64 beam_search_forward(
    u64 N,
    const int *matrices,
    int n_forward,          /* number of forward-only matrices (typically 6) */
    int beam_width,
    int max_steps,
    int time_limit_ms,
    int n_clusters,
    int diversity_frac,
    int restart_patience,
    u64 seed,
    int *steps_out,
    int *nodes_out
) {
    rng_seed(seed);
    struct timespec ts_start, ts_now;
    clock_gettime(CLOCK_MONOTONIC, &ts_start);

    double log2_N = log2((double)N);
    double log2_sqrt_N = log2_N / 2.0;

    int cluster_capacity = beam_width / n_clusters;
    if (cluster_capacity < 3) cluster_capacity = 3;
    int forced_random_count = beam_width * diversity_frac / 100;
    int greedy_count = beam_width - forced_random_count;

    int max_cands = beam_width * n_forward + 256;
    BeamEntry *beam = (BeamEntry *)malloc(beam_width * 2 * sizeof(BeamEntry));
    BeamEntry *candidates = (BeamEntry *)malloc(max_cands * sizeof(BeamEntry));
    int *cluster_counts = (int *)calloc(n_clusters * 5, sizeof(int));

    i64 root_A = 3, root_B = 4, root_C = 5;
    i64 best_ever_A = root_A, best_ever_B = root_B, best_ever_C = root_C;
    u64 best_ever_scent = (u64)1e15;
    int total_nodes = 0;
    int beam_size = 0;

    /* Init: random walks using forward matrices only */
    int init_depths[] = {0, 2, 4, 6, 8, 10, 12, 15, 18, 20, 25, 30};
    for (int di = 0; di < 12 && beam_size < beam_width; di++) {
        for (int rep = 0; rep < 5 && beam_size < beam_width; rep++) {
            i64 cA = root_A, cB = root_B, cC = root_C;
            for (int d = 0; d < init_depths[di]; d++) {
                int mi = (int)(rng_next() % n_forward);
                const int *M = matrices + mi * 9;
                i64 nA = M[0]*cA + M[1]*cB + M[2]*cC;
                i64 nB = M[3]*cA + M[4]*cB + M[5]*cC;
                i64 nC = M[6]*cA + M[7]*cB + M[8]*cC;
                if (nA > 0 && nB > 0 && nC > 0) { cA = nA; cB = nB; cC = nC; }
            }
            total_nodes++;
            u64 scent;
            u64 factor = check_scent(cA, cB, cC, N, &scent);
            if (factor > 1 && factor < N) {
                *steps_out = 0; *nodes_out = total_nodes;
                free(beam); free(candidates); free(cluster_counts);
                return factor;
            }
            beam[beam_size].A = cA; beam[beam_size].B = cB;
            beam[beam_size].C = cC; beam[beam_size].scent_fp = scent;
            beam_size++;
            if (scent < best_ever_scent) {
                best_ever_scent = scent;
                best_ever_A = cA; best_ever_B = cB; best_ever_C = cC;
            }
        }
    }
    qsort(beam, beam_size, sizeof(BeamEntry), cmp_beam);

    u64 prev_best = (u64)1e15;
    int stuck_count = 0;

    for (int step = 0; step < max_steps; step++) {
        if ((step & 0x3F) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &ts_now);
            long elapsed_ms = (ts_now.tv_sec - ts_start.tv_sec) * 1000 +
                              (ts_now.tv_nsec - ts_start.tv_nsec) / 1000000;
            if (elapsed_ms >= time_limit_ms) break;
        }

        int n_cands = 0;
        for (int bi = 0; bi < beam_size; bi++) {
            i64 bA = beam[bi].A, bB = beam[bi].B, bC = beam[bi].C;
            for (int mi = 0; mi < n_forward; mi++) {
                const int *M = matrices + mi * 9;
                i64 nA = M[0]*bA + M[1]*bB + M[2]*bC;
                i64 nB = M[3]*bA + M[4]*bB + M[5]*bC;
                i64 nC = M[6]*bA + M[7]*bB + M[8]*bC;
                if (nA <= 0 || nB <= 0 || nC <= 0) continue;

                total_nodes++;
                u64 scent;
                u64 factor = check_scent(nA, nB, nC, N, &scent);
                if (factor > 1 && factor < N) {
                    *steps_out = step; *nodes_out = total_nodes;
                    free(beam); free(candidates); free(cluster_counts);
                    return factor;
                }
                if (scent < best_ever_scent) {
                    best_ever_scent = scent;
                    best_ever_A = nA; best_ever_B = nB; best_ever_C = nC;
                }
                if (n_cands < max_cands) {
                    candidates[n_cands].A = nA; candidates[n_cands].B = nB;
                    candidates[n_cands].C = nC; candidates[n_cands].scent_fp = scent;
                    n_cands++;
                }
            }
        }
        if (n_cands == 0) break;

        qsort(candidates, n_cands, sizeof(BeamEntry), cmp_beam);

        /* Diversified selection */
        memset(cluster_counts, 0, n_clusters * 5 * sizeof(int));
        int greedy_n = 0;
        beam_size = 0;
        for (int i = 0; i < n_cands && greedy_n < greedy_count; i++) {
            i64 cval = candidates[i].C;
            int cid = 0;
            if (cval > 0) {
                double lc = log2((double)cval);
                cid = (int)(lc / (log2_sqrt_N > 0 ? log2_sqrt_N : 1) * n_clusters);
                if (cid < 0) cid = 0;
                if (cid >= n_clusters * 4) cid = n_clusters * 4 - 1;
            }
            if (cluster_counts[cid] < cluster_capacity) {
                beam[beam_size++] = candidates[i];
                cluster_counts[cid]++;
                greedy_n++;
            }
        }
        /* Forced diversity */
        if (n_cands > greedy_n && forced_random_count > 0) {
            int avail = n_cands - greedy_n;
            int to_add = forced_random_count < avail ? forced_random_count : avail;
            int stride = avail / (to_add + 1);
            if (stride < 1) stride = 1;
            int added = 0;
            for (int i = greedy_n; i < n_cands && added < to_add && beam_size < beam_width; i += stride) {
                beam[beam_size++] = candidates[i];
                added++;
            }
        }
        qsort(beam, beam_size, sizeof(BeamEntry), cmp_beam);
        if (beam_size > beam_width) beam_size = beam_width;

        /* Restart when stuck */
        u64 cur_best = beam_size > 0 ? beam[0].scent_fp : (u64)1e15;
        if (cur_best < 1000000000ULL &&
            (cur_best > prev_best ? cur_best - prev_best : prev_best - cur_best) < 100) {
            stuck_count++;
            if (stuck_count >= restart_patience) {
                /* Restart from best-ever + random deep nodes */
                for (int r = 0; r < beam_width / 2 && beam_size < beam_width * 2; r++) {
                    i64 cA = best_ever_A, cB = best_ever_B, cC = best_ever_C;
                    int walk = 3 + (int)(rng_next() % 13);
                    for (int w = 0; w < walk; w++) {
                        int mi = (int)(rng_next() % n_forward);
                        const int *M = matrices + mi * 9;
                        i64 nA = M[0]*cA + M[1]*cB + M[2]*cC;
                        i64 nB = M[3]*cA + M[4]*cB + M[5]*cC;
                        i64 nC = M[6]*cA + M[7]*cB + M[8]*cC;
                        if (nA > 0 && nB > 0 && nC > 0) { cA = nA; cB = nB; cC = nC; }
                    }
                    total_nodes++;
                    u64 scent;
                    u64 factor = check_scent(cA, cB, cC, N, &scent);
                    if (factor > 1 && factor < N) {
                        *steps_out = step; *nodes_out = total_nodes;
                        free(beam); free(candidates); free(cluster_counts);
                        return factor;
                    }
                    beam[beam_size].A = cA; beam[beam_size].B = cB;
                    beam[beam_size].C = cC; beam[beam_size].scent_fp = scent;
                    beam_size++;
                }
                for (int r = 0; r < beam_width / 4 && beam_size < beam_width * 2; r++) {
                    i64 cA = root_A, cB = root_B, cC = root_C;
                    int depth = 10 + (int)(rng_next() % 26);
                    for (int d = 0; d < depth; d++) {
                        int mi = (int)(rng_next() % n_forward);
                        const int *M = matrices + mi * 9;
                        i64 nA = M[0]*cA + M[1]*cB + M[2]*cC;
                        i64 nB = M[3]*cA + M[4]*cB + M[5]*cC;
                        i64 nC = M[6]*cA + M[7]*cB + M[8]*cC;
                        if (nA > 0 && nB > 0 && nC > 0) { cA = nA; cB = nB; cC = nC; }
                    }
                    total_nodes++;
                    u64 scent;
                    u64 factor = check_scent(cA, cB, cC, N, &scent);
                    if (factor > 1 && factor < N) {
                        *steps_out = step; *nodes_out = total_nodes;
                        free(beam); free(candidates); free(cluster_counts);
                        return factor;
                    }
                    beam[beam_size].A = cA; beam[beam_size].B = cB;
                    beam[beam_size].C = cC; beam[beam_size].scent_fp = scent;
                    beam_size++;
                }
                qsort(beam, beam_size, sizeof(BeamEntry), cmp_beam);
                if (beam_size > beam_width) beam_size = beam_width;
                stuck_count = 0;
            }
        } else {
            if (stuck_count > 0) stuck_count--;
        }
        prev_best = cur_best;
    }

    *steps_out = max_steps; *nodes_out = total_nodes;
    free(beam); free(candidates); free(cluster_counts);
    return 0;
}

/* Simpler expand_beam for Python hybrid use */
u64 expand_beam(
    const i64 *beam_abc, int beam_size, u64 N,
    const int *matrices, int n_matrices,
    i64 *out_abc, u64 *out_scent, int max_out, int *out_count
) {
    *out_count = 0;
    int cnt = 0;
    for (int bi = 0; bi < beam_size; bi++) {
        i64 A = beam_abc[bi*3], B = beam_abc[bi*3+1], C = beam_abc[bi*3+2];
        for (int mi = 0; mi < n_matrices; mi++) {
            const int *M = matrices + mi * 9;
            i64 nA = M[0]*A + M[1]*B + M[2]*C;
            i64 nB = M[3]*A + M[4]*B + M[5]*C;
            i64 nC = M[6]*A + M[7]*B + M[8]*C;
            if (nA <= 0 || nB <= 0 || nC <= 0) continue;

            u64 scent;
            u64 factor = check_scent(nA, nB, nC, N, &scent);
            if (factor > 1 && factor < N) { *out_count = cnt; return factor; }

            if (cnt < max_out) {
                out_abc[cnt*3] = nA; out_abc[cnt*3+1] = nB; out_abc[cnt*3+2] = nC;
                out_scent[cnt] = scent;
                cnt++;
            }
        }
    }
    *out_count = cnt;
    return 0;
}
