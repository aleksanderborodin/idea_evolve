# Constraints

## Hard Constraints
- Function must be non-negative: f(x) ≥ 0 for all x
- All values must be finite real numbers (no NaN or infinity)
- Function must not be identically zero (∫f > 0)
- Represented as 1D NumPy array of float values

## Soft Constraints
- Use numpy, jax, scipy, or standard library
- Fix random seeds for reproducibility
- Solutions must implement `def entrypoint() -> np.ndarray`
- Higher resolution (larger N) generally gives better results but slower computation

## Environment
- Python 3.12
- NumPy available
- SciPy available
- JAX + optax available
- Standard library available

## Autoconvolution Details
- Domain: [-1/4, 1/4], width = 0.5
- dx = 0.5 / N (inferred from array length)
- Autoconvolution computed via FFT with zero-padding
- C = max(f ★ f * dx) / (sum(f) * dx)²
