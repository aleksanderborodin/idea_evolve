# Research Agent Debrief — Gen 001, research_1

## Solutions Table

| File | Fitness (C) | Valid | Notes |
|------|-------------|-------|-------|
| (none) | — | — | No solutions produced; research-only session |

---

## 1. What did I try?

This was a pure research session. I did not produce solution files — the research agent's
role is to produce knowledge, not code. I investigated the mathematical theory behind the
first autocorrelation inequality via web search and paper review.

**Papers/sources consulted:**
- arXiv:1403.7988 — Cloninger & Steinerberger (2017): proves C ≥ 1.28 lower bound
- arXiv:0907.1379 — Matolcsi & Vinuesa (2010): proves C ≤ 1.50992, disproves Schinzel-Schmidt conjecture
- arXiv:2602.07292 — Rechnitzer (2026): computes related L² constant to 128 digits
- arXiv:2506.16750 — Boyer et al. (2025): improved example for related inequality
- arXiv:2508.02803 — further lower bound improvements for related inequality
- arXiv:2511.23473 — ThetaEvolve (2025): achieves C₁ = 1.503133 on our exact problem
- AlphaEvolve GitHub: 600-interval step function achieving C₁ ≤ 1.5032
- arXiv:2001.02326 — Extensions of autocorrelation inequalities

**Key findings written to findings.md** — see that file for full structured output.

---

## 2. What information did I lack?

- The **exact coefficient values** of the AlphaEvolve/ThetaEvolve 600-interval step function
  that achieves C = 1.5032. These are in the AlphaEvolve GitHub notebook (mathematical_results.ipynb
  Section B.2) but I couldn't retrieve raw notebook values from web.
- The **explicit construction** Matolcsi & Vinuesa used to achieve 1.50992. The paper is
  behind journal access; only the abstract was available via arXiv.
- What the gradient-descent-optimized function actually looks like (shape, symmetry) —
  would require running the baseline optimizer to convergence.

---

## 3. What given facts might be wrong or outdated?

- **fact_002.md** says "best known bounds are 1.28 <= C <= 1.5098." This is outdated.
  The current upper bound is **C ≤ 1.5032** (AlphaEvolve) / **1.503133** (ThetaEvolve).
  The project target of 1.5053 is already beaten by the existing literature.
- The lower bound 1.28 appears to be current (Cloninger-Steinerberger 2017).

---

## 4. Was the State of Affairs accurate?

Yes — it correctly reflected that no solutions have been run yet and everything is open.
No inaccuracies to report.

---

## 5. What would I do differently with more context?

- Download and extract the AlphaEvolve mathematical_results.ipynb to get the actual
  600-interval coefficient array. That array, used as initialization, would likely
  immediately achieve C ≤ 1.5032 without any further optimization.
- Run the baseline optimizer to see what the converged function shape looks like,
  which would reveal whether it's symmetric, unimodal, multi-peaked, etc.
- Try running the Matolcsi-Vinuesa paper's construction directly.

---

## 6. Specific experiments to run

1. **Better gradient descent hyperparameters**: Increase num_steps from 40,000 to 200,000;
   lower end_value of cosine schedule to 1e-6 instead of learning_rate * 1e-4.
   Expected result: C closer to 1.503 without any structural changes.

2. **Coarse-to-fine**: Start N=50, optimize 10,000 steps → upsample to N=200, optimize
   10,000 steps → upsample to N=600, optimize 20,000 steps. Use scipy.ndimage.zoom or
   jnp.interp for upsampling. This was shown effective in arXiv:2506.16750.

3. **Multiple restarts**: Run 10 independent optimizations from different random seeds,
   keep the best. JAX makes this efficient with vmap.

4. **Simulated annealing wrapper**: After gradient descent converges, add random Gaussian
   perturbation (σ=0.1) and re-run descent 50 times. Temperature schedule: σ = 0.1 * (1-t/T).

5. **Smooth initialization from theory**: Initialize with f(x) = (1-4x²)^{-1/2} shape
   (the near-optimal form from Rechnitzer's ansatz) — this is the arcsine distribution
   on [-1/4, 1/4], which has minimum Fourier peak properties.

6. **Check the AlphaEvolve notebook**: Retrieve Section B.2 from
   https://github.com/google-deepmind/alphaevolve_results/blob/main/mathematical_results.ipynb
   to get the exact 600-interval array.

---

## 7. What surprised me?

- The target of 1.5053 is ALREADY beaten by published work (1.5032 by AlphaEvolve, 1.503133
  by ThetaEvolve). The system's target was set before these results were published.
- The optimal function appears to have **non-symmetric, multi-peaked, complex** structure —
  not a simple Gaussian or tent function as one might naively expect.
- The Schinzel-Schmidt conjecture (C = π/2 ≈ 1.5708) was disproved as recently as 2010,
  showing this is an active research area with surprises still happening.
- There is a closely related L² problem (ν₂²) that has been solved to 128 decimal places,
  while our L∞ problem is far from settled.
- The gap between the lower bound (1.28) and best upper bound (1.5032) remains large;
  the true optimum is genuinely unknown.

---

## 8. Findings document

The full structured findings are in:
`/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen001_research_1/output/findings.md`
