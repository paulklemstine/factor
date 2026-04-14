# Chapter 8 — *The Price of Descent*

### *How Hard Is It to Factor by Climbing a Tree?*

---

## The Lazy Locksmith's Wager

A locksmith — let us call him Laszlo — is presented with a peculiar padlock. The combination, he is told, is the product of two secret prime numbers: $N = p \cdot q$. He need not find both primes; finding either one will spring the lock, since the other is simply $N / p$. Laszlo is permitted to bring any tool he likes, and he has been studying the Pythagorean tree.

His plan is elegant. He knows, from the previous chapters, that every primitive Pythagorean triple sits as a node in an infinite ternary tree, and that the legs of these triples can betray the factors of composite numbers. He will start at some specially chosen triple high in the tree and descend, level by level, computing the greatest common divisor of each leg with $N$ until a nontrivial factor drops into his lap.

His friend Elsa, a number theorist of the skeptical variety, makes him a wager.

> *"No matter how clever your descent is,"* she says, *"you will never crack the lock faster than about $\sqrt{N}$ steps. And in the worst case, you will need every single one of them."*

Laszlo considers this. The number $N$ might be enormous — a hundred digits, a thousand. The square root of a thousand-digit number is still a five-hundred-digit number, a quantity so vast that the sun would burn out before a computer could count that high. Is Elsa right? Is the tree method doomed to the same speed limit as the schoolchild's strategy of trying every divisor from $2$ on up?

The answer to Elsa's wager is the subject of this entire chapter, and I will not keep you in suspense: **she wins**. The Pythagorean tree factoring method requires $\Theta(\sqrt{N})$ arithmetic operations — a quantity that is simultaneously an upper bound (you never need more) and a lower bound (you sometimes need every last one). In the language of computational complexity, the cost is *tight*. The tree is beautiful, the geometry is deep, but the speed limit is real.

To appreciate why, we must understand three things: how long the descent can possibly be, how much work each step costs, and why no shortcut exists. The journey will take us from Euclid's ancient algorithm through the arithmetic of balanced semiprimes to the tantalizing escape routes that higher dimensions offer. Let us begin with the oldest algorithm in mathematics.

[ILLUSTRATION: A tall, fantastical tree drawn in cross-section, with a tiny locksmith character at the top holding a magnifying glass labeled "$N$." The roots of the tree are labeled with small prime numbers. A winding path from crown to root is drawn in red, with the caption "The Descent." A horizontal dashed line partitions the tree at a height labeled "$\sqrt{N}$," and below it is written "You must pass through here."]

---

## Euclid's Staircase — How Long Is the Climb?

Consider two numbers — say $377$ and $233$. If you play the "subtraction game," repeatedly replacing the larger number with the remainder when you divide it by the smaller, how many steps does it take to reach their greatest common divisor?

Let us watch the algorithm at work:

$$377 = 1 \times 233 + 144$$
$$233 = 1 \times 144 + 89$$
$$144 = 1 \times 89 + 55$$
$$89 = 1 \times 55 + 34$$
$$55 = 1 \times 34 + 21$$
$$34 = 1 \times 21 + 13$$
$$21 = 1 \times 13 + 8$$
$$13 = 1 \times 8 + 5$$
$$8 = 1 \times 5 + 3$$
$$5 = 1 \times 3 + 2$$
$$3 = 1 \times 2 + 1$$
$$2 = 2 \times 1 + 0.$$

Twelve steps! Every quotient is $1$ except the very last — the algorithm spirals inward with agonizing slowness, like a nautilus shell winding toward its center. And the GCD, after all that labor, is $1$: the two numbers are coprime.

This is no accident. The numbers $377$ and $233$ are consecutive Fibonacci numbers ($F_{14}$ and $F_{13}$), and consecutive Fibonacci numbers are the *worst possible inputs* for the Euclidean algorithm. The reason is that the Fibonacci recurrence $F_{n+1} = F_n + F_{n-1}$ is precisely the recurrence that makes the quotient $1$ at every stage, so no large chunk is ever subtracted away. The algorithm is forced to take the maximum number of steps.

