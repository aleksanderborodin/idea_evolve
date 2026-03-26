#!/usr/bin/env python3
"""
Alpha Evolve Orchestrator

Stateless loop that reads files, launches Claude Code agents, and moves outputs.
All state lives in the file system. If this script crashes, it can resume by
inspecting which files exist.
"""

import argparse
import ast
import fcntl
import hashlib
import json
import math
import os
import re
import signal
import shutil
import subprocess
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MAX_TURNS = {
    "architect": 50,
    "explore": 135,
    "exploit": 135,
    "genetic": 100,
    "full": 135,
    "research": 70,
    "experimentator": 100,
    "evaluator": 200,
    "system_critic": 50,
    "consistency_reviewer": 70,
    "wrap_up": 100,
    "debrief_recovery": 25,
}


# ---------------------------------------------------------------------------
# Timing data
# ---------------------------------------------------------------------------

def _load_timing(project_root: Path) -> dict:
    path = project_root / "history" / "timing.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"generations": {}}


def _save_timing(project_root: Path, timing: dict):
    path = project_root / "history" / "timing.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(timing, indent=2))


def _record_timing(project_root: Path, gen: int, key: str, elapsed: float):
    """Thread-safe timing record with file locking."""
    lock_path = project_root / "history" / "timing.json.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(lock_path, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            timing = _load_timing(project_root)
            gen_key = f"gen{gen:03d}"
            if gen_key not in timing["generations"]:
                timing["generations"][gen_key] = {}
            timing["generations"][gen_key][key] = round(elapsed, 1)
            _save_timing(project_root, timing)
            fcntl.flock(lock, fcntl.LOCK_UN)
    except Exception:
        pass


def _get_recent_timing(project_root: Path, current_gen: int, lookback: int = 3) -> dict:
    """Get timing data from recent generations for the Architect."""
    timing = _load_timing(project_root)
    result = {}
    for g in range(max(1, current_gen - lookback), current_gen):
        key = f"gen{g:03d}"
        if key in timing.get("generations", {}):
            result[key] = timing["generations"][key]
    return result


PREFLIGHT_CACHE = "history/.preflight_ok"

REQUIRED_FILES = [
    "problem/description.md",
    "problem/evaluate.py",
    "problem/validate.py",
    "problem/metrics.yaml",
    "user/config.yaml",
    "agents/architect.md",
    "agents/explore.md",
    "agents/exploit.md",
    "agents/genetic.md",
    "agents/full.md",
    "agents/research.md",
    "agents/experimentator.md",
    "agents/evaluator.md",
    "agents/system_critic.md",
    "agents/consistency_review.md",
    "prompts/debrief_instructions.md",
    "prompts/analysis_debrief.md",
    "prompts/debrief_recovery.md",
    "problem/helpers/__init__.py",
    "problem/helpers/core.py",
]


