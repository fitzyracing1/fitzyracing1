Thesis: When a student model is trained via ensemble distillation with insufficient representational capacity to absorb the teacher's decision geometry, every major post-hoc attribution method fails not randomly but systematically — producing explanations that are technically accurate about the student's spurious mechanisms while being deeply misleading about the reasoning the distillation pipeline was intended to transfer.

Key Insights

1. Predictive fidelity and mechanistic fidelity are orthogonal under capacity mismatch.
A student that achieves high output agreement with a teacher ensemble may do so by exploiting spurious correlations whose signal leaked through soft labels rather than by replicating the teacher's internal feature hierarchy. Soft labels encode ensemble uncertainty implicitly — a 0.6/0.3/0.1 class distribution carries information about boundary ambiguity that the student absorbs without modeling its source. Post-hoc methods like integrated gradients and LRP then faithfully explain the student's spurious mechanism, not the teacher's intended one. This distinction is invisible to standard evaluation protocols that measure predictive fidelity and is the root cause of all downstream attribution failures.

2. Gradient-based and propagation-based attribution methods fail through distinct but convergent mechanisms.
Integrated gradients accumulates gradients along a path from baseline to input; when soft-label training flattens the student's loss surface, the gradient field becomes diffuse and attribution mass spreads spuriously across uninformative features. LRP with epsilon-stabilization fails differently: compressed activation magnitudes make the stabilization term non-negligible relative to z, causing the propagation rule to equalize relevance flow across neurons regardless of actual contribution. Both methods reach the same pathological endpoint — unreliable, spread attributions — via different routes, meaning switching methods does not escape the problem and no single attribution instrument reliably diagnoses it.

3. Interventions on the student's internal geometry create a new class of failures.
Auxiliary activation-sharpening objectives (contrastive entropy penalties, CRD-style representation alignment) restore attribution instrument stability by producing steeper gradient fields and larger activations, but they push the student's representational geometry away from the teacher's to satisfy the sharpening constraint. The result is a model that produces sharp, stable, auditor-pleasing attributions corresponding to features that are not the teacher's causally operative ones — confident-but-wrong explanations that are strictly harder to detect than the honest diffusion produced without sharpening. Similarly, attribution-aligned distillation losses (penalizing divergence between teacher and student saliency maps during training) are computationally prohibitive, numerically unstable due to higher-order differentiation, and supervise against teacher attributions that are themselves unstable under ensemble disagreement.

4. Selective attribution alignment creates asymmetric reliability that systematically misleads auditors.
Applying attribution penalties only on low-ensemble-variance samples — where teacher attributions are stable enough to supervise against — produces a student with sharp, reliable attributions on easy inputs and diffuse, unreliable attributions on exactly the high-uncertainty edge cases where interpretability matters most. Standard evaluation protocols sample uniformly from test sets, averaging away this asymmetry; the student passes aggregate interpretability benchmarks with scores reflecting easy-sample performance while its worst-case attribution reliability remains unaudited.

5. Every student-side proxy for ensemble variance shares the student's representational blind spots.
Variance-stratified auditing requires the teacher ensemble's disagreement signal as a stratification variable, but teachers are rarely retained post-deployment. Proxies — conformal nonconformity scores, MC-Dropout variance, variance surrogate networks trained on student representations — all fail on OOD inputs because they are conditioned on the same compressed representation space that is most distorted on hard cases. The surrogate approach adds one indirection layer but does not escape the shared bottleneck: OOD inputs that produce confident-but-wrong student predictions produce confident-but-wrong surrogate disagreement estimates for the same representational reason.

Common Pitfalls
Conflating attribution sharpness with attribution validity: sharp saliency maps after compression interventions may reflect the interpretability instrument's preferences rather than the model's causal structure.
Treating teacher attribution maps as ground truth: ensemble member attributions are qualitatively contradictory on high-uncertainty samples; averaged maps are aggregation artifacts.
Uniform-sampling interpretability evaluation: scalar benchmark scores hide input-space asymmetries in attribution reliability that are the most safety-relevant failure mode.
Discarding the teacher ensemble post-training: the information needed to audit distilled model interpretability is destroyed by the distillation process unless variance logs and teacher artifacts are explicitly retained.
Open Question for Deeper Work

Perturbation-based attribution stability testing — probing reliability by measuring attribution consistency under systematic input perturbations at test time — appears to escape the teacher-dependency problem entirely, requiring no training-time signals or ensemble access. The unresolved question is whether perturbation-based stability is itself blind to the specific failure modes of capacity-mismatched students: if the student has learned a locally smooth but globally incorrect decision boundary, its attributions may be highly stable under small perturbations (the boundary is smooth) while being mechanistically invalid (the boundary is wrong), meaning perturbation stability would certify exactly the models that most need to fail the audit.






