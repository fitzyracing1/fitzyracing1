Thesis: Token budget constraints do not uniformly degrade chain-of-thought reasoning — they interact with problem difficulty in a structured, non-linear way that causes systematic prior collapse, propagates through distillation pipelines, and creates failure modes that are qualitatively different from simple truncation and not always recoverable at inference time.

Key Insights

1. Budget pressure causes structured bias, not random degradation.
When token budgets are tight, models do not fail randomly — they collapse toward the modal solution path encoded in their prior. This means errors on budget-constrained models are directional: wrong answers tend to match the correct answer for the most common variant of the problem, not a random guess. The empirical signature is that perturbing a problem slightly causes discontinuous accuracy drops, and wrong answers are correlated with the correct answer to a nearby easier problem. Shi et al. (2023) showed that semantically plausible distractors degraded math performance by 17-65%, consistent with prior-pulling under constraint rather than graceful degradation.

2. Compression during distillation bakes prior collapse into weights permanently.
When student models are trained on compressed teacher traces, they inherit the teacher's pruning decisions as implicit ground truth. The student never sees the discarded reasoning branches, so it cannot learn to recognize when a problem requires departing from the modal path. Magister et al. (2022) found that distilled students' errors were correlated with teacher errors rather than independently distributed — the signature of structural prior collapse rather than situational budget pressure. Unlike runtime budget constraints, this form of collapse cannot be relieved by simply allocating more inference-time tokens.

3. Teacher diversity is the binding constraint on reasoning coverage, but introduces a calibration tradeoff.
Training on traces from multiple teachers with different pruning patterns expands the student's reasoning coverage but introduces trace inconsistency that degrades calibration. The optimal diversity level is where the marginal coverage gain equals the marginal calibration cost — and this optimum shifts by objective: hard novel problems favor high diversity, while easy familiar problems favor consistency. Self-consistency sampling (Wang et al., 2023) provides partial evidence for this mechanism by showing that diverse reasoning paths from a single model improve GSM8K accuracy by ~17 points, suggesting diversity of search is itself the operative variable.

4. MoE routing entropy provides a model-derived difficulty gradient for targeted distillation.
Rather than relying on human-designed difficulty ratings, a MoE model's routing entropy — the degree of disagreement across its expert subnetworks — correlates with human difficulty ratings at r=0.6-0.7 on math benchmarks and identifies precisely the problems where distillation supervision will be most inconsistent. Using routing entropy to allocate trace diversity budget concentrates distillation effort where coverage failures are most likely, converting model-internal uncertainty into an adaptive curriculum signal.

5. Self-consistency recovery at inference time has a hard boundary.
Dense students distilled from MoE teachers are architecturally guaranteed to be narrower, but self-consistency sampling can recover roughly 60-70% of the gap by serializing the model's uncertainty across samples. This recovery depends entirely on whether the correct reasoning path has non-negligible probability in the student's sampling distribution. If distillation compressed the correct path's probability to near-zero on hard problems, no amount of sampling recovers it — and the practical diagnostic is whether accuracy scales with sample count on high-entropy problems.

Common Pitfalls
Assuming budget effects are monotonic. More tokens do not always help; verbose reasoning on easy problems introduces noise and spurious steps.
Using final-answer accuracy as the sole metric. Process reward models (Lightman et al., 2023) catch ~30% more errors than outcome-only evaluation, because final accuracy masks intermediate failures.
Conflating efficient compression with step-skipping. These produce identical accuracy on easy cases but diverge sharply under perturbation; error distribution shape and verifier gap are the distinguishing tests.
Treating distillation compression as a runtime problem. Baked-in prior collapse requires retraining to fix; inference-time interventions cannot recover reasoning branches that were never represented in training.
Open Question for Deeper Work

Does the temperature used during distillation training — which controls how sharply the student mimics the teacher's modal trace — determine whether hard problems land in the recoverable or unrecoverable regime at inference time, and does this make distillation temperature a more consequential hyperparameter than model size for tail-distribution reasoning coverage? A clean experiment would vary distillation temperature across a fixed student architecture, measure self-consistency scaling curves on high-entropy MoE problems, and test whether flatter training distributions preserve enough probability mass on non-modal paths to remain inference-recoverable.






