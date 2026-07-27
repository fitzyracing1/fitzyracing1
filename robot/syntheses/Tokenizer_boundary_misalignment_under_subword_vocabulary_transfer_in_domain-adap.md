Thesis: When a general-domain tokenizer is applied to domain-specific text during adaptive pretraining, systematic fertility skew — the inflation of token count per semantic unit — does not merely impose an efficiency cost but structurally corrupts the model's representational geometry, attention head allocation, and downstream fine-tuning capacity in ways that compound across training stages and resist correction by standard fine-tuning alone.

Key Insights

1. Fertility skew produces anisotropic embedding collapse, not generic domain shift.
High-fertility fragmentation causes subword fragments to cluster tightly along low-variance manifolds driven by positional co-occurrence rather than semantic content. This signature — localized anisotropy, elevated intra-word cosine similarity above 0.85–0.90, and a fertility-stratified intrinsic dimensionality gradient measurable via TwoNN estimation — is geometrically distinct from normal domain shift, which produces global translation of the representation cloud without stratified dimensionality loss. The diagnostic is a fertility × dimensionality interaction that survives frequency controls, which pure domain shift cannot produce.

2. Upper transformer layers are displaced from semantic composition toward fragment aggregation.
Under high-fertility pretraining, the layer at which entity-level semantics becomes linearly decodable shifts upward by 2–4 layers, and 20–25% of upper-layer attention heads develop low-entropy fragment-tracking specialization rather than semantic composition roles. This is not free overhead — it constitutes direct capacity displacement measurable via head entropy profiles, and because head specialization is sticky (Merchant et al. 2020), the functional geometry of upper layers is substantially set by the time domain-adaptive pretraining ends, making downstream correction expensive.

3. Fine-tuning routes around displaced heads rather than retasking them.
Gradient signals during fine-tuning preferentially exploit remaining flexible heads rather than overwriting entrenched fragment-tracking heads, because rewriting a specialized head requires traversing a local loss-landscape basin boundary. This routing-around strategy consumes the model's redundancy budget — the same slack Michel et al. (2019) showed allows 20–40% head pruning with minimal loss — meaning high-fertility pretrained models arrive at fine-tuning with a systematically reduced capacity reserve before the first fine-tuning gradient is applied.

4. Budget exhaustion produces a task complexity cliff and objective-ordering sensitivity.
When fine-tuning tasks are complex enough to exhaust the remaining head budget, interference between subtasks manifests as erratic loss oscillation and sharp nonlineear performance degradation. Complexity-first curriculum sequencing — introducing the highest-compositional-depth subtask first to claim the most flexible surviving heads — can recover 3–5% performance, but hits a hard ceiling when fertility damage is severe enough that the residual budget is geometrically insufficient regardless of ordering. This ceiling is the clearest diagnostic that upstream tokenizer repair, not fine-tuning strategy, is the binding constraint.

5. Vocabulary augmentation interventions can propagate distortion if fragment embeddings are already corrupted.
Targeted atomic vocabulary addition for the top 1–5% highest-fertility domain terms is the minimum viable tokenizer intervention, but initializing new token embeddings via static fragment averaging launders positional artifact into the new entries when the source fragments are themselves fertility-damaged. Cross-context centroid extraction at intermediate layers (6–8) partially cancels this artifact by averaging over varied co-occurrence contexts, but cancellation degrades for terms appearing in stereotyped syntactic positions — a structural limit on any averaging-based initialization strategy.

Common Pitfalls
Treating fertility as an efficiency problem only. Practitioners often respond to high fertility by truncating sequences or increasing batch size, missing the representational and capacity consequences entirely.
Using global embedding metrics to assess intervention success. Standard probing for semantic content misses positional-artifact contamination; nearest-neighbor audits must explicitly check for positional-role clustering versus semantic clustering.
Assuming fine-tuning will self-correct tokenizer damage. The stickiness of head specialization and the routing-around behavior of fine-tuning gradients mean that fertility-induced distortions are largely preserved through fine-tuning, not corrected by it.
Applying complexity-first curriculum without auditing residual head budget first. Ordering optimization is only effective when sufficient budget remains; applying it to severely depleted models wastes engineering effort while the real fix is tokenizer intervention.
Open Question for Deeper Work

Does the residual positional artifact in domain terms that occupy stereotyped syntactic positions — gene names always as grammatical subjects, chemical entities always in object position — represent a fundamental limit on averaging-based vocabulary augmentation, and if so, does contrastive re-embedding (explicitly training new token representations to repel positional-role neighbors while attracting semantic neighbors) provide a tractable path past this limit without requiring full tokenizer retraining? Quantifying the fraction of high-value domain vocabulary that falls into this stereotyped-position trap across biomedical, legal, and code domains would establish whether this is an edge case or a systematic barrier to vocabulary transfer in specialized domains.






