Thesis: KV cache eviction policy is not a cache engineering detail but a systems-level design decision whose correctness depends entirely on the statistical structure of the prompt distribution — and most production failure modes in long-context inference serving trace back to a mismatch between the assumptions embedded in a policy and the actual shape of incoming workloads.

Key Insights

1. Prefix tree depth-to-branching-ratio determines whether LRU is near-optimal or catastrophic.
LRU performs well when prompts share a deep common trunk with few diverging suffixes — a single stable system prompt serving many users. It collapses under RAG and agent workloads where a shallow shared prefix fans into thousands of unique long-document continuations, because recency loses all correlation with reuse probability. SGLang's RadixAttention exploits the high-ratio case by evicting radix tree leaves first; vLLM's prefix caching similarly assumes high match rates. Both degrade silently when the branching structure inverts, and standard hit-rate metrics do not surface the degradation because they treat all misses as equal.

2. Hit rate is the wrong metric; recomputation FLOP rate exposes what hit rate hides.
Under heavy-tailed prompt length distributions, evicting a 4,000-token document encoding and a 200-token system prompt are both single eviction events in hit-rate accounting, but the recomputation cost differs by 400×. Block-based allocators (vLLM's 16-token pages) add internal fragmentation at sequence boundaries, consuming 5–15% of cache capacity invisibly. The metric that predicts user-visible latency is recomputation FLOP rate, which is length-weighted and captures the burst structure of eviction cascades that hit rate averages away.

3. Decode-phase blocks create a pinning-versus-admission tradeoff with no clean local resolution.
Blocks held by in-flight decode requests are simultaneously "actively required" and "eviction candidates" in systems without explicit residency pinning. Evicting them triggers preemption and full prefill recomputation — a 3–8× latency multiplier. Pinning them shrinks the evictable pool, causing admission starvation under sustained load. The correct optimization target depends on objective: throughput maximization favors evicting early-decode requests via a completion-proximity heuristic; SLA P99 commitments require pinning much earlier (30–40% completion) to bound tail latency, accepting lower raw throughput.

4. Live KV migration relocates the consistency hazard rather than eliminating it.
Migrating KV blocks between instances while decode advances on the source produces migrating-state divergence: the destination receives a snapshot stale by 3–7 tokens for typical context sizes and inter-node transfer latencies. Disaggregated prefill-decode architectures (Splitwise, DistServe) move this hazard to a permanent architectural interface — the prefill-to-decode transfer barrier — which now sits on the critical path of every request. The barrier must be enforced at last-token-of-prefill with layer-granularity sequence numbers, adding per-layer synchronization overhead that can consume 10–40ms under interconnect contention.

5. The optimal architecture is workload-conditional on prefill fraction φ and arrival burstiness.
When φ is high (long prompts, short outputs — summarization, RAG extraction), disaggregation moves the bottleneck onto the interconnect without parallelizing the dominant cost; co-location wins. When φ is low (long generation, short prompts), disaggregation pipelines prefill across requests while decode runs continuously, and transfer cost amortizes over hundreds of steps. Model size shifts the crossover: the co-location-favoring prompt length threshold drops from ~2,000 tokens for 7B models to ~400 tokens for 70B models on the same interconnect.

Common Pitfalls
Evaluating eviction policy on uniform synthetic workloads. Production prompt distributions are heavy-tailed and structurally heterogeneous; a policy that achieves 90% hit rate on synthetic benchmarks can produce near-zero reuse on real RAG traffic.
Conflating cache miss count with cache miss cost. Length-weighted cost accounting is mandatory; unweighted metrics actively mislead capacity planning.
Treating preemption as a rare edge case. Under sustained memory pressure with continuous batching, preemption of decode-phase requests becomes a steady-state phenomenon, not an exception, and must be budgeted explicitly.
Assuming disaggregation is unconditionally better at scale. The transfer barrier cost is real and scales with model depth; disaggregation can increase P99 latency for high-φ workloads even while improving throughput on low-φ ones.
Open Question for Deeper Work

Production request streams have continuously varying φ and arrival burstiness, making any static architectural choice suboptimal across the full distribution. The open question is whether a system can make dynamic co-location versus disaggregation routing decisions per request or per time window — and at what decision latency that switching becomes useful rather than harmful. The challenge is that the switching decision requires predicting output length (to estimate φ) before generation begins, and output length prediction for open-ended generation remains unsolved with the accuracy needed to make routing decisions whose cost differential is measured in tens of milliseconds.






