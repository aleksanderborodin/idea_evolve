# Available Helpers

## `helpers.core`

Import: `from helpers.core import compile_and_test, read_baseline_times`

### `compile_and_test(cpp_code: str) -> dict`
Quick compile + correctness check without benchmarking.
Returns `{"ok": True}` or `{"ok": False, "error": "..."}`.
Use this to iterate quickly on correctness before running the full evaluation.

### `read_baseline_times() -> dict`
Returns the baseline V14opt times in microseconds per benchmark size.
Example: `{"32x1024x9": 15.78, "64x16384x27": 911.64, "128x65536x54": 12422.36}`
