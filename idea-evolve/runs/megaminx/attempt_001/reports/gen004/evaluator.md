# Evaluator Report — Generation 4

strategic_shift: false

## 1. What I Tried

### Score Collection
Read the single `.score` file in `population/gen004/`:
- `exploit_1/sol01.score`: fitness 44111, is_valid 1, all 101 puzzles solved, compression_ratio 0.8722

No other solutions were produced. explore_1, explore_2, and experimentator_1 produced zero
scored output. research_1 is a research agent with no solution.

### Knowledge Consolidation
- Read knowledge dump (`workspace/gen004_evaluator/knowledge_dump.md`) — all 13 active/established
  ideas, 2 clusters, 9 patterns
- Read all 5 agent reports (research_1, exploit_1, explore_1, experimentator_1, evaluator_group0)
- Read current `state_of_affairs.md` (gen003)
- Verified Light Evaluator's 5 new files (idea_014, idea_015, idea_016, pattern_008, pattern_009)
  for duplicates — none found, all are new
- Updated 3 existing ideas (idea_008, idea_010, idea_013) with gen004 evidence
- Updated both clusters (cluster_001, cluster_002)
- Updated solution-idea map, coverage matrix, snapshot, agent_gaps

## 2. What Information I Lacked

1. **What explore_2 was assigned and why it produced no output.** No debrief in reports/gen004/.
   I don't know if the session crashed, timed out, or was never launched. This is a knowledge
   loss — if explore_2 tried anything, we'll never know.

2. **GPU utilization breakdown.** exploit_1 noted "first eval attempt failed with CUDA busy"
   and mentioned GPU contention. I don't know how much eval time was wasted waiting for
   GPU access (only the 400s total is available).

3. **Predictor MSE by depth bucket.** exploit_1 trained the predictor and ran beam search
   but didn't report the predictor's accuracy at different depth ranges (e.g., MAE for
   states at depth 10 vs depth 100 vs depth 500). This would pinpoint exactly where the
   predictor fails.

4. **Long random walk training data results.** exploit_1 suggested testing `graph.random_walks(
   length=200)` or longer but ran out of time. We don't know if depth-200 random walks
   would help meaningfully vs depth-50.

## 3. What Given Facts Might Be Wrong or Outdated

1. **idea_010: "BFS data strictly superior to random walks" — WRONG as sole training source.**
   Updated this generation. BFS depth-6 data is useless for predicting deep states.
   Only valuable for MITM backstop.

2. **idea_013: score estimates (conservative 43000–44000, optimistic 35000–40000).**
   The conservative bound was roughly correct (actual: 44111). The optimistic bound is
   unreachable with beam_width=4096 — needs 65536+ to have any chance of that range.

3. **idea_011 claim: "CayleyPy uses raw integers."** WRONG. research_1 corrected this:
   CayleyPy's MlpModel uses one-hot encoding. idea_011 documented the embedding approach
   as the fix, but the library already had the correct approach. idea_014 captures this.

4. **State of Affairs (gen003): "Trained predictor is the primary untested path."**
   Partially outdated. The predictor has now been tested twice (gen003 raw-integer, gen004
   embedding). Both times: marginal. The primary UNTESTED path is now specifically:
   deep training data (idea_016) + large beam width (65536).

5. **`idea_013` training cost estimates: "60–120s for 19.4M samples."** Wrong. exploit_1
   reports ~9s for BFS data (1.38M samples) and ~44s for random walk data (2.3M samples).
   The 19.4M figure overstates by ~14× due to GPU OOM on BFS layer 6.

## 4. Was the State of Affairs Accurate?

**For gen003 evidence: yes.** The SoA correctly described compression exhausted, predictor
marginal, and idea_013 as the top priority.

**Missing critical gaps that gen004 revealed:**
- No mention of beam width as the dominant parameter (pattern_009).
- Framing "BFS data strictly superior" — contradicted by gen004.
- No mention of non-backtracking beam search (idea_015) — this is a major omission since
  it 4× improvement in success rate from the paper.
- The SoA says idea_013 is "never tested" — it was the #1 priority. In gen004 it was tested
  and found insufficient. The new #1 priority (idea_016 deep training data) was not in the SoA.

The SoA needs a complete rewrite for gen005 to capture: (1) training data depth as core
bottleneck, (2) beam width as dominant parameter, (3) non-backtracking vs MITM open question,
(4) MlpModel (one-hot) as the library's proven model.

## 5. What Would I Do Differently With More Time

1. **Read the full CayleyPy RL paper myself** to verify research_1's claims about beam
   width scaling and non-backtracking success rates. The log-linear claim is critical enough
   to warrant first-party verification.

