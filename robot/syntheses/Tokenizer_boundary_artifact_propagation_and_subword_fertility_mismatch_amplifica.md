Thesis: Subword fertility mismatch between high- and low-resource languages is not merely a surface inconvenience but a structural defect that propagates through every layer of cross-lingual transfer — corrupting gradient geometry during training, destabilizing attention distributions during adaptation, and ultimately encoding English-prior bias into the very subspaces practitioners attempt to preserve as language-neutral anchors.

Key Insights

1. Fertility mismatch creates systematic gradient asymmetry that compounds across training.
When a Turkish or Yoruba morpheme fragments into 6–8 subword tokens while its English equivalent maps to one, the alignment loss gradient is diluted across the high-fertility side by a factor of roughly 1/n per boundary token. Each training step simultaneously delivers concentrated, high-magnitude updates to English embeddings and weak, diffuse updates to high-fertility language embeddings — a form of implicit representation colonization that accumulates across hundreds of thousands of steps. Rust et al. (2021) quantified this directly: languages with fertility above 3.0 in XLM-R consistently underperformed on NER despite adequate pretraining data, because per-token gradient signal at morpheme boundaries was too weak to form stable cross-lingual attractors.

2. Boundary artifact tokens occupy pathological embedding positions that contaminate the attention stack.
The ▁ prefix markers and split-point residuals produced at subword junctions carry embeddings trained in ambiguous left-contexts — appearing sometimes as word-initial, sometimes as continuation pieces — leaving them in low-density, high-variance regions of embedding space. Because attention is computed over the full sequence, a corrupted boundary token embedding in layer 2 propagates into the key-value pairs of layers 6–12, making the failure mode non-local and invisible to perplexity monitoring while silently degrading token-level task accuracy on NER boundaries, morpheme labeling, and dependency head selection.

3. Adapter-based fertility normalization shifts rather than solves the misalignment problem.
A morpheme-boundary-aware adapter pre-embedding can renormalize sequence length ratios and partially close gradient dilution, but the adapter's output must interface with transformer Q/K/V projections pretrained on subword geometry. The result is positional encoding drift in lower layers: probing studies on adapter-augmented models show improved morphological coherence at layer 6 alongside increased attention entropy at layers 2–3, confirming that the misalignment is displaced into the early attention stack rather than eliminated. The trilemma — between fertility normalization, positional geometry preservation, and representation stability — has no clean architectural resolution.

4. Gradient conflict between alignment and morphological adaptation localizes to specific, dangerous architectural sites.
KFAC-style curvature analysis reveals that conflict concentrates in the token embedding matrix, Q/K projection matrices in layers 2–5, and — most critically — LayerNorm scale and shift parameters in those same layers. LayerNorm parameters are simultaneously the highest-conflict site and the most dangerous to freeze: even a 15–20% shift in γ pushes Q/K dot-product magnitudes outside the softmax regime where pretrained attention heads produce calibrated distributions, triggering cascading renormalization failure across layers 3–6 that probing studies show can decrease intermediate representation quality even as final-layer task loss improves.

5. The "language-neutral" preservation target is itself English-biased, and unsupervised correction is only partially achievable.
The second-moment eigenvectors of the residual stream encode the alignment-critical subspace, but because pretraining corpora are English-dominated, these eigenvectors embed English geometric priors as hard constraints. Intersection subspace methods — computing directions shared across per-language second-moment matrices from monolingual data — recover a less biased target, but Muller et al. (2021) show approximately 20–30% of ostensibly language-neutral directions carry language-family rather than universal signal. Truly unbiased preservation targets likely require typologically balanced synthetic augmentation during pretraining, not post-hoc subspace estimation.

Common Pitfalls
Trusting perplexity as a transfer health signal: fertility-driven representation corruption is invisible to perplexity while degrading token-level task accuracy by substantial margins.
Treating adapter insertion as a complete fix: without co-training lower layers, adapters relocate rather than resolve positional geometry mismatch.
Applying per-layer norm bounds independently: individually bounded LayerNorm updates can compose into large cumulative distribution shifts across layers 2–6 that no single-layer constraint catches.
Conflating language-neutral with English-orthogonal: intersection subspace methods reduce English bias but substitute family-level bias, which is less visible and harder to diagnose.
Open Question for Deeper Work

Can a pretraining regime using synthetically generated languages — designed to span the typological space across morphological complexity, fertility distribution, and word order — produce a second-moment subspace that is demonstrably invariant to real-language typological variation, and if so, what is the minimal typological coverage (number and diversity of synthetic languages) required before the estimated alignment subspace stops improving on held-out cross-lingual transfer benchmarks for unseen morphological types?






