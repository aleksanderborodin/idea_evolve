---
id: fact_004
type: fact
name: "Violation Policy — Sentinel Scoring"
confidence: 1.0
first_seen: generation_0
last_updated: generation_4
verified: true
source: "validate.py behavior, confirmed by CLAUDE.md sentinel policy, all gen 1-4 solutions"
tags: [validation, scoring, policy]
---

If a solution has ANY violations (repeated pairwise sums), validate.py returns
`is_valid: 0` and the fitness is set to the sentinel value of **0**. There is
NO partial credit, NO subset extraction, and NO rewarding near-misses. Only
fully valid Sidon sets receive a real fitness score.

**WARNING**: Previous version of this fact (in facts/ directory, generation 0) incorrectly
stated that "the validator extracts the largest valid Sidon subset using a greedy algorithm."
This was WRONG. The validator does NOT extract subsets — any violation results in fitness=0.
Agents must ensure zero violations before submitting.
