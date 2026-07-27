Thesis: Retrieval index fragmentation under concurrent write-heavy workloads is not a performance degradation problem but a silent correctness failure — the graph's metric space and topological space decouple invisibly, and no combination of query-time tuning, geometric monitoring, or latency instrumentation can detect or repair the damage without semantic ground truth signals collected synchronously at serving time.

Key Insights

1. HNSW navigability is a global fixed-point property that concurrent writes destroy locally but corrupt globally.
Bidirectional edge invariant violations under concurrent inserts produce directed sink nodes — vertices with many inbound edges but few outgoing ones — that trap greedy search in local minima that are connectivity dead-ends rather than geometric nearest neighbors. Because HNSW's SELECT_NEIGHBORS_HEURISTIC permanently encodes the neighborhood geometry at insertion time, patching sink nodes retroactively fails to repair the edges of the M nodes that selected them under false pretenses. The corrupted subgraph scales as O(M·log²N) per original sink, meaning localized graph surgery becomes exponentially incomplete as corpus size grows, and only global re-indexing restores the fixed point.

2. Rolling embedding model upgrades dissolve the fixed point into a chimeric attractor that defeats all geometric metrics.
When old and new embedding spaces coexist in the same index during a transition window, the graph's highway structure routes queries toward old-space centroids that are metrically alien in new-space, producing phantom near-neighbors — false positives that score high on cosine similarity within the mixed index but rank nowhere in a clean new-space index. Critically, recall@k remains artificially stable throughout this window because it measures self-consistency of the chimeric space rather than semantic correctness, as Qdrant's parallel collection benchmarks demonstrated with recall@10 holding at ~0.91 while downstream task accuracy dropped 15–22 points.

3. The minimum viable observability architecture must be causally instrumented at serving time, not retrospectively.
The only signals capable of detecting mixed-space corruption before it contaminates downstream metrics are: cross-encoder reranker scores per retrieved chunk, rank displacement variance via shadow traffic against a brute-force reference index (Kendall tau below 0.7 as the trigger threshold), query embedding provenance tags with model version hashes, and downstream LLM output entropy on retrieved context. Retrospective detection fails because the 2–4 day lag in human evaluation pipelines allows millions of corrupted retrievals to propagate, and the causal chain back to the embedding model transition is obscured by intervening changes.

4. Reranker score variance — not mean — is the corruption signal, but its interpretation requires skewness and intra-query autocorrelation analysis.
Legitimate query distribution broadening produces rightward variance expansion from a new high-score tail; chimeric corruption produces bimodal score splitting with negative excess kurtosis and non-monotonic within-query score profiles (Spearman rho between rank position and reranker score dropping below 0.4). These two signatures are geometrically distinguishable but require stratified monitoring by query intent — navigational queries have structurally low rho by design and must be evaluated via top-1 dominance ratio instead.

5. Dual-backbone serving architecture is the non-obvious operational conclusion of correct observability design.
Pinning the intent classifier to a frozen embedding backbone while the retrieval backbone is upgraded preserves the validity of the query stratification gate that makes corruption discriminators interpretable during transition windows. Without this separation, the intent classifier degrades simultaneously with the retrieval system, making the stratum labels unreliable precisely when they are most needed.

Common Pitfalls
Trusting ef_search tuning as a recall lever during graph corruption: increasing ef_search cannot recover recall when sink nodes make graph regions unreachable; it adds candidates from the same corrupted neighborhood.
Running recall@k against the live index as the ground truth: this validates chimeric self-consistency, not semantic correctness; brute-force ground truth must be computed independently.
Treating reranker scores as model-agnostic: rerankers trained on old-retriever-mined candidates inherit the old retriever's blind spots and actively misidentify new-space true positives as irrelevant.
Skipping query embedding provenance tagging: without model version hashes on logged query vectors, rank displacement events cannot be attributed to pipeline components versus query distribution shifts.
Open Question for Deeper Work

When the frozen classification backbone and live retrieval backbone develop divergent tokenization behavior for neologisms, code-switching, or post-cutoff domain terminology, the stratification gate mislabels query intent precisely for the long-tail queries most likely to expose retrieval corruption. The open question is: what is the minimum retraining signal — in terms of labeled query volume, labeling latency, and annotation schema — needed to keep the frozen classifier's intent boundaries calibrated against a continuously drifting live query distribution, without retraining it on the live embedding backbone and collapsing the architectural separation that makes it useful?






