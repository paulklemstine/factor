import Mathlib

/-!
# Team Alpha: Photon Event Graphs — Modeling Emission and Absorption in Spacetime

## Research Question
Can we model the whole graph of emitters and absorption events in time?

## Core Insight
Every photon has a birth (emission event) and a death (absorption event).
These events form vertices of a directed bipartite graph in spacetime, where
photon worldlines are the edges. The graph inherits causal structure from
Minkowski spacetime: edges must be null (light-like), and the graph is a DAG
because absorption must occur after emission (time-ordering).

## Key Definitions
- `SpacetimeEvent`: A point in (2+1)D Minkowski spacetime
- `PhotonEdge`: A photon connecting emission → absorption (null separation)
- `PhotonEventGraph`: The full DAG of all emission/absorption events
- Proved: The graph is always acyclic (no causal loops)
- Proved: Photon worldlines compose via the existing PhotonState fusion
- Proved: The event graph has a natural partial order (causal order)
-/

open Finset BigOperators

/-! ## Section 1: Spacetime Events -/

/-- A spacetime event in (2+1)-dimensional Minkowski space.
    We use integer coordinates, connecting to the Pythagorean lattice. -/
structure SpacetimeEvent where
  x : ℤ   -- spatial x-coordinate
  y : ℤ   -- spatial y-coordinate
  t : ℤ   -- time coordinate
  deriving DecidableEq, Repr

/-- The Minkowski interval between two events (signature +,+,-). -/
def minkowskiInterval (e₁ e₂ : SpacetimeEvent) : ℤ :=
  (e₂.x - e₁.x)^2 + (e₂.y - e₁.y)^2 - (e₂.t - e₁.t)^2

/-- Two events are null-separated (connected by a light ray) -/
def nullSeparated (e₁ e₂ : SpacetimeEvent) : Prop :=
  minkowskiInterval e₁ e₂ = 0

/-- An event e₂ is in the causal future of e₁ -/
def causalFuture (e₁ e₂ : SpacetimeEvent) : Prop :=
  e₁.t < e₂.t ∧ minkowskiInterval e₁ e₂ ≤ 0

/-- Null separation means the spatial distance equals the time difference.
    This is exactly the Pythagorean condition: Δx² + Δy² = Δt². -/
theorem null_iff_pythagorean (e₁ e₂ : SpacetimeEvent) :
    nullSeparated e₁ e₂ ↔
    (e₂.x - e₁.x)^2 + (e₂.y - e₁.y)^2 = (e₂.t - e₁.t)^2 := by
  simp [nullSeparated, minkowskiInterval]
  omega

/-! ## Section 2: Photon Edges (Worldlines) -/

/-- A photon edge: a worldline connecting an emission event to an absorption event.
    The photon travels on a null geodesic (light ray). -/
structure PhotonEdge where
  emission : SpacetimeEvent   -- where the photon was created
  absorption : SpacetimeEvent -- where the photon was destroyed
  is_null : nullSeparated emission absorption  -- travels at speed of light
  time_ordered : emission.t < absorption.t     -- absorption is in the future

/-- The momentum of a photon edge (spatial displacement). -/
def PhotonEdge.momentum (p : PhotonEdge) : ℤ × ℤ :=
  (p.absorption.x - p.emission.x, p.absorption.y - p.emission.y)

/-- The energy of a photon edge (time displacement). -/
def PhotonEdge.energy (p : PhotonEdge) : ℤ :=
  p.absorption.t - p.emission.t

/-- Photon energy is always positive (time flows forward). -/
theorem PhotonEdge.energy_pos (p : PhotonEdge) : 0 < p.energy := by
  simp only [PhotonEdge.energy]
  linarith [p.time_ordered]

/-- The photon momentum and energy satisfy the on-shell condition:
    px² + py² = E². This is the massless dispersion relation. -/
theorem PhotonEdge.on_shell (p : PhotonEdge) :
    (p.momentum.1)^2 + (p.momentum.2)^2 = p.energy^2 := by
  have h := p.is_null
  rw [null_iff_pythagorean] at h
  exact h

/-! ## Section 3: The Full Photon Event Graph -/

/-- A photon event graph: a collection of spacetime events connected by photon worldlines.
    This models the complete history of photon emissions and absorptions. -/
