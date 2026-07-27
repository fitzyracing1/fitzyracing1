Thesis: Attention sinks in hybrid sliding-window architectures are not merely an inference artifact but a training-time pathology with deterministic geometric origins — seeded by positional bias dominance in the first 2000 pretraining steps, entrenched by flat loss manifold geometry that standard optimizers traverse freely, and amplified catastrophically at the first full-attention layer — making them structurally resistant to post-hoc correction unless intervened upon at multiple levels simultaneously.

Key Insights

1. Sink formation is a structural interaction between window boundaries and learned positional bias, not a softmax normalization accident.
ALiBi slopes and RoPE frequency spectra create logit gradients that steepen at sliding window edges, concentrating probability mass onto the nearest in-window tokens regardless of semantic content. In hybrid architectures, this boundary artifact is periodically laundered through full-attention layers that broadcast the corrupted value vectors globally — converting a local receptive-field artifact into a sequence-wide residual stream contaminant. The distinction between structural sinks (softmax needing a dump position) and bias-amplified sinks (parametric pressure toward fixed offsets) matters because only the latter are amenable to optimizer-level correction.

2. The loss landscape around sink configurations is a flat manifold that standard optimizers are mechanistically designed to traverse, not escape.
Sink-routing configurations achieve low perplexity on typical long-context corpora because recency bias plus a few anchor positions satisfies most next-token prediction objectives. The Hessian in the positional bias subspace is approximately rank-deficient along directions that trade off which positions become sinks, creating a flat manifold of equivalent-loss configurations. Adam's second-moment normalization actively inflates effective step size in these flat directions, and LoRA's low-rank constraint prevents the coordinated full-rank parameter moves needed to exit the manifold — making both the default optimizer and the default fine-tuning method co-conspirators in sink entrenchment.

3. Inference-time intervention is bounded by value subspace recoverability, which depends on sink depth and head heterogeneity.
Once a sink token's corrupted value vector has been committed to the residual stream, no same-layer attention reweighting can recover the original signal. The maximum recoverable retrieval fidelity is bounded by the mutual information surviving in layers above the sink formation depth, which empirically approaches zero for sinks forming in layers 1–4. The practical ceiling for inference-time recovery — around 60–70% of baseline retrieval performance — depends on whether heterogeneous head behavior preserved a clean retrieval subspace in parallel heads that never participated in sink routing.

4. Head specialization versus uniform sink collapse is determined by QK singular value geometry in the first 2000 pretraining steps.
Retrieval-specialist heads develop QK^T matrices with 2–4 dominant singular values oblique to the positional encoding subspace; sink-routing heads collapse to rank-1 QK^T aligned with the positional bias direction. This geometric signature is detectable at step 2000 via the singular value ratio (largest SV / sum of top-4 SVs) and forecasts long-context behavior at convergence with ~70–80% accuracy in large-head-count models. The specialization window closes because SGD finds rank-1 solutions first — they have larger basins of attraction — and subsequent gradient pressure mostly refines rather than reverses early functional roles.

5. Surgical reinitialization of collapsed heads can reopen the specialization window, but only with coordinated V-weight perturbation and optimizer state reset.
Resetting QK weights alone fails because preserved V/O weights and Adam's moment buffers encode the pre-reset sink configuration and reconstruct it within ~2000 steps via hysteresis. Effective intervention requires coordinated partial reset of QK and V weights, a brief LR spike to amplify gradient variance, and crucially, erasure of the optimizer's second-moment buffer for the affected parameter blocks — otherwise cross-parameter correlations in the moment buffer steer the reset heads back toward the sink manifold along the path of least resistance.

Common Pitfalls
Conflating sink presence with sink harm: not all attention concentration is pathological; the danger is value-vector overwriting at positions subsequently read by many downstream queries.
Applying long-context fine-tuning without diagnosing pretraining head geometry: fine-tuning cannot recover functional specialization that failed to emerge in the first 2000 steps.
Treating inference-time attention masking as a full fix: StreamingLLM-style sink reservation prevents future contamination but does not recover already-corrupted residual stream positions.
Ignoring optimizer state during surgical reinitialization: resetting weights without resetting Adam moments leaves a biased gradient environment that reconstructs the pathology.
Open Question for Deeper Work

Does the cross-parameter correlation structure in Adam's second-moment buffer between reset QK blocks and preserved V/O blocks encode sufficient information about the pre-reset sink configuration to quantitatively predict re-collapse rate — and could selectively zeroing only the off-diagonal correlations while preserving diagonal variance estimates provide a principled minimal reset that avoids full optimizer state erasure while still breaking the hysteresis?






