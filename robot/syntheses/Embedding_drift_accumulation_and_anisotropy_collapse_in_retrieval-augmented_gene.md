Thesis: When only one side of a bi-encoder retrieval system is fine-tuned while the other remains frozen, and the index is refreshed incrementally rather than wholesale, the joint embedding space undergoes progressive geometric degeneration — anisotropy collapse, score compression, and manifold heterogeneity — that is largely invisible to standard rank-ordinal evaluation metrics yet causes systematic, query-distribution-dependent retrieval failure in production RAG systems.

Key Insights
1. Asymmetric fine-tuning destroys joint geometry without destroying individual encoder quality

Fine-tuning only the query encoder causes its output distribution to collapse toward a low-dimensional subspace — Ethayarajh (2019) measured effective dimensionalities as low as 20–50 out of 768 in BERT-family upper layers — while document embeddings remain anchored to the original geometry. The result is not that either encoder is individually broken, but that their output spaces become geometrically misaligned: dot products between query and document vectors lose discriminative spread, producing score compression where rank-1 and rank-100 candidates receive nearly identical similarity scores. This failure is structurally undetectable by MRR@10 or Recall@100 because both metrics are rank-ordinal and blind to score margin collapse.

2. Iterative partial re-indexing creates a temporally heterogeneous manifold

Because full corpus re-encoding is expensive, production systems re-index only new or updated documents, leaving old embeddings encoded by earlier encoder versions coexisting with new embeddings in the same ANN index. This creates a mixed-geometry index where a single query vector must simultaneously retrieve across multiple geometric regimes — old documents occupy the pre-drift manifold, new documents occupy the post-drift manifold — and no standard FAISS or HNSW index structure tracks this distinction. Score-thresholded filtering and hybrid dense-sparse fusion (as in Lewis et al.'s RAG, 2020) break silently under this condition because score scales differ systematically across regimes.

3. Query-side affine correction and per-shard score calibration are the pragmatic interventions

The most deployable remediation — requiring neither full re-indexing nor retraining — is query-side whitening: a linear map 
𝑊
=
Σ
𝑞
−
1
/
2
W=Σ
q
−1/2
	​

 that sphericizes the collapsed query distribution, estimated online from a rolling query buffer. For the mixed-geometry index problem, per-shard z-score normalization (calibrated via ~500 probe queries per epoch shard, as validated in FAISS deployment work) restores cross-regime score comparability. Both interventions operate as stateless middleware layers between the encoder and the index, making them incrementally adoptable without architectural changes.

4. Causal attribution of score compression requires a frozen anchor encoder

In production, query distribution shift and encoder drift co-occur because fine-tuning is typically triggered by detected query shift — the two sources of geometric change are causally entangled. Disentangling them requires a frozen anchor encoder running in parallel on a random sample of queries: covariance changes in the anchor stream isolate query distribution shift, while the divergence between live and anchor covariance isolates encoder drift. This is a representation-space implementation of the interventional logic formalized in do-calculus, and connects to the Failing Loudly (Rabanser et al., 2019) finding that representation-space drift detectors substantially outpower input-space detectors.

5. The optimal fine-tuning trigger policy is prospective and gradient-constrained

Because triggering on observed distribution shift initiates fine-tuning at maximum geometric stress, the optimal policy triggers on the rate of change of the query covariance rather than its absolute displacement — early, small-step updates are geometrically preferable to late, large-step corrections (consistent with loss landscape sharpness findings in Jastrzębski et al., 2020). Fine-tuning updates should further be projected onto the null space of the document manifold via gradient projection (cf. GPM, Saha et al., 2021), constraining the query encoder to move in directions that preserve existing query-document alignment.

Common Pitfalls
Trusting rank-ordinal metrics as geometric health signals. MRR and Recall@k are necessary but insufficient; score spread statistics and cross-regime calibration gaps must be monitored independently.
Treating index refresh and encoder fine-tuning as independent operations. Their interaction is the primary source of manifold heterogeneity; production pipelines that schedule them separately without coordination accumulate geometric debt silently.
Conflating query distribution shift with encoder drift when only a single covariance estimate is maintained, leading to miscalibrated trigger policies and misattributed retrieval failures.
Assuming document corpus stationarity when computing document null spaces for gradient projection; in live systems, the document manifold is itself evolving, invalidating static basis representations.
Open Question for Deeper Work

When the document corpus is large, heterogeneous, and continuously evolving, the document null space needed for gradient-projected fine-tuning is a moving target that cannot be faithfully represented by any fixed sample basis. What is the minimum sample size and basis rank required to capture sufficient null space structure for a corpus of 
10
8
10
8
 heterogeneous documents — and is there a theoretically grounded adaptive sampling strategy (perhaps importance-weighted by document retrieval frequency or embedding boundary proximity) that maintains null space fidelity under continuous corpus evolution without recomputing the full SVD?