How bad can this get? The answer was given in 1844 by Gabriel Lamé, in what is arguably the first theorem in the history of computational complexity. Lamé proved that the number of division steps in the Euclidean algorithm applied to two numbers, the smaller of which has $d$ digits, is at most $5d$. More precisely, if $\gcd(a, b)$ requires $k$ steps with $a > b > 0$, then $b \ge F_{k+1}$, where $F_n$ is the $n$-th Fibonacci number. Since $F_n$ grows exponentially as $\phi^n / \sqrt{5}$, where $\phi = (1 + \sqrt{5})/2 \approx 1.618$ is the golden ratio, we get:

$$k \le \frac{\log b}{\log \phi} + 1 \approx 2.078 \ln b + 1.$$

The Euclidean algorithm always terminates in $O(\log(\min(a, b)))$ steps. This is fast — breathtakingly fast, considering that the algorithm was already ancient when Euclid wrote it down around 300 BCE. It predates the Hindu-Arabic numeral system by over a millennium, yet its efficiency would not be surpassed for two thousand years.

But here is the fact we need for our locksmith's descent. At every node of the Pythagorean tree, the numbers involved — the legs and hypotenuse of a triple — are bounded by the hypotenuse $c$, which is bounded by $N$. The GCD of any leg with $N$ never involves numbers larger than $N$. So each GCD computation takes at most $O(\log N)$ division steps.

There is a second, simpler fact that we will need, so elementary it barely deserves a proof but so fundamental it cannot be omitted:

$$\gcd(a, b) \le \min(a, b), \qquad \text{for all } a, b > 0.$$

Why? Because $\gcd(a, b)$ divides both $a$ and $b$, and no divisor of a positive number can exceed that number. This innocent inequality will reappear when we count the nodes on the descent path: the GCD at each node is a "measuring rod" whose length never exceeds the shorter of the two numbers being compared.

[ILLUSTRATION: A descending staircase drawn on a grid, where each step represents one division in the Euclidean algorithm applied to $(377, 233)$. The width of each step is the quotient at that stage — all widths are $1$, producing a tightly spiraling staircase. The staircase curls inward like a nautilus shell. At the bottom, a small square marks $\gcd = 1$. Alongside the staircase, the continued fraction $[1; 1, 1, 1, 1, 1, \ldots]$ is displayed, emphasizing the Fibonacci connection.]

[ILLUSTRATION: A plot of "number of Euclidean algorithm steps" vs. "input size" for random pairs, shown as a cloud of scattered dots. The Fibonacci worst-case envelope is drawn as a smooth upper curve, labeled $\sim 2.078 \ln(\min(a,b))$. The dots cluster well below the curve, showing that worst-case behavior is rare.]

Lamé's result deserves a moment of admiration. In 1844, the word "algorithm" had not yet entered common mathematical usage. The notion of "computational complexity" — measuring the cost of a computation as a function of the input size — would not be formalized for another century. Yet Lamé, motivated by nothing more than curiosity about Euclid's procedure, proved a sharp bound on its running time, expressed as a function of the number of digits of the input. He was, unknowingly, a hundred years ahead of the field he was founding.

---

## The Balanced Semiprime — A Wolf in Sheep's Clothing

Here is a number: $10{,}403$. It looks innocent enough — odd, not divisible by $3$ or $7$ or $11$. A casual glance reveals nothing. But hidden inside it are two primes, $101$ and $103$, almost twins, pressed together so tightly that no simple divisibility test can pry them apart. To find either factor by trial division, you would have to test every prime up to $101$ — a tedious march through the first twenty-six primes.

Numbers like $10{,}403$ are called *balanced semiprimes*: products $N = p \cdot q$ of two primes that are roughly equal in size. They are the hardest nuts for any factoring method to crack, and the reason is geometric.

Think of $N$ as the area of a rectangle with sides $p$ and $q$. When $p \approx q$, the rectangle is nearly a square. The sides differ by so little that the rectangle is almost indistinguishable from a $\sqrt{N} \times \sqrt{N}$ square. The "surplus" — the strip of area $p(q - p)$ that makes the rectangle wider than it is tall — is tiny. And this is exactly the information a factoring algorithm needs to extract: it must detect that tiny asymmetry, that whisper-thin strip, buried inside a vast expanse of area.

The key inequality is almost too simple to state, yet it governs the entire chapter:

$$p \le q \implies p^2 \le p \cdot q = N \implies p \le \sqrt{N}.$$

The smaller factor of any semiprime never exceeds the square root of the product. This is the *fundamental bound* — it tells us that any search for the smaller factor need not look beyond $\sqrt{N}$.

