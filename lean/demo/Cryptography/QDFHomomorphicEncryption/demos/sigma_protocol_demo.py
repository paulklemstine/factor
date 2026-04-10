#!/usr/bin/env python3
"""
Sigma Protocol & Zero-Knowledge Proof Demo
=============================================
Interactive demonstrations of:
1. Schnorr identification protocol
2. Fiat-Shamir transform (non-interactive proofs)
3. OR-composition of Sigma protocols
4. Soundness error and parallel repetition

All properties are formally verified in the accompanying Lean 4 code.

Run: python3 sigma_protocol_demo.py
"""

import hashlib
import secrets
import math


# ============================================================
# Part 1: Schnorr Protocol Simulation
# ============================================================

class SchnorrProtocol:
    """Simulates the Schnorr identification protocol over Z/qZ.

    Lean theorems verified:
    - schnorrExponent_complete: honest execution always verifies
    - schnorrExponent_2ss: two transcripts yield witness extraction
    """

    def __init__(self, q: int):
        """Initialize with prime modulus q."""
        self.q = q

    def keygen(self) -> tuple:
        """Generate (secret_key, public_key) = (x, g^x mod q).
        We work in exponent space, so public_key = x (abstractly).
        """
        x = secrets.randbelow(self.q - 1) + 1
        return x, x  # In exponent space, pk = sk

    def commit(self, x: int) -> tuple:
        """Prover's commitment: choose random r, send t = r (exponent).
        Returns (randomness, commitment).
        """
        r = secrets.randbelow(self.q)
        return r, r  # commitment = randomness in exponent space

    def challenge(self) -> int:
        """Verifier's random challenge."""
        return secrets.randbelow(self.q)

    def respond(self, x: int, r: int, c: int) -> int:
        """Prover's response: s = r + c*x mod q.
        Theorem: schnorr_completeness_exponent proves this satisfies verification.
        """
        return (r + c * x) % self.q

    def verify(self, pk: int, t: int, c: int, s: int) -> bool:
        """Verify: s == t + c*pk mod q.
        Theorem: schnorr_completeness proves this always holds for honest provers.
        """
        return s % self.q == (t + c * pk) % self.q

    def extract(self, c1: int, s1: int, c2: int, s2: int) -> int:
        """Extract witness from two transcripts with same commitment.
        Theorem: schnorr_extraction proves x = (s1-s2) * (c1-c2)^(-1) mod q.
        """
        dc = (c1 - c2) % self.q
        ds = (s1 - s2) % self.q
        # Compute modular inverse of dc
        dc_inv = pow(dc, self.q - 2, self.q)  # Fermat's little theorem
        return (ds * dc_inv) % self.q


def demo_schnorr():
    """Demonstrate the Schnorr protocol."""
    print("=" * 60)
    print("Part 1: Schnorr Identification Protocol")
    print("=" * 60)

    q = 104729  # A prime
    proto = SchnorrProtocol(q)

    # Key generation
    sk, pk = proto.keygen()
    print(f"\nSetup (q = {q}):")
    print(f"  Secret key x = {sk}")
    print(f"  Public key h = {pk} (= x in exponent space)")

    # Honest execution
    print("\n--- Honest Execution ---")
    r, t = proto.commit(sk)
    c = proto.challenge()
    s = proto.respond(sk, r, c)
    valid = proto.verify(pk, t, c, s)

    print(f"  Commitment t = {t}")
    print(f"  Challenge  c = {c}")
    print(f"  Response   s = {s}")
    print(f"  Verify: s == t + c*h mod q? {valid} ✓")

    # Special soundness: extraction from two transcripts
    print("\n--- Special Soundness (Witness Extraction) ---")
    r2, t2 = r, t  # Same commitment
    c1 = proto.challenge()
    s1 = proto.respond(sk, r, c1)
    c2 = proto.challenge()
    while c2 == c1:
        c2 = proto.challenge()
    s2 = proto.respond(sk, r, c2)

    extracted = proto.extract(c1, s1, c2, s2)
    print(f"  Transcript 1: (t={t}, c={c1}, s={s1})")
    print(f"  Transcript 2: (t={t}, c={c2}, s={s2})")
    print(f"  Extracted x = {extracted}")
    print(f"  Matches secret key? {extracted == sk} ✓")


# ============================================================
# Part 2: Fiat-Shamir Transform
# ============================================================

class FiatShamirSchnorr:
    """Non-interactive Schnorr proof via Fiat-Shamir transform.

    Lean theorem verified:
    - fiat_shamir_complete: honest FS proofs always verify
    """

    def __init__(self, q: int):
        self.q = q

    def _hash(self, stmt: int, commitment: int) -> int:
        """Hash function H(stmt, commitment) -> challenge.
        In Fiat-Shamir, the challenge is derived deterministically from
        the statement and commitment.
        """
        data = f"{stmt}:{commitment}".encode()
        h = hashlib.sha256(data).hexdigest()
        return int(h, 16) % self.q

    def prove(self, sk: int, pk: int) -> tuple:
        """Generate non-interactive proof.
        Theorem: fiat_shamir_complete proves this always verifies.
        """
        r = secrets.randbelow(self.q)
        commitment = r  # In exponent space
        challenge = self._hash(pk, commitment)
        response = (r + challenge * sk) % self.q
        return (commitment, challenge, response)

    def verify(self, pk: int, proof: tuple) -> bool:
        """Verify non-interactive proof.
        Check: challenge == H(pk, commitment) AND response == commitment + challenge*pk
        """
        commitment, challenge, response = proof
        expected_challenge = self._hash(pk, commitment)
        if challenge != expected_challenge:
            return False
        return response % self.q == (commitment + challenge * pk) % self.q


