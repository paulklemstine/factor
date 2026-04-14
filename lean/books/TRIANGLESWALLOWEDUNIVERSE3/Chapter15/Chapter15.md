# Chapter 15 — *The Algebra Where Two Plus Three Equals Two: Tropical Geometry and the Shortest-Path Semiring*

---

## The Calculator That Forgot How to Add

Imagine, if you will, a calculator with a peculiar defect. Every time you press the "$+$" key, it returns whichever of the two numbers is *smaller*. And pressing "$\times$" gives you — of all things — their ordinary sum. On this deranged little machine, $7 \oplus 3 = 3$, while $7 \odot 3 = 10$. The readout of $2 \oplus 5$ is not $7$ but $2$. The product $2 \odot 5$ is not $10$ but $7$. Everything you learned in third grade has been stood on its head.

[ILLUSTRATION: A whimsical blueprint-style diagram of a calculator keypad. The "$+$" key is relabeled "$\min$" in tropical-orange ink, and the "$\times$" key is relabeled "$+$". Beside the calculator, a small table shows several example computations: $5 \oplus 3 = 3$, $5 \odot 3 = 8$, $2 \oplus 2 = 2$, $2 \odot 2 = 4$. At the bottom, the "equals" key emits a small question-mark cloud.]

Here is the puzzle I would like you to consider before reading further: *does this broken calculator still obey the familiar laws of arithmetic?* Can you commute? Associate? Distribute multiplication over addition? Or does the redefinition of "$+$" as "take the minimum" shatter the algebraic contract?

The answer — and this is what makes the subject irresistible — is that the contract survives. Not merely survives, but *thrives*. The system $(\mathbb{Z} \cup \{\infty\},\; \oplus,\; \odot)$, where

$$a \oplus b = \min(a, b), \qquad a \odot b = a + b,$$

satisfies every axiom of a semiring. Tropical addition is commutative, because the smaller of $a$ and $b$ is the smaller of $b$ and $a$:

$$a \oplus b = \min(a,b) = \min(b,a) = b \oplus a.$$

It is associative, because the minimum of three numbers does not depend on which pair you compare first:

$$(a \oplus b) \oplus c = \min(\min(a,b),\, c) = \min(a,\, \min(b,c)) = a \oplus (b \oplus c).$$

And there is even a "zero" — an identity element for this strange addition. But here the paradox deepens. In ordinary arithmetic, zero is the humblest number, smaller than every positive integer. In tropical arithmetic, "zero" is $\infty$: the number larger than all others. Add it to anything and nothing changes:

$$a \oplus \infty = \min(a, \infty) = a.$$

The tropical zero is infinitely large. It is the identity precisely *because* it always loses the minimum contest — a wallflower at the party of numbers, content to let every other guest win.

A reader exercise: what is the tropical "one"? That is, what element $e$ satisfies $a \odot e = a$ for all $a$? Since $a \odot e = a + e$, we need $e = 0$. Ordinary zero is the tropical multiplicative identity. The familiar and the bizarre cohabit the same equation.

The name "tropical" honors the Brazilian mathematician Imre Simon, who pioneered the study of min-plus algebras in the 1980s at the University of São Paulo. His colleagues in Paris, charmed by the provenance, coined the adjective — one of those moments when mathematics names a deep structure not by its content but by its geography. It is as if we called Euclidean geometry "Alexandrian" because Euclid worked in Egypt.

---

## A Distributive Law That Actually Works

Here is a dare. Ordinary multiplication distributes over ordinary addition: $a \times (b + c) = a \times b + a \times c$. Everyone learns this by age ten. But does the same law survive in the upside-down world of tropical arithmetic?

Before you read on, try it yourself with $a = 4$, $b = 7$, $c = 2$. Compute both sides of

$$a \odot (b \oplus c) \;\stackrel{?}{=}\; (a \odot b) \oplus (a \odot c).$$

The left side: $4 \odot (7 \oplus 2) = 4 \odot \min(7,2) = 4 \odot 2 = 4 + 2 = 6$.

The right side: $(4 \odot 7) \oplus (4 \odot 2) = (4+7) \oplus (4+2) = 11 \oplus 6 = \min(11, 6) = 6$.

