Thesis: Additively merging task-specific LoRA adapters into a shared base model is not a neutral superposition operation — it is a geometric collision whose severity is determined by subspace overlap, domain skew, and training dynamics, and managing it requires rethinking rank allocation, training order, and merge procedure simultaneously.

Key Insights
1. Interference is geometric, not just statistical

The fundamental problem is that LoRA constrains each adapter's update to a low-rank subspace of the full weight matrix, and additive merging assumes those subspaces are orthogonal — an assumption that is almost never met. When two adapters' column spaces overlap, their merged update ΔW₁ + ΔW₂ produces a combined matrix that satisfies neither task's objective, and in the worst case the shared directions cancel entirely, producing rank deficiency in the merged update. The diagnostic tools are weight-space signatures computed before any inference: principal angles between singular vector subspaces, magnitude-weighted sign conflict rates (above ~40% in top-magnitude parameters predicts >3 point degradation), and the numerical rank of the summed update compared to the sum of individual ranks.

2. Domain skew makes interference asymmetric and structural

When one domain dominates the fine-tuning corpus, its adapter occupies the highest-variance directions of the weight matrix — directions that are richest precisely because the pretrained model already concentrated its representations there. The minority adapter, trained with weaker gradient signal, cannot find genuinely orthogonal directions and instead clusters near the majority subspace, producing asymmetric interference where minority-task performance degrades disproportionately. This is not a noise problem; it is a structured geometric displacement problem.

3. Rank is the wrong resource to ration — gradient signal quality is the binding constraint

The intuitive response to minority-task degradation is to allocate more rank to the minority adapter, but this backfires: additional rank vectors must be orthogonalized against the already-entrenched majority subspace, leaving the minority adapter with more dimensions concentrated in low-variance residual directions. The correct intervention equalizes gradient signal quality first — via upsampling, per-adapter learning rate scaling, or gradient reweighting — and then uses lower rank for the minority adapter to force concentration into its single best available direction. AdaLoRA's finding that rank should track singular value importance, not task priority, supports this principle empirically.

4. Training order creates hidden coupling that survives the merge

When adapters are trained sequentially, the later adapter implicitly bends its subspace around the earlier frozen adapter's directions. This coupling is detectable as anomalously low residual alignment between the adapters' B matrices, but it breaks at merge time because the base model receiving the merged update no longer has the earlier adapter pre-applied. Dependency-aware merge procedures — such as RegMean-style regression over activation statistics — recover 2–8% of lost performance by correcting for this coupling, but require activation data from both domains, which is unavailable in privacy-sensitive or federated settings.

5. Post-merge recovery is efficient but structurally limited

Rank deficiency in the merged update can be partially recovered through 200–500 steps of fine-tuning a fresh low-rank adapter on top of the merged model, using balanced domain data and knowledge distillation from the original pre-merge adapters rather than hard labels. This recovers 70–85% of the performance gap with 2–4x better sample efficiency than label-based recovery. However, recovery should be scoped to a new adapter rather than modifying merged weights directly, to avoid re-introducing interference in directions the merge handled correctly.

Common Pitfalls
Treating interference as catastrophic forgetting. Forgetting is sequential; interference is simultaneous and geometric. The remedies differ fundamentally.
Giving the minority adapter more rank. This compounds the problem by creating more vectors competing for residual subspace.
Freezing both adapters simultaneously. The minority adapter should be frozen earlier, at or before validation loss plateau, to prevent overfitting from baking noise into the merge.
Ignoring weight-space diagnostics. Principal angle analysis and rank deficiency checks are fast and data-free, yet absent from standard merging libraries.
Single-domain recovery fine-tuning. Fixing minority-task degradation with minority-domain data alone re-introduces the original interference pattern.
Open Question for Deeper Work

At what point does a stacked structure — base model plus merged adapter plus recovery adapter — become functionally equivalent to a single higher-rank adapter trained from scratch on balanced data? If the equivalence holds, it implies that multi-adapter merging is an inefficient approximation of joint training, valuable only when data cannot be pooled. Establishing the precise conditions under which merging dominates joint training (or fails to) would clarify whether adapter merging is a principled architectural strategy or an engineering convenience that accumulates hidden costs with each additional layer of low-rank structure.






