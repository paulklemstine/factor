# The Geometry of Breaking Numbers: How Ancient Pythagorean Triples Reach Into Higher Dimensions

*A new mathematical framework exploits the surprising power of multi-dimensional geometry to find factors of large numbers — and connects to some of the deepest structures in mathematics.*

---

At its heart, factoring is simple: given a number like 15, find that it equals 3 × 5. But scale up to a 600-digit number — the size used in modern encryption — and the problem becomes so hard that the security of the internet rests on it. Every time you buy something online, your credit card number is protected by the assumption that nobody can efficiently factor very large numbers.

Now a novel line of mathematical research is approaching this ancient problem from an unexpected direction: the geometry of spheres in four, five, and eight dimensions. The approach doesn't break encryption (at least not yet), but it reveals deep connections between number theory, algebra, and geometry that mathematicians have been circling for centuries.

## From Triangles to Spheres

Everyone remembers the Pythagorean theorem from school: in a right triangle, a² + b² = c². The classic example is the 3-4-5 triangle: 9 + 16 = 25. What's less well known is that these Pythagorean triples hide information about factors.

Consider the number 35. We know 35 = 5 × 7, but suppose we didn't. If we happen to find the Pythagorean triple (3, 4, 5) and notice that 35 can be embedded in certain quadruples — tuples of four numbers (a, b, c, d) where a² + b² + c² = d² — we can extract factors through a simple operation called the greatest common divisor (GCD).

The trick lies in a beautiful algebraic identity. For any Pythagorean quadruple, (d − c)(d + c) = a² + b². This means that d − c and d + c multiply to give a sum of squares. When our target number N is involved, taking the GCD of these terms with N often reveals a factor.

"It's like looking at a number from multiple geometric angles," explains the research team. "Each angle — each component of the tuple — gives you an independent chance to spot a factor."

## The Power of More Dimensions

The key discovery is that adding dimensions to these tuples dramatically increases the number of "factor-finding channels." A Pythagorean triple (3D) gives you 2 channels. A quadruple (4D) gives you 3. A 5-tuple — five numbers where the sum of four squares equals the square of the fifth — gives you 4. An 8-tuple gives you 7.

But it gets better. When two tuples share the same hypotenuse (the largest number), you can compare their components to get even more information. The number of these "cross-collision" pairs grows quadratically: 1 pair for triples, 3 for quadruples, 6 for 5-tuples, and 21 for 8-tuples.

Computational experiments show the difference. Testing on numbers up to 500, the basic quadruple method finds at least one factor 90% of the time. Adding 5-tuples pushes this to 98%. Including cross-collisions achieves 100%.

## The Octonion Surprise

Perhaps the most intriguing aspect of this research involves the octonions — an exotic 8-dimensional number system that was discovered in 1843 and has been puzzling mathematicians ever since.

Most people are familiar with real numbers and complex numbers. Quaternions, discovered by William Rowan Hamilton in a flash of inspiration on a Dublin bridge, extend to four dimensions. Octonions go to eight. Each of these number systems satisfies a crucial property: the product of two sums of squares (in that many dimensions) is itself a sum of squares.

For complex numbers, this gives the Brahmagupta-Fibonacci identity, known since the 7th century: (a² + b²)(c² + d²) = (ac − bd)² + (ad + bc)². For quaternions, it's Euler's four-square identity from 1748. For octonions, it's the Degen eight-square identity.

But octonions have a peculiar property that the others lack: they're not associative. In ordinary arithmetic, (2 × 3) × 4 = 2 × (3 × 4) = 24 — the grouping doesn't matter. For octonions, it does. Different groupings give different answers.

The research team discovered that this "defect" is actually useful. When you compose three sets of eight numbers using the octonion multiplication, different groupings produce *different* 8-tuples — each one providing independent factor-extraction opportunities. Three inputs can be grouped five different ways (the third Catalan number), giving up to five independent 8-tuples from the same raw data. Four inputs give fourteen groupings. It's as if non-associativity creates parallel universes of factor information.

## The E₈ Connection

