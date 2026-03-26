# Problem Helpers

All reusable helpers live here. Import them in solution files as:

    from helpers.<module> import <function>

`evaluate.py` adds `problem/` to `sys.path`, so `helpers/` is directly importable.

---

## Built-in helpers

### `core.py` — Problem-specific core helper

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c` | `(f_values: jnp.ndarray) -> float` | JAX-based, differentiable. Computes C = max(f★f) / (∫f)² via FFT. |

Import: `from helpers.core import compute_c`

---

## Experimentator-created helpers

Helpers built by experimentator agents and validated by the orchestrator appear below once deployed.

*(none yet)*

---

## How helpers are added

Experimentator agents write helpers to `output/helpers/<name>.py`. The orchestrator:
1. Validates syntax, checks import blocklist, verifies no top-level side effects.
2. Deploys the file here as `problem/helpers/<name>.py`.
3. Updates this README and the orchestrator's `_helpers_section()` prompt.

Do **not** add files directly to this directory — always go through the experimentator workflow.
