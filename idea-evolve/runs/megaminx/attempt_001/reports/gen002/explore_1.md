# Debrief Report — gen002_explore_1

## Files in output/

| File | Score | Status |
|------|-------|--------|
| sol01.py | — | NOT EVALUATED (timed out after 10 min — IDA* depth-first search is too slow for depth 20+ puzzles) |
| sol02.py | 1,000,000,000 (sentinel) | INVALID — syntax error (UTF-8 corruption in the file) |
| sol03.py | 46,312 | Valid — same as gen001 baseline |
| sol04.py | 46,312 | Valid — same as gen001 baseline |

## Approaches Tried

### sol01 — IDA* with corner-only pattern database (NOT EVALUATED)
**Intention:** Depth-first admissible search outside beam search family.
**Result:** Timed out after 10 minutes. The IDA* search with BFS-built PDB (depth 5) was far too slow for Megaminx puzzles with depth 20-1000.
**Key discovery:** Megaminx has NO 3-cycles or 2-cycles — all 24 generators use 5-cycles. This means the classic corner/edge classification (which works for cubes) does NOT apply here. The "corner PDB" approach was based on a flawed assumption.

### sol02 — Hamming-predictor-guided beam search (INVALID)
**Intention:** Run EXP-1 (zero-cost hamming predictor test) from experiment suggestions.
**Result:** File corrupted by UTF-8 encoding issue. Score is sentinel 1e9.
**Note:** The approach was sound — even a hamming predictor would have tested whether guided search beats compression.

### sol03 — Enhanced compression + beam fallback (46,312)
**Intention:** Multi-pass X.-X cancellation + hamming-guided beam search for hard/very_hard buckets.
**Result:** Compression-only baseline confirmed at 46,312 (compression_ratio=0.9158). Beam search phase was cut off by timeout.
**The problem:** Even with bucket-specialized params, 101 puzzles at beam_width=1500-3000, max_steps=150-300 takes too long on CPU.

### sol04 — Hybrid with timing budget (46,312)
**Intention:** Enhanced compression for all + focused beam on deepest very_hard puzzles (ids 600+).
**Result:** Identical score to gen001 baseline. The compression floor is confirmed at 46,312 (0.9158 compression ratio).

## Summary

- **All evaluated solutions scored 46,312** — same compression floor as gen001
- **Compression ceiling confirmed:** X.-X cancellation gets to 0.9158, no further without smarter search
- **The beam search approach timed out** on hard/very_hard buckets — even hamming-predictor guided search is too slow at the parameter scales needed
- **Key structural discovery:** Megaminx has no 2-cycles or 3-cycles (all 5-cycles). Classic cube-style corner/edge PDB heuristics don't directly apply.
- **The only path forward** is predictor-trained beam search with GPU acceleration, as the gen001 experiment suggestions document (EXP-2, EXP-5)

## Per-bucket scores (sol03/sol04, identical)
- special: 72 (1/1 solved)
- short: 30 (2/2 solved)
- medium: 474 (8/8 solved)
- hard: 11,102 (40/40 solved)
- very_hard: 34,634 (50/50 solved) — **dominates score**