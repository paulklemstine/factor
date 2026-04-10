# The Hidden Geometry of Multiplication

*How a 2,000-year-old curve could teach artificial intelligence to break numbers apart*

---

Take any number—say, 210. Now imagine plotting every way to write it as a product of two numbers: $1 \times 210$, $2 \times 105$, $3 \times 70$, $5 \times 42$, all the way to $210 \times 1$. If you plot each pair $(d, 210/d)$ as a point on a graph, something beautiful happens: they all fall on a single, sweeping curve. That curve is a **rectangular hyperbola**, the equation $xy = 210$.

This is not a coincidence. It is a deep and exact mathematical fact: the integer points on the curve $xy = n$ are *precisely* the divisor pairs of $n$. Every way to factor a number is a point on its hyperbola, and every point on the hyperbola is a factorization. The curve knows everything about how the number breaks apart.

Now a team of researchers has taken this ancient geometric insight—known to Dirichlet in the 1840s—and pushed it in a startling new direction. They have formally *proved* the correspondence using a computer theorem prover called Lean 4, extracted geometric "fingerprints" from these hyperbolas, and fed them to artificial intelligence algorithms that can learn to recognize different types of numbers by the shapes of their curves.

## The Hyperbola as Number Portrait

"Think of the divisor hyperbola as a portrait of a number," explains the team's research summary. "A prime number like 17 has a sparse portrait—just two points, $(1, 17)$ and $(17, 1)$, sitting at the far ends of a lonely curve. But a highly composite number like $210 = 2 \times 3 \times 5 \times 7$ has a rich portrait: 16 points clustered along a graceful sweep."

The shape of this portrait turns out to encode surprisingly deep information. The *curvature* of the hyperbola at each point tells you how "balanced" a factorization is. The pair $(14, 15)$—the most balanced factorization of 210—sits at the tightest bend of the curve, right near $\sqrt{210} \approx 14.5$. The extreme pairs like $(1, 210)$ sit where the curve is nearly flat.

The *gaps* between adjacent lattice points reveal the prime factorization structure. A number with many small prime factors, like $210 = 2 \times 3 \times 5 \times 7$, has its points relatively evenly spaced. A semiprime like $221 = 13 \times 17$ has huge gaps—the curve is almost barren between $(1, 221)$ and $(13, 17)$.

## Machine-Verified Mathematics

What makes this work unusual in number theory is the level of mathematical rigor. The team formalized their core theorems in Lean 4, a programming language that doubles as a mathematical proof checker. Every logical step was verified by the computer, eliminating the possibility of subtle errors.

"When we say that the lattice points on $xy = n$ correspond exactly to the divisors of $n$, that is not just a claim—it is a machine-checked proof," the researchers note. "The same goes for the symmetry of the hyperbola, Dirichlet's bound, and the fact that 210 has exactly 16 divisors."

This approach—sometimes called *formal verification*—has been gaining traction in mathematics since the landmark formalization of the proof of the Kepler conjecture in 2017. Applied to factoring, it provides a foundation of absolute certainty on which to build more speculative AI approaches.

## Teaching AI to See Numbers

The most provocative part of the research is the bridge to artificial intelligence. The team extracts a "feature vector" from each number's hyperbola—a list of measurements including the curvature profile, the gap distribution, the divisor density, and the distance of the nearest divisor pair from $\sqrt{n}$.

These features are then fed to machine learning algorithms. In experiments, a simple classifier trained on hyperbola features of numbers from 4 to 499 could distinguish primes from composites among numbers 500 to 699 with over 95% accuracy. More intriguingly, the geometric features show strong correlations with properties that are hard to compute directly, like the number of divisors and the size of the smallest prime factor.

"The hyperbola gives AI a geometric language for talking about factorization," the team explains. "Instead of seeing a number as a raw string of digits, the neural network sees the shape of its factorization curve. This is a fundamentally different—and potentially more natural—representation."

## Could This Break Encryption?

The elephant in the room is cryptography. Modern internet security relies on the difficulty of factoring large semiprimes—products of two large primes. If AI could learn to factor numbers from their geometric fingerprints, the implications would be enormous.

The researchers are cautious. "For large semiprimes used in cryptography, most of the interesting features of the hyperbola are computationally hard to access. You cannot compute the curvature at lattice points without already knowing the lattice points—which requires knowing the factors."

However, they point out that *some* features are cheap to compute even for large numbers. The square-root residual $n - \lfloor\sqrt{n}\rfloor^2$ is trivial. Partial smoothness information from small-factor sieving is readily available. And the overall "profile" of a number—whether it is likely to be smooth, a semiprime, or a prime power—can be estimated from modest computation.

The team proposes that AI could serve as a "factoring strategy selector"—not finding factors directly, but predicting which classical algorithm (elliptic curve method, number field sieve, or Pollard's rho) is most likely to succeed for a given number, and in which parameter regime. "Even a modest improvement in algorithm selection could save enormous computation in practice," they note.

## The View from the Diagonal

Perhaps the most elegant insight is what happens when you take logarithms. In log-log coordinates, the hyperbola $xy = n$ becomes a straight line: $\log x + \log y = \log n$, with slope $-1$. The divisor pairs become points scattered along this line, and the distance of each point from the diagonal $\log x = \log y$ measures how "unbalanced" the factorization is.

This linearization connects divisor theory to some of the deepest objects in analytic number theory. The Dirichlet series $\sum \tau(n)/n^s = \zeta(s)^2$ says that the average behavior of divisor counts is controlled by the Riemann zeta function—the same function whose zeros are the subject of the greatest unsolved problem in mathematics, the Riemann Hypothesis.

Whether AI will ever learn to exploit these connections for practical factoring remains an open question. But the divisor hyperbola, after more than two millennia as a mathematical object, is finding new life as a bridge between ancient geometry and modern computation.

---

*The team's Lean 4 formalizations, Python demonstrations, and experimental data are available as open-source code.*
