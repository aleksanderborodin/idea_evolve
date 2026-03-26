# fitness: 0.0
"""
Properly calibrated Simulated Annealing at N=23.

Key fixes vs gen3 failures:
- N=23 exactly (Boyer et al.)
- sigma = 0.05 * std(raw_params)  (not 0.3 * mean)
- metro_temp calibrated from actual ΔC measurements (~30% acceptance)
- Cold inner optimizer: T=0.001 ONLY, 300 steps (not warm restart)
- 4 seeds with coarse SA, best upsampled + fine-tuned to N=600
"""
import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.interpolate import CubicSpline
import sys

jax.config.update("jax_enable_x64", True)

N_COARSE = 23
N_FINE = 600
LR = 0.005


# ---- Objective ----

def smooth_max_c(raw_params, T):
    f = jax.nn.softplus(raw_params)
    dx = 0.5 / len(f)
    N = len(f)
    padded = jnp.pad(f, (0, N))
    fft = jnp.fft.fft(padded)
    conv = jnp.fft.ifft(fft * fft).real * dx
    c_max = jnp.max(conv)
    smax = c_max + T * jnp.log(jnp.sum(jnp.exp(jnp.clip((conv - c_max) / T, -50, 0))))
    integral = jnp.sum(f) * dx
    return smax / jnp.maximum(integral ** 2, 1e-9)


def hard_c_from_raw(raw_params):
    f = jax.nn.softplus(raw_params)
    dx = 0.5 / len(f)
    N = len(f)
    padded = jnp.pad(f, (0, N))
    fft = jnp.fft.fft(padded)
    conv = jnp.fft.ifft(fft * fft).real * dx
    integral = jnp.sum(f) * dx
    return float(jnp.max(conv) / jnp.maximum(integral ** 2, 1e-9))


# ---- Adam optimizer ----

def run_adam(raw_params, temps, steps_per_phase, lr=LR):
    params = jnp.array(raw_params)
    for T in temps:
        grad_fn = jax.jit(jax.value_and_grad(lambda p: smooth_max_c(p, T)))
        optimizer = optax.adam(lr)
        opt_state = optimizer.init(params)

        @jax.jit
        def step(p, s):
            loss, g = grad_fn(p)
            upd, ns = optimizer.update(g, s)
            return optax.apply_updates(p, upd), ns, loss

        for _ in range(steps_per_phase):
            params, opt_state, _ = step(params, opt_state)
    return params


# ---- Coarse optimization ----

def coarse_optimize(seed):
    key = jax.random.PRNGKey(seed * 17 + 3)
    raw = jax.random.normal(key, (N_COARSE,)) * 0.5
    raw = run_adam(raw, [0.05, 0.003, 0.001], 10000)
    c = hard_c_from_raw(raw)
    print(f"  Seed {seed}: coarse C = {c:.6f}")
    return raw, c


# ---- Calibration ----

def calibrate(base_raw, n=20):
    sigma = 0.05 * float(jnp.std(base_raw))
    sigma = min(sigma, 1.0)
    c_base = hard_c_from_raw(base_raw)
    deltas = []
    for _ in range(n):
        p = np.random.randn(N_COARSE) * sigma
        c_p = hard_c_from_raw(base_raw + jnp.array(p))
        deltas.append(abs(c_p - c_base))
    med = float(np.median(deltas))
    metro_t = med * 2.0
    print(f"  Calibration: sigma={sigma:.5f}, median|ΔC|={med:.6f}, init metro_t={metro_t:.6f}")
    return metro_t, sigma


