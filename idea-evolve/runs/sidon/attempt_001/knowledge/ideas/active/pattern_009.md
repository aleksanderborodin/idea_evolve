---
type: pattern
id: pattern_009
name: "Singer q=101 perturbation is provably futile for all k"
lifecycle: active
confidence: 0.9
first_seen: generation_3
last_updated: generation_4
evidence: [gen003_exploit_1_sol01, gen003_experimentator_1, gen004_experimentator_1]
related_ideas: [idea_012, idea_017, idea_008]
tags: [singer-101, perturbation, dead-end, proof]
---

Combined evidence from gen 2 (small k=1-5), gen 3 (large k=5-25, plus blocker analysis),
and gen 4 (corrected blocker count) proves that perturbation of the Singer q=101 set
cannot exceed 102 for any value of k:

- **k < 43**: The minimum blocker count is **43** (at c=9931). Removing fewer than 43
  elements cannot free even a single new candidate. (Corrected from gen 3's claim of 45;
  experimentator_1 gen 4 found the true minimum is 43.)
- **k = 5-25**: 4000+ random and strategic trials, all return <= 102 (exploit_1 gen 3).
- **k >= 43**: The base drops to <=59 elements. No greedy extension from 59 elements has
  ever reached 102, let alone 103.

**Gen 4 addition**: Experimentator_1 also showed that removing all 43 blockers of c=9931
leaves only 59 elements. Pair-trade analysis (3828 pairs) found net gain 0 universally.
2-element trades are structurally impossible for this set.

This closes the entire perturbation research direction for Singer q=101.
