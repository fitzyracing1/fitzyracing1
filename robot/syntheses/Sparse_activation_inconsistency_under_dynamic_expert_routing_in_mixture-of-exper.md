Thesis: Sparse expert routing in MoE inference is not a solved load-balancing problem but a deeply entangled system pathology in which capacity constraints, representation corruption, attention distortion, temporal routing rigidity, and KV cache coherence violations form a mutually reinforcing failure complex that standard auxiliary losses and serving optimizations address only at the surface.

Key Insights
1. Capacity overflow converts statistical imbalance into hard representational damage

Expert load imbalance is not merely a throughput inefficiency — when token demand exceeds expert capacity buffers, overflowed tokens traverse the layer via identity pass-through, receiving no expert transformation. Because overflowed tokens share semantic similarity by construction (the router sent them to the same hot expert for a reason), the representation deficit is structured rather than random: entire semantic categories — entity mentions, numerics, domain-specific terminology — are systematically undertransformed, producing a shallower and less discriminable token population that propagates corrupted representations into every subsequent layer. This corruption is invisible to perplexity metrics and standard benchmarks but surfaces as degraded performance on tasks requiring fine-grained token discrimination such as coreference resolution and cross-sentence numerical reasoning.

2. Structured omission is thermodynamically inevitable under fixed expert capacity

Every routing regime trades one form of structured omission for another. Token-choice routing overflows hot experts; Expert Choice routing systematically excludes low-priority tokens; hash routing destroys specialization; soft MoE pre-hoc averages token representations before expert processing, smoothing away the individual token identity that downstream attention requires. The information-theoretic constraint is absolute: at fixed total expert compute, any non-uniform input distribution must accept either dropped tokens, diluted specialization, or serialized computation. The design space is not "how to eliminate structured omission" but "which structure of omission is least harmful for the target task distribution."

3. Autoregressive decoding transforms spatial imbalance into temporal routing rigidity

Single-token decode passes eliminate within-layer capacity overflow but replace it with a temporal pathology: routing decisions across generation steps are correlated, quasi-deterministic, and self-reinforcing. Early routing choices shape the hidden state that drives subsequent routing, creating hysteresis — routing errors compound across steps rather than averaging out. At the serving level, concurrent requests with similar prompt distributions cluster onto the same expert subsets, creating cross-request hot experts in continuous batching systems even when no individual request exceeds per-request capacity. Decode-phase expert utilization variance measured in DeepSpeed-MoE runs 3-4× higher than prefill-phase variance, with direct throughput consequences.

4. Speculative routing prediction is accurate but brittle at precisely the wrong moments

The quasi-determinism of decode routing trajectories enables prefix-conditioned routing prediction with 75-85% accuracy in stable same-domain generation, supporting expert weight pre-fetching as a latency optimization. However, prediction accuracy collapses at generative branching points and domain transitions — exactly the moments when the optimization is most needed to avoid bandwidth penalties from wrong pre-fetches. Worse, pre-fetching under memory pressure can implicitly bias actual routing toward predicted experts by making non-predicted experts unavailable, corrupting the trajectory statistics that the prediction system relies on and creating a self-fulfilling feedback loop between the predictor and the router.

5. KV cache coherence is structurally violated by routing regime changes

KV cache entries encode not just token representations but the full routing history of the generation — each cached key-value pair reflects the specific sequence of expert projections applied at every prior layer. Partial cache invalidation after a routing regime change produces a chimera cache in which entries from incompatible routing regimes coexist, and attention over this mixed population introduces magnitude-driven softmax distortion orthogonal to semantic relevance. The representational distance between old- and new-regime cache entries can reach 0.3-0.6 cosine distance units for domain-shifted inputs, far exceeding attention's noise tolerance. Full recomputation restores consistency at O(T) cost; partial invalidation trades drift for discontinuity; neither is satisfactory for long-form generation.

Common Pitfalls
Treating load imbalance as a training problem solved by auxiliary loss: Auxiliary load-balancing losses reduce but do not eliminate routing concentration, and their effect on inference-time imbalance under distribution shift is poorly calibrated.
Benchmarking MoE serving with perplexity or average latency: Both metrics obscure the tail behaviors — structured token omission and throughput variance spikes — that constitute the real failure modes.
Assuming Expert Choice routing fixes overflow: It eliminates overflow while recreating structured omission through systematic non-selection, which is equally damaging for token discrimination tasks.
Treating prefix caching and MoE routing as independent optimizations: Shared KV cache entries across requests with different routing histories introduce coherence violations that neither system is designed to detect or handle.
Open Question for Deeper Work

Can a serving system maintain a per-request routing provenance tag on KV cache entries — tracking which expert regime produced each cached representation — and use this metadata to either reject cache reuse across incompatible regimes or apply a learned representational alignment transformation at cache retrieval time? The challenge is that routing provenance is high-dimensional (a regime fingerprint spans all layers and all steps) and alignment transformations would need to be applied at attention time without breaking the linear structure that makes KV caching efficient — but solving this would decouple prefix caching from routing consistency in a principled way and unlock safe cache sharing across MoE serving workloads that current systems cannot support.






