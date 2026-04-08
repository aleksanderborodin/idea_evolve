---
type: pattern
id: pattern_018
name: "Ruzsa-Lindström and ET converge to same 75-ceiling basin"
lifecycle: confirmed
confidence: 0.90
first_seen: generation_7
last_updated: generation_7
evidence: [gen007_explore_1_sol01, gen007_explore_1_sol03]
related_ideas: [idea_025, idea_011, idea_009]
tags: [basin, convergence, ruzsa, erdos-turan, 75-ceiling]
---

Two structurally different algebraic constructions — quadratic Erdos-Turan ({2ip + i² mod p})
and exponential Ruzsa-Lindström ({x*2p + gˣ mod p}) — converge to the same 75-element
ceiling under VLNS/local search for p=71.

**Gen 7 evidence (explore_1):**
- Ruzsa p=71 (71 elements) + greedy + VLNS → 74-75 (sol01: 74, sol03: 75)
- Ruzsa p=61 (61 elements) + greedy + VLNS → 70 (within sol03)
- Previous ET(71) + greedy + 1-opt/LNS → 75 (gens 2, 6)

The 75 ceiling is not specific to any seed type — it appears to be a structural barrier
in the Sidon set landscape for {0,...,10000} at the interface between algebraic (~70-element)
seeds and the search-based extension frontier. All local search methods (1-opt, 2-opt,
LNS, VLNS with k=3-25) converge to the same basin.

**Additional finding:** The naive Ruzsa formula {x*p + gˣ mod p} is NOT a valid Sidon set
in integer arithmetic (264 violations for p=71). Only the 2p-scaled version works. This
corrects idea_025's original claim.

**Implication:** Trying more algebraic seed types (e.g., different constructions for p≈70)
is unlikely to break the 75 barrier. The gap to 105 is structural and requires fundamentally
different methods (full CP-SAT, or non-local optimization).
