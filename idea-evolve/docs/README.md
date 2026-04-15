# Technical Documentation

Component-level reference for the idea-evolve system.

| File | What it covers |
|------|---------------|
| [architect.md](architect.md) | Architect phase: inputs, outputs, session flow, crash recovery |
| [agents.md](agents.md) | Agent work phase: types, workspace layout, output movement, session flow |
| [analysis_phases.md](analysis_phases.md) | Evaluator, System Critic, Consistency Reviewer: inputs, outputs, movement |
| [knowledge_base.md](knowledge_base.md) | Knowledge directory structure, file schemas (idea/cluster/fact/pattern), lifecycle transitions |
| [file_layout.md](file_layout.md) | Complete run directory tree with every file and its purpose |
| [harness.md](harness.md) | Harness adapter layer: ClaudeCodeAdapter, OpenCodeAdapter, config, process management |

## Update Rule

**When you change any system component, update the relevant doc file here.**
This includes: new file paths, changed schemas, new config keys, new phases or agent types,
bug fixes that change file layout, new output movement rules.

CLAUDE.md is the operational quick-reference (setup, running, known issues).
This `docs/` folder is the technical deep-dive (file I/O, schemas, data flow).
They are complementary — keep both in sync.
