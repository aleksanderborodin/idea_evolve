# Evaluator Report — Generation 5

**strategic_shift: false**

## 1. What did I try?

Evaluated all 11 solutions across 4 agents (exploit_1, exploit_2, explore_1, research_1).
Collected verified scores from `.score` sidecar files (no re-evaluation needed — all present).
Analyzed each solution's strategy, mapped to existing ideas, created 2 new ideas and 2 new
patterns, updated 4 ideas and 3 clusters, and updated the coverage matrix and solution-idea map.

## 2. What information did I lack?

- **The actual numpy arrays from solutions.** I can read code and scores but cannot run
  solutions to inspect the function shapes. Comparing structural properties (sparsity pattern,
  peak locations, support intervals) across the AlphaEvolve intermediate arrays would reveal
  how LP-guided optimization evolves the function shape — useful for guiding future agents.

- **Details of exploit_2's 116 individual improvements.** Which elements were changed, by how
  much, and in what direction? This would reveal whether the LP residual cleanup is systematic
  (all changes are "zero out near-zero elements") or diverse.

## 3. What given facts might be wrong or outdated?

- **Pattern_007 may need revision.** It was tested entirely with float32 compute_c. exploit_2
  demonstrated that float32 accept/reject decisions are unreliable. The gen 4 experiments that
  established pattern_007 should be re-tested with float64 throughout. Pattern_007 is probably
  still correct (smooth-max Adam really can't improve published solutions) but the evidence
  base is tainted by float32.

- **idea_005 (Regularization approaches, confidence 0.4):** Never tested in 5 generations.
  Should be archived — it's eating idea budget without providing information.

- **idea_011 (Lion optimizer, confidence 0.35):** Last confirmed gen 1. The marginal evidence
  (1.5182, same as baseline) doesn't warrant keeping it active. Should be archived.

## 4. Was the State of Affairs accurate?

**No — stale since gen 3.** Key issues:
- Still recommends "Priority 1: Warm-start smooth-max Adam from the 1.5032 array" — debunked
  by gen 4's pattern_007.
- Says "Current SOTA: Yuksekgonul et al. report C <= 1.5029 but no public array yet" — gen 4
  already retrieved the TTT-Discover array.
- Missing: the entire gen 4-5 results, pattern_007, pattern_008, the float64 insight, the
  intermediate AlphaEvolve arrays.

The Consistency Reviewer MUST run before gen 6 to update the SoA.

## 5. What would I do differently?

- **Request float64 compute_c as a helper before gen 5.** The precision mismatch was the biggest
  obstacle across both exploit agents. If this helper existed, exploit_2 would have started with
  float64 coordinate descent and had time for more passes.

- **Explicitly flag eval_time > 60s solutions.** exploit_2/sol01 takes 792.6s because it re-runs
  coordinate descent. The pipeline should catch this and require baked arrays for production solutions.

## 6. Specific experiments to run

### Experiment 1: LP-based refinement (HIGHEST PRIORITY)
Formulate the autocorrelation constraint as a linear program at the current TTT-Discover
solution. Identify near-tight constraints and solve for LP descent directions. This is the
only method that has ever produced sub-1.505 scores. Significant engineering effort but
the gradient approach is exhausted.

### Experiment 2: Extended float64 coordinate descent
Bake the exploit_2 array. Run coordinate descent with:
- Top-2000 elements (not just 500)
- Finer deltas (1e-7, 1e-8)
- 30 passes (not just 10)
- Pair-wise element perturbation for top-50

### Experiment 3: Warm-start N=600 arrays with smooth-max pipeline
research_1/sol01 (C=1.5053) and sol02 (C=1.5040) are at N=600 — same resolution as the
gradient pipeline. Convert to raw_params via inv_softplus, run standard coarse-to-fine warm.
These arrays may not be as deeply optimized as the 30k array and may respond to gradient methods.

### Experiment 4: Re-test pattern_007 in float64
Run gen 4 exploit_1's conservative warm-start experiment on the 1319-element array but with
float64 compute_c for ALL accept/reject decisions. If the result differs, pattern_007 needs
revision and warm-start smooth-max may be viable after all.

### Experiment 5: Bulk-zero LP residuals
Zero ALL elements below 1e-8 in the TTT-Discover array simultaneously. The LP solver left
many residuals at ~1e-13. A bulk cleanup may find a larger improvement than element-by-element.

## 7. What surprised me?

1. **The SA calibration bug made zero difference.** explore_1's buggy SA (inner opt before
   Metropolis) and corrected SA produced identical scores (1.5227). This means the coarse SA
   perturbations are completely irrelevant — the N=600 fine-tuning determines everything.

2. **exploit_2 achieved the first agent-driven improvement** — tiny (8.82e-9) but real. After
   4 generations of "retrieval is the only path forward," an agent finally contributed original
   optimization value. The key was float64 precision.

3. **The float32/float64 discrepancy is massive** for this problem. Top-20 sensitive elements
   completely different. This means ALL previous sensitivity analysis was wrong, and any gen 4
   optimization guided by float32 sensitivity was misguided.

4. **exploit_1's gradient analysis was remarkably thorough.** 6 distinct approaches tested in
   one session. The finding that smooth-max gradient at T=0.0001 is still ~-0.539 everywhere
   is important — it means smooth-max is fundamentally broken for well-optimized arrays, not
   just poorly tuned.

5. **Gaussian mixture (15 peaks) performed terribly** at C=1.5418. The minimum-amplitude
   constraint prevents representing the sparse multi-peaked structure that good solutions have.
   This confirms that the function parameterization matters enormously.

## 8. Helper tools feedback

I did not directly use helpers (evaluator reads scores and files, doesn't run optimization).
Based on agent reports:

**Helpers that worked well:**
- `compute_c` (core.py): Useful for sanity checks but float32 precision is dangerous for
  optimization oracle use.
- `interpolate_sparse` (interpolation.py): Used by explore_1 for N=80->600 upsampling.
  Works well for arcsine-type inits.
- `inv_softplus_safe` (inv_softplus.py): Used by explore_1 for warm-start at N=600.

**Helpers with bugs/limitations:**
- `sensitivity_map` (sensitivity.py): Uses float32, gives completely wrong rankings for
  well-optimized solutions (pattern_008). Needs float64 mode.
- `compute_c` (core.py): Float32 precision insufficient for accept/reject decisions on
  solutions below C~1.505. Needs float64 variant.

**Missing helpers (ordered by priority):**
1. `compute_c_f64`: numpy float64 compute_c matching validate.py. #1 request across agents.
2. `autoconv_analysis`: Returns autoconvolution peak position and contributing element pairs.
3. `benchmark_step_time(N)`: Returns ms/step for gradient optimization at given grid size.
4. `load_cached_solution(path)`: Loads evaluated numpy array without re-running entrypoint.
5. `prepare_warm_start(array, target_n)`: Converts published array to raw_params + optional
   interpolation, ready for gradient optimization.