def _preflight_check(project_root: Path):
    """Validate all required files exist. Cached so re-runs are instant."""
    cache_path = project_root / PREFLIGHT_CACHE
    # Build a hash of all required file mtimes for cache invalidation
    mtimes = []
    missing = []
    for rel in REQUIRED_FILES:
        p = project_root / rel
        if p.exists():
            mtimes.append(f"{rel}:{p.stat().st_mtime}")
        else:
            missing.append(rel)

    if missing:
        print("ERROR: Required files missing:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    check_hash = hashlib.md5("\n".join(mtimes).encode()).hexdigest()

    # If cache matches, skip
    if cache_path.exists():
        try:
            if cache_path.read_text().strip() == check_hash:
                return
        except Exception:
            pass

    # All files present — write cache
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(check_hash)
    print("  Preflight check passed — all required files present.")


def load_config(project_root: Path) -> dict:
    config_path = project_root / "user" / "config.yaml"
    if not config_path.exists():
        print(f"ERROR: Config not found at {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_metrics_file(project_root: Path) -> dict:
    """Load the full metrics.yaml file. Returns raw dict."""
    metrics_path = project_root / "problem" / "metrics.yaml"
    if metrics_path.exists():
        try:
            return yaml.safe_load(metrics_path.read_text()) or {}
        except Exception:
            pass
    return {}


def load_metrics(project_root: Path) -> dict:
    """Load all metric specs from metrics.yaml. Returns dict of {name: spec}."""
    return load_metrics_file(project_root).get("specs", {})


def primary_metric(project_root: Path) -> tuple[str, dict]:
    """Return (name, spec) for the primary metric from metrics.yaml."""
    specs = load_metrics(project_root)
    for name, spec in specs.items():
        if spec.get("is_primary", False):
            return name, spec
    # Fallback: first metric or empty
    if specs:
        name = next(iter(specs))
        return name, specs[name]
    return "fitness", {}


def fitness_is_higher_better(project_root: Path) -> bool:
    """Determine if higher fitness is better from metrics.yaml primary metric."""
    _, spec = primary_metric(project_root)
    return spec.get("higher_is_better", True)


def get_target_score(project_root: Path, config: dict) -> float:
    """Get target score from metrics.yaml (preferred) or config.yaml (fallback)."""
    mf = load_metrics_file(project_root)
    if "target_score" in mf:
        return float(mf["target_score"])
    return float(config.get("target_score", 0.95))


def _score_fmt(project_root: Path) -> str:
    """Return format string for primary metric based on decimals field."""
    _, spec = primary_metric(project_root)
    decimals = spec.get("decimals", 4)
    return f".{decimals}f"


def get_max_turns(config: dict, agent_type: str) -> int:
    overrides = config.get("max_turns", {})
    return overrides.get(agent_type, DEFAULT_MAX_TURNS.get(agent_type, 50))


DEFAULT_TIMEOUTS = {
    "architect": 1020,
    "agent_default": 1530,
    "evaluator": 1530,
    "system_critic": 1020,
    "consistency_reviewer": 1530,
    "wrap_up": 1530,
    "debrief_recovery": 510,
}


def get_timeout(config: dict, key: str) -> int:
    return config.get("timeouts", {}).get(key, DEFAULT_TIMEOUTS.get(key, 900))


# ---------------------------------------------------------------------------
# State reconstruction from file system
# ---------------------------------------------------------------------------

def current_generation(project_root: Path) -> int:
    gen_dir = project_root / "history" / "generations"
    if not gen_dir.exists():
        return 1
    snapshots = sorted(gen_dir.glob("gen*.md"))
    return len(snapshots) + 1


def phase_status(project_root: Path, gen: int) -> str:
    gen_str = f"gen{gen:03d}"

    snapshot = project_root / "history" / "generations" / f"{gen_str}.md"
    if snapshot.exists():
        return "complete"

    # Check moved outputs (survive cleanup) OR workspace (mid-run)
    consistency_review = project_root / "feedback" / "consistency_reviews" / f"{gen_str}.md"
    consistency_ws = project_root / "workspace" / f"{gen_str}_consistency_reviewer"
    if consistency_review.exists() or (
        consistency_ws.exists() and (consistency_ws / "output" / "state_of_affairs.md").exists()
    ):
        return "consistency_done"

    critic_analysis = project_root / "feedback" / "system_analysis" / f"{gen_str}.md"
    critic_ws = project_root / "workspace" / f"{gen_str}_system_critic"
    if critic_analysis.exists() or (
        critic_ws.exists() and (critic_ws / "output" / "system_analysis.md").exists()
    ):
        return "critic_done"

    # Check moved outputs (survive cleanup) OR workspace (mid-run)
    evaluator_report = project_root / "reports" / gen_str / "evaluator.md"
    evaluator_debrief = project_root / "reports" / gen_str / "evaluator_debrief.md"
    evaluator_dir = project_root / "workspace" / f"{gen_str}_evaluator"
    if evaluator_report.exists() or evaluator_debrief.exists():
        return "evaluator_done"
    if evaluator_dir.exists():
        ev_output = evaluator_dir / "output"
        ev_has_output = (
            (ev_output / "evaluator_report.md").exists()
            or (ev_output / "report.md").exists()
            or (ev_output / "generation_snapshot.md").exists()
            or ((ev_output / "new_ideas").exists() and any((ev_output / "new_ideas").iterdir()))
            or ((ev_output / "updated_ideas").exists() and any((ev_output / "updated_ideas").iterdir()))
        )
        if ev_has_output:
            return "evaluator_done"

    # Agents are done if ALL manifest agents have produced output or report.
    # Check manifest to know how many agents were planned.
    # IMPORTANT: only trust the manifest if the architect session completed cleanly
    # (.architect_done sentinel). Without it, the manifest may be an intermediate write
    # from an orphaned architect process (written before the orchestrator was killed).
    manifest_path = project_root / "briefs" / gen_str / "manifest.yaml"
    architect_done = project_root / "briefs" / gen_str / ".architect_done"
    if manifest_path.exists() and not architect_done.exists():
        # Manifest exists but architect didn't finish cleanly — treat as not started
        # so the orchestrator re-runs the architect and gets a complete manifest.
        return "not_started"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest_data = yaml.safe_load(f) or {}
            planned_agents = manifest_data.get("agents", [])
            if planned_agents:
                pop_dir = project_root / "population" / gen_str
                reports_dir = project_root / "reports" / gen_str
                research_dir = project_root / "knowledge" / "research" / gen_str
                experiments_dir = project_root / "knowledge" / "experiments" / gen_str

                completed = 0
                for spec in planned_agents:
                    atype = spec.get("type", "")
                    inst = spec.get("instance", 1)
                    agent_name = f"{atype}_{inst}"
                    # Check: output dir in population, OR report in reports/, OR
                    # research/experiment output, OR workspace still has output/
                    has_agent_output = (
                        (pop_dir / agent_name).exists()
                        or (reports_dir / f"{agent_name}.md").exists()
                        or (atype == "research" and research_dir.exists() and any(research_dir.iterdir()))
                        or (atype == "experimentator" and experiments_dir.exists() and any(experiments_dir.iterdir()))
                    )
                    # Also check workspace (agent ran but outputs not yet moved)
                    ws_dir = project_root / "workspace" / f"{gen_str}_{agent_name}"
                    if not has_agent_output and ws_dir.exists():
                        ws_output = ws_dir / "output"
                        has_agent_output = ws_output.exists() and any(ws_output.iterdir())
                    if has_agent_output:
                        completed += 1

                if completed >= len(planned_agents):
                    return "agents_done"
                elif completed > 0:
                    # Some agents done but not all — still in progress.
                    # Return "planned" so run_agents re-runs (it will skip completed ones
                    # since their workspaces are already moved).
                    return "planned"
        except Exception:
            pass

    # Fallback for missing/corrupt manifest: check if any output exists
    pop_dir = project_root / "population" / gen_str
    reports_dir = project_root / "reports" / gen_str
    research_dir = project_root / "knowledge" / "research" / gen_str
    has_output = (
        (pop_dir.exists() and any(pop_dir.iterdir()))
        or (reports_dir.exists() and any(reports_dir.iterdir()))
        or (research_dir.exists() and any(research_dir.iterdir()))
    )
    if has_output:
        return "agents_done"

    manifest = project_root / "briefs" / gen_str / "manifest.yaml"
    if manifest.exists():
        return "planned"

    return "not_started"


# ---------------------------------------------------------------------------
# Claude Code session launcher
# ---------------------------------------------------------------------------

MODEL_MAP = {
    "opus": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}


class SessionTimeout(Exception):
    """Raised when a Claude session exceeds its timeout."""
    def __init__(self, msg, session_id=None):
        super().__init__(msg)
        self.session_id = session_id


class SessionError(Exception):
    """Raised when a Claude session exits with a non-zero return code."""
    def __init__(self, msg, session_id=None):
        super().__init__(msg)
        self.session_id = session_id


def _run_claude_process(cmd, prompt_text, project_root, timeout):
    """Low-level: run a Claude Code CLI process with timeout and process-group cleanup."""
    env = os.environ.copy()
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = "16000"

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root),
            env=env,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(input=prompt_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
            raise SessionTimeout(f"Timed out after {timeout}s")

        if proc.returncode != 0:
            if stderr:
                print(f"  STDERR: {stderr[:500]}")
            raise SessionError(f"Exited with code {proc.returncode}: {stderr[:200] if stderr else 'no stderr'}")
        return stdout
    except FileNotFoundError:
        print("  ERROR: Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)


def launch_claude_session(
    project_root: Path,
    prompt_text: str,
    model: str = "sonnet",
    timeout: int = 300,
    max_turns: int = 50,
    allowed_tools: list[str] | None = None,
    session_id: str | None = None,
) -> tuple[str, str]:
    """Launch a new Claude Code session. Returns (stdout, session_id)."""
    model_id = MODEL_MAP.get(model, model)
    if session_id is None:
        session_id = str(uuid.uuid4())

    cmd = [
        "npx", "@anthropic-ai/claude-code",
        "--print",
        "--model", model_id,
        "--max-turns", str(max_turns),
        "--session-id", session_id,
    ]

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

    try:
        stdout = _run_claude_process(cmd, prompt_text, project_root, timeout)
    except SessionTimeout as e:
        raise SessionTimeout(str(e), session_id=session_id) from None
    except SessionError as e:
        raise SessionError(str(e), session_id=session_id) from None
    return stdout, session_id


def resume_claude_session(
    project_root: Path,
    session_id: str,
    prompt_text: str,
    model: str = "sonnet",
    timeout: int = 300,
    max_turns: int = 50,
    allowed_tools: list[str] | None = None,
) -> str:
    """Resume an existing Claude Code session with a follow-up message.
    The agent retains full memory of its previous work."""
    model_id = MODEL_MAP.get(model, model)

    cmd = [
        "npx", "@anthropic-ai/claude-code",
        "--print",
        "--resume", session_id,
        "--model", model_id,
        "--max-turns", str(max_turns),
    ]

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

    try:
        return _run_claude_process(cmd, prompt_text, project_root, timeout)
    except SessionTimeout as e:
        raise SessionTimeout(str(e), session_id=session_id) from None
    except SessionError as e:
        raise SessionError(str(e), session_id=session_id) from None


# ---------------------------------------------------------------------------
# Workspace management
# ---------------------------------------------------------------------------

def create_workspace(project_root: Path, gen: int, agent_type: str, instance: int) -> Path:
    gen_str = f"gen{gen:03d}"
    ws_name = f"{gen_str}_{agent_type}_{instance}"
    ws_path = project_root / "workspace" / ws_name
    output_path = ws_path / "output"
    output_path.mkdir(parents=True, exist_ok=True)

    prompt_src = project_root / "agents" / f"{agent_type}.md"
    if prompt_src.exists():
        shutil.copy2(prompt_src, ws_path / "prompt.md")

    brief_src = project_root / "briefs" / gen_str / f"{agent_type}_{instance}.md"
    if brief_src.exists():
        shutil.copy2(brief_src, ws_path / "brief.md")

    if agent_type == "experimentator":
        (output_path / "sandbox").mkdir(exist_ok=True)
        (output_path / "helpers").mkdir(exist_ok=True)

    return ws_path


def create_analysis_workspace(project_root: Path, gen: int, agent_type: str) -> Path:
    gen_str = f"gen{gen:03d}"
    ws_name = f"{gen_str}_{agent_type}"
    ws_path = project_root / "workspace" / ws_name
    output_path = ws_path / "output"
    output_path.mkdir(parents=True, exist_ok=True)

    prompt_src = project_root / "agents" / f"{agent_type}.md"
    if prompt_src.exists():
        shutil.copy2(prompt_src, ws_path / "prompt.md")

    return ws_path


def cleanup_workspace(project_root: Path, gen: int, agent_type: str, instance: int | None = None):
    gen_str = f"gen{gen:03d}"
    if instance is not None:
        ws_name = f"{gen_str}_{agent_type}_{instance}"
    else:
        ws_name = f"{gen_str}_{agent_type}"
    ws_path = project_root / "workspace" / ws_name
    if ws_path.exists():
        shutil.rmtree(ws_path)


# ---------------------------------------------------------------------------
# File movement
# ---------------------------------------------------------------------------

def move_agent_outputs(project_root: Path, gen: int, agent_type: str, instance: int):
    """Move solution-producing agent outputs to population/ and reports/."""
    gen_str = f"gen{gen:03d}"
    ws_output = project_root / "workspace" / f"{gen_str}_{agent_type}_{instance}" / "output"
    if not ws_output.exists():
        return

    pop_dest = project_root / "population" / gen_str / f"{agent_type}_{instance}"
    pop_dest.mkdir(parents=True, exist_ok=True)
    reports_dir = project_root / "reports" / gen_str
    reports_dir.mkdir(parents=True, exist_ok=True)

    for f in ws_output.iterdir():
        if f.name == "sandbox":
            continue
        if f.name == "report.md":
            shutil.copy2(f, reports_dir / f"{agent_type}_{instance}.md")
        elif f.name == "experiment_requests.md":
            # Collect experiment requests for Architect
            req_dir = project_root / "feedback" / "experiment_requests" / gen_str
            req_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, req_dir / f"{agent_type}_{instance}.md")
        elif f.is_file():
            # Solutions, observations, score files go to population
            shutil.copy2(f, pop_dest / f.name)
        elif f.is_dir():
            target = pop_dest / f.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(f, target)


def move_research_outputs(project_root: Path, gen: int, instance: int):
    """Move research agent outputs to knowledge/research/ and reports/."""
    gen_str = f"gen{gen:03d}"
    ws_output = project_root / "workspace" / f"{gen_str}_research_{instance}" / "output"
    if not ws_output.exists():
        return

    dest = project_root / "knowledge" / "research" / gen_str / f"research_{instance}"
    dest.mkdir(parents=True, exist_ok=True)

    for f in ws_output.iterdir():
        if f.name == "report.md":
            reports_dir = project_root / "reports" / gen_str
            reports_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, reports_dir / f"research_{instance}.md")
        elif f.is_file():
            shutil.copy2(f, dest / f.name)

    # Also copy solutions and findings to population/ so rankings and dashboard see them
    pop_dest = project_root / "population" / gen_str / f"research_{instance}"
    pop_dest.mkdir(parents=True, exist_ok=True)
    for f in ws_output.iterdir():
        if f.name == "report.md":
            continue  # Already moved to reports/
        if f.is_file() and (f.suffix in (".py", ".score", ".md")):
            shutil.copy2(f, pop_dest / f.name)


def _validate_helper(filepath: Path) -> tuple[bool, str]:
    """Validate a helper file is safe for shared use by all agents.

    Checks: valid Python syntax, no blocked imports, no top-level side effects.
    Returns (ok, reason).
    """
    content = filepath.read_text()

    # 1. Syntax check
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    # 2. Import blocklist
    BLOCKED_MODULES = {
        "subprocess", "shutil", "sys", "socket", "http",
        "requests", "urllib", "ctypes", "multiprocessing",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in BLOCKED_MODULES:
                    return False, f"Blocked import: {mod}"
                if mod == "os" and alias.name != "os.path":
                    return False, f"Blocked import: {alias.name} (only os.path allowed)"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                if mod in BLOCKED_MODULES:
                    return False, f"Blocked import from: {mod}"
                if mod == "os" and node.module != "os.path":
                    return False, f"Blocked import from: {node.module}"

    # 3. No top-level side effects (only defs, imports, assignments, docstrings)
    ALLOWED_TOP = (
        ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
        ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign,
        ast.Constant, ast.Pass,
    )
    for node in tree.body:
        if not isinstance(node, ALLOWED_TOP):
            # Allow Expr nodes that are just string constants (docstrings)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                continue
            return False, f"Top-level side effect: {type(node).__name__} at line {node.lineno}"

    return True, "ok"


def move_experiment_outputs(project_root: Path, gen: int, instance: int):
    """Move experimentator outputs to knowledge/experiments/ and reports/."""
    gen_str = f"gen{gen:03d}"
    ws_output = project_root / "workspace" / f"{gen_str}_experimentator_{instance}" / "output"
    if not ws_output.exists():
        return

    dest = project_root / "knowledge" / "experiments" / gen_str / f"experimentator_{instance}"
    dest.mkdir(parents=True, exist_ok=True)

    for f in ws_output.iterdir():
        if f.name == "report.md":
            reports_dir = project_root / "reports" / gen_str
            reports_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, reports_dir / f"experimentator_{instance}.md")
        elif f.is_dir() and f.name == "helpers":
            # Validate and deploy helper tools to problem/helpers/
            helpers_dest = project_root / "problem" / "helpers"
            helpers_dest.mkdir(parents=True, exist_ok=True)
            for hf in f.iterdir():
                if hf.suffix == ".py" and hf.name != "__init__.py":
                    ok, reason = _validate_helper(hf)
                    if ok:
                        shutil.copy2(hf, helpers_dest / hf.name)
                        print(f"    Deployed helper: {hf.name}")
                    else:
                        print(f"    REJECTED helper {hf.name}: {reason}")
            # Also copy helpers dir to experiment archive for reference
            target = dest / f.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(f, target)
        elif f.is_file():
            shutil.copy2(f, dest / f.name)
        elif f.is_dir():
            target = dest / f.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(f, target)


def move_evaluator_outputs(project_root: Path, gen: int):
    gen_str = f"gen{gen:03d}"
    ws_output = project_root / "workspace" / f"{gen_str}_evaluator" / "output"
    if not ws_output.exists():
        return

    for subdir in ["new_ideas", "updated_ideas"]:
        src = ws_output / subdir
        if src.exists():
            for f in src.iterdir():
                lifecycle = _read_frontmatter_field(f, "lifecycle", "active")
                dest_dir = project_root / "knowledge" / "ideas" / lifecycle
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest_dir / f.name)
                _remove_from_other_lifecycles(
                    project_root / "knowledge" / "ideas", f.name, lifecycle, _IDEA_LIFECYCLES
                )

    src = ws_output / "new_patterns"
    if src.exists():
        for f in src.iterdir():
            lifecycle = _read_frontmatter_field(f, "lifecycle", "active")
            dest_dir = project_root / "knowledge" / "patterns" / lifecycle
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_dir / f.name)
            _remove_from_other_lifecycles(
                project_root / "knowledge" / "patterns", f.name, lifecycle, _PATTERN_LIFECYCLES
            )

    # SCALE-6: When clusters are updated, fix orphaned idea back-references
    src = ws_output / "updated_clusters"
    if src.exists():
        clusters_dir = project_root / "knowledge" / "clusters"
        clusters_dir.mkdir(parents=True, exist_ok=True)
        old_cluster_names = {f.stem for f in clusters_dir.glob("*.md")}
        for f in src.iterdir():
            shutil.copy2(f, clusters_dir / f.name)
        new_cluster_names = {f.stem for f in (project_root / "knowledge" / "clusters").glob("*.md")}
        removed_clusters = old_cluster_names - new_cluster_names
        if removed_clusters:
            _fix_orphaned_cluster_refs(project_root, removed_clusters)

    for fname in ["solution_idea_map.md", "coverage_matrix.md"]:
        src = ws_output / fname
        if src.exists():
            shutil.copy2(src, project_root / "history" / fname)

    src = ws_output / "generation_snapshot.md"
    if src.exists():
        gen_dir = project_root / "history" / "generations"
        gen_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, gen_dir / f"{gen_str}.md")

    src = ws_output / "evaluator_report.md"
    if src.exists():
        dest = project_root / "reports" / gen_str
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / "evaluator.md")

    src = ws_output / "agent_gaps.md"
    if src.exists():
        dest = project_root / "feedback" / "agent_gaps"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / f"{gen_str}.md")

    # Gen-1 bootstrap: evaluator writes initial State of Affairs
    src = ws_output / "state_of_affairs.md"
    if src.exists():
        shutil.copy2(src, project_root / "knowledge" / "state_of_affairs.md")

    # Debrief report
    src = ws_output / "report.md"
    if src.exists():
        dest = project_root / "reports" / gen_str
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / "evaluator_debrief.md")


