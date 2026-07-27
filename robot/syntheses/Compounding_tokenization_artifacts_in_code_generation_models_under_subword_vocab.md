Thesis: Subword tokenization imposes a closed-world vocabulary assumption on an open-world identifier space, and the resulting fragmentation of rare or domain-specific identifiers creates a cascade of compounding failures — attractor-biased reconstruction, span-length ambiguity, geometric incoherence in extended vocabularies, and reranking ceilings — that no single downstream intervention can fully resolve because the information destroyed by the tokenizer cannot be recovered by any component operating after it.

Key Insights

1. Identifier fragmentation produces structured, not random, hallucination.
When a rare identifier is absent from the subword vocabulary, its fragments are statistically indistinguishable from sequences of legitimate separate tokens. The model's next-token prediction objective then pulls completions toward high-frequency token n-gram attractors, producing plausible-but-wrong identifiers like getAccountUser where getUserAccount was intended. This failure is invisible to perplexity metrics and passes syntax checkers, making it a silent bug class that standard benchmarks like HumanEval are structurally incapable of surfacing.

2. Span-length ambiguity at completion boundaries is epistemic, not aleatoric.
When a completion boundary falls mid-identifier, the model faces genuine uncertainty about how many additional fragment tokens constitute a valid completion — uncertainty that cannot be resolved by adjusting temperature or beam width because the information was never present in the training signal. Beam search exacerbates this via premature termination bias (shorter completions accumulate higher token probability), while sampling produces over-extension hallucinations. No decoding strategy resolves an epistemic gap; the problem must be addressed upstream.

3. Identifier-aware tokenizers improve in-distribution fertility but worsen out-of-distribution generalization.
Code-specific tokenizers like StarCoder's reduce token-per-line counts by ~30% for common identifiers by promoting frequent patterns to single tokens — but this consumes vocabulary slots that would otherwise serve as productive compositional sub-units. Novel deployment-time identifiers are then forced through maximally uninformative fragment decompositions, hitting the high-fertility, high-ambiguity regime the specialized tokenizer was designed to escape. The identifier-aware merge rules encode a closed-world assumption that software systems structurally violate.

4. Post-hoc vocabulary extension introduces geometrically incoherent embeddings.
New tokens initialized via mean-of-fragments heuristics occupy centroid positions in embedding space — geometrically interior to their constituent cluster and therefore less discriminable from neighbors than any individual fragment token. Because RoPE and similar encodings bake positional signal into the key-query rotation rather than as an additive bias, attention-level span injection at inference time creates representational integrity violations that corrupt hidden states throughout the residual stream. The directional structure that encodes semantic relationships in pretrained embeddings cannot be inherited through initialization heuristics alone.

5. Reranking and oracle-based decoding are bounded by base model recall.
Syntax-aware rerankers and type-oracle filters genuinely reduce surface error rates but hit a semantic ambiguity ceiling when multiple syntactically and type-consistently valid identifiers are equally consistent with local context. More critically, if attractor bias causes the correct identifier to fall below beam search's probability threshold, it never enters the candidate set — and no selection operation can recover a hypothesis that was never generated. Reranking is downstream of the tokenization pathology and therefore cannot resolve it.

Common Pitfalls
Treating fertility as a sufficient quality metric: Low tokens-per-identifier on a benchmark corpus masks the open-world generalization penalty for out-of-distribution identifiers.
Conflating syntactic validity with semantic correctness: AST-passing completions are the majority of attractor-induced hallucinations; parse success is not a correctness signal.
Assuming fine-tuning corrects vocabulary extension failures: New token embeddings converge slowly due to flat initial gradient landscapes and typically remain 3–5x less reliable than equivalent-frequency pretrained tokens in generative contexts.
Treating span-length ambiguity as a decoding hyperparameter problem: Adjusting temperature or beam width redistributes errors between truncation and over-extension without reducing total error mass.
Open Question for Deeper Work

Can the attractor basin geometry of a deployed code model be directly measured — via probing experiments that quantify the probability mass a given fragment sequence assigns to competing identifier completions — and would such measurements reveal whether attractor bias is localized to specific attention heads (making targeted fine-tuning feasible) or diffusely encoded across the residual stream (making it irreducible without full retraining)? The answer determines whether the pathology is an engineering problem with a targeted fix or a fundamental consequence of next-token training on fragmented representations.






