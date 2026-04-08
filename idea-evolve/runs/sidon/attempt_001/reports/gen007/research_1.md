# Debrief Report — gen007_research_1

## 1. What did you try?

### Primary objective: Find F₂(10000)

**Step 1 — Read `rokicki_data.py`:** Done immediately. File contains BEST_105 (105 marks, span 9884), BEST_104 (104 marks, span 9581), BEST_102 (102 marks, span 9775). **No BEST_106 entry exists.** The absence is itself evidence: if a 106-mark ruler with span ≤ 10000 were known to the Rokicki-Dogon database, it would be here.

**Step 2 — Web searches for F₂(10000):**
- Searched: OEIS A003022, "B2 sequence N=10000 maximum", "Sidon set record 10000", "Golomb ruler 106 marks span", "cube20.org golomb 106 marks", "Sidon set 106 elements 10000 record 2024"
- Fetched: cube20.org/golomb/ main page and indexp2.html, arXiv 2310.20032, OEIS A003022 (403 error), cs.toronto.edu Golomb page
- **Result: No published record of F₂(10000) > 105 found anywhere.**

**Step 3 — Targeted searches for 106-mark minimum span:**
- Searched: "minimum span Golomb ruler 106 marks", "Golomb ruler 106 marks optimal span"
- cube20.org database starts at 160+ marks (does not cover 106-mark rulers)
- Proven optimal rulers go only to n=28 (distributed.net OGR project)
- No tabulated minimum span for n=106 found in any accessible source
- **Conclusion: The minimum span of a 106-mark ruler is not publicly documented in accessible form.**

**Step 4 — Literature survey for algorithm approaches:**
- Found arXiv:1902.08660 on computational comparison of Golomb ruler optimization methods
- Found arXiv:2107.05744 (Eberhard 2023) on structural theory of dense Sidon sets
- Found arXiv:2103.15850 and 2207.07800 on upper bounds (confirming ~109)
- Found Rokicki-Dogon 2023 paper on larger Golomb rulers (160-40000 marks)

**Step 5 — Analyzed gen6 VLNS code (sol03.py):**
- Read the actual VLNS implementation from population/gen006/full_1/sol03.py
- Found that `y[i] != fv` constraints ARE already present — the "formulation bug" diagnosis may be incorrect
- The fast INFEASIBLE results more likely reflect genuine combinatorial infeasibility

**Step 6 — Did NOT implement or evaluate any solutions** due to time pressure from user instruction.

---

## 2. What information did I lack?

- **The minimum known span for a 106-mark Golomb ruler.** This single number would definitively answer whether F₂(10000) ≥ 106. It's not in any accessible public database. Shearer's IBM Research tables (historically at research.ibm.com/people/s/shearer/) were not accessible.
- **CP-SAT verbose output from gen6 VLNS trials.** Knowing WHICH variable's domain became empty would clarify if INFEASIBLE is genuine or a domain-range bug.
- **Whether Ruzsa-Lindström is implemented anywhere in the pipeline.** Did not have time to check if any gen6-7 agents wrote RL code.

---

## 3. What given facts might be wrong or outdated?