They agree. And they always will. The tropical distributive law, translated back into ordinary notation, reads:

$$a + \min(b, c) = \min(a + b,\; a + c).$$

Why does this hold universally? Because shifting two numbers by the same amount $a$ does not change which is smaller. If $b < c$, then $a + b < a + c$, so $\min(a + b,\, a + c) = a + b = a + \min(b,c)$. The argument for $b \ge c$ is symmetric.

[ILLUSTRATION: A number line running from $0$ to $15$. Two points are marked at $b = 7$ and $c = 2$, with an arc labeled "$\oplus$" pointing to $2$ (the minimum). Then the entire line is shifted right by $a = 4$ (shown as a translucent orange overlay), placing the shifted points at $11$ and $6$, with a new arc pointing to $6$. The caption reads: "Shifting preserves the winner."]

So our broken calculator is a genuine *semiring* — it obeys every axiom of a ring except one: tropical addition has no inverses. You can take a minimum, but you cannot "un-take" it. Once the smaller number wins, the larger is forgotten. This asymmetry will haunt us for the rest of the chapter.

---

## When Infinity Is Your Friend

Let us linger a moment on that strange identity element $\infty$. We have enlarged the integers to $\mathbb{Z} \cup \{\infty\}$ — mathematicians sometimes call this $\text{WithTop}\;\mathbb{Z}$, the integers crowned with a point at infinity. Without this extra element, the system has no identity for $\min$: there is no finite integer that is larger than *all* others. The moment we adjoin $\infty$, everything clicks.

[ILLUSTRATION: A vertical "totem pole" of integers from $-3$ up to $+5$, with a cloud at the very top labeled "$\infty = $ tropical zero". An arrow from any integer $a$ to the cloud is labeled "$\oplus$", and the result arrow points back to $a$. The caption: "The king of all numbers does nothing when added."]

There is a pleasing duality here. In classical algebra, the additive identity sits at the *bottom* of the natural ordering — zero is the smallest non-negative integer. In tropical algebra, it sits at the *top*. This is a shadow of a deeper symmetry: one can build a mirror-image system, the **max-plus algebra**, where $a \oplus b = \max(a,b)$ and the identity is $-\infty$. Everything we prove in the min-plus world has a twin in the max-plus world, related by flipping the number line. Economists, who think in terms of maximizing profit rather than minimizing cost, tend to prefer the max-plus convention. Mathematicians, who are congenitally attracted to the austere, favor the minimum. Both are looking at the same algebra through opposite ends of the telescope.

Euler himself would not have blinked at any of this. The man who cheerfully wrote $1 + 2 + 3 + \cdots = -\tfrac{1}{12}$ and who routinely extended functions to infinite and imaginary arguments would have found a world where $\infty$ plays the role of zero perfectly natural. Extended number systems are among the oldest tools in the mathematical workshop; the tropical semiring is merely the newest tenant in a very old building.

---

## Two Candidates, One Winner

A polynomial $f(x) = 3x^2 + 7x + 2$ has three coefficients: $3$, $7$, and $2$. Now "tropicalize" it — strip away the polynomial structure and take the tropical sum of the coefficients: $3 \oplus 7 \oplus 2 = \min(3, 7, 2) = 2$. The minimum is $2$, and it was contributed by the constant term.

This is the observation that makes tropical algebraic geometry possible: *the minimum of any finite set of integers is always achieved by at least one member of the set.* In symbols, for two terms:

$$\min(a_0,\, a_1) = a_0 \quad \text{or} \quad \min(a_0,\, a_1) = a_1.$$

It sounds trivially obvious — and in tropical arithmetic, it is. But notice what makes it special: in *classical* arithmetic, a sum $a + b$ almost never equals $a$ or $b$ individually. The tropical world is different. One of the inputs always *wins*. There is no blending, no compromise. Addition is a contest, not a collaboration.

[ILLUSTRATION: A coordinate plane with horizontal axis labeled "exponent $i$" and vertical axis labeled "valuation $a_i$". Three points are plotted: $(0, 2)$, $(1, 7)$, $(2, 3)$. The lower convex hull is drawn as two line segments connecting $(0,2)$ to $(2,3)$, passing below $(1,7)$. The slopes of the hull segments are labeled. Caption: "The Newton polygon of $2 \oplus 7x \oplus 3x^{\odot 2}$: roots live at the slope-breaks."]

