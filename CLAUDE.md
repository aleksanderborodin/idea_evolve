# Alpha Evolve

Evolutionary code optimization through collaborative AI agent work sessions.
Based on the design spec in `ALPHA_EVOLVE_COMPLETE_V4.md`.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

All commands below assume the venv is active. Dependencies: `requirements.txt` at project root.

## Running

```bash
source venv/bin/activate
cd alpha-evolve
python3 orchestrator.py .            # full run
python3 orchestrator.py . --single   # one generation only
python3 orchestrator.py . --start-gen 5  # resume from gen 5
python3 orchestrator.py . --dry-run  # show plan without launching agents
```

Current problem: **First Autocorrelation Inequality** (functional optimization, target C ≤ 1.5053, lower is better).
Baseline score: **1.5185** (`problem/initial_programs/optimize.py`).
Problem files at `alpha-evolve/problem/`. Fitness direction read from `problem/metrics.yaml`.

## Dashboard

Web UI for tracking evolution runs, browsing solutions/knowledge, and visualizing the pipeline.

```bash
source venv/bin/activate
python dashboard/app.py              # http://localhost:5000
python dashboard/app.py --port 8080  # custom port
python dashboard/app.py --debug      # hot reload
```

Lives in `dashboard/`. Modular Flask app: `data/` (filesystem scanning), `routes/` (blueprints),
`templates/` (Jinja2 with tab partials), `static/` (CSS + JS). 6 tabs: Overview, Pipeline,
Architecture, Solutions, Knowledge, Reports. Auto-refreshes every 10s on Overview.
API endpoints at `/api/*` return JSON. See `dashboard/README.md` for full structure.

Dashboard reads fitness direction and decimals from `problem/metrics.yaml`. Scores display with
proper precision (4 decimals for this problem). Solutions table sorted best-first (respects
lower-is-better). Score source priority: `.score` sidecar → eval cache (by content hash) →
header comment. Progression chart shows baseline from initial programs and target line with
direction indicator ("↓ better" / "↑ better"). Agent column shows full identifier (e.g.,
`explore_1` not just `explore`).

## Architecture

The orchestrator is a stateless Python loop. All state lives in files. If it crashes, it resumes
from the last completed phase by inspecting which files exist (`phase_status()`).

**Generation loop (6 phases):**
1. **Architect** — reads system state, writes `manifest.yaml` + per-agent briefs to `briefs/genNNN/`
2. **Agent work sessions** — launched in parallel per `parallel_groups` in manifest. Each agent reads files, writes code, runs evaluate.py, iterates, writes debrief report. All in one session.
3. **Evaluator** — verifies scores, extracts knowledge (ideas/patterns/facts), updates clusters, generates coverage matrix
4. **System Critic** — reads agent reports, identifies pipeline problems, writes recommendations
5. **Consistency Review** — every 3rd gen or on strategic shift: audits knowledge base, rewrites State of Affairs
6. **Finalize** — update rankings, population summary, score progression, detect user interventions

**Agents are launched as:** `npx @anthropic-ai/claude-code --print --model <model> --max-turns <N>`
with `--allowedTools Read,Write,Bash,Glob,Grep`. Each agent gets a lean prompt with file paths to read
(not inline content), so prompts stay small regardless of knowledge base size.

## File Structure

