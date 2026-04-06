---
type: idea
id: idea_004
name: "Modular Arithmetic Structure"
lifecycle: established
confidence: 0.9
first_seen: generation_0
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen002_exploit_1_sol01, gen002_exploit_1_sol03]
contradicted_by: []
related_ideas: [idea_006, idea_008, idea_009]
cluster: cluster_001
tags: [algebraic, modular, structure]
---

Elements chosen with modular structure (e.g., quadratic residues, powers modulo a prime) tend to have good difference properties. Explore sets of the form {f(k) mod N : k in range} for various functions f. The structure provides a scaffold that can then be improved by local search.

Generation 1 evidence: This idea is strongly confirmed through the Singer difference set (idea_006), which is the specific instantiation of this general principle. Singer uses GF(q³) arithmetic to produce perfect difference sets. The Erdos-Turan construction (idea_009) is another instance, explaining the greedy-66 baseline.

Caution: Not all modular constructions work. The parabola construction {i*p + (i² mod p)} was tried by full_1 and FAILED for large primes (312 violations for p=101). The construction is only valid for small primes. GF(p³) (Singer) is the correct framework, not simple quadratic residues mod p.

Status: Established. This is the foundational principle behind all competitive solutions. Note: the stale copy in ideas/active/ should be deleted — this established/ version is canonical.
