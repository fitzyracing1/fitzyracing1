Thesis: Activation steering informed by sparse autoencoder decompositions rests on a chain of assumptions — linear feature geometry, context-invariant dictionary atoms, and alignment between internal computational primitives and behavioral causal variables — that empirical evidence now suggests are jointly false for non-trivial model scales, meaning that apparent steering successes may be artifacts of basis convenience rather than genuine causal interventions on the model's computational structure.

Key Insights

1. Feature splitting across SAE widths creates uncontrolled causal side-effects.
When two SAEs trained at different widths decompose the same steering vector differently — a coarse feature in the narrow SAE fragmenting into three finer children in the wide SAE — a steering intervention targeting the coarse feature activates all child features with unequal magnitudes. The behaviorally intended effect may land, but the residual causal footprint across unintended child features silently alters downstream circuits. This makes steering claims nearly unfalsifiable without explicit measurement of off-target feature activation, a control virtually absent from published steering evaluations.

2. Causal sufficiency testing via ablation bracketing distinguishes descriptive from causal decompositions.
The correct experimental response to conflicting SAE decompositions is not to prefer the more interpretable one but to test each as a causal hypothesis: reconstruct the steering vector from each basis, zero-ablate the non-target residual features, and measure behavioral preservation. The decomposition that survives residual ablation without behavioral degradation is causally sufficient; if neither exceeds ~85–90% behavioral replication, both SAEs are missing a causally active component — evidence that the true feature manifold has non-negligible curvature that linear dictionary atoms cannot capture at the intervention magnitudes used in practice.

3. Context-rotation of feature directions breaks the fixed-dictionary assumption and induces sparsity pathologies.
When causally relevant feature directions rotate as a function of co-active context features, no fixed SAE dictionary atom can stably capture them. Conditioning the decoder on context appears to resolve this but introduces context-stratified feature death: features causally necessary in minority-context partitions never receive adequate gradient signal during training batches dominated by majority-context activations, dying silently while global activation statistics look healthy. Per-context gradient variance is the earliest detectable proxy for this failure, visible 200–500 steps before activation rate collapse.

4. Context-stratified minibatch construction breaks sparsity penalty exchangeability.
Promoting stratified sampling to a first-class training objective prevents minority-context feature death but destroys the exchangeability assumption underlying the L1 sparsity penalty. A single global L1 coefficient is simultaneously too tight for some context partitions and too loose for others, requiring partition-local sparsity coefficients — which in turn depend on a clustering procedure that risks circular dependency on the SAE features it is meant to calibrate. Bootstrap convergence with Jaccard stability thresholding (~0.85 across rounds) offers a practical resolution, using raw residual stream geometry or behavioral output probes as circularity-free clustering anchors.

5. Mechanistic and behavioral interpretability objectives are not interchangeable.
Behavioral output probing as a clustering anchor quietly privileges features that predict output variation over features that correspond to internal computational primitives — and these two sets diverge substantially above ~1B parameters. Many high-activation SAE features have negligible direct causal effect on output probabilities; many behaviorally potent features are composites that mechanistically-oriented SAEs would correctly split. Using a single SAE to serve both objectives introduces an unmeasured systematic bias whose direction depends on implicit choices in training corpus construction and regularization strength.

Common Pitfalls
Confirming steering by output inspection alone: behavioral shift is necessary but not sufficient evidence of clean causal intervention; off-target feature activation must be independently measured.
Treating SAE width as a hyperparameter rather than an epistemological commitment: different widths recover different granularities of the feature hierarchy, and cross-width comparisons without causal sufficiency testing produce illusory conflicts.
Assuming dead-neuron diagnostics catch all feature failure modes: context-stratified feature death is invisible to global activation rate monitoring and requires stratified evaluation buffers maintained during training.
Conflating the two interpretability objectives: safety-critical applications require behavioral causal variables; mechanistic understanding requires internal primitives; neither SAE design currently serves both without explicit architectural commitment.
Open Question for Deeper Work

If a model's computation is causally non-transparent at the granularity SAEs recover — meaning behavioral causal variables do not align with internal computational primitives — then what would a steering method look like that doesn't presuppose this alignment? Specifically, can distributed alignment search techniques (Geiger et al.'s interchange intervention framework) be scaled to identify the true causal abstraction level at which interventions are clean, and does that level correspond to any representation recoverable by sparse coding, or does it require fundamentally non-linear decomposition methods operating on the activation manifold's intrinsic coordinates?






