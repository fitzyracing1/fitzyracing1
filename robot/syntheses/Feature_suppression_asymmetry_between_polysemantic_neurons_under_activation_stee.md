Thesis: Two leading mechanistic intervention modalities — activation steering and representation engineering — produce systematically different collateral feature suppression profiles when targeting polysemantic neurons, and behavioral equivalence between them is not mechanistic equivalence, meaning alignment-critical conclusions drawn from one modality may not transfer to the other.

Key Insights

1. Polysemanticity makes collateral suppression geometrically inevitable, but the profile is modality-dependent.
Because transformer neurons encode multiple unrelated concepts superimposed in the same weight space, any intervention vector targeting one concept will project energy onto co-encoded features. Activation steering adds a vector derived from a small paired prompt set that may sit at an angle to the true feature direction, causing broad geometric crosstalk. Representation engineering finds the principal contrast-consistent axis, which tracks the target concept more faithfully but introduces bias from contrast-pair selection. These different optimization pressures produce different intervention vectors and therefore different collateral suppression profiles — even when both successfully suppress the target behavior.

2. Measuring suppression profiles requires triangulated mechanistic instrumentation, not behavioral evaluation.
The suppression profile is only visible by reading out SAE latent activations across both intervention conditions, comparing suppression on target-concept latents versus unrelated co-activated latents. To rule out SAE-as-artifact concerns, results must be triangulated across SAEs trained with different sparsity penalties, widths, and architectures, and cross-validated against linear probing classifiers that bypass learned dictionaries entirely. Behavioral evaluation is structurally blind to this distinction; a model can show identical output distributions under two interventions while one silences three latent features and the other silences one.

3. Predictability of collateral suppression, not its magnitude, is the correct safety criterion.
A blunter intervention suppressing more features is not automatically less safe — collateral suppression of hazardous co-encoded features may be desirable. The alignment-critical criterion is auditability: whether the suppression profile is predictable and inspectable. Designing a confined intervention vector is mathematically possible — project the target feature direction onto the orthogonal complement of the protected feature subspace — but current SAEs at production scale recover only an estimated 20-40% of explainable variance in MLP layers, meaning the protected subspace is incomplete and confinement guarantees are partial.

4. Intervention locus determines causal pathway and failure mode.
Early-layer interventions face correction pressure: MLP associative memory dynamics (Geva et al. 2022) can reinstate suppressed features through subsequent layers, requiring intervention strength sufficient to overcome this, which typically increases collateral damage. Late-layer interventions bypass correction but only block output expression rather than underlying computation, leaving the concept fully processed internally. Middle-to-late layers near the model's semantic commitment point offer the best tradeoff, consistent with Li et al.'s ITI findings locating truth-relevant causal directions at layers 15-20 in 32-layer models.

5. Correction threshold inversion means interventions are weakest precisely when stakes are highest.
MLP reinstatement strength scales with how richly the prompt activates the suppressed feature's semantic neighborhood. This creates a structurally dangerous inversion: on prompts where the target concept is most salient — exactly the high-stakes deployment cases — correction pressure is strongest and intervention effectiveness is lowest. This failure mode is invisible to black-box evaluation and requires internal activation monitoring at layers immediately downstream of the intervention point to detect before deployment.

Common Pitfalls
Treating behavioral equivalence as mechanistic equivalence. Two interventions matching on output token distributions can differ dramatically in which internal features they suppress.
Trusting a single SAE's suppression profile. SAE geometry is artifact-prone; conclusions require triangulation across architectures, sparsity penalties, and probe-based cross-validation.
Ignoring layer-local feature identity. SAE latents at different layers are not in correspondence; a "confined" vector at layer L has no confinement guarantee at layer L+5 without a cross-layer feature trajectory map.
Conflating "less collateral suppression" with "safer." Alignment safety requires predictability and auditability, not minimal footprint.
Open Question for Deeper Work

Can a cross-layer SAE — one trained with shared or aligned dictionary atoms across multiple layers — provide the feature trajectory maps needed to design intervention vectors with provable downstream confinement guarantees, and at what scale does the computational cost of maintaining such alignment become prohibitive relative to the safety benefit?






