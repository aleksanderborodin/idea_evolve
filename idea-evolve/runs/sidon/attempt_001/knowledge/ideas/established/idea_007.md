---
type: idea
id: idea_007
name: "Singer Set Perturbation (Remove-k, Re-extend)"
lifecycle: established
confidence: 0.9
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen002_exploit_2_sol01]
contradicted_by: []
related_ideas: [idea_002, idea_006, idea_008, idea_010]
cluster: cluster_003
tags: [hybrid, perturbation, singer, local-search]
---

Starting from the 98-element Singer set (idea_006), remove 1-3 elements to free up their
pairwise differences, then greedily extend the set using candidates from the full range
{0, ..., 10000} (including elements above 9506 not reachable by Singer alone).

**Generation 1 evidence**: explore_1/sol02-04 all achieved fitness=99 using this approach.

**Generation 2 evidence**: exploit_2/sol01 applied SA from the 99-element Singer q=97 perturbation
seed. After 114 seconds and ~500K SA iterations, result remained 99. This confirms the 99-element
basin around Singer q=97 perturbation is a robust local optimum that SA cannot escape.

**Superseded**: With Singer q=101 truncation (idea_008) achieving 102, the Singer q=97 perturbation
approach is no longer the frontier. Its peak of 99 is 3 elements below the new best. However,
the perturbation methodology remains valuable — applying it to the q=101 base (102 elements)
is the logical next step for pushing beyond 102.
