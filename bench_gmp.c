/* Benchmark GMP operations for secp256k1 field */
#include <stdio.h>
#include <gmp.h>
#include <time.h>

int main(void) {
    mpz_t p, a, b, r, inv;
    mpz_init(p); mpz_init(a); mpz_init(b); mpz_init(r); mpz_init(inv);
    mpz_set_str(p, "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16);
    mpz_set_str(a, "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16);
    mpz_set_str(b, "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16);

    int N = 1000000;
    clock_t t0, t1;

    /* Benchmark mul+mod */
    t0 = clock();
    for (int i = 0; i < N; i++) {
        mpz_mul(r, a, b); mpz_mod(r, r, p);
    }
    t1 = clock();
    printf("mul+mod: %.1f ns/op (%d ops in %.3fs)\n",
           1e9*(double)(t1-t0)/CLOCKS_PER_SEC/N, N, (double)(t1-t0)/CLOCKS_PER_SEC);

    /* Benchmark invert */
    t0 = clock();
    for (int i = 0; i < N/10; i++) {
        mpz_invert(inv, a, p);
    }
    t1 = clock();
    printf("invert:  %.1f ns/op (%d ops in %.3fs)\n",
           1e9*(double)(t1-t0)/CLOCKS_PER_SEC/(N/10), N/10, (double)(t1-t0)/CLOCKS_PER_SEC);

    mpz_clear(p); mpz_clear(a); mpz_clear(b); mpz_clear(r); mpz_clear(inv);
    return 0;
}
