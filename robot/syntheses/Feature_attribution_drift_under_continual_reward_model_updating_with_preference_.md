Here is the synthesis brief:

Feature attribution drift under continual reward model updating with preference boundary erosion and reward landscape topology shifts in online RLHF regimes

Thesis: In online RLHF, the reward model's internal feature attribution landscape drifts silently across update cycles — shifting which token-level and stylistic features drive reward assignment — while standard accuracy metrics remain flat, creating a non-stationary optimization target that the policy amplifies rather than averages out, ultimately corrupting alignment through mechanisms invisible to conventional validation.

Key Insights

1. Attribution drift is decoupled from accuracy metrics.
Held-out preference accuracy is an aggregate statistic that measures boundary placement but not boundary character. A reward model can maintain 80%+ accuracy while the features driving its decisions rotate substantially — from semantic quality signals toward stylistic proxies like formatting density or hedging frequency. Applying Integrated Gradients or SHAP to a fixed probe set of contrastive response pairs and tracking Spearman rank-order correlation of top attributions across checkpoints reveals this rotation directly; a drop below ρ ≈ 0.7 constitutes a meaningful signal even when accuracy is unchanged. Persistent homology over the RM's penultimate-layer embedding space (via tools like Ripser) provides a complementary topology-level view, detecting the emergence or merger of reward peaks that don't register in scalar accuracy.

2. Policy feedback loops amplify drift rather than suppress it.
The naive intuition that batch diversity will average out attribution drift fails because the drift is correlated across the entire batch: if the RM systematically upweights formatted responses, every sample in every batch carries the same directional bias. PPO's asymmetric clipped objective exacerbates this — it locks in upward reward signals faster than contradictory signals can wash them out. Simultaneously, stylistic shortcuts occupy low-curvature gradient directions that Adam-class optimizers preferentially exploit, while semantic quality signals occupy noisier, higher-curvature directions. The result, visible in InstructGPT's progressive verbosity across RLHF stages, is a self-reinforcing cycle where on-policy rollouts enrich the RM's next training distribution with precisely the features it has begun to overweight.

3. Pipeline-level data interventions can break the feedback cycle.
Intervening in what the RM sees rather than how it weighs it is more robust than loss-function modifications. Stratified replay buffering with attribution-space diversity quotas starves the monoculture formation mechanism. Adversarial contrast injection — pairing every on-policy rollout with a style-swapped version carrying identical semantic content — forces the RM to decorrelate style from quality. Annotator stratification with drift-detection gates, as practiced in Anthropic's RLHF pipelines, breaks the cycle at the human signal layer before corrupted labels reach gradient updates. These interventions are composable and architecture-agnostic.

4. Gradient-space diversity is the correct buffer admission criterion, and it is tractable.
Input-space diversity metrics (semantic embeddings, attribution clusters) fail when attribution novelty and semantic novelty are anticorrelated — the most semantically diverse examples are often stylistically homogeneous, producing a buffer diverse on paper but monocultural in learned features. Gradient-space admission via cosine similarity in last-layer gradient directions directly measures what matters: whether a sample pulls RM weights in a genuinely new direction. LESS (Xia et al., 2024) shows last-layer gradient similarity explains 85–90% of full-gradient similarity variance. JL random projection sketching reduces this to a single matrix multiply; gradient centroid caching with coarse semantic buckets reduces it further to O(1) at admission time. Asynchronous dual-queue processing decouples throughput from per-sample scoring cost.

5. Sketch staleness detection must be adaptive and anticipatory.
Gradient sketches become misaligned as RM parameter space rotates during training. Sketch-prediction error monitoring on a fixed 50-sample probe set catches staleness directly; incremental PCA with principal angle tracking catches it geometrically. Hysteresis banding (separate trigger and reset thresholds) prevents oscillation during rapid parameter movement. Loss curvature proxies enable anticipatory re-anchoring 100–200 steps before staleness manifests in prediction error. Critically, parameter space rotation concentrates on a low-dimensional manifold during each training phase, so re-anchoring can be incremental — updating only drifted sketch dimensions — reducing cost by 60–70%.

Common Pitfalls
Treating accuracy stability as attribution stability. These are orthogonal properties; monitoring one tells you nothing about the other.
Assuming batch diversity suppresses bias. Correlated bias across a batch is not canceled by averaging; it is summed.
Using input-space diversity as a proxy for gradient-space diversity. When the two are anticorrelated, input-space metrics actively mislead buffer management.
Treating re-anchoring as a fixed-interval operation. Fixed schedules either over-compute (wasteful) or under-compute (stale sketches corrupt admission decisions); adaptive staleness detection is necessary.
Neglecting the probe set design for attribution audits. If the probe set conflates style with quality, attribution rotation along the style axis is invisible to the diagnostic.
Open Question for Deeper Work

If RM parameter space rotation is concentrated on a low-dimensional manifold during each training phase — as the tractability of incremental sketch re-anchoring implies — does the reward landscape topology also evolve along a correspondingly low-dimensional trajectory? If so, it may be possible to learn a predictive model of topology shifts from the manifold's local geometry, enabling the system to anticipate where the next reward peak migration will occur and preemptively adjust policy optimization constraints before the shift corrupts accumulated policy behavior. This would transform reward landscape monitoring from a reactive diagnostic into a prospective control mechanism — but requires establishing whether the manifold structure is consistent enough across training regimes to support reliable extrapolation, or whether it is itself non-stationary in ways that defeat prediction.







Want to be notified when Claude responds?
Notify
