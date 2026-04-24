# System Critic Debrief — Generation 3

## 1. What Did I Try?

I conducted a comprehensive analysis of gen003 by reading:

- **All 8 agent/debrief reports** from gen003 (architect, explore_1, explore_2, exploit_1, experimentator_1, research_1, evaluator, evaluator_debrief)
- **Previous generation summaries** (gen001, gen002, gen003 snapshots)
- **Previous system analysis and recommendations** (gen002 system_analysis.md, system_recommendations.md, experiment_suggestions.md)
- **Knowledge state**: State of Affairs (gen002), agent_gaps/gen003.md
- **Manifest and progress tracking**: manifest.yaml, gen_progress.json
- **Population outputs**: verified explore_2 produced 2 solutions, all other agent dirs were empty

I identified 6 CRITICAL/HIGH findings, wrote 3 output files (system_analysis.md, system_recommendations.md, experiment_suggestions.md), and formulated 8 recommendations with 7 experiment suggestions.

The analysis focused on three interconnected themes:
1. **Agent productivity collapse** (3/5 agents failed → 70% compute waste)
2. **The predictor experiment still not executed correctly** after 3 generations
3. **Knowledge update lag** preventing agents from using research_1's breakthroughs

## 2. What Information Did I Lack?

1. **No diagnostic evidence for failed agents.** I could not determine WHY explore_1, exploit_1, and experimentator_1 timed out. No proc_logs, no workspace artifacts, no stderr capture. The most impactful finding (agent productivity crisis) is based on circumstantial evidence (timeouts + empty dirs) rather than root cause analysis.

2. **I could not read the cayleypy source code** to independently verify research_1's API claims (BFS layers, Predictor interface, MITM integration). I trust research_1's analysis but it's a single point of failure — if research_1 made an error about `bfs_result_for_mitm`, my recommendations propagate it.

3. **I don't know the gen004 architect's prompt constraints.** My recommendation to add a "Milestone Protocol" to the architect prompt requires modifying `agents/architect.md`, but I don't know if the orchestrator has a mechanism for injecting new protocol sections or if it's purely a prompt template change.

4. **No access to GPU utilization during the generation.** research_1 reported GPU contention (only 8-10GB free of 16GB). I couldn't verify whether GPU memory pressure contributed to the 3 agent failures or whether they failed for other reasons.

5. **The light evaluator's actual output for Group 0.** gen_progress.json shows it completed, but I couldn't find its output files (knowledge/group_notes/gen003/group0.md). If it produced notes despite having zero agent output, those notes may be misleading.

## 3. What Given Facts Might Be Wrong or Outdated?

1. **State of Affairs says "trained MLP predictor NEVER TESTED end-to-end."** This is now partially outdated — explore_2/sol01 tested it with raw MLP (44094). The SoA also doesn't mention the architecture was fundamentally wrong.

2. **Idea_008 confidence (0.5) may be too high.** The raw MLP produces negligible improvement (20 moves). The embedding architecture is untested. The idea's confidence should reflect that the original approach failed and only an untested variant remains.

3. **Gen002 system recommendations (REC-1 through REC-7) are still labeled as current** but most have not been acted on. The file has not been archived or updated to reflect gen003 outcomes.

4. **The "compression ceiling at ~44114" claim** — explore_2/sol01 scored 44094, which is 20 moves below the previously reported ceiling. This suggests the ceiling is actually 44094, not 44114. The 20-move delta is negligible but the ceiling claim should be precise.

## 4. Was the State of Affairs Accurate?

**Strategically accurate, factually incomplete.**

The SoA correctly identifies:
- Compression is exhausted
- Trained predictor is the path forward
- very_hard bucket dominates (74.8%)
- Dead ends are correctly listed

**Missing from SoA (critical):**
- The model architecture was wrong for 2 generations (raw integer MLP → 5.3x worse loss)
- BFS depth 6 produces exact-distance training data (idea_010)
- CayleyPy has built-in MITM via `bfs_result_for_mitm` (idea_012)
- The combined recipe (idea_013) exists and is individually verified
- The `beam_mode='advanced'` bug
- The hasher compatibility requirement for MITM

The SoA knew WHAT to do (train predictor) but not HOW (wrong architecture, wrong training data, missed built-in capabilities). This is the most dangerous type of inaccuracy — confident direction but wrong implementation details.

## 5. What Would I Do Differently With More Context?