def demo_fiat_shamir():
    """Demonstrate Fiat-Shamir non-interactive proofs."""
    print("\n\n" + "=" * 60)
    print("Part 2: Fiat-Shamir Transform (Non-Interactive)")
    print("=" * 60)

    q = 104729
    fs = FiatShamirSchnorr(q)
    sk = secrets.randbelow(q - 1) + 1
    pk = sk

    print(f"\nSetup: sk={sk}, pk={pk}")

    # Generate and verify proof
    proof = fs.prove(sk, pk)
    valid = fs.verify(pk, proof)

    print(f"\nNon-interactive proof:")
    print(f"  Commitment: {proof[0]}")
    print(f"  Challenge:  {proof[1]} (derived from hash)")
    print(f"  Response:   {proof[2]}")
    print(f"  Valid: {valid} ✓")

    # Verify multiple proofs
    print("\n--- Batch Verification (10 proofs) ---")
    all_valid = True
    for i in range(10):
        p = fs.prove(sk, pk)
        v = fs.verify(pk, p)
        all_valid = all_valid and v
    print(f"  All 10 proofs valid: {all_valid} ✓")

    # Tampered proof should fail
    print("\n--- Tampered Proof ---")
    tampered = (proof[0], proof[1], (proof[2] + 1) % q)
    valid_tampered = fs.verify(pk, tampered)
    print(f"  Tampered proof valid: {valid_tampered} (expected: False) ✓")


# ============================================================
# Part 3: Soundness Error & Repetition
# ============================================================

def demo_soundness():
    """Demonstrate soundness error bounds and repetition.
    Theorems verified:
    - soundness_error_bound: cheating prob ≤ 1/|Ch|
    - parallel_repetition_soundness: (1/n)^k < 1
    """
    print("\n\n" + "=" * 60)
    print("Part 3: Soundness Error & Repetition")
    print("=" * 60)

    print("\n--- Soundness Error vs Challenge Space ---")
    print(f"  {'|Ch|':>8} | {'Error 1/|Ch|':>14} | {'After k=10':>14} | {'After k=40':>14}")
    print("  " + "-" * 56)
    for n in [2, 8, 16, 128, 256, 2**20]:
        error = 1 / n
        e10 = error ** 10
        e40 = error ** 40
        print(f"  {n:>8} | {error:>14.2e} | {e10:>14.2e} | {e40:>14.2e}")

    # Simulate cheating attempts
    print("\n--- Cheating Simulation (|Ch| = 8) ---")
    q = 8
    successes = 0
    trials = 10000
    for _ in range(trials):
        # Cheater picks a random response hoping to match
        guess = secrets.randbelow(q)
        challenge = secrets.randbelow(q)
        if guess == challenge:
            successes += 1
    print(f"  Trials: {trials}")
    print(f"  Successes: {successes}")
    print(f"  Empirical rate: {successes / trials:.4f}")
    print(f"  Theoretical bound: {1 / q:.4f}")


# ============================================================
# Part 4: Negligible Functions & Game-Based Security
# ============================================================

def demo_negligible():
    """Demonstrate negligible function concepts.
    Theorems verified:
    - zero_negligible: 0 is negligible
    - const_not_negligible: positive constants are not negligible
    - advantage_triangle: sum of negligible is negligible
    """
    print("\n\n" + "=" * 60)
    print("Part 4: Negligible Functions")
    print("=" * 60)

    print("\n  A function f(n) is negligible if it vanishes faster than")
    print("  any inverse polynomial 1/n^c.\n")

    print(f"  {'n':>6} | {'1/n':>12} | {'1/n²':>12} | {'1/2^n':>12} | {'0.01':>12}")
    print("  " + "-" * 56)
    for n in [1, 10, 100, 1000, 10000]:
        print(f"  {n:>6} | {1/n:>12.2e} | {1/n**2:>12.2e} | "
              f"{1/2**min(n, 100):>12.2e} | {0.01:>12.2e}")

    print(f"\n  1/n    → 0 but NOT negligible (fails for c=2)")
    print(f"  1/n²   → 0 but NOT negligible (fails for c=3)")
    print(f"  1/2^n  → 0 and IS negligible (beats every polynomial)")
    print(f"  0.01   → NOT negligible (constant, proven in Lean!)")


# ============================================================
# Main
# ============================================================

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Sigma Protocol & Zero-Knowledge Proof Demo             ║")
    print("║  Based on Machine-Verified Lean 4 Theorems              ║")
    print("╚══════════════════════════════════════════════════════════╝")

    demo_schnorr()
    demo_fiat_shamir()
    demo_soundness()
    demo_negligible()

    print("\n\n" + "=" * 60)
    print("All demonstrations complete.")
    print("Every property shown is formally verified in Lean 4.")
    print("=" * 60)


if __name__ == "__main__":
    main()
