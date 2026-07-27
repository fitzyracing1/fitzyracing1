Thesis: Iterative attention head pruning does not discover and remove redundancy — it actively manufactures the appearance of redundancy through a cascade of coupled importance inflation, absorbed-load weight encoding, subspace estimation drift, and loss landscape corruption that compounds irreversibly across rounds, producing compressed models that benchmark acceptably while having silently lost representational diversity.

Key Insights

1. Importance scores are relational, not intrinsic — and coupling between heads makes iterative scoring systematically unreliable.
A head's importance score is not a fixed property of that head; it is a measurement of its contribution relative to the current surviving population. When two heads attend to overlapping query-key subspaces and one is removed, the survivor must absorb the pruned head's function, causing its activation variance, output norm, and gradient magnitude to spike. This elevates its score in the next round, shielding it from removal even if it carries no unique information relative to remaining heads. The effect compounds geometrically: each removal tightens coupling among survivors, so by round three or four, every importance score reflects accumulated load transfer from prior rounds rather than intrinsic contribution. Michel et al. (2019) demonstrated that BERT heads removable in isolation degrade much faster under sequential removal than independence assumptions predict — the empirical signature of this coupling.

2. Fine-tuning between rounds encodes absorbed-load state into weights and cannot redistribute function without escaping a locked basin.
Short fine-tuning schedules (1–3% of original training compute, the industry norm) are insufficient to escape the local minimum that load-absorbing survivors settle into. Adam's second-moment estimates adapt to the post-absorption gradient landscape, and downstream layers co-adapt to the survivor's expanded role, creating cross-layer dependencies that make unilateral redistribution destabilizing. Even optimizer reinitialization provides only partial relief, since the weight values themselves encode the absorbed state — a fresh optimizer will rediscover approximately the same basin unless learning rates are high enough to escape it, which conflicts with stability requirements of a partially-pruned network.

3. Pruning-aware weight perturbation can target vacated subspaces but introduces calibration-sensitive drift that compounds non-recoverably.
A theoretically sound perturbation scheme — projecting survivors' W_V matrices along the null space of the pruned head's output variance, scaled by Fisher-approximated curvature — can move weights toward covering vacated representational territory without triggering loss spikes. However, the vacated subspace estimate depends on a calibration set, and tail singular vectors (corresponding to rare attention patterns) require far more samples than GPTQ's default 128–256 to stabilize. Distribution mismatch encodes domain-specific blind spots into the weight trajectory as permanent bias. Unlike importance score bias, which merely causes suboptimal selection, subspace perturbation errors physically corrupt the loss landscape model for subsequent rounds — a non-recoverable structural problem.

4. Geometric drift is detectable but no standard pipeline monitors for it.
When accumulated corruption makes further iterative pruning counterproductive, two measurable signals flag the threshold: the inter-round Hessian trace ratio (TrH_k / TrH_{k-1}, approximated via Hutchinson's estimator) exceeding ~1.3–1.5, and the fine-tuning trajectory angle between rounds flipping by more than ~40–60 degrees. At this point the pipeline should switch to one-shot global pruning rather than halt, using the corrupted model as initialization. However, no major pruning library (HuggingFace Optimum, SparseML, MIT HAN Lab tools) currently exposes these signals as monitoring outputs, leaving practitioners without operational visibility into when the iterative regime has become self-defeating.

5. One-shot scoring on a corruption-initialized model inherits the same bias in spatial rather than temporal form.
Global joint scoring does not escape the coupling problem — it merely transforms it. Heads that absorbed load in iterative rounds have elevated output norms and activation variance baked into their weights, so they score highly in any sensitivity-based ranking. The one-shot ranker measures importance within a corrupted functional geometry, systematically over-retaining the same cluster survivors the iterative phase protected. Re-anchoring scores against an early EMA checkpoint can discount load-transfer inflation, but the anchor must predate the first pruning round to provide an uncontaminated reference.

Common Pitfalls
Treating validation loss as a sufficient compression health signal. Loss remains flat while Hessian sharpness rises and representational diversity collapses; distribution-shift or downstream fine-tuning performance reveals the damage too late.
Attributing the pruning cliff to over-pruning. Sharp degradation at 50–60% head removal typically reflects accumulated coupling bias, not an inherent model capacity limit.
Using the same calibration set across all rounds. Fixed calibration data encodes its own distributional blind spots into every subspace estimate, compounding rather than averaging out across rounds.
Conflating one-shot with unbiased. Switching to global scoring mid-pipeline does not neutralize prior corruption; it inherits it in a different form.
Open Question for Deeper Work

At what granularity should the reference anchor for importance score re-anchoring be maintained — per-layer, per-head, or per-singular-direction — and does the optimal granularity depend on the model's depth-to-width ratio or the functional specialization profile of its attention heads? Answering this requires a formal account of how functional load distributes across the residual stream during pruning, which currently lacks both theoretical treatment and empirical benchmark infrastructure.






