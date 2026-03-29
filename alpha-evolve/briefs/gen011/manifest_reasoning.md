# Manifest Reasoning — Generation 11

## Situation Assessment

**Best score:** C = 1.5028628681165177 (gen010_explore_2_sol01)
**Target:** C ≤ 1.5053 — beaten since gen 3 by 0.0024.
**Trajectory:** Decelerating. Gen 8: -4.1e-10, Gen 9: -2.6e-10, Gen 10: -1.1e-10. Extrapolating: ~5e-11 this gen.
**Diversity:** Zero. Every frontier solution is ultra-fine CD on the TTT-Discover 30k array.

Gen 10 was highly productive in closing open questions:
- Minimax LP (idea_023): **debunked** — 68k trials, 0 improvements. Solution is locally minimax-optimal.
- Pattern_020: **confirmed** — all multi-element integral-preserving moves exhausted.
- A/B test: CD-only strictly beats CD+multi-element interleaving.
- Three engineering discoveries: top-K screening (50x speedup), incremental drift quantified, no convergence at 1e-13 scale.

The only productive technique remains ultra-fine coordinate descent. The only untested direction with theoretical justification is non-integral-preserving multi-element moves.

## Agent Mix Rationale

**4 agents total** (conservative — matching gen 10 agent count minus the experimentator overhead).

### exploit_1 — Per-round FFT resync CD (HIGHEST PRIORITY)
**Why:** This is Experiment 1 from the system critic (highest priority). Gen 10 exploit_1 discovered drift of ~1.4e-12/round and used resync every 5 rounds. Per-round resync has never been tested. It should produce cleaner improvements and reveal the true CD convergence rate without drift artifacts.
**Model:** sonnet (CD is mechanical, doesn't need opus reasoning).
**Timeout:** 2700s (base array load takes ~490s, need max time for CD rounds).

### exploit_2 — Adaptive delta range + multi-trajectory competition
**Why:** Tests Experiments 2 and 4 from the system critic. Two questions: (a) does focusing on productive deltas (1e-14 to 1e-11) yield more improvement per second than the broad grid? (b) does running multiple trajectories with different random orderings exploit path-dependent variance (~1e-11 observed in gen 10)?
**Model:** sonnet.
**Timeout:** 2700s (needs time for both phases).

### explore_1 — Non-integral-preserving multi-element moves
**Why:** This is the only remaining untested direction with theoretical backing. CD improves C by changing the integral (pattern_024). All exhausted multi-element approaches required integral preservation. Removing this constraint opens a fundamentally different optimization pathway. Three agents and the evaluator independently flagged this as highest priority.
**Model:** sonnet.
**Timeout:** 1800s (includes ~490s array load + ~800s pair testing + remaining for CD follow-up).

### experimentator_1 — Build topk_screened_cd helper
**Why:** **Mandatory** — system critic has recommended this for 2+ consecutive generations (Priority 7 in gen 10). Both exploit_1 and explore_2 from gen 10 independently reimplemented similar fast screening inline, wasting 30-50 turns each. A validated helper saves all future agents this engineering overhead.
**Model:** opus (helper quality is critical — used by all future agents).
**Timeout:** 1200s (gen 10 experimentator took 461s for plateau_analyzer; this is more complex).

## What I Deliberately Did NOT Include

1. **Research agent.** No new papers or external techniques to investigate. The problem is now in pure engineering/optimization territory.

2. **Full agent.** No fundamentally new end-to-end approach to attempt. All from-scratch approaches cap at C~1.509, far from the frontier.

3. **Genetic crossover.** All frontier solutions are variants of the same TTT-Discover 30k array. Crossing two near-identical arrays is pointless.

4. **More explores for radical directions.** The coverage matrix shows all alternative approaches (GD, SA, LP, multi-element, gradient methods) are exhausted. The only radical direction left is non-integral-preserving moves, which explore_1 covers.

5. **3rd exploit.** Diminishing returns — all exploits start from the same array and apply the same technique. Two exploits testing different engineering parameters (resync frequency, delta range, trajectory diversity) is sufficient.

## Timeout Calibration

From gen 10 timing:
- exploit_1: 2087s work (no wrap-up needed)
- exploit_2: 791s work
- explore_1: 1372s work
- explore_2: 2434s (including wrap-up)
- experimentator_1: 461s work

Set 2700s for exploits (they need maximum CD time after the ~490s array load). 1800s for explore (pair testing is faster than sustained CD). 1200s for experimentator (building + testing a helper is bounded work).

## Risks

1. **Array load bottleneck.** The best solution (gen010_explore_2/sol01.py) runs live CD during entrypoint(), taking ~490s. Three agents loading it simultaneously = 3× the compute with identical work. If the experimentator doesn't finish the helper in time, gen 12 will have the same problem.

2. **Non-integral-preserving moves may also be null.** If the solution is locally optimal for ALL 2-element perturbations (not just integral-preserving ones), then we've exhausted the entire 2-element search space. This would be a strong negative result but still valuable.

3. **Exploit convergence data may be noisy.** Per-round FFT resync changes the algorithm enough that we can't directly compare convergence rates with gen 10 (which used 5-round resync). The comparison is still informative but not apples-to-apples.

4. **Diminishing practical value.** Target beaten since gen 3. We're optimizing at the 12th decimal place. The user may want to declare convergence and stop. Open Question 4 from the State of Affairs.
