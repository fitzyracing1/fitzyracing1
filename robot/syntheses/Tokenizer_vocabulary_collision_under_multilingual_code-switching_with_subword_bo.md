Thesis: The dominant failure mode in low-resource multilingual adaptation is not data scarcity alone but a cascade of tokenizer-induced geometric corruptions — fertility spikes, Trojan embeddings, directional merge bias, and tokenization priming — that systematically degrade the embedding space at precisely the linguistic positions where code-switched text carries its highest information density.

Key Insights
1. Over-segmentation degrades embedding geometry differently across language typologies

When a BPE tokenizer trained on high-resource corpora encounters a low-resource morpheme it cannot represent as a single token, each fragment inherits embedding statistics from its high-resource co-occurrence contexts, scattering semantically coherent units across incompatible regions of embedding space. For agglutinative languages like Turkish or Hungarian, this damage is multiplicative: a single word encoding tense, aspect, person, and case may be shattered into 6–10 tokens, each receiving inconsistent gradient updates across morphologically varied surface forms, preventing the root from ever accumulating a stable representation. Rust et al. (2021) quantified this directly, showing that tokenizer fertility above ~2.0 tokens-per-word correlates with significant downstream performance degradation. Isolating languages suffer differently — BPE may merge characters across word boundaries where whitespace cues are absent — but the geometric outcome is the same: anisotropic, low-variance embedding clusters that make cosine similarity unreliable for the target language.

2. BPE's left-to-right merge order introduces directional bias that concentrates at script transitions

BPE's greedy left-to-right merge algorithm systematically produces longer, more coherent tokens for prefixes than suffixes — a bias that is largely invisible in left-to-right languages but becomes catastrophic for right-to-left scripts like Arabic, where morphologically critical person/number/gender information is suffix-final. At code-switch boundaries, this directional bias creates a localized fertility spike — a burst of high-token-count, low-coherence fragments — precisely at the syntactically most informative position in the sentence. Aji et al. (2022) documented asymmetric perplexity behavior in mBART on Arabic-English code-switched text consistent with this mechanism. Critically, aggregate perplexity metrics mask this spike entirely, meaning models can appear competent on benchmarks while systematically failing at switch-point morphosyntax.

3. Positional encoding schemes compound tokenization damage across script transitions

Absolute position embeddings encode syntactic expectations learned from high-resource training distributions, where a given position index predicts specific dependency relations statistically. When a fertility spike expands 3 Arabic words into 11 tokens, every subsequent token receives a position index shifted by 8, inheriting syntactically incorrect priors. Relative encodings (RoPE, Shaw et al. 2018) preserve intra-segment relative distances but still inflate the cross-segment distance spanning the spike, degrading long-range syntactic attention exactly where cross-script dependencies are most critical. The damage is also retrospective: bidirectional encoders corrupt pre-switch token representations when those tokens attend rightward across the spike.

4. Trojan tokens from shared Unicode codepoints create cross-lingual negative transfer

Digits, punctuation, and certain shared codepoints appear identically across scripts and receive a single token ID in multilingual vocabularies. Their embeddings become weighted averages of incompatible distributional contexts across all languages, producing geometrically collapsed vectors that serve no language well — a signature Kementchedjhieva et al. (2023) identified as anomalously high anisotropy in numeral tokens. Since numerals and proper nouns are the most frequent triggers of real-world code-switching, these Trojan tokens degrade representation quality precisely at switch-point lexical items. Fine-tuning on low-resource target data pulls Trojan embeddings toward the target distribution, inadvertently degrading their quality for all other languages sharing that token ID.

5. Tokenization priming creates entity-level label noise invisible to data audits

BPE's merge context is reset at script boundaries, meaning the same romanized surface form receives different token ID sequences depending on its preceding script context. Identical proper nouns or entities can map to [4521, 892] in one context and [4521, 1103, 45] in another, providing contradictory supervision signals for NER span detectors. Entities appearing predominantly in code-switched contexts develop looser, less retrievable embeddings than frequency-matched entities in monolingual contexts — a systematic asymmetry that is undetectable through standard data quality audits and persists even after fine-tuning.

Common Pitfalls
Treating fertility as the only metric: High fertility predicts degradation, but Trojan token collapse and tokenization priming cause severe failures at normal fertility values.
Evaluating on aggregate perplexity: Boundary-localized spikes are washed out by sequence-level averaging; boundary-stratified evaluation is required.
Assuming vocabulary extension fixes underrepresentation: New token embeddings have no geometric relationship to the pretrained manifold and require thousands of unlabeled sentences to stabilize — unavailable in low-resource settings.
Applying document-level tokenization caching as a complete fix: It eliminates within-document priming inconsistency but leaves cross-document inconsistency intact and fails entirely in streaming inference.
Open Question for Deeper Work

Does the asymmetry in entity embedding quality between monolingual and code-switched contexts scale predictably with the ratio of monolingual-to-code-switched occurrences in the pretraining corpus — and if so, can this ratio be used to construct a per-entity "tokenization reliability score" that could guide selective vocabulary extension, targeting only those entities whose code-switched tokenization variance exceeds a recoverable threshold, rather than extending the vocabulary indiscriminately?






