Thesis: Gradient conflict in multi-objective fine-tuning is not a balancing problem but a geometric incompatibility problem — competing objectives impose irreconcilable curvature structures on shared representation layers, causing optimization to collapse into dominated regions that are worse than any single-objective baseline, and no first-order resolution method can fix what is fundamentally a second-order algebraic constraint violation.

Key Insights

1. Pareto collapse is driven by Hessian anti-alignment, not gradient magnitude imbalance.
The determining factor for whether optimization lands on a valid Pareto front or collapses into a dominated region is the principal curvature alignment between competing objectives' Hessians in shared parameter subspaces. When top eigenvectors of H₁ and H₂ are anti-aligned, any descent step that reduces one loss increases the other's curvature-amplified loss faster than any gradient scaling can compensate. The sharpness of this boundary — why it is a cliff rather than a gradual slope — arises because misaligned Hessians impose saddle structure on each other's loss surfaces, capturing gradient flow in unstable manifolds that pull both objectives away from their individual optima simultaneously. Condition number ratios exceeding ~10–50× between objectives in shared layers empirically correlate with collapse into dominated regions.

2. First-order conflict resolution methods systematically discard the directions both objectives require.
PCGrad, MGDA, and CAGrad all operate on gradient directions and are blind to parameter-space geometry. In shared layers with low intrinsic dimensionality (empirically as low as 200 dimensions for NLP fine-tuning tasks), both objectives concentrate their gradient mass in the same subspace. PCGrad's conflict-free projection removes the shared component — the residual gradient is large only in directions neither task cares about, and tiny or zero in the high-variance directions both tasks compete over. CAGrad and Nash-MTL improve weighting but remain first-order, unable to distinguish contested-but-essential directions from contested-but-redundant ones.

3. Adam actively destroys the curvature signal needed for representational negotiation, driving contested directions to degenerate attractors.
Adam's per-parameter gradient normalization equalizes curvature across directions, removing the signal that would otherwise allow the higher-curvature objective to maintain dominance in contested shared-layer directions. The result is that contested high-curvature directions — the most representationally critical directions for both objectives — converge not to a compromise encoding but to a maximally ambiguous attractor that is decodable by neither objective's downstream circuits. Second-order optimizers (K-FAC, Shampoo) reveal that this collapse is often algebraically inevitable: when the sum of objectives' critical subspace dimensionalities exceeds the effective rank of the shared layer, no optimizer can prevent collapse because the constraint is geometric, not dynamic.

4. Per-objective LoRA adapters displace but do not eliminate conflict — it re-emerges at inference-time composition.
Routing objective-specific gradient updates through separate low-rank adapter subspaces prevents training-time gradient conflict in shared layers, but when adapters are merged or simultaneously active at inference, the representation conflict re-emerges in the residual stream. Naive adapter summation degrades individual task performance by 10–30% (Yadav et al. 2023, TIES-Merging), with interference scaling with subspace cosine similarity. Critically, the merged model's behavior is governed by the frozen base model's geometry, not adapter rank ratios — the base model's value projections determine which adapter's directions survive into subsequent layers.

5. Training order is a hidden geometric variable — the later objective destroys the earlier objective's flat-valley geometry irreversibly.
Pareto collapse is asymmetric with respect to objective introduction order. The second objective's Hessian curves the directions that were flat under the first objective's loss surface, eliminating the restoring force that would have protected the first objective's representations. In RLHF pipelines, the KL penalty is inadvertently performing geometry-repair work — opposing RL curvature's destruction of SFT's flat-valley structure — and when KL coefficients are annealed, capability regression occurs as a threshold phenomenon, not gradually.

Common Pitfalls
Conflating gradient magnitude conflict with curvature conflict. Loss weighting and GradNorm address the former; the latter requires Hessian-level analysis and is not fixed by any scaling method.
Treating Pareto stationarity as Pareto optimality. MGDA guarantees a stationary point in the gradient convex hull, which can be a dominated interior point when Hessians differ by large condition number ratios.
Assuming adapter separation is sufficient. Separate training subspaces do not guarantee separate inference behavior; composition re-introduces the conflict at the residual stream level.
Ignoring training order effects. Evaluating multi-objective fine-tuning only by final joint loss conceals time-asymmetric geometric destruction that ordering-aware analysis would reveal.
Open Question for Deeper Work

Does there exist an optimal curriculum ordering of objectives — derivable from their Fisher information spectra before training begins — that minimizes total geometric destruction across shared layers? If the later objective's Hessian irreversibly curves the earlier objective's flat directions, then the ordering that introduces the highest-curvature objective last should preserve the most geometry for lower-curvature objectives. Whether this ordering is globally consistent (no cyclic curvature dependencies across layer depth) or requires layer-wise curriculum scheduling remains unresolved, and answering it would transform multi-objective fine-tuning from an empirical tuning problem into a principled geometric planning problem.






