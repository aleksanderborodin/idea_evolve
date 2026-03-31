---
type: pattern
id: pattern_004
name: "Incremental optimization trajectory: each fix builds on previous"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [explore_1/sol01 through explore_1/sol10]
related_ideas: [idea_001, idea_004, idea_007, idea_010, idea_011, idea_012]
tags: [optimization-process, incremental, compounding]
---

The explore_1 agent demonstrated a highly effective incremental optimization
trajectory across 10 solutions:

1. AVX-512 popcount (sol01: 654 µs) — basic port from AVX2
2. + vpternlogd + NC=256 (sol02: 400 µs) — fix truth tables, tune tiling
3. 8-row kernel attempt (sol03: 493 µs) — regression, abandoned
4. + direct store (sol04: 381 µs) — eliminate read-for-ownership
5. Aligned temp buffer + streaming (sol05: 964 µs) — regression, memcpy too expensive
6. NC=512 + direct store (sol06: 465 µs) — regression, NC=512 consistently worse
7. + vectorized pack_B (sol07: 306 µs) — major win
8. + remove memset (sol08: 178 µs) — massive win
9. + thread_local buffers (sol09: 171 µs) — slight improvement
10. + stack buffers (sol10: 148 µs) — best result

Each successful optimization compounds with the previous ones. Failed experiments
(sol03, sol05, sol06) provided negative knowledge that guided subsequent attempts.
The pattern of "try → measure → keep or revert → try next" is the ideal workflow.
