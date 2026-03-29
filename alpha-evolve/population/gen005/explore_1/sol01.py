# fitness: 1.5227
# Approach: Calibrated Simulated Annealing at N=23, gen5 (3rd attempt)
# Key fixes vs gen4: 2 seeds (not 4), 100 SA iters (not 500), 5k coarse steps/phase (not 10k)
# SA calibration: sigma=0.05*std(raw_params), 20 trials, metro_t=2*median|ΔC|, tune to 20-40% acceptance
# Cold inner optimizer: T=0.001 only (300 steps) after each SA acceptance
# Upsample: interpolate_sparse (NOT cubic spline) to N=600
# Fine-tune: T=0.05->0.01->0.003->0.001->0.0003, 10k steps/phase at N=600

import sys
import time
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helpers.core import compute_c
from helpers.interpolation import interpolate_sparse
from helpers.inv_softplus import inv_softplus_safe

# Enable float64 for better numerical precision
jax.config.update("jax_enable_x64", True)


def make_smooth_c(N):
    """Smooth-max approximation of C for gradient-based optimization."""
    domain_width = 0.5
    dx = domain_width / N

    def _fn(raw_params, temp):
        f_nn = jax.nn.softplus(raw_params)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq = jnp.maximum(integral_f ** 2, 1e-9)
        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx
        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
        return smooth_max / integral_f_sq

    return jax.jit(_fn)


def run_stage(raw_init, temps, steps_per_temp, peak_lr=0.01, end_lr=1e-5):
    """Run smooth-max Adam optimization for given temperature schedule."""
    N = len(raw_init)
    smooth_c = make_smooth_c(N)
    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=peak_lr,
        warmup_steps=min(300, total_steps // 10),
        decay_steps=total_steps, end_value=end_lr)
    optimizer = optax.adam(learning_rate=schedule)

    step_fn_raw = lambda raw_params, temp, opt_state: (
        lambda loss_grads: (
            optax.apply_updates(raw_params, optimizer.update(loss_grads[1], opt_state, raw_params)[0]),
            optimizer.update(loss_grads[1], opt_state, raw_params)[1],
            loss_grads[0]
        )
    )(jax.value_and_grad(smooth_c)(raw_params, temp))

    @jax.jit
    def step_fn(raw_params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c)(raw_params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, raw_params)
        return optax.apply_updates(raw_params, updates), new_opt_state, loss

    opt_state = optimizer.init(raw_init)
    raw_params = raw_init
    for temp in temps:
        t = jnp.array(temp, dtype=jnp.float64)
        for _ in range(steps_per_temp):
            raw_params, opt_state, _ = step_fn(raw_params, t, opt_state)
    return raw_params


def make_arcsine_init(N, seed):
    """Arcsine-weighted initialization (best family from gen3)."""
    x = jnp.linspace(-0.25, 0.25, N)
    # Arcsine density: high at boundaries, low in middle — strongly asymmetric
    eps = 0.02
    arcsine_weight = 1.0 / jnp.sqrt(jnp.maximum((0.25 - jnp.abs(x)) * (0.25 + jnp.abs(x)), eps))
    arcsine_weight = arcsine_weight / jnp.sum(arcsine_weight)
    # Add asymmetry tilt
    if seed == 0:
        tilt = jnp.linspace(0.1, 1.0, N)
    else:
        # Comb-like: two dominant peaks
        tilt = 0.5 + 0.5 * jnp.sin(3 * jnp.pi * (x + 0.25) / 0.5)
    f = arcsine_weight * N * tilt
    f = jnp.maximum(f, 1e-4)
    return inv_softplus_safe(f)


