# Debrief Report — Explore 2, Generation 2

## Agent: explore_2
## Task: Simulated Annealing wrapper around smooth-max Adam optimization

---

## 1. What did I try?

### sol01 — SA with weak initial convergence (C = 1.5176)
- 2 SA restarts, each: 5 phases × 5k steps Adam = 25k init, then 40 SA iters × 2 phases × 1.5k inner Adam = 3k inner
- Total: ~290k steps, ~99 seconds
- SA parameters: sigma_0=0.4, sigma_decay=0.97, T_anneal_0=0.008, T_anneal_decay=0.93
- Result: **1.5176** — worse than sol03 (1.5108). Insufficient initial convergence meant SA started from a bad basin.

### sol02 — SA with 4-seed init (C = 1.5162)
- 4 seeds × 5 phases × 15k steps = 75k per seed (same as sol03 but 4 seeds not 8)
- SA: 60 iters × 3 phases × 2k inner Adam = 6k per iter
- Total: ~660k steps, ~177 seconds
- SA parameters: sigma_0=0.35, T_anneal_0=0.006
- Result: **1.5162** — improved over sol01 but still below sol03. 4 seeds insufficient to find the good basin.

### sol03 — Full sol03-style init + SA with L-BFGS inner (C = 1.5108)
- 8 seeds × 5 phases × 15k Adam steps = 75k per seed (exact sol03 hyperparams)
- SA: 60 iters × L-BFGS(300 iterations) inner optimization at temp=0.001
- Total: 600k Adam steps + 60 L-BFGS runs
- SA parameters: sigma_0=0.25, T_anneal_0=0.004, T_anneal_decay=0.94
- Result: **1.5108** — ties the existing best. SA with L-BFGS did not improve beyond initial Adam convergence.

| Solution | Fitness | Valid | Notes |
|----------|---------|-------|-------|
| sol01    | 1.5176  | 1     | SA + weak init (2 seeds, 25k steps each) |
| sol02    | 1.5162  | 1     | SA + medium init (4 seeds, 75k steps each) |
| sol03    | 1.5108  | 1     | SA + full init (8 seeds, 75k steps) + L-BFGS inner |

---

## 2. What information did I lack?

- **Inner step count needed for basin-hopping**: I didn't know how many inner optimization steps are required to actually escape a local minimum vs. just returning to it. The Boyer et al. paper uses ~1M steps at the fine stage, which is 100× more than I tried.
- **SA acceptance rates**: I couldn't measure what fraction of SA proposals were being accepted, making it hard to diagnose whether sigma was too large (too many rejections) or too small (never leaving the basin).
- **Function shape of C=1.5108 solution**: Without visualizing what gen001/sol03's function looks like, I couldn't reason about how far C≈1.503 solutions might be in function space.

---

## 3. What given facts might be wrong or outdated?

- **Finding 4 from research** says SA should give "C ≈ 1.503" but this was based on Boyer et al. doing SA at N=23 (coarse grid), not N=600. The extrapolation to fine-grid SA may be incorrect. SA at N=600 faces a much harder landscape than at N=23.

---

## 4. Was the State of Affairs accurate?

Yes — it correctly identified simulated annealing as unexplored. It was accurate that combining smooth-max with SA was untried. The experiment confirmed the gap exists, but SA alone at fine resolution doesn't yield the expected gains.

---

## 5. What would I do differently with more context?

- Apply SA at **N=30 coarse grid** first (as Boyer et al. actually did), then upsample. The fine-grid SA I implemented is not what the literature recommends.
- Use larger sigma (1.0–2.0) with much more inner steps (50k+) per SA iteration for fine-grid SA.
- Try **structured perturbations**: perturb specific Fourier modes or localized bumps rather than random Gaussian noise across all 600 values.
- Measure acceptance rate during SA and tune sigma to get ~40% acceptance.

---

## 6. Specific experiments to run next

1. **Coarse-to-fine SA** (highest priority): N=30 → N=150 → N=600. SA at N=30 (30 restarts, 5k steps each). This is the actual Boyer et al. approach. Another agent is supposedly covering coarse-to-fine; they should add SA at the coarse stage.

2. **Structured perturbations**: Perturb the top-K Fourier modes of the function with random phase shifts (|Δφ_k| ~ Uniform[0, π/4]). This explores the function's frequency structure rather than its pointwise values.

3. **Basin hopping with very large perturbations**: sigma=1.5 × f_max, but 50k inner Adam steps to properly re-converge. Run 20 such hops. Very expensive but might actually escape.

4. **SA with warm inner restarts**: After perturbation, run inner optimizer with temp schedule [0.05, 0.01, 0.003, 0.001] (not just cold). This would take 10k inner steps but might navigate properly.

---

## 7. What surprised me?

- **SA matches but doesn't beat Adam-only** (sol03): The 8-seed Adam run (sol03 in gen001) already finds C=1.5108. Running 60 SA iterations with L-BFGS inner optimization after that produces exactly the same score. The L-BFGS SA phase is essentially a no-op — every proposal comes back to the same local minimum.

- **The "sticky" local minimum at C≈1.511**: All random initializations converge to roughly the same local minimum region (1.511–1.52). The basin of attraction for this region appears very wide at N=600. It's not that SA is failing to explore — it's that every perturbation + re-optimization returns to the same basin.

- **Speed**: At 2929–3729 steps/second (JAX on CPU), the compute budget is actually quite tight. The 600k Adam steps that sol03 uses take ~160–200 seconds (3–3.5 minutes). Adding meaningful SA on top doubles the compute with no gain.

- **L-BFGS inner optimization is fast but ineffective for basin-hopping**: L-BFGS is great at finding the nearest local minimum (gradient to zero), which is exactly the wrong property for escaping a local minimum via SA. It needs to explore to find a *different* local minimum, but L-BFGS always converges to the nearest one.
