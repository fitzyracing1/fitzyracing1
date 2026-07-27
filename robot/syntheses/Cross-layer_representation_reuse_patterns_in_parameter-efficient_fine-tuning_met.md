Thesis: Sharing adapter parameters across transformer layers does not merely reduce parameter count — it fundamentally restructures the geometry of catastrophic forgetting, coupling gradient flows, distorting curvature estimates, and creating rank-exhaustion limits that make forgetting boundaries qualitatively different from those of independent per-layer PEFT methods.

Key Insights
1. Cross-layer sharing creates correlated, non-local forgetting

When layers share a LoRA adapter, a single update to the shared 
𝐴
,
𝐵
A,B matrices propagates interference simultaneously across all participating layers. Unlike independent adapters, where forgetting is localized to the layer whose update overwrites pretrained structure, shared adapters can destroy capabilities encoded across multiple layers in a single gradient step. The interference is governed by the inner product between per-layer gradient contributions in the adapter parameter space: when these are anti-aligned, the shared adapter is pulled in contradictory directions, and their sum projects destructively onto the pretrained weight subspace. The forgetting boundary is therefore not a smooth frontier but potentially a cliff — and one that is invisible if you monitor only parameter count or aggregate loss.

2. Fisher curvature imbalance determines which layer dominates — and when

Layers with higher Fisher information curvature dominate the shared adapter's update direction early in fine-tuning, when their loss gradients are large. As the high-curvature layer saturates, its gradient magnitude drops and the low-curvature layer's influence grows. The transition zone — when both layers exert comparable gradient magnitudes — is the period of maximum forgetting risk, because the shared adapter is simultaneously pulled in two directions of comparable strength, maximizing projection onto the pretrained weight subspace. This crossover is empirically detectable from per-layer gradient norm ratios and predicts forgetting spikes 100–500 steps ahead of their occurrence.

3. Coupled K-FAC approximations systematically misestimate curvature in the most dangerous directions

The cross-layer sharing structure causes K-FAC Fisher approximations to average per-layer curvature signals, discarding the variance across layers. Directions where layers have opposing high curvature — precisely the directions most likely to produce destructive interference — appear as low-curvature to the coupled estimator and receive insufficient regularization penalty. The result is that the pretrained directions most worth protecting (high singular value in 
𝑊
0
W
0
	​

, high cross-layer curvature variance) are the ones the approximation most systematically under-protects. A cross-layer curvature variance correction term, added back to the mean K-FAC estimate, addresses this without requiring full per-layer Fisher recomputation.

4. Preemptive subspace projection beats adaptive regularization — except when tasks share geometric real estate

Dangerous update directions can be identified before fine-tuning using only the pretrained model and a calibration set (high pretrained singular value combined with high cross-layer curvature variance). Hard projection away from these directions is structurally superior to adaptive regularization because it cannot be overridden by large task gradients and requires no staleness monitoring. However, when the fine-tuning task genuinely requires movement along those same directions — as in domain-adaptive coding or semantically adjacent task transfer — preemptive projection prevents learning as well as forgetting. The practical optimum is hybrid: hard projection on the top-
𝑘
k most dangerous directions, adaptive regularization on the remainder.

5. Sequential fine-tuning faces a rank exhaustion limit that is geometry-dependent, not merely arithmetic

A rank-
𝑟
r shared adapter can stably accommodate only as many sequential tasks as there are linearly independent gradient directions within its subspace. For semantically related tasks on LLaMA-7B with rank-16 adapters, interference appears after roughly 4–6 tasks. Stability depends critically on task ordering and gradient orthogonality: diverse task sequences consume rank more slowly than semantically clustered ones. Adapter superposition methods (LoRAHub-style task-specific scaling over a shared basis) decouple the boundary negotiation problem from rank exhaustion, extending stable capacity to 20+ tasks in reported benchmarks.

Common Pitfalls
Treating parameter count as a proxy for forgetting risk. Rank and count determine capacity; subspace alignment with pretrained structure determines actual forgetting.
Using a single Fisher estimate throughout training. Staleness accumulates rapidly with shared adapters; KL-divergence-triggered recomputation is necessary.
Ignoring task ordering in sequential fine-tuning. Semantically clustered task sequences exhaust adapter rank far faster than diverse sequences at identical total task count.
Applying adaptive regularization without variance correction. Standard K-FAC on shared adapters under-protects the most dangerous directions by construction.
Open Question for Deeper Work

Does increasing shared adapter rank increase sequential task capacity linearly, or does the geometry of low-rank subspaces produce a sharp nonlinear threshold — a phase transition — where capacity suddenly collapses as the cumulative task subspace begins to overlap the pretrained model's high-curvature directions? If such a threshold exists, its location would depend on the angular distribution of task gradient directions relative to pretrained singular structure, and identifying it analytically or empirically would give practitioners a principled rank selection criterion grounded in forgetting geometry rather than downstream benchmark performance alone.






