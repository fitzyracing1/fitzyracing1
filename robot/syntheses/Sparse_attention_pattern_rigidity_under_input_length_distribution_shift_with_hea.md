Thesis: Sparse attention head specialization is not a stable intrinsic property of learned weights but an emergent, geometry-dependent phenomenon that silently dissolves under input length distribution shift, triggering a cascade of functional cession, gradient shadowing, and downstream suppression that renders the failure nearly invisible to standard evaluation and deeply resistant to inference-time repair.

Key Insights
1. Head specialization is pattern-geometry-dependent, not weight-intrinsic

A retrieval head's functional role emerges from the interaction between its Q-K subspace geometry and the attention pattern it is permitted to execute. The critical measurable property is the participation ratio of the W_Q^T W_K singular value spectrum: heads with near-rank-1 anisotropic spectra encode retrieval selectivity in their weight geometry and degrade gracefully under length shift; heads with flat spectra have offloaded selection to the sparse mask itself and collapse catastrophically when mask geometry changes. This means fragility is diagnosable from weights alone, before any long-context inference is run, providing a pre-deployment screen that requires no benchmark evaluation.

2. Functional cession is driven by gradient shadowing and is self-reinforcing

When a mask-dependent head encounters out-of-distribution lengths, its diffuse attention produces poorly directed gradients into W_Q and W_K. Geometrically intact heads in the same model receive sharper, better-conditioned gradients, adapt first, and absorb the retrieval function. Once this redistribution stabilizes — often within a few hundred fine-tuning steps — the originally specialized head's loss contribution drops, its gradients collapse further, and functional cession becomes self-locking. The process is silent: perplexity and aggregate benchmarks remain stable because the model compensates, while structured long-range retrieval degrades without any surface signal.

3. Ceded heads are detectable from activations before retrieval failure surfaces

Two activation-level signals jointly identify ceded heads without labels or probes: output cosine similarity across diverse inputs exceeding ~0.90 (output variance collapse, indicating near-constant residual stream contribution) and attention entropy exceeding ~0.8 × log(sequence_length) simultaneously. The V projection matrix retains latent structure from the pre-cession functional role — its dominant singular subspace remains aligned with intact retrieval heads in the same layer — but W_O begins drifting toward anti-alignment with the residual stream directions it once wrote into, providing a quantitative recoverability threshold around 0.3 cosine drift distance.

4. Downstream MLPs build conditional suppression circuitry around ceded heads

As a ceded head's output becomes anomalous (off-manifold relative to the trained residual stream distribution), MLP layers L+1 through L+4 develop neurons that conditionally activate on that anomalous signature and cancel it. This suppression is not a static filter but a content-gated mechanism: it fires when the ceded head produces unusual output and is quiescent otherwise. W_O drift concentrates in the columns projecting onto the dominant singular directions of these downstream MLP output matrices, fingerprinting exactly which layers built suppression circuitry and making the ceded head's functional territory legible from weight geometry alone.

5. Inference-time reactivation is defeated by the suppression-reactivation trap

Surgically injecting a sharp attention pattern into a ceded head simultaneously triggers the downstream suppression neurons, because the retrieval-relevant output the head now produces is precisely the anomalous signature those neurons were trained to detect and cancel. The net effect on the residual stream is near-zero. Recovery requires either fine-tuning before gradient shadowing consolidates (catching the head within ~50-100 gradient steps of cession onset) or simultaneous intervention on both the ceded head and the suppression neurons in downstream layers — a multi-site patching requirement that defeats single-site mechanistic interpretability repair strategies.

Common Pitfalls
Treating benchmark stability as safety: Aggregate perplexity and even task benchmarks mask retrieval failure because compensation by other heads preserves average performance while specific long-range retrieval collapses.
Conflating weight preservation with functional preservation: A ceded head's W_V retains meaningful geometry long after functional cession; inspecting W_V alone will falsely suggest the head is recoverable when W_O drift has already made it unrecoverable at inference time.
Single-site patching on circuits with suppression: Activation patching literature (IOI circuit, ROME) succeeds on intact circuits; applying the same methodology to ceded heads ignores the conditional suppression layer and consistently underestimates intervention complexity.
Open Question for Deeper Work

Suppression neurons activate conditionally on the ceded head's anomalous output signature and generalize across inputs that produce similar off-manifold residual vectors. This raises a precise and underexplored question: does the suppression neuron activation pattern constitute a real-time, position-resolved signal of near-recovery events — moments when a ceded head accidentally receives input within its trained length distribution and partially reactivates — and if so, can that signal be harvested during inference to dynamically route those specific context positions through an explicit retrieval pathway, effectively using the model's own suppression machinery as a failure detector rather than fighting it as an obstacle?






