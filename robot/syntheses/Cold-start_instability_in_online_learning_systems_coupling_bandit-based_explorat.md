Thesis: Cold-start instability in coupled bandit-representation systems is not a data-sparsity problem but a feedback loop problem — bad representations generate uninformative exploration, which produces corrupted reward signal, which produces worse representations — and every practical mitigation trades one failure mode for another, making the architecture of the tradeoff the central engineering decision.

Key Insights
1. The coupling is the problem, not the components individually

A bandit alone and a deep network alone each have well-understood cold-start behaviors. The instability emerges specifically from their coupling: the bandit's uncertainty estimates depend on the quality of the embedding space, but that space is shaped by rewards the bandit's own (poor, early) policy generates. When the embedding updates, previously computed context vectors stored in the bandit's memory become stale, producing structured misestimation — confidently wrong uncertainty rather than appropriately wide uncertainty. This index poisoning problem is the core failure mode that beginner treatments of cold-start miss entirely.

2. Reward delay and representation drift interact multiplicatively

When conversion rewards arrive 24–48 hours after the action, the embedding that generated the original context vector has already drifted through gradient updates. The arriving reward gets attributed to the wrong embedding version, creating apparent noise that the bandit interprets as arm inconsistency and responds to with unnecessary re-exploration. The principled fix — aligning checkpoint commits to the leading edge of the reward delay distribution — directly conflicts with the need to respond to rapid non-stationarity, creating a fundamental cadence tension that cannot be resolved without a secondary, lower-latency proxy signal layer.

3. Proxy signals enable fast response but introduce correlated failure

Using proxy signals (clicks, dwell time) to trigger emergency embedding updates solves the cadence tension but introduces a new failure mode: proxy-reward correlation breaks down precisely during the high-salience events (viral trends, flash sales, atypical traffic surges) that are most likely to trigger emergency updates. The detection infrastructure — covariance monitors, rank inversion checks, guardrail metrics — all require calibrated historical baselines, which are unavailable during cold-start, making the safeguard architecture circular at system launch.

4. Warm-start priors are necessary but introduce miscalibration risk

No self-referential system can bootstrap its own detection thresholds from zero; every production system imports prior knowledge via transfer learning, shadow deployment, or synthetic feedback injection. The risk is that an imported prior that is subtly wrong for the new context produces arm diversity collapse within the first few hundred impressions — the bandit becomes confidently wrong rather than broadly uncertain. The earliest detectable signature is posterior variance compressing anomalously fast relative to the volume of observed data, detectable as cluster-level rank inversion around impression 200–500.

5. Remediation phases require gradient gating but reintroduce static representation risk

During uncertainty re-injection (the response to detected miscalibration), embedding gradient updates should be gated by example provenance or reweighted by inverse propensity scores to prevent artificially forced exploration from corrupting the training signal. However, extended gradient suppression starves the embedding of learning signal and recreates a variant of the representation-freezing failure mode. The exit criterion for re-injection must be tied to the restoration of arm diversity entropy, not elapsed time, to avoid indefinite stagnation.

Common Pitfalls
Treating cold-start as a volume problem: Collecting more data does not break the degeneracy spiral if the exploration policy generating that data is already miscalibrated.
Ignoring embedding versioning at reward join time: Failing to log snapshot IDs at serving time makes delayed reward attribution structurally incorrect and indistinguishable from genuine reward noise.
Setting guardrail thresholds from population averages: Proxy-reward decorrelation appears first in specific user segments and is masked in aggregates until propagation is advanced.
Conflating normal cold-start variance with active prior miscalibration: The two require opposite responses — patience versus immediate uncertainty re-injection — and the cost of conflating them compounds through the representation update cycle.
Treating re-injection as a bounded perturbation: Severe miscalibration can trigger successive re-injection rounds, causing cumulative gradient suppression that the system has no natural exit from without an explicit entropy-restoration criterion.
Open Question for Deeper Work

Production systems universally decouple bandit policy updates from embedding gradient updates, managing their interaction through gating, versioning, and reweighting mechanisms. The open question is whether a joint optimization of exploration policy and representation — where the embedding's training objective explicitly accounts for the bandit's current uncertainty state, and the bandit's exploration bonus is a function of representation stability rather than just posterior variance — would eliminate the sequential coupling failures described above, or whether the resulting optimization landscape is sufficiently non-convex and non-stationary that joint training is unstable in ways that make the decoupled architecture, with all its patchwork mitigations, the practical optimum by default. Formulating the conditions under which joint optimization converges during cold-start on a non-stationary reward surface remains largely an open research problem.






