The request is for a markdown brief — inline content, not a Word document. I'll produce it directly.

Cross-lingual transfer degradation in multilingual fine-tuning under script-distance asymmetry with catastrophic interference in shared subword space and per-language capacity starvation

Thesis: Multilingual fine-tuning fails low-resource languages not through a single mechanism but through a cascade of compounding failures — fertility-driven gradient asymmetry, shared subword collision, layer-wise representational drift, and high-resource-biased sparse masking — each of which is invisible to aggregate benchmarks and resistant to the interventions designed to address the others.

Key Insights

1. Tokenizer fertility asymmetry biases gradient flow before any intervention can act.
Script-distance between languages creates radical divergence in subword fertility: a Tamil or Turkish sentence may tokenize into 2–3× as many pieces as its English semantic equivalent, producing proportionally larger gradient signals per semantic unit. Temperature-based sampling and loss-weighting correct for data volume imbalance but leave per-token gradient magnitude entirely untouched — a Tamil sentence sampled at the correct frequency still floods the shared embedding matrix with 2× the gradient of its English counterpart. This means the embedding geometry is being continuously sculpted by high-fertility language gradients regardless of sampling discipline, and low-fertility high-resource languages implicitly dominate the direction of weight updates even in nominally balanced training regimes.

2. Language-ID prepending masks subword collision rather than resolving it.
The standard remedy for shared subword ambiguity — prepending a language-ID token as used in XLM-R and mBART — works by propagating a language-specific bias vector through attention into downstream layers, not by disentangling the underlying embedding vectors. The embedding for an ambiguous subword remains a single contaminated vector; the model learns to conditionally interpret it differently based on attention context from the language-ID token. This masking fails on short inputs where attention budget is insufficient to condition all positions, and during fine-tuning the language-ID token's own embedding drifts, rupturing the routing geometry that non-fine-tuned languages depend on for zero-shot transfer.

3. Fine-tuning damage concentrates in upper layers and displaces rather than eliminates when frozen.
Upper transformer layers (roughly 8–12 in 12-layer models) store the cross-lingual alignment that zero-shot transfer depends on, and they absorb the largest representational shift during fine-tuning — Blevins & Zettlemoyer (2022) showed upper-layer degradation for Arabic and Swahili was 2–4× larger than lower-layer degradation after English fine-tuning. Selectively freezing upper layers partially preserves transfer but displaces adaptation into middle layers, which serve as compositional interfaces between surface encodings and abstract representations; corrupting middle layers induces a covariate shift that the frozen upper layers receive as out-of-distribution activations, degrading them indirectly. The optimal freeze depth is language-pair and task-specific, and static freezing provides diminishing protection over long fine-tuning horizons as middle-layer drift accumulates.

4. Sparse fine-tuning masks exhibit systematic high-resource bias and leave low-resource-critical parameters exposed.
Sparse fine-tuning approaches like SparseFT learn binary masks that constrain which parameters update, ostensibly protecting cross-lingual structure. However, masks are learned from the fine-tuning language's gradient signal, and parameters load-bearing for low-resource languages frequently produce near-zero gradients on high-resource data — making them invisible to mask selection. The protected parameter set and the low-resource-critical parameter set are largely non-overlapping, meaning unmasked gradient flow from the high-resource fine-tuning language corrupts low-resource representations without restriction. Identifying low-resource-protective masks requires gradient information from those languages, creating a circular dependency that sparse fine-tuning cannot internally resolve.

5. Monitoring signals for dynamic intervention become unreliable as the model's geometry drifts.
Dynamic scheduling of freezing or learning rates requires a cross-lingual alignment signal to trigger protective interventions. CKA against pretrained representations is the natural candidate, but the pretrained distribution becomes an increasingly poor reference as fine-tuning progresses — the model improves on the task precisely by moving away from it. Any monitoring signal is further subject to a Goodhart's Law dynamic: the optimizer implicitly finds configurations that preserve probe-set geometry while shifting representations in unmonitored subspaces, producing false confidence about transfer preservation for languages not covered by the probe set.

Common Pitfalls
Trusting average cross-lingual benchmark scores. High-resource languages mask low-resource collapse; per-language stratified evaluation, particularly for morphologically rich and low-resource languages, is required to detect real damage.
Treating sampling balance as gradient balance. Equalized document counts do not equalize gradient magnitudes when fertility diverges across scripts — these are orthogonal axes.
Interpreting early-checkpoint stability as training stability. Zero-shot transfer metrics that look acceptable at early checkpoints routinely degrade at later ones as middle-layer drift accumulates past frozen boundaries.
Assuming sparse fine-tuning is language-neutral. SparseFT and related methods protect task-relevant high-resource structure; without low-resource gradient signal, they cannot protect low-resource-critical parameters by construction.
Open Question for Deeper Work

The geometric structure of the pretrained multilingual representation space encodes implicit information about which parameters are disproportionately load-bearing for which languages — in principle, languages that rely on sparse, fragile representational subspaces should be identifiable through the curvature or spectral structure of the pretrained weight manifold without requiring any target-language task examples. The open question is whether this geometric signal is sufficiently reliable and practically extractable to serve as a proxy for constructing language-protective masks prior to fine-tuning: specifically, whether Fisher information estimates computed on unlabeled target-language text, or principal subspace analysis of pretrained layer activations on multilingual corpora, can identify low-resource-critical parameters with enough precision to constrain fine-tuning in a way that genuinely decouples task adaptation from cross-lingual transfer degradation — without itself being corrupted by the same high-resource dominance that undermines sampling-based approaches.







Want to be notified when Claude responds?
Notify
