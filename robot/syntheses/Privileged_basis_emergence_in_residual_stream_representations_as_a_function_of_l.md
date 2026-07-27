Thesis: Whether a transformer's residual stream develops a stable privileged basis — a consistent coordinate frame in which semantically meaningful directions persist across layers — is determined not just by normalization placement but by an interacting system of architectural choices, training dynamics, and scaling pressures that together govern the tradeoff between representational stability and computational flexibility.

Key Insights

1. Pre-norm architecture is a permissive condition, not a sufficient cause.
Placing LayerNorm before each sublayer rather than after removes the continuous rescaling pressure that would otherwise destroy any stable directional structure in the residual stream. But absence of destruction is not emergence: the privileged basis that forms in pre-norm models is a product of gradient flow, weight initialization, and task structure. Post-norm models actively prevent basis formation; pre-norm models merely allow it. The empirical signature of genuine emergence — as opposed to mere non-destruction — is anisotropic residual stream covariance whose principal directions remain aligned across layers in the original parameter coordinate frame, not just in a rotated PCA basis.

2. Gradient asymmetry across depth is an independent driver of basis formation.
In pre-norm transformers, early layers receive larger and more consistent gradient signals than late layers because gradients accumulate across residual additions without intervening normalization. This causes early layers to converge faster and establish representational directions that later layers are implicitly pressured to write into, creating a scaffold-locking effect through training dynamics alone. Crucially, models trained with µP — which equalizes effective learning rates across depth — show weaker privileged basis signatures, confirming that gradient asymmetry is not a nuisance but an active cause of basis formation independent of normalization placement.

3. A privileged basis trades representational capacity for compositional reliability.
By allocating stable directions for inter-layer communication, a privileged basis reduces the effective dimensionality available for task-relevant feature storage. SAE scaling results suggest feature density grows as roughly D^1.6 to D^1.7 with width rather than linearly, and the active features per token scale as D^0.65 — consistent with structural overhead consuming a meaningful and persistent fraction of nominal capacity. This overhead shrinks proportionally as width increases, but does not vanish, and wider models may benefit partly by storing more features below the interference threshold rather than pushing deeper into superposition.

4. Attention heads can function as superposition relievers, extending manipulation capacity.
Because MLP readout fidelity degrades with superposition density, attention heads can partially recover manipulation capacity by copying targeted feature bundles from other token positions into the current token's residual stream before MLP processing. The weight-matrix signatures of this mechanism are low-rank W_OV structure with singular vectors aligned to specific residual stream feature directions. This mechanism is context-dependent: it is unavailable for features superposed within a single token with no distributed counterpart, making single-token-dense computations a fundamental bottleneck.

5. Chain-of-thought prompting partially works by externalizing superposition relief.
When a model writes intermediate results as tokens, it decodes dense superposed representations into low-interference token-stream format that subsequent attention can selectively copy — functioning as an externalized relief depot rather than purely decomposing reasoning steps. This account explains why even semantically empty filler tokens improve performance on computationally deep tasks (Pfau et al. 2024), and predicts that CoT gains should be largest on tasks requiring simultaneous manipulation of many interfering features, which matches the empirical pattern.

Common Pitfalls
Conflating permissive condition with mechanism: Pre-norm does not cause privileged basis formation; it removes one obstacle. Attributing basis structure to norm placement alone misses gradient dynamics, initialization, and task structure.
Confusing storage and manipulation bounds: Superposition capacity governs how many concepts can be stored; it does not determine how many can be cleanly operated on simultaneously. The manipulation bound is tighter and degrades nonlinearly with superposition density.
Treating CoT benefit as purely semantic: The decomposition account of CoT is incomplete. Relief and decomposition interact, and clean separation requires probing intermediate token attention patterns, not just task performance.
Open Question for Deeper Work

The non-local error propagation prediction remains largely untested: if intermediate CoT tokens serve as relief depots attended to by distant later layers, corrupting a single intermediate token should produce cascading failures in computations that depend on it for superposition relief — failures that are spatially distant from the corruption point and invisible to step-by-step reasoning audits. Characterizing this failure mode empirically, and determining whether it is exploitable adversarially, is both a pressing safety question and a direct test of the mechanistic account developed here.






