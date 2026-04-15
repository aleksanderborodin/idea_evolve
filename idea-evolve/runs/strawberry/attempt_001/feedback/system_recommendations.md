# System Recommendations — Generation 1

## Priority 1: Fix yolo11s BrokenPipeError (Critical)

### What to change
Debug and fix the GPU lock cleanup code in `problems/strawberry/evaluate.py`. The BrokenPipeError occurs during eval cleanup after training completes successfully.

### Why
The larger model (yolo11s) trains well (mAP50 trending ~0.81 at epoch 40) but evaluation never completes. This blocks the pipeline from exploring a fundamentally different model architecture. The crash is NOT a model capacity issue — training was healthy with no divergence.

### Expected impact
If yolo11s can be evaluated successfully, we learn whether larger models outperform nano on this task. This could be a significant score improvement opportunity (2-3x more parameters).

### Action
1. Add debugging output to GPU lock acquire/release in evaluate.py
2. Check if the BrokenPipe occurs when the eval subprocess writes to stdout/stderr pipes during cleanup
3. Ensure `atexit` cleanup is properly registered so crashed evals don't leave stale lock files
4. Consider adding `torch.cuda.synchronize()` before eval cleanup to ensure GPU operations complete

---

## Priority 2: Document TTA as non-functional for YOLO11n-seg (Critical)

### What to change
Either:
- **Option A**: Remove `tta` from `train_and_eval` helper defaults and update description.md to reflect YOLO11n-seg doesn't support it
- **Option B**: Implement manual TTA via multiple `predict()` calls with different augmentations

### Why
Three agents independently tried TTA expecting the documented 0.5-2% boost. All got silently ignored behavior. This wastes evaluation time and produces misleading score comparisons (solutions with TTA flags that don't actually apply TTA).

### Expected impact
Agents stop wasting time on non-functional TTA. If Option B is chosen, actual TTA benefits become available.

### Action
Check ultralytics version and YOLO11n-seg val() capabilities. Update `helpers/core.py` REC-1 comment to include this limitation. Consider implementing manual TTA in evaluate.py if the feature is valuable enough.

---

## Priority 3: Establish per-class mAP50 baseline for WEIGHTS_EXP5 (Critical)

### What to change
Add `get_per_class_metrics()` helper to `helpers/core.py` that reads `LAST_PER_CLASS_METRICS` and returns a structured dict.

### Why
No agent knows the per-class breakdown for the best checkpoint (WEIGHTS_EXP5). This makes targeted optimization impossible — agents can't tell if an approach helps or hurts specific classes. The rare class Anthracnose improved to 0.858 (best across all solutions) with mixup, but without per-class baseline, no agent can estimate headroom or design targeted strategies.

### Expected impact
All subsequent agents can make data-driven decisions about which classes to target. Enables proper hypothesis formation for loss engineering and class weighting experiments.

### Action
```python
def get_per_class_metrics() -> dict:
    """Read per-class metrics from the most recent evaluation."""
    # Implementation reads LAST_PER_CLASS_METRICS from the standard path
    # Returns structured dict with class names as keys
```

Also add a note to `agents/explore.md` and `agents/full.md` that per-class metrics are available via this helper.

---

## Priority 4: Verify research output persistence (Moderate)

### What to change
Verify that `move_research_outputs()` in the orchestrator correctly copies `output/report.md` from agent workspaces to `knowledge/research/genNNN/`. If the function is being called, investigate why research_1 never wrote `output/report.md` (only wrote to `reports/gen001/`).

### Why
Research agent's literature findings exist only in the debrief report. The next Architect cannot read what research_1 found without access to that report. Research insights are lost between generations.

### Expected impact
Research knowledge persists across generations. Architect can build on prior research rather than starting from scratch each generation.

### Action
1. Check orchestrator logs for `move_research_outputs()` calls after research_1 session
2. Verify research_1 was told to write findings to `output/report.md` (not just `report.md` in workspace root)
3. Consider adding a check that verifies research outputs were successfully moved

---

## Priority 5: Update State of Affairs to highlight Anthracnose improvement (Minor)

### What to change
`knowledge/state_of_affairs.md` should note that Anthracnose (rarest class) achieved 0.858 in gen 1 — a significant improvement suggesting the class is not fundamentally limited by rarity but by appropriate augmentation strategy.

### Why
The State of Affairs correctly identifies Angular Leafspot and Leaf Spot as bottleneck classes (0.66-0.76 range), but doesn't highlight that Anthracnose improved to 0.858 with mixup. This positive signal should inform gen 2 strategy — the rare class responds to augmentation, not class weighting.

### Expected impact
Architect can better prioritize experiments. If Anthracnose has headroom (0.858 vs theoretical 1.0), agents should continue exploring augmentation strategies for it. If Angular Leafspot is stuck at 0.66-0.74 across all approaches, it may need a fundamentally different strategy (boundary loss, higher resolution).

---

## Priority 6: Launch an experimentator in gen 2 (Moderate)

### What to change
The Architect should include an experimentator in gen 2's manifest. Key experiments to run:
1. WEIGHTS_EXP6 vs WEIGHTS_EXP5 fine-tune comparison (same config, different starting point)
2. copy_paste sweep (0.55, 0.65, 0.70) with mixup=0.15 to find exact optimum

### Why
Gen 1 produced no experimental results in `knowledge/experiments/gen001/`. Research identified BCE-Dice-Lovász composite loss as promising but no agent tested it empirically. The pipeline needs experimentator agents to run controlled comparisons.

### Expected impact
Validated hypotheses rather than theoretical claims. We learn whether WEIGHTS_EXP6 (0.936 val) outperforms WEIGHTS_EXP5 (0.945 val) as a fine-tuning starting point, and whether copy_paste=0.65 is the true optimum.

---

## Priority 7: Fix prompt context — copy_paste convergence lag caveat (Moderate)

### What to change
The `description.md` note about "copy_paste lags behind at epoch 20-40 but overtakes at epoch 50+" should be flagged in the agent prompts as only applying to from-scratch training (Mode 2), NOT to fine-tuning from converged WEIGHTS_EXP5.

### Why
Research agent noted this caveat was "irrelevant for the default Mode 1 (fine-tune from exp5)" but didn't realize it when planning experiments. Agents may incorrectly apply this caveat to fine-tuning scenarios.

### Expected impact
Agents don't waste time worrying about copy_paste convergence lag in fine-tuning context. Cleaner mental model of when different behaviors apply.

---

## Summary of Changes

| Priority | File to Change | Change |
|----------|----------------|--------|
| 1 | `problems/strawberry/evaluate.py` | Debug/fix BrokenPipeError in GPU lock cleanup |
| 2 | `problems/strawberry/helpers/core.py` | Document TTA limitation in REC-1 |
| 2 | `problems/strawberry/description.md` | Update TTA claim to reflect non-support on YOLO11n-seg |
| 3 | `problems/strawberry/helpers/core.py` | Add `get_per_class_metrics()` helper |
| 4 | `orchestrator.py` | Verify research output persistence |
| 5 | `knowledge/state_of_affairs.md` | Highlight Anthracnose improvement signal |
| 6 | `agents/architect.md` | Mandate experimentator inclusion for gen 2 |
| 7 | `agents/explore.md` / `agents/full.md` | Add note about TTA limitation |