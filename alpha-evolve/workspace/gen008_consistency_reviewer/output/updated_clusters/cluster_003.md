---
type: cluster
id: cluster_003
name: "Published solutions and warm-start approaches"
member_ideas: [idea_014, idea_016, idea_018, idea_020]
best_score: 1.5028628685
best_solution: gen008_explore_1_sol01
status: active
last_updated: generation_8
---

Groups ideas related to leveraging published solutions and alternative algorithms
from the literature. This cluster IS the frontier — all scores below 1.505 come from here.

**Gen 8 consistency review update:**
- idea_018 (TTT-Discover) PROMOTED TO ESTABLISHED (confidence 0.8). Foundation of all
  frontier work since gen 4. Five generations of continuous refinement.
- idea_020 (LP refinement) remains DISPUTED at 0.2. Gen 8 explore_2 showed downsampling
  destroys solution structure (pattern_015). LP at intermediate N requires fresh
  optimization from scratch — not achievable in one session.
- Best score: **1.5028628685** (gen008_explore_1_sol01).

**Members:**
- idea_014 (warm-start from published solutions): ESTABLISHED, confidence 0.9.
- idea_016 (LP-guided memetic): ESTABLISHED, confidence 0.8.
- idea_018 (TTT-Discover LLM+LP): **ESTABLISHED** (promoted from active), confidence 0.8.
- idea_020 (LP-based refinement): DISPUTED, confidence 0.2. Blocked by plateau at N=30k;
  intermediate-N path requires fresh optimization (30-60 min compute).

**Priority experiments for gen 9:**
1. Full interleaved multi-order cycle (coord → triplet → quadruplet → repeat)
2. Quintuplet perturbation (5-element integral-preserving moves)
3. Near-optimal N=5000 solution from scratch (if budget allows: Adam+smooth-max → coord descent → LP test)
4. Vectorized batch trial evaluation for throughput improvement