```
alpha-evolve/
├── orchestrator.py          # Stateless loop (~2300 lines)
├── problem/                 # Problem definition (read-only for agents)
│   ├── description.md       # Problem description (problem-agnostic)
│   ├── constraints.md
│   ├── evaluate.py          # Problem-agnostic evaluator (loads validate.py, caches results)
│   ├── validate.py          # Problem-specific validation logic
│   ├── helper.py            # Problem-specific helper functions
│   └── metrics.yaml         # Fitness direction, bounds, sentinel values
├── agents/                  # Prompt templates (read-only, 10 files)
│   ├── architect.md, explore.md, exploit.md, genetic.md, full.md
│   ├── research.md, experimentator.md, evaluator.md
│   ├── system_critic.md, consistency_review.md
├── knowledge/               # Three-layer hierarchy (written by orchestrator only)
│   ├── state_of_affairs.md  # Layer 0
│   ├── clusters/            # Layer 1
│   ├── ideas/{active,established,disputed,debunked,archived}/  # Layer 2
│   ├── patterns/{active,confirmed}/  # Layer 2
│   ├── facts/               # Global (no lifecycle)
│   ├── research/            # Research findings per gen
│   └── experiments/         # Experimentator results per gen
├── population/              # All solutions
│   ├── best.py → symlink    # top/ → ranked symlinks
│   └── genNNN/{type}_{instance}/sol*.py
├── history/                 # generations/, score_progression.md, solution_idea_map.md, coverage_matrix.md
├── briefs/genNNN/           # manifest.yaml + per-agent briefs
├── reports/genNNN/          # Agent debrief reports
├── papers/                  # Academic paper library
│   ├── manage.py            # Pipeline CLI: add, list, status, summarize
│   ├── index.yaml           # Tracks all papers + pipeline status
│   ├── pdf/                 # Raw PDFs (NNN_name_author.pdf)
│   ├── md/                  # Auto-extracted text (NNN_name_author.md)
│   └── summaries/           # Agent-written structured summaries
├── prompts/                 # Prompt templates (loaded by orchestrator)
├── feedback/                # system_recommendations.md, experiment_suggestions/, experiment_requests/, agent_gaps/, consistency_reviews/
├── workspace/               # Ephemeral (cleaned after each agent)
└── user/                    # config.yaml, initial_ideas.md, initial_facts.md, interventions.md
```

## What Works

- **Three-phase timeout with session resume.** Work session runs with timeout T1 (default 900s)
  and gets a `--session-id`. If it times out without writing `report.md`, a **wrap-up message**
  is sent to the **same session** via `--resume` (same model, 900s) — the agent retains full
  memory of its work and is told to stop creating and evaluate/report. If the wrap-up also
  fails, a **debrief recovery** message resumes the same session (sonnet, 300s). Falls back to
  a new session only if no session_id exists. Work gets completed and knowledge is never lost.
- **Mandatory evaluate-immediately workflow.** Agent prompts (explore, exploit, full, genetic)
  and the orchestrator's global prompt context enforce: write one solution → run evaluate.py →
  update `# fitness:` header → then move on. Prevents agents from batch-writing unevaluated solutions.
- **Turn budgets from config.** `user/config.yaml` `max_turns:` section is authoritative.
  `DEFAULT_MAX_TURNS` in orchestrator.py is just a fallback if config is missing.
- **Timing tracking.** Every phase and agent records elapsed time to `history/timing.json`.
  The Architect sees recent timing data and can set per-agent `timeout` in `manifest.yaml`.
- **Evaluation caching.** `evaluate.py` caches results by file content hash in `history/eval_cache.json`.
  Thread-safe with `fcntl` file locking for parallel agent access.
- **Stateless crash recovery.** `phase_status()` reconstructs position from file existence.
- **Lean prompts.** File paths, not inline content. Stable prompt size across generations.
- **In-session debrief.** Agent writes `report.md` while it still remembers everything it tried.
- **Parallel groups.** `parallel_groups` in manifest → groups sequential, agents within group parallel.
- **Research/experiment routing.** Each agent type has its own output mover to the correct directory.
- **Initial knowledge bootstrap.** `initial_ideas.md`/`initial_facts.md` → proper YAML-frontmatter files before gen 1.
- **Gen-1 Evaluator bootstrap.** Special prompt instructions to write initial State of Affairs.
- **Manifest fallback + validation.** Invalid/missing YAML → default manifest generated.
- **Agent failure logging.** Failure reports written to `reports/` so next Architect knows.
- **Idea limits + staleness.** Evaluator gets current idea count + thresholds. Consistency Reviewer gets staleness config.
- **experiment_requests collection.** Full agent requests → `feedback/experiment_requests/` → Architect prompt.