def move_critic_outputs(project_root: Path, gen: int):
    gen_str = f"gen{gen:03d}"
    ws_output = project_root / "workspace" / f"{gen_str}_system_critic" / "output"
    if not ws_output.exists():
        return

    src = ws_output / "system_analysis.md"
    if src.exists():
        dest = project_root / "feedback" / "system_analysis"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / f"{gen_str}.md")

    src = ws_output / "system_recommendations.md"
    if src.exists():
        # SCALE-3: Archive previous version before overwriting
        current = project_root / "feedback" / "system_recommendations.md"
        if current.exists():
            archive_dir = project_root / "feedback" / "system_recommendations_archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            # Archive with previous gen's name (the file being archived is from before this gen)
            prev_gen_str = f"gen{gen - 1:03d}" if gen > 1 else "gen000"
            shutil.copy2(current, archive_dir / f"{prev_gen_str}.md")
        shutil.copy2(src, current)

    src = ws_output / "experiment_suggestions.md"
    if src.exists():
        dest = project_root / "feedback" / "experiment_suggestions"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / f"{gen_str}.md")

    src = ws_output / "report.md"
    if src.exists():
        dest = project_root / "reports" / gen_str
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / "system_critic_debrief.md")


def move_consistency_outputs(project_root: Path, gen: int):
    gen_str = f"gen{gen:03d}"
    ws_output = project_root / "workspace" / f"{gen_str}_consistency_reviewer" / "output"
    if not ws_output.exists():
        return

    src = ws_output / "state_of_affairs.md"
    if src.exists():
        shutil.copy2(src, project_root / "knowledge" / "state_of_affairs.md")

    src = ws_output / "updated_ideas"
    if src.exists():
        for f in src.iterdir():
            lifecycle = _read_frontmatter_field(f, "lifecycle", "active")
            dest_dir = project_root / "knowledge" / "ideas" / lifecycle
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_dir / f.name)
            _remove_from_other_lifecycles(
                project_root / "knowledge" / "ideas", f.name, lifecycle, _IDEA_LIFECYCLES
            )

    src = ws_output / "updated_clusters"
    if src.exists():
        clusters_dir = project_root / "knowledge" / "clusters"
        clusters_dir.mkdir(parents=True, exist_ok=True)
        old_cluster_names = {f.stem for f in clusters_dir.glob("*.md")}
        for f in src.iterdir():
            shutil.copy2(f, clusters_dir / f.name)
        new_cluster_names = {f.stem for f in (project_root / "knowledge" / "clusters").glob("*.md")}
        removed_clusters = old_cluster_names - new_cluster_names
        if removed_clusters:
            _fix_orphaned_cluster_refs(project_root, removed_clusters)

    src = ws_output / "consistency_review.md"
    if src.exists():
        dest = project_root / "feedback" / "consistency_reviews"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / f"{gen_str}.md")


_IDEA_LIFECYCLES = ["active", "established", "disputed", "debunked", "archived"]
_PATTERN_LIFECYCLES = ["active", "confirmed"]


def _remove_from_other_lifecycles(
    base_dir: Path, filename: str, current_lifecycle: str, lifecycles: list[str]
):
    """Remove copies of a file from all lifecycle dirs except the current one (BUG-1 fix)."""
    for lc in lifecycles:
        if lc == current_lifecycle:
            continue
        old = base_dir / lc / filename
        if old.exists():
            old.unlink()


def _fix_orphaned_cluster_refs(project_root: Path, removed_clusters: set[str]):
    """SCALE-6: When clusters are removed/merged, clear orphaned idea cluster refs."""
    ideas_dir = project_root / "knowledge" / "ideas"
    if not ideas_dir.exists():
        return
    for lc_dir in ideas_dir.iterdir():
        if not lc_dir.is_dir():
            continue
        for idea_file in lc_dir.glob("*.md"):
            cluster_val = _read_frontmatter_field(idea_file, "cluster", "")
            if cluster_val in removed_clusters:
                try:
                    text = idea_file.read_text()
                    if text.startswith("---"):
                        end = text.index("---", 3)
                        frontmatter = text[: end + 3]
                        body = text[end + 3 :]
                        # Use regex to replace only the cluster field value
                        frontmatter = re.sub(
                            r'^(cluster:\s*).*$',
                            r'\1unclustered',
                            frontmatter,
                            count=1,
                            flags=re.MULTILINE,
                        )
                        idea_file.write_text(frontmatter + body)
                except Exception:
                    pass


def _read_frontmatter_field(filepath: Path, field: str, default: str = "") -> str:
    try:
        text = filepath.read_text()
        if not text.startswith("---"):
            return default
        end = text.index("---", 3)
        fm = yaml.safe_load(text[3:end])
        if not fm:
            return default
        val = fm.get(field)
        # Fallback: if looking for "lifecycle", also accept "status" (template compat)
        if val is None and field == "lifecycle":
            val = fm.get("status")
        return val if val is not None else default
    except Exception:
        return default


def log_agent_failure(project_root: Path, gen: int, agent_type: str, instance: int, error: str):
    """Log agent failure so the next generation's Architect knows about it."""
    gen_str = f"gen{gen:03d}"
    reports_dir = project_root / "reports" / gen_str
    reports_dir.mkdir(parents=True, exist_ok=True)
    failure_path = reports_dir / f"{agent_type}_{instance}.md"
    failure_path.write_text(
        f"# Agent Failure Report\n\n"
        f"Agent {agent_type}_{instance} failed in generation {gen}.\n\n"
        f"## Error\n```\n{error}\n```\n\n"
        f"## Impact\nNo solutions or observations were produced by this agent.\n"
    )


# ---------------------------------------------------------------------------
# Score tracking
# ---------------------------------------------------------------------------

