Thesis: Acceptance rate collapse in speculative decoding is not a monolithic failure but a structured, multi-layered problem whose root causes span distributional divergence geometry, tokenizer incompatibility, position encoding architecture, and embedding capacity — and conflating these distinct mechanisms produces both misdiagnosed failures and misguided remediation attempts.

Key Insights

1. Divergence geometry determines collapse phenotype, not just severity.
Whether α collapse manifests as chronic low-level attrition or rare catastrophic resets depends on where in the token frequency distribution the corpus divergence is concentrated. High-frequency token divergence (function words, common subwords) compounds multiplicatively across the speculation window — a 0.85 per-token acceptance rate at depth 6 yields α ≈ 0.38, well below break-even — producing chronic attrition. Low-frequency divergence in domain-specific terminology produces catastrophic resets: most windows proceed normally until a trigger token forces p_target/p_draft toward zero, wasting the entire window. Aggregate α statistics mask this bimodal structure, and naive corpus audit metrics like vocabulary overlap or perplexity ratios fail to predict which conditional distributions will diverge worst because the problem is about high-order conditional probability mass allocation in long-tail contexts, not marginal token frequency.

2. Tokenizer mismatch is a distinct failure mode that inflates apparent distributional divergence.
When draft and target models use different vocabularies or BPE merge sequences, the standard token-level acceptance criterion becomes formally undefined over incomparable discrete spaces. Fertility ratio divergence — one tokenizer segmenting a span into more tokens than the other — generates spurious rejections that inflate observed α collapse by 20–40% beyond true distributional divergence, as demonstrated in universal speculative decoding work (Sun et al., 2024). Byte-span marginalization corrects for this by comparing probability mass over surface strings rather than token indices, but lattice width grows with vocabulary dissimilarity and can render marginalization computationally intractable for spans beyond 3–4 characters.

3. KV cache invalidity under retokenization is a hard correctness barrier, not a soft efficiency penalty.
RoPE and ALiBi encode position as token index, so any retokenization that shifts token count corrupts all downstream attention scores depending on relative position. Span-anchored position encodings — assigning positions by byte offset rather than token index — restore cache consistency but introduce positional aliasing: attention patterns become invariant to morphologically distinct but byte-length-equivalent sequences, concentrating all disambiguation pressure onto token embeddings. This is not merely a theoretical concern; CANINE evaluations show 2–4% accuracy degradation on morphologically rich languages attributable to this aliasing effect.

4. Positional aliasing implies a provable embedding dimensionality floor.
Removing positional co-signal forces token embeddings to carry additional mutual information that was previously shared with position encodings. An information-theoretic channel capacity argument yields a 15–40% dimensionality inflation as a theoretical lower bound, consistent with empirical results showing CANINE-S underperforming BERT-base by 3–6 GLUE points when embedding dimension is not compensatorily increased. Critically, naive dimensionality inflation is insufficient — the additional capacity must be actively structured toward positional-semantic joint encoding, requiring training incentives that standard pretraining objectives do not automatically provide.

5. Morphological co-signal reconstruction is feasible but architecturally fragile.
A lightweight character- or byte-level encoder can reconstruct lost positional co-signal with as little as 50–100MB of typologically balanced multilingual text, but must remain frozen when inserted into a pretrained base model to prevent co-signal absorption through compensatory weight drift. Typological coverage is the binding constraint: introflective languages (Arabic, Hebrew) require longer receptive fields than agglutinative ones, and encoders trained on typologically imbalanced corpora systematically underperform on underrepresented morphological classes.

Common Pitfalls
Treating aggregate α as a diagnostic. Per-task or per-context α variance can exceed 0.3 absolute, masking localized failure modes that only appear under specific input distributions.
Conflating tokenizer mismatch with true distributional divergence. Up to 40% of observed α collapse in cross-family model pairings may be tokenizer artifact, not semantic mismatch — auditing fertility ratios first is essential.
Assuming byte-span marginalization is always net-positive. When lattice width exceeds 8 and KV cache reuse is disrupted by retokenization, the overhead provably exceeds the speculation gain.
Retrofitting span-anchored encodings onto frozen pretrained weights. Without fine-tuning to recalibrate position-dependent attention heads, the positional aliasing problem is introduced without the training signal needed to compensate for it.
Open Question for Deeper Work

Does the layer-depth at which reconstructed morphological co-signal is injected into a pretrained transformer determine how effectively it propagates through the residual stream — and is there a theoretical basis for predicting the optimal injection depth as a function of the base model's learned positional attention specialization profile? Resolving this would clarify whether morphological encoder insertion is a viable zero-retraining retrofit or whether it requires at minimum a targeted layer-wise fine-tuning pass to achieve meaningful disambiguation recovery.