def entrypoint():
    N_COARSE = 23
    N_FINE = 600
    N_SEEDS = 2
    SA_ITERS = 100
    SA_INNER_STEPS = 300
    COARSE_STEPS_PER_PHASE = 5000
    FINE_STEPS_PER_PHASE = 10000
    SA_EARLY_STOP = 30  # stop if no improvement for this many consecutive iters

    # ---- STEP 0: Timing benchmark (100 steps at N=23) ----
    print("=== TIMING BENCHMARK ===")
    smooth_c_bench = make_smooth_c(N_COARSE)
    bench_raw = jnp.ones(N_COARSE, dtype=jnp.float64) * 0.5
    bench_opt = optax.adam(1e-3)
    bench_state = bench_opt.init(bench_raw)

    @jax.jit
    def bench_step(raw, state):
        loss, grads = jax.value_and_grad(smooth_c_bench)(raw, jnp.array(0.01, dtype=jnp.float64))
        updates, new_state = bench_opt.update(grads, state, raw)
        return optax.apply_updates(raw, updates), new_state, loss

    # Warmup JIT
    bench_raw, bench_state, _ = bench_step(bench_raw, bench_state)

    t0 = time.time()
    for _ in range(100):
        bench_raw, bench_state, _ = bench_step(bench_raw, bench_state)
    bench_elapsed = time.time() - t0
    step_time_ms = bench_elapsed / 100 * 1000
    print(f"N=23 step time: {step_time_ms:.3f}ms per step")

    if step_time_ms > 1.0:
        print(f"WARNING: step time {step_time_ms:.3f}ms > 1ms. Reducing budget.")
        # Reduce budget proportionally
        factor = 0.5 / step_time_ms  # target 0.5ms
        SA_ITERS = max(20, int(SA_ITERS * factor))
        SA_INNER_STEPS = max(100, int(SA_INNER_STEPS * factor))
        print(f"Adjusted: SA_ITERS={SA_ITERS}, SA_INNER_STEPS={SA_INNER_STEPS}")

    # Estimate total budget
    total_coarse_steps = N_SEEDS * 3 * COARSE_STEPS_PER_PHASE
    total_sa_steps = N_SEEDS * SA_ITERS * SA_INNER_STEPS
    total_fine_steps = 5 * FINE_STEPS_PER_PHASE
    # N=600 steps take ~3x longer (rough estimate)
    estimated_s = (total_coarse_steps + total_sa_steps) * step_time_ms / 1000 + total_fine_steps * step_time_ms * 3 / 1000
    print(f"Estimated total time: {estimated_s:.1f}s")
    print(f"Budget: coarse={total_coarse_steps} + SA={total_sa_steps} + fine={total_fine_steps}")

    # ---- STEP 1: Coarse optimization at N=23 ----
    print("\n=== COARSE OPTIMIZATION (N=23) ===")
    coarse_temps = [0.05, 0.003, 0.001]
    best_coarse_raw = None
    best_coarse_c = float('inf')

    for seed in range(N_SEEDS):
        print(f"  Seed {seed}: ", end='', flush=True)
        raw_init = make_arcsine_init(N_COARSE, seed)
        raw_params = run_stage(raw_init, coarse_temps, COARSE_STEPS_PER_PHASE)
        f = jax.nn.softplus(raw_params)
        c = float(compute_c(f))
        print(f"C = {c:.6f}")
        if c < best_coarse_c:
            best_coarse_c = c
            best_coarse_raw = raw_params

    print(f"Best coarse C: {best_coarse_c:.6f}")

    # ---- STEP 2: SA Calibration ----
    print("\n=== SA CALIBRATION ===")
    # Start from best coarse result
    raw_cal = best_coarse_raw.copy()
    f_cal = jax.nn.softplus(raw_cal)
    c_baseline = float(compute_c(f_cal))
    print(f"Baseline C for calibration: {c_baseline:.6f}")

    # sigma = 0.05 * std(raw_params)
    sigma = 0.05 * float(jnp.std(raw_cal))
    print(f"sigma = {sigma:.6f}")

    # 20 trial perturbations to measure median |ΔC|
    key = jax.random.PRNGKey(999)
    delta_cs = []
    for i in range(20):
        key, subkey = jax.random.split(key)
        perturb = sigma * jax.random.normal(subkey, raw_cal.shape)
        raw_pert = raw_cal + perturb
        f_pert = jax.nn.softplus(raw_pert)
        c_pert = float(compute_c(f_pert))
        delta_cs.append(abs(c_pert - c_baseline))

    median_delta_c = float(np.median(delta_cs))
    metro_t = 2.0 * median_delta_c
    print(f"Median |ΔC| = {median_delta_c:.6f}, initial metro_t = {metro_t:.6f}")

    # Tune metro_t: run 10 test SA steps, target 20-40% acceptance
    # Also need inner optimizer for calibration test
    smooth_c_coarse = make_smooth_c(N_COARSE)
    cold_opt = optax.adam(1e-3)

    def run_inner_cold(raw_params):
        """Run cold inner optimizer (T=0.001, 300 steps)."""
        opt_state = cold_opt.init(raw_params)

        @jax.jit
        def inner_step(raw, state):
            loss, grads = jax.value_and_grad(smooth_c_coarse)(raw, jnp.array(0.001, dtype=jnp.float64))
            updates, new_state = cold_opt.update(grads, state, raw)
            return optax.apply_updates(raw, updates), new_state

        for _ in range(SA_INNER_STEPS):
            raw_params, opt_state = inner_step(raw_params, opt_state)
        return raw_params

    for tune_iter in range(3):
        acceptances = 0
        test_raw = raw_cal.copy()
        test_c = float(compute_c(jax.nn.softplus(test_raw)))
        key, _ = jax.random.split(key)
        for i in range(10):
            key, subkey = jax.random.split(key)
            perturb = sigma * jax.random.normal(subkey, test_raw.shape)
            proposed_raw = test_raw + perturb
            proposed_raw = run_inner_cold(proposed_raw)
            proposed_c = float(compute_c(jax.nn.softplus(proposed_raw)))
            delta = proposed_c - test_c
            if delta < 0 or np.random.random() < np.exp(-delta / metro_t):
                test_raw = proposed_raw
                test_c = proposed_c
                acceptances += 1
        accept_rate = acceptances / 10.0
        print(f"  Tune iter {tune_iter}: accept_rate={accept_rate:.2f}, metro_t={metro_t:.6f}")
        if accept_rate > 0.40:
            metro_t /= 2.0
            print(f"    Accept rate too high, halving metro_t -> {metro_t:.6f}")
        elif accept_rate < 0.20:
            metro_t *= 2.0
            print(f"    Accept rate too low, doubling metro_t -> {metro_t:.6f}")
        else:
            print(f"    Accept rate in target range [0.20, 0.40]. metro_t = {metro_t:.6f}")
            break

    print(f"Final metro_t = {metro_t:.6f}")

    # ---- STEP 3: Main SA loop (per seed) ----
    print("\n=== MAIN SA LOOP ===")
    best_sa_raw = None
    best_sa_c = float('inf')
    best_sa_f = None

    np.random.seed(42)

    for seed in range(N_SEEDS):
        print(f"\n--- Seed {seed} ---")
        # Re-run coarse optimization for this seed
        raw_init = make_arcsine_init(N_COARSE, seed)
        raw_params = run_stage(raw_init, coarse_temps, COARSE_STEPS_PER_PHASE)
        current_c = float(compute_c(jax.nn.softplus(raw_params)))
        current_raw = raw_params
        print(f"  Starting C: {current_c:.6f}")

        best_c_seed = current_c
        best_raw_seed = current_raw
        no_improvement_count = 0

        key = jax.random.PRNGKey(seed * 1000)

        for sa_iter in range(SA_ITERS):
            key, subkey = jax.random.split(key)
            perturb = sigma * jax.random.normal(subkey, current_raw.shape)
            proposed_raw = current_raw + perturb
            proposed_raw = run_inner_cold(proposed_raw)
            proposed_c = float(compute_c(jax.nn.softplus(proposed_raw)))

            delta = proposed_c - current_c
            accepted = delta < 0 or np.random.random() < np.exp(-delta / metro_t)

            if accepted:
                current_raw = proposed_raw
                current_c = proposed_c
                if current_c < best_c_seed:
                    best_c_seed = current_c
                    best_raw_seed = current_raw
                    no_improvement_count = 0
                    if sa_iter % 10 == 0 or sa_iter < 5:
                        print(f"  SA iter {sa_iter}: NEW BEST C = {best_c_seed:.6f}")
                else:
                    no_improvement_count += 1
            else:
                no_improvement_count += 1

            if no_improvement_count >= SA_EARLY_STOP:
                print(f"  SA early stop at iter {sa_iter} (no improvement for {SA_EARLY_STOP} iters)")
                break

        print(f"  Seed {seed} best C: {best_c_seed:.6f}")

        if best_c_seed < best_sa_c:
            best_sa_c = best_c_seed
            best_sa_raw = best_raw_seed
            best_sa_f = jax.nn.softplus(best_raw_seed)

    print(f"\nBest SA result: C = {best_sa_c:.6f}")

    # ---- STEP 4: Upsample to N=600 using interpolate_sparse ----
    print("\n=== UPSAMPLING TO N=600 ===")
    f_coarse = np.array(best_sa_f)
    f_upsampled = interpolate_sparse(f_coarse, N_FINE, threshold=1e-4)
    f_up_jax = jnp.array(f_upsampled)
    c_upsampled = float(compute_c(f_up_jax))
    print(f"C after upsampling: {c_upsampled:.6f}")

    # Convert to raw_params for fine-tuning
    raw_fine_init = inv_softplus_safe(f_up_jax)

    # ---- STEP 5: Fine-tuning at N=600 ----
    print("\n=== FINE-TUNING AT N=600 ===")
    fine_temps = [0.05, 0.01, 0.003, 0.001, 0.0003]
    raw_fine = run_stage(raw_fine_init, fine_temps, FINE_STEPS_PER_PHASE)
    f_final = jax.nn.softplus(raw_fine)
    c_final = float(compute_c(f_final))
    print(f"C after fine-tuning: {c_final:.6f}")

    return np.array(jnp.maximum(f_final, 0.0))


if __name__ == "__main__":
    import json
    result = entrypoint()
    print(f"Final array shape: {result.shape}")
    print(f"Min/Max: {result.min():.6f} / {result.max():.6f}")
