---
type: pattern
id: pattern_007
name: Agent failure mode — complex algorithm tasks timeout with zero output
lifecycle: active
confidence: 0.85
first_seen: gen_003
last_updated: gen_003
evidence: [gen003_explore_1, gen003_exploit_1, gen003_experimentator_1]
related_ideas: []
tags: [agents, timeout, failure_mode, observability]
---

# Agent Failure Mode — Complex Algorithm Tasks Timeout with Zero Output

## Observation

In gen003, three of five agents (explore_1, exploit_1, experimentator_1) produced **zero
output** — no solutions, no reports, no observations. All three timed out at every phase
(work, wrap-up, debrief). Combined waste: ~3+ hours of GPU compute with no recoverable
knowledge.

## Pattern Details

The three failing agents were all assigned complex implementation tasks:
- explore_1: "Track B radical exploration" — CFOP-like solving, A* search, exploit scramble structure
- exploit_1: Full predictor pipeline (generate data, train MLP, beam search 101 puzzles)
- experimentator_1: Build reusable helper module with GPU code

The two successful agents had more constrained scopes:
- explore_2: Incremental improvement on known working approach (compression + predictor tail)
- research_1: Read code + run small experiments, no full solution required

## Root Cause

Complex algorithmic tasks that require (1) writing non-trivial code, (2) integrating with
external libraries (cayleypy), (3) running GPU computations, and (4) evaluating on 101
puzzles within a single session are too ambitious. The agents get stuck in implementation
details, hit API incompatibilities, or spend all their time on data generation/training
without reaching evaluation.

## Implication

1. **Incremental tasks are essential.** Agents should first validate a minimal version
   (1 puzzle, tiny data), then scale up. The evaluate-immediately workflow requires
   a working solution early.
2. **Complex tasks need staged briefs.** Instead of "build the full predictor pipeline,"
   break into: (a) train MLP on 100 samples, verify Predictor doesn't crash; (b) run on
   1 puzzle; (c) scale to full proxy.
3. **No observability on failure.** When all three phases timeout with zero output, there
   is zero forensic evidence. The proc_log system may help but these agents may not even
   reach evaluate.py.
4. **Fallback solutions prevent total loss.** explore_2 produced a compression-only
   fallback first, then iterated. The failing agents had no "save what you have" strategy.
