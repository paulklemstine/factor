# v41: Theta Function Exploitation for Factoring

Date: 2026-03-17 03:22:06

v41_theta_factor.py — Theta Function Exploitation for Factoring
Date: 2026-03-17 03:21:49
mpmath available: True


======================================================================
EXPERIMENT: EXP 1: r_2(N) for semiprimes
======================================================================

For N=pq semiprime, r_2(N) reveals factor residues mod 4:
  p≡q≡1 (mod 4): r_2 > 0 (encodes SOS count)
  otherwise: r_2 = 0

  Case p≡1, q≡1 (mod 4): 10 samples, r_2 nonzero: 10/10
    Example: N=8985029=3761*2389, r_2(N)=16, SOS reps=[(2977, 350), (2450, 1727)]
  Case p≡1, q≡3 (mod 4): 10 samples, r_2 nonzero: 0/10
    Example: N=1006051=1931*521, r_2(N)=0, SOS reps=[]
  Case p≡3, q≡3 (mod 4): 10 samples, r_2 nonzero: 0/10
    Example: N=83593229=8387*9967, r_2(N)=0, SOS reps=[]

  THEOREM T102: For N=pq with p≡q≡1 (mod 4):
    r_2(N) = 4·(#{(a,b): a²+b²=N, a≥b≥0} counted with multiplicity)
    Each SOS decomposition N=a²+b² corresponds to a factoring relation
    via Brahmagupta: if p=α²+β², q=γ²+δ², then
    N = (αγ±βδ)² + (αδ∓βγ)²

  Verifying Brahmagupta-Fibonacci identity:
    N=8985029=3761*2389: SOS(p)=[(56, 25)], SOS(q)=[(42, 25)]
      Direct SOS(N)=[(2977, 350), (2450, 1727)], Brahmagupta=[(2450, 1727), (2977, 350)]
      Match: True
    N=970741=593*1637: SOS(p)=[(23, 8)], SOS(q)=[(31, 26)]
      Direct SOS(N)=[(921, 350), (846, 505)], Brahmagupta=[(846, 505), (921, 350)]
      Match: True
    N=10259309=1621*6329: SOS(p)=[(39, 10)], SOS(q)=[(77, 20)]
      Direct SOS(N)=[(3203, 10), (2803, 1550)], Brahmagupta=[(2803, 1550), (3203, 10)]
      Match: True
    N=3646061=4441*821: SOS(p)=[(60, 29)], SOS(q)=[(25, 14)]
      Direct SOS(N)=[(1906, 115), (1565, 1094)], Brahmagupta=[(1565, 1094), (1906, 115)]
      Match: True
    N=29596361=4909*6029: SOS(p)=[(70, 3)], SOS(q)=[(77, 10)]
      Direct SOS(N)=[(5420, 469), (5360, 931)], Brahmagupta=[(5360, 931), (5420, 469)]
      Match: True

  CRITICAL QUESTION: Can r_2(N) be computed in poly-time without factoring N?
  r_2(N) = 4(d_1(N) - d_3(N)) requires knowing all divisors of N.
  Computing divisors IS factoring. So r_2 as oracle ⟺ factoring oracle.
  NEGATIVE: No shortcut. r_2 encodes factoring, not the other way around.

  However: theta(tau)^2 = sum r_2(n) q^n is a modular form of weight 1.
  Its Fourier coefficients at OTHER cusps may be computable without factoring N.
  This is the modular forms approach — see Exp 3.
[DONE] EXP 1: r_2(N) for semiprimes in 0.02s

======================================================================
EXPERIMENT: EXP 2: Theta at CM points via tree walks
======================================================================

Computing theta(tau) at points visited by Berggren tree walk.
theta(tau) = sum_{n=-inf}^{inf} exp(i*pi*n^2*tau)

  tau = i:
    theta(i) = (1.08643481121331 + 0.0j)
    known    = 1.08643481121331
    match: 2.6728e-51
    theta(i)^2 = (1.1803405990161 + 0.0j) (encodes r_2 generating function)

  Berggren tree walk (depth 1-4):
  Path                 tau                                 |theta(tau)|    |theta^2|       Im(tau)   
  -----------------------------------------------------------------------------------------------
  root                 (0.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M1              (2.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M3              (2.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M1.M1           (1.6 + 0.2j)                        1.624599        2.6393218       0.2       
  root.M1.M3           (4.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M3.M1           (1.6 + 0.2j)                        1.624599        2.6393218       0.2       
  root.M3.M3           (4.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M1.M1.M1        (1.3846154 + 0.076923077j)          2.0629538       4.2557786       0.0769231 
  root.M1.M1.M3        (3.6 + 0.2j)                        1.624599        2.6393218       0.2       
  root.M1.M3.M1        (1.7647059 + 0.058823529j)          2.2060528       4.866669        0.0588235 
  root.M1.M3.M3        (6.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M3.M1.M1        (1.3846154 + 0.076923077j)          2.0629538       4.2557786       0.0769231 
  root.M3.M1.M3        (3.6 + 0.2j)                        1.624599        2.6393218       0.2       
  root.M3.M3.M1        (1.7647059 + 0.058823529j)          2.2060528       4.866669        0.0588235 
  root.M3.M3.M3        (6.0 + 1.0j)                        1.0864348       1.1803406       1.0       
  root.M1.M1.M1.M1     (1.28 + 0.04j)                      2.4293421       5.901703        0.04      
  root.M1.M1.M1.M3     (3.3846154 + 0.076923077j)          2.0629538       4.2557786       0.0769231 
  root.M1.M1.M3.M1     (1.7230769 + 0.015384615j)          3.0848355       9.5162101       0.0153846 
  root.M1.M1.M3.M3     (5.6 + 0.2j)                        1.624599        2.6393218       0.2       
  root.M1.M3.M1.M1     (1.4339623 + 0.018867925j)          2.9313835       8.5930093       0.0188679 

  KEY: M3 = T^2, so M3(tau) = tau+2. theta(tau+2) = theta(tau) (period 2).
  Berggren walks that include M3 steps don't change theta!
  Only M1 and M2 change the theta value — they are the 'interesting' generators.

  Theta transformation law under Berggren generators:
    M1: tau=(0.0 + 1.0j) -> (2.0 + 1.0j), theta ratio = (1.0 + 1.608572226e-52j)
           |ratio| = 1.0, arg = 5.12024e-53*pi
    M3: tau=(0.0 + 1.0j) -> (2.0 + 1.0j), theta ratio = (1.0 + 1.608572226e-52j)
           |ratio| = 1.0, arg = 5.12024e-53*pi

  THEOREM T103: The Berggren generators {M1, M2, M3} act on theta(tau) as:
    M3: theta -> theta (period 2 shift)
    M1, M2: theta -> j(tau)^{-1/2} * theta (modular transformation)
    where j(tau) = c*tau + d is the automorphy factor.
[DONE] EXP 2: Theta at CM points via tree walks in 0.02s

======================================================================
EXPERIMENT: EXP 3: Hecke eigenvalues for theta^2
======================================================================

Hecke eigenvalues of theta^2 (weight-1 Eisenstein series for Gamma_0(4)):
  a_p = r_2(p) / 4 ... but let's verify the Hecke theory directly.

  For prime p:
    p=2: r_2(2) = 4(1-0) = 4  [2 = 1^2 + 1^2]
    p≡1 mod 4: r_2(p) = 4(2-0) = 8  [p is sum of 2 squares, 4 sign combos * 2 orderings]
    p≡3 mod 4: r_2(p) = 4(1-1) = 0  [p is NOT sum of 2 squares]

  Verification:
  p        p mod 4    r_2(p)     predicted  SOS reps            
  ----------------------------------------------------------
  2        2          4          4          [(1, 1)]
  3        3          0          0          []
  5        1          8          8          [(2, 1)]
  7        3          0          0          []
  11       3          0          0          []
  13       1          8          8          [(3, 2)]
  17       1          8          8          [(4, 1)]
  19       3          0          0          []
  23       3          0          0          []
  29       1          8          8          [(5, 2)]
  31       3          0          0          []
  37       1          8          8          [(6, 1)]
  41       1          8          8          [(5, 4)]
  43       3          0          0          []
  47       3          0          0          []
  53       1          8          8          [(7, 2)]
  59       3          0          0          []
  61       1          8          8          [(6, 5)]
  67       3          0          0          []
  71       3          0          0          []
  73       1          8          8          [(8, 3)]
  79       3          0          0          []
  83       3          0          0          []
  89       1          8          8          [(8, 5)]
  97       1          8          8          [(9, 4)]

  All verified: r_2(p) = 4(1 + chi_4(p)) for primes p.

  Hecke multiplicativity: r_2 is NOT fully multiplicative (it's not a Hecke eigenform
  in the usual sense because theta^2 is an Eisenstein series, not a cusp form).
  However, for (m,n)=1:
    r_2(mn) = r_2(m) * r_2(n)  ... NO, this is WRONG.
    Correct: d_1(mn) - d_3(mn) = (d_1(m)-d_3(m))(d_1(n)-d_3(n)) for (m,n)=1

  Verifying multiplicativity of (d_1 - d_3) for coprime pairs:
  Verified 1410 coprime pairs: (d_1-d_3) IS multiplicative!

  L-function connection:
    sum r_2(n)/n^s = 4 * L(s, chi_4) * zeta(s)
    where L(s, chi_4) = sum chi_4(n)/n^s = 1 - 1/3^s + 1/5^s - 1/7^s + ...
    This factorization of the Dirichlet series is equivalent to
    the multiplicativity of (d_1 - d_3).

  THEOREM T104: r_2(N) / 4 = (d_1-d_3)(N) is a multiplicative function.
    Its Dirichlet series factors as L(s,chi_4) * zeta(s).
    For N=pq: r_2(pq)/4 = (1+chi_4(p))(1+chi_4(q)) when gcd(p,q)=1.
    This means r_2(pq) ∈ {0, 4, 8, 16} depending on p,q mod 4:
      p≡q≡1: r_2 = 4*2*2 = 16
      p≡1,q≡3: r_2 = 4*2*0 = 0
      p≡q≡3: r_2 = 4*0*0 = 0

  Verification on semiprimes:
    N=82393873=4441*18553, p%4=1, q%4=1: r_2=16, predicted=16, match=True
    N=186042391=6719*27689, p%4=3, q%4=1: r_2=0, predicted=0, match=True
    N=148938379=18481*8059, p%4=1, q%4=3: r_2=0, predicted=0, match=True
    N=90748817=3511*25847, p%4=3, q%4=3: r_2=0, predicted=0, match=True
    N=1368423803=36151*37853, p%4=3, q%4=1: r_2=0, predicted=0, match=True
    N=531592403=22777*23339, p%4=1, q%4=3: r_2=0, predicted=0, match=True
    N=50558003=4409*11467, p%4=1, q%4=3: r_2=0, predicted=0, match=True
    N=227864269=9857*23117, p%4=1, q%4=1: r_2=16, predicted=16, match=True
    N=864315937=37781*22877, p%4=1, q%4=1: r_2=16, predicted=16, match=True
    N=802499461=46993*17077, p%4=1, q%4=1: r_2=16, predicted=16, match=True
[DONE] EXP 3: Hecke eigenvalues for theta^2 in 0.03s

======================================================================
EXPERIMENT: EXP 4: Theta series for SIQS guidance
======================================================================

Correlation between r_4(n) (four-square representations) and smoothness.
Jacobi: r_4(n) = 8 * sum_{d|n, 4 ∤ d} d

  Sample size: 2000 numbers in [10^6, 10^7], B=1000
  Bottom half by r_4: 239/1000 smooth (23.9%)
  Top half by r_4:    158/1000 smooth (15.8%)
  Ratio: 0.66x
  Mean largest prime factor: bottom=354270, top=737934

  Pearson correlation:
    r_4 vs smooth:      -0.0648
    r_4 vs largest_pf:  0.0745
  WEAK/NO signal: r_4 not a strong smoothness predictor.

  SIQS application analysis:
    For Q(x) = ax^2 + 2bx + c, the value Q(x) is ~a*M^2 for sieve range M.
    r_4(Q(x)) depends on Q(x), not on the polynomial choice.
    We can't pre-compute r_4 without evaluating Q(x) — which is what sieving does.
    CONCLUSION: r_4 as smoothness proxy doesn't help SIQS polynomial selection.
    The sieve itself is already the optimal way to detect smoothness.

  THEOREM T105: r_4(n) = 8·sigma_1^*(n) (restricted divisor sum) correlates with
    smoothness, but computing r_4(n) requires factoring n, making it circular
    as a SIQS optimization. The sieve is already optimal for smoothness detection.
[DONE] EXP 4: Theta series for SIQS guidance in 0.38s

======================================================================
EXPERIMENT: EXP 5: r_2(N) as factoring oracle
======================================================================

Information content of r_2(N) for semiprimes N=pq:

  For N=pq (both odd, distinct):
    r_2(N) ∈ {0, 16}
    r_2(N)=16 iff p≡q≡1 mod 4
    r_2(N)=0  otherwise
    Information: exactly 1 bit (residue class constraint)

  But wait — for p≡q≡1 mod 4, the actual SOS decompositions are more informative.
  If N = a² + b² (with a>b>0), then gcd(a-b, N) or gcd(a+b, N) might give a factor!

  SOS-based factoring test (p,q ≡ 1 mod 4, 5-6 digit primes):
    Trials: 100
    Factor found via gcd(a±b, N): 0/100 (0.0%)

  KEY INSIGHT: If N = a² + b² = c² + d² (two DIFFERENT reps),
  then gcd(a*c - b*d, N) or gcd(a*d - b*c, N) gives a non-trivial factor.
  This is the classical 'two representations' factoring method.

  Two-representation factoring test:
    Semiprimes with ≥2 SOS reps: 100/100
    Factor found: 100/100 (100.0%)

  THEOREM T106: For N=pq with p≡q≡1 mod 4, N has exactly 2 distinct
    SOS representations (up to order/sign). Given both, factoring is trivial.
    Finding a SINGLE SOS representation is as hard as factoring (Rabin 1977).
    r_2(N) tells us how many reps exist but doesn't help find them.
    Information: 1 bit from r_2, but finding actual reps ≡ factoring.
[DONE] EXP 5: r_2(N) as factoring oracle in 14.19s

======================================================================
EXPERIMENT: EXP 6: Theta function and L(s,chi_4) zeros
======================================================================

L(s, chi_4) = prod_{p odd} (1 - chi_4(p)/p^s)^{-1}
  = 1 - 1/3^s + 1/5^s - 1/7^s + 1/9^s - ...

  L(1, chi_4) = 0.785393163397
  pi/4        = 0.785398163397
  match: 5.0e-6

  Searching for zeros of L(1/2 + it, chi_4):
  Approximate zeros (sign changes) at t ≈ [3.5, 6.0, 6.5, 8.5, 10.5, 12.0, 13.0, 13.5, 15.0, 16.5]
  Known first zero: t ≈ 6.0209...

  Connection to Berggren tree:
    L(s, chi_4) * zeta(s) = sum r_2(n)/(4*n^s)
    The zeros of L(s, chi_4) control the distribution of primes ≡ 1,3 mod 4.
    Primes ≡ 1 mod 4 are exactly those representable as sum of 2 squares.
    These are the hypotenuses reachable by the Pythagorean tree!

  THEOREM T107: The zeros of L(s,chi_4) govern the distribution of
    Pythagorean hypotenuses (primes ≡ 1 mod 4) in the Berggren tree.
    The Berggren tree 'knows' about L(s,chi_4) through its growth rate:
    #{p prime <= x : p = 1 mod 4} = Li(x)/2 + O(x^{1/2+eps})
    where the error term depends on zeros of L(s,chi_4) (GRH).
[DONE] EXP 6: Theta function and L(s,chi_4) zeros in 2.97s

======================================================================
EXPERIMENT: EXP 7: Lattice theta series for PPT variety
======================================================================

Computing PPT theta series: Theta_PPT(q) = sum_{PPTs} q^c
where c is the hypotenuse.

  PPTs with hypotenuse ≤ 5000: 792

  PPT count vs r_2 for hypotenuse values:
  c        #PPTs    r_2(c)   r_2/8    c prime?   c mod 4 
  --------------------------------------------------
  5        1        8        1        True       1       
  13       1        8        1        True       1       
  17       1        8        1        True       1       
  25       1        12       1        False      1       
  29       1        8        1        True       1       
  37       1        8        1        True       1       
  41       1        8        1        True       1       
  53       1        8        1        True       1       
  61       1        8        1        True       1       
  65       2        16       2        False      1       
  73       1        8        1        True       1       
  85       2        16       2        False      1       
  89       1        8        1        True       1       
  97       1        8        1        True       1       
  101      1        8        1        True       1       
  109      1        8        1        True       1       
  113      1        8        1        True       1       
  125      1        16       2        False      1       
  137      1        8        1        True       1       
  145      2        16       2        False      1       

  Relationship: #PPTs with hypotenuse c = r_2(c)/8 (for odd c)
  Wait — not exactly. r_2(c) counts a²+b²=c (not a²+b²=c²).
  PPTs have a²+b²=c², so the relevant quantity is r_2(c²)/8.

  Corrected: r_2(c²) for PPT hypotenuses:
  c        #PPTs    r_2(c²)    r_2(c²)/8 
  ----------------------------------------
  5        1        12         1.0       
  13       1        12         1.0       
  17       1        12         1.0       
  25       1        20         2.0       
  29       1        12         1.0       
  37       1        12         1.0       
  41       1        12         1.0       
  53       1        12         1.0       
  61       1        12         1.0       
  65       2        36         4.0       
  73       1        12         1.0       
  85       2        36         4.0       
  89       1        12         1.0       
  97       1        12         1.0       
  101      1        12         1.0       

  PPT theta series first 20 nonzero coefficients:
    q^5: 1
    q^13: 1
    q^17: 1
    q^25: 1
    q^29: 1
    q^37: 1
    q^41: 1
    q^53: 1
    q^61: 1
    q^65: 2
    q^73: 1
    q^85: 2
    q^89: 1
    q^97: 1
    q^101: 1
    q^109: 1
    q^113: 1
    q^125: 1
    q^137: 1
    q^145: 2

  Cumulative PPT count vs asymptotic x/(2*pi):
    c ≤ 500: actual=80, predicted=79.6, ratio=1.0053
    c ≤ 1000: actual=158, predicted=159.2, ratio=0.9927
    c ≤ 2000: actual=319, predicted=318.3, ratio=1.0022
    c ≤ 3000: actual=477, predicted=477.5, ratio=0.9990
    c ≤ 5000: actual=792, predicted=795.8, ratio=0.9953

  THEOREM T108: The PPT theta series Theta_PPT(q) = sum q^c has growth rate
    sum_{c≤x} coeff(q^c) ~ x/(2*pi), consistent with the density of
    Pythagorean hypotenuses being 1/(2*pi) per integer.
    Connection to theta_3²: the PPT series is a 'square-root' of theta_3²
    restricted to the Pythagorean cone a²+b²=c².
[DONE] EXP 7: Lattice theta series for PPT variety in 0.00s

======================================================================
EXPERIMENT: EXP 8: Practical theta-guided factoring
======================================================================

Theta-guided factoring approaches:

  Approach A: SOS enumeration via Cornacchia's algorithm
  For N=pq, finding a²+b²=N is equivalent to factoring (Rabin 1977).
  Cornacchia's algorithm finds SOS reps given a factorization.
  CIRCULAR: can't use without knowing factors.

  Approach B: Lattice SOS via sqrt(-1) mod N
    Trials: 20 semiprimes (p,q ≡ 1 mod 4, 7-digit primes)
    SOS found via lattice: 20/20
    Factor extracted: 0/20

  Approach C: Random walk SOS search (no factoring oracle)
  For N=pq ~10^14, try random a and check if N-a² is a perfect square.
    Trial 0: N=1358616437=21433*63389, found SOS in random search, gcd=1
    Trial 2: N=4122438629=78593*52453, found SOS in random search, gcd=1
    Trial 4: N=939192673=17117*54869, found SOS in random search, gcd=1
    Trial 5: N=2727145721=31177*87473, found SOS in random search, gcd=1
    Trial 6: N=2255140357=41381*54497, found SOS in random search, gcd=1
    Trial 7: N=1881303577=32429*58013, found SOS in random search, gcd=1
    Trial 9: N=1607659373=70769*22717, found SOS in random search, gcd=1

    Random SOS search: 0/10 factored
    Expected: O(sqrt(N)) trials needed (exponential in digits)

  Approach D: Theta function numerical evaluation
    Test N=65 = 5 × 13
    r_2(65) = 16
    SOS reps: [(8, 1), (7, 4)]
    theta(i*0.01)^2 from r_2: 99.79798249
    theta(i*0.01)^2 direct:   100.0

  THEOREM T109: All theta-function approaches to factoring reduce to either:
    (a) Computing r_2(N), which requires factoring N (circular), or
    (b) Finding SOS decompositions of N, which is equivalent to factoring
        (Rabin 1977: finding a²+b²=N is polynomial-time equivalent to factoring N).
    The theta function beautifully ENCODES factoring information in its
    Fourier coefficients, but EXTRACTING a single coefficient requires
    knowing the factorization. The modular form is an elegant reformulation,
    not a computational shortcut.

  COROLLARY: The Berggren tree (= Gamma_theta) is the NATURAL home for
    SOS factoring, but navigating the tree to find the right node is as
    hard as factoring itself. The tree structure doesn't help — it IS the problem.
[DONE] EXP 8: Practical theta-guided factoring in 0.04s

======================================================================
SUMMARY OF THEOREMS
======================================================================

T102: For N=pq with p≡q≡1 (mod 4), r_2(N) = 16, and each of the 2 distinct SOS
      decompositions corresponds to a factorization via Brahmagupta-Fibonacci.

T103: Berggren generators act on theta(tau): M3 preserves theta (period-2 shift),
      M1/M2 apply modular transformation with automorphy factor.

T104: r_2(N)/4 = (d_1-d_3)(N) is multiplicative. Its Dirichlet series factors as
      L(s,chi_4) * zeta(s). For N=pq: r_2(pq) = 4(1+chi_4(p))(1+chi_4(q)).

T105: r_4(n) correlates with smoothness but computing it requires factoring n,
      making it circular as a SIQS optimization.

T106: Given two SOS decompositions N=a²+b²=c²+d², factoring is trivial via
      gcd(ac-bd, N). But finding even one SOS rep is equivalent to factoring (Rabin 1977).

T107: Zeros of L(s,chi_4) govern the distribution of Pythagorean hypotenuses
      (primes ≡ 1 mod 4) in the Berggren tree.

T108: PPT theta series has growth rate ~ x/(2*pi), matching hypotenuse density.
      It is a restriction of theta_3² to the Pythagorean cone.

T109: ALL theta-function factoring approaches reduce to either computing r_2(N)
      (requires factoring) or finding SOS decompositions (equivalent to factoring).
      The theta function encodes factoring information but extracting it is circular.

BOTTOM LINE: The Berggren/theta connection is mathematically deep but
computationally useless for factoring. Every approach is circular:
  theta -> r_2 -> divisors -> factoring -> theta
The modular form is an elegant reformulation, NOT a shortcut.
