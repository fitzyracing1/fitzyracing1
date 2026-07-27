Thesis: In multi-tenant LLM serving, preemptive priority scheduling does not merely redistribute latency across tiers — it amplifies latency variance nonlinearly through a chain of coupled feedback loops spanning KV cache allocation, recomputation queuing, admission control, and SLO contract enforcement, such that a single misconfigured preemption threshold can produce system-wide cascade instability that no per-tenant dashboard reveals and no single-layer fix resolves.

Key Insights

1. Variance, not mean latency, is the primary cascade vector.
Preemption events reorder the decode queue for all co-resident requests simultaneously, shifting inter-token delay distributions in a correlated burst rather than independently. Requests already near their SLO boundary absorb this jitter spike and breach, triggering client-side retries that re-enter the queue and amplify load. Standard queueing models (Little's Law, M/M/1) fail to capture this because they assume Poisson arrivals and memoryless service times; LLM decode violates both, making tail latency behavior analytically intractable without simulation or empirical profiling.

2. KV cache eviction creates a recomputation cost that attacks the system at its moment of maximum pressure.
When a preempted request's KV cache is evicted, the recompute cost — a full O(n²) prefill pass, 200–800ms for 4K-token contexts on A100 hardware — hits GPU memory precisely when the system is already under the pressure that triggered preemption. Naively re-queuing the evicted request at its original priority causes effective livelock: it is repeatedly displaced before recomputation completes. The correct fix — priority inheritance for recompute jobs — directly conflicts with the preemption rationale, requiring a reserved memory partition (empirically 15–20% of KV cache) that the allocator enforces at admission time, not eviction time.

3. Misconfiguration and burst absorption produce identical surface signals but require opposite interventions.
The preemption-to-completion ratio (PCR) per priority tier, tracked over a 30–60 second sliding window and cross-referenced against high-priority arrival rate, distinguishes systematic over-preemption from legitimate burst handling. Correction requires an asymmetric exponential ramp — loosening preemption aggressiveness at half the rate of tightening — gated on recompute queue drain confirmation at each step, because premature loosening creates a demand peak that can exceed the original misconfiguration's pressure.

4. Multi-tenant correction ramps must be globally serialized to prevent second-order cascades.
When multiple tenants simultaneously detect misconfiguration and initiate independent correction ramps, the aggregate memory demand increase per interval can exceed reserved partition capacity, triggering a new preemption round during the correction phase. A global token-bucket at the correction layer — one loosening token per 5–15 second interval, awarded to the highest-distress tenant — serializes recovery and bounds aggregate memory demand, but introduces recovery latency proportional to tenant count, requiring SLO contracts with explicit windowed compliance budgets and per-cause correction reserves to avoid breach during legitimate deferral.

5. Incentive alignment and information exposure are coupled problems that cannot be solved independently.
A correction credit mechanism that makes over-reporting self-penalizing requires tenants to have real-time visibility into their credit balance, but that visibility exposes global scheduler state enabling strategic coordination attacks. Differential privacy (ε ≤ 0.1 per observation, with 60-second bucketed publication) bounds per-observation leakage, but composition theorem degradation over long observation horizons requires treating the privacy budget as a lifetime allocation with periodic noise rotation — and each rotation event resets tenants' accumulated statistical baselines, creating a transient rational incentive to over-report that the credit mechanism must explicitly absorb.

Common Pitfalls
Conflating P50 and P99 in SLO definitions, which masks tail variance until cascades are already in progress.
Treating the memory allocator as priority-unaware, allowing recompute jobs to displace high-priority decode steps through a resource layer the scheduler cannot observe.
Applying symmetric PID control to preemption aggressiveness adjustment, which oscillates around equilibrium at frequencies that map directly onto P99 latency spikes.
Issuing per-tenant SLO dashboards without cross-tenant variance analysis, making correction-induced instability invisible to both operators and tenants.
Negotiating SLA correction reserves with procurement teams who never see scheduler internals, rendering incentive-compatible contract structures behaviorally inert.
Open Question for Deeper Work

Noise rotation events in the differential privacy layer create transient windows of rational over-reporting — but the duration of that window, and therefore the correction credit reserve the global controller must hold against it, depends on how quickly tenants can rebuild a statistical baseline post-rotation. This is an open empirical question: does baseline reconstruction time scale with tenant request rate, context length distribution, or co-tenant count, and can the controller adaptively time rotation events to coincide with naturally low-distress periods to minimize the transient over-reporting incentive without violating the lifetime privacy budget?






