# Evaluator Report — Generation 5

**strategic_shift: true**

## Executive Summary

Generation 5 is the most productive generation in this run. After a 3-generation plateau at 102,
the pipeline broke through to **105** — a +3 improvement driven by the Rokicki-Dogon database
that two agents independently verified. The algebraic ceiling is now exhaustively confirmed at
105 for N=10000. Beam search (the last untested greedy variant) reaches 70, closing the greedy
research direction. CP-SAT remains UNKNOWN for k=103 after 1800s of compute.

## Score Table — All Gen 5 Solutions

| # | Agent | Solution | Score | Valid | Violations | Strategy |
|---|-------|----------|-------|-------|------------|----------|
| 1 | experimentator_1 | sol01 | **105** | YES | 0 | Rokicki-Dogon ap q=107 mul=433 |
| 2 | research_1 | sol01 | **105** | YES | 0 | Rokicki-Dogon ap q=107 mul=433 |
| 3 | experimentator_1 | sol02 | 104 | YES | 0 | Rokicki-Dogon pp q=103 mul=400 |
| 4 | research_1 | sol02 | 104 | YES | 0 | Rokicki-Dogon pp q=103 mul=400 |
| 5 | experimentator_1 | sol03 | 103 | YES | 0 | Rokicki-Dogon pp q=103 mul=400 |
| 6 | full_1 | sol01 | 102 | YES | 0 | CP-SAT fallback to Singer q=101 |
| 7 | explore_1 | sol05 | 70 | YES | 0 | Beam search k=500 |
| 8 | explore_1 | sol07 | 70 | YES | 0 | Beam search k=800 |
| 9 | explore_1 | sol01 | 69 | YES | 0 | Beam search k=30 |
| 10 | explore_1 | sol02 | 67 | YES | 0 | Beam search k=20 |
| 11 | explore_1 | sol03 | 67 | YES | 0 | Beam search k=50 |
| 12 | explore_1 | sol04 | 67 | YES | 0 | Beam search multi-seed |
| 13 | explore_1 | sol06 | 66 | YES | 0 | Beam search k=500 percentile |
| 14 | explore_2 | sol01 | 0 | NO | 312 | Naive Bose-Chowla p=97 |

**14 solutions total. 13 valid, 1 invalid. New best: 105.**

## Knowledge Changes Summary

### New Ideas (3)
- **idea_021**: Beam Search Greedy (active, confidence 0.6). Ceiling 70 at k=500+.
- **idea_022**: Bose-Chowla Affine Plane Construction (established, confidence 0.95). 105 marks for N=10000.
- **idea_023**: Multiplier Optimization (established, confidence 0.9). Essential for algebraic constructions.

### New Patterns (2)
- **pattern_012**: 105 is the algebraic ceiling for N=10000 (confirmed, confidence 0.95).
- **pattern_013**: Beam search greedy ceiling at 70 (confirmed, confidence 0.85).

### Updated Ideas (3)
- **idea_020**: Rokicki-Dogon — upgraded active→established, confidence 0.5→0.95.
- **idea_019**: CP-SAT — confidence downgraded 0.6→0.5 after 1800s of UNKNOWN.
- **idea_011**: ET Extension — flagged as 3 generations stale.

### Updated Patterns (1)
- **pattern_011**: Greedy ceiling updated 66-69 → 66-70.

### Updated Clusters (3)
- **cluster_001**: Algebraic Constructions — best 102→105, added idea_022 and idea_023.
- **cluster_002**: Search Methods — added idea_021 (beam search).
- **cluster_004**: Exact Methods — updated with gen 5 CP-SAT results.

### Idea Count
- Previous: 23 ideas (10 active, 5 established, 8 debunked)
- After gen 5: 26 ideas (10 active, 8 established, 8 debunked)
- Under the 30-idea threshold — additions are appropriate.

### Stale Ideas
- **idea_005 (Backtracking with Pruning)**: 5 generations stale (first_seen gen 0, never tested).
  Recommend: test or archive in gen 6.

## Strategic Assessment

### What Changed
The pipeline was stuck at 102 for 3 generations with two credible paths forward: Rokicki-Dogon
and CP-SAT. This generation resolved both:
- **Rokicki-Dogon: SUCCESS** — verified, yielding 105 (new best, +3).
- **CP-SAT: STALLED** — 1800s of UNKNOWN for k=103. No progress visible.

The strategic picture is now clear:
1. Algebraic constructions are exhausted at 105.
2. The remaining gap (105 to ~109-114) requires computational search.
3. CP-SAT is the only proven approach but needs much more compute than agent sessions provide.

### What Should Happen Next (Gen 6 Priorities)

