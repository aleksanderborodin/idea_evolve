# Architect Report — Generation 3

## Confidence: Medium

The plan is sound given what we know, but there are several things that felt off about this generation's data that make me uncertain.

## Data Anomalies

1. **Gen 2 complete stalemate:** Zero improvement over gen 1 (best stays 0.8328). But gen 2 closed 3 major directions at once — this is actually positive (wasted computation avoided). The strategic redirection was correct, just not productive yet.

2. **Architecture mismatch between yolo11s and exp5 was unknown:** The exploit_1 agent in gen 2 spent an entire evaluation cycle discovering that pretrained= does wholesale weight replacement, not fine-tuning. This should have been knowable from documentation. Next Architect should not plan yolo11s+exp5 via pretrained= as a viable direction.

3. **Two solutions timed out before evaluation (explore_1 sol02, full_1 sol01):** These consumed significant GPU time (~75 min for full_1) and produced zero data. The orchestrator infrastructure for handling long-running evaluations is inadequate. This is a recurring problem (gen 1 explore_1 also timed out).

4. **No per-class mAP data after 2 generations:** This is the most glaring gap. Every agent report cited it. The system critic marked it P0. Yet no experimentator was assigned to fix it until now (gen 3). This is a systemic failure, not just bad luck.

5. **Gen 2 timing was extremely high:** The architect session itself took 1922.9s (32 min) — nearly the entire generation budget. Something caused the Architect to take 18x longer in gen 2 vs gen 1 (108.6s). Possibly the pre-concatenated knowledge dump wasn't available yet, causing more file reads. If gen 3 architect times out, that's a pipeline problem.

## What Didn't Fit

- **copy_paste=0.55-0.6 range:** Completely untested after 2 generations. REC-5 from system critic (Architect assigns specific values) was never implemented in gen 2 planning. I'm fixing this in gen 3 by assigning specific values.
- **Progressive resizing:** Only untested approach for the resolution hypothesis. Should have been tried in gen 2, but the explore_1 was assigned to imgsz=832 direct fine-tuning instead (which failed).
- **Per-class metrics:** REC-3 P0 since gen 1. Now gen 3 and we're just implementing it.

## Strategic Risks

1. **Over-reliance on yolo11s from COCO at 20ep = 0.8328:** This is the only strong result in 2 generations. If it turns out to be noise or a lucky seed, the entire search strategy has been built on a fragile foundation. The exploit_1 40ep experiment is the most important single data point in the run.

2. **Progressive resizing may still fail:** Even the staged approach might not work. If both explore_1 (progressive resizing) and exploit_1 (yolo11s 40ep) fail this generation, we have no clear path to 0.92+.

3. **copy_paste ceiling may be below 0.55:** If explore_2 crashes at both 0.55 and 0.6, the only safe value is 0.5 and the class imbalance direction is essentially closed.

4. **Experimentator modifies helpers/core.py incorrectly:** If the experimentator's code change breaks evaluate_on_test(), it affects all future generations. The orchestrator needs to validate carefully.

5. **Research findings sit unimplemented:** If research_1 finds that per-class data shows Anthracnose is the bottleneck and TTA is permanently non-functional, those findings need to be actioned in gen 4 — not filed and forgotten.

## Open Questions for the System Critic

1. **Is the 0.8328 baseline real or noise?** yolo11s from COCO at 20 epochs has only 1 data point. Need confirmation from exploit_1's 40ep run. If it plateaus at 0.8328, the approach is exhausted.

2. **Why did gen 2 full_1 timeout consistently?** 50 epochs was the culprit (PROXY_EPOCHS_SCRATCH = 50 exceeds constraints.md max of 40). But even with corrected epoch count, long-running evaluations seem to get killed by the infrastructure. What is killing them?

3. **What is the actual RTX 5060 Ti memory limit?** explore_1 will test this with progressive resizing. If OOM at 832, we need to know batch size limits.

4. **Is the val-test gap from resolution or distribution shift?** The imgsz=832 fine-tuning destroyed domain knowledge (0.5453 regression vs 0.7876 zero-shot at same resolution). But we don't know if the gap is resolution-specific or a general distribution shift problem.

5. **Should gen 4 switch to yolo11m if yolo11s succeeds?** The scaling path is yolo11s → yolo11m → yolo11l. But we need to know if more parameters help before committing compute to larger models.

6. **REC-8: OpenCode model routing** — All opencode tiers map to the same model (minimax-m2.7). The architect, evaluator, and consistency reviewer are supposed to get opus-tier reasoning but are silently downgraded. This affects quality of all high-reasoning tasks. Needs explicit routing to claude-code for these roles or tier-based model selection.