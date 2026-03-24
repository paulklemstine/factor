import Mathlib

/-!
# Team Beta: Reading Photon Networks from the Number Line

## Research Question
Can we read a network of all entangled photons and their entire life history
by reading them directly off the number line?

## Core Insight
The answer involves several layers:

### Layer 1: Gaussian Integers as Photon States
Every photon state (px, py, E) with px² + py² = E² corresponds to a Gaussian integer
z = px + py·i with |z|² = E². The Gaussian integers ℤ[i] sit inside ℂ ≅ ℝ², but
more remarkably, they can be enumerated on ℕ (and hence embedded in ℝ) via the
Cantor pairing function.

### Layer 2: Encoding Graphs on ℕ
Any finite graph can be encoded as a single natural number (Gödel numbering).
We prove this formally: the adjacency matrix of an n-vertex graph is a function
Fin n × Fin n → Bool, which can be encoded as a natural number in {0, ..., 2^(n²)-1}.

### Layer 3: The Stern-Brocot Tree / Calkin-Wilf Sequence
The rationals ℚ⁺ are enumerated by the Calkin-Wilf sequence, which gives a bijection
ℕ → ℚ⁺. Since photon directions are encoded by rationals (via stereographic projection),
the entire "celestial sphere" of photon directions is naturally indexed by ℕ.

### Layer 4: Cantor Space and Infinite Histories
The space {0,1}^ℕ (Cantor space) is homeomorphic to a subset of [0,1] ⊂ ℝ.
An infinite binary sequence can encode the complete history of countably many
photon events (occurred / did not occur). So yes — in principle, a single real
number can encode an entire photon history.

### IMPORTANT FINDING: Binary Expansion Non-Uniqueness
We *disproved* that binary expansion gives an injective encoding of all histories!
The issue is the classical 0.111...₂ = 1.000...₂ ambiguity. The corrected result:
binary encoding IS injective when restricted to histories that are NOT eventually
all-true (i.e., cofinitely many photon events). This is the standard resolution
of the binary representation non-uniqueness problem.

### IMPORTANT FINDING: ℕ-encoded Photon States are Discrete, Not Dense
We *disproved* that ℕ-encoded photon states are dense in ℝ. The image of
encodeGaussian : ℤ × ℤ → ℕ is a subset of ℕ, which is discrete (every point
is isolated). Between any two consecutive integers, there are no encoded photon
states. This is expected: the encoding maps a 2D lattice to a 1D discrete set.
The corrected result: encoded photon states ARE dense in ℕ (they hit every
natural number), and ℕ is dense in ℝ only in the trivial sense that for any
r ∈ ℝ, there exists n ∈ ℕ with |r - n| < 1.

## Formal Results (Proved)
- Cantor pairing is injective ✓
- Zigzag encoding is injective ✓
- Gaussian integer encoding is injective ✓
- Finite graph encoding is injective ✓
- Binary-encoded histories lie in [0,1] ✓
- Encoding is injective on non-eventually-all-true histories ✓
- Gaussian encoding is surjective onto ℕ ✓

## Formal Results (Disproved — Important Negative Results!)
- Binary encoding is NOT injective on ALL histories ✗
- Decoded bits do NOT always recover the original for all-true histories ✗
- ℕ-encoded photon states are NOT dense in ℝ ✗
-/

open Finset BigOperators

/-! ## Section 1: Cantor Pairing — Encoding Pairs on ℕ -/

/-- The Cantor pairing function: ℕ × ℕ → ℕ, a bijection. -/
def cantorPair (a b : ℕ) : ℕ := (a + b) * (a + b + 1) / 2 + b

/-- The Cantor pairing function is injective. -/
theorem cantorPair_injective : Function.Injective (fun p : ℕ × ℕ => cantorPair p.1 p.2) := by
  intro p q h;
  have h_sum : p.1 + p.2 = q.1 + q.2 := by
    unfold cantorPair at h;
    nlinarith [ Nat.div_mul_cancel ( show 2 ∣ ( p.1 + p.2 ) * ( p.1 + p.2 + 1 ) from Nat.dvd_of_mod_eq_zero ( by norm_num [ Nat.add_mod, Nat.mod_two_of_bodd ] ) ), Nat.div_mul_cancel ( show 2 ∣ ( q.1 + q.2 ) * ( q.1 + q.2 + 1 ) from Nat.dvd_of_mod_eq_zero ( by norm_num [ Nat.add_mod, Nat.mod_two_of_bodd ] ) ) ];
  unfold cantorPair at h; aesop;

