"""Filesystem scanning for Idea Evolve project state.

Each function scans the idea-evolve/ directory tree and returns
structured data. No caching — reads fresh on each call.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .config import get_project_root, list_problems, list_attempts, get_run_root, get_problem_dir
from .helpers import read_frontmatter, read_body, extract_score, get_metrics_config

# Request-scoped context — set by API routes before calling scanner functions.
# Avoids threading run_root/problem_dir through every function signature.
_request_run_root: Path | None = None
_request_problem_dir: Path | None = None


def set_scanner_context(run_root: Path | None, problem_dir: Path | None):
    """Set the scanner context for the current request."""
    global _request_run_root, _request_problem_dir
    _request_run_root = run_root
    _request_problem_dir = problem_dir


def _root(run_root: Path | None = None) -> Path:
    """Return the run root directory (where population/, history/, etc. live)."""
    if run_root is not None:
        return run_root
    # Check request-scoped context first
    if _request_run_root is not None:
        return _request_run_root
    # Auto-detect
    project_root = get_project_root()
    problems_dir = project_root / "problems"
    if problems_dir.is_dir():
        problems = list_problems()
        for pid in problems:
            attempts = list_attempts(pid)
            if attempts:
                resolved = get_run_root(pid, attempts[-1])
                if resolved and resolved.is_dir() and resolved != project_root:
                    return resolved
    return project_root


def _is_sentinel(score: float | None, problem_dir: Path | None = None) -> bool:
    """Check if a score is the sentinel (evaluation error) value."""
    if score is None:
        return False
    metrics = get_metrics_config(problem_dir=problem_dir)
    sentinel = metrics.get("sentinel_value")
    if sentinel is not None and score == sentinel:
        return True
    return False


def _is_valid_score(result: dict | None, problem_dir: Path | None = None) -> bool:
    """Check if an extracted score result represents a real valid score."""
    if not result:
        return False
    score = result.get("fitness")
    if score is None:
        return False
    if not result.get("is_valid", 0):
        return False
    if _is_sentinel(score, problem_dir=problem_dir):
        return False
    return True


# ---------------------------------------------------------------------------
# Run State
# ---------------------------------------------------------------------------

def get_run_state() -> dict:
    """Read orchestrator's run_state.json and add derived liveness fields."""
    root = _root()
    state_path = root / "history" / "run_state.json"
    if not state_path.exists():
        return {"available": False}

    try:
        state = json.loads(state_path.read_text())
    except Exception:
        return {"available": False}

    state["available"] = True

    # PID liveness check
    pid = state.get("pid")
    if pid:
        try:
            os.kill(pid, 0)
            state["pid_alive"] = True
        except (OSError, ProcessLookupError):
            state["pid_alive"] = False
    else:
        state["pid_alive"] = False

    # Staleness check
    last_updated = state.get("last_updated")
    if last_updated:
        try:
            lu = datetime.fromisoformat(last_updated)
            if lu.tzinfo is None:
                lu = lu.replace(tzinfo=timezone.utc)
            age_s = (datetime.now(timezone.utc) - lu).total_seconds()
            state["age_seconds"] = round(age_s, 1)
            state["is_stale"] = age_s > 120
        except Exception:
            state["age_seconds"] = None
            state["is_stale"] = True
    else:
        state["age_seconds"] = None
        state["is_stale"] = True

    # Derived: is_running = pid alive AND not stale AND status is "running"
    state["is_running"] = (
        state.get("pid_alive", False)
        and not state.get("is_stale", True)
        and state.get("status") == "running"
    )

    return state


# ---------------------------------------------------------------------------
# Generations & Phases
# ---------------------------------------------------------------------------

