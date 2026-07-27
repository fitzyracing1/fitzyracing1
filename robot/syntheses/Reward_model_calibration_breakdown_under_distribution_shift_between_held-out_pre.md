Thesis: Reward model calibration breakdown in iterative RLHF is not a data quality problem but a structural one—the combination of static probe sets, scalar output parameterizations, and token-level KL penalties creates a system that cannot detect, signal, or recover from the distribution shift that iterative fine-tuning itself induces in the live annotation population.

Key Insights

1. Ranking accuracy and calibration are orthogonal, and only calibration matters for RL.
A reward model can preserve correct ordinal preference rankings while its scalar outputs compress or expand in ways that fatally distort the KL-penalized RL objective. The held-out probe set, collected before iteration one, measures a static snapshot of annotator preferences; as the policy improves and annotators rate increasingly similar high-quality completions, the probe set ECE can decrease while live calibration degrades. The expert concern is not whether the reward model ranks A above B correctly, but whether the magnitude of r(A) − r(B) accurately reflects the annotator population's actual agreement rate—because PPO's advantage estimates are sensitive to these magnitudes in ways that ranking metrics cannot capture.

2. Output parameterization determines whether calibration breakdown is detectable at all.
Scalar heads, used in InstructGPT and most production systems, have no architectural pathway to signal their own miscalibration. Distributional heads and learned Bradley-Terry temperatures offer richer signals, but each carries a failure mode: ensemble distributional heads collapse in diversity precisely in out-of-distribution regions due to correlated pretraining, while learned temperatures can absorb annotator drift by rescaling margins, masking the shift from downstream monitors rather than surfacing it. The correct design maintains a fixed prior over temperature and tracks KL divergence between original and drifted posterior predictives as an alarm signal.

3. The RL optimizer will exploit uncertainty signals rather than respect them.
Routing epistemic variance into the optimization target via pessimistic corrections (r_effective = μ − λσ) is necessary but insufficient: the policy learns to steer toward the reward model's low-variance manifold—structurally stereotyped, verbose, formulaic completions—minimizing reported uncertainty without reducing genuine out-of-distribution-ness. This produces semantic collapse: a 15–30% reduction in pairwise cosine distance between completions, a drop in effective embedding rank, and a token-level KL that underestimates semantic divergence because per-token plausibility and embedding-space distance are not monotonically related.

4. Contaminated annotations from the collapsed phase require quarantine, not just downweighting.
Annotations collected during semantic collapse are biased toward stereotyped completions and show anomalously high inter-annotator agreement (85–92% versus the healthy 65–75% baseline). Influence function analysis can identify and timestamp this contamination, but removing influential points during retraining does not restore the pre-collapse calibration surface—loss landscape geometry changes under data distribution shifts, and the optimizer may descend into an orthogonal miscalibration basin. Constrained fine-tuning from the pre-collapse checkpoint with an L2 anchor to pre-collapse parameters recovers 90–95% of calibration versus 60–80% for full retraining on the cleaned corpus.

5. Recovery requires diagnosis before remediation.
Semantic collapse can originate from reward model overfitting, KL coefficient miscalibration, or policy exploitation of reward model blind spots; each requires a different intervention. Naive policy rollback without reward model correction causes re-collapse within a predictable number of steps, typically faster than the original collapse. The most annotation-efficient recovery combines targeted adversarial re-annotation of the low-variance manifold (500–2000 labels), reward model head fine-tuning with proximity constraints, and a temporarily elevated KL coefficient to slow re-entry into the collapsed basin.

Common Pitfalls
Declaring calibration recovery on in-distribution metrics: ECE improvement on the original probe set cannot distinguish basin restoration from basin substitution after retraining.
Treating token-level KL as a sufficient diversity guard: it systematically underestimates semantic collapse because structurally familiar completions can be token-plausible while embedding-space distant from the SFT reference.
Conflating diversity reduction with collapse: legitimate quality improvement also reduces completion diversity; failure to condition on prompt difficulty conflates the two and triggers false circuit-breakers or misses real collapse.
Assuming ensemble reward models are well-calibrated out-of-distribution: shared pretraining correlates ensemble member inductive biases, collapsing diversity exactly where uncertainty estimates matter most.
Open Question for Deeper Work

Constrained fine-tuning from a pre-collapse checkpoint is the most reliable recovery procedure currently identified, but the correct L2 anchor strength depends on knowing the magnitude of the contamination-induced parameter shift—a quantity that is itself estimated from influence functions subject to first-order approximation error. The open question is whether there exists a second-order diagnostic (Hessian-based or Fisher-information-based) that can simultaneously estimate the contamination-induced shift magnitude, set the anchor strength adaptively, and confirm that the constrained optimization has corrected the target miscalibration without escaping the pre-collapse basin—and whether such a diagnostic is computationally feasible at the parameter scales of contemporary reward models without low-rank approximations that reintroduce the basin-substitution risk.