This "winner-take-all" property connects directly to **Newton polygons**, a tool that Isaac Newton himself used in his 1676 correspondence with Leibniz. Given a polynomial $\sum a_i x^i$, plot the points $(i, a_i)$ and take the lower convex hull. The slopes of this hull correspond to the roots of the tropicalized polynomial. Newton used the device to approximate roots of equations over three centuries before anyone dreamed of calling it "tropical." One of those beautiful retroactive revelations: a 300-year-old tool turned out to be secretly about an algebra that hadn't been invented yet.

---

## The Tropical Convex Hull, or: The Winner Never Loses

If you are the smallest number at a party, you are automatically no larger than any other guest. This kindergarten observation is actually a theorem in tropical convex geometry:

$$\text{If } c = \min(a, b), \quad \text{then } c \le a \text{ and } c \le b.$$

Or, in tropical notation: if $c = a \oplus b$, then $c \le a$ and $c \le b$. The winner of a minimum contest is no larger than either contestant — the winner never loses.

[ILLUSTRATION: Two side-by-side panels. LEFT: Classical convex hull — a shaded triangle with vertices $A$, $B$, $C$ in $\mathbb{R}^2$, showing the line segment from $A$ to $B$ and the interior. RIGHT: Tropical convex hull — a staircase-shaped region in $\mathbb{R}^2$ formed by taking componentwise minima of the same three points, with characteristic "L-shaped" contours. Caption: "Classical versus tropical convexity: smooth triangles become staircase polygons."]

In classical geometry, the convex hull of a set of points is the intersection of all half-planes containing them — a smooth, rounded shape built from weighted averages $\lambda a + (1 - \lambda)b$ for $\lambda \in [0,1]$. In tropical geometry, the "convex combination" is simply the componentwise minimum. The resulting shapes are not smooth at all: they are staircase polygons, angular and piecewise-linear, with sharp corners where the minimum switches from one coordinate to another. This is the geometry of optimization — and, as we shall see, of shortest paths.

---

## The Triangle Inequality in a World Without Triangles

Every child who has tried to build a triangle from three sticks knows the rule: the longest stick must be shorter than the other two combined. Formally, for any three points $x$, $y$, $z$ in a metric space:

$$d(x,\, z) \;\le\; d(x,\, y) + d(y,\, z).$$

Does this law still hold if we replace ordinary addition with tropical addition? In fact, it does more than hold — it *becomes the fundamental axiom* of the tropical metric. In the tropical setting, the triangle inequality is not a theorem to be derived but an axiom to be imposed. The inequality says: the direct path is never more expensive than the detour. Once you accept it, a rich geometry unfolds.

[ILLUSTRATION: Three cities ($x$, $y$, $z$) arranged on a road map, with roads of integer length connecting them. The direct road from $x$ to $z$ has length $d(x,z) = 5$, while the detour through $y$ has total length $d(x,y) + d(y,z) = 3 + 4 = 7$. An inequality symbol "$\le$" floats between the two paths. Caption: "The shortest path never detours — the triangle inequality as a shortest-path principle."]

Maurice Fréchet introduced the notion of an abstract metric space in his 1906 thesis — a mathematical universe defined entirely by a distance function satisfying three axioms: non-negativity, symmetry, and the triangle inequality. Tropical metric spaces are the newest members of this century-old family, where distance measures not Euclidean length but *cost* — the minimum total weight of traveling between two nodes in a network.

---

## The Traveling Salesman's Secret Algebra

A delivery driver must find the shortest route between $n$ cities. This is the legendary Traveling Salesman Problem, NP-hard in its full glory. But consider a simpler question: what is the shortest path from city $A$ to city $B$ in a weighted network? You may recall Dijkstra's algorithm from a computer science course. What you almost certainly were not told is that Dijkstra's algorithm is secretly doing *tropical matrix multiplication*.

Given two matrices $A$ and $B$ over $(\mathbb{Z} \cup \{\infty\},\; \min,\; +)$, their tropical product $C = A \odot B$ has entries:

$$C_{ij} = \bigoplus_k (A_{ik} \odot B_{kj}) = \min_k \big(A_{ik} + B_{kj}\big).$$

