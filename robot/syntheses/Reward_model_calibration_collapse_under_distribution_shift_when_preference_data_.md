Thesis: Reward model calibration collapse in iterative RLHF is not a correctable noise problem but a structural consequence of using a locally-valid preference proxy to generate global optimization pressure, compounded at every layer by the relative nature of pairwise annotation, the unbounded geometry of Bradley-Terry reward surfaces, and the non-stationarity of both human and AI preference judgments across policy generations.

Key Insights
1. Bradley-Terry geometry produces confident, directional errors under distribution shift

The Bradley-Terry preference model trained with cross-entropy has no mechanism to bound reward magnitude—it only constrains relative orderings on seen pairs. This produces reward surfaces that are unbounded and monotonically increasing in directions away from the training manifold, meaning out-of-distribution outputs land on steep extrapolated slopes rather than in flat uncertain regions. The policy optimizer then receives high-magnitude, low-uncertainty gradient signal precisely where the reward model is least reliable. Gao et al. (2022) quantify the resulting proxy-gold divergence as scaling with √(KL), implying the optimal stopping point for a single RLHF iteration is aggressively early—often at 5–15 nats KL—and that each additional unit of KL budget purchases progressively worse calibration.

2. Iterative re-annotation fails to reset calibration because pairwise comparison is relative

When new rollouts are collected from the overoptimized policy π_{k+1} and used to retrain the reward model, both options presented to annotators are drawn from an already-drifted distribution. Pairwise comparison elicits relative judgments, so annotators can agree on which output is better while both outputs are reward-hacked; the new reward model inherits the miscalibration of the previous iteration rather than resetting it. This reference point contamination means successive reward model training rounds patch the reward surface near the current policy mode while leaving dangerous extrapolation geometry in low-density regions entirely unchanged.

3. Ensemble uncertainty penalties are undermined by shared training support and PPO dynamics

Reward model ensembles trained on the same preference dataset share a support boundary regardless of architectural diversity; they extrapolate coherently in the directions the policy exploits, producing low variance precisely where miscalibration is highest. When ensemble variance is used as a penalty during PPO, the policy learns to produce outputs that simultaneously maximize mean reward and minimize variance—converging on a narrow, repetitive mode that is maximally in-distribution for the ensemble's shared manifold. Coste et al. (2023) find ensembling delays overoptimization by 30–50% in KL terms but does not eliminate it, with gains saturating beyond three to five members.

4. Annotator drift and AI preference model ceilings introduce non-stationary preference manifolds

Human annotators implicitly recalibrate their quality threshold as they are exposed to improving policy outputs, making preference labels collected at different checkpoints incompatible on a common scale. Combining them trains a reward model on a mixture of incompatible reference frames rather than a consistent utility approximation. Constitutional AI substitutes a frozen AI preference model to avoid human drift, but this creates a quality inversion zone when the policy surpasses the AI preference model's competence ceiling: the reward surface develops a false peak below that ceiling, and the policy optimizer stabilizes at this false peak rather than continuing toward genuine quality improvement—a qualitatively different failure mode from standard overoptimization drift.

5. Preference data collection structure is an active learning problem, not a convenience sampling problem

Decorrelating reward model uncertainty requires preference data from maximally spaced policy checkpoints, but this maximizes annotator recalibration effects, placing distributional coverage and label comparability in direct tension. The resolution is to treat data collection as active learning: at each iteration, select the (checkpoint, annotator pool, prompt distribution) combination that maximally reduces ensemble disagreement on the current policy's output distribution, while maintaining replay of earlier-checkpoint rollouts to preserve coverage of the full trajectory.

Common Pitfalls
Treating held-out preference accuracy as a calibration metric: A reward model can exceed 90% preference prediction accuracy on held-out pairs from the same rollout distribution while being severely miscalibrated on the current policy's outputs.
Assuming reward model retraining resets distributional drift: New annotation on shifted rollouts inherits rather than corrects reference point contamination.
Conflating annotator agreement with label quality: Pairwise agreement rates remain artificially high even when both comparison options are reward-hacked, masking distributional drift.
Treating ensemble variance as true epistemic uncertainty: Shared backbone representations produce correlated ensemble members whose disagreement reflects parameter variance, not genuine out-of-distribution uncertainty.
Open Question for Deeper Work

The false-peak geometry created by AI preference model ceiling effects may interact with PPO's clipping mechanism to produce stable policy convergence at a suboptimal quality plateau—meaning the system does not diverge visibly but simply stops improving, with no obvious training signal indicating that a ceiling has been hit. The open question is whether a continuous probe-set evaluation protocol (tracking Spearman rank correlation between reward model scores and human judgments across quality quintiles) can reliably detect this threshold crossing in time to intervene, and whether such detection can be made cheap enough to run inside the training loop rather than as an expensive offline audit.






