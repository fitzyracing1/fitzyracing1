Thesis: Quantization accuracy degradation at reduced bit-widths is not primarily a precision problem but a distribution mismatch problem — the calibration dataset encodes implicit assumptions about activation statistics that break under deployment distribution shift, and the resulting miscalibration interacts catastrophically with the non-linear sensitivity of low-bit quantization grids to outlier channel magnitudes, producing accuracy cliffs that are invisible during development and irreproducible without deployment-matched calibration data.

Key Insights
1. Outlier channels are structural, not stochastic, and their magnitude is partially input-dependent

Transformer models develop a small set of activation channels (0.1–1% of hidden dimensions) that carry anomalously large magnitudes across virtually all token positions. These channels are structurally determined by weight column norms and residual stream accumulation — the same indices are outliers regardless of input — but their peak magnitude is input-dependent, driven by attention sink dynamics and token distribution. Dettmers et al. (2022) showed this phenomenon emerges as a phase transition near 6.7B parameters. Calibration sets that fail to excite these channels to their deployment-maximum magnitude will produce scale factors set 2–5× too low, causing catastrophic clipping on deployment inputs that do.

2. AWQ and GPTQ each leave a distinct residual vulnerability under distribution shift

AWQ's weight-space scaling handles calibration-time outlier magnitudes correctly but cannot adapt when deployment inputs drive outlier channels beyond the calibration-observed maximum, making it brittle on high-kurtosis domains (code, mathematical reasoning) relative to the calibration corpus. GPTQ's Hessian-weighted rounding optimizes for calibration activation directions and actively misdirects rounding effort when deployment changes the correlation structure of activations — making it vulnerable to structural distributional shift rather than magnitude shift. These failure modes are complementary and neither method addresses both simultaneously.

3. The principled calibration criterion is Fisher coverage, not kurtosis matching or sample count

The theoretically correct calibration objective is minimizing the Fisher discrepancy between calibration and deployment activation distributions, which is equivalent to ensuring the empirical Hessian over quantization perturbations approximates the deployment Hessian. Per-channel kurtosis matching is insufficient because it ignores joint activation structure. Activation subspace coverage — verifying that the top-
𝑘
k singular vectors of calibration activations span the same subspace as deployment activations — is a tractable approximation. QuIP# addresses this implicitly through incoherence preprocessing, which reduces Fisher sensitivity to any particular calibration set.

4. QAT's geometric adaptations are distribution-specific and fragile under shift

QAT does not eliminate outlier channels but redistributes their magnitude and learns partial functional rerouting — the same channel indices remain highest-magnitude post-QAT, just reduced in peak value. Critically, these adaptations are optimized for the QAT training distribution: out-of-distribution deployment inputs can reactivate suppressed outlier channels, potentially making QAT worse than PTQ if the QAT training set was narrower than the PTQ calibration set. The PTQ-QAT perplexity gap at INT4 (~0.4 perplexity on LLaMA-2-7B on WikiText-2) widens further under domain shift because QAT's learned suppression mechanisms are distribution-conditional.

5. Runtime-adaptive quantization is theoretically optimal but computationally constrained by causality

Fully dynamic per-token scale computation (as in LLM.int8()) handles input-dependent outliers but introduces a causality-latency tradeoff: scale factors require observing the full activation vector before quantization, inserting a non-parallelizable reduction barrier between layers. Atom's hybrid approach — dynamic activation scales with static weight group scales — achieves most of the robustness at ~20% overhead, but static weight groups create systematic quantization error when outlier channels cluster within group boundaries (scale contamination) and when long-context inputs drive position-dependent activation drift that static group scales cannot track.

Common Pitfalls
Assuming more calibration data is better: Coverage of the outlier activation regime matters more than sample count; 512 domain-matched samples outperform 4096 generic ones.
Trusting training loss as a calibration diagnostic: Smooth QAT loss can mask latent miscalibration that only surfaces as an accuracy cliff when bit-width drops below the probed threshold.
Treating group size as a throughput-only decision: Group size interacts with outlier channel clustering and context length to create structured, position-dependent quantization error — not just a uniform precision tradeoff.
Assuming PTQ and QAT are interchangeable under shift: PTQ's accuracy gap is formally lower-bounded by the H-divergence between calibration and deployment distributions; no algorithmic improvement to PTQ can close this gap when distributions are well-separated.
Open Question for Deeper Work

Can a quantization scheme decouple outlier channel handling from calibration distribution assumptions entirely — for instance, by identifying outlier channels through weight structure alone (without any calibration data) and applying mixed-precision or rotation-based treatment exclusively to those channels, while reserving calibration-dependent optimization for the remaining low-kurtosis channels? This would reduce the calibration sensitivity problem to a subset of parameters and potentially allow one-shot PTQ to match QAT accuracy on outlier channels specifically, where the current gap is largest.






