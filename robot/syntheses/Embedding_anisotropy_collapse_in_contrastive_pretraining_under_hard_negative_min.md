Thesis: Hard negative mining in contrastive pretraining contains a self-defeating feedback loop — anisotropy concentrates embeddings into a narrow cone, which causes the miner to preferentially sample false negatives, which corrupts the gradient signal, which accelerates anisotropy, producing a thin-shell collapse that standard metrics are structurally blind to and cannot reliably detect or stop.

Key Insights
1. Anisotropy transforms false negatives from noise into the modal case

In an isotropic embedding space, false negative contamination scales with the corpus positive rate — a manageable, bounded error. Under anisotropy, the geometry itself amplifies contamination: when most embeddings cluster within a narrow cone (BERT's pre-softmax representations show average pairwise cosine similarity above 0.99), the hard negative miner's distance threshold selects almost exclusively from within that cone, making the hardness-to-contamination ratio collapse to near zero. The critical insight is that the miner cannot distinguish "hard true negative" from "false negative" once the angular spread of the cone is smaller than the semantic margin the task requires — contamination becomes structural, not statistical.

2. False negative gradients and true positive gradients interfere in the same collapsed subspace

When repulsion gradients from false negatives and attraction gradients from true positives operate in the same low-dimensional subspace, their interference reduces the effective rank of the batch gradient covariance matrix. This is detectable without ground-truth labels: the eigenvalue spectrum of the gradient covariance narrows, the top-eigenvalue-to-trace ratio rises, and within-batch cosine similarity histograms show merging of the positive and negative modes. The rank collapse in gradient space both reflects and reinforces the rank collapse in embedding space, creating a coupled degradation that accelerates faster than either mechanism alone.

3. Learned per-anchor temperature introduces a collapse accelerant, not a safeguard

The intuitive intervention — allowing the model to soften its loss when it suspects false negatives — backfires because the model discovers that raising temperature universally eliminates gradient pressure more efficiently than discriminating true from false negatives. Temperature collapse preferentially disengages the loss for the most anisotropic (centroid-proximal) embeddings, leaving only peripheral anchors active. Those peripheral anchors receive asymmetrically large gradients, but those gradients are tangential to the cone's surface rather than radial, compressing the cone's boundary without expanding into unused dimensions and producing a thin-shell equilibrium.

4. The thin-shell equilibrium is locally loss-satisfying but globally retrieval-destroying

The thin-shell geometry — a cone whose interior is depopulated and whose surface is densely packed — satisfies the contrastive loss locally because surface embeddings are well-separated from their along-surface hard negatives. This is why contrastive validation loss fails as an early stopping criterion: the loss decreases monotonically through collapse. Geometric diagnostics — participation ratio, neighbor overlap coefficient, Wang & Isola's Uniformity metric — detect collapse earlier but require full-corpus re-encoding at prohibitive frequency, creating an operationalization gap that most pipelines cannot bridge cheaply.

5. STS-B is structurally blind to thin-shell failure

STS-B Spearman correlation remains high under thin-shell collapse because it is a pairwise ordinal task: it measures whether pair A is more similar than pair B, and local angular orderings are preserved on the shell surface even as global volumetric structure is destroyed. The decoupling from retrieval performance becomes measurable when the embedding manifold's effective dimensionality drops below what the retrieval corpus requires — empirically visible as a 15+ percentage point gap between STS-B Spearman and BEIR nDCG@10, with several high-STS-B models performing below BM25 on retrieval tasks in Thakur et al. (2021).

Common Pitfalls
Treating hard negatives as uniformly beneficial: hardness amplifies contamination under anisotropy; harder is not always better.
Using validation loss as the primary stopping criterion: it decouples from geometric health before collapse is visible in downstream metrics.
Trusting STS-B as a proxy for retrieval utility: the two objectives decouple precisely at the failure regime most relevant to production retrieval systems.
Adding learned temperature without rank constraints: per-anchor temperature creates a learned escape hatch that accelerates rather than corrects collapse.
Diagnosing collapse retrospectively: geometric signals like participation ratio are most actionable as online probes, but the infrastructure to run them cheaply does not exist in standard pipelines.
Open Question for Deeper Work

Can a mining strategy be designed that is geometry-aware online — estimating the current anisotropy level from batch statistics alone and dynamically adjusting hardness thresholds to maintain a target hardness-to-contamination ratio — without requiring full-corpus re-encoding? The core challenge is that the anisotropy level is a population-level property but the miner operates on local batches; closing this gap likely requires either a maintained low-rank sketch of the embedding covariance updated incrementally, or a surrogate signal derivable from the gradient covariance rank that can be computed cheaply per step and fed back into the mining policy.






