Thesis: Routing instability in MoE systems under auxiliary loss annealing is not a transient optimization artifact but a structural consequence of competing loss surfaces, optimizer memory, and representational co-dependence between the gating network and expert parameters — and resolving it requires intervening at each of these levels independently rather than treating the problem as a single hyperparameter tuning challenge.

Key Insights

1. Routing collapse is detectable in the gating distribution before it appears in assignment statistics.
The earliest signals of imminent collapse are entropic and distributional rather than discrete: per-token softmax entropy dropping below ~1.0 nats (from a healthy ~2.3 nats in 8-expert settings), gating logit variance collapsing across token types, router gradient magnitudes falling an order of magnitude below expert gradient magnitudes, and cross-token logit correlation rising above ~0.85. These precursors precede visible expert utilization collapse by hundreds of training steps, as observed in Switch Transformer training dynamics, providing a detection window that discrete assignment monitoring entirely misses.

2. Experts losing traffic suffer passive divergence, not active corruption — and this asymmetry makes recovery structurally harder than collapse.
When routing transitions occur, experts gaining tokens experience noisy but corrective gradient updates, while experts losing tokens suffer a categorically different fate: the surrounding network — layer norms, residual projections, downstream attention weights — continues evolving while the stale expert's parameters freeze, causing the expert's outputs to drift off the activation manifold without any parameter change. This context drift, documented in DeepSpeed-MoE ablations showing degraded perplexity contribution from experts below ~5% token traffic, means the damage is not self-contained and cannot be reversed simply by restoring token flow. The router's subsequent avoidance of the stale expert is then self-reinforcing: forced re-engagement produces high loss, generating negative gradient signal that further suppresses the expert's logit scores.

3. Collapse is fast and coherent; recovery is slow and token-selective — implying fundamentally asymmetric loss surface curvature.
Routing collapse proceeds along a low-curvature descent where gradients from many token types align coherently, enabling rapid, large parameter updates. Recovery requires climbing out of this basin via token-selective gradients that conflict across input subpopulations, producing a rough, high-variance landscape where progress in one context partially undoes progress in another. This asymmetry means collapse can occur in tens of steps while recovery under natural gradients alone may require 3–5× more training steps to restore equivalent utilization — a ratio documented informally in ST-MoE and consistent with the curvature geometry.

4. Adam's second moment accumulator is structurally mismatched to router training dynamics.
Adam normalizes gradient magnitudes via accumulated second moments, which suppresses the effective learning rate precisely when recovery demands exploration. The large second moment built during collapse persists through the β₂ decay constant (typically 0.999), poisoning the recovery phase by treating coherent collapse history as informative prior. Selective second moment resets at detected transition events can restore learning rate sensitivity, but hard resets introduce cold-start oscillation and optimizer-expert asymmetry; soft interpolated resets toward zero, calibrated to the expected recovery timescale, are more robust.

5. Expert rehabilitation and router re-engagement must be decoupled as separate mechanisms.
Freezing stale experts preserves their internal parameters but accelerates manifold divergence by preventing realignment with the evolving network context. The more principled intervention is router logit perturbation with asymmetric gradient blocking — forcing exploratory assignments without penalizing the router for them — combined with expert-local context adaptation via synthetic samples drawn from the current activation distribution. These interventions treat expert competence and router preference as separately maintainable quantities, honoring the original motivation for auxiliary loss annealing (router specialization) without sacrificing expert viability.

Common Pitfalls
Monitoring argmax routing statistics instead of distributional properties, missing collapse precursors by hundreds of steps.
Freezing stale experts to prevent noisy gradient updates, which eliminates active corruption but accelerates the dominant damage mechanism — passive manifold divergence.
Reintroducing auxiliary loss to recover utilization, which conflicts with the specialization the annealing was intended to enable and does not address optimizer state poisoning.
Treating routing recovery as symmetric to collapse, leading to under-resourced recovery interventions that underestimate the required training budget by 3–5×.
Open Question for Deeper Work

What is the minimal sufficient statistic over the real-time gating distribution that enables a computationally cheap online detector to reliably distinguish genuine routing transitions from stochastic routing variance — and how does the answer change structurally between token-drop routing (where capacity constraints create hard assignment floors) and expert-choice routing (where experts select their own tokens, inverting the gradient flow through the gating mechanism)? Answering this question would ground all downstream interventions — optimizer resets, logit perturbation, expert rehabilitation — in a principled trigger condition rather than heuristic thresholds.






