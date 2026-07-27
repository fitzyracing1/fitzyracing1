Thesis: Iterative vocabulary pruning in multilingual models creates a silent, compounding misalignment between the token boundary assumptions encoded in the model's weight geometry and the segmentation the pruned tokenizer actually delivers — a mismatch that is invisible in aggregate perplexity but causes catastrophic transfer collapse in low-resource languages through a cascade that runs from positional distribution shift through mid-layer attention corruption to permanent FFN geometric scarring.

Key Insights

1. Fertility explosion is the primary damage vector, and it strikes non-uniformly.
Pruning shifts the fertility distribution asymmetrically across languages: high-resource languages lose a few merged tokens and absorb the change gracefully, while morphologically rich or script-diverse low-resource languages suffer fertility explosions — a word that was one or two tokens becomes seven or eight. This non-uniformity is the core diagnostic failure point, because aggregate validation loss remains stable while per-language fertility drift silently destroys the positional co-occurrence statistics the model trained on. The damage is not to mean fertility alone; the variance of the token-length distribution matters more, since the long tail of very high-fertility words drives the positional outliers that corrupt mid-layer attention statistics.

2. Attention layers are damaged first; FFN layers accumulate a permanent geometric scar.
Early-to-mid attention layers (roughly layers 2–8 in a 12-layer encoder) carry the tightest implicit priors over token-to-token distance distributions and are immediately corrupted when fertility-driven positional spans exceed the statistical regime seen during pretraining. FFN layers degrade only secondarily — but critically, after extended exposure to corrupted attention outputs, the FFN key subspace re-centers its detection geometry around the corrupted distribution. Surgical attention-only fine-tuning cannot undo this because the FFN value emission remains calibrated to wrong inputs; the only viable recovery is full continued pretraining on a repaired tokenizer, which is expensive precisely because the FFN scar forces re-learning of mid-layer representations from scratch.

3. Morpheme-level fertility constraints are necessary but practically blocked.
Word-level fertility ceilings are insufficient because the damaging distribution shift occurs at the morpheme level — agglutinative suffixes that previously merged into single tokens become sequences of character-level fragments the model has no syntactic priors for, even when word-level fertility looks stable. Morpheme-level constraints require per-language morphological analyzers that most low-resource languages lack. Proxy analyzers trained on related high-resource languages introduce systematically biased errors — failing coherently along language-divergence axes (verbal extensions, applicative and causative morphology, tonal morphophonology) — and produce false confidence failures where the pruning pipeline reports constraint satisfaction while the actual protection logic is inverted.

4. Proxy conflict scores can be inverted into a risk map, but the signal is asymmetric.
The pattern of proxy analyzer errors is itself informative: positions where the proxy segmentation diverges from tokenizer boundaries flag token types most at risk of fertility explosion. This proxy conflict score can be intersected with gradient-based token importance from a small labeled set, but gradient signals become unreliable below ~100 examples for classification and ~300–500 per label type for sequence labeling. Crucially, cross-lingual gradient priors reintroduce the proxy problem at a higher abstraction level — they can invert token retention rankings for grammatical function morphemes that are surface-similar across languages but carry different syntactic loads, anti-correlating with native-language task performance (Spearman ρ as low as -0.31 for verbal morphology in Niger-Congo pairs).

5. Rank correlation between gradient prior and proxy conflict score is the practical safety signal.
Where cross-lingual gradient importance and proxy conflict score agree, they are likely tracking genuine shared morphological structure and the intersection is trustworthy. Where they disagree, the disagreement identifies inversion-prone token types that should be defaulted to maximum retention priority regardless of what either signal individually recommends. This diagnostic is conceptually cheap but computationally requires the same labeled data that makes gradient estimation expensive — a circularity that has no clean resolution in the zero-resource regime.

Common Pitfalls
Monitoring aggregate perplexity instead of per-language fertility drift, missing collapse until task evaluation.
Applying fertility constraints at word level rather than morpheme level, providing false safety guarantees.
Using proxy morphological analyzers without auditing their error patterns against the target language's typological profile, producing systematically inverted pruning decisions.
Attempting attention-only surgical fine-tuning post-pruning, which corrects routing but leaves FFN key geometry calibrated to corrupted inputs.
Conflating mean fertility shift with distribution shift — a 5% mean fertility increase can co-occur with catastrophic tail fragmentation that destroys positional priors for morphologically complex forms.
Open Question for Deeper Work

The rank-correlation safety check between proxy conflict scores and cross-lingual gradient priors is theoretically sound but computationally circular in the zero-resource regime: computing it reliably requires labeled data whose scarcity is the original problem. The open question is whether unsupervised typological distance metrics — derived from WALS or URIEL feature vectors without any task labels — can serve as a sufficient proxy for the rank-correlation signal, effectively replacing the gradient component entirely with a linguistically structured prior over which token types are divergence-prone. If such metrics can predict inversion-prone token categories with sufficient precision, fertility-aware vocabulary pruning becomes feasible without any labeled target-language data, which would represent a genuine practical advance for the roughly 1,500 languages currently represented in multilingual corpora but lacking usable annotation resources.






