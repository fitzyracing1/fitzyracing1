Thesis: Mixed-precision speculative decoding introduces systematic, directionally biased quantization errors at draft-acceptance boundaries that propagate through attention circuits non-uniformly, accumulate faster than sequence length alone predicts, and resist correction by naive precision allocation strategies that ignore circuit topology.

Key Insights
1. Precision boundary artifacts are deterministic, not stochastic

When a speculative decoding system accepts a draft token and writes its KV projection into the verifier's cache, the dtype cast (e.g., INT8→BF16) introduces a fixed quantization residual Δk at that cache position. Because keys participate in the non-linear softmax scoring step — where small magnitude errors are amplified by query norm and exponentiated — while values enter only as post-softmax weighted sums, key quantization errors cause disproportionate attention distribution shifts. At LLaMA-70B scale, INT8 key quantization residuals produce logit perturbations of 0.1–3.0 before softmax, large enough to materially shift probability mass between competing tokens.

2. Systematic bias versus zero-mean noise is determined by subspace alignment

Whether draft-origin quantization errors cause systematic attention bias or average-out noise depends on the geometric alignment between the draft model's key subspace and the verifier's query subspace. When these subspaces are aligned — as in same-family draft-verifier pairs like LLaMA-7B drafting for LLaMA-70B — quantization error projects coherently onto high-energy query directions, producing a bias term proportional to ||q||·||Δk||·cos(θ) that accumulates additively. Cross-family pairs with near-orthogonal subspaces produce closer to zero-mean error. The Platonic Representation Hypothesis implies that semantically compatible draft-verifier pairs, precisely those most useful in practice, suffer the worst systematic bias.

3. Acceptance rate governs bias injection rate, with phase transitions causing catastrophic retrieval failure

Perplexity drift accumulates proportionally to accepted draft token count rather than sequence length, making acceptance rate a direct multiplier on contamination density. More critically, when acceptance rate drops sharply at distribution shift boundaries — topic transitions, reasoning pivots — the verifier must perform accurate retrieval over a cache already densely populated with biased draft-origin keys. The silent accumulation phase followed by sudden retrieval failure at the hardest sequence positions constitutes a two-stage failure mode invisible to short-horizon evaluations.

4. Head functional typing predicts quantization sensitivity but reveals a propagation paradox

Retrieval heads, which implement induction and content-matching circuits with sharp near-one-hot attention distributions, are maximally sensitive to key quantization errors — small logit shifts flip attended positions entirely. Protecting them at full precision is the correct first-order policy. However, path patching experiments show that these same heads propagate errors from upstream quantized heads forward with only 15–30% attenuation per layer, making full-precision retrieval heads efficient error conduits rather than firewalls. The correct protection target is the heads immediately upstream that write into retrieval heads' input subspaces, not the retrieval heads themselves.

5. Key-tensor pre-correction at write time is numerically feasible but estimation-budget-constrained

Absorbing the expected bias correction into the key tensor at write time preserves flash attention's uniform kernel structure while eliminating the logit-space penalty overhead. Activation-aware correction schemes analogous to AWQ can reduce quantization error by 40–60% in practice. However, the correction introduces an estimation residual that can exceed the original error when estimator calibration error correlates with activation distributions — requiring estimators accurate to within ~20% of bias magnitude to guarantee net improvement, a tight budget that degrades under distribution shift.

Common Pitfalls
Treating quantization error as i.i.d.: The central mistake; errors are directional, correlated with semantic content dimensions, and self-reinforcing through attention feedback.
Optimizing precision per head in isolation: Ignoring circuit topology means protecting retrieval heads while leaving their upstream inputs quantized, amplifying rather than blocking error propagation.
Evaluating perplexity on short horizons: Drift is non-monotonic and may be invisible for hundreds of tokens before catastrophic failure at a phase transition boundary.
Assuming cross-family speculative decoding is safer: While subspace misalignment reduces systematic bias, it also reduces acceptance rates, producing different but comparably damaging failure modes.
Open Question for Deeper Work

Does the superposition of multiple simultaneously active draft-origin error propagation pathways produce interference patterns with predictable constructive and destructive phases? If constructive interference — where multiple biased keys reinforce the same attention score distortion — can be predicted from sequence-level structure (repetition density, topic coherence, syntactic regularity), it may be possible to build an online sequence monitor that triggers cache remediation selectively at high-risk positions, converting an unpredictable catastrophic failure into a manageable, detectable degradation signal.