---

# ALL KNOWN PROBLEMS

## BUGS — will break things

### [BUG-1] ~~Idea lifecycle moves leave ghost files~~ — FIXED
Fixed: `_remove_from_other_lifecycles()` now deletes old copies from all other lifecycle dirs
when an idea or pattern is moved to a new lifecycle directory.

### [BUG-2] ~~Negative scores enter rankings~~ — FIXED
Fixed: `update_rankings()` now filters `score > 0`.

### [BUG-3] ~~validate.py is O(N²) with Python loops~~ — N/A
Problem changed to First Autocorrelation Inequality. New validate.py uses FFT (O(N log N)).
Also mitigated by SCALE-8 eval caching.

### [BUG-4] ~~Brief paths are relative~~ — FIXED
Fixed: `_absolutize_brief_paths()` post-processes all briefs after the Architect writes them,
converting relative paths to absolute.

### [BUG-5] ~~Partial evaluator work is lost~~ — FIXED
Fixed: `phase_status()` now checks for any meaningful output files (generation_snapshot,
new_ideas, updated_ideas), not just the final report.

### [BUG-6] ~~Workspace cleanup destroys evidence~~ — FIXED
Fixed: Cleanup only runs on full success (both session and output move). On failure,
workspace is preserved for debugging.

### [BUG-7] ~~Evaluator writes `status:` but orchestrator reads `lifecycle:`~~ — FIXED
The evaluator template documented `status: active|established|...` but `_read_frontmatter_field()`
and all orchestrator routing read the `lifecycle` field. Ideas always landed in `active/`
regardless of evaluator intent. Fixed: evaluator.md and consistency_review.md now use `lifecycle`.
Orchestrator also falls back to reading `status` if `lifecycle` is missing (belt and suspenders).

### [BUG-8] ~~explore.md shows wrong evaluate.py invocation~~ — FIXED
Template said `python evaluate.py --solution output/sol01.py` but evaluate.py takes a positional
arg. Fixed to `python3 evaluate.py output/sol01.py`.

### [BUG-9] ~~Agent templates use `# score:` but orchestrator reads `# fitness:`~~ — FIXED
explore.md and exploit.md showed `# score: 0.612` header format but `_extract_score()` searched
for the primary metric name (`fitness`). Fixed: templates now show `# fitness:` header.
Also added `score` as a fallback key in `_extract_score()` for robustness.

### [BUG-10] ~~System critic template references nonexistent files~~ — FIXED
Template referenced `generator_log.md`, `pipeline_config.yaml`, and `generation_history/`
which don't exist. Fixed to reference actual paths: `reports/genNNN/`, `user/config.yaml`,
`history/generations/`.

### [BUG-11] ~~Orphan child processes after timeout~~ — FIXED
`subprocess.run()` with timeout sent SIGKILL to `npx` but grandchild node processes survived.
Fixed: `launch_claude_session` now uses `start_new_session=True` to create a process group,
then kills the entire group (`os.killpg`) on timeout. SIGTERM first, SIGKILL fallback.

### [BUG-12] ~~launch_claude_session swallowed errors — crash debrief never triggered~~ — FIXED
The function caught all exceptions internally and returned `""`. Agent crash detection code
(`work_error`) never triggered. Fixed: function now raises `SessionTimeout` or `SessionError`.
Callers catch these explicitly.

### [BUG-13] ~~phase_status missed evaluator completion when only report.md written~~ — FIXED
If evaluator wrote `report.md` (debrief) but not `evaluator_report.md`, `phase_status()` didn't
detect completion. Fixed: now also checks for `evaluator_debrief.md` in reports/ and `report.md`
in workspace output.

