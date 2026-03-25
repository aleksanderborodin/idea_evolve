# System Analysis — Generation 1

## Executive Summary

Generation 1 ran 4 agents (explore_1, explore_2, full_1, research_1). The pipeline produced
real improvement: multiple solutions in the 1.517x range beat the baseline (1.5185), with the
best cache entry at **1.5167**. However, 3 of 4 solution agents failed the evaluate-immediately
workflow, causing cascading timeouts. Enormous compute was wasted writing unevaluated solutions.
The evaluate-immediately breakdown is the defining problem of this generation.

---

## Pipeline Problems

### [P1] CRITICAL — Evaluate-immediately workflow failed for all 3 solution agents

Evidence:
- explore_1: 13 solutions written, 4 evaluated in-session (.score files for sol01–sol04).
  Sol05/06 have fitness headers but no .score files. Sol07–13 completely unevaluated.
- explore_2: 12 solutions written, only 1 evaluated in-session (sol01). Sol02–12 show
  `# fitness: 0.0` with no .score files — the agent set a placeholder and moved on.
- full_1: 5 solutions written, **zero** evaluated in-session. No .score files, all fitness
  headers show "TBD". The agent ran evaluate.py at least once informally (referenced a 1.5178
  score in a comment in sol04) but never persisted the result.

Impact: The evaluator had to re-evaluate all of explore_2 and full_1's solutions post-hoc,
adding load and delay. More critically, agents could not iterate on results — they were writing
blindly rather than learning within their session.

Root cause: Agents are front-loading solution writing before evaluation. With long training
runs (40k–80k gradient steps per solution), even a single evaluation takes significant
wall-clock time. Under pressure to "explore many directions," agents default to writing code
and deferring evaluation.

### [P2] CRITICAL — Timeout cascade: all solution agents timed out their work session

Timing evidence (from history/timing.json):
- explore_1: work=458s, wrap-up=900s (also timed out), debrief=1029s. **Total: 2387s**
- explore_2: work=1200s, wrap-up=900s (also timed out), debrief=974s. **Total: 3074s**
- full_1: work=900s, wrap-up=161s, debrief=267s. **Total: 1328s**
- research_1: work=600s, wrap-up=63s. **Total: 663s**

Both explore agents triggered three sessions each (work → wrap-up → debrief). The wrap-up
session for explore_1 and explore_2 also timed out, consuming another 900s each. Combined,
the 4 agents consumed ~7452s of compute for what should have been ~900s per agent.

Root cause: Closely linked to P1. An agent that has written 10 solutions without evaluating
any will need many more turns to catch up on evaluations during wrap-up, causing wrap-up
to also time out.

### [P3] MODERATE — explore_2 didn't read the baseline before starting

Evidence: explore_2/sol01 implemented a symmetric truncated Gaussian (C=2.000046). The
baseline already achieves 1.5185. Had the agent read the baseline, it would have known
(a) what score to beat, and (b) that the existing optimizer achieves single-bump solutions
which are locally optimal but bad. This sent explore_2 on an early dead end.

Impact: sol01 wasted a long optimization run. The subsequent 11 solutions were all unevaluated.

### [P4] MODERATE — No evaluator_report.md in reports/gen001/

The evaluator ran (554.8s, producing knowledge files, ideas, patterns), but no
`evaluator_report.md` appears in `reports/gen001/`. The orchestrator detects evaluator
completion via `generation_snapshot.md`, `new_ideas`, or `report.md`. If only the knowledge
files were created and no report written, the evaluator's own analysis of this generation is
lost. The next Architect will read prev_gen_reports.md which would be missing the evaluator's
strategic recommendations.

### [P5] MINOR — State of Affairs not updated after gen 1

`knowledge/state_of_affairs.md` still shows `generation: 0` and "Pre-Generation" text.
This file is the Layer 0 summary that agents read for orientation. After one generation,
it should reflect what was learned: best score, key findings, what works. The evaluator
may have been tasked to write it but didn't, or the finalize phase didn't update it.

---

## Missing Capabilities

### [M1] MODERATE — No baseline-reading enforcement before first solution

explore_2's failure (P3) reveals a structural gap: nothing enforces that agents read
`problem/initial_programs/optimize.py` before writing their first solution. In gen 1, the
agent that did read it (explore_1) performed significantly better. The one that didn't started
with a C=2.0 solution.

Recommendation: Add "read the best current solution before writing anything" as step 0 in
all solution agent prompts (explore, exploit, full, genetic).

### [M2] MINOR — No coverage matrix exists yet

`history/coverage_matrix.md` was not created in gen 1. The Architect for gen 2 will lack
this tool for strategic planning. The Evaluator was supposed to create it but may not have
done so in a first-gen bootstrap.

---

## Prompt Problems

### [PR1] CRITICAL — Evaluate-immediately instruction is not making agents comply

The prompts include evaluate-immediately instructions, but 3/3 agents violated them. The
instruction may be present but not prominent enough, or agents rationalize deferring evaluation
("I'll evaluate them all at the end").

The explore_1 debrief confirms: the workflow was followed for sol01–sol04, then broke down
around sol05. The agent may have decided to batch-write as the session progressed.

