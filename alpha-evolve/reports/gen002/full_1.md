# Full Agent Gen 002 — Debrief Report

## Solutions

| File | Score | Has .score | Approach |
|------|-------|------------|----------|
| sol01.py | TBD (eval timed out/killed) | No | Coarse-to-fine (N=50→200→600) + smooth-max annealing + 16 restarts + L-BFGS-B polish + softplus reparam + gradient clipping |

## What Happened

Only sol01.py was written. Two evaluation attempts were made:
1. Background task `bocz0l4ho` — no output retrieved (task not found on lookup)
2. Background task `b5kv49jmc` — status: **killed** before completion

The solution did not produce a scored result. The evaluation itself likely ran out of time — sol01 is compute-heavy (16 coarse restarts × 3 temps × 3000 steps, then mid and fine stages, then L-BFGS). Estimated runtime: 10–20 minutes on CPU.

## What sol01 Tried

Combined ALL recommended techniques from the brief in one pipeline:
- **Coarse-to-fine:** N=50 coarse → N=200 mid → N=600 fine (upsample via jnp.interp)
- **Smooth-max (log-sum-exp):** at every stage, temperatures [0.05, 0.01, 0.003] → [0.003, 0.001] → [0.001, 0.0003, 0.0001, 0.00003]
- **16 diverse restarts** at coarse stage (Gaussian bumps, ramps, random noise)
- **Softplus reparameterization** for guaranteed non-negativity
- **Gradient clipping** (global norm 1.0) via optax.chain
- **L-BFGS-B polish** at the end (smooth-max T=1e-5, 3000 iters)
- **jax_enable_x64** for float64 precision throughout

## What I Lacked

- A way to estimate runtime before committing to a heavy pipeline
- A pre-evaluated warm-start (e.g., sol03's output array) to skip the coarse exploration
- Time to run even one complete evaluation

## What I Would Do Differently

1. Start with a lighter sol01 (fewer restarts, fewer steps) to get a scored result quickly
2. Then add complexity in sol02/sol03
3. The warm-start approach (load sol03's entrypoint() output, continue with lower temps) would have been faster and safer as first attempt

## Experiments to Run

1. **Runtime profiling:** How long does sol01 actually take? If < 10 min, just run it.
2. **Warm-start from gen001/full_1/sol03:** Load sol03 output, run fine_temps [0.0001, 0.00003] + L-BFGS-B. Should be fast and start from C=1.5108.
3. **L-BFGS-B after smooth-max:** The key untested combination — was the core hypothesis here.

## State of Affairs Accuracy

Accurate. Best score C=1.5108 from sol03 (smooth-max + 8 restarts). No further progress made this session due to evaluation failures.
