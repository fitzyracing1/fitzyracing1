Thesis: Sparse MoE routing is a co-adapted contract between router and experts that is systematically fragile under inference-time distribution shift, and the architectural features that make MoE models efficient — confident sparse routing, layer normalization, auxiliary load-balancing losses — are precisely the features that conceal and amplify this fragility.

Key Insights
1. The router-expert contract breaks silently under shift

MoE routers and their experts are jointly optimized during training, producing a stable partition of token feature space where each expert becomes specialized for the tokens it receives. Under distribution shift, this contract breaks asymmetrically: the router continues to produce high-confidence gating scores while the expert receives tokens outside its competence envelope, producing geometrically malformed outputs — high-magnitude, misaligned vectors — without any visible error signal. The gating scores remain confident, the loss does not spike, and the system produces no explicit flag that routing has become semantically invalid.

2. Layer normalization actively erases the diagnostic signal

The residual stream architecture of transformer MoEs compounds the detection problem. Expert outputs are added residually, diluting individual expert failures, and layer normalization before each subsequent sublayer rescales corrupted activations back into a normal magnitude range. This destroys the norm-based signal that might otherwise reveal miscalibration, making the failure invisible to any monitoring strategy that inspects post-norm activations — which is what virtually all current inference monitoring does.

3. Auxiliary losses designed for training stability suppress shift detection at inference

Load-balancing losses (importance loss, z-loss) were designed to enforce uniform expert utilization during training, but they also suppress routing entropy variation. The entropy signal that would naturally indicate a distribution-shifted token — either collapsed certainty toward a single undertrained expert, or diffused uncertainty across many poor-fit experts — is regularized away during training, meaning the router arrives at inference with a systematically compressed dynamic range for the very signal needed to detect OOD inputs. Useful runtime indicators do exist in principle (per-layer router entropy, gating score margin collapse, pre-norm kurtosis, cross-layer routing consistency) but none are implemented in current production serving stacks.

4. Hierarchical routing trades one failure mode for another

Hierarchical MoE structures might seem to offer robustness through error containment across routing levels, but coarse router ossification — the tendency for the coarse partition to become rigid because fine-level specialization depends on its stability — means distribution-shifted tokens can be locked into incorrect coarse groups before fine routing can recover. Bottom-up routing (fine decisions first, coarse assignments emergent) avoids ossification in principle but creates bi-level optimization instability and destroys load balance by aggregation. The scaling evidence favors flat routing with many experts over hierarchy for raw perplexity, but no study has cleanly isolated routing structure as a variable under controlled distribution shift conditions.

5. Expert choice routing solves training load balance but breaks inference

Expert choice routing — where experts select their top-k tokens rather than tokens selecting experts — eliminates load imbalance by construction during training but becomes undefined at inference with small batches or single-token decoding. The standard fix (falling back to token-choice at inference) means the router's learned affinities were shaped by one selection mechanism but are evaluated under another, potentially making inference-time routing worse than a router trained end-to-end with token-choice. This training-inference mismatch has prevented expert choice from crossing from research into any major production deployment.

Common Pitfalls
Mistaking high gating confidence for correct routing. Gating scores measure router certainty, not expert competence for that token. High scores under shift indicate router overconfidence, not correct assignment.
Monitoring post-norm activations. Layer norm erases the magnitude signal from expert miscalibration. Any monitoring strategy that only inspects normalized representations is blind to the failure mode.
Assuming load balance implies routing quality. Uniform expert utilization is a property of the routing distribution, not of whether any individual token is routed to a competent expert.
Treating per-token perplexity as a sufficient evaluation. Held-out perplexity on training-adjacent data is structurally blind to routing failures that concentrate on minority distributional regions and rare token types.
Open Question for Deeper Work

Per-token perplexity is the dominant MoE evaluation metric, but it aggregates over the token distribution in a way that systematically discounts routing failures concentrated in low-frequency, high-shift regions — exactly where sparse routing instability is worst. The open question is whether a routing-conditional evaluation protocol — measuring perplexity stratified by router entropy, gating margin, and expert assignment stability — would reveal systematic performance cliffs in current MoE models that aggregate metrics conceal, and whether such a protocol could serve as a practical benchmark for routing robustness across deployment distributions.






