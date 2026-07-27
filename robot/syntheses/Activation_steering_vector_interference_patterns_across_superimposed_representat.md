Thesis: Activation steering is not a clean intervention on a target concept but a projection onto a shared geometric subspace occupied by multiple superimposed features, making interference with unintended concepts structurally unavoidable with current techniques — and every tool we have for measuring, bounding, or correcting that interference is itself limited by our incomplete decomposition of the superposition basis.

Key Insights
1. Interference is geometric, not incidental

When a steering vector is added to the residual stream, it projects onto every feature whose decoder direction has nonzero component along that vector — regardless of whether those features were targeted. Because polysemantic neurons superimpose many unrelated concepts in the same weight space, a vector extracted for "anger" will partially activate or suppress "authority," "red," or any other concept sharing that representational neighborhood. The interference is not a bug of poor vector extraction; it is a direct consequence of the geometry of superposition and cannot be eliminated without either solving superposition or steering in a strictly orthogonal subspace, which requires knowing the full feature basis.

2. Evaluation on fixed prompt sets is structurally overconfident

The interference pattern of a steering vector depends on which features are already active at the intervention point — a function of hidden activation state, not surface input. Fixed held-out prompt sets implicitly evaluate the vector in one particular distribution of pre-activated features, conflating the vector's intended effect with interference patterns specific to that distribution. A vector that appears clean on ethical-dilemma prompts may catastrophically interfere with safety-relevant features on coding or code-switching prompts where different features dominate the residual stream.

3. SAE-based stratification improves evaluation but introduces its own blind spots

Sparse autoencoders (Bricken et al. 2023, Cunningham et al. 2023) offer a partial decomposition of the superposition basis and can be used to stratify evaluation prompts by activation-space clustering rather than semantic category. However, when two concepts genuinely share a superposition subspace but are erroneously split into separate SAE features, cross-feature interference terms disappear from the estimate entirely — producing a systematic lower bound on interference complexity rather than an unbiased measure. The SAE residual, the reconstruction error the dictionary cannot explain, carries exactly the interference signal most likely to be missed.

4. Adversarial prompt search can map blind spots but doesn't converge cleanly

The pattern of SAE reconstruction errors across prompts is structured, not noise, and can be exploited: optimizing token sequences to maximize steering vector projection onto the residual subspace (using GCG-style methods) finds prompts where the intervention operates outside the characterized feature space. These adversarially found prompts tend to cluster in interpretable semantic neighborhoods — domain boundaries, code-switching contexts, low-frequency concept combinations — revealing the topology of the steering vector's blind spots. However, iterating between adversarial search and SAE dictionary extension displaces rather than eliminates residual, as new features redistribute sparse coding assignments and push previously-characterized activations into adjacent uncharacterized regions.

5. Causal validation is the binding bottleneck

Replacing L1 sparsity with a learned prior trained on adversarially discovered activations can recover low-frequency features that L1 suppresses, but risks overfitting to activation regions where the SAE fails rather than regions where features genuinely occur in deployment. The only reliable way to distinguish recovered genuine features from prior artifacts is causal intervention — activation patching and targeted ablation — which confirms that a feature is causally active in model behavior. This makes the entire pipeline bottlenecked by causal validation cost, which does not scale to large feature dictionaries.

Common Pitfalls
Confusing surface input diversity with activation-space diversity. Semantically varied prompt sets can be geometrically clustered in hidden state space, producing false confidence in evaluation coverage.
Treating SAE feature count as a proxy for decomposition completeness. Larger dictionaries reduce average reconstruction loss without eliminating structured residual; the residual's principal components are where interference estimates fail.
Assuming adversarial prompts found by residual-projection search represent deployment risk. Many will be token-artifact-driven rather than semantically coherent; without fluency constraints, the stress test finds brittleness rather than genuine blind spots.
Open Question for Deeper Work

Is causal validity of recovered SAE features measurable by a proxy cheaper than full activation patching — for instance, predictive consistency of the feature's activation across paraphrastic prompt variants — and would such a proxy be tight enough to make the adversarial-extension-validation pipeline tractable at the scale of frontier models?






