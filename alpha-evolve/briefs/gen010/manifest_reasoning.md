# Manifest Reasoning — Generation 10

## Situation Assessment

**Best score:** C = 1.5028628682228971 (gen009_exploit_1_sol01)
**Target:** C ≤ 1.5053 — beaten since gen 3.
**Trajectory:** Exponentially decaying improvements: -3e-4 → -9e-9 → -2.6e-8 → -3.6e-9 → -4.1e-10 → -2.6e-10.
**Generations since target beaten:** 7.

The system is deep in the refinement phase. All competitive solutions derive from the TTT-Discover 30k array. Gen 9's key discovery was that ultra-fine coordinate descent deltas (1e-8 to 1e-11) reopened 4943 improvements after apparent convergence — but we don't know where the true float64 floor lies. Three critical open questions remain from gen 9:

1. **Where is the precision floor?** Does improvement continue at 1e-12 and below?
2. **Does ordering matter?** Is the optimal sequence [multi-element → ultra-fine CD] or [ultra-fine CD alone]?
3. **Can minimax perturbation (idea_023) break through where single-peak perturbation failed?**

Gen 10 is designed to answer all three definitively.

## Agent Selection Rationale

### exploit_1 (opus, 2700s) — Geometric Delta Grid to Float64 Limits

**Why:** The single most important scientific question is whether improvements continue at 1e-12 scale. Gen 9 tested down to 5e-11 and found 375 improvements. A comprehensive sweep from 1e-14 to 1e-1 with 100 geometric points will map the entire improvement landscape by delta scale. This is the convergence criterion experiment.

**Why opus:** Precision matters — this agent must implement the delta grid correctly and track per-decade statistics without errors.

**Timeout 2700s:** Gen 9 exploit_1 took 2612s. Geometric grid with 100 delta values over 30k elements is computationally heavy.

### exploit_2 (opus, 2700s) — A/B Ordering Test + Checkpoint Scoring

**Why:** Pattern_020 (ultra-fine CD subsumes multi-element) was inferred, not tested. This agent runs Path A (ultra-fine CD only) vs Path B (triplets+quads → ultra-fine CD) on the same starting array. Quick win: also scores the gen 9 exploit_2 checkpoint that timed out.

**Why opus:** Must implement two clean parallel paths and compare rigorously.

**Timeout 2700s:** Gen 9 exploit agents needed 1500-2612s. Two paths plus checkpoint scoring needs full budget.

### explore_1 (sonnet, 1800s) — Minimax Multi-Element Perturbation (idea_023)

**Why:** Highest-priority untested idea. The 13 near-tied plateau positions are the structural reason single-peak perturbation fails after ultra-fine CD. Minimax addresses this directly with a small LP (13 constraints, 2-3 variables). If it works, it reopens multi-element improvement after the current tools are exhausted.

**Why sonnet:** The LP implementation is straightforward (scipy.optimize.linprog). The core insight is algorithmic, not requiring opus-level precision.

**Timeout 1800s:** Gen 9 explore_1 took 904s. Minimax adds LP overhead per trial but the LP is tiny.

### explore_2 (sonnet, 1800s) — Batch Evaluator Integration + Extended Triplets

**Why:** Gen 9 experimentator built batch_trial_evaluator (46x speedup) but no agent has used it in production. Gen 9 explore_1 found 150 triplet improvements in 20k trials with rate not plateauing. With batch pre-filtering, 500k+ screened triplets should find hundreds more. This validates the helper infrastructure and pushes the triplet approach further.

**Why sonnet:** Integration task, not requiring opus precision.

**Timeout 1800s:** Triplet search is computationally bounded by wall time, not turns.

### experimentator_1 (opus, 900s) — plateau_analyzer Helper

**Why:** Priority 7 from system recommendations (2 consecutive generations requesting it). The plateau_analyzer is needed by explore_1 for minimax and by future agents for understanding the autoconvolution plateau structure. Without it, each agent re-implements plateau analysis ad hoc.

**Why opus:** Helper code must be numerically correct (gradient computation at the plateau). One wrong sign destroys all downstream minimax work.

**Timeout 900s:** Gen 9 experimentator took 647s. Helper build + test is well-scoped.

## What I Chose NOT to Do

1. **Research agent.** No new papers or domain knowledge to find. The problem is fully characterized. All remaining improvement comes from technique refinement.

2. **Full agent.** No fundamentally different approach to try from scratch. The TTT-Discover 30k array is the only competitive starting point. Building from random init caps at C≈1.509.

3. **Genetic crossover.** All competitive solutions derive from the same array via different optimization paths. Crossing two near-identical arrays produces a near-identical array with no structural novelty.

4. **N=5000 warm-start experiment.** Low priority — scientifically interesting but not on the improvement path. N=5000 floor is C≈1.517, far from the frontier.

5. **Second experimentator.** The README fix (still saying "none yet" despite 8 deployed helpers) is important but doesn't block any agent. The plateau_analyzer is more urgent.

## Timeout Calibration

| Agent | Gen 9 timing | Gen 10 timeout | Rationale |
|-------|-------------|----------------|-----------|
| exploit_1 | 2612s | 2700s | Geometric grid with 100 deltas is heavier than gen 9's 3-pass approach |
| exploit_2 | 2838s (timeout) | 2700s | Two paths but with time guards — should complete within budget |
| explore_1 | 904s | 1800s | Minimax LP adds overhead; generous budget for implementation |
| explore_2 | 1057s | 1800s | 500k trials with batch evaluator needs wall time |
| experimentator_1 | 647s | 900s | Well-scoped helper build |

## Risk Assessment

1. **Incrementalism risk: MEDIUM.** All 5 agents operate on the same 30k array. But each answers a distinct question — this is a diagnostic generation, not a pure exploitation one. If all three exploit/explore approaches find zero improvements, that's a valid and useful result (convergence declaration).

2. **explore_1 minimax failure risk: HIGH.** If the K plateau gradients are linearly dependent, the minimax LP has no improving direction. This is plausible given the autoconvolution structure. But even a null result closes the last untested idea.

3. **Batch evaluator integration risk: LOW.** The helper is tested and deployed. Worst case, explore_2 falls back to sequential evaluation.

4. **Time budget risk: LOW.** All briefs include mandatory time-budget guards. Gen 9 exploit_2's timeout should not recur.
