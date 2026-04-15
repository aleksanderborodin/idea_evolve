# System Recommendations — Generation 2

Prioritized by expected impact on pipeline effectiveness.

---

## P0 — Fix immediately, affects all future generations

### REC-1: Fix the finalize phase bug

**What:** The orchestrator's `run_finalize()` is not being called or is exiting early after gen 2 agents. This causes `all_scores.json`, `score_progression.md`, and `run_state.json` to remain stale.

**Why:** Without finalize running, the orchestrator loses track of completed generations. If it crashes and restarts, it will re-run gen-2 agents, overwriting the evaluator's knowledge work. The dashboard shows wrong scores. Rankings are incomplete.

**How:** Check `phase_status()` return values and the finalize call site in the generation loop. Add assertion checks that `all_scores.json` was updated. The root cause may be that `run_state.json` shows `current_phase: system_critic` but the orchestrator hasn't actually entered that phase — it may be stuck between phases.

**Expected impact:** Data integrity restored. Crash recovery works correctly. Dashboard accurate.

---

### REC-2: Rewrite the State of Affairs for gen 2

**What:** The State of Affairs (knowledge/state_of_affairs.md) is still labeled "Generation 1" and contains wrong strategic guidance (TTA as "free lunch," yolo11s+exp5 as "top priority"). The gen-2 evaluator produced a comprehensive strategic rewrite in gen002_summary.md.

**Why:** The Architect reads the State of Affairs to plan gen 3. Wrong priorities waste an entire generation of agents on debunked directions.

**How:** The gen-2 generation_summary.md in history/generations/ has the correct strategic picture. Copy it to knowledge/state_of_affairs.md with updated frontmatter (gen 2, updated timestamps). The consistency reviewer should have done this — investigate why it ran for gen 1 (255s) but not gen 2 despite `consistency_review_interval: 1`.

**Expected impact:** Gen 3 Architect makes correct strategic decisions. Three debunked directions (TTA, imgsz=832 fine-tuning, yolo11s+exp5 via pretrained=) are avoided.

---

### REC-3: Implement per-class mAP in evaluate_on_test()

**What:** Modify `helpers/core.py` `evaluate_on_test()` to return per-class precision, recall, and mAP50. YOLO's `model.val()` returns `m.seg.cp`, `m.seg.cr`, and `m.seg.ap50`.

**Why:** All agents and the Evaluator are flying blind on class-level performance. The 15x imbalance (Leaf Spot 1365 vs Anthracnose 89) means aggregate mAP50 is dominated by the common class. Without per-class metrics, the pipeline cannot determine whether improvements target the bottleneck or the already-strong majority. This was marked P0 in gen 1 and is still unfixed.

**How:**
```python
return {
    "mAP50": round(float(m.seg.map50), 4),
    "mAP50_95": round(float(m.seg.map), 4),
    "per_class": {
        "precision": [float(x) for x in m.seg.cp],
        "recall": [float(x) for x in m.seg.cr],
        "mAP50": [float(x) for x in m.seg.ap50],
    }
}
```

**Expected impact:** The Evaluator can identify which classes are bottleneck. Agents can target rare-class improvements specifically. This changes the entire search strategy.

---

## P1 — High value, reasonable effort

### REC-4: Preserve training logs on error

**What:** Modify `train_and_eval()` in helpers/core.py to save the YOLO training output (results.csv, training curves) to a persistent location before cleanup runs, especially on error.

**Why:** explore_2's crash (gen 1) and full_1's interrupted run (gen 2) produced zero diagnostic information. With per-epoch val mAP curves, the next agent could determine whether models were still improving at epoch 20 or had plateaued. Currently, every timeout is a total loss.

