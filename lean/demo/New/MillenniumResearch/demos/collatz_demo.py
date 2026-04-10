#!/usr/bin/env python3
"""
Collatz Conjecture Visualization Demo

Demonstrates the Collatz (3n+1) trajectory for various starting values,
corresponding to the formally verified results in Foundations.lean.
"""


def collatz(n: int) -> int:
    """The Collatz function: n -> n/2 if even, 3n+1 if odd."""
    return n // 2 if n % 2 == 0 else 3 * n + 1


def collatz_trajectory(n: int, max_steps: int = 10000) -> list:
    """Compute the full Collatz trajectory from n to 1."""
    trajectory = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = collatz(current)
        trajectory.append(current)
    return trajectory


def stopping_time(n: int, max_steps: int = 10000) -> int:
    """Number of steps for n to reach 1."""
    current = n
    steps = 0
    for _ in range(max_steps):
        if current == 1:
            return steps
        current = collatz(current)
        steps += 1
    return -1


def print_trajectory(n: int):
    """Pretty-print a Collatz trajectory."""
    traj = collatz_trajectory(n)
    print(f"\nCollatz trajectory for n = {n}:")
    print(f"  Stopping time: {len(traj) - 1} steps")
    print(f"  Maximum value: {max(traj)}")
    if len(traj) <= 20:
        print(f"  Trajectory: {' -> '.join(map(str, traj))}")
    else:
        first = ' -> '.join(map(str, traj[:8]))
        last = ' -> '.join(map(str, traj[-4:]))
        print(f"  Trajectory: {first} -> ... -> {last}")


def stopping_time_distribution(max_n: int = 1000):
    """Analyze the distribution of stopping times."""
    times = {}
    max_time = 0
    max_time_n = 1

    for n in range(1, max_n + 1):
        t = stopping_time(n)
        times[n] = t
        if t > max_time:
            max_time = t
            max_time_n = n

    avg_time = sum(times.values()) / len(times)
    print(f"\nStopping time distribution for n = 1 to {max_n}:")
    print(f"  Maximum stopping time: {max_time} (at n = {max_time_n})")
    print(f"  Average stopping time: {avg_time:.1f}")

    # Histogram
    buckets = {}
    bucket_size = max(1, max_time // 15)
    for t in times.values():
        bucket = (t // bucket_size) * bucket_size
        buckets[bucket] = buckets.get(bucket, 0) + 1

    print(f"\n  Histogram (bucket size = {bucket_size}):")
    max_count = max(buckets.values())
    for bucket in sorted(buckets.keys()):
        bar_len = int(40 * buckets[bucket] / max_count)
        print(f"    {bucket:4d}-{bucket + bucket_size - 1:4d}: {'#' * bar_len} ({buckets[bucket]})")


def verify_formally_proved():
    """Verify the specific results formally proved in Lean."""
    print("=" * 60)
    print("VERIFICATION OF FORMALLY PROVED RESULTS")
    print("=" * 60)

    # collatz_even_decreases
    for n in [2, 4, 6, 8, 10, 100]:
        assert collatz(n) < n
    print("[OK] collatz_even_decreases: collatz(n) < n for even n >= 2")

    # collatz_odd_then_even
    for n in [1, 3, 5, 7, 9, 11]:
        assert (3 * n + 1) % 2 == 0
    print("[OK] collatz_odd_then_even: 3n+1 is even for odd n")

    # collatz_two_step
    for n in [1, 3, 5, 7, 9, 27]:
        result = collatz(collatz(n))
        expected = (3 * n + 1) // 2
        assert result == expected
    print("[OK] collatz_two_step: Two steps from odd n gives (3n+1)/2")

    # collatz_27
    traj = collatz_trajectory(27)
    assert len(traj) - 1 == 111
    assert traj[-1] == 1
    print(f"[OK] collatz_27: n=27 reaches 1 in 111 steps (peak={max(traj)})")


def main():
    print("=" * 60)
    print("  COLLATZ CONJECTURE DEMONSTRATION")
    print("  Companion to formally verified results in Lean 4")
    print("=" * 60)

    verify_formally_proved()

    print("\n" + "=" * 60)
    print("NOTABLE TRAJECTORIES")
    print("=" * 60)

    for n in [7, 27, 97, 871, 6171]:
        print_trajectory(n)

    print("\n" + "=" * 60)
    print("STOPPING TIME ANALYSIS")
    print("=" * 60)
    stopping_time_distribution(1000)


if __name__ == "__main__":
    main()
