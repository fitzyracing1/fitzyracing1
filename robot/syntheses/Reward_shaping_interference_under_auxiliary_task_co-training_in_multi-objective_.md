Thesis: Auxiliary task co-training in multi-objective RL does not merely add noise to the primary policy gradient — it introduces systematic directional bias through implicit non-potential-based reward shaping, non-stationary effective scalarization, and mixing-time-sensitive gradient conflict dynamics that collectively prevent convergence to any true Pareto-stationary point and produce Pareto front instability that is structurally undetectable by standard reward curve monitoring.

Key Insights
1. Auxiliary rewards implicitly violate potential-based shaping conditions

Ng et al. (1999) established that only potential-based reward shaping preserves optimal policy invariance. Auxiliary task rewards almost never satisfy this condition globally — they may appear locally consistent with the primary objective's reward landscape but introduce path-dependent inconsistencies across the full state space. The result is that the policy gradient descends a composite surface whose fixed points do not correspond to optima of the primary objective, and because the violation is global rather than local, it cannot be corrected by re-weighting or annealing the auxiliary reward coefficient alone.

2. Linear scalarization structurally excludes non-convex Pareto front regions

Das & Dennis (1997) proved that weighted-sum scalarization can only recover solutions on the convex hull of the Pareto front. Since neural policy classes generically produce non-convex achievable sets, entire concave front segments are unreachable regardless of weight tuning. This means auxiliary task interference cannot be diagnosed by checking Pareto dominance alone — a corrupted policy can be locally non-dominated while sitting far from the true front in a region that linear methods cannot probe, making standard evaluation metrics blind to the interference.

3. Gradient projection methods introduce parameter-dependent scalarization bias

PCGrad and related gradient surgery methods eliminate destructive interference by projecting conflicting gradients, but the projection weights become implicit functions of the current policy parameters. This violates the stationarity conditions established by Désidéri (2012) for MGDA convergence: the policy gradient estimator is no longer unbiased for any fixed multi-objective target, and the optimizer converges to a limit cycle around the Pareto front rather than to a Pareto-stationary point. The untracked Jacobian term 
(
∇
𝜃
𝑤
)
⊤
𝑅
(∇
θ
	​

w)
⊤
R is the mathematical source of this bias and is of the same order as the primary gradient in high-conflict regimes.

4. Gradient angle volatility temporal structure determines front coverage quality

Auxiliary task gradient conflict is functionally equivalent to a Pareto front exploration mechanism, but its effectiveness depends critically on temporal autocorrelation. Bursty conflict — large displacement events separated by low-conflict drift — is theoretically superior to sustained conflict for escaping low-curvature Pareto front attractors, analogous to Lévy-stable noise outperforming Gaussian noise for basin escape (Simsekli et al., 2019). However, bursty conflict only produces useful front displacement when burst duration exceeds the gradient estimator's mixing time 
𝜏
≈
𝐵
/
(
1
−
𝛾
)
τ≈B/(1−γ); subthreshold bursts register as pure noise and destabilize the value baseline without moving the policy.

5. The mixing time threshold is non-stationary and grows during training

Adaptive gradient gating — suppressing auxiliary gradients during subthreshold conflict bursts — is implementable with EMA-based cosine similarity tracking, but the mixing time threshold itself grows as training progresses due to improving policy correlations and lengthening effective discount horizons. This creates a progressive permissiveness requirement: gating must become less restrictive over time to avoid suppressing increasingly many beneficial bursts. This directly conflicts with standard curriculum intuitions that auxiliary tasks should be down-weighted as the primary task matures, suggesting the two scheduling logics are fundamentally incompatible without explicit mixing-time-aware calibration.

Common Pitfalls
Misattributing limit cycles to reward conflict: Oscillation near the Pareto front is routinely blamed on task reward incompatibility when the true cause is optimizer-induced scalarization non-stationarity.
Using dominance checks as interference detectors: A policy can be locally non-dominated and still be far from the true Pareto front; hypervolume tracking across diverse weight vectors is necessary.
Treating gradient angle volatility as uniformly harmful: High-variance auxiliary gradients may carry high-information signals pointing toward high-curvature front regions; magnitude-based clipping destroys exactly these updates.
Fixed gating thresholds: Mixing time grows during training; a gate calibrated at initialization systematically suppresses beneficial bursts late in training.
Open Question for Deeper Work

Does the temporal autocorrelation structure of auxiliary task gradient conflict leave a detectable fingerprint in the curvature profile of the recovered Pareto front — specifically, is there a measurable mapping from burst duration distribution parameters to the hypervolume deficit in concave front regions — and if so, could that mapping be inverted to design auxiliary task schedules that target specific under-explored front segments by engineering conflict burst statistics rather than reward function shapes?






