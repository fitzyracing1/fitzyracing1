Thesis: Freezing the routing network in a MoE model during continual domain-incremental fine-tuning does not merely prevent routing adaptation — it converts distributional novelty into a self-reinforcing cascade of capacity misallocation, optimizer state desynchronization, and monitoring blindness that standard auxiliary losses and Adam-based optimizers are structurally incapable of detecting or correcting.

Key Insights
1. Frozen routing transforms domain shift into structured capacity failure

When the router is frozen, new-domain tokens are force-mapped onto an expert partition optimized for prior domains. A subset of experts becomes systematically overloaded while others receive near-zero token flow. Because Switch Transformer-style capacity constraints drop overflow tokens rather than rerouting them, the gradient signal for overloaded experts is both truncated and biased toward routing-confident, easier examples — the hardest novel-domain tokens are statistically most likely to be dropped. This is not random noise; it is a deterministic degradation path whose severity grows with distributional distance between the new domain and the routing network's training distribution.

2. Auxiliary loss saturation masks per-domain collapse

Standard load-balancing losses (GShard's importance loss, ST-MoE's z-loss) are computed over aggregate batch statistics, not per-domain statistics. Under mixed-batch training or when domain increments are processed sequentially, these metrics can report acceptable global balance while per-domain expert utilization collapses silently. The monitoring signal stays green precisely because it is insensitive to the structured imbalance that frozen routing produces — a classic case where the evaluation metric and the failure mode are orthogonal.

3. Adam optimizer state desynchronizes irreversibly across experts

Overloaded experts accumulate inflated second-moment estimates 
𝑣
𝑡
v
t
	​

 from repeated high-variance gradient spikes; underloaded experts retain near-zero 
𝑣
𝑡
v
t
	​

 from gradient starvation. Given Adam's 
𝛽
2
≈
0.999
β
2
	​

≈0.999 and typical per-domain fine-tuning windows of 1K–10K steps, the moment estimates never decay to a neutral baseline before the next domain arrives. This optimizer state desynchronization compounds monotonically across domain increments and, critically, persists even if the router is later unfrozen — the router weights enter Adam with zero moment history, causing aggressive oscillatory updates against suppressed expert weights.

4. Domain arrival order is an exploitable attack surface

Because Adam's second-moment estimates encode an implicit memory of token load history, adversarial or non-i.i.d. domain sequencing can deliberately drive targeted expert collapse without corrupting any individual training example. An adversary with access to the router's affinity map can execute a two-phase attack: saturate target experts' 
𝑣
𝑡
v
t
	​

 estimates with high-affinity domains first, then submit the capability domain of interest to find those experts update-resistant. This attack leaves no forensic signature in per-domain data quality and generalizes to accidental non-i.i.d. sequencing, making it a systemic reliability concern as well as a security one.

5. Routing-aware optimizer defenses face a recursive exploitability problem

A routing-conditional moment normalization scheme — tracking per-expert load fractions 
𝑛
^
𝑒
n
^
e
	​

 as read-only router statistics and rescaling 
𝑣
𝑡
v
t
	​

 accumulation accordingly — can in principle prevent moment divergence without reintroducing router-optimizer coupling. However, any asymmetric smoothing policy sensitive enough to track real domain transitions (fast response to load increases, slow response to decreases) creates an exploitable hysteresis gap: adversarial burst sequences can ratchet 
𝑛
^
𝑒
n
^
e
	​

 to an artificially high plateau, using the defense mechanism itself as a learning rate suppression weapon. Robust defense ultimately requires data provenance guarantees at the pipeline level, not just algorithmic fixes.

Common Pitfalls
Conflating routing freeze with stability: Practitioners freeze routers to reduce training complexity, but interpret the absence of routing oscillation as evidence of stability — missing that weight-level pathology is accumulating beneath static routing assignments.
Trusting aggregate auxiliary loss as a health signal: Global load balance metrics are insufficient diagnostics; per-domain, per-layer expert utilization must be monitored explicitly.
Ignoring optimizer state when unfreezing: Resuming end-to-end training after a frozen-router phase without resetting or re-warming optimizer states produces routing oscillation that is misattributed to architectural instability rather than moment miscalibration.
Assuming clean data implies safe sequencing: Multi-tenant or multi-source fine-tuning pipelines with individually clean datasets can still produce adversarial-equivalent optimizer corruption through non-i.i.d. arrival order.
Open Question for Deeper Work

Can a tamper-evident, decentralized load statistics protocol be designed for expert-parallel MoE systems that provides provenance guarantees over token routing assignments without reintroducing the centralization bottlenecks that expert parallelism eliminates — and if so, what is the minimum cryptographic or consensus primitive required, and how does its synchronization cost interact with the all-to-all collectives already on the critical path of large-scale MoE training?




