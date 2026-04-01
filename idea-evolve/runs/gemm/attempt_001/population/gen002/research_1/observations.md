# Observations — Research Agent gen002

## Role
This is a Research agent. No solution files were written. Output is findings.md and report.md.

## Work Done
- Read all required context files: description.md, constraints.md, state_of_affairs.md, clusters, facts, coverage_matrix, best.py (sol10)
- Performed theoretical lower-bound analysis for all 3 benchmark sizes
- Analyzed instruction-level bottlenecks in current kernel (best.py / sol10)
- Identified 5 concrete new approaches not yet tried by the system
- Launched background web research agents on Tiger Lake bandwidth, BNN kernels, LUT approaches

## Key Findings Summary
1. Target 24 µs is physically achievable but requires NT stores for large + 8-row int8 kernel + size-adaptive behavior
2. Current large bottleneck: 32 MB C write without NT stores (3176 µs vs ~640 µs theoretical with NT stores)
3. 8-row int8 accumulation reduces register pressure and halves B-loads
4. Size-adaptive NT stores: use only when n*m*4 > 8 MB (L3 size), otherwise regular stores
5. Pack_A is a scalar bottleneck for small benchmark — vectorizable
