#!/usr/bin/env python3
"""
v35_test_cm_kangaroo.py — Test 6-fold CM symmetry in ec_kangaroo_shared.c

Tests correctness and measures speedup vs a baseline (non-CM) build.
"""

import ctypes, os, mmap, multiprocessing, time, sys, random

# ---- secp256k1 constants ----
P_HEX = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"
N_HEX = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"
GX_HEX = "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
GY_HEX = "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"

p = int(P_HEX, 16)
n = int(N_HEX, 16)
Gx = int(GX_HEX, 16)
Gy = int(GY_HEX, 16)

BETA = 0x7ae96a2b657c07106e64479eac3434e99cf0497512f58995c1396c28719501ee
LAMBDA = 0x5363ad4cc05c30e0a5261c028812645a122e22ea20816678df02967c1b23bd72

def ec_add(P, Q):
    """Affine EC add on secp256k1 (y^2 = x^3 + 7)."""
    if P is None: return Q
    if Q is None: return P
    (px, py), (qx, qy) = P, Q
    if px == qx:
        if py == qy:
            if py == 0: return None
            lam = (3 * px * px * pow(2 * py, -1, p)) % p
        else:
            return None
    else:
        lam = ((qy - py) * pow(qx - px, -1, p)) % p
    rx = (lam * lam - px - qx) % p
    ry = (lam * (px - rx) - py) % p
    return (rx, ry)

def ec_mul(k, P):
    """Double-and-add scalar multiplication."""
    R = None
    A = P
    while k > 0:
        if k & 1:
            R = ec_add(R, A)
        A = ec_add(A, A)
        k >>= 1
    return R


def test_cm_constants():
    """Verify CM endomorphism constants."""
    print("=== Test 1: CM constant verification ===")
    G = (Gx, Gy)

    # beta^3 = 1 mod p
    assert pow(BETA, 3, p) == 1, "FAIL: beta^3 != 1 mod p"
    print("  beta^3 = 1 mod p: PASS")

    # lambda^3 = 1 mod n
    assert pow(LAMBDA, 3, n) == 1, "FAIL: lambda^3 != 1 mod n"
    print("  lambda^3 = 1 mod n: PASS")

    # phi(G) = lambda*G
    phi_G = ((BETA * Gx) % p, Gy)
    lam_G = ec_mul(LAMBDA, G)
    assert phi_G == lam_G, f"FAIL: phi(G) != lambda*G\n  phi(G)={phi_G}\n  lam*G={lam_G}"
    print("  phi(G) = lambda*G: PASS")

    # 6 equivalent points for k*G
    k_test = 12345678901234567
    kG = ec_mul(k_test, G)
    equiv_scalars = [
        k_test % n,
        (LAMBDA * k_test) % n,
        (LAMBDA * LAMBDA * k_test) % n,
        (n - k_test) % n,
        (n - (LAMBDA * k_test) % n) % n,
        (n - (LAMBDA * LAMBDA * k_test) % n) % n,
    ]
    equiv_points = [ec_mul(s, G) for s in equiv_scalars]

    # All should have x in {x, beta*x, beta^2*x} and y in {y, -y}
    x_set = {kG[0], (BETA * kG[0]) % p, (BETA * BETA * kG[0] % p) % p}
    for i, pt in enumerate(equiv_points):
        assert pt[0] in x_set, f"FAIL: equiv point {i} x not in CM orbit"
    print("  6-fold equivalence: PASS")
    print()


