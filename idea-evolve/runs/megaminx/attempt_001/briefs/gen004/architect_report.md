# Architect Report — Gen 004

## Confidence
**Medium-high** on the overall plan. Medium on the execution outcomes.

- Plan: the single most valuable experiment (idea_013 combined recipe) is finally scheduled with a milestone-protocol safety net. Track B (GNN + research) keeps diversity alive. Scope is bounded and every agent has a guaranteed path to at least one scored solution.
- Execution: gen003's failure mode — 3 agents producing zero output in 6300s each — can recur if the milestone protocol is ignored. I have embedded it in every complex brief (exploit_1, experimentator_1, explore_1, explore_2) with concrete "must produce sol01 first" language and an explicit compression-only fallback for insurance. But the system does not yet enforce milestones programmatically (REC-1 asked for it — not yet wired in), so I am relying on the agents to follow instructions. If they don't, we get a rerun of gen003.

## Data anomalies worth flagging

1. **Gen003 had THREE agents hit the work+wrap_up+debrief full timeout chain (6300s each).** That is not a timeout tuning problem — the agents are apparently getting stuck in long generation loops with no checkpoint. The milestone protocol I have enforced should address this, but if gen004 shows the same pattern, the issue may be Claude Code (or opencode) itself silently hanging on long-lived subprocesses, which would need investigation at the harness layer, not the architect layer.
2. **7 solutions converge at exactly 44114 (compression floor).** This is strong evidence that compression is saturated — but also possible evidence that the eval cache is returning the same score for solutions that are actually different. Worth a sanity-check pass from the Evaluator: compare content hashes of the 7 top solutions. If two have identical hashes, something is wrong with agent name folding; if they have different hashes but identical per-bucket breakdowns, the compression transform is genuinely deterministic and we've hit a real ceiling.
3. **Single-solution jump from 44114 → 44094 (20 moves) from gen003_explore_2.** explore_2 optimized path suffixes only (not full paths) and the improvement is small. This suggests the predictor was weak AND that compression + local-edit is close to converged. The combined recipe (exploit_1's task) should produce a much larger jump if it works — anything beating 44000 would meaningfully shift the trajectory.
4. **The "very_hard" bucket is 74.8% of total score.** This is an extreme concentration. Small gains on short/medium puzzles are nearly invisible in total fitness. Any gen004 finding that does NOT move the very_hard bucket is a strategic dead end even if it looks like progress on the other buckets.

## What didn't fit

- **A dedicated "verify 44114 compression is truly saturated" pass.** Someone could run a quick experiment to confirm the 7 different-looking solutions really all hit the same score for the same reason. Didn't budget an agent for this — the Evaluator can do it end-of-gen during knowledge consolidation.
- **A path-database (PDB) exploration.** Classical Rubik's-family tool. research_1's brief mentions PDBs as a thread to survey, but no agent is building one. If research_1 confirms PDBs are the top Kaggle paradigm, gen005 must try it.
- **A proper DeepCubeA reading.** research_1 will cite it; nobody will implement it this generation. Expect this to be a gen005 experimentator task if research_1 confirms applicability.
- **Cleanup of idea_004 (manual MITM, superseded).** REC-8 asks for it; I left it for the Evaluator or Consistency Reviewer to archive properly (not an architect task to file-move).
- **Cayleypy API documentation (REC-6).** Not building this as a gen004 task. research_1 was supposed to produce it in gen003 but went wide instead. The API facts are distributed across idea_010–012; agents can piece them together.

## Strategic risks

1. **If exploit_1's combined recipe produces a score worse than 44114:** we learn the predictor paradigm is stuck at compression-level performance, which invalidates 2 generations of knowledge base direction. Then gen005 must pivot to whatever research_1 identifies. High-impact negative result.
2. **If experimentator_1's helper fails validation:** gen005 agents have to rewrite the recipe boilerplate again. Recoverable but annoying.
3. **If explore_1's GNN trains but doesn't produce valid paths:** we spent 1800s on a negative result. Acceptable cost for a Track B radical. The GNN idea moves to a "debunked" pattern in the knowledge base.
4. **MPS contention (see manifest_reasoning risk #1).** If three GPU-heavy processes fight for VRAM, one or more may crash with OOM. The staggered group structure (3 → 2) helps but does not eliminate the risk. Mitigation: the briefs instruct agents to start with modest beam widths and scale up only after confirming no OOM.
5. **Milestone protocol is a LLM-level instruction, not a system enforcement.** An agent that ignores it will hang identically to gen003. Trust is load-bearing.

## Open questions for the System Critic

1. **Should the Milestone Protocol be enforced at the orchestrator level?** REC-1 proposed adding it to `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/agents/architect.md` (which I have effectively done via briefs, but the architect-prompt change isn't there yet). A stronger enforcement would have the orchestrator kill an agent that hasn't produced ANY scored output by the `min_first_milestone_s` deadline. Worth adding to `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/user/config.yaml`.
2. **Should gen004's work timeout default be reduced system-wide (REC-4)?** Gen003 agents that hung used ALL their timeout; lowering the default won't fix the hang but will detect it faster and free compute. I left per-agent timeouts explicit for gen004 (2100s for exploit_1, etc.) rather than lowering the default, but the default reduction is worth doing in `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/user/config.yaml` regardless.
3. **Is cayleypy's `beam_search` reliably reentrant under MPS?** If not, concurrency: 3 is a bug. The evidence from gen001–gen003 is thin — mostly single-agent usage. Gen004 will be the first real concurrent-predictor-beam test. If we see mysterious failures in group 1, this is a likely root cause.
4. **Does the eval cache distinguish between a predictor trained from seed A vs seed B?** If content-hash caching sees two solutions that only differ in training RNG, it might return a stale score. The `solve_all` function should embed the random seed in the solution file (or use `torch.manual_seed`) to ensure reproducible evaluations under caching.
5. **Should the 7 compression-floor solutions be pruned from `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/`?** Keeping 7 copies of a 44114 variation consumes slots that could hold more diverse results. Not an architect call — this is a population-management policy decision.

## What I would do differently if gen004 fails

If exploit_1 produces no scored solution OR the combined recipe scores worse than 44114:
- Gen005 pivots hard to whatever research_1 surfaces. Kaggle-top paradigm becomes the primary Track A task.
- Keep at most one exploit on predictor tuning.
- Add an experimentator for pattern databases if research_1 confirms applicability.
- Escalate to Consistency Review: the 2-generation assumption that "embedding MLP + beam + MITM is the path forward" needs re-audit.

If 3 or more agents time out without output (gen003 recurrence):
- This is a harness-level problem. Investigate before launching gen005. Possibly reduce max_turns aggressively or switch to a different harness for the next run.