1. **Read cayleypy source code directly** to verify research_1's API claims before recommending the combined recipe as the #1 priority. If `bfs_result_for_mitm` doesn't work as described, my primary recommendation is wrong.

2. **Analyze GPU memory utilization patterns** to determine whether the 3 agent failures were caused by GPU contention, task complexity, or prompt issues. This would change the recommendation — if GPU contention is the root cause, reducing concurrency is the fix; if task complexity is the root cause, milestone protocol is the fix.

3. **Read the actual brief files** (briefs/gen003/*.md) to assess whether the architect's briefs were well-constructed. My analysis assumes the briefs were reasonable but the agents failed on execution. If the briefs were poorly constructed, the fix is different (fix the architect prompt, not the milestone protocol).

4. **Compute expected score improvement from idea_013** more rigorously using BFS layer sizes, beam width scaling estimates, and per-bucket analysis. My current recommendation is based on qualitative reasoning ("all components verified individually") rather than quantitative projection.

## 6. Specific Experiments to Run?

See experiment_suggestions.md for 7 detailed experiments. The top 3:

1. **EXP-1: Combined recipe (idea_013)** — BFS + embedding MLP + MITM + compression. This is the definitive experiment. If it fails, the predictor paradigm is dead.

2. **EXP-2: Architecture A/B test** — Embedding vs raw integer MLP on same training data. Quantifies the architecture impact on beam search success.

3. **EXP-4: Shallow puzzle MITM** — Use `MeetInTheMiddle.find_path_between()` on puzzles with id ≤ 20. Low-risk validation that the tooling works.

## 7. What Surprised Me?

1. **The agent productivity collapse was worse than I expected.** After gen002's 1 failure (experimentator), I expected maybe 1-2 failures in gen003. Three out of five agents producing literally nothing is a systemic problem, not an unlucky generation.

2. **research_1's output quality.** A single research agent produced 10 findings that are each individually actionable and that collectively explain why 2 generations of predictor experiments stalled. This is the highest-value single agent output of the entire run despite producing no scored solution. The research role is the pipeline's most underutilized asset.

3. **The experimentator's persistent failure.** Two consecutive generations of zero output from this role. The pipeline treats it as a regular agent but assigns it the hardest tasks (infrastructure, helper construction). This role needs either a fundamentally different task structure or should be eliminated in favor of more explore/exploit agents.

4. **The gap to target hasn't changed meaningfully.** After 3 generations and ~10 hours of compute, the best score improved by 478 moves (50572 → 44094), which is only 0.9% of the gap to target (44094 - 15000 = 29094 remaining). At this rate, reaching the target would require ~180 more generations. This suggests the current approach may be fundamentally insufficient.

## 8. Helper Tools Feedback

I did not use any helpers from `problem/helpers/` during this analysis. The system critic role reads reports and metadata, not code. The helpers I'm aware of from agent reports:

- **`helpers/core.py`**: `cayleypy_beam_solver`, `load_sample_submission_paths`, `compression_ratio` — used by solution agents. No bugs reported in gen003. However, `cayleypy_beam_solver` doesn't expose `predictor` or `bfs_result_for_mitm` parameters, which limits its usefulness for the combined recipe.

- **`helpers/trained_predictor_beam_search.py`**: Has the wrong model architecture (raw integer MLP). research_1 confirmed the embedding-based architecture is 5.3x better. This helper needs to be updated before any agent uses it again.

**Helper I wish existed:** `problems/megaminx/docs/cayleypy_api.md` — a reference document of cayleypy's key APIs with usage examples, based on research_1's source code analysis. Every agent that touches cayleypy currently spends turns rediscovering the API. A reference document would save 5-10 turns per agent session and prevent the "wrong architecture for 2 generations" problem.

## 9. Time Budget

Sufficient. The analysis was straightforward — only 1 scored solution to evaluate (gen003_explore_2_sol01 at 44094) and the real value was in the agent reports and research findings. The most time-consuming part was reading 8 reports + 3 generation summaries + 2 previous system analyses to build a complete picture.

With more time I would have:
1. Read the actual brief files (briefs/gen003/*.md) to assess architect brief quality
2. Read the cayleypy source code to verify research_1's API claims independently
3. Checked the light evaluator's output for Group 0 to verify it handled the empty-group case correctly
4. Analyzed GPU utilization patterns to distinguish GPU contention failures from task complexity failures
5. Attempted to compute a quantitative projection of idea_013's expected score improvement
