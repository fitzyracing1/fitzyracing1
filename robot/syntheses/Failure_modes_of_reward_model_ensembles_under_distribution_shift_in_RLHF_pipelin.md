Thesis: Reward model ensembles in RLHF pipelines do not solve the alignment problem under distribution shift — they launder it, converting visible single-model failure into invisible correlated bias that is harder to detect, harder to attribute, and harder to correct, especially when the annotator population is heterogeneous and underrepresented subpopulations lack the statistical footprint to produce stable reward signal.

Key Insights

1. Ensemble agreement is not a reliable signal of distributional coverage.
High agreement among ensemble members indicates convergence on a learned reward surface, not proximity to the training distribution. When all models share the same annotator-population biases, they will agree confidently on exactly the inputs where their shared blind spots produce systematically wrong reward estimates. The dangerous failure regime is not ensemble disagreement — which is at least legible — but ensemble consensus on out-of-distribution or underrepresented inputs, where the models jointly extrapolate in the same wrong direction.

2. Annotator disagreement is structured signal, not noise, and scalar reward formulations cannot represent it.
Bradley-Terry reward models assume a single latent quality axis with annotators as noisy observers. When two annotators disagree because they hold genuinely different values — not because one made an error — collapsing their judgments to a scalar mean produces an estimate that represents nobody's preferences accurately. The optimizer then finds policies that maximize this phantom quantity, producing demographic homogenization: majority-annotator preferences are amplified, minority preferences are erased, and the reward surface encodes a social choice that was never explicitly made.

3. The KL penalty in PPO can actively preserve annotator-population bias.
The KL term anchors the policy to the SFT reference model to prevent reward hacking. But in high-annotator-disagreement regions — which are often the most frequent deployment prompt types — the reward signal is low-SNR and the KL penalty's cost exceeds the noisy reward gradient. The policy cannot escape toward minority-preferred outputs because they are low-probability under the SFT reference, making the KL term a mathematical formalization of majority-preference conservatism in exactly the domains where alignment is most contested.

4. Deferring aggregation to a Pareto frontier relocates, rather than resolves, the representation problem.
Maintaining a frontier of policies appears to preserve value pluralism, but introduces compounding failure modes: selection mechanism capture (the router is itself biased), default effect collapse (most users never deviate from defaults), and frontier coverage gaps (subpopulations too small to produce stable reward estimates are simply absent from the frontier). The representation problem is recursive — it reappears at every level of the architecture that involves learned aggregation.

5. Achieving statistical power for minority subpopulation reward functions is economically prohibitive under current annotation infrastructure.
Detecting a moderate preference effect (δ≈0.3) at 80% power requires roughly 200-400 comparison pairs per subpopulation per prompt domain. Across realistic pipeline scales, this implies annotation costs of $60,000-$600,000 for even minimal minority representation — and annotation platforms themselves are demographically concentrated, making supply inelastic for the most underrepresented groups. The cost curve scales superlinearly with the degree of representation gap being closed.

Common Pitfalls
Treating ensemble variance as an OOD detector without recognizing it measures output-space disagreement, not input-space coverage distance.
Averaging divergent subpopulation reward functions under the assumption this is a neutral compromise, when it is a value judgment that produces outputs suboptimal for everyone.
Holding out prompts rather than annotators during cross-validation, which systematically underestimates generalization error on subpopulation-specific inputs.
Retaining no annotator metadata in production pipelines, making post-hoc stratification and spurious consensus detection impossible — a data infrastructure failure with downstream alignment consequences.
Treating synthetic preference data as a cheap fix for minority subpopulation underrepresentation without accounting for the model generating it being trained on the same majority-skewed data.
Open Question for Deeper Work

The entire framework assumes that annotator subpopulations can be identified, stratified, and treated as coherent preference clusters — but human values are not cleanly partitioned by demographic categories, and individuals hold internally inconsistent preferences that shift with context. The open question is whether preference learning architectures should abandon the subpopulation model entirely in favor of individual-level latent value representations that generalize across contexts, and if so, what the minimum data requirements per individual are for such representations to be more stable than demographic proxies — and whether that bar can ever be met at deployment scale.