Possible fixes:
1. Make the evaluate-immediately rule more prominent (first instruction, bold/caps).
2. Limit solution count per session more aggressively (e.g., "write at most 5 solutions;
   evaluate each before the next").
3. Add explicit "STOP if you have written 2 unevaluated solutions" language.

### [PR2] MODERATE — Agents interpret "diverse exploration" as "write many solutions"

Both explore agents wrote 12–13 solutions. The full agent wrote 5. In all cases, the later
solutions in each session were unevaluated. The prompt's emphasis on exploring diverse
approaches may be causing agents to maximize the number of ideas tried rather than
maximizing the quality of evaluated results.

The evaluate-immediately workflow and diversity-of-exploration are in tension: agents
cannot both evaluate after each solution AND write 13 solutions in 900s when each training
run takes 60–180s.

---

## Resource Issues

### [R1] CRITICAL — explore_2 consumed 3074s for 1 valid score

explore_2 produced 12 solutions but only 1 was evaluated in-session. The wrap-up session
also failed to evaluate the remaining solutions. The evaluator likely had to process them.
For the compute equivalent of ~3 normal agent sessions, explore_2 returned marginal value.

### [R2] MODERATE — explore_1 and full_1 show similar (if lesser) waste

explore_1: 7 of 13 solutions unevaluated in-session.
full_1: 5 of 5 solutions unevaluated in-session.

The pattern is consistent across all solution agents: write too many solutions, run out
of time for evaluation.

### [R3] MINOR — Multi-scale solutions cluster around 1.517x suggesting local minimum

The best gen-1 score is ~1.5167 (eval_cache). The target is 1.5053. The 10 best-scoring
solutions in the cache all cluster in [1.5167, 1.5203], suggesting they're converging to
the same or similar local minimum. The multi-scale Adam approach is good but may have
reached a local attractor that requires qualitatively different techniques to escape.

---

## Knowledge Quality Issues

### [K1] POSITIVE — Evaluator bootstrapped a strong knowledge base

12 ideas, 4 patterns, 2 confirmed findings. The established ideas (idea_001: Adam optimizer,
idea_004: multi-scale) are well-supported and accurate. Pattern_001 (symmetric unimodal → C=2)
is confirmed by 3 independent solutions. This is good quality for gen 1.

### [K2] MINOR — idea_005 (regularization) marked disputed based on limited evidence

idea_005 is marked disputed based on TV regularization (explore_2/sol10) and L1 normalization
(explore_1/sol13) underperforming. However, both of those solutions were complex pipelines
where regularization was confounded with other design choices. Simple regularization (e.g.,
weight decay in Adam) was not isolated tested. The disputed status may be premature.

### [K3] MINOR — Research findings not formally linked to knowledge base

research_1's findings.md is in `knowledge/research/gen001/research_1/`. The evaluator
created ideas/patterns from agent solutions but it's unclear how much of the research
agent's theoretical insights (Sidon set connection, spectral interpretation, softplus
reparameterization) made it into the formal knowledge base.

---

## Experiment Gaps

### [E1] HIGH PRIORITY — Symmetry enforcement with bimodal init not yet tested

Pattern_001 confirms symmetric unimodal → C=2 is a dead end. But research_1 correctly
identifies that symmetric bimodal functions (two bumps at ±x) are theoretically optimal.
No agent tested: enforce symmetry (optimize half-domain, mirror) WITH bimodal initialization.
All three solutions that got C=2 used unimodal init with symmetry enforcement. This combination
has not been ruled out.

### [E2] HIGH PRIORITY — softplus/exp reparameterization untested

Research finding 4 and idea_007 identify ReLU reparameterization as a key deficiency.
The baseline uses relu(g); research strongly recommends softplus(g) or exp(g). No gen-1
solution used this reparameterization systematically. explore_1/sol01 used "softplus" (per
debrief) but got C=1.6904 — worse than Adam from scratch, possibly confounded with L-BFGS.

### [E3] MODERATE — Sidon-inspired initializations not tried

Research finding 6 provides specific initialization recipes (4-bump Gaussian at Sidon
positions). No gen-1 agent tried these. explore_1/sol09 tried "diverse inits (flat, narrow,
wide, two-bump)" but not specifically Sidon-inspired. This is a high-quality prior from
theory that deserves a dedicated test.

### [E4] MODERATE — Adam→L-BFGS hybrid with softplus not yet properly tested

explore_1/sol10 and full_1/sol03–sol04 tried Adam→L-BFGS hybrids, but with ReLU
parameterization. Research argues that softplus is better suited for L-BFGS because
it provides continuous gradients. The combination of Adam(softplus) → L-BFGS is untested.

### [E5] LOW — Basin hopping and multi-start diverse inits not yet scored

explore_1 sol07–sol13 and most of explore_2 sol02–sol12 were not evaluated in-session.
The evaluator may have scored them (they're in the eval_cache), but no debrief reports
document what these approaches achieved. Several theoretically sound approaches (basin
hopping, cyclic LR, B-spline parameterization, TV annealing) have uncertain status.