### [BUG-14] ~~Evaluator snapshot blocks finalize timing data~~ — FIXED
If evaluator wrote `generation_snapshot.md`, finalize skipped its own snapshot (with timing).
Fixed: finalize now appends timing section to existing snapshot instead of skipping.

### [BUG-15] ~~`inf` written to score_progression for minimize problems~~ — FIXED
When no valid solutions exist, `best_score` was `float("inf")` for minimize problems. Written
directly to progression file. Fixed: scores of 0.0 or non-finite values display as `--`.

### [BUG-16] ~~Valid solution count used `score > 0` heuristic~~ — FIXED
Population summary counted "valid" solutions by checking `score > 0`. Fixed: now reads
`is_valid` from `.score` JSON files.

### [BUG-17] ~~Evaluator confused about report.md vs evaluator_report.md~~ — FIXED
Debrief instructions pointed to `report.md` while evaluator template said `evaluator_report.md`.
Two files with different routing. Fixed: evaluator's debrief instruction now points to
`evaluator_report.md` so there's one canonical output file.

### [BUG-18] ~~Bootstrap idea schema mismatched evaluator template schema~~ — FIXED
Bootstrap wrote `certainty`, `solutions`, `stats` (nested), `related`. Evaluator template
documents `confidence`, `supported_by`, `contradicted_by`, `related_ideas`, `cluster`.
Fixed: bootstrap now writes the same fields as the evaluator template.

### [BUG-19] ~~`debrief_max_turns` in timeouts section but is a turn count~~ — FIXED
`debrief_max_turns` was under `timeouts:` config section and retrieved via `get_timeout()`.
Moved to `max_turns:` section as `debrief_recovery: 20` and read via `get_max_turns()`.

### [BUG-20] ~~`name:` vs `title:` field inconsistency across frontmatter~~ — FIXED
Bootstrap facts used `title:`, evaluator template uses `name:`. Dashboard read `title:` only.
Fixed: all bootstrap files now use `name:` (matching evaluator template). Dashboard scanner
reads `name` with `title` as fallback for backward compat.

### [BUG-21] ~~Evaluator template describes single-solution workflow~~ — FIXED
Step 1 said "Re-run evaluate.py on the solution" (singular) but evaluator processes all
solutions in a generation. Fixed to say "each solution in this generation's population."

### [BUG-22] ~~`proc.wait()` after SIGKILL could hang without timeout~~ — FIXED
After SIGKILL to process group, `proc.wait()` had no timeout. Added `timeout=5`.

### [BUG-23] ~~`significant_change` field in metrics.yaml unused~~ — FIXED
Was defined but never read. Now used in `_update_score_progression()` to mark trivial deltas
with `~` and show improvement direction in the progression table.

### [BUG-24] ~~Agent prompt lists `best.py` at gen 1 when it doesn't exist~~ — FIXED
Agents wasted a turn trying to read nonexistent symlink. Now only listed for gen 2+.

### [BUG-25] ~~`knowledge_hierarchy` and `idea_limits` config unclear if enforced~~ — FIXED
Added comments clarifying these are advisory (passed to agents as guidance text, not enforced
programmatically by the orchestrator).

## SCALING — surfaces after gen 10-15

### [SCALE-1] ~~Evaluator turn budget exhaustion~~ — FIXED
Fixed: Default max_turns bumped to 150. Pre-concatenated knowledge dump (`knowledge_dump.md`)
written to evaluator workspace before launch — evaluator reads one file instead of dozens.

### [SCALE-2] ~~update_rankings() rescans ALL generations~~ — FIXED
Fixed: `history/all_scores.json` caches all known scores. Only the new generation is scanned.

### [SCALE-3] ~~system_recommendations.md overwritten~~ — FIXED
Fixed: Previous version archived to `feedback/system_recommendations_archive/genNNN.md` before overwriting.

### [SCALE-4] ~~Coverage matrix grows O(N²)~~ — FIXED
Fixed: Evaluator prompt now instructs to cap matrix to top 30 most-used ideas and use sparse format.