def update_rankings(project_root: Path, gen: int):
    population = project_root / "population"
    higher_better = fitness_is_higher_better(project_root)

    # SCALE-2: Load cached scores, only scan new generation
    scores_cache_path = project_root / "history" / "all_scores.json"
    cached: list[tuple[float, str]] = []
    if scores_cache_path.exists():
        try:
            cached = json.loads(scores_cache_path.read_text())
        except Exception:
            cached = []

    # Scan only the current generation's population dir
    gen_str = f"gen{gen:03d}"
    gen_dir = population / gen_str
    metric_name, primary_spec = primary_metric(project_root)
    sentinel = primary_spec.get("sentinel_value", 1e9 if not higher_better else -1e9)
    new_entries: list[tuple[float, str]] = []
    if gen_dir.exists():
        for agent_dir in gen_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            for sol in agent_dir.glob("sol*.py"):
                score = _extract_score(sol, metric_name)
                if score is not None:
                    # Filter invalid/sentinel/non-finite scores
                    if not math.isfinite(score):
                        continue
                    if higher_better and score <= 0:
                        continue
                    if not higher_better and score >= sentinel * 0.9:
                        continue
                    new_entries.append((score, str(sol)))

    # Merge: filter out stale entries from cache (files that no longer exist)
    all_scores_str = cached + new_entries
    all_scores: list[tuple[float, Path]] = []
    valid_cache: list[tuple[float, str]] = []
    for score, path_str in all_scores_str:
        p = Path(path_str)
        if p.exists():
            all_scores.append((score, p))
            valid_cache.append((score, path_str))

    # Save updated cache (with file locking for crash-resume safety)
    scores_cache_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = scores_cache_path.parent / "all_scores.json.lock"
    try:
        with open(lock_path, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            scores_cache_path.write_text(json.dumps(valid_cache))
            fcntl.flock(lock, fcntl.LOCK_UN)
    except Exception:
        scores_cache_path.write_text(json.dumps(valid_cache))

    # Find best score based on direction
    if not all_scores:
        best_score = 0.0
        best_path = None
    else:
        best_score = all_scores[0][0]  # Will be overwritten
        best_path = all_scores[0][1]
        if higher_better:
            best_score = max(s for s, _ in all_scores)
            best_path = next(p for s, p in all_scores if s == best_score)
        else:
            best_score = min(s for s, _ in all_scores)
            best_path = next(p for s, p in all_scores if s == best_score)

    best_link = population / "best.py"
    if best_path:
        if best_link.exists() or best_link.is_symlink():
            best_link.unlink()
        best_link.symlink_to(best_path.relative_to(population))

    top_dir = population / "top"
    if top_dir.exists():
        shutil.rmtree(top_dir)
    top_dir.mkdir()

    fmt = _score_fmt(project_root)
    all_scores.sort(key=lambda x: x[0], reverse=higher_better)
    for i, (score, path) in enumerate(all_scores[:10], 1):
        link = top_dir / f"rank{i:02d}_{format(score, fmt)}.py"
        link.symlink_to(path.relative_to(population))

    _update_score_progression(project_root, gen, best_score)
    _update_population_summary(project_root, all_scores)

    return best_score


def _extract_score(sol_path: Path, metric_name: str = "fitness") -> float | None:
    """Extract the primary metric score for a solution.

    Priority: .score sidecar → eval cache (by content hash) → header comment.
    The eval cache is written by evaluate.py and is the authoritative source.
    """
    # 1. .score sidecar file (written by agents alongside solutions)
    score_file = sol_path.with_suffix(".score")
    if score_file.exists():
        try:
            data = json.loads(score_file.read_text())
            if isinstance(data, dict) and metric_name in data:
                return float(data[metric_name])
        except Exception:
            pass

    # 2. Eval cache — keyed by file content hash, written by evaluate.py
    try:
        content_hash = hashlib.sha256(sol_path.read_bytes()).hexdigest()
        cache_path = sol_path.parents[3] / "history" / "eval_cache.json"  # population/genNNN/agent/sol.py → project_root
        if not cache_path.exists():
            # Try from project root directly
            for parent in sol_path.parents:
                candidate = parent / "history" / "eval_cache.json"
                if candidate.exists():
                    cache_path = candidate
                    break
        if cache_path.exists():
            cache_lock = cache_path.with_suffix(".lock")
            with open(cache_lock, "w") as lock:
                fcntl.flock(lock, fcntl.LOCK_SH)
                cache = json.loads(cache_path.read_text())
                fcntl.flock(lock, fcntl.LOCK_UN)
            if content_hash in cache:
                cached_result = cache[content_hash]
                if isinstance(cached_result, dict) and metric_name in cached_result:
                    return float(cached_result[metric_name])
    except Exception:
        pass

    # 3. Header comment fallback (# fitness: 1.234)
    try:
        text = sol_path.read_text()
        for line in text.split("\n")[:10]:
            for key in [metric_name, "fitness", "score"]:
                if f"{key}:" in line.lower():
                    parts = line.split(":")
                    for part in parts[1:]:
                        try:
                            return float(part.strip().split()[0])
                        except (ValueError, IndexError):
                            continue
    except Exception:
        pass
    return None


def _update_score_progression(project_root: Path, gen: int, best_score: float):
    prog_path = project_root / "history" / "score_progression.md"
    name, spec = primary_metric(project_root)
    fmt = _score_fmt(project_root)
    sig_change = spec.get("significant_change", 0)
    higher_better = spec.get("higher_is_better", True)

    # Don't write meaningless scores (no solutions yet)
    if best_score == 0.0 or not math.isfinite(best_score):
        score_str = "--"
        delta_str = ""
    else:
        score_str = format(best_score, fmt)
        # Compute delta from previous gen's best
        delta_str = ""
        if prog_path.exists():
            text = prog_path.read_text()
            lines_existing = text.strip().split("\n")
            for prev_line in reversed(lines_existing):
                if prev_line.startswith("|") and "--" not in prev_line.split("|")[1]:
                    parts = [p.strip() for p in prev_line.split("|") if p.strip()]
                    if len(parts) >= 2:
                        try:
                            prev_score = float(parts[1])
                            delta = best_score - prev_score
                            if abs(delta) < sig_change:
                                delta_str = " ~"
                            elif (higher_better and delta > 0) or (not higher_better and delta < 0):
                                delta_str = f" (+{abs(delta):{fmt}})" if higher_better else f" (-{abs(delta):{fmt}})"
                            elif delta != 0:
                                delta_str = f" ({'+' if delta > 0 else ''}{delta:{fmt}})"
                        except ValueError:
                            pass
                    break

    line = f"| {gen:3d} | {score_str}{delta_str} |\n"

    if not prog_path.exists():
        prog_path.parent.mkdir(parents=True, exist_ok=True)
        prog_path.write_text(
            "# Score Progression\n\n"
            f"| Gen | Best {name} |\n"
            "|-----|-------------|\n"
            + line
        )
    else:
        with open(prog_path, "a") as f:
            f.write(line)


def _update_population_summary(project_root: Path, all_scores: list[tuple[float, Path]]):
    if not all_scores:
        return

    higher_better = fitness_is_higher_better(project_root)
    name, _ = primary_metric(project_root)
    fmt = _score_fmt(project_root)
    summary_path = project_root / "population" / "summary.md"
    total = len(all_scores)
    scores = [s for s, _ in all_scores]
    best = max(scores) if higher_better else min(scores)
    avg = sum(scores) / total
    # Count valid solutions by checking is_valid in .score files
    valid = 0
    for _, path in all_scores:
        score_file = path.with_suffix(".score")
        if score_file.exists():
            try:
                data = json.loads(score_file.read_text())
                if data.get("is_valid", 0):
                    valid += 1
                    continue
            except Exception:
                pass
        valid += 1  # If no .score file, assume valid (it passed sentinel filter)
    direction = "higher" if higher_better else "lower"

    by_agent: dict[str, list[tuple[float, str]]] = {}
    for score, path in all_scores:
        agent_dir = path.parent.name
        agent_type = agent_dir.rsplit("_", 1)[0]
        gen_name = path.parent.parent.name
        by_agent.setdefault(agent_type, []).append((score, f"{gen_name}/{agent_dir}/{path.name}"))

    lines = [
        "# Population Summary\n",
        f"Total solutions: {total}",
        f"Valid solutions: {valid}",
        f"Best {name}: {format(best, fmt)} ({direction} is better)",
        f"Average {name}: {format(avg, fmt)}\n",
        "## By Agent Type\n",
    ]

    for atype in sorted(by_agent):
        entries = by_agent[atype]
        type_scores = [s for s, _ in entries]
        best_type = max(type_scores) if higher_better else min(type_scores)
        lines.append(f"### {atype}")
        lines.append(f"- Count: {len(entries)}")
        lines.append(f"- Best: {format(best_type, fmt)}")
        lines.append(f"- Avg: {format(sum(type_scores)/len(type_scores), fmt)}")
        entries.sort(key=lambda x: x[0], reverse=higher_better)
        for score, path in entries[:3]:
            lines.append(f"  - {path}: {name} {format(score, fmt)}")
        lines.append("")

    summary_path.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# User intervention detection
# ---------------------------------------------------------------------------

def detect_interventions(project_root: Path, gen: int):
    prev_gen = gen - 1
    if prev_gen < 1:
        return

    prev_snapshot = project_root / "history" / "generations" / f"gen{prev_gen:03d}.md"
    if not prev_snapshot.exists():
        return

    ref_time = prev_snapshot.stat().st_mtime
    interventions = []

    for dirpath in [
        project_root / "knowledge",
        project_root / "user",
        project_root / "agents",
    ]:
        if not dirpath.exists():
            continue
        for f in dirpath.rglob("*"):
            if f.is_file() and f.stat().st_mtime > ref_time:
                interventions.append(str(f.relative_to(project_root)))

    if interventions:
        log_path = project_root / "user" / "interventions.md"
        with open(log_path, "a") as f:
            f.write(f"\n## Generation {gen}\n")
            f.write(f"Files modified since gen {prev_gen}:\n")
            for path in interventions:
                f.write(f"- {path}\n")


# ---------------------------------------------------------------------------
# Initial knowledge bootstrap
# ---------------------------------------------------------------------------

def bootstrap_initial_knowledge(project_root: Path):
    print("  Bootstrapping initial knowledge...")

    facts_src = project_root / "user" / "initial_facts.md"
    if facts_src.exists():
        _bootstrap_facts(project_root, facts_src)

    ideas_src = project_root / "user" / "initial_ideas.md"
    if ideas_src.exists():
        _bootstrap_ideas(project_root, ideas_src)

    soa_path = project_root / "knowledge" / "state_of_affairs.md"
    if not soa_path.exists():
        soa_path.write_text(
            "---\n"
            "generation: 0\n"
            "best_score: 0\n"
            "trajectory: starting\n"
            "last_updated_gen: 0\n"
            "---\n\n"
            "# State of Affairs — Pre-Generation\n\n"
            "## Current Standing\n"
            "No generations have run yet. Initial knowledge has been seeded from user-provided facts and ideas.\n\n"
            "## What Works\n"
            "Unknown — no solutions have been evaluated yet.\n\n"
            "## Coverage Map\n"
            "Nothing has been explored yet. See initial ideas in knowledge/ideas/active/ for starting directions.\n\n"
            "## Open Questions\n"
            "Everything is open. The first generation should explore diverse approaches.\n"
        )

    print("  Bootstrap complete.")


def _bootstrap_facts(project_root: Path, facts_src: Path):
    text = facts_src.read_text()
    facts_dir = project_root / "knowledge" / "facts"
    facts_dir.mkdir(parents=True, exist_ok=True)

    current_id = None
    current_title = ""
    current_body = []

    for line in text.split("\n"):
        if line.startswith("## fact_"):
            if current_id:
                _write_fact_file(facts_dir, current_id, current_title, "\n".join(current_body).strip())
            parts = line[3:].split(":", 1)
            current_id = parts[0].strip()
            current_title = parts[1].strip() if len(parts) > 1 else current_id
            current_body = []
        elif current_id:
            current_body.append(line)

    if current_id:
        _write_fact_file(facts_dir, current_id, current_title, "\n".join(current_body).strip())


def _write_fact_file(facts_dir: Path, fact_id: str, title: str, body: str):
    filepath = facts_dir / f"{fact_id}.md"
    if filepath.exists():
        return
    filepath.write_text(
        f"---\n"
        f"id: {fact_id}\n"
        f"type: fact\n"
        f"name: \"{title}\"\n"
        f"confidence: 0.8\n"
        f"first_seen: generation_0\n"
        f"verified: false\n"
        f"source: user-provided\n"
        f"tags: []\n"
        f"---\n\n"
        f"{body}\n"
    )


def _bootstrap_ideas(project_root: Path, ideas_src: Path):
    text = ideas_src.read_text()
    ideas_dir = project_root / "knowledge" / "ideas" / "active"
    ideas_dir.mkdir(parents=True, exist_ok=True)

    current_id = None
    current_title = ""
    current_body = []

    for line in text.split("\n"):
        if line.startswith("## idea_"):
            if current_id:
                _write_idea_file(ideas_dir, current_id, current_title, "\n".join(current_body).strip())
            parts = line[3:].split(":", 1)
            current_id = parts[0].strip()
            current_title = parts[1].strip() if len(parts) > 1 else current_id
            current_body = []
        elif current_id:
            current_body.append(line)

    if current_id:
        _write_idea_file(ideas_dir, current_id, current_title, "\n".join(current_body).strip())


def _write_idea_file(ideas_dir: Path, idea_id: str, title: str, body: str):
    filepath = ideas_dir / f"{idea_id}.md"
    if filepath.exists():
        return
    filepath.write_text(
        f"---\n"
        f"id: {idea_id}\n"
        f"type: idea\n"
        f"name: \"{title}\"\n"
        f"lifecycle: active\n"
        f"confidence: 0.3\n"
        f"first_seen: generation_0\n"
        f"last_updated: generation_0\n"
        f"last_confirmed_gen: 0\n"
        f"supported_by: []\n"
        f"contradicted_by: []\n"
        f"related_ideas: []\n"
        f"cluster: null\n"
        f"tags: []\n"
        f"---\n\n"
        f"{body}\n"
    )


# ---------------------------------------------------------------------------
# Prompt builders — LEAN: point to files, don't inject content
# ---------------------------------------------------------------------------

def _load_prompt(project_root: Path, name: str) -> str:
    """Load a prompt template from prompts/ directory."""
    path = project_root / "prompts" / f"{name}.md"
    return path.read_text()


def DEBRIEF_INSTRUCTIONS(project_root: Path) -> str:
    return _load_prompt(project_root, "debrief_instructions")


def ANALYSIS_DEBRIEF_PROMPT(project_root: Path) -> str:
    return _load_prompt(project_root, "analysis_debrief")


def DEBRIEF_RECOVERY_PROMPT(project_root: Path) -> str:
    return _load_prompt(project_root, "debrief_recovery")


def build_architect_prompt(project_root: Path, gen: int, config: dict) -> str:
    gen_str = f"gen{gen:03d}"
    prev_gen_str = f"gen{gen-1:03d}" if gen > 1 else None
    prompt_template = _read_file(project_root / "agents" / "architect.md")
    briefs_dir = project_root / "briefs" / gen_str
    agent_config = yaml.dump(config.get("agents", {}), default_flow_style=False)

    # Collect recent experiment request paths (last 2 generations only to avoid bloat)
    exp_req_section = ""
    exp_req_dir = project_root / "feedback" / "experiment_requests"
    if exp_req_dir.exists():
        recent_gens = {f"gen{g:03d}" for g in range(max(1, gen - 2), gen)}
        req_files = []
        for gen_dir in sorted(exp_req_dir.iterdir()):
            if gen_dir.is_dir() and gen_dir.name in recent_gens:
                req_files.extend(sorted(gen_dir.glob("*.md")))
        if req_files:
            exp_req_section = "## Experiment Requests from Agents (last 2 gens)\n"
            for rf in req_files:
                exp_req_section += f"- `{rf}`\n"

    return f"""{prompt_template}

---

# CONTEXT FOR GENERATION {gen}

## Files to Read (in order of priority)

1. `{project_root}/problem/description.md` — Problem definition
2. `{project_root}/problem/constraints.md` — Hard/soft constraints
3. `{project_root}/knowledge/state_of_affairs.md` — Layer 0 strategic overview
4. `{project_root}/knowledge/clusters/` — ALL cluster files (Layer 1)
5. `{project_root}/knowledge/facts/` — ALL fact files
6. `{project_root}/history/score_progression.md` — Score history
7. `{project_root}/population/summary.md` — Population stats
8. `{project_root}/history/coverage_matrix.md` — Which idea combos tried
9. `{project_root}/history/solution_idea_map.md` — Solution-idea associations
{f"10. `{briefs_dir}/prev_gen_reports.md` — **PRE-CONCATENATED** reports from gen {gen-1} (read this instead of individual files)" if prev_gen_str else ""}
11. `{project_root}/feedback/system_recommendations.md` — System critic recommendations
12. `{project_root}/feedback/experiment_suggestions/` — Latest experiment suggestions
13. `{project_root}/feedback/consistency_reviews/` — Latest consistency review
14. `{project_root}/user/interventions.md` — User edits between generations

{exp_req_section}

## Agent Configuration
```yaml
{agent_config}
```
max_parallel_sessions: {config.get('max_parallel_sessions', 10)}
default_model: {config.get('default_model', 'sonnet')}

## Timing Data

You can set a `timeout` field (in seconds) per agent in `manifest.yaml`. When an agent exceeds
its timeout, a **wrap-up session** is launched to finish the work (same model, {get_timeout(config, 'wrap_up')}s).
If that also fails, a lightweight debrief recovery writes a report. Use timing data from previous
generations to set appropriate timeouts. Default work timeout: {get_timeout(config, 'agent_default')}s.

Previous generation timing:
```json
{json.dumps(_get_recent_timing(project_root, gen), indent=2)}
```

## Output

Write ALL files to: `{briefs_dir}/`

1. `{briefs_dir}/manifest.yaml` — execution plan
2. `{briefs_dir}/{{type}}_{{instance}}.md` — one brief per agent instance
3. `{briefs_dir}/manifest_reasoning.md` — strategic reasoning

Brief paths in manifest.yaml MUST be relative to project root: `briefs/{gen_str}/explore_1.md`
"""


def build_agent_prompt(
    project_root: Path, gen: int, agent_type: str, instance: int, brief_path: str
) -> str:
    """Build lean prompt for a work-session agent."""
    gen_str = f"gen{gen:03d}"
    prompt_template = _read_file(project_root / "agents" / f"{agent_type}.md")
    brief = _read_file(project_root / Path(brief_path))
    ws_path = project_root / "workspace" / f"{gen_str}_{agent_type}_{instance}"
    report_path = f"{ws_path}/output/report.md"
    debrief = DEBRIEF_INSTRUCTIONS(project_root).format(report_path=report_path)

    return f"""{prompt_template}

---

# CONTEXT

You are **{agent_type}** instance {instance} for generation {gen}.
Project root: `{project_root}`
Output directory: `{ws_path}/output/`

## Your Brief
{brief}

## Files to Read

Your brief's "Read first" section lists specific files. In addition, always read:

1. `{project_root}/problem/description.md` — Problem definition (READ THIS FIRST)
2. `{project_root}/problem/constraints.md` — Constraints
3. `{project_root}/knowledge/state_of_affairs.md` — Strategic overview (Layer 0)
4. `{project_root}/knowledge/facts/` — All fact files (global context)
5. `{project_root}/knowledge/ideas/active/` — Current active ideas
6. `{project_root}/knowledge/clusters/` — Topic cluster summaries (read ones relevant to your task)
{f"7. `{project_root}/population/best.py` — Current best solution" if gen > 1 else ""}
{"8" if gen > 1 else "7"}. `{project_root}/problem/initial_programs/` — Example/baseline programs

For deeper context, you can read any file in the project. The knowledge hierarchy is:
- Layer 0: `knowledge/state_of_affairs.md` (read always)
- Layer 1: `knowledge/clusters/*.md` (read relevant ones)
- Layer 2: `knowledge/ideas/`, `knowledge/patterns/` (drill in when needed)

**Paper library:** `{project_root}/papers/summaries/` contains structured summaries of
relevant academic papers (downloaded by research agents). Check if any exist before solving.
{_helpers_section(project_root)}
## Evaluation

```bash
python3 {project_root}/problem/evaluate.py {ws_path}/output/sol01.py
```
Output: JSON with at minimum `{{"fitness": <value>, "is_valid": 1}}`
If time tracking is enabled: also includes `"eval_time_s"` (wall-clock seconds for evaluation).
{_fitness_description(project_root)}

## MANDATORY WORKFLOW: Evaluate Every Solution Immediately

**NEVER write multiple solutions before evaluating them. The cycle for EACH solution is:**
1. Write `sol01.py`
2. Run `python3 {project_root}/problem/evaluate.py {ws_path}/output/sol01.py`
3. Update the `# fitness:` header with the REAL score from evaluate.py
4. Save the eval JSON output to `{ws_path}/output/sol01.score`
5. ONLY THEN move on to `sol02.py`

A solution with `# fitness: 0.0` or `# fitness: TBD` is WORTHLESS. If you run out of time
with 1 evaluated solution, that is far more valuable than 5 unevaluated ones.

## Output Format

- Solutions: `{ws_path}/output/sol01.py`, `sol02.py`, etc.
  - Must implement `def entrypoint()`
  - Header comment: `# fitness: <value>` (REAL score, not placeholder)
  - Save eval JSON: write to `{ws_path}/output/sol01.score`
- Observations: `{ws_path}/output/observations.md`
- Debrief report: `{ws_path}/output/report.md` (REQUIRED — see below)
{debrief}
"""


def build_evaluator_prompt(project_root: Path, gen: int, config: dict) -> str:
    gen_str = f"gen{gen:03d}"
    prompt_template = _read_file(project_root / "agents" / "evaluator.md")
    ws_path = project_root / "workspace" / f"{gen_str}_evaluator"
    # Evaluator's debrief goes into evaluator_report.md (its main output),
    # not a separate report.md — avoids confusion about which file to write.
    report_path = f"{ws_path}/output/evaluator_report.md"

    # Count current ideas for idea-limit guidance
    idea_count = 0
    ideas_dir = project_root / "knowledge" / "ideas"
    if ideas_dir.exists():
        for ld in ideas_dir.iterdir():
            if ld.is_dir():
                idea_count += len(list(ld.glob("*.md")))

    idea_limits = config.get("idea_limits", {})
    staleness = config.get("staleness_threshold", 5)

    gen1_extra = ""
    if gen == 1:
        gen1_extra = f"""
**GENERATION 1 BOOTSTRAP:** This is the first generation. You MUST also write:
- `output/state_of_affairs.md` — the initial State of Affairs (Layer 0).
  Write a narrative (800-1500 tokens): Current Standing, What Works,
  Coverage Map, Dead Ends, Open Questions.
  Include YAML frontmatter: generation, best_score, trajectory, last_updated_gen.
"""

    debrief = DEBRIEF_INSTRUCTIONS(project_root).format(report_path=report_path)

    return f"""{prompt_template}

---

# CONTEXT FOR GENERATION {gen} EVALUATION

{gen1_extra}

## Files to Read

1. `{project_root}/problem/description.md` — Problem definition
2. `{project_root}/knowledge/state_of_affairs.md` — Current Layer 0
3. `{project_root}/population/{gen_str}/` — ALL submitted solutions this generation (read code + score files)
4. `{project_root}/reports/{gen_str}/` — ALL agent debrief reports this generation
5. `{project_root}/knowledge/clusters/` — Current cluster summaries (Layer 1)
6. `{project_root}/knowledge/ideas/` — All idea files across lifecycles (Layer 2)
7. `{project_root}/knowledge/experiments/{gen_str}/` — Experiment results this generation
8. `{project_root}/history/solution_idea_map.md` — Current solution-idea associations
9. `{project_root}/knowledge/research/{gen_str}/` — Research findings this generation
10. `{ws_path}/knowledge_dump.md` — **PRE-CONCATENATED** knowledge dump (ideas, clusters, patterns in one file — read this FIRST to save turns, then drill into individual files only if needed)

## Idea Limits

Current idea count: {idea_count}
- Under 30 ideas: add if the idea is good
- 30-50 ideas: add only if very good (strong evidence)
- 50-100 ideas: add only if revolutionary (changes the frontier)
- Over 100 ideas: merge or cluster instead of adding

## Experiment Consolidation

Check `knowledge/experiments/` for results older than 3 generations. Extract key findings
from old experiments into new patterns or facts, then note in your report which experiments
have been consolidated so they can be archived.

## Staleness

Ideas not confirmed in {staleness} or more generations should be flagged as stale
in your report. Check `last_confirmed_gen` in each idea's frontmatter.

## Output

Write all output to: `{ws_path}/output/`

1. Collect scores from `.score` files (only run `evaluate.py` if a `.score` file is missing)
2. `output/new_ideas/` — new idea files with YAML frontmatter
3. `output/new_patterns/` — new pattern files with YAML frontmatter
4. `output/updated_ideas/` — updated idea files
5. `output/updated_clusters/` — updated cluster summaries
6. `output/solution_idea_map.md` — updated map
7. `output/coverage_matrix.md` — which idea combos tried (**SCALE-4: cap to top 30 most-used ideas; use sparse format for large matrices**)
8. `output/generation_snapshot.md` — generation summary
9. `output/evaluator_report.md` — include `strategic_shift: true` or `false`
10. `output/agent_gaps.md` — synthesized gaps from agent reports
{"11. `output/state_of_affairs.md` — GENERATION 1 ONLY: initial Layer 0" if gen == 1 else ""}

{debrief}
"""


def build_critic_prompt(project_root: Path, gen: int) -> str:
    gen_str = f"gen{gen:03d}"
    prompt_template = _read_file(project_root / "agents" / "system_critic.md")
    ws_path = project_root / "workspace" / f"{gen_str}_system_critic"
    report_path = f"{ws_path}/output/report.md"
    debrief = DEBRIEF_INSTRUCTIONS(project_root).format(report_path=report_path)

    return f"""{prompt_template}

---

# CONTEXT FOR GENERATION {gen} SYSTEM CRITIQUE

## Files to Read

1. `{project_root}/reports/{gen_str}/` — ALL agent debrief reports this generation
2. `{project_root}/population/{gen_str}/` — Agent observations (observations.md in each agent dir)
3. `{project_root}/feedback/system_recommendations.md` — Current recommendations
4. `{project_root}/feedback/agent_gaps/` — Latest agent gaps synthesis
5. `{project_root}/knowledge/state_of_affairs.md` — Current system understanding

## Output

Write all output to: `{ws_path}/output/`

1. `output/system_analysis.md` — pipeline analysis
2. `output/system_recommendations.md` — updated actionable recommendations for the user
3. `output/experiment_suggestions.md` — recommended experiments for the Experimentator

{debrief}
"""


def build_consistency_prompt(project_root: Path, gen: int, config: dict) -> str:
    gen_str = f"gen{gen:03d}"
    prompt_template = _read_file(project_root / "agents" / "consistency_review.md")
    ws_path = project_root / "workspace" / f"{gen_str}_consistency_reviewer"
    staleness = config.get("staleness_threshold", 5)

    # Find last consistency review generation
    cr_dir = project_root / "feedback" / "consistency_reviews"
    last_review_gen = 0
    if cr_dir.exists():
        reviews = sorted(cr_dir.glob("gen*.md"))
        if reviews:
            try:
                last_review_gen = int(reviews[-1].stem.replace("gen", ""))
            except ValueError:
                pass

    return f"""{prompt_template}

---

# CONTEXT FOR GENERATION {gen} CONSISTENCY REVIEW

Last consistency review was at generation {last_review_gen}.
Staleness threshold: {staleness} generations (flag ideas with last_confirmed_gen + {staleness} <= {gen}).

## Files to Read (ALL of these — this is a full audit)

1. `{project_root}/knowledge/state_of_affairs.md` — Current Layer 0 (you will rewrite this)
2. `{project_root}/knowledge/clusters/` — ALL cluster files (Layer 1, audit each)
3. `{project_root}/knowledge/ideas/` — ALL idea files across all lifecycles (Layer 2, audit each)
4. `{project_root}/knowledge/patterns/` — ALL pattern files (audit each)
5. `{project_root}/knowledge/facts/` — ALL fact files (verify each)
6. `{project_root}/history/coverage_matrix.md` — Structured combo data (use for accuracy)
7. `{project_root}/history/solution_idea_map.md` — Solution-idea associations
8. `{project_root}/reports/` — Reports from last 3 generations (agent doubts = top priority)

## Output

Write all output to: `{ws_path}/output/`

1. `output/state_of_affairs.md` — complete rewrite of Layer 0 (800-1500 tokens)
2. `output/updated_ideas/` — ideas with changed lifecycle/status
3. `output/updated_clusters/` — corrected cluster summaries
4. `output/consistency_review.md` — full audit report
"""


def _helpers_section(project_root: Path) -> str:
    """Generate a prompt section listing available shared helper tools."""
    helpers_dir = project_root / "problem" / "helpers"
    if not helpers_dir.exists():
        return ""
    helper_files = sorted(f for f in helpers_dir.glob("*.py") if f.name != "__init__.py")
    if not helper_files:
        return ""
    lines = ["\n## Shared Helper Tools\n",
             "The following helper tools are available in `problem/helpers/`:\n"]
    for hf in helper_files:
        # Try to extract module docstring
        doc = ""
        try:
            tree = ast.parse(hf.read_text())
            if (tree.body and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str)):
                doc = f" — {tree.body[0].value.value.split(chr(10))[0]}"
        except Exception:
            pass
        lines.append(f"- `{hf}`{doc}")
    lines.append(f"\nImport in solution files: `from helpers.<module> import <function>`")
    lines.append(f"Examples: `from helpers.core import compute_c`  |  `from helpers.sa_calibration import calibrate_sa_temperature`")
    lines.append(f"(`evaluate.py` adds `problem/` to sys.path, so `helpers/` is directly importable)")
    lines.append(f"See `problem/helpers/README.md` for full index and documentation.\n")
    return "\n".join(lines)


