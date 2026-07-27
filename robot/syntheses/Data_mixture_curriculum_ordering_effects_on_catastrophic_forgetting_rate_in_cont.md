Thesis: The order in which data mixtures are presented during continual fine-tuning causally shapes both the trajectory and the terminal geometry of catastrophic forgetting — not merely its final magnitude — and this ordering effect persists even under parameter-efficient methods like LoRA, making curriculum design a first-class concern rather than a secondary tuning detail.

Key Insights
1. Forgetting has trajectory, not just magnitude

Catastrophic forgetting is not a single endpoint measurement but a dynamic process with at least two distinct signatures: representational drift (rotation of internal feature geometry away from old-task structure) and decision boundary collapse (overwriting of task-specific output weights). These respond differently to curriculum interventions, and critically, two curricula can produce identical final-checkpoint accuracy while having traversed dramatically different forgetting trajectories mid-training. The basin the model lands in — its sharpness, generalization geometry, and susceptibility to subsequent fine-tuning — is shaped by that trajectory. Checkpoint-only evaluation is therefore structurally blind to curriculum effects that matter enormously at deployment.

2. Curriculum order has a causal signature separable from mixture ratio

Holding mixture ratio fixed while varying order produces detectable differences in backward transfer trajectories, basin sharpness, calibration, and brittleness to downstream adaptation — even when final accuracy converges. The falsification criterion is concrete: if trajectory variance across orderings exceeds seed variance by more than approximately 2×, order is doing causal work. This framing separates curriculum ordering effects from the more commonly studied question of how much replay data to include.

3. Curvature-gated replay can target basin geometry, but threshold calibration is fragile

A mechanistically principled curriculum monitors the empirical Fisher trace as a live curvature signal and triggers old-task replay bursts when sharpening is detected — forcing the optimizer toward flatter basins before it commits to sharp new-task geometry. This approach outperforms fixed-interval replay (roughly 18% forgetting reduction at matched compute in recent work), but the Fisher trace threshold is highly sensitive: miscalibration degrades basin flatness by 3-5× even when accuracy remains stable. Self-calibrating alternatives — relative curvature ratios against an exponential moving average, or PI-controller-style continuous replay rate adjustment — remove the fixed threshold but introduce their own design choices. Critically, global Fisher trace misses layer-wise heterogeneity: forgetting in transformers concentrates in attention layers at roughly 40-60% of model depth, meaning layer-wise Fisher-weighted gradient scaling is needed to avoid missing localized sharpening events.

4. LoRA reduces but does not eliminate curriculum ordering sensitivity

LoRA's low-rank constraint structurally reduces catastrophic forgetting by confining updates to a subspace that is partially orthogonal to old-task representations — but orthogonality is imperfect, especially at higher ranks (r=16 and above), and the subspace itself is order-dependent: early training batches establish the principal directions of the adapter, and later batches cannot easily correct a poorly initialized basis. Curriculum ordering effects scale with adapter rank, approaching full fine-tuning severity at r=64, and compound further in adapter composition settings where sequential adapters must navigate each other's occupied subspaces.

5. Fisher-orthogonal initialization is promising but erosion is the binding constraint

Initializing LoRA adapters in directions orthogonal to old-task Fisher eigenvectors reduces interference from the start, but gradient descent has no native mechanism to maintain that orthogonality during training — significant drift occurs within the first 5-10% of training steps. Mitigation strategies (post-update re-orthogonalization, auxiliary penalty terms, directional learning rate scaling) each trade computational cost against approximation quality. The deeper problem is that new-task and old-task gradients often share directions due to overlapping linguistic structure, meaning enforcing strict orthogonality risks blocking legitimate learning rather than just preventing forgetting.

Common Pitfalls
Evaluating only at the final checkpoint, which masks trajectory-dependent basin geometry differences that predict deployment brittleness.
Conflating mixture ratio and curriculum order as a single intervention, making it impossible to attribute observed forgetting rates to either cause.
Using global Fisher trace as the sole curvature signal, missing layer-wise heterogeneity that concentrates forgetting in specific transformer depth ranges.
Assuming LoRA eliminates the curriculum problem, when in fact rank choice and adapter composition reintroduce ordering sensitivity at scale.
Treating orthogonal initialization as a static fix, without accounting for orthogonality erosion during training.
Open Question for Deeper Work

If new-task and old-task gradients necessarily share directions in weight space due to overlapping linguistic structure, the boundary between "safe to update" and "must preserve" directions is not cleanly defined by Fisher orthogonality alone. The open question is whether this shared subspace can be empirically decomposed — perhaps via dual Fisher estimation on both task distributions simultaneously — into directions where joint curvature is low (safe to update), directions where only old-task curvature is high (freeze or penalize), and directions where both tasks have high curvature (requiring explicit negotiation via gradient projection or loss weighting). Identifying this tripartite boundary empirically, and determining whether it is stable across training or shifts dynamically, would transform curriculum design from a heuristic scheduling problem into a geometry-grounded optimization problem with principled stopping criteria.






