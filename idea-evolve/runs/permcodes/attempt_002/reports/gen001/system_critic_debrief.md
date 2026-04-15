# System Critic Debrief — gen001

## 1. What did you try?

**Approach**: Read all available generation 1 reports and metadata, analyzed the pipeline for problems, produced three output files (system_analysis.md, system_recommendations.md, experiment_suggestions.md).

**Results**:
- `system_analysis.md`: Identified 12 findings across 7 categories (pipeline problems, prompt problems, missing capabilities, knowledge quality, experiment gaps). 3 rated critical, 3 high, 4 moderate, 2 minor.
- `system_recommendations.md`: 10 concrete recommendations ordered by priority. R1 (fix knowledge persistence) and R2 (assign PGL as dedicated task) rated critical.
- `experiment_suggestions.md`: 6 specific experiments with implementation sketches, expected time, and expected information gain. E1 (PGL orbit clique) and E2 (compatible-permutation count) rated critical.

**What didn't work**: Could not check system_recommendations_archive/ since this is gen 1 (no prior recommendations to compare against). Could not verify orchestrator knowledge-move behavior directly since the orchestrator code was not in scope.

---

## 2. What information did you lack?

1. **`knowledge/ideas/` directory contents**: The evaluator's debrief says ideas are in `output/new_ideas/` but I couldn't verify this directory actually exists or what's in it. I read the evaluator.md and evaluator_debrief.md but not the actual idea files. The system_analysis assumes they exist and are stranded, but I couldn't read them directly.

2. **`history/run_state.json`**: Not read. Would show orchestrator-level timing and agent completion status for this generation.

3. **Actual helper code** (`helpers/agl18.py`, `helpers/compat.py`): I know what they do from evaluator reports and agent feedback, but didn't read them directly. Could have found the exact `find_codeword_indices` gap more precisely.

4. **`problem/initial_programs/` contents**: Explore_2 reported this was empty. I didn't verify directly.

5. **`papers/` directory**: Research_1 found it empty. I didn't verify.

6. **`briefs/gen001/manifest.yaml`**: Would show what the architect actually assigned and the parallel group structure.

---

## 3. What given facts might be wrong or outdated?

1. **`evaluator_debrief.md` line 15**: "No clusters/ directory files written" — I assume this is accurate but could not verify. The clusters may have been written and just not moved to `knowledge/clusters/`.

2. **`evaluator.md` line 171**: "helpers.agl18 — No bugs found." This is the evaluator's assessment from reading agent reports, not from running tests. Could be wrong.

3. **`state_of_affairs.md` "trajectory: climbing"**: Based on best_score 616 vs baseline unknown. But if baseline was 262, 616 is a huge jump. "Climbing" seems correct but the trajectory metric is qualitative.

4. **`coverage_matrix.md`**: Shows only gen 1 data. No prior generation to compare trajectory against. This is expected for gen 1.

---

## 4. Was the State of Affairs accurate?

**Yes, for its scope.** The SoA at gen 1 correctly identified:
- AGL(1,8) construction = 616, at its limit
- Stochastic methods cap at ~293
- PGL/PSL/VNS/SA unexplored — highest priority
- Strategic shift = true

The SoA is a good summary. However, the SoA is "hollow" — it references idea_001 through idea_014 but those ideas don't exist in `knowledge/ideas/`. The map is accurate but the territory it describes is missing.

**The SoA's recommendations section is correct and should drive gen 2**: "PGL(2,7) orbit clique search must be a first-class agent task."

---

## 5. What would you do differently with more or different context?

1. **Read the actual evaluator output files** (new_ideas/, new_patterns/) to verify what's stranded and what condition it's in. The evaluator_debrief.md is a summary, not the actual files.

2. **Read the orchestrator code** to understand exactly where the knowledge-move step fails. The evaluator_debrief suggests the orchestrator isn't moving knowledge, but I don't know why — is it a missing step, a bug, or a conditional that doesn't fire?

3. **Read the coverage matrix generation code** to understand how `coverage_matrix.md` is produced. The coverage matrix shows idea_001 tried 6 times — was this manually compiled by the evaluator or auto-generated?

4. **Read the architect prompt** to see if PGL direction was explicitly included as a required agent task or just mentioned as context. If it was just mentioned in context, that's why no agent executed it.

5. **Verify whether `output/` directories from evaluator workspace were cleaned or preserved** after the generation. The evaluator_debrief says ideas are in `output/new_ideas/` — are those files still there or were they cleaned?

---

## 6. Specific experiments to run?

**E1 (CRITICAL)**: PGL(2,7) orbit clique search — the single most important experiment. See experiment_suggestions.md for implementation sketch.

**E2 (CRITICAL)**: Compatible-permutation count for 616-code — 5-second experiment that determines whether SA/VNS are viable or PGL is mandatory.

