# Debrief Report — gen006_full_1 (full_1)

## Solution Table

| File | Fitness | is_valid | Approach |
|------|---------|----------|----------|
| sol01.py | **105** | 1 | 105-mark Rokicki-Dogon baseline |
| sol02.py | **105** | 1 | CP-SAT k=106 (UNKNOWN, fallback to 105-mark) |
| sol03.py | **105** | 1 | VLNS 9 trials (all INFEASIBLE in <1s, fallback to 105-mark) |
| sol04.py | **105** | 1 | Binary search on N (UNKNOWN N=10000–15000, fallback) |

Best score this session: **105** (no improvement over gen 5).

---

## 1. What Did I Try?

### Phase 1: CP-SAT k=106 with 105-mark warm-start (sol02)
- **k=104 verification** (30s, 8 workers): UNKNOWN — surprisingly, even k=104 returned UNKNOWN
  with the 30s budget. This suggests the formulation is harder than expected even for sub-optimal k.
- **k=106 main run** (1200s, 16 workers): UNKNOWN. No feasible solution found.
- **k=106 with linearization_level=2, symmetry_level=2** (600s): UNKNOWN (killed by session timeout).
- The 105-mark hint provided 105 of 5671 variables; presolve ran 105 loop iterations reducing
  linear domains, but search made no visible progress toward feasibility.

### Phase 2: VLNS — Very Large Neighborhood Search (sol03, novel approach)
Instead of the full k=106 problem, fixed 85 elements from the 105-mark set and used CP-SAT to
find 21 replacements (a much smaller subproblem: 21 free vars vs 106).

**All 9 trials returned INFEASIBLE in < 1 second** (< 0.9s each via presolve).

Trials covered: random-20 (×3), random-15 (×2), random-25 (×2), high-density-20, spread-20.

Error: `INFEASIBLE: 'linear: never in domain'` — presolve reduces a difference variable's
domain to empty.

**Likely bug:** The `add_abs_equality(d, y[i] - fv)` creates a difference variable with domain
[1, N] (excluding fixed differences). But during presolve, if y[i] = fv is still in the
variable's domain, the absolute difference can be 0 — excluded by the [1,N] domain → INFEASIBLE.
The `y[i] != fv` constraints may not fire before this domain conflict is detected.

**Fix:** Create cross-diff variables with domain [0, N], handle 0 separately, or add explicit
bounds to exclude y[i] = fv before the abs constraint.

### Phase 3: Binary search on N (sol04)
Tested N=10000, 10200, 10500, 11000, 12000, 15000 with 120s CP-SAT each.
All returned UNKNOWN. N=20000 was killed by session timeout.

**Finding:** k=106 is hard even at N=15000 (50% larger range). Difficulty is not primarily
from the tight N=10000 bound — the search tree is hard regardless.

---

## 2. What Information Did I Lack?

- Whether the VLNS INFEASIBLE results are genuine or a formulation bug. This would change the
  interpretation entirely (bug → promising approach; genuine → strong evidence for k=106 infeasibility).
- CP-SAT search tree statistics for the k=106 run (node counts, LP bounds). The verbose log
  showed presolve details but no search tree progress — the solver may be stuck before tree search.
- Published F₂(10000) value to know whether k=106 is even achievable.

---

## 3. What Given Facts Might Be Wrong or Outdated?

- The SoA says "VLNS: untested." I tested it, found likely formulation bug — the INFEASIBLE
  results are probably artifacts, not genuine proofs of infeasibility.
- k=104 with 30s CP-SAT returned UNKNOWN — previous sessions claimed this should be easy with hint.
  May indicate the formulation (AllDifferent over 5565 diffs) is harder than expected even for
  feasible cases.

---

## 4. Was the State of Affairs Accurate?

Mostly yes. The SoA correctly identified CP-SAT k=106 and binary search on N as priorities.
The main new finding not in SoA: the VLNS approach needs a corrected formulation before being
judged. The SoA note that "VLNS: untested" is now updated by this session.

---

## 5. What Would I Do Differently?

1. **Fix VLNS formulation**: Change cross-diff domain from [1,N] to [0,N] and add an explicit
   constraint `d >= 1` (or equivalently `y[i] != fv`). Ensure the != constraint fires before
   the abs constraint domain reduction.
2. **VLNS with k=105 goal**: Instead of asking for 106, ask for 105 from a different fixed set.
   This would verify the formulation works and find alternative 105-element sets.
3. **Much longer CP-SAT runs**: The brief suggested 4h+ runs. 1200s = 20min is still too short.
   A dedicated overnight run (4-8h) with 16 workers is the most likely path to resolution.
4. **Try maximize formulation**: Instead of "find exactly k=106", maximize the number of elements.
   This allows CP-SAT to find k=105 first, then improve. More likely to produce useful solutions.

---

## 6. Specific Experiments to Run

1. **Fix VLNS and retry**: Correct the abs-equality formulation bug, retry with 50+ random
   removal patterns. This is cheap (each trial < 1s if INFEASIBLE, up to 120s if tractable).
2. **VLNS with maximize formulation**: After removing 20 elements from S105, maximize the
   number of free elements instead of requiring exactly 21. May find 105-element sets.
3. **Overnight CP-SAT for k=106**: 4h+ run with 105-mark hint. Most likely to find k=106 if
   it exists, or accumulate search tree evidence.
4. **CP-SAT infeasibility for k=106**: Run with `enumerate_all_solutions: false` and `stop_after_first_solution: false` for maximum proof effort. If it returns INFEASIBLE (not UNKNOWN), that settles the question.

---

## 7. What Surprised Me?

- **VLNS INFEASIBLE in <1s**: All 9 trials proved infeasible in under 1 second. Even if this
  is a bug, the speed is surprising — the presolve is very effective at detecting conflicts.
- **k=104 UNKNOWN in 30s**: With 105 of 106 hints provided, finding a k=104 set should be
  trivial (just drop one element). That it returned UNKNOWN suggests either the hint wasn't
  propagated as expected, or the AllDifferent formulation is harder than the direct approach.
- **Binary search shows N doesn't matter much**: k=106 hard even at N=15000. The difficulty
  is inherent to finding 106 mutually distant elements, not just the tight [0,10000] range.

---

## 8. Helper Tools Feedback

- `helpers/core.py`, `helpers/search.py`, `helpers/singer.py`: Not used this session (all work
  was CP-SAT based, no greedy construction needed).
- **Desired helper**: `solve_sidon_cpsat(k, N, hint, time_limit, workers)` — a clean wrapper
  that handles the integer element formulation (x[0] < ... < x[k-1], AllDifferent on diffs).
  This was re-derived from scratch again. The gen 5 report also requested this — it's still needed.
- **Desired helper**: `vlns_sidon(fixed_elements, n_free, N, time_limit)` — a corrected VLNS
  implementation with proper abs-equality handling.

---

## 9. Time Budget

Session was tight due to long CP-SAT runs:
- sol02 CP-SAT k=106: ~1800s (phases 1+2+partial 3)
- sol03 VLNS: ~10s (all INFEASIBLE instantly)
- sol04 binary search: ~724s (6 N values × 120s)

Total compute: ~2534s. Three generations of CP-SAT evidence accumulated.

With more time:
1. Fix VLNS formulation and run 100+ trials
2. Run CP-SAT k=106 maximize formulation for 4+ hours
3. Investigate why k=104 returns UNKNOWN with 105-element hint
