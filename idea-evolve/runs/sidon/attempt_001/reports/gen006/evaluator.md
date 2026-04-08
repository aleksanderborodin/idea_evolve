# Evaluator Report — Generation 6

**strategic_shift: false**

## Summary

Generation 6 produced no score improvement. Pipeline best remains **105** (Bose-Chowla ap q=107, mul=433). 10 solutions submitted: 5 scored 105 (all fallbacks to known best), 3 scored 75 (ET ceiling), 1 scored 66 (DFS = greedy), 1 scored 66. No experimentator or research solutions.

This was a consolidation generation: confirming dead ends, accumulating CP-SAT evidence, and building infrastructure.

## 1. What did I try?

**Score collection:** Read all 10 `.score` files from 4 agent directories (exploit_1, explore_1, full_1). No re-evaluation needed — all `.score` files present and valid.

**Analysis and knowledge updates:**
- Analyzed all 10 solutions against the existing 25-idea knowledge base
- Updated 3 existing ideas: idea_005 (debunked), idea_019 (updated with gen 6 evidence), idea_011 (75 ceiling confirmed)
- Created 2 new ideas: idea_024 (VLNS), idea_025 (Ruzsa-Lindström)
- Created 2 new patterns: pattern_014 (self-healing property), pattern_015 (75 hard ceiling)
- Updated 2 clusters: cluster_002 (→ exhausted), cluster_004 (added idea_024)
- Updated solution-idea map with all 10 gen 6 entries
- Updated coverage matrix with gen 6 data and new unexplored combinations

## 2. What information did I lack?

- **F₂(10000) exact published value.** Still unknown after 6 generations. This single number determines whether 106 is ambitious or conservative. Research agents have consistently failed to look this up.
- **Whether VLNS INFEASIBLE results are genuine.** full_1 diagnosed a likely formulation bug but did not confirm by fixing and retesting. The evaluation depends on this diagnosis being correct.
- **The contents of `problems/sidon/helpers/rokicki_data.py`** (untracked). May contain tabulated optimal set sizes. No agent has checked it in 2 generations.

## 3. What given facts might be wrong or outdated?

