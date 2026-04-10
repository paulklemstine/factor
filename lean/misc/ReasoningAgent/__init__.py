"""
Geodesic Reasoning Agent — State-of-the-art collaborative reasoning AI
built on formally verified mathematical foundations.
"""

from .geodesic_reasoning_agent import (
    GeodesicReasoningAgent,
    SelfImprovingAgent,
    TreeOfThoughts,
    ReasoningResult,
    ReasoningStep,
    ReasoningStrategy,
    ReasoningContext,
    Oracle,
    tropical_max,
    bayesian_update,
    diversity_bonus,
    contraction_convergence,
    geodesic_distance,
    fixed_point_iterate,
    koopman_lift,
)

__all__ = [
    "GeodesicReasoningAgent",
    "SelfImprovingAgent",
    "TreeOfThoughts",
    "ReasoningResult",
    "ReasoningStep",
    "ReasoningStrategy",
    "ReasoningContext",
    "Oracle",
    "tropical_max",
    "bayesian_update",
    "diversity_bonus",
    "contraction_convergence",
    "geodesic_distance",
    "fixed_point_iterate",
    "koopman_lift",
]
