# fitness: 1.5227
# Approach: Calibrated SA at N=23 — CORRECTED: Metropolis on RAW perturbed state,
#   inner optimizer runs ONLY on accepted proposals (not before acceptance check).
# Key fix vs sol01: sol01 ran inner optimizer before Metropolis check → ~100% acceptance (wrong).
# Correct SA-with-local-search:
#   1. Perturb current_raw → proposed_raw
#   2. Compute C(softplus(proposed_raw)) — no inner opt
#   3. Metropolis(ΔC) on raw perturbed C
#   4. If accepted: run inner optimizer on proposed_raw → refined_raw
#   5. Set current to refined_raw
# This ensures metro_t calibrated from raw perturbations actually controls acceptance.

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

jax.config.update("jax_enable_x64", True)


def make_smooth_c(N):
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
    N = len(raw_init)
    smooth_c = make_smooth_c(N)
    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=peak_lr,
        warmup_steps=min(300, total_steps // 10),
        decay_steps=total_steps, end_value=end_lr)
    optimizer = optax.adam(learning_rate=schedule)

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
    x = jnp.linspace(-0.25, 0.25, N)
    eps = 0.02
    arcsine_weight = 1.0 / jnp.sqrt(jnp.maximum((0.25 - jnp.abs(x)) * (0.25 + jnp.abs(x)), eps))
    arcsine_weight = arcsine_weight / jnp.sum(arcsine_weight)
    if seed == 0:
        tilt = jnp.linspace(0.1, 1.0, N)
    else:
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
    SA_EARLY_STOP_NO_ACCEPT = 30  # stop if no ACCEPTANCE for this many consecutive iters

    # ---- TIMING BENCHMARK ----
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

    bench_raw, bench_state, _ = bench_step(bench_raw, bench_state)  # warmup
    t0 = time.time()
    for _ in range(100):
        bench_raw, bench_state, _ = bench_step(bench_raw, bench_state)
    step_time_ms = (time.time() - t0) / 100 * 1000
    print(f"N={N_COARSE} step time: {step_time_ms:.3f}ms")

    # SA inner optimizer (cold, T=0.001, fixed steps)
    smooth_c_coarse = make_smooth_c(N_COARSE)
    cold_opt = optax.adam(5e-4)

    def run_inner_cold(raw_params):
        """Run cold inner optimizer on ACCEPTED proposals. T=0.001, 300 steps."""
        opt_state = cold_opt.init(raw_params)

        @jax.jit
        def inner_step(raw, state):
            loss, grads = jax.value_and_grad(smooth_c_coarse)(raw, jnp.array(0.001, dtype=jnp.float64))
            updates, new_state = cold_opt.update(grads, state, raw)
            return optax.apply_updates(raw, updates), new_state

        for _ in range(SA_INNER_STEPS):
            raw_params, opt_state = inner_step(raw_params, opt_state)
        return raw_params

    # ---- COARSE OPTIMIZATION ----
    print("\n=== COARSE OPTIMIZATION (N=23) ===")
    coarse_temps = [0.05, 0.003, 0.001]
    seeds_raw = []
    seeds_c = []
    for seed in range(N_SEEDS):
        raw_init = make_arcsine_init(N_COARSE, seed)
        raw_params = run_stage(raw_init, coarse_temps, COARSE_STEPS_PER_PHASE)
        # Refine with cold inner optimizer to get proper local min
        raw_params = run_inner_cold(raw_params)
        c = float(compute_c(jax.nn.softplus(raw_params)))
        print(f"  Seed {seed}: C = {c:.6f}")
        seeds_raw.append(raw_params)
        seeds_c.append(c)

    best_seed_idx = int(np.argmin(seeds_c))

    # ---- SA CALIBRATION (on raw perturbations, NO inner optimizer) ----
    print("\n=== SA CALIBRATION ===")
    raw_cal = seeds_raw[best_seed_idx]
    c_baseline = seeds_c[best_seed_idx]
    print(f"Calibration baseline C: {c_baseline:.6f}")

    sigma = 0.05 * float(jnp.std(raw_cal))
    print(f"sigma = {sigma:.6f} (0.05 * std(raw_params))")

    # 20 trial perturbations — NO INNER OPTIMIZER — measure |ΔC|
    key = jax.random.PRNGKey(9999)
    delta_cs = []
    for i in range(20):
        key, subkey = jax.random.split(key)
        perturb = sigma * jax.random.normal(subkey, raw_cal.shape)
        raw_pert = raw_cal + perturb
        c_pert = float(compute_c(jax.nn.softplus(raw_pert)))
        delta_cs.append(abs(c_pert - c_baseline))

    median_delta_c = float(np.median(delta_cs))
    metro_t = 2.0 * median_delta_c
    print(f"Median |ΔC| (raw) = {median_delta_c:.6f}, initial metro_t = {metro_t:.6f}")

    # Tune metro_t: 10 test SA steps with RAW C comparison (no inner optimizer)
    np.random.seed(42)
    for tune_iter in range(4):
        acceptances = 0
        test_raw = raw_cal.copy()
        test_c = c_baseline
        key, _ = jax.random.split(key)
        for _ in range(10):
            key, subkey = jax.random.split(key)
            perturb = sigma * jax.random.normal(subkey, test_raw.shape)
            proposed_raw = test_raw + perturb
            proposed_c = float(compute_c(jax.nn.softplus(proposed_raw)))
            delta = proposed_c - test_c
            # Metropolis on RAW C
            if delta < 0 or np.random.random() < np.exp(-delta / metro_t):
                test_raw = proposed_raw
                test_c = proposed_c
                acceptances += 1
        accept_rate = acceptances / 10.0
        print(f"  Tune iter {tune_iter}: accept_rate={accept_rate:.2f}, metro_t={metro_t:.6f}")
        if accept_rate > 0.40:
            metro_t /= 2.0
        elif accept_rate < 0.20:
            metro_t *= 2.0
        else:
            print(f"  -> Converged at metro_t = {metro_t:.6f}")
            break

    print(f"Final metro_t = {metro_t:.6f}")

    # ---- MAIN SA LOOP ----
    print("\n=== MAIN SA LOOP ===")
    best_sa_raw = seeds_raw[best_seed_idx]
    best_sa_c = seeds_c[best_seed_idx]
    best_sa_f = jax.nn.softplus(best_sa_raw)

    for seed in range(N_SEEDS):
        print(f"\n--- Seed {seed} (starting C={seeds_c[seed]:.6f}) ---")
        current_raw = seeds_raw[seed]
        current_c = seeds_c[seed]
        best_c_seed = current_c
        best_raw_seed = current_raw
        no_accept_count = 0  # stop if no ACCEPTANCE (not no improvement) for 30 consecutive

        key = jax.random.PRNGKey(seed * 1000 + 42)

        for sa_iter in range(SA_ITERS):
            key, subkey = jax.random.split(key)
            perturb = sigma * jax.random.normal(subkey, current_raw.shape)
            proposed_raw_raw = current_raw + perturb  # raw perturbation, no inner opt

            # Compute C on RAW perturbation (no inner optimizer)
            proposed_c_raw = float(compute_c(jax.nn.softplus(proposed_raw_raw)))

            # Metropolis criterion on RAW perturbed C
            delta = proposed_c_raw - current_c
            accepted = delta < 0 or np.random.random() < np.exp(-delta / metro_t)

            if accepted:
                # NOW run inner optimizer on accepted proposal
                refined_raw = run_inner_cold(proposed_raw_raw)
                refined_c = float(compute_c(jax.nn.softplus(refined_raw)))

                current_raw = refined_raw
                current_c = refined_c
                no_accept_count = 0

                if refined_c < best_c_seed:
                    best_c_seed = refined_c
                    best_raw_seed = refined_raw
                    print(f"  SA iter {sa_iter}: NEW BEST C = {best_c_seed:.6f} (raw perturbed C={proposed_c_raw:.6f})")
            else:
                no_accept_count += 1

            if no_accept_count >= SA_EARLY_STOP_NO_ACCEPT:
                print(f"  SA early stop at iter {sa_iter}: no acceptance for {SA_EARLY_STOP_NO_ACCEPT} iters")
                break

            if sa_iter % 20 == 19:
                print(f"  SA iter {sa_iter}: current_c={current_c:.6f}, best_c={best_c_seed:.6f}")

        print(f"  Seed {seed} best C: {best_c_seed:.6f}")

        if best_c_seed < best_sa_c:
            best_sa_c = best_c_seed
            best_sa_raw = best_raw_seed
            best_sa_f = jax.nn.softplus(best_raw_seed)

    print(f"\nBest SA C (before upsampling): {best_sa_c:.6f}")

    # ---- UPSAMPLE TO N=600 ----
    print("\n=== UPSAMPLING TO N=600 ===")
    f_coarse = np.array(best_sa_f)
    f_upsampled = interpolate_sparse(f_coarse, N_FINE, threshold=1e-4)
    f_up_jax = jnp.array(f_upsampled)
    c_upsampled = float(compute_c(f_up_jax))
    print(f"C after upsampling: {c_upsampled:.6f}")

    # Convert to raw_params for fine-tuning
    raw_fine_init = inv_softplus_safe(f_up_jax)

    # ---- FINE-TUNING AT N=600 ----
    print("\n=== FINE-TUNING AT N=600 ===")
    fine_temps = [0.05, 0.01, 0.003, 0.001, 0.0003]
    raw_fine = run_stage(raw_fine_init, fine_temps, FINE_STEPS_PER_PHASE)
    f_final = jax.nn.softplus(raw_fine)
    c_final = float(compute_c(f_final))
    print(f"C after fine-tuning: {c_final:.6f}")

    return np.array(jnp.maximum(f_final, 0.0))
