
#include <stdio.h>
#include <stdint.h>

// Each thread tests one (candidate, prime) pair
// Grid: candidates x prime_blocks
__global__ void trial_div_kernel(
    const int64_t *norms,      // candidate norms (absolute values)
    const int64_t *primes,     // FB primes
    int *exponents,            // output: exponent[cand * n_primes + prime_idx]
    int n_cands, int n_primes
) {
    int cand_idx = blockIdx.x;
    int prime_idx = blockIdx.y * blockDim.x + threadIdx.x;

    if (cand_idx >= n_cands || prime_idx >= n_primes) return;

    int64_t norm = norms[cand_idx];
    int64_t p = primes[prime_idx];
    int exp = 0;

    if (norm >= p && norm % p == 0) {
        exp = 1;
        int64_t reduced = norm / p;
        while (reduced % p == 0) {
            reduced /= p;
            exp++;
        }
    }
    exponents[cand_idx * n_primes + prime_idx] = exp;
}

// Host wrapper
extern "C" int gpu_trial_divide(
    const int64_t *h_norms, int n_cands,
    const int64_t *h_primes, int n_primes,
    int *h_exponents  // output: n_cands x n_primes
) {
    int64_t *d_norms, *d_primes;
    int *d_exponents;

    cudaMalloc(&d_norms, n_cands * sizeof(int64_t));
    cudaMalloc(&d_primes, n_primes * sizeof(int64_t));
    cudaMalloc(&d_exponents, (int64_t)n_cands * n_primes * sizeof(int));

    cudaMemcpy(d_norms, h_norms, n_cands * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_primes, h_primes, n_primes * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemset(d_exponents, 0, (int64_t)n_cands * n_primes * sizeof(int));

    int threads = 256;
    int prime_blocks = (n_primes + threads - 1) / threads;
    dim3 grid(n_cands, prime_blocks);

    trial_div_kernel<<<grid, threads>>>(d_norms, d_primes, d_exponents, n_cands, n_primes);
    cudaDeviceSynchronize();

    cudaMemcpy(h_exponents, d_exponents, (int64_t)n_cands * n_primes * sizeof(int), cudaMemcpyDeviceToHost);

    cudaFree(d_norms);
    cudaFree(d_primes);
    cudaFree(d_exponents);

    return 0;
}