def _fitness_description(project_root: Path) -> str:
    """Generate a description of ALL metrics from metrics.yaml for agent prompts."""
    all_specs = load_metrics(project_root)
    config = load_config(project_root)
    target = get_target_score(project_root, config)

    if not all_specs:
        return f"Check problem/description.md for fitness details. Target: {target}"

    lines = []
    for name, spec in all_specs.items():
        if not spec.get("include_in_prompts", True):
            continue
        higher = spec.get("higher_is_better", True)
        direction = "higher is better" if higher else "lower is better"
        desc = spec.get("description", name)
        line = f"- **`{name}`**: {desc} ({direction})"
        if spec.get("is_primary", False):
            cmp = ">=" if higher else "<="
            line += f" — **PRIMARY. Target: {cmp} {target}**"
        bounds = []
        if "lower_bound" in spec:
            bounds.append(f"theoretical best: {spec['lower_bound']}")
        if "upper_bound" in spec:
            bounds.append(f"worst expected: {spec['upper_bound']}")
        if bounds:
            line += f" [{', '.join(bounds)}]"
        lines.append(line)

    return "\n".join(lines)


def _read_file(path: Path) -> str:
    try:
        return path.read_text()
    except (FileNotFoundError, IsADirectoryError):
        return ""


# ---------------------------------------------------------------------------
# Phase execution
# ---------------------------------------------------------------------------