def get_phase_status(gen: int) -> str:
    """Determine which phase a generation is in by checking file existence."""
    root = _root()
    gen_str = f"gen{gen:03d}"

    if (root / "history" / "generations" / f"{gen_str}.md").exists():
        return "complete"

    ws = root / "workspace"

    # Check consistency reviewer
    cons_ws = ws / f"{gen_str}_consistency_reviewer"
    if (cons_ws / "output" / "state_of_affairs.md").exists():
        return "consistency_done"
    if cons_ws.exists():
        return "consistency_running"

    # Check system critic
    critic_ws = ws / f"{gen_str}_system_critic"
    if (critic_ws / "output" / "system_analysis.md").exists():
        return "critic_done"
    if critic_ws.exists():
        return "critic_running"

    # Check evaluator
    ev_ws = ws / f"{gen_str}_evaluator"
    ev_output = ev_ws / "output"
    if ev_output.exists():
        if any([
            (ev_output / "evaluator_report.md").exists(),
            (ev_output / "generation_snapshot.md").exists(),
        ]):
            return "evaluator_done"
    if ev_ws.exists():
        return "evaluator_running"

    # Check agent workspaces (exclude evaluator/critic/consistency)
    special = {f"{gen_str}_evaluator", f"{gen_str}_system_critic", f"{gen_str}_consistency_reviewer"}
    agent_workspaces = [
        d for d in (ws.glob(f"{gen_str}_*") if ws.exists() else [])
        if d.is_dir() and d.name not in special
    ]

    pop_dir = root / "population" / gen_str
    reports_dir = root / "reports" / gen_str
    has_output = (
        (pop_dir.exists() and any(pop_dir.iterdir()))
        or (reports_dir.exists() and any(reports_dir.iterdir()))
    )

    if has_output:
        if agent_workspaces:
            return "agents_running"
        return "agents_done"

    if agent_workspaces:
        return "agents_running"

    if (root / "briefs" / gen_str / "manifest.yaml").exists():
        return "planned"

    return "not_started"


def get_generation_status() -> list[dict]:
    """Return status of every generation that has any trace."""
    root = _root()
    generations = []
    gen = 1
    while True:
        gen_str = f"gen{gen:03d}"
        has_briefs = (root / "briefs" / gen_str).exists()
        has_pop = (root / "population" / gen_str).exists()
        has_reports = (root / "reports" / gen_str).exists()
        has_snapshot = (root / "history" / "generations" / f"{gen_str}.md").exists()
        has_workspace = any((root / "workspace").glob(f"{gen_str}_*")) if (root / "workspace").exists() else False

        if not any([has_briefs, has_pop, has_reports, has_snapshot, has_workspace]):
            break

        status = get_phase_status(gen)
        sol_count = 0
        agent_dirs = []
        pop_dir = root / "population" / gen_str
        if pop_dir.exists():
            for d in sorted(pop_dir.iterdir()):
                if d.is_dir():
                    agent_dirs.append(d.name)
                    sol_count += len(list(d.glob("sol*.py")))

        report_count = 0
        reports_dir = root / "reports" / gen_str
        if reports_dir.exists():
            report_count = len(list(reports_dir.glob("*.md")))

        best_score = None
        metrics = get_metrics_config()
        higher_is_better = metrics.get("higher_is_better", True)

        def _update_best(score):
            nonlocal best_score
            if best_score is None:
                best_score = score
            elif higher_is_better and score > best_score:
                best_score = score
            elif not higher_is_better and score < best_score:
                best_score = score

        # Scores from finalized population
        if pop_dir.exists():
            for d in pop_dir.iterdir():
                if d.is_dir():
                    for sol in d.glob("sol*.py"):
                        result = extract_score(sol)
                        if _is_valid_score(result):
                            _update_best(result["fitness"])

        # Also scan workspace for in-progress solutions
        # Only trust .score sidecar files (written by evaluate.py with is_valid).
        # Header-only scores may be 0.0 placeholders.
        ws_sol_count = 0
        ws_scored_count = 0
        ws_dir = root / "workspace"
        if ws_dir.exists():
            for ws in ws_dir.glob(f"{gen_str}_*/output"):
                for sol in ws.glob("sol*.py"):
                    ws_sol_count += 1
                    score_file = sol.with_suffix(".score")
                    if score_file.exists():
                        result = extract_score(sol)
                        if _is_valid_score(result):
                            ws_scored_count += 1
                            _update_best(result["fitness"])

        generations.append({
            "gen": gen,
            "gen_str": gen_str,
            "status": status,
            "solutions": sol_count + ws_scored_count,
            "agents": agent_dirs,
            "reports": report_count,
            "best_score": best_score,
        })
        gen += 1

    return generations


# ---------------------------------------------------------------------------
# Solutions
# ---------------------------------------------------------------------------