| Priority | Action | Expected Outcome |
|----------|--------|-----------------|
| **CRITICAL** | CP-SAT k=106 with 105-mark hint, 4h+ budget | Could find 106 or prove infeasible |
| **HIGH** | Remove-k perturbation of 105-mark set (k=3-10, 100K+ trials) | Unlikely but must be eliminated |
| **HIGH** | Alternative solver evaluation (Gurobi/SCIP/HiGHS for k=106) | Better LP relaxation |
| **MEDIUM** | Binary search on N for k=106 feasibility | Find tractable sub-problem |
| **MEDIUM** | Download Carter-Hunter-O'Bryant paper for exact upper bound | Calibrate remaining gap |
| **LOW** | Test or archive idea_005 (backtracking) | Housekeeping |

---

## Debrief — Evaluator Self-Assessment

### 1. What did I try?

- Read all 14 solutions from 5 agents, verified scores from .score files (no re-evaluation needed)
- Analyzed 5 agent debrief reports
- Created 3 new ideas, 2 new patterns
- Updated 3 existing ideas, 1 existing pattern
- Updated 3 clusters
- Updated full solution-idea map (now covering gens 1-5)
- Updated coverage matrix with gen 5 data
- Identified 7 agent gaps and 1 stale idea

### 2. What information did I lack?

- The exact Carter-Hunter-O'Bryant upper bound for N=10000 (is it 109 or higher?)
- Whether any other 105-mark Sidon set exists in {0..10000} with different structure than
  the Rokicki-Dogon set — this matters for perturbation search (different starting points
  may have different extension potential)
- CP-SAT internal metrics (how close was it to finding k=103? Was it exploring promising
  regions or completely lost?)

### 3. What given facts might be wrong or outdated?

- **problem/description.md** says "theoretical maximum approximately 100 elements." This is
  wrong — the upper bound is ~109-114 and the constructive lower bound is now 105. Should
  be updated.
- **State of Affairs** says "Singer constructions are exhausted." This was technically
  incorrect — it should have said "Singer projective plane constructions are exhausted."
  The Bose-Chowla affine plane construction (distinct from Singer) yields 105.

### 4. Was the State of Affairs accurate?

Partially. It correctly identified:
- Rokicki-Dogon as highest priority (confirmed: yielded +3)
- The 102 Singer ceiling
- CP-SAT as the other credible path

It was wrong about:
- "Singer constructions are exhausted" — should distinguish Singer (pp) from Bose-Chowla (ap)
- Underestimated the Rokicki-Dogon database potential (confidence 0.5 was too low)

### 5. What would I do differently with more context?

- Would have liked to see the full Rokicki-Dogon database metadata (all constructions for
  N≤10000) to identify whether alternative 105-mark sets exist
- Would have liked timing data on CP-SAT's search tree to understand whether longer runs
  are worth pursuing or whether the formulation is fundamentally inadequate

### 6. Specific experiments to run

1. **CP-SAT k=106 with 105-mark hint** — the single most important next step. 4h budget.
2. **Anti-Singer CP-SAT** — forbid top 50 Singer elements to explore novel structures.
3. **Different 105-mark starting points** — are there other Bose-Chowla q=107 configurations
   with multiplier ≠ 433 that also give 105 marks but with different elements? If so, try
   perturbation from each.
4. **Exact upper bound computation** — download arXiv:2310.20032 and compute F(10000) bound precisely.

### 7. What surprised me?

- **Two agents independently solved the same problem identically.** The Architect assigned
  both experimentator_1 and research_1 to download Rokicki-Dogon, producing duplicate work.
  The independent verification is useful but expensive.
- **The 105-mark set is completely maximal** — not a single element can be added. This is a
  stronger result than expected (Singer 102 also has ~43 minimum blockers, but the 105-mark
  set has zero extensible candidates at all).
- **The beam search ceiling is exactly 70** — only +1 over standard greedy after testing
  k up to 800. The greedy basin is remarkably deep and narrow.
- **Singer q=103 with multiplier=400 gives 104**, explaining why previous q=103 attempts
  scored only 102. The multiplier search space was the missing ingredient for 4 generations.

### 8. Helper tools feedback

- Did not use helpers directly (evaluator role is analysis, not solution construction).
- Both experimentator_1 and research_1 independently recommended a `greedy_extend(S, N)`
  helper in `helpers/core.py`. This is a clear gap — nearly every solution agent reimplements
  this function.
- `helpers/singer.py` should be updated to search the full multiplier space, or a companion
  `helpers/bose_chowla.py` should be created for the affine plane construction.
- A `helpers/rokicki_dogon.py` that hardcodes the 103-105 mark sets as static data would
  prevent future agents from re-deriving them.

### 9. Time budget

Sufficient. All evaluation steps completed. The knowledge base is well-maintained and the
strategic picture is clear. If I had more time, I would:
1. Analyze the difference structure of the 105-mark set in detail (which differences are
   used, which are free) to quantify the perturbation landscape
2. Compare the 105-mark set element distribution against Singer q=101 to understand why
   Bose-Chowla yields more elements
3. Write a more detailed analysis of the CP-SAT blocking issue and whether the formulation
   itself needs improvement
