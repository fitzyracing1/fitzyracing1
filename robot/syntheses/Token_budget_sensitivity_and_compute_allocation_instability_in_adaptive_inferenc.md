Thesis: Adaptive inference systems that dynamically allocate compute based on estimated problem difficulty are structurally vulnerable to distribution shift not because they allocate too little compute on average, but because their difficulty estimators fail silently and selectively on problems that are superficially easy but genuinely hard — producing fluent, confident wrong answers with no internal or external signal that anything has gone wrong.

Key Insights

1. The failure mode is confident underallocation, not uniform degradation.
When the input distribution shifts, the danger is not that the system becomes uniformly worse — aggregate metrics may look stable. The real failure is selective misallocation concentrated in a specific quadrant: problems that resemble easy training examples in surface features but require significantly more reasoning depth. In this quadrant, the difficulty estimator assigns a low budget, the model executes a shallow path, commits to an answer early, and produces a fluent rationalization. Standard accuracy evals miss this because they don't condition on the joint distribution of compute spent, true difficulty, and correctness.

2. Budget compression is a fine-tuning artifact, not a pretraining deficiency.
The base pretrained model retains depth-extension capability — it will explore for thousands of tokens if unconstrained. The compression happens during reinforcement fine-tuning with length penalties or outcome-supervised RL, which drives the policy to front-load commitment: the answer distribution collapses early because the gradient signal rewards terminal correctness at low cost and never penalizes premature lock-in. Evidence from Muennighoff et al.'s s1 (2025) shows that fine-tuning on as few as 1,000 long-chain examples can recover suppressed depth capability, confirming it is latent rather than absent.

3. Geometry-based uncertainty estimation breaks the classifier regress.
Every learned difficulty classifier inherits the distributional assumptions of its training data, pushing the vulnerability one level up rather than resolving it. The regress terminates by replacing classifiers with non-parametric distance estimation in a frozen, task-relevant embedding space: problems in low-density regions of the training manifold are flagged for budget optionality preservation regardless of their surface features. The embeddings must be frozen — never updated by the budget-optimization objective — or RL collapses the geometry the distance metric depends on.

4. Compute-outcome curves are the right training signal, but single-pass proxies are necessary in practice.
The ideal supervision signal for a metric learner or depth-demand probe is the compute-outcome curve: accuracy measured at 25%, 50%, 75%, and 100% of max budget per problem. In latency-constrained deployment, the minimum viable proxy is the answer entropy trajectory from a single full-budget forward pass — the shape of entropy collapse across generation steps approximates the curve's ordinal structure. Kadavath et al. (2022) and Wang et al.'s self-consistency work (2023) suggest roughly 60–70% of curve ranking is recoverable from single-pass internal signals, with fidelity loss concentrated at the hard-but-easy-looking boundary.

5. A frozen scalar probe on the residual stream can make depth estimation architecturally free.
The theoretical minimum intervention is a single linear depth-demand head on the residual stream, trained with auxiliary supervision and never backpropagated into the main model weights. This reframes the CALM early-exit classifier's target from answer confidence to structural depth demand — identical architecture, different supervision. The probe is essentially free at inference time (one dot product per layer) and preserves epistemic uncertainty estimation relevant to distribution shift, while forfeiting aleatoric uncertainty from path-dependent reasoning.

Common Pitfalls
Trusting aggregate metrics: A system can look stable on mean compute consumption while catastrophically failing on a shifted subpopulation.
Conflating fluent output with correct reasoning: Budget-trained models produce confident, well-formed wrong answers; downstream confidence scores do not reliably distinguish these from correct answers.
Freezing embeddings without auditing them: Frozen pretrained embeddings are only useful if the pretrained geometry is meaningful for the deployment domain — a misleading geometry requires a thin contrastive metric learner on top, trained on deployment-domain compute-outcome proxies.
Assuming forced full compute fixes underallocation: A model not trained to use extra tokens productively will pad rather than extend reasoning; genuine benefit requires preserved optionality from training, not just inference-time budget relaxation.
Open Question for Deeper Work

The depth-demand probe must be trained on residual stream states already shaped by the budget-optimization fine-tuning it is meant to correct — states that may systematically misrepresent depth requirements for exactly the problems of interest. How do you bootstrap a reliable probe training signal without access to a ground-truth oracle for reasoning depth, when your only behavioral signal comes from the same model whose representations you distrust? This bootstrapping problem sits at the intersection of representation auditing, weak supervision, and adaptive compute, and remains unsolved.






