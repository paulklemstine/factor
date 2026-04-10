# The Number Sieve Hidden Inside Ancient Geometry

*How a 2,500-year-old equation about right triangles could help crack the codes that protect your bank account*

---

You probably remember the Pythagorean theorem from school: $a^2 + b^2 = c^2$. The classic 3-4-5 right triangle. Simple, elegant, ancient.

But what happens when you add a dimension? What if instead of flat triangles, you consider points in three-dimensional space? The equation becomes $a^2 + b^2 + c^2 = d^2$ — and suddenly, this seemingly innocent generalization hides a powerful secret about the nature of numbers themselves.

## Three Windows into a Number's Soul

Consider the number 35 = 5 × 7. Now consider the equation $6^2 + 10^2 + 33^2 = 35^2$. Check it: 36 + 100 + 1089 = 1225 = 35². It works.

Here's the magic trick. Rearrange the equation three different ways:

- **Window 1:** $6^2 + 10^2 = (35 - 33)(35 + 33) = 2 \times 68 = 136$
- **Window 2:** $6^2 + 33^2 = (35 - 10)(35 + 10) = 25 \times 45 = 1125$  
- **Window 3:** $10^2 + 33^2 = (35 - 6)(35 + 6) = 29 \times 41 = 1189$

Each "window" — what mathematicians call a *channel* — splits the number 35 into a product of two factors. Look at Window 2: 25 × 45. Both 25 and 45 are divisible by 5. That immediately tells us that 5 divides 35. We've found a factor!

This isn't a coincidence. It's a mathematical law, and we've now proved it with mathematical certainty using computer verification.

## The GCD Cascade: A Factor-Finding Machine

The real power emerges when you have *multiple* solutions. The number $35^2 = 1225$ can be written as a sum of three squares in more than one way:

- $6^2 + 10^2 + 33^2 = 1225$
- $15^2 + 10^2 + 30^2 = 1225$

Each solution opens three windows, giving six windows total. The **GCD Cascade** systematically compares information from different windows:

1. Compute differences: $(35-33) = 2$ and $(35-30) = 5$
2. Compute GCDs: $\gcd(2, 5) = 1$ — not helpful here
3. But: $(35+33) = 68$ and $(35+30) = 65$, $\gcd(68, 65) = 1$
4. Cross-compare windows: $(35-10)(35+10) = 25 \times 45$, and $\gcd(25, 45) = 5$ — factor found!

We proved that this cascade has a mathematical structure called *transitivity*: once you find that a number $g$ divides $(d - c_1)$, and you know $g$ divides $(c_2 - c_1)$, then automatically $g$ divides $(d - c_2)$. Factor information *propagates* through the cascade like a chain reaction.

## Why This Matters for Your Bank Account

Modern internet security — the encryption protecting your bank transactions, medical records, and private messages — relies on the assumption that multiplying two large prime numbers is easy, but *un*-multiplying (factoring) the result is practically impossible. The RSA encryption system, used billions of times daily, depends on this asymmetry.

Any new mathematical insight into factoring is therefore of enormous practical and theoretical interest. The GCD Cascade framework doesn't break RSA — it's a theoretical framework, not a practical algorithm — but it reveals deep geometric structure in the factoring problem that was previously hidden.

The key insight: the problem of factoring a number $d$ is *equivalent* to understanding the geometry of integer points on a sphere of radius $d$ in three-dimensional space. Different points on the sphere correspond to different ways of writing $d^2$ as a sum of three squares, and the *relationships between* these points (their distances, angles, GCDs) encode the prime factorization of $d$.

## No Balanced Points Allowed

One of our most striking results is the **No Balanced Quadruple Theorem**: you can never have $a = b = c$ in a Pythagorean quadruple (unless everything is zero). Why? Because $3a^2 = d^2$ would mean $d/a = \sqrt{3}$, and $\sqrt{3}$ is irrational.

This means lattice points on the sphere are *forced away* from the body diagonal — the line where $a = b = c$. They're always asymmetric, always carrying different information in each of their three channels. This built-in asymmetry is what makes the cascade framework work.

## The Pell Equation Connection

When two components are equal ($a = b$), the quadruple equation becomes $2a^2 + c^2 = d^2$. Set $c = 1$, and you get $d^2 - 2a^2 = 1$ — the famous **Pell equation**, studied for over a thousand years.

The Pell equation has infinitely many solutions: $(d, a) = (3, 2), (17, 12), (99, 70), \ldots$ Each gives a Pythagorean quadruple: $(2, 2, 1, 3)$, $(12, 12, 1, 17)$, $(70, 70, 1, 99)$. These "Pell quadruples" have a special recursive structure: each can be computed from the previous one, forming an infinite chain of factoring opportunities.

## Higher Dimensions: More Windows, More Power

What if we go further? In four dimensions, $a^2 + b^2 + c^2 + d^2 = e^2$ (a Pythagorean quintuple), there are six pair-channels instead of three. We proved that their sum follows a beautiful pattern:

| Dimensions | Pair channels | Sum |
|-----------|--------------|-----|
| 3 (triples) | 1 | $c^2$ |
| 4 (quadruples) | 3 | $2d^2$ |
| 5 (quintuples) | 6 | $3e^2$ |
| 6 (sextuples) | 10 | $4f^2$ |
| 7 (septuples) | 15 | $5g^2$ |

The general formula: for $n$ spatial components, $\binom{n}{2}$ pair channels summing to $(n-1)y^2$. More dimensions means more windows, which means more factoring information — though finding the lattice points becomes harder too.

## Machine-Verified Mathematics

Every theorem in this work has been verified by computer using Lean 4, a proof assistant that checks mathematical reasoning with absolute rigor. No human error, no gaps in logic, no hand-waving. The proofs are as certain as the laws of logic themselves.

This represents a growing trend in mathematics: using computer verification not just to check existing results, but to *explore* new mathematical territory with confidence. When the computer confirms that your theorem is correct, you know it's correct — period.

## What's Next?

The GCD Cascade framework opens several exciting directions:

1. **Algorithmic development**: Can the cascade be made efficient enough for practical factoring?
2. **Quantum connections**: How does the geometry of integer spheres interact with quantum algorithms?
3. **Cryptographic implications**: What does the cascade tell us about the hardness of factoring?
4. **Higher-dimensional exploration**: As we add dimensions, does factoring become easier or harder?

The ancient Pythagoreans knew that numbers have geometric souls. Twenty-five centuries later, we're discovering that they were even more right than they imagined. The geometry of numbers isn't just beautiful — it's powerful, and it's hiding secrets we're only beginning to understand.

---

*The formal proofs are available in `Pythagorean__SharedFactorBridge__GCDCascade.lean`, verified in Lean 4 with zero remaining unproved statements.*
