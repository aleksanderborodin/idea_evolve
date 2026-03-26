---
type: cluster
id: cluster_003
name: "Published solutions and warm-start approaches"
member_ideas: [idea_014, idea_016, idea_018]
best_score: 1.5029
best_solution: gen004_research_1_sol01
status: active
last_updated: generation_4
---

Groups ideas related to leveraging published solutions and alternative algorithms
from the literature.

**Gen 4 update — MAJOR PROGRESS:**
- idea_018 (TTT-Discover) ADDED: LLM-guided LP method, produced new best C=1.50286.
- idea_014 (warm-start) PROMOTED to established: only idea producing sub-1.505 scores.
- Best score improved: 1.5032 → **1.50286** (TTT-Discover 30k array).

**Members:**
- idea_014 (warm-start from published solutions): ESTABLISHED. AlphaEvolve (1.5032)
  and TTT-Discover (1.50286) arrays retrieved. Smooth-max Adam cannot improve them
  (pattern_007).
- idea_016 (LP-guided memetic, AlphaEvolve): Active. Not implemented.
- idea_018 (TTT-Discover LLM+LP): Active. New SOTA method. Not implemented.

**This cluster IS the frontier.** All scores below 1.505 come from this cluster.
The gradient pipeline (clusters 1+2) cannot break below ~1.509.

**Priority experiments for gen 5:**
1. Projected gradient descent (idea_017) on the TTT-Discover 30k array — may find
   improvements that smooth-max cannot
2. Coordinate descent on 30k array — simple, avoids parameterization issues
3. Retrieve additional published arrays (Cell 46 N=600, Cell 49-58)
4. Warm-start from TTT-Discover 30k array with ultra-gentle optimization (lr=1e-6)
