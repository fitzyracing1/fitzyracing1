Thesis: Prefill latency in production LLM pipelines does not merely scale with prompt length — it explodes quadratically due to full self-attention over increasingly bloated templates, and the interventions required to contain this explosion (prefix caching, KV reuse, position remapping) interact with positional encoding schemes, attention head heterogeneity, and GQA grouping in ways that create silent correctness failures invisible to standard quality metrics.

Key Insights

1. Quadratic attention complexity makes prompt bloat a nonlinear operational hazard.
Doubling a prompt more than doubles prefill time, and in continuous batching systems, long prefill phases create head-of-line blocking that inflates P99 tail latency across unrelated requests. The true bottleneck is frequently memory bandwidth saturation rather than compute, meaning GPU upgrades fail to help. System prompts, tool schemas, safety preambles, and RAG context each individually appear manageable but compound into explosive sequence lengths that destabilize throughput SLAs at production scale.

2. Prefix caching hit rates are fragile and require active engineering to maintain.
Prefix caching (as implemented in vLLM and extended by SGLang's RadixAttention) requires exact token-level prefix matches, meaning minor prompt variations — a shuffled tool list, an interpolated timestamp, a user ID mid-template — collapse cache hit rates to near zero. The correct interventions are strict slot discipline (dynamic content appended only at the suffix), canonical tool ordering (recovering 30–60% hit rates in agentic workloads per Vertex AI findings), and prefix canonicalization enforced at the application layer, not the serving layer.

3. RoPE's rotation structure makes mid-sequence KV reuse mathematically non-trivial, but frequency stratification enables surgical correction.
RoPE invalidates cached keys after any insertion point because downstream position indices shift, corrupting relative offset computations. However, this corruption is unevenly distributed across embedding dimensions: high-frequency bands (which cycle every ~6 tokens) are the primary corruption source for small position shifts, while low-frequency bands remain approximately valid. YaRN's selective frequency interpolation and CacheBlend's partial KV recomputation both exploit this structure, with CacheBlend achieving up to 4× prefill speedup by recomputing only the KV neighborhood most affected by injection. ALiBi avoids this problem entirely by keeping KV tensors position-agnostic, at the cost of weaker long-context extrapolation.

4. Attention head heterogeneity creates a principled but operationally complex partition between reuse-safe and recompute-required heads.
Induction and syntactic heads concentrate in early-to-middle layers and rely on high-frequency RoPE bands for precise relative position signals, making them highly sensitive to remapping. Semantic retrieval heads in later layers use low-frequency bands and tolerate position shifts gracefully. Head-level profiling (measuring per-head KV cosine similarity under controlled position shifts, with a ~0.97 reuse threshold) can generate a static reuse mask, but GQA architectures complicate this because shared KV heads force group-level recompute decisions — any position-sensitive query head in a group contaminates the entire group's KV entry.

5. Reuse masks derived from calibration data degrade silently under distribution shift.
Induction head sensitivity profiles are 30–50% less stable across domains (e.g., prose versus code) than semantic head profiles, and the failure modes of mask misclassification — degraded coreference resolution, in-context copying errors, structured format failures — are invisible to perplexity, ROUGE, and aggregate LLM-judge scores. The correct monitoring strategy tracks proxy signals (attention entropy variance, near-diagonal attention frequency, attention sink distribution) rather than output quality, with recalibration cadence tied to measured domain drift rate on production traffic.

Common Pitfalls
Optimizing average latency while ignoring P99: head-of-line blocking from prefill makes tail latency the operationally relevant metric, not throughput.
Assuming prefix caching is a serving-layer concern: cache hit rates collapse without application-layer prompt discipline.
Using standard quality metrics to validate KV reuse correctness: perplexity and ROUGE miss the structured output and copying failures that reuse errors introduce.
Applying uniform GQA group sizes across layers: early layers need smaller groups for sensitivity containment; later layers can tolerate larger groups safely.
Treating calibration-derived reuse masks as static artifacts: gradual modality creep silently degrades mask accuracy over weeks without triggering quality alarms.
Open Question for Deeper Work

Can per-request induction head fire rate — measured cheaply as the frequency of near-offset-1 attention spikes during a lightweight forward pass — serve as a real-time dynamic signal to gate KV cache reuse decisions at inference time, replacing static offline masks with an adaptive per-request policy that remains correct under arbitrary distribution shift without requiring scheduled recalibration?






