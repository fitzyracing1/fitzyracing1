Thesis: Continual fine-tuning under unlabeled, non-stationary streams fails not because replay buffers run out of capacity, but because coverage collapse silently corrupts the gradient geometry and distillation signal in ways that standard loss monitoring cannot detect, and every downstream mitigation — curvature diagnostics, orthogonality-weighted sampling, distillation-based consolidation — inherits and amplifies the corruption unless the buffer's compositional statistics are actively managed as a first-class optimization target.

Key Insights
1. Gradient interference is a curvature-space phenomenon, not a direction-space phenomenon

Cosine similarity between replay and current-task gradients is a misleading proxy for interference. The operative quantity is how much replay gradient energy projects onto the high-curvature eigendirections of the current task's loss surface — measured tractably via diagonal EMA Fisher approximations rather than full Hessian eigendecomposition. Replay gradients that are nearly orthogonal in raw parameter space can still be maximally destructive if they concentrate on the 10-20 parameter dimensions where the current task's loss is steepest. This means interference diagnostics must operate in curvature-weighted parameter space, and the EMA decay rate governing the curvature estimate must be tuned to task timescale rather than optimizer timescale.

2. Task boundary detection resets create a chimera curvature basis

When a boundary is detected and the EMA Fisher is reset, the new curvature estimate is built from the first arriving gradients — which are disproportionately influenced by replay samples still drawn from prior tasks. The resulting chimera basis correctly represents neither the prior task nor the new task, and causes the interference diagnostic to systematically misclassify destructive replay gradients as benign for 500-1000 steps post-reset. The fix — orthogonality-weighted replay sampling at reset — accelerates curvature basis convergence by maximizing the effective rank of the gradient matrix, but transiently increases prior-task replay loss, requiring a secondary diagnostic to distinguish acceptable basin-internal displacement from genuine forgetting.

3. Basin connectivity determines whether parameter-space recovery is even possible

The linear mode connectivity criterion — whether prior and current task parameter solutions are connected by a low-loss interpolation path — is the correct frame for interpreting transient replay loss spikes. When distributions are sufficiently dissimilar, inter-basin barriers of 10-40% loss elevation at the interpolation midpoint make parameter-space recovery impossible regardless of replay schedule. The observable signature of connectivity failure is a plateauing prior-task loss curve under resumed uniform replay, combined with persistently elevated gradient norms on prior-task samples, distinguishing it from slow genuine recovery which produces monotonically decreasing loss.

4. Distillation-based consolidation inherits coverage collapse

When basin connectivity fails and distillation replaces parameter-space replay, the buffer's compositional collapse directly corrupts the distillation signal. Teacher soft labels are only queried on high-density, high-confidence buffer exemplars — precisely the inputs with lowest distillation information content, since off-peak probabilities at decision boundaries carry the discriminative signal. The student learns to match the teacher on covered inputs while developing unconstrained, divergent behavior everywhere else, creating false flat regions in the KL divergence loss surface that generate no corrective gradient. This failure is undetectable on standard replay-loss metrics because monitored inputs are exactly those the distillation succeeded on.

5. Coverage collapse produces selective, invisible forgetting

Unlike uniform parameter degradation, distillation from a collapsed buffer degrades performance selectively on the tail-distribution and boundary-region inputs the buffer missed — producing apparent retention on common inputs and catastrophic failure on rare ones. This forgetting profile evades standard evaluation because held-out test sets mirror the training distribution's density, not its boundary structure.

Common Pitfalls
Monitoring replay loss instead of replay gradient geometry: low replay loss is compatible with maximally destructive gradient interference; only curvature-projected gradient analysis reveals the true interference regime.
Treating boundary detection as binary: intermittent correct detections create a false impression of self-correction while buffer composition continues drifting.
Applying uniform replay immediately post-reset: the chimera curvature basis period requires orthogonality-weighted sampling before uniform replay is informative.
Using distillation as a safe fallback without auditing buffer coverage: distillation from a collapsed buffer produces worse tail-distribution forgetting than no distillation, because it actively suppresses gradient signal in uncovered regions.
Open Question for Deeper Work

Given that every mitigation — curvature diagnostics, orthogonality weighting, distillation — requires the replay buffer to span the input distribution's boundary regions, and given that generative reconstruction of missing coverage requires either the original data or explicit task labels, can a self-supervised diversity signal derived purely from model uncertainty or embedding geometry identify and prioritize boundary-region samples for buffer insertion in a fully unlabeled streaming setting, and does such a signal remain calibrated under the same distribution shifts that cause coverage collapse in the first place?






