#!/usr/bin/env python3
"""Cross-reference validator for code ↔ docs ↔ agent prompts.

Walks every doc/prompt and asserts:

1. Constants mentioned (`EVAL_QUEUE_PATH`, `GPU_LOCK_PATH`, env-var names, etc.)
   resolve to a definition in `problems/_shared/constants.py`.
2. Hardcoded constant *values* (e.g. literal `/tmp/idea_evolve_eval_queue.json`) only
   appear in `constants.py` itself — never duplicated in another file.
3. metrics.yaml flags referenced by name in docs (`concurrency:`, `archive_checkpoints:`,
   `checkpoint_retention:`) are actually parsed by the orchestrator.
4. The shared eval-contract block exists and is referenced by all four solution agents.
5. Per-problem `eval_hooks.py` either exists or is provably optional (default hook).

Exit 0 on success, 1 on any failure. Run before committing cross-cutting changes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent      # idea-evolve/
IDEA_EVOLVE = REPO_ROOT
PROJECT_ROOT = REPO_ROOT.parent                         # project_alpha/
CONSTANTS_FILE = IDEA_EVOLVE / "problems" / "_shared" / "constants.py"

sys.path.insert(0, str(IDEA_EVOLVE))
from problems._shared.constants import KAGGLE_PROBLEM_SKELETON  # noqa: E402


DOC_TARGETS = [
    PROJECT_ROOT / "CLAUDE.md",
    PROJECT_ROOT / "docs" / "problem_design_guide.md",
    IDEA_EVOLVE / "agents" / "_shared_eval_contract.md",
    IDEA_EVOLVE / "agents" / "architect.md",
    IDEA_EVOLVE / "agents" / "explore.md",
    IDEA_EVOLVE / "agents" / "exploit.md",
    IDEA_EVOLVE / "agents" / "full.md",
    IDEA_EVOLVE / "agents" / "genetic.md",
    IDEA_EVOLVE / "problems" / "strawberry" / "description.md",
    IDEA_EVOLVE / "problems" / "strawberry" / "helpers" / "README.md",
]


def _is_skeleton(path: Path) -> bool:
    """True if `path` is inside the Kaggle skeleton dir, which must be skipped
    by every problem-dir walk (it ships placeholder content, not real code)."""
    return any(part == KAGGLE_PROBLEM_SKELETON for part in path.parts)

# Constants whose VALUES are duplicated as string literals in non-constants.py
# files — flag this. Only the canonical literal in constants.py is allowed.
SENSITIVE_LITERALS = [
    "/tmp/idea_evolve_eval_queue.json",
    "/tmp/idea_evolve_gpu.lock",
    "IDEA_EVOLVE_AGENT_NAME",
    "IDEA_EVOLVE_PROBLEM",
    "IDEA_EVOLVE_ATTEMPT",
    "IDEA_EVOLVE_RUN_ROOT",
]

EXPECTED_METRICS_KEYS = ["concurrency", "archive_checkpoints", "checkpoint_retention"]


def parse_constants() -> dict[str, str]:
    """Return {name: literal_value} from constants.py."""
    out = {}
    for line in CONSTANTS_FILE.read_text().splitlines():
        m = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)(?:\s*#.*)?$', line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def check_constant_names_resolve(constants: dict[str, str]) -> list[str]:
    """Identifiers like EVAL_QUEUE_PATH mentioned in docs must exist in constants.py."""
    failures = []
    for doc in DOC_TARGETS:
        if not doc.exists():
            failures.append(f"missing doc: {doc}")
            continue
        text = doc.read_text()
        for ident in re.findall(r'\b(EVAL_QUEUE_PATH|GPU_LOCK_PATH|KILL_GRACE_SECONDS|'
                                r'KILL_DEADLINE_SECONDS|DEFAULT_CHECKPOINT_RETENTION|'
                                r'DEFAULT_CONCURRENCY|ENV_AGENT_NAME|ENV_PROBLEM|'
                                r'ENV_ATTEMPT|ENV_RUN_ROOT|PROC_LOGS_SUBDIR|'
                                r'CHECKPOINTS_SUBDIR|AGENT_KILL_LOCK_TEMPLATE)\b', text):
            if ident not in constants:
                failures.append(f"{doc}: references {ident} but it is not defined in constants.py")
    return failures


def check_no_duplicate_literals() -> list[str]:
    """Sensitive literal values must only appear in constants.py."""
    failures = []
    self_path = Path(__file__).resolve()
    for code_file in IDEA_EVOLVE.rglob("*.py"):
        if code_file.resolve() in (CONSTANTS_FILE.resolve(), self_path):
            continue
        # skip pycache, archives, and the Kaggle skeleton (placeholder content)
        if "__pycache__" in code_file.parts or "/runs/" in str(code_file):
            continue
        if _is_skeleton(code_file):
            continue
        try:
            text = code_file.read_text()
        except Exception:
            continue
        for literal in SENSITIVE_LITERALS:
            if literal in text:
                # allow if the only occurrence is in a comment
                lines = [ln for ln in text.splitlines() if literal in ln]
                non_comment = [ln for ln in lines if not ln.lstrip().startswith("#")]
                if non_comment:
                    failures.append(
                        f"{code_file.relative_to(REPO_ROOT)}: hardcoded literal "
                        f"{literal!r} — import the constant from problems._shared.constants instead"
                    )
    return failures


def check_metrics_keys_parsed() -> list[str]:
    """Keys mentioned in docs as metrics.yaml fields must be parsed by orchestrator/eval code."""
    failures = []
    code_text = ""
    for f in (IDEA_EVOLVE / "orchestrator.py",):
        if f.exists():
            code_text += f.read_text()
    for f in IDEA_EVOLVE.glob("problems/*/evaluate.py"):
        code_text += f.read_text()
    for f in IDEA_EVOLVE.glob("problems/*/helpers/core.py"):
        code_text += f.read_text()
    for key in EXPECTED_METRICS_KEYS:
        if key not in code_text:
            failures.append(f"metrics.yaml key {key!r} mentioned in docs but never read in code")
    return failures


def check_shared_contract_referenced() -> list[str]:
    """All four solution agents must reference _shared_eval_contract.md."""
    failures = []
    for agent in ("explore.md", "exploit.md", "full.md", "genetic.md"):
        path = IDEA_EVOLVE / "agents" / agent
        if "_shared_eval_contract.md" not in path.read_text():
            failures.append(f"{path}: missing reference to _shared_eval_contract.md")
    return failures


def check_eval_hooks_present() -> list[str]:
    """Problems with concurrency: serial must ship an eval_hooks.py."""
    import yaml  # noqa: PLC0415
    failures = []
    for metrics in IDEA_EVOLVE.glob("problems/*/metrics.yaml"):
        if _is_skeleton(metrics):
            continue
        try:
            data = yaml.safe_load(metrics.read_text()) or {}
        except Exception as e:
            failures.append(f"{metrics}: invalid YAML ({e})")
            continue
        mode = (data.get("concurrency") or "parallel").strip().lower()
        if mode == "serial":
            hook = metrics.parent / "eval_hooks.py"
            if not hook.exists():
                failures.append(
                    f"{metrics.parent.name}: concurrency: serial but no eval_hooks.py — "
                    f"required for problem-specific kill_eval()"
                )
    return failures


def check_kaggle_specs() -> list[str]:
    """Every .kaggle_spec.yaml must declare a valid classification + strategy.

    Enforces the contract documented in docs/problem_design_guide.md §13.3.
    Skeleton spec is allowed to contain `<REPLACE>` placeholders.
    """
    import yaml  # noqa: PLC0415
    failures = []
    valid_class = {"A", "B", "C", "D"}
    valid_strategy = {"self_check", "holdout_split", "simulator", "submit"}
    for spec in IDEA_EVOLVE.glob("problems/*/data/.kaggle_spec.yaml"):
        if _is_skeleton(spec):
            continue  # skeleton uses placeholders
        try:
            data = yaml.safe_load(spec.read_text()) or {}
        except Exception as e:
            failures.append(f"{spec}: invalid YAML ({e})")
            continue
        cls = str(data.get("classification") or "").strip()
        strat = str(data.get("local_eval_strategy") or "").strip()
        if cls not in valid_class:
            failures.append(f"{spec}: classification {cls!r} not in {sorted(valid_class)}")
        if strat not in valid_strategy:
            failures.append(f"{spec}: local_eval_strategy {strat!r} not in {sorted(valid_strategy)}")
        if not data.get("competition_id"):
            failures.append(f"{spec}: missing competition_id")
    return failures


def main() -> int:
    constants = parse_constants()
    all_failures = []
    all_failures += check_constant_names_resolve(constants)
    all_failures += check_no_duplicate_literals()
    all_failures += check_metrics_keys_parsed()
    all_failures += check_shared_contract_referenced()
    all_failures += check_eval_hooks_present()
    all_failures += check_kaggle_specs()

    if all_failures:
        print(f"FAIL — {len(all_failures)} consistency issues:\n", file=sys.stderr)
        for f in all_failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("OK — docs and code are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
