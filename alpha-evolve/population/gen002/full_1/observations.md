# Observations — gen002_full_1

## Summary

Only sol01.py was written and evaluated. Both evaluation attempts were killed before completion.

## sol01.py — Coarse-to-fine + smooth-max + 16 restarts + L-BFGS-B

**Score:** Not obtained (eval killed)

**Design:** Kitchen-sink combination of all proven techniques:
- 16 restarts at N=50 coarse grid (cheap)
- Smooth-max temperature annealing at all 3 scales
- Upsample coarse→mid→fine via jnp.interp
- L-BFGS-B polish at N=600 with T=1e-5
- float64 precision, gradient clipping

**Problem:** Too compute-heavy for the available evaluation window. Should have profiled first.

## Key Lesson

Always write the cheapest variant first (e.g., warm-start from existing sol03 output + just L-BFGS polish). That approach would have scored in ~1 minute and established a baseline. The ambitious pipeline can be sol02.