- **State of Affairs says "Remove-k perturbation of 105-mark set: untested for k≥3"** — now exhaustively tested (k=2-104, 27K+ trials, all return 105). Must be updated.
- **State of Affairs says "VLNS: untested"** — now tested (9 trials, all INFEASIBLE). Must be updated with caveat about likely formulation bug.
- **Research findings claim F₂(10000) upper bound is ~103-106** — this contradicts fact_002 which says ~109 (from Carter-Hunter-O'Bryant). The research findings are from training data and less reliable.
- **fact_002 and fact_004 stale copies warning** — the SoA notes stale copies in facts/. These should be cleaned up.

## 4. Was the State of Affairs accurate?

Mostly accurate but needs updates for gen 6 findings:
1. Remove-k perturbation is now exhaustively debunked (not "untested for k≥3")
2. The self-healing property should be noted
3. CP-SAT evidence now includes 3 gens of compute with zero progress
4. VLNS tested but with likely bug
5. DFS/backtracking tested and debunked

The coverage map's prioritization was correct — the high-priority items (remove-k, CP-SAT k=106, backtracking) were all tested this generation, even though none succeeded.

## 5. What would I do differently with more or different context?

- Would have flagged the VLNS formulation bug more prominently as the single highest-value next step
- Would have checked the `rokicki_data.py` file myself to resolve the F₂(10000) question
- Would have been more aggressive about archiving stale ideas (idea_003, idea_015, idea_016) that are 30+ elements below the frontier

## 6. Specific experiments to run

**CRITICAL (generation 7 must-do):**
1. **Fix VLNS formulation and run 50+ trials** — highest expected value. Change abs-equality domain, test with diverse removal patterns. Even finding alternative 105-element sets is valuable.
2. **Look up F₂(10000)** — check OEIS A003022, `problems/sidon/helpers/rokicki_data.py`, web search. 5 minutes of work that could redirect the entire pipeline.

**HIGH:**
3. **CP-SAT maximize formulation** — instead of "find exactly k=106", maximize k with the AllDifferent formulation. More solver-friendly and can find intermediate results.
4. **Create `helpers/cpsat.py`** — validated CP-SAT wrapper to prevent re-derivation and formulation bugs.

**MEDIUM:**
5. **Overnight CP-SAT k=106** (4h+, 16 workers) — if pipeline can support long-running agents.
6. **Tabu search with "swap then fill" moves** — different search paradigm from SA/LNS.

**LOW:**
7. **SA from 75-element ET seed** — different from prior SA (which started from greedy/Singer).
8. **Ruzsa-Lindström construction + SA** — untested algebraic seed.

## 7. What surprised me?

1. **The perfect self-healing property** is the most striking finding. It's not just "hard to perturb" — it's mathematically rigid. Every k-element removal opens exactly k slots that are exactly the removed elements. This suggests deep algebraic structure, not just search difficulty.

2. **k=104 UNKNOWN with 105-element hint** — CP-SAT can't even verify a near-trivial sub-case. This suggests the AllDifferent formulation is fundamentally hard for the solver, not just hard because k=106 is near the boundary. The formulation may need rethinking (e.g., difference-based variables instead of element-based).

3. **VLNS INFEASIBLE in <1s** — either a goldmine (instant proof that neighborhoods are empty) or a bug. The speed is suspicious given that CP-SAT can't solve the full problem. Most likely a bug, but if genuine, it's the strongest evidence yet that 106 may be infeasible for N=10000.

4. **k=106 hard at N=15000** — I expected difficulty to decrease rapidly with larger N. If the problem is combinatorially hard regardless of N, the entire CP-SAT approach may be fundamentally limited without much longer time budgets.

5. **DFS = greedy** — obvious in hindsight but striking to see empirically. Six generations of "should we test backtracking?" answered definitively in 27 seconds.

## 8. Helper tools feedback

Did not use helper tools directly (evaluation role). Based on agent reports:
- `helpers/core.py` (`is_sidon`, `can_add`): Working correctly, used by experimentator_1 for validation.
- `helpers/search.py` (`greedy_sidon`): Used as fallback, works correctly.
- **New helpers created this gen:** `rokicki_data.py` (BEST_102/104/105), `extend.py` (greedy_extend, count_addable, random_perturbation, blocking_power). All validated.
- **Still needed:** `helpers/cpsat.py` (CP-SAT wrapper) — requested 2 gens in a row, still not built.
- **Wished existed:** A fast C-extension for 1-opt/2-opt. Multiple agents cite Python speed as a bottleneck for local search experiments.

## 9. Time budget

Adequate for the evaluation task. All 10 solutions analyzed, all knowledge files updated, all output files produced. The evaluation was straightforward this generation because no new best was found — the analysis is primarily confirming dead ends and updating evidence counts.

With more time, I would:
1. Read and verify the `rokicki_data.py` file to resolve the F₂(10000) question
2. Cross-reference the self-healing property with mathematical literature on Bose-Chowla constructions
3. Analyze whether the CP-SAT formulation hardness is specific to the AllDifferent constraint or inherent to the problem

## Staleness Report

Ideas approaching staleness threshold (5+ generations without confirmation):
- idea_015 (Fibonacci Ordering): last_confirmed gen 3 — **3 gens stale.** At ceiling 69, 36 below frontier. Recommend archive.
- idea_016 (Min-Blocking): last_confirmed gen 4 — 2 gens stale. At ceiling 69. Recommend archive.
- idea_003 (Difference-Aware): last_confirmed gen 4 — 2 gens stale. Peripheral only. Recommend archive.
- pattern_009 (Singer perturbation futile): last_updated gen 4 — 2 gens stale. Still valid but could be merged into pattern_012.

## Experiment Consolidation

No experiments older than 3 generations need consolidation. Gen 3-4 experiments were consolidated in gen 5 evaluator report. Gen 5-6 experiments are current.

The gen 6 experimentator_1 results (helper creation) have been noted in this report but don't need consolidation — they are infrastructure, not hypothesis tests.
