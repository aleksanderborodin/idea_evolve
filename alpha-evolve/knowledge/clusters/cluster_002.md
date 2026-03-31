---
type: cluster
id: cluster_002
name: "Memory & Tiling Optimization"
member_ideas: [idea_005, idea_006, idea_008, idea_010, idea_012, idea_013]
best_score: 148.18
best_solution: explore_1/sol10
status: active
last_updated: generation_1
---

This cluster groups ideas about memory access patterns, buffer management, and
tiling strategy: tile size tuning (idea_005), streaming stores (idea_006), KC
elimination (idea_008), memset skip (idea_010), stack allocation (idea_012),
and no-packing direct kernel (idea_013).

The memset-skip optimization (idea_010) was the single highest-impact discovery
in gen001, providing up to 2x speedup alone. KC elimination (idea_008) is
universally adopted. NC=256 appears optimal (pattern_002).

**Next frontier for this cluster:**
- No-packing direct kernel (idea_013) — untested, potentially large win
- Systematic NC tuning (128, 192, 256, 384) across all benchmark sizes
- Software prefetching for next B panel
- Investigate why NC=512 regresses (pattern_002)
