Thesis: Attention sinks are not a passive symptom of context length degradation but an active causal mechanism — a trained escape valve that monopolizes head capacity, corrupts middle-layer entity-binding computations, and triggers a compounding failure cascade that long-context fine-tuning patches superficially without repairing the underlying routing pathology.

Key Insights
1. Sink formation is a learned positional strategy, not a model defect

Token 0 becomes an attention sink because softmax attention cannot represent abstention — it must distribute probability mass even when no key is semantically relevant. During pretraining on short contexts, the model discovers that routing surplus weight to a fixed, positionally stable anchor is cheaper than learning uniform suppression. RoPE-based models (LLaMA, Mistral, Falcon) reinforce this: token 0's geometric neutrality in angular space makes it a consistently low-competition target. Critically, Xiao et al. (2023) showed that the sink attaches to positional identity, not token content — swapping token 0's content preserves sink behavior entirely. This means sink formation is a hardcoded attractor baked in by billions of training steps, not a correctable edge case.

2. Sink severity exhibits a phase transition, not monotonic growth

Sink mass — the fraction of attention weight on sink tokens — is non-linear with context length. In LLaMA-2 7B, sink mass across layers 4–16 slightly decreases between 512 and 2048 tokens as RoPE's angular geometry spreads attention across more high-similarity neighborhoods, then spikes sharply beyond 4096 tokens as rotary angles wrap into incoherent extrapolation territory. This phase transition means models evaluated at 4K tokens appear healthy while sitting one threshold away from catastrophic sink amplification — perplexity-based evaluations miss this entirely because late-layer fluency remains intact through the transition.

3. Layer-wise damage is non-uniform: middle layers fail first

Sink heads concentrate in early-to-middle layers (roughly layers 2–12 of a 32-layer model), which are responsible for positional bookkeeping and entity-position binding. When sink mass spikes at extrapolation boundaries, middle-layer binding computations — subject-attribute association, coreference, entity tracking — degrade first. Late layers performing semantic composition and next-token prediction remain relatively functional, which is precisely why perplexity stays reasonable while NIAH retrieval collapses. The failure is not diffuse: it targets the specific computational stratum responsible for maintaining coherent referents across long distances.

4. Long-context fine-tuning installs a late-layer patch, not a middle-layer repair

Standard long-context fine-tuning recipes (LongLoRA, continual pretraining on long documents) primarily grow late-layer veto circuits and strengthen parametric memory substitution rather than repairing corrupted middle-layer routing. The residual stream at the middle-to-late boundary carries actively wrong entity-position bindings — not absent signal — making late-layer correction harder than gap-filling. This is detectable via layer-freezing ablations and attention-pattern probing: if freezing late layers during fine-tuning collapses long-context gains while freezing middle layers does not, compensation rather than repair is the dominant mechanism.

5. The capacity tax on late layers degrades chained reasoning superlinearly

Veto circuits recruited in late layers cannibalize heads previously performing compositional reasoning — likely including name-mover and S-inhibition heads identified in IOI circuit analyses. The damage is asymmetric: chained multi-hop reasoning (where step N's output is step N+1's input) suffers compounding residual stream noise at each handoff, degrading as approximately (1−ε)^k for chain length k, while parallel independent lookups pay the capacity tax only once each. This explains steeper-than-expected performance cliffs on Musique and 2WikiMultiHopQA in long-context fine-tuned models, independent of context length effects.

Common Pitfalls
Using perplexity as a long-context health metric. It measures late-layer next-token prediction, which remains intact while middle-layer retrieval collapses silently.
Conflating StreamingLLM-style sink preservation with context repair. Stabilizing softmax normalization by keeping sink tokens does not restore the routing capacity those sink heads are consuming.
Evaluating long-context fine-tuning only on retrieval benchmarks. This misses the compositional reasoning regression incurred by late-layer capacity cannibalization.
Assuming monotonic sink growth with context length. The phase transition means intermediate-length evaluations structurally underestimate extrapolation vulnerability.
Open Question for Deeper Work

Does chain-of-thought prompting — by externalizing intermediate reasoning steps into the context window — partially offload residual stream handoff failures onto the attention mechanism's ability to retrieve from generated tokens, and if so, does CoT's effectiveness collapse at exactly the context lengths where sink mass phase-transitions? If true, this would establish a precise, mechanistically grounded prediction: CoT should provide reasoning gains up to the sink-transition threshold and then fail sharply, not gradually — a testable signature that would simultaneously validate the phase-transition model and expose a critical brittleness in CoT-dependent deployment at long contexts.






