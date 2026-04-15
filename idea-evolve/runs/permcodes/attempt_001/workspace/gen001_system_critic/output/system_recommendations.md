# System Recommendations — Generation 1

## Priority 1: Diagnose and Fix Agent Launch Failures (CRITICAL)

### R1.1: Add Agent Launch Diagnostic Logging
**What to change:** `orchestrator_harness.py` — add logging of harness stdout/stderr at launch time, even on success. Capture the first 1KB of output to confirm the harness is producing expected startup messages.

**Why:** We have no record of why agents failed. The empty output directories could mean:
- Agents never launched
- Agents launched but crashed immediately
- Agents ran but outputs were never written

**Expected impact:** Would reveal the root cause. If opencode produces "No API key found" we know the credentials aren't being passed. If claude-code produces a session URL, we know it launched.

### R1.2: Add Pre-Flight Agent Environment Validation
**What to change:** Before launching any agent, write a 10-second validation job that:
1. Launches the agent harness with `--version` or equivalent
2. Checks that the environment has `MODELGATE_API_KEY` if using opencode
3. Verifies Python can import `helpers.core` from the problem directory

**Why:** The CLAUDE.md explicitly warns that opencode needs `.env` loaded. If the orchestrator is not passing env vars to agent subprocesses, agents will fail silently.

**Expected impact:** Prevent entire generations from being wasted due to environment misconfiguration.

### R1.3: Require Agent Checkpoint Writes
**What to change:** Agent prompt templates — add a directive that agents MUST write checkpoint files every 5 minutes during long sessions. Format: `output/checkpoint_N.md` with current progress.

**Why:** If an agent times out after 20 minutes without writing anything, all work is lost. Checkpoints would preserve partial progress.

**Expected impact:** Even on timeout, we'd have partial outputs. The evaluator could incorporate incomplete experiment results.

---

## Priority 2: Validate Helper Infrastructure (CRITICAL)

### R2.1: Pre-Run Helper Validation
**What to change:** `_preflight_check()` in orchestrator.py — add a step that imports and smoke-tests all helpers in `problem/helpers/`. For this problem specifically:
1. `from helpers.agl18 import max_clique_code; code = max_clique_code(); assert len(code) >= 616`
2. `from helpers.compat import fast_compatible_mask, build_all_perms, build_bucket_ids; ...`

**Why:** The entire gen1 strategy was built on `helpers.agl18.max_clique_code()` producing 616+ codewords. This was never confirmed. If the helper has a bug, agents using it would fail.

**Expected impact:** Eliminates a whole class of agent failures due to broken helpers.

### R2.2: Create Simple Helper CLI
**What to change:** Add a `helpers/cli.py` that provides direct command-line access to helper functions:
```bash
python3 -c "from helpers.cli import run_agl18; print(run_agl18())"
```

**Why:** The evaluator recommended this. It would let any agent (or the evaluator itself) quickly test helper outputs without writing a full solution file.

**Expected impact:** Faster debugging, ability for evaluator to confirm helper correctness.

---

## Priority 3: Fix Architect Quality Issues (MODERATE)

### R3.1: Architect Math Verification Step
**What to change:** Architect prompt — add a step after writing the manifest where the architect verifies key numerical claims by cross-checking with known bounds. Specifically: verify that 11 × orbit_size = 616, and if orbit_size is claimed to be 168, flag this as inconsistent with the known upper bound of 926.

**Why:** The architect wrote "11 × 168 = 1848" which exceeds the known upper bound of 926. A simple sanity check would have caught this.

**Expected impact:** Prevents incorrect mathematical claims from propagating to agent briefs.

### R3.2: Architect Should Test Helpers Before Assigning
**What to change:** Architect prompt — add guidance that before assigning agents to use a helper function, the architect should verify the helper exists and is documented correctly. If the brief references `helpers.compat.fast_compatible_mask`, the architect should confirm this function exists in the helpers directory.

**Why:** If briefs reference nonexistent helpers, agents would fail at import time.

**Expected impact:** Briefs become more reliable.

---

## Priority 4: Improve Phase/Geneation Tracking (MODERATE)

### R4.1: Fix gen_progress.json Status Tracking
**What to change:** `run_single_agent()` in orchestrator.py — update gen_progress.json status at each phase transition (launch → running → wrapping_up → done/failed).

**Why:** Currently gen_progress.json shows all agents as "pending" despite the orchestrator being in the system_critic phase. The status tracking is incomplete.

**Expected impact:** Accurate progress tracking for dashboard and crash recovery.

### R4.2: Add Agent Error Log Capture
**What to change:** `run_single_agent()` — capture stderr from agent subprocesses and write to `reports/genNNN/{agent}_error.log` on failure.

**Why:** When agents fail, we need to know why. Currently errors go to /dev/null.

**Expected impact:** Debugging information for agent failures.

---

## Priority 5: Streamline Briefs (MINOR)

### R5.1: Use Relative Paths with Run Root
**What to change:** Architect prompt — instruct to use paths relative to `briefs/genNNN/` or use a `$RUN_ROOT` placeholder, not absolute paths. The orchestrator's `_absolutize_brief_paths()` is a workaround for a preventable problem.

**Why:** Absolute paths are fragile across different run directories.

**Expected impact:** More portable briefs.

### R5.2: Abstract Evaluate.py Path
**What to change:** Brief template — show `python3 evaluate.py output/sol01.py` with a note that evaluate.py is found via `$PATH` or that the orchestrator sets up the path. Remove the full absolute path from individual briefs.

**Why:** Repetition of the full path in every brief is error-prone and makes briefs harder to read.

**Expected impact:** Cleaner briefs, fewer path errors.

---

## Priority 6: Knowledge Base Quality (LOW)

### R6.1: Confidence Score Calibration
**What to change:** Evaluator prompt — when creating ideas from architect reports (not agent outputs), set confidence to a lower value (e.g., 0.3-0.5) to reflect that they are unvalidated theoretical claims.

**Why:** idea_002 (AGL construction) was assigned confidence 0.8 despite zero empirical confirmation. This miscalibration could cause future agents to over-trust unvalidated ideas.

**Expected impact:** Better-calibrated confidence scores.

---

## Summary: Expected Impact by Recommendation

| Priority | Recommendation | Expected Impact |
|----------|----------------|-----------------|
| CRITICAL | Add agent launch diagnostics | Know why agents fail |
| CRITICAL | Pre-flight env validation | Prevent wasted generations |
| CRITICAL | Agent checkpoint writes | Preserve partial progress |
| CRITICAL | Validate helpers before use | Eliminate broken-helper failures |
| MODERATE | Architect math verification | Prevent bad numerical claims |
| MODERATE | Fix gen_progress tracking | Accurate status for dashboard |
| MODERATE | Capture agent error logs | Debug failures |
| MINOR | Use relative paths | Portable briefs |
| MINOR | Abstract evaluate.py path | Cleaner briefs |
| LOW | Confidence calibration | Better-informed agents |

---

## Immediate Action for Generation 2

Before launching gen 2:
1. **Verify agent harness works** — run a simple "hello world" agent to confirm the harness is functional
2. **Confirm helper correctness** — run `python3 -c "from helpers.agl18 import max_clique_code; print(len(max_clique_code()))"` to confirm it returns 616+
3. **Check .env is loaded** in agent subprocess environment

If gen 2 agents also fail, we should consider:
- Reducing agent complexity (single solution per agent)
- Adding explicit "verify you can read/write files" steps in agent prompts
- Running a minimal test agent first to validate the pipeline
