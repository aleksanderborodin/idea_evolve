---
id: fact_004
type: fact
name: "Violation Policy — Sentinel Scoring"
confidence: 1.0
first_seen: generation_0
last_confirmed_gen: 6
verified: true
source: evaluate.py + validate.py source code, metrics.yaml sentinel_value
tags: [scoring, validation, sentinel]
---

If a solution has ANY violations (repeated pairwise sums), the fitness score is
set to **0** (sentinel value from metrics.yaml). There is NO partial credit, NO
subset extraction, and NO tolerance for near-valid solutions. Only fully valid
Sidon sets receive a real fitness score equal to the set size.

**Correction history:** Original fact incorrectly stated "the validator extracts
the largest valid Sidon subset using a greedy algorithm." This was WRONG. The
system uses strict sentinel scoring as defined in metrics.yaml. Corrected in
gen 2 consistency review.

**NOTE**: This file replaces the STALE version in facts/fact_004.md which still
contains the incorrect subset extraction claim. The facts/ version must be
overwritten with this corrected content.