### [SCALE-5] ~~Experiment results never consolidated~~ — FIXED
Fixed: Evaluator prompt now includes guidance to consolidate experiments older than 3 gens
into patterns/facts.

### [SCALE-6] ~~Cluster merge orphans idea back-references~~ — FIXED
Fixed: `_fix_orphaned_cluster_refs()` scans all ideas when clusters are removed/merged and
updates orphaned `cluster:` frontmatter to `unclustered`.

### [SCALE-7] Agent context window fills up during long sessions
With 150 max turns, an agent's context window accumulates tool results (file reads, bash outputs).
By turn 100+, earlier work may be compressed or lost. The agent forgets approaches it tried
at turn 10. This is inherent to Claude Code sessions but worsens with more complex knowledge bases.

**No fix** — fundamental limitation. Mitigate by keeping file reads targeted.

### [SCALE-8] ~~No evaluation caching~~ — FIXED
Fixed: `evaluate.py` caches results in `history/eval_cache.json` keyed by SHA-256 of file content.
Identical solutions return cached scores instantly.

### [SCALE-9] ~~Knowledge dump truncates without marker~~ — FIXED
`_preconcat_knowledge` truncated idea/cluster/pattern content at char limits but didn't indicate
truncation. Evaluator could read half an idea body thinking it was complete. Fixed: truncated
entries now end with `[TRUNCATED — read full file for details]`.

### [SCALE-10] Eval cache grows unbounded
`history/eval_cache.json` never prunes old entries. After hundreds of evaluations, file grows
indefinitely. **Not yet fixed** — low priority, can be pruned manually.

### [SCALE-11] `all_scores.json` stat-checks every cached path each generation
`update_rankings()` calls `Path.exists()` on every cached score entry. O(N) stat calls per
generation. **Not yet fixed** — low priority until 500+ solutions.

### [SCALE-12] ~~Experiment requests accumulate across all generations~~ — FIXED
Architect prompt listed ALL experiment requests from ALL generations via `rglob`. By gen 15+,
dozens of stale requests. Fixed: now only shows last 2 generations' requests.

### [SCALE-13] ~~Architect reads all prev-gen reports unbounded~~ — FIXED
With 8 agents producing 2-5K char reports, Architect spent many turns just reading.
Fixed: `_preconcat_prev_reports()` writes a single `prev_gen_reports.md` to briefs dir
(each report capped at 3K chars, total capped at 40K). Architect reads one file.

### [SCALE-14] ~~Knowledge dump can grow unbounded~~ — FIXED
With 100+ ideas × 2000 chars each, the evaluator's `knowledge_dump.md` could reach 200K+.
Fixed: total dump capped at 80K chars with truncation marker.

### [SCALE-15] ~~`agents.*.enabled` config never enforced~~ — FIXED
Config had `enabled: true/false` per agent type but orchestrator ignored it. Fixed:
`run_agents()` now filters manifest agents against config `enabled` flag before launching.

## DESIGN — architectural gaps vs spec

### [DESIGN-1] Write isolation is advisory only
The spec says agents write ONLY to `output/`. We tell them to in the prompt but nothing
enforces it. A misbehaving agent could corrupt `knowledge/`, `population/`, or any file.

**Risk:** Medium. Claude Code agents generally follow instructions. But a confused agent
could overwrite `state_of_affairs.md` directly instead of writing to its output dir.

### [DESIGN-2] No solution lineage tracking
When Exploit refines `gen005_explore_1/sol01.py`, it produces a new `sol01.py` with no
record of what it descended from. The solution-idea map tracks which ideas a solution uses,
but not parent→child relationships between solutions. The Architect can't distinguish
independent solutions from derivatives when planning Genetic crossovers.

### [DESIGN-3] Knowledge files have no version history
When the Evaluator updates `idea_042.md`, it overwrites the file. No diff, no changelog.
The Consistency Reviewer audits current state but can't see how knowledge evolved.
Git would solve this but the project isn't a repo.

