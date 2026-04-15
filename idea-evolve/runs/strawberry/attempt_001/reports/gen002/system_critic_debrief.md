# System Critic Debrief — Generation 2

## 1. What did you try?

I performed a comprehensive system critique of generation 2 of the strawberry disease segmentation evolution. My approach was to:

1. **Read all available reports** from gen 2 agents (evaluator, explore_1, exploit_1, full_1, research_1) and their observations files
2. **Read persistent state files** (all_scores.json, score_progression.md, run_state.json, timing.json, coverage_matrix.md)
3. **Read knowledge files** (state_of_affairs.md, idea files across all lifecycles, patterns, clusters)
4. **Read feedback files** (system_recommendations.md, agent_gaps/gen002.md)
5. **Read config** (user/config.yaml)
6. **Cross-reference** gen 1 summaries vs gen 2 to identify what changed and what should have been updated but wasn't

**What I found — by category:**

### Pipeline Problems (CRITICAL)
- **Finalize phase skipped for gen 2**: `all_scores.json` has only gen 1 scores (0.8137, 0.8328). Gen 2 scores (0.8087, 0.8103, 0.5453, 0.8271) are absent. `score_progression.md` shows only gen 1. `run_state.json` shows `"completed_gens": [1]` with gen 2 not marked complete, and current_phase = "system_critic" — but the timing shows no system_critic entry for gen 2. This is a data integrity failure.
- **State of Affairs is stale**: Still titled "Generation 1 (Rewrite)" with gen 1 strategic priorities. TTA is listed as "free lunch" (debunked), yolo11s+exp5 via pretrained= is "top priority" (debunked), and the coverage map is gen 1 data.
- **Two high-value solutions never evaluated**: explore_1/sol02 (yolo11s 40ep) and full_1/sol01 (yolo11s 50ep) both timed out. The most important unanswered question (does yolo11s benefit from more than 20 epochs?) remains unanswerable.

### Recommendation Status
- **REC-1 (optimizer default)**: Unfixed. Marked P0 in gen 1, still unfixed.
- **REC-2 (per-class mAP)**: Unfixed. Marked P0 in gen 1, still unfixed. All agents cited this as the #1 information gap.
- **REC-3 (TTA on best model)**: Superseded — TTA is now debunked entirely.
- **REC-4 (zero-shot exp5)**: Done — research_1 ran this experiment.
- **REC-5 (training log preservation)**: Unfixed. No experimentator was assigned to build this.
- **REC-7 (Architect assigns specific copy_paste values)**: Unimplemented. 0.55-0.6 range still untested.

### Strategic Landscape Changes (gen 2 findings)
- TTA non-functional (idea_003/idea_011 debunked)
- imgsz=832 fine-tuning catastrophic regression (idea_010 debunked)
- yolo11s+exp5 via pretrained= fails (idea_009 debunked)
- Fine-tuning from converged checkpoint: marginal at best (idea_012 established)
- Zero-shot exp5 (0.8271) nearly matches best fine-tuned (0.8328, +0.0057)

---

## 2. What information did you lack?

1. **Why finalize was skipped**: I don't have access to the orchestrator code execution trace. I can see the effect (stale files) but not the cause. Was there an exception? A missing sentinel check? A phase_status() misclassification?
2. **Why the consistency reviewer ran for gen 1 (255s) but not gen 2**: Config has `consistency_review_interval: 1` and `emergency_review_on_strategic_shift: true`. A strategic shift definitely occurred (3 major directions closed). Yet no gen002 consistency review file exists.
3. **The actual evaluate.py source code**: I don't have direct access to `helpers/core.py` to confirm the optimizer behavior and PROXY_EPOCHS_SCRATCH value. I had to infer from agent reports.
4. **Whether explore_1/sol02 and full_1/sol01 weights still exist**: If the training completed but evaluation timed out, the weights may still be on disk. If they are, they could be evaluated in gen 3 without retraining.
5. **The orchestrator's phase_status() logic**: I don't know how the orchestrator decides when finalize has run. The run_state.json shows current_phase = "system_critic" which is where the orchestrator is now, but timing.json has no system_critic entry — suggesting the phase started but hasn't been recorded yet.

