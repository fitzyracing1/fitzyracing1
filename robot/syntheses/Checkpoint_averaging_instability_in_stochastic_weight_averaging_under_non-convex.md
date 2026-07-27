Thesis: SWA's geometric promise — that averaging late-phase SGD checkpoints finds a flatter, better-generalizing basin center — rests on assumptions about loss surface homogeneity and basin alignment that systematically fail under architectural constraints, training dynamics, distribution shift, and fine-tuning regimes, producing averaged solutions that are not merely suboptimal but structurally mislocated in weight space.

Key Insights

1. Basin alignment is a precondition, not a guarantee.
Linear mode connectivity analysis is the canonical test for whether checkpoints can be safely averaged: interpolating between two checkpoints and measuring the midpoint loss barrier distinguishes basin-aligned pairs (barrier <0.1 nats) from separated pairs (barriers of 1–3 nats). Critically, permutation symmetry can make barriers appear artificially large — Entezari et al. (2022) showed that neuron permutation realignment collapses many apparent separations — but this rescue fails in residual networks, where skip connections constrain admissible permutations, and in transformers, where residual stream geometry prevents head-level alignment from closing the barrier. When alignment fails after symmetry correction, the averaged weights provably land in a high-loss inter-basin valley.

2. Interpolation path curvature introduces systematic bias even within a single basin.
Even when checkpoints share a basin, anisotropic loss surface curvature means that arithmetic averaging in parameter space conflates directions that should be averaged with directions where checkpoint spread reflects genuine curvature. High-curvature directions pull the averaged solution toward the basin wall rather than the basin center, producing a solution that is biased in precisely the dimensions where the loss surface penalizes deviation most severely. This is not detectable from individual checkpoint loss values alone.

3. Online SWA during SAM training improves basin alignment but introduces a geometric inconsistency.
Running SWA concurrently with SAM (as in SWAD) reduces inter-checkpoint basin drift by making the running mean a gravitational attractor for subsequent iterates. However, SAM's perturbation is computed at instantaneous weights rather than the SWA mean, so it explores curvature around a point that is not the final output solution. The SWA mean's oscillation-cancellation artificially suppresses curvature estimates, and anchoring SAM's ascent step to the mean introduces gradient staleness and a Pareto conflict between SAM's minimax objective and SWA's centroid objective.

4. SWAG's low-rank variance approximation leaves bulk Hessian curvature undetected.
Using checkpoint ensemble variance as a curvature proxy — as in SWAG's rank-20 approximation — captures outlier Hessian eigenvalues but misses the dense bulk spectrum documented by Ghorbani et al. (2019), which collectively accounts for substantial total curvature in the complement space. This bulk becomes active under distribution shift, where the loss surface reorients into previously unsampled directions, causing SWAG's uncertainty estimates and any variance-corrected SAM perturbations to systematically underestimate sharpness precisely where it matters most.

5. Fine-tuning SWA inherits and amplifies complement-space risk from pretraining.
Fine-tuning trajectories occupy an intrinsically low-dimensional subspace (fewer than 200 directions for BERT-scale models), leaving the vast complement unsampled. Pretrained weights carry frozen curvature structure in this complement — directions that were sharp during pretraining remain sharp in the Hessian even though fine-tuning SGD never visits them. SWA during fine-tuning therefore produces averaged weights whose flatness is certified only along the narrow fine-tuning subspace, with inherited pretraining curvature fully intact in the orthogonal complement, degrading OOD robustness by 1–2+ F1 points compared to single-checkpoint fine-tuning (Chronopoulou et al., 2023).

Common Pitfalls
Trusting individual checkpoint loss as a proxy for averageability: two checkpoints with identical low loss can have a high-loss midpoint if they sit in distinct basins.
Assuming permutation alignment solves basin separation: it reduces but does not eliminate barriers in residual and attention architectures.
Treating SWA flatness metrics as distribution-shift robust: flatness along the SGD trajectory does not imply flatness in directions activated by covariate shift.
Conflating low checkpoint variance with flat complement space: low variance in the complement reflects underexploration, not genuine flatness.
Open Question for Deeper Work

Can a trajectory-aware, curvature-stratified averaging scheme — one that weights checkpoints not uniformly or by recency but by their position relative to detected basin boundaries and local Hessian bulk mass — provably outperform standard SWA under distribution shift, and what is the minimum geometric information (LMC probes, variance spectrum, Hessian-vector products) required to implement such a scheme at production scale without prohibitive overhead?






