Thesis: When sparse autoencoders are retrained on shifted activation distributions — whether from domain shift, model fine-tuning, or prompt distribution change — the learned feature dictionaries can drift in ways that silently invalidate prior mechanistic circuit explanations, even when geometric similarity metrics suggest stability, because causal role and decoder direction are not the same thing.

Key Insights
1. Geometric stability is not semantic stability

High cosine similarity between pre- and post-shift decoder vectors is necessary but not sufficient for feature identity. The definitive test is activation context auditing: comparing the semantic distribution of top-activating examples across both SAEs, combined with causal intervention tests on a fixed probe dataset. A feature that has geometrically drifted less than 10° can still activate on entirely different input contexts, making prior interpretability labels stale without any obvious reconstruction loss signal.

2. Feature splitting exposes underspecification in original explanations

When a parent feature splits into daughter features after retraining, attribution cannot simply be redistributed by projection coefficients. The orthogonal components of daughter features — directions not inherited from the parent — represent genuinely new variance that the original explanation was silent about. A split is therefore a diagnostic signal: the parent feature was doing multiple causally distinct jobs that the pre-shift distribution never forced the SAE to disentangle, meaning the original circuit explanation was never fully correct to begin with.

3. Model fine-tuning corrupts circuits at the path level before the node level

When model weights are fine-tuned alongside or instead of the SAE, MLP layers write into residual stream directions that can destructively interfere with downstream attention head outputs without changing those heads' individual patching effects. The earliest detectable signature is a drop in principal subspace alignment of the residual stream at intermediate layers, visible via logit lens trajectory analysis or participation ratio of the circuit-relevant covariance subspace — both of which precede any output-level behavioral change.

4. Surgical circuit restoration is possible but creates new interpretability debt

Corrective interventions — low-rank residual stream edits, activation addition, or LayerNorm parameter retraining — can restore circuit function without reverting fine-tuning. However, any gating mechanism used to make corrections input-conditional must itself be treated as a circuit node: expressed as an auditable logical conjunction over named SAE features, ablation-tested for component necessity, and revalidated whenever the SAE or model changes. A gate requiring more than roughly 20 features to achieve precision is evidence that the underlying circuit explanation is causally incomplete.

5. High gate complexity reveals overlapping circuit implementations

When a behavior requires a large feature gate for precise correction, the original explanation likely captured one of several overlapping circuits that jointly implement the behavior. Standard activation patching misattributes causal responsibility in this regime because it measures marginal contribution under single-path interventions, masking redundancy. The correct experimental design involves simultaneous multi-path ablations and checking whether the sum of individual path effects exceeds the total behavioral effect — a superadditivity signature that distinguishes parallel circuits from a single clean mechanism.

Common Pitfalls
Trusting reconstruction loss as a validity proxy: An SAE can maintain low L0/L2 error on shifted activations while its features have drifted substantially in causal role.
Treating circuit explanations as distribution-free: Every circuit explanation is implicitly conditioned on the probe distribution used to validate it; generalization must be tested, not assumed.
Confusing node validity with path validity: Patching effects on individual nodes can be preserved while composed virtual weights across layers have been silently altered by fine-tuning.
Stopping at cosine similarity for feature matching: Cross-run feature matching based on decoder weight similarity will miss context drift, which is the more dangerous failure mode for downstream attribution.
Open Question for Deeper Work

When a behavior is implemented by multiple partially overlapping circuits, no single SAE decomposition may be the right level of analysis — different circuits may be best described by different feature dictionaries trained on different activation subspaces. The open question is whether there exists a principled method for jointly learning a set of SAEs whose union covers the full causal support of a behavior without redundancy, and whether the intersection structure of their feature supports could serve as a formal measure of circuit explanation completeness.






