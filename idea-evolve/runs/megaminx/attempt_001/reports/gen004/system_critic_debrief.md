# System Critic Debrief — Gen 004

## 1. What I Tried

I conducted a comprehensive pipeline analysis covering all 5 agent reports, the evaluator report, the light evaluator report, the architect report, population outputs, timing data, the coverage matrix, agent gaps analysis, and the full knowledge base state.

**Key findings produced:**
- Identified that the milestone protocol failed as an LLM-level instruction for the 2nd consecutive generation (PA-1)
- Diagnosed the experimentator role as broken for this problem after 3 consecutive failures (PA-2)
- Detected the first score regression in the run (PA-3: 44111 < 44094)
- Traced idea_010 (BFS data superiority) as actively misleading for 2 generations (KQ-1)
- Identified beam_width ≤ 4096 as the single biggest unexplored parameter (EG-1)
- Proposed pre-injecting compression baselines as a system-level fix for agent failures (REC-1)

## 2. What Information I Lacked

1. **Explore_2's session details.** No debrief report exists. I don't know if explore_2 was assigned a GNN task (as the architect planned for Track B), crashed, or was never launched. The timing data shows it ran for 1831s with 11.8s wrap_up and 14.3s debrief — the short wrap_up/debrief suggest immediate failure or crash.

2. **Experimentator_1 timing data.** The timing.json doesn't include experimentator_1 entries for gen004, even though the agent was launched and produced empty output. I don't know how long it ran or which phase it was in when it failed.

3. **Per-bucket breakdown from gen003 best (44094).** I could compare exploit_1's gen004 per-bucket scores against the gen004 sol01 but not against gen003's explore_2 sol01 (the previous best). The score files should be comparable but I didn't read the gen003 score file to check.

4. **Whether the architect's manifest for gen004 actually included explore_2.** The architect report mentions Track A (exploit_1, experimentator_1) and Track B (explore_1, explore_2, research_1), but I couldn't verify the actual manifest.yaml that was produced.

5. **The actual sol01.py code from exploit_1.** The evaluator noted it didn't have time to verify that exploit_1's reported pipeline matches the actual code. I also couldn't verify this. The agent may have described an intended pipeline that differs from what was implemented.

## 3. What Given Facts Might Be Wrong or Outdated

1. **The SoA's framing of the predictor as "the primary untested path."** It's been tested twice now (gen003 raw integer, gen004 embedding). Both marginal. The real untested path is beam_width > 4096.

2. **pattern_006 says "raw integer MLP is ineffective."** This is true but misleading. The real pattern should be "wrong state encoding (raw integers instead of one-hot or embedding) produces 5.3× worse training loss." The MLP architecture itself is fine — it's the input representation.

3. **The 44094 result from gen003 is presented as a predictor improvement (+20 over compression).** But this improvement used the WRONG architecture (raw integer). The gen004 result with the CORRECT architecture (embedding) scored worse (44111). This suggests the gen003 improvement may have been due to the tail-optimization approach (optimizing path suffixes), not the predictor itself.

## 4. Was the State of Affairs Accurate?

**For gen003 evidence: yes, mostly accurate.** The SoA correctly identified compression as exhausted and idea_013 as the top priority.

**Missing from SoA:**
- Training data depth as THE binding constraint (identified by exploit_1 gen004)
- Beam width as the dominant parameter (identified by research_1 gen004, pattern_009)
- Non-backtracking beam search as an option (identified by research_1 gen004, idea_015)
- CayleyPy's MlpModel using one-hot (identified by research_1 gen004, idea_014)
- idea_013's actual test result (44111, marginal)

**Incorrect in SoA:**
- "BFS data strictly superior to random walks" — contradicted by exploit_1's empirical test
- "The combined recipe is the #1 priority" — tested and found marginal. New #1: deep training data + large beam width

## 5. What Would I Do Differently With More or Different Context

1. **Read the actual manifest.yaml for gen004** to verify the architect's planned group structure vs what actually ran. This would tell me whether the 60% failure rate is a planning problem or an execution problem.

2. **Compare per-bucket scores between gen003 best and gen004 best** to understand WHERE the 17-move regression came from. If it's concentrated in hard puzzles, the predictor is actively harmful there. If it's spread across buckets, it's noise.

3. **Read the CayleyPy RL paper's beam width scaling data** myself to verify research_1's claims about log-linear quality scaling. This claim drives my REC-3 (mandate beam_width ≥ 8192) and should be first-party verified.

4. **Profile GPU memory at beam_width=65536** to validate REC-3's feasibility before recommending it. research_1 calculated ~300 MB per batch, but this needs empirical confirmation.

## 6. Specific Experiments to Run

See `experiment_suggestions.md` — 7 experiments ranked in 3 priority tiers.

The most critical: **EXP-1** (path-intermediate data + MlpModel + beam_width=65536) is the gatekeeper experiment. Its result determines whether the beam search paradigm can work for Megaminx or whether the pipeline must pivot entirely.

## 7. What Surprised Me

1. **The correct architecture (embedding MLP) scored WORSE than the wrong architecture (raw integer).** 44111 (embedding) < 44094 (raw integer). This contradicts the 2-generation assumption that fixing the architecture would unlock predictor value. The training data depth problem dominates the architecture problem by a wide margin.

2. **idea_010 (BFS data superiority) was completely wrong for the predictor use case.** It was created from theoretical reasoning ("exact labels > noisy labels") and treated as established knowledge, but never tested. When tested, it produced a predictor that predicts every state as depth ~4. This is the clearest example of theoretical reasoning failing without empirical validation.

3. **The experimentator has a 0% success rate over 3 generations.** I expected improvement after the architect reduced scope and added milestone instructions. Instead, another complete failure. The role itself is the problem, not the brief.

4. **The pipeline's two biggest levers (beam width, training data depth) have been untested for 4 generations** while agents debated architecture (raw integer vs embedding vs one-hot). Architecture matters much less than these two factors. The debate was a distraction from the real problem.

5. **explore_1 ran for only 221s (vs gen003's 6301s)** — the reduced timeout worked. Still zero output, but 28× less wasted time. The timeout reduction (architect REC-4 from gen003) was the one recommendation that actually worked.

## 8. Helper Tools Feedback

I did not use any helpers from `problem/helpers/` during this analysis session. My work was entirely reading files and writing analysis.

**Observations from agent reports about helpers:**
- `helpers/core.py` is functional but `cayleypy_beam_solver` only supports unguided beam search (useless for the current strategy)
- `helpers/trained_predictor_beam_search.py` is actively harmful (wrong architecture, misleads agents)
- Multiple agents requested a `full_pipeline_solver()` helper that encapsulates train → beam search → fallback
- The `extract_path_intermediates()` helper would eliminate ~50 lines of boilerplate per agent for idea_016

## 9. Time Budget

Sufficient for the analysis. Reading all reports, knowledge files, and data was the bulk of the work. Writing the three output files and this debrief took the remainder.

With more time, I would have:
1. Read the gen003 score file to compare per-bucket breakdowns with gen004
2. Read the actual manifest.yaml for gen004 to verify the architect's plan
3. Read the exploit_1 sol01.py code to verify its described pipeline
4. Checked whether idea_010's file has been updated with the evaluator's correction or still contains the misleading "strictly superior" claim
5. Verified the gen004 score progression file hasn't been updated to include gen004's result (it currently stops at gen003)
