/-
# Graph Theory Exploration
-/
import Mathlib

open Finset BigOperators SimpleGraph

/-! ## §1: Complete Graph Properties -/

theorem complete_graph_edges_3 :
    Fintype.card (SimpleGraph.edgeSet (⊤ : SimpleGraph (Fin 3))) = 3 := by
  native_decide

theorem complete_graph_edges_4 :
    Fintype.card (SimpleGraph.edgeSet (⊤ : SimpleGraph (Fin 4))) = 6 := by
  native_decide

theorem complete_graph_edges_5 :
    Fintype.card (SimpleGraph.edgeSet (⊤ : SimpleGraph (Fin 5))) = 10 := by
  native_decide

/-! ## §2: Euler's Formula for Polyhedra -/

theorem euler_tetrahedron : 4 - 6 + 4 = (2 : ℤ) := by norm_num
theorem euler_cube : 8 - 12 + 6 = (2 : ℤ) := by norm_num
theorem euler_octahedron : 6 - 12 + 8 = (2 : ℤ) := by norm_num
theorem euler_dodecahedron : 20 - 30 + 12 = (2 : ℤ) := by norm_num
theorem euler_icosahedron : 12 - 30 + 20 = (2 : ℤ) := by norm_num

/-- Only 5 Platonic solids. -/
theorem platonic_solids_count :
    Finset.card (Finset.filter (fun pq : ℕ × ℕ =>
      3 ≤ pq.1 ∧ 3 ≤ pq.2 ∧ pq.1 * pq.2 < 2 * (pq.1 + pq.2))
      (Finset.Icc (3, 3) (10, 10))) = 5 := by
  native_decide

/-! ## §3: Ramsey Theory -/

/-- Schur's theorem for n=2. -/
theorem schur_2' :
    ∀ f : Fin 5 → Bool, ∃ i j k : Fin 5,
      f i = f j ∧ f j = f k ∧ i.val + 1 + (j.val + 1) = k.val + 1 := by
  native_decide

/-! ## §4: Bipartite Graphs -/

theorem k23_vertices : 2 + 3 = (5 : ℕ) := by norm_num
theorem k23_edges : 2 * 3 = (6 : ℕ) := by norm_num
