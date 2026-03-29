---
type: idea
id: idea_023
name: "Minimax multi-element perturbation (gradient at all plateau positions)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_9
last_updated: generation_10
last_confirmed_gen: 9
supported_by: []
contradicted_by: [gen010_explore_1_sol01]
related_ideas: [idea_021, idea_022, idea_019]
cluster: cluster_001
tags: [minimax, perturbation, plateau, gradient, LP, multi-peak, debunked]
---

Instead of computing the gradient at a single autoconvolution peak (current argmax),
compute gradients at ALL near-peak positions and find a perturbation direction that
reduces the maximum across all of them.

**DEBUNKED — Gen 10 provides definitive test.**

**Gen 10 evidence (explore_1 — FULL IMPLEMENTATION):**
- Implemented complete LP-based minimax approach with K=28 plateau positions (within 1e-10 of max)
- Triplet minimax: 47,233 trials, ~215 trials/s. **Every trial returned t* ≥ 0 (LP infeasible for improvement).** 0 improvements.
- Quadruplet minimax: 21,217 trials. **Same result: 0 improvements.** Every LP solution has t* ≥ 0.
- Total: 68,450 trials across triplets and quadruplets. Zero improvements.

**Why it fails:** With K=28 gradient vectors in 2D (triplets) or 3D (quadruplets), the
origin is contained in the convex hull of the gradient directions. This means no
integral-preserving perturbation can simultaneously reduce ALL plateau positions.
The solution is **locally minimax-optimal** with respect to integral-preserving moves.

**Theoretical interpretation:** The gradient vectors {h_p} for p in 1..K span enough
of the perturbation space that no descent direction exists. This is not an engineering
failure — it reflects genuine local optimality in the minimax sense.

**Distinction from CD:** Coordinate descent (which DOES still find improvements) works
through a fundamentally different mechanism: it changes the integral (non-integral-preserving),
optimizing C = max_ac / integral² by adjusting the denominator. Minimax LP only considers
integral-preserving moves that reduce the numerator.

Confidence lowered to 0.05. This approach should not be retried.
