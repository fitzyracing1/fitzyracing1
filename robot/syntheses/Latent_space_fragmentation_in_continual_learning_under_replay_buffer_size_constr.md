Thesis: When a shared encoder must sequentially represent tasks whose feature manifolds are geometrically incompatible, bounded replay buffers cannot simultaneously preserve distributional coverage and subspace recoverability, producing latent space fragmentation that is invisible to per-task accuracy metrics until it becomes unrecoverable.

Key Insights
1. Fragmentation is a geometric phenomenon, not just an accuracy phenomenon

Catastrophic forgetting manifests first in the encoder's latent geometry — shrinking principal angles between task subspaces, intra-class variance expansion, Gram matrix rank collapse, and negative gradient cosine similarity in later layers — well before any task's test accuracy moves. These geometric signatures are detectable 50–200 gradient steps before accuracy degradation and constitute an early-warning system that per-task evaluation completely misses. The implication is that monitoring must operate at the representation level, not the output level.

2. Architectural interventions that preserve task A's geometry distort task B's feature formation

Freezing later encoder layers after task A protects task A's activation subspace locally but imposes it as a fixed basis that earlier layers must learn to "speak." This creates gradient starvation and directional suppression in early layers: task B features that fall outside the frozen layer's expected input geometry are either discarded or artifactually warped to satisfy the frozen basis, producing representations that are accurate but geometrically incoherent. Orthogonal gradient projection (OWM, GPCL) partially addresses this by constraining task B updates to directions orthogonal to task A's subspace, but the constraint is only as strong as the subspace estimate, which is bounded by buffer quality.

3. The replay buffer's geometric coverage determines the orthogonality constraint's integrity

Orthogonal projection methods implicitly treat the replay buffer as a faithful sample of task A's activation subspace. In practice, small buffers undersample boundary regions and low-density manifold directions, leaving holes that task B's gradients exploit. Proactively filling these holes with synthetic samples — generated or interpolated to target underrepresented subspace directions — hardens the constraint before exploitation rather than after. However, synthetic content above roughly 30–40% of buffer capacity introduces mode-seeking artifacts that cause the estimated subspace to shrink below the true task manifold, making the orthogonality constraint overconfident and paradoxically more brittle.

4. Compound subspace drift across many tasks requires cross-task consistency monitoring

No single-task audit reveals the slow accumulation of synthetic artifacts across a long task sequence. Tracking retroactive inter-task subspace angle shifts — measuring whether task A's stored subspace estimate and its current buffer activations subtend a growing angle over time — provides a cross-task signal that is independent of current task geometry and directly measures accumulated corruption. This signal can trigger global subspace recalibration, but recalibration using a corrupted buffer risks crystallizing rather than correcting the error, particularly for early tasks whose real samples have been largely evicted.

5. Buffer eviction policy must optimize for geometric recoverability, not distributional coverage alone

The minimal real-sample set needed to keep a task's subspace recalibratable is geometrically precise: approximately 2k samples spanning the extremal points of the task's convex hull in activation space, where k is the task's effective manifold dimensionality (empirically 15–40 for typical vision encoders). Standard reservoir sampling evicts boundary and interior samples at equal rates, systematically destroying the boundary points that are irreplaceable for subspace recovery. A minimum enclosing ellipsoid eviction policy — retaining support points and evicting interior samples first — preserves recalibratable geometric footprints at minimal slot cost, but imposes fixed per-task allocations that consume a growing fraction of any bounded buffer across long task sequences.

Common Pitfalls
Trusting accuracy as a proxy for representation health. Encoder geometry degrades silently; a model can achieve acceptable per-task accuracy while its latent space has lost the structure that downstream heads and orthogonality constraints depend on.
Treating generative replay as a drop-in solution. Generators reproduce the buffer's distributional gaps, not just its density. Without explicit gap detection before generation, synthetic samples reinforce the holes they were meant to fill.
Freezing layers without auditing gradient starvation. Layer freezing is not geometrically neutral; it displaces conflicting gradient pressure onto earlier layers rather than resolving it.
Using a single threshold for recalibration triggers. Fixed thresholds on violation magnitude are confounded by the degrading subspace estimate itself; Mahalanobis-distance thresholds relative to an early-training baseline are more robust.
Open Question for Deeper Work

If each task requires a fixed geometric footprint of real samples for recalibratable subspace preservation, and buffer capacity is strictly bounded, the system faces a structural allocation problem that worsens with sequence length. The open question is whether dynamic subspace compression — progressively distilling older tasks' activation subspaces into lower-dimensional but geometrically faithful summaries as those representations stabilize — can free buffer slots without sacrificing recoverability. This requires formalizing what "stabilized" means for a task representation under ongoing encoder drift, and whether a compressed subspace summary remains valid as an orthogonality reference when the encoder continues to change around it.






