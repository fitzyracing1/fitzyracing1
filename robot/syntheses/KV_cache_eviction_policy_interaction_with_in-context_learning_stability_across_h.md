Thesis: KV cache eviction is not merely a systems efficiency problem but a correctness problem — eviction decisions interact with the mechanistic structure of in-context learning in ways that produce silent, distribution-dependent accuracy collapse, and no eviction policy can fully solve this without architectural and scheduling co-design.

Key Insights

1. Prefix-based cache keying is structurally insufficient for ICL protection.
Eviction policies like LRU and prefix-aware schemes (e.g., RadixAttention in SGLang) protect reuse of identical token sequences, but ICL prompts violate the assumption that exemplar utility is localized to a fixed prefix. In a Zipfian prompt-length distribution with exponent ~1.2 (consistent with Azure production traces characterized in Splitwise), the longest 10% of prompts consume ~60% of KV cache budget while representing only ~10% of requests, causing LRU to evict them almost immediately. The result is zero cache reuse for exactly the requests where ICL is most elaborately constructed — and the failure is silent, producing drifted behavior rather than errors.

2. Even perfect eviction policy cannot guarantee ICL stability due to causal architecture.
Standard decoder-only transformers freeze KV projections at compute time, meaning exemplar token representations encode "exemplar given left context only," not "exemplar given full prompt." The query-side attention compensates for this causal blindness, but cached exemplar KV entries are geometrically stale relative to the full sequence. This means prompt caching systems requiring byte-identical, left-anchored prefixes (as documented in both Anthropic and OpenAI's caching APIs) are correct in their constraint, but the deeper implication is that even a perfect cache hit delivers only approximately correct ICL activations, with error growing with semantic distance between cached context and current query.

3. Models maintain a fallback hierarchy of answer mechanisms with a catastrophic threshold.
Drawing on Wang et al. (2022), Todd et al. (2023), and Merullo et al. (2023), at least three mechanisms operate in parallel: induction-head-driven pattern matching (fragile, position-sensitive), middle-layer task vector composition (moderate robustness, requires 2-3 complete exemplars), and late MLP prior association (fully context-insensitive). Eviction is merely costly when induction circuits are disrupted but task vectors remain intact on high-prior tasks; it becomes catastrophic when exemplar count drops below the task vector formation threshold (~2-3 exemplars) on low-prior tasks. This non-linearity explains the empirically observed cliff-shaped accuracy degradation rather than smooth decline.

4. Prompt compression compounds the problem by disrupting induction head circuits.
LLMLingua-style compression discards tokens to fit a budget, but induction heads operate on local bigram structure and relative positional offsets. Compression that breaks these anchors degrades the induction pathway while preserving final accuracy on high-prior benchmarks — masking mechanistic damage. The correct detection methodology requires label-flipped ICL probes, attention entropy measurement via activation patching, and out-of-distribution format transfer tests, stratified by task prior strength. Current compression literature reports only aggregate accuracy, systematically hiding failures on low-prior tasks where induction circuits are load-bearing.

5. Observable proxy signals at serving time can predict eviction risk regime.
Prompt perplexity under the base model (cheap, single-pass), induction head attention entropy on query tokens at early prefill layers, and prompt format regularity together provide a classifiable signal distinguishing "merely costly" from "catastrophic" eviction regimes before committing to an eviction decision. Staged prefill — running the first K layers to extract this signal before completing prefill — is architecturally feasible but creates a new scheduling dependency incompatible with current batch-level eviction decisions in systems like vLLM.

Common Pitfalls
Treating eviction-induced accuracy drop as a latency problem (recomputation cost) rather than a correctness problem (mechanistic ICL failure).
Benchmarking compression or eviction robustness on high-prior tasks (sentiment, NLI) where fallback mechanisms mask induction circuit damage.
Assuming smooth accuracy degradation under eviction; the actual curve is step-shaped due to discrete fallback mechanism switching.
Conflating cache miss rate (a systems metric) with ICL stability (a model behavior metric); they are correlated only weakly under skewed length distributions.
Open Question for Deeper Work

The staged prefill approach surfaces a fundamental scheduling conflict: per-request eviction-risk signals require partial execution before memory allocation, while continuous batching systems make eviction decisions at the batch level across requests simultaneously. The open question is whether a lightweight, layer-zero proxy — something extractable from token statistics or prompt structure alone, before any forward pass — can achieve sufficient discrimination between eviction regimes to make staged prefill unnecessary, and whether such a proxy can be learned efficiently enough to deploy inline in a production serving stack without becoming the new latency bottleneck.






