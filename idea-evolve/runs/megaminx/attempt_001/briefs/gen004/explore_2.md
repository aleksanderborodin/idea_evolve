## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness **44094**.
Compression-only floor: 44114.
Target: **15000 proxy**. very_hard bucket (ids 501–1000) contributes **74.8% of total score**.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/state_of_affairs.md` — current standing, dead ends, open questions
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_013.md` — combined recipe (what exploit_1 is running)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/established/idea_009.md` — compression baseline (44114)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_012.md` — built-in MITM
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py` — compression reference
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen003/explore_2/sol01.py` — the current best, your previous attempt (suffix-only beam)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen003/explore_2.md` — your own gen003 debrief
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/helpers/README.md` — helper index
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/description.md` — proxy vs full, bucket definitions

## Directive — Track A DIRECTED EXPLORATION

**Your target is the very_hard bucket specifically (ids 501–1000, 74.8% of total score).** exploit_1 is running the combined recipe end-to-end. Your complementary mission is to attack the one bucket that dominates fitness, using a **per-bucket hybrid strategy** that combines the best technique for each depth range.

### Hypothesis to test

Different depth ranges want different solvers. A single beam configuration that works for short puzzles wastes compute on very_hard, and a configuration aggressive enough for very_hard is overkill for short. Specifically:

- **special/short (ids 0–25, minor score contribution):** BFS depth-6 alone finds exact solutions (special id=0 is a 72-move scramble outlier; handle separately). Use `bfs_result_for_mitm` + tiny beam. Should solve optimally in microseconds per puzzle.
- **medium (ids 26–100):** embedding-MLP predictor + moderate beam (2048, max_steps 80) + MITM. Should improve over compression.
- **hard (ids 101–500):** predictor + wide beam (8192, max_steps 200) + MITM. Where we expect the first real gains.
- **very_hard (ids 501–1000):** wide beam + MITM backstop, potentially with **iterative deepening** (run beam multiple times with increasing max_steps, early-exit on success) or **path concatenation** (solve to an intermediate state ≤ 50 moves from solved, then MITM finishes). If predictor+beam cannot reach very_hard depths, fall back to compression and ADMIT IT.

### Milestone Protocol (mandatory)

- **Milestone 1 (first ~25 min) — produce `output/sol01.py` that is the compression baseline (simplest — import `compress_path` from `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py` and apply it). Score: 44114 guaranteed.** This is your insurance.
- **Milestone 2 (~30 min) — produce `output/sol02.py` that adds the MITM-only pass on short puzzles** (ids 0–25, reuse BFS depth-6 `bfs_result_for_mitm` with a very small beam_width=256, max_steps=30). For the rest, use compression. This demonstrates the MITM+beam integration WITHOUT any predictor. Score it.
- **Milestone 3 (remaining) — produce `output/sol03.py` and beyond that adds the per-bucket strategy**, using exploit_1's embedding-MLP output (or training your own smaller one — 5 epochs on the BFS data is enough for a baseline).

### Where you MUST differ from exploit_1

- exploit_1 uses a single `beam_width × max_steps` for all puzzles. You must use **per-bucket settings**. Record your chosen `(beam_width, max_steps)` tuple per bucket in the report.
- exploit_1's goal is "does the recipe work at all?" Your goal is "where is compute best spent?" You can re-use exploit_1's trained model if it finishes first (check `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen004/exploit_1/` for a saved `.pt` file or reproducible training — if present, load it; if not, train your own quickly).
- Prioritise **diagnostics**. The bucket breakdown in `.score` is your primary metric. You are trying to identify which bucket has the most headroom — that is a finding the system needs even if your score is worse than exploit_1.

### Concrete approach for the very_hard bucket

Per-puzzle plan for ids 501–1000:
1. Try predictor+beam with `beam_width=8192, max_steps=300, bfs_result_for_mitm=bfs_result`. Time-box: 60 s per puzzle.
2. If beam returns `None`, fall back to compression (score = sample_submission compressed ≈ 440 per very_hard puzzle).
3. Record which puzzles were solved by beam vs by fallback. Include this in your report.

### Off-limits

- **Do NOT duplicate exploit_1.** If you run the exact same recipe end-to-end, your results are wasted.
- **Do NOT revisit unguided beam search.** SoA dead end #1.
- **Do NOT use Hamming predictor.** Debunked.
- **Do NOT use `beam_mode='advanced'`.** Broken.
- **Do NOT modify files outside `output/`.** All your work lives in your workspace.

### Deliverable contract

- At minimum: `output/sol01.py` (compression baseline) + `output/sol02.py` (MITM-only on short puzzles).
- Ideally: `output/sol03.py` or higher with per-bucket hybrid strategy.
- `output/report.md` must include:
  - Table: bucket × `(beam_width, max_steps)` × (solved, fallback, fitness contribution). This is your most valuable output for the Evaluator.
  - **Verdict:** which bucket has the most headroom? Where should gen005 focus?
  - Any shared findings that apply to exploit_1's end-to-end run (e.g. "beam_width > 4096 gave no improvement on medium but helped on hard").

### Group-1 context (light evaluator)

You are in parallel-group 2. Group 1 (exploit_1, experimentator_1, research_1) will have finished before you start. Read `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/group_notes/gen004/group1.md` (if present — light evaluator writes it) and any new ideas in `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/` that weren't listed in this brief. If experimentator_1's helper (`helpers/embedding_predictor_beam.py`) was deployed, use it directly. If exploit_1 reported an OOM at beam_width=X, avoid that setting.
