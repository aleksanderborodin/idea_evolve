# Generation 1 — Strategic Reasoning

## Situation Assessment
- **Generation 1 cold start.** No population, no clusters, no coverage data.
- **Baseline:** C = 1.5185 from initial program (JAX Adam, N=600, 40k steps).
- **Target:** C <= 1.5053 (lower is better). Gap: ~0.013 (0.88% improvement needed).
- **Known bounds:** 1.28 <= C <= 1.5098. The target is just below the upper bound.

## Agent Mix: 2 explore + 1 full + 1 research

Following cold-start rules. No exploit/genetic/experimentator — nothing to refine or cross.

### explore_1 — Gradient optimization improvements
**Direction:** Optimizer tuning, higher resolution, smarter initialization.
**Rationale:** The baseline is a straightforward Adam run. There is low-hanging fruit in (a) more steps, (b) higher N, (c) better initializations, (d) alternative optimizers like L-BFGS. These are incremental but likely to yield quick improvements.

### explore_2 — Analytical/structural approaches
**Direction:** Symmetry enforcement, parametric function families, sparse constructions, regularization.
**Rationale:** Orthogonal to explore_1. Instead of tuning the optimizer, this explores whether the function *shape* matters more than the optimization algorithm. Symmetry constraints halve the search space. Known function families (Gaussians, cosines, B-splines) provide structured search. The Sidon set connection hints at sparse solutions.

### full_1 — Robust combined baseline
**Direction:** Multi-restart gradient descent with all obvious improvements stacked.
**Rationale:** Combines the most promising incremental improvements (higher N, more steps, symmetry, non-negativity enforcement) into one reliable solution. Acts as a safety net — even if the explores go in unusual directions, full_1 should produce a solid improvement.

### research_1 — Mathematical survey
**Direction:** Literature survey on the first autocorrelation inequality.
**Rationale:** The problem has known mathematical structure (Sidon sets, additive combinatorics). Understanding the theory will inform gen 2+ strategy. If the extremal function has known properties (e.g., specific symmetry, support pattern), we can exploit those directly.

## Timeouts
- **explore_1, explore_2:** 1200s each. First gen needs room for multiple iterations and potential slow higher-resolution runs.
- **full_1:** 900s. Straightforward work, doesn't need extra time.
- **research_1:** 600s. Reading and writing a report, no code iteration needed.

No prior timing data to calibrate against.

## Parallel Groups
All 4 agents in one parallel group. No dependencies between them. Maximizes throughput.

## What I Deliberately Did Not Do
- **No exploit/genetic:** Nothing to refine or cross yet.
- **No experimentator:** No specific hypotheses to test yet — need gen 1 results first.
- **No opus agents:** Gen 1 is exploratory. Sonnet is cost-efficient for broad search. Will escalate to opus in gen 2+ for precision refinement.
- **Did not launch 3+ explores:** 2 explores with orthogonal directions plus 1 full gives sufficient diversity for gen 1 without over-spending.

## Risks
1. **All agents converge to same local minimum.** Mitigated by giving explore_2 a fundamentally different direction (structural vs. optimizer tuning).
2. **Research agent produces unusable findings.** Low risk — even vague mathematical context helps future strategy.
3. **High-N runs timeout.** explore_1 has 1200s timeout and instructions to use multi-scale if needed.
