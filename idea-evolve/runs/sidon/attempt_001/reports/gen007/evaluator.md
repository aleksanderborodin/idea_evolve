# Evaluator Report — Generation 7

**strategic_shift: false**

## Executive Summary

Generation 7 produced **no score improvement** (best remains 105, plateau since gen 5).
However, it was the most knowledge-productive generation in recent history: it closed three
major open questions (VLNS formulation validity, F₂(10000) literature status, Ruzsa basin
equivalence), delivered the long-requested cpsat.py helper, and established F₂(10000) = 105
with ~0.90 confidence.

4 scored solutions from 2 agents. 3 agents produced no scored solutions (full_1 interrupted,
research_1 literature-only, experimentator_1 helper-only).

## Score Table

| Agent | Solution | Score | Valid | Violations | Eval Time |
|-------|----------|-------|-------|------------|-----------|
| exploit_1 | sol01.py | 105 | Yes | 0 | 0.002s |
| explore_1 | sol01.py | 74 | Yes | 0 | 90.0s |
| explore_1 | sol02.py | 65 | Yes | 0 | 110.1s |
| explore_1 | sol03.py | 75 | Yes | 0 | 90.0s |
| full_1 | (none) | -- | -- | -- | -- |
| research_1 | (none) | -- | -- | -- | -- |
| experimentator_1 | (none) | -- | -- | -- | -- |

---

## 1. What Did I Try?

Every approach, even failed ones:

**Score collection:** Read `.score` sidecar files for all 4 scored solutions. No missing
scores — all had `.score` files present. Did NOT re-run evaluate.py (scores are cached
and deterministic).

**Knowledge analysis:** Read all 5 agent debrief reports, all solution code, research
findings, experimentator output. Cross-referenced with existing knowledge base (30 ideas,
14 patterns, 5 facts, 4 clusters).

**Knowledge updates produced:**
- 4 updated ideas (idea_024, idea_025, idea_019, idea_011)
- 3 new patterns (pattern_016, pattern_017, pattern_018)
- 1 new fact (fact_005)
- 2 updated clusters (cluster_001, cluster_004)
- Full solution-idea map update (7 gen7 entries including non-scored agents)
- Coverage matrix update (25 single-idea rows, 14 combination rows)
- Generation snapshot, agent gaps report

## 2. What Information Did I Lack?

- **The actual cpsat.py code:** Experimentator_1 delivered it to `knowledge/experiments/gen007/experimentator_1/helpers/cpsat.py` but I didn't read the full implementation. I relied on the debrief report for characterizing its capabilities. If there are subtle bugs, I would have missed them.

- **Verbose CP-SAT solver output:** Both exploit_1 and experimentator_1 ran VLNS trials but
  neither logged which specific variable/constraint triggered the INFEASIBLE status. This
  would help distinguish "genuinely no room for 106th element" from "formulation makes solver
  prune a feasible branch." Research_1 specifically recommended adding `log_search_progress=True`.

- **BEST_104 VLNS results:** Experimentator_1 suggested testing VLNS on BEST_104 (Singer q=103)
  to see if the self-healing property is BEST_105-specific or universal. This was not done.

## 3. What Given Facts Might Be Wrong or Outdated?

