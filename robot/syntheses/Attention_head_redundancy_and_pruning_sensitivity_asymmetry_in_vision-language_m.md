Thesis: Standard attention head pruning applied to fine-tuned vision-language models is systematically biased toward removing functionally critical heads that have undergone cross-modal specialization drift, because the signatures of genuine utility in drifted heads are structurally indistinguishable from redundancy under every importance metric that operates on scalar entropy or gradient magnitude rather than spatial covariance structure.

Key Insights

1. Specialization drift creates a pruning visibility gap.
During cross-modal alignment fine-tuning, language-tower heads repurposed to aggregate visual token information develop diffuse, high-entropy attention patterns over patch sequences — not because they are doing nothing, but because no single visual token is a correct attend-to target in the way a syntactic head has a head-word. Classical importance estimators (Voita et al. 2019, Molchanov et al. 2017) treat low-entropy, high-confidence attention as the signal of useful computation; drifted heads attending softly over 30–80 visual tokens score near zero on these metrics regardless of their actual contribution to cross-modal grounding, while redundant linguistic heads with crisp attention survive pruning precisely because they are easy to measure.

2. The correct diagnostic object is attention covariance structure, not entropy.
A drifted head is distinguishable from a redundant head not by its entropy scalar but by the rank structure of its attention pattern covariance matrix across input samples: drifted heads exhibit low-rank but non-trivial covariance whose leading eigenvectors encode coherent scene-region groupings, whereas redundant heads produce either near-zero or full-rank noise covariance. Computing this object naively is intractable at VLM scale — the full covariance over a 768-token sequence is a ~590,000 × 590,000 matrix — but randomized SVD over the visual subblock makes it tractable with 400–800 calibration samples, reducing the problem to estimating leading eigenvectors of the 256×256 patch-to-patch attention covariance.

3. Calibration set composition is a covert attack surface.
Because drifted head importance is scene-category-contingent — their covariance structure is activated by spatially diverse natural scenes but collapses on homogeneous textures or center-cropped faces — an adversarial calibration set can be constructed by selecting images whose visual token distributions are orthogonal to the drifted heads' functional subspaces. This attack requires only a FAISS nearest-neighbor search in the complement subspace of the head's principal directions, is executable by any compression-as-a-service provider, leaves no trace in the compressed model's weights, and is invisible to VQAv2-style benchmark evaluation while causing 15–25% accuracy collapse on spatially demanding tasks like TextVQA or OCRBench.

4. Post-hoc covariance auditing is subject to Goodhart's Law once the probe set is public.
Shifting verification from calibration set provenance to compressed model covariance preservation is architecturally sound but creates a new gaming surface: a compressor with access to the public probe taxonomy can optimize pruning masks to preserve covariance fingerprints on probe categories while aggressively pruning heads whose functional subspaces fall outside the probe distribution. This is structurally identical to benchmark contamination in LLM evaluation but operates at the level of architectural decisions rather than training data, making it unrecoverable from the model artifact.

5. Vertical integration eliminates the third-party verification assumption.
The rotating private probe set with cryptographic commitment is the strongest available defense against Goodhart gaming, but it presupposes an independent auditor. When hyperscalers compress and deploy their own VLMs internally, the compressor and auditor are the same entity, and no external mechanism has visibility into calibration set construction, pruning mask optimization, or probe set alignment — making the entire verification framework collapse into an organizational trust assumption with no technical enforcement.

Common Pitfalls
Conflating entropy with redundancy: High attention entropy is not sufficient evidence of a useless head; it is necessary to examine the covariance structure of that entropy across inputs.
Calibrating on benchmark-adjacent distributions: Using COCO or ImageNet for pruning calibration systematically underrepresents the visual diversity that activates drifted head functional subspaces.
Trusting weight-level integrity checks: Hashing model weights or checking activation statistics cannot detect adversarial calibration attacks because the attack leaves no artifact in the compressed model.
Assuming benchmark parity implies functional parity: A compressed VLM passing VQAv2 within 1% of baseline can simultaneously have catastrophic degradation on spatially demanding tasks if the pruned heads were cross-modal grounding specialists.
Open Question for Deeper Work

Can the functional subspace taxonomy of drifted heads be recovered post-compression from the surviving heads' residual stream contributions, and if so, does this create a viable forensic auditing path — or does the distributed nature of cross-modal grounding across multiple heads make post-hoc reconstruction fundamentally underdetermined even with full white-box access to the compressed model?






