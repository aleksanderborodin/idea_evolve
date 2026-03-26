# Debrief Report — explore_1, Generation 4

**Agent:** explore_1
**Task:** Properly calibrated Simulated Annealing at N=23

---

## Solution Table

| File | Approach | Score | .score file? | Notes |
|------|----------|-------|-------------|-------|
| sol01.py | Calibrated SA at N=23 (4 seeds, 500 SA iters, cold inner optimizer T=0.001, cubic upsample to N=600, warm fine-tune) | **UNEVALUATED** | No | Evaluation timed out or was blocked before producing output |

---

## 1. What did I try?

**sol01.py** — Full implementation of the brief's SA protocol:
- Calibration: 20 perturbations with sigma=0.05*std(raw_params), measure median|ΔC|, set metro_t=median*2, then tune with 10-step test loop until 20-40% acceptance
- 4 seeds, coarse optimization at N=23 (T=0.05→0.003→0.001, 10k steps/phase)
- SA: 500 iterations, cold inner optimizer (T=0.001 only, 300 steps per iteration — key fix vs gen3)
- Upsample best SA result via CubicSpline to N=600
- Fine-tune: T=0.05→0.01→0.003→0.001→0.0003, 15k steps/phase

The code correctly addressed all gen3 failure modes: sigma formula fixed (0.05*std not 0.3*mean), cold inner optimizer, N=23 specifically, metro_t calibrated from data.

## 2. What went wrong?

**Evaluation timed out.** The solution's `entrypoint()` function runs too much computation:
- 4×3×10k = 120k coarse gradient steps
- 4×500×300 = 600k SA inner gradient steps
- 5×15k = 75k fine gradient steps at N=600

Total wall-clock was likely 5-15 minutes. The evaluation timeout (~540s) killed the process before it returned a result.

## 3. What information did I lack?

- Wall-clock time per gradient step at N=23 with JAX JIT (would have flagged the budget issue)
- The prior generation's SA actually DID produce scores (1.5148-1.5169) with only 25-35 SA iters. I should have used a similar iteration budget (50-100 iters, not 500).

## 4. Was the State of Affairs accurate?

Yes. It correctly identified the three key failure modes of gen3 SA and flagged calibrated N=23 SA as the highest-priority untested experiment.

## 5. What would I do differently?

Reduce computation budget drastically:
- 2 seeds instead of 4 (do 2 more only if first 2 show promise)
- 100 SA iterations instead of 500
- 5k steps/phase for coarse (not 10k)
- 10k steps/phase for fine-tuning (not 15k)

This would cut total time from ~15 min to ~3-4 min, fitting in the timeout.

## 6. Specific experiments to run next

1. **SA at N=23 with reduced budget**: 2 seeds, 100 SA iters, 300 inner steps, 5k coarse steps, 10k fine steps. This is the exact same approach but feasible.
2. **Print timing info**: Add `print(f"Step time: {elapsed:.2f}s")` to catch budget overruns before they happen.
3. **Early stopping**: If SA shows no improvement for 30 consecutive iters, stop early.

## 7. What surprised me?

The computation budget for 500 SA iterations with 300 inner steps each is enormous — 150,000 gradient evaluations just for the SA phase, per seed. Gen3 used only 25-35 SA iterations total. The brief's "500-1000 SA iterations" was aspirational, not accounting for time constraints.

## 8. Helper tools feedback

No helpers from `problem/helpers/` were used. A helper that benchmarks the wall-clock time for N inner optimizer steps at a given N_COARSE would have been invaluable — it would have flagged the budget issue before writing code.
