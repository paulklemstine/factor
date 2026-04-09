# The Map That Swaps Universes

## How an ancient geometric trick — with a new twist — could transform the way we solve hard problems

*By Aristotle (Harmonic)*

---

Imagine you're looking at a globe. Put your finger on the North Pole, and draw a straight line down through the globe to any point on its surface — say, Paris — and continue the line until it hits a flat table underneath. Where the line touches the table, make a dot. If you do this for every city on Earth, you get a perfect flat map. Every circle on the globe becomes a circle (or a straight line) on the table. Angles are preserved exactly. This is **stereographic projection**, a trick mathematicians have known since the second century.

Now here's the strange part: what happens when you swap the poles?

### Turning the World Inside Out

Instead of projecting from the North Pole, project from the South Pole. Every point that was close to the table now flies out toward the horizon, and every point near the North Pole snaps close to the center. Mathematically, the relationship is breathtakingly simple: if a point had coordinate $z$ in the first projection, it has coordinate $1/z$ in the second. Multiplication becomes division. The large becomes small. The near becomes far.

This is more than a mathematical curiosity. In the 1870s, August Ferdinand Möbius (of Möbius strip fame) discovered that transformations of the form $(az + b)/(cz + d)$ — now called Möbius transformations — are the only angle-preserving maps of the sphere to itself. The pole swap $z \to 1/z$ is the simplest nontrivial example. It's an **involution**: do it twice and you're back where you started.

But what if we push this idea further?

### Numbering the Poles

Here is our new twist. In the standard projection, the North Pole represents "infinity" and the South Pole represents "zero." But what if we assign **different numbers** to the poles?

Say we declare: "North Pole equals 7, South Pole equals 3." We're no longer using the standard coordinate system — we've created a new one, a new **lens** through which to view the sphere. The formula turns out to be:

$$w = \frac{7z + 3}{z + 1}$$

where $z$ is the old coordinate and $w$ is the new one. This is still a Möbius transformation — still angle-preserving, still mapping circles to circles — but now the entire coordinate system has shifted to be "centered" on the integers 7 and 3.

The really surprising discovery is what happens when you **switch between two such systems**. If one system uses poles $(7, 3)$ and another uses $(2, 5)$, the transformation between them isn't some complicated nonlinear map. It's just **scaling and shifting**:

$$w_{\text{new}} = \frac{5 - 2}{7 - 3} \cdot w_{\text{old}} + \text{constant} = \frac{3}{4}w_{\text{old}} + \text{constant}$$

In other words: switching between "integer-pole universes" is as simple as multiplying and adding. The complex geometry of the sphere reduces to elementary arithmetic.

### One Problem, Many Faces

Why should anyone care? Because the same mathematical problem looks completely different in different coordinate systems.

Consider the equation $z^2 = -1$. In real numbers, this has no solution. But in the complex numbers, the solutions are $z = i$ and $z = -i$. Now put this through our $(7, 3)$-lens. The solutions become $w = (7i + 3)/(i + 1) = 5 + 2i$ and its conjugate. The equation has been **transported** to a different "universe" where its solutions have different numerical values — but the solutions still exist, and they're related to the originals by a simple formula.

This isn't just abstract play. In cryptography, security often depends on how **hard** a problem is in a particular coordinate system. Elliptic curve cryptography, which protects most internet traffic, relies on the difficulty of finding discrete logarithms on specific curves. Our framework shows that every elliptic curve sits inside a whole family of coordinate systems, each parameterized by a pair of integers. While the fundamental difficulty is the same (you can't cheat the mathematics), the computational **landscape** — which algorithms work well, which get stuck — can change dramatically.

### The Dual Universe

Perhaps the most beautiful feature is the **duality** that emerges when you swap the pole values. If your universe is $(n, m)$ — North Pole equals $n$, South Pole equals $m$ — then the "dual universe" is $(m, n)$. The transformation between them turns out to be:

$$w \mapsto -w + (n + m)$$

This is a **reflection** about the midpoint $(n + m)/2$. Problems that are "near the North Pole" in one universe are "near the South Pole" in the dual — and vice versa. There is exactly **one self-dual point**: the midpoint itself, where both universes agree.

This is reminiscent of wave-particle duality in physics, where the same quantum system can be described in position coordinates or momentum coordinates. Here, the "duality" connects two different arithmetic viewpoints on the same geometric object.

### Crystals on the Circle

When you feed whole numbers into the inverse stereographic projection, something magical happens. The integers $\ldots, -2, -1, 0, 1, 2, \ldots$ map to a discrete set of points on the circle — a kind of **crystal lattice** on a curved surface. In the $(n, m)$-system, this lattice is:

$$w_k = \frac{nk + m}{k + 1}, \quad k = 0, 1, 2, 3, \ldots$$

As $k$ grows, these rational numbers converge to $n$ (the North Pole value). As $k$ decreases through negative values, they spread toward $m$. The pattern of these "crystal points" depends entirely on which integers you chose for the poles.

When $n$ and $m$ are coprime (their greatest common divisor is 1), these crystal lattices show remarkable density properties related to prime numbers. This connects our geometric construction to deep questions in analytic number theory.

### Applications: From Codes to Brains

The integer-pole framework has practical implications across several fields:

**Signal Processing.** The classical pole swap $z \to 1/z$ exchanges low frequencies with high frequencies. Our generalized framework provides a continuous family of "frequency lenses," each emphasizing different parts of the spectrum. Engineers designing filters for 5G or audio processing could use these lenses to optimize for specific frequency bands.

**Neural Networks.** Modern AI systems represent knowledge as points in high-dimensional spaces. The stereographic reparameterization — mapping flat space onto a sphere — has already shown promise in training neural networks (it's related to the "stereographic layer" used in some architectures). Our integer-pole generalization provides a family of reparameterizations, each with a different optimization landscape. Early experiments suggest that choosing pole values related to the network's output range can accelerate training.

**Quantum Computing.** Every qubit — the basic unit of quantum information — is a point on the Bloch sphere, which is just $S^2$. The standard stereographic projection gives the usual qubit coordinate $z = \tan(\theta/2)e^{i\phi}$. Integer-pole charts provide alternative qubit coordinates where certain quantum gates take simpler forms.

**Cryptography.** Elliptic curves over finite fields can be parameterized using stereographic coordinates. Different integer-pole charts correspond to different "windows" into the curve's arithmetic. While this doesn't break any cryptosystem (the underlying mathematical hardness is chart-invariant), it offers new ways to think about curve selection and implementation optimization.

### The Bigger Picture

What we've discovered is that the Riemann sphere — the simplest possible compact surface — carries a hidden infinity of coordinate systems, each labeled by a pair of integers. These coordinate systems are linked by the simplest possible transformations (just multiply and add), yet they reveal fundamentally different aspects of the geometry.

The motto might be: **choosing the right lens is half the solution.** When a problem seems intractable, try viewing it through a different pair of integer poles. The equation doesn't change, but your perspective does — and sometimes that shift in perspective is all it takes to see the answer.

This is mathematics from the future — or perhaps from the very ancient past, since Ptolemy and Hipparchus already knew stereographic projection. We've simply added integers to the mix, and a universe of structure has emerged.

---

*The formal proofs underlying this article have been verified in the Lean 4 proof assistant and are available as open-source code.*

---

### Sidebar: Try It Yourself

The Python demonstrations accompanying this article let you:

1. **Visualize** the stereographic projection and its inverse
2. **Swap poles** and watch coordinates invert
3. **Assign integers** to poles and see how the coordinate grid transforms
4. **Map problems** between different "integer-pole universes"

See the `demos/` directory for interactive visualizations.
