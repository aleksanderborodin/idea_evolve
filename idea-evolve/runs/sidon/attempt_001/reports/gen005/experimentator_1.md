# Experimentator 1 Debrief — Gen 5

## 1. What did you try?

| Approach | Result |
|----------|--------|
| Download Rokicki-Dogon database (cube20.org/golomb/) | SUCCESS — all 4 data files downloaded and parsed |
| Extract 105-mark ruler (ap q=107, mul=433, span=9884) | **fitness=105** — new pipeline best |
| Extract 104-mark ruler (pp q=103, mul=400, span=9581) | fitness=104 — valid |
| Extract 103-mark ruler (pp q=103, mul=400, span=9408) | fitness=103 — valid |
| Greedy extension of 105-mark ruler | 0 elements can be added — maximal |
| Remove-and-extend perturbation (k=1: 2000 trials, k=2: 2000 trials) | Never exceeded 105 |
| Exhaustive multiplier search for 106 marks (pp q=107: 9072 muls) | Best span = 10135 > 10000 |
| Exhaustive multiplier search for 106 marks (ap q=107: ~5700 muls) | Best span = 10163 > 10000 |
| Exhaustive multiplier search for 106 marks (pp q=109: ~9900 muls) | Best span = 10169 > 10000 |
| Check 107, 108 marks from q=109 | All spans > 10000 |

## 2. What information did you lack?

Nothing critical — the brief was excellent. The directive correctly identified this as a pure data-engineering task. The cube20.org/golomb/ page had everything needed.

One minor issue: the brief suggested the URL `cube20.org/golomb-all-00.zip` which returned 404. The actual URL was `cube20.org/golomb/golomb-all-00` (a zip archive without the .zip extension). This was resolved by fetching the index page first.

## 3. What given facts might be wrong or outdated?

- **problem/description.md**: Says "theoretical maximum is approximately 100 elements (sqrt(N) bound)". This is outdated — the upper bound is 109 (Carter-Hunter-O'Bryant 2023), and the constructive lower bound is now confirmed at 105.
- **State of Affairs**: Says "Singer constructions are exhausted — no prime gives >102 for N=10000." This is WRONG. The affine plane construction (Bose-Chowla) with q=107 gives 105 elements. Singer ≠ all algebraic constructions. The pipeline was stuck at 102 because it only explored Singer (pp) type, not affine plane (ap) type.
- **fact_002** and **fact_004** in the facts/ directory are confirmed stale (as SOA noted).

## 4. Was the State of Affairs accurate?

Partially. It correctly identified:
- Rokicki-Dogon as the highest-priority action
- The 102 ceiling for Singer q=101
- The gap to theoretical upper bound

It was **wrong** about:
- "Singer constructions are exhausted" — only projective plane (pp) type was exhausted. The affine plane (ap) construction with q=107 gives 105.
- The SOA should distinguish between Singer (pp), Bose-Chowla (ap), and Ruzsa (rl) construction types.

## 5. What would you do differently?

Nothing — the task was well-defined and completed efficiently. The download-parse-verify pipeline worked exactly as planned.

## 6. Specific experiments to run

| Priority | Experiment | Expected Outcome |
|----------|------------|------------------|
| **HIGH** | CP-SAT/ILP for k=106 at N=10000 with 4h+ timeout | Could prove 106 feasible or infeasible |
| **HIGH** | Backtracking search with pruning from 105-mark seed | Could find 106 via non-algebraic means |
| **MEDIUM** | Remove-5 through remove-10 + re-extend on 105-mark set (100K+ trials) | Unlikely to exceed 105, but worth eliminating |
| **MEDIUM** | Hybrid: combine elements from 105-mark (ap q=107) and 104-mark (pp q=103) sets | Check if any union subset exceeds 105 |
| **LOW** | Check Ruzsa (rl) construction type for q=107-113 | Ruzsa is known to be worse, but haven't verified |

## 7. What surprised you?

1. **The database had DIRECT ruler mark positions** in `rulers-all-00`. Previous agents tried to download a nonexistent zip file and never found the actual data. The index page clearly listed all file types.

2. **105 is maximal** — not a single element can be added to the 105-mark set within [0, 10000]. The set uses 5460 of the 10000 possible differences, and every non-member candidate conflicts with at least one existing difference.

3. **The gap between 105 and 106 is EXACTLY 135 in span** — the best 106-mark ruler has span 10135, overshooting our limit by just 135. This is tantalizingly close.

4. **The 104-mark and 103-mark rulers are nested** — the 104-mark ruler is the 103-mark ruler plus one element (9581). Both come from the same pp q=103 construction.

5. **The 105-mark ruler comes from a DIFFERENT construction type** (ap/Bose-Chowla, not pp/Singer). The pipeline had been fixated on Singer-type constructions and missed this.

## 8. Helper tools feedback

- Did not use any helpers from `problem/helpers/` — this was a data engineering task.
- **helpers/singer.py** only implements the Singer (pp) construction. The ap (affine plane / Bose-Chowla) construction is missing. Adding a `helpers/bose_chowla.py` that implements the ap construction would be valuable, but given that the 105-mark ruler is already extracted as a static list, the marginal benefit is low.
- **Wish existed**: A `helpers/rokicki_dogon.py` that encodes the key rulers (103-105 marks) as static data and provides `get_best_ruler(marks)` would save future agents from re-deriving these. However, it's simpler to just hardcode the 105-mark set in solution files.

## 9. Time budget

Sufficient. The core task (download, parse, extract, verify) completed quickly. Had ample time for extension experiments, perturbation search, and exhaustive multiplier verification. All planned work completed.

If I had more time, I would:
1. Implement the Bose-Chowla (ap) construction as a helper for arbitrary q
2. Run a more thorough perturbation search with k=3-10 (though unlikely to improve)
3. Start a CP-SAT formulation seeded with the 105-mark set to search for k=106

---

## Solution Table

| File | Fitness | is_valid | Strategy |
|------|---------|----------|----------|
| sol01.py | **105** | 1 | Rokicki-Dogon ap q=107 mul=433 (NEW BEST) |
| sol02.py | 104 | 1 | Rokicki-Dogon pp q=103 mul=400 |
| sol03.py | 103 | 1 | Rokicki-Dogon pp q=103 mul=400 |
