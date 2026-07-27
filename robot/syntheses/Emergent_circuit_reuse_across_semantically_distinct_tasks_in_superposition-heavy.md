Thesis: When neural networks encode more features than they have dimensions through superposition, circuits become entangled across semantically unrelated tasks in ways that make standard modular fine-tuning methods geometrically unsafe — and the tools needed to detect, measure, and constrain this entanglement are only now becoming tractable.

Key Insights
1. Circuit sharing has two mechanistically distinct causes that demand different responses

Two tasks can share a circuit either because they genuinely share a sub-computation (semantic sharing) or because superposition forces unrelated features to co-habit the same neuronal directions (geometric collision). The diagnostic distinction is intervention asymmetry: causally ablating a semantically shared circuit degrades both tasks proportionally, while ablating a superposition-induced shared circuit degrades tasks unequally and in ways that depend on the direction of ablation, not just its magnitude. Linear probe geometry provides a second signature — genuinely shared features align in activation space, while superposition-induced co-habitants sit at large angles within the same neurons. This distinction is not academic: semantic sharing is stable across scale and training, while superposition-induced sharing dissolves as models gain capacity, which means the two cases require entirely different mitigation strategies.

2. Entanglement risk is non-monotonic across training time

Superposition-induced circuit entanglement peaks during a mid-training window when the model has saturated its representational capacity but not yet reorganized into a more disentangled regime. This predicts a non-monotonic fine-tuning risk curve: mid-training checkpoints should exhibit more cross-task bleed than either early or fully converged checkpoints. Evidence from grokking dynamics (Nanda et al., 2023) and fine-tuning instability studies is suggestive but confounded, because existing work attributes mid-training volatility to optimization geometry rather than representational entanglement. No published work has tracked circuit identity across training checkpoints using activation patching, leaving the predicted risk curve empirically unconfirmed.

3. LoRA's low-rank constraint does not bound angular reach in activation space

A rank-r LoRA update confines the dimensionality of weight changes but not their angular displacement in the full activation space, meaning a rank-16 update can substantially rotate a 4096-dimensional layer's feature geometry if update directions align with high-variance activation subspaces. A provable safety constraint requires projecting the LoRA B matrix onto the orthogonal complement of the superposition-heavy subspace identified by a sparse autoencoder (SAE), with maximum safe rank bounded by (d − s) where s is the dimension of the protected subspace. This bound is tight at initialization but erodes as fine-tuning drifts the feature geometry the SAE was trained to decompose — the confinement guarantee degrades exactly when it is most needed.

4. SAE-based geometry maps become stale during fine-tuning

Sparse autoencoders are currently the best tool for identifying which directions in activation space carry multiple features simultaneously, but they are trained on base model activations and become misaligned as fine-tuning rotates the feature basis. The failure is more severe than ordinary distribution shift: the SAE's encoder projections measure wrong inner products entirely, feature splitting and merging go undetected, and — critically — SAE reconstruction loss can decrease during fine-tuning even when geometry is being corrupted, because more structured task-specific activations are easier to reconstruct. The correct diagnostic requires held-out probing on features unrelated to the fine-tuning objective, not reconstruction loss on fine-tuning data.

5. Subspace alignment score as a pre-fine-tuning safety diagnostic

The fraction of gradient energy landing inside the protected subspace during unconstrained pilot fine-tuning steps provides a continuous risk score before committing to a full run. Scores below ~0.2 suggest the task can be learned in orthogonal capacity; scores above ~0.6 indicate capacity collision — the base model is superposition-saturated for the target domain and no constraint-based method can make the fine-tune safe without evicting existing features. This connects to task arithmetic interference (Ilharco et al., 2023) but operates in activation space rather than weight space, catching interference that weight-space cosine similarity misses.

Common Pitfalls
Conflating catastrophic forgetting with entanglement-induced corruption. Forgetting is visible in benchmark degradation; geometry corruption can leave benchmarks intact while silently displacing feature directions that matter only under distribution shift or compositional generalization.
Trusting SAE reconstruction loss as a geometry health signal. It is not. Reconstruction loss and feature geometry integrity are dissociable, and the cases where they diverge are precisely the dangerous ones.
Assuming LoRA rank controls the scope of representational change. Rank controls dimensionality of the weight delta, not angular reach in activation space. Low rank is necessary but not sufficient for geometric safety.
Treating Fisher-based regularization (EWC) as equivalent to subspace projection. EWC protects output-sensitive directions; superposition entanglement operates at intermediate representation level, which output sensitivity does not capture.
Open Question for Deeper Work

Does a measurable per-domain superposition pressure exist in the base model — detectable from how the model processes domain-specific inputs before any fine-tuning — that predicts capacity collision risk? If the base model's MLP activations on target-domain inputs already show elevated polysemanticity (multimodal activation distributions, high SAE feature co-activation rates, dense gradient energy in the protected subspace), that would provide a pre-fine-tuning safety screen requiring no pilot gradient steps. Answering this requires systematic comparison of SAE feature activation statistics across domains in large base models, correlated against observed fine-tuning outcomes — work that sits exactly at the intersection of mechanistic interpretability and alignment-relevant model evaluation, and that no current research program has made its primary target.