### [DESIGN-4] Architect is a single point of failure
If the Architect writes poor briefs, all agents in that generation suffer. Debrief reports
feed back to the NEXT generation's Architect, but there's no mid-generation correction.
A bad Architect turn wastes an entire generation of compute.

### [DESIGN-5] No cost awareness or budget management
Each generation: 1 Architect (opus) + 3-8 agents (sonnet) + 1 Evaluator (opus) +
1 Critic (sonnet) + possibly 1 Consistency Reviewer (opus). Rough cost: $1-5 per generation.
30-gen run: **$30-150+**. No budget limit, no throttle, no "this gen was expensive, reduce next."

### [DESIGN-6] No semantic deduplication of solutions
Two Explore agents might independently arrive at the same approach (e.g., both use D₁₁ root system).
The system treats them as distinct. The Evaluator should catch this during idea matching, but
compute is wasted on redundant work that the coverage map was supposed to prevent.

### [DESIGN-7] "Read broadly" principle vs lean prompts tension
The spec says agents can "read the entire project file system." Our lean prompts list specific
files. An agent that follows the list strictly might miss relevant files not mentioned
(e.g., a research finding from 5 gens ago, an experiment result in a non-obvious directory).
The agent CAN read any file, but needs to know to look.

### [DESIGN-8] No rate limiting or backoff
10 parallel Claude Code sessions × 150 turns = potentially 1500 near-simultaneous API calls.
Could trigger API rate limits depending on tier, causing sessions to fail or degrade.

### [DESIGN-9] No warm-up / cold-start handling for gen 1-2
Gen 1 has no clusters, no coverage matrix, no solution-idea map, no population summary.
All agents get "no data yet" placeholders. The Evaluator must create all knowledge structures
from scratch with no examples. Gen 1-2 knowledge quality may be poor and set a bad foundation.

### [DESIGN-10] ~~Agents can't iterate as fast as spec envisions~~ — MITIGATED
Turn limits raised to 150 for solution agents. Agent prompts now enforce evaluate-immediately
workflow (write one → evaluate → update header → move on). With 150 turns and ~3 turns per
write-evaluate cycle plus ~15 turns reading overhead, agents can do **40+ iterations**.
Previously agents batch-wrote solutions without evaluating, wasting all their turns.

## SPEC DEVIATIONS — intentional differences from the design doc

| Spec says | We do | Why |
|-----------|-------|-----|
| Write isolation enforced | Advisory only | Would need sandboxing, complex |
| Solution names: `gen007_explore_2_sol03` | Raw naming `sol01.py` in `population/gen007/explore_2/` | Simpler; path provides identity |
| Debrief as follow-up to same session | Resume same session with `--resume` | Now matches spec; agent keeps full memory |
| Agents read at granular L0→L1→L2 drill-down | Agents get file path list, read what they want | Lean prompts; agents navigate autonomously |
| Knowledge files versioned | Overwritten in place | Would need git or versioning layer |
| `workspace/` archived after run | Deleted after output moved | Saves disk; prevents debugging (see BUG-6) |
| `observations/` directory used | Observations stay in `population/{gen}/{agent}/observations.md` | Simpler routing; evaluator reads from population/ |
| Consistency Reviewer debrief to `feedback/` | Debrief to `reports/` like all agents | Consistent; system critic reads from reports/ |

## UNCERTAIN — needs a real run to verify

1. ~~**Will agents actually write report.md?**~~ **MITIGATED.** Debrief recovery session now
   runs automatically if report.md is missing after timeout. Knowledge is never fully lost.

2. **Will the Architect produce valid manifest.yaml?** LLM writing YAML. Could produce invalid
   syntax, wrong brief paths, or skip agent types. Fallback manifest exists but loses strategy.
   **MITIGATED:** architect.md now shows correct manifest format with examples matching
   what the orchestrator actually parses.

3. ~~**Do 80 max turns suffice?**~~ **ADDRESSED.** Turn limits raised to 150 for solution agents.
   With mandatory evaluate-immediately workflow, agents now have room for 30+ write-evaluate cycles.

4. **Will lean prompts cause missed context?** Agents might not read all listed files, or miss
   relevant unlisted files. Monitor debrief reports for "I didn't know about X."

5. **Rate limiting with 10 parallel sessions.** May need to reduce `max_parallel_sessions`
   or add backoff logic.

6. **Will gen-1 Evaluator create clusters from scratch?** No example cluster files exist.
   Prompt describes the format but there's nothing to imitate. First clusters may be bad.

7. **Does the experiment_requests flow actually work?** Full agents → `experiment_requests.md` →
   collected to `feedback/` → listed in Architect prompt. Untested end-to-end.

8. ~~**Will agents handle absolute paths correctly?**~~ **FIXED.** `_absolutize_brief_paths()`
   post-processes all briefs to convert relative paths to absolute.

9. **Does `--allowedTools` auto-approve tools?** We assume it does. If it doesn't, agents will
   be blocked on every tool call waiting for user approval that never comes in `--print` mode.

10. **Context window pressure at high turn counts.** With 150 turns of tool results accumulating,
    does Claude Code compress/drop early context? If so, agents lose memory of early iterations.

11. **Will the Architect read and use the coverage matrix?** It's listed in "Files to Read" but
    the matrix format (N×N table) may be hard for the LLM to parse into actionable strategy.
    **MITIGATED:** Coverage matrix now capped to top 30 ideas with sparse format.

12. **Can the Evaluator reliably do idea matching?** Mapping which ideas each solution implements
    (central vs peripheral) requires understanding both the code and the idea descriptions.
    LLM judgment here could be inconsistent across generations.

## REMAINING POTENTIAL ISSUES — not bugs, monitor during runs

### Performance (negligible until proven otherwise)
- **YAML re-parsing**: `config.yaml` and `metrics.yaml` re-parsed ~30 times per generation
  across `load_config()`, `primary_metric()`, `_score_fmt()`, etc. ~50ms total. Would require
  threading config as a parameter through all functions to fix. Not worth the refactor.
- **`detect_interventions` rglob**: Scans `knowledge/`, `user/`, `agents/` trees every gen
  during finalize. ~200 stat() calls at gen 20. Non-blocking.

### Scaling (monitor after gen 15)
- **`all_scores.json` existence checks**: Every cached entry gets `Path.exists()` per gen.
  ~100 calls at gen 20. Could skip and just trust the cache, but stale entries would linger.
- **Eval cache unbounded**: `eval_cache.json` never pruned. Could add LRU or gen-based pruning
  if it grows past 10MB.
- **`.score` file reads in population summary**: Valid count reads every `.score` file.
  Could extend `all_scores.json` to cache `is_valid` alongside score.

### Advisory config not enforced
- **`max_instances` per agent type**: Architect sees the limit but orchestrator doesn't reject
  extra instances. Intentional — hard enforcement would override Architect judgment. Monitor
  if the Architect consistently exceeds limits.
- **`knowledge_hierarchy` values**: Token limits for State of Affairs, clusters, etc. are
  advisory guidance for agents. The orchestrator doesn't truncate knowledge files to fit.
  Monitor if knowledge files grow excessively large.

### Untested end-to-end flows
- **Genetic crossover**: Requires Architect to specify 2 parents by path. Never tested in a
  real run. The genetic.md template is correct but parent path resolution is untested.
- **Experimentator → knowledge pipeline**: Experiment results go to `knowledge/experiments/`,
  evaluator consolidates old ones. The full cycle is untested.
- **Consistency reviewer cluster updates**: When the reviewer writes `updated_clusters/`,
  the orchestrator diffs against existing clusters to find removed ones and fix orphaned refs.
  Untested with real cluster data.
