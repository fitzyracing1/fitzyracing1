Thesis: Extended context fine-tuning systematically corrupts the flexible attention routing developed during pretraining by reinforcing proximity-biased and domain-specific lexical anchor patterns through gradient asymmetry, producing models that generalize poorly to heterogeneous document structures while appearing healthy on standard in-distribution benchmarks.

Key Insights
1. Gradient Asymmetry Is the Proximate Cause of Ossification

The cross-entropy loss during long-context fine-tuning is dominated by locally-predictable tokens — function words, formulaic continuations, syntactically forced completions — whose gradients systematically reward heads that attend to the preceding 50–200 tokens. Rare long-range retrieval events contribute high per-token loss but are diluted in the batch average, meaning the gradient signal is positionally skewed by construction under standard flat loss weighting. As demonstrated by LongLoRA (Chen et al., 2023), up-weighting long-range dependency tokens via retrieval-targeted loss masking measurably slows ossification, confirming that the loss weighting scheme — not fine-tuning per se — is the proximate cause.

2. Positional Encoding Scheme Determines Bottom-Up Vulnerability Profile

RoPE encodes positional bias multiplicatively inside the Q/K dot product, entangling semantic and positional components such that any gradient update to Q/K weights simultaneously corrupts long-range rotational geometry. ALiBi's fixed additive penalty is downstream of Q/K computation, structurally decoupling semantic routing from positional preference and conferring architectural resistance to positional ossification. Learned absolute embeddings are most vulnerable: early positions receive dense gradient signal while long-distance embeddings decay toward noise, producing positional embedding collapse. The vulnerability ordering is learned absolute > RoPE > ALiBi, but RoPE's NTK-aware interpolation partially mitigates this by pre-distributing positional signal across the full target context length before fine-tuning.

3. Semantic Ossification Is More Dangerous Than Positional Ossification

ALiBi's architectural advantage over RoPE does not protect against semantic ossification, where Q/K weights overfit to domain-specific lexical anchors (e.g., legal clause-boundary tokens) rather than positional proximity. Semantic ossification produces non-monotonic, structurally unpredictable generalization failures: a model may correctly retrieve information at 16K tokens within its fine-tuning domain but fail at 512 tokens in a structurally alien document where its learned anchors are absent. This mirrors the domain transfer findings of Gururangan et al. (2020), where domain-adaptive pretraining improved in-domain performance while degrading cross-domain transferability — the behavioral signature of ossified retrieval keys.

4. Residual Stream Intervention Is More Principled Than Projection Freezing

Freezing Q/K projections to preserve routing geometry is undermined by the fact that structural routing is an emergent circuit property spanning Q, K, V, and MLP layers — V adaptation still reshapes what content is routed, indirectly reinforcing proximity bias. Regularizing the attention sublayer's contribution to the residual stream (penalizing ∥Attn(x) − Attn₀(x)∥ per layer) targets the information bottleneck directly, and the NTK-aware RoPE scaling work demonstrates that rebalancing residual contributions recovers long-range retrieval. Optimal intervention requires depth-specific schedules: early layers handle local syntactic routing, middle layers carry the vulnerable long-range retrieval circuits, and late layers perform output formatting — a single uniform regularization knob cannot satisfy all three simultaneously.

5. Ossification Is Quantifiable via Pre-Deployment Key Distribution Audits

Semantic ossification can be measured by computing Jensen-Shannon divergence between per-head activated key vector distributions on in-domain versus structurally heterogeneous out-of-domain corpora. Heads with high JSD are routing to domain-specific anchors absent from the out-of-domain distribution; entropy collapse on out-of-domain documents confirms the behavioral failure. This audit is implementable with existing tools (TransformerLens, BertViz) without architectural modification, but requires maximally structurally diverse contrast corpora — topically different but structurally similar out-of-domain text will underestimate ossification severity.

Common Pitfalls
Trusting in-distribution perplexity as a health signal: Ossification is invisible on held-out data from the fine-tuning distribution; standard benchmarks like SCROLLS and LongBench share structural statistics with fine-tuning corpora, guaranteeing the failure mode goes undetected until deployment.
Conflating positional and semantic ossification: Interventions targeting positional encoding (RoPE interpolation, ALiBi adoption) leave semantic Q/K overfitting entirely unaddressed.
Applying LLRD schedules calibrated for short-context tasks: Standard 0.9× per-layer decay places middle layers in the worst position — vulnerable to both bottom-up positional corruption and top-down output pressure simultaneously.
Treating Q/K freezing as a clean architectural boundary: The routing/content dissociation between Q/K and V/O is an approximation; V adaptation reshapes effective information flow even when routing topology is nominally frozen.
Open Question for Deeper Work

Is there a training-time early warning signal — detectable within the first 5–10% of fine-tuning steps — that reliably predicts which heads will ossify, enabling targeted intervention before Q/K geometry is irreversibly corrupted? Specifically, it remains unknown whether per-head attention entropy trajectory, key activation JSD relative to a frozen reference model, or gradient alignment between local-prediction and long-range-retrieval token subsets can serve as a practical ossification precursor metric that generalizes across architectures and domain fine-tuning regimes.






