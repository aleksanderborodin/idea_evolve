---
type: idea
id: idea_018
name: "TTT-Discover: LLM-guided LP at test time"
lifecycle: active
confidence: 0.75
first_seen: generation_4
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen004_research_1_sol01]
contradicted_by: []
related_ideas: [idea_016, idea_014, idea_006]
cluster: cluster_003
tags: [TTT-Discover, LLM, LP, test-time-training, literature]
---

TTT-Discover (Yuksekgonul et al., Jan 2026, arXiv:2601.16175) is a method that uses
LLMs combined with LP (linear programming) at test time to solve mathematical
optimization problems. Applied to the First Autocorrelation Inequality, it achieved
C = 1.50286 with a 30,000-element array — the current best known result.

**Key characteristics:**
- The method uses "LP with heuristic focusing on near-tight constraints" (per the
  solution header). This is conceptually similar to AlphaEvolve's LP-guided approach
  (idea_016) but uses LLM-generated heuristics to focus the LP.
- The resulting 30k-element array has qualitatively different structure from both
  our gradient-descent solutions AND the AlphaEvolve 1319-element array:
  - ~100 elements of moderate values (0.11-0.13)
  - Sharp transition to near-zero gap
  - Complex multi-peaked structure with near-zero valleys
  - The density pattern is much finer than the 1319-element AlphaEvolve solution

**Evidence:**
- gen004_research_1/sol01: Verbatim retrieval. C = 1.502863, verified.
  Beats the AlphaEvolve 1319-element solution (C=1.5032) by 0.00030.

**Implication:** LP-based methods at high resolution (N=30000) can find solutions
unreachable by gradient descent at any resolution we've tested. The N=30000 resolution
itself may be important — fine structure matters at this score level.
