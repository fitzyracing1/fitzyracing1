Thesis: Model merging via task-vector arithmetic can preserve behavioral outputs while silently destroying or relocating the causal mechanisms that produce them, and this fidelity loss is structurally amplified in multilingual transformers because their shared language-neutral middle-layer substrate simultaneously serves as the load-bearing zone for both cross-lingual alignment and task-specific computation.

Key Insights

1. Behavioral accuracy is a false proxy for causal fidelity.
Post-merge benchmark performance can remain high while the internal causal pathway responsible for a capability has been disrupted and replaced by a shallower heuristic. Causal tracing — specifically path-patching in the style of Meng et al. (2022) — distinguishes two failure modes: relocation, where the indirect effect peak shifts to a new (layer, position) site while total effect is conserved, and destruction, where the indirect effect profile flattens everywhere and no single site recovers performance when restored. Only by comparing the area-under-curve of the full indirect effect distribution, not just peak height, can these modes be reliably separated.

2. Multilingual middle layers create a structural collision zone.
Multilingual transformers route non-English inputs through a language-neutral substrate concentrated in the middle 40–60% of layers before task computation fires, then decode back to the target language in late layers. When a monolingual task vector is merged into this system, its weight delta lands precisely in this shared substrate. Causal tracing on non-English prompts then reveals an intact semantic hotspot but degraded late-layer output-language heads — the model retrieves the right concept but fails at surface realization — a dissociation invisible to accuracy metrics.

3. Two task vectors occupying the same zone produce causal basis interference, not simple cancellation.
When two task vectors both concentrate weight changes in the middle-layer MLPs, their implicit causal subspaces overlap in activation space, producing cross-task crosstalk: restoring activations for one task's corrupted run partially recovers the other task's output. TIES-merging's sign-conflict resolution addresses destructive weight-space interference but is blind to this subspace overlap problem, which is geometric rather than arithmetic.

4. Weight-space safety metrics are first-order approximations that fail adversarially.
Fisher overlap, singular subspace principal angles, and TIES sign-conflict rates all operate on weights, but causal fidelity depends on activation flow through nonlinear forward passes. Two task vectors can be fully orthogonal in weight space yet maximally dangerous in activation space if one rotates the residual stream such that the other's input-gated computation fires unexpectedly — a failure mode structurally identical to polysemantic feature interference described in Elhage et al. (2022). The multilingual shared manifold maximizes exposure to this failure because it is designed to collapse diverse input distributions onto a common geometry.

5. Manifold-aligned fine-tuning improves merge fidelity but introduces an unlearnability regime.
Constraining task-vector fine-tuning to the manifold's principal directions makes subsequent merging more causally faithful by ensuring task computations write along shared geometric directions rather than across them. However, tasks requiring language-specific computation — morphological agreement, script-level processing, phonological patterns — are precisely what the manifold was trained to suppress, so manifold-constrained fine-tuning hits an irreducible performance ceiling for these tasks. The crossover point is measurable: if projecting an unconstrained task vector onto the manifold basis captures less than roughly 60–70% of its variance, the expressive cost of manifold alignment likely outweighs the merge fidelity gain.

Common Pitfalls
Inspecting only peak indirect effect rather than the full distribution, missing relocation disguised as partial destruction.
Treating TIES or DARE sparsification as sufficient merge safety guarantees — they address weight-space sign conflicts, not activation-space subspace overlap.
Assuming cross-lingual transfer implies cross-lingual causal fidelity — a merged model can perform a task in a new language via a degraded causal pathway that is fragile under distribution shift.
Using a fixed manifold rank across languages without accounting for the higher intrinsic dimensionality required by morphologically complex languages.
Open Question for Deeper Work

Two models fine-tuned on the same task in different languages may produce task vectors that are nearly orthogonal to each other — one forced off the shared manifold by language-specific demands, one aligned with it. Merging them is therefore not a merge of two compatible representations of the same capability but a merge of two differently grounded causal implementations of it. What the resulting model actually computes causally — whether it produces a hybrid circuit, selects one implementation conditionally, or collapses to a third structure resembling neither — is almost entirely uncharacterized empirically, and answering it would require a new experimental paradigm: cross-lingual causal tracing with controlled same-task, different-language fine-tuning pairs, run before and after merge with differential path-patching across both language conditions simultaneously.






