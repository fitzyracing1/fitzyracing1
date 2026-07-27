Thesis: Attention sinks are not noise or training artifacts but structurally necessary solutions to softmax geometry, and their interaction with positional encoding scheme — particularly RoPE's distance-dependent decay — determines whether the emergent memory and entropy-relief functions they provide survive length generalization or silently degrade it.

Key Insights

1. Softmax geometry actively selects for sinks.
The softmax operator must distribute a full probability mass of 1.0 with no abstain option, and in high-dimensional attention heads (dimension 64–128), the effective temperature is low enough that small dot-product advantages produce near-total probability capture. This creates a rich-get-richer dynamic during training: any token whose key vector drifts slightly higher captures disproportionate mass and receives gradient signal reinforcing that drift. Position 0 wins reliably because every query attends to it, making it the lowest-variance candidate. The result, quantified in Xiao et al. (2023), is that sink tokens accumulate 50–80% of attention mass across many heads in models like LLaMA and Pythia despite carrying negligible semantic content.

2. Sinks serve two distinct functions that are easy to conflate.
The attention pattern (routing probability mass to position 0) provides entropy relief — a learned escape valve for heads with nothing useful to attend to. But the value vector retrieved from position 0 carries a second, independent function: because other heads write into the sink token's residual stream throughout the forward pass, it accumulates a compressed global summary of the sequence. Ablation experiments show that zeroing value contributions from sink heads causes larger perplexity degradation than zeroing their attention weights alone, confirming the memory-retrieval pathway is load-bearing. These two functions can in principle be decoupled — as Darcet et al. (2023) demonstrated with register tokens in vision transformers — with spatially precise tasks benefiting from the separation.

3. RoPE's distance-dependent decay creates an asymmetric failure mode.
RoPE modulates the query-key dot product via rotation matrices that decay with relative distance, but does not modulate value retrieval. This asymmetry means that at long contexts, a query far from position 0 loses the routing signal to the global sink (attention weight drops ~40–60% beyond 8K tokens in standard RoPE models) while the value content stored there remains perfectly intact. The entropy-relief and memory functions therefore fail at different rates and for different reasons as context length grows — a failure mode with no direct analog in APE models, which lose both functions simultaneously at out-of-distribution positions.

4. Models develop heterogeneous sink ecologies under length pressure.
When RoPE routing attenuation severs access to global sinks, models can develop compensatory near-sinks — local entropy drains anchored near each query position rather than at position 0, visible as diagonal bands in attention matrices rather than single high-mass columns. These near-sinks restore entropy relief but cannot replicate the global memory function, producing a windowed rather than sequence-wide information channel. Empirical layer distributions in Llama-2 and Mistral show a bimodal pattern — sinks concentrated in early and late layers with diffuse middle layers — suggesting different functional roles at different depths rather than a uniform mechanism throughout.

5. Sink head identity is seed-dependent; sink position is not.
Drawing on the parallel with induction head formation (Olsson et al., 2022), the structural position that hosts the sink (position 0) should replicate across random seeds due to its universal-access property, while the specific heads and layers that develop sink behavior should shuffle. This predicts high cross-seed correlation for sink position but low rank-correlation (~0.3–0.5) for head-level sink ratios — with implications for any intervention that ablates specific heads, since such interventions must be re-identified per model instance.

Common Pitfalls
Treating sink weight as pure noise. High attention mass at position 0 is often filtered out in visualizations or dismissed as an artifact; this misses the load-bearing value-retrieval channel.
Conflating attention entropy with model uncertainty. Low entropy in sink heads reflects softmax geometry, not confident semantic processing.
Assuming RoPE and APE fail symmetrically at long context. RoPE's routing/retrieval asymmetry produces qualitatively different failure modes than APE's hard out-of-distribution cliff.
Measuring only perplexity across length. Sink degradation under RoPE harms precise relative-position-sensitive tasks far more than aggregate perplexity indicates.
Open Question for Deeper Work

If register tokens trained from scratch eliminate the emergent global memory at position 0, what routing mechanism replaces it for propagating early-sequence information to late-layer computations — and do models without strong sinks develop qualitatively different, potentially more robust long-range information pathways, or do they simply lose the capability and compensate with shorter effective context windows?