def get_solutions() -> list[dict]:
    """Get all solutions with scores, sorted by fitness descending."""
    root = _root()
    solutions = []
    pop_dir = root / "population"
    if not pop_dir.exists():
        return solutions

    for gen_dir in sorted(pop_dir.iterdir()):
        if not gen_dir.is_dir() or not gen_dir.name.startswith("gen"):
            continue
        gen_num = int(gen_dir.name[3:])
        for agent_dir in sorted(gen_dir.iterdir()):
            if not agent_dir.is_dir():
                continue
            agent_type = agent_dir.name.rsplit("_", 1)[0]
            instance = agent_dir.name.rsplit("_", 1)[-1] if "_" in agent_dir.name else "0"
            for sol in sorted(agent_dir.glob("sol*.py")):
                result = extract_score(sol)
                score = result.get("fitness") if result else None
                is_valid = result.get("is_valid", 0) if result else 0
                solutions.append({
                    "gen": gen_num,
                    "agent_type": agent_type,
                    "instance": instance,
                    "file": sol.name,
                    "path": str(sol.relative_to(pop_dir.parent)),
                    "score": score,
                    "is_valid": is_valid,
                    "is_sentinel": _is_sentinel(score),
                    "size": sol.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        sol.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                })

    # Also include workspace (in-progress) solutions not yet in population/
    ws_dir = root / "workspace"
    if ws_dir.exists():
        pop_gen_agents = set()
        for s in solutions:
            pop_gen_agents.add((s["gen"], s["agent_type"] + "_" + s["instance"], s["file"]))

        for ws in sorted(ws_dir.iterdir()):
            if not ws.is_dir():
                continue
            parts = ws.name.split("_", 1)
            if len(parts) < 2 or not parts[0].startswith("gen"):
                continue
            gen_str = parts[0]
            agent_id = parts[1]
            gen_num = int(gen_str[3:]) if gen_str[3:].isdigit() else 0

            agent_parts = agent_id.rsplit("_", 1)
            agent_type = agent_parts[0] if len(agent_parts) == 2 and agent_parts[1].isdigit() else agent_id
            instance = agent_parts[1] if len(agent_parts) == 2 and agent_parts[1].isdigit() else "0"

            output_dir = ws / "output"
            if not output_dir.exists():
                continue
            for sol in sorted(output_dir.glob("sol*.py")):
                if (gen_num, agent_type + "_" + instance, sol.name) in pop_gen_agents:
                    continue
                result = extract_score(sol)
                score = result.get("fitness") if result else None
                is_valid = result.get("is_valid", 0) if result else 0
                solutions.append({
                    "gen": gen_num,
                    "agent_type": agent_type,
                    "instance": instance,
                    "file": sol.name,
                    "path": str(sol.relative_to(root)),
                    "score": score,
                    "is_valid": is_valid,
                    "is_sentinel": _is_sentinel(score),
                    "size": sol.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        sol.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                    "in_progress": True,
                })

    metrics = get_metrics_config()
    higher_is_better = metrics.get("higher_is_better", True)

    def _sort_key(x):
        s = x.get("score")
        # Sentinels and None sort to bottom
        if s is None or x.get("is_sentinel"):
            return float('inf') if not higher_is_better else float('-inf')
        return s

    solutions.sort(key=_sort_key, reverse=higher_is_better)
    return solutions


# ---------------------------------------------------------------------------
# Knowledge
# ---------------------------------------------------------------------------

def get_knowledge() -> dict:
    """Gather all knowledge base items across all layers."""
    root = _root()
    kb = {
        "state_of_affairs": "",
        "state_of_affairs_meta": {},
        "ideas": [],
        "facts": [],
        "patterns": [],
        "clusters": [],
    }

    soa = root / "knowledge" / "state_of_affairs.md"
    if soa.exists():
        kb["state_of_affairs"] = read_body(soa)
        kb["state_of_affairs_meta"] = read_frontmatter(soa)

    ideas_dir = root / "knowledge" / "ideas"
    if ideas_dir.exists():
        for lc_dir in sorted(ideas_dir.iterdir()):
            if not lc_dir.is_dir():
                continue
            for f in sorted(lc_dir.glob("*.md")):
                fm = read_frontmatter(f)
                stats = fm.get("stats", {}) if isinstance(fm.get("stats"), dict) else {}
                kb["ideas"].append({
                    "id": fm.get("id", f.stem),
                    "title": fm.get("name", fm.get("title", f.stem)),
                    "lifecycle": lc_dir.name,
                    "confidence": fm.get("confidence", fm.get("certainty", "?")),
                    "first_seen": fm.get("first_seen", fm.get("created_gen", "?")),
                    "last_confirmed_gen": fm.get("last_confirmed_gen", "?"),
                    "supported_by": fm.get("supported_by", []),
                    "cluster": fm.get("cluster", ""),
                    "body": read_body(f),
                })

    facts_dir = root / "knowledge" / "facts"
    if facts_dir.exists():
        for f in sorted(facts_dir.glob("*.md")):
            fm = read_frontmatter(f)
            kb["facts"].append({
                "id": fm.get("id", f.stem),
                "title": fm.get("name", fm.get("title", f.stem)),
                "confidence": fm.get("confidence", "?"),
                "verified": fm.get("verified", False),
                "first_seen": fm.get("first_seen", fm.get("created_gen", "?")),
                "body": read_body(f),
            })

    patterns_dir = root / "knowledge" / "patterns"
    if patterns_dir.exists():
        for lc_dir in patterns_dir.iterdir():
            if not lc_dir.is_dir():
                continue
            for f in sorted(lc_dir.glob("*.md")):
                fm = read_frontmatter(f)
                kb["patterns"].append({
                    "id": fm.get("id", f.stem),
                    "title": fm.get("name", fm.get("title", f.stem)),
                    "lifecycle": lc_dir.name,
                    "body": read_body(f),
                })

    clusters_dir = root / "knowledge" / "clusters"
    if clusters_dir.exists():
        for f in sorted(clusters_dir.glob("*.md")):
            fm = read_frontmatter(f)
            kb["clusters"].append({
                "id": fm.get("id", f.stem),
                "title": fm.get("name", fm.get("title", f.stem)),
                "idea_count": len(fm.get("member_ideas", fm.get("ideas", []))) if isinstance(fm.get("member_ideas", fm.get("ideas", [])), list) else 0,
                "status": fm.get("status", "unknown"),
                "body": read_body(f),
            })

    return kb


