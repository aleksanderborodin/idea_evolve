"""JSON API endpoints for the dashboard frontend."""

import json
import os
from pathlib import Path

from flask import Blueprint, jsonify, request

from dashboard.data import (
    get_active_agents,
    get_config,
    get_coverage_matrix,
    get_eval_cache_stats,
    get_feedback,
    get_file_tree,
    get_gen_progress,
    get_generation_status,
    get_initial_scores,
    get_knowledge,
    get_knowledge_item,
    get_knowledge_lifecycle_counts,
    get_manifest,
    get_phase_status,
    get_reports,
    get_run_state,
    get_score_progression,
    get_solution_idea_map,
    get_solutions,
    get_state_of_affairs_staleness,
    get_timing_data,
    get_frontier_data,
    list_problems,
    list_attempts,
    get_run_root,
    get_problem_dir,
)
from dashboard.data.helpers import get_metrics_config

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _resolve_context():
    """Extract problem/attempt from query params and resolve paths.

    Returns (run_root, problem_dir) — either or both may be None.
    """
    problem = request.args.get("problem")
    attempt = request.args.get("attempt")
    run_root = get_run_root(problem, attempt) if problem else None
    problem_dir = get_problem_dir(problem) if problem else get_problem_dir()
    return run_root, problem_dir


# ---------------------------------------------------------------------------
# Problem / Attempt Discovery
# ---------------------------------------------------------------------------

@api_bp.route("/problems")
def problems():
    """List all problems with their attempts and summary stats."""
    result = []
    for pid in list_problems():
        pdir = get_problem_dir(pid)

        # Read problem name from description.md first line
        name = pid
        desc_first_line = ""
        desc_path = pdir / "description.md"
        if desc_path.exists():
            try:
                lines = desc_path.read_text().splitlines()
                for line in lines:
                    stripped = line.strip().lstrip("# ").strip()
                    if stripped:
                        name = stripped
                        break
                # First non-title content line
                for line in lines[1:]:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        desc_first_line = stripped[:120]
                        break
            except Exception:
                pass

        # Read metrics
        metrics = get_metrics_config(problem_dir=pdir)
        target_score = metrics.get("target_score")
        higher_is_better = metrics.get("higher_is_better", True)
        decimals = metrics.get("decimals", 4)

        # Build attempts
        attempts_list = []
        for aid in list_attempts(pid):
            rroot = get_run_root(pid, aid)
            if rroot is None:
                continue

            # Count generations
            gen_dir = rroot / "history" / "generations"
            gen_count = len(list(gen_dir.glob("gen*.md"))) if gen_dir.is_dir() else 0

            # Count solutions
            pop_dir = rroot / "population"
            sol_count = 0
            if pop_dir.is_dir():
                for gd in pop_dir.iterdir():
                    if gd.is_dir() and gd.name.startswith("gen"):
                        for ad in gd.iterdir():
                            if ad.is_dir():
                                sol_count += len(list(ad.glob("sol*.py")))

            # Best score from all_scores.json
            best_score = None
            scores_path = rroot / "history" / "all_scores.json"
            if scores_path.exists():
                try:
                    all_scores = json.loads(scores_path.read_text())
                    for score, _path in all_scores:
                        if score is None or not isinstance(score, (int, float)):
                            continue
                        if best_score is None:
                            best_score = score
                        elif higher_is_better and score > best_score:
                            best_score = score
                        elif not higher_is_better and score < best_score:
                            best_score = score
                except Exception:
                    pass

            # Run state / status
            status = "idle"
            state_path = rroot / "history" / "run_state.json"
            if state_path.exists():
                try:
                    rs = json.loads(state_path.read_text())
                    pid_val = rs.get("pid")
                    pid_alive = False
                    if pid_val:
                        try:
                            os.kill(pid_val, 0)
                            pid_alive = True
                        except (OSError, ProcessLookupError):
                            pass
                    if pid_alive and rs.get("status") == "running":
                        status = "running"
                    elif not pid_alive and rs.get("status") == "running":
                        status = "crashed"
                except Exception:
                    pass

            attempts_list.append({
                "id": aid,
                "generations_completed": gen_count,
                "best_score": best_score,
                "total_solutions": sol_count,
                "status": status,
            })

        result.append({
            "id": pid,
            "name": name,
            "description_first_line": desc_first_line,
            "target_score": target_score,
            "higher_is_better": higher_is_better,
            "decimals": decimals,
            "attempts": attempts_list,
        })

    return jsonify(result)


