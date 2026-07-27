Thesis: When draft and target models diverge in vocabulary distribution due to domain adaptation, speculative decoding's exact output-distribution guarantee degrades in ways that are invisible to standard metrics, compound systematically across sequence positions, and require task-anchored monitoring strategies rather than abstract divergence measures to detect and control.

Key Insights

1. The guarantee breaks silently at the residual distribution, not the acceptance step.The acceptance criterion 
min
⁡
(
1
,
𝑝
target
/
𝑝
draft
)
min(1,p
target
	​

/p
draft
	​

) correctly rejects tokens the target assigns zero probability — that part is fine. The failure occurs when floating-point underflow in float16 silently zeros out small-but-nonzero target probabilities across a slice of the vocabulary, causing the residual distribution to be renormalized over a truncated support. The resampled token is then drawn from the wrong distribution with no exception, no flag, and no perceptible output anomaly. Production systems including vLLM and Hugging Face's assisted_generation perform the residual subtraction in probability space after log-space scoring, placing them squarely in this failure regime for domain-shifted inputs.

2. Miscalibration compounds with systematic directional bias, not noise.
Each resampled token becomes conditioning context for the next draft step, so positional errors do not average out — they steer. Domain-adapted drafts push toward specialized terminology early in a sequence; once a domain-specific token is accepted or incorrectly resampled, the target's own probabilities for related terms increase given that context, partially masking the miscalibration and causing acceptance rates to rise mid-sequence even as the overall distribution drifts. The diagnostic is not mean acceptance rate (the metric reported by SpecInfer, Medusa, and most published ablations) but the positional acceptance rate profile 
𝛼
𝑖
α
i
	​

, whose stationarity is violated under distribution shift in a characteristic and detectable pattern.

3. Active recalibration via temperature or top-p adjustment voids the guarantee.
Using position-0 rejection rate as a control signal to tune draft temperature is intuitive but breaks the theoretical derivation: temperature is a global intervention that degrades well-calibrated regions while fixing miscalibrated ones, and any feedback loop coupling draft proposals to target accept/reject decisions introduces a dependency the original i.i.d. derivation does not permit. The guarantee can be approximately restored by logging per-token proposal probabilities under the policy active at proposal time and recomputing the acceptance criterion accordingly, but this requires storing draft logit snapshots — expensive enough to eliminate most latency benefit. The SpecTr framework offers TV-distance-bounded approximate restoration as a practical middle ground.

4. Task-metric-anchored tolerance intervals are the right engineering interface.
Abstract divergence measures (KL, TV distance) do not translate cleanly into clinical F1 or legal exact-match degradation. The correct approach is to empirically fit a conversion function from divergence estimates to downstream metric gap using a tail-weighted calibration corpus — typical-case corpora underestimate the metric gap on hard cases by 3–5x, based on analogous findings in quantization literature. This function is nonstationary and must be monitored for staleness, which can be done using the rejection system's own outputs.

5. Rejection events are a self-supervised drift detector.
The set of position-0 rejected tokens is drawn from exactly the region of maximum draft-target disagreement, making it a free hard-case detector. A rolling histogram of rejected token IDs, tracked against a reference histogram from the initial calibration period via KS test or MMD, detects shifts in the nature of disagreement before downstream task metrics degrade — providing lead time for targeted active learning queries without requiring new labeled data.

Common Pitfalls
Reporting scalar mean acceptance rate obscures positional correlation structure and masks compounding drift.
Calibrating on typical inputs underestimates tail miscalibration where domain-specific tokens concentrate.
Conflating overconfidence on wrong tokens with overconfidence on right tokens causes temperature-tuning controllers to hunt unstably.
Assuming fluent output implies correct distribution — the target's dominant modes survive miscalibration; rare but high-value domain tokens do not.
Open Question for Deeper Work

Two observationally identical rejected-token histograms can arise from fundamentally different causes: draft overconfidence on domain-specific terms versus target conservatism induced by RLHF fine-tuning on the target side. These failure modes call for opposite corrective actions (adapt the draft versus adjust the acceptance threshold), yet no published method can distinguish them from token-ID rejection logs alone. Whether observable signals — rejection entropy, positional profile shape, or cross-request correlation structure — carry enough information to identify the causal source of distribution shift, and whether that identification actually changes the optimal corrective policy, remains an open and consequential problem for production deployment of domain-adapted speculative decoding systems.






