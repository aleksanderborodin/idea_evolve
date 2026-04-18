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

# Default values for metrics.yaml (used when key absent).
#
# DEFAULT_CONCURRENCY is a non-negative integer eval-slot budget:
#   0      = unlimited (CPU-bound problems, or GPU problems using NVIDIA MPS)
#   1      = serial (exactly one eval at a time; GPU without MPS)
#   N >= 2 = at most N simultaneous evals per group
# Only integers are accepted — no "parallel"/"serial" strings.
# See docs/problem_design_guide.md §9.1.
DEFAULT_CONCURRENCY = 0
DEFAULT_ARCHIVE_CHECKPOINTS = False
DEFAULT_CHECKPOINT_RETENTION = 50

# Per-problem opt-in for the per-group Light Evaluator (Phase 2.5). True by
# default — parallel-eval problems with multi-agent groups benefit from the
# mid-gen feedback loop. Serial-eval problems may prefer to disable it since
# the light eval runs between every agent and compounds wall-clock per gen.
# See docs/problem_design_guide.md §9.5.
DEFAULT_EVALUATOR_LIGHT_ENABLED = True

# Every agent role (explore, exploit, genetic, full, research, experimentator)
# may call evaluate.py during its session — research agents sometimes sanity-
# check a baseline they find in a paper, experimentator agents test the helpers
# they build, etc. All roles therefore count equally against the concurrency
# budget. The architect sizes parallel_groups so no group exceeds the budget;
# the orchestrator auto-splits any that do. There is no per-role exemption.

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

# ---- Kaggle-competition-as-problem constants (docs/problem_design_guide.md §13) ----

# Env var that the kaggle CLI reads for authentication. Added to .env.
KAGGLE_API_TOKEN_ENV = "KAGGLE_API_TOKEN"

# Template directory (leading underscore so the orchestrator's problem scan
# can skip it). The scaffolding script copies this into problems/<new_id>/.
KAGGLE_PROBLEM_SKELETON = "_kaggle_template"

# Per-problem data subdirectory. Gitignored via pattern
# `idea-evolve/problems/*/data/`; the .kaggle_spec.yaml inside is negated
# so the classification/hash manifest commits even when the payload doesn't.
DATA_SUBDIR = "data"

# Name of the committed Kaggle classification manifest inside DATA_SUBDIR.
KAGGLE_SPEC_FILENAME = ".kaggle_spec.yaml"
