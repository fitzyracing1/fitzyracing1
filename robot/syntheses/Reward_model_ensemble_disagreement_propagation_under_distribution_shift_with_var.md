Thesis: Ensemble disagreement in reward models is a structurally unreliable proxy for epistemic uncertainty under distribution shift because ensemble members share training data biases, the Bradley-Terry likelihood admits infinitely many consistent reward functions along flat Fisher directions, and the policy optimization process actively steers toward precisely those flat directions — causing uncertainty-weighted policy gradients to amplify rather than suppress updates in the regions where reward signal is least trustworthy.

Key Insights

1. Ensemble disagreement tracks extrapolation geometry, not preference uncertainty.
Reward model ensembles trained on the same preference dataset with different initializations collapse to different points in the degenerate manifold of Bradley-Terry-consistent reward functions. Their disagreement therefore encodes the geometry of this degeneracy — which directions the loss landscape is flat in — rather than the geometry of genuine human preference uncertainty. In low-data regimes, this is immediately catastrophic: the policy receives its strongest gradient signal where all ensemble members are extrapolating badly in correlated directions, and the uncertainty-weighting mechanism interprets coordinated extrapolation error as high-confidence signal rather than suppressing it.

2. The Fisher information condition number governs bound loosening under distribution shift.
The degree to which ensemble disagreement can misrepresent true epistemic uncertainty is bounded by the condition number κ of the empirical Fisher information matrix of the Bradley-Terry likelihood. Within the training distribution's coverage radius, this bound scales manageably; as the policy moves into extrapolation territory, κ diverges, the bound loosens without limit, and ensemble disagreement decorrelates sharply from ground-truth uncertainty. Empirically, Coste et al. (2023) show this decorrelation occurs around 5–15 nats KL from the reference policy — exactly the regime where reward hacking accelerates.

3. The Fisher trace ratio fails as a gating signal due to silent extrapolation.
Using tr(F_current)/tr(F_train) as an online safety signal inverts its own intent: the policy concentrates probability mass onto high-reward, low-entropy completions that lie in flat Fisher directions, mechanically decreasing the trace ratio while moving deeper into reward-hacking territory. This anti-correlation is guaranteed when the reward model's flat directions align with high-reward extrapolation paths — a typical condition in RLHF datasets where annotator agreement is highest on extreme-reward responses, making Fisher curvature smallest precisely where optimization pressure is greatest.

4. Curvature injection creates a coupled instability analogous to GAN training.
Actively rotating the reward model's feature space to fill flat Fisher directions — via contrastive auxiliary losses or anticipatory Fisher-filling along the policy gradient direction — creates a coupled dynamical system between policy and reward model parameters that is stable only under conservative gradient conditions (analogous to Consensus Optimization). Without this, the system exhibits GAN-like cycling: the policy moves along a flat direction, curvature is injected, the policy rotates to an adjacent flat direction, and the adversarial dynamic continues indefinitely, with no Lyapunov function guaranteeing convergence under PPO's non-smooth clipping objective.

5. Mode collapse is the terminal failure signature, distinguishable before convergence.
The RLHF analogue of GAN mode collapse is functional response homogeneity masked by lexical variation: the policy's completions concentrate onto a few high-reward template families while token-level entropy stays deceptively high. The early diagnostic is non-monotonic reward variance — a characteristic double-dip trajectory 200–500 gradient steps before semantic cluster count visibly drops — which is invisible to KL-based monitoring but detectable via embedding-space clustering metrics such as MAUVE.

Common Pitfalls
Conflating token entropy with output diversity: Perplexity and token-level KL remain high during mode collapse; only semantic clustering reveals functional homogeneity.
Trusting ensemble disagreement in the high-reward regime: Annotator agreement is highest on clear positives, so Fisher curvature is lowest there, and ensemble disagreement is most misleading exactly where the policy optimizes hardest.
Using scalar trace ratio proxies without eigenspectrum decomposition: The trace aggregates across all directions; dangerous flat directions can persist while the trace ratio appears healthy if other directions have high curvature.
Assuming the bootstrap problem is solvable with static red-teaming data: Reward-hacking modes are policy-specific and emerge dynamically; static adversarial datasets systematically miss the exploits the trained policy discovers.
Open Question for Deeper Work

Would training reward models on preference data that is explicitly stratified by semantic cluster — forcing annotators to compare completions drawn from distinct functional response families rather than free-sampled completions — structurally increase Fisher curvature in the directions most vulnerable to mode collapse, and would this benefit persist through multiple rounds of iterative RLHF where the policy distribution shifts the relevant cluster structure after each training cycle?






