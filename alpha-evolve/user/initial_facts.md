# Initial Facts

## fact_001: Problem definition
The first autocorrelation inequality asks for the smallest constant C such that
max_{t in [-1/2,1/2]} (f * f)(t) >= C * (integral of f over [-1/4,1/4])^2
for all non-negative functions f. Lower C is better.

## fact_002: Known bounds
The best known bounds are 1.28 <= C <= 1.5098. The target is C <= 1.5053.
The problem arises in additive combinatorics and Sidon set theory.

## fact_003: Computation method
Autoconvolution is computed via FFT with zero-padding. The function is discretized
on [-1/4, 1/4] with uniform grid spacing dx = 0.5/N where N is array length.
C = max(f*f * dx) / (sum(f)*dx)^2.

## fact_004: Available tools
JAX with optax is available for gradient-based optimization. helper.py provides
a differentiable compute_c function. The initial program uses Adam optimizer
with warmup cosine schedule for 40000 steps.

## fact_005: Solution format
Solutions must implement def entrypoint() returning a 1D NumPy float array of
non-negative values. The array represents f on [-1/4, 1/4].