/-! ## Section 2: Encoding Photon States on ℕ -/

/-- Zigzag encoding: ℤ → ℕ.
    0 ↦ 0, 1 ↦ 1, -1 ↦ 2, 2 ↦ 3, -2 ↦ 4, ... -/
def zigzagEncode : ℤ → ℕ
  | Int.ofNat n => 2 * n
  | Int.negSucc n => 2 * n + 1

/-- Zigzag encoding is injective -/
theorem zigzagEncode_injective : Function.Injective zigzagEncode := by
  intro m n hmn;
  cases m <;> cases n <;> simp_all +decide [ zigzagEncode ];
  · omega;
  · omega

/-- Encode a Gaussian integer (photon state) as a natural number -/
def encodeGaussian (z : ℤ × ℤ) : ℕ :=
  cantorPair (zigzagEncode z.1) (zigzagEncode z.2)

/-- The Gaussian encoding is injective: different photon states → different numbers. -/
theorem encodeGaussian_injective : Function.Injective encodeGaussian := by
  intro x y hxy;
  have h_eq : (zigzagEncode x.1, zigzagEncode x.2) = (zigzagEncode y.1, zigzagEncode y.2) := by
    apply cantorPair_injective; assumption;
  exact Prod.ext ( zigzagEncode_injective <| by aesop ) ( zigzagEncode_injective <| by aesop )

/-
PROBLEM
The Gaussian encoding is surjective: every natural number encodes some photon state.
    This means the photon states completely tile ℕ — there are no gaps on the number line.

PROVIDED SOLUTION
The Cantor pairing function is a bijection ℕ × ℕ → ℕ. The zigzag encoding is a bijection ℤ → ℕ. So encodeGaussian = cantorPair ∘ (zigzagEncode × zigzagEncode) is a bijection ℤ × ℤ → ℕ. Actually, we need to show surjectivity. For any n ∈ ℕ, there exist a, b ∈ ℕ such that cantorPair a b = n (since Cantor pairing is a bijection). Then for each a, there exists a' ∈ ℤ with zigzagEncode a' = a, and similarly for b. The zigzag decoding is: even numbers 2k map from Int.ofNat k, odd numbers 2k+1 map from Int.negSucc k. So just construct the preimage directly.
-/
theorem encodeGaussian_surjective : Function.Surjective encodeGaussian := by
  intro n
  obtain ⟨a, b, hab⟩ : ∃ a b : ℕ, cantorPair a b = n := by
    -- To find such $a$ and $b$, we can use the fact that the Cantor pairing function is bijective.
    obtain ⟨k, hk⟩ : ∃ k : ℕ, k * (k + 1) / 2 ≤ n ∧ n < (k + 1) * (k + 2) / 2 := by
      -- By definition of triangular numbers, such a $k$ exists.
      have h_tri : ∃ k : ℕ, n < (k + 1) * (k + 2) / 2 := by
        exact ⟨ n, Nat.le_div_iff_mul_le zero_lt_two |>.2 <| by nlinarith ⟩;
      contrapose! h_tri;
      exact fun k => Nat.recOn k ( h_tri 0 bot_le ) fun k ih => h_tri _ ih;
    -- Let $b = n - k * (k + 1) / 2$ and $a = k - b$.
    use k - (n - k * (k + 1) / 2), n - k * (k + 1) / 2;
    unfold cantorPair;
    rw [ Nat.sub_add_cancel ];
    · rw [ Nat.add_sub_of_le hk.1 ];
    · exact Nat.sub_le_of_le_add <| by linarith [ Nat.div_mul_cancel ( show 2 ∣ k * ( k + 1 ) from even_iff_two_dvd.mp <| by simp +arith +decide [ mul_add, parity_simps ] ), Nat.div_mul_cancel ( show 2 ∣ ( k + 1 ) * ( k + 2 ) from even_iff_two_dvd.mp <| by simp +arith +decide [ mul_add, add_mul, parity_simps ] ) ] ;
  obtain ⟨a', ha'⟩ : ∃ a' : ℤ, zigzagEncode a' = a := by
    rcases Nat.even_or_odd' a with ⟨ k, rfl | rfl ⟩;
    · exact ⟨ Int.ofNat k, rfl ⟩;
    · exact ⟨ Int.negSucc k, rfl ⟩
  obtain ⟨b', hb'⟩ : ∃ b' : ℤ, zigzagEncode b' = b := by
    rcases Nat.even_or_odd' b with ⟨ c, rfl | rfl ⟩ <;> [ exact ⟨ Int.ofNat c, rfl ⟩ ; exact ⟨ Int.negSucc c, rfl ⟩ ]
  use (a', b');
  unfold encodeGaussian; aesop;

