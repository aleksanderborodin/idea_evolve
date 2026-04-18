# System Critic Debrief — Generation 2

## 1. What did you try?

I performed a complete pipeline critique analyzing all available reports from gen 002:
- Read all 8 agent debrief reports (architect, evaluator, explore_1, explore_2, exploit_1, experimentator_1, research_1, evaluator_debrief)
- Read all population observations (explore_1, explore_2, exploit_1)
- Read state_of_affairs (gen 001), coverage_matrix, agent_gaps/gen002.md, feedback files
- Read generation snapshots (gen 001, gen 002) and consistency review (gen 001)
- Compared gen 002 outcomes against gen 001 to identify trends

**Outputs produced:**
1. `system_analysis.md` — 12 findings across 5 categories (pipeline problems, missing capabilities, prompt problems, resource issues, knowledge quality, experiment gaps)
2. `system_recommendations.md` — 8 concrete recommendations with implementation guidance
3. `experiment_suggestions.md` — 4 experiments (1 critical, 1 high, 2 medium) + status of previously suggested experiments
4. This debrief report

---

## 2. What information did you lack?

1. **The experimentator_1 directory had no observations.md or findings.md.** The experimentator produced literally nothing — no files, no output. I could not analyze what it tried or why it failed. I had to infer from the debrief report that it was told to stop before producing output. I wish there had been an in-process observations file from the experimentator so I could understand what it attempted before being told to stop.

2. **No full evaluation results for gen 002.** All scores were proxy (1/10) evaluation. The evaluator noted that identities might perform differently on full 1001-puzzle set. I could not assess generalization.

3. **No proc_log files available for reading.** The proc_log system is designed to write markdown timelines for non-trivial process outcomes, but I had no proc_log files to read from any agent. I don't know if they were written or where they would be.

4. **The `research_1/observations.md` did not exist.** research_1 produced findings.md but no observations.md in the population directory. The findings.md was detailed enough (143 lines) but I couldn't compare observations vs findings for research_1.

---

## 3. What given facts might be wrong or outdated?

1. **The State of Affairs (gen 001) was stale for gen 002.** It listed idea_006 (hamming) as untested with confidence 0.8. research_1 debunked it in gen 002 — zero advantage. But gen 002 agents read the stale state before the update, causing exploit_1 and explore_1 to waste time on hamming.

2. **The architect report confirmed ongoing path confusion.** It noted "The architect context again referenced run-local problem files under `runs/megaminx/attempt_001/problem/`" — these files do not exist. This confusion has persisted since gen 001.

3. **helpers/README.md PROXY_SIZE=100 is documented as wrong but never fixed.** This was flagged in REC-4 from gen 001 and REC-3 from gen 001 consistency review. It persists.

4. **The claim that hamming predictor was "untested" became false mid-generation.** Once research_1 ran and debunked hamming, the State of Affairs should have been updated mid-generation. The knowledge update lag is a structural issue — agents plan based on stale information.

---

## 4. Was the State of Affairs accurate?

**Mostly accurate but with significant blind spots:**

The gen 001 state_of_affairs correctly:
- Identified compression baseline at 46312 ✓
- Identified predictor-guided beam as primary path ✓
- Noted hamming predictor as zero-cost untested experiment ✓

But it missed:
- idea_005 (identity discovery) was already established by gen 002 explore_2 — should have been marked active, not unexplored
- idea_006 (hamming) is now definitively debunked — should be marked debunked
- idea_007 (corner PDB) was invalidated — all generators are 5-cycles
- research_1 confirmed ML pipeline but no solution actually ran predictor-guided beam

The coverage matrix's priority order (idea_006 first, then idea_003) should have been reversed — idea_008 (trained MLP) is the only viable predictor option now that hamming is definitively debunked.

The state_of_affairs also did not capture the most important finding of gen 002: **the compression ceiling was broken to 44114 via empirical algebraic identities**. This was genuinely new and the gen 001 state couldn't have predicted it.

---

## 5. What would you do differently with more or different context?

1. **I would have read the consistency_review gen 002 output if it existed.** The gen 001 consistency review was available and useful. A gen 002 consistency review would have caught the stale state_of_affairs issue before my analysis. I should check if one was written and wasn't available.

2. **I would have interviewed the experimentator_1 agent directly.** Its directory was empty and its report was one sentence. I don't know if it attempted anything before being told to stop. A more thorough debrief from that agent would tell me whether the failure was prompt-based, role-based, or execution-based.

3. **I would have traced the exact state encoding error exploit_1 hit.** `rshift_cuda on float` — this is a concrete technical error that blocks the primary path. I wish I had the full traceback or a proc_log from exploit_1 so I could diagnose whether it's a device placement issue, a state representation issue, or a API misuse issue.

4. **I would have read the prompt.md that was given to the experimentator_1 agent.** The workspace had a `prompt.md` file that I didn't read before writing my analysis. That prompt might explain why the experimentator stopped before producing output.

---

## 6. Specific experiments to run?

### EXP-A: Trained MLP Predictor Baseline (CRITICAL — run first in gen 3)
```
1. Generate 100k random walks from solved state, depths 10-50
2. Train 3-layer MLP (120→256→128→1) for 10 epochs, MSE loss
3. Compare beam_search with trained predictor vs unguided at beam_width=4096
4. Record: per-puzzle path length, solve rate, wall-clock time
```
**Expected time:** 10-15 minutes on GPU.
**This is the single most important experiment for the pipeline.**

