---
name: "Singer Set Perturbation (Remove-k, Re-extend)"
type: idea
lifecycle: archived
confidence: 0.2
first_seen: generation_1
last_updated: generation_7
last_confirmed_gen: 2
cluster: cluster_003
supported_by:
  - gen001_explore_1_sol02
  - gen001_explore_1_sol03
  - gen001_explore_1_sol04
  - gen002_exploit_2_sol01
contradicted_by: []
related_ideas:
  - idea_002
  - idea_006
  - idea_008
  - idea_010
tags:
  - hybrid
  - perturbation
  - singer
  - local-search
  - archived
---

Remove 1-3 elements from Singer set to free differences, then greedily extend.

**Gen 1-2 results:** Singer q=97 (98 base) -> 99 via perturbation. SA from 99-element seed (114s, ~500K iterations) -> remained 99. 99-element basin is robust local optimum.

**Superseded:** Singer q=101 truncation (idea_008) achieves 102 (+3 over perturbation best). Bose-Chowla q=107 achieves 105 (+6). All perturbation approaches proven futile — Singer q=101 has 43-blocker minimum (pattern_009), Bose-Chowla has perfect self-healing (pattern_014). Cluster_003 exhausted.

**Archived gen 7:** 5 generations stale (last confirmed gen 2). Superseded by direct algebraic constructions. Cluster_003 exhausted with all members debunked. Perturbation methodology has no remaining application — self-healing property (pattern_014, pattern_017) closes this direction permanently.