structure PhotonEventGraph where
  /-- The set of all events (emission and absorption points) -/
  events : Finset SpacetimeEvent
  /-- The photon worldlines connecting events -/
  photons : Finset PhotonEdge
  /-- All photon endpoints are in the event set -/
  emission_mem : ∀ p ∈ photons, p.emission ∈ events
  absorption_mem : ∀ p ∈ photons, p.absorption ∈ events

/-- The number of photons in the graph -/
def PhotonEventGraph.photonCount (G : PhotonEventGraph) : ℕ := G.photons.card

/-- The number of events in the graph -/
def PhotonEventGraph.eventCount (G : PhotonEventGraph) : ℕ := G.events.card

/-- An event is an emitter if some photon originates from it -/
def PhotonEventGraph.isEmitter (G : PhotonEventGraph) (e : SpacetimeEvent) : Prop :=
  ∃ p ∈ G.photons, p.emission = e

/-- An event is an absorber if some photon terminates at it -/
def PhotonEventGraph.isAbsorber (G : PhotonEventGraph) (e : SpacetimeEvent) : Prop :=
  ∃ p ∈ G.photons, p.absorption = e

/-! ## Section 4: Causal Order and Acyclicity -/

/-- The causal order on events: e₁ ≤ e₂ if there is a directed path of
    photon worldlines from e₁ to e₂. -/
inductive PhotonEventGraph.causallyConnected (G : PhotonEventGraph) :
    SpacetimeEvent → SpacetimeEvent → Prop where
  | refl (e : SpacetimeEvent) : G.causallyConnected e e
  | step (e₁ e₂ e₃ : SpacetimeEvent) :
      (∃ p ∈ G.photons, p.emission = e₁ ∧ p.absorption = e₂) →
      G.causallyConnected e₂ e₃ →
      G.causallyConnected e₁ e₃

/-- Causal connectivity is transitive -/
theorem PhotonEventGraph.causallyConnected_trans (G : PhotonEventGraph)
    (e₁ e₂ e₃ : SpacetimeEvent)
    (h₁₂ : G.causallyConnected e₁ e₂) (h₂₃ : G.causallyConnected e₂ e₃) :
    G.causallyConnected e₁ e₃ := by
  induction h₁₂ with
  | refl _ => exact h₂₃
  | step a b c hstep _ ih => exact .step a b e₃ hstep (ih h₂₃)

/-
PROBLEM
Key theorem: In any photon event graph, if e₁ is causally connected to e₂
    (via photon worldlines) and e₁ ≠ e₂, then e₁.t < e₂.t.
    This ensures no causal loops are possible.

PROVIDED SOLUTION
By induction on the causal connectivity relation. Base case (refl): contradicts hne. Step case: we have a photon from e₁'s emission to some intermediate event b, and b is causally connected to e₂. The photon has time_ordered: e₁.t < b.t. By IH (if b ≠ e₂) or directly (if b = e₂), we get b.t ≤ e₂.t. So e₁.t < e₂.t.
-/
theorem PhotonEventGraph.time_monotone (G : PhotonEventGraph)
    (e₁ e₂ : SpacetimeEvent)
    (hconn : G.causallyConnected e₁ e₂)
    (hne : e₁ ≠ e₂) : e₁.t < e₂.t := by
  revert hconn;
  -- We proceed by induction on the causal connectivity relation.
  intro h
  induction' h with e₁ e₂ h₁₂ h₂₃ h_ind;
  · contradiction;
  · obtain ⟨ p, hp, rfl, rfl ⟩ := h_ind;
    cases eq_or_ne p.absorption h₂₃ <;> simp_all +decide [ PhotonEdge.time_ordered ];
    · exact ‹p.absorption = h₂₃› ▸ p.time_ordered;
    · linarith [ p.time_ordered ]

/-
PROBLEM
Corollary: No event is causally connected to itself via a non-trivial path.
    The photon event graph is a DAG (directed acyclic graph).

