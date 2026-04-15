# System Analysis — Generation 1

## Pipeline Status: CRITICAL FAILURE

**Severity: CRITICAL**

This generation produced zero usable outputs from all solution agents. The evolutionary pipeline failed completely — no solutions, no research findings, no agent reports. The orchestrator advanced to the system_critic phase with only the architect's report and the evaluator's bootstrap knowledge available.

---

## 1. Pipeline Problems

### 1.1 Complete Agent Failure (CRITICAL)
**Evidence:** All four agent workspaces (`gen001_full_1`, `gen001_explore_1`, `gen001_explore_2`, `gen001_research_1`) have empty `output/` directories. The `gen_progress.json` shows all agents in "pending" status with no completion markers.

**Root Cause:** Unknown. Possible causes:
- Agent launch failures (binary not found, credential issues)
- Workspace path issues (agents may not have been able to write to output/)
- Timeout before first write (unlikely given 600-1200s timeouts)
- opencode harness failures (if using opencode)

**Impact:** No empirical data from this generation. The gap from 262 (greedy baseline) to 616 (AGL theoretical bound) remains unbridged.

### 1.2 Missing Agent Debrief Reports (CRITICAL)
**Evidence:** `reports/gen001/` contains only `architect.md`. No `explore_1.md`, `explore_2.md`, `full_1.md`, or `evaluator.md` reports exist.

**Impact:** The system cannot learn from what agents attempted. We don't know if agents:
- Crashed immediately on startup
- Failed to import helpers
- Ran but found no improvements
- Produced outputs that were never moved

### 1.3 Evaluator Resorted to Reconstruction (MODERATE)
**Evidence:** The evaluator, finding no agent outputs, reconstructed 7 ideas and 2 clusters from the architect's report alone. This is bootstrapping, not evaluation.

**Impact:** Knowledge created is theoretical/unvalidated. No empirical confirmation that AGL(1,8) produces 616, that ILS parameters are appropriate, or that alternative groups are viable.

### 1.4 Architect Math Error (MODERATE)
**Evidence:** `architect.md` line 39 states "11 orbits × 168 = 1848" but the correct calculation is 11 × 56 = 616 (as confirmed by the evaluator and Smith-Montemanni literature).

**Impact:** The architect confused AGL(1,8) orbit size (56) with AΓL(1,8) orbit size (168). This error propagates to any agent that relied on the architect's orbit calculations for designing alternative group approaches.

### 1.5 Gen Progress Tracking Shows Pending Agents (MODERATE)
**Evidence:** `briefs/gen001/gen_progress.json` shows all agents still in "pending" status despite the orchestrator believing it reached the "system_critic" phase.

**Impact:** The orchestrator may be incorrectly advancing phases. If agents are still running, they could still produce outputs. If they truly failed, the gen_progress.json should reflect that.

---

## 2. Missing Capabilities

### 2.1 No Pipeline Self-Diagnostics
The pipeline has no mechanism to detect WHY agents fail. There is no:
- Startup verification that agent binaries/harnesses are functional
- Heartbeat monitoring during agent execution
- Diagnostic output capture on agent failure
- Automatic retry logic for failed agent launches

### 2.2 No Intermediate Checkpoint System
Agents are expected to produce final outputs only at session end. If a session times out, all work is lost. There is no checkpoint system for agents to write partial progress.

### 2.3 No Helper Verification Before Agent Assignment
The architect assigned agents to use `helpers.agl18.max_clique_code()` and `helpers.compat.fast_compatible_mask`, but no pre-flight check confirmed these helpers are importable and functional. If these helpers had bugs, agents would fail silently.

---

## 3. Prompt Problems

### 3.1 Brief Paths Are Absolute (MINOR)
The architect wrote briefs with absolute paths like:
```
/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_001/population/gen000/baseline/sol01.py
```

This is fragile — if the run directory changes, these paths break. The orchestrator has `_absolutize_brief_paths()` which should fix this, but it's a post-processing step that shouldn't be necessary.

### 3.2 Evaluate.py Path Repetition (MINOR)
Every brief repeats the full evaluate.py path:
```bash
python3 /home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/evaluate.py output/sol01.py
```

