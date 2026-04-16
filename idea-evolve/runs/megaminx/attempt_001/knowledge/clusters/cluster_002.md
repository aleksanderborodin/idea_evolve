---
type: cluster
id: cluster_002
name: Search algorithms
member_ideas: [idea_003, idea_004, idea_007]
best_score: 46312
best_solution: gen001_full_1_sol01
status: active
last_updated: gen_001
---

# Cluster: Search Algorithms

Search-based approaches explore the Megaminx state space to find shorter paths than compression. This cluster includes beam search, meet-in-the-middle, and IDA*.

**Member ideas:**
- idea_003: Predictor-guided beam search (ACTIVE — highest priority, ML pipeline confirmed working)
- idea_004: Meet-in-the-middle BFS (ACTIVE — limited depth, useful for shallow puzzles)
- idea_007: Corner-only pattern database for IDA* (ACTIVE — not yet attempted)

**Current status:** Unguided beam search is confirmed dead (adds nothing over compression). Predictor-guided beam search is the highest-leverage direction. MITM works for shallow puzzles but is intractable for very_hard bucket without significant extensions.

**Best achieved:** 46312 (same as compression — unguided search hasn't beaten compression yet).