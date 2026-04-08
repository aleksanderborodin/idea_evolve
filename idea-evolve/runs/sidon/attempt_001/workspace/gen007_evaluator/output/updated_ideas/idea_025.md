---
id: idea_025
type: idea
name: "Ruzsa-Lindström Construction as Search Seed"
lifecycle: disputed
confidence: 0.15
first_seen: generation_6
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_001
supported_by: [gen007_explore_1_sol01, gen007_explore_1_sol03]
contradicted_by: [gen007_explore_1_sol03]
related_ideas: [idea_004, idea_006, idea_010, idea_022, idea_011]
tags: [algebraic, ruzsa, construction, seed, tested, same-basin]
---

Ruzsa-Lindström construction: for prime p, use primitive root g mod p and define
S = {x*2p + g^x mod p : x in {0,...,p-1}}. The **2p scaling** is essential — the naive
formula {x*p + g^x mod p} produces sets with 264 violations for p=71 due to carry-induced
sum collisions in integer arithmetic. Only the 2p-scaled version is a valid Sidon set.

**Gen 7 — FIRST TEST (explore_1):**

| Starting seed | Base size | After greedy | After VLNS | Time |
|---------------|-----------|-------------|------------|------|
| Ruzsa p=71 (2p-scaled) | 71 | 73 | **74** (sol01) | 90s |
| Ruzsa p=61 (2p-scaled) | 61 | 68 | 70 (within sol03) | 30s |
| Ruzsa p=71 (2p-scaled) | 71 | 73 | **75** (sol03) | 30s |
| Random greedy (best of 20) | 62 | 62 | **65** (sol02) | 110s |

**Critical finding: The Ruzsa basin ceiling is 75 — SAME as ET(71).**

The hypothesis that Ruzsa seeds would reach "different basins of attraction" under local
search is **refuted**. Both quadratic ET ({2ip + i²mod p}) and exponential Ruzsa
({x*2p + g^x mod p}) with the same p converge to the identical 75-element ceiling under VLNS.
This suggests the 75-ceiling is a structural barrier in the non-algebraic search landscape,
not specific to any particular algebraic seed.

**Corrections to gen 6 description:**
- Original idea_025 claimed {x*p + g^x mod p} "produces a p-element Sidon set in {0,...,p²-1}".
  This is WRONG for integer arithmetic. The formula may be correct in Z_{p²} (cyclic group)
  but fails in the integers due to carries. The 2p-scaled version is the correct implementation.
- Expected raw score of "~97 for p=97" is also incorrect — the 2p scaling pushes max value
  to 2p²-p ≈ 18,721 for p=97, which exceeds N=10000. Only p≤71 fits within range.

**Lifecycle downgraded to disputed** — the construction works but the "different basin"
hypothesis that motivated it is refuted. Raw score (75) matches the existing ET ceiling
and is 30 elements below the frontier (105). No further value as a standalone idea unless
combined with CP-SAT VLNS from Ruzsa seeds (untested, but VLNS from BEST_105 subsets is
already proven futile).