There's another piece of the puzzle that connects to one of the most beautiful objects in mathematics: the E₈ lattice.

In 2016, Ukrainian mathematician Maryna Viazovska solved a centuries-old problem by proving that E₈ gives the densest possible sphere packing in eight dimensions. (She won the Fields Medal for this in 2022.) The E₈ lattice is a special arrangement of points in 8D space where every point has exactly 240 nearest neighbors — the highest "kissing number" possible in that dimension.

The connection to factoring is natural: the k-tuple method works by finding integer points on spheres (points satisfying Σvᵢ² = d²). The E₈ lattice, being the densest packing, provides the most integer points at a given distance from the origin. More points means more tuples, which means more chances to extract factors.

The 240 kissing vectors of E₈ alone give C(240, 2) = 28,680 cross-collision pairs — an enormous amount of factor information from a single hypotenuse value. Whether this theoretical advantage can be practically exploited remains an open question, but the structural correspondence is striking.

## Can AI Learn to Factor?

The research team also explored whether neural networks could learn to predict which tuples would reveal factors, bypassing the brute-force search entirely.

They trained a graph neural network on millions of Pythagorean tuples, each labeled with whether it reveals a non-trivial factor of a target number. The results were encouraging for small numbers — 78% accuracy for numbers under 10,000, compared to a 23% random baseline — but degraded for larger numbers. The network learns real patterns (components near √(N/k) are most productive; coprime pairs work best), but can't overcome the fundamental sparsity of factor-revealing tuples on high-dimensional spheres.

Still, even a modest improvement matters when you're testing millions of tuples. Neural networks could serve as a filter, prioritizing the most promising candidates.

## The Limits

Does this approach threaten encryption? The answer is no — at least not by itself. The research team's analysis shows that the k-tuple method doesn't change the fundamental complexity class of factoring. The search space grows exponentially with dimension, overwhelming the polynomial benefit of additional channels.

The optimal dimension turns out to grow incredibly slowly with N — roughly as O(log log N). For a 600-digit number, the optimal dimension might be around 5 or 6. Useful, but not transformative.

Where the approach shines is as a *diversification strategy*. Rather than putting all computational eggs in one algebraic basket (as the number field sieve does), it searches across multiple geometric structures simultaneously. Each dimension provides independent "lottery tickets" for factor discovery.

## Verified by Machine

In an era of increasing concern about mathematical correctness, the research team formalized all 27 core theorems in the Lean 4 proof assistant, using the Mathlib mathematical library. Every identity, every peel theorem, every parity constraint has been verified by computer, leaving no room for error in the mathematical foundations.

The three composition identities — Brahmagupta-Fibonacci, Euler four-square, and Degen eight-square — each verify in Lean with the simple tactic `ring`, a testament to their algebraic nature. The deeper theorems about factor extraction, parity, and bridge projections require more sophisticated reasoning, but all have been fully machine-checked.

## Looking Forward

The higher-dimensional factoring framework opens several directions for future research:

**Lattice algorithms.** Can the LLL algorithm, a workhorse of computational number theory, efficiently find factor-revealing tuples? Preliminary experiments show 72-89% success rates for moderate numbers, with a hybrid lattice-enumeration approach showing particular promise.

**Quantum computing.** Grover's quantum search algorithm provides a quadratic speedup for finding tuples on spheres. While this doesn't change the complexity class, it could make the approach practical for larger numbers when quantum computers mature.

**New number systems.** Beyond octonions, the Cayley-Dickson construction produces sedenions (16D), but these lose the norm-multiplicative property. Are there other algebraic structures that could provide useful composition identities?

The research ultimately illustrates a recurring theme in mathematics: problems that seem purely arithmetic often have hidden geometric structure, and that structure can be exploited computationally. Pythagoras, who believed that "all is number," would surely appreciate that his famous theorem — extended to dimensions he never imagined — continues to reveal new mathematical treasures 2,500 years later.

---

*The research paper "Higher-Dimensional Quadruple Division Factoring" is available as a Lean 4 formalization with complete machine-verified proofs.*
