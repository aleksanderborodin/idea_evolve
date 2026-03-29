# System Critic Debrief — Generation 4

**Agent:** System Critic
**Generation:** 4

---

## 1. What Did I Try?

### Files Read

1. `reports/gen004/evaluator.md` — detailed evaluator analysis with specific findings
2. `reports/gen004/evaluator_debrief.md` — completion status and output summary
3. `reports/gen004/explore_1.md` — SA timeout post-mortem
4. `reports/gen004/exploit_1.md` — warm-start smooth-max Adam failure analysis
5. `reports/gen004/exploit_2.md` — upsample + polish failure analysis
6. `reports/gen004/research_1.md` — TTT-Discover retrieval success
7. `population/gen004/explore_1/observations.md` — detailed SA budget breakdown
8. `population/gen004/exploit_1/observations.md` — benchmarking data (1.8ms/step at N=1319)
9. `population/gen004/research_1/observations.md` — full SOTA table and notebook structure
10. `knowledge/state_of_affairs.md` — current state (gen 3, stale)
11. `feedback/system_recommendations.md` — gen 3 recommendations, status tracking
12. `feedback/agent_gaps/gen004.md` — evaluator's gap analysis
13. `history/generations/gen004.md` — generation snapshot
14. `history/coverage_matrix.md` — full coverage table

### Analysis Performed

- Compared gen 4 outcomes against gen 3 recommendations to track recommendation adherence
- Identified the sequential-group success (research before exploit) vs brief-adaptation failure
  (exploit agents still used old warm-start target)
- Traced the three-generation pattern of SA timeouts to the common root cause (no timing data
  in briefs)
- Evaluated pattern_007's strategic implications for gen 5
- Identified six untested experiments across the debrief reports and prioritized them by ROI

---

## 2. What Information Did I Lack?

- **The actual Architect brief for gen 4.** I don't know whether it said "warm-start from
  population/best.py" or "check research_1 output first." Knowing the exact brief wording
  would tell me whether the sequential-group failure is a brief-writing problem or an agent
  compliance problem. I inferred it was a brief specificity issue from the agents' behaviors.

- **Whether the Consistency Review ran before gen 4.** The gen 3 Priority 2 recommendation
  said it should. The State of Affairs is still dated gen 3. Either the review ran and didn't
  update the SoA, or it didn't run. The system_recommendations.md status table shows "UNCLEAR."

- **Exact timing data for N=23 gradient steps.** exploit_1 benchmarked N=1319 (1.8ms/step)
  but not N=23. I estimated ~0.5ms based on problem size ratio. The SA experiment budget
  calculations depend on this estimate being roughly correct.

- **The gen 4 Architect manifest.** I couldn't verify whether exploit agents were told to
  check research_1's output directory. The manifest would show the actual parallel_groups
  structure and brief instructions.

---

## 3. What Given Facts Might Be Wrong or Outdated?

- **State of Affairs priority ("warm-start smooth-max Adam")** — CONFIRMED WRONG by gen 4.
  Pattern_007 closes this approach. The SoA must be updated before gen 5.

- **research_1's recommendation in debrief:** "Warm-start smooth-max Adam from TTT-Discover
  30k array: Convert to raw_params via inv_softplus, run T=0.005→0.0001 schedule. May find
  improvements." — This recommendation was made before pattern_007 was processed. Given that
  pattern_007 says smooth-max Adam can't improve published solutions, this recommendation is
  already contradicted by gen 4's own findings. The Evaluator correctly tagged it as low-priority
  in the coverage matrix, but the research_1 debrief may confuse future agents who read it.

- **"ThetaEvolve at 1.50313 = our best.py"** — Approximately correct but the rounding is
  tricky. Our best.py shows 1.5031635; ThetaEvolve is listed as 1.50313 in the SOTA table
  (5 decimal rounding). The underlying arrays may be identical or slightly different.

---

## 4. Was the State of Affairs Accurate?

**Mostly no for gen 5 planning purposes.** The gen 3 State of Affairs was accurate *at the time
it was written*, but gen 4 has invalidated its two main strategic recommendations:

1. "Priority 1: Warm-start smooth-max Adam from 1.5032 array" — now proven impossible (pattern_007)
2. "Current SOTA: Yuksekgonul et al. (Jan 2026) C≤1.5029 but no public array yet" — now retrieved
   (TTT-Discover, C=1.50286, 30k array)

The structural description (gradient-descent floor at 1.509, coarse-to-fine works at N=80→600,
multi-seed diversity) remains accurate.

