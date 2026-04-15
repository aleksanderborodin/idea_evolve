# System Critic Debrief — Generation 1

## What Did You Try?

I analyzed the Generation 1 pipeline for the permcodes problem (M(8,5) permutation codes). My approach was to:

1. **Read all available reports and artifacts** — architect.md, evaluator outputs (evaluator_report.md, agent_gaps.md, coverage_matrix.md, state_of_affairs.md), ideas, patterns, clusters created by the evaluator.

2. **Attempted to find agent debrief reports** — These don't exist. Only the architect's report is in `reports/gen001/`. The agent workspaces have empty `output/` directories.

3. **Investigated gen_progress.json** — All 4 agents (full_1, explore_1, explore_2, research_1) show status "pending", meaning they were started but never completed.

4. **Identified the core problem** — Complete pipeline failure. All solution agents produced zero outputs. The orchestrator advanced to system_critic phase with no agent results to analyze.

## What Information Did You Lack?

1. **Why agents failed** — No error logs, no stderr captures, no agent reports. The empty output directories could mean:
   - Agents never launched (harness failure)
   - Agents crashed at startup (import error, credential error)
   - Agents ran but timed out before writing anything
   - Agents wrote outputs that were never moved to final location

2. **Agent prompt outputs** — The `workspace/gen001_*/prompt.md` files exist (these are the global prompts sent to agents), but I don't know what the agents actually did with them.

3. **Orchestrator logs** — No log file exists documenting what happened during agent launch/execution. `history/run_state.json` shows the orchestrator state but not agent-level events.

4. **The opencode harness status** — CLAUDE.md warns that opencode needs `.env` loaded or it exits silently. I don't know if the orchestrator passed env vars to agent subprocesses.

## What Given Facts Might Be Wrong or Outdated?

1. **AGL(1,8) orbit size** — The architect's report claims "11 orbits × 168 = 1848" but the correct orbit size is 56 (11 × 56 = 616). The evaluator caught this and created pattern_002 documenting the error. The architect appears to have confused AGL(1,8) with AΓL(1,8).

2. **fast_compatible_mask 23x speedup claim** — The architect cited this but no agent validated it. The evaluator noted it as "unverified."

3. **Target score of 624** — metrics.yaml shows target_score: 624 (8 above the 616 lower bound). The evaluator noted this is "an arbitrary round number." The actual goal should be to beat 616, not specifically 624.

4. **Agent timeouts** — Briefs specify 600-1200s timeouts, but without knowing when agents actually started and whether they ran to completion, these numbers are meaningless.

## Was the State of Affairs Accurate?

The state_of_affairs.md in the evaluator's output accurately reflects the situation:
- "Complete pipeline failure" — correct
- "best_score: 262" — correct (gen000 baseline)
- "All solution agents failed to submit outputs" — correct
- "The knowledge base now contains 7 ideas...theoretically grounded but lack empirical validation" — correct assessment

The bootstrap state_of_affairs.md (gen 0) was minimal and appropriate for a cold start.

## What Would You Do Differently with More Context?

1. **With agent error logs** — I would diagnose whether it was an import failure, credential issue, or timeout problem. Each root cause has different fixes.

2. **With harness startup output** — If opencode produced "No API key found" or claude-code produced a URL, I'd know exactly what failed.

3. **With timing data for agents** — Currently only architect timing (279.6s) is recorded. If agent timing was recorded, I'd know if they ran for 1 second (crashed) or 20 minutes (timed out mid-work).

4. **With workspace cleanup logs** — I can't tell if outputs were written then deleted, or never written.

## Specific Experiments to Run

### P0: Diagnostic Experiments (before any solution agents)

**EXP-DIAG-Harness:**
```
Launch a minimal test agent with 60s timeout:
- Directives: write "hello" to output/test.txt and output/report.md
- Expected: both files exist
- If fails: pipeline is broken at harness level
```

**EXP-DIAG-Helper:**
```
python3 -c "from helpers.agl18 import max_clique_code; print(len(max_clique_code()))"
Expected: 616+
If fails: helper is broken
```

**EXP-DIAG-Env:**
```
Check that MODELGATE_API_KEY is accessible to subprocess
If not: orchestrator needs to pass env vars
```

### P1: Solution Experiments (if diagnostics pass)

**AGL(1,8) baseline (full_1):** Confirms 616 works.

**ILS with k=30 (explore_1):** Tests if 616 is tight.

**ILS with k=100 (explore_1 variant):** Tests larger destruction.

**AΓL(1,8) alternative group (explore_2):** Tests if different orbit structure yields better codes.

## What Surprised You?

1. **Complete agent failure with no diagnostic trace** — Usually when something fails, you get an error message. Here, we have zero indication of what went wrong. The empty output directories are the only evidence.

2. **Evaluator had to reconstruct all knowledge from scratch** — The evaluator essentially said "I had no agent outputs, so I read the architect's report and bootstrapped 7 ideas." This means the knowledge base for gen 2 will be entirely theoretical.

3. **gen_progress.json showed "pending" for all agents despite orchestrator being in system_critic phase** — This suggests the orchestrator advanced phases without agents completing. Either the orchestrator is misreporting phase, or gen_progress.json wasn't updated when agents failed.

4. **The architect made a math error (11×168=1848) that the evaluator caught** — The evaluator created a pattern documenting this error. It's good that the evaluator catches these things, but the architect should have caught it.

## Helper Tools Feedback

I read the helper documentation during my analysis:
- `helpers/core.py`: hamming_distance, check_code, min_distance, pairwise_distances, compatible_permutations — well-documented with docstrings
- `helpers/agl18.py`: Implements AGL(1,8) orbit clique search — exists and appears complete, but **never validated by any agent**
- `helpers/compat.py`: fast_compatible_mask — claims 23x speedup but **never validated**

**Bugs found:** None in the helpers themselves. The issue is that no agent ever used them.

**Helper I wish existed:** A direct CLI for helpers, as the evaluator recommended:
```bash
python3 helpers/cli.py agl18  # prints the AGL(1,8) code
python3 helpers/cli.py compat --code output/sol01.py  # runs compatibility check
```
This would let the evaluator or a diagnostic agent verify helpers without writing full solution files.

## Time Budget

I had sufficient time for my analysis given the available data. The limitation was data availability (no agent outputs), not time.

I read ~15 files covering:
- Architect report
- Evaluator outputs (report, gaps, coverage, state of affairs, ideas, patterns, clusters)
- Briefs for all 4 agents
- gen_progress.json and run_state.json
- Agent workspace structures

If I had more time, I would:
1. **Run the diagnostic experiments myself** — I could have run `python3 -c "from helpers.agl18 import max_clique_code; print(len(max_clique_code()))"` to confirm the helper works, but that's outside my role as system critic (I analyze the system, I don't run solutions).

2. **Check the orchestrator source code** — I could have read `orchestrator.py` to understand how agents are launched and whether env vars are passed, but I focused on observable artifacts.

3. **Investigated the opencode harness** — The CLAUDE.md mentions opencode needs `.env` loaded, but I couldn't verify if this was the actual cause of failure without running diagnostic commands.

## Recommendations Summary

**Immediate (before gen 2):**
1. Run harness smoke test to confirm agents can launch
2. Validate helpers produce expected outputs
3. Check MODELGATE_API_KEY is accessible to agent subprocesses

**Short-term fixes:**
4. Add agent error log capture
5. Add checkpoint writing to agent workflow
6. Fix gen_progress.json status tracking

**Longer-term improvements:**
7. Architect math verification step
8. Pre-flight helper validation in orchestrator
9. Confidence calibration for ideas from reports vs. empirical results
