Thesis: Sink token entrenchment in sparse attention architectures is not an optimization artifact or geometric accident but a functional strategy whereby models externalize learned bias corrections into structurally reliable anchor positions, with consequences for fine-tuning stability, OOD robustness, and the design of long-context inference systems that are poorly captured by existing regularization frameworks.

Key Insights
1. Sparse attention's utility guarantee is architectural, not representational

Sliding window and landmark attention eliminate the O(n²) compute cost but provide no guarantee that the learned attention distribution exploits the permitted sparse structure meaningfully. Under extended sequences, models frequently collapse into degenerate configurations where a small number of positions absorb disproportionate attention mass across heads and layers, rendering the sparsity informationally hollow. The sliding window boundary compounds this: tokens near window edges see systematically impoverished context, and landmark tokens intended as hierarchical aggregators can themselves degenerate into uniform routing targets indistinguishable from global average pooling.

2. Sink formation is mechanistically driven by bias-register externalization

The most durable mechanistic account of sink tokens — supported by value vector norm analysis in LLaMA-family models and ablation studies showing perplexity degradation upon sink removal — is that models learn to store layer-specific bias corrections in the value vectors of structurally reliable anchor positions, then retrieve them by routing attention there. This is not a no-op: sink value vectors carry non-trivial norm and write meaningful content to the residual stream. The model exploits the attention mechanism as a parameter-efficient bias implementation, offloading what could be a learned additive bias vector into the key-query routing system, with position 0 serving as the default register because its rotational penalty under RoPE is zero and its positional reliability across training documents is maximal.

3. Sink identity is determined by training corpus structure, not architecture alone

Which tokens become sinks depends on positional reliability in the training distribution. Models with consistent BOS tokens concentrate sinks at position 0; models trained with packed documents and newline delimiters (e.g., Falcon) develop distributed sinks at delimiter positions; code-trained models recruit syntactic anchors like opening braces. This predicts that OOD prompt formats — system prompts displacing natural anchors, JSON inputs suppressing delimiters — disrupt bias-register retrieval in early layers, producing compounding residual stream errors that manifest as sensitivity to prompt template variation.

4. Pre-norm architecture modulates sink formation through residual write dynamics

Pre-norm transformers (LLaMA, GPT-3, Mistral) make near-zero residual updates structurally cheap, which initially suggested sinks were no-ops, but the correct interpretation is that pre-norm lowers the cost of consistent retrieval rather than null retrieval. Post-norm architectures couple attention output magnitude to normalization statistics, creating gradient pressure against stable sink formation — but this also makes post-norm models harder to train at scale, confounding direct comparison. Sink count scales with head count more than layer count, with later layers showing greater per-head sink diversity as finer bias corrections are specialized across heads.

5. Catastrophic forgetting in fine-tuning is partly mediated by sink disruption

Instruction fine-tuning displaces sink anchors during a transient unanchored period, degrading early-layer bias-register retrieval before new anchors stabilize. This accounts for why capability loss concentrates in long-range coherence tasks and why freezing early layers in LoRA fine-tuning disproportionately preserves base capabilities. EWC fails to protect sink function because its Fisher information approximation operates in parameter space without modeling the distributed, cross-matrix nature of sink-routing circuits. Sink-preserving strategies — attention floor constraints at BOS, controlled sink transfer supervision to new format anchors — are theoretically superior and experimentally testable.

Common Pitfalls
Conflating sparsity with diversity: A model satisfying its attention mask perfectly can still be informationally degenerate if all heads route through the same sink positions.
Treating sinks as no-ops based on downstream metric stability: Value vector norms and ablation perplexity reveal non-trivial content being written; apparent no-op behavior reflects useful bias correction canceling downstream, not null writes.
Attributing sink formation solely to RoPE geometry: The rotational-penalty-free origin contributes but gradient-variance dynamics, training corpus structure, and residual stream write costs are jointly necessary explanations.
Applying EWC to protect fine-tuning without modeling functional circuits: Standard regularization protects parameters proportional to Fisher importance, missing the distributed sink-routing circuit that spans Q, K, V, and O projections simultaneously.
Open Question for Deeper Work

If semantically null anchor tokens (special delimiters) produce better fine-tuning generalization than semantically loaded anchors (e.g., "Assistant:") because the latter conflates bias-register retrieval with content routing, this implies an optimal fine-tuning template design principle: reserve dedicated, semantically vacuous tokens exclusively for sink function. The open question is whether this principle extends to landmark attention — can explicitly designated landmark tokens be prevented from degenerating into bias registers by architectural constraints (e.g., value vector norm penalties on landmark positions), and if so, does this recover the intended hierarchical routing behavior at scale?






