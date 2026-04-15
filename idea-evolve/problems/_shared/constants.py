"""Single source of truth for cross-problem constants.

Every evaluate.py, helper, kill hook, and orchestrator module imports from here.
No string duplication — if you find yourself hard-coding any of these values
elsewhere, replace with an import.

Doc files (CLAUDE.md, docs/problem_design_guide.md, problems/*/description.md)
must reference these names verbatim. The check_docs_consistency.py script
enforces this.
"""

EVAL_QUEUE_PATH = "/tmp/idea_evolve_eval_queue.json"

# System-wide GPU lock for problems that train on a single GPU (e.g. strawberry).
# CPU problems do not touch this file.
GPU_LOCK_PATH = "/tmp/idea_evolve_gpu.lock"

# How long to wait between SIGTERM and SIGKILL when killing a stale eval.
KILL_GRACE_SECONDS = 2

# Total deadline for a kill operation (signal + verify resources released).
KILL_DEADLINE_SECONDS = 10

# Per-agent kill mutex prevents two new evals from racing to kill each other.
AGENT_KILL_LOCK_TEMPLATE = "/tmp/idea_evolve_agent_{name}.lock"

# Default values for metrics.yaml (used when key absent — backward compat).
DEFAULT_CONCURRENCY = "parallel"   # one of: parallel, serial
DEFAULT_ARCHIVE_CHECKPOINTS = False
DEFAULT_CHECKPOINT_RETENTION = 50

# Process-log retention per attempt (LRU; sticky logs excluded).
DEFAULT_PROC_LOG_RETENTION = 200

# Env vars the orchestrator injects into every agent subprocess so that
# any evaluate.py spawned downstream knows who launched it.
ENV_AGENT_NAME = "IDEA_EVOLVE_AGENT_NAME"
ENV_PROBLEM = "IDEA_EVOLVE_PROBLEM"
ENV_ATTEMPT = "IDEA_EVOLVE_ATTEMPT"
ENV_RUN_ROOT = "IDEA_EVOLVE_RUN_ROOT"

# Process-log subdirectory under runs/<problem>/<attempt>/.
PROC_LOGS_SUBDIR = "proc_logs"

# Checkpoint archive subdirectory under runs/<problem>/<attempt>/.
CHECKPOINTS_SUBDIR = "checkpoints"