Read that formula slowly. For each pair of cities $i$ and $j$, we consider every possible intermediate city $k$, compute the cost of going $i \to k \to j$, and take the minimum. This is precisely the recurrence at the heart of the **Floyd–Warshall algorithm** for all-pairs shortest paths.

[ILLUSTRATION: A $4 \times 4$ weighted directed graph with cities labeled $A$, $B$, $C$, $D$. Edge weights are single-digit integers. Beside the graph, two $4 \times 4$ matrices: the adjacency matrix $D$ (with $\infty$ for missing edges) and the squared matrix $D^{(2)} = D \odot D$ (with shortest two-hop distances filled in). Changed entries are highlighted in orange. Caption: "One tropical matrix squaring reveals all two-hop shortcuts."]

Iterate the process — compute $D^{(n)} = D \odot D \odot \cdots \odot D$ ($n$ times) — and you obtain all shortest paths using at most $n$ hops. The entire Floyd–Warshall algorithm reduces to a single sentence: *raise the distance matrix to the $n$-th tropical power*. The semiring axioms guarantee that every intermediate computation is valid — associativity ensures we can parenthesize the product however we like, and distributivity ensures that combining paths from different intermediate nodes is consistent.

---

## Bellman's Equation: The Optimality Principle in Tropical Dress

Richard Bellman was once asked why he named his method "dynamic programming." He confessed that the word "programming" was chosen to camouflage the mathematics from a hostile Secretary of Defense who disliked research. The word "dynamic" was added because no congressman could object to something *dynamic*. Beneath this political theater lay one of the deepest ideas in optimization: the **principle of optimality**.

In tropical language, the principle becomes a single equation. Let $d(v)$ denote the shortest distance from a source vertex $0$ to any vertex $v$, and let $w(v)$ be the weight of the direct edge from $0$ to $v$. The Bellman equation states:

$$d(v) = d(v) \oplus \big(d(0) \odot w(v)\big) = \min\!\big(d(v),\; d(0) + w(v)\big).$$

In words: the best known distance to $v$ is the minimum of the current estimate and the cost of going directly from the source. Since $\min(d(v),\; d(0) + w(v))$ is either $d(v)$ or something smaller, the immediate consequence is:

$$d(v) \;\le\; d(0) + w(v).$$

[ILLUSTRATION: A five-vertex directed graph with source vertex $0$ at left. Arrows show edges with integer weights. Below the graph, a row of boxes showing $d(v)$ values after each relaxation round: Round 0 shows $d(0) = 0$ and all others $= \infty$; Round 1 shows updated neighbors of $0$; Round 2 shows further propagation. Arrows indicate which edges caused each update. Caption: "Bellman–Ford: each round is a tropical matrix-vector product."]

The **Bellman–Ford algorithm** is nothing more than iterated application of this equation — a sequence of "relaxation" steps, each one tropically adding new shortest-path information to the current estimate. The $\min$ operation is *non-expansive*: once a distance decreases, it stays decreased. Every relaxation step either improves the estimate or leaves it unchanged. Convergence is guaranteed in at most $n - 1$ rounds, where $n$ is the number of vertices.

Bellman's autobiography recounts the Cold War origins of operations research, when the Pentagon funded mathematical optimization under the guise of "programming" military logistics. The Bellman equation reappears today in reinforcement learning, Markov decision processes, and the training of game-playing AI — the same tropical skeleton, dressed in modern clothing.

---

## From Shortest Paths to Factoring Numbers

The reader who has followed us from the Berggren tree of Pythagorean triples (Chapter 1) through the hyperbolic plane (Chapter 3) and up to Cayley–Dickson algebras (Chapter 9) may be wondering: what does tropical geometry have to do with factoring integers?

The answer is: everything. The entire book has been about finding shortest paths in disguised graphs.

