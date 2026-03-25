# fitness: TBD
# Lion optimizer + cosine annealing warm restarts, N=2000
# Lion has different update dynamics than Adam, tends to find different basins

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def run_phase(f_init, optimizer, steps):
    opt_state = optimizer.init(f_init)
    f = f_init

    @jax.jit
    def step_fn(f, s):
        loss, g = jax.value_and_grad(compute_c)(f)
        upd, s = optimizer.update(g, s, f)
        return optax.apply_updates(f, upd), s, loss

    best_f = f
    best_loss = float('inf')
    for i in range(steps):
        f, opt_state, loss = step_fn(f, opt_state)
        if float(loss) < best_loss:
            best_loss = float(loss)
            best_f = f
    return jax.nn.relu(best_f)


def entrypoint() -> np.ndarray:
    N = 2000

    # Start with flat block init like baseline
    key = jax.random.PRNGKey(42)
    f = jnp.zeros((N,))
    si, ei = N // 4, 3 * N // 4
    f = f.at[si:ei].set(1.0)
    f = f + 0.05 * jax.random.uniform(key, (N,))

    # Phase 1: Adam warmup at N=2000 (30k steps)
    schedule1 = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.003,
        warmup_steps=2000, decay_steps=28000,
        end_value=0.003 * 1e-4,
    )
    f = run_phase(f, optax.adam(schedule1), 30000)

    # Phase 2: Lion optimizer with cosine decay (80k steps)
    schedule2 = optax.cosine_decay_schedule(init_value=3e-5, decay_steps=80000, alpha=1e-4)
    f = run_phase(f, optax.lion(learning_rate=schedule2), 80000)

    # Phase 3: Fine-tune with Adam at very low LR (30k steps)
    schedule3 = optax.cosine_decay_schedule(init_value=5e-4, decay_steps=30000, alpha=1e-4)
    f = run_phase(f, optax.adam(schedule3), 30000)

    return np.array(f)
