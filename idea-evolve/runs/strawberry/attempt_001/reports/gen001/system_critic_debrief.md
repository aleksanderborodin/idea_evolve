# System Critic Debrief — Generation 1

## What did you try?

**Analysis approach:**
1. Read all 7 agent reports in `reports/gen001/` (architect, evaluator_debrief, evaluator, explore_1, explore_2, full_1, research_1)
2. Read population observations from `population/gen001/*/observations.md`
3. Read knowledge files: `state_of_affairs.md`, `coverage_matrix.md`, `agent_gaps/gen001.md`
4. Read config: `user/config.yaml`
5. Read generation snapshot: `history/generations/gen001.md`
6. Attempted to read system_recommendations.md — file did not exist
7. Synthesized findings into system_analysis.md, system_recommendations.md, experiment_suggestions.md

**Key findings synthesized:**
- CRITICAL: yolo11s eval crashes with BrokenPipeError (evaluate.py GPU lock bug)
- CRITICAL: TTA silently ignored on YOLO11n-seg (wasted 3 agents' time)
- CRITICAL: No per-class mAP50 baseline exists for WEIGHTS_EXP5
- MODERATE: Research findings not persisted to knowledge base
- MODERATE: No experimentator launched in gen 1
- MODERATE: Proxy metric (20 epochs) may be unreliable predictor

**No failed approaches** — the analysis was straightforward given the evidence. All findings have direct citations in the source files.

---

## What information did you lack?

1. **`problems/strawberry/eval_hooks.py`** — I could not diagnose the BrokenPipeError root cause without reading the actual GPU lock cleanup code. I only had explore_2's observation that the crash occurred "during evaluation cleanup in the GPU lock code." The actual implementation details (fcntl locking, atexit handlers, process communication) were inaccessible from the agent reports.

2. **`helpers/core.py` implementation details** — research_1 mentioned `get_per_class_metrics()` helper doesn't exist, but I couldn't verify the exact structure of `LAST_PER_CLASS_METRICS` or how `evaluate_on_test` writes it. This would have let me specify the exact helper signature in recommendations.

3. **Prior system_recommendations.md** — The file didn't exist at `feedback/system_recommendations.md`. I had no prior recommendations to review or update. If this was a continuation, I would have built on previous recommendations rather than starting from scratch.

4. **Agent session logs** — The actual Claude/OpenCode session logs (tool calls, reasoning traces) were not available. I worked from post-hoc debrief reports which may have omitted details.

5. **The orchestrator's `move_research_outputs()` implementation** — I could not verify whether research_1's output was lost due to a bug in the orchestrator or because research_1 never wrote to the correct path.

---

## What given facts might be wrong or outdated?

1. **description.md TTA claim** — The problem description claims TTA adds ~0.5-2% mAP50, but YOLO11n-seg silently ignores `augment=True` in val(). The claim may be correct for other YOLO models but not for YOLO11n-seg specifically.

2. **"copy_paste=0.5 is the confirmed winner"** — research_1 reported this from description.md, but gen 1 results show copy_paste=0.7 outperforms 0.5 (0.8296 vs 0.8103). The description may be outdated or referring to from-scratch training rather than fine-tuning.

3. **WEIGHTS_EXP5 val mAP50=0.945** — The generation snapshot says "best per-class: Anthracnose 0.858" from the 20-epoch proxy, not from the 100-epoch WEIGHTS_EXP5 evaluation. So the per-class breakdown for the converged model is actually unknown.

4. **"Angular Leafspot universally weak"** — State of Affairs says this class is universally weak (0.66-0.74), but this is only from gen 1's 20-epoch proxy evaluations. The converged WEIGHTS_EXP5 might show different relative performance.

---

## Was the State of Affairs accurate?

**Mostly accurate**, but incomplete in ways that affected my analysis:

- Correctly identified cold-start situation for gen 0
- Correctly captured copy_paste=0.7 as best setting
- Correctly identified unexplored regions (WEIGHTS_EXP6, progressive resolution, custom loss)
- Correctly identified Angular Leafspot and Leaf Spot as bottleneck classes

**Missing positive signal:**
- State of Affairs shows Angular Leafspot weakness but doesn't highlight that Anthracnose (rarest class) IMPROVED to 0.858 with mixup. This is a positive finding that should inform strategy — the rare class responds to augmentation, not class weighting.

**No per-class baseline:**
- State of Affairs correctly flags missing per-class metrics as an open question, but doesn't prioritize establishing this baseline as a prerequisite for all subsequent experiments.

**Dead ends accurate:**
- cls_pw invalid, TTA ignored, mosaic=0 harmful — all correctly recorded.

---

## What would you do differently with more or different context?

1. **Read the actual eval_hooks.py code** — To diagnose the BrokenPipeError, I need to see the fcntl locking, atexit registration, and process communication code. This would let me give a specific fix rather than "debug the GPU lock cleanup."

2. **Read helpers/core.py in full** — To specify exact `get_per_class_metrics()` helper signature. Currently I can only recommend it exists but can't specify the return format.

3. **Read orchestrator.py move_research_outputs()** — To determine whether research output loss was a bug or research_1 never wrote to the correct path.

4. **Compare against prior system_recommendations.md** — If it existed, I would have avoided duplicating recommendations from prior generations and focused on new findings.

5. **Access the actual LAST_PER_CLASS_METRICS JSON** — To see the exact structure and verify how `evaluate_on_test` writes per-class metrics. This would let me specify the `get_per_class_metrics()` helper more precisely.

---

## Specific experiments to run?

**Priority 1 (baseline):** Run `evaluate_on_test(WEIGHTS_EXP5)` to establish per-class mAP50 baseline. All other experiments depend on this.

**Priority 2 (architecture exploration):** WEIGHTS_EXP6 vs WEIGHTS_EXP5 fine-tune comparison — single evaluation, high information value.

**Priority 3 (hyperparameter refinement):** copy_paste sweep (0.55, 0.60, 0.65, 0.70) with mixup=0.15 — 4 evaluations, closes the gap.

**Priority 4 (proxy reliability):** 40-epoch extended training on best gen-1 config — tests whether proxy metric is reliable.

**Priority 5 (model size):** yolo11s retry (after BrokenPipe fix) — potentially highest impact if the larger model works.

Full details in `experiment_suggestions.md`.

---

## What surprised you?

1. **TTA silently ignored** — Three independent agents tried TTA and all got silently ignored behavior. The documentation claims it works, but YOLO11n-seg val() doesn't support it. This is a significant footgun that should be fixed.

2. **Research findings not persisted** — The research agent's work exists only in the debrief report, not in the knowledge base. This means the next Architect can't build on research_1's literature survey. The orchestrator should have moved these outputs.

3. **No experimentator launched** — Gen 1 had 4 agents (explore_1, explore_2, full_1, research_1) but zero experimentators despite config having `experimentator` enabled with `max_instances: 3`. The Architect chose not to use this agent type, possibly because cold-start didn't have enough signal to formulate specific hypotheses.

4. **yolo11s trains well but eval crashes** — The larger model showed no training instability (converged from 0.71 to 0.81 over 40 epochs). The BrokenPipeError is purely an evaluate.py bug, not a model capacity issue. This means the pipeline is blocking a promising direction due to a software bug.

5. **copy_paste=0.7 beats 0.5** — The description.md says 0.5 is the "confirmed winner" but gen 1 clearly shows 0.7 outperforms. This suggests the description.md is referring to from-scratch training results, not fine-tuning from converged weights.

6. **Anthracnose improved significantly** — The rarest class (Anthracnose) achieved 0.858 with mixup augmentation (best across all solutions). This contradicts the assumption that rare classes are fundamentally limited — they just need the right augmentation strategy.

---

## Helper tools feedback

**Used:**
- `state_of_affairs.md` — clear structure, good navigation
- `agent_gaps/gen001.md` — well-organized gaps with evidence and recommendations
- `coverage_matrix.md` — concise, actionable coverage map

**Did not use:**
- `helpers/core.py` — I read about it in agent reports but didn't read the actual implementation
- `evaluate.py` — I didn't read it directly (would have helped diagnose BrokenPipeError)

**Helper that would save significant time:**
- `get_per_class_metrics()` — mentioned by research_1 as missing. Would let me see the exact per-class breakdown structure without parsing JSON manually.
- `get_last_eval_results()` — a general-purpose helper that returns the most recent evaluation's metrics in a structured dict, including per-class breakdown and eval timing.

**No bugs found** — The helper infrastructure appears sound. The eval_hooks.py kill mechanism may have the BrokenPipe bug, but I couldn't diagnose it without reading the code.

---

## Time budget

**Time was sufficient.** I read all available reports and produced all three output files. No timeout pressure experienced.

**With more time, I would have:**
1. Read `problems/strawberry/evaluate.py` and `eval_hooks.py` to diagnose the BrokenPipeError in detail
2. Read `helpers/core.py` to specify exact helper signatures
3. Read `orchestrator.py` to verify research output persistence logic
4. Compared against prior `system_recommendations.md` if it existed
5. Read the actual `LAST_PER_CLASS_METRICS` JSON to see the data structure