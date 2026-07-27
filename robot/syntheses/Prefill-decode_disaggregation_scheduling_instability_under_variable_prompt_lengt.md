Thesis: Prefill-decode disaggregation improves LLM inference efficiency by separating compute-bound and memory-bandwidth-bound phases onto dedicated accelerator pools, but this separation introduces a class of scheduling instabilities — oscillating queue depths, cascading evictions, and bidirectional backpressure — that only manifest under realistic heavy-tailed prompt length distributions and heterogeneous accelerator memory bandwidth profiles, and that simple throughput metrics will not detect until SLA breach is already underway.

Key Insights

1. The transfer channel is a first-class resource, not a consequence of node counts.
The KV cache transfer protocol between prefill and decode nodes — whether push- or pull-based, atomic or chunked, over NVLink or RoCEv2 — determines whether queue oscillation damps or amplifies under long-prompt bursts. Push-based atomic transfer creates thundering-herd write storms; pull-based chunked transfer damps injection rate to decode-side absorption capacity. Critically, the interconnect's bandwidth-delay product sets the oscillation frequency: a 70B-model KV tensor for a 4096-token sequence transfers in 3–4ms over NVLink, meaning schedulers operating on coarser timescales will systematically mis-estimate decode-node readiness. Current orchestration layers have no native abstraction for inter-node bandwidth as a schedulable resource, making this failure mode structurally invisible to standard Kubernetes-based autoscalers.

2. Checkpoint-based eviction recovery is architecture-dependent in non-obvious ways.
When HBM pressure forces KV eviction on prefill nodes, layer-boundary activation checkpoints can make recomputation cheaper than full re-prefill — but this path closes in hybrid architectures. SSM hidden states (e.g., Mamba's selective scan state, ~64 KB per sequence per layer) are causally non-decomposable: reconstructing them requires replaying every preceding token through the SSM kernel. In Jamba-style interleaved architectures, transformer KV eviction cannot be decided per-layer independently because retained SSM states are only useful if all upstream transformer layers are either retained or cheaply recomputable from a preceding checkpoint, requiring the scheduler to maintain a live dependency DAG over layer ranges.

3. Sequence-level interventions must precede checkpoint-level ones under extreme pressure.
When no transformer KV eviction is possible without forcing SSM-state recomputation, the prefill node's options are sequence-level: admission gating with explicit HBM occupancy backpressure, mid-prefill preemption with CPU-DRAM parking (~140ms to park 4 GB at PCIe 4.0 bandwidth), sequence migration to less-pressured peer nodes, or accelerating decode-side KV pull to flush completed tensors from prefill HBM. The intervention most consistently overlooked is the last: pulling already-completed KV tensors converts prefill HBM from a staging buffer back into working memory without any recomputation cost.

4. Static prefill-to-decode ratios are stationarity assumptions that production traffic continuously violates.
Bidirectional backpressure — prefill nodes unable to flush, decode nodes unable to accept — reveals that the optimal ratio identified under a given prompt/output length distribution (as in DistServe) becomes harmful the moment that distribution shifts. Prefill and decode have asymmetric scaling curves: prefill scales linearly with added nodes for compute-bound long prompts, while decode scales sublinearly under memory-bandwidth saturation due to increasingly random KV access patterns. Autoscalers must treat transfer channel utilization as a leading indicator, with ~70% sustained utilization predicting saturation 20–40 seconds before queue depth metrics cross thresholds.

5. The provisioning gap demands layered in-situ buffering strategies.
With GPU node provisioning taking 30–120 seconds, the serving layer must survive autonomously: priority-stratified queue shedding with client-visible 429s, prompt-length-based admission tiering, speculative decode draft-length increases (30–50% throughput gain under favorable conditions per Medusa), and CPU-DRAM KV offload as a pressure relief valve. Pre-provisioning warm standby capacity scaled to historical burst variance — typically 10–15% idle GPU overhead — eliminates the provisioning gap for predictable diurnal bursts and is consistently cheaper than SLA penalty credits from cascading violations.

Common Pitfalls
Monitoring queue depth instead of transfer channel utilization causes autoscaler reactions to lag saturation by 20–40 seconds, well inside the zone where cascading failures begin.
Treating eviction decisions as per-layer independent in hybrid architectures ignores upstream dependency chains; evicting a transformer KV block that feeds a retained SSM state forces SSM recomputation anyway, negating the savings.
Implementing push-based atomic KV transfer creates thundering-herd injection storms under long-prompt bursts; chunked or pull-based transfer should be the default design choice.
Scaling decode nodes proportionally to queue depth under long-prompt saturation increases KV pull demand before decode-side HBM has capacity to absorb it, transiently worsening channel saturation.
Open Question for Deeper Work

Current mitigation strategies treat the prefill-decode boundary as fixed: a sequence completes prefill on one node and transfers its KV state to a decode node. The deeper open question is whether continuous, partial-prefill pipelining — where decode begins on early-layer KV blocks while prefill is still computing later layers — can eliminate the transfer channel as a discrete bottleneck entirely, and what new scheduling primitives, consistency guarantees, and attention kernel modifications this would require in hybrid SSM-transformer architectures where layer interdependencies make partial-state handoff semantically non-trivial.







Want to be notified when Claude responds?
Notify
