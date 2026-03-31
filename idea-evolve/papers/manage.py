#!/usr/bin/env python3
"""Paper management pipeline: find → download → extract → summarize → index.

Usage:
    python3 papers/manage.py list                          # show all papers
    python3 papers/manage.py add <arxiv_id> [--name SHORT_NAME] [--by AGENT_ID]
    python3 papers/manage.py add-doi <doi> [--name SHORT_NAME] [--by AGENT_ID]
    python3 papers/manage.py add-url <url> [--name SHORT_NAME] [--by AGENT_ID]
    python3 papers/manage.py status                        # pipeline status summary
    python3 papers/manage.py summarize <paper_id>          # mark as summarized (agent writes summary)

All papers go through: found → downloaded → extracted → summarized
Files are named: NNN_shortname_author.{pdf,md}
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

SCRIPT_DIR = Path(__file__).parent
INDEX_PATH = SCRIPT_DIR / "index.yaml"
PDF_DIR = SCRIPT_DIR / "pdf"
MD_DIR = SCRIPT_DIR / "md"
SUMMARY_DIR = SCRIPT_DIR / "summaries"

for d in [PDF_DIR, MD_DIR, SUMMARY_DIR]:
    d.mkdir(exist_ok=True)


def _load_index():
    import yaml
    if INDEX_PATH.exists():
        return yaml.safe_load(INDEX_PATH.read_text()) or {"papers": [], "next_id": 1}
    return {"papers": [], "next_id": 1}


def _save_index(index):
    import yaml
    INDEX_PATH.write_text(yaml.dump(index, default_flow_style=False, sort_keys=False, allow_unicode=True))


def _make_filename(paper_id, name):
    """Create filename like 001_shortname."""
    return f"{paper_id:03d}_{name}"


def _slugify(text, max_len=40):
    """Convert text to a clean filename slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text[:max_len].rstrip('_')


def _fetch_arxiv_metadata(arxiv_id):
    """Fetch title and authors from arXiv API."""
    clean_id = re.sub(r'v\d+$', '', arxiv_id)
    url = f"http://export.arxiv.org/api/query?id_list={clean_id}"
    try:
        req = Request(url, headers={"User-Agent": "IdeaEvolve/1.0"})
        response = urlopen(req, timeout=10)
        xml = response.read().decode()

        # Simple XML parsing (no lxml dependency)
        title_match = re.search(r'<title[^>]*>(.*?)</title>', xml, re.DOTALL)
        # Skip the feed title, get the entry title
        titles = re.findall(r'<title[^>]*>(.*?)</title>', xml, re.DOTALL)
        title = titles[-1].strip().replace('\n', ' ') if len(titles) > 1 else "unknown"

        authors = re.findall(r'<name>(.*?)</name>', xml)
        return title, authors
    except Exception as e:
        print(f"  Warning: Could not fetch metadata: {e}")
        return "unknown", []


