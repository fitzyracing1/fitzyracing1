Thesis: Effective multi-task learning requires managing gradient conflicts not in loss-magnitude space but in the directional geometry of the parameter manifold, and the failure to account for the non-stationarity, layer-heterogeneity, and distributional bias of that geometry undermines every downstream mechanism—surgery, routing, and dynamic balancing alike.

Key Insights
1. Gradient surgery operates on direction, not magnitude—and projection destroys signal in both directions

Loss-weighting schemes like GradNorm and uncertainty weighting address the wrong quantity: the damage and opportunity in MTL live in the cosine angle between task gradient vectors, not their relative scales. PCGrad's projection onto the orthogonal complement of a conflicting gradient discards not only harmful anti-aligned components but also beneficial aligned components when implementation is careless, stripping shared syntactic or semantic signal that auxiliary tasks were providing for free. The signal lost in projection is most costly when shared parameter subspaces have high intrinsic dimensionality, because no single-task gradient can recover directions that only appear in the joint gradient basis.

2. Task affinity is non-stationary, asymmetric, and non-transitive—making checkpoint-based estimation structurally unreliable

Affinity matrices estimated at discrete checkpoints reflect gradient geometry at a fixed parameter location, but the landscape rotates continuously during training—especially at phase transitions like representation specialization or loss plateau breaks. The resulting lag produces affinity sign inversion, where a task pair estimated as cooperative becomes conflicting before the next affinity update, and surgery configured to preserve their joint gradient component now amplifies interference. The failure is worst during rapid loss descent phases, precisely when accurate affinity information is most critical.

3. Layer-wise conflict heterogeneity means uniform surgery is a category error

Gradient conflict angles are not uniform across depth: early layers typically show low inter-task conflict (below 45 degrees) because they encode broadly shared structure, while upper and middle layers frequently exceed 120 degrees as task-specific representational demands diverge. Applying surgery uniformly destroys beneficial shared signal in early layers while failing to catch the conflict hotspots that migrate across middle layers during training. The correct intervention is depth-conditioned and within-layer selective—attention heads within a single layer can simultaneously show near-zero and near-180-degree conflict angles across different task pairs.

4. The shared-private boundary should be a learned, dynamic parameter—but learned boundaries collapse without the right inductive biases

Fixed architectural split points are misaligned with moving conflict frontiers; the boundary should be a per-layer (or per-parameter-group) gating variable updated on a meta-gradient signal. However, unconstrained routing policies collapse to degenerate solutions: fully private (when task meta-gradients reward interference elimination) or fully shared (when a dominant task overwhelms minority signals). Productive intermediate regimes require task-conditional feature diversity pressure, layer-dependent entropy regularization on gating distributions, and temporal consistency regularization to prevent oscillation—but each stabilization mechanism introduces its own failure mode.

5. The validation signal that drives routing is itself a biased proxy for training gradient geometry

Meta-gradient routing updates depend on validation loss, but validation sets constructed by label-stratified sampling systematically underrepresent high-conflict gradient regimes that dominate training. The routing policy therefore learns configurations optimal for clean, low-conflict validation examples while leaving unresolved the interference that actually matters. Conflict-stratified validation sampling is the principled fix, but constructing such a set requires knowing the training gradient conflict distribution—which the routing policy is simultaneously reshaping, creating a circular dependency.

Common Pitfalls
Treating cosine similarity threshold as a static hyperparameter: conflict angles vary by layer, training phase, and parameter location; a fixed threshold will misfire systematically across training.
Conflating loss improvement with conflict resolution: a task's validation loss can improve while its gradient is being dominated by a higher-magnitude task that happened to push a compatible direction transiently.
Applying temporal consistency regularization with a global coefficient: over-regularization freezes routing in suboptimal configurations; under-regularization causes oscillation that destroys shared representational stability. Layer-dependent coefficients are necessary.
Ignoring affinity asymmetry: assuming that if task A benefits task B then B benefits A leads to surgery policies that protect the wrong gradient direction.
Open Question for Deeper Work

The circular dependency between conflict-stratified validation construction and the routing policy that reshapes the conflict distribution it depends on is unresolved. A productive direction is whether an online, self-supervised conflict geometry estimator—built directly from training batch gradient statistics without any held-out set—can replace the validation meta-signal entirely, decoupling routing from validation composition bias while remaining adaptive to the non-stationary landscape. This would require the estimator to be both sample-efficient enough to update within a training step and robust enough to the high variance of stochastic gradient directions to avoid chasing noise.






