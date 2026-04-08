# User Directives

Write directives here to steer the evolution process. Each directive is a `.md` file
with YAML frontmatter. The Architect reads all active directives every generation and
MUST acknowledge each one.

## Creating a Directive

Create a new `.md` file in this directory (e.g., `try_simulated_annealing.md`):

```markdown
---
id: try_sa
name: Try simulated annealing with slow cooling
mode: test_next_gen
proposed_gen: 7
status: pending
resolution: null
---

Simulated annealing with very slow cooling (T *= 0.9999) should break past the 105
plateau. The greedy approach gets stuck in local optima — SA allows temporary score
decreases to escape them.

Evidence: SA is proven effective for combinatorial optimization. Our current best
solutions all use greedy/local search variants.
```

## Modes

| Mode | Meaning | Architect obligation |
|------|---------|---------------------|
| `test_next_gen` | Test this in the very next generation | MUST assign agent(s) to test it |
| `one_shot` | Test once, give definitive answer | MUST assign agent(s), then resolve |
| `keep_in_mind` | Factor in when relevant, no urgency | Should consider, no forced action |
| `mandatory` | Work on every gen until resolved | MUST have active work each gen |

## Status Lifecycle

```
pending ──► acknowledged ──► testing ──► resolved
                │                           │
                └── (keep_in_mind stays ─────┘
                     acknowledged until
                     relevant)
```

- **pending** — You just wrote it, Architect hasn't seen it yet
- **acknowledged** — Architect read it and planned for it
- **testing** — Agent(s) actively working on it
- **resolved** — Done. Check `resolution` field for outcome

## Resolution Values

- `confirmed` — Your idea was right, evidence supports it
- `refuted` — Your idea was wrong, evidence contradicts it (with explanation)
- `partially_confirmed` — Partly right, partly wrong
- `inconclusive` — Tested but no clear signal
- `superseded` — Overtaken by events (new best approach, problem changed, etc.)

## System Feedback

The Architect appends feedback sections to your directive file after each generation:

```markdown
### Gen 8 — Architect Response
**Assigned agents:** explore_1, experimentator_1
Assigned explore_1 to test SA with cooling 0.9999. Experimentator_1 will
calibrate optimal cooling schedule.

### Gen 9 — Architect Response
**Status: resolved (confirmed)**
explore_1 achieved score 108 with SA (cooling 0.9999), beating previous best
of 105. SA confirmed as effective. The key was the slow cooling schedule —
fast cooling (0.99) was tried in gen 5 and failed.
```

## Tips

- Be specific. "Try something different" is useless. "Try constructing Sidon sets
  from perfect difference sets over GF(p)" is actionable.
- Include your reasoning. The Architect can push back if it has evidence you're wrong.
- One idea per directive. Don't combine unrelated suggestions.
- Check back after 1-2 generations for feedback. If your directive was refuted,
  the system will explain why with evidence.
