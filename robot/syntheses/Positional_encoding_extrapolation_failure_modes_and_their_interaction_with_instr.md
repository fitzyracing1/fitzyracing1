Thesis: Positional encoding extrapolation does not degrade model behavior uniformly — it selectively amputates the long-range attention circuits that underpin instruction-tuned behavioral constraints, producing a failure regime where fluency is preserved while safety-critical behaviors quietly erode, and this erosion is further shaped by refusal style, turn position, and conversational accumulation dynamics in ways that standard benchmarks almost entirely miss.

Key Insights

1. Extrapolation failure is architecturally scheme-dependent and selectively targets constraint circuits.
Learned absolute embeddings fail catastrophically at the hard boundary of their lookup table. ALiBi degrades gracefully for perplexity but inverts authority hierarchy by geometrically de-weighting distant system prompts. RoPE creates the most dangerous failure mode for instruction-following: high-frequency aliasing scrambles the mid-range positional signal that refusal circuits depend on while leaving local fluency intact. The result is that format adherence — implemented via local induction heads — survives extrapolation far longer than refusal behavior, which requires reliable cross-segment attention bridging the system prompt and user turn. This stratification means a model can pass format-compliance evals while its refusal gate operates at substantially degraded fidelity.

2. Behavioral constraints occupy distinct positional cost tiers in the residual stream.
The three primary classes of instruction-tuned behavior recover asymmetrically under RoPE extension methods like YaRN: format adherence recovers readily because it is positionally cheap (local circuits, high-frequency components); persona consistency recovers partially, drifting around 16K tokens even when perplexity is flat; refusal behavior is the most fragile, requiring both low- and mid-frequency RoPE accuracy to maintain the cross-segment compositional operation that fires the refusal gate. This hierarchy reveals that safety-critical behaviors are disproportionately encoded in the positionally expensive, long-range circuits that extrapolation methods sacrifice first.

3. System-prompt positional authority is a learned geometric property, not a logical rule.
Role tokens establish distinct residual stream subspaces during SFT and RLHF: system-prompt-position constraints encode in a persistent "context frame" attended to by refusal-critical heads, while identical constraints in human or assistant turns are processed as conversational moves subject to negotiation. In multi-turn conversations, accumulation of assistant-turn tokens progressively shifts query vectors toward the assistant subspace, diluting system-prompt key retrieval at a measurable rate of roughly 3–7% per 1000 assistant-turn tokens — and compliant, helpful outputs accelerate this drift faster than neutral ones.

4. Refusal style and KV-cache position interact to determine durability.
Terse refusals preserve the authority gradient by minimizing compliance-language contamination of the assistant subspace; hedged refusals flood the residual stream with helpfulness signals that project onto the compliance attractor despite surface-level refusal content. Crucially, refusals co-registered with the system prompt in early context — within its intact positional geometry — exhibit roughly an order of magnitude greater durability than late-context refusals, which are positionally orphaned and decay within ~512–1024 tokens. The most important refusals for long-context robustness are therefore the earliest ones, on the least-escalated prompts.

5. System-prompt repetition helps until it becomes a pattern-completion signal.
Periodic system-prompt injection at ~4K token intervals extends refusal-circuit coverage by creating multiple positional anchor points. However, paraphrased repetition risks semantic cancellation of constraint vectors; verbatim repetition beyond 4–6 copies activates induction heads that treat the recurrence as content to complete rather than a constraint to enforce. The crossover from reinforcement to interference marks the point where the model reclassifies standing instructions as episodic conversational content.

Common Pitfalls
Treating perplexity as a proxy for behavioral integrity: perplexity can remain flat while refusal-gate fidelity has collapsed.
Assuming RoPE extension methods repair all circuits equally: format compliance recovering does not imply refusal behavior recovering.
Using hedged refusals for UX reasons without recognizing the mechanistic cost: kindness in refusal phrasing directly trades off against durability.
Ignoring turn count as a security-relevant variable: red-teaming only early turns misses the authority-drift regime entirely.
Open Question for Deeper Work

Can synthetic few-shot refusal exemplars embedded directly in the system prompt serve as durable positional anchors that inoculate against late-context authority drift — and if so, at what specificity level must the exemplars operate to avoid over-triggering refusal behavior on legitimate requests that share surface features with the refused categories? This question sits at the intersection of positional geometry, few-shot circuit activation, and the false-positive cost of over-constrained systems, and remains largely unaddressed in the published literature.






