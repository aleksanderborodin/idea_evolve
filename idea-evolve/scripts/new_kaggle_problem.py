#!/usr/bin/env python3
"""Scaffold a new Kaggle-as-idea-evolve problem.

Usage:
    python3 scripts/new_kaggle_problem.py <kaggle_id> <problem_id> --class A|B|C|D
    python3 scripts/new_kaggle_problem.py --refresh <problem_id>
    python3 scripts/new_kaggle_problem.py --dry-run <kaggle_id> <problem_id>

Behavior:
- Validates KAGGLE_API_TOKEN is set (sourced from .env via `set -a && source .env && set +a`).
- Copies problems/_kaggle_template/ → problems/<problem_id>/.
- Downloads competition data via `kaggle competitions download -c <id> -p problems/<id>/data/ --unzip`.
- Catches HTTP 403 → prints TOS-acceptance instructions (must click "Understand and Accept" on kaggle.com).
- Writes problems/<id>/data/.kaggle_spec.yaml with competition_id, classification, UTC timestamp, sha256 per file.
- --refresh: re-downloads, diffs hashes, warns if anything changed (operator must clear eval_cache).

See docs/problem_design_guide.md §13 for the full Kaggle-problem workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"

sys.path.insert(0, str(REPO_ROOT))
from problems._shared.constants import (  # noqa: E402
    KAGGLE_API_TOKEN_ENV,
    KAGGLE_PROBLEM_SKELETON,
    KAGGLE_SPEC_FILENAME,
    DATA_SUBDIR,
)


SKELETON_DIR = PROBLEMS_DIR / KAGGLE_PROBLEM_SKELETON
SIZE_WARN_BYTES = 1 * 1024 * 1024 * 1024  # warn above 1 GB


def _check_token() -> None:
    if not os.environ.get(KAGGLE_API_TOKEN_ENV):
        print(
            f"ERROR: {KAGGLE_API_TOKEN_ENV} is not set.\n"
            f"  Generate at https://www.kaggle.com/settings → API → Create New API Token,\n"
            f"  then add to .env and `set -a && source .env && set +a`.",
            file=sys.stderr,
        )
        sys.exit(2)


def _kaggle_cli() -> str:
    cli = shutil.which("kaggle")
    if not cli:
        print("ERROR: 'kaggle' CLI not found on PATH. `pip install kaggle`.", file=sys.stderr)
        sys.exit(2)
    return cli


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def _file_hashes(data_dir: Path) -> dict[str, str]:
    out = {}
    for p in sorted(data_dir.iterdir()):
        if p.is_file() and p.name != KAGGLE_SPEC_FILENAME:
            out[p.name] = _sha256_file(p)
    return out


def _download(comp_id: str, dest: Path, dry_run: bool = False) -> None:
    """Download competition zip and unpack. Kaggle CLI 2.x dropped --unzip,
    so we unzip + delete the archive ourselves."""
    cli = _kaggle_cli()
    dest.mkdir(parents=True, exist_ok=True)
    cmd = [cli, "competitions", "download", comp_id, "-p", str(dest), "-o"]
    if dry_run:
        print(f"DRY RUN: {' '.join(cmd)} && unzip -o <zip>")
        return
    print(f"Downloading {comp_id} → {dest}/ ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        out = (res.stdout or "") + (res.stderr or "")
        if "403" in out or "Forbidden" in out:
            print(
                f"\nERROR: HTTP 403 from Kaggle. You must accept the competition rules first:\n"
                f"  https://www.kaggle.com/competitions/{comp_id}/rules\n"
                f"  Click 'Understand and Accept', then re-run this script.\n",
                file=sys.stderr,
            )
        else:
            print(out, file=sys.stderr)
        sys.exit(1)
    print(res.stdout)
    # Unpack any *.zip and delete the archive.
    import zipfile
    for z in dest.glob("*.zip"):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(dest)
        z.unlink()


def _copy_skeleton(target: Path, dry_run: bool = False) -> None:
    if not SKELETON_DIR.exists():
        print(f"ERROR: skeleton not found at {SKELETON_DIR}", file=sys.stderr)
        sys.exit(2)
    if target.exists():
        print(
            f"ERROR: {target} already exists. Refusing to overwrite.\n"
            f"  Use --refresh <id> to re-download data only.",
            file=sys.stderr,
        )
        sys.exit(1)
    if dry_run:
        print(f"DRY RUN: copytree {SKELETON_DIR} → {target}")
        return
    shutil.copytree(SKELETON_DIR, target)


def _write_spec(
    spec_path: Path,
    comp_id: str,
    classification: str,
    file_hashes: dict[str, str],
    dry_run: bool = False,
) -> None:
    strategy_default = {
        "A": "self_check",
        "B": "self_check",
        "C": "holdout_split",
        "D": "simulator",
    }.get(classification, "<REPLACE>")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    body = (
        f"competition_id: {comp_id}\n"
        f"classification: {classification}\n"
        f"local_eval_strategy: {strategy_default}\n"
        f"primary_metric_name: <REPLACE>\n"
        f"primary_metric_direction: <REPLACE>\n"
        f"primary_metric_kaggle_leaderboard_top: <REPLACE>\n"
        f"downloaded_at: {now}\n"
        f"file_hashes:\n"
    )
    for fname, h in file_hashes.items():
        body += f"  {fname}: {h}\n"
    body += (
        f"holdout_spec: null\n"
        f"simulator_spec: null\n"
        f"tos_accepted_by: {os.environ.get('USER', '<REPLACE>')}\n"
        f"tos_accepted_at: {now}\n"
    )
    if dry_run:
        print(f"DRY RUN: write {spec_path}\n---\n{body}---")
        return
    spec_path.write_text(body)


def cmd_new(comp_id: str, problem_id: str, classification: str, dry_run: bool) -> int:
    _check_token()
    target = PROBLEMS_DIR / problem_id
    data_dir = target / DATA_SUBDIR
    spec_path = data_dir / KAGGLE_SPEC_FILENAME

    _copy_skeleton(target, dry_run)
    # Skeleton copies a placeholder spec; remove it before populating real one.
    if not dry_run and spec_path.exists():
        spec_path.unlink()
    _download(comp_id, data_dir, dry_run)
    if dry_run:
        print(f"DRY RUN: would write {spec_path}")
        return 0
    hashes = _file_hashes(data_dir)
    total_bytes = sum(p.stat().st_size for p in data_dir.iterdir() if p.is_file())
    if total_bytes > SIZE_WARN_BYTES:
        print(f"WARNING: data dir is {total_bytes/1e9:.2f} GB. Confirm you want this committed-by-spec.")
    _write_spec(spec_path, comp_id, classification, hashes)
    print(
        f"\n✓ Scaffolded {target}\n"
        f"  Data: {data_dir} ({len(hashes)} files, {total_bytes/1e6:.1f} MB)\n"
        f"  Spec: {spec_path}\n\n"
        f"Next: fill in the <PLACEHOLDER> tags following docs/problem_design_guide.md §13.\n"
    )
    return 0


def cmd_refresh(problem_id: str) -> int:
    _check_token()
    target = PROBLEMS_DIR / problem_id
    data_dir = target / DATA_SUBDIR
    spec_path = data_dir / KAGGLE_SPEC_FILENAME
    if not spec_path.exists():
        print(f"ERROR: {spec_path} missing. Run without --refresh first.", file=sys.stderr)
        return 1
    import yaml  # local import; PyYAML is in requirements.txt
    spec = yaml.safe_load(spec_path.read_text()) or {}
    comp_id = spec.get("competition_id")
    if not comp_id:
        print(f"ERROR: {spec_path} missing competition_id", file=sys.stderr)
        return 1
    old = dict(spec.get("file_hashes") or {})

    # Re-download (kaggle CLI overwrites in place)
    _download(comp_id, data_dir, dry_run=False)
    new = _file_hashes(data_dir)
    spec["file_hashes"] = new
    spec["downloaded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False))

    changed = [k for k in new if old.get(k) != new[k]]
    added = [k for k in new if k not in old]
    removed = [k for k in old if k not in new]
    if changed or added or removed:
        print("\n⚠ Data has changed since last download:")
        for k in added:    print(f"  +  {k}")
        for k in changed:  print(f"  ~  {k}")
        for k in removed:  print(f"  -  {k}")
        print(
            "\nClear cached eval results so agents re-score against the new data:\n"
            f"  rm -f runs/{problem_id}/*/history/eval_cache.json\n"
        )
    else:
        print("\n✓ Data unchanged; eval cache remains valid.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("kaggle_id", nargs="?")
    ap.add_argument("problem_id", nargs="?")
    ap.add_argument("--class", dest="classification", choices=["A", "B", "C", "D", "E"])
    ap.add_argument("--refresh", metavar="PROBLEM_ID", help="Re-download data; report hash changes.")
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen, don't write.")
    args = ap.parse_args()

    if args.refresh:
        return cmd_refresh(args.refresh)
    if not args.kaggle_id or not args.problem_id:
        ap.error("kaggle_id and problem_id are required (or use --refresh)")
    if not args.classification and not args.dry_run:
        ap.error("--class A|B|C|D is required (see docs/problem_design_guide.md §13.1)")
    if args.classification == "E":
        ap.error("Class E (proprietary/TOS-blocked data) is not supported. See §13.1.")
    return cmd_new(args.kaggle_id, args.problem_id, args.classification or "A", args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
