Thesis: When deep residual networks are fine-tuned on narrow distributions, cross-layer activation correlations progressively build up across skip-distant layer pairs, collapsing effective depth well below nominal depth through a deterministic sequence driven by pretrained CKA geometry — a process invisible to standard loss metrics but predictable, detectable early, and partially preventable through data-side auditing and augmentation-aware checkpoint selection.

Key Insights
1. Effective Depth Collapse Is Structurally Invisible but Measurable

Standard training metrics — loss curves, accuracy, and even per-layer gradient norms — do not reveal effective depth collapse because residual skip connections arithmetically absorb the task signal even as branch contributions decay toward zero. The correct diagnostic is the singular value spectrum of inter-layer representation matrices: genuine collapse produces a dominant singular vector accounting for >90% of variance with no task-aligned structure, distinguishable from benign task-driven convergence (where task-orthogonal singular values drop but task-aligned values hold) using the SVCCA and PWCCA frameworks developed by Raghu et al. (2017) and Morcos et al. (2018). High CKA similarity (>0.85) across skip-distant layer pairs — separations of 8–12 layers in ResNet-50-scale models — is the operational alarm signal.

2. Branch Gradient Collapse Precedes Activation Correlation Buildup

The branch-to-skip gradient norm ratio — defined as the ratio of the backpropagated gradient magnitude through the residual branch versus the skip path — drops below 0.05 and becomes highly variable across batches approximately 500–2000 gradient steps before SVCCA-detectable correlation appears in activations. This early warning exists because gradient collapse reduces the rate of weight change while activation patterns still reflect prior weights through inertia. Monitoring per-layer branch-to-skip ratios with an exponential moving average (α ≈ 0.99) and flagging sustained drops below 0.1 provides a practically zero-cost early detection system implementable as a training callback.

3. Collapse Sequence Is Predetermined by Pretrained CKA Block Structure

The order in which branches collapse during fine-tuning is largely determined before training begins, encoded in the CKA similarity matrix of the pretrained model's activations over the fine-tuning dataset. Redundant clusters — contiguous CKA blocks exceeding 0.80 — collapse boundary-first, with boundary layers receiving conflicting gradients from adjacent non-redundant layers and dropping their gradient norm ratios 300–800 steps before interior layers. Nguyen et al. (2021) demonstrated ~73% accuracy in predicting post-fine-tuning dead layer identity from pre-fine-tuning CKA structure, enabling a ranked freeze schedule derived entirely from a single forward pass over the fine-tuning dataset.

4. Checkpoint CKA Geometry Is Engineered by Pretraining Duration, Data Diversity, and Augmentation Policy

Longer pretraining on diverse data shrinks CKA block size from 8–12 layers to 2–4 layers, creating structurally collapse-resistant checkpoints. SSL augmentation policy is a direct lever: low mutual information augmentation pairs (aggressive asymmetric cropping, scale diversity spanning 4–8x area ratio, modality-asymmetric transforms) force multi-scale invariance specialization across layers, producing fine-grained CKA differentiation. Tian et al. (2020) quantified this as a 2–3 versus 6–8 layer block size difference in ResNet-50 depending on augmentation MI. The practical checkpoint selection heuristic is a mean off-diagonal CKA score below 0.65 in the target fine-tuning layer range, which predicts collapse resistance better than proxy task accuracy.

5. Intervention Efficacy Is Basin-Dependent and Data-Constrained

Targeted interventions at flagged layers — learning rate scaling, gradient amplification, branch re-initialization with optimizer state reset — can rescue effective depth but only within a narrow window and only if the fine-tuning dataset's intrinsic dimensionality can sustain the additional layers. TwoNN ID estimation in pretrained activation space provides a pre-fine-tuning capacity audit: layers where data ID is less than 15–20% of nominal capacity are structurally unsustainable regardless of intervention. Re-attracted collapse reasserts within 1000–3000 steps unless intervention is coupled with task augmentation that broadens the gradient signal and develops landscape curvature in branch-weight directions.

Common Pitfalls
Measuring correlation in adjacent layers: Adjacent layers trivially correlate through residual addition; only skip-distant pairs (≥8 layers) reveal pathological collapse.
Conflating low loss with healthy depth: The skip connection masks branch failure; accuracy metrics are structurally blind to effective depth.
Applying interventions too late: Branch re-initialization after activation correlations are visible is largely futile; the gradient norm ratio is the correct trigger.
Ignoring the augmentation-width interaction: Maximally diverse augmentation exceeding architecture width capacity causes intra-layer uniformity collapse, eliminating the collapse-resistance benefit.
Open Question for Deeper Work

Does augmentation-induced layer specialization during SSL pretraining transfer faithfully into the fine-tuning regime, or does fine-tuning loss rapidly overwrite the differentiated CKA geometry before it provides collapse resistance — and if overwriting occurs, at what gradient step count and loss scale does the pretrained geometric structure become irrelevant to the collapse trajectory?






