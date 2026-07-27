Thesis: Tokenizer fertility mismatch — the systematic over-segmentation of high-fertility languages by English-dominant BPE vocabularies — does not merely degrade fluency but creates structured, measurable failures in instruction-following alignment that are invisible to standard safety evaluations and compound across every stage of the SFT and RLHF pipeline.

Key Insights
1. Fertility mismatch dilutes constraint signal during fine-tuning

When SFT loss is averaged over token sequences, semantically identical instruction-response pairs in Amharic (fertility ~2.5–3× English) contribute proportionally weaker gradient signal per constraint token than their English equivalents. The instruction portion shrinks as a fraction of total sequence loss, meaning the model is effectively trained to minimize fluency loss at the expense of constraint internalization. This is not a resource problem — it occurs even with large multilingual datasets — because the loss weighting architecture is calibrated to English token densities and never adjusted per language fertility tier.

2. Erratic subword segmentation creates brittle, tokenization-dependent alignment

Fertility-normalized loss weighting, the intuitive fix, introduces a new failure: for languages where BPE over-segmentation is semantically unpredictable (morphological suffixes split arbitrarily across subword boundaries in Tamil or Yoruba), upweighting amplifies noise tokens alongside signal tokens. The model learns to associate constraint-following with surface tokenization accidents rather than semantic content, producing alignment that is paraphrase-sensitive at the sub-lexical level — two phrasings a native speaker considers identical can trigger different constraint adherence based solely on subword boundary shift.

3. Differential transfer creates a deceptive alignment surface

Cross-lingual transfer from English SFT is not uniform across constraint types. Refusal and safety constraints transfer at roughly 40–60% even in low-resource settings; format, length, and epistemic hedging constraints transfer below 20% for agglutinative high-fertility languages. This asymmetry means a model can pass standard safety benchmarks in Tamil or Amharic — because coarse refusal behavior is intact — while systematically failing within-compliance behavioral constraints: producing overconfident medical answers, omitting scope qualifications, and dropping uncertainty markers in ways that constitute genuine alignment failures invisible to binary safety audits.

4. Back-translation delta is a measurable alignment proxy

The smoothing effect of back-translation — where translating a target-language response back to English inserts hedges, qualifications, and constraints the original lacked — can be operationalized as a Back-Translation Alignment Gap (BTAG) score. High BTAG indicates the translation model performed behavioral repair, directly quantifying within-compliance misalignment without requiring fluent human evaluators in every target language. BTAG is internally validated by the expectation that it reproduces the constraint-category transfer hierarchy: near-zero for refusal (nothing to repair) and highest for epistemic hedging and format constraints (most under-transferred).

5. No fully automated protocol is sufficient, but targeted automation makes human audits tractable

Surface-feature extraction (hedge density, epistemic marker frequency, sentence boundary patterns) can flag distributional failures at scale without semantic comprehension of target-language text. Back-translation judging adds a semantic layer catching roughly 70% of gross behavioral failures. Together these make human spot-audits targeted rather than exhaustive — directing fluent evaluator attention to specific constraint categories and language pairs where divergence scores exceed threshold, rather than requiring comprehensive fluent coverage of every deployment language.

Common Pitfalls
Conflating fluency with alignment: A model generating fluent Swahili is not necessarily well-aligned in Swahili; representational capability and instruction-following calibration are independently learned and independently degraded.
Treating fertility normalization as a complete fix: Upweighting by fertility without accounting for intra-language segmentation variance amplifies noise and creates brittle, boundary-dependent alignment.
Over-relying on LLM-as-judge for cross-lingual evaluation: Judge models share the same differential transfer failures as the models under evaluation and will systematically miss within-compliance misalignment in high-fertility languages.
Assuming safety benchmarks cover behavioral texture: Published multilingual safety benchmarks measure harmful content production, not epistemic constraint maintenance — a model can ace every benchmark while being structurally overconfident in Amharic.
Open Question for Deeper Work

BTAG and surface-feature audits are both anchored to English behavioral norms, measuring misalignment as divergence from what the model would produce in English. This assumes English alignment is the correct target — but well-aligned behavior in Amharic or Tamil may legitimately differ in epistemic register, politeness structure, and uncertainty expression due to cultural-linguistic norms rather than training failure. Constructing norm-relative alignment standards for high-fertility languages — defining what correct within-compliance behavior looks like in those languages specifically, independent of English as ground truth — is the foundational unsolved problem on which the validity of every measurement protocol described here ultimately depends.






