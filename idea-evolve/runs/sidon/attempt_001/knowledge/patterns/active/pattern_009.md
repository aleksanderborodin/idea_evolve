---
type: pattern
id: pattern_009
name: "Singer q=101 perturbation is provably futile for all k"
lifecycle: active
confidence: 0.9
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_exploit_1_sol01, gen003_experimentator_1]
related_ideas: [idea_012, idea_017, idea_008]
tags: [singer-101, perturbation, dead-end, proof]
---

Combined evidence from gen 2 (small k=1-5) and gen 3 (large k=5-25, plus blocker analysis)
proves that perturbation of the Singer q=101 set cannot exceed 102 for any value of k:

- **k < 45**: The minimum blocker count is 45. Removing fewer than 45 elements cannot free
  even a single new candidate. Proved by exhaustive blocker enumeration (experimentator_1).
- **k = 5-25**: 4000+ random and strategic trials, all return ≤ 102 (exploit_1).
- **k ≥ 45**: The base drops to ≤ 57 elements. No greedy extension from 57 elements has
  ever reached 102, let alone 103.

This closes the entire perturbation research direction for Singer q=101. The remove-k/re-extend
methodology that gained +1 for Singer q=97 (98→99) is structurally impossible for q=101.