def tune_metro(base_raw, sigma, metro_t):
    """Adjust metro_t until acceptance rate is 20-40%."""
    for attempt in range(6):
        params = base_raw.copy()
        c_cur = hard_c_from_raw(params)
        accepted = 0
        n_test = 10
        for _ in range(n_test):
            perturb = np.random.randn(N_COARSE) * sigma
            cand = run_adam(params + jnp.array(perturb), [0.001], 300)
            c_cand = hard_c_from_raw(cand)
            delta = c_cand - c_cur
            if delta < 0 or np.random.rand() < np.exp(-delta / metro_t):
                params = cand
                c_cur = c_cand
                accepted += 1
        rate = accepted / n_test
        print(f"  Tune {attempt+1}: metro_t={metro_t:.6f}, accept={rate:.2f}")
        if rate > 0.50:
            metro_t *= 0.5
        elif rate < 0.15:
            metro_t *= 2.0
        else:
            break
    return metro_t


# ---- Simulated Annealing ----

def run_sa(raw_coarse, sigma, metro_t, n_iters=500):
    params = raw_coarse.copy()
    c_cur = hard_c_from_raw(params)
    best_params = params.copy()
    best_c = c_cur
    accepted = 0

    for i in range(n_iters):
        perturb = np.random.randn(N_COARSE) * sigma
        cand = run_adam(params + jnp.array(perturb), [0.001], 300)
        c_cand = hard_c_from_raw(cand)
        delta = c_cand - c_cur
        if delta < 0 or np.random.rand() < np.exp(-delta / metro_t):
            params = cand
            c_cur = c_cand
            accepted += 1
            if c_cur < best_c:
                best_params = params.copy()
                best_c = c_cur
        if (i + 1) % 100 == 0:
            print(f"    SA iter {i+1}/{n_iters}: best={best_c:.6f}, cur={c_cur:.6f}, accept={accepted/(i+1):.2f}")

    print(f"  SA best coarse C: {best_c:.6f} (accept={accepted/n_iters:.2f})")
    return best_params, best_c


# ---- Upsample ----

def upsample(raw_coarse, n_fine=N_FINE):
    f_coarse = np.array(jax.nn.softplus(raw_coarse))
    x_c = np.linspace(0, 1, N_COARSE)
    x_f = np.linspace(0, 1, n_fine)
    cs = CubicSpline(x_c, f_coarse)
    f_fine = np.maximum(cs(x_f), 0.0)
    # inv_softplus: raw = log(exp(f) - 1)
    eps = 1e-6
    f_safe = np.maximum(f_fine, eps)
    raw_fine = np.log(np.expm1(f_safe) + eps)
    return jnp.array(raw_fine)


# ---- Entry point ----

def entrypoint():
    np.random.seed(42)

    N_SEEDS = 4
    SA_ITERS = 500

    # === Calibration from seed 0 ===
    print("=== Coarse opt + calibration (seed 0) ===")
    raw0, c0 = coarse_optimize(0)
    metro_t, sigma = calibrate(raw0)
    metro_t = tune_metro(raw0, sigma, metro_t)
    print(f"Final: metro_t={metro_t:.6f}, sigma={sigma:.5f}")

    # === All coarse optimizations ===
    print("\n=== Coarse optimization (seeds 1-3) ===")
    all_raw = [raw0]
    for s in range(1, N_SEEDS):
        raw_s, _ = coarse_optimize(s)
        all_raw.append(raw_s)

    # === SA + fine-tune for each seed ===
    print("\n=== SA + fine-tune ===")
    global_best_c = float('inf')
    global_best_raw = None

    for s, raw_c in enumerate(all_raw):
        print(f"\n--- Seed {s} ---")
        sa_raw, sa_c = run_sa(raw_c, sigma, metro_t, SA_ITERS)

        print(f"  Upsampling to N={N_FINE}...")
        raw_fine = upsample(sa_raw)
        raw_fine = run_adam(raw_fine, [0.05, 0.01, 0.003, 0.001, 0.0003], 15000)
        c_fine = hard_c_from_raw(raw_fine)
        print(f"  Seed {s} final C = {c_fine:.6f}")

        if c_fine < global_best_c:
            global_best_c = c_fine
            global_best_raw = raw_fine

    print(f"\n=== Best C: {global_best_c:.6f} ===")
    return np.array(jax.nn.softplus(global_best_raw))
