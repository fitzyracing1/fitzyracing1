Thesis: Standard MoE routing mechanisms — whether token-choice or expert-choice — contain structural failure modes that cause systematic under-representation of rare and combinatorially complex inputs under long-tail training distributions, and these failures are invisible to the monitoring metrics most practitioners actually use, making them among the most dangerous silent degradations in large-scale model training.

Key Insights
1. Capacity overflow creates a gradient void that is self-reinforcing

When tokens are dropped due to expert capacity overflow (as in GShard and Switch Transformer), they pass through a residual bypass that produces zero informative gradient for the router. The load-balancing auxiliary loss then pushes marginal tokens toward the second-most-loaded expert rather than genuinely underutilized ones, because the overload distribution is itself skewed by long-tail inputs. The result is a positive feedback loop: dominant experts attract more tokens, overflow drops the excess without corrective signal, and the router never learns that those tokens needed expert computation — only that the expert was full.

2. Expert Choice eliminates dropping but creates silent selection starvation

By inverting routing so experts select tokens, Expert Choice guarantees no token is dropped. However, expert selection weights are shaped by gradient signal dominated by frequent tokens, causing rare tokens' affinity scores to drift downward over training. They get selected only when frequent tokens are absent — which under long-tail distributions is rarely. This failure is specifically invisible in perplexity metrics because perplexity is frequency-weighted: rare-token degradation contributes almost nothing to aggregate loss, while standard utilization dashboards show balanced load and no overflow.

3. Combinatorial rarity defeats token-level frequency diagnostics entirely

Many real failure cases involve not lexically rare tokens but rare combinations — unusual syntactic frames, low-frequency collocations — where individual tokens are common but their co-occurrence is not. The router assigns these with high confidence (affinity scores are not suppressed) but routes them to the expert handling the nearest high-frequency neighbor in representation space, which may be structurally wrong. No existing frequency-stratified monitoring catches this because the tokens themselves are not rare; the failure is a representation collision that looks, from the outside, like correct behavior.

4. Confidence-adversarial sampling can surface failures but exposes a chicken-and-egg deadlock

Oversampling training examples where the router is highly confident but loss is elevated can force the router into uncertainty on collapsed regions. However, this reveals a deeper problem: router uncertainty distributes newly surfaced rare structures semi-randomly across experts, and with E=64 experts and moderate oversampling, each expert may receive fewer than one example per batch of a given rare structure — far below the signal threshold for meaningful specialization. Router learning and expert specialization are implicitly assumed to be co-paced, but long-tail rarity breaks this assumption, creating a deadlock that end-to-end gradient training cannot resolve without explicit coordination such as temporary expert consolidation or targeted warmup phases.

5. The right diagnostics don't yet exist in standard training infrastructure

Frequency-stratified affinity tracking, per-token-type routing entropy by frequency decile, and gradient norm stratification by input frequency would all reveal these failures during training — but none are shipped as defaults in major MoE frameworks. Standard dashboards report expert-level utilization aggregated over all tokens, auxiliary loss values, and perplexity, all of which remain healthy while silent under-representation compounds over hundreds of thousands of training steps.

Common Pitfalls
Conflating balanced utilization with balanced representation: uniform expert load across a batch does not imply that all input types are receiving proportional expert computation.
Treating auxiliary loss convergence as a health signal: the load-balancing loss can be near its target while rare tokens are systematically excluded from expert computation.
Applying frequency corrections at the wrong granularity: unigram or subword frequency misses combinatorial rarity entirely and can actively mislead reweighting interventions.
Assuming Expert Choice's no-drop guarantee solves the core problem: it eliminates one failure mode while introducing selection starvation, which is harder to detect.
Open Question for Deeper Work

Should MoE routing incorporate an explicit exploration mechanism — analogous to the exploration-exploitation tradeoff in reinforcement learning — where the router is periodically incentivized to route tokens to non-dominant experts regardless of learned affinity, with a reward signal derived from the reduction in per-expert loss on those tokens over subsequent steps? The core challenge is defining a reward that captures genuine specialization improvement rather than short-term loss noise, and doing so without destabilizing the training dynamics that make MoE efficient in the first place. This reframes MoE routing not as a static assignment problem but as an online learning problem with delayed, sparse, and potentially deceptive feedback — which may require fundamentally different algorithmic primitives than current end-to-end gradient training provides.