@api_bp.route("/overview")
def overview():
    run_root, problem_dir = _resolve_context()
    config = get_config()
    metrics = get_metrics_config(problem_dir=problem_dir)
    generations = get_generation_status()
    progression = get_score_progression()
    timing = get_timing_data()
    cache_stats = get_eval_cache_stats()
    initial_scores = get_initial_scores()
    run_state = get_run_state()

    # Compute stats from generations — respect fitness direction
    higher_is_better = metrics.get("higher_is_better", True)
    best_score = None
    total_solutions = 0
    for g in generations:
        s = g["best_score"]
        if s is not None:
            if best_score is None:
                best_score = s
            elif higher_is_better and s > best_score:
                best_score = s
            elif not higher_is_better and s < best_score:
                best_score = s
        total_solutions += g["solutions"]

    completed_gens = sum(1 for g in generations if g["status"] == "complete")
    current_gen = generations[-1]["gen"] if generations else 0
    current_phase = generations[-1]["status"] if generations else "not_started"

    # Prefer run_state phase when orchestrator is actively running (more accurate)
    if run_state.get("is_running") and run_state.get("current_phase"):
        current_phase = run_state["current_phase"]
        if run_state.get("current_gen"):
            current_gen = run_state["current_gen"]

    # Quick knowledge counts (avoid full scan — just count files)
    from dashboard.data.config import get_project_root
    root = run_root if run_root is not None else get_project_root()
    idea_count = sum(
        len(list(d.glob("*.md")))
        for d in (root / "knowledge" / "ideas").iterdir()
        if d.is_dir()
    ) if (root / "knowledge" / "ideas").exists() else 0
    fact_count = len(list((root / "knowledge" / "facts").glob("*.md"))) if (root / "knowledge" / "facts").exists() else 0
    pattern_count = sum(
        len(list(d.glob("*.md")))
        for d in (root / "knowledge" / "patterns").iterdir()
        if d.is_dir()
    ) if (root / "knowledge" / "patterns").exists() else 0
    cluster_count = len(list((root / "knowledge" / "clusters").glob("*.md"))) if (root / "knowledge" / "clusters").exists() else 0

    # Build agent types from config
    agent_purposes = {
        "explore": "Novel approaches",
        "exploit": "Refine top solutions",
        "genetic": "Crossover parents",
        "full": "Full autonomy",
        "research": "Math research",
        "experimentator": "Test hypotheses",
    }
    max_turns_cfg = config.get("max_turns", {})
    agent_types = []
    for atype, aconf in config.get("agents", {}).items():
        if not isinstance(aconf, dict):
            continue
        agent_types.append({
            "type": atype,
            "enabled": aconf.get("enabled", True),
            "max_instances": aconf.get("max_instances", 3),
            "max_turns": max_turns_cfg.get(atype, 150),
            "model": aconf.get("model", "sonnet"),
            "purpose": agent_purposes.get(atype, ""),
        })

    # Count valid solutions
    all_sols = get_solutions()
    valid_solutions = sum(1 for s in all_sols if s.get("is_valid"))

    # Compute baseline: from initial programs, or from first generation's worst valid score
    sentinel = metrics.get("sentinel_value")
    init_vals = [s["score"] for s in initial_scores
                 if s.get("score") is not None and s.get("score") != sentinel]
    if init_vals:
        baseline_score = min(init_vals) if not higher_is_better else max(init_vals)
    elif generations:
        first_gen_score = generations[0].get("best_score")
        baseline_score = first_gen_score if first_gen_score != sentinel else None
    else:
        baseline_score = None

    # Knowledge staleness and lifecycle counts
    soa_staleness = get_state_of_affairs_staleness()
    lifecycle_counts = get_knowledge_lifecycle_counts()

    return jsonify({
        "config": {
            "target_score": metrics.get("target_score", config.get("target_score")),
            "total_generations": config.get("generations", 30),
            "max_parallel": config.get("max_parallel_sessions", 10),
            "higher_is_better": higher_is_better,
            "decimals": metrics.get("decimals", 4),
            "baseline_score": baseline_score,
            "sentinel_value": sentinel,
        },
        "agent_types": agent_types,
        "stats": {
            "best_score": best_score,
            "target_score": metrics.get("target_score", config.get("target_score")),
            "total_solutions": total_solutions,
            "valid_solutions": valid_solutions,
            "total_ideas": idea_count,
            "total_facts": fact_count,
            "total_patterns": pattern_count,
            "total_clusters": cluster_count,
            "completed_gens": completed_gens,
            "current_gen": current_gen,
            "current_phase": current_phase,
        },
        "generations": generations,
        "progression": progression,
        "timing": timing,
        "eval_cache": cache_stats,
        "initial_scores": initial_scores,
        "run_state": run_state,
        "soa_staleness": soa_staleness,
        "lifecycle_counts": lifecycle_counts,
    })


@api_bp.route("/solutions")
def solutions():
    return jsonify(get_solutions())


@api_bp.route("/knowledge")
def knowledge():
    return jsonify(get_knowledge())


@api_bp.route("/knowledge/coverage")
def coverage():
    return jsonify({
        "coverage_matrix": get_coverage_matrix(),
        "solution_idea_map": get_solution_idea_map(),
    })


@api_bp.route("/reports")
def reports():
    return jsonify(get_reports())


@api_bp.route("/reports/<int:gen>")
def reports_gen(gen):
    return jsonify(get_reports(gen))


@api_bp.route("/agents/active")
def active_agents():
    return jsonify(get_active_agents())


@api_bp.route("/knowledge/<kind>/<item_id>")
def knowledge_item(kind, item_id):
    item = get_knowledge_item(kind, item_id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@api_bp.route("/files")
def files():
    return jsonify(get_file_tree())


@api_bp.route("/feedback")
def feedback():
    return jsonify(get_feedback())


@api_bp.route("/generation/<int:gen>/progress")
def generation_progress(gen):
    return jsonify(get_gen_progress(gen))


@api_bp.route("/generation/<int:gen>")
def generation(gen):
    gen_str = f"gen{gen:03d}"
    result = {
        "gen": gen,
        "status": get_phase_status(gen),
        "manifest": get_manifest(gen),
        "reports": get_reports(gen),
        "solutions": [s for s in get_solutions() if s["gen"] == gen],
    }

    from dashboard.data.config import get_project_root
    snapshot_path = get_project_root() / "history" / "generations" / f"{gen_str}.md"
    if snapshot_path.exists():
        result["snapshot"] = snapshot_path.read_text()[:5000]

    return jsonify(result)


@api_bp.route("/frontier")
def frontier():
    """Return record-breaking (frontier) solutions with idea annotations."""
    return jsonify({"frontier": get_frontier_data()})