# ---------------------------------------------------------------------------
# Score Progression
# ---------------------------------------------------------------------------

def get_score_progression() -> list[dict]:
    """Derive score progression from all_scores.json, grouped by generation.

    Falls back to parsing score_progression.md if all_scores.json is unavailable.
    """
    root = _root()
    all_scores_path = root / "history" / "all_scores.json"

    if all_scores_path.exists():
        try:
            all_scores = json.loads(all_scores_path.read_text())
            if all_scores:
                metrics = get_metrics_config()
                higher_is_better = metrics.get("higher_is_better", True)

                # Group by generation (extract gen from path)
                gen_best = {}
                for score, path_str in all_scores:
                    if score is None or not isinstance(score, (int, float)):
                        continue
                    # Extract gen number from path like .../population/gen002/agent/sol.py
                    path = Path(path_str)
                    for part in path.parts:
                        if part.startswith("gen") and part[3:].isdigit():
                            gen_num = int(part[3:])
                            if gen_num not in gen_best:
                                gen_best[gen_num] = score
                            elif higher_is_better and score > gen_best[gen_num]:
                                gen_best[gen_num] = score
                            elif not higher_is_better and score < gen_best[gen_num]:
                                gen_best[gen_num] = score
                            break

                return [{"gen": g, "best_fitness": s}
                        for g, s in sorted(gen_best.items())]
        except Exception:
            pass

    # Fallback: parse score_progression.md
    prog_path = root / "history" / "score_progression.md"
    points = []
    if not prog_path.exists():
        return points

    text = prog_path.read_text()
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("|") and not line.startswith("| Gen") and not line.startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                try:
                    points.append({
                        "gen": int(parts[0]),
                        "best_fitness": float(parts[1]),
                    })
                except ValueError:
                    pass
    return points


def get_initial_scores() -> list[dict]:
    """Get scores for baseline programs (gen 0 in population, or initial_programs in problem dir)."""
    root = _root()
    results = []

    # First try gen 0 population (evaluated baselines from bootstrap)
    gen0_dir = root / "population" / "gen000"
    if gen0_dir.exists():
        for agent_dir in sorted(gen0_dir.iterdir()):
            if not agent_dir.is_dir():
                continue
            for sol in sorted(agent_dir.glob("sol*.py")):
                result = extract_score(sol)
                results.append({
                    "file": sol.name,
                    "score": result.get("fitness") if result else None,
                    "is_valid": result.get("is_valid", 1) if result else 0,
                })

    if results:
        return results

    # Fallback: read from problem dir initial_programs (unevaluated)
    problem_dir = _request_problem_dir or get_problem_dir()
    if problem_dir:
        init_dir = problem_dir / "initial_programs"
        if init_dir.exists():
            for sol in sorted(init_dir.glob("*.py")):
                result = extract_score(sol)
                results.append({
                    "file": sol.name,
                    "score": result.get("fitness") if result else None,
                    "is_valid": result.get("is_valid", 1) if result else 0,
                })

    return results


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def get_reports(gen: int | None = None) -> list[dict]:
    """Get agent reports, optionally filtered by generation."""
    root = _root()
    reports = []
    reports_dir = root / "reports"
    if not reports_dir.exists():
        return reports

    gen_dirs = sorted(reports_dir.iterdir())
    if gen is not None:
        gen_dirs = [d for d in gen_dirs if d.name == f"gen{gen:03d}"]

    for gen_dir in gen_dirs:
        if not gen_dir.is_dir():
            continue
        gen_num = int(gen_dir.name[3:])
        for f in sorted(gen_dir.glob("*.md")):
            reports.append({
                "gen": gen_num,
                "agent": f.stem,
                "content": f.read_text(),
                "size": f.stat().st_size,
            })
    return reports