---

## 3. What given facts might be wrong or outdated?

1. **"TTA provides ~0.5-2% mAP50 lift"** — Completely wrong. TTA is non-functional. This was in gen-1 system_recommendations as a P1 recommendation and in the state_of_affairs as a top priority. Every agent planned around it. gen 2 proved it provides zero lift.

2. **"yolo11s from exp5 checkpoint — top priority direction"** — Wrong approach. The pretrained= flag does wholesale weight replacement, not fine-tuning. yolo11n weights cannot load into yolo11s architecture. The combination is not achievable via the documented approach.

3. **State of Affairs says copy_paste=0.65 crashes** — Technically correct for that specific value, but the actual lesson (ceiling is below 0.65, do not exceed 0.6) is right. The range 0.55-0.6 is untested and might be stable.

4. **"val-test gap is 0.10"** — Based on full_1 only (val=0.91, test=0.8137). With only 1 data point and the optimizer bug confounding it, this estimate is imprecise.

5. **The coverage matrix says "idea_001 alone (yolo11s from COCO)" was tested 1 time** — This is the gen-1 best at 0.8328. But the description says "alone" which implies it wasn't combined with anything. In reality, it used copy_paste=0.5, AdamW was not set (optimizer=auto), and it was evaluated without TTA. These confounds make it hard to know which variable caused the improvement.

---

## 4. Was the State of Affairs accurate?

**No.** The State of Affairs was the gen-1 rewrite and was never updated for gen 2. It had several critical inaccuracies:

1. **TTA listed as top priority** — Debunked, non-functional.
2. **yolo11s+exp5 as top priority** — Debunked, architecture mismatch prevents this approach.
3. **imgsz=832 as "highest-priority unexplored direction"** — The approach (fine-tuning at 832 from 640-converged checkpoint) was tested and caused catastrophic regression. The idea itself (resolution hypothesis) may still be valid via progressive resizing, but the State of Affairs didn't distinguish between the approach and the hypothesis.
4. **Coverage map shows TTA and imgsz=832 as "0 tries"** — Actually tested in gen 2, now debunked.
5. **Best score listed as 0.8328** — Still correct as of gen 2 (no improvement).
6. **"Gen 2 should prioritize three directions"** — The three directions were all tested: TTA (dead), yolo11s+exp5 (failed), AdamW (confirmed fix). Only the third actually worked.

The State of Affairs needs a complete rewrite for gen 3. The gen 2 evaluator's generation_summary.md in history/generations/gen002.md has the correct strategic picture.

---

## 5. What would you do differently with more or different context?

1. **I would run the finalize phase manually** — I could potentially write the gen 2 scores to all_scores.json and update score_progression.md directly to fix the immediate data loss, but this should be done by the orchestrator, not the system critic.

2. **I would examine the orchestrator code** to understand why finalize was skipped. Without this, I can't propose a targeted fix — only a general "check your phase transitions" recommendation.

3. **I would attempt to evaluate explore_1/sol02 and full_1/sol01** if their weights exist on disk, to recover the wasted GPU time. But I don't have a tool to check if those .pt files still exist.

4. **I would read helpers/core.py directly** to verify the optimizer default and PROXY_EPOCHS_SCRATCH values rather than inferring from agent reports.

5. **I would look at the consistency_review code** to understand why it didn't run for gen 2 despite interval=1.

---

## 6. Specific experiments to run

See `experiment_suggestions.md` for full details. The prioritized list:

