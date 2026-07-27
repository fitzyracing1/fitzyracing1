Thesis: In hybrid sliding window and ALiBi positional encoding schemes, attention sink formation and positional bias interact to produce structurally irreversible long-range retrieval failure, where the visible context window is systematically larger than the attended context window—and the architectural interventions required to fix this are considerably more invasive than the literature currently acknowledges.

Key Insights
1. The sink-ALiBi interaction creates dead zones, not just bias

ALiBi's linear distance penalty and softmax sink pressure are not independent failure modes—they compound. ALiBi monotonically discounts distant tokens by fiat, while the sink absorbs residual probability mass that has nowhere else to go, together carving out large regions of the nominal context window as effectively unreachable. The result is that a 128K-token context is not a 128K-token memory: it is whatever the learned bias geometry allows the model to actually retrieve, and the compounding across layers means that by the first third of the layer stack—roughly layers 6–12 in a 32-layer model—long-range retrieval failure transitions from recoverable to structurally irreversible.

2. Key and value vectors degrade asymmetrically, and this asymmetry is architecturally exploitable

Sink-induced degradation is not uniform across the attention mechanism. Key vectors undergo gradient starvation—tokens that are never selected receive weak gradient signal and drift toward the sink-aligned low-norm attractor—while value vectors remain semantically intact significantly longer, since they receive gradient signal from any head that selects the token, even spuriously. This asymmetry explains why cross-attention retrieval architectures like RETRO and Memorizing Transformers outperform in-context retrieval at long range: they substitute externally computed keys while preserving value content, bypassing the broken key pathway entirely. The practical implication is that key computation, not value aggregation, is the correct intervention target.

3. The sink is a load-bearing architectural feature, not an artifact

Eliminating the sink via key normalization onto a hypersphere removes the low-norm attractor but does not remove the functional pressure that created it—softmax requires probability mass to go somewhere when no semantically relevant token is present. Models with suppressed primary sinks reliably develop surrogate sinks on semantically inert tokens, typically punctuation. Critically, surrogate sink identity matters: BOS-token sink pollution injects near-orthogonal null-direction noise, while period-token sink pollution injects structured syntactic boundary signals into semantically inappropriate positions, corrupting exactly the representations that coreference and long-range agreement tasks depend on.

4. Auxiliary training interventions delay sink collapse but do not repair key geometry

Forcing early-layer attention to select long-range tokens via attention supervision, auxiliary losses, or scheduled sink-blocking during training produces models with artificially maintained key geometry under the training signal—but because the underlying distributional imbalance (far more short-range than long-range dependencies in pretraining data) remains unchanged, the auxiliary signal competes against the dominant gradient direction rather than restructuring it. Once removed, key vectors relax back toward the sink-aligned cluster. Architectural interventions—key normalization, Differential Attention's dual-softmax subtraction, explicit null token insertion—are more durable because they change the attractor geometry rather than fighting against it.

5. Per-layer sink control is necessary and not achievable with a single prefix embedding

Prefix tuning offers a promising path toward a manufactured inert sink token without modifying shared projection matrices, but a single trained prefix embedding propagated through the residual stream fails because sink pressure is layer-depth-dependent: early layers require high dot-product affinity in low-level feature space, middle layers must absorb residual mass from structurally saturated heads, and late layers compete against high-level semantic representations. P-Tuning v2's finding that per-layer independent prefix vectors substantially outperform shallow prefix tuning on long-range tasks is direct empirical confirmation. Effective sink prefix tuning requires per-layer key and value vectors initialized from the corresponding layer's BOS key representations, making the intervention domain-sensitive by construction.

Common Pitfalls
Conflating visible context with attended context: the window size reported in a model's spec is an upper bound on retrieval, not a guarantee.
Treating sink formation as a bug to eliminate rather than a functional pressure to redirect—removal without substitution reliably produces surrogate sinks that are worse.
Targeting value aggregation when key vector geometry is the actual failure mode.
Using auxiliary training signals as long-term fixes when they address symptoms rather than the distributional cause.
Assuming a single prefix embedding adapts across layers—per-layer parameterization is not optional for sink control.
Open Question for Deeper Work

Since per-layer sink prefix vectors must be initialized from layer-specific BOS key representations—which themselves encode the cumulative positional and frequency statistics of the pretraining distribution—sink prefix fine-tuning is potentially domain-sensitive by construction: a sink geometry calibrated on one data distribution may actively mis-route attention on a domain with substantially different token frequency profiles. The open question is whether this domain sensitivity is measurable and correctable without full retraining, or whether it implies that long-context models require distribution-aware sink recalibration as a standard component of domain adaptation fine-tuning—analogous to how batch normalization statistics must be updated when transferring to a new domain.






