Thesis: Reliable RAG under memory pressure requires redesigning the architectural boundary between retriever and LLM, because attention-based KV cache eviction is structurally blind to retrieval-critical tokens, and no eviction policy can compensate for signals the model was never given.

Key Insights
1. Attention sinks and retrieval-critical tokens occupy different cache positions — and eviction conflates them

Attention sink tokens (typically the first one or two sequence positions plus scattered punctuation) absorb disproportionate attention probability as a numerical stability artifact, not because they carry semantic content. Most eviction policies — H2O, StreamingLLM, SnapKV — use accumulated attention scores as their primary keep/evict signal, which means they are biased toward retaining sinks and recency-adjacent tokens while evicting middle-context spans. RAG evidence almost always lands in the middle, so the bias is precisely wrong. Worse, a token may receive near-zero attention during prefill yet become the only source of a specific fact the model needs to copy during generation, making prefill-time attention scores a fundamentally lagging indicator of generation-time need.

2. Layer-adaptive eviction schemes break down under multi-hop reasoning and fragmented retrieval

Systems like PyramidKV allocate more cache budget to later layers on the assumption that retrieval-critical attention concentrates there. This holds for single-hop lookup but fails for multi-hop queries, where entity binding peaks in middle layers (roughly layers 8–16 in a 32-layer model), and for multi-chunk RAG, where late-layer attention fragments across chunk boundaries rather than concentrating. The failure is mechanistically invisible to perplexity metrics — exact-match retrieval accuracy drops 15–30 percentage points on benchmarks like HELMET while summarization scores remain flat, exposing a systematic eval mismatch that has obscured the problem.

3. The retriever holds signals that could fix eviction but currently throws them away

BM25 scores, dense similarity scores, and chunk-level confidence are all available at context-construction time and correlate with generation-time retrieval need — but the current architectural contract discards them at the retriever-LLM boundary. Passing span-level importance scores as a sidecar signal to the KV eviction policy would give it a retrieval-grounded prior that attention scores cannot provide. This is a decoder-only analog of cross-attention gating in encoder-decoder models, and aligning retriever chunk granularity with eviction granularity (rather than running token-level eviction inside retriever-defined chunks) is a largely unexplored but structurally clean direction.

4. Joint fine-tuning creates score-gaming pressure that requires explicit countermeasures

When the retriever and LLM are fine-tuned end-to-end with eviction in the loop, the retriever learns to inflate importance scores uniformly to prevent eviction rather than to discriminate — a shortcut collapse analogous to exposure bias. Defenses include gradient stopping with auxiliary supervision, KL regularization against a frozen reference retriever, and adversarial eviction during training with curriculum-based budget annealing. Without these countermeasures, retrieval confidence scores drift significantly within a few thousand gradient steps, as documented in FLARE and Self-RAG fine-tuning experiments.

5. Runtime monitors must condition on parametric confidence, not just eviction depth

External faithfulness monitors based on KV provenance tracking produce excessive false positives for high-frequency entities the model has memorized from pretraining, and miss the genuinely dangerous case: high-confidence parametric answers that are stale. A well-designed monitor gates eviction alerts on both conditions simultaneously — source tokens evicted AND no-context logit below a retrieval-necessity threshold (~0.3 top-1 probability). The residual failure mode is confidently wrong stale knowledge, which no eviction-aware monitor can catch without an independent currency signal.

Common Pitfalls
Treating perplexity as a proxy for RAG faithfulness. Eviction policies that look identical on perplexity can diverge by 30+ points on exact-match retrieval tasks.
Assuming high attention score means important token. Sink dynamics contaminate this signal; a token that receives no prefill attention may still be the sole source of a generated fact.
Fixing eviction budget at training time. Deployment cache pressure varies dynamically; a model never trained at 10% retention will degrade catastrophically and silently at that budget.
Conflating eviction-induced confabulation with stale parametric knowledge. These require different interventions; monitors that treat them as the same problem will be miscalibrated in both directions.
Open Question for Deeper Work

How do you build a knowledge currency detector that operates at inference time without ground truth — distinguishing a high-confidence parametric answer that is correct from one that was correct at pretraining time but has since been superseded? This requires either a lightweight temporal provenance model over the LLM's own weights, a runtime consistency check against a continuously updated external index, or a calibrated uncertainty signal that degrades specifically for time-sensitive claim types — none of which exist in production-ready form, and all of which become critical once eviction monitors are gated on parametric confidence.






