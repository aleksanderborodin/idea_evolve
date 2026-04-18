---
type: cluster
id: cluster_002
name: Search algorithms
member_ideas: [idea_003, idea_004, idea_007, idea_008]
best_score: 46312
best_solution: gen002_exploit_1_sol02
status: active
last_updated: gen_002
---

# Cluster: Search Algorithms

Search-based approaches explore the Megaminx state space to find shorter paths
than compression. This cluster includes beam search, meet-in-the-middle, and IDA*.

**Member ideas:**
- idea_003: Predictor-guided beam search (ACTIVE — highest priority, ML pipeline confirmed)
- idea_004: Meet-in-the-middle BFS (ACTIVE — limited depth, useful for shallow puzzles)
- idea_007: Corner-only pattern database for IDA* (ACTIVE — INVALID assumptions, needs reformulation)
- idea_008: Trained MLP predictor-guided beam search (ACTIVE — new idea, highest priority)

**Current status:**
- Unguided beam search: confirmed dead (adds nothing over compression)
- Hamming predictor: DEBUNKED — provides zero advantage (research_1 gen002)
- Trained MLP predictor: pipeline confirmed functional, never tested end-to-end
- MITM: irrelevant for medium/hard/very_hard buckets (research_1 gen002)

**Best achieved:** 46312 (same as compression — search hasn't beaten compression yet)

## gen_002 Findings

1. **Hamming predictor is useless** — research_1 definitively proved zero advantage
2. **Beam width must be 4x-32x larger** than gen001 used for depth-10 puzzles
3. **beam_mode='simple' required** — advanced mode has path-return bug
4. **GPU is automatically used** by CayleyGraph (dtype=int8)
5. **All Megaminx generators are 5-cycles** — idea_007's corner PDB assumptions are wrong
