# Debrief Report — gen007_experimentator_1

## Primary Deliverable

**`output/helpers/cpsat.py`** — shared CP-SAT helper module with 3 functions + self-test.

All self-tests pass. All returned solutions verified as valid Sidon sets via `is_sidon()`.

---

## 1. What did you try?

### Phase 1: Initial implementation with naive VLNS formulation
Wrote cpsat.py with `solve_sidon_cpsat`, `vlns_sidon`, `vlns_batch`, `self_test`.
Initial VLNS used separate constraint systems for free-to-fixed and free-to-free diffs.
**Result:** Self-test FAILED — VLNS returned `[0,1,3,7,12,20,30,48]` which has duplicate
diff 18 (12→30 and 30→48). The separate constraint systems missed cross-type collisions.

### Phase 2: Unified per-difference-value constraint
Rewrote VLNS with a unified approach: for each diff value d, collect ALL sources (type-2:
free-to-fixed, type-3: free-to-free) into a single `add_at_most_one` constraint.
**Result:** All 6 self-tests pass. VLNS returns valid Sidon sets.

### Phase 3: Validation with real 105-element set
- `vlns_sidon(BEST_105[:100], 6, N=10000, time_limit=60)` → **OPTIMAL, size=105, 0.097s**
- 9-trial batch (rm=3,5,10 × 3 trials): **All OPTIMAL at 105 in <0.1s each**

**Critical finding:** The gen-6 INFEASIBLE results were confirmed as a formulation bug.
The corrected formulation returns OPTIMAL (not INFEASIBLE), proving the solver CAN find
replacements — they just never exceed 105 elements. The self-healing property is confirmed
computationally with a correct formulation.

### Formulation details

**`solve_sidon_cpsat`:**
- N ≤ 500: Binary formulation. x_i ∈ {0,1}, per-difference at-most-one pair indicator.
  Practical and correct. Found 12-element Sidon set in [0,100] in 30s.
- N > 500: Element formulation with pairwise != (NOT AllDifferent). Variables e_0 < ... < e_{k-1}.
  All C(k,2) differences constrained pairwise distinct. Found 10-element set in [0,1000] in 0.5s.
- N=10000 binary formulation is impractical (~50M auxiliary variables). Element formulation
  with pairwise != is the same decomposition as AllDifferent but may propagate differently.

**`vlns_sidon`:**
- Binary vars for candidates not in fixed set.
- Pre-filters: eliminates candidates conflicting with fixed-fixed diffs or producing
  duplicate diffs with different fixed elements.
- Unified constraints: for each diff value d, at-most-one over {y[c] for type-2 sources}
  ∪ {p(c1,c2) for type-3 pairs}, where p = (y[c1] AND y[c2]) via channeling.
- Also handles free-to-free diffs that collide with fixed diffs (explicit mutual exclusion).

---

## 2. What information did I lack?

- **No performance benchmarks for VLNS at scale.** I tested rm=3,5,10 with 3 trials each.
  A systematic sweep over rm=1-50 with 20+ trials would characterize the landscape better.
  But that's compute work, not helper-building work.

---

## 3. What given facts might be wrong or outdated?

- **SoA says "VLNS: 0 valid trials (9 trials had bug)"** — now outdated. 9 valid trials
  completed with corrected formulation, all OPTIMAL at 105. VLNS works but confirms
  the self-healing property, not a path to 106.

---

## 4. Was the State of Affairs accurate?

Yes. The SoA correctly identified VLNS formulation bug as highest priority and helpers/cpsat.py
as a 3-generation-old missing deliverable. Both are now resolved.

---

## 5. What would you do differently?

Nothing significant. The task was well-scoped. I caught the free-to-free vs free-to-fixed
collision bug during self-testing (test 2), which is exactly how the self-test was designed
to work.

---

## 6. Specific experiments to run

| Priority | Experiment | Expected Outcome |
|----------|------------|------------------|
| HIGH | `vlns_batch(BEST_105, range(1,50), 20, time_limit=30)` | Full landscape characterization. Expect all OPTIMAL at 105 (self-healing). |
| HIGH | `vlns_batch(BEST_104, [3,5,10], 10, time_limit=30)` | Test if 104-mark Singer set is also self-healing. If replacements find 105+, that's a different construction. |
| MEDIUM | `solve_sidon_cpsat(k=106, N=10000, hint=BEST_105, time_limit=3600)` | Element formulation with pairwise !=. Different decomposition than AllDifferent — may propagate differently. |
| MEDIUM | Anti-algebraic VLNS: fix 50 elements from BEST_105, add constraint that free elements share ≤10% with BEST_105's remaining elements | Forces exploration of non-algebraic region |

---

## 7. What surprised me?

1. **VLNS OPTIMAL in <0.1s** — the corrected formulation is incredibly fast. 100 fixed
   elements with 10 free slots in 10001-element domain, solved to proven optimality in 70ms.
   CP-SAT's presolve is extremely effective when most variables are pre-filtered.

2. **The naive VLNS formulation produced invalid results silently** — the gen-6 INFEASIBLE
   was actually a better failure mode. My initial implementation returned OPTIMAL with an
   invalid Sidon set. Without the is_sidon() self-test, this would have poisoned downstream
   agents. Lesson: self-tests must validate results against ground truth, not just check
   solver status.

3. **Binary formulation for N=10000 is impractical** — O(N^2) auxiliary variables makes
   direct binary encoding infeasible. The element formulation with pairwise != is the
   practical choice for large N. The VLNS binary formulation works because the pre-filter
   reduces candidates from ~9900 to ~hundreds.

---

## 8. Helper tools feedback

- **`helpers/core.py`**: `is_sidon()` essential for self-test validation. Works correctly.
- **`helpers/rokicki_data.py`**: `BEST_105` used for real-world VLNS testing. Not in
  `problem/helpers/` directory (lives at `problems/sidon/helpers/rokicki_data.py` only).
  Agents may have trouble importing it depending on sys.path setup.
- **Missing helper:** `rokicki_data.py` should be copied to `problem/helpers/` in the
  run directory for consistent imports.

---

## 9. Time budget

Adequate. Primary deliverable (cpsat.py) completed with full self-testing and real-world
validation. If I had more time:
1. Run comprehensive VLNS sweep (rm=1-50, 20 trials each)
2. Test element formulation for k=106, N=10000 with 1h timeout
3. Compare VLNS on BEST_104 vs BEST_105 to test if self-healing is construction-specific