### EXP-B: Compression + Beam Search Combination
```
1. Apply 336 empirical identity rules (from explore_2/sol01) to get compression_ratio=0.8723
2. Run beam_search from compressed starting points, NOT raw sample_submission
3. Compare: pure compression (44114) vs compression-then-beam
```
**Expected time:** 15-20 minutes.

### EXP-C: Beam Width Scaling with Trained Predictor
```
1. Same pipeline as EXP-A, varying beam_width: [1024, 2048, 4096, 8192]
2. Find optimal beam width for each depth bucket with trained predictor
```

### EXP-D: Training Depth Generalization
```
1. Train predictors on single-depth distributions: depth = [10, 20, 30, 50]
2. Evaluate each on puzzles across ALL depth ranges
3. Measure: does depth-matched training generalize?
```

---

## 7. What surprised you?

1. **The experimentator_1 produced literally nothing.** I expected at least some failed experiments, even if they were unsuccessful. The fact that an entire agent slot produced zero output in a generation is a significant pipeline failure.

2. **The compression breakthrough was unexpected.** The gen 001 state_of_affairs predicted "compression ceiling likely ~44100" — it turned out to be right but for the wrong reasons. The actual breakthrough (empirical algebraic identities) was not predicted by any agent in gen 001. It came from explore_2 doing something completely different from what the state_of_affairs suggested.

3. **Hamming was exactly as bad as unguided at EVERY beam width.** research_1 showed zero difference at 2048, 8192, 32768, and 65536. I expected at least marginal improvement. The fact that they're identical even at very large widths is a strong structural finding about the Megaminx Cayley graph's geometry.

4. **beam_mode='advanced' returns path=None silently.** This is a significant API bug that was found independently by research_1 and exploited_1's experience. The fact that it silently returns nothing (no error, no warning) means agents using 'advanced' mode for speed get no output at all.

5. **The architect flagged documentation inconsistencies that were already flagged in gen 001.** The "CPU-only" vs "GPU available" contradiction in description.md, the PROXY_SIZE=100 typo in helpers/README.md, the non-existent `runs/.../problem/` paths — these were all flagged in gen 001 and persist unchanged into gen 002. This suggests the recommendation filing system isn't producing fixes.

---

## 8. Helper tools feedback.

I did not directly use helpers from `problem/helpers/` as part of my analysis. I read the agent reports that described helper usage.

From the reports:

**What worked:**
- `load_test(proxy=True)` — works correctly (used by all agents)
- `load_sample_submission_paths()` — works correctly
- `apply_path()` — works correctly (but raises ValueError on unknown moves)
- `is_solved()`, `solved_state()`, `depth_bucket()`, `GENERATOR_NAMES` — all correct

**Bugs found:**
- `apply_path` raises `ValueError` on unknown moves. String replacement in sol04 created empty move names which caused `unknown move '-'` errors. The error message was clear but the root cause was not obvious.
- **String replacement danger is not documented.** The danger of using `.replace()` on dot-joined paths is not in any docstring.

**Missing helpers (confirmed by exploit_1 and research_1):**
- No `trained_predictor_beam_search()` wrapper
- No helper exposes `graph.random_walks()`, `Predictor(graph, model)`, or `beam_search(predictor=...)`
- agents must import cayleypy directly and rediscover the API each time

**What I wished existed:** A single function `run_trained_predictor_experiment(state, ...)` that handles device placement, state encoding, and beam search under one documented API. This would unblock the primary path.

---

## 9. Time budget.

**I had sufficient time.** My analysis involved:
- Reading ~15 files (8 reports + 6 observations/coverage/feedback + 2 histories)
- Cross-referencing between gen 001 and gen 002
- Writing 4 output files (~400 lines total)

This took approximately 45 minutes of focused analysis. I was able to complete all outputs before the session ended.

**If I had more time, I would have:**

1. **Traced the exploit_1 state encoding error more precisely.** `rshift_cuda on float` — I could have searched the codebase for this error string to understand the exact failure mode. This would let me write a more precise recommendation for the helper fix.

2. **Read the workspace prompt.md given to experimentator_1.** The workspace had a `prompt.md` file I didn't read before finishing my analysis. Understanding why the experimentator stopped would let me write a better recommendation for fixing the experimentator role.

3. **Compared the gen 002 evaluator report against the consistency review template.** The consistency reviewer had gen 001 audit findings; a gen 002 audit would have caught the stale state_of_affairs issue (listing hamming as untested when it was already debunked). I didn't check if the gen 002 consistency review was written and available.

4. **Written a specific implementation plan for the `trained_predictor_beam_search` helper.** The recommendation says "add a helper" but doesn't give the exact function signature that would work. With more time, I would have read the cayleypy source to determine the correct device-placement handling and written the exact code.

---

## Key Takeaway

**The single most important pipeline change for gen 3:** Force the trained-predictor experiment to run. idea_008 has 0 central uses after 2 generations. The primary path to the target cannot be evaluated if it is never executed. The pipeline must ensure that at least one agent successfully runs `graph.random_walks()` → train MLP → `beam_search(predictor=...)` end-to-end in gen 3.