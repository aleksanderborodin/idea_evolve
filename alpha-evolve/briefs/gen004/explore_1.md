## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5032 (AlphaEvolve 1319-element array)
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank05_1.5090.py` (best gradient-descent result)
Target: C ≤ 1.5053 (BEATEN). New stretch goal: C < 1.503.

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_007.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_013.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen003/explore_1.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`

## Directive

**Properly calibrated coarse-scale Simulated Annealing at N=23.** All 3 SA attempts in gen 3 failed due to poor temperature calibration (96-100% acceptance rate). This attempt must fix that.

### Mandatory calibration step (do this FIRST)

Before running any full SA:
1. Run baseline coarse optimization at N=23 with smooth-max Adam (T=0.05→0.003→0.001, 10k steps/phase, 4 seeds). Record the best coarse C.
2. From the best coarse solution, generate 20 random perturbations with sigma = 0.05 * std(raw_params). Evaluate each perturbation's C.
3. Compute the typical ΔC between neighboring solutions. This tells you the energy scale.
4. Set `metro_temp = median(|ΔC|) * 2`. This should give ~30% acceptance rate.
5. Run 10 test SA steps with this temperature. Measure actual acceptance rate. If > 50%, halve metro_temp. If < 15%, double it. Repeat until 20-40%.

### Full SA run (after calibration)

1. From each of 4 seeds, run coarse optimization at N=23 (smooth-max Adam, same schedule as baseline).
2. From each converged coarse solution, run SA:
   - SA iterations: 500-1000
   - sigma: 0.05 * std(raw_params) (capped at 1.0)
   - metro_temp: calibrated value from step above
   - Inner optimizer: 300 steps of Adam at T=0.001 per SA iteration
3. Upsample the best SA result to N=600 via cubic interpolation.
4. Run warm smooth-max fine-tuning: T=0.05 → 0.01 → 0.003 → 0.001 → 0.0003, 15k steps/phase.
5. Evaluate. Compare against the no-SA baseline (same seeds, same fine-tuning, but skip SA step).

### Why N=23 specifically

Boyer et al. used N=23 and found it effective. At N=23, there are only 23 degrees of freedom — the coarse landscape has far fewer local minima and SA can hop between fundamentally different solution structures. Our failed attempts used N=30-80 where the landscape may already be too complex for SA to explore effectively.

### What NOT to do

- Do NOT skip the calibration step. This is the #1 reason all prior SA attempts failed.
- Do NOT use sigma > 1.0 or sigma = 0.3 * mean(|f|). The old formula produced absurdly large perturbations (sigma=6-15).
- Do NOT use metro_temp > 0.01 without calibration evidence. Gen 3 SA had acceptance rates of 96-100% because metro_temp was too high.
- Do NOT try SA at N=600 (fine grid). This is confirmed dead (returns to same basin every time).
- Do NOT warm-start from the AlphaEvolve array (exploit agents are doing that).

### Success criterion

At least one SA seed that, after fine-tuning to N=600, achieves C < 1.509 (better than the current gradient-descent floor). Even C = 1.508 would be a breakthrough for this approach.
