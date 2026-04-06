---
type: idea
id: idea_017
name: "Large-k Perturbation of Singer q=101 (k=5-25)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_3
last_updated: generation_4
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_exploit_1_sol01, gen004_experimentator_1]
related_ideas: [idea_012, idea_007, idea_008]
cluster: cluster_003
tags: [perturbation, singer-101, large-k, search, debunked]
---

Extend the perturbation approach (idea_012) to larger k values (5-25 removals) from the
Singer q=101 102-element set. Three strategies tested:
1. Remove top-k blockers (elements that block the most non-member candidates)
2. Remove bottom-k blockers (least useful elements)
3. Random k-element removals (hundreds of trials per k)

Generation 3 evidence: exploit_1/sol01 tested k = 5, 8, 10, 12, 15, 18, 20, 25 with all
three strategies. Total: ~4000+ trials across all k values. Result: **102** (no improvement).
Every trial returned exactly 102 or fewer elements.

**Generation 4 correction**: Minimum blockers = **43** (corrected from 45, experimentator_1
gen 4). Removing k < 43 elements cannot free even a single candidate. For k >= 25, the base
drops to 77 elements, and greedy recovery from 77 cannot reach 103. There is a "valley"
between k=1 (net zero) and k=43+ (base too small) where no improvement is possible.

**Verdict**: Debunked. Large-k perturbation is a dead end for Singer q=101. The 43-blocker
minimum creates an impassable barrier for all perturbation sizes. Combined with idea_012,
perturbation of Singer q=101 is proven futile for ALL k values.
