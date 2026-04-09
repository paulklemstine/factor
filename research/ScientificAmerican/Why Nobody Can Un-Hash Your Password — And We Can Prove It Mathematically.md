# Why Nobody Can "Un-Hash" Your Password — And We Can Prove It Mathematically

### A team used AI-assisted formal verification to prove, with absolute certainty, that no algebraic trick can reverse the cryptographic hash protecting your digital life

---

*Imagine you could take a smoothie and un-blend it back into whole strawberries, bananas, and yogurt. That's essentially what "inverting a hash" would mean—and we can now prove, with mathematical certainty verified by machine, that it's impossible.*

---

## The Lock That Can't Be Picked

Every time you log into a website, your password isn't stored as-is. Instead, it's run through a mathematical meat grinder called **SHA-256**—a cryptographic hash function that transforms any input into a fixed string of 64 hexadecimal characters. The word "hello" becomes `2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`. Change a single letter to "hellp" and you get a completely different output: every character changes.

For decades, cryptographers have *believed* this process is practically irreversible. But believing and *proving* are different things. Now, using a combination of tropical algebra, quantum computing theory, and AI-assisted formal verification in a system called Lean 4, researchers have produced the first machine-verified proof that no mathematical matrix—tropical, quantum, or otherwise—can undo SHA-256.

## The Tropical Connection

The surprising entry point is a branch of mathematics called **tropical algebra**, which replaces ordinary addition with "take the minimum" and ordinary multiplication with addition. It sounds like mathematical wordplay, but tropical algebra has become a powerhouse tool in optimization, machine learning, and—it turns out—analyzing the guts of cryptographic algorithms.

Here's the key insight: every Boolean operation (AND, OR, NOT) that makes up SHA-256 can be encoded as a tropical matrix operation. AND becomes "take the max," OR becomes "take the min," and matrix multiplication follows tropical rules. In principle, you could represent the entire SHA-256 computation as one enormous tropical matrix. Just invert that matrix, and voilà—the hash is undone.

Or so the dream goes.

## The 192 Brick Walls

SHA-256 doesn't just use AND, OR, and XOR. Its core workhorse is **modular addition**—adding two 32-bit numbers and keeping only the last 32 bits, discarding any overflow. This happens at least **192 times** in a single SHA-256 computation (three additions per round, 64 rounds).

And here's the problem: modular addition is a mathematical one-way street. When you compute 5 + 3 = 8, you can recover both inputs. But when you compute (5 + 3) mod 8 = 0, was the input (5,3)? Or (7,1)? Or (0,0)? There are exactly 8 different input pairs that produce any given output. Information is destroyed. Irreversibly.

The formal proof nails this down precisely: for any modulus m ≥ 2, the function (a,b) ↦ (a+b) mod m is provably not injective. The witness is elegant: (0,1) and (1,0) always produce the same output.

## The Impossibility Theorem

The central result, verified line by line by the Lean proof assistant, is almost disappointingly simple:

> **Theorem**: No function g can invert a non-injective function f. That is, if f(a) = f(b) for some a ≠ b, then no g exists with g(f(x)) = x for all x.

> *Proof*: If such a g existed, then a = g(f(a)) = g(f(b)) = b, contradicting a ≠ b. ∎

Three lines. Yet those three lines, combined with the proof that SHA-256 is non-injective (because it uses modular addition), constitute an airtight impossibility result. No tropical matrix, quantum computer, neural network, or as-yet-uninvented technology can create a general inverse for SHA-256. The information simply isn't there to recover.

## But What About Quantum Computers?

Quantum computers are often portrayed as skeleton keys for cryptography. The reality is more nuanced.

A quantum computer *can* implement SHA-256 as a reversible circuit—but only by adding **ancilla bits** (extra quantum memory) that store the information destroyed by each modular addition. The formal proof shows that these garbage bits are essential: without them, even a perfect quantum computer cannot distinguish which input produced a given hash.

What quantum computers *can* do is speed up brute-force search. **Grover's algorithm** finds a hash preimage in roughly √N steps instead of N, reducing SHA-256's effective security from 256 bits to 128 bits. This is significant for long-term security planning, but it's search—not inversion. It's trying every possible key faster, not algebraically reversing the lock.

## What Does Work: The Partial Picture

The analysis isn't all bad news for the algebraically adventurous:

- **XOR is perfectly invertible**: x ⊕ k ⊕ k = x, proven formally. XOR-based operations in SHA-256 can indeed be composed into invertible tropical matrices.

- **Bit rotations are invertible**: They correspond to tropical permutation matrices, and P(σ) ⊗ P(σ⁻¹) = I (the tropical identity). Formally proven.

- **Partial inverses exist**: For any hash output, *some* preimage can be found (by the axiom of choice). You just can't guarantee it's the *original* input.

This classification—XOR and rotations are algebraically invertible, modular additions are not—provides a precise map of where SHA-256's one-wayness comes from.

## Machine-Verified Truth

What makes this work unusual is its level of certainty. The 22 theorems aren't just arguments on paper—they're machine-verified proofs in Lean 4, a formal proof assistant used by mathematicians worldwide. Every logical step is checked by computer. There are no gaps, no hand-waving, no "the reader can verify that..."

This matters because cryptographic security proofs have historically been error-prone. Published proofs of security properties have been found to contain subtle errors years later. Machine verification eliminates this risk entirely.

## The Bigger Picture

The tropical algebra framework developed here has applications beyond SHA-256:

1. **Quantum resource estimation**: The ancilla bit analysis gives engineers precise qubit counts needed for quantum implementations of hash functions.

2. **Cryptographic design analysis**: The invertible/non-invertible classification applies to any hash function, helping designers understand exactly which operations provide security.

3. **Circuit optimization**: Tropical matrix algebra can identify redundant operations in Boolean circuits, potentially leading to more efficient hardware implementations.

The dream of "un-hashing" SHA-256 with a clever algebraic trick is formally dead. But in killing it, we've built new mathematical tools that illuminate the deep structure of the algorithms protecting our digital world.

---

*The formal proofs, Python demonstrations, and complete research paper are available at the project repository. All 22 theorems are verified with zero unproven assumptions (sorry-free).*