- **The VLNS "formulation bug" diagnosis (idea_024, pattern_014):** After reading sol03.py carefully, the `y[i] != fv` constraints ARE present. The bug may not be what was diagnosed. The INFEASIBLE result may be genuine.
- **The target score of 108 in the evaluation header:** No web source confirms 108 is achievable. The theoretical upper bound is 109 (O'Bryant 2022), but the practical optimum may be 105. The target should perhaps be updated to reflect this.
- **"Algebraic ceiling exhaustively proven":** The claim is that all multipliers for all primes q≤109 were searched. This needs verification — was the search truly exhaustive over all constructions, or only multiplier-optimized Singer/Bose-Chowla?

---

## 4. Was the State of Affairs accurate?

Mostly yes. The SoA correctly states:
- F₂(10000) lookup is unanswered (confirmed — still no definitive answer after this session)
- Algebraic ceiling is 105 (confirmed by web search — no published 106)
- VLNS needs formulation fix (partially wrong — the code already has `y[i] != fv`)
- Theoretical upper bound ~109 (confirmed by O'Bryant 2022)

Minor corrections:
- The VLNS formulation bug may be different than diagnosed — the constraint IS there
- The `rokicki_data.py` file exists and was read (brief said "MAY contain F2(10000) data" — it does NOT contain F2 data, only the best known constructions)

---

## 5. What would I do differently with more time?

1. **Contact Rokicki/Dogon directly** (cube20.org contact form) asking for the minimum known span of a 106-mark ruler. This is the single most efficient path to answering F₂(10000).
2. **Implement and evaluate the corrected VLNS** with verbose CP-SAT output to diagnose exactly why INFEASIBLE occurs. Add: `solver.parameters.log_search_progress = True` and check which constraint causes the infeasibility.
3. **Implement tabu search** with swap-then-fill and run 10,000+ iterations. Even if it doesn't find 106, finding multiple DIFFERENT 105-element sets would be valuable.
4. **Implement Ruzsa-Lindström** (p=97, p=101) and use as starting point for VLNS.
5. **Download arXiv:1902.08660** and read the full CP formulation section — it might contain a better Golomb ruler CP formulation than what we're using.

---

## 6. Specific experiments to run

**Highest priority:**
1. **CP-SAT maximize formulation (4h+, 16 workers):** Replace "find k=106" with "maximize k" starting from BEST_105 hint. If it proves INFEASIBLE at k=106, that settles F₂(10000) = 105.

2. **VLNS with verbose logging:** Re-run sol03's VLNS with `log_search_progress=True`. Identify the specific variable/constraint that empties the domain. This diagnoses genuine vs bug infeasibility in minutes.

3. **Tabu search with swap-then-fill (10,000 iterations):** Implement as described in findings.md Finding 3. The key is using the tabu list to prevent the self-healing return to BEST_105.

**Medium priority:**
4. **Ruzsa-Lindström construction:** Implement `S = {x*p + g^x mod p : x in range(p)}` for p=97, p=101. Use as VLNS seed instead of BEST_105.

5. **Download and analyze arXiv:1902.08660** for a better CP-SAT formulation of the Golomb ruler problem.

---

## 7. What surprised me?

- **No published F₂(10000) anywhere.** After 6 generations of research agent failures to look this up, I expected the answer to be trivially findable (e.g., on OEIS). It is NOT — there is no published table of F₂(N) for moderate N values. The best databases either cover proven optima up to n=28 marks (too small) or near-optimal constructions for 160+ marks (too large).

- **The VLNS code already has the "bug fix."** Gen6's full_1 was diagnosed as having a bug in abs-equality domain handling, but reading sol03.py shows `model.add(yi != fv)` IS present. The INFEASIBLE results might be genuine.

- **The Bose-Chowla q=107 construction naturally gives 108 marks** (q+1), not 105. The 105-element set is a subset that happens to fit in {0,...,9884}. Three elements of the full 108-mark set have positions > 10000.

---

## 8. Helper tools feedback

- `helpers/core.py` (`is_sidon`, `can_add`): Appeared correct and useful from reading.
- `helpers/rokicki_data.py`: Contains the best known constructions. This is correct and extremely useful as a baseline. **It does NOT contain F₂(10000) as a tabulated value — it IS the best known construction.**
- `helpers/search.py`: Has `greedy_sidon` and `build_diff_counts`. Missing: a tabu search implementation with swap-then-fill moves. This helper would save significant time for future agents.

**Most wanted helper (not yet existing):**
```python
# helpers/cpsat.py
def solve_sidon_cpsat(k, N, hint=None, time_limit=120, workers=8, maximize=False):
    """Wrapper for CP-SAT Sidon set solver. Returns (status, solution or None)."""
    ...
```
This has been requested for 3 consecutive generations. Every CP-SAT agent re-derives the formulation from scratch.

---

## 9. Time budget

**Time was limited.** The session was cut short by user instruction before implementing any solutions. Work completed:
- Read `rokicki_data.py` ✓
- Read state_of_affairs.md ✓  
- Read coverage_matrix.md ✓
- Read gen6 reports and relevant ideas ✓
- Launched 4 parallel web search agents ✓
- Analyzed VLNS code from sol03.py ✓
- Wrote findings.md ✓

**Not done due to time:**
- Implementing sol01.py (tabu search or corrected VLNS)
- Evaluating any solutions
- Downloading specific papers (arXiv:1902.08660)

**If I had more time (in priority order):**
1. Implement tabu search with swap-then-fill and evaluate (~30 min)
2. Implement and test VLNS with verbose logging to diagnose infeasibility (~20 min)
3. Implement Ruzsa-Lindström construction as SA seed (~20 min)
4. Download and read arXiv:1902.08660 for better CP formulation (~15 min)
