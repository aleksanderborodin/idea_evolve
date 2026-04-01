#!/usr/bin/env python3
"""
Migrate Idea Evolve from single-problem layout to multi-problem layout.

Before:
  idea-evolve/
    problem/          -> problems/gemm/
    problem-permcodes/ -> problems/permcodes/
    population/, knowledge/, history/, briefs/, reports/, feedback/, workspace/
      -> runs/gemm/attempt_001/

After:
  idea-evolve/
    problems/{gemm, permcodes}/
    runs/{gemm/attempt_001/, ...}
    agents/, prompts/, user/  (unchanged — global)

Usage:
  python3 migrate_to_multi.py [project_root] [--dry-run]
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


MIGRATION_MARKER = ".migrated"

RUN_STATE_DIRS = [
    "population",
    "knowledge",
    "history",
    "briefs",
    "reports",
    "feedback",
    "workspace",
    "papers",
]


def migrate(project_root: Path, dry_run: bool = False):
    marker = project_root / MIGRATION_MARKER
    if marker.exists():
        print("Already migrated (marker file exists). Aborting.")
        return

    problem_dir = project_root / "problem"
    permcodes_dir = project_root / "problem-permcodes"

    if not problem_dir.exists():
        print(f"ERROR: {problem_dir} does not exist. Nothing to migrate.")
        sys.exit(1)

    problems_dir = project_root / "problems"
    runs_dir = project_root / "runs"

    # --- Step 1: Move problem definitions ---
    print("\n=== Step 1: Move problem definitions ===")

    gemm_dest = problems_dir / "gemm"
    print(f"  {problem_dir} -> {gemm_dest}")
    if not dry_run:
        gemm_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(problem_dir, gemm_dest, dirs_exist_ok=True)

    if permcodes_dir.exists():
        perm_dest = problems_dir / "permcodes"
        print(f"  {permcodes_dir} -> {perm_dest}")
        if not dry_run:
            shutil.copytree(permcodes_dir, perm_dest, dirs_exist_ok=True)

    # --- Step 2: Move run state to runs/gemm/attempt_001/ ---
    print("\n=== Step 2: Move run state directories ===")

    attempt_dir = runs_dir / "gemm" / "attempt_001"
    if not dry_run:
        attempt_dir.mkdir(parents=True, exist_ok=True)

    for dirname in RUN_STATE_DIRS:
        src = project_root / dirname
        if src.exists():
            dest = attempt_dir / dirname
            print(f"  {src} -> {dest}")
            if not dry_run:
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(src, dest, symlinks=True, dirs_exist_ok=True)

    # --- Step 3: Update paths in all_scores.json ---
    print("\n=== Step 3: Update paths in all_scores.json ===")

    all_scores_path = attempt_dir / "history" / "all_scores.json"
    if all_scores_path.exists() or (not dry_run and (project_root / "history" / "all_scores.json").exists()):
        scores_src = all_scores_path if all_scores_path.exists() else project_root / "history" / "all_scores.json"
        try:
            scores = json.loads(scores_src.read_text())
            updated = 0
            new_scores = []
            for score, path_str in scores:
                old_path = str(project_root)
                if old_path in path_str:
                    new_path_str = path_str.replace(old_path, str(attempt_dir))
                    new_scores.append([score, new_path_str])
                    updated += 1
                else:
                    new_scores.append([score, path_str])
            print(f"  Updated {updated}/{len(scores)} paths")
            if not dry_run:
                all_scores_path.write_text(json.dumps(new_scores, indent=2))
        except Exception as e:
            print(f"  WARNING: Failed to update all_scores.json: {e}")

    # --- Step 4: Generate retroactive gen_progress.json ---
    print("\n=== Step 4: Generate retroactive gen_progress.json ===")

    briefs_dir = attempt_dir / "briefs"
    if briefs_dir.exists() or (not dry_run):
        src_briefs = briefs_dir if briefs_dir.exists() else project_root / "briefs"
        if src_briefs.exists():
            import yaml
            for gen_dir in sorted(src_briefs.iterdir()):
                if not gen_dir.is_dir() or not gen_dir.name.startswith("gen"):
                    continue
                progress_path = gen_dir / "gen_progress.json"
                if progress_path.exists():
                    continue  # Already has progress

                gen_str = gen_dir.name
                gen_num = int(gen_str[3:]) if gen_str[3:].isdigit() else 0

                # Check if generation is complete
                snapshot = attempt_dir / "history" / "generations" / f"{gen_str}.md"
                is_complete = snapshot.exists() if not dry_run else (project_root / "history" / "generations" / f"{gen_str}.md").exists()

                if not is_complete:
                    continue

                # Read manifest to know planned agents
                manifest_path = gen_dir / "manifest.yaml"
                agents = {}
                if manifest_path.exists():
                    try:
                        manifest = yaml.safe_load(manifest_path.read_text())
                        for spec in (manifest or {}).get("agents", []):
                            agent_name = f"{spec['type']}_{spec['instance']}"
                            agents[agent_name] = {
                                "status": "complete",
                                "outputs_moved": True,
                            }
                    except Exception:
                        pass

                progress = {
                    "schema_version": 1,
                    "agents": agents,
                    "evaluator": {"status": "complete"},
                    "system_critic": {"status": "complete"},
                    "consistency_review": {"status": "complete"},
                    "finalize": {"status": "complete"},
                    "retroactive": True,
                }
                print(f"  {gen_str}: {len(agents)} agents")
                if not dry_run:
                    progress_path.write_text(json.dumps(progress, indent=2))

    # --- Step 5: Regenerate missing .score files from eval_cache ---
    print("\n=== Step 5: Regenerate missing .score files ===")

    eval_cache_path = attempt_dir / "history" / "eval_cache.json"
    if not eval_cache_path.exists():
        eval_cache_path = project_root / "history" / "eval_cache.json"

    if eval_cache_path.exists():
        try:
            import hashlib
            cache = json.loads(eval_cache_path.read_text())
            pop_dir = attempt_dir / "population" if (attempt_dir / "population").exists() else project_root / "population"
            regenerated = 0
            for sol_path in pop_dir.rglob("sol*.py"):
                score_file = sol_path.with_suffix(".score")
                if score_file.exists():
                    continue
                content_hash = hashlib.sha256(sol_path.read_bytes()).hexdigest()
                if content_hash in cache:
                    result = cache[content_hash]
                    print(f"  Regenerating: {sol_path.relative_to(pop_dir.parent)}")
                    if not dry_run:
                        score_file.write_text(json.dumps(result, indent=2))
                    regenerated += 1
            print(f"  Regenerated {regenerated} .score files")
        except Exception as e:
            print(f"  WARNING: Failed to regenerate .score files: {e}")
    else:
        print("  No eval_cache.json found, skipping")

    # --- Step 6: Write migration marker ---
    if not dry_run:
        marker.write_text(f"Migrated to multi-problem layout\n")
        print(f"\n=== Migration complete! Marker written to {marker} ===")
        print("\nOriginal directories preserved. Once verified, you can remove:")
        for dirname in RUN_STATE_DIRS:
            if (project_root / dirname).exists():
                print(f"  rm -rf {project_root / dirname}")
        if problem_dir.exists():
            print(f"  rm -rf {problem_dir}")
        if permcodes_dir.exists():
            print(f"  rm -rf {permcodes_dir}")
    else:
        print("\n=== DRY RUN complete — no changes made ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Idea Evolve to multi-problem layout")
    parser.add_argument("project_root", nargs="?", default=".", help="Project root")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    migrate(project_root, dry_run=args.dry_run)
