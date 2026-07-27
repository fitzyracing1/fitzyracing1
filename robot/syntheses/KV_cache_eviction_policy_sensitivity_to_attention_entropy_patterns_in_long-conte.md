Thesis: Attention entropy is a necessary but deeply insufficient signal for KV cache eviction in long-context retrieval — naive entropy thresholding systematically evicts the tokens that matter most, and building a robust policy requires treating entropy as a categorical, layer-typed, and head-role-aware signal rather than a scalar importance rank.

Key Insights

1. Entropy polarity is inverted for retrieval-critical tokens.
The intuition that "low entropy = high importance" breaks precisely at the tokens an eviction policy most needs to protect. Retrieval targets in needle-in-a-haystack and multi-hop QA tasks are often syntactically plain, mentioned once, and attended to sharply but briefly — producing low entropy at the moment of relevance but near-zero cumulative attention mass thereafter. Recency-based and cumulative-score policies (H2O, 2023) both fail this case. The fix requires distinguishing transient sharp attention from sustained diffuse attention, which demands temporal tracking across decode steps rather than a single prefill snapshot.

2. Layer heterogeneity makes cross-layer entropy aggregation actively misleading.
Early transformer layers use attention for positional and syntactic bookkeeping; middle layers aggregate semantics and perform entity binding; late layers execute task-specific retrieval. An entropy score in layer 2 and the same score in layer 22 reflect entirely different computational roles. PyramidKV (2024) exploits this by allocating cache budget non-uniformly across layers, achieving near-lossless retrieval at 20% cache size on RULER benchmarks. Any policy that aggregates entropy across layers without weighting by layer function will misallocate budget in predictable, benchmark-measurable ways.

3. Positional encoding poisons ANN-based retrieval of evicted blocks.
When evicted KV blocks are indexed by key vectors for approximate nearest-neighbor retrieval (as in InfLLM), RoPE-encoded keys from the same semantic content at different document positions are rotationally displaced and will not match under cosine similarity. DeepSeek-V2's MLA architecture sidesteps this by decomposing keys into a position-agnostic latent (the retrieval index) and a positional component computed on-the-fly, achieving 93% KV cache reduction — but this requires architectural commitment at training time and cannot be retrofitted to existing models.

4. Head role determines what entropy means: induction heads require special-case protection.
Induction heads — identifiable via a cheap prefix-copying diagnostic (Olsson et al., 2022) in a single forward pass — produce near-zero entropy spikes onto lexically repeated tokens and are the primary circuit for exact in-context retrieval. Because they are sparse (1–2 heads per layer) and their targets look unremarkable in surrounding layers, entropy-based eviction without head-role awareness systematically under-protects induction targets. Weighting retention scores by an induction-head multiplier (λ≈3–5) is a tractable intervention requiring only a one-time per-model head characterization.

5. Fuzzy retrieval produces medium-entropy signatures that current policies treat as noise.
Semantic (non-lexical) retrieval is handled by composed circuits that attend to clusters of 5–20 thematically related positions, producing entropy in the 2.5–4.0 nats range (versus <0.5 for induction heads). This medium-entropy band is the most underprotected regime in all current systems because it is indistinguishable from confused diffuse attention by entropy alone. A principled policy would maintain separate eviction budgets per entropy band rather than treating entropy as an ordinal importance rank.

Common Pitfalls
Treating entropy as ordinal: Lower is not always more important; the relationship is categorical and head-role-dependent.
Ignoring the prefill/decode gap: Importance scores computed at prefill are query-agnostic and systematically wrong for retrieval-heavy decode in streaming or agentic settings where query intent arrives incrementally.
Uniform layer treatment: Applying the same eviction budget and entropy threshold across all layers wastes budget in early layers and starves semantic layers.
Conflating MLA compression with retrieval safety: The shared low-rank latent in MLA is optimized for average head reconstruction loss, suppressing minority heads (including induction heads) that carry disproportionate retrieval weight.
Open Question for Deeper Work

Can entropy consistency across paraphrased queries serve as a runtime discriminator between genuine fuzzy retrieval (stable medium-entropy clusters) and confused diffuse attention (unstable, query-sensitive spread)? If a head's entropy pattern over a given context region is stable across two or three lightweight paraphrase variants of the decode prefix, that stability is a strong signal of structured semantic retrieval rather than noise — but generating paraphrases at inference time and running parallel forward passes multiplies compute cost in a regime where the whole point is to save memory. The question is whether a single-pass approximation (e.g., dropout-based ensemble over attention weights, or consistency across adjacent decode steps) preserves enough of the discriminative signal to be useful, and whether the resulting eviction decisions recover measurable accuracy on HELMET or MDQA benchmarks relative to entropy-only baselines.






