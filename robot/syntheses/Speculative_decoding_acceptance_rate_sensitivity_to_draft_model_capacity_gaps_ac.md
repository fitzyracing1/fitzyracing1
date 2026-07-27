Thesis: Speculative decoding's latency gains are far more fragile than benchmark numbers suggest — acceptance rate degradation under domain shift is nonlinear, architecturally entangled, and systematically invisible to standard evaluation pipelines, making it a latent production risk in any system that combines speculative decoding with quantization, batched serving, or cross-domain prompt distributions.

Key Insights

1. Acceptance rate collapse is driven by distribution divergence, not accuracy degradation.
The acceptance rate equals 1 − TV(p_target, p_draft), so what matters is the overlap between draft and target distributions, not whether the draft's argmax is correct. Under domain shift, low-capacity draft models produce high-entropy, diffuse distributions while capable target models sharpen onto a narrow token set — the worst possible configuration for TV distance. This entropy divergence is catastrophic in narrow-vocabulary domains (LaTeX, SMILES strings, low-resource code) where the target concentrates mass on syntactically constrained tokens the draft has never reliably modeled. The practical implication is that acceptance rate can collapse from ~0.8 to below ~0.5 on shifted prompts while the draft's top-1 accuracy looks reasonable, cutting theoretical speedup from ~5x to ~2x or worse.

2. Tree topology must adapt dynamically to acceptance rate, but widening has hard limits.
When per-token acceptance rate α falls, deep speculative trees compound rejection exponentially (expected yield ~ α^γ), so the optimal response is shallower, wider trees that front-load branching. However, tree widening raises verification cost linearly with node count, and the target model must run structured tree attention over all candidate nodes simultaneously — practical systems like vLLM and SGLang cap effective tree sizes at 40–64 nodes before verification overhead consumes the speedup. This creates a critical acceptance rate floor below which no tree topology recovers positive latency benefit, and that floor is higher than most practitioners assume.

3. Batched serving inverts the speedup calculus and raises the break-even floor.
Speculative decoding's premise — that verification is cheaper than autoregressive generation — holds only when the target model's per-step cost is high relative to verification overhead. Under continuous batching, per-request autoregressive cost falls as ~C_g/B while verification cost stays fixed, linearly raising the required acceptance rate floor with batch size. A configuration that breaks even at α = 0.6 under batch size 1 may require α = 0.85 at batch size 8. Dynamic batch size changes mid-generation further destabilize topology choices made at draft time, and KV cache churn from partial speculative token rejection adds latency under memory pressure.

4. W4A16 quantization introduces silent, asymmetric distribution distortion that degrades acceptance rates without perplexity signals.
When draft and target models are both quantized — potentially with different schemes or bit-widths — the rounding noise introduced by weight quantization distorts their output distributions differently. Outlier channels in the residual stream corrupt logits for rare, domain-specific tokens disproportionately, and because draft and target error structures are uncorrelated, TV distance increases silently. Standard quantization benchmarks (WikiText-2 perplexity, MMLU) are insensitive to this cross-model distributional divergence, meaning a system can pass all offline quality gates while suffering 10–15% acceptance rate degradation in production.

5. Vocabulary-adaptive quantization is the wrong fix; residual stream incoherence is the right target.
The tempting intervention — applying finer quantization granularity to low-frequency token embeddings in the unembedding matrix — misidentifies the causal layer. Outlier channels corrupt hidden states mid-network, and a single channel distorts thousands of vocabulary logits simultaneously through the lm_head projection. Approaches like QuIP# that apply incoherence processing to redistribute outlier energy in the residual stream before quantization attack the root cause more effectively than any vocabulary-level fix.

Common Pitfalls
Evaluating speculative decoding speedup on in-distribution benchmarks only, then deploying on mixed or shifted prompt traffic where acceptance rates collapse.
Treating fallback to autoregressive decoding as a safe default on acceptance rate spikes — transient domain shifts often resolve within 10–20 tokens, making fallback more costly than γ reduction.
Ignoring batch size when setting speculation parameters — γ and tree topology that are optimal at low QPS become net-negative at high QPS.
Assuming quantization errors cancel when both draft and target are quantized — uncorrelated distortion increases TV distance even if individual model perplexity is acceptable.
Open Question for Deeper Work

Does the layer depth distribution of residual stream outliers — which varies systematically across model families (e.g., outliers concentrating in early layers in some architectures, late layers in others) — predict the domain-shift sensitivity profile of speculative decoding acceptance rates under quantization? If outlier depth correlates with the layers most responsible for domain-specific token probability sharpening, then architecture choice may be a first-order determinant of speculative decoding robustness that is currently unmeasured and unreported in any serving system evaluation.