def _absolutize_brief_paths(project_root: Path, briefs_dir: Path):
    """BUG-4: Convert relative paths in briefs to absolute so agents' Read tool works."""
    # Match lines like "- population/best.py" or "1. knowledge/state_of_affairs.md"
    # that look like file references but aren't already absolute
    path_prefixes = (
        "population/", "knowledge/", "problem/", "history/", "reports/",
        "briefs/", "feedback/", "user/", "agents/", "workspace/",
        "papers/", "prompts/", "dashboard/",
    )
    # Only match paths that look like file references:
    # inside backticks, after list markers (- or N.), or at line start
    path_context = r'(?:(?<=`)|(?<=^)|(?<=\s- )|(?<=\d\. ))'
    for brief in briefs_dir.glob("*.md"):
        if brief.name in ("manifest.yaml", "manifest_reasoning.md"):
            continue
        try:
            text = brief.read_text()
            changed = False
            new_lines = []
            for line in text.split("\n"):
                new_line = line
                for prefix in path_prefixes:
                    # Match relative paths in file-reference contexts, not already absolute
                    pattern = rf'(?<![/\w])`?{re.escape(prefix)}'
                    if re.search(pattern, line) and str(project_root) not in line:
                        # Only replace paths inside backticks or after list markers
                        # Inside backticks: `population/...` → `{root}/population/...`
                        bt_pattern = rf'`({re.escape(prefix)})'
                        if re.search(bt_pattern, line):
                            new_line = re.sub(bt_pattern, f'`{project_root}/{prefix}', new_line)
                            changed = True
                        # After list markers: "- population/..." or "1. population/..."
                        list_pattern = rf'((?:^|\s)(?:[-*]|\d+\.)\s+){re.escape(prefix)}'
                        if re.search(list_pattern, line):
                            new_line = re.sub(list_pattern, rf'\g<1>{project_root}/{prefix}', new_line)
                            changed = True
                new_lines.append(new_line)
            if changed:
                brief.write_text("\n".join(new_lines))
        except Exception:
            pass


def _preconcat_prev_reports(project_root: Path, gen: int, briefs_dir: Path):
    """SCALE-R1: Pre-concatenate previous gen reports so Architect reads one file."""
    if gen <= 1:
        return
    prev_gen_str = f"gen{gen - 1:03d}"
    reports_dir = project_root / "reports" / prev_gen_str
    if not reports_dir.exists():
        return
    lines = [f"# Agent Reports — Generation {gen - 1}\n"]
    report_files = sorted(reports_dir.glob("*.md"))
    # Failures first (most important for Architect), then others capped
    for f in report_files:
        content = f.read_text()
        is_failure = "Agent Failure" in content[:100]
        header = "FAILURE" if is_failure else f.stem
        # Cap each report to 3000 chars
        if len(content) > 3000:
            content = content[:3000] + "\n\n[TRUNCATED]\n"
        lines.append(f"\n## [{header}] {f.stem}\n")
        lines.append(content)
    # Cap total to 40K chars
    dump = "\n".join(lines)
    if len(dump) > 40000:
        dump = dump[:40000] + "\n\n[REMAINING REPORTS TRUNCATED — read individual files if needed]\n"
    (briefs_dir / "prev_gen_reports.md").write_text(dump)


def run_architect(project_root: Path, gen: int, config: dict):
    gen_str = f"gen{gen:03d}"
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen} — Phase 1: Architect")
    print(f"{'='*60}")

    briefs_dir = project_root / "briefs" / gen_str
    briefs_dir.mkdir(parents=True, exist_ok=True)

    # SCALE-R1: Pre-concat previous gen reports
    _preconcat_prev_reports(project_root, gen, briefs_dir)

    prompt = build_architect_prompt(project_root, gen, config)
    model = config.get("architect_model", "opus")

    t0 = time.time()
    try:
        launch_claude_session(
            project_root, prompt, model=model,
            timeout=get_timeout(config, "architect"),
            max_turns=get_max_turns(config, "architect"),
            allowed_tools=["Read", "Write", "Glob", "Grep", "Bash"],
        )
    except (SessionTimeout, SessionError) as e:
        print(f"  WARNING: Architect session issue: {e}")
    _record_timing(project_root, gen, "architect", time.time() - t0)

    # Find manifest — check expected location, then project root
    manifest_path = briefs_dir / "manifest.yaml"
    if not manifest_path.exists():
        alt = project_root / "manifest.yaml"
        if alt.exists():
            shutil.move(str(alt), str(manifest_path))

    # Rescue any briefs written to project root
    for f in project_root.glob("*.md"):
        if f.name.startswith(("explore_", "exploit_", "genetic_", "full_", "research_", "experimentator_")):
            shutil.move(str(f), str(briefs_dir / f.name))

    if not manifest_path.exists():
        print("  ERROR: Architect did not produce manifest.yaml")
        print("  Creating a minimal default manifest...")
        _create_default_manifest(project_root, gen, config)
    else:
        # Validate manifest YAML
        try:
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)
            if not manifest or "agents" not in manifest:
                raise ValueError("manifest missing 'agents' key")
        except Exception as e:
            print(f"  ERROR: Invalid manifest.yaml: {e}")
            print("  Creating a minimal default manifest...")
            _create_default_manifest(project_root, gen, config)

    # BUG-4: Post-process briefs to convert relative paths to absolute
    _absolutize_brief_paths(project_root, briefs_dir)

    # Mark architect phase as cleanly complete. phase_status() checks for this sentinel
    # before trusting the manifest. Without it, an orphaned architect (killed mid-session)
    # could leave a partial manifest that a restarted orchestrator would blindly use.
    (briefs_dir / ".architect_done").touch()


def _create_default_manifest(project_root: Path, gen: int, config: dict):
    gen_str = f"gen{gen:03d}"
    briefs_dir = project_root / "briefs" / gen_str
    briefs_dir.mkdir(parents=True, exist_ok=True)

    model = config.get("default_model", "sonnet")
    agents = []

    if gen == 1:
        for i in range(1, 3):
            agents.append({"type": "explore", "instance": i, "model": model,
                           "brief": f"briefs/{gen_str}/explore_{i}.md"})
            brief = briefs_dir / f"explore_{i}.md"
            brief.write_text(
                f"## Directive\nGeneration 1 — explore different approaches to the problem.\n"
                f"You are explore instance {i}. Try a distinct approach from other instances.\n"
                f"Read the problem description carefully first. Try fundamentally different strategies.\n\n"
                f"## Read first\n1. problem/description.md\n2. problem/constraints.md\n"
                f"3. knowledge/state_of_affairs.md\n4. knowledge/facts/ (all files)\n"
                f"5. knowledge/ideas/active/ (all files)\n6. problem/initial_programs/\n"
            )
        agents.append({"type": "full", "instance": 1, "model": model,
                        "brief": f"briefs/{gen_str}/full_1.md"})
        (briefs_dir / "full_1.md").write_text(
            "## Directive\nGeneration 1 — solve the problem however you see fit.\n"
            "Read the problem description and initial programs, then build the best solution you can.\n\n"
            "## Read first\n1. problem/description.md\n2. problem/constraints.md\n"
            "3. knowledge/state_of_affairs.md\n4. knowledge/facts/ (all files)\n"
            "5. knowledge/ideas/active/ (all files)\n6. problem/initial_programs/\n"
        )
        agents.append({"type": "research", "instance": 1, "model": model,
                        "brief": f"briefs/{gen_str}/research_1.md"})
        (briefs_dir / "research_1.md").write_text(
            "## Directive\nGeneration 1 — research known approaches to this problem.\n"
            "Read the problem description first, then investigate relevant techniques, algorithms, "
            "and mathematical background.\n\n"
            "## Read first\n1. problem/description.md\n2. knowledge/facts/ (all files)\n"
        )
    else:
        for atype in ["explore", "exploit", "full"]:
            agents.append({"type": atype, "instance": 1, "model": model,
                           "brief": f"briefs/{gen_str}/{atype}_1.md"})
            (briefs_dir / f"{atype}_1.md").write_text(
                f"## Directive\nGeneration {gen} — work on the problem as a {atype} agent.\n\n"
                f"## Read first\n1. problem/description.md\n2. knowledge/state_of_affairs.md\n"
                f"3. knowledge/facts/ (all files)\n"
            )

    all_names = [f"{a['type']}_{a['instance']}" for a in agents]
    manifest = {
        "generation": gen,
        "strategy_summary": "Default manifest (Architect did not produce one)",
        "agents": agents,
        "parallel_groups": [all_names],
    }

    with open(briefs_dir / "manifest.yaml", "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    (briefs_dir / "manifest_reasoning.md").write_text(
        "# Manifest Reasoning\n\nDefault manifest — Architect did not produce one.\n"
    )