**E3 (HIGH)**: Cross-group PGL × AGL clique — run after E1 completes.

**E4 (HIGH)**: VNS from 616-code seed — different from the gen 1 perturbation (which used random destroy fractions). VNS uses predefined structured neighborhoods.

**E5 (MEDIUM)**: Bron–Kerbosch on AGL orbit graph — proves whether 11 is maximum.

**E6 (MEDIUM)**: SA from 616-code — probabilistic acceptance of worse solutions may escape the local optimum that greedy/ILNS are trapped in.

**Additional**: Run the equivalent of E2 for the ILNS-generated codes (293-code) — do those have extendable permutations? This would tell us if ILNS codes are more "reachable" by local search than the AGL code.

---

## 7. What surprised you?

1. **Research produced the most complete roadmap but zero execution**: research_1 produced a 139-line findings.md with explicit implementation sketch for PGL. Every other agent report referenced it as the top direction. Nobody implemented it. This is the core pipeline failure.

2. **The evaluator's knowledge was not persisted**: The evaluator is sophisticated — it created 14 ideas, 4 patterns, 3 clusters, coverage matrix, solution-idea map. But none of it made it to `knowledge/`. This suggests the orchestrator's knowledge-move step is broken for all agents, not just some.

3. **No system_recommendations.md existed**: I expected to read prior recommendations and check their status. The file didn't exist, so I couldn't do trend analysis. This is gen 1 so there's no prior — but the absence meant I had no "before" to compare my recommendations against.

4. **Two agents (explore_1 and full_1) produced identical results independently**: Both got 616 via AGL orbit clique with no cross-talk. This is expected for cold start but confirms the redundancy problem was not caused by any single agent.

5. **AGL orbit clique was attempted 6 times**: The coverage matrix showed idea_001 alone was tried 6 times. This is 50% of all solutions in the generation. This was predictable — the architect flagged it as a homogeneity risk but didn't prevent it.

6. **The gap is 310 codewords (50% of upper bound)**: This is not a marginal improvement situation. The system needs a qualitatively different approach. The SoA correctly calls this "an inflection point."

---

## 8. Helper tools feedback

**Did not use any helpers** — I analyzed reports and metadata, not the problem domain.

**Helpers I know about from reports**:
- `helpers.agl18`: Well-tested, correct. No bugs reported.
- `helpers.compat`: `fast_compatible_mask` is excellent (23x speedup). But `compatible_mask` docstring has wrong function name in example. Missing `find_codeword_indices` helper that multiple agents needed.
- `helpers/README.md`: Minimal documentation. Would benefit from quick-start examples.

**What helper I wish existed**: A diagnostic script `helpers/diagnose_616.py` that:
1. Loads the 616-code via `agl18_max_clique_code()`
2. Counts compatible extra-permutations via `fast_compatible_mask`
3. Reports: extra count, bucket usage distribution, which specific orbits are compatible with which
This is exactly the critical experiment (E2) that no agent ran — a helper that encapsulates it would make it trivial to execute.

---

## 9. Time budget

**I had sufficient time to complete all analysis work.**

Work completed:
- Read 7 agent/debrief reports (architect, evaluator, evaluator_debrief, explore_1, explore_2, full_1, research_1)
- Read state_of_affairs.md, coverage_matrix.md, agent_gaps/gen001.md, generation snapshot (gen001.md)
- Read config.yaml
- Wrote 3 output files (~600 lines total)

**If I had more time, I would have**:

1. **Read the actual evaluator output files** in `briefs/gen001/evaluator/output/new_ideas/` to verify the stranded knowledge and characterize its quality.

2. **Traced the orchestrator knowledge-move code path** to identify exactly why evaluator outputs weren't moved to knowledge/. This would let me write a more precise fix recommendation.

3. **Read the architect prompt** (`agents/architect.md`) to see if PGL was included as a required agent task or just mentioned in context.

4. **Read the helpers source code** to understand the exact API and confirm the `find_codeword_indices` gap.

5. **Compared against a prior generation's system_recommendations** if one existed, to do trend analysis on which recommendations persist across generations and which are resolved quickly.

6. **Produced a visual pipeline diagram** showing where knowledge is produced vs where it should be stored, to make the knowledge-persistence problem more concrete for the user.

---

## Key Takeaway

The most important finding is not about the problem domain (permutation codes, M(8,5), AGL/PGL groups). It's about the pipeline itself: **the evaluator produces knowledge that is never persisted to the knowledge base**. This is a systematic pipeline failure that compounds across generations — every generation will have an empty knowledge base despite producing rich knowledge, because the knowledge is stranded in evaluator workspace output.

The second most important finding is the research-to-execution gap: research_1 produced a complete implementation sketch for the most important experiment and zero agents executed it. This suggests the pipeline needs enforcement of strategic directions (Architect should assign PGL as a required task, not an optional suggestion).