def get_feedback() -> dict:
    """Get system critic analysis, recommendations, and consistency reviews.

    Checks both finalized feedback/ and in-progress workspace/ outputs.
    """
    root = _root()
    result = {"recommendations": None, "analyses": [], "consistency_reviews": []}
    seen_analysis_gens = set()

    # Current recommendations (finalized)
    rec_path = root / "feedback" / "system_recommendations.md"
    if rec_path.exists():
        result["recommendations"] = rec_path.read_text()[:8000]

    # Per-gen analyses (finalized)
    analysis_dir = root / "feedback" / "system_analysis"
    if analysis_dir.exists():
        for f in sorted(analysis_dir.glob("*.md"), reverse=True):
            gen_num = int(f.stem[3:]) if f.stem.startswith("gen") and f.stem[3:].isdigit() else 0
            seen_analysis_gens.add(gen_num)
            result["analyses"].append({
                "gen": gen_num,
                "content": f.read_text()[:5000],
                "in_progress": False,
            })

    # In-progress critic outputs from workspace
    ws_dir = root / "workspace"
    if ws_dir.exists():
        for ws in sorted(ws_dir.iterdir(), reverse=True):
            if not ws.name.endswith("_system_critic") or not ws.is_dir():
                continue
            gen_str = ws.name.split("_")[0]
            gen_num = int(gen_str[3:]) if gen_str.startswith("gen") and gen_str[3:].isdigit() else 0

            # Analysis
            analysis = ws / "output" / "system_analysis.md"
            if analysis.exists() and gen_num not in seen_analysis_gens:
                result["analyses"].insert(0, {
                    "gen": gen_num,
                    "content": analysis.read_text()[:5000],
                    "in_progress": True,
                })

            # Recommendations (workspace version if no finalized one)
            recs = ws / "output" / "system_recommendations.md"
            if recs.exists() and result["recommendations"] is None:
                result["recommendations"] = recs.read_text()[:8000]

    # Sort analyses newest first
    result["analyses"].sort(key=lambda a: a["gen"], reverse=True)

    # Consistency reviews (finalized)
    cons_dir = root / "feedback" / "consistency_reviews"
    if cons_dir.exists():
        for f in sorted(cons_dir.glob("*.md"), reverse=True):
            gen_num = int(f.stem[3:]) if f.stem.startswith("gen") and f.stem[3:].isdigit() else 0
            result["consistency_reviews"].append({
                "gen": gen_num,
                "content": f.read_text()[:5000],
            })

    return result


# ---------------------------------------------------------------------------
# File Tree
# ---------------------------------------------------------------------------

def get_file_tree() -> dict:
    """Build a tree of all idea-evolve files grouped by top-level directory."""
    root = _root()
    tree = {}
    if not root.exists():
        return tree

    important_dirs = [
        "population", "knowledge", "reports", "briefs",
        "feedback", "history", "agents", "problem", "user",
    ]

    for dirname in important_dirs:
        dirpath = root / dirname
        if not dirpath.exists():
            continue
        files = []
        for f in sorted(dirpath.rglob("*")):
            if f.is_file():
                files.append({
                    "path": str(f.relative_to(root)),
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        f.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                })
        tree[dirname] = files
    return tree


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def get_manifest(gen: int) -> dict | None:
    """Read a generation's manifest.yaml."""
    import yaml
    manifest_path = _root() / "briefs" / f"gen{gen:03d}" / "manifest.yaml"
    if manifest_path.exists():
        try:
            return yaml.safe_load(manifest_path.read_text())
        except Exception:
            return None
    return None


# ---------------------------------------------------------------------------
# Timing Data (from history/timing.json)
# ---------------------------------------------------------------------------