1. **yolo11s from COCO at 40 epochs** — The #1 unanswered question. Did gen-1's 0.8328 represent real signal or noise? (Agent: full or explore)
2. **Progressive resizing 640→832** — The cleanest test of the resolution/small-lesion hypothesis. Direct 832 fine-tuning failed catastrophically. (Agent: explore)
3. **Per-class mAP50 extraction** — Eliminates all the guesswork about which classes are bottleneck. (Agent: research or experimentator)
4. **copy_paste=0.55 and 0.6** — Maps the stability ceiling incrementally. (Agent: explore)
5. **TTA revalidation after fresh training** — If TTA works on a freshly trained model, it's a free lunch on all future evals. (Agent: research)
6. **yolo11s + exp5 augmentation strategy** — Tests whether exp5's training config generalizes to yolo11s. (Agent: full)

---

## 7. What surprised you?

1. **The finalize phase was skipped** — This is a serious bug. I expected to find some minor recommendations, not a fundamental data integrity failure. The orchestrator is currently in an inconsistent state (gen 2 not marked complete, scores not recorded, but the next phase is running).

2. **No consistency review for gen 2** — Despite `consistency_review_interval: 1` and a massive strategic shift (3 directions closed), the consistency review didn't run. The state of affairs is now 2 generations stale.

3. **REC-1 and REC-2 were both unfixed despite being P0** — The optimizer bug and per-class mAP were identified in gen 1. Both were P0. Neither was fixed. The optimizer bug affected full_1's experiment in gen 1 and wasn't fixed before gen 2. This suggests the recommendation system is not producing actionable fixes.

4. **The architecture mismatch was a surprise** — Multiple agents assumed pretrained= would do shape adaptation. The Ultralytics behavior (wholesale weight replacement, not fine-tuning) is counterintuitive. The fact that it fails silently (model summary shows yolo11n layers despite loading yolo11s-seg.pt) is especially dangerous.

5. **TTA was completely non-functional** — Not just ineffective but silently reverted to single-scale with a warning. The fact that Ultralytics produces identical scores with and without TTA (0.8271 both ways) means no agent could have detected this without checking the stderr warning message.

---

## 8. Helper tools feedback

I did not directly use helpers from `problem/helpers/` because I am a critique agent, not a solution agent. However, I assessed their impact through agent reports:

**What worked:**
- `train_and_eval()` in helpers/core.py: Multiple agents confirmed it works correctly when used properly
- `WEIGHTS_EXP5`, `DATA_V1` constants: All agents found and used them correctly
- GPU lock mechanism: No evaluation conflicts reported in parallel runs

**What didn't work:**
- `evaluate_on_test` doesn't support `augment=True`: Should be documented. Multiple agents wasted time discovering this.
- `model_name` is NOT a valid kwarg: Misleading error if passed. Should either be accepted (as a no-op) or produce a clear error message.
- `PROXY_EPOCHS_SCRATCH = 50` exceeds constraints (max 40): Caused full_1 to attempt an impossible run. Mismatch between constant and documented constraint.

**What I wished existed:**
- Per-class mAP extraction in evaluate_on_test(): Would have saved 3 agents from noting this gap independently
- Training log preservation: Would have recovered the only diagnostic info from the full_1 crash
- Evaluation resume capability: Explore_1's weights exist on disk but the evaluation can't be resumed

---

## 9. Time budget

I had enough time to:
- Read all available reports and state files
- Cross-reference gen 1 vs gen 2 data
- Write comprehensive system_analysis.md, system_recommendations.md, and experiment_suggestions.md
- Write this debrief

I did NOT have time to:
- Examine the orchestrator source code to understand the finalize skip root cause
- Check if explore_1/sol02 and full_1/sol01 weights still exist on disk
- Manually fix the stale all_scores.json (which I could do but shouldn't — orchestrator should own this)

**If I had more time:** I would read the orchestrator code to understand exactly why finalize was skipped and propose a targeted fix rather than a general "check your phase transitions" recommendation. I would also try to evaluate the interrupted solutions if their weights exist.
