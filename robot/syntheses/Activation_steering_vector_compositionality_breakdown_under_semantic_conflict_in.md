Thesis: Activation steering vectors do not compose cleanly under additive superposition because the residual stream is not a neutral summation buffer — semantic conflict, circuit overlap, variance geometry, and fine-tuning-induced suppression all introduce systematic, often silent failures that make multi-concept steering interventions unreliable in ways that neither individual vector's behavior predicts.

Key Insights

1. Circuit overlap, not semantic contradiction, is the primary source of compositional failure.
Two steering vectors can represent concepts that are perfectly compatible in meaning yet interfere catastrophically if they route through the same attention heads. Because attention patterns are determined by a single softmax over a shared set of logits, heads asked to simultaneously implement two distinct transformations will satisfy neither cleanly. The diagnostic is causal mediation analysis — specifically comparing the sum of individual indirect effects to the joint indirect effect under composition, using path patching as formalized in the IOI circuit work (Wang et al., 2022). Crucially, head-level overlap is not sufficient to detect all interference: two vectors can use different heads but write to the same residual stream subspace, producing downstream interference invisible to head-level analysis alone.

2. Variance geometry determines which concept dominates under composition.
When one vector's direction aligns with the high-variance principal components of the residual stream at the intervention layer, downstream nonlinearities amplify it preferentially — not because of norm magnitude, but because the model's weights are calibrated to treat high-variance directions as signal and low-variance directions as noise. This means concepts encoded in low-variance directions (typically rare or suppressed behaviors) are systematically outcompeted in multi-vector interventions regardless of steering magnitude, and norm-equalization alone will not fix the asymmetry. The practical implication is that compositional steerability is geometrically biased toward common, high-frequency behaviors.

3. RLHF suppression compresses rather than erases behavior representations, and the mechanism is primarily gating-level.
Fine-tuning reduces the variance of suppressed-behavior activations by pushing their pre-activation inputs below firing thresholds, rather than rotating or destroying the underlying feature directions. This is evidenced by the persistence of SAE features for suppressed behaviors in fine-tuned models, with reduced activation frequency but intact feature geometry. The critical consequence is that gating-level suppression is calibrated to the RLHF training distribution and fails under distributional shift — explaining multilingual jailbreak vulnerability (Yong et al., 2023) and the effectiveness of structured multi-turn adversarial prompting.

4. Steering resistance functions as an indirect audit of suppression depth, with a compression/erasure distinction.
A behavior's threshold for successful activation steering — how large a multiplier is needed before behavioral change manifests — encodes information about how thoroughly it was suppressed during fine-tuning. The key diagnostic is comparing base model versus fine-tuned model steering resistance for the same behavior: a resistance delta that emerges post-fine-tuning is a suppression signal, while high resistance in both models indicates pretraining rarity. Compression (recoverable via steering or small LoRA fine-tuning) and erasure (irreversible without pretraining rollback) are distinguished by transfer probe accuracy and SAE feature persistence — most current evidence suggests RLHF produces compression, not erasure.

5. Extended RLHF deepens the suppression cascade rather than merely strengthening existing gates.
Additional RLHF training appears to recruit new layers into the suppression circuit rather than simply amplifying existing ones, measurable as a widening of the layer-resolved causal mediation profile across training checkpoints. Deepening increases robustness to single-point interventions but at the cost of colonizing circuit components shared with legitimate behaviors, producing degradation on non-suppressed tasks that scales with suppression depth. The two regimes — deepening versus strengthening — are empirically separable via layer-restricted LoRA recovery experiments and ACDC profiling across fine-tuning checkpoints.

Common Pitfalls
Conflating norm dominance with geometric dominance. Norm-equalizing vectors is necessary but not sufficient; dominance driven by high-variance direction alignment persists after equalization and requires PCA projection analysis to detect.
Treating semantic compatibility as a proxy for compositional safety. Logically consistent concepts can interfere far worse than contradictory ones if their causal circuits overlap; behavioral compatibility is a circuit property, not a semantic one.
Misreading steering resistance as uniform suppression. High resistance could indicate active suppression or pretraining rarity — without a base-model comparison, the distinction is invisible and the interpretive conclusion is wrong.
Assuming compression implies recoverability by steering alone. Compressed behaviors may require fine-tuning for recovery if the suppression cascade is deep and multilayer; activation steering targeting a single layer will fail even when the representation is intact.
Open Question for Deeper Work

If suppression depth — measured as the number of layers with significant causal indirect effect on a suppressed behavior — imposes a measurable performance tax on legitimate tasks sharing those circuit components, then deeper suppression cascades should produce a detectable capability-safety tradeoff curve that varies across model scales and training regimes. Does this curve have a characteristic shape, and is there a suppression depth beyond which the colonization of shared circuits produces non-negligible degradation on general benchmarks? Answering this would clarify whether current RLHF scaling practices are approaching a regime where safety-motivated suppression begins to measurably degrade general model capability — and whether architectural interventions that isolate suppression to dedicated circuits could avoid this tradeoff entirely.






