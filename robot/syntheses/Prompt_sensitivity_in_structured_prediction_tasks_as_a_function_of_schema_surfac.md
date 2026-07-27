Thesis: In structured prediction, surface-form variation in schema presentation — field naming conventions, structural format, nesting depth, delimiter choice — produces measurable output degradation independent of semantic content, and the failure modes this exposes reveal that LLMs perform schema-conditioned pattern completion against pretraining distributions rather than abstract relational reasoning over task specifications.

Key Insights

1. Surface form and semantic content are not interchangeable in model behavior.
Two prompts that mean the same thing to a human do not activate the same priors in a model. Field names like "sentiment" carry dense co-occurrence statistics from pretraining; semantically equivalent alternatives like "emotional_valence" do not, and the output distribution shifts accordingly. This is not a calibration failure — it is evidence that the model's schema understanding is lexically and syntactically anchored, not meaning-anchored. The practical consequence is that schema design is a latent hyperparameter of any structured prediction pipeline, rarely treated as one.

2. Structural perturbations inflate cardinality and boundary errors more than semantic labeling errors.
When format varies — flat versus nested, array versus concatenated string, JSON versus YAML — the model's most common failure is collapsing multi-valued slots into scalars or misplacing values across nesting levels, while field-level semantic labels remain relatively stable. This asymmetry reveals that the model's representation of "is this slot complete?" is tied to syntactic boundary signals (brackets, indentation, delimiters) rather than to a schema-level understanding of cardinality constraints. Production pipelines validated on one canonical format are therefore silently brittle to schema revision.

3. Positional bias and frequency priors compete when multi-valued slots collapse.
When a model collapses an array to a scalar, it most often retains the first-listed value — but high-frequency parametric associations can override position when the field name carries strong real-world priors. This means the failure is a weighted competition between positional encoding and parametric retrieval, not a uniform strategy. Interventions must target the right mechanism: positional bias yields to prompt-level enumeration and schema layout changes; frequency-prior dominance requires fine-tuning or retrieval grounding.

4. Chain-of-thought reasoning does not reliably override positional or causal priors — it rationalizes them.
Turpin et al. (2023) and mechanistic interpretability work converge on the same finding: answer distributions are largely committed at mid-network layers before CoT tokens are generated. Scratchpad reasoning functions as working memory extension for enumeration tasks but as post-hoc rationalization for tasks where positional or causal priors are dominant. This means CoT-based pipelines that rely on reasoning traces to correct extraction bias are auditing confident wrong answers rather than preventing them.

5. Log-probability confidence signals measure fluency, not reliability.
Because output token probabilities reflect confidence in surface realization of an already-committed answer, high log-prob preferentially flags well-formatted wrong answers. The correct uncertainty signal is context-sensitivity slope — how much does the output shift under controlled evidence perturbation? — and cross-schema-surface consistency is a useful proxy only when perturbations span multiple axes simultaneously, including evidence presence and order, not just format.

Common Pitfalls
Single-axis consistency checking: Testing reliability by reformatting the schema alone will be fooled by format-invariant parametric priors that produce the same wrong answer across all surface variants tested.
Conflating failure modes: Treating tokenization-frequency artifacts and genuine semantic underdetermination as the same problem leads to interventions (robustness engineering vs. task redesign) that miss the actual cause.
Benchmark contamination: Evaluating on naturalistic documents where model parametric knowledge agrees with document labels inflates accuracy and masks prior-dominance; adversarial counterfactual evaluation sets are necessary to isolate grounding fidelity.
Order-manipulation without scope control: Reordering document content to counteract positional bias in extraction stages poisons downstream tasks that treat narrative or temporal order as an implicit feature.
Open Question for Deeper Work

How do you distinguish a model that has learned a genuine grounding mechanism — suppressing parametric priors in favor of document evidence when the two conflict — from one that has learned a shallow heuristic like "distrust recognized values," which would score well on adversarial counterfactual benchmarks but degrade on real documents where parametric recognition is a legitimate signal? Resolving this requires mechanistic interpretability tools that can trace whether document-evidence tokens are causally upstream of output commitments at the mid-network layers where answers are set — work that remains largely undone for structured prediction tasks specifically.






