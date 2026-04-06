# User Interventions

## [2026-03-31] TARGET CHANGED: 477 µs → 24 µs

The old target of 477 µs has been beaten. The new target is **24 µs** (geometric median).
This is ~32x faster than the V14opt baseline (~770 µs). The old target was easy —
this is the real goal now.

Scoring also changed from geometric **mean** to geometric **median** across the 3 benchmark
sizes, for more stable/reproducible measurements.

Solutions in the 100-200 µs range already exist. Incremental improvements to existing
approaches will NOT reach 24 µs. Fundamentally new strategies are needed.

## Generation 2
Files modified since gen 1:
- knowledge/clusters/cluster_001.md
- knowledge/clusters/cluster_002.md
- knowledge/clusters/cluster_003.md
- knowledge/research/gen002/research_1/findings.md
- knowledge/research/gen002/research_1/observations.md
- knowledge/experiments/gen002/experimentator_1/sol01.score
- knowledge/experiments/gen002/experimentator_1/observations.md
- knowledge/experiments/gen002/experimentator_1/sol01.py
- knowledge/experiments/gen002/experimentator_1/__pycache__/sol01.cpython-312.pyc
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp2b_int8_accum.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp2b_int8_accum
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp1b_store_cost.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp3_nc_sweep
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp2c_combined
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp2c_combined.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp2_kernel_only.s
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp2_kernel_only.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp1_timing
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp1_timing_v2
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp1b_store_cost
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp4_bandwidth
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp4_bandwidth.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp3_nc_sweep.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp1_timing_v2.cpp
- knowledge/experiments/gen002/experimentator_1/sandbox/scripts/exp1_timing.cpp
- knowledge/patterns/active/pattern_008.md
- knowledge/patterns/active/pattern_007.md
- knowledge/patterns/active/pattern_005.md
- knowledge/patterns/confirmed/pattern_006.md
- knowledge/ideas/established/idea_004.md
- knowledge/ideas/active/idea_018.md
- knowledge/ideas/active/idea_019.md
- knowledge/ideas/active/fact_007.md
- knowledge/ideas/active/fact_006.md
- knowledge/ideas/active/idea_006.md
- knowledge/ideas/active/idea_012.md
- knowledge/ideas/active/idea_005.md
- knowledge/ideas/active/idea_016.md
- knowledge/ideas/active/idea_017.md
- knowledge/ideas/active/idea_015.md
- knowledge/ideas/active/idea_014.md
- knowledge/ideas/disputed/idea_009.md
- knowledge/ideas/disputed/idea_013.md
- user/interventions.md
- user/initial_facts.md
- user/config.yaml
- user/initial_ideas.md
- agents/full.md
- agents/genetic.md
- agents/system_critic.md
- agents/architect.md
- agents/research.md
- agents/consistency_review.md
- agents/explore.md
- agents/experimentator.md
- agents/evaluator.md
- agents/exploit.md
- agents/briefs/gen003/explore_2.md
- agents/briefs/gen003/prev_gen_reports.md
- agents/briefs/gen003/explore_1.md
- agents/briefs/gen003/research_1.md
- agents/briefs/gen003/manifest.yaml
- agents/briefs/gen003/exploit_1.md
- agents/briefs/gen003/manifest_reasoning.md
- agents/briefs/gen002/explore_2.md
- agents/briefs/gen002/explore_1.md
- agents/briefs/gen002/manifest.yaml
- agents/briefs/gen002/full_1.md
- agents/briefs/gen002/exploit_1.md
- agents/briefs/gen002/manifest_reasoning.md
- agents/briefs/gen002/prev_gen_reports.md

## Generation 3
Files modified since gen 2:
- knowledge/state_of_affairs.md
- knowledge/clusters/cluster_001.md
- knowledge/clusters/cluster_002.md
- knowledge/clusters/cluster_003.md
- knowledge/research/gen003/research_1/findings.md
- knowledge/research/gen003/research_1/observations.md
- knowledge/experiments/gen003/experimentator_1/sol01.score
- knowledge/experiments/gen003/experimentator_1/observations.md
- knowledge/experiments/gen003/experimentator_1/sol02.score
- knowledge/experiments/gen003/experimentator_1/sol01b.py
- knowledge/experiments/gen003/experimentator_1/sol01b.score
- knowledge/experiments/gen003/experimentator_1/sol01.py
- knowledge/experiments/gen003/experimentator_1/sol02.py
- knowledge/experiments/gen003/experimentator_1/__pycache__/sol02.cpython-312.pyc
- knowledge/experiments/gen003/experimentator_1/__pycache__/sol01.cpython-312.pyc
- knowledge/experiments/gen003/experimentator_1/__pycache__/sol01b.cpython-312.pyc
- knowledge/experiments/gen003/experimentator_1/sandbox/scripts/port_bench
- knowledge/experiments/gen003/experimentator_1/sandbox/scripts/port_bench.cpp
- knowledge/patterns/active/pattern_009.md
- knowledge/patterns/active/pattern_010.md
- knowledge/patterns/active/pattern_011.md
- knowledge/ideas/established/idea_014.md
- knowledge/ideas/established/idea_004.md
- knowledge/ideas/active/idea_009.md
- knowledge/ideas/active/fact_008.md
- knowledge/ideas/active/idea_022.md
- knowledge/ideas/active/idea_020.md
- knowledge/ideas/active/idea_021.md
- knowledge/ideas/active/idea_011.md
- knowledge/ideas/active/idea_012.md
- knowledge/ideas/active/idea_005.md
- knowledge/ideas/active/idea_016.md
- knowledge/ideas/active/idea_015.md
- knowledge/ideas/archived/idea_013.md
- knowledge/ideas/debunked/idea_018.md
- knowledge/ideas/disputed/idea_006.md

## Generation 4
Files modified since gen 3:
- knowledge/state_of_affairs.md
- knowledge/clusters/cluster_004.md
- knowledge/clusters/cluster_001.md
- knowledge/clusters/cluster_003.md
- knowledge/clusters/cluster_002.md
- knowledge/experiments/gen004/experimentator_1/experiment_results.md
- knowledge/experiments/gen004/experimentator_1/sandbox/scripts/exp6_multi_singer_hybrid.py
- knowledge/experiments/gen004/experimentator_1/sandbox/scripts/exp4_difference_spectrum.py
- knowledge/experiments/gen004/experimentator_1/sandbox/data/exp4_output.txt
- knowledge/experiments/gen004/experimentator_1/sandbox/data/exp6_output.txt
- knowledge/research/gen004/research_1/sol01.py
- knowledge/research/gen004/research_1/sol01.score
- knowledge/research/gen004/research_1/findings.md
- knowledge/research/gen004/research_1/observations.md
- knowledge/patterns/active/pattern_012.md
- knowledge/patterns/active/pattern_011.md
- knowledge/ideas/active/fact_004.md
- knowledge/ideas/active/idea_005.md
- knowledge/ideas/active/fact_002.md
- knowledge/ideas/active/idea_003.md
- knowledge/ideas/active/idea_016.md
- knowledge/ideas/active/pattern_009.md
- knowledge/ideas/active/idea_020.md
- knowledge/ideas/active/idea_019.md
- knowledge/ideas/debunked/idea_018.md
- knowledge/ideas/debunked/idea_013.md
- knowledge/ideas/debunked/idea_012.md
- knowledge/ideas/debunked/idea_002.md
- knowledge/ideas/debunked/idea_014.md
- knowledge/ideas/debunked/idea_017.md
- knowledge/ideas/established/idea_004.md
- knowledge/ideas/established/idea_006.md