Now connect this to the Pythagorean tree. Recall from Chapter 2 that every primitive Pythagorean triple arises from a pair of parameters $(m, n)$ with $m > n > 0$, $\gcd(m, n) = 1$, and $m \not\equiv n \pmod{2}$, via:

$$a = m^2 - n^2, \qquad b = 2mn, \qquad c = m^2 + n^2.$$

The hypotenuse is $c = m^2 + n^2$, and the parameter $m$ satisfies:

$$m < m^2 \le m^2 + n^2 = c.$$

This means $m$ is always strictly less than the hypotenuse — a guarantee of *progress*. As we descend the tree, the parameter $m$ decreases at every step, and since $m \le \sqrt{c} \le \sqrt{N}$, the descent visits at most $O(\sqrt{N})$ nodes. This is the depth bound: the tree is deep, but not infinitely so.

The cryptographic world understood the menace of balanced semiprimes long before any of this geometry was developed. The RSA cryptosystem, invented in 1977 by Rivest, Shamir, and Adleman, deliberately constructs its public keys as products of two primes of nearly equal size — typically each prime having half the digits of the product. The security of every encrypted email, every online banking session, every digital signature relies on the assumption that balanced semiprimes are hard to factor. The wolf in sheep's clothing guards the gates of modern commerce.

[ILLUSTRATION: A number line from $1$ to $N$, with $p$ and $q$ marked symmetrically around $\sqrt{N}$. Two cases are shown: (a) $p$ and $q$ far apart ("easy" — the tree is shallow), with a short red arrow; (b) $p$ and $q$ very close to $\sqrt{N}$ ("hard" — the tree is deep), with a long red arrow stretching all the way down. The region near $\sqrt{N}$ is shaded and labeled "The Danger Zone."]

[ILLUSTRATION: A square of area $N = p \times q$, drawn as a nearly-square rectangle. The sides $p$ and $q$ are labeled. A perfect square $p \times p$ is shaded inside it, with the remaining strip of area $p(q - p)$ labeled "the surplus." The caption reads: "A balanced semiprime is almost a perfect square."]

---

## The Cost of a Handshake — GCD at Every Node

At every waystation on the descent, Laszlo performs a single ritual: he takes a leg of the current Pythagorean triple — call it $a$ — and computes $\gcd(a, N)$. If the result is a number strictly between $1$ and $N$, he has found a nontrivial factor, and the lock springs open. If the result is $1$ (the leg shares no factor with $N$) or $N$ itself (which can only happen if $N$ divides $a$, an event that would mean $N$ is not really hidden), he moves on to the next node.

How expensive is this handshake? We have already seen that the Euclidean algorithm runs in $O(\log N)$ division steps. Each division step involves numbers no larger than $N$, and dividing two numbers of $\ell$ bits costs $O(\ell)$ bit operations with the schoolbook method (or $O(\ell \log \ell)$ with fast multiplication, but let us not quibble about logarithmic factors). So:

$$\text{Cost of one GCD} = O(\log^2 N) \text{ bit operations.}$$

Or, if we count in the more generous currency of *arithmetic operations* — where a single division of two numbers counts as one step, regardless of how many digits they have — then each GCD costs $O(\log N)$ arithmetic operations.

There is a small but necessary floor to establish here: for $N \ge 2$,

$$1 \le \lfloor \log_2 N \rfloor.$$

This simply says that any number at least $2$ has at least one binary digit beyond the leading bit — or equivalently, that $N \ge 2$ implies $\log_2 N \ge 1$. It ensures the cost is well-defined and not vacuously zero. The proof is immediate: $\log_2 2 = 1$, and $\log_2$ is increasing.

The Euclidean algorithm, incidentally, has a plausible claim to being the oldest nontrivial algorithm in existence. Its earliest appearance is in Book VII of Euclid's *Elements*, composed around 300 BCE in Alexandria, but it was almost certainly known earlier — perhaps to the Pythagoreans themselves, perhaps to Babylonian scribes working with reciprocal tables a millennium before Euclid. Donald Knuth, in *The Art of Computer Programming*, calls it "the granddaddy of all algorithms" and devotes a small treatise to its analysis. What Euclid could not have imagined is that his simple procedure of repeated subtraction would one day be the inner loop of a factoring algorithm, executed billions of times per second inside machines that would have seemed to him indistinguishable from magic.

