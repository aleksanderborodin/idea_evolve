---
type: cluster
id: cluster_002
name: "Memory & Tiling Optimization"
member_ideas: [idea_005, idea_006, idea_008, idea_010, idea_012, idea_013, idea_015, idea_017, idea_019]
best_score: 147.26
best_solution: gen002/explore_1/sol01
status: active
last_updated: generation_2
---

This cluster groups ideas about memory access patterns, buffer management, and
tiling strategy: tile size tuning (idea_005), streaming stores (idea_006), KC
elimination (idea_008), memset skip (idea_010), stack allocation (idea_012),
no-packing direct kernel (idea_013), size-adaptive NT stores (idea_015), B
micro-packing (idea_017), and adaptive NC (idea_019).

**Gen002 key findings:**

1. **Streaming stores quantified:** 2.3x on large, 0.9x on medium. Size-adaptive
   approach is critical — idea_015. This is the single highest-leverage optimization.
2. **NC sweep data:** NC=128 best for medium, NC=m best for large. Adaptive NC
   (idea_019) recommended.
3. **C alignment constraint discovered:** Harness uses `std::vector<int>`,
   blocking direct NT stores (fact_006).
4. **Packing is negligible:** Phase timing shows pack_B < 1%, pack_A ~6%.
   Optimization effort should target kernel+store (pattern_006).
5. **idea_013 (no-pack) disputed:** 23% worse than BLIS overall, but competitive
   for small where B fits in L1.
6. **B micro-packing (idea_017):** Helps large (46% improvement) but hurts medium
   due to non-sequential C writes.

**Next frontier for this cluster:**
- Size-adaptive NT stores (idea_015) — #1 priority, potentially 3-5x on geomean
- Aligned-buffer workaround for NT stores when C is unaligned
- Adaptive NC per size (idea_019)
- Hybrid architecture: no-pack for small + BLIS pack for medium/large