def get_timing_data() -> list[dict]:
    """Read timing data if it exists."""
    timing_path = _root() / "history" / "timing.json"
    if not timing_path.exists():
        return []
    try:
        data = json.loads(timing_path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Coverage Matrix & Solution-Idea Map
# ---------------------------------------------------------------------------

def get_coverage_matrix() -> str:
    """Read the coverage matrix markdown."""
    path = _root() / "history" / "coverage_matrix.md"
    if path.exists():
        return path.read_text()[:10000]
    return ""


def get_solution_idea_map() -> str:
    """Read the solution-idea map markdown."""
    path = _root() / "history" / "solution_idea_map.md"
    if path.exists():
        return path.read_text()[:10000]
    return ""


# ---------------------------------------------------------------------------
# Eval Cache Stats
# ---------------------------------------------------------------------------

def get_active_agents() -> list[dict]:
    """Get currently running agents by scanning workspace directories."""
    root = _root()
    ws_dir = root / "workspace"
    agents = []
    if not ws_dir.exists():
        return agents

    # Only show workspaces for the current generation to avoid stale gen artifacts
    run_state = get_run_state()
    current_gen = run_state.get("current_gen")
    current_gen_str = f"gen{current_gen:03d}" if current_gen else None

    for ws in sorted(ws_dir.iterdir()):
        if not ws.is_dir():
            continue
        name = ws.name  # e.g. gen003_explore_1
        parts = name.split("_", 1)
        if len(parts) < 2:
            continue
        gen_str = parts[0]
        # Skip workspaces from past generations
        if current_gen_str and gen_str != current_gen_str:
            continue
        agent_id = parts[1]  # e.g. explore_1

        # Determine agent type and instance
        agent_parts = agent_id.rsplit("_", 1)
        agent_type = agent_parts[0] if len(agent_parts) == 2 and agent_parts[1].isdigit() else agent_id
        instance = agent_parts[1] if len(agent_parts) == 2 and agent_parts[1].isdigit() else "0"

        gen_num = int(gen_str[3:]) if gen_str.startswith("gen") and gen_str[3:].isdigit() else 0

        output_dir = ws / "output"
        solutions = []
        best_score = None
        metrics = get_metrics_config()
        higher_is_better = metrics.get("higher_is_better", True)

        if output_dir.exists():
            for sol in sorted(output_dir.glob("sol*.py")):
                result = extract_score(sol)
                score = result.get("fitness") if result else None
                is_valid = result.get("is_valid", 0) if result else 0
                solutions.append({
                    "file": sol.name,
                    "score": score,
                    "is_valid": is_valid,
                })
                if _is_valid_score(result):
                    if best_score is None:
                        best_score = score
                    elif higher_is_better and score > best_score:
                        best_score = score
                    elif not higher_is_better and score < best_score:
                        best_score = score

        # Check for report (means agent is done)
        has_report = (output_dir / "report.md").exists() if output_dir.exists() else False

        # Check for observations
        has_observations = (output_dir / "observations.md").exists() if output_dir.exists() else False

        # Read brief if available
        brief_path = root / "briefs" / gen_str / f"{agent_id}.md"
        brief_snippet = ""
        if brief_path.exists():
            try:
                text = brief_path.read_text()[:500]
                # Extract mission/goal line
                for line in text.split("\n"):
                    if line.strip().startswith("**Mission") or line.strip().startswith("## Mission") or line.strip().startswith("## Goal"):
                        brief_snippet = line.strip()
                        break
                if not brief_snippet:
                    brief_snippet = text[:200].strip()
            except Exception:
                pass

        # Determine status
        if has_report:
            status = "completed"
        elif solutions:
            status = "working"
        else:
            status = "starting"

        # Workspace age
        try:
            created = datetime.fromtimestamp(ws.stat().st_mtime).isoformat(timespec="seconds")
        except Exception:
            created = ""

        agents.append({
            "id": agent_id,
            "gen": gen_num,
            "gen_str": gen_str,
            "agent_type": agent_type,
            "instance": instance,
            "status": status,
            "solutions": solutions,
            "solution_count": len(solutions),
            "best_score": best_score,
            "has_report": has_report,
            "has_observations": has_observations,
            "brief_snippet": brief_snippet,
            "last_modified": created,
        })

    return agents


def get_knowledge_item(kind: str, item_id: str) -> dict | None:
    """Get full details of a single knowledge item."""
    root = _root()

    if kind == "idea":
        ideas_dir = root / "knowledge" / "ideas"
        if ideas_dir.exists():
            for lc_dir in ideas_dir.iterdir():
                if not lc_dir.is_dir():
                    continue
                for f in lc_dir.glob("*.md"):
                    fm = read_frontmatter(f)
                    fid = fm.get("id", f.stem)
                    if fid == item_id or f.stem == item_id:
                        return {
                            "kind": "idea",
                            "id": fid,
                            "title": fm.get("name", fm.get("title", f.stem)),
                            "lifecycle": lc_dir.name,
                            "confidence": fm.get("confidence", fm.get("certainty", "?")),
                            "first_seen": fm.get("first_seen", fm.get("created_gen", "?")),
                            "last_confirmed_gen": fm.get("last_confirmed_gen", "?"),
                            "supported_by": fm.get("supported_by", []),
                            "contradicted_by": fm.get("contradicted_by", []),
                            "related_ideas": fm.get("related_ideas", []),
                            "cluster": fm.get("cluster", ""),
                            "body": read_body(f),
                            "frontmatter": fm,
                        }

    elif kind == "fact":
        facts_dir = root / "knowledge" / "facts"
        if facts_dir.exists():
            for f in facts_dir.glob("*.md"):
                fm = read_frontmatter(f)
                fid = fm.get("id", f.stem)
                if fid == item_id or f.stem == item_id:
                    return {
                        "kind": "fact",
                        "id": fid,
                        "title": fm.get("name", fm.get("title", f.stem)),
                        "confidence": fm.get("confidence", "?"),
                        "verified": fm.get("verified", False),
                        "first_seen": fm.get("first_seen", fm.get("created_gen", "?")),
                        "body": read_body(f),
                        "frontmatter": fm,
                    }

    elif kind == "pattern":
        patterns_dir = root / "knowledge" / "patterns"
        if patterns_dir.exists():
            for lc_dir in patterns_dir.iterdir():
                if not lc_dir.is_dir():
                    continue
                for f in lc_dir.glob("*.md"):
                    fm = read_frontmatter(f)
                    fid = fm.get("id", f.stem)
                    if fid == item_id or f.stem == item_id:
                        return {
                            "kind": "pattern",
                            "id": fid,
                            "title": fm.get("name", fm.get("title", f.stem)),
                            "lifecycle": lc_dir.name,
                            "body": read_body(f),
                            "frontmatter": fm,
                        }

    elif kind == "cluster":
        clusters_dir = root / "knowledge" / "clusters"
        if clusters_dir.exists():
            for f in clusters_dir.glob("*.md"):
                fm = read_frontmatter(f)
                fid = fm.get("id", f.stem)
                if fid == item_id or f.stem == item_id:
                    return {
                        "kind": "cluster",
                        "id": fid,
                        "title": fm.get("name", fm.get("title", f.stem)),
                        "member_ideas": fm.get("member_ideas", fm.get("ideas", [])),
                        "status": fm.get("status", "unknown"),
                        "body": read_body(f),
                        "frontmatter": fm,
                    }

    return None


def get_gen_progress(gen: int) -> dict:
    """Read briefs/genNNN/gen_progress.json for durable per-agent status."""
    root = _root()
    gen_str = f"gen{gen:03d}"
    progress_path = root / "briefs" / gen_str / "gen_progress.json"
    if progress_path.exists():
        try:
            return json.loads(progress_path.read_text())
        except Exception:
            pass
    return {}


def get_knowledge_lifecycle_counts() -> dict:
    """Count ideas by lifecycle stage."""
    root = _root()
    counts = {}
    ideas_dir = root / "knowledge" / "ideas"
    if ideas_dir.exists():
        for lc_dir in ideas_dir.iterdir():
            if lc_dir.is_dir():
                counts[lc_dir.name] = len(list(lc_dir.glob("*.md")))
    return counts


def get_state_of_affairs_staleness() -> dict:
    """Check how stale the State of Affairs is relative to current generation."""
    root = _root()
    soa_path = root / "knowledge" / "state_of_affairs.md"
    result = {"exists": False, "last_updated_gen": None, "current_gen": None, "gens_behind": None}

    if not soa_path.exists():
        return result

    result["exists"] = True

    # Read SOA frontmatter for generation info
    try:
        text = soa_path.read_text()
        if text.startswith("---"):
            import yaml
            end = text.index("---", 3)
            fm = yaml.safe_load(text[3:end])
            if isinstance(fm, dict):
                result["last_updated_gen"] = fm.get("generation", fm.get("last_updated_gen"))
    except Exception:
        pass

    # Current generation from history
    gen_dir = root / "history" / "generations"
    if gen_dir.exists():
        snapshots = sorted(gen_dir.glob("gen*.md"))
        result["current_gen"] = len(snapshots)

    if result["last_updated_gen"] is not None and result["current_gen"] is not None:
        result["gens_behind"] = result["current_gen"] - result["last_updated_gen"]

    return result


def get_frontier_data() -> list[dict]:
    """Compute record-breaking (frontier) solutions with idea annotations.

    Reads all_scores.json, computes running best respecting fitness direction,
    and annotates each frontier point with ideas from solution_idea_map.md.
    """
    import math
    import re

    root = _root()
    all_scores_path = root / "history" / "all_scores.json"
    if not all_scores_path.exists():
        return []

    try:
        all_scores = json.loads(all_scores_path.read_text())
    except Exception:
        return []

    if not all_scores:
        return []

    metrics = get_metrics_config()
    higher_is_better = metrics.get("higher_is_better", True)

    # Parse each entry: [score, path]
    entries = []
    for score, path_str in all_scores:
        if score is None or not isinstance(score, (int, float)):
            continue
        if score == 0.0 or not math.isfinite(score):
            continue
        if _is_sentinel(score):
            continue

        path = Path(path_str)
        gen_num = None
        agent = None
        filename = path.name

        for part in path.parts:
            if part.startswith("gen") and part[3:].isdigit():
                gen_num = int(part[3:])
                break

        # Extract agent from path: .../genNNN/agent_name/solXX.py
        parts = path.parts
        for i, part in enumerate(parts):
            if part.startswith("gen") and part[3:].isdigit():
                if i + 1 < len(parts) and i + 2 <= len(parts):
                    agent = parts[i + 1]
                break

        if gen_num is None:
            continue

        entries.append({
            "gen": gen_num,
            "score": score,
            "agent": agent or "unknown",
            "file": filename,
            "path": path_str,
        })

    # Sort by generation, then by score within gen
    entries.sort(key=lambda e: (e["gen"], e["score"] if not higher_is_better else -e["score"]))

    # Compute running best (frontier)
    frontier = []
    current_best = None
    for entry in entries:
        is_new_record = False
        if current_best is None:
            is_new_record = True
        elif higher_is_better and entry["score"] > current_best:
            is_new_record = True
        elif not higher_is_better and entry["score"] < current_best:
            is_new_record = True

        if is_new_record:
            prev_best = current_best
            current_best = entry["score"]

            delta_pct = None
            if prev_best is not None and prev_best != 0:
                delta_pct = round(((entry["score"] - prev_best) / abs(prev_best)) * 100, 2)

            frontier.append({
                "gen": entry["gen"],
                "score": entry["score"],
                "agent": entry["agent"],
                "file": entry["file"],
                "delta_pct": delta_pct,
                "central_ideas": [],
                "label": None,
            })

    # Parse solution_idea_map.md for idea annotations
    idea_map_path = root / "history" / "solution_idea_map.md"
    if idea_map_path.exists():
        try:
            map_text = idea_map_path.read_text()
            _annotate_frontier_with_ideas(frontier, map_text, re)
        except Exception:
            pass

    return frontier


def _annotate_frontier_with_ideas(frontier: list[dict], map_text: str, re) -> None:
    """Parse solution_idea_map.md and annotate frontier points with central ideas."""
    # Build a lookup: (agent, file) -> central_ideas list
    idea_lookup = {}
    current_key = None

    for line in map_text.split("\n"):
        line = line.strip()

        # Match section headers like ### explore_1/sol01 or ### gen002/explore_1/sol01
        header_match = re.match(r'^###\s+(?:gen\d+/)?([\w]+/sol\d+)', line)
        if header_match:
            key_str = header_match.group(1)  # e.g. "explore_1/sol01"
            parts = key_str.split("/")
            if len(parts) == 2:
                current_key = (parts[0], parts[1] + ".py")
            continue

        # Match Central ideas line
        if current_key and line.startswith("- Central:"):
            ideas_str = line[len("- Central:"):].strip()
            ideas = [i.strip() for i in ideas_str.split(",") if i.strip()]
            idea_lookup[current_key] = ideas

    # Annotate frontier
    for fp in frontier:
        key = (fp["agent"], fp["file"])
        if key in idea_lookup:
            fp["central_ideas"] = idea_lookup[key]
            if fp["central_ideas"]:
                fp["label"] = fp["central_ideas"][0]


def get_eval_cache_stats() -> dict:
    """Stats about the evaluation cache."""
    cache_path = _root() / "history" / "eval_cache.json"
    if not cache_path.exists():
        return {"entries": 0, "size_bytes": 0}
    try:
        data = json.loads(cache_path.read_text())
        return {
            "entries": len(data),
            "size_bytes": cache_path.stat().st_size,
        }
    except Exception:
        return {"entries": 0, "size_bytes": 0}