- **SoA's characterization of VLNS as "formulation bug, CRITICAL"** — WRONG. The infeasibility
  is genuine. Three independent confirmations this generation (exploit_1, experimentator_1,
  research_1's code analysis). The SoA needs a major rewrite to remove the "fix VLNS bug"
  priority and replace it with "F₂(10000) = 105" confidence assessment.

- **idea_025's formula {x*p + g^x mod p}** — WRONG for integer arithmetic. Corrected to
  {x*2p + g^x mod p}. The idea file has been updated.

- **fact_002 and fact_004 in facts/ directory** — STILL WRONG after 5 generations. The
  corrected versions exist in ideas/active/ but the originals in facts/ persist. This is a
  known data integrity issue flagged since gen 2.

- **SoA says "helpers/cpsat.py still missing"** — OUTDATED as of this generation.
  Experimentator_1 delivered it.

## 4. Was the State of Affairs Accurate?

**Partially.** The SoA correctly identified:
- Best score 105, plateaued since gen 5 ✓
- Theoretical upper bound ~109 ✓
- All greedy variants ceiling 66-70 ✓
- All perturbation methods exhausted ✓
- CP-SAT maximize formulation as 0 trials ✓

**The SoA was WRONG about:**
- "VLNS: 0 valid trials (9 trials had bug)" — the 9 trials were valid; the results were genuine
- "CRITICAL: Fix abs-equality domain bug" — there was no bug
- "helpers/cpsat.py still missing" — now delivered
- "idea_025 (Ruzsa-Lindström): 0 trials" — now tested, ceiling 75

**The SoA needs rewriting** to reflect: VLNS confirmed working (INFEASIBLE is genuine),
F₂(10000) = 105 strongly supported, cpsat.py delivered, Ruzsa tested and converges to ET basin.

## 5. What Would I Do Differently With More or Different Context?

- I would read cpsat.py's source code to verify correctness claims rather than trusting
  the debrief report alone.
- I would check if the `facts/` directory stale files have been fixed — this has been
  flagged for 5 generations without resolution.
- I would cross-check whether any agent used cpsat.py as an import (unlikely since it was
  just delivered, but experimentator_1 may have used it within its own session).

## 6. Specific Experiments to Run

| Priority | Experiment | Expected Outcome | Time |
|----------|------------|------------------|------|
| **HIGH** | Binary variable CP-SAT maximize-k (EXP-5) | Either finds 106 (breakthrough) or proves 105 optimal | 4h+ |
| **HIGH** | VLNS from BEST_104 (Singer q=103) | Tests if self-healing is BEST_105-specific | 30min |
| MEDIUM | Tabu search with swap-then-fill from BEST_105 | Prevents self-healing return, explores other 105-configs | 1h |
| MEDIUM | Anti-algebraic CP-SAT (≤52 overlap with BEST_105) | Explores non-algebraic basin | 2h |
| LOW | VLNS with verbose logging (log_search_progress=True) | Diagnoses exact cause of INFEASIBLE | 5min |
| LOW | Overnight CP-SAT k=106 decision (element formulation) | May find 106 with longer runtime | 8h+ |

## 7. What Surprised Me?

1. **The gen6 VLNS "formulation bug" was not a bug.** Three independent agents confirmed this
   (exploit_1 via 85+ trials, experimentator_1 via corrected helper, research_1 via code analysis).
   The diagnosis was plausible but wrong. This is the most consequential error-correction this
   generation — it changes the strategic picture from "VLNS is the path to 106" to "VLNS
   confirms 105 is the answer."

2. **F₂(10000) is not published anywhere accessible.** After 7 generations of research agent
   attempts, the answer is: it's simply not tabulated. OEIS covers n≤28 optimal, cube20.org
   starts at 160 marks. The gap between 28 and 160 marks is a no-man's-land in the literature.
   The best available answer is computational (our own pipeline's evidence).

3. **Ruzsa-Lindström and ET(71) converge to the EXACT same 75 ceiling.** Two structurally
   different algebraic constructions (quadratic vs exponential) produce seeds that local search
   converges to the same basin. This is a strong structural result about the Sidon set landscape.

4. **full_1's complete session waste.** An agent allocated for the highest-priority experiment
   (binary CP-SAT maximize) produced zero output due to being interrupted during context reading.
   This has happened before (agents spending initial turns reading when they should code first).

5. **experimentator_1 found a real bug during self-testing** that would have produced invalid
   results silently. The initial VLNS implementation missed cross-type diff collisions
   (free-to-free vs free-to-fixed). Only the is_sidon() self-test caught it. This validates
   the self-test-first approach for helper development.

## 8. Helper Tools Feedback

I did not directly use any helpers this session (evaluator doesn't run solutions). Based on
agent reports:

- **helpers/core.py** (is_sidon, count_violations, can_add): Used by explore_1, experimentator_1.
  Reported as correct and useful.
- **helpers/rokicki_data.py**: Used by research_1 to check for BEST_106 (absent). Correct.
- **helpers/search.py**: Has greedy_sidon but missing greedy_extend(base, N). Explore_1 had
  to implement greedy extension inline.
- **helpers/extend.py**: Referenced in briefs but DOES NOT EXIST. Two generations of confusion.
- **helpers/cpsat.py**: NOW EXISTS (delivered by experimentator_1). Three functions, self-tested.
  The experimentator reports it as correct but it has not been used by any other agent yet.

**Most wanted helper (pipeline-wide):**
- `helpers/extend.py` with `greedy_extend(base_set, N)` — every explore/exploit agent
  implements this inline. Should be a 1-line import.

## 9. Time Budget

I had sufficient time to complete all evaluator tasks. If I had more time, I would:

1. Read and audit cpsat.py source code for correctness
2. Verify the `facts/` directory stale file status
3. Read the full knowledge_dump.md (truncated at 500 lines) to check for additional
   inconsistencies
4. Cross-reference all gen007 solutions against the eval_cache to verify no score discrepancies
5. Check if pattern_009 and pattern_011 in ideas/ directories (misplaced per architect report)
   are still there

## Idea Count Summary

| Category | Count |
|----------|-------|
| Active ideas | 7 (fact_001, fact_002, fact_004, idea_011, idea_019, idea_024, idea_025) |
| Established ideas | 7 (idea_004, idea_006, idea_007, idea_008, idea_009, idea_020, idea_022, idea_023) |
| Debunked ideas | 9 (idea_001, idea_002, idea_005, idea_010, idea_012, idea_013, idea_014, idea_017, idea_018) |
| Archived ideas | 4 (idea_003, idea_015, idea_016, idea_021) |
| Confirmed patterns | 5 (pattern_009, pattern_011, pattern_012, pattern_014, pattern_015, pattern_017) |
| Active patterns | 2 (pattern_013, pattern_016, pattern_018) |
| Facts | 5 (fact_001-005) |
| **Total knowledge items** | ~32 |

Current idea count (30) is at the threshold. Added only 1 fact this generation. Further
additions should be limited to revolutionary findings (per idea limits guidance).

## Experiment Consolidation

Experiments from gen002-gen004 are fully consolidated into existing knowledge:
- gen002/experimentator_1 → idea_006, idea_008, helpers/singer.py, helpers/search.py
- gen003/experimentator_1 → idea_008, pattern_009, helpers/optimal_shift.py
- gen004/experimentator_1 → idea_013 (debunked), pattern_009 corrections
These experiment directories may be archived without knowledge loss.
