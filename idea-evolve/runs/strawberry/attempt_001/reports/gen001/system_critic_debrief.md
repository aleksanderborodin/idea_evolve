# Debrief Report — System Critic, Generation 1

## 1. What did you try?

I performed a comprehensive critique of generation 1 across all available pipeline metadata:

**Files read:**
- `reports/gen001/architect.md` — architect's strategy and risk assessment
- `reports/gen001/evaluator.md` — full evaluator analysis with 8 ideas, 3 clusters, coverage matrix
- `reports/gen001/evaluator_debrief.md` — evaluator summary
- `reports/gen001/explore_1.md` — explore_1 debrief (yolo11s from COCO, 0.8328)
- `reports/gen001/explore_2.md` — explore_2 debrief (copy_paste=0.65, broken pipe, 0.0)
- `reports/gen001/full_1.md` — full_1 debrief (exp5 fine-tune, 0.8137)
- `reports/gen001/research_1.md` — research_1 findings (6 techniques surveyed)
- `population/gen001/*/observations.md` — all agent observations
- `feedback/agent_gaps/gen001.md` — evaluator-identified gaps
- `knowledge/state_of_affairs.md` — current knowledge state
- `history/coverage_matrix.md` — coverage matrix
- `history/generations/gen001.md` — generation snapshot
- `knowledge/patterns/confirmed/*.md` — 3 confirmed patterns
- `helpers/core.py` — train_and_eval and evaluate_on_test source

**Analysis performed:**
- Cross-referenced all agent reports for consistency
- Traced the optimizer='auto' bug through full_1's training log evidence
- Identified the training log preservation gap via explore_2's broken pipe
- Catalogued research_1's 6 documented techniques vs the 8 ideas actually created
- Assessed coverage matrix for gaps (most ideas at zero coverage)
- Verified knowledge quality issues (pattern_001 has contradictory framing)

**Output produced:**
- `system_analysis.md` — categorized findings (pipeline problems, missing capabilities, prompt problems, resource issues, knowledge quality, experiment gaps)
- `system_recommendations.md` — 9 prioritized recommendations (P0/P1/P2/P3)
- `experiment_suggestions.md` — 6 prioritized experiments with expected information gain

---

## 2. What information did you lack?

**Most critical gap: No per-class mAP data exists anywhere.** All scores are aggregate mAP50. The 15x class imbalance means we cannot tell if improvements come from better Leaf Spot detection (already dominant) or Anthracnose/Blossom Blight detection (the actual bottleneck). Every recommendation I could make about "targeting rare classes" is speculative without per-class metrics.

**Second gap: No training logs for explore_2's crash.** I cannot determine whether copy_paste=0.65 specifically caused the broken pipe or whether it was a random/CUDA failure. The difference matters — if 0.65 specifically crashes, we know the ceiling is < 0.65. If it was random, retrying at 0.65 might work.

**Third gap: No visibility into test images.** I cannot verify whether the "small lesions" hypothesis is correct. All recommendations about imgsz=832 are based on speculation, not evidence.

**Fourth gap: The knowledge/ideas/ directory is empty.** Ideas exist in the evaluator's workspace output but not in the knowledge base as formal files. I couldn't verify the idea frontmatter schema or read individual idea contents. This made it impossible to assess idea quality or detect duplicate/subset relationships between ideas.

---

## 3. What given facts might be wrong or outdated?

**state_of_affairs.md:14** says "The core fine-tuning approach (WEIGHTS_EXP5 + copy_paste=0.5 + 20 epochs) produced 0.8137 — identical to the gen-0 baseline." This is slightly misleading. The gen-0 baseline used yolo11n from COCO at 20 epochs (not exp5 fine-tune). full_1 used exp5 fine-tune. The scores are the same value but for different reasons — this should be clarified because it affects how we interpret "neutral."

**state_of_affairs.md:19-20** says "copy_paste=0.65 causes broken pipe crashes" and "Values above 0.5 cause instability or crashes." But this is based on a single observation (explore_2) that had "limited time due to interrupted workflow" (explore_2 observations). The crash might not be specifically caused by copy_paste=0.65. The pattern_002 confidence of 0.8 is probably overstated for this reason.

**coverage_matrix.md:10** lists "copy_paste=0.5 alone (baseline)" with 2 tries and best=0.8175 from gen_000. But the actual best result in gen_1 (0.8328) used copy_paste=0.5 too — so the coverage should show more tries at 0.5. The matrix may be incomplete.

---

## 4. Was the State of Affairs accurate?

**Mostly accurate but incomplete in two ways:**

1. It correctly identifies the core uncertainty (val-test gap) and the top unexplored directions. The "Unexplored regions" section (state_of_affairs.md:33-39) is a good summary.

2. It lists 6 unexplored technique families but doesn't connect them to specific implementations. An Architect reading this knows "TTA is unexplored" but would need to derive the implementation from first principles or from research_1's report.

3. The State of Affairs says "The search space is essentially unexplored" — this is correct for gen 1 but the next State of Affairs should start differentiating between "not yet tried" and "tried and confirmed neutral."

**Missing from State of Affairs:** No mention of the optimizer='auto' bug, even though it was discovered in gen 1. The bug should be flagged as a "known failure mode" in the next State of Affairs.

---

## 5. What would you do differently with more or different context?

