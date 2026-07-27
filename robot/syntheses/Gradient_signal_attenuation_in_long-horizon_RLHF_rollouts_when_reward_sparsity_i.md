Thesis: In long-horizon RLHF, the interaction between sparse terminal reward and PPO's clipped importance weights produces a structured, non-monotonic gradient attenuation profile that systematically undermines credit assignment at mid-sequence positions, and no intervention within the policy gradient framework fully resolves this without trading one pathology for another along the variance-bias-consistency triangle.

Key Insights
1. Clipping attenuation is multiplicative and position-compounding

The per-token importance ratio product ∏π_θ/π_old collapses toward zero for early tokens after even modest policy drift, and PPO's ε-clip mechanism — designed to stabilize training — simultaneously destroys gradient signal for tokens distant from the terminal reward. The effective optimization horizon shrinks endogenously as training progresses: as the policy improves at late tokens, it drifts from π_old, clips harder at early positions, and progressively removes gradient pressure from the upstream generation decisions that determine whether high-reward terminal states are reachable at all.

2. The gradient magnitude profile is non-monotonic, with a mid-sequence dead zone

Contrary to the intuitive assumption of clean exponential decay from terminal to initial positions, the empirical gradient profile exhibits a local minimum near the trajectory midpoint. Mid-sequence tokens accumulate the worst combination of compounded ratio clipping and peak bootstrapping error from the value head — early tokens benefit from stable (if biased) value priors, late tokens receive clean Monte Carlo signal near the reward, but mid-sequence tokens fall into a dead zone where neither mechanism provides reliable gradient direction. This produces a characteristic "hourglass" competence profile: strong opening (from SFT initialization), strong closing (from direct reward optimization), and degraded coherence in the middle third.

3. Joint value-policy training creates a destabilizing feedback loop

When the value head and policy share a backbone and train jointly on sparse terminal reward, their gradients carry contradictory geometric pressure — the policy gradient pushes toward action-discriminating representations while the value loss pushes toward return-predictive ones. At early token positions, policy gradients are near-zero due to clipping attenuation, so the shared backbone is effectively trained only by the value loss during the destabilized phase, imprinting representations optimized for value prediction under a poor policy. This self-reinforcing loop destabilizes early training and only conditionally stabilizes if policy drift remains slow enough for the value head to track the shifting return distribution — a condition frequently violated for rollouts exceeding ~256 tokens.

4. Architectural separation relocates rather than resolves the problem

Separating value and policy networks eliminates backbone interference and produces a more predictable attenuation profile, but the exponential decay slope remains nearly identical to shared architectures during early training because the dominant mechanism — clipped ratio products — is independent of parameter sharing. Separation buys diagnostic clarity and removes representation corruption, but does not extend the effective optimization horizon for early tokens. GRPO's value-free formulation (DeepSeek-R1) confirms this: eliminating the value network widens the attenuation gap at early positions, establishing that the value head's primary contribution is variance reduction via baseline subtraction, not interference elimination.

5. Position-aware corrections face a fundamental safety-recovery tension

A position-indexed ε(t) schedule — widening the trust region at early positions — is theoretically motivated but practically undermined by the fact that advantage estimates are least reliable precisely where the wider clip is applied. Position-aware normalization (dividing by per-position σ_t) makes large steps safe but cancels the gradient magnitude recovery that widening ε was meant to provide. The step direction problem at early positions is ultimately downstream of credit assignment failure, not normalization choice, meaning no within-PPO correction fully resolves the issue without first solving the upstream problem it was designed to address.

Common Pitfalls
Treating attenuation as monotonic: Assuming gradient magnitude decays cleanly from t=T to t=0 misses the mid-sequence dead zone and leads to interventions (e.g., reward shaping at endpoints only) that leave the most structurally damaged positions untouched.
Conflating architectural separation with problem resolution: Practitioners who switch to separate actor-critic networks and observe stability improvements often attribute this to gradient flow improvement when the actual gain is interference elimination — a meaningfully different diagnosis with different downstream implications.
Mistaking value loss convergence for bootstrapping reliability: Decreasing value loss during training does not imply accurate bootstrapping targets at early positions; it can reflect the value head accurately tracking a suboptimal policy's returns while providing systematically biased TD targets for policy improvement.
Open Question for Deeper Work

Does the mid-sequence bootstrapping dead zone suggest that rollout segmentation — splitting trajectories into overlapping sub-episodes with position-specific reward signals derived from a process reward model — could specifically target the hourglass failure mode without disrupting endpoint gradient flow? The key unresolved issue is whether overlapping sub-episode boundaries introduce new importance weight discontinuities that recreate the attenuation problem at segment transitions, or whether sufficiently dense segmentation effectively converts the sparse terminal reward problem into a dense reward problem with all the credit assignment properties that entails — and whether any PRM trained on outcome data can provide genuinely independent intermediate signal rather than merely redistributing terminal reward topology across positions.