The **Berggren tree descent** of Chapters 1–3 is a shortest-path problem in the Cayley graph of the Lorentz group. Each step down the tree is a "tropical multiplication" — an additive step in a metric derived from the quadratic form $Q(a,b,c) = a^2 + b^2 - c^2$. The **lattice reduction** of Chapter 2 — the Euclidean algorithm computing a shortest vector in a 2D lattice, and its higher-dimensional cousin LLL — finds its natural framework in tropical convexity. The **GCD cascade** of Chapter 13 is repeated application of the Bellman equation: at each step, we "relax" the current factor estimate using a new Pythagorean relation. And the tropical distributive law guarantees that multi-channel factor extraction (Chapter 6) works: each independent channel provides a new "edge" in the tropical factor graph, and the minimum over all channels gives the best factor.

[ILLUSTRATION: A large "map of the book" diagram, drawn as a network graph. Each chapter is a node (labeled $1$ through $16$), and directed edges connect chapters whose concepts feed into later ones. The path from Chapters $1 \to 2 \to 3 \to 14 \to 15 \to 16$ is highlighted in tropical orange, labeled "The Tropical Highway." Chapter 15 sits at a crossroads where several paths converge. Caption: "The tropical semiring is the hidden algebra connecting every factoring algorithm in this book."]

The tropical semiring is not a curiosity — it is the hidden algebra that unifies the book's seemingly disparate threads. Every time we asked "what is the cheapest way to factor $N$?" or "what is the most efficient descent in the Berggren tree?", we were solving a shortest-path problem in a tropical semiring. We simply did not know it yet.

---

## Puzzles, Paradoxes, and Open Questions

We close, in the Gardner tradition, with a collection of puzzles for the reader — some easy, some devious, and one that remains unsolved.

**1. Tropical Determinants.** Define the "tropical determinant" of a $3 \times 3$ matrix as the minimum over all six terms of the Leibniz formula, with ordinary addition replacing multiplication and $\min$ replacing summation. Compute the tropical determinant of

$$\begin{pmatrix} 1 & 5 & 3 \\ 4 & 2 & 6 \\ 7 & 8 & 0 \end{pmatrix}.$$

(Hint: enumerate all six permutations of $\{1, 2, 3\}$, compute the sum of the selected entries for each, and take the minimum.)

**2. Tropical Roots.** The tropical polynomial $p(x) = \min(3,\; 1 + x,\; 4 + 2x)$ is a piecewise-linear function. Sketch its graph and find its "roots" — the points where the minimum switches from one linear piece to another.

[ILLUSTRATION: A piecewise-linear graph of the tropical polynomial $p(x) = \min(3,\; 1+x,\; 4+2x)$, drawn on a standard $xy$-plane. Three line segments of different slopes meet at two "kink" points (the tropical roots). Each linear piece is colored differently — blue, orange, green — and labeled with its monomial. The kink points are circled and labeled with their $x$-coordinates. Caption: "A tropical polynomial: three lines, two roots, zero curves."]

**3. No Subtraction.** Explain why there is no "tropical subtraction." Given $a \oplus b = c$, can you recover $a$ from $c$ and $b$? (If $c = \min(3, 7) = 3$, all you know is that $a$ was $3$ and $b$ was $7$ — or that $a$ was $3$ and $b$ was $3$ — or that $a$ was $3$ and $b$ was a million. The loser is forgotten forever.) What does this tell us about the irreversibility of optimization?

**4. Tropical Rank.** The rank of a tropical matrix is not the same as the rank of the corresponding classical matrix. Can you construct a $3 \times 3$ matrix that has classical rank $3$ but tropical rank $2$?

**5. An Open Question.** Is there a polynomial-time algorithm for computing the tropical convex hull of $n$ points in $\mathbb{R}^d$? For $d = 2$, the answer is yes. For general $d$, the problem remains open — a small but stubborn frontier where tropical geometry meets computational complexity.

**6. Shortest Path and Pythagorean Triples.** Model the Berggren tree as a weighted graph where each edge has weight equal to the change in hypotenuse. Show that descent in the tree is equivalent to finding the shortest path (in the tropical sense) back to the root $(3, 4, 5)$. Does the "trivial triple" from Chapter 14 always have the largest hypotenuse-to-$N$ ratio?

These puzzles are not idle amusements. Each one opens a door to an active area of research — tropical linear algebra, tropical algebraic geometry, combinatorial optimization, computational complexity. The broken calculator, it turns out, computes more than we ever asked it to.

---

*Next: Chapter 16 — where the tropical highway reaches its destination, and the shortest path leads us, at last, to a new algorithm.*
