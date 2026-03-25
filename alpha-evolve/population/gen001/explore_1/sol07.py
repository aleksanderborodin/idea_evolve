# fitness: 0.0
# More aggressive multi-seed: 32 seeds with diverse asymmetric inits, top-3 fully refined
# Strategy: sol05 showed multi-seed finds better basins; 4x more seeds + better asymmetric init
# Key insight: optimal function likely asymmetric; deliberately explore asymmetric initializations

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize

from helper import compute_c


def run_adam_best(f_init, num_steps, lr, warmup=500):
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=lr,
        warmup_steps=warmup, decay_steps=num_steps - warmup,
        end_value=lr * 1e-5,
    )
    optimizer = optax.adam(learning_rate=schedule)
    f_values = jnp.array(f_init, dtype=jnp.float32)
    opt_state = optimizer.init(f_values)

    @jax.jit
    def step_fn(f_v, o_s):
        loss, grads = jax.value_and_grad(compute_c)(f_v)
        updates, o_s = optimizer.update(grads, o_s, f_v)
        f_v = optax.apply_updates(f_v, updates)
        return f_v, o_s, loss

    best_loss = float('inf')
    best_f = f_values
    for _ in range(num_steps):
        f_values, opt_state, loss = step_fn(f_values, opt_state)
        if float(loss) < best_loss:
            best_loss = float(loss)
            best_f = f_values

    return np.array(jax.nn.relu(best_f)), best_loss


def lbfgs(f_init):
    N = len(f_init)
    def obj_grad(x):
        f_jax = jnp.array(x, dtype=jnp.float32)
        loss, grads = jax.value_and_grad(compute_c)(f_jax)
        return float(loss), np.array(grads, dtype=np.float64)

    res = scipy.optimize.minimize(
        obj_grad, f_init.astype(np.float64), method='L-BFGS-B', jac=True,
        bounds=[(0.0, None)] * N,
        options={'maxiter': 5000, 'ftol': 1e-14, 'gtol': 1e-9},
    )
    return np.maximum(res.x, 0.0).astype(np.float32)


def make_init(N, seed, mode):
    """Create diverse initializations emphasizing asymmetric shapes."""
    key = jax.random.PRNGKey(seed * 31 + 17)
    f = jnp.zeros((N,))

    if mode == 0:  # flat center block, no offset
        f = f.at[N//4:3*N//4].set(1.0)
    elif mode == 1:  # shifted block (positive direction)
        shift = N // 8
        f = f.at[min(N//4+shift, N-1):min(3*N//4+shift, N)].set(1.0)
    elif mode == 2:  # shifted block (negative direction)
        shift = N // 8
        f = f.at[max(N//4-shift, 0):max(3*N//4-shift, 0)].set(1.0)
    elif mode == 3:  # right half only
        f = f.at[N//2:].set(1.0)
    elif mode == 4:  # left half only
        f = f.at[:N//2].set(1.0)
    elif mode == 5:  # right 3/4
        f = f.at[N//4:].set(1.0)
    elif mode == 6:  # left 3/4
        f = f.at[:3*N//4].set(1.0)
    elif mode == 7:  # whole domain
        f = f.at[:].set(1.0)
    elif mode == 8:  # right edge emphasis (linear ramp up toward right)
        xs = jnp.linspace(0, 1, N)
        f = xs  # linearly increasing
    elif mode == 9:  # Gaussian center
        xs = jnp.linspace(-0.25, 0.25, N)
        f = jnp.exp(-xs**2 / (2 * 0.08**2))
    elif mode == 10:  # Gaussian right-shifted
        xs = jnp.linspace(-0.25, 0.25, N)
        f = jnp.exp(-(xs - 0.1)**2 / (2 * 0.07**2))
    elif mode == 11:  # Hann window
        xs = jnp.linspace(0, 1, N)
        f = 0.5 - 0.5 * jnp.cos(2 * jnp.pi * xs)
    elif mode == 12:  # Shifted block x2 positive
        shift = N // 5
        f = f.at[min(N//4+shift, N-1):min(3*N//4+shift, N)].set(1.0)
    elif mode == 13:  # Wide right block
        f = f.at[N//5:].set(1.0)
    elif mode == 14:  # Wide left block
        f = f.at[:4*N//5].set(1.0)
    elif mode == 15:  # Raised half
        xs = jnp.linspace(-0.25, 0.25, N)
        f = jnp.where(xs >= 0, 1.0, 0.5)
    else:
        shift = ((seed % 8) - 4) * N // 20
        f = f.at[max(0, N//4+shift):min(N, 3*N//4+shift)].set(1.0)

    noise = 0.03 * jax.random.uniform(key, (N,))
    f = f + noise
    return np.array(jax.nn.relu(f))


def entrypoint() -> np.ndarray:
    N = 600
    n_modes = 16
    seeds_per_mode = 2

    # Phase 1: 32 seeds × 12k steps
    results = []
    for mode in range(n_modes):
        for s in range(seeds_per_mode):
            seed = mode * seeds_per_mode + s
            f_init = make_init(N, seed, mode)
            f_res, loss = run_adam_best(f_init, num_steps=12000, lr=0.008)
            results.append((loss, f_res))

    results.sort(key=lambda x: x[0])

    # Phase 2: refine top 3 with 100k Adam steps
    top_refined = []
    for loss_0, f_0 in results[:3]:
        f_r, loss_r = run_adam_best(f_0, num_steps=100000, lr=0.004)
        top_refined.append((loss_r, f_r))

    top_refined.sort(key=lambda x: x[0])
    _, best_f = top_refined[0]

    # Phase 3: L-BFGS fine-tune
    return lbfgs(best_f)
