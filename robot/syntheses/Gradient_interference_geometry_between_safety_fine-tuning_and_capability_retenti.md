Thesis: Safety fine-tuning in large language models produces weight updates that are geometrically concentrated, architecturally localized, and structurally separable from capability-relevant updates — properties that make safety behavior the predictable loser in low-rank adapter composition conflicts, and that resist straightforward hardening without fundamental redesign of the training objective.

Key Insights

1. Interference is structured, not random, and safety loses by geometry.
When LoRA-style adapters are composed, their weight updates interact through the spectral properties of the matrices they share. Safety fine-tuning concentrates its gradient mass on a small number of high-influence singular directions — primarily in mid-to-late layer MLP down-projection matrices (roughly layers 60-80% through network depth) — while capability adapters using standard rank-8 to rank-16 configurations target the same matrices by default. Because safety updates occupy a lower-rank, more localized subspace than capability updates, even a benign capability adapter has elevated probability of projecting onto safety-critical singular directions, degrading refusal behavior without adversarial intent. The asymmetry is fundamental: safety is a narrow behavioral target (a small cone in activation space) while capability is broad, so safety loses more structure per unit of interference.

2. Spectral detection is possible but not adversarially robust.
The principal subspace overlap between an adapter's ΔW = BA and the safety-critical singular vectors of the base model's W_down matrices provides a concrete, computable interference score. However, any adversary with white-box access to the base model can recover the safety-critical subspace via contrastive gradient decomposition and construct adapters that remain in its orthogonal complement — a constrained but solvable optimization. Detection schemes are useful against naive or automated adapter generation but fail against determined adversaries, and there is a fundamental information-theoretic obstruction: the verification oracle and the attack oracle are the same function evaluated on the same weights.

3. Hardening requires making safety high-rank and distributed, at significant cost.
The only durable defense is engineering inseparability — making safety-relevant weight changes occupy a genuinely high-rank, architecturally distributed structure that low-rank adapters cannot span. Nuclear norm maximization regularizers and multi-path consistency regularization (requiring safety behavior to survive random low-rank erasure of weight subspaces) both point in this direction, but at 70B+ parameter scale the computational cost is prohibitive unless restricted to a small subset of critical layers. That restriction reintroduces localization and creates an adversarial target-shifting problem: attackers route through unhardened layers, exploiting the fact that perturbing early layers shifts residual stream inputs to hardened layers without touching the protected subspace directly.

4. Safety redundancy is shallow; refusal commitment is brittle.
Mechanistic interpretability evidence shows that harmfulness-detection features appear at multiple depths, but the refusal-commitment circuit is narrow and depth-localized, with perturbation costs roughly 3-5x higher at non-critical depths. Redundancy in detection does not translate to redundancy in intervention surface. Proposals to deliberately separate detection (early, distributed) from commitment (late, hardened) increase robustness against unsophisticated attacks but worsen the worst-case: explicit, auxiliary-trained harm-flag subspaces achieve >95% linear probe accuracy, giving adversaries a cleaner geometric target than the diffuse implicit architecture they replace.

5. Interpretability and adversarial fragility are in direct tension.
Across circuit-level interventions in published mechanistic interpretability work, explicit and legible circuits are consistently easier to ablate than distributed implicit ones. The same structural properties that make safety behavior understandable to researchers — localization, linear separability, low intrinsic dimensionality — make it targetable by attackers. Any hardening scheme that operates by obscuring this structure is defeated by white-box access; any scheme that preserves interpretability while improving robustness has not yet been demonstrated.

Common Pitfalls
Assuming interference requires adversarial intent. Standard capability fine-tuning with no malicious goal routinely hits safety-critical subspaces due to shared architectural bottlenecks.
Conflating detection difficulty with robustness. A hard-to-detect adapter is not a hard-to-construct one; the adversary does not need to evade your detector to cause harm.
Treating safety redundancy as a defense. Multi-layer detection does not protect a single-point commitment circuit.
Underestimating the cost of rank-spreading. High-rank safety updates require substantially more data and compute and introduce their own capability interference.
Open Question for Deeper Work

What would it mean, mechanistically, for a safety-relevant computation to be resistant to linear probing while still reliably influencing model behavior? If safety assessment must be nonlinearly encoded to resist white-box recovery, does that require a fundamentally different architectural primitive than the residual stream's additive composition — and is there any existence proof, in current models or in theory, that such a computation is achievable without sacrificing the behavioral reliability that makes safety fine-tuning worth doing at all?