**How:** Before `shutil.rmtree(_run)` in core.py, check for errors (best.pt doesn't exist, or evaluation failed) and copy the YOLO run directory to `knowledge/experiments/<solution_name>_crash/`. Save at minimum `results.csv` and the final val mAP.

**Expected impact:** Agents learn from failures. The yolo11s training curve question (was it still improving at epoch 20?) becomes answerable.

---

### REC-5: Architect must assign specific copy_paste values to avoid gaps

**What:** When assigning agents to explore "higher copy_paste values," the Architect should specify the exact value (e.g., 0.55 or 0.6) rather than leaving it open-ended.

**Why:** The 0.55-0.6 range was identified as a potential quick win in gen 1 but was skipped entirely in gen 2. The coverage matrix shows zero coverage for this range. Systematic exploration requires coordination, not independent agents making ad-hoc choices.

**Expected impact:** The copy_paste stability ceiling (currently between 0.5 and 0.65) is mapped efficiently. copy_paste=0.55 and 0.6 are tested before attempting either extreme.

---

### REC-6: Fix PROXY_EPOCHS_SCRATCH constraint mismatch

**What:** `PROXY_EPOCHS_SCRATCH = 50` in helpers/core.py exceeds the documented epoch limits (20-40 per constraints.md). full_1 attempted 50 epochs and the run kept getting interrupted, wasting 75+ minutes.

**Why:** Agents use `train_and_eval()` constants to determine epoch counts. The mismatch between the constant value (50) and the constraint (max 40) caused full_1 to choose an impossible epoch count. Its run never completed.

**How:** Change `PROXY_EPOCHS_SCRATCH` to 40 in helpers/core.py, matching constraints.md. Update the docstring to match.

**Expected impact:** full_1 type agents use achievable epoch counts. Training runs complete within time budgets.

---

## P2 — Medium effort, significant strategic value

### REC-7: Add TTA compatibility investigation

**What:** Determine WHY TTA is non-functional with exp5 and current weights. Document the root cause (export format? Ultralytics version? Model architecture?).

**Why:** TTA was the #1 recommended direction in gen 1 (REC-3, REC-9). Every plan included it. gen 2 research proved it provides zero lift. We need to know if a freshly trained model supports TTA (would require a dedicated experiment) or if the entire TTA direction is permanently closed.

**How:** The research_1 findings.md has the key observation: Ultralytics v8.4.37 issues "Model does not support 'augment=True'" warning. Determine if re-training from scratch with augment=True in training enables TTA at eval. This is a single experiment (train yolo11s at 20 epochs, test TTA on the same machine).

**Expected impact:** Either TTA is revived as a direction (retrain + use TTA) or it's permanently closed and removed from all future planning.

---

### REC-8: Fix opencode model routing (all tiers map to same model)

**What:** All `models.opencode.*` tier aliases (opus, sonnet, haiku) map to `modelgate/minimax-m2.7` in config.yaml. This means the Evaluator, Architect, and Consistency Reviewer — all configured for `opus` reasoning quality — are silently downgraded to the same model as solution agents.

**Why:** The Evaluator is supposed to do high-reasoning synthesis (evaluating ideas, updating clusters, writing coverage analysis). The sonnet/opus tiers exist to match task complexity to model capability. With all tiers using minimax-m2.7, there's no tier-based routing at all.

**How:** Either update config.yaml to point tiers to different models (if available), or acknowledge this limitation and ensure high-reasoning roles (evaluator, architect, consistency_reviewer) are explicitly routed to `claude-code` harness in `harnesses.per_agent`.

**Expected impact:** High-reasoning analysis tasks get appropriate model capacity. Quality of Evaluator output improves.

---

### REC-9: Resume interrupted evaluations on restart

**What:** The orchestrator should detect solutions that were trained but not evaluated (e.g., explore_1 sol02, full_1 sol01) and re-run their evaluation on restart rather than discarding the work.

**Why:** These solutions consumed significant GPU time (full_1 ran ~75 minutes before interruption) and represent the most important unanswered question (does yolo11s benefit from more than 20 epochs?). Losing them to a restart is wasteful.

**How:** In `phase_status()`, check for solutions in `population/genNNN/*/sol*.py` that lack corresponding `.score` files. If a `.score` is missing but the `.py` exists, mark the solution as needing evaluation and re-run it before proceeding to the next generation.

**Expected impact:** Wasted GPU time recovered. Important experiments complete. Coverage matrix fills in.

---

## Summary Table

| Rec | Priority | Expected Impact | Effort |
|-----|----------|-----------------|--------|
| REC-1: Fix finalize phase | P0 | Critical — prevents data loss on crash | Medium |
| REC-2: Rewrite State of Affairs | P0 | High — correct gen-3 planning | Low |
| REC-3: Per-class mAP | P0 | High — enables targeted improvements | Low |
| REC-4: Preserve training logs | P1 | Medium — enables failure diagnosis | Low |
| REC-5: Architect assigns copy_paste values | P1 | Medium — systematic exploration | Low |
| REC-6: Fix PROXY_EPOCHS_SCRATCH | P1 | Medium — prevents wasted runs | Low |
| REC-7: TTA compatibility investigation | P2 | Medium — resolves TTA direction | Medium |
| REC-8: Fix opencode model routing | P2 | Medium — appropriate model per role | Medium |
| REC-9: Resume interrupted evaluations | P2 | Medium — recover wasted GPU time | Medium |

(End of file - total 152 lines)
