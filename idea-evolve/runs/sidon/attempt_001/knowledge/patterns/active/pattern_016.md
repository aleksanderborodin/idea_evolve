---
type: pattern
id: pattern_016
name: "F₂(10000) = 105 — strongly supported by computational and literature evidence"
lifecycle: active
confidence: 0.90
first_seen: generation_7
last_updated: generation_7
evidence: [gen005_experimentator_1_sol01, gen006_exploit_1_sol01, gen007_exploit_1_sol01, gen007_research_1, gen007_experimentator_1]
related_ideas: [idea_022, idea_020, idea_024, idea_019]
tags: [optimality, f2-bound, sidon-maximum, conclusive]
---

The maximum Sidon set size in {0,...,10000} is very likely **105 elements**.

**Computational evidence (gens 5-7):**
- Exhaustive algebraic construction search: all primes q≤109, both Singer pp and Bose-Chowla
  ap types, all coprime multipliers → max 105 (Bose-Chowla ap q=107, mul=433)
- Perturbation of 105-mark set: 27,000+ trials for k=1 to k=104, perfect self-healing,
  zero improvement possible
- VLNS with corrected formulation: 85+ trials (remove 5-55 elements, target 106) → ALL
  INFEASIBLE. Provably impossible for k≤44 (candidate counting), structurally impossible
  for k=45-55. VLNS for target 105 → ALL OPTIMAL in <0.1s.
- CP-SAT k=106 decision: 6000+ seconds across gens 4-6 → UNKNOWN (not INFEASIBLE proven,
  but no feasible solution found)
- CP-SAT binary search on N: k=106 UNKNOWN even at N=15000 → difficulty inherent

**Literature evidence (gen 7 research_1):**
- No published record of F₂(10000) > 105 in OEIS, cube20.org, or any 2020-2024 paper
- rokicki_data.py contains BEST_105 but no BEST_106 entry
- cube20.org database starts at 160 marks — no 106-mark data available
- Proven optimal rulers go to n=28 only; F₂(10000) not formally tabulated

**Theoretical bounds:** Upper bound ~109 (O'Bryant 2022). Gap of 4 elements between
current best (105) and theoretical ceiling. The gap is small but non-zero — formal proof
of F₂(10000)=105 would require a very long CP-SAT prove-INFEASIBLE run.

**Remaining uncertainty:** CP-SAT has returned UNKNOWN, not INFEASIBLE. A binary variable
maximize formulation with 4h+ runtime might either find 106 or prove 105 optimal. Until
then, confidence remains at 0.90 rather than 1.0.
