---
type: cluster
id: cluster_003
name: "Published solutions and warm-start approaches"
member_ideas: [idea_014, idea_016, idea_018, idea_020]
best_score: 1.5028628677925082
best_solution: gen011_explore_1_sol01
status: active
last_updated: generation_11
---

Groups ideas related to leveraging published solutions and alternative algorithms
from the literature. This cluster IS the frontier — all scores below 1.505 come from here.

**Gen 11 update:**
- idea_014 confirmed again — both scored solutions use TTT-Discover 30k derivatives.
  19 supporting solutions across 9 generations, 0 contradictions.
- Best score updated: **1.5028628677925082** (gen011_explore_1_sol01).
- Critical finding: deadline-based entrypoints are non-reproducible (~6e-11 variance).
  Must bake arrays as numpy literals (pattern_028).
- idea_020 (LP refinement) remains DEBUNKED. Not retested.

**Members:**
- idea_014 (warm-start from published solutions): ESTABLISHED, confidence 0.95.
- idea_016 (LP-guided memetic): ESTABLISHED, confidence 0.8.
- idea_018 (TTT-Discover LLM+LP): ESTABLISHED, confidence 0.8.
- idea_020 (LP-based refinement): DEBUNKED, confidence 0.05.
