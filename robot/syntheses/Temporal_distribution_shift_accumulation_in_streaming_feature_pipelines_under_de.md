Thesis: Maintaining calibrated probability estimates in streaming ML pipelines is not a single drift-correction problem but a compounding control problem across at least five asynchronous feedback loops — feature distribution, label marginal, label-conditional relationship, calibration method hyperparameters, and external anchor reliability — each evolving at different rates and each correction mechanism introducing its own lag, instability, or self-reinforcing failure mode.

Key Insights

1. Delayed labels introduce structural selection bias, not merely noise.
Labels that arrive early are systematically different from labels that arrive late — fraud confirmed within hours differs structurally from fraud uncovered in monthly audits. This means any online retraining or recalibration that consumes labels as they arrive is fitting to a biased slice of the true label distribution. The bias is not reducible by accumulating more samples; it is a property of the arrival mechanism itself, requiring either propensity correction or explicit modeling of the delay process (as in Chapelle's 2014 delayed feedback framework) before any calibration scheme can be theoretically unbiased.

2. Every label weighting scheme produces a distinct, predictable failure mode.
Uniform weighting anchors calibration to a ghost distribution, producing systematic underconfidence in the new regime. Recency weighting amplifies early-arrival selection bias at the decision boundary, producing overconfidence spikes exactly where uncertainty is highest. Inverse-propensity scoring is theoretically unbiased but practically unstable under covariate drift, because stale propensity models assign extreme weights to newly sparse regions, causing variance explosions that require hard truncation. The choice of scheme is therefore not a tuning decision but a failure mode selection.

3. Discrete stratum partitioning and continuous kernel methods fail in complementary ways, and joint optimization of their hyperparameters introduces its own lag.
Static strata become misaligned with drifting mass, causing abrupt per-stratum sample starvation below the ~30-sample stability threshold of isotonic regression. Adaptive strata oscillate under cyclic drift, never converging. Kernel methods avoid discontinuous resets but suffer ghost kernel support from depopulated regions and bandwidth misspecification under anisotropic drift. Joint optimization of bandwidth and projection dimensionality compounds both timescales multiplicatively, and decoupled adaptation introduces projection-bandwidth resonance — calibration error spikes at every projection refresh because the previously tuned bandwidth is immediately wrong for the new geometry.

4. Drift-aware projection refresh converts an estimation problem into a control problem, but is most likely to fail precisely when it is most needed.
Treating projection updates as control decisions — triggered by disruption cost rather than subspace convergence — reduces resonance and allows incremental subspace rotation matched to bandwidth adaptation speed. However, drift direction misidentification is worst when labeled samples are sparse and drift is fast, the exact conditions demanding the most accurate updates. Unlabeled data can stabilize the subspace estimate via online PCA but is blind to concept drift orthogonal to covariate drift, and pseudo-label patches create self-reinforcing miscalibration loops that encode existing errors into the projection.

5. External anchor signals can break the pseudo-label contamination loop but require their own reliability hierarchy.
Outcome-adjacent signals — dispute rates, chargeback timestamps, privileged features — provide calibration-relevance anchors independent of model outputs. Operationalized as secondary covariate shift detectors, they can trigger projection audits before label-confirmed drift is observable. But anchor signals are themselves non-stationary, requiring meta-monitoring that must terminate in a ground-truth primitive — typically human audit samples — whose throughput (tens to hundreds per day) imposes hard limits on detection latency and sample efficiency at the bottom of the reliability hierarchy.

Common Pitfalls
Treating ECE as a global health metric while per-stratum calibration collapses silently in low-traffic subpopulations.
Conflating detection lag with correction lag — drift may be detected promptly while the recalibration budget remains insufficient for reliable fitting.
Assuming IPS is a safe default because it is theoretically unbiased, without accounting for propensity model staleness under the very drift it is meant to correct.
Refreshing projections on fixed schedules rather than disruption-cost triggers, guaranteeing resonance under any non-stationary drift pattern.
Using model predictions as pseudo-labels to supervise subspace tracking, inadvertently encoding current miscalibration into future projections.
Open Question for Deeper Work

Can the five asynchronous feedback loops be unified into a single online control objective — one that jointly minimizes calibration error, adaptation lag, and disruption cost across feature, label, hyperparameter, and anchor layers simultaneously — and if so, what is the minimum oracle information (label throughput, drift velocity estimate, anchor reliability) required for that objective to be tractable in real-time streaming constraints?






