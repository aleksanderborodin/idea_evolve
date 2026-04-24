# Light Evaluator Debrief — Group 0, Generation 4

## 1. What I Tried

Read and analyzed outputs from 3 agents in group 0:

- **exploit_1** (sol01, score 44111): Full combined recipe with embedding MLP + random walk training + MITM beam search. Marginal improvement (3 moves over compression). Confirmed embedding MLP architecture works but training data depth is the bottleneck.
- **experimentator_1**: Zero output. Timed out with empty directories. Second consecutive failure on the helper creation task.
- **research_1**: Major literature review — read CayleyPy RL paper (32 pages), CayleyPy-1 paper, source code, DeepCubeA paper. Found critical corrections to our understanding of the library's architecture.

Created 3 new ideas and 2 new patterns after checking all 10 existing ideas (7 active, 3 established) and 7 existing patterns for duplicates.

## 2. What Information I Lacked

- Could not read experimentator_1's failed session to understand why it timed out (no logs, no artifacts)
- Did not have access to the CayleyPy papers myself (relied on research_1's report)
- Could not verify research_1's claims about MlpModel source code without reading it directly (chose to trust the agent's report since it cited specific file paths and line numbers)

## 3. What Given Facts Might Be Wrong or Outdated

- **idea_011 (embedding MLP)** is partially outdated — research_1 found that CayleyPy's MlpModel uses one-hot, not our custom embedding. The embedding approach is valid but the library already has a proven model. idea_014 updates this.
- **idea_010 (BFS training data "strictly superior")** is wrong for this use case. exploit_1 proved BFS-only data produces a useless predictor. The SoA's claim needs correction.
- **idea_013 score estimates** (conservative 43000-44000, optimistic 35000-40000) are accurate — exploit_1 hit 44111, near the conservative bound. The optimistic bound appears unreachable with beam_width=4096.

## 4. Was the State of Affairs Accurate?

Mostly accurate for what it covers. Missing:
- No mention of one-hot encoding as the library's actual approach (vs our embedding assumption)
- No mention of non-backtracking beam search as an option
- No mention of beam_width as the dominant scaling parameter
- The claim "BFS data is strictly superior to random walks" (idea_010) should be qualified: superior for shallow puzzles, useless for deep ones

## 5. What Would I Do Differently

Would have read `models/models.py` from the CayleyPy source myself to verify research_1's finding about one-hot encoding before creating idea_014. The claim is critical enough to warrant first-party verification.

## 6. Specific Experiments to Run

1. **MlpModel + beam_width=65536 + non-backtracking**: The definitive experiment. Use CayleyPy's built-in model, maximum beam width, advanced mode. This should be the #1 priority.
2. **Path-intermediate training + MlpModel**: Train on compressed-path intermediates (idea_016) for full depth coverage, then beam search.
3. **Beam width sweep**: 4096 → 8192 → 16384 → 32768 → 65536 on a fixed 10-puzzle subset to quantify the log-linear relationship on Megaminx specifically.

## 7. What Surprised Me

- exploit_1's result (44111) is actually WORSE than gen003's best (44094). The combined recipe with corrected architecture + better training data performed worse than gen003's ad-hoc approach. This suggests the training data depth problem is even more severe than expected.
- The experimentator has now failed 2 consecutive generations on the same task. The architect should consider routing this work to a full/explore agent instead.

## 8. Helper Tools Feedback

Did not use helpers directly. Noted that `cayleypy_beam_solver` in helpers/core doesn't expose predictor, beam_mode, or beam_width parameters, forcing every agent to re-implement the full pipeline.

## 9. Time Budget

Sufficient. All 3 agent outputs were compact (1 solution, 2 research reports, 1 empty experimentator). Reading existing ideas took the most time (10 files). Would have liked to verify research_1's source code claims by reading CayleyPy's `models/models.py` directly, but the finding is well-documented enough to act on.

## Files Produced

- `output/new_ideas/idea_014.md` — CayleyPy built-in MlpModel (one-hot)
- `output/new_ideas/idea_015.md` — Non-backtracking beam search
- `output/new_ideas/idea_016.md` — Path-intermediate training data
- `output/new_patterns/pattern_008.md` — Shallow training data → useless deep predictor
- `output/new_patterns/pattern_009.md` — Log-linear beam width scaling
- `output/group_notes.md` — Summary for next group