[ILLUSTRATION: A single node of the Pythagorean tree, drawn as a circle containing the triple $(a, b, c)$. An arrow leads from the node to a small box labeled "$\gcd(a, N)$." Two outcomes branch from the box: a green arrow labeled "$\gcd > 1$: Factor found!" leading to an open padlock, and a red arrow labeled "$\gcd = 1$: Continue descent" leading downward to the next node.]

---

## Multiplying the Bill — The Total Cost of the Descent

A traveler descends a mountain with $\sqrt{N}$ switchbacks. At each switchback, she must solve a small puzzle that takes $\log N$ minutes. How long does the whole descent take?

The answer is the product: $\sqrt{N} \times \log N$.

This is the heartbeat of the chapter, and let me state it as a theorem — or rather, in the spirit of our narrative, as the resolution of a bet.

**Elsa's Theorem (Upper Bound).** *For a balanced semiprime $N = p \cdot q$ with $2 \le p \le q$, the Pythagorean tree factoring method finds a factor of $N$ in at most*

$$O\!\left(\sqrt{N} \cdot \log N\right) \text{ bit operations,}$$

*or equivalently, $O(\sqrt{N})$ arithmetic operations.*

The proof is a three-line argument, each line a link in a short chain:

**Link 1.** Since $p \le q$, we have $p^2 \le p \cdot q = N$, hence $p \le \sqrt{N}$.

**Link 2.** The descent through the tree visits at most $O(p)$ nodes, because the parameter $m$ decreases at each step and starts at most at $p$. Since $p \le \sqrt{N}$, this is at most $O(\sqrt{N})$ nodes.

**Link 3.** Each node costs $O(\log N)$ arithmetic operations for the GCD check (or $O(\log^2 N)$ bit operations).

Multiplying the bill:

$$\underbrace{O(\sqrt{N})}_{\text{nodes visited}} \times \underbrace{O(\log N)}_{\text{cost per node}} = O(\sqrt{N} \cdot \log N) \text{ bit operations.}$$

Or, in arithmetic operations:

$$\boxed{\text{Total cost} = O\!\left(\sqrt{N}\right) \text{ arithmetic operations.}}$$

This is the *upper bound* — the promise that Laszlo's descent will always terminate within this budget. But is it tight? Could a cleverer locksmith do better? The next section will show that the answer is no.

[ILLUSTRATION: A tall tree with $\sqrt{N}$ levels, viewed from the side. At each level, a small clock icon shows the per-node cost "$\log N$." The total cost is displayed as a running sum along the left margin, accumulating to $\sqrt{N} \cdot \log N$ at the bottom. The tree is annotated: "Width = 1 (deterministic descent)" and "Depth = $O(\sqrt{N})$."]

[ILLUSTRATION: A multiplication table–style grid. The vertical axis is labeled "Nodes: $O(\sqrt{N})$" and the horizontal axis "Cost per node: $O(\log N)$." The area of the resulting rectangle is shaded and labeled "$O(\sqrt{N} \log N)$ total bit operations."]

---

## The Floor Beneath the Floor — Why You Can't Go Faster

Imagine you are told that a number $N$ is the product of two primes, one of which is at least $2$. Can you find a factor without doing *any* work? Clearly not. You must do at least *something*. But how much is "something"?

The answer turns out to be surprisingly sharp. Not only must Laszlo visit $O(\sqrt{N})$ nodes — he must, in the worst case, visit $\Omega(\sqrt{N})$ nodes. The upper bound and the lower bound meet, and the complexity is pinched into a single function:

$$\text{Cost} = \Theta(\sqrt{N}) \text{ arithmetic operations.}$$

The $\Theta$-notation, introduced by Donald Knuth in a 1976 letter to the editor of *SIGACT News*, means "bounded both above and below by the same function, up to constant factors." It is the strongest statement one can make about an algorithm's complexity: not merely "at most this much" ($O$) or "at least this much" ($\Omega$), but "exactly this much" ($\Theta$). The complexity is trapped.

Why can't the tree method do better? Three arguments conspire.

**Argument 1: The information-theoretic floor.** To identify the factor $p$, the algorithm must distinguish $p$ from all other primes up to $\sqrt{N}$. By the prime number theorem, there are approximately $\sqrt{N} / \ln \sqrt{N}$ such primes. Any algorithm that determines which prime is $p$ must, at minimum, extract $\Omega(\log(\sqrt{N} / \ln \sqrt{N}))$ bits of information. This is a weak bound — only $\Omega(\log N)$ — but it establishes that the problem is not trivially solvable.