The State of Affairs MUST be rewritten before gen 5. It's the highest-read document in the
knowledge hierarchy and it's describing a strategy that gen 4 proved doesn't work.

---

## 5. What Would I Do Differently With More or Different Context?

- If I had the gen 4 Architect briefs: I could definitively diagnose whether the exploit agents
  failed to adapt to research_1's output because of brief wording or agent compliance. This
  would sharpen Priority 3 (brief adaptation) into either a template fix or a compliance issue.

- If I had timing data for N=23 operations: I could provide exact step counts for the gen 5
  SA brief rather than estimates with safety margins.

- With more time: I would analyze whether the TTT-Discover 30k array's structure (uniform
  low values, gradual rise, terminal spike) is fundamentally different from the AlphaEvolve
  1319-element structure in a way that might make projected gradient descent more effective
  for one vs the other.

---

## 6. Specific Experiments to Run

Detailed in `experiment_suggestions.md`. Summary order:

1. **Projected gradient descent** (CRITICAL) — direct f-space optimization, bypasses
   softplus dead-zone. First real test of whether we can improve any published solution.

2. **Sensitivity-guided coordinate descent** (HIGH) — ∂C/∂f[i], top-500 sensitive elements,
   ±δ perturbations. Low cost, may find micro-improvements.

3. **Calibrated SA at N=23, reduced budget** (HIGH) — explore_1's correct protocol,
   2 seeds × 100 iters × 300 steps × 5k coarse steps. Fits in timeout.

4. **Warm-start from Cell 47 (N=600, C=1.5053)** (HIGH) — tests pattern_007 at N=600
   resolution. If smooth-max Adam can improve a 600-element published solution, it opens
   a whole class of experiments.

5. **Verify AlphaEvolve V2 identity** (MEDIUM) — closes the ThetaEvolve mystery.

6. **Ultra-conservative warm-start at T=0.0001 from TTT-Discover** (MEDIUM) — last test of
   smooth-max framework before abandoning it entirely.

---

## 7. What Surprised Me?

1. **The research pipeline has a 2-for-2 record on finding SOTA arrays.** gen 3: AlphaEvolve
   1.5032. gen 4: TTT-Discover 1.50286. This is remarkable — a general-purpose agent using
   web search has found the state of the art in two consecutive generations. The research
   agent type is currently the pipeline's highest-ROI component.

2. **Exploit agents didn't use research_1's output despite sequential ordering.** The gen 3
   Priority 1 recommendation (sequential groups) was implemented, but both exploit agents
   still warm-started from the old best (AlphaEvolve 1.5032) rather than the new best
   (TTT-Discover 1.50286). Sequential ordering is necessary but not sufficient — the brief
   needs to explicitly instruct agents to check and adapt.

3. **Pattern_007 is the most actionable finding in 4 generations.** It definitively closes
   an entire class of experiments (smooth-max Adam warm-start) and forces the pipeline to
   find new optimization approaches. This is exactly the kind of finding the pipeline is
   supposed to produce, and it changes strategy clearly.

4. **explore_1's implementation was completely correct except for the budget.** The sigma
   formula (0.05×std), cold inner optimizer, N=23 resolution, calibration loop — all correct,
   directly addressing the three gen 3 failure modes. A 10× computation overrun is the only
   thing that prevented what might have been the first successful SA run. Frustrating.

---

## 8. Helper Tools Feedback

No helpers from `problem/helpers/` were used by any gen 4 agent. This is expected — the
helpers directory is new and has only `__init__.py`. However, four helpers were requested
by multiple agents this generation:

1. **`inv_softplus_safe(array)`** — 4 independent requests. Critical for warm-start agents.
   Current status: every agent implements this ad hoc with inconsistent epsilon handling.

2. **`sensitivity_map(f_array)`** — 5 requests across 3 generations. 5-line JAX function
   (`jax.grad(compute_c)(f)`) that would unlock an entire class of targeted experiments.

3. **`interpolate_sparse(array, target_n)`** — 3 requests. Would have prevented exploit_2's
   cubic spline failure. Standard implementation: piecewise-linear in non-zero regions,
   zero-preserving in near-zero regions.

4. **`timing_benchmark(n_coarse, n_steps=100)`** — 3 requests across 3 generations of SA
   timeouts. A helper that runs 100 Adam steps at given N and returns ms/step would have
   prevented every SA timeout. This is the most impactful missing tool given the pattern.

All four helpers are well-defined, low-complexity, and would provide immediate value to
gen 5 agents. The Experimentator should prioritize these before gen 5 launches.
