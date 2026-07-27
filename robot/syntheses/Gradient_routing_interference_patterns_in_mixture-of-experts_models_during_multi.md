Thesis: In multi-objective fine-tuning of MoE models, the router is a shared differentiable bottleneck through which all task gradients compete, and the resulting interference is geometric, non-stationary, and largely invisible to loss-level interventions — requiring architectural and distributional reasoning to diagnose and repair.

Key Insights
1. The router is the true locus of multi-task interference

Beginners assume expert specialization provides automatic task isolation, but the gate is a fully shared parameter that receives a superposition of all task gradients simultaneously. When task loss scales differ by an order of magnitude, the dominant loss steers routing decisions regardless of expert suitability, and even "inactive" experts receive gradient updates proportional to their gate weight. Loss normalization equalizes scalar magnitudes but cannot resolve the underlying geometric conflict: tasks requiring different directions in residual stream space will produce conflicting gate updates that no scalar reweighting scheme can separate, because the conflict lives in the convex combination coefficients at the expert output combination step.

2. Freezing the router trades one failure mode for a structurally worse one

Freezing gate parameters eliminates routing drift but introduces expert capacity mismatch: the frozen gate, calibrated to the pre-training token distribution, systematically funnels narrow fine-tuning distributions into a small subset of experts, starving the rest of gradient signal. This converts a slow, monitorable corruption into a hard structural exclusion — underutilized experts go stale and cannot recover without unfreezing, and the overloaded experts must absorb conflicting objectives they were not specialized for.

3. Gradient surgery on gate parameters is theoretically unsound in sparse top-k routing

Gradient surgery requires stable pairwise conflict estimates, but in top-k sparse routing the conflict structure over gate parameters shifts with every batch as stochastic expert selection changes which parameters receive nonzero gradients. The surrogate gradients produced by softmax-before-topk tricks are computed over the full expert distribution even though only k experts fired, making cosine similarity estimates unreliable. The theoretically stable object is the expected routing distribution — the marginal assignment probability averaged over the data distribution — whose Jacobian with respect to gate parameters averages out selection noise and provides a consistent target for conflict-resolution schemes.

4. Trust region constraints and load-balancing losses are in direct tension

Treating the router as a stochastic policy and imposing TRPO-style KL constraints correctly slows routing drift early in fine-tuning, but actively resists the rebalancing signal later when utilization entropy has collapsed. Standard auxiliary loss coefficients (0.01–0.1) combined with typical trust region radii (KL ≤ 0.01) mean load balancing makes negligible per-step progress precisely when it is most needed. No current MoE system implements an adaptive trust region radius coupled to a routing health metric such as utilization entropy.

5. Expert cloning is the least destructive architectural recovery intervention — but only if token heterogeneity exists

When utilization entropy collapses late in fine-tuning, cloning overloaded experts into gradient-starved ones and breaking symmetry with small input-projection perturbations can restore balance without corrupting learned representations. However, divergence after cloning requires the overloaded expert's token population to contain distinguishable subpopulations in activation space — verifiable via GMM or k-means with silhouette score above roughly 0.3. If fine-tuning has collapsed token heterogeneity into a single tight cluster, the MoE layer itself cannot solve the problem; the intervention must move upstream to the input representation or tokenization level.

Common Pitfalls
Assuming loss normalization is sufficient. It addresses scalar magnitude but not gradient direction conflict at the combination step.
Treating expert parameters as isolated. Gate weights are fully shared; no expert is shielded from other tasks' gradient influence through the router.
Measuring cluster structure in pre-trained activations. Domain-specific fine-tuning actively destroys token heterogeneity; only the fine-tuned activation space is diagnostic.
Applying gradient surgery with fixed conflict graphs. The non-stationarity of sparse routing invalidates convergence guarantees of all standard gradient-modification schemes.
Using a fixed auxiliary loss coefficient throughout training. Early and late fine-tuning have opposite requirements for how much the router should be allowed to move.
Open Question for Deeper Work

If single-cluster token heterogeneity collapse indicates the MoE layer cannot self-repair, precisely what property of the upstream input representation determines whether re-heterogenization is possible without restarting fine-tuning — and is there a measurable threshold in the pre-MoE hidden state geometry below which any fine-tuning run on a narrow distribution is guaranteed to produce irrecoverable expert collapse, regardless of loss weighting or architectural intervention?






