Thesis: Composing multiple steering vectors in the residual stream is not a linear superposition problem but a geometry problem — interference patterns are structurally inevitable given how transformers compress concepts during pretraining, and managing them requires understanding layer-dependent Jacobian dynamics, corpus co-occurrence geometry, and the fundamental tension between semantic specificity and compositional reliability.

Key Insights

1. Interference is a readout of training geometry, not a steering artifact.
When two concept vectors compose to produce a spurious third concept, the model is faithfully reporting that these concepts formed a relational constellation during pretraining. Because models trained on natural text must represent more concepts than they have dimensions, they pack concepts into near-regular polytopes in activation space (Elhage et al., 2022), and the geometric sums of polytope vertices point toward other vertices. Spurious interference is therefore not noise — it is the algebraic signature of corpus co-occurrence structure, and it persists even when steering vectors are extracted from causally controlled synthetic datasets, because the MLP weights themselves encode the associative geometry no extraction procedure can fully remove.

2. Cosine similarity in mid-layer residual space is the pre-run interference diagnostic.
The most predictive geometric property for interference is the cosine similarity between two concept vectors measured at the intended injection layer in residual stream coordinates. Similarities above roughly 0.3–0.4 at mid-layer depth (consistent with Zou et al., 2023) correlate with unpredictable compound behavior because downstream attention heads cannot disambiguate the composed direction. Sparse autoencoder analyses further reveal that concepts sharing polysemantic neurons or co-activating dictionary features are structurally coupled, making their interference a property of the weight structure rather than the steering procedure.

3. Optimal injection depth minimizes MLP-mediated cross-concept contamination.
Early layers act as nonlinear feature detectors with dense associative responses; middle layers (~30–50% depth) represent the window where concepts are semantically coherent but not yet fully committed by the heaviest associative MLPs. Injecting in this window — approximately layers 12–18 in a 32-layer model like Llama-2-13B — minimizes the MLP Jacobian norm in directions orthogonal to the target concept, reducing lateral activation of correlated features. Depth-staggered injection of two vectors can reduce co-residence in high-interference layers, but only when the two concepts have non-overlapping optimal windows.

4. Injected vectors rotate as they propagate, and corrections must be empirically grounded.
A vector injected at layer L is transformed by the composed Jacobian of all subsequent layers before reaching layer L+k, rotating and stretching in ways that are both prompt-dependent and norm-distorting. Designing a second vector to be orthogonal to the original first vector is therefore wrong; it should be orthogonal to the first vector's empirically pushed-forward representation at the second injection depth. The MEMIT result — that spreading edits across multiple layers outperforms single-layer injection — is implicitly a correction for this distortion.

5. Prompt-invariant subspaces exist but are semantically impoverished.
Directions that rotate predictably across diverse prompts correspond to high-singular-value directions of the mean MLP Jacobian, and universal adversarial perturbations occupy exactly this kind of stable subspace. Steering vectors confined here compose reliably across prompts but tend toward generic or semantically weak concepts, while semantically rich, context-sensitive vectors are inherently prompt-unstable. This creates a structural tradeoff: compositional robustness and semantic precision pull in opposite directions.

Common Pitfalls
Testing vectors in isolation and assuming composability. Single-vector success is necessary but not sufficient; interference only appears under joint activation.
Orthogonalizing in the wrong space. Checking cosine similarity in vocabulary or logit space rather than at the target injection layer gives misleading safety signals.
Ignoring the Jacobian rotation problem. Designing vector B to be orthogonal to vector A's extraction-space representation rather than its layer-propagated representation guarantees residual interference.
Conflating "no spurious output" with "no interference." Interference can be constructive and fluent — the model produces confident, coherent text targeting a concept neither vector intended.
Open Question for Deeper Work

The deepest unresolved tension is whether any architectural modification — sparse attention, privileged bases, or disentangled residual stream designs — could structurally break the tradeoff between semantic specificity and compositional reliability, or whether this tradeoff is a provable consequence of any system that must compress a high-dimensional concept space into a lower-dimensional continuous representation under a next-token prediction objective.