def _run_agent_group(project_root: Path, gen: int, config: dict,
                     agent_specs: list[dict], max_parallel: int):
    """Run a group of agents in parallel."""

    def run_single_agent(agent_spec):
        atype = agent_spec["type"]
        instance = agent_spec["instance"]
        # Experimentator defaults to opus (creates shared tools); others default to sonnet
        if atype == "experimentator":
            default_model = config.get("experimentator_model", config.get("default_model", "sonnet"))
        else:
            default_model = config.get("default_model", "sonnet")
        model = agent_spec.get("model", default_model)
        brief_path = agent_spec.get("brief", "")
        # Architect can override timeout per-agent via manifest; falls back to config
        work_timeout = agent_spec.get("timeout", get_timeout(config, "agent_default"))
        debrief_timeout = get_timeout(config, "debrief_recovery")

        gen_str = f"gen{gen:03d}"
        ws_path = project_root / "workspace" / f"{gen_str}_{atype}_{instance}"
        report_path = f"{ws_path}/output/report.md"

        wrap_up_timeout = get_timeout(config, "wrap_up")

        print(f"  Launching {atype}_{instance} (model: {model}, work: {work_timeout}s, wrap-up: {wrap_up_timeout}s, debrief: {debrief_timeout}s)")
        create_workspace(project_root, gen, atype, instance)

        prompt = build_agent_prompt(project_root, gen, atype, instance, brief_path)

        t0 = time.time()
        work_timed_out = False
        work_error = None
        session_id = None
        try:
            tools = ["Read", "Write", "Bash", "Glob", "Grep"]
            if atype == "research":
                tools.extend(["WebSearch", "WebFetch"])
            _, session_id = launch_claude_session(
                project_root, prompt, model=model,
                timeout=work_timeout,
                max_turns=get_max_turns(config, atype),
                allowed_tools=tools,
            )
        except SessionTimeout as e:
            work_timed_out = True
            session_id = e.session_id
            print(f"  {atype}_{instance} timed out after {work_timeout}s")
        except (SessionError, Exception) as e:
            work_error = str(e)
            session_id = getattr(e, 'session_id', None)
            print(f"  ERROR in {atype}_{instance}: {work_error}")

        work_elapsed = time.time() - t0
        _record_timing(project_root, gen, f"agent_{atype}_{instance}_work", work_elapsed)

        # --- Phase 2: Wrap-up (resume SAME session — agent keeps its memory) ---
        has_report = Path(report_path).exists()
        if not has_report and (work_timed_out or work_error) and session_id:
            status_msg = "timed out" if work_timed_out else "crashed"
            print(f"  {atype}_{instance} {status_msg} — resuming session for wrap-up")

            wrap_up_msg = (
                "STOP. Time is running out. Do NOT write new solutions or explore new ideas.\n\n"
                "Do this NOW, in order:\n"
                f"1. Run `python3 {project_root}/problem/evaluate.py <file>` on every sol*.py "
                f"in `{ws_path}/output/` that does NOT have a .score file yet. One at a time.\n"
                "2. After each evaluation, update the `# fitness:` header in the .py file with the real score.\n"
                "3. Write observations.md summarizing what you tried and the scores.\n"
                f"4. Write `{report_path}` with a table of all solutions and scores.\n\n"
                "Do NOT read any new files. Do NOT write new code. Just evaluate and report."
            )
            try:
                resume_claude_session(
                    project_root, session_id, wrap_up_msg, model=model,
                    timeout=wrap_up_timeout,
                    max_turns=get_max_turns(config, "wrap_up"),
                    allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"],
                )
            except SessionTimeout:
                print(f"  {atype}_{instance} wrap-up also timed out after {wrap_up_timeout}s")
            except Exception as e:
                print(f"  {atype}_{instance} wrap-up failed: {e}")

            wrap_up_elapsed = time.time() - t0 - work_elapsed
            _record_timing(project_root, gen, f"agent_{atype}_{instance}_wrap_up", wrap_up_elapsed)
            has_report = Path(report_path).exists()

        # --- Phase 3: Debrief (resume same session or fall back to new session) ---
        if not has_report:
            print(f"  {atype}_{instance} — debrief recovery")

            debrief_msg = (
                f"Write `{report_path}` RIGHT NOW. This is your last chance.\n\n"
                f"List every file in `{ws_path}/output/`, note which have .score files, "
                "and summarize what approaches were tried. Keep it short."
            )

            try:
                if session_id:
                    # Try resuming same session first (agent remembers everything)
                    resume_claude_session(
                        project_root, session_id, debrief_msg, model="sonnet",
                        timeout=debrief_timeout,
                        max_turns=get_max_turns(config, "debrief_recovery"),
                        allowed_tools=["Read", "Write", "Glob", "Grep"],
                    )
                else:
                    # No session to resume — fall back to new session with context
                    debrief_prompt = DEBRIEF_RECOVERY_PROMPT(project_root).format(
                        project_root=project_root,
                        ws_path=ws_path,
                        agent_type=atype,
                        instance=instance,
                        gen=gen,
                        brief_path=project_root / Path(brief_path) if brief_path else "N/A",
                        report_path=report_path,
                    )
                    launch_claude_session(
                        project_root, debrief_prompt, model="sonnet",
                        timeout=debrief_timeout,
                        max_turns=get_max_turns(config, "debrief_recovery"),
                        allowed_tools=["Read", "Write", "Glob", "Grep"],
                    )
            except Exception as e:
                print(f"  Debrief recovery also failed for {atype}_{instance}: {e}")

            _record_timing(project_root, gen, f"agent_{atype}_{instance}_debrief", time.time() - t0 - work_elapsed)

        total_elapsed = time.time() - t0
        _record_timing(project_root, gen, f"agent_{atype}_{instance}", total_elapsed)

        # Log failure if work session had issues (but we still have debrief output)
        if work_error and not work_timed_out:
            log_agent_failure(project_root, gen, atype, instance, work_error)

        # Route outputs to correct permanent location
        try:
            if atype == "experimentator":
                move_experiment_outputs(project_root, gen, instance)
            elif atype == "research":
                move_research_outputs(project_root, gen, instance)
            else:
                move_agent_outputs(project_root, gen, atype, instance)
            # BUG-6: Only cleanup on full success (both session and output move)
            cleanup_workspace(project_root, gen, atype, instance)
        except Exception as e:
            print(f"  ERROR moving outputs for {atype}_{instance}: {e}")
            log_agent_failure(project_root, gen, atype, instance, f"Output move failed: {e}")
            # Workspace preserved for debugging

        print(f"  Completed {atype}_{instance} ({total_elapsed:.0f}s total)")
        return atype, instance

    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = [executor.submit(run_single_agent, spec) for spec in agent_specs]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"  ERROR in agent thread: {e}")


def run_agents(project_root: Path, gen: int, config: dict):
    """Phase 2: Launch agents respecting parallel_groups ordering."""
    gen_str = f"gen{gen:03d}"
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen} — Phase 2: Agent Work Sessions")
    print(f"{'='*60}")

    manifest_path = project_root / "briefs" / gen_str / "manifest.yaml"
    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
    except Exception as e:
        print(f"  ERROR reading manifest: {e}")
        print("  Falling back to default manifest...")
        _create_default_manifest(project_root, gen, config)
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

    if not manifest or not manifest.get("agents"):
        print("  WARNING: Manifest is empty or has no agents — regenerating default manifest...")
        _create_default_manifest(project_root, gen, config)
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

    agents = manifest.get("agents", [])
    parallel_groups = manifest.get("parallel_groups", [])
    max_parallel = config.get("max_parallel_sessions", 10)

    # Filter out disabled agent types from config
    agent_cfg = config.get("agents", {})
    enabled_agents = []
    for spec in agents:
        atype = spec.get("type", "")
        type_cfg = agent_cfg.get(atype, {})
        if not type_cfg.get("enabled", True):
            print(f"  Skipping {atype}_{spec.get('instance', '?')} — disabled in config")
            continue
        enabled_agents.append(spec)
    agents = enabled_agents

    # Build lookup from agent name to spec
    agent_lookup = {}
    for spec in agents:
        name = f"{spec['type']}_{spec['instance']}"
        agent_lookup[name] = spec

    if not parallel_groups:
        # No groups specified — run all in parallel
        parallel_groups = [list(agent_lookup.keys())]

    # Execute groups sequentially; agents within each group in parallel
    for group_idx, group in enumerate(parallel_groups):
        # Deduplicate agent names within group to prevent double-launches
        seen = set()
        deduped_group = []
        for name in group:
            if name not in seen:
                seen.add(name)
                deduped_group.append(name)
        group_specs = [agent_lookup[name] for name in deduped_group if name in agent_lookup]
        if not group_specs:
            continue
        if len(parallel_groups) > 1:
            names = [f"{s['type']}_{s['instance']}" for s in group_specs]
            print(f"  --- Group {group_idx + 1}/{len(parallel_groups)}: {names} ---")
        _run_agent_group(project_root, gen, config, group_specs, max_parallel)