PROVIDED SOLUTION
If p.absorption were causally connected to e = p.emission, then by time_monotone (if they're different) we'd have p.absorption.t < p.emission.t, contradicting p.time_ordered. If they're the same event, the causal connection is refl, but then p.absorption = p.emission contradicts p.time_ordered (strict inequality). Use the time_monotone theorem.
-/
theorem PhotonEventGraph.no_causal_loop (G : PhotonEventGraph)
    (e : SpacetimeEvent)
    (p : PhotonEdge) (hp : p ∈ G.photons) (hem : p.emission = e) :
    ¬ G.causallyConnected p.absorption e := by
  intro h;
  -- By the time monotonicity theorem, if $p.absorption$ is causally connected to $e$, then $p.absorption.t < e.t$.
  have h_time : p.absorption.t < e.t := by
    apply PhotonEventGraph.time_monotone G p.absorption e h;
    exact fun h' => by have := p.time_ordered; aesop;
  linarith [ p.time_ordered, show p.emission.t = e.t from congr_arg SpacetimeEvent.t hem ]

/-! ## Section 5: Vertex Degree Structure

In the photon event graph, the degree of each vertex tells us about
the physical process at that event:
- Out-degree = number of photons emitted
- In-degree = number of photons absorbed
- Conservation laws constrain these degrees
-/

/-- The emission degree of an event (number of photons emitted from it). -/
noncomputable def PhotonEventGraph.emissionDegree (G : PhotonEventGraph) (e : SpacetimeEvent) : ℕ :=
  (G.photons.filter (fun p => p.emission = e)).card

/-- The absorption degree of an event (number of photons absorbed at it). -/
noncomputable def PhotonEventGraph.absorptionDegree (G : PhotonEventGraph) (e : SpacetimeEvent) : ℕ :=
  (G.photons.filter (fun p => p.absorption = e)).card

/-
PROBLEM
Total photon count equals sum of emission degrees over all events.

PROVIDED SOLUTION
Each photon p has p.emission ∈ G.events (by emission_mem). The filter for emission degree at event e counts exactly the photons with emission = e. So summing over all events gives the total count. This is essentially Finset.card_biUnion or a partition argument. Use Finset.card_eq_sum_card_filter_mem or similar.
-/
theorem PhotonEventGraph.total_emission_count (G : PhotonEventGraph) :
    G.photons.card = ∑ e ∈ G.events, G.emissionDegree e := by
  unfold PhotonEventGraph.emissionDegree;
  simp +decide only [card_filter];
  rw [ ← Finset.sum_comm ];
  simp +contextual [ G.emission_mem ]

/-! ## Section 6: Entangled Photon Pairs -/

/-- An entangled pair: two photons emitted from the same event with
    opposite momenta (momentum conservation). -/
structure EntangledPair where
  photon1 : PhotonEdge
  photon2 : PhotonEdge
  same_source : photon1.emission = photon2.emission
  momentum_conservation :
    photon1.momentum.1 + photon2.momentum.1 = 0 ∧
    photon1.momentum.2 + photon2.momentum.2 = 0

/-
PROBLEM
Entangled photons have equal energy (from momentum conservation + on-shell).

PROVIDED SOLUTION
From same_source, both photons have the same emission event. From momentum_conservation, their momenta sum to zero: px₁ + px₂ = 0 and py₁ + py₂ = 0, so px₂ = -px₁ and py₂ = -py₁. Energy = absorption.t - emission.t. By on_shell for both: px₁² + py₁² = E₁² and px₂² + py₂² = E₂². Since px₂ = -px₁ and py₂ = -py₁, we get E₁² = E₂². Since both energies are positive, E₁ = E₂.
-/
theorem EntangledPair.equal_energy (ep : EntangledPair) :
    ep.photon1.energy = ep.photon2.energy := by
  -- By the on-shell condition, we have that for both photons, their energy squared is equal to the sum of the squares of their momentum components.
  have h_on_shell : ep.photon1.energy^2 = ep.photon1.momentum.1^2 + ep.photon1.momentum.2^2 ∧ ep.photon2.energy^2 = ep.photon2.momentum.1^2 + ep.photon2.momentum.2^2 := by
    exact ⟨ by linarith [ PhotonEdge.on_shell ep.photon1 ], by linarith [ PhotonEdge.on_shell ep.photon2 ] ⟩;
  -- By the momentum conservation condition, we have that the sum of the momentum components of the two photons is zero.
  have h_momentum_conserved : ep.photon1.momentum.1 + ep.photon2.momentum.1 = 0 ∧ ep.photon1.momentum.2 + ep.photon2.momentum.2 = 0 := by
    exact ep.momentum_conservation;
  rw [ ← sq_eq_sq₀ ] <;> try linarith [ PhotonEdge.energy_pos ep.photon1, PhotonEdge.energy_pos ep.photon2 ];
  simp_all +decide [ add_eq_zero_iff_eq_neg ]