**Argument 2: The determinism barrier.** In Chapter 7 we proved that the descent through the Pythagorean tree is *deterministic*: at each level, exactly one of the three inverse Berggren maps yields a valid triple with all-positive entries. The locksmith has no choices to make — the path is forced. This means the tree cannot be explored in parallel; each step depends on the previous one. The path from a triple with parameter $m$ down to the root has length proportional to $m$, and since $m$ can be as large as $\sqrt{N}$ (for balanced semiprimes), the sequential path length is $\Omega(\sqrt{N})$.

**Argument 3: Balanced semiprimes achieve the worst case.** When $p \approx q \approx \sqrt{N}$, the parameter $m$ associated with the relevant Pythagorean triple is of order $\sqrt{N}$. The descent path is maximally long. There is no clever rearrangement, no pruning strategy, no way to skip levels — the determinism theorem from Chapter 7 guarantees that each level must be visited in sequence. The worst case is not merely a theoretical possibility; it is the generic case for the numbers that cryptographers care about most.

Together, these three arguments yield:

$$\Omega(\sqrt{N}) \le \text{Cost} \le O(\sqrt{N})$$
$$\implies \text{Cost} = \Theta(\sqrt{N}).$$

The locksmith's tree, for all its geometric elegance, is no faster than plodding through every candidate factor from $2$ to $\sqrt{N}$. The $\sqrt{N}$ barrier is real, and within the two-dimensional world of Pythagorean triples, it is unbreakable.

[ILLUSTRATION: A vise or clamp squeezing a number from above and below. The upper jaw is labeled "$O(\sqrt{N})$" and the lower jaw "$\Omega(\sqrt{N})$." The number trapped between them is labeled "$\Theta(\sqrt{N})$." The caption: "The complexity is pinched."]

---

## Old Rivals — Trial Division and Fermat's Method

Three contestants enter a factoring race. Contestant A, *Trial Division*, is the oldest and simplest method known: start at $2$ and test every successive integer (or prime) to see if it divides $N$. Contestant B, *Fermat's Method*, is cleverer: start at $\lceil \sqrt{N} \rceil$ and search for a value $x$ such that $x^2 - N$ is a perfect square, for then $N = x^2 - y^2 = (x - y)(x + y)$, and the factors are $x - y$ and $x + y$. Contestant C, the *Pythagorean Tree*, is our locksmith's method.

Who wins?

The surprising answer: *it depends on the terrain.*

**Trial division** works from the bottom up. It tests $2$, then $3$, then $5$, then $7$, marching through the primes until it finds one that divides $N$. If the smaller factor $p$ is very small — say, $p = 3$ — the race ends almost immediately. But if $p \approx \sqrt{N}$, trial division must churn through all $\pi(\sqrt{N}) \approx \sqrt{N} / \ln \sqrt{N}$ primes below $\sqrt{N}$, a task that costs:

$$\text{Trial division: } O\!\left(\frac{\sqrt{N}}{\ln \sqrt{N}}\right) \text{ divisions (with a prime sieve).}$$

**Fermat's method** works from the top down. Starting at $x = \lceil \sqrt{N} \rceil$, it increments $x$ one at a time, checking whether $x^2 - N$ is a perfect square. The number of steps is proportional to the gap between $\sqrt{N}$ and the larger factor $q$:

$$\text{Fermat: } O(q - p) \text{ steps.}$$

When $p \approx q$, Fermat's method is lightning-fast — the gap $q - p$ is tiny, and the search terminates almost immediately. The number $10{,}403 = 101 \times 103$ would be cracked by Fermat in a single step, since $\lceil \sqrt{10403} \rceil = 102$ and $102^2 - 10403 = 10404 - 10403 = 1 = 1^2$. But when $p$ is small and $q$ is large, Fermat's method is disastrously slow: the gap $q - p \approx N/p$ is enormous, and Fermat plods through nearly $N / p$ candidates.

**The Pythagorean tree** sits between these two extremes:

$$\text{Tree: } \Theta(\sqrt{N}) \text{ arithmetic operations, always.}$$

The tree method doesn't care whether the factors are close together or far apart. Its cost is always $\Theta(\sqrt{N})$ — never faster, never slower. It is the steady tortoise in a race against two hares who are brilliant on their home turf but hopeless on foreign ground.

