## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py` → C = 1.5028628682228971

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_023.md` — minimax perturbation (motivates the helper)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/system_recommendations.md` — Priority 7: plateau_analyzer
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen009/exploit_1.md` — 13 plateau positions within 1e-12 of max
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — existing float64 compute_c
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — existing incremental update
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/batch_trial_evaluator.py` — example of a well-structured helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md`

## Directive

**Build and validate the `plateau_analyzer` helper — Priority 7 from system recommendations, needed by explore_1 for minimax perturbation.**

### Deliverable 1: `output/helpers/plateau_analyzer.py`

Implement this function:

```python
def plateau_analysis(f, autoconv=None, threshold_rel=1e-12):
    """
    Analyze the autoconvolution plateau structure.

    Args:
        f: (N,) array of non-negative function values
        autoconv: (optional) pre-computed autoconvolution array. If None, computed from f.
        threshold_rel: relative threshold for near-max positions

    Returns dict with:
        positions: (K,) int array — indices where autoconv >= max * (1 - threshold_rel)
        values: (K,) float array — autoconv values at those positions
        gradients: (K, N) float array — per-element gradient of autoconv at each plateau position.
                   gradients[p, m] = d(autoconv[positions[p]]) / d(f[m])
        max_val: float — current max(autoconv)
        max_idx: int — argmax of autoconv
    """
```

**Gradient computation:** For each plateau position n, the gradient with respect to f[m] is:
`d(autoconv[n])/d(f[m]) = 2 * dx * f_padded[(n - m) % M]`
where M = len(autoconv), f_padded is f zero-padded to length M, and dx = 0.5/N.

This is because autoconv[n] = dx * sum_j f_padded[j] * f_padded[n-j], so the derivative w.r.t. f[m] = dx * (f_padded[n-m] + f_padded[n-m]) = 2*dx*f_padded[(n-m) % M] (since autoconvolution is symmetric in its two copies of f).

**Performance requirements:**
- K is small (~13 at current optimum), N is large (~30k)
- The (K, N) gradient matrix should be computed vectorized, not in a Python loop
- Total time for `plateau_analysis` should be < 100ms at N=30k

### Deliverable 2: Tests

Write tests in `output/sandbox/scripts/test_plateau_analyzer.py`:
1. **Gradient correctness:** For a small test array (N=100), verify each gradient entry against finite differences (`(autoconv(f + eps*e_m) - autoconv(f - eps*e_m)) / (2*eps)` at each plateau position).
2. **Consistency with compute_c_f64:** Verify `max_val * dx / (sum(f)*dx)^2 == compute_c(f)`.
3. **Threshold behavior:** Verify that `positions` grows as `threshold_rel` increases.
4. **Performance:** Verify < 100ms at N=30000.

### Deliverable 3: Updated `output/helpers/README.md`

Add documentation for `plateau_analyzer` to the helpers README. Follow the same format as existing entries. Also update the README to document ALL deployed helpers (it currently says "none yet" for experimentator-created helpers despite 8 existing ones).

### What NOT to do
- Do NOT modify any existing helper files — only write new files to `output/helpers/`.
- Do NOT write a solution file — this is a tools-only session.
- Do NOT use JAX for this helper — use pure NumPy for compatibility with all agents.
