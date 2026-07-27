Thesis: Positional encoding schemes trained on fixed context windows produce attention score distortions at out-of-distribution sequence lengths that are mechanistically distinct, evaluation-invisible under standard metrics, and dangerous in retrieval pipelines precisely because they produce confident confabulation rather than detectable failure.

Key Insights
1. RoPE aliasing is frequency-stratified, not uniform

RoPE encodes position via rotation frequencies θ_i = 10000^(-2i/d), and high-frequency components (small i) complete full rotation cycles within short spans, accumulating phase aliasing rapidly at OOD positions. At inference beyond training length L, these components map OOD positions onto in-distribution phase angles belonging to different token pairs, causing the model to attend to semantically incorrect but positionally plausible locations. Low-frequency components extrapolate more gracefully because their wavelengths exceed L and have never aliased during training. This stratification motivates selective interpolation strategies like YaRN, which interpolates only high-frequency components while leaving low-frequency ones intact — but YaRN's boundary between "safe" and "must interpolate" is empirically calibrated rather than theoretically derived, and its transfer across model families and extension ratios remains unvalidated.

2. Perplexity is structurally blind to aliasing failures

Because aliasing affects a sparse subset of positions rather than all tokens uniformly, aggregate perplexity remains low even when retrieval at specific OOD positions collapses. The appropriate diagnostic is position-controlled needle-in-a-haystack evaluation — planting a retrievable fact at a specific absolute position and measuring accuracy as a function of both position and total context length — which produces a 2D heatmap that exposes non-monotonic, periodically-structured failure invisible to perplexity. Current public benchmarks including LongBench and SCROLLS measure aggregate task accuracy rather than position-resolved retrieval, making them inadequate for localizing aliasing artifacts. BABILong shows that most models collapse past 32k despite low perplexity, but cannot isolate aliasing from other failure modes.

3. Aliasing produces confabulation, not omission, when the landing position is semantically coherent

Whether aliasing causes active confabulation or silent omission is determined by the semantic content at the aliased in-distribution position p1: if p1 contains content plausible for the query, the model retrieves and reports it confidently; if p1 is semantically unrelated, attention diffuses and the model simply omits. In RAG pipelines with topically related document chunks, the probability of semantically coherent aliased content is high, making confabulation the dominant failure mode. This is strictly more dangerous than omission because standard faithfulness evaluators (RAGAS, TruLens) verify that outputs are entailed by some retrieved chunk — a confabulated answer grounded in p1 passes faithfulness evaluation even though the correct answer at p2 was never accessed.

4. Ensemble verification requires architectural diversity, not just parametric diversity

Verifiers drawn from the same model family share RoPE frequency configurations and therefore produce correlated aliasing errors, creating systematic blind spots where the verifier endorses exactly the generator's confabulations. Decorrelation requires pairing models with sufficiently different training context lengths (the aliasing period scales with L) or, more robustly, mixing mechanistically distinct encoding schemes — an ALiBi verifier's errors are structurally uncorrelated with RoPE aliasing because its linear penalty mechanism fails differently, providing genuine independence rather than a noisy copy of the generator's blind spots.

Common Pitfalls
Trusting perplexity as a proxy for extrapolation quality. Models can maintain near-nominal perplexity at 4x training length while failing completely on position-specific retrieval tasks.
Treating interpolation as a solved problem. Position Interpolation and YaRN reduce aliasing but introduce resolution compression; the tradeoff is benchmark-specific and does not generalize cleanly across model architectures or extension ratios.
Conflating "lost in the middle" with aliasing. Primacy and recency bias and positional aliasing both produce non-uniform retrieval accuracy, but their spatial signatures and underlying mechanisms are distinct and require different interventions.
Assuming chunk-level citation solves traceability. Systems that attribute outputs to retrieved chunks do not detect within-chunk aliasing, where the attended position is in the correct chunk but the wrong absolute location.
Open Question for Deeper Work

Does the aliasing failure distribution shift systematically with fine-tuning on extended contexts — specifically, does instruction fine-tuning on long documents implicitly teach models to avoid high-frequency attention components at OOD positions, or does it merely teach models to produce fluent outputs that conceal positional failures more effectively? Answering this requires per-position attention analysis before and after fine-tuning on the same base model, comparing aliasing periodicity in attention weights against retrieval accuracy on position-controlled probes — work that to date has not been published in a form that cleanly separates learned positional robustness from learned confabulation fluency.