def _extract_text(pdf_path, md_path):
    """Extract text from PDF to markdown."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            md_path.write_text(result.stdout)
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    md_path.write_text(
        f"# Text extraction failed\n\nRead the PDF directly: `{pdf_path}`\n"
    )
    return False


def _download_pdf(url, pdf_path):
    """Download a PDF file."""
    try:
        subprocess.run(
            ["curl", "-sL", "-o", str(pdf_path), url],
            timeout=60, check=True,
        )
        # Verify it's a PDF
        result = subprocess.run(["file", str(pdf_path)], capture_output=True, text=True)
        if "PDF" in result.stdout:
            return True
        print(f"  Warning: Downloaded file is not a PDF: {result.stdout.strip()}")
        return False
    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def cmd_add(args):
    """Add an arXiv paper: download, extract, index."""
    index = _load_index()
    arxiv_id = args.identifier.strip()
    clean_id = re.sub(r'v\d+$', '', arxiv_id)

    # Check if already indexed
    for p in index["papers"]:
        if clean_id in p.get("source", ""):
            print(f"  Already indexed as {p['id']:03d}_{p['name']} (status: {p['status']})")
            return

    # Fetch metadata
    print(f"  Fetching metadata for arxiv:{clean_id}...")
    title, authors = _fetch_arxiv_metadata(clean_id)
    first_author = _slugify(authors[0].split()[-1]) if authors else "unknown"

    # Build name
    if args.name:
        short_name = _slugify(args.name)
    else:
        # Auto-generate from title + first author
        title_slug = _slugify(title, max_len=30)
        short_name = f"{title_slug}_{first_author}" if title_slug != "unknown" else f"arxiv_{clean_id.replace('.', '')}"

    paper_id = index["next_id"]
    filename = _make_filename(paper_id, short_name)
    pdf_path = PDF_DIR / f"{filename}.pdf"
    md_path = MD_DIR / f"{filename}.md"
    summary_path = SUMMARY_DIR / f"{filename}.md"

    # Download
    url = f"https://arxiv.org/pdf/{clean_id}.pdf"
    print(f"  Downloading {url}...")
    if not _download_pdf(url, pdf_path):
        print("  FAILED: Could not download PDF")
        return

    # Extract text
    print(f"  Extracting text...")
    extracted = _extract_text(pdf_path, md_path)

    # Add frontmatter to md
    content = md_path.read_text()
    header = (
        f"---\n"
        f"paper_id: {paper_id:03d}\n"
        f"title: \"{title}\"\n"
        f"authors: {json.dumps(authors)}\n"
        f"source: \"arxiv:{clean_id}\"\n"
        f"url: \"{url}\"\n"
        f"---\n\n"
    )
    md_path.write_text(header + content)

    # Update index
    entry = {
        "id": paper_id,
        "name": short_name,
        "title": title,
        "authors": authors,
        "source": f"arxiv:{clean_id}",
        "url": url,
        "status": "extracted" if extracted else "downloaded",
        "relevance": "unknown",
        "pdf": str(pdf_path.relative_to(SCRIPT_DIR)),
        "md": str(md_path.relative_to(SCRIPT_DIR)),
        "summary": str(summary_path.relative_to(SCRIPT_DIR)),
        "found_by": args.by or "manual",
        "notes": "",
    }
    index["papers"].append(entry)
    index["next_id"] = paper_id + 1
    _save_index(index)

    print(f"\n  Added: {filename}")
    print(f"  Title: {title}")
    print(f"  Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
    print(f"  Status: {entry['status']}")
    print(f"  Text: {md_path}")
    print(f"  Summary needed: {summary_path}")


def cmd_add_doi(args):
    """Add a paper by DOI."""
    index = _load_index()
    doi = args.identifier.strip()

    for p in index["papers"]:
        if doi in p.get("source", ""):
            print(f"  Already indexed as {p['id']:03d}_{p['name']}")
            return

    paper_id = index["next_id"]
    short_name = args.name or f"doi_{_slugify(doi, max_len=30)}"
    short_name = _slugify(short_name)
    filename = _make_filename(paper_id, short_name)
    pdf_path = PDF_DIR / f"{filename}.pdf"
    md_path = MD_DIR / f"{filename}.md"
    summary_path = SUMMARY_DIR / f"{filename}.md"

    # Try Sci-Hub mirrors
    downloaded = False
    for mirror in ["https://sci-hub.se", "https://sci-hub.st", "https://sci-hub.ru"]:
        print(f"  Trying {mirror}/{doi}...")
        if _download_pdf(f"{mirror}/{doi}", pdf_path):
            downloaded = True
            break

    if not downloaded:
        print("  FAILED: Could not download from any mirror")
        # Still index as "found" so we don't retry
        entry = {
            "id": paper_id, "name": short_name, "title": "unknown",
            "authors": [], "source": f"doi:{doi}", "url": "",
            "status": "found", "relevance": "unknown",
            "pdf": "", "md": "", "summary": str(summary_path.relative_to(SCRIPT_DIR)),
            "found_by": args.by or "manual", "notes": "download failed",
        }
        index["papers"].append(entry)
        index["next_id"] = paper_id + 1
        _save_index(index)
        return

    extracted = _extract_text(pdf_path, md_path)

    entry = {
        "id": paper_id, "name": short_name, "title": "unknown (DOI)",
        "authors": [], "source": f"doi:{doi}", "url": f"doi:{doi}",
        "status": "extracted" if extracted else "downloaded",
        "relevance": "unknown",
        "pdf": str(pdf_path.relative_to(SCRIPT_DIR)),
        "md": str(md_path.relative_to(SCRIPT_DIR)),
        "summary": str(summary_path.relative_to(SCRIPT_DIR)),
        "found_by": args.by or "manual", "notes": "",
    }
    index["papers"].append(entry)
    index["next_id"] = paper_id + 1
    _save_index(index)
    print(f"\n  Added: {filename} (status: {entry['status']})")


def cmd_add_url(args):
    """Add a paper by direct URL."""
    index = _load_index()
    url = args.identifier.strip()

    paper_id = index["next_id"]
    short_name = _slugify(args.name or f"paper_{paper_id}", max_len=40)
    filename = _make_filename(paper_id, short_name)
    pdf_path = PDF_DIR / f"{filename}.pdf"
    md_path = MD_DIR / f"{filename}.md"
    summary_path = SUMMARY_DIR / f"{filename}.md"

    print(f"  Downloading {url}...")
    if not _download_pdf(url, pdf_path):
        print("  FAILED")
        return

    extracted = _extract_text(pdf_path, md_path)

    entry = {
        "id": paper_id, "name": short_name, "title": "unknown",
        "authors": [], "source": url, "url": url,
        "status": "extracted" if extracted else "downloaded",
        "relevance": "unknown",
        "pdf": str(pdf_path.relative_to(SCRIPT_DIR)),
        "md": str(md_path.relative_to(SCRIPT_DIR)),
        "summary": str(summary_path.relative_to(SCRIPT_DIR)),
        "found_by": args.by or "manual", "notes": "",
    }
    index["papers"].append(entry)
    index["next_id"] = paper_id + 1
    _save_index(index)
    print(f"\n  Added: {filename} (status: {entry['status']})")


def cmd_summarize(args):
    """Mark a paper as summarized (agent should have written the summary file)."""
    index = _load_index()
    pid = int(args.paper_id)
    for p in index["papers"]:
        if p["id"] == pid:
            summary_path = SCRIPT_DIR / p["summary"]
            if summary_path.exists():
                p["status"] = "summarized"
                _save_index(index)
                print(f"  {pid:03d}_{p['name']}: marked as summarized")
            else:
                print(f"  Summary file missing: {summary_path}")
                print(f"  Write the summary first, then run this command.")
            return
    print(f"  Paper {pid} not found in index")


def cmd_list(args):
    """List all indexed papers."""
    index = _load_index()
    if not index["papers"]:
        print("  No papers indexed yet.")
        print("  Use: python3 papers/manage.py add <arxiv_id>")
        return

    print(f"  {'ID':>3}  {'STATUS':<11}  {'REL':<7}  {'NAME':<40}  {'SOURCE'}")
    print(f"  {'---':>3}  {'-'*11}  {'-'*7}  {'-'*40}  {'-'*30}")
    for p in index["papers"]:
        pid = f"{p['id']:03d}"
        status = p["status"]
        rel = p.get("relevance", "?")
        name = p["name"][:40]
        source = p.get("source", "")
        print(f"  {pid}  {status:<11}  {rel:<7}  {name:<40}  {source}")


def cmd_status(args):
    """Show pipeline status summary."""
    index = _load_index()
    papers = index["papers"]
    total = len(papers)
    if total == 0:
        print("  No papers yet.")
        return

    counts = {}
    for p in papers:
        s = p["status"]
        counts[s] = counts.get(s, 0) + 1

    print(f"  Total papers: {total}")
    for stage in ["found", "downloaded", "extracted", "summarized"]:
        c = counts.get(stage, 0)
        bar = "█" * c + "░" * (total - c)
        print(f"  {stage:<12}: {c:>3} / {total}  {bar}")

    needs_summary = [p for p in papers if p["status"] == "extracted"]
    if needs_summary:
        print(f"\n  Papers needing summary:")
        for p in needs_summary:
            print(f"    {p['id']:03d}_{p['name']}: {p.get('title', '?')[:60]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paper management pipeline")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add arXiv paper")
    p_add.add_argument("identifier", help="arXiv ID (e.g. 2301.12345)")
    p_add.add_argument("--name", help="Short name override")
    p_add.add_argument("--by", help="Agent that found this paper")

    p_doi = sub.add_parser("add-doi", help="Add paper by DOI")
    p_doi.add_argument("identifier", help="DOI (e.g. 10.1090/proc/12345)")
    p_doi.add_argument("--name", help="Short name override")
    p_doi.add_argument("--by", help="Agent that found this paper")

    p_url = sub.add_parser("add-url", help="Add paper by URL")
    p_url.add_argument("identifier", help="Direct URL to PDF")
    p_url.add_argument("--name", help="Short name override")
    p_url.add_argument("--by", help="Agent that found this paper")

    p_sum = sub.add_parser("summarize", help="Mark paper as summarized")
    p_sum.add_argument("paper_id", help="Paper ID number")

    sub.add_parser("list", help="List all papers")
    sub.add_parser("status", help="Pipeline status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {
        "add": cmd_add,
        "add-doi": cmd_add_doi,
        "add-url": cmd_add_url,
        "summarize": cmd_summarize,
        "list": cmd_list,
        "status": cmd_status,
    }[args.command](args)
