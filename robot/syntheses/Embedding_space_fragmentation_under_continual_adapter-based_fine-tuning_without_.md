Thesis: Freezing a pretrained backbone is not sufficient to prevent representational drift under sequential adapter-based fine-tuning; new adapters corrupt prior task geometry through residual stream interference, and this corruption is largely invisible to standard accuracy-based evaluation while silently degrading retrieval, similarity search, and any downstream system that depends on embedding structure rather than classification heads.

Key Insights
1. The residual stream is the attack surface

The transformer residual stream is a shared additive channel: every adapter injects a delta directly into the running hidden state, and all subsequent layers — including earlier tasks' frozen adapters — receive a cumulative sum they were never trained to handle. Because adapter outputs are not gated or re-normalized before being passed forward, a new adapter trained on task N reshapes the effective representational basis seen by task N-1's adapter on future inference passes, without modifying a single backbone weight. The interference is directional and asymmetric: earlier adapters cannot update to compensate, so geometric damage accumulates monotonically with task count.

2. Accuracy is a lagging and insensitive indicator

Classification accuracy can remain stable while the underlying embedding geometry degrades substantially, because linear classifiers tolerate rotations, rescalings, and moderate neighborhood distortions that destroy retrieval and clustering performance. Detecting early-stage fragmentation requires geometry-native metrics: CKA for global representational similarity, intrinsic dimensionality estimators (TwoNN, Levina-Bickel MLE) for manifold integrity, and k-NN stability at multiple neighborhood scales for local structure. No single metric suffices — CKA misses anisotropic rescaling, intrinsic dimensionality is noisy on small samples, and k-NN stability misses distance distortions that preserve rank order.

3. Rehearsal-free geometric monitoring has an intrinsic horizon

Without access to prior task data, fragmentation can be detected by monitoring how much a new adapter's output deltas project onto stored per-task residual covariance eigenvectors. However, with k≈50 eigenvectors per task in ℝ⁷⁶⁸, the union of prior-task subspaces spans the full space after roughly 8–16 tasks depending on inter-task similarity, at which point any new adapter delta projects substantially onto some prior task's subspace and the signal becomes uninterpretable. This is a fundamental detectability ceiling, not an engineering limitation, implying that long task sequences require periodic subspace consolidation.

4. Subspace consolidation provably destroys task-specific anisotropy

Merging per-task eigenvector sets via incremental SVD produces a compressed basis that spans the union of prior subspaces but loses the eigenvalue weights encoding how much variance each task placed on each direction. This task-specific anisotropy is irrecoverable without the original data. Storing full per-task Gaussian summaries (mean and covariance) preserves anisotropy but fails for multi-class tasks where the residual distribution is a mixture — a single fitted Gaussian smears across inter-class gaps and cannot detect class-selective fragmentation. Per-class Gaussians address this but introduce label dependency and linear storage growth in both task count and class count.

5. AdapterFusion does not solve the problem

AdapterFusion's learned attention over adapter outputs partially mitigates interference but cannot provably preserve embedding geometry because its attention weights are trained discriminatively on task loss, not on any geometry-preserving objective. For fusion to guarantee structural preservation, task-k attention weights would need to zero out all adapters trained after task k — an orthogonal decomposition condition that is empirically violated because adapter output vectors across tasks occupy substantially overlapping subspaces in the shared backbone's feature space.

Common Pitfalls
Conflating parameter isolation with representational isolation. Frozen backbone weights do not prevent representational drift; the composition of adapter deltas in the residual stream is the true locus of interference.
Using FID or Fréchet distance as a geometry proxy. These metrics assume Gaussianity and will report false preservation when per-class manifold structure is reorganized within a globally similar covariance envelope.
Treating CKA above 0.9 as safety. CKA is invariant to isotropic rescaling and orthogonal rotation, both of which can be catastrophic for metric-sensitive downstream systems.
Assuming label disjointness across tasks. Overlapping or hierarchically related label spaces corrupt per-class Gaussian anchors by making class identity ambiguous at consolidation time.
Open Question for Deeper Work

Per-class Gaussian anchors require stable class identity across tasks, but real continual learning deployments frequently involve label spaces that are non-disjoint, hierarchically nested, or progressively refined. A principled correction would need to either map overlapping class labels into a shared semantic space before computing anchors — potentially using the backbone's own representation to define class identity geometrically rather than label-nominally — or maintain a dynamic class ontology that updates as label relationships are revealed. Whether such an ontology can be maintained without rehearsal, and whether the geometric anchors derived from it remain tight enough to detect fragmentation before accuracy degrades, remains an open and largely unaddressed problem at the intersection of continual learning theory and representation geometry.






