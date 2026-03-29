# Manifest Reasoning — Generation 9

## Situation Assessment

**Score trajectory:** C = 1.5028628684790137 (gen 8 best). Improvements per generation: gen5 -8.8e-9, gen6 -2.6e-8, gen7 -3.6e-9, gen8 -4.1e-10. The improvement magnitude is decreasing roughly one order of magnitude every 1-2 generations. We are deep in micro-optimization territory.

**Score progression display shows a false plateau.** Due to 4-decimal display precision (BUG: unfixed for 5 gens), the progression table shows gens 4-8 all at "1.502863", making it look like a stall. In reality, every generation since gen 5 has improved C. This is an operator issue, not an agent issue.

**State of Affairs is from gen 7.** The consistency review ran before gen 8 but the SoA was not updated for gen 8 findings. Key gen 8 results (quadruplet perturbation, interleaving confirmation, FFT padding validation, downsampling destruction) are in the evaluator report but not in the SoA. Agents will need to read gen 8 reports to get current context.

**Key gen 8 findings:**
1. Quadruplet perturbation works: 8015 improvements, -4.13e-10 (idea_022)
2. Interleaving confirmed by two independent agents (pattern_014)
3. FFT padding validated — all improvements are real (pattern_016)
4. Downsampling N=30k to intermediate N destroys structure (pattern_015)
5. Momentum triplets on unmodified gen 7 best: 0 improvements — triplets exhausted without prior interleaving
6. Coord descent on triplet-modified array: 2008 new improvements — confirms interleaving

**Helpers status:** 7 deployed helpers in `problem/helpers/` but README says "none yet". This has been flagged for 3 generations. The `coordinate_descent.py` helper was built in gen 8 but not validated at N=30k and not deployed.

## Agent Mix Rationale

5 agents total: 2 exploits, 2 explores, 1 experimentator.

### exploit_1 (opus, 2700s) — Full Interleaved Multi-Order Cycle

**THE single highest-priority experiment.** The interleaving hypothesis is confirmed: each perturbation order unlocks new improvements for lower-order methods. But nobody has run a complete cycle (coord → triplet → quadruplet → repeat until all converge). Gen 8 ran each method independently or sequentially. The full cycle is the logical completion.

**Why opus:** This is precision work on the frontier. The agent needs to implement three different methods correctly, handle edge cases (non-negativity clamping, integral preservation), and make real-time decisions about when to move between methods. Worth the premium.

**Why 2700s:** Gen 8 exploit_1 used 1800s and ran out of time mid-interleave (only completed 1 coord descent round). The full cycle needs multiple passes of all three methods. 2700s gives room for 3-4 complete cycles.

### explore_1 (sonnet, 1800s) — Quintuplet Perturbation

**The radical exploration direction (25% diversity budget).** The perturbation hierarchy has shown: pairs (1 improvement), triplets (160), quadruplets (8015). Quintuples are the mathematical next step. Even if the per-move delta is tiny (~1e-11), confirming or denying the pattern is valuable.

**Why sonnet:** The implementation is straightforward (extend the quadruplet code to 5 elements). The mathematical reasoning is the same pattern.

**Why 1800s:** Quintuplet trials are ~same cost as quadruplet (~10 incremental updates per trial). 50k trials + follow-ups ≈ 20 min compute + overhead.

### exploit_2 (sonnet, 1500s) — Optimized Quadruplet with Momentum

**Different approach from exploit_1.** While exploit_1 cycles between methods, exploit_2 focuses on maximizing quadruplet output with momentum-after-acceptance chains. Gen 8 showed 8015 improvements from quadruplets — there may be more with momentum (retry accepted moves at larger step, nearby indices). Also drops S2 (consecutive neighbors, weakest strategy) and adds a new S4 (3 large + 1 random) to test whether focusing on large elements is more efficient.

**Why not opus:** The technique is a variation on gen 8's quadruplet code, not fundamentally new reasoning.