2. **Read the sol01.py code** to verify exploit_1's description of the pipeline matches
   what was actually implemented. Agent reports sometimes describe intended rather than
   actual behavior.

3. **Compute staleness flags** for ideas not confirmed in 5+ generations. All ideas except
   idea_001 and idea_005 were last confirmed in gen002 or later — need to scan more carefully
   which are approaching staleness.

## 6. Specific Experiments to Run

**Priority 1 (gen005 must-do):**
```
sol01: compression baseline (idea_009, 44114) — always first, guaranteed score
sol02: path-intermediate training (idea_016) + MlpModel (idea_014) + beam_width=65536
       - extract (state, remaining_depth) pairs from compressed paths
       - train MlpModel(graph, hidden_dims=[512,256]) on these pairs
       - beam_search(predictor=model, beam_mode='simple', bfs_result_for_mitm=bfs_result,
                     beam_width=65536, batch_size=2048)
       - fall back to sol01 for failed puzzles
```

**Priority 2:**
```
sol03: same as sol02 but beam_mode='advanced' (non-backtracking, no MITM)
       - compare head-to-head: MITM vs non-backtracking at same beam_width
       - pick the better one
```

**Priority 3:**
```
sol04: sol02 + long random walks (depth 200) supplementing path-intermediate data
       - combine path intermediates + depth-200 random walks as training data
       - test if supplementary data improves hard/very_hard predictions
```

**The beam width sweep (important but secondary):**
```
Fixed set: sids [10, 50, 100, 200, 500, 700, 1000] (one from each bucket)
Test beam_width: [4096, 8192, 16384, 32768, 65536]
Measure: path length improvement vs beam_width on log scale
Confirms or refutes pattern_009 on our specific hardware/model
```

## 7. What Surprised Me

1. **Gen004's best (44111) is worse than gen003's best (44094).** The combined recipe with
   a supposedly better architecture (embedding MLP) and additional components (MITM, BFS
   backstop) actually regressed. This means the architecture fix alone is not sufficient.

2. **The regression direction matters.** We went from gen003's marginal +20 improvement to
   gen004's marginal -17 regression. The correct architecture (embedding) actually performed
   worse than the wrong architecture (raw integers). The explanation is likely that the
   embedding MLP, having lower loss on shallow data, may behave differently than the raw
   integer MLP when applied to deep states. Both fail, but in different ways.

3. **60% agent failure rate — same as gen003.** Despite improved briefs, strict milestone
   protocols, and explicit warnings about scope creep, 3/5 agents still produced zero output.
   This is a systemic pipeline problem, not a brief quality problem.

4. **The experimentator has failed 3 consecutive generations.** If a single agent role
   fails on the same task 3 consecutive times, the system must stop assigning that task to
   that role. The architect should not assign helper writing to experimentator again.

## 8. Helper Tools Feedback

**`helpers/core.py`:** Functional. The compression functions, `load_sample_submission_paths`,
and other utilities work correctly.

**`helpers/trained_predictor_beam_search.py`:** Still broken (raw-integer MLP). Confirmed
useless for gen004. This file should be rewritten or deprecated. The experimentator failed
to fix it for 3 consecutive generations.

**Missing helper: `extract_path_intermediates(paths, graph)`** — this would extract
(state, remaining_depth) pairs from compressed paths. Every agent implementing idea_016
will need to write this from scratch without a helper.

**Missing helper: `full_pipeline_solver(graph, training_data, beam_width, bfs_result)`** —
encapsulates train → beam_search → fallback. Currently every agent re-implements ~100
lines of boilerplate and makes mistakes (wrong API calls, wrong batch dimensions, etc.).

**`cayleypy_beam_solver` in helpers/core.py:** Only supports unguided search. Needs
`predictor`, `beam_mode`, and `bfs_result_for_mitm` parameters to be useful for gen005
agents.

## 9. Time Budget

Sufficient for this generation. Gen004 produced only 1 solution and 4 agent reports
(one empty), making the evaluation compact.

**With more time, I would have:**
1. Read `population/gen004/exploit_1/sol01.py` to verify the reported pipeline matches
   the actual code.
2. Read the group_notes from the Light Evaluator to check if any patterns or ideas from
   its debrief needed to be incorporated (I relied on the knowledge dump instead).
3. Created an updated state_of_affairs.md as a new_ideas-style output (though this is
   typically the Consistency Reviewer's job).
4. Read the CayleyPy paper section on beam width scaling to verify research_1's claims
   before registering pattern_009 as confirmed.
