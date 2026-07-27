Thesis: KV cache fragmentation in continuous batching inference servers is not a static allocator property but a dynamically evolving pathology driven by the interaction of preemptive scheduling, prefix sharing, speculative decoding, and staging buffer commit semantics — and no current system has a unified memory abstraction capable of managing all four simultaneously without silent consistency failures or throughput collapse.

Key Insights

1. Fragmentation is a scheduler artifact, not just an allocator artifact.
Block-granular allocation via PagedAttention decouples logical and physical KV memory, eliminating classical external fragmentation — but preemptive scheduling reintroduces fragmentation through time: evicted sequences strand partially-filled blocks, resume decisions scatter reloaded blocks non-contiguously, and the free-block estimates the scheduler uses for admission control diverge from physical reality under sustained preemption pressure. The fundamental error is treating memory availability as a static precondition for scheduling rather than a quantity that scheduling decisions actively reshape.

2. The recomputation/swap boundary is dynamic and regime-dependent.
The crossover point between recomputing evicted KV state and swapping it over PCIe is not a fixed token-count threshold but a function of concurrent sequence count, PCIe contention, and whether the GPU has idle capacity during prefill. Under high concurrency, PCIe convoy effects inflate swap latency while recomputation steals capacity from live decode batches, pushing both strategies toward mutual degradation. No production system currently implements an adaptive policy that conditions this choice on real-time queue depth and length distribution histograms, despite this being the correct operating point.

3. Prefix sharing and preemption have irreconcilable semantics under current allocators.
Reference counting protects shared prefix blocks while any referencing sequence is active, but simultaneous preemption of all sharers drops the refcount to zero, allowing silent reclamation. On resume, each sequence independently reloads the shared prefix, degrading O(1) sharing to O(N) redundant PCIe transfers with no mechanism to reconstruct the shared mapping. A lease-based ownership model with dependency DAG tracking is the necessary architectural primitive, but introduces its own livelock risk when the lease holder is itself preempted mid-reload under the same memory pressure that triggered eviction.

4. Speculative decoding rejection creates semantic invalidation invisible to reference counting.
When draft tokens are rejected, KV blocks written during the speculation window must be overwritten with corrected content, but DAG edges from dependent sequences encode block addresses rather than block epochs — meaning dependents can resume with physically valid but semantically stale block pointers. Staging buffers isolate speculative writes correctly in principle, but commit-time main-cache exhaustion forces a choice between stalling the decode batch, falling back to single-token decode, or partial acceptance, all of which are strictly worse than not speculating. The right fix — a three-state allocator with committed, reserved-pending, and staged block classes — does not exist in any current open-source system.

5. Reservation accounting must treat speculation windows as first-class resources.
The allocator's free-block estimate must subtract staged block capacity before each decode step, or commit failures are guaranteed under sustained load above roughly (1 − γ × block_size / total_cache) utilization. This interacts with prefix sharing in the speculation window: two sequences with converging drafts could share committed speculation blocks, but divergence at any token position requires copy-on-write separation at the exact divergence point, a fine-grained ownership transfer that neither RadixAttention nor any staging buffer design currently supports.

Common Pitfalls
Assuming block size is a tunable constant: block size governs the internal/external fragmentation tradeoff differently across request length distributions; a fixed block size is never Pareto-optimal for mixed short- and long-sequence workloads.
Conflating physical free blocks with schedulable capacity: staged, reserved-pending, and transfer-in-flight blocks are all physically occupied but invisible to naive free-block counts, causing systematic overcommit.
Treating eviction policies independently of resume policies: the choice to evict via swap vs. discard determines the resume cost structure; optimizing them separately produces locally rational but globally incoherent decisions.
Ignoring tensor parallelism in coherence analysis: partial eviction of a single layer requires coordinated shard eviction across all TP ranks; missing one shard produces a stall at the resume barrier that serializes the entire TP group.
Open Question for Deeper Work

Can a unified two-level scheduler — an outer planner managing lease grants, DAG dependencies, speculative epoch tracking, and three-state reservation accounting on a coarse time horizon, combined with an inner dispatcher handling chunk interleaving and batch composition at microsecond granularity — be implemented without the outer planner's coordination overhead becoming the new throughput bottleneck? Specifically, what is the minimum information the outer planner needs to make correct reservation decisions without observing every block-level allocation event, and does that minimum constitute a tractable abstraction boundary or does it require solving a variant of online bin-packing with precedence constraints?






