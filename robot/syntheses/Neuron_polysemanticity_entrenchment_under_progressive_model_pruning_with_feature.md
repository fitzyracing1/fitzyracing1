Thesis: Progressive model pruning does not merely reduce capacity — it systematically entrenches polysemanticity by forcing surviving neurons to absorb representational load from removed units, corrupting the feature geometry that mechanistic interpretability tools assume, and producing circuit findings that are formally coherent but causally invalid.

Key Insights
1. Pruning Converts Incidental Polysemanticity Into Structural Entrenchment

Polysemanticity exists in dense models as a manageable superposition phenomenon — features occupy near-orthogonal directions recoverable by sparse autoencoders (SAEs). Pruning breaks this recoverability by forcing surviving neurons to absorb removed neurons' representational load, rotating absorbed feature directions into the surviving weight vector. The result is structural entrenchment: fused representations whose semantic clusters are no longer linearly separable in the surviving neuron's activation space, detectable as inter-atom cosine similarities rising from below 0.1 to above 0.3–0.5 in the SAE dictionary, and as spurious coefficient correlations (r > 0.6) between features that should activate independently.

2. The Pruning History Is Forensically Legible in Boundary Geometry

The shape of the decision boundary separating entangled semantic clusters in activation space encodes the pruning method. Gradual magnitude pruning produces curved, low-margin boundaries with wide transition bands (10–20% of the activation range), because incremental weight adjustments smoothly rotate absorbed features into the surviving neuron's direction. Sudden structured pruning of entire heads or MLP blocks produces sharp, approximately linear boundaries with high margin, reflecting abrupt load absorption without blending. Post-pruning fine-tuning erases this forensic signal progressively, acting as a low-pass filter on boundary geometry — making rapid post-compression analysis essential.

3. SAE Dictionary Blind Spots Disable Disentanglement Protection

Designing a pruning-aware fine-tuning regularizer that penalizes off-diagonal SAE coefficient correlations is a principled response to entrenchment, but it is only as complete as the pre-pruning SAE dictionary. SAEs systematically fail to recover low-frequency features (active on fewer than ~0.1% of tokens) due to L1 sparsity penalties shrinking rare coefficients toward zero — and these are precisely the features most vulnerable to pruning absorption. The semantic dissimilarity mask M used by the regularizer has structural blind spots exactly where pruning damage is most severe, producing false assurance that disentanglement is being maintained.

4. Genuine Unrecovered Features Are Detectable in the SAE Residual

Unrecovered low-frequency features leave structured non-stationarity in the SAE reconstruction residual: genuine features produce covariance eigenvalue spikes (>3σ above baseline spectral distribution) at semantically coherent input contexts, and bimodal projection distributions onto the candidate direction, while noise produces flat spectra and unimodal Gaussian projections. Iterative residual pursuit — fitting, extracting, and regressing out candidate directions sequentially — can recover these atoms, with semantic coherence confirmed when top-50 activating tokens show inter-embedding cosine similarity above 0.4. Recovery remains corpus-bound: features active on fewer than 1/N tokens are inaccessible given corpus size N.

5. Circuit-Level Interpretability Findings Are Silently Invalidated

Activation patching spuriously validates entangled circuits because it operates on full residual stream vectors, which remain behaviorally predictive even when the underlying feature decomposition is corrupted. Causal scrubbing fails on entangled post-compression circuits because feature-level substitution produces non-local interference the hypothesis graph doesn't model. This means IOI circuits, induction head attributions, and any SAE-derived mechanistic claim from a compressed model require explicit entrenchment auditing — measuring pre/post-compression dictionary cosine distributions and ablation asymmetry profiles — before being treated as ground truth about computational primitives.

Common Pitfalls
Trusting reconstruction loss as a disentanglement proxy: SAE reconstruction loss remains low even when structural entrenchment is severe, because fused representations still reconstruct activations faithfully. Loss is a fidelity metric, not a geometry metric.
Assuming activation patching validates circuit identity: Behavioral success of patching experiments is consistent with both genuine circuit identification and entangled feature fusion — it cannot distinguish them.
Treating the pre-pruning SAE dictionary as complete: Dictionary incompleteness is not random; blind spots concentrate among low-frequency, high-vulnerability features, creating systematic rather than uniformly distributed protection gaps.
Ignoring fine-tuning as a forensic eraser: Post-pruning fine-tuning smooths boundary geometry and blends entangled features further, making delayed analysis progressively less informative about the true pruning history.
Open Question for Deeper Work

When iterative residual pursuit recovers a candidate feature direction post-pruning, it remains unresolved whether that direction reflects the absorbed feature's original causal geometry or a pruning-distorted projection of it — and no existing method cleanly distinguishes these cases without access to the uncompressed model. Developing a self-contained causal validity test for recovered post-pruning feature directions, one that determines whether steering along the recovered direction produces the same behavioral effect as the pre-pruning feature without requiring a reference model, would close the most critical gap between compression-aware feature recovery and actionable mechanistic interpretability.






