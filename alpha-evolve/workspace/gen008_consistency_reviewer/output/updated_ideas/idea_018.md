---
type: idea
id: idea_018
name: "TTT-Discover: LLM-guided LP at test time"
lifecycle: established
confidence: 0.8
first_seen: generation_4
last_updated: generation_8
last_confirmed_gen: 8
supported_by: [gen004_research_1_sol01, gen005_exploit_2_sol01, gen006_exploit_1_sol01, gen007_explore_1_sol01, gen008_explore_1_sol01]
contradicted_by: []
related_ideas: [idea_016, idea_014, idea_006, idea_020]
cluster: cluster_003
tags: [TTT-Discover, LLM, LP, test-time-training, literature, established]
---

TTT-Discover (Yuksekgonul et al., Jan 2026, arXiv:2601.16175) is a method that uses
LLMs combined with LP at test time to solve mathematical optimization problems. Applied
to the First Autocorrelation Inequality, it achieved C = 1.50286 with a 30,000-element
array — the current best known published result.

**Key characteristics:**
- Uses "LP with heuristic focusing on near-tight constraints."
- The resulting 30k-element array has ~100 elements of moderate values (0.11-0.13),
  sharp transition to near-zero gap, complex multi-peaked structure with near-zero valleys.

**PROMOTED TO ESTABLISHED (gen 8 consistency review):**
- The TTT-Discover 30k array is the foundation of ALL frontier work since gen 4.
- Every gen 5-8 improvement (coord descent, triplets, quadruplets) starts from this array.
- Five generations of continuous refinement have improved it from C=1.502862898 to
  C=1.502862868 — a cumulative delta of -3.0e-8.
- The array's autoconvolution plateau structure (~6500 near-max points at tight@1e-7,
  pattern_013) is well-characterized.
- Confidence raised to 0.8 (from 0.75) based on sustained centrality to pipeline.
- supported_by expanded to include all solutions that used this array as their starting point.

**Evidence:**
- gen004_research_1/sol01: Verbatim retrieval. C = 1.502863, verified.
- gen005-gen008: All frontier improvements derive from coord descent, triplet, and
  quadruplet perturbation applied to this array.
