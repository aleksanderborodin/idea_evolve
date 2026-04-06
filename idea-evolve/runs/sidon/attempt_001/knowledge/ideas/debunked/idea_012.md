---
type: idea
id: idea_012
name: "Singer q=101 Perturbation (Remove-k, Re-extend)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_2
last_updated: generation_4
last_confirmed_gen: 2
supported_by: []
contradicted_by: [gen002_exploit_1_sol01, gen002_exploit_2_sol04, gen003_exploit_1_sol01, gen003_experimentator_1, gen004_experimentator_1]
related_ideas: [idea_007, idea_008, idea_006, idea_017]
cluster: cluster_003
tags: [hybrid, perturbation, singer-101, debunked, dead-end]
---

Apply the perturbation strategy (idea_007) to the Singer q=101 base of 102 elements. Remove
k elements, then greedily re-extend.

**Generation 2 evidence**: Small-k (1-5) tested exhaustively. Net zero every time.

**Generation 3 evidence**: exploit_1 tested large-k (5-25) with strategic and random removals
(4000+ trials). All returned <=102. Experimentator_1 proved minimum blocker count.

**Generation 4 correction**: Experimentator_1 found the true minimum blocker count is **43**
(at c=9931), not 45 as reported in gen 3. For k < 43, perturbation is provably futile —
cannot free even a single new candidate. For k >= 43, the base drops to <=59 elements and
greedy recovery cannot reach 103.

**Verdict**: Debunked. Perturbation of Singer q=101 is proven ineffective across the full
spectrum of k values. The 43-blocker minimum creates a structural barrier that no
perturbation size can overcome.
