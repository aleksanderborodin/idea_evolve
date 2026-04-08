---
name: "Ruzsa-Lindstrom Construction as Search Seed"
type: idea
lifecycle: debunked
confidence: 0.05
first_seen: generation_6
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_001
supported_by:
  - gen007_explore_1_sol01
  - gen007_explore_1_sol03
contradicted_by:
  - gen007_explore_1_sol03
related_ideas:
  - idea_004
  - idea_006
  - idea_010
  - idea_022
  - idea_011
tags:
  - algebraic
  - ruzsa
  - construction
  - seed
  - debunked
  - same-basin
---

Ruzsa-Lindstrom: for prime p, S = {x*2p + g^x mod p : x in {0,...,p-1}} where g is primitive root.

**Critical correction:** Naive formula {x*p + g^x mod p} does NOT produce valid Sidon set in integers (264 violations for p=71). Only 2p-scaled version valid (fact_005). Max prime fitting N=10000 is p=71 (2p scaling pushes span to ~2p^2).

**Gen 7 test results:**
- Ruzsa p=71 (71 base) -> 73 greedy -> 74 VLNS (sol01, 90s)
- Ruzsa p=61 (61 base) -> 68 greedy -> 70 VLNS
- Ruzsa p=71 -> 75 VLNS (sol03, 30s)
- Random greedy -> 65

**Debunked gen 7:** "Different basin" hypothesis definitively refuted. Both quadratic ET(71) and exponential Ruzsa(71) converge to identical 75-element ceiling under VLNS (pattern_018). The 75-ceiling is a structural barrier in the Sidon set landscape, not seed-specific. 30-element gap to frontier (105). No remaining value unless combined with fundamentally new search methods.
