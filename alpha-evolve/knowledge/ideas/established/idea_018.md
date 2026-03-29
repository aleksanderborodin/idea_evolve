---
type: idea
id: idea_018
name: "TTT-Discover: LLM-guided LP at test time"
lifecycle: established
confidence: 0.8
first_seen: generation_4
last_updated: generation_10
last_confirmed_gen: 10
supported_by: [gen004_research_1_sol01]
contradicted_by: []
related_ideas: [idea_016, idea_014, idea_006, idea_020]
cluster: cluster_003
tags: [TTT-Discover, LLM, LP, test-time-training, literature, established]
---

TTT-Discover (Yuksekgonul et al., Jan 2026) combines LLMs with LP at test time for
combinatorial optimization. Achieved C = 1.50286 on 30,000-element array — current best
known published result. Uses "LP with heuristic focusing on near-tight constraints."

**PROMOTED TO ESTABLISHED (gen 10 consistency review):**
- Confidence 0.75 -> 0.8 (above 0.7 threshold).
- The TTT-Discover 30k array is the foundation of ALL frontier scores since gen 4 (8
  consecutive generations). Every gen 10 solution derives from it (idea_014).
- Array has been improved to C = 1.5028628681165177 via coordinate descent (idea_019),
  confirming the quality of the starting point.
- Method validated by independent reproduction and citation in academic literature.
- Autoconvolution plateau structure (28 near-maximal positions within 1e-10 of max)
  well-characterized through gens 7-10 analysis.
