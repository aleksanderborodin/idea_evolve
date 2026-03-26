# Observations — explore_1, Generation 4

## Summary

One solution was written (`sol01.py`). Evaluation did not complete — the process either timed out (sol01 runs a very large computation) or was blocked by permissions. No `.score` file exists.

## What was attempted

### sol01.py — Calibrated SA at N=23
- Properly calibrated Simulated Annealing following the brief exactly
- Calibration step: generate 20 random perturbations with sigma=0.05*std(raw_params), measure median |ΔC|, set metro_t = median*2
- Tuning loop: run 10 test SA steps, adjust metro_t until 20-40% acceptance
- 4 seeds × coarse optimization at N=23 (Adam, T=0.05→0.003→0.001, 10k steps/phase)
- SA: 500 iterations per seed, cold inner optimizer (T=0.001 only, 300 steps)
- Upsample best SA result via CubicSpline to N=600
- Fine-tune: T=0.05→0.01→0.003→0.001→0.0003, 15k steps/phase

## Why evaluation likely timed out

The computation budget was too high:
- 4 seeds × 10k steps × 3 phases = 120k coarse gradient steps
- Calibration: 20 perturbations, 10 tune-steps × 300 inner steps = 9k steps
- SA: 4 seeds × 500 iters × 300 inner steps = 600k coarse gradient steps
- Fine-tuning: 5 phases × 15k steps at N=600 = 75k fine gradient steps

Total: ~800k+ gradient evaluations. At N=23 coarse most are fast, but the total wall-clock time exceeded the evaluation timeout (~540s).

## Key learnings / what to fix next attempt

1. **Reduce SA iterations from 500 to 100-200** — still meaningful exploration with much less compute
2. **Reduce coarse optimization from 10k to 5k steps/phase** — N=23 converges fast
3. **Reduce fine-tuning from 15k to 10k steps/phase** — cuts 75k→50k fine steps
4. **Run calibration from seed 0 only, share across all seeds** — already done in sol01, good
5. **Add per-iteration timing and early stopping** — abort SA if it's not improving after 50 iters

## Score

- sol01.py: **UNEVALUATED** (evaluation timed out or blocked)

## What I wish I knew

- The typical wall-clock time for one coarse Adam step at N=23 with JAX JIT
- Whether the prior approach (gen3 failed SA) even ran the inner optimizer or skipped it
