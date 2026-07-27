Thesis: Frozen-encoder fine-tuning in vision-language models creates a silent failure regime in which task loss improves while cross-modal semantic geometry degrades — because alignment loss saturation eliminates the contrastive gradient that previously constrained the modality gap, leaving adapter optimization free to exploit projection-layer shortcuts that erode compositional generalization without surfacing in standard benchmarks.

Key Insights
1. The modality gap is a geometric structure, not a scalar distance

The separation between vision and language embedding clusters in joint spaces like CLIP's is not adequately described by centroid cosine similarity. What matters is the principal angle spectrum between the two modalities' embedding subspaces and the effective rank of the cross-modal Gram matrix. When the smallest principal angles are large, the two modalities occupy nearly orthogonal manifolds, and adapter fine-tuning has no shared geometric scaffold — gradient updates rotate representations apart rather than together. Centroid distance is a first-order statistic that collapses distributional geometry into a single scalar, masking anisotropy, intra-modal variance, and subspace orientation — all of which determine whether fine-tuning will preserve or destroy cross-modal coherence.

2. Alignment loss saturation is not neutral stasis — it is a geometric unconstrained phase

Once the contrastive loss plateaus, the adapter operates without any gradient signal that enforces cross-modal consistency. This is the phase during which modality gap widening accelerates most dangerously, precisely because the training loss curve appears stable. The correct intervention — rank-preserving regularization, rank-constrained LoRA, or geometric consistency penalties — must be triggered at saturation and not before, because premature regularization interferes with the legitimate early-phase geometric reorganization the projection needs, empirically increasing final task loss by 2–4% while providing no subspace protection.

3. Saturation detection requires robust batch geometry estimation

Detecting the saturation trigger reliably requires monitoring the effective rank of the cross-modal Gram matrix via an exponential moving average over many batches, conditioned on batch semantic diversity. Mini-batch Gram matrices are corrupted by Marchenko-Pastur noise — for B=256 samples in D=768-dimensional space, roughly 30–40% of apparent signal eigenvalues are spurious — and batches with accidental semantic homogeneity produce false saturation signals. Batch diversity must itself be estimated via frozen cross-modal prototype assignments rather than dynamic k-means, to avoid the circular dependency where drift corrupts the diversity measure used to detect drift.

4. Cross-modal prototypes must be paired and modality-conditioned

Unimodal prototypes cannot partition the other modality's embedding space due to the modality gap — vision-space Voronoi cells literally do not extend into the language embedding cloud. Reliable diversity estimation requires paired prototype tuples (v̄ᵢ, l̄ᵢ) with strictly modality-conditioned assignment. Divergence between vision and language prototype assignments for semantically matched samples directly measures asymmetric drift magnitude and serves as a more sensitive trigger than Gram matrix rank alone.

5. Prototype validity must be certified before fine-tuning begins

When fine-tuning targets an OOD domain relative to pretraining, prototype assignments become semantically meaningless — OOD samples scatter across prototypes, producing artificially high entropy that permanently suppresses the intervention trigger. A mandatory pre-flight silhouette audit (mean silhouette > 0.2, no per-prototype score < 0) on 100–500 unlabeled target-domain samples, combined with cross-modal prototype consistency checks (>70% agreement between vision- and language-assigned clusters), certifies whether the monitoring framework is valid for a given domain. Silhouette thresholds must further be calibrated to the target manifold's effective intrinsic dimensionality rather than nominal embedding dimension, since distance concentration in high-dimensional spaces collapses silhouette scores toward zero even for genuinely separable clusters.

Common Pitfalls
Trusting task loss as a proxy for alignment health. VQAv2 accuracy can improve while compositional generalization on CREPE/SugarCrepe probes collapses — these are measuring different geometric properties.
Using centroid cosine similarity as the alignment diagnostic. It misses subspace orientation, effective rank, and intra-modal variance — the quantities that actually predict fine-tuning behavior.
Applying regularization too early. Pre-saturation penalties interfere with necessary early-phase projection geometry formation.
Computing diversity from dynamic k-means during drift. The cluster structure is corrupted by the same drift you are trying to detect, creating a circular failure.
Assuming pretraining prototypes cover the fine-tuning distribution. For domains like histopathology or remote sensing, CLIP-pretrained prototypes produce geometrically collapsed OOD assignments that corrupt every downstream monitoring signal.
Open Question for Deeper Work

The silhouette certification threshold is currently calibrated heuristically (>0.2 from Rousseeuw 1987) against nominal embedding dimension, but the relevant quantity is the effective intrinsic dimensionality of the target domain's embedding manifold. A rigorous open question is: can a domain-adaptive silhouette threshold be derived analytically from a pre-fine-tuning estimate of the manifold's intrinsic dimension (via, e.g., TwoNN or correlation dimension estimators), such that the certification criterion is both necessary and sufficient for monitoring framework validity — and does such a threshold have a closed-form relationship to the Marchenko-Pastur bulk edge that already governs Gram matrix rank estimation?






