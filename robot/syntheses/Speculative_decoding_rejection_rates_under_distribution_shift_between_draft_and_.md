11:24 PM



Working
Working
Check available skills
Synthesis brief on speculative decoding rejection rates under distribution shift

markdown

# Speculative decoding rejection rates under distribution shift between draft and target models across domain-specialized corpora

**Thesis:** When draft and target models are trained on different domain corpora, speculative decoding's acceptance rate degrades in structured, non-random ways that can eliminate latency gains entirely — and the path to recovery requires domain-specific instrumentation that undermines the generality the technique was designed to provide.

---

## Key Insights

### 1. Distribution shift produces clustered, not uniform, rejection

The standard intuition — that rejection rate degrades gracefully and uniformly under domain shift — is wrong. Rejections cluster at domain-specific structural boundaries: ring-closure tokens in SMILES strings, brace transitions in JSON, scope changes in code, stereochemistry markers in chemical notation. This clustering matters because the rollback mechanism discards the entire suffix after the first rejection; a clustered streak therefore causes repeated full-cost target passes that accept only one token each, which is strictly more expensive than naive autoregressive decoding. The decisive vocabulary property is not coverage but *conditional structure*: terms that impose long-range constraints (SMILES, formal proofs, typed APIs) create irreducible divergence that scaling the draft model cannot fix, because the bottleneck is the functional form of the conditional distribution, not parameter count.

### 2. Adaptive γ controllers are structurally reactive, not predictive

Dynamic speculation-length controllers that shrink γ in response to observed rejections are implicitly doing online estimation of the local acceptance rate — but that rate is non-stationary, shifting with latent syntactic and semantic context in ways a reactive controller cannot anticipate. The controller arrives at γ=1 two or three tokens after the rejection streak ends, then re-expands into the next hard region. The true signal is the target model's internal state, which the draft model by definition cannot access. Using the target's next-token entropy as a forward-looking proxy is cheap (negligible cost against a full target forward pass) but conflates high certainty with easy-for-draft, since structured domains produce near-zero entropy at exactly the positions where the draft is most likely to be wrong.

### 3. An auxiliary acceptance-prediction model is theoretically attractive but faces a self-defeating training dynamic

Training a small model to predict acceptance sequences rather than tokens — using the verification pass's ground-truth binary acceptance vectors as free supervision — could in principle internalize long-range constraint structure implicitly. The training signal is free, the architectural requirement is modest (10–50M parameters operating on compressed target hidden states), and the approach reframes the problem usefully: predicting the *verifier's decision* rather than the next token. The fatal complication is that success degrades the training distribution: as the auxiliary model improves γ selection and reduces rejection streaks, the hard constraint-boundary examples it needs to generalize vanish from the data stream. Maintaining coverage requires epsilon-forced exploration, stratified replay weighted by acceptance-vector variance, and ultimately synthetic data generation targeting known hard boundaries — domain-specific work that cannot be automated away.

### 4. Robust deployment requires a domain-specific inference stack

Synthetic data generation targeting hard constraint boundaries is, practically speaking, unavoidable for robust auxiliary model training. This means the deployment unit is not a general speculative decoding system but a domain-adapted stack: a (draft model, auxiliary controller, synthetic data pipeline) tuple per domain, routed to by a request classifier that identifies domain before reaching the inference backend. At serving scale this creates a maintenance matrix: every target model update invalidates the auxiliary model's training signal and triggers retraining. The organizations best positioned to capture the latency gains are those with both domain depth and infrastructure scale; a general-purpose API provider serving hundreds of domains faces a combinatorial maintenance burden that may make domain-specific speculative decoding economically irrational compared to faster hardware.

### 5. The theoretical correctness guarantee masks the latency collapse

Because the rejection sampling mechanism provably preserves the target model's output distribution regardless of acceptance rate, practitioners may not notice when speculative decoding has stopped providing latency benefits. Outputs remain correct; the speedup simply disappears. This makes the failure mode silent in production monitoring unless wall-clock time per token is tracked per domain and compared against an autoregressive baseline — a discipline most inference pipelines don't enforce. The implication is that acceptance rate must be treated as a first-class serving metric, not an internal implementation detail.

---

## Common Pitfalls

- **Assuming rejection rate is uniform:** Performance on general benchmarks (α ≈ 0.7–0.8, per Leviathan et al. 2023) does not predict behavior on structured domains; code generation with mismatched drafts shows rates below 0.5, and cheminformatics pipelines have reported net slowdowns of 1.3–1.5×.
- **Conflating vocabulary coverage with distributional compatibility:** A draft model that tokenizes domain terms correctly can still fail catastrophically if it cannot maintain the right conditional structure across constrained sequences.
- **Using entropy as a universal proxy for acceptance rate:** Low target entropy near a structural constraint means high certainty about a token the draft likely assigns near-zero probability — the opposite of the easy case.
- **Treating the auxiliary model's training distribution as stable:** Online learning on live inference traffic looks appealing until you recognize that good policy performance actively removes the hard examples from the buffer.
- **Ignoring the γ=0 failure mode:** When the expected number of accepted tokens per round falls below roughly 1 + ε×γ (where ε is draft cost ratio), speculative decoding is net negative and should be disabled — but most systems have no circuit breaker for this condition.

---

## Open Question for Deeper Work

Could the auxiliary controller be made target-model-agnostic by training it on *residuals* between draft and target distributions — the signed difference in log-probabilities at each position — rather than on a specific target model's verification decisions? If the residual captures the structural gap independently of the target's absolute probability scale, a single auxiliary model might transfer across target fine-tunes and even across target architectures of similar capability. The key unknown is whether the residual signal is stable enough across target model updates to make transfer worthwhile, or whether fine-tuning shifts the residual distribution in ways that are as model-specific as the raw acceptance vectors — in which case target-model-agnostic training buys generality at the cost of the prediction accuracy that makes the auxiliary model worth running at all.

Want to be notified when Claude responds?
Notify