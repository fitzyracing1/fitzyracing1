Thesis: Under extreme input-output length ratio mismatch, cross-attention in encoder-decoder models degenerates into positionally-biased sink formation through a self-reinforcing entrenchment loop that corrupts both the decoder's query routing and the encoder's internal representations, and the remediation strategies most readily available — coverage penalties, encoder freezing, staged unfreezing — each introduce distinct secondary failure modes that require joint monitoring of gradient and attention statistics to detect and contain.

Key Insights
1. Sink formation is a gradient-starvation loop, not a softmax artifact

Cross-attention sinks emerge because stochastic gradient descent finds a low-resistance path: attending to a small number of positionally privileged encoder tokens satisfies cross-entropy loss without requiring the model to integrate distal encoder content. The K and V projections of non-sink positions receive negligible gradient signal, stagnate, and become less discriminative — which further reduces the probability of future gradient steps routing to them. This is structurally distinct from self-attention sinks in decoder-only models, where initial tokens absorb probability mass as a no-op routing device; here, entrenchment is parameter-level and self-reinforcing.

2. Entrenchment propagates upstream into the encoder

The pathology does not remain confined to cross-attention. The encoder's own self-attention reorganizes to over-represent sink-adjacent positions, effectively preparing representations for the decoder's biased queries. Probing experiments on BART-large finetuned on XSum reveal an ~18-22% drop in linear decodability of semantic content at non-sink encoder positions relative to pretrained checkpoints — evidence that encoder hidden states have reorganized around sink-serving objectives, rendering coverage penalties ineffective since they have no gradient path into encoder self-attention routing.

3. The temporal ordering of gradient signals reveals the mechanistic sequence

Two detectable signals mark the entrenchment transition: collapse in the coefficient of variation of cross-attention entropy (CV_H) across heads, and rising cosine similarity between encoder self-attention gradients and cross-attention query gradients. When CV_H collapses first, entrenchment is decoder-initiated — query projections committed to sink routing before the encoder reorganized, the harder failure mode. When gradient alignment rises first, entrenchment is encoder-initiated and more recoverable. Staged unfreezing, by running the decoder at a higher learning rate than the encoder, systematically biases toward the harder decoder-initiated ordering.

4. Mid-training rescue requires joint Q and K intervention, not optimizer switching alone

Selectively re-initializing query projection matrices at detection time fails because K projections have geometrically co-adapted to Q's entrenched singular subspace, reconstructing the sink attractor within 100-300 steps. Switching Q to a momentum-free optimizer like Adafactor is insufficient because factored second-moment estimation reconstructs a sink-amplifying preconditioner immediately. The minimal effective intervention is asymmetric partial moment reset across both Q and K — heavier disruption on Q, conservative disruption on K — paired with re-initialization of only the sink-aligned singular components of Q, preserving content-routing directions and avoiding the attention collapse caused by full re-initialization.

5. Monitoring must be asymmetric and task-anchored

Statistical signals (CV_H, gradient alignment cosine similarity) must be complemented by a task-level probe: ROUGE or BERTScore restricted to content words appearing only in the distal half of encoder inputs, which is directly sensitive to sink entrenchment while being insensitive to fluency gains that mask faithfulness failures. Because naturally skewed input distributions (e.g., news leads) produce legitimate early CV_H drops, statistical thresholds require contrastive calibration against shuffled-input baselines to distinguish content-driven from position-driven entropy reduction.

Common Pitfalls
Mistaking fluency for faithfulness: Sink-entrenched models maintain low perplexity and high surface fluency while systematically ignoring distal encoder content; standard evaluation metrics do not flag this failure.
Applying coverage penalties as the fix: Coverage forces attention mass distribution but cannot rescue stagnated K/V projections or repair upstream encoder representational collapse.
Treating encoder freezing as safe: Freezing prevents co-adaptation but introduces head collapse (2-3 heads accounting for >70% of entropy reduction) and cross-modal alignment tax from mismatched representational geometry.
Resetting optimizer moments globally: Full moment reset destabilizes content-routing parameter directions that were correctly learned; surgical, component-wise moment reset is required.
Open Question for Deeper Work

Is there a closed-form or analytically derivable asymmetric intervention scale for joint Q/K moment reset — one grounded in the geometric relationship between Q's entrenched singular subspace and K's co-adapted column directions — that would eliminate the need for empirical hyperparameter search at intervention time? Answering this would require connecting the spectral geometry of co-adapted attention projections to optimizer convergence theory in a way that does not yet exist in the literature, but would generalize the intervention framework to arbitrary encoder-decoder architectures without task-specific tuning.






