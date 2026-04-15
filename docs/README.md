# Technical Documentation

Component-level reference for the idea-evolve system.
Lives at project root so it covers both the engine (`idea-evolve/`) and the dashboard (`dashboard/`).

## Engine

| File | What it covers |
|------|---------------|
| [architect.md](architect.md) | Architect phase: inputs, outputs, session flow, crash recovery |
| [agents.md](agents.md) | Agent work phase: types, workspace layout, output movement, session flow |
| [analysis_phases.md](analysis_phases.md) | Evaluator, System Critic, Consistency Reviewer: inputs, outputs, movement |
| [knowledge_base.md](knowledge_base.md) | Knowledge directory structure, file schemas (idea/cluster/fact/pattern), lifecycle transitions |
| [file_layout.md](file_layout.md) | Complete run directory tree with every file and its purpose |
| [harness.md](harness.md) | Harness adapter layer: ClaudeCodeAdapter, OpenCodeAdapter, config, process management |

## Dashboard

| File | What it covers |
|------|---------------|
| [dashboard.md](dashboard.md) | Dashboard app architecture, tabs, API endpoints, scanner functions, live status |

## Integration

| File | What it covers |
|------|---------------|
| [communication.md](communication.md) | Engine ↔ Dashboard file interface: what the orchestrator writes, what the dashboard reads |

## Update Rule

**When you change any system component, update the relevant doc file here.**
This includes: new file paths, changed schemas, new config keys, new phases or agent types,
new dashboard endpoints, bug fixes that change file layout, new output movement rules.

CLAUDE.md is the operational quick-reference (setup, running, known issues).
This `docs/` folder is the technical deep-dive (file I/O, schemas, data flow).
They are complementary — keep both in sync.
