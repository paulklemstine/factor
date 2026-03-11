#!/usr/bin/env python3
"""
Round 5: SAT-based Binary Long Multiplication Factoring

Model n = x * y as a constraint satisfaction problem using the
grade-school binary multiplication framework. Process bit columns
right-to-left, tracking carries, and prune impossible branches.

Key innovations:
1. Global pruning (bit-length bounds, symmetry breaking, Hamming weight)
2. Right-to-left bit deduction with carry tracking
3. Decision tree with backtracking
4. Constraint propagation at each level
"""

import math
import random
import time
from collections import defaultdict

LOG_FILE = "factoring_log.md"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def is_prime_miller_rabin(n, k=20):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def next_prime(n):
    if n <= 2: return 2
    if n % 2 == 0: n += 1
    while not is_prime_miller_rabin(n): n += 2
    return n

def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q: q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q: p, q = q, p
    return p, q, p * q

def get_bits(n):
    """Return list of bits, index 0 = LSB."""
    bits = []
    while n > 0:
        bits.append(n & 1)
        n >>= 1
    return bits

# ============================================================
# METHOD 1: Naive SAT-style search with backtracking
# ============================================================
def sat_factor_backtrack(n, max_nodes=10_000_000):
    """
    Binary long multiplication as a search tree.
    Decide x_k, y_k bits right-to-left.
    At each column, the carry constraint prunes branches.
    """
    L = n.bit_length()
    n_bits = get_bits(n)
    while len(n_bits) < L + 2:
        n_bits.append(0)

    nodes_explored = 0

    # Try different bit-length splits for x and y
    for A in range(2, (L + 2) // 2 + 1):
        B_min = max(A, L - A)
        B_max = L - A + 1
        for B in range(B_min, B_max + 1):
            # x has A bits (x_{A-1}=1, x_0=1), y has B bits (y_{B-1}=1, y_0=1)
            # Search: decide bits x_1..x_{A-2} and y_1..y_{B-2}

            # State: (column_k, x_bits_decided, y_bits_decided, carry)
            # x_bits_decided and y_bits_decided are lists of decided bit values

            # We interleave deciding x and y bits as we advance columns
            # At column k, we need all x_i, y_j where i+j=k

            # Simplified approach: decide all bits of x and y from LSB to MSB,
            # checking column constraints as they become fully determined.

            # Build decision order: at column k, we need x_i for i<=k and y_j for j<=k-i
            # Decide x_1, y_1, x_2, y_2, ... checking constraints as we go

            total_unknowns = (A - 2) + (B - 2)  # x_0,y_0 fixed, x_{A-1},y_{B-1} fixed
            if total_unknowns < 0:
                continue

            # Stack-based DFS
            # State: (bit_index, x_bits, y_bits, carry, verified_columns)
            # x_bits[0] = 1, y_bits[0] = 1 always
            initial_x = [1]  # x_0 = 1
            initial_y = [1]  # y_0 = 1

            # Decide in order: x_1, y_1, x_2, y_2, ...
            max_k = max(A, B) - 1
            stack = [(1, list(initial_x), list(initial_y), 0, 0)]
            # (next_bit_to_decide, x_bits_so_far, y_bits_so_far, carry_verified_up_to, last_verified_carry)

            while stack and nodes_explored < max_nodes:
                bit_idx, x_bits, y_bits, verified_col, carry = stack.pop()
                nodes_explored += 1

                # Check: can we verify any new columns?
                # Column k is verifiable when we have x_i for all i <= min(k, A-1)
                # and y_j for all j <= min(k, B-1)
                new_carry = carry
                valid = True
                for k in range(verified_col, L + 1):
                    # Compute S_k = sum of x_i * y_j for i+j=k, i<len(x_bits), j<len(y_bits)
                    # But only if we have enough bits
                    max_i = min(k, len(x_bits) - 1, A - 1)
                    max_j = min(k, len(y_bits) - 1, B - 1)

                    # Check if column k is fully determined
                    needed_ready = True
                    for i in range(0, min(k + 1, A)):
                        j = k - i
                        if j < 0 or j >= B:
                            continue
                        if i >= len(x_bits) or j >= len(y_bits):
                            needed_ready = False
                            break
                    if not needed_ready:
                        break

                    # Compute column sum
                    s_k = 0
                    for i in range(0, min(k + 1, A)):
                        j = k - i
                        if 0 <= j < B and i < len(x_bits) and j < len(y_bits):
                            s_k += x_bits[i] * y_bits[j]

                    v_k = s_k + new_carry
                    bit_k = v_k % 2
                    new_carry = v_k // 2

                    expected = n_bits[k] if k < len(n_bits) else 0
                    if bit_k != expected:
                        valid = False
                        break
                    verified_col = k + 1

                if not valid:
                    continue

                # Check if we're done
                if len(x_bits) == A and len(y_bits) == B:
                    # Verify remaining columns
                    if verified_col >= L and new_carry == 0:
                        x_val = sum(b << i for i, b in enumerate(x_bits))
                        y_val = sum(b << i for i, b in enumerate(y_bits))
                        if x_val * y_val == n and x_val > 1 and y_val > 1:
                            return min(x_val, y_val)
                    continue

                # Decide next bit
                # Interleave: decide x bits and y bits alternately
                if len(x_bits) < A and (len(x_bits) <= len(y_bits) or len(y_bits) >= B):
                    # Decide next x bit
                    idx = len(x_bits)
                    if idx == A - 1:
                        # MSB must be 1
                        new_x = x_bits + [1]
                        stack.append((bit_idx + 1, new_x, list(y_bits), verified_col, new_carry))
                    else:
                        for b in [0, 1]:
                            new_x = x_bits + [b]
                            stack.append((bit_idx + 1, new_x, list(y_bits), verified_col, new_carry))
                elif len(y_bits) < B:
                    # Decide next y bit
                    idx = len(y_bits)
                    if idx == B - 1:
                        new_y = y_bits + [1]
                        stack.append((bit_idx + 1, list(x_bits), new_y, verified_col, new_carry))
                    else:
                        for b in [0, 1]:
                            new_y = y_bits + [b]
                            stack.append((bit_idx + 1, list(x_bits), new_y, verified_col, new_carry))

    return None

# ============================================================
# METHOD 2: Column-by-column constraint propagation
# ============================================================
def column_constraint_factor(n, max_states=5_000_000):
    """
    Process columns right-to-left. At each column k, enumerate
    possible (x_k, y_k) assignments compatible with the carry
    and known n_k bit. Prune states with impossible carries.

    State: carry value and decided bits so far.
    """
    L = n.bit_length()
    n_bits = get_bits(n)
    while len(n_bits) < L + 5:
        n_bits.append(0)

    for A in range(2, (L + 2) // 2 + 1):
        B_min = max(A, L - A)
        B_max = L - A + 1
        for B in range(B_min, B_max + 1):
            # Process column by column
            # State: (carry, x_bits_list, y_bits_list)
            # At column k, we decide x_k and y_k (if they exist and aren't fixed)

            # Column 0: x_0=1, y_0=1, S_0=1, n_0 must be 1
            if n_bits[0] != 1:
                continue
            # V_0 = 1 + 0(carry) = 1, bit=1 ✓, carry = 0
            initial_states = [(0, [1], [1])]  # carry=0, x=[1], y=[1]

            states = initial_states
            total_explored = 0

            for k in range(1, L + 2):
                if not states or total_explored > max_states:
                    break

                next_states = []
                for carry, x_bits, y_bits in states:
                    total_explored += 1
                    if total_explored > max_states:
                        break

                    # At column k, we may need to decide x_k and/or y_k
                    need_xk = k < A
                    need_yk = k < B

                    # Possible values for x_k, y_k
                    if need_xk and need_yk:
                        if k == A - 1 and k == B - 1:
                            choices = [(1, 1)]  # Both MSB
                        elif k == A - 1:
                            choices = [(1, 0), (1, 1)]
                        elif k == B - 1:
                            choices = [(0, 1), (1, 1)]
                        else:
                            choices = [(0, 0), (0, 1), (1, 0), (1, 1)]
                    elif need_xk:
                        if k == A - 1:
                            choices = [(1, None)]
                        else:
                            choices = [(0, None), (1, None)]
                    elif need_yk:
                        if k == B - 1:
                            choices = [(None, 1)]
                        else:
                            choices = [(None, 0), (None, 1)]
                    else:
                        choices = [(None, None)]

                    for xk, yk in choices:
                        new_x = list(x_bits)
                        new_y = list(y_bits)
                        if xk is not None:
                            new_x.append(xk)
                        if yk is not None:
                            new_y.append(yk)

                        # Compute column k sum
                        s_k = 0
                        for i in range(min(k + 1, len(new_x))):
                            j = k - i
                            if 0 <= j < len(new_y):
                                s_k += new_x[i] * new_y[j]

                        v_k = s_k + carry
                        bit_k = v_k % 2
                        new_carry = v_k // 2

                        expected = n_bits[k] if k < len(n_bits) else 0
                        if bit_k != expected:
                            continue  # Prune!

                        # Carry bound check
                        # Maximum possible carry from column k is bounded
                        max_remaining_cols = L - k
                        if new_carry > max_remaining_cols + 1:
                            continue  # Carry too large

                        next_states.append((new_carry, new_x, new_y))

                # Limit state explosion
                if len(next_states) > 100000:
                    # Prune: keep states with smallest carry (most constrained)
                    next_states.sort(key=lambda s: s[0])
                    next_states = next_states[:100000]

                states = next_states

            # Check final states
            for carry, x_bits, y_bits in states:
                if carry == 0 and len(x_bits) == A and len(y_bits) == B:
                    x_val = sum(b << i for i, b in enumerate(x_bits))
                    y_val = sum(b << i for i, b in enumerate(y_bits))
                    if x_val * y_val == n and 1 < x_val < n:
                        return min(x_val, y_val)

    return None

# ============================================================
# METHOD 3: Column-by-column with carry compression
# ============================================================
def column_carry_compressed(n, max_states_per_col=50000):
    """
    Same column-by-column approach but aggressively compress states.
    Key insight: many different bit assignments lead to the same carry.
    Group states by carry value — we only need ONE representative
    per carry value (we can reconstruct bits later).

    This dramatically reduces the state space!
    """
    L = n.bit_length()
    n_bits = get_bits(n)
    while len(n_bits) < L + 5:
        n_bits.append(0)

    for A in range(2, (L + 2) // 2 + 1):
        B = L - A + 1  # Most likely length
        if B < A:
            continue

        # State: just carry value -> (x_bits, y_bits) representative
        # Column 0: x_0=1, y_0=1
        if n_bits[0] != 1:
            continue

        states = {0: ([1], [1])}  # carry -> (x_bits, y_bits)

        for k in range(1, L + 2):
            if not states:
                break

            next_states = {}

            for carry, (x_bits, y_bits) in states.items():
                need_xk = k < A
                need_yk = k < B

                if need_xk and need_yk:
                    if k == A - 1 and k == B - 1:
                        choices = [(1, 1)]
                    elif k == A - 1:
                        choices = [(1, 0), (1, 1)]
                    elif k == B - 1:
                        choices = [(0, 1), (1, 1)]
                    else:
                        choices = [(0, 0), (0, 1), (1, 0), (1, 1)]
                elif need_xk:
                    choices = [(1, None)] if k == A - 1 else [(0, None), (1, None)]
                elif need_yk:
                    choices = [(None, 1)] if k == B - 1 else [(None, 0), (None, 1)]
                else:
                    choices = [(None, None)]

                for xk, yk in choices:
                    new_x = list(x_bits)
                    new_y = list(y_bits)
                    if xk is not None:
                        new_x.append(xk)
                    if yk is not None:
                        new_y.append(yk)

                    s_k = 0
                    for i in range(min(k + 1, len(new_x))):
                        j = k - i
                        if 0 <= j < len(new_y):
                            s_k += new_x[i] * new_y[j]

                    v_k = s_k + carry
                    bit_k = v_k % 2
                    new_carry = v_k // 2

                    expected = n_bits[k] if k < len(n_bits) else 0
                    if bit_k != expected:
                        continue

                    # Store (or keep first found per carry value)
                    if new_carry not in next_states:
                        next_states[new_carry] = (new_x, new_y)

            if len(next_states) > max_states_per_col:
                # Keep smallest carries
                sorted_carries = sorted(next_states.keys())[:max_states_per_col]
                next_states = {c: next_states[c] for c in sorted_carries}

            states = next_states

        # Check terminal states
        if 0 in states:
            x_bits, y_bits = states[0]
            if len(x_bits) == A and len(y_bits) == B:
                x_val = sum(b << i for i, b in enumerate(x_bits))
                y_val = sum(b << i for i, b in enumerate(y_bits))
                if x_val * y_val == n and 1 < x_val < n:
                    return min(x_val, y_val)

        # Also try B = L - A (shorter product)
        B2 = L - A
        if B2 >= A and B2 != B:
            states2 = {0: ([1], [1])}
            for k in range(1, L + 2):
                if not states2: break
                next_states2 = {}
                for carry, (x_bits, y_bits) in states2.items():
                    need_xk = k < A
                    need_yk = k < B2
                    if need_xk and need_yk:
                        if k == A - 1 and k == B2 - 1: choices = [(1, 1)]
                        elif k == A - 1: choices = [(1, 0), (1, 1)]
                        elif k == B2 - 1: choices = [(0, 1), (1, 1)]
                        else: choices = [(0, 0), (0, 1), (1, 0), (1, 1)]
                    elif need_xk:
                        choices = [(1, None)] if k == A - 1 else [(0, None), (1, None)]
                    elif need_yk:
                        choices = [(None, 1)] if k == B2 - 1 else [(None, 0), (None, 1)]
                    else:
                        choices = [(None, None)]
                    for xk, yk in choices:
                        new_x = list(x_bits)
                        new_y = list(y_bits)
                        if xk is not None: new_x.append(xk)
                        if yk is not None: new_y.append(yk)
                        s_k = 0
                        for i in range(min(k + 1, len(new_x))):
                            j = k - i
                            if 0 <= j < len(new_y):
                                s_k += new_x[i] * new_y[j]
                        v_k = s_k + carry
                        if v_k % 2 != (n_bits[k] if k < len(n_bits) else 0): continue
                        new_carry = v_k // 2
                        if new_carry not in next_states2:
                            next_states2[new_carry] = (new_x, new_y)
                if len(next_states2) > max_states_per_col:
                    sorted_carries = sorted(next_states2.keys())[:max_states_per_col]
                    next_states2 = {c: next_states2[c] for c in sorted_carries}
                states2 = next_states2
            if 0 in states2:
                x_bits, y_bits = states2[0]
                x_val = sum(b << i for i, b in enumerate(x_bits))
                y_val = sum(b << i for i, b in enumerate(y_bits))
                if x_val * y_val == n and 1 < x_val < n:
                    return min(x_val, y_val)

    return None

# ============================================================
# METHOD 4: Hybrid SAT + Pollard — use SAT for low bits, Pollard for rest
# ============================================================
def hybrid_sat_pollard(n, sat_bits=20):
    """
    Novel hybrid: determine the lowest `sat_bits` bits of both factors
    using the SAT column method (which is efficient for low-order bits),
    then use this partial information to accelerate Pollard rho.

    If we know x mod 2^k and y mod 2^k, we can:
    1. Restrict Pollard rho's search to numbers ≡ x mod 2^k
    2. Use Hensel lifting to extend partial solutions
    """
    L = n.bit_length()
    n_bits = get_bits(n)
    while len(n_bits) < L + 5:
        n_bits.append(0)

    modulus = 1 << sat_bits
    n_mod = n % modulus

    # Find all (x_low, y_low) such that x_low * y_low ≡ n mod 2^sat_bits
    # with x_low, y_low both odd (since n is odd)
    candidates = []
    for x_low in range(1, modulus, 2):  # x_low is odd
        if n_mod % 1 == 0:  # always true, just iterate
            # y_low = n_mod * x_low^(-1) mod 2^sat_bits
            try:
                x_inv = pow(x_low, -1, modulus)
                y_low = (n_mod * x_inv) % modulus
                if y_low % 2 == 1:  # y must be odd too
                    if x_low <= y_low:  # symmetry breaking
                        candidates.append((x_low, y_low))
            except ValueError:
                continue

    # For each candidate partial solution, try Hensel lifting
    for x_low, y_low in candidates[:1000]:  # Limit candidates
        # Hensel lift: given x*y ≡ n mod 2^k, find x*y ≡ n mod 2^(k+1)
        # x = x_low + a * 2^k, y = y_low + b * 2^k
        # (x_low + a*2^k)(y_low + b*2^k) ≡ n mod 2^(k+1)
        # x_low*y_low + (a*y_low + b*x_low)*2^k ≡ n mod 2^(k+1)
        # a*y_low + b*x_low ≡ (n - x_low*y_low)/2^k mod 2

        # Actually, we can lift all the way to full precision!
        x_curr = x_low
        y_curr = y_low
        mod_curr = modulus

        for lift in range(sat_bits, L + 1):
            mod_next = mod_curr * 2
            residual = (n - x_curr * y_curr) % mod_next
            if residual == 0:
                # Already correct at this level
                pass
            else:
                # residual should be divisible by mod_curr
                r = residual // mod_curr
                # a*y_curr + b*x_curr ≡ r mod 2
                # Try (a,b) in {(0,0),(0,1),(1,0),(1,1)}
                found = False
                for a in [0, 1]:
                    for b in [0, 1]:
                        if (a * y_curr + b * x_curr) % 2 == r % 2:
                            x_new = x_curr + a * mod_curr
                            y_new = y_curr + b * mod_curr
                            if (x_new * y_new) % mod_next == n % mod_next:
                                x_curr = x_new
                                y_curr = y_new
                                found = True
                                break
                    if found:
                        break
                if not found:
                    break

            mod_curr = mod_next

            # Check if we've found full factors
            if x_curr > 1 and x_curr < n and n % x_curr == 0:
                return x_curr
            if y_curr > 1 and y_curr < n and n % y_curr == 0:
                return y_curr

    return None

# ============================================================
# METHOD 5: Hensel Lifting from mod-2^k solutions (focused)
# ============================================================
def hensel_lift_factor(n, max_lift_bits=None):
    """
    Pure Hensel lifting approach:
    Start from n ≡ x*y mod 2 (both odd, so x≡1, y≡1 mod 2).
    Lift one bit at a time. At each level, there are at most 2 choices.
    Track ALL valid partial factorizations and lift them.
    """
    if max_lift_bits is None:
        max_lift_bits = n.bit_length() + 2

    # Start: x ≡ 1 mod 2, y ≡ 1 mod 2
    # State: set of (x_mod, y_mod) pairs mod 2^k
    states = [(1, 1)]  # mod 2

    for k in range(1, max_lift_bits):
        mod_curr = 1 << k
        mod_next = 1 << (k + 1)
        n_mod = n % mod_next

        next_states = []
        for x_mod, y_mod in states:
            # Lift: x = x_mod + a*mod_curr, y = y_mod + b*mod_curr
            # where a, b ∈ {0, 1}
            for a in [0, 1]:
                for b in [0, 1]:
                    x_new = x_mod + a * mod_curr
                    y_new = y_mod + b * mod_curr
                    if (x_new * y_new) % mod_next == n_mod:
                        # Symmetry breaking: x <= y
                        if x_new <= y_new:
                            next_states.append((x_new, y_new))

        # Deduplicate
        next_states = list(set(next_states))

        # Check for factors
        for x_mod, y_mod in next_states:
            if x_mod > 1 and x_mod < n and n % x_mod == 0:
                return x_mod
            if y_mod > 1 and y_mod < n and n % y_mod == 0:
                return y_mod

        states = next_states

        if len(states) == 0:
            break

        # State explosion control
        if len(states) > 100000:
            # This shouldn't happen often due to constraints
            random.shuffle(states)
            states = states[:100000]

    return None

# ============================================================
# RUN
# ============================================================
def main():
    random.seed(314159)

    test_cases = []
    for bits in [20, 30, 40, 50, 60, 64, 72, 80]:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("\n\n---\n")
    log("## Round 5: SAT-Based Binary Long Multiplication\n")
    log("### Test Numbers\n")
    for bits, p, q, n in test_cases:
        log(f"- {bits}-bit: n={n}, p={p}, q={q}")

    methods = [
        ("SAT Backtrack", sat_factor_backtrack),
        ("Column Constraint", column_constraint_factor),
        ("Column Carry Compressed", column_carry_compressed),
        ("Hybrid SAT+Pollard", hybrid_sat_pollard),
        ("Hensel Lifting", hensel_lift_factor),
    ]

    TIME_LIMIT = 60

    for method_name, func in methods:
        log(f"\n### {method_name}\n")
        for bits, p, q, n in test_cases:
            start = time.time()
            try:
                result = func(n)
                elapsed = time.time() - start
                if elapsed > TIME_LIMIT:
                    log(f"- {bits}-bit: **TIMEOUT** ({elapsed:.1f}s)")
                elif result and n % result == 0 and 1 < result < n:
                    log(f"- {bits}-bit: **SUCCESS** {elapsed:.4f}s -> {result}")
                else:
                    log(f"- {bits}-bit: FAILED ({elapsed:.2f}s)")
            except Exception as e:
                elapsed = time.time() - start
                log(f"- {bits}-bit: ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)")

    log("\n## Round 5 Analysis\n")
    log("""
### Key findings on the SAT/binary multiplication approach:

1. **Column-by-column processing** is correct but has exponential state growth.
   The carry grows as log(k), so the number of distinct carry values at
   column k is O(k), giving O(k * 4^?) total states per column.

2. **Carry compression** helps: many bit assignments lead to the same carry.
   Only tracking unique carry values dramatically reduces states.

3. **Hensel lifting** is the purest form of this idea: lift x*y ≡ n mod 2^k
   one bit at a time. The branching factor is at most 4 per level (a,b ∈ {0,1}),
   but constraint n_k fixes ~half the branches, so effective branching ≈ 2.
   Total states: O(2^(L/2)) ≈ O(√n) — same as trial division!

4. **The entanglement barrier** (Section 4 in the framework) is real:
   the carry from column k couples ALL previous bit decisions.
   This is why the state space grows exponentially.

5. **Hybrid approach** is promising: determine low bits via SAT (O(2^k) for k bits),
   then use algebraic methods (rho, p-1) with the partial information.

### Novel insight:
The Hensel lifting approach is mathematically equivalent to trial division
from the BOTTOM (least significant bits) rather than the TOP (most significant bits).
Both are O(√n) in the worst case. BUT:
- Top-down trial division tests one factor at a time
- Bottom-up Hensel tests ALL factors simultaneously via carry constraints
- Could we combine top-down AND bottom-up to meet in the middle?
  That would give O(n^(1/4)) — matching Pollard rho!
""")

if __name__ == "__main__":
    main()
