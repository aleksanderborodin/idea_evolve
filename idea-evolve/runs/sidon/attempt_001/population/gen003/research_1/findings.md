# Research Findings — Best Known Sidon Set Sizes and Construction Methods

## Summary

This report answers the single most important unresolved question for this project: **what is the best known Sidon set size for N=10000?** After extensive literature search across arXiv, OEIS, MathWorld, and related computational databases, the answer is: **102 elements (Singer q=101) is the best known construction, and no published source reports a Sidon set with >102 elements in {0,...,10000}**. The exact value of F(10000) is unknown and lies between 102 and ~109. Our current score of 102 matches the standard algebraic reference construction.

---

## Finding 1: F(10000) is Unknown — 102 is the Best Published Construction

**Relevance**: All agents planning strategies for 103+

**Detail**: No published paper, computational database, or OEIS sequence contains an exact value for F(10000) = maximum Sidon set size in {0,...,10000}. The literature has:

- **OEIS A143824**: "Maximum size of a Sidon subset of {1,...,n}" — this is exactly what we want, but the b-file only covers n=0..500. At n=500, the value is 26. The sequence does not extend to n=10000.
- **Singer q=101 construction**: Gives 102 elements in Z/(10303)Z ≅ a set in {0,...,10302}. With optimal cyclic shift, all 102 fit in {0,...,10000}. This is the standard reference result.
- **Upper bound** (Carter, Hunter, O'Bryant 2023, arXiv:2310.20032): F(N) ≤ √N + 0.98183·N^{1/4} + O(1). For N=10000: F(10000) ≤ 100 + 0.98183·10 + O(1) ≈ **109.8**.

**Key implication**: The gap F(10000) ∈ [102, 109] is **an open problem**. Our score of 102 IS the current state-of-the-art for this specific N. There is no "secret known construction" we are missing. Reaching 103+ is genuinely a research frontier.

**Actionable implication**: Do not assume a published 103+ construction exists that we haven't implemented. The path forward requires genuinely novel approaches, not missed literature.

---

## Finding 2: OEIS A143824 Shows Optimal Sidon Sets Beat Singer for Small N

**Relevance**: exploit agents, hybrid/perturbation strategies

**Detail**: The OEIS A143824 b-file (n=0..500) shows exact maximum Sidon set sizes. These values are larger than what the Singer construction gives for those ranges:

| n | F(n) [exact, OEIS] | Singer bound (best q≤√n) | Ratio to √n |
|---|---|---|---|
| 100 | **12** | ~10 (q=9, size=10 in {0..90}) | 1.20 |
| 200 | **17** | ~13 (q=13, size=14 in {0..182}) | 1.20 |
| 300 | **20** | ~15 (q=16, size=17 in {0..272}) | 1.155 |
| 400 | **23** | ~18 (q=19, size=20 in {0..380}) | 1.15 |
| 500 | **26** | ~20 (q=22≈22, not prime; q=23: size=24 in {0..552}) | 1.16 |

The ratio F(n)/√n ≈ **1.15-1.20** consistently, which means the true optimal for n=10000 could be as high as **115-120** if this ratio holds. But the upper bound of ~109 is tighter. The ratio converges to 1 as n→∞ (Singer construction is asymptotically optimal), but for finite n, better sets exist.

**What achieves these optimal values for small n?** The OEIS doesn't document the explicit constructions for n=100..500. These were likely found by exhaustive search (feasible for small n). For n=10000, exhaustive search is computationally infeasible.

**Actionable implication**: The optimal set for N=10000 exists and has size between 102 and 109. Since the OEIS ratio pattern suggests ~115-120 might be achievable (if small-n patterns hold), but the upper bound says ≤109, the true optimal is likely 103-109. Hitting even 103 would be a significant new result.

---

## Finding 3: No Computational Sidon Database Extends to N=10000

**Relevance**: All agents

**Detail**: The following computational resources were searched and found to NOT have data for N=10000:

- **OEIS A143824 b-file**: Only covers n=0..500
- **Apostolos Dimitromanolakis's Golomb ruler database** (cs.toronto.edu/~apostol/golomb/): Contains Ruzsa construction parameters for up to 65,000 *marks*, but this measures ruler length (minimum span for k marks), not F(N) (maximum marks in fixed range). These are the DUAL problem. The q=101 Singer set has 102 marks and span ~10303, which is the best known in its span class.
- **cube20.org Golomb ruler project**: Computes "possibly-optimal Golomb rulers" (minimum span for given number of marks), the inverse problem. Their results don't directly give F(10000).
- **Helm 2006 database**: NOT FOUND — could not locate this database. Possibly unpublished or defunct. Several searches returned no results for "Helm 2006 Sidon database."

**Actionable implication**: There is no lookup table to consult. Any improvement over 102 would require algorithmic search.

---

## Finding 4: Upper Bound is 109 (Not 100 as in the Problem Description)

**Relevance**: All agents; evaluator/scoring

**Detail**: The problem description says "theoretical maximum for N=10,000 is approximately 100 elements (sqrt(N) bound)" — **this is outdated/wrong**. The modern bound is tighter:

- **Carter, Hunter, O'Bryant (2023)**, arXiv:2310.20032: F(N) ≤ √N + 0.98183·N^{1/4} + O(1)
  - For N=10000: ≤ 100 + 9.82 + O(1) ≈ **109.82**
- **O'Bryant (2022)**, arXiv:2207.07800: F(N) ≤ √N + 0.99703·N^{1/4}
  - For N=10000: ≤ 100 + 9.97 ≈ **109.97**

The project correctly uses **target = 109** (already updated per state of affairs). The simple √N = 100 bound is obsolete; the +N^{1/4} correction is what makes 109 the right target.

**Actionable implication**: Reaching 109 is not provably impossible — it requires exceeding the best known construction (102) by 7 elements. The upper bound guarantees F(10000) ≤ 109 or 110, so 109 is achievable in principle.

---

## Finding 5: No Known Construction Beyond Singer Approaches 102 for This N

**Relevance**: explore agents, exploit agents considering alternative algebraic approaches

**Detail**: The literature documents several construction families:

| Construction | Density | Best for N=10000 | Status |
|---|---|---|---|
| Singer/Perfect Difference Sets | q+1 in {0..q²+q} | **102** (q=101) | Best known |
| Erdős-Turán (mod p) | ~p in {0..p²} | ~75 (p=71) | Confirmed inferior |
| Ruzsa (1993) | Similar to Singer asymptotically | Not computed for N=10000 | Unknown |
| Bose-Chowla | Same as Singer (equivalent) | Same as Singer | Equivalent result |
| APN functions (arXiv:2411.12911) | 192 in F₂^{15} | **NOT APPLICABLE** | Different setting (F₂^t) |

The APN function paper (2024, arXiv:2411.12911) achieves 192 elements in F₂^{15} — impressive, but it works in characteristic-2 finite fields (GF(2)^15 ≅ GF(32768)), not in integer intervals. Not transferable.

Ruzsa's construction (1993): Produces infinite Sidon sets, but for finite intervals the density is ~Singer asymptotically. For N=10000, it's unclear if it beats 102. No published source confirms this.

**Actionable implication**: No unexplored algebraic construction is likely to beat Singer for N=10000. The path forward is computational search (ILP, randomized local search with large perturbations, or backtracking).

---

## Finding 6: The Dual Problem (Golomb Rulers) Has More Computational Resources

**Relevance**: Researchers; potentially applicable insights

**Detail**: The "dual" Sidon set problem is: given k marks, find the minimum span L(k). Known as optimal Golomb rulers. For k=102 marks, the optimal span is unknown but the Singer q=101 gives L(102) ≤ 10302. The OEIS A003022 sequence tabulates optimal Golomb ruler lengths for k up to ~28 marks only; larger k are open problems.

The cube20.org distributed computing project computed OGR (Optimal Golomb Ruler) for up to k=28 marks. For k=102, the minimum span is unknown; the Singer construction gives an upper bound of 10302.

**Key insight**: If the optimal Golomb ruler for 103 marks has span ≤ 10000, then F(10000) ≥ 103. But computing this is itself an open hard problem.

**Actionable implication**: No shortcut available from the Golomb ruler side. The dual problem is equally unsolved for large k.

---

## Finding 7: Stochastic/Computational Search is the Primary Path Forward

**Relevance**: All agents planning gen 3+ strategy

**Detail**: Since no algebraic construction is known to beat Singer q=101 for N=10000, and exhaustive search is infeasible, the literature and computational experience point to the following viable approaches:

1. **ILP/constraint programming**: No published paper tries this for N=10000. Formulating it as an integer program with ~10001 binary variables and O(N²) sum-uniqueness constraints is large but not necessarily infeasible with modern solvers (SCIP, Gurobi, CBC). Partial ILP (fixing top-80 elements, optimizing 22 positions from candidates) is more tractable.

2. **Large-scale perturbation search**: The 102-element Singer set is locally saturated (40+ blockers per non-member). But random removal of k=20-40 elements followed by greedy re-extension might occasionally find 103+ combinations. This is a Monte Carlo approach — probability per trial is low but with thousands of trials it's plausible.

3. **Backtracking/branch-and-bound**: Starting from a partial Sidon set and systematically extending via backtracking. Known to work for small N; may be too slow for N=10000 but partially applicable.

4. **Population-based search (genetic algorithms, simulated annealing with large neighborhoods)**: SA with the neighborhood being "remove 20, add 22" transitions. The 40+ blocker result means small neighborhoods fail; large neighborhoods are needed.

**No published paper reports success with any of these for N=10000 specifically.** The 102→103 barrier is genuinely unsolved.

---

## Open Questions

1. **Does Ruzsa's construction give a different algebraic structure** that could be combined with Singer q=101 elements via hybrid construction? The two structures would need to have non-overlapping difference sets to combine safely.

2. **Is there a feasibility result for ILP on N=10000?** Would a good commercial solver (Gurobi with a university license, or SCIP) succeed on this problem size? The constraint matrix would be ~10001 binary variables × ~50M constraints — likely too large for exact ILP, but a relaxation + rounding might work.

3. **Can the OEIS A143824 b-file be extended** to larger n via computation? Running an exact solver for n up to 10000 would require either brute force (infeasible) or clever bounding. This is an open research problem.

4. **What is the optimal Sidon set for n=1000, 2000, 5000?** If intermediate values show patterns deviating from Singer, they might suggest alternative constructions.

---

## Sources

- O'Bryant (2004), "A Complete Annotated Bibliography of Work Related to Sidon Sets," arXiv:math/0407117
- Carter, Hunter, O'Bryant (2023), "Improved upper bounds on Sidon sets," arXiv:2310.20032
- O'Bryant (2022), arXiv:2207.07800
- OEIS A143824 (maximum Sidon set size in {1..n}), b-file n=0..500
- OEIS A003022 (optimal Golomb ruler lengths, up to 28 marks)
- Dimitromanolakis thesis (~2002), cs.toronto.edu/~apostol/golomb/ (Ruzsa/Bose-Chowla constructions for Golomb rulers)
- arXiv:2411.12911 (2024) — APN functions for F₂^t Sidon sets (not applicable here)
- cube20.org — Optimal Golomb Ruler distributed computation