### experimentator_1 (sonnet, 900s) — Batch Evaluator + README Update

**Two deliverables that address recurring system recommendations:**

1. **Vectorized batch trial evaluator** (Priority 4 from system critic). The Python loop at 100-220 trials/s is THE bottleneck for all perturbation methods. A vectorized K=100 batch evaluator could reach 1000+ trials/s, transforming what's feasible within a session. This is the single highest-impact infrastructure investment.

2. **helpers/README.md update** (Priority 2 from system critic, flagged 3 consecutive gens). 7 helpers are deployed but undocumented. Agents waste 8-16 turns reading individual files.

**Why sonnet:** Helper building is implementation work. README is documentation. Neither requires opus-level reasoning.

**Why 900s:** Gen 8 experimentator took 901s for one helper. This one builds one helper + docs. The batch evaluator is conceptually simpler (no accept/reject logic, just prediction).

### explore_2 (sonnet, 2100s) — N=5000 LP Tractability Study

**Closes a persistent open question (Priority 7 from system critic).** LP at intermediate resolution has been discussed since gen 6 with no conclusive answer. Gen 8 explore_2 tried to answer it by downsampling (failed: C=7+). The correct approach is optimization from scratch at N=5000, which requires 30-60 min compute.

**Why this matters:** If LP is tractable at N=5000 with <500 tight constraints, it opens a completely different optimization avenue that doesn't rely on the TTT-Discover array. If it fails (plateau at N=5000 too), we archive idea_020 and stop spending agents on it.

**Why 2100s:** The compute budget is 45-90 min (gradient descent + coord descent + LP). 2100s accommodates this with margin.

## What I Deliberately Did NOT Do

1. **No research agent.** All relevant literature has been identified (TTT-Discover, AlphaEvolve). No new papers to survey. Research would be wasted compute.

2. **No genetic crossover.** All top-10 solutions are variants of the TTT-Discover 30k array with micro-optimizations. Crossing two nearly-identical solutions produces nothing useful.

3. **No full agent.** The gen 8 full agent's LP attempts failed. The LP question is better addressed by explore_2's systematic approach.

4. **No second experimentator for coordinate_descent.py validation.** The system critic recommended validating it at N=30k. I'm deferring this: exploit_1 will use inline coord descent (proven in gen 5-8) rather than relying on the unvalidated helper. If the batch evaluator helper is delivered, it supersedes coordinate_descent.py for most use cases anyway.

5. **No agent dedicated to fact_002 or score progression display.** These are operator-level changes (edit a knowledge file, edit orchestrator.py). Agents can't fix them efficiently. Flagging for manual update.

## Timeout Justification

| Agent | Timeout | Rationale |
|-------|---------|-----------|
| exploit_1 | 2700s | Gen 8 exploit_1 took 1800s for incomplete interleave. Full cycle needs 3-4 passes. |
| explore_1 | 1800s | 50k quintuplet trials (~8 min) + follow-ups (~5 min) + overhead |
| exploit_2 | 1500s | 60k quadruplet trials with momentum (~10 min) + follow-ups |
| experimentator_1 | 900s | Gen 8 experimentator took 901s for one helper |
| explore_2 | 2100s | 45-90 min compute for gradient descent + coord descent + LP |

## Risks

1. **exploit_1 could timeout mid-cycle again.** Mitigated by saving after each cycle.
2. **Quintuplets might find zero improvements** — the hierarchy may terminate at quadruplets. This is still valuable information (closes the question).
3. **Batch evaluator approximation might be too noisy** for small deltas (~1e-9). The experimentator should test accuracy at multiple delta scales.
4. **N=5000 gradient descent might not reach C < 1.510** within the time budget. The LP question can still be partially answered with C ≈ 1.51.
5. **All agents start from the same gen 8 best.** Since they run in parallel, any cross-pollination happens in gen 10.
