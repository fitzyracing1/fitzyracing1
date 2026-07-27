Thesis: When activation patching and causal scrubbing disagree about whether a sparse autoencoder feature is causally relevant, the asymmetry is not noise to be averaged away but diagnostic signal that simultaneously reveals failures in the SAE's learned basis, the causal hypothesis graph, and the training distribution — and resolving it requires a coordinated set of geometric, interventional, and data-curation techniques that each address a different layer of the problem.

Key Insights

1. The two methods answer different causal questions, but their disagreement localizes the failure.
Activation patching operates in the full continuous activation space and implicitly respects superposition, while causal scrubbing reasons over a discretized feature graph with an explicit hypothesis about which paths matter. When they disagree about a specific feature, a path-patching experiment that measures the residual causal effect unexplained by scrubbing-approved features can distinguish "the SAE basis mislabeled a genuine computational unit" from "the scrubbing hypothesis graph was underspecified." A residual effect above the SAE's baseline reconstruction error (~5–15%) implicates the basis; a near-zero residual implicates the hypothesis.

2. Feature splitting and absorption are the two failure modes the basis can exhibit, and they have opposite signatures.
Splitting occurs when a single computational unit is carved across two correlated dictionary elements — detectable when the activation-patching effect vector aligns with a linear combination of nearby features rather than one alone. Absorption occurs when a common feature silently absorbs a rare feature's causal role — detectable when causal scrubbing requires retaining a surprisingly high fraction of features to preserve behavior despite clean geometric metrics. Standard L1 regularization is indifferent to splitting, and a coherence penalty on dictionary columns prevents it; but geometric cleanliness and causal faithfulness can dissociate, so verification must be behavioral, using intervention separability and output KL divergence rather than cosine similarity.

3. The training distribution drives absorption more than the SAE objective does.
Conditional frequency imbalance — when concept A almost always co-occurs with concept B — removes the gradient signal needed to keep their features separate. Rare features are disproportionately vulnerable because they almost exclusively appear near common features, placing their entire learning signal in the ambiguous boundary zone. The critical co-occurrence threshold for reliable absorption in synthetic experiments is approximately p ≈ 0.7–0.8; above this, standard SAEs fail to recover separate features regardless of dictionary size.

4. Importance weighting rescues rare features from absorption but distorts their boundaries.
Reweighting reconstruction loss by inverse marginal feature frequency prevents rare features from being absorbed without changing the training distribution, preserving decoder geometry calibration. However, because the rare feature's gradient signal remains concentrated in near-miss contexts shared with the common feature, its decision boundary gets shaped by ambiguous examples rather than clean exemplars — producing a feature that fires promiscuously on near-misses. Hard negative mining corrects this but requires bootstrapping: iterative self-distillation using the initial SAE's high-confidence rejections to seed a negative set, converging in 3–4 rounds to a mutually consistent boundary.

5. Self-distillation converges to consistency, not ground truth, requiring external validation.
The iterative negative-mining loop cannot detect systematic boundary errors that its own activations cannot see. External signals — behavioral probes on held-out tasks where the rare concept's causal role is independently known, or mechanistic circuit analysis using path patching on synthetic inputs with controlled ground-truth feature presence — are required to catch cases where the converged boundary is biased toward the high-frequency syntactic contexts the rare feature happened to fire on during initialization.

Common Pitfalls
Treating geometric metrics as proxies for causal faithfulness. Low pairwise cosine similarity and high sparsity are necessary but not sufficient; a dictionary can score well on both while exhibiting severe absorption.
Fixing the SAE objective without auditing the training distribution. Coherence penalties and importance weighting only help if the co-occurrence structure is diagnosed first; applied blindly, they shift rather than eliminate failure modes.
Stopping self-distillation at convergence without external validation. Mutual consistency between mined negatives and learned boundaries is not correctness; a biased initialization produces a biased stable point.
Conflating scrubbing hypothesis failure with basis failure. An underspecified hypothesis graph mimics a bad basis in downstream metrics; path patching is the surgical tool to separate them.
Open Question for Deeper Work

The entire framework assumes that features learned by an SAE should correspond to units the model routes computation through — but what if the model's actual computation is irreducibly distributed across directions that no sparse dictionary can isolate without distortion? The open question is whether there exists a formal criterion, grounded in the model's weight structure rather than its activations, that determines a priori which layers and components admit sparse causal decompositions and which do not — and whether that criterion could guide where SAE-based interpretability is trustworthy versus where it will systematically mislead regardless of training procedure.






