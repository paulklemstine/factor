
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// atomicAdd for uint16_t (not natively supported on all architectures)
__device__ void atomicAdd_u16(uint16_t *addr, uint16_t val) {
    // Use 32-bit atomicAdd on the aligned 32-bit word containing addr
    unsigned int *base = (unsigned int *)((size_t)addr & ~3ULL);
    unsigned int shift = ((size_t)addr & 2) ? 16 : 0;
    unsigned int add_val = ((unsigned int)val) << shift;
    atomicAdd(base, add_val);
}

// GPU kernel: each thread handles one prime, sieving its arithmetic progression
__global__ void sieve_kernel(
    uint16_t *sieve_arr,       // sieve array (size = 2*A+1)
    const int64_t *primes,     // factor base primes
    const uint16_t *log_ps,    // log(p) * 128
    const int64_t *starts,     // start positions for this b-line
    int n_primes,
    int size
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= n_primes) return;

    int64_t p = primes[tid];
    uint16_t lp = log_ps[tid];
    int64_t idx = starts[tid];

    while (idx < size) {
        atomicAdd_u16(&sieve_arr[idx], lp);
        idx += p;
    }
}

// Host function: sieve one b-line on GPU
extern "C" int gpu_sieve_line(
    int b, int A, int64_t m,
    const int64_t *h_rat_primes, const uint16_t *h_rat_logp, int n_rat,
    const int64_t *h_alg_primes, const int64_t *h_alg_roots,
    const uint16_t *h_alg_logp, int n_alg,
    uint16_t *h_rat_sieve,  // output: rational sieve (host)
    uint16_t *h_alg_sieve,  // output: algebraic sieve (host)
    // GPU device pointers (persistent across calls)
    int64_t *d_rat_primes, uint16_t *d_rat_logp, int64_t *d_rat_starts,
    int64_t *d_alg_primes, int64_t *d_alg_roots, uint16_t *d_alg_logp, int64_t *d_alg_starts,
    uint16_t *d_rat_sieve, uint16_t *d_alg_sieve
) {
    int size = 2 * A + 1;

    // Compute start positions on host
    int64_t *h_rat_starts = (int64_t *)malloc(n_rat * sizeof(int64_t));
    int64_t *h_alg_starts = (int64_t *)malloc(n_alg * sizeof(int64_t));

    for (int i = 0; i < n_rat; i++) {
        int64_t p = h_rat_primes[i];
        int64_t bm_mod = ((int64_t)b % p) * (((m % p) + p) % p) % p;
        int64_t start = ((-bm_mod % p) + p) % p;
        h_rat_starts[i] = (start + (int64_t)A) % p;
    }
    for (int i = 0; i < n_alg; i++) {
        int64_t p = h_alg_primes[i];
        int64_t r = h_alg_roots[i];
        int64_t br_mod = ((int64_t)b % p) * ((r % p + p) % p) % p;
        int64_t start = ((-br_mod % p) + p) % p;
        h_alg_starts[i] = (start + (int64_t)A) % p;
    }

    // Copy starts to device
    cudaMemcpy(d_rat_starts, h_rat_starts, n_rat * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_starts, h_alg_starts, n_alg * sizeof(int64_t), cudaMemcpyHostToDevice);

    // Clear sieve arrays on device
    cudaMemset(d_rat_sieve, 0, size * sizeof(uint16_t));
    cudaMemset(d_alg_sieve, 0, size * sizeof(uint16_t));

    // Launch rational sieve kernel
    int threads = 256;
    int blocks_rat = (n_rat + threads - 1) / threads;
    int blocks_alg = (n_alg + threads - 1) / threads;

    sieve_kernel<<<blocks_rat, threads>>>(d_rat_sieve, d_rat_primes, d_rat_logp, d_rat_starts, n_rat, size);
    sieve_kernel<<<blocks_alg, threads>>>(d_alg_sieve, d_alg_primes, d_alg_logp, d_alg_starts, n_alg, size);

    cudaDeviceSynchronize();

    // Copy results back
    cudaMemcpy(h_rat_sieve, d_rat_sieve, size * sizeof(uint16_t), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_alg_sieve, d_alg_sieve, size * sizeof(uint16_t), cudaMemcpyDeviceToHost);

    free(h_rat_starts);
    free(h_alg_starts);
    return 0;
}

// Allocate persistent GPU buffers
extern "C" int gpu_alloc(
    int n_rat, int n_alg, int size,
    const int64_t *h_rat_primes, const uint16_t *h_rat_logp,
    const int64_t *h_alg_primes, const int64_t *h_alg_roots, const uint16_t *h_alg_logp,
    // Output: device pointers (stored as uint64 on host)
    uint64_t *out_ptrs  // 9 pointers
) {
    int64_t *d_rat_primes, *d_alg_primes, *d_alg_roots;
    uint16_t *d_rat_logp, *d_alg_logp;
    int64_t *d_rat_starts, *d_alg_starts;
    uint16_t *d_rat_sieve, *d_alg_sieve;

    cudaMalloc(&d_rat_primes, n_rat * sizeof(int64_t));
    cudaMalloc(&d_rat_logp, n_rat * sizeof(uint16_t));
    cudaMalloc(&d_rat_starts, n_rat * sizeof(int64_t));
    cudaMalloc(&d_alg_primes, n_alg * sizeof(int64_t));
    cudaMalloc(&d_alg_roots, n_alg * sizeof(int64_t));
    cudaMalloc(&d_alg_logp, n_alg * sizeof(uint16_t));
    cudaMalloc(&d_alg_starts, n_alg * sizeof(int64_t));
    cudaMalloc(&d_rat_sieve, size * sizeof(uint16_t));
    cudaMalloc(&d_alg_sieve, size * sizeof(uint16_t));

    // Copy constant data
    cudaMemcpy(d_rat_primes, h_rat_primes, n_rat * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_rat_logp, h_rat_logp, n_rat * sizeof(uint16_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_primes, h_alg_primes, n_alg * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_roots, h_alg_roots, n_alg * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_logp, h_alg_logp, n_alg * sizeof(uint16_t), cudaMemcpyHostToDevice);

    out_ptrs[0] = (uint64_t)d_rat_primes;
    out_ptrs[1] = (uint64_t)d_rat_logp;
    out_ptrs[2] = (uint64_t)d_rat_starts;
    out_ptrs[3] = (uint64_t)d_alg_primes;
    out_ptrs[4] = (uint64_t)d_alg_roots;
    out_ptrs[5] = (uint64_t)d_alg_logp;
    out_ptrs[6] = (uint64_t)d_alg_starts;
    out_ptrs[7] = (uint64_t)d_rat_sieve;
    out_ptrs[8] = (uint64_t)d_alg_sieve;

    return 0;
}

// Free GPU buffers
extern "C" void gpu_free(uint64_t *ptrs) {
    for (int i = 0; i < 9; i++) {
        cudaFree((void*)ptrs[i]);
    }
}