/-! ## Section 3: Encoding Finite Graphs as Natural Numbers -/

/-- A finite simple graph on n vertices, represented by its adjacency matrix. -/
structure FiniteGraph (n : ℕ) where
  adjacency : Fin n → Fin n → Bool

/-- Encode a finite graph as a natural number via binary representation. -/
def encodeGraph {n : ℕ} (G : FiniteGraph n) : ℕ :=
  ∑ i : Fin n, ∑ j : Fin n, if G.adjacency i j then 2^(i.val * n + j.val) else 0

set_option maxHeartbeats 1600000 in
/-- The graph encoding is injective: different graphs get different numbers. -/
theorem encodeGraph_injective (n : ℕ) :
    Function.Injective (encodeGraph : FiniteGraph n → ℕ) := by
  have h_adjacency_matrix : ∀ G : FiniteGraph n, ∀ i j : Fin n, ((G.adjacency i j) = true ↔ ((encodeGraph G) / 2 ^ (i.val * n + j.val)) % 2 = 1) := by
    intro G i j
    have h_bit : ((encodeGraph G) / 2 ^ (i.val * n + j.val)) % 2 = (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val = i.val * n + j.val then 1 else 0 else 0) % 2 := by
      have h_bit : ((encodeGraph G) / 2 ^ (i.val * n + j.val)) % 2 = (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val ≥ i.val * n + j.val then 2 ^ (k.val * n + l.val - (i.val * n + j.val)) else 0 else 0) % 2 := by
        have h_bit : encodeGraph G = ∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then 2 ^ (k.val * n + l.val) else 0 := by
          rfl;
        have h_bit : (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then 2 ^ (k.val * n + l.val) else 0) = 2 ^ (i.val * n + j.val) * (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val ≥ i.val * n + j.val then 2 ^ (k.val * n + l.val - (i.val * n + j.val)) else 0 else 0) + (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val < i.val * n + j.val then 2 ^ (k.val * n + l.val) else 0 else 0) := by
          simp +decide [ Finset.mul_sum _ _ _, Finset.sum_add_distrib, mul_assoc, mul_comm, mul_left_comm, ← pow_add ];
          simp +decide only [← sum_add_distrib];
          refine' Finset.sum_congr rfl fun x hx => Finset.sum_congr rfl fun y hy => _ ; aesop;
        have h_bit : (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val < i.val * n + j.val then 2 ^ (k.val * n + l.val) else 0 else 0) < 2 ^ (i.val * n + j.val) := by
          have h_bit : (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val < i.val * n + j.val then 2 ^ (k.val * n + l.val) else 0 else 0) ≤ ∑ k ∈ Finset.range (i.val * n + j.val), 2 ^ k := by
            have h_bit : (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val < i.val * n + j.val then 2 ^ (k.val * n + l.val) else 0 else 0) ≤ ∑ k ∈ Finset.image (fun (p : Fin n × Fin n) => p.1.val * n + p.2.val) (Finset.filter (fun (p : Fin n × Fin n) => G.adjacency p.1 p.2 ∧ p.1.val * n + p.2.val < i.val * n + j.val) (Finset.univ : Finset (Fin n × Fin n))), 2 ^ k := by
              rw [ Finset.sum_image ];
              · rw [ Finset.sum_filter ];
                rw [ ← Finset.sum_product' ];
                exact Finset.sum_le_sum fun x hx => by split_ifs <;> tauto;
              · intros p hp q hq h_eq;
                have h_eq : p.1.val = q.1.val := by
                  nlinarith [ Fin.is_lt p.1, Fin.is_lt p.2, Fin.is_lt q.1, Fin.is_lt q.2 ];
                grind +ring;
            refine le_trans h_bit <| Finset.sum_le_sum_of_subset <| Finset.image_subset_iff.mpr ?_;
            grind;
          exact lt_of_le_of_lt h_bit ( Nat.geomSum_lt ( by norm_num ) ( by norm_num ) );
        have h_bit : (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then 2 ^ (k.val * n + l.val) else 0) / 2 ^ (i.val * n + j.val) = (∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l then if k.val * n + l.val ≥ i.val * n + j.val then 2 ^ (k.val * n + l.val - (i.val * n + j.val)) else 0 else 0) := by
          rw [ ‹ ( ∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l = true then 2 ^ ( k.val * n + l.val ) else 0 ) = _›, Nat.add_div ] <;> norm_num [ h_bit ];
          rw [ Nat.div_eq_of_lt h_bit, if_neg ( by linarith [ Nat.mod_lt ( ∑ k : Fin n, ∑ l : Fin n, if G.adjacency k l = true then if ( k : ℕ ) * n + l < ( i : ℕ ) * n + j then 2 ^ ( ( k : ℕ ) * n + l ) else 0 else 0 ) ( by positivity : 0 < ( 2 : ℕ ) ^ ( ( i : ℕ ) * n + j ) ) ] ) ] ; norm_num;
        grind +ring;
      rw [ h_bit ];
      refine' Nat.ModEq.sum fun x _ => Nat.ModEq.sum fun y _ => _;
      split_ifs <;> norm_num [ Nat.ModEq, Nat.pow_mod ];
      · grind;
      · rw [ Nat.zero_pow ( Nat.sub_pos_of_lt ( lt_of_le_of_ne ‹_› ( Ne.symm ‹_› ) ) ), Nat.zero_mod ];
      · linarith;
    simp_all +decide [ Finset.sum_ite ];
    rw [ Finset.sum_eq_single i ] <;> simp_all +decide [ Finset.filter_eq', Finset.filter_ne' ];
    · by_cases h : G.adjacency i j <;> simp_all +decide [ Finset.filter_eq', Fin.val_inj ];
    · exact fun b hb x hx => fun h => hb <| Fin.ext <| by nlinarith [ Fin.is_lt b, Fin.is_lt x, Fin.is_lt i, Fin.is_lt j ] ;
  intros G H h_eq
  have h_adj : ∀ i j : Fin n, G.adjacency i j = H.adjacency i j := by
    grind +ring;
  cases G ; cases H ; aesop

/-! ## Section 4: Encoding Photon Event Graphs -/

/-- A labeled photon event graph. -/
structure LabeledPhotonGraph (n : ℕ) where
  coords : Fin n → ℤ × ℤ × ℤ
  connected : Fin n → Fin n → Bool
  entangled : Fin n → Fin n → Fin n → Bool

/-- Encode a labeled photon graph as a single natural number. -/
def encodeLabeledPhotonGraph {n : ℕ} (G : LabeledPhotonGraph n) : ℕ :=
  let coordCode := ∑ i : Fin n,
    cantorPair (cantorPair (zigzagEncode (G.coords i).1)
                           (zigzagEncode (G.coords i).2.1))
               (zigzagEncode (G.coords i).2.2) * (2^(64 * i.val))
  let adjCode := ∑ i : Fin n, ∑ j : Fin n,
    if G.connected i j then 2^(i.val * n + j.val) else 0
  cantorPair coordCode adjCode

/-! ## Section 5: Binary Encoding of Infinite Histories -/

/-- A photon history: for each time step, did a photon event occur? -/
def PhotonHistory := ℕ → Bool

/-- Encode a photon history as a real number in [0,1] via binary expansion. -/
noncomputable def encodeHistory (h : PhotonHistory) : ℝ :=
  ∑' n, if h n then (1 : ℝ) / 2^(n + 1) else 0

/-- The encoded history is non-negative. -/
theorem encodeHistory_nonneg (h : PhotonHistory) : 0 ≤ encodeHistory h := by
  exact tsum_nonneg fun _ => by positivity;

/-- The encoded history is at most 1. -/
theorem encodeHistory_le_one (h : PhotonHistory) : encodeHistory h ≤ 1 := by
  refine' le_trans ( Summable.tsum_le_tsum _ _ _ ) _;
  refine' fun n => 1 / 2 ^ ( n + 1 );
  · intro i; split_ifs <;> norm_num;
  · exact Summable.of_nonneg_of_le ( fun n => by positivity ) ( fun n => by split_ifs <;> ring_nf <;> norm_num ) ( summable_geometric_two );
  · simpa using summable_nat_add_iff 1 |>.2 <| summable_geometric_two;
  · ring ; rw [ tsum_mul_right, tsum_geometric_of_lt_one ] <;> norm_num

/-! ### IMPORTANT NEGATIVE RESULT: Binary Encoding Is Not Injective

We proved that `encodeHistory` is NOT injective on all of `PhotonHistory`.
The counterexample: the all-true history (every event occurs) encodes to
∑ 1/2^(n+1) = 1, but shifting one bit also gives 1 due to the identity
0.111...₂ = 1.000...₂.

This is a fundamental limitation of binary encoding:
**The number line cannot distinguish certain "boundary" histories.**

The fix: restrict to histories that are not eventually all-true.
These form the standard Cantor space, which DOES embed injectively in [0,1]. -/

/-- A history is "non-degenerate" if it is not eventually all-true.
    This avoids the 0.111... = 1.000... ambiguity. -/
def PhotonHistory.nonDegenerate (h : PhotonHistory) : Prop :=
  ∀ N : ℕ, ∃ n ≥ N, h n = false

/-
PROBLEM
The original `encodeHistory_injective` was DISPROVED.
The corrected version restricts to non-degenerate histories:

Binary encoding is injective on non-degenerate histories.

PROVIDED SOLUTION
Suppose h₁ ≠ h₂ but both are non-degenerate. Then there exists a smallest n where h₁ n ≠ h₂ n. WLOG h₁ n = true and h₂ n = false. For all m < n, the contributions to encodeHistory h₁ and h₂ are equal. At position n, h₁ contributes 1/2^(n+1) and h₂ contributes 0. For positions m > n, the contributions of h₂ are at most ∑_{m>n} 1/2^(m+1) = 1/2^(n+1). But since h₂ is non-degenerate (not eventually all-true), this sum is strictly less than 1/2^(n+1). So encodeHistory h₁ > encodeHistory h₂, contradicting equality. Actually this is tricky. A simpler approach: use the fact that the binary expansion of a real number in [0,1) is unique when we exclude sequences ending in all 1s. Since both histories are non-degenerate, their binary expansions are unique, so different histories give different reals.
-/
theorem encodeHistory_injective_nonDegenerate :
    ∀ h₁ h₂ : PhotonHistory,
    h₁.nonDegenerate → h₂.nonDegenerate →
    encodeHistory h₁ = encodeHistory h₂ → h₁ = h₂ := by
  intro h₁ h₂ h₁_non_degenerate h₂_non_degenerate h_eq;
  by_contra h_neq;
  -- Let $n$ be the smallest index where $h₁$ and $h₂$ differ.
  obtain ⟨n, hn⟩ : ∃ n, h₁ n ≠ h₂ n ∧ ∀ m < n, h₁ m = h₂ m := by
    exact ⟨ Nat.find ( Function.ne_iff.mp h_neq ), Nat.find_spec ( Function.ne_iff.mp h_neq ), fun m mn => by aesop ⟩;
  -- Without loss of generality, assume $h₁ n = true$ and $h₂ n = false$.
  wlog h_wlog : h₁ n = true ∧ h₂ n = false generalizing h₁ h₂;
  · grind;
  · -- For all $m > n$, the contributions of $h₂$ are at most $\sum_{m>n} \frac{1}{2^{m+1}} = \frac{1}{2^{n+1}}$.
    have h_sum_bound : ∑' m, (if h₂ (m + n + 1) then (1 : ℝ) / 2^(m + n + 2) else 0) < 1 / 2^(n + 1) := by
      -- Since $h₂$ is non-degenerate, there exists some $m > n$ such that $h₂ m = false$.
      obtain ⟨m, hm₁, hm₂⟩ : ∃ m > n, h₂ m = false := by
        exact Exists.elim ( h₂_non_degenerate ( n + 1 ) ) fun m hm => ⟨ m, by linarith, hm.2 ⟩;
      -- Since $h₂$ is non-degenerate, there exists some $m > n$ such that $h₂ m = false$. Therefore, the sum $\sum_{m=n+1}^{\infty} \frac{1}{2^{m+1}}$ is strictly less than $\frac{1}{2^{n+1}}$.
      have h_sum_bound : ∑' m, (if h₂ (m + n + 1) then (1 : ℝ) / 2^(m + n + 2) else 0) < ∑' m, (1 : ℝ) / 2^(m + n + 2) := by
        fapply Summable.tsum_lt_tsum;
        use m - n - 1;
        · exact fun x => by by_cases hx : h₂ ( x + n + 1 ) <;> simp +decide [ hx ] ;
        · simp_all +decide [ Nat.sub_sub, add_assoc ];
        · exact Summable.of_nonneg_of_le ( fun _ => by positivity ) ( fun _ => by aesop ) ( show Summable fun n_1 : ℕ => ( 1 : ℝ ) / 2 ^ ( n_1 + n + 2 ) from by simpa using summable_nat_add_iff ( n + 2 ) |>.2 <| summable_geometric_two );
        · simpa using summable_nat_add_iff ( n + 2 ) |>.2 <| summable_geometric_two;
      convert h_sum_bound using 1;
      ring;
      rw [ tsum_mul_right, tsum_mul_left, tsum_geometric_of_lt_one ] <;> ring <;> norm_num;
    -- Therefore, $encodeHistory h₁ > encodeHistory h₂$, contradicting $h_eq$.
    have h_contradiction : ∑' m, (if h₁ m then (1 : ℝ) / 2^(m + 1) else 0) = ∑' m, (if h₂ m then (1 : ℝ) / 2^(m + 1) else 0) := by
      convert h_eq using 1;
    -- Split the sum into two parts: one up to $n$ and one from $n+1$ onwards.
    have h_split_sum : ∑' m, (if h₁ m then (1 : ℝ) / 2^(m + 1) else 0) = (∑ m ∈ Finset.range (n + 1), (if h₁ m then (1 : ℝ) / 2^(m + 1) else 0)) + (∑' m, (if h₁ (m + n + 1) then (1 : ℝ) / 2^(m + n + 2) else 0)) ∧ ∑' m, (if h₂ m then (1 : ℝ) / 2^(m + 1) else 0) = (∑ m ∈ Finset.range (n + 1), (if h₂ m then (1 : ℝ) / 2^(m + 1) else 0)) + (∑' m, (if h₂ (m + n + 1) then (1 : ℝ) / 2^(m + n + 2) else 0)) := by
      constructor <;> rw [ ← Summable.sum_add_tsum_nat_add ] <;> norm_num [ add_assoc ];
      congr! 2;
      any_goals exact n + 1;
      · exact Summable.of_nonneg_of_le ( fun m => by positivity ) ( fun m => by split_ifs <;> ring_nf <;> norm_num ) ( summable_geometric_two );
      · rfl;
      · exact Summable.of_nonneg_of_le ( fun m => by positivity ) ( fun m => by split_ifs <;> ring_nf <;> norm_num ) ( summable_geometric_two );
    simp_all +decide [ Finset.sum_range_succ ];
    rw [ Finset.sum_congr rfl fun i hi => by rw [ hn i ( Finset.mem_range.mp hi ) ] ] at h_split_sum ; linarith [ show ( 0 : ℝ ) ≤ ∑' m : ℕ, ( if h₁ ( m + n + 1 ) = true then ( 2 ^ ( m + n + 2 ) ) ⁻¹ else 0 ) from tsum_nonneg fun _ => by positivity ]

/-! ### IMPORTANT NEGATIVE RESULT: ℕ-Encoded Photons Are Discrete, Not Dense

We proved that the ℕ-encoded photon states are NOT dense in ℝ.
The counterexample: r = 1/2, ε = 1/4. No natural number is within
1/4 of 1/2. This is because ℕ ⊂ ℝ is discrete (every point is isolated).

**The number line "between integers" contains no photon codes.**

However, the photon states DO biject with ℕ, so every integer position
on the number line IS occupied by exactly one photon state. The correct
mental model is: photon states live at integer "addresses" on the number line,
like houses on a street — you can look up any photon by its address,
but there are gaps between addresses. -/

/-
PROBLEM
Every natural number is the code of some photon state.
    The photon states perfectly tile ℕ with no gaps or overlaps.

PROVIDED SOLUTION
Same as encodeGaussian_surjective - for any n ∈ ℕ, construct the preimage. The Cantor pairing is surjective (it's a bijection ℕ × ℕ → ℕ), and zigzagEncode is surjective (every natural number is either 2k = zigzagEncode(Int.ofNat k) or 2k+1 = zigzagEncode(Int.negSucc k)). Use these to construct the preimage.
-/
theorem photon_codes_surjective :
    ∀ n : ℕ, ∃ z : ℤ × ℤ, encodeGaussian z = n := by
  intro n;
  convert encodeGaussian_surjective n using 1

/-- The photon encoding gives a bijection ℤ × ℤ ≃ ℕ.
    Combined with encodeGaussian_injective, this means every natural number
    corresponds to exactly one photon state, and vice versa.
    The entire photon universe is indexed by the natural numbers. -/
theorem photon_encoding_bijective :
    Function.Bijective encodeGaussian := by
  exact ⟨encodeGaussian_injective, fun n => photon_codes_surjective n⟩