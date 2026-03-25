"""Filesystem scanning for Alpha Evolve project state.

Each function scans the alpha-evolve/ directory tree and returns
structured data. No caching — reads fresh on each call.
"""

import json
from datetime import datetime
from pathlib import Path

from .config import get_project_root
from .helpers import read_frontmatter, read_body, extract_score, get_metrics_config


def _root() -> Path:
    return get_project_root()


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
    if (ws / f"{gen_str}_consistency_reviewer" / "output" / "state_of_affairs.md").exists():
        return "consistency_done"
    if (ws / f"{gen_str}_system_critic" / "output" / "system_analysis.md").exists():
        return "critic_done"

    ev_output = ws / f"{gen_str}_evaluator" / "output"
    if ev_output.exists():
        if any([
            (ev_output / "evaluator_report.md").exists(),
            (ev_output / "generation_snapshot.md").exists(),
        ]):
            return "evaluator_done"

    # Check if agents are still running (workspace dirs exist)
    ws_dir = root / "workspace"
    agent_workspaces = list(ws_dir.glob(f"{gen_str}_*")) if ws_dir.exists() else []

    pop_dir = root / "population" / gen_str
    reports_dir = root / "reports" / gen_str
    has_output = (
        (pop_dir.exists() and any(pop_dir.iterdir()))
        or (reports_dir.exists() and any(reports_dir.iterdir()))
    )

    if has_output:
        # If workspace dirs still exist, agents are still running
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

        if not any([has_briefs, has_pop, has_reports, has_snapshot]):
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
                        if result and result.get("fitness") is not None and result.get("is_valid", 1):
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
                        if result and result.get("fitness") is not None and result.get("is_valid", 1):
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
                    "size": sol.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        sol.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                })

    metrics = get_metrics_config()
    higher_is_better = metrics.get("higher_is_better", True)
    if higher_is_better:
        solutions.sort(key=lambda x: x.get("score") if x.get("score") is not None else -9999, reverse=True)
    else:
        solutions.sort(key=lambda x: x.get("score") if x.get("score") is not None else 9999)
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
    """Parse score_progression.md into data points."""
    prog_path = _root() / "history" / "score_progression.md"
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
    """Get scores for initial/baseline programs."""
    root = _root()
    init_dir = root / "problem" / "initial_programs"
    results = []
    if not init_dir.exists():
        return results
    for sol in sorted(init_dir.glob("*.py")):
        result = extract_score(sol)
        results.append({
            "file": sol.name,
            "score": result.get("fitness") if result else None,
            "is_valid": result.get("is_valid", 0) if result else 0,
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
                "content": f.read_text()[:5000],
                "size": f.stat().st_size,
            })
    return reports


# ---------------------------------------------------------------------------
# File Tree
# ---------------------------------------------------------------------------

def get_file_tree() -> dict:
    """Build a tree of all alpha-evolve files grouped by top-level directory."""
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

    for ws in sorted(ws_dir.iterdir()):
        if not ws.is_dir():
            continue
        name = ws.name  # e.g. gen003_explore_1
        parts = name.split("_", 1)
        if len(parts) < 2:
            continue
        gen_str = parts[0]
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
                if score is not None and is_valid:
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
