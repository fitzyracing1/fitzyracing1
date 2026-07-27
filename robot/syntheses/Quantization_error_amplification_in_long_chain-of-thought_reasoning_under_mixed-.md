Thesis: KV cache compression in mixed-precision decoding systems introduces anisotropic, compounding quantization error that silently degrades long chain-of-thought reasoning fidelity through a cascade of structural failure modes—spectral concentration, head-function plasticity, correction budget exhaustion, and speculative recovery blind spots—none of which are captured by standard next-token loss metrics.

Key Insights
1. Quantization error is anisotropic and targets the wrong heads

KV cache compression (INT4/INT2 via KIVI, FlexGen) does not distribute error uniformly across the representational space. Activation magnitudes follow heavy-tailed distributions, and quantization clipping concentrates error in the high-magnitude subspaces that constraint-tracking and induction heads rely on for sharp, long-range attention. Because these heads are precisely the ones responsible for maintaining logical bindings, negations, and quantifier scopes across CoT steps, anisotropic error produces reasoning drift rather than perplexity collapse—the model's outputs remain fluent and locally coherent while its long-range logical commitments erode silently. This explains the empirical finding that INT4 compression degrades performance on multi-step reasoning (GSM8K, MATH) before degrading factual recall.

2. Per-head mixed-precision caching recovers reasoning fidelity substantially but not completely

Selectively caching constraint-tracking heads at FP16 while compressing others (HeadKV) recovers ~90–95% of full-precision reasoning accuracy at meaningful memory savings. The residual gap is explained not by cross-head residual stream mixing—which is real but asymmetric in favor of high-magnitude retrieval head outputs—but by value-side compression error: systems that protect K tensors but not V tensors preserve attention pattern sharpness while still retrieving degraded content. Robust per-head precision allocation must be per-component (separate K and V precision), and the heads requiring K-side vs. V-side protection are not identical.

3. Static head-importance assignments fail at OOD reasoning phase transitions

Head-function is contextually plastic: a head that behaves as low-importance (high entropy, diffuse attention) on a familiar reasoning prefix can become a critical constraint-tracker mid-CoT when the problem pivots to a novel inference pattern. Static importance assignments from calibration sets show 15–20% head-set overlap variance across task types, and failures cluster at structural novelty points—precisely where precision starvation is most harmful. Standard benchmarks used to validate mixed-precision KV systems are in-distribution relative to their calibration sets, creating an evaluation blind spot that masks this vulnerability.

4. Residual correction vectors solve precision switching but introduce a bounded memory liability

Storing FP16 correction vectors (quantization error deltas) only for dynamically important heads avoids full precision-switching overhead while recovering fidelity. However, correction budget demand spikes at reasoning phase transitions, and when the fraction of heads requiring correction exceeds ~35–40%, the combined memory footprint surpasses uniform INT8 caching cost, eliminating the compression motivation. The optimal eviction policy for correction vectors is structurally distinct from token-level KV eviction (H2O, SnapKV): it must operate over the head × position joint space, weighting both future attention probability and per-entry quantization distortion magnitude.

5. Speculative recovery creates a systematic blind spot at the hardest positions

Batched speculative recovery—using subsampled approximate attention to prefetch correction vectors before full attention computation—achieves ~85–90% fidelity recovery at ~8–12% latency overhead. The critical failure mode is that approximate attention itself runs on uncorrected quantized KV entries, meaning positions most distorted by quantization produce the least reliable query-key similarity scores and are systematically under-predicted as high-attention targets. The recovery mechanism is therefore least reliable precisely where reasoning fidelity is most at risk—a self-defeating correlation that cannot be resolved without either full-precision fallback or architectural separation of the prefetch and precision-correction pathways.

Common Pitfalls
Evaluating on in-distribution benchmarks and concluding that mixed-precision KV systems are robust; OOD reasoning failures are structurally invisible to standard aggregate metrics.
Protecting only K tensors in per-head precision allocation and missing V-side distortion as the dominant fidelity bottleneck.
Treating correction budget as a soft threshold rather than a hard cap; importance fraction can spike unpredictably at phase transitions and silently exhaust memory headroom.
Conflating token eviction and correction vector eviction; the optimal policies differ in dimensionality, reversibility, and cost structure.
Open Question for Deeper Work

Does the self-defeating correlation between quantization distortion magnitude and speculative recovery miss-rate admit a distortion-aware query projection—a lightweight learned transformation applied to the query vector before the prefetch pass that specifically amplifies dimensions most sensitive to INT4 clipping error—and would such a projection generalize across reasoning domains or overfit to the calibration distribution in the same way static head-importance assignments do?






