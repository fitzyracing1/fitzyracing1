Thesis: When vision-language models are fine-tuned on unimodal task distributions, the cross-modal representational alignment geometry degrades selectively and silently — sparing dominant object-recognition directions while destroying compositional structure — in ways that standard benchmarks cannot detect and that current regularization strategies cannot reliably prevent without solving a circular dependency between probe coverage and direction identification.

Key Insights
1. Collapse is geometric and selective, not behavioral and uniform

Unimodal fine-tuning does not degrade all cross-modal alignment equally. It preferentially destroys the lower singular value directions of the cross-modal alignment matrix — the directions encoding relational, compositional, and attributive structure — while leaving dominant object-co-occurrence directions intact. This selectivity is why behavioral metrics give false reassurance: recall@1 on standard retrieval benchmarks is dominated by top singular value directions, which survive fine-tuning, while compositional benchmarks like Winoground and SugarCrepe, where fine-tuned models drop 20–30% versus minimal degradation on standard recall, probe exactly the dimensions that collapse earliest.

2. Architecture determines where collapse initiates

The location of collapse depends critically on which components receive gradient flow. In LLaVA-style architectures with a frozen language tower, image embeddings drift while text embeddings stay fixed, making the damage asymmetric and invisible to text-side evaluations. Linear projectors are the most dangerous intermediaries: they can remap drifted image embeddings into the language tower's input space in ways that appear locally consistent while destroying nonlinear neighborhood structure. Q-Former projectors offer theoretical robustness through active semantic querying, but lose this advantage when query tokens overfit to the unimodal training distribution.

3. Reliable detection requires geometric diagnostics, not accuracy probes

A diagnostic suite for early-stage collapse must measure cross-modal rank consistency distributions (not mean recall), the ratio of singular value spectra before and after fine-tuning, negation and relation sensitivity in retrieval (which degrades 2–3x faster than object-level retrieval), and cross-modal CKA at intermediate layers. Critically, measurements must be taken at multiple fine-tuning checkpoints, because cross-modal consistency can partially recover late in training through implicit regularization, masking intermediate damage that has already corrupted the projector's calibration.

4. Spectral regularization is theoretically motivated but practically fragile

Explicitly penalizing deviation of lower singular values from their pre-training configuration during unimodal fine-tuning is the most principled intervention, but it requires identifying which directions to protect. Directions worth protecting must be both above the Marchenko-Pastur bulk edge (statistically supported given finite training data) and cross-dataset consistent across compositional benchmarks. Protecting statistically noisy below-bulk directions anchors the model to pre-training sampling artifacts; protecting only within-distribution-consistent directions leaves genuinely compositional but probe-invisible dimensions exposed.

5. Direction identification faces an unresolved circular dependency

Identifying which singular value directions encode genuine compositionality requires a probe set with sufficient compositional coverage — but knowing what coverage is sufficient requires already knowing which compositional axes the model encodes. Unsupervised approaches exploiting cross-modal symmetry, linear interpolation coherence, and cross-scale stability of singular vectors offer a partial escape, but cross-scale correspondence itself requires solving a non-trivial matching problem between models of different architecture and dimension, and the reliability of that matching likely varies by compositionality type in ways not yet characterized.

Common Pitfalls
Trusting unimodal retrieval metrics: High image→image or text→text retrieval performance after fine-tuning does not imply cross-modal alignment is intact; unimodal neighborhood structure is partially reinforced by the fine-tuning task itself.
Conflating behavioral recovery with geometric recovery: Late-training implicit regularization can restore surface performance while leaving projector calibration permanently misconfigured.
Assuming the projector compensates: A trainable projector during unimodal fine-tuning is as likely to amplify collapse as to correct it, particularly when the task signal is low-rank or visually uninformative.
Using a single pre/post measurement: Collapse dynamics — including partial recovery artifacts — are invisible to evaluations that only compare initial and final checkpoints.
Open Question for Deeper Work

Can the cross-scale stability criterion for identifying compositional singular value directions be made computationally tractable and architecturally general — specifically, is there a correspondence method between alignment matrices of different VLM families (contrastive vs. generative vs. Q-Former-based) that is stable enough to serve as a foundation for a model-agnostic compositional direction registry, and would such a registry be transferable across fine-tuning regimes or would it need to be recomputed per model family?






