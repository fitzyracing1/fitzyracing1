Thesis: Sparse autoencoders fail to faithfully decompose superimposed neural representations not through smooth degradation but through geometry-dependent, density-triggered phase transitions that cause correlated feature suppression and polysemanticity collapse—failures that are systematically invisible to standard average-case evaluation metrics and cannot be resolved by scaling dictionary size alone.

Key Insights
1. The Collapse-vs-Suppression Boundary Is Geometric

When two genuinely monosemantic features co-activate, whether the SAE merges them into a single bisecting latent (polysemantic collapse) or zeroes one out (asymmetric suppression) is determined primarily by the cosine similarity of their activation vectors. At cosine similarity ≳ 0.7, the encoder cannot assign differential pre-activations sufficient to route them to separate latents under the sparsity budget, and a bisecting polysemantic latent emerges. At lower similarity, the weaker-magnitude feature is suppressed because the marginal L1 cost of recovering it exceeds the marginal L2 reconstruction gain after the stronger feature is already explained. The L1 coefficient λ directly modulates this boundary: higher λ raises the suppression floor and causes collapse or suppression to occur even for moderately dissimilar feature pairs, while lower λ reduces sparsity globally—establishing a non-convex Pareto frontier with no single λ that works across all density regimes.

2. High Activation Density Triggers a Phase Transition, Not Smooth Degradation

Feature recovery does not degrade linearly with co-activation count. When the number of simultaneously active features exceeds approximately 1/5 of the square root of dictionary dimension—a threshold derivable from Johnson-Lindenstrauss geometry—the SAE crosses a phase boundary where the encoder's pre-activation landscape loses well-separated per-feature basins and the L1 penalty dominates all directional gradients simultaneously. Recovery rates can drop discontinuously from ~90% to below 40% as this threshold is crossed. Critically, this threshold shifts with λ: aggressive sparsity regularization lowers it, shrinking the density regime where the SAE behaves faithfully.

3. Collapsed Latents Are Causally Distinguishable But Practically Hard to Identify

A bisecting SAE latent produces a characteristic blended, context-invariant causal intervention signature—perturbing two circuits simultaneously regardless of input context—whereas a genuinely polysemantic base-model neuron switches discretely between causal footprints depending on context. Context-conditioned activation patching can distinguish these cases, but requires knowing which features collapsed in the first place. Unsupervised fingerprinting via GMM bimodality on (latent activation, downstream logit effect) distributions, reconstruction residual isotropy analysis, and silhouette scoring of top-activating input embeddings can identify collapsed latent candidates without prior feature knowledge.

4. SAE Training Is Structurally Biased Toward Common Features

Under uniform training distributions, rare features are packed into near-parallel directions under superposition while common features occupy well-separated directions—and gradient mass during SAE training is proportional to feature frequency, so common features receive disproportionate optimization pressure. Importance-weighted or frequency-stratified sampling can correct this bias, with empirical evidence from analogous imbalanced dictionary learning settings suggesting 3–5× oversampling of rare-feature inputs produces negligible common-feature degradation. However, this risks introducing a validity gap between the SAE's learned geometry and the model's actual computational structure at the original deployment distribution.

5. Surgical Interventions Risk Cascade Entanglement

Splitting a collapsed latent into two atoms initialized at GMM submode directions is the most targeted intervention, but requires temporarily reducing λ locally (otherwise the same suppression dynamic re-collapses the split) and risks propagating entanglement to neighboring latents whose residual absorption patterns are disrupted. Geometry-regularized retraining with atom repulsion penalties avoids cascade but cannot distinguish artifactual atom similarity (collapse) from intrinsic model-side feature similarity (genuine near-duplicates), introducing frequency-correlated distortion bias against rare features.

Common Pitfalls
Averaging fidelity metrics over the training distribution conceals phase-transition failures; high-density inputs are underrepresented in average loss but are exactly where interpretability is most critical.
Conflating dead latents with suppressed latents: correlated dead latents under high density look like clean sparsity but reflect penalty-induced interference, not feature absence.
Assuming dictionary widening resolves suppression: empirical activation density in large models scales with model width, potentially keeping real systems near the critical threshold regardless of dictionary size.
Treating reconstruction loss as a fidelity proxy: an SAE can achieve low L2 reconstruction error while producing causally incoherent latents that do not correspond to stable, interventionable circuits.
Open Question for Deeper Work

Does the phase-transition threshold scale favorably enough with dictionary dimension that sufficiently large SAEs escape the high-density failure regime for realistic LLM activation distributions, or do the co-activation counts in frontier models scale with width in a way that keeps deployed SAEs perpetually near the critical boundary—and if the latter, does this imply that sparse linear decomposition is architecturally insufficient for mechanistic interpretability of large models, necessitating fundamentally non-linear decomposition frameworks?






