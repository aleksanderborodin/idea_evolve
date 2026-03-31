# User Interventions

## [2026-03-31] TARGET CHANGED: 477 µs → 24 µs

The old target of 477 µs has been beaten. The new target is **24 µs** (geometric median).
This is ~32x faster than the V14opt baseline (~770 µs). The old target was easy —
this is the real goal now.

Scoring also changed from geometric **mean** to geometric **median** across the 3 benchmark
sizes, for more stable/reproducible measurements.

Solutions in the 100-200 µs range already exist. Incremental improvements to existing
approaches will NOT reach 24 µs. Fundamentally new strategies are needed.