**With per-class mAP data:** I could identify which specific disease classes are the bottleneck and give concrete recommendations about which experiments to prioritize. Right now all rare-class recommendations are speculative.

**With access to individual idea files:** I could verify idea frontmatter quality, detect overlapping ideas, and assess whether the idea lifecycle (active/established/...) is being used correctly. Without this, I'm critiquing the idea creation process blindly.

**With training logs from explore_2:** I could determine whether copy_paste=0.65 specifically crashes or whether it was a random failure. This changes whether we map the boundary at 0.6 or 0.55.

**With the Architect's brief (briefs/gen001/):** I couldn't find the architect's output directory — it either wasn't created or was cleaned up. Having the architect's brief would let me assess whether the optimizer='auto' warning should have been in the brief but wasn't.

**With historical timing data:** The State of Affairs says timing data is tracked (state_of_affairs references "recent timing data") but I found no timing.json. Knowing how long each agent phase took would help me assess whether the 4-agent × ~4min = ~16min wall-clock estimate is accurate.

---

## 6. Specific experiments to run?

Listed in detail in `experiment_suggestions.md`. The priority order:

1. **EXP-1: Zero-shot exp5 evaluation** — 30 seconds, resolves the central val-test gap question. Do this first before any fine-tuning experiments.

2. **EXP-2: Apply TTA to best model** — 60 seconds, immediate free improvement to fitness signal accuracy.

3. **EXP-3: yolo11s from exp5** — 3.6 min, most promising combination of gen 1 findings.

4. **EXP-4: imgsz=832 from exp5** — 3.6 min, tests the small-lesion hypothesis.

5. **EXP-5: copy_paste=0.6** — 3.6 min, fills the coverage gap between safe (0.5) and crashed (0.65).

---

## 7. What surprised you?

**Surprise 1:** Only 2 of 3 agents produced valid data. In a first generation with a cold start, you'd expect more redundancy, not less. The explore_2 crash meant 33% of gen 1's exploration bandwidth was lost. This suggests the proxy regime (20-epoch fine-tune) is unstable in ways the pipeline isn't accounting for.

**Surprise 2:** The optimizer='auto' bug was discovered reactively by full_1, not prevented by the helper's documentation. The `train_and_eval()` docstring actively misleads by showing `lr0=0.001` as a usage example without a warning that it will be silently overridden. This is a design flaw in the helper, not just a missing warning.

**Surprise 3:** research_1 produced 6 detailed technique analyses with implementation code, but only TTA was converted to an idea file. The other 5 are trapped in a report. This is a systemic routing failure — the pipeline can generate good research but doesn't route it into the knowledge system.

**Surprise 4:** TTA was never applied despite being the #1 "easy win" recommendation from research_1 with complete implementation code. The Evaluator's debrief (evaluator.md:109) even says "apply TTA to the best model FIRST." Yet no agent or evaluator actually did it. This suggests the mandatory evaluate-immediately workflow discourages post-hoc evaluation improvements.

---

## 8. Helper tools feedback

**helpers/core.py: `train_and_eval()` and `evaluate_on_test()`**

The helpers are generally well-designed and saved agents significant boilerplate. Key feedback:

**Issue 1 (Critical):** `train_and_eval()` uses `optimizer='auto'` by default (inherited via `**train_kwargs` into `model.train()`). This silently ignores any explicit `lr0` passed by the caller. The docstring shows `lr0=0.001` as a usage example without any warning about the optimizer override. **This is the single most impactful bug in the generation.**

**Issue 2 (Medium):** No training log preservation on error. When a run crashes (like explore_2's broken pipe), the RUN_DIR is cleaned up before any diagnostics can be captured. Agents are flying blind on crashes.

**Issue 3 (Minor):** `evaluate_on_test()` doesn't support TTA (`augment=True`). The Evaluator couldn't apply TTA post-hoc without modifying the helper or writing custom eval code. This should be a simple kwarg.

**Positive:** The dataset constants (WEIGHTS_EXP5, DATA_V1, etc.) and the dataset stats (class names, imbalance ratio) are all accurate and well-organized. The `cleanup=True` default is correct for the GPU-lock constrained Strawberry environment where disk space matters.

**Helper I wished existed:** A `diagnostic_eval()` function that saves test predictions (masks overlaid on images) to a directory for later review. This would let agents visually diagnose failure modes without needing per-class metrics. Given that the research_1 agent explicitly asked for "test image visibility" and got nothing, this would have been high value.

---

## 9. Time budget

I completed all analysis and writing work within the session time. No time pressure issues.

**What I would do with more time:**

1. **Read the actual idea files** (knowledge/ideas/*.md) to assess idea quality, frontmatter consistency, and duplicate detection. Without this, my critique of the knowledge system is based on second-hand descriptions rather than direct evidence.

2. **Cross-reference per-agent timing** from `history/timing.json` to identify whether any agent was disproportionately slow, which might explain why explore_2 only produced one solution.

3. **Audit the brief paths** that the Architect specified, to verify that agents were actually pointed to the right files. The briefs directory didn't exist at the path I checked — if briefs were generated, I couldn't verify their content.

4. **Compare gen 1 coverage against a simulated optimal coverage matrix** to quantify how inefficiently the search space was explored. With only 3 agents and 2 valid solutions, there's significant room for improvement in allocation.

5. **Investigate whether the "broken pipe" error is reproducible** — run copy_paste=0.65 again to determine if it's a specific cause or random failure.