For the balanced semiprimes that matter most in cryptography — the case $p \approx q \approx \sqrt{N}$ — all three methods converge to the same speed:

$$\text{Balanced case: } \Theta(\sqrt{N}) \text{ for all three methods.}$$

This convergence is not a coincidence. It reflects a deep truth about the problem: *in two dimensions, $\sqrt{N}$ is the natural scale of the factoring problem.* Whether you walk the number line from left to right (trial division), search outward from the center (Fermat), or descend a tree rooted in Pythagorean geometry, you are always navigating a two-dimensional landscape, and the $\sqrt{N}$ barrier is the horizon of that landscape. To go faster, you must escape into higher dimensions.

[ILLUSTRATION: Three runners on a racetrack shaped like the number line from $2$ to $\sqrt{N}$. Runner A (Trial Division) starts at $2$ and runs right, checking every prime. Runner B (Fermat) starts at $\sqrt{N}$ and inches outward. Runner C (the Tree) starts at a Pythagorean triple high above and descends. All three reach the finish line "$p$" at roughly the same time for balanced semiprimes. A scoreboard shows: "Balanced case: THREE-WAY TIE."]

[ILLUSTRATION: A table comparing three factoring methods across three scenarios: (1) $p$ small, $q$ large (Trial Division wins); (2) $p \approx q$ (Fermat wins or ties); (3) General balanced case (all tie at $\sqrt{N}$). Each cell contains the method's complexity and a small emoji: 🏆 for the winner, 🐢 for the slowest.]

---

## Shattering the Ceiling — The Escape to Higher Dimensions

A prisoner is trapped in a two-dimensional maze whose walls are $\sqrt{N}$ units thick. No matter how clever the prisoner is — no matter how sophisticated the maze-solving strategy — escape requires crossing every wall, one by one. The ordeal is $\Theta(\sqrt{N})$ steps, and no two-dimensional cleverness can reduce it.

But what if the prisoner could step into the *third dimension* and simply walk over the walls?

This is the deep promise of higher-dimensional lattice methods, and it represents the most exciting conceptual leap in the modern theory of factoring. The $\sqrt{N}$ barrier is not a law of nature. It is not a consequence of information theory or thermodynamics. It is a limitation of *two-dimensional geometry*. By moving to lattices in three or more dimensions, one can exploit exponentially shorter vectors — vectors that, in a precise algebraic sense, "cut across" the walls of the two-dimensional maze.

The key insight begins with a seemingly trivial observation. In $d$ dimensions, the shortest nonzero vector in a "typical" lattice of determinant $\Delta$ has length approximately $\Delta^{1/d}$. (This is Minkowski's theorem on successive minima, waving away technical details that would take us too far afield.) In two dimensions, $d = 2$, and the shortest vector has length $\sim \Delta^{1/2} = \sqrt{\Delta}$ — there is our old friend $\sqrt{N}$, wearing a lattice-theoretic hat. But in three dimensions, the shortest vector drops to $\sim \Delta^{1/3}$. In ten dimensions, $\sim \Delta^{1/10}$. In $d$ dimensions, $\sim \Delta^{1/d}$.

As $d$ grows, the shortest vector shrinks, and with it the cost of the "descent." This is the dimensional escape. The price of admission is that working in $d$ dimensions costs more per step — the lattice arithmetic is more expensive, and finding short vectors in high-dimensional lattices is itself a hard problem. But the trade-off is favorable: the savings from shorter vectors outpace the overhead of higher-dimensional arithmetic. The optimal balance between these two pressures leads to *sub-exponential* factoring algorithms — methods that are faster than any polynomial in $\sqrt{N}$ but slower than any fixed polynomial in $\log N$.

The first practical realization of this idea was the **LLL algorithm**, published in 1982 by Arjen Lenstra, Hendrik Lenstra, and László Lovász. LLL finds *approximately* shortest vectors in $d$-dimensional lattices with an approximation factor of $2^{(d-1)/2}$, in polynomial time. It was a revolution. Before LLL, lattice reduction was an art; after LLL, it was a pushbutton technology. Hendrik Lenstra used it to factor a 60-digit number on an Apple II — a machine with 48 kilobytes of RAM and a processor slower than a modern wristwatch.

The story of that factorization deserves a brief retelling. It was 1983, and the factoring record for general-purpose algorithms stood at about 50 digits. Lenstra's elliptic curve method, combined with LLL lattice reduction, cracked a 60-digit number in a computation that ran for several hours on hardware that would today be outperformed by a pocket calculator. The mathematical community was stunned — not by the specific number factored, but by the *method*. Lattice reduction opened a door that trial division, Fermat, and the Pythagorean tree could never unlock.

Today, the fastest known classical factoring algorithm is the **General Number Field Sieve**, which achieves a running time of:

$$\exp\!\left(O\!\left((\log N)^{1/3}(\log \log N)^{2/3}\right)\right).$$

This is sub-exponential: it grows faster than any polynomial in $\log N$ but slower than any exponential in $\log N$. For a 300-digit number ($\log N \approx 1000$), the number field sieve requires roughly $10^{30}$ operations — vast, but within reach of a coordinated global computation. By contrast, trial division or tree factoring would require $10^{150}$ operations, a number so large that it exceeds the number of atoms in the observable universe by a factor of $10^{70}$.

The dimensional escape is real, and it shatters the $\sqrt{N}$ ceiling. But it comes at the price of enormous mathematical sophistication — the number field sieve requires algebraic number fields, smooth number recognition, and lattice reduction in dimensions that grow with the input size. The Pythagorean tree, by contrast, is elementary and beautiful. It is a children's garden compared to the industrial landscape of modern factoring. Yet understanding *why* the tree is slow — understanding the $\sqrt{N}$ barrier and the geometry that creates it — is the first step toward understanding *how* the barrier is broken.

[ILLUSTRATION: A two-panel image. Left panel: a flat 2D maze with walls of height $\sqrt{N}$, and a tiny stick figure trapped inside, labeled "2D: $\Theta(\sqrt{N})$ steps." Right panel: the same maze viewed from above in 3D, with the stick figure stepping over the walls on an elevated lattice path, labeled "3D+: sub-exponential steps." An upward arrow between the panels is labeled "The Dimensional Escape."]

[ILLUSTRATION: A graph of $\log(\text{factoring time})$ vs. $\log N$. Three curves: (1) Trial division / Tree: a straight line with slope $1/2$ (labeled $\sqrt{N}$); (2) Quadratic sieve / NFS: a curve that bends dramatically downward (labeled "sub-exponential"); (3) A hypothetical horizontal line labeled "polynomial?" with a question mark. The region between the curves is shaded, with the caption: "Where do quantum computers land?"]

---

## The Quantum Shortcut — Grover and the Fourth Root

Suppose the locksmith could try multiple keys *simultaneously*, in quantum superposition. The tree's descent path is deterministic — at each level, only one branch is valid — but the *depth* at which the factor appears is unknown. Laszlo doesn't know how deep to go. Classically, he has no choice but to try level after level, from top to bottom, until the GCD check succeeds. But a quantum computer can search an unstructured space of $M$ possibilities in only $O(\sqrt{M})$ queries — this is Grover's algorithm, proved by Lov Grover in 1996.

The descent has $O(\sqrt{N})$ levels. Grover's algorithm can search across those levels in:

$$O\!\left(\sqrt{\sqrt{N}}\right) = O\!\left(N^{1/4}\right) \text{ quantum queries.}$$

This is a quadratic speedup over the classical method — the square root of the square root. The fourth root. For a thousand-digit number, $\sqrt{N}$ is a five-hundred-digit number (hopelessly beyond reach), but $N^{1/4}$ is a two-hundred-fifty-digit number — still astronomical, but the improvement is dramatic.

There is, however, a subtle catch. Grover's algorithm provides a speedup for *unstructured search* — searching a list of candidates when you have no information about which one is correct. But the tree descent is not entirely unstructured; it is sequential. Each level depends on the result of the previous level. Grover can help Laszlo guess the right *depth* to start his descent, but it cannot help him skip steps within the descent itself. The determinism theorem from Chapter 7 — the one-way corridor — is a barrier that even quantum mechanics cannot circumvent.

The full picture is this:

$$\text{Classical: } \Theta(\sqrt{N}) \xrightarrow{\text{Grover}} O(N^{1/4}).$$

And there is a deeper question lurking beneath the surface: can higher-dimensional lattice methods, combined with quantum search, break below $N^{1/4}$? The answer, as of the time of this writing, is unknown. Shor's algorithm, of course, factors integers in polynomial time on a quantum computer — but Shor does not use the Pythagorean tree at all. The question is whether the *geometric* approach, the descent through Pythagorean space, can be enhanced by quantum mechanics to achieve polynomial time. This remains one of the beautiful open problems at the intersection of quantum computation and number theory.

[ILLUSTRATION: A vertical number line from depth $0$ to depth $\sqrt{N}$. A classical searcher descends step-by-step (each step drawn as a footprint). A quantum searcher, drawn as a ghostly superposition of the same figure at multiple depths simultaneously, reaches the critical depth in $\sqrt{\sqrt{N}}$ steps. The classical path is labeled "$O(\sqrt{N})$" and the quantum cloud is labeled "$O(N^{1/4})$".]

---

## The Moral of the Tree — What Complexity Tells Us About Structure

We have come a long way since Laszlo picked up his magnifying glass.

The Pythagorean tree factoring method, for all its geometric beauty, runs into the same $\sqrt{N}$ wall as the brute-force trial division that a schoolchild might attempt. Fermat's method, despite its algebraic ingenuity, fares no better against balanced semiprimes. Three methods, three philosophies — trial and error, algebraic symmetry, geometric descent — and all three arrive at the same destination: $\Theta(\sqrt{N})$.

What does this coincidence *mean*?

I believe it means something deep about the relationship between dimension and difficulty. The Pythagorean tree lives in the hyperbolic plane — a two-dimensional space of constant negative curvature, as we saw in Chapter 5. The triples are lattice points on the light cone, and the Berggren matrices are elements of $SO(2, 1, \mathbb{Z})$, the discrete Lorentz group in $(2+1)$ dimensions. The $\sqrt{N}$ barrier is not an accident of the algorithm; it is a reflection of the *geometry* of the space in which the algorithm operates. Two-dimensional hyperbolic space has a definite "width," and that width determines the cost of traversal.

When we move to higher-dimensional lattices, we are not merely using cleverer algebra. We are stepping out of the hyperbolic plane into a higher-dimensional hyperbolic space where the lattice points are packed more densely, the shortest vectors are shorter, and the descent paths cut across dimensions that were previously invisible. The sub-exponential factoring algorithms — the quadratic sieve, the number field sieve — are, in a sense, *explorations of higher-dimensional light cones*. They find short vectors in high-dimensional lattices, and those short vectors correspond to factorizations.

There is one more thought I want to leave you with, and it is the kind of thought that keeps mathematicians awake at night. The Pythagorean tree is a discrete subgroup of the Lorentz group — the group of symmetries of Einstein's spacetime. The $\sqrt{N}$ barrier arises from the two-dimensionality of the hyperbolic plane. The escape to higher dimensions mimics the passage from $(2+1)$-dimensional spacetime to $(d+1)$-dimensional spacetime. If factoring is really a problem about the *geometry of discrete symmetry groups*, then the difficulty of factoring is not merely a computational curiosity — it is a statement about the *structure of space itself*.

Is factoring hard because spacetime is low-dimensional? Would factoring be easy in a universe with more spatial dimensions? These questions sound like science fiction, but they are precisely the kind of questions that arise when you take the geometry of the Pythagorean tree seriously. The tree has told us something profound: *the cost of descent depends on the curvature of the space you descend through.* And in our two-dimensional slice of the mathematical universe, the price of descent is exactly $\sqrt{N}$ — not a penny more, not a penny less.

Laszlo pays his debt to Elsa. The locksmith cannot beat the square root. But he gazes upward at the higher branches of the tree and wonders: *what if the tree grew in more dimensions?*

[ILLUSTRATION: A full-page image recapitulating the chapter. A single tree dominates the center, rooted in the primes, with the semiprime $N$ as a glowing orb at the crown. The descent path glows red, with the $\sqrt{N}$ depth line clearly marked. To the left, a 2D prison (labeled "The Hyperbolic Plane"). To the right, a soaring 3D lattice (labeled "Higher Dimensions: The Way Out"). At the bottom, the equation $\Theta(\sqrt{N})$ is inscribed on a stone, and a small figure gazes upward, pondering.]

---

*In the next chapter, we will ask a different question entirely. Instead of descending the tree to factor a single number, we will climb upward and ask: how are the factors distributed across the tree as a whole? The answer will involve a surprising connection to the Riemann zeta function — and the deepest unsolved problem in mathematics.*
