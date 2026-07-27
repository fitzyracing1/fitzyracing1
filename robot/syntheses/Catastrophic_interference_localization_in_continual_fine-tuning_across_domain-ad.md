Thesis: Domain-adjacent task sequences are more dangerous than domain-orthogonal ones not despite their similarity but because of it — shared representational surfaces concentrate gradient updates in high-Fisher-mass parameter regions, producing silent, localized degradation that aggregate metrics mask, while the correct interventions must be selected and sequenced according to computable geometric properties of the tasks themselves.

Key Insights
1. Fisher subspace overlap predicts interference, but diagonal approximations deceive

The element-wise overlap of Fisher information matrices — measurable as a Jaccard-like ratio over parameter importance — is the primary pre-training signal for anticipated interference. However, diagonal Fisher misses correlated parameter blocks, particularly in attention head weight matrices. Kronecker-factored (KFAC) Fisher estimates and principal subspace alignment via canonical correlation between top-k eigenvectors provide a substantially more reliable pre-training forecast, with high subspace alignment predicting significant T₁ degradation even when diagonal overlap appears modest.

2. Interference localizes to final layers, not where Fisher alignment is highest

When early transformer layers show high Fisher alignment and late layers show near-zero alignment, degradation concentrates in the final two to three layers — precisely because those layers are unprotected by gradient co-alignment and are overwritten by T₂'s unconstrained updates. Early layers, counter-intuitively, are self-protecting: high Fisher alignment means both tasks tolerate similar update directions. Regularization budget — whether EWC penalties, LoRA rank, or adapter insertion — should therefore concentrate on late layers, not early ones where freezing is largely wasteful.

3. Adversarially adjacent tasks break early-layer self-protection via gradient anti-alignment

Task pairs that share surface statistics but require opposing compositional operations — such as standard NLI paired with entailment-reversal tasks — can force destructive interference specifically in early layers responsible for negation and syntactic scope. The detectable pre-training signature is negative gradient cosine similarity (below −0.2) in early layers combined with high Fisher mass overlap, flagging confident, mutually destructive updates. A 500-step probe run measuring CKA drift in early layers provides a cheap diagnostic catching this failure mode before full fine-tuning.

4. Gradient projection is the efficient intervention for short chains, with a computable viability threshold

Online gradient projection onto the orthogonal complement of T₁'s gradient subspace — constructed at rank 20–50 via randomized SVD — neutralizes anti-aligned components at roughly 3% of EWC's memory cost while recovering comparable T₁ performance. However, projection degrades as fine-tuning chains lengthen: cumulative CKA drift from pretrained activations exceeding approximately 0.35 in any early layer marks the threshold beyond which the protection basis is too misaligned with the current model's operating subspace to be reliable. This threshold is computable by extrapolating per-stage drift from a two-task pilot run.

5. Beyond the drift threshold, LoRA isolation shifts the problem to rank allocation and subspace collision

LoRA adaptors isolate task-specific directions in low-rank subspaces whose minimum safe rank is readable from the singular value decay of the fine-tuning weight delta ΔW, typically rank 8–32 for domain-adjacent tasks. Composition risk arises not from insufficient rank but from subspace collision between T₁ and T₂ adaptor A matrices, detectable via principal angles (dangerous below ~15°). TIES-merging's magnitude-based pruning before composition recovers most per-task performance, but B matrix initialization asymmetry creates artificial subspace correlations that principal angle analysis alone cannot catch.

Common Pitfalls
Trusting aggregate metrics: T₁ accuracy may drop only 5–10% while early-layer representational fidelity collapses 40–60% on specific subpopulations — always probe layer-wise CKA, not just held-out task accuracy.
Freezing early layers by default: In domain-adjacent sequences, early layers are self-protecting; freezing them wastes capacity without reducing interference where it actually occurs.
Assuming Fisher overlap implies safe ordering: High Fisher overlap with positive gradient alignment is safe; high overlap with negative alignment is the adversarial case and requires active intervention.
Using gradient bases from heavily fine-tuned models: Optimizer artifacts distort gradient subspaces; activation-derived or dual-basis constructions anchored to pretrained geometry are substantially more reliable.
Open Question for Deeper Work

Can a task-ordering algorithm over T₁…Tₙ simultaneously minimize cumulative Fisher subspace collision and cumulative CKA drift from pretraining — and when these two criteria conflict, which dominates actual end-of-chain performance? The ordering that minimizes Fisher overlap may not minimize representational drift, and the relationship between these two objective landscapes remains uncharacterized both theoretically and empirically across chain lengths greater than four.






