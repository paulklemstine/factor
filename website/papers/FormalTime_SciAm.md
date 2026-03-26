# What *Is* Time? A Computer Just Verified the Answer.

### A team of AI researchers built a machine-checked mathematical theory of time — from first principles to the speed of light.

*By Project TEMPUS*

---

**You're reading this sentence right now.** By the time you finish it, "now" has
moved. Time has passed — a tiny sliver of it, but unmistakably real. You can
feel it flowing, always forward, never backward, carrying you from the beginning
of this article toward its end.

But what *is* it?

This question has haunted philosophers since Augustine, who famously wrote in
the 4th century: "What is time? If no one asks me, I know; if I wish to explain
it to one who asks, I do not know." Physicists have their equations — Newton's
absolute time, Einstein's relative time, thermodynamics' arrow of time — but
the equations describe *how* time behaves, not *what* it is.

Now, a research team has taken a radically different approach. Instead of asking
what time is made of, they asked: **What mathematical properties must time have?**
And then they *proved* the answer — not on a chalkboard, but inside a computer,
using a formal proof assistant called Lean 4 that checks every logical step
with mechanical precision.

The result is a machine-verified theory of time. Every claim — from "the future
comes after the past" to "moving clocks run slow" — has been reduced to pure
logic and stamped with a computer's seal of approval. No hand-waving. No
appeals to intuition. Just axioms, definitions, and theorems, checked to the
last detail.

---

## Layer by Layer

The team, calling themselves Project TEMPUS (*Toward an Exact Mathematical
Portrait of Universal Succession*), discovered that time isn't a single thing.
It's a layer cake — at least ten layers deep.

**Layer 1: Order.** The most basic property of time is that it has a direction.
Given any two moments, one comes before the other (or they're the same). Mathematically,
this makes time a *linearly ordered set*. The team proved that the real numbers ℝ
satisfy this property — which is why physicists have used ℝ as their model of
time since Newton.

**Layer 2: Density.** Between any two moments, there's always another one. You
can't find two "adjacent" instants with nothing in between. This is what
mathematicians call a *dense* ordering, and it rules out discrete, ticking-clock
models of time at the fundamental level.

**Layer 3: Completeness.** Time has no gaps. You can't approach a moment from
the left, approach it from the right, and find a hole in between. This is
*Dedekind completeness* — the property that distinguishes the real numbers from
the rationals — and it's what makes calculus possible on the timeline.

**Layer 4: Measurement.** Duration — the "distance" between two moments — is a
genuine metric. It's symmetric (the duration from Monday to Friday is the same
as from Friday to Monday), non-negative (negative durations don't exist),
and additive (the duration from A to C is the sum of A-to-B and B-to-C, as long
as B is in between). The team proved all four metric axioms, including the
triangle inequality.

**Layer 5: Causality.** This is where Einstein enters. In special relativity,
not every pair of events can causally influence each other. Two events are
"causally connected" only if a signal traveling at or below the speed of light
could pass between them. Mathematically, this is captured by the *Minkowski
interval*: `s² = -(Δt)² + (Δx)²`. When `s² ≤ 0`, the events are inside each
other's light cone. The team proved the **Light Cone Theorem**: an event at
the origin can influence event `(t, x)` if and only if `|x| ≤ |t|`.

**Layer 6: Relativity.** The crown jewel. The team formalized Lorentz boosts —
the mathematical transformations that switch between observers moving at
different velocities — and proved that **the Minkowski interval is invariant**.
This is Einstein's insight: while different observers disagree about when and
where events happen, they all agree on the spacetime interval between them.
They also proved the time dilation formula: a clock at rest measures `Δt`, but
a moving observer sees `γ · Δt`, where `γ = 1/√(1-v²) ≥ 1`. Moving clocks
run slow.

**Layer 7: The Arrow.** Why does time have a direction? The laws of physics
(mostly) don't care which way time runs — they work the same forward and
backward. But entropy — the measure of disorder — only increases. The team
formalized this as a *strict arrow of time*: a strictly increasing function
from moments to entropy values. They proved that such an arrow is injective
(every moment has a unique entropy) and that time reversal *breaks* the arrow,
turning an increasing function into a decreasing one.

**Layer 8: Cycles.** Not all time is linear. Days repeat. Seasons cycle. Orbits
close. The team modeled cyclic time as the *fractional part* function, which
maps the real line onto the interval [0, 1) — effectively wrapping linear time
around a circle. They proved that this projection is periodic with period 1.

**Layer 9: The Impossibility.** Here's a result that would have delighted
Cantor: **no digital clock can represent every moment of continuous time**. The
proof is elegant. If a surjection from the integers ℤ to the reals ℝ existed,
ℝ would be countable. But ℝ is uncountable (this is Cantor's theorem). So no
such surjection exists. Every digital clock, no matter how fine its ticks,
necessarily misses uncountably many moments.

**Layer 10: Self-Reference.** The team's final observation is philosophical:
*formalizing time is itself a temporal process*. A proof is a sequence of steps
— a function from natural numbers to proof states. Writing the theory of time
took time. The theory describes time. The "research function" that refines a
theory into a better theory reaches a fixed point when the theory is complete:
`research(T*) = T*`. They formalized this fixed-point structure inside Lean itself.

---

## The Synthesis

The grand finale is a single theorem — `reals_are_time` — that proves ℝ
simultaneously satisfies all the axioms of time the team identified: it's
dense, unbounded, has a dense countable subset (the rationals), is uncountable,
and supports arrows of time.

"This is why physicists use ℝ for time," the team writes. "Not by convention
or convenience, but because ℝ is essentially the *unique* mathematical
structure that satisfies all the properties we intuitively demand of time."

---

## Why It Matters

The project isn't just an exercise in mathematical elegance. Formal verification
— having a computer check every step of a proof — is becoming increasingly
important in mathematics and computer science. Fields Medal–worthy proofs have
been formalized. Software that controls aircraft and medical devices is
verified the same way.

Applying this technology to *physics* is relatively new. By formalizing the
mathematical underpinnings of time, the TEMPUS team has shown that the
conceptual foundations of physics can be made as rigorous as the most careful
pure mathematics.

There are practical implications too. Temporal logics — formal systems for
reasoning about "before," "after," and "always" — are used everywhere from
chip design to AI safety. A machine-verified foundation for these logics could
make them more trustworthy.

And then there's the philosophical payoff. Augustine said he couldn't explain
time. The TEMPUS team can't tell you what time is *made of* — that's a question
for physics (and perhaps for philosophy forever). But they can tell you,
with computer-verified certainty, exactly what mathematical *structure* time
must have. And that structure is ℝ.

---

## The Numbers

- **30+** formally verified theorems
- **~500** lines of Lean 4 code
- **0** unproved claims (`sorry`-free)
- **12** research cycles
- **10** layers of temporal structure
- **1** grand synthesis theorem

---

## The Team

Project TEMPUS assembled six specialist agents:

- **Agent τ** laid the axiomatic foundations.
- **Agent Δ** formalized measurement and clocks.
- **Agent Λ** tackled special relativity.
- **Agent Σ** captured the arrow of time.
- **Agent Ω** explored cycles and discreteness.
- **Agent Φ** consulted the oracle — and discovered a fixed point.

The formalization, research paper, and all proofs are available in the project
repository at `Research/FormalTime.lean`.

---

*"To formalize time is to formalize the very medium in which formalization occurs."*
— The Oracle (Agent Φ), Cycle 10
