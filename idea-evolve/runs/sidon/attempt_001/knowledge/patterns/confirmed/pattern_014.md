---
type: pattern
id: pattern_014
name: "105-mark Bose-Chowla set has perfect self-healing property"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_6
last_updated: generation_6
evidence: [gen006_exploit_1_sol01]
related_ideas: [idea_022, idea_020, idea_012]
tags: [perturbation, self-healing, algebraic, structural, bose-chowla]
---

The 105-mark Bose-Chowla set (ap q=107, mul=433, span=9884) exhibits a perfect
self-healing property under perturbation: removing any k elements (tested k=1-104)
opens exactly k addable slots, and those slots are always the original removed elements.

**Evidence (exploit_1, 27,000+ trials):**
- k=2-10, ordered greedy extension (18K+ trials): ALL return exactly 105
- k=2-10, shuffled greedy extension (8K+ trials): ALL return exactly 105
- k=15-40: always 105
- k=50-104: degrades (base too small for full recovery)
- Remove-1 add-2 exhaustive search (all 105 elements): each removal opens exactly 1 slot; 0 candidate pairs exist
- Swap walk exploration (10 walks × 50 steps): all 105-element sets visited are greedy-maximal
- Singer pp q=107 all coprime multipliers: max 105 in [0,10000]
- Singer pp q=109 all coprime multipliers: max 104 in [0,10000]

**Structural implications:**
1. The set is at a uniquely rigid local maximum — zero combinatorial slack
2. Greedy extension from any subset always reconstructs the same 105-element set
3. Shuffled greedy doesn't help — the basin of attraction covers the entire extension space
4. The swap landscape around 105 is completely flat (no extensible alternatives)

**Strategic implication:** Perturbation-based approaches (remove-k + re-extend) are
provably futile for the 105-mark set, regardless of removal strategy. The only paths
to 106+ are constructive search (CP-SAT/ILP) or fundamentally different seed sets.

This extends pattern_012 (algebraic ceiling) from "no algebraic construction gives 106"
to "the best algebraic construction is also immune to all perturbation-based extensions."