This is error-prone and could be abstracted. The brief template shows the full path but the orchestrator sets `IDEA_EVOLVE_RUN_ROOT` — agents should use a相对 path or the environment variable.

### 3.3 Agent Prompt vs. Brief Disconnect
The agent `prompt.md` files exist in workspaces but briefs are also provided. It's unclear which takes precedence. The brief (`brief.md`) is supposed to be the operative directive, but the prompt includes global context that may conflict.

---

## 4. Resource Issues

### 4.1 Baseline Evaluation Time Not Accounted For (MODERATE)
The architect noted that the greedy baseline takes 22s to evaluate. ILS agents were given 1200s timeouts, which should allow ~50 evaluations. However, if agents naively call evaluate.py inside their search loops, they could exhaust time on evaluation alone.

The brief tells agents to "track scores internally and only call evaluate.py at the end," but this guidance may not be prominent enough.

### 4.2 All Agents Launched in Single Parallel Group (LOW)
The manifest shows all 4 agents in one parallel group. This is correct for parallelism but means if all fail, nothing is learned. No fallback sequence exists.

---

## 5. Knowledge Quality Issues

### 5.1 Unvalidated Ideas Dominate Knowledge Base (MODERATE)
The evaluator created 7 ideas, but all are "active" lifecycle with `last_confirmed_gen: null`. Only idea_001 (greedy baseline, 262) is confirmed. The remaining 6 ideas are theoretical.

**Confidence scores are miscalibrated:** idea_002 (AGL construction) has confidence 0.8 despite zero empirical confirmation this generation.

### 5.2 Pattern "AGL(1,8) Orbit Size is 56, Not 168" Documents an Error (LOW)
The evaluator created pattern_002 documenting the architect's math error. This is good knowledge tracking, but the error shouldn't have occurred.

### 5.3 Coverage Matrix Is Empty
The coverage matrix shows 0 trials for all strategic approaches except greedy (1 trial). This is expected given agent failure, but confirms no empirical progress.

---

## 6. Experiment Gaps

### 6.1 AGL(1,8) Helper Never Validated
The most critical unverified assumption is that `helpers.agl18.max_clique_code()` actually produces 616+ codewords. This should be the first experiment.

### 6.2 ILS Parameter Space Completely Unexplored
Even if agents had run, the ILS destruction sizes {30, 100} and SA parameters were prescribed by the architect without any empirical basis.

### 6.3 Alternative Group Space Unsearched
AΓL(1,8), PGL(2,7), PSL(2,7), and coset constructions were all assigned but never attempted.

---

## Summary of Findings by Severity

| Severity | Finding | Evidence |
|----------|---------|----------|
| CRITICAL | All agents produced zero outputs | Empty output/ dirs, gen_progress.json shows "pending" |
| CRITICAL | No debrief reports exist | reports/gen001/ has only architect.md |
| CRITICAL | Cannot diagnose root cause | No error logs, no agent stderr captured |
| MODERATE | Architect math error: 11×168=1848 | architect.md line 39, evaluator correction |
| MODERATE | Ideas are theoretical, not empirical | All ideas have last_confirmed_gen: null |
| MODERATE | Evaluator had to bootstrap knowledge | 7 ideas created from architect report, not agent outputs |
| MODERATE | Baseline eval time (22s) may affect ILS timing | architect.md noted, brief mentioned but may not be heeded |
| MINOR | Brief paths are absolute | Architect wrote full paths instead of relative |
| MINOR | Evaluate.py path repeated in every brief | Could be abstracted via env var |
| LOW | Pattern documents an error rather than preventing it | pattern_002.md |

---

## Root Cause Hypothesis

The most likely explanation for the complete agent failure is that the **opencode harness** (if being used) failed to launch properly. The CLAUDE.md notes that "Without `.env` loaded, opencode exits silently with empty stdout."

If the orchestrator launched agents via opencode without the `.env` being loaded in the agent subprocess environment, all opencode sessions would fail immediately.

Alternative hypothesis: the **agent prompt template** or **brief template** references paths or resources that don't exist in the workspace context.

**Recommended diagnostic:** Check if opencode binary is on PATH in the agent execution environment, and verify that `MODELGATE_API_KEY` is accessible to agent subprocesses.
