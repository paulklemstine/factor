# The Equation That Cannot Lie

## How Mathematicians Built a Machine That Proves Its Own Answers

*Can a computer not only solve an equation, but prove — beyond all doubt — that
its answer is correct? A new approach to ancient number puzzles does exactly that.*

---

In 1637, Pierre de Fermat scribbled a note in the margin of a book. He claimed
to have found a "truly marvelous proof" that certain equations have no solutions
in whole numbers, but the margin was "too narrow to contain it." It took 358 years
and thousands of pages of modern mathematics before Andrew Wiles finally proved
Fermat right.

Today, a different kind of revolution is unfolding. Mathematicians are no longer
just proving theorems — they're teaching computers to check those proofs, line by
line, with absolute certainty. And they've started with one of the oldest problems
in mathematics: solving equations in whole numbers.

### The Oldest Question in Math

A **Diophantine equation** — named after the 3rd-century Greek mathematician
Diophantus of Alexandria — is any equation where you're only allowed to use
whole numbers: 1, 2, 3, and so on. No fractions, no decimals, no square roots.

For example: is there a right triangle whose sides are all whole numbers?
The ancient Babylonians knew the answer: yes. The triple (3, 4, 5) works because
3² + 4² = 9 + 16 = 25 = 5². So do (5, 12, 13) and infinitely many others.

But here's what's remarkable: every single one of these "Pythagorean triples"
can be generated from (3, 4, 5) using exactly three simple operations. It's as
if (3, 4, 5) is the trunk of a tree, and three branching rules produce every
Pythagorean triple that will ever exist. This is the **Berggren tree**, discovered
in 1934.

### The Seven-Step Pipeline

Researchers have now built a seven-stage pipeline that takes a Diophantine
equation as input and produces a **machine-verified** solution as output. Here's
how it works, in broad strokes:

**Step 1: Encode.** Write the equation as a mathematical object a computer can
manipulate. "Find whole numbers x and y with 3x + 5y = 1" becomes a precise
formal statement.

**Step 2: Tropicalize.** Replace the hard operations (multiplication, addition)
with simpler ones (maximum, addition) to get a rough estimate of how big the
answer might be. This is like sketching the outline before painting the details.

**Step 3: Lift.** Map the problem onto a sphere using **stereographic projection** —
the same technique mapmakers use to flatten the globe. This transforms the
equation into geometry, where powerful tools become available.

**Step 4: Project.** Apply a mathematical "oracle" — a special function that,
when applied twice, gives the same result as applying it once. (Mathematicians
call this **idempotence**.) This is like a projector beam: once an image is on
the screen, shining the projector again doesn't change anything.

**Step 5: Descend.** Walk down the Berggren tree (for Pythagorean problems) or
use algebraic composition laws (for Pell equations) to find the actual integer
solution.

**Step 6: Decode.** Extract the answer as plain integers.

**Step 7: Verify.** Feed the answer into Lean 4, a proof assistant used by
mathematicians worldwide, which checks every logical step. If Lean accepts it,
the proof is correct — period.

### What the Computer Proved

Using this pipeline, 20 theorems have been formalized and machine-verified:

- **Bézout's Identity**: For any two numbers, you can always find a combination
  of them that equals their greatest common divisor. This 2,300-year-old result
  is the foundation of all linear Diophantine equations.

- **The Solvability Criterion**: The equation ax + by = c has whole-number
  solutions *if and only if* gcd(a, b) divides c. No exceptions, no special
  cases — this is a complete characterization.

- **Pell's Equation**: The equation x² − 2y² = 1 has infinitely many solutions,
  and they can all be generated from the starting solution (3, 2) using a simple
  recurrence. The solutions grow exponentially: (3, 2), (17, 12), (99, 70),
  (577, 408), ...

- **The √2 Barrier**: There are no positive whole numbers x and y with x² = 2y².
  This is the ancient proof that √2 is irrational, now machine-certified.

- **Fermat's Last Theorem for n = 4**: The equation x⁴ + y⁴ = z⁴ has no
  solutions in positive integers. Fermat himself proved this case around 1640;
  now a computer has verified his argument independently.

- **The Mod-4 Obstruction**: No number of the form 4k + 3 can be written as
  a sum of two squares. (Try it: 3, 7, 11, 15, 19 — none of them work.)

### Why Machine Verification Matters

In 1993, Andrew Wiles announced his proof of Fermat's Last Theorem. Then a gap
was found. It took another year to fix. In 1998, Thomas Hales proved the Kepler
Conjecture about sphere packing — but the referees said they were only "99%
certain" the proof was correct. Hales spent the next 20 years formalizing it in
a proof assistant to achieve 100% certainty.

Machine verification eliminates this uncertainty. When Lean accepts a proof,
it has checked every inference against the foundational axioms of mathematics.
There is no gap to find, no subtle error hiding in a 200-page argument. The
proof either compiles or it doesn't — just like software.

The key insight of the idempotent pipeline is that *verification is itself a
projection*. Checking a proof is an operation that, once performed, need never
be repeated. The proof is either valid or it isn't. There's no "partially
verified" — the projection snaps you to one state or the other.

### The Bigger Picture

In 1900, the great mathematician David Hilbert posed 23 problems for the
20th century. His Tenth Problem asked: "Is there a general algorithm to decide
whether any Diophantine equation has solutions?" In 1970, Yuri Matiyasevich
proved the answer is *no* — no such algorithm can exist.

But this doesn't mean we can't solve *specific* equations. The pipeline
described here handles linear equations completely, quadratic equations in many
important cases, and provides a framework for extending to higher degrees. Each
solved case adds another verified building block to our mathematical knowledge.

Perhaps most importantly, the pipeline demonstrates that the gap between
"finding an answer" and "proving an answer is correct" can be bridged
automatically. The computer doesn't just solve — it *knows why* the solution
works, and it can show its work in a form that any mathematician (or any other
computer) can verify independently.

The margin of Fermat's book may have been too narrow for his proof. But inside
a computer, there is always room for one more theorem.

---

*The formalization described in this article uses Lean 4.28.0 with the Mathlib
library. The complete source code, including Python demonstrations with
visualizations, is available in the project repository.*
