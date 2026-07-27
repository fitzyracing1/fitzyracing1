Here is the synthesis brief:

Token embedding space fragmentation under vocabulary extension with subword boundary misalignment and semantic drift in domain-adaptive continual pre-training

Thesis: Vocabulary extension during domain-adaptive continual pre-training fails not because new token embeddings are poorly initialized in isolation, but because the geometric reference frame they anchor to is simultaneously unstable, namespace-asymmetric, and contaminated by co-training interference — making fragmentation a dynamic systems problem rather than a static initialization problem.

Key Insights

1. The instability is co-training interference, not initialization
The central diagnostic question is whether freezing existing embeddings during early domain adaptation improves new-token geometric coherence — and it does, substantially. This reveals that the primary failure mode is the moving reference frame: new tokens receive gradient signal pointing toward a target that is itself shifting under domain-shifted co-occurrence statistics. If initialization were the dominant problem, freezing (which does nothing to fix initialization) would only marginally help. The fact that it helps significantly implicates the joint-training dynamics as the core pathology. The practical consequence is that interventions targeting initialization quality (e.g., averaging semantic neighbor embeddings) are necessary but insufficient without also stabilizing the reference frame during early training.

2. BPE namespace asymmetry imprints latent geometric structure that vocabulary extension ignores
BPE training produces a latent prefix/suffix namespace asymmetry baked into embedding geometry through asymmetric co-occurrence statistics: prefix tokens appear in sentence-initial positions with characteristic context distributions, while continuation tokens appear exclusively post-prefix with entirely different distributions. When vocabulary extension adds tokens that span original BPE prefix/suffix boundaries — as domain-specific biochemical morphemes frequently do — the new token's embedding receives gradient signal from both namespaces simultaneously, producing geometrically inconsistent embeddings that are neither coherent prefix-space nor coherent suffix-space representations. SciFive (Phan et al., 2021) observed intra-class embedding variance ratios exceeding 2.1× for cross-boundary tokens versus single-namespace tokens, confirming that this namespace contamination is empirically measurable and substantial.

3. Adam moment accumulation transforms the frozen-to-joint phase transition into a re-anchoring lag
When staged training unfreezes existing embeddings after a frozen phase, new-token embeddings exhibit systematic re-anchoring lag: their Adam second moments accumulated under the frozen geometry, encoding the wrong loss surface curvature and suppressing effective learning rate precisely when the largest gradient updates are needed. This lag scales with both the length of the frozen phase and the geometric distance neighbors travel during it. Critically, resetting Adam moments for new-token parameters at the unfreeze boundary produces a smaller loss spike than never freezing — confirming that the accumulated moments were suppressing useful gradient signal rather than encoding useful curvature of the actual domain loss surface.

4. Namespace-encoding dimensions are detectable and surgically neutralizable
BPE namespace identity is recoverable with >95% accuracy using only 8–12 embedding dimensions out of 768 in BERT-scale models, meaning the namespace signal is geometrically concentrated and isolable via linear probing. This enables surgical initialization of cross-boundary tokens by projecting candidate embeddings onto the null space of the namespace-encoding subspace, zeroing the namespace prior while preserving semantic content. However, namespace-encoding dimensions are partially confounded with lexical category dimensions, so full null-space projection risks collateral semantic damage — requiring partial neutralization with tunable projection strength α rather than hard zeroing.

5. Convergence target is determined by temporal ordering of drift relative to new-token gradient receipt
When a domain corpus forces co-occurrence between a newly added token and an existing token whose embedding has already drifted, the new token anchors to the drifted position because that is the only geometric reality it ever observes. PubMedBERT's superiority over BioBERT reflects this: from-scratch domain training gives new tokens a stable, coherent reference frame, while continued pre-training exposes them to neighbors in mid-drift, producing embeddings that are geometrically inconsistent — simultaneously general and domain-specific without being coherent in either register.

Common Pitfalls
Treating vocabulary extension as a static initialization problem and investing exclusively in smarter initialization schemes (mean-of-neighbors, subword composition) while ignoring the co-training dynamics that destabilize any initialization within the first training steps.
Evaluating staged training at intermediate checkpoints after unfreezing, where re-anchoring lag temporarily increases geometric incoherence relative to end-of-frozen-phase state, leading to incorrect conclusions that staged training is worse than joint training.
Assuming the embedding matrix is a uniform geometric space rather than recognizing the latent namespace structure imprinted by BPE training, causing vocabulary extension tools (e.g., HuggingFace add_tokens()) to silently assign new tokens to geometrically inappropriate namespace regions.
Carrying Adam moments across the frozen-to-joint phase boundary without reset or recalibration, converting what should be a clean re-anchoring step into a lagged, damped response that trails neighbor movement by thousands of training steps.
Open Question for Deeper Work

The most pressing unresolved question is whether the collateral damage to lexical category encoding from namespace-neutralizing null-space projection is actually corrective rather than destructive for cross-boundary domain tokens specifically. If domain biochemical morphemes have atypical lexical category distributions relative to general-vocabulary tokens in the same namespace — which is plausible, since terms like ##glycosylation function as nominal suffixes with different distributional profiles than the general-vocabulary continuation tokens they were previously fragmented across — then erasing the inherited lexical category prior may improve rather than harm downstream task performance. No published work has directly tested this prediction, and confirming or disconfirming it would resolve whether namespace-neutral initialization requires the careful partial-projection tuning suggested here, or whether full null-space projection is safe and sufficient for domain vocabulary extension.







Want to be notified when Claude responds?
Notify