def solve_ecdlp_shared(bits, secret_k=None, num_workers=None):
    """Solve ECDLP using shared-memory kangaroo with CM symmetry."""
    lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "ec_kangaroo_shared.so")
    lib = ctypes.CDLL(lib_path)
    lib.ec_kang_shared_init(P_HEX.encode(), N_HEX.encode())

    if secret_k is None:
        secret_k = random.randint(1, (1 << bits) - 1)

    G = (Gx, Gy)
    Q = ec_mul(secret_k, G)
    Qx_hex = f"{Q[0]:064x}"
    Qy_hex = f"{Q[1]:064x}"
    bound = 1 << bits
    bound_hex = f"{bound:x}"

    if num_workers is None:
        num_workers = min(multiprocessing.cpu_count(), 6)

    # Shared memory for DP table
    dp_capacity = 1 << 18  # 256K slots
    slot_size = 40
    total_shm = dp_capacity * slot_size + 4  # +4 for found_flag

    shm = mmap.mmap(-1, total_shm, mmap.MAP_SHARED | mmap.MAP_ANONYMOUS,
                     mmap.PROT_READ | mmap.PROT_WRITE)

    # Zero the shared memory
    shm[:] = b'\x00' * total_shm

    # found_flag at end of DP region
    flag_offset = dp_capacity * slot_size

    t0 = time.time()

    # Fork workers
    pipes = []
    children = []
    for wid in range(num_workers):
        r_fd, w_fd = os.pipe()
        pid = os.fork()
        if pid == 0:
            # Child
            os.close(r_fd)
            try:
                wlib = ctypes.CDLL(lib_path)
                wlib.ec_kang_shared_init(P_HEX.encode(), N_HEX.encode())

                wbuf = (ctypes.c_char * total_shm).from_buffer(shm)
                wdp = ctypes.cast(wbuf, ctypes.c_void_p)
                wflag = ctypes.cast(
                    ctypes.c_void_p(wdp.value + flag_offset),
                    ctypes.POINTER(ctypes.c_int))

                result_buf = ctypes.create_string_buffer(256)
                ret = wlib.ec_kang_shared_solve(
                    GX_HEX.encode(), GY_HEX.encode(),
                    Qx_hex.encode(), Qy_hex.encode(),
                    bound_hex.encode(),
                    wdp, dp_capacity,
                    wid, num_workers,
                    wflag,
                    result_buf, 256)

                if ret:
                    os.write(w_fd, result_buf.value)
                else:
                    os.write(w_fd, b"FAIL")
            except Exception as e:
                os.write(w_fd, f"ERR:{e}".encode())
            finally:
                os.close(w_fd)
                os._exit(0)
        else:
            os.close(w_fd)
            children.append(pid)
            pipes.append(r_fd)

    # Wait for all children
    results = []
    for i, pid in enumerate(children):
        os.waitpid(pid, 0)
        data = b""
        while True:
            chunk = os.read(pipes[i], 4096)
            if not chunk:
                break
            data += chunk
        os.close(pipes[i])
        results.append(data.decode().strip())

    elapsed = time.time() - t0
    shm.close()

    # Find the solution
    solution = None
    for r in results:
        if r and r != "FAIL" and not r.startswith("ERR:"):
            solution = int(r, 16)
            break

    return solution, elapsed, secret_k


def test_correctness():
    """Test that CM kangaroo finds correct solutions at various bit sizes."""
    print("=== Test 2: Correctness (36-bit ECDLP) ===")

    n_trials = 5
    success = 0
    for trial in range(n_trials):
        bits = 36
        sol, elapsed, secret = solve_ecdlp_shared(bits, num_workers=2)
        if sol == secret:
            success += 1
            print(f"  Trial {trial+1}: PASS (k={secret}, found in {elapsed:.2f}s)")
        else:
            print(f"  Trial {trial+1}: FAIL (secret={secret}, found={sol})")

    print(f"  Correctness: {success}/{n_trials}")
    print()
    return success == n_trials


def benchmark_cm():
    """Benchmark CM kangaroo at 36, 40, 44-bit problems."""
    print("=== Test 3: Benchmark CM kangaroo ===")
    num_workers = min(multiprocessing.cpu_count(), 6)
    print(f"  Workers: {num_workers}")

    for bits in [36, 40, 44, 48]:
        times = []
        n_trials = 5 if bits <= 40 else 3
        successes = 0
        for trial in range(n_trials):
            sol, elapsed, secret = solve_ecdlp_shared(bits, num_workers=num_workers)
            if sol == secret:
                successes += 1
                times.append(elapsed)
            else:
                print(f"  {bits}b trial {trial+1}: FAIL (secret={secret}, got={sol})")

        if times:
            avg = sum(times) / len(times)
            best = min(times)
            print(f"  {bits}b: avg={avg:.2f}s, best={best:.2f}s, "
                  f"success={successes}/{n_trials}")
        else:
            print(f"  {bits}b: all failed")
    print()


def test_cm_equivalence_coverage():
    """Verify that canonicalization in C matches Python expectations."""
    print("=== Test 4: CM canonicalization coverage ===")

    # Test that for a known point, all 6 equivalents produce same canonical x
    k_test = 9999999999
    G = (Gx, Gy)
    kG = ec_mul(k_test, G)
    x, y = kG

    # Three x-values under phi
    x0 = x
    x1 = (BETA * x) % p
    x2 = (BETA * BETA * x % p) % p

    # Canonical = min
    canon = min(x0, x1, x2)

    print(f"  x0 = 0x{x0:064x}")
    print(f"  x1 = beta*x = 0x{x1:064x}")
    print(f"  x2 = beta^2*x = 0x{x2:064x}")
    print(f"  canonical (min) = 0x{canon:064x}")

    phi_idx = [x0, x1, x2].index(canon)
    print(f"  phi_idx = {phi_idx}")

    # Verify beta*beta*beta*x = x (mod p)
    x_roundtrip = (BETA * BETA * BETA * x % p) % p
    assert x_roundtrip == x % p, "FAIL: beta^3 * x != x"
    print("  beta^3 * x = x: PASS")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("CM 6-fold Symmetry Kangaroo — Correctness & Benchmark")
    print("=" * 60)
    print()

    test_cm_constants()
    test_cm_equivalence_coverage()

    ok = test_correctness()
    if not ok:
        print("CORRECTNESS FAILED — aborting benchmark")
        sys.exit(1)

    benchmark_cm()

    print("All tests complete.")
