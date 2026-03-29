"""JSON API endpoints for the dashboard frontend."""

from flask import Blueprint, jsonify

from dashboard.data import (
    get_active_agents,
    get_config,
    get_coverage_matrix,
    get_eval_cache_stats,
    get_feedback,
    get_file_tree,
    get_generation_status,
    get_initial_scores,
    get_knowledge,
    get_knowledge_item,
    get_manifest,
    get_phase_status,
    get_reports,
    get_run_state,
    get_score_progression,
    get_solution_idea_map,
    get_solutions,
    get_timing_data,
)
from dashboard.data.helpers import get_metrics_config

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/overview")
def overview():
    config = get_config()
    metrics = get_metrics_config()
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
    root = get_project_root()
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
