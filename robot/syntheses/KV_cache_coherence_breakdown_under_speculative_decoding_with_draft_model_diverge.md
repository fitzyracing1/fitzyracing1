Thesis: Speculative decoding's distribution-preservation guarantee — the mathematical foundation of its correctness — silently collapses in multi-tenant serving environments because block reference counting protocols have no representation for the draft-write/verify-read phase split, enabling eviction races that corrupt both draft and target model outputs without raising detectable errors, and existing eviction policies are structurally misaligned with speculative decoding's bursty, variable-length acceptance pattern.

Key Insights

1. Reference counting cannot represent speculative decoding's intermediate block states.
Standard block reference counting in systems like vLLM's PagedAttention tracks logical ownership — a refcount incremented on acquisition and decremented on release — but speculative decoding introduces a third block state between "reserved" and "shared": partially written by the draft model, awaiting target model verification. No refcount increment covers this window, so a concurrent eviction triggered by another tenant's memory pressure sees refcount=0 on a physically in-use block and reclaims it legally. The correct primitive is a versioned reader-writer latch that carries phase information — draft-write, verify-read, committed — so eviction eligibility is determined by block phase rather than logical owner count alone.

2. Rejected suffix blocks cannot be safely reused without full recompute, except in backbone-sharing architectures.
When a verification pass accepts k of n draft tokens, the KV activations in the rejected n-k blocks were computed by the draft model under its own weights, not the target model's. Reusing them violates the target-model KV equivalence invariant: because attention is a global dot product over the entire context, a single draft-model KV entry contaminates all subsequent attention outputs, making partial reuse strictly worse than eviction and recompute. The narrow exception is backbone-sharing draft architectures like Medusa, where layers 0 through L produce identical activations for both models, enabling genuine block reuse at shared-layer depth.

3. Multi-tenant prefix sharing converts single-sequence eviction races into cohort-wide integrity failures.
RadixAttention's shared prefix blocks are immutable once committed, so a single tenant's speculative rejection does not directly corrupt shared state. The failure mode is instead stale pointer retention: when memory pressure evicts a shared block, all tenants whose in-flight verification passes hold GPU-side pointers to that block's physical address continue reading from reclaimed memory, producing numerically arbitrary attention scores across the entire cohort simultaneously. With O(100) live references to a shared prefix block set in high-throughput deployments, a single eviction event can silently corrupt dozens of concurrent outputs.

4. Target model output corruption breaks the fundamental correctness guarantee of speculative decoding.
The distribution-preservation theorem assumes the target model's verification pass operates against an intact KV cache. When shared prefix blocks are stale, the target model's own logits are corrupted — not merely the draft tokens it evaluates. The most dangerous configuration is low-temperature greedy decoding over long retrieval-dependent contexts: the target model assigns maximum probability to a wrong token based on corrupted mid-context attention, accepts it with probability 1.0, and the system produces output that is strictly worse than non-cached autoregressive decoding with no error signal.

5. LRU eviction is structurally misaligned with speculative decoding's acceptance burst pattern.
Corruption events cluster around 88–92% GPU memory utilization because variable-length acceptance atomically commits multiple blocks, spiking occupancy and triggering burst evictions precisely when the most verification passes are in-flight. LRU misclassifies actively depended-upon shared prefix blocks as cold because they were last read at the start of the verification window. A corruption-resistant policy combines verification-in-flight pinning, predictive pre-eviction during the draft generation phase using the geometric acceptance length distribution, and a reserved speculative buffer sized to the 99th-percentile acceptance burst (~8–10% of GPU memory).

Common Pitfalls
Conflating logical and physical block safety: operators assume refcount=0 means safe-to-evict, missing the draft-write/verify-read phase gap entirely.
Monitoring mean acceptance rate: corruption-induced drops are masked by normal inter-prompt variance; per-block cache-state instrumentation is required to isolate the signal.
Assuming shared prefix immutability provides full protection: it prevents draft corruption propagation but not stale-pointer use-after-eviction, which is a distinct and equally dangerous failure mode.
Treating the speculative buffer as a tunable throughput knob: undersizing it to recover memory capacity eliminates the headroom needed to absorb acceptance bursts, re-entering the corruption regime under tail load.
Open Question for Deeper Work

A corruption-resistant eviction policy requires predicting post-acceptance memory occupancy before the verification result arrives, using the geometric distribution of acceptance lengths as a prior. The open question is whether this prior is stationary across serving sessions: draft model acceptance rates shift with prompt domain, batch composition, and quantization regime, and an eviction policy calibrated on one distribution may systematically underreserve headroom on out-of-distribution traffic, recreating the corruption regime at a different utilization threshold. Characterizing the non-stationarity of acceptance length distributions across realistic multi-tenant workloads — and designing online-adaptive reservation policies that track distributional drift without introducing their own coherence hazards — remains an open systems research problem.