def _preconcat_knowledge(project_root: Path, ws: Path):
    """SCALE-1: Pre-concatenate knowledge files into a single dump so evaluator reads fewer files."""
    dump_lines = ["# Pre-Concatenated Knowledge Dump\n"]
    def _truncate(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + "\n\n[TRUNCATED — read full file for details]\n"

    # Ideas
    ideas_dir = project_root / "knowledge" / "ideas"
    if ideas_dir.exists():
        dump_lines.append("\n## All Ideas\n")
        for lc_dir in sorted(ideas_dir.iterdir()):
            if not lc_dir.is_dir():
                continue
            for f in sorted(lc_dir.glob("*.md")):
                dump_lines.append(f"\n### [{lc_dir.name}] {f.stem}\n")
                dump_lines.append(_truncate(f.read_text(), 2000))
    # Clusters
    clusters_dir = project_root / "knowledge" / "clusters"
    if clusters_dir.exists():
        dump_lines.append("\n## All Clusters\n")
        for f in sorted(clusters_dir.glob("*.md")):
            dump_lines.append(f"\n### {f.stem}\n")
            dump_lines.append(_truncate(f.read_text(), 1500))
    # Patterns
    patterns_dir = project_root / "knowledge" / "patterns"
    if patterns_dir.exists():
        dump_lines.append("\n## All Patterns\n")
        for lc_dir in sorted(patterns_dir.iterdir()):
            if not lc_dir.is_dir():
                continue
            for f in sorted(lc_dir.glob("*.md")):
                dump_lines.append(f"\n### [{lc_dir.name}] {f.stem}\n")
                dump_lines.append(_truncate(f.read_text(), 1000))

    dump = "\n".join(dump_lines)
    # Cap total dump to 80K chars to avoid overwhelming evaluator context
    if len(dump) > 80000:
        dump = dump[:80000] + "\n\n[KNOWLEDGE DUMP TRUNCATED at 80K chars — drill into individual files for full content]\n"
    dump_path = ws / "knowledge_dump.md"
    dump_path.write_text(dump)
    return dump_path


def _write_failure_notice(dest_dir: Path, filename: str, agent_type: str, gen: int,
                          expected_files: list[str], ws: Path):
    """Write a failure notice when an analysis agent produces no output."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    gen_str = f"gen{gen:03d}"

    # Gather debug info
    ws_output = ws / "output"
    produced = []
    if ws_output.exists():
        produced = [f.name for f in ws_output.iterdir() if f.is_file()]

    prompt_size = 0
    prompt_path = ws / "prompt.md"
    if prompt_path.exists():
        prompt_size = prompt_path.stat().st_size

    # Check timing
    timing_path = ws.parent.parent / "history" / "timing.json"
    timing_info = "unknown"
    try:
        if timing_path.exists():
            import json as _json
            timing = _json.loads(timing_path.read_text())
            gen_timing = timing.get("generations", {}).get(gen_str, {})
            agent_time = gen_timing.get(agent_type)
            if agent_time is not None:
                timing_info = f"{agent_time:.1f}s"
    except Exception:
        pass

    notice = f"""# {agent_type.replace('_', ' ').title()} — FAILED (Gen {gen})

**Status:** Agent did not produce expected output files.

## Expected Files
{chr(10).join(f'- `{f}`' for f in expected_files)}

## Files Actually Produced
{chr(10).join(f'- `{f}`' for f in produced) if produced else '- (none)'}

## Debug Info
- Generation: {gen}
- Workspace: `{ws}`
- Prompt size: {prompt_size:,} bytes
- Elapsed time: {timing_info}
- Workspace still exists: {ws.exists()}

## Possible Causes
- Agent timed out before writing output
- Agent wrote files to wrong directory
- Agent errored during execution
- Session crashed without recovery
"""
    (dest_dir / filename).write_text(notice)
    print(f"  NOTICE: {agent_type} failure recorded to {dest_dir / filename}")


def _run_analysis_with_debrief(
    project_root: Path, gen: int, agent_type: str, ws: Path,
    prompt: str, model: str, timeout: int, max_turns: int,
    allowed_tools: list[str], config: dict,
):
    """Run an analysis session with 3-phase timeout using session resume."""
    wrap_up_timeout = get_timeout(config, "wrap_up")
    debrief_timeout = get_timeout(config, "debrief_recovery")
    debrief_max_turns = get_max_turns(config, "debrief_recovery")

    t0 = time.time()
    timed_out = False
    errored = False
    session_id = None
    try:
        _, session_id = launch_claude_session(
            project_root, prompt, model=model, timeout=timeout,
            max_turns=max_turns, allowed_tools=allowed_tools,
        )
    except SessionTimeout as e:
        timed_out = True
        session_id = e.session_id
    except (SessionError, Exception) as e:
        errored = True
        session_id = getattr(e, 'session_id', None)
        print(f"  WARNING: {agent_type} session error: {e}")
    elapsed = time.time() - t0
    _record_timing(project_root, gen, agent_type, elapsed)

    # --- Phase 2: Wrap-up (resume same session) ---
    has_report = (ws / "output" / "report.md").exists()
    if not has_report and (timed_out or errored) and session_id:
        status_msg = "timed out" if timed_out else "crashed"
        print(f"  {agent_type} {status_msg} — resuming session for wrap-up")

        wrap_up_msg = (
            "STOP. Time is running out. Do NOT start over or re-read files you already read.\n\n"
            f"Write the MISSING output files to `{ws}/output/` now. "
            "Focus on the most important outputs first. Write the report last."
        )
        try:
            resume_claude_session(
                project_root, session_id, wrap_up_msg, model=model,
                timeout=wrap_up_timeout,
                max_turns=get_max_turns(config, "wrap_up"),
                allowed_tools=allowed_tools,
            )
        except SessionTimeout:
            print(f"  {agent_type} wrap-up also timed out after {wrap_up_timeout}s")
        except Exception as e:
            print(f"  {agent_type} wrap-up failed: {e}")

        wrap_up_elapsed = time.time() - t0 - elapsed
        _record_timing(project_root, gen, f"{agent_type}_wrap_up", wrap_up_elapsed)
        has_report = (ws / "output" / "report.md").exists()

    # --- Phase 3: Debrief (resume same session or fall back to new session) ---
    if not has_report:
        print(f"  {agent_type} — debrief recovery")
        debrief_msg = (
            f"Write `{ws}/output/report.md` RIGHT NOW. Summarize what you produced and "
            "what remains incomplete. Keep it short — just document the current state."
        )
        try:
            if session_id:
                resume_claude_session(
                    project_root, session_id, debrief_msg, model="sonnet",
                    timeout=debrief_timeout, max_turns=debrief_max_turns,
                    allowed_tools=["Read", "Write", "Glob", "Grep"],
                )
            else:
                debrief_prompt = ANALYSIS_DEBRIEF_PROMPT(project_root).format(
                    project_root=project_root, ws_path=ws,
                    agent_type=agent_type, gen=gen,
                )
                launch_claude_session(
                    project_root, debrief_prompt, model="sonnet",
                    timeout=debrief_timeout, max_turns=debrief_max_turns,
                    allowed_tools=["Read", "Write", "Glob", "Grep"],
                )
        except Exception as e:
            print(f"  Debrief recovery failed for {agent_type}: {e}")
        _record_timing(project_root, gen, f"{agent_type}_debrief", time.time() - t0 - elapsed)


def run_evaluator(project_root: Path, gen: int, config: dict):
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen} — Phase 3: Evaluator")
    print(f"{'='*60}")

    ws = create_analysis_workspace(project_root, gen, "evaluator")
    for subdir in ["new_ideas", "updated_ideas", "new_patterns", "updated_clusters"]:
        (ws / "output" / subdir).mkdir(exist_ok=True)

    # SCALE-1: Pre-concat knowledge to save evaluator turns
    knowledge_dump = _preconcat_knowledge(project_root, ws)

    model = config.get("analysis", {}).get("evaluator", {}).get("model", "opus")
    prompt = build_evaluator_prompt(project_root, gen, config)

    _run_analysis_with_debrief(
        project_root, gen, "evaluator", ws, prompt, model=model,
        timeout=get_timeout(config, "evaluator"),
        max_turns=get_max_turns(config, "evaluator"),
        allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"], config=config,
    )

    # Check if evaluator produced key output; write failure notice if not
    ws_output = ws / "output"
    has_report = (ws_output / "evaluator_report.md").exists() if ws_output.exists() else False
    has_snapshot = (ws_output / "generation_snapshot.md").exists() if ws_output.exists() else False
    if not has_report and not has_snapshot:
        gen_str = f"gen{gen:03d}"
        reports_dir = project_root / "reports" / gen_str
        _write_failure_notice(
            reports_dir, "evaluator_failure.md", "evaluator", gen,
            ["evaluator_report.md", "generation_snapshot.md", "new_ideas/", "updated_ideas/"],
            ws,
        )

    try:
        move_evaluator_outputs(project_root, gen)
        cleanup_workspace(project_root, gen, "evaluator")
    except Exception as e:
        print(f"  ERROR moving evaluator outputs: {e}")
        # Workspace preserved for debugging
    print("  Evaluator complete")


def run_system_critic(project_root: Path, gen: int, config: dict):
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen} — Phase 4: System Critic")
    print(f"{'='*60}")

    ws = create_analysis_workspace(project_root, gen, "system_critic")
    model = config.get("analysis", {}).get("system_critic", {}).get("model", "sonnet")
    prompt = build_critic_prompt(project_root, gen)

    _run_analysis_with_debrief(
        project_root, gen, "system_critic", ws, prompt, model=model,
        timeout=get_timeout(config, "system_critic"),
        max_turns=get_max_turns(config, "system_critic"),
        allowed_tools=["Read", "Write", "Glob", "Grep"], config=config,
    )

    # Check if critic produced output; write failure notice if not
    ws_output = ws / "output"
    has_analysis = (ws_output / "system_analysis.md").exists() if ws_output.exists() else False
    if not has_analysis:
        _write_failure_notice(
            project_root / "feedback" / "system_analysis",
            f"gen{gen:03d}.md", "system_critic", gen,
            ["system_analysis.md", "system_recommendations.md", "experiment_suggestions.md"],
            ws,
        )

    try:
        move_critic_outputs(project_root, gen)
        cleanup_workspace(project_root, gen, "system_critic")
    except Exception as e:
        print(f"  ERROR moving system critic outputs: {e}")
    print("  System Critic complete")


def should_run_consistency_review(project_root: Path, gen: int, config: dict) -> bool:
    interval = config.get("consistency_review_interval", 3)
    if interval < 1:
        interval = 3
    if gen % interval == 0:
        return True

    if config.get("emergency_review_on_strategic_shift", True):
        gen_str = f"gen{gen:03d}"
        report = project_root / "reports" / gen_str / "evaluator.md"
        if report.exists():
            text = report.read_text()
            if "strategic_shift: true" in text.lower() or "strategic_shift:true" in text.lower():
                return True

    return False


def run_consistency_review(project_root: Path, gen: int, config: dict):
    gen_str = f"gen{gen:03d}"
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen} — Phase 5: Consistency Review")
    print(f"{'='*60}")

    ws = create_analysis_workspace(project_root, gen, "consistency_reviewer")
    for subdir in ["updated_ideas", "updated_clusters"]:
        (ws / "output" / subdir).mkdir(exist_ok=True)

    model = config.get("architect_model", "opus")
    prompt = build_consistency_prompt(project_root, gen, config)

    _run_analysis_with_debrief(
        project_root, gen, "consistency_reviewer", ws, prompt, model=model,
        timeout=get_timeout(config, "consistency_reviewer"),
        max_turns=get_max_turns(config, "consistency_reviewer"),
        allowed_tools=["Read", "Write", "Glob", "Grep"], config=config,
    )

    # Check if reviewer produced output; write failure notice if not
    ws_output = ws / "output"
    has_soa = (ws_output / "state_of_affairs.md").exists() if ws_output.exists() else False
    if not has_soa:
        _write_failure_notice(
            project_root / "feedback" / "consistency_reviews",
            f"gen{gen:03d}.md", "consistency_reviewer", gen,
            ["state_of_affairs.md", "updated_ideas/", "updated_clusters/"],
            ws,
        )

    try:
        move_consistency_outputs(project_root, gen)
        cleanup_workspace(project_root, gen, "consistency_reviewer")
    except Exception as e:
        print(f"  ERROR moving consistency review outputs: {e}")
    print("  Consistency Review complete")


def finalize_generation(project_root: Path, gen: int, config: dict) -> float:
    gen_str = f"gen{gen:03d}"
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen} — Phase 6: Finalize")
    print(f"{'='*60}")

    best_score = update_rankings(project_root, gen)
    detect_interventions(project_root, gen)

    snapshot = project_root / "history" / "generations" / f"{gen_str}.md"
    snapshot.parent.mkdir(parents=True, exist_ok=True)

    # Build timing section
    timing = _load_timing(project_root)
    gen_timing = timing.get("generations", {}).get(gen_str, {})
    timing_section = ""
    if gen_timing:
        timing_section = "\n## Timing\n"
        for k, v in gen_timing.items():
            timing_section += f"- {k}: {v:.1f}s\n"

    name, _ = primary_metric(project_root)
    fmt = _score_fmt(project_root)

    if snapshot.exists():
        # Evaluator may have written snapshot — append timing if missing
        existing = snapshot.read_text()
        if "## Timing" not in existing and timing_section:
            snapshot.write_text(existing.rstrip() + "\n" + timing_section)
    else:
        snapshot.write_text(
            f"---\ngeneration: {gen}\nbest_score: {best_score}\n"
            f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n"
            f"# Generation {gen} Snapshot\n\nBest {name}: {format(best_score, fmt)}\n"
            f"{timing_section}"
        )

    fmt = _score_fmt(project_root)
    print(f"  Best fitness: {format(best_score, fmt)}")
    return best_score


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_generation(project_root: Path, gen: int, config: dict) -> float:
    status = phase_status(project_root, gen)
    print(f"\n  Resuming from phase: {status}")

    if status == "complete":
        print(f"  Generation {gen} already complete, skipping.")
        # Return actual best score from cache
        scores_cache = project_root / "history" / "all_scores.json"
        if scores_cache.exists():
            try:
                cached = json.loads(scores_cache.read_text())
                if cached:
                    higher_better = fitness_is_higher_better(project_root)
                    scores_only = [s for s, _ in cached]
                    return max(scores_only) if higher_better else min(scores_only)
            except Exception:
                pass
        return 0.0

    gen_t0 = time.time()

    if status == "not_started":
        run_architect(project_root, gen, config)
        status = "planned"

    if status == "planned":
        run_agents(project_root, gen, config)
        status = "agents_done"

    if status == "agents_done":
        run_evaluator(project_root, gen, config)
        status = "evaluator_done"

    if status == "evaluator_done":
        run_system_critic(project_root, gen, config)
        status = "critic_done"

    if status == "critic_done":
        if should_run_consistency_review(project_root, gen, config):
            run_consistency_review(project_root, gen, config)
        status = "consistency_done"

    best_score = finalize_generation(project_root, gen, config)
    _record_timing(project_root, gen, "total", time.time() - gen_t0)
    return best_score


def main():
    parser = argparse.ArgumentParser(description="Alpha Evolve Orchestrator")
    parser.add_argument(
        "project_root", nargs="?", default=".",
        help="Path to the alpha-evolve project root"
    )
    parser.add_argument(
        "--start-gen", type=int, default=None,
        help="Override starting generation number"
    )
    parser.add_argument(
        "--single", action="store_true",
        help="Run a single generation and exit"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without launching agents"
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    print(f"Alpha Evolve — Project root: {project_root}")

    _preflight_check(project_root)

    config = load_config(project_root)
    max_gens = config.get("generations", 20)
    target = get_target_score(project_root, config)
    higher_better = fitness_is_higher_better(project_root)

    start_gen = args.start_gen if args.start_gen else current_generation(project_root)

    if start_gen == 1:
        bootstrap_initial_knowledge(project_root)

    direction = "higher" if higher_better else "lower"
    print(f"Starting from generation {start_gen}")
    print(f"Target fitness: {target} ({direction} is better)")
    print(f"Max generations: {max_gens}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would run generations {start_gen} to {max_gens}")
        return

    for gen in range(start_gen, max_gens + 1):
        print(f"\n{'#'*60}")
        print(f"  GENERATION {gen} / {max_gens}")
        print(f"{'#'*60}")

        best_score = run_generation(project_root, gen, config)

        target_reached = (
            (higher_better and best_score >= target)
            or (not higher_better and best_score <= target and best_score > 0)
        )
        if target_reached:
            fmt = _score_fmt(project_root)
            print(f"\n  TARGET REACHED! Fitness {format(best_score, fmt)} {'≥' if higher_better else '≤'} {target}")
            print(f"  Best solution: {project_root / 'population' / 'best.py'}")
            break

        if args.single:
            print(f"\n  Single generation mode — stopping after gen {gen}")
            break

    print(f"\n{'#'*60}")
    print("  Alpha Evolve complete.")
    print(f"  Best solution: {project_root / 'population' / 'best.py'}")
    print(f"  State of Affairs: {project_root / 'knowledge' / 'state_of_affairs.md'}")
    print(f"{'#'*60}")


if __name__ == "__main__":
    main()
