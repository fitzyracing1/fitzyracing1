Thesis: When a student network is distilled from a substantially larger teacher, the central failure mode is not output approximation error but geometric misalignment between intermediate representations — a pathology that is invisible to training loss, amplified by alignment objectives themselves, and only revealed under distribution shift or data scarcity.

Key Insights
1. Intermediate representational collapse is causally distinct from output error

A student can match the teacher's training-set output distribution while its intermediate layers occupy a dramatically lower-dimensional manifold. Kornblith et al. (2019) showed that networks with identical ImageNet accuracy can have CKA similarity scores below 0.4 at intermediate layers, and these CKA gaps predict low-shot transfer degradation far better than accuracy does. The effective dimensionality gap — teacher layers spanning rank ~47 versus student layers spanning rank ~12 in ViT distillation variants (Huh et al., 2023) — represents discarded variability that the teacher encoded for generalization but that the student's capacity-limited training never enforced. This collapse is only revealed by few-shot linear probe accuracy on held-out semantic domains, where representational intrinsic dimensionality, not decision boundary quality, determines performance.

2. Alignment objectives can actively cause the collapse they are designed to prevent

Point-wise feature matching losses (FitNets, hint layers) penalize the student for exploring representational directions orthogonal to the teacher's subspace — directions the student may need for its own lower-dimensional solution. This produces layer-selective rank suppression concentrated at hinted layers, diagnosable by monotonic rank decay with increasing alignment loss weight λ at fixed student capacity, and by persistent high-angle gradient conflicts between the distillation and task loss gradients. Relational objectives (RKD, CRD) avoid direct subspace enforcement but introduce their own pathologies: relational overfitting to batch geometry, metric distortion from embedding high-dimensional relational structure into lower-dimensional student space, and false negative contamination in contrastive variants.

3. Relational distillation amplifies teacher spurious structure by default

When the teacher's relational geometry encodes spurious correlations — demographic shortcuts, texture biases — the student's capacity constraint forces it to prioritize high-variance relational dimensions, and spurious correlations that are strongly reinforced across batches systematically win this competition over weaker genuine semantic signals. Attenuation of spurious structure only occurs when the student is so capacity-constrained that it cannot afford to encode spurious dimensions at all, functioning as an accidental information bottleneck. In fairness-sensitive or medical imaging domains, this means relational distillation from an ERM-trained teacher can produce students whose metric spaces are more organized around demographic shortcuts than task loss alone would produce.

4. Spuriousness identification requires head-level decomposition in ViTs

Cross-layer relational consistency — normally a useful signal for identifying non-causally-grounded structure — inverts in ViTs due to residual stream preservation: spurious structure written by early heads persists unchanged through later layers, appearing maximally cross-layer consistent. The correct diagnostic unit is the per-head value-projection contribution to the pairwise Gram matrix, filtered by augmentation fragility score. DeiT's distillation token aggregates across heads indiscriminately, explaining why it inherits teacher texture biases at rates comparable to direct fine-tuning.

5. Filtered distillation targets introduce realizability gaps with their own failure modes

Post-hoc filtered relational targets are not producible by any end-to-end trained network, violating metric consistency properties that emerge from joint optimization. This creates optimization pressure toward unnatural representational configurations, amplifies gradient conflicts, and can produce semantic holes where filtering removed structure that, despite being spurious, happened to correlate with genuine class boundaries. Soft reweighting by augmentation fragility scores with Frobenius norm regularization bounding deviation from the raw target — consistent with ReviewKD's partial matching approach — is preferable to hard suppression.

Common Pitfalls
Equating training accuracy with representational quality: cross-entropy is insensitive to feature matrix rank; a student can achieve teacher-matching training accuracy with a collapsed representation.
Assuming layer-index homology: aligning student layer k to teacher layer k assumes functional equivalence that does not hold under capacity asymmetry; the student may need layer k to encode what the teacher encodes at layer k+3.
Treating relational objectives as safe defaults: RKD and CRD avoid point-wise collapse but introduce batch-geometric overfitting, metric distortion, and spurious structure transfer.
Applying cross-layer consistency diagnostics to ViTs without accounting for residual stream semantics: stable cross-layer presence in a ViT reflects residual stream accessibility, not causal grounding.
Open Question for Deeper Work

Is there a principled, computable bound on how much a distillation target can deviate from any realizable network's geometry — measured in terms of Gram matrix metric violations or singular value distribution divergence — before student optimization becomes systematically worse than training from scratch without distillation? Establishing such a bound would transform filtered and synthetic distillation target design from an empirical art into a constrained optimization problem with failure-mode guarantees.






