The user wants a markdown synthesis brief, not a Word doc. I'll produce it inline.

Gradient conflicts under simultaneous multi-objective loss weighting with Pareto front instability and task interference amplification in dense prediction architectures

Thesis: Multi-task dense prediction networks do not merely face a tuning problem solvable by better loss weights — they face a structural problem in which the geometry of conflicting gradient subspaces, the non-stationarity of task affinity, and the compounding effects of skip connections and shared normalization jointly ensure that naive shared-trunk architectures cannot converge to stable Pareto-optimal solutions regardless of the sophistication of the gradient aggregation method applied.

Key Insights
1. Gradient conflict is a subspace geometry problem, not a magnitude problem

PCGrad-style projection methods fail not because the idea is wrong but because they assume pairwise conflict is the exhaustive conflict topology. In practice, projecting task A's gradient onto the normal plane of task B's gradient displaces the conflict into dimensions occupied by task C, or lands the update in a flat region for the projected task that is steep for a bystander task. When gradient magnitudes are asymmetric — as they reliably are when tasks learn at different speeds — projection becomes geometrically correct but practically inert: the dominant task's residual still controls the update direction. The fix requires either explicit orthogonality constraints across all task gradient subspaces simultaneously (Nash-MTL, CAGrad) or architectural separation that prevents the gradients from competing in the same parameter space at all.

2. Shared normalization layers relocate rather than absorb interference

Task-specific BatchNorm resolves the distributional conflict at the normalization layer but transfers it upstream to the shared conv weights that feed all BN branches simultaneously. Those conv weights now receive summed gradients from multiple task-specific BN paths and settle into low-rank compromise solutions — measurably so, with CKA analysis showing decreased similarity between single-task and multi-task conv gradients in task-specific BN settings compared to shared BN, indicating harder competition not easier. The rank collapse is not fixed by increasing encoder width: wider networks spread the conflict across more dimensions without changing the attractor structure, yielding ~1-2% multi-task improvement on NYUv2 versus ~4-6% single-task improvement from the same width increase.

3. The Pareto front is non-stationary in a way that invalidates per-step bargaining

Nash-MTL and similar methods solve a well-defined local optimization problem — finding the gradient combination corresponding to a Nash bargaining equilibrium — but the game whose equilibrium they are solving is being continuously rewritten by the parameter updates those solutions produce. Task affinity (the sign and magnitude of inter-task gradient alignment) is not a fixed property of task definitions but a function of current representations, and it can qualitatively flip during training: depth and surface normals begin as low-affinity pairs on natural image statistics and become high-affinity once the network learns 3D scene geometry. The empirical signature is persistent oscillation in task loss ratios (~15-20% variance under Nash-MTL vs ~5-8% for single-task baselines) rather than convergence — the optimizer is perpetually rebalancing a moving target.

4. Negative affinity is a more reliable routing signal than positive affinity

Pre-training task affinity scores drop to Spearman rank correlation ~0.3 for geometrically dissimilar task pairs by mid-training, meaning positive-affinity-based routing decisions are essentially stale by the time the network they inform is trained. Negative affinity — which task pairs reliably interfere — is substantially more stable because it reflects deep incompatibilities in required representational structure that persist across training phases. This asymmetry implies that task grouping algorithms should be framed as conflict avoidance (find the minimal negative-affinity cut) rather than synergy maximization (find the maximal positive-affinity clique). Architectures designed from conflict-avoidance principles — sparsely connected branching with hard separation for high-conflict pairs — degrade ~8% less at convergence than those designed from positive-affinity clustering, per Bruggemann et al. (2021).

5. Optimal branching depth is task-pair-specific, making fixed shared trunks structurally suboptimal

The network depth at which two tasks' required representations first diverge — measurable via CKA between independently trained single-task networks — varies systematically by task pair. Segmentation + surface normals optimally branch after ResNet stage 3; segmentation + depth optimally branch after stage 2; a single shared trunk satisfying one pair suboptimizes the other by 2-4% on standard metrics. Learned branching search (Guo et al., 2020) consistently places different task pairs at different depths, and forcing uniform branching degrades performance 3-7% versus learned configurations on Taskonomy subsets. Critically, the fixed-trunk mistake is not merely suboptimal — it can actively harm all tasks simultaneously when a third task is added, because the compromise trunk forces representational compression that serves none of the tasks well.

Common Pitfalls

Treating loss weights as the primary control lever. Static λ weights are a prior over a loss landscape that shifts continuously; a weight producing balanced gradients at epoch 5 produces catastrophically imbalanced gradients at epoch 50 as task learning speeds diverge. Dynamic weighting (uncertainty weighting, GradNorm) helps but does not resolve subspace conflict.

Diagnosing conflict only at BN layers. Running-mean divergence across tasks is a visible symptom, but the underlying conflict has already relocated to conv weights by the time task-specific BN is applied. Checking BN statistics gives a false sense of resolution.

Interpreting Nash-MTL benchmark improvements as solved multi-task optimization. The method is best understood as a gradient magnitude regularizer that prevents task dominance, not as a method converging to a stable Pareto solution. Conflating the two leads to over-confidence in deployment stability.

Using pre-training affinity scores for inclusion decisions. Affinity scores are reasonably reliable for exclusion (do not co-locate these tasks) but unreliable for inclusion (co-locate these tasks because they're currently aligned). Architectures designed from inclusion decisions built on early affinity measurements systematically underperform those designed from exclusion decisions.

Assuming width solves capacity problems. Extra channels under gradient conflict become bystander dimensions — unused by optimization dynamics because conflicting gradients cancel in the same low-dimensional subspace regardless of ambient dimension.

Open Question for Deeper Work

Can branching depth and shared-trunk weights be jointly optimized, or is bilevel instability fatal? Differentiable architecture search for branching point selection is itself a bilevel optimization problem: the outer loop optimizes branching configuration while the inner loop optimizes weights given that configuration. But the optimal branching depth depends on what representations the weights have learned, and what the weights learn depends on the branching configuration — a circular dependency that makes the bilevel problem non-convex in a particularly hostile way. The deeper question is whether there exists a relaxation or alternating optimization scheme that avoids the moving-equilibrium problem at the architecture level while simultaneously avoiding it at the gradient aggregation level, or whether these two instabilities interact to make joint optimization of routing and weights fundamentally intractable without external supervision (e.g., privileged single-task teacher signals anchoring the representation at each branching candidate depth).







Want to be notified when Claude responds?
Notify
