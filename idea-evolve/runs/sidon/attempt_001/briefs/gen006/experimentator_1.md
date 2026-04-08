## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 105
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_105.py` → fitness = 105
Third best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank03_104.py` → fitness = 104

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/README.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`

## Directive

**Task: Create two shared helper modules for the pipeline.**

This is a mandatory helper creation task. Multiple agents across gens 4-5 needed these
utilities and had to reimplement them from scratch each time (REC-5, REC-6 from system
recommendations — 2+ consecutive generations unresolved).

### Helper 1: `output/helpers/rokicki_data.py`

Store the best known Sidon sets as Python literals so all future agents can import them
directly instead of hardcoding or downloading.

```python
"""Best known Sidon sets from the Rokicki-Dogon database (cube20.org/golomb/)."""

# 105-mark ruler: Bose-Chowla ap q=107, multiplier=433, span=9884
BEST_105 = [0, 12, 200, 213, 235, 296, 402, 468, 473, 513, 725, 854, 855, 964, 1018, 1059, 1209, 1375, 1392, 1578, 1657, 1664, 1907, 1974, 2048, 2087, 2208, 2285, 2295, 2695, 2793, 2818, 2842, 2868, 2969, 2975, 3074, 3112, 3130, 3190, 3194, 3322, 3640, 3654, 3683, 4066, 4081, 4128, 4277, 4342, 4358, 4411, 4431, 4523, 4662, 4698, 4717, 4820, 5239, 5291, 5323, 5381, 5408, 5683, 5839, 5992, 6026, 6034, 6219, 6365, 6441, 6509, 6589, 6768, 6952, 7009, 7161, 7358, 7446, 7565, 7624, 7823, 7860, 7893, 7923, 8228, 8231, 8259, 8390, 8399, 8653, 8697, 8823, 8871, 8917, 8968, 9330, 9402, 9520, 9644, 9655, 9746, 9748, 9769, 9884]

# 104-mark ruler: Singer pp q=103, multiplier=400, span=9581
BEST_104 = [...]  # Extract from population/top/rank03_104.py

# 102-mark ruler: Singer pp q=101, multiplier=1758, span=9218
BEST_102 = [...]  # Extract from population/gen003/exploit_1/sol01.py or similar
```

Read the actual solution files to get the exact integer lists for BEST_104 and BEST_102.

### Helper 2: `output/helpers/extend.py`

Shared utility functions for Sidon set manipulation:

```python
"""Utility functions for extending and perturbing Sidon sets."""

def greedy_extend(initial_set, N=10000):
    """Greedily add elements to a Sidon set. Returns the extended set (sorted list)."""
    # Use a set of used differences for O(k) per candidate check
    # Iterate through 0..N, add element if all new differences are unique
    ...

def count_addable(S, N=10000):
    """Count how many elements in {0..N} can be individually added to S."""
    ...

def random_perturbation(S, k, N=10000):
    """Remove k random elements from S, greedily re-extend, return result."""
    ...

def blocking_power(S, N=10000):
    """For each element in S, count how many potential elements it blocks."""
    ...
```

**Implementation requirements:**
- Use Python sets for O(1) difference lookups — this is performance-critical
- `greedy_extend` must handle both sorted lists and unsorted inputs
- All functions must work correctly (test with `from helpers.core import is_sidon`)
- Include a `if __name__ == "__main__"` block that tests each function on the 105-mark set

### Validation

After writing both helpers:
1. Test that `from helpers.rokicki_data import BEST_105` works and `is_sidon(BEST_105)` returns True
2. Test that `greedy_extend(BEST_105[:100], 10000)` returns a set of size >= 100
3. Test that `count_addable(BEST_105, 10000)` returns 0 (confirming greedy-maximality)
4. Test that `random_perturbation(BEST_105, 3, 10000)` returns a valid Sidon set

Write helpers to `output/helpers/rokicki_data.py` and `output/helpers/extend.py`. The
orchestrator will validate and deploy them to `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/`.
