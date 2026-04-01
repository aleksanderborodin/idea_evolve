# Observations — Experimentator 1, Gen 2

## Solutions

| File | Fitness (µs) | Valid | Notes |
|------|-------------|-------|-------|
| sol01.py | 223.17 | Yes | int8 accum + NC=128 (no streaming stores — harness C is unaligned) |
| best.py (ref) | 148.18 | Yes | int16 accum + NC=256 |

sol01 is worse than best.py (223 vs 148 µs). The NC=128 change hurts large (5091 vs 3176 µs) because more NC blocks = more pack_A calls. The int8 accumulation helps kernel throughput but doesn't overcome the NC regression on large.

## Key Finding: Streaming stores are the biggest win but can't be used in the harness
The harness allocates C with `std::vector<int>` (not 64-byte aligned), which means `_mm512_stream_si512` causes a fault. Streaming stores gave 2.3x on the large benchmark in standalone tests. To exploit this, the solution must internally allocate an aligned buffer and copy, or the harness must be modified.

## Experimental data collected (primary value of this session)
See report.md for complete tables from all 4 experiments.
