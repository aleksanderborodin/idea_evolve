# Alpha Evolve — V4
## Evolutionary Code Optimization Through Collaborative AI Agent Work Sessions

**V4 changes from V3:** Three-phase timeout with session resume (work → wrap-up → debrief, all in the same conversation), Architect-controlled per-agent timeouts, timing analytics, evaluation caching, knowledge pre-concatenation, configurable timeouts, incremental rankings, academic paper library with pipeline, prompt externalization, and numerous bug fixes. See [Section 14: Changes from V3](#14-changes-from-v3) for the complete list.

---

# 1. Why This System Exists

## 1.1 The Problem

Optimizing code is an iterative process. A developer writes a solution, tests it, sees where it falls short, tries a different approach, tests again. The best solutions often emerge not from a single brilliant insight but from the accumulation of many small discoveries: this data structure works better here, this edge case needs special handling, this optimization technique helps for large inputs but hurts for small ones.

Large language models are good at each individual step — writing code, analyzing results, proposing improvements. But they lack persistence. Each conversation starts fresh. There is no memory of what was tried, what worked, what failed, or why. The same dead ends get explored repeatedly. Promising directions get abandoned because no one remembered them.

The original AlphaEvolve system by Google DeepMind demonstrated that wrapping an LLM in an evolutionary loop — where solutions are stored, scored, and fed back as context for generating better solutions — can lead to genuine discoveries, including improvements to 56-year-old mathematical algorithms. But it operates as a single LLM pipeline: one prompt sampler, one model, one loop.

This system asks: what if instead of one LLM doing everything, we had a team of specialized agents, each with a distinct cognitive role, sharing knowledge through a structured file system, coordinating through an architect, and learning not just about the problem but about their own process?

## 1.2 The Core Idea

Alpha Evolve decomposes the evolutionary optimization process into specialized agent roles, each implemented as a Claude Code work session. Every agent can read files, write code, execute evaluation scripts, see results, iterate, and submit its best work. The agents share a common file system containing solutions, accumulated knowledge, and feedback. An Architect agent coordinates each generation by writing short briefs that guide each agent's attention. After each round, analysis agents extract knowledge from results and critique the system itself.

The file system is the single source of truth. The orchestrator — a simple Python loop — stores nothing in memory. It reads files to know what to do, launches agents by pointing them to their role definition and brief, and moves output files to their permanent locations between phases. If the orchestrator crashes and restarts, it reconstructs its state entirely from what files exist.

The result is a system where:

- Multiple approaches are explored in parallel by agents with different strategic roles
- Knowledge accumulates across generations in a hierarchical, compressed form that scales to many generations
- Every piece of knowledge tracks its provenance — who discovered it, when, based on what evidence
- Agents read knowledge at the right level of detail — high-level summaries for orientation, full detail only when relevant
- A dedicated Experimentator runs controlled tests that produce knowledge rather than solutions
- Agents report what they lacked, enabling the system to improve its own context quality
- A dedicated System Critic identifies pipeline problems and missing capabilities
- All system state lives in files — the orchestrator is stateless and recoverable
- The user can observe, intervene, or extend the system at any point by editing files
- **[V4] Agent work is never lost to timeouts — three-phase timeout with session resume preserves full agent memory**
- **[V4] The Architect controls per-agent timeouts based on timing analytics from prior generations**
- **[V4] Evaluation results are cached — identical solutions return scores instantly**
- **[V4] Research agents have internet access and a paper management pipeline (find → download → extract → summarize)**
- **[V4] Prompt templates externalized to `prompts/` directory — editable without touching Python code**

## 1.3 What Problems It Solves

The system targets optimization problems where candidate solutions can be automatically evaluated — sorting algorithms, scheduling heuristics, mathematical constructions, ML hyperparameter configurations, code optimization. The user provides a problem description, constraints, an evaluation script, and test cases. The system evolves solutions toward a target score.

Beyond the immediate optimization task, the system also solves meta-problems that plague LLM-based optimization: context loss between iterations, repeated exploration of dead ends, inability to learn from failures, lack of strategic coordination between parallel search efforts, and — critically — knowledge base bloat that overwhelms agent context windows as generations accumulate.

---

# 2. Design Philosophy

## 2.1 Agents Are Work Sessions, Not Function Calls

Each agent runs as a full Claude Code session with tool access. It reads files, writes code, runs evaluation scripts, sees results, and iterates — all within a single session. An agent might try five different approaches, evaluate each, and submit only its best. This is fundamentally different from systems where an LLM produces a single output that gets evaluated externally. The agent gets immediate feedback and can learn within its session.

## 2.2 Files Are the Single Source of Truth

All system state lives in the file system. The orchestrator is a stateless Python loop that reads files to determine what to do next and launches agents by pointing them to files. Agents read from the shared file system and write only to their designated output directories. The orchestrator moves outputs to permanent locations between phases.

This means: the Architect controls strategy by writing files (briefs, manifest). The Evaluator updates knowledge by writing files. The orchestrator just reads those files and acts. If any process crashes, the system can resume by examining which files exist. No state is held in memory, in databases, or in message queues. Files are the API between every component.

## 2.3 Read Broadly, Write Narrowly

All agents can read the entire project file system. Reading is unrestricted because agents need broad context to make good decisions.

Writing is restricted. Every agent writes only to its own `output/` directory inside its workspace. The orchestrator is the only process that moves files from agent output directories to their permanent locations in the shared file system. This means:

- An agent cannot accidentally overwrite another agent's work
- An agent cannot corrupt the knowledge base, population, or briefs
- Every file in the shared system was placed there by the orchestrator
- The user can inspect exactly what each agent produced before the orchestrator moved it
- Analysis agents write to designated output directories that the orchestrator copies to knowledge and feedback locations

Note: write isolation is advisory. The agents are instructed to write only to `output/`, but nothing enforces it. Claude Code agents generally follow instructions, but a confused agent could theoretically write elsewhere.

## 2.4 Information Flows Up as Compression, Down as Curation

Raw tries and metrics flow upward through the Evaluator agent, which compresses them into structured knowledge: ideas, patterns, and facts. That knowledge is further compressed into topic cluster summaries and a single State of Affairs document. The Architect reads the compressed layers and curates them into per-agent briefs — short reading lists that guide attention. No one assembles giant context blocks. Agents read at the level of detail they need: summaries for orientation, full files only when directly relevant.

## 2.5 Knowledge Has Three Layers of Resolution

The knowledge system is organized as a three-layer hierarchy. Layer 0 is a single State of Affairs document — a short narrative covering where the system stands, what works, what has been tried, and what the current frontier is. Layer 1 is a set of topic cluster summaries that group related ideas into themes, each with aggregated evidence and status. Layer 2 is the full detail: individual idea files, pattern files, fact files, each with complete provenance and evidence.

Every agent reads Layer 0. Agents read the Layer 1 clusters relevant to their task. Agents drill into Layer 2 files only when a specific idea or pattern is directly relevant to what they are working on. This ensures that an agent in generation 50 gets the same quality of orientation as an agent in generation 3, without drowning in accumulated detail.

**[V4]** The Evaluator receives a pre-concatenated knowledge dump (`knowledge_dump.md`) that combines all ideas, clusters, and patterns into a single file. This saves the Evaluator dozens of file-read turns, allowing it to spend its turn budget on analysis rather than navigation.

## 2.6 Every Piece of Knowledge Has Provenance

Every idea, pattern, fact, and observation records who created it, when, with what certainty, based on what evidence, and when it was last confirmed to still be true. An insight from generation 3 that was last confirmed in generation 3 is suspicious by generation 10. An insight confirmed in generation 9 is solid. Provenance enables the Consistency Reviewer to audit knowledge systematically and enables agents to weigh claims appropriately.

## 2.7 Structured Shell, Freeform Payload

The data model uses YAML frontmatter for structured metadata (queried by the orchestrator for filtering, aggregation, and ranking) wrapped around a markdown body of freeform text (read by agents for comprehension). The orchestrator uses the shell. Agents read the text. This balances machine-queryability with the nuanced reasoning that LLMs excel at.

## 2.8 The System Debugs Itself

Every agent gets debriefed after its run: what did you lack, what might be wrong, what would you do differently? These reports feed back to the Architect (for better briefs), the Evaluator (for knowledge correction), and the System Critic (for pipeline improvements). The System Critic looks at the system itself — not the solutions — and identifies missing capabilities, prompt problems, and actionable recommendations for the user. The system is aware of its own limitations and reports them.

**[V4]** The debrief is embedded in the agent's work prompt (not a separate follow-up session). If an agent times out before writing its report, a debrief recovery session runs automatically. See Section 6.

## 2.9 Debunked Knowledge Is Still Knowledge

When an idea is proven wrong, it is marked as debunked with an explanation of why. It is not deleted. Debunked ideas prevent agents from rediscovering dead ends. But if an agent independently tries a debunked approach and succeeds, that is a legitimate discovery — it means the debunking was context-dependent. Knowledge evolves; nothing is permanently forbidden.

## 2.10 [V4] Nothing Is Lost to Timeouts

Agent sessions have finite time budgets. In V3, if an agent timed out, its debrief was lost — the only record of what it tried died with the session. V4 uses a three-phase timeout: when an agent's work session times out, a **wrap-up session** continues the actual work (same model, full capabilities) with a fresh time budget. If the wrap-up also fails, a lightweight **debrief recovery** captures what was produced. Agents get a second chance to finish their work, not just report on it. See Section 6.

## 2.11 [V4] The System Measures Itself

Every phase and agent records how long it took. This timing data flows back to the Architect, which uses it to set per-agent timeouts for the next generation. Agents that need more time get more time. Agents that finish quickly get tighter budgets. The system adapts its resource allocation based on empirical measurement.

---

# 3. System Overview

## 3.1 The Orchestrator

The orchestrator is a Python script that runs the generation loop. It holds no state in memory. It determines what to do by reading files:

- To know which generation it is running: it reads the `history/generations/` directory and counts existing snapshots.
- To know which agents to launch: it reads the Architect's manifest at `briefs/gen{NNN}/manifest.yaml`.
- To know if a phase completed: it checks for the expected output files from that phase.
- To know if the user intervened: it compares file modification timestamps against the last generation snapshot.

The orchestrator's job is mechanical:
1. Launch the Architect agent.
2. Post-process briefs (convert relative paths to absolute).
3. Read the manifest the Architect wrote.
4. Launch the agents listed in the manifest, in parallel where specified, each with its work timeout.
5. For any agent that times out without a debrief report, launch a debrief recovery session.
6. Move agent outputs from workspaces to permanent locations.
7. Launch the Evaluator agent (with pre-concatenated knowledge dump).
8. Move Evaluator outputs to knowledge directories.
9. Launch the System Critic agent.
10. Move System Critic outputs to feedback directories (archiving previous recommendations).
11. If this is a consistency review generation (or if the Evaluator flagged `strategic_shift: true`), launch the Consistency Reviewer.
12. Move Consistency Reviewer outputs.
13. Update rankings (incrementally, scanning only the new generation).
14. Record timing data for all phases.
15. Save the generation snapshot (including timing).
16. Check for target score. If met, stop. Otherwise, loop.

Every step is: read a file → launch a session → move the outputs. The orchestrator does not decide strategy. It does not pick agents. It does not evaluate solutions. It moves files.

**Recovery.** If the orchestrator crashes mid-generation, it restarts and inspects the file system. Which files exist tells it exactly where it stopped. Briefs exist but no agent outputs? Resume at step 3. Agent outputs exist but no evaluator report? Resume at step 7. **[V4]** The evaluator completion check accepts partial outputs — if the evaluator produced some knowledge files but crashed before writing its final report, the partial work is preserved and used.

## 3.2 The Generation Loop

Each generation proceeds through these phases:

**Phase 1 — Planning.** The orchestrator launches the Architect. The Architect reads the State of Affairs (Layer 0), all topic cluster summaries (Layer 1), the population summary, score history, agent reports from the previous generation, system feedback, the latest consistency review, **[V4] and timing data from recent generations**. It assesses the strategic situation and writes a manifest plus a brief for each agent instance. **[V4]** The manifest can include per-agent `timeout` values. The orchestrator post-processes all briefs to convert relative file paths to absolute paths.

**Phase 2 — Parallel work sessions.** The orchestrator reads the manifest and launches all listed agent instances in parallel as Claude Code sessions. Each agent has a work timeout (from manifest or default). Each works autonomously: reading files, writing solutions, running the evaluation script, seeing scores, iterating, and submitting its best work. The debrief instructions are embedded in the agent's prompt — the agent writes its report as its final action.

**[V4] Phase 2b — Wrap-up.** If an agent's work session times out or crashes without producing `report.md`, the orchestrator launches a **wrap-up session** — a new session with the same model, same workspace access, and full tool permissions. The wrap-up agent reads the brief and partial work, then **continues the actual work**: completing solutions, running evaluations, and producing real results. This is not a reporting session — it is a continuation of the original agent's mission with a fresh time budget (default 900s, 60 turns).

**[V4] Phase 2c — Debrief recovery.** If no `report.md` exists after the wrap-up (or if wrap-up also timed out), a lightweight debrief recovery session (sonnet, 300s, 15 turns) examines what was produced and writes a report. This ensures knowledge is never fully lost.

**Phase 3 — Evaluation and knowledge update.** The orchestrator launches the Evaluator agent, pointed to its prompt template and the current generation's outputs. **[V4]** The evaluator workspace includes a pre-concatenated `knowledge_dump.md` containing all ideas, clusters, and patterns — saving dozens of file-read turns. The Evaluator verifies scores, extracts knowledge, performs idea matching, updates the solution-idea map, updates cluster summaries, **[V4] consolidates old experiment results into patterns/facts**, and generates the coverage matrix **(capped to top 30 ideas)**. **[V4]** When ideas move between lifecycle directories (active → established, etc.), old copies in previous directories are automatically deleted. When clusters are merged, orphaned idea back-references are updated.

**Phase 4 — System critique.** The orchestrator launches the System Critic. It reads all agent reports, observations, and feedback, and writes its analysis. **[V4]** Previous system recommendations are archived before being overwritten, so good insights from earlier generations are preserved.

**Phase 5 — Consistency review (every 3 generations).** The orchestrator checks the generation number. If it is a consistency review generation (or if the Evaluator flagged `strategic_shift: true`), the orchestrator launches the Consistency Reviewer. The Reviewer audits the knowledge base, corrects clusters, and rewrites the State of Affairs.

**Phase 6 — Finalize.** The orchestrator updates ranking symlinks (best.py, top/), saves a generation snapshot **(including timing data)** to `history/generations/`, and logs any detected user interventions. **[V4]** Rankings are updated incrementally: only the new generation's solutions are scanned, with previous scores loaded from `history/all_scores.json`. Negative scores are filtered out.

## 3.3 The Architecture

```
          User
           │ setup + optional intervention between gens
           ▼
    ┌─────────────┐
    │  Orchestrator │ ← Stateless Python loop. Reads files, launches agents,
    │  (stateless)  │   moves outputs. Records timing. Recovers from crashes.
    └──────┬──────┘
           │
   Phase 1 │ launch Architect → it writes manifest + briefs
           │ orchestrator post-processes briefs (absolute paths)
           ▼
    ┌─────────────┐
    │  Architect   │ reads Layer 0 + Layer 1 + state + timing data
    │              │ → writes manifest.yaml (with per-agent timeouts)
    │              │   + per-instance briefs + manifest reasoning
    └──────┬──────┘
           │ orchestrator reads manifest.yaml
   Phase 2 │ launches everything listed in manifest
           ├──→ Explore ×1-3        ─┐
           ├──→ Exploit ×1-3         │ all parallel within groups
           ├──→ Genetic ×1-3         │ sequential between groups
           ├──→ Full Agent ×1-2      ├── each has work timeout
           ├──→ Research ×1-2        │   each writes only to output/
           └──→ Experimentator ×0-3 ─┘   debrief embedded in prompt
                      │
                      │ solutions + observations + findings + experiment results
  Phase 2b │ orchestrator checks for missing report.md
           │ → launches wrap-up session (same model, finish the work)
  Phase 2c │ if still no report.md
           │ → launches debrief recovery (sonnet, write report only)
           ▼
   Phase 3 │ orchestrator launches Evaluator (with knowledge dump)
           ▼
    ┌─────────────────┐
    │ Evaluator Agent  │ verify scores (cached), extract knowledge,
    │                  │ idea matching, update Layer 1 clusters,
    │                  │ consolidate old experiments
    └────────┬────────┘
             │ orchestrator moves outputs, cleans ghost files
   Phase 4  │ orchestrator launches System Critic
            ▼
    ┌─────────────────┐
    │ System Critic    │ pipeline analysis, missing capabilities
    └────────┬────────┘
             │ orchestrator archives old recommendations, moves outputs
   Phase 5  │ (every 3rd gen or on strategic shift)
            ▼
    ┌─────────────────┐
    │ Consistency      │ audit knowledge base,
    │ Reviewer         │ rewrite Layer 0 State of Affairs
    └────────┬────────┘
             │ orchestrator moves outputs, fixes orphaned refs
   Phase 6  ▼
        Orchestrator: incremental rankings, save snapshot + timing, check target
```

## 3.4 The Manifest

The Architect's manifest is the bridge between strategic intelligence and mechanical execution. It is a YAML file that the orchestrator reads literally.

**Example manifest:**
```yaml
# briefs/gen007/manifest.yaml
generation: 7
strategy_summary: >
  Score stagnating at 0.89. Launching 3 explores for diversity
  in untried directions. 1 experimentator to test whether the
  score ceiling is metric-dependent. 1 exploit on best solution.

agents:
  - type: explore
    instance: 1
    model: sonnet
    brief: briefs/gen007/explore_1.md
    timeout: 1200

  - type: explore
    instance: 2
    model: sonnet
    brief: briefs/gen007/explore_2.md
    timeout: 900

  - type: exploit
    instance: 1
    model: opus
    brief: briefs/gen007/exploit_1.md
    timeout: 1500

  - type: research
    instance: 1
    model: sonnet
    brief: briefs/gen007/research_1.md
    timeout: 600

parallel_groups:
  - [explore_1, explore_2, research_1]
  - [exploit_1]
```

**Fields per agent:**
- `type` — One of: `explore`, `exploit`, `genetic`, `full`, `research`, `experimentator`.
- `instance` — Sequential integer within the type for this generation.
- `model` — Which model to use (`opus`, `sonnet`, `haiku`).
- `brief` — Path to the brief file, relative to project root.
- `timeout` — **[V4]** Optional. Session timeout in seconds. Default from `config.yaml` `timeouts.agent_default`. The Architect sets this per agent based on timing data from previous generations.

**Parallel groups:**
- `parallel_groups` — A list of lists. Each inner list contains agent names as `"type_instance"` strings.
- Groups execute sequentially. Agents within a group run in parallel.
- If omitted, all agents run in one parallel group.

The `strategy_summary` is for humans and analysis agents. The orchestrator ignores it.

---

# 4. Agent Roster

Every agent is launched the same way by the orchestrator: a Claude Code session that receives its prompt template (from `agents/`) and the path to its brief (from `briefs/`). The prompt template defines the agent's role, rules, and output format. The brief defines this specific instance's task for this generation.

Every agent can read the entire project file system. Every agent writes only to its `workspace/{gen}_{type}_{instance}/output/` directory. The orchestrator moves outputs to permanent locations after the session ends. **[V4]** Workspaces are only cleaned up on full success — if output movement fails, the workspace is preserved for debugging.

## 4.1 Architect — The Coordinator

The Architect reads the State of Affairs (Layer 0), all topic cluster summaries (Layer 1), the population summary, score history, agent reports from the previous generation, system feedback, consistency reviews, **[V4] and timing data from recent generations (`history/timing.json`)**. It writes a manifest (the execution plan for this generation) and a brief for each agent instance.

**[V4]** The Architect sets per-agent `timeout` values in the manifest based on empirical timing data. Agents that took long in previous generations get more time. Research agents that finish quickly get tighter budgets. The Architect sees the last 3 generations' timing data in its prompt.

The manifest tells the orchestrator exactly what to launch. The briefs tell each agent what to focus on. The Architect is the only agent that decides the composition of each generation.

**[V4]** All file paths in briefs must be absolute (using the project root). The orchestrator post-processes briefs to convert any remaining relative paths to absolute, ensuring agents' Read tool calls always work.

**Prompt template:** `agents/architect.md`
**Reads:** Layer 0 always. Layer 1 always. Population summary, score history, previous reports, feedback, timing data. Layer 2 as needed.
**Writes to output/:** Manifest (`manifest.yaml`) + one brief per agent instance + manifest reasoning (`manifest_reasoning.md`).
**Orchestrator moves to:** `briefs/{generation}/`

## 4.2 Explore — Divergent Search

The Explore agent finds fundamentally different approaches that the population has not tried. Its value comes from trying things other agents would not consider. It runs as a Claude Code work session: writes solutions, runs evaluate.py, iterates as many times as it decides, and submits its best work.

Multiple instances can run in parallel with different directives. Each instance can produce multiple solutions.

**Prompt template:** `agents/explore.md`
**Reads:** Layer 0 always. Layer 1 clusters as guided by brief. Layer 2 and other files as needed.
**Writes to output/:** Solutions (`sol*.py`), observations (`observations.md`), debrief report (`report.md`).
**Orchestrator moves to:** `population/{generation}/explore_{instance}/`

## 4.3 Exploit — Depth-First Refinement

The Exploit agent takes a specific solution and makes it better. Micro-optimizations, edge case handling, parameter tuning, structural tightening.

**Prompt template:** `agents/exploit.md`
**Reads:** Layer 0 always. Layer 1 clusters relevant to target solution. Layer 2 ideas and patterns for the target. Full code of target solution.
**Writes to output/:** Refined solutions (`sol*.py`), observations (`observations.md`), debrief report (`report.md`).
**Orchestrator moves to:** `population/{generation}/exploit_{instance}/`

## 4.4 Genetic — Crossover Synthesis

The Genetic agent combines the best parts of exactly 2 parent solutions into something better than either. The Architect selects parents for complementary strengths.

**Prompt template:** `agents/genetic.md`
**Reads:** Layer 0 always. Layer 1 clusters relevant to both parents. Layer 2 ideas for each parent. Full code of both parent solutions.
**Writes to output/:** Synthesized solutions (`sol*.py`), observations (`observations.md`), debrief report (`report.md`).
**Orchestrator moves to:** `population/{generation}/genetic_{instance}/`

## 4.5 Full Agent — Autonomous Problem Solver

The Full Agent is a skilled developer given a problem to solve with no restrictions. It gets the problem, the evaluation script, and full read access to every file in the project. No one tells it what to do.

The Full Agent can also write experiment requests to `output/experiment_requests.md`. These are collected to `feedback/experiment_requests/` and listed in the next Architect's prompt.

**Prompt template:** `agents/full.md`
**Reads:** Everything.
**Writes to output/:** Solutions (`sol*.py`), observations (`observations.md`), optionally experiment requests (`experiment_requests.md`), debrief report (`report.md`).
**Orchestrator moves to:** `population/{generation}/full_{instance}/`

## 4.6 Experimentator — Controlled Knowledge Producer

The Experimentator does not try to solve the problem. It runs controlled experiments that answer specific questions, producing knowledge rather than solutions.

The Experimentator runs all code inside a `sandbox/` subdirectory within its workspace.

**Prompt template:** `agents/experimentator.md`
**Reads:** Layer 0, Layer 1 clusters relevant to the experiment, Layer 2 files as needed, specific solutions referenced in brief.
**Writes to output/:** Experiment results, raw data (`sandbox/` directory). Does NOT write solutions to the population.
**Orchestrator moves to:** `knowledge/experiments/{generation}/experimentator_{instance}/`

## 4.7 Research — Knowledge Gatherer

The Research agent investigates techniques, algorithms, and approaches relevant to the problem. It does not produce solutions — it produces knowledge. It has **internet access** (WebSearch, WebFetch) and a **paper management pipeline** for downloading, extracting, and summarizing academic papers.

**Paper pipeline:** Research agents search for relevant papers online, download them via `papers/manage.py add <arxiv_id>`, read the auto-extracted text from `papers/md/`, and write structured summaries to `papers/summaries/`. These summaries include key results, relevance assessment, and actionable techniques. All future agents can read summaries from `papers/summaries/` without re-downloading.

**Prompt template:** `agents/research.md`
**Tools:** Read, Write, Bash, Glob, Grep, **WebSearch, WebFetch**
**Reads:** Layer 0 always. All Layer 1 clusters. Layer 2 as needed. Agent gap reports. `papers/summaries/` (existing paper summaries).
**Writes to output/:** Findings (`findings.md`), debrief report (`report.md`).
**Writes to papers/:** Downloaded PDFs (`pdf/`), extracted text (`md/`), summaries (`summaries/`), updated `index.yaml`.
**Orchestrator moves to:** `knowledge/research/{generation}/research_{instance}/`

## 4.8 Evaluator Agent — Knowledge Extraction, Score Verification, and Layer 1 Maintenance

The Evaluator agent runs after all work sessions complete. It is the primary knowledge worker: it verifies scores, extracts ideas and patterns from results, manages the knowledge lifecycle, maintains the solution-idea map, and updates the topic cluster summaries (Layer 1).

**[V4] Changes from V3:**

- **Pre-concatenated knowledge dump.** The evaluator workspace includes `knowledge_dump.md` — all ideas, clusters, and patterns in one file. The evaluator reads this first, then drills into individual files only when needed. This saves dozens of file-read turns.
- **Default max_turns increased to 120** (from 60) to give the Evaluator enough room for its analysis work.
- **Coverage matrix capped to top 30 most-used ideas** with sparse format to prevent O(N²) growth.
- **Experiment consolidation.** The evaluator is instructed to consolidate experiment results older than 3 generations into patterns/facts, preventing unbounded growth of `knowledge/experiments/`.
- **Ghost file cleanup.** When ideas move between lifecycle directories (active → established, etc.), the orchestrator automatically deletes old copies from previous directories. This prevents duplicates that compound every generation.
- **Cluster merge cleanup.** When clusters are removed or merged, the orchestrator updates orphaned idea `cluster:` references in YAML frontmatter to `unclustered`.

**Prompt template:** `agents/evaluator.md`
**Reads:** Everything, with focus on this generation's submitted solutions, observations, experiment results, the knowledge dump, and existing Layer 1 clusters.
**Writes to output/:** New/updated knowledge files (Layer 2), updated cluster summaries (Layer 1), solution-idea map, coverage matrix, generation snapshot, evaluator report, agent gaps.
**Orchestrator moves to:** `knowledge/` (ideas, patterns, facts, clusters), `history/` (solution-idea map, coverage matrix, snapshot).

## 4.9 System Critic — Pipeline Analyst

The System Critic runs after the Evaluator. It looks at the system itself, not the solutions.

**[V4]** Previous system recommendations are archived to `feedback/system_recommendations_archive/genNNN.md` before being overwritten. This preserves good insights from earlier generations that a weak critic might lose.

**Prompt template:** `agents/system_critic.md`
**Reads:** Everything, with focus on `reports/`, `feedback/`, and observations.
**Writes to output/:** System analysis, system recommendations, experiment suggestions.
**Orchestrator moves to:** `feedback/system_analysis/`, `feedback/system_recommendations.md`, `feedback/experiment_suggestions/`.

## 4.10 Consistency Reviewer — Knowledge Auditor and Layer 0 Maintainer

The Consistency Reviewer runs every 3 generations (configurable). It audits the entire knowledge base against current evidence, then rewrites the State of Affairs document (Layer 0) from scratch.

**Prompt template:** `agents/consistency_review.md`
**Reads:** Everything. Full knowledge base at all layers, coverage matrix, recent results, all agent reports.
**Writes to output/:** Consistency review report, updated knowledge files (Layer 2), corrected cluster summaries (Layer 1), rewritten State of Affairs (Layer 0).
**Orchestrator moves to:** `feedback/consistency_reviews/`, `knowledge/` (all layers).

---

# 5. Knowledge Model

## 5.1 Three Layers, One System

Knowledge is organized as a three-layer hierarchy designed to scale across many generations without overwhelming agent context windows.

```
┌─────────────────────────────────────────────────────┐
│  Layer 0 — State of Affairs                         │
│  Single document. ~800-1500 tokens.                 │
│  Written by: Consistency Reviewer (every 3 gens)    │
│              Gen-1 Evaluator (bootstrap)             │
│  Read by: ALL agents, FIRST thing                   │
├─────────────────────────────────────────────────────┤
│  Layer 1 — Topic Cluster Summaries                  │
│  One file per cluster. ~200-400 tokens each.        │
│  Written by: Evaluator (incremental updates)        │
│              Consistency Reviewer (corrections)      │
│  Read by: Agents read clusters relevant to task     │
├─────────────────────────────────────────────────────┤
│  Layer 2 — Ideas, Patterns, Facts                   │
│  Individual files with YAML frontmatter.            │
│  Written by: Evaluator (new + updates)              │
│              Consistency Reviewer (lifecycle moves)  │
│  Read by: Agents drill in when detail is needed     │
└─────────────────────────────────────────────────────┘
```

## 5.2 Knowledge Lifecycle

Ideas progress through lifecycle stages: `active` → `established` → `archived`, or `active` → `disputed` → `debunked`. Each transition requires evidence and is recorded with provenance.

**[V4]** When an idea moves from one lifecycle directory to another (e.g., `ideas/active/` → `ideas/established/`), the orchestrator automatically removes the old copy from all other lifecycle directories. This prevents ghost files that accumulated in V3.

## 5.3 Knowledge Files

All knowledge files use YAML frontmatter with a markdown body:

```markdown
---
id: idea_042
type: idea
title: "Use D₁₁ root system for lattice construction"
lifecycle: active
certainty: medium
created_gen: 3
created_by: explore_1
last_confirmed_gen: 7
cluster: cluster_lattice
tags: [lattice, algebraic]
solutions: [gen003/explore_1/sol01, gen007/exploit_1/sol01]
stats:
  times_used: 4
  avg_score: 0.82
  top_score: 0.91
  median_score: 0.83
related: [idea_038, idea_045]
---

The D₁₁ root system provides 2×11 = 22 vectors...
```

## 5.4 [V4] Knowledge Pre-Concatenation

For the Evaluator, reading dozens of individual idea, cluster, and pattern files consumes most of its turn budget. The orchestrator pre-concatenates all knowledge into a single `knowledge_dump.md` file in the evaluator's workspace. The evaluator reads this file first for orientation, then drills into individual files only when it needs to make specific edits. Ideas are truncated to 2000 characters, clusters to 1500, patterns to 1000 — enough for the evaluator to understand each piece without exhausting context.

## 5.5 [V4] Evaluation Caching

`evaluate.py` caches results in `history/eval_cache.json`, keyed by SHA-256 hash of file content. If two agents generate identical solutions, or the Evaluator re-validates already-validated solutions, cached scores are returned instantly. The cache uses `fcntl` file locking for thread-safe parallel access.

## 5.6 [V4] Metrics System — `problem/metrics.yaml`

The system supports multiple fitness metrics defined in `problem/metrics.yaml`. This file is the single source of truth for how scores are interpreted, formatted, and reported to agents.

**Schema:**

```yaml
specs:
  fitness:                          # Metric name — must match key in validate() return dict
    description: "C constant"       # Human-readable description
    decimals: 4                     # Decimal places for formatting (used in all score output)
    is_primary: true                # Only one metric should be primary — used for rankings/target
    higher_is_better: false         # Fitness direction: true = maximize, false = minimize
    lower_bound: 1.5053             # Theoretical best achievable value
    upper_bound: 5.0                # Worst expected value for valid solutions
    include_in_prompts: true        # Whether to show this metric in agent prompts
    significant_change: 0.0001      # Minimum change to consider meaningful
    sentinel_value: 1000.0          # Value returned on evaluation error

  is_valid:                         # Secondary metric
    description: "Whether valid"
    decimals: 0
    is_primary: false
    higher_is_better: true
    lower_bound: 0.0
    upper_bound: 1.0
    include_in_prompts: true
    significant_change: 1.0
    sentinel_value: 0
```

**How each field is used:**

| Field | Used by | Purpose |
|-------|---------|---------|
| `is_primary` | Orchestrator | Determines which metric drives rankings, target comparison, score progression |
| `higher_is_better` | Orchestrator | Determines sort direction for rankings, best-score selection, target comparison (`>=` vs `<=`) |
| `decimals` | Orchestrator | All score formatting — symlink names, summary, progression, snapshots, prints |
| `include_in_prompts` | Orchestrator | Which metrics appear in agent evaluation description |
| `sentinel_value` | evaluate.py | Error return value per metric; orchestrator filters scores near sentinel |
| `description` | Orchestrator | Shown in agent prompts and population summary |
| `lower_bound`/`upper_bound` | Orchestrator | Shown in agent prompts as theoretical bounds |
| `significant_change` | (Available for future use — evaluator could use to detect meaningful improvement) |

**Problem-agnostic design:** The orchestrator never hardcodes metric names, directions, or formatting. Everything flows from `metrics.yaml`. To change the problem:

1. Replace `problem/description.md`, `constraints.md`, `validate.py`, `helper.py`, `initial_programs/`
2. Replace `problem/metrics.yaml` with the new metric definitions
3. Update `user/config.yaml` `target_score` to match the new target
4. Clear old state: `knowledge/`, `population/`, `history/`, `reports/`, `feedback/`, `briefs/`
5. Update `user/initial_ideas.md` and `user/initial_facts.md`

**`evaluate.py` is also problem-agnostic:** It dynamically loads `validate.py` from its own directory using `importlib`. On error, it reads `metrics.yaml` to return the correct sentinel value for every metric. Solutions can `import helper` because `evaluate.py` adds the problem directory to `sys.path`.

---

# 6. The Debrief System

## 6.1 How It Works — [V4] Three-Phase Timeout

In V3, debrief was a separate follow-up session. In V4, debrief instructions are **embedded in the agent's work prompt** and recovery uses **session resume** (`--resume SESSION_ID`) so the agent retains full memory of its work across all phases.

**Phase 1 — Work session.** The agent runs with its work timeout (configurable per-agent via manifest, default from `config.yaml`) and a unique `--session-id`. The debrief instructions are at the end of its prompt, telling it to write `output/report.md` before finishing. If the agent completes normally, it writes the report and the session ends.

**Phase 2 — Wrap-up (same session resumed).** If the work session ends (timeout or crash) without `report.md` existing, the orchestrator **resumes the same session** using `--resume SESSION_ID`:
- The agent retains its **full conversation history** — it remembers every file it read, every solution it wrote, every evaluation it ran
- It receives a short directive message: "STOP creating. Evaluate all existing solutions. Write report."
- Model: same as the original agent (not downgraded)
- Timeout: configurable (`timeouts.wrap_up`, default 900s)
- Tools: full access — same as work session
- Because the agent has full memory, it doesn't waste turns re-reading context

This is a direct continuation of the same conversation, not a new session. The agent picks up exactly where it left off.

**Phase 3 — Debrief recovery (same session resumed again, or fallback).** If no `report.md` exists after the wrap-up:
- First tries resuming the same session again with "Write report NOW"
- Falls back to a new lightweight session (sonnet, 300s) only if no session_id is available
- The recovery agent reads the workspace output and writes a report based on what files were produced

This ensures even doubly-timed-out agents contribute knowledge. The session resume approach means the agent knows exactly what it tried — no inference from file contents needed.

## 6.2 Who Reads Debriefs

**Architect:** Reads all reports before writing briefs for the next generation.
**Evaluator:** Reads reports looking for knowledge corrections and observations.
**System Critic:** Reads reports looking for pipeline problems and missing capabilities.
**Research agent:** Reads `feedback/agent_gaps/` for knowledge gaps to fill.
**Consistency Reviewer:** Reads reports for "I think X might be wrong" statements.
**User:** Can read any report at any time.

## 6.3 Analysis Agent Debriefs

The Evaluator, System Critic, and Consistency Reviewer also use the three-phase timeout with session resume. If they time out, a wrap-up message resumes the same session. If that also fails, a debrief recovery resumes again (or falls back to a new session).

---

# 7. Multi-Instance Agents

## 7.1 How It Works

The Architect decides how many instances of each agent type to launch per generation by writing them into the manifest. The orchestrator reads the manifest and launches exactly what it says.

Each instance gets its own brief with a distinct directive. **[V4]** Each instance can also get its own timeout.

## 7.2 Instance Coordination

Instances of the same type do not communicate directly. They run in parallel without knowledge of each other. Coordination happens through the Architect: it writes different directives for each instance.

---

# 8. Many-to-Many: Solutions and Ideas

## 8.1 The Solution-Idea Map

The solution-idea map tracks which ideas are implemented in which solutions and how central each idea is. This enables the Architect to identify unexplored combinations for the Genetic agent, the Evaluator to assess idea impact quantitatively, and the coverage matrix to track what has been tried.

## 8.2 The Coverage Matrix

**[V4]** The coverage matrix is capped to the top 30 most-used ideas and uses a sparse format. At 50+ ideas, a full N×N matrix becomes unwieldy for both agents and the Evaluator to maintain. The sparse format lists only combinations that have been tried, with their best score and count.

---

# 9. File Structure

## 9.1 Directory Layout

```
alpha-evolve/
├── problem/                          # User-created problem definition (read-only for agents)
│   ├── description.md                # Problem description (problem-agnostic)
│   ├── constraints.md                # Hard/soft constraints
│   ├── evaluate.py                   # Problem-agnostic evaluator (loads validate.py, caches)
│   ├── validate.py                   # Problem-specific validation (returns {metric: value} dict)
│   ├── helper.py                     # Problem-specific helpers (e.g., differentiable objective)
│   ├── metrics.yaml                  # [V4] Metric definitions: direction, decimals, sentinels
│   └── initial_programs/             # Baseline solutions for agents to study
│
├── population/                       # All solutions (written only by orchestrator)
│   ├── best.py                       # Symlink to highest-scoring solution
│   ├── top/                          # Top 10 by score (ranked symlinks)
│   ├── gen007/
│   │   ├── explore_1/
│   │   │   ├── sol01.py
│   │   │   ├── sol01.score           # JSON: {fitness, margin, is_valid}
│   │   │   └── observations.md
│   │   ├── exploit_1/
│   │   │   └── sol01.py
│   │   └── ...
│   └── summary.md                    # Auto-generated population stats
│
├── knowledge/                        # Accumulated intelligence (3 layers)
│   ├── state_of_affairs.md           # Layer 0 — single strategic overview
│   ├── clusters/                     # Layer 1 — topic cluster summaries
│   ├── ideas/                        # Layer 2 — individual idea files
│   │   ├── active/
│   │   ├── established/
│   │   ├── disputed/
│   │   ├── debunked/
│   │   └── archived/
│   ├── patterns/                     # Layer 2 — pattern files
│   │   ├── active/
│   │   └── confirmed/
│   ├── facts/                        # Global — no lifecycle subdirs
│   ├── research/                     # Research findings per gen
│   └── experiments/                  # Experimentator results per gen
│
├── history/                          # Written only by orchestrator
│   ├── generations/                  # Per-gen snapshots (include timing in V4)
│   ├── score_progression.md
│   ├── solution_idea_map.md
│   ├── coverage_matrix.md            # [V4] Capped to top 30 ideas, sparse format
│   ├── all_scores.json               # [V4] Incremental rankings cache
│   ├── timing.json                   # [V4] Per-phase, per-agent timing data
│   └── eval_cache.json               # [V4] Evaluation results cache (SHA-256 keyed)
│
├── briefs/                           # Written only by orchestrator from Architect output
│   └── gen007/
│       ├── manifest.yaml             # [V4] Includes per-agent timeout field
│       ├── manifest_reasoning.md
│       ├── explore_1.md              # [V4] Paths post-processed to absolute
│       └── ...
│
├── reports/                          # Debrief reports (from agents or recovery sessions)
│   └── gen007/
│       ├── explore_1.md
│       ├── evaluator.md
│       └── ...
│
├── feedback/
│   ├── agent_gaps/
│   ├── system_analysis/
│   ├── system_recommendations.md
│   ├── system_recommendations_archive/  # [V4] Previous recommendations preserved
│   ├── experiment_suggestions/
│   ├── experiment_requests/           # Collected from Full agents
│   └── consistency_reviews/
│
├── workspace/                        # [V4] Preserved on failure, cleaned on success
│   ├── gen007_explore_1/
│   │   ├── prompt.md
│   │   ├── brief.md
│   │   └── output/
│   ├── gen007_evaluator/
│   │   ├── prompt.md
│   │   ├── knowledge_dump.md          # [V4] Pre-concatenated knowledge
│   │   └── output/
│   └── ...
│
├── user/
│   ├── initial_ideas.md
│   ├── initial_facts.md
│   ├── interventions.md
│   └── config.yaml                    # [V4] Expanded with timeouts section
│
├── agents/                            # Agent prompt templates
│   ├── architect.md                   # [V4] Rewritten to match actual manifest format
│   ├── explore.md
│   ├── exploit.md
│   ├── genetic.md
│   ├── full.md
│   ├── research.md                    # Has internet + paper pipeline instructions
│   ├── experimentator.md
│   ├── evaluator.md
│   ├── system_critic.md
│   └── consistency_review.md
│
├── prompts/                           # Prompt templates loaded by orchestrator at runtime
│   ├── debrief_instructions.md        # Appended to every agent prompt
│   ├── debrief_recovery.md            # Fallback when no session to resume
│   └── analysis_debrief.md            # Fallback for analysis agents
│
├── papers/                            # Academic paper library
│   ├── manage.py                      # Pipeline CLI: add, list, status, summarize
│   ├── index.yaml                     # Tracks all papers + pipeline status
│   ├── pdf/                           # Raw PDFs (NNN_shortname_author.pdf)
│   ├── md/                            # Auto-extracted text (NNN_shortname_author.md)
│   └── summaries/                     # Agent-written structured summaries
│
└── orchestrator.py
```

## 9.2 Write Permissions Summary

| Directory | Written by | Read by |
|-----------|-----------|---------|
| `problem/` | User (setup) | All agents |
| `population/` | Orchestrator (moves from agent output) | All agents |
| `knowledge/` | Orchestrator (moves from Evaluator/Reviewer output) | All agents |
| `history/` | Orchestrator (moves, timing, caches) | All agents |
| `briefs/` | Orchestrator (moves from Architect, post-processes) | All agents |
| `reports/` | Orchestrator (moves from agent/recovery output) | All agents |
| `feedback/` | Orchestrator (moves from Critic/Reviewer output) | All agents, user |
| `papers/` | Research agents (download + summarize) | All agents |
| `prompts/` | User (setup) | Orchestrator (loads at runtime) |
| `workspace/{agent}/output/` | That specific agent | Orchestrator (to move outputs) |
| `user/` | User | All agents, orchestrator |
| `agents/` | User (setup) | Orchestrator (copies to workspaces) |

---

# 10. User Interaction

## 10.1 The User Never Blocks the System

Alpha Evolve runs autonomously. The user sets up the problem, starts the system, and optionally intervenes between generations by editing files. The system never waits for user input.

## 10.2 Before the First Run

The user creates: `problem/description.md`, `problem/constraints.md`, `problem/evaluate.py`. Optionally, the user seeds knowledge: `user/initial_ideas.md` and `user/initial_facts.md`. The user configures the system in `user/config.yaml`.

## 10.3 Between Generations

The user can:

- Read `knowledge/state_of_affairs.md` for the system's compressed self-knowledge
- Read `feedback/system_recommendations.md` for what the system thinks needs changing
- **[V4]** Read `history/timing.json` to see how long each phase and agent took
- Edit knowledge files, prompts, briefs, or config
- All user edits are auto-detected and logged in `user/interventions.md`

---

# 11. Cold Start — Generation 1

Generation 1 has no population, no history, and minimal knowledge. The Architect writes a simple manifest: 2 explore + 1 full + 1 research. No exploit, genetic, or experimentator.

After generation 1's Evaluator pass, the system has its first knowledge files, clusters, coverage matrix, and State of Affairs. By generation 3, the system is fully operational.

---

# 12. Configuration

Configuration is split into two files:

- **`problem/metrics.yaml`** — Problem-specific: target score, metric definitions, fitness direction. See Section 5.6 for the full schema.
- **`user/config.yaml`** — Run-specific: how many generations, agent types, timeouts, models, parallelism. This file stays the same when you change problems.

```yaml
# user/config.yaml — run parameters (problem-independent)

# --- Evolution parameters ---
generations: 30                    # Maximum number of generations to run
# NOTE: target_score is in problem/metrics.yaml (problem-specific)

# --- Agent types ---
agents:
  explore:
    enabled: true
    max_instances: 3               # Broad search agents
  exploit:
    enabled: true
    max_instances: 3               # Refine existing solutions
  genetic:
    enabled: true
    max_instances: 3               # Cross two parent solutions
    parents_per_instance: 2
  full:
    enabled: true
    max_instances: 2               # End-to-end builders
  research:
    enabled: true
    max_instances: 2               # Domain research
  experimentator:
    enabled: true
    max_instances: 3               # Controlled experiments

# --- Analysis phases ---
analysis:
  evaluator:
    enabled: true
    model: opus                    # Needs high reasoning quality
  system_critic:
    enabled: true
    model: sonnet

# --- [V4] Timeouts (seconds) ---
# Three-phase timeout: work → wrap-up (continue work) → debrief recovery (report only).
# The Architect can override agent_default per agent via manifest.yaml.
timeouts:
  architect: 600                   # Architect planning session
  agent_default: 900               # Default work phase for solution agents
  evaluator: 900                   # Evaluator analysis phase
  system_critic: 600               # System critic analysis phase
  consistency_reviewer: 900        # Consistency review phase
  wrap_up: 900                     # Wrap-up session (continue work after timeout)
  debrief_recovery: 300            # Debrief recovery session (report only, after wrap-up fails)

# --- Turn budgets ---
max_turns:
  architect: 30
  explore: 80
  exploit: 80
  full: 80
  genetic: 60
  experimentator: 60
  research: 40
  evaluator: 120                   # [V4] Bumped from 60
  system_critic: 30
  consistency_reviewer: 40

# --- Models ---
default_model: sonnet
architect_model: opus

# --- Parallelism ---
max_parallel_sessions: 10

# --- Knowledge management ---
knowledge_hierarchy:
  state_of_affairs_max_tokens: 1500
  cluster_max_tokens: 400
  max_clusters: 20
  merge_threshold: 0.7

idea_limits:
  max_ideas: 100

staleness_threshold: 5

consistency_review_interval: 3
emergency_review_on_strategic_shift: true
```

---

# 13. What Makes This Different

The original AlphaEvolve is a single LLM loop that generates, evaluates, and iterates. This system inherits those principles but restructures them:

**Specialization.** Specialized agents do what they do best. Explore diverges. Exploit refines. Genetic combines. Research investigates. The Experimentator runs controlled tests. The Evaluator extracts knowledge. The System Critic debugs the pipeline.

**Hierarchical accumulated knowledge.** A three-layer knowledge hierarchy: State of Affairs for orientation, cluster summaries for themes, individual files for detail. An agent in generation 50 reads the same compact State of Affairs as one in generation 3.

**Coverage tracking.** The coverage matrix (structured data) and coverage map (narrative) prevent retreading explored ground.

**Controlled experimentation.** The Experimentator produces high-confidence knowledge rather than score-chasing solutions.

**Files as single source of truth.** All state lives in the file system. The orchestrator is stateless. If it crashes, it resumes from files.

**Self-awareness.** Through debriefs and the System Critic, the system identifies its own limitations and reports them.

**Human-in-the-loop without blocking.** The user can intervene at any point by editing files. The system never waits.

**[V4] Resilience.** Three-phase timeout with session resume (work → wrap-up → debrief, same conversation) ensures work is completed and knowledge is never lost. The agent retains full memory across all phases. Partial outputs are accepted. Workspaces are preserved on failure. The system degrades gracefully rather than losing work.

**[V4] Self-measurement.** Timing data flows back to the Architect, which adapts timeout budgets per agent. The system measures its own resource usage and optimizes allocation.

**[V4] Scaling.** Incremental rankings, evaluation caching, knowledge pre-concatenation, coverage matrix capping, experiment consolidation, and ghost file cleanup keep the system efficient through generation 30+.

---

# 14. Changes from V3

## Bugs Fixed

| Issue | Fix |
|-------|-----|
| **Ghost files** — ideas kept in old lifecycle dirs after moving | Orchestrator deletes old copies from all other lifecycle dirs |
| **Negative scores in rankings** — dragged down averages | Filtered: `score > 0` required |
| **Relative paths in briefs** — agents' Read tool failed | Orchestrator post-processes all briefs to absolute paths |
| **Partial evaluator loss** — restart from scratch on crash | Accepts partial outputs (any meaningful file, not just final report) |
| **Workspace cleanup on failure** — destroyed debugging evidence | Cleanup only on full success; workspace preserved on failure |
| **Orphaned cluster refs** — idea `cluster:` field pointed to merged/deleted cluster | Orchestrator updates to `unclustered` when clusters are removed |
| **Operator precedence** — phase_status had `or ... and` without parens | Added parentheses for correct evaluation |

## Scaling Improvements

| Issue | Fix |
|-------|-----|
| **Evaluator turn exhaustion** — ran out of turns reading files at gen 12+ | Default turns bumped to 120 + pre-concatenated knowledge dump |
| **Rankings rescanned all gens** — quadratic total work | Incremental: `all_scores.json` cache, only scan new generation |
| **Recommendations overwritten** — good insights lost | Previous version archived to `system_recommendations_archive/` |
| **Coverage matrix O(N²)** — unwieldy at 50+ ideas | Capped to top 30 ideas, sparse format |
| **Experiments never consolidated** — unbounded growth | Evaluator instructed to consolidate experiments older than 3 gens |
| **No eval caching** — identical solutions re-validated | Cache by SHA-256 content hash in `eval_cache.json` with file locking |

## New Capabilities

| Feature | Description |
|---------|-------------|
| **Three-phase timeout with session resume** | Work → wrap-up → debrief, all via `--resume` on the same session. Agent keeps full memory across phases. Falls back to new session only if no session_id. |
| **Architect-controlled timeouts** | Per-agent `timeout` field in manifest, based on timing data |
| **Timing analytics** | Every phase/agent timed, stored in `history/timing.json`, shown in generation snapshots |
| **Configurable timeouts** | All timeouts in `config.yaml` `timeouts` section, not hardcoded |
| **Knowledge pre-concatenation** | Single `knowledge_dump.md` for evaluator, saves dozens of turns |
| **Eval cache with file locking** | Thread-safe cache for parallel agent evaluation |
| **Paper library** | `papers/` directory with pipeline: find → download → extract → summarize. Managed via `papers/manage.py`. Research agents have WebSearch + WebFetch. Paper summaries available to all agents. |
| **Externalized prompts** | Prompt templates in `prompts/` directory, loaded at runtime. Editable without touching orchestrator code. |

## Architecture Changes

| V3 | V4 |
|----|-----|
| Debrief as separate follow-up session | Debrief embedded in work prompt + wrap-up session to finish work + debrief recovery as final fallback |
| Fixed 900s agent timeout | Architect sets per-agent timeout from timing data |
| Evaluator 60 max turns | Evaluator 120 max turns + knowledge dump |
| All timeouts hardcoded | All timeouts in `config.yaml` |
| Full N×N coverage matrix | Top-30 sparse coverage matrix |
| Rankings rescan all gens | Incremental scan + JSON cache |
| Workspace always cleaned | Workspace preserved on failure |
| architect.md referenced wrong paths/format | architect.md rewritten to match actual orchestrator |
