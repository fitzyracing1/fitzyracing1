Thesis: When a multilingual model's tokenizer is built on high-resource language corpora, it structurally impairs low-resource language fine-tuning by inflating subword fertility, diluting gradient signal, and creating cascading representational failures that no amount of data weighting alone can fix — effective intervention requires coordinated choices across vocabulary extension, embedding initialization, layer unfreezing, and gradient aggregation strategy.

Key Insights

1. Subword fertility is the root pathology, not a symptom.
Fertility — the ratio of tokens to words for a given language — directly determines how much semantic content a model can encode per training example. High-resource languages average 1.1–1.3 tokens per word under standard multilingual tokenizers; morphologically rich or agglutinative languages can reach 4–8. This isn't merely an efficiency problem: high fertility forces the model to learn longer-range dependencies to recover structure that other languages encode in a single token, consumes sequence length budget faster, and compounds data scarcity by reducing information density per gradient step.

2. Vocabulary extension is the highest-leverage intervention, but initialization strategy determines whether it helps or harms.
Adding target-language subwords to the tokenizer can cut fertility by 30–50% and is supported by consistent downstream gains in work like MAD-X (Pfeiffer et al., 2021). However, the initialization of new embeddings is high-stakes: random initialization wastes early training steps on repositioning and risks the model routing around new tokens entirely; embedding-space interpolation from existing subwords risks anchoring new tokens in semantically misleading neighborhoods, particularly for morphological categories absent from the dominant pretraining languages. Neither strategy self-corrects without sufficient data — gains largely disappear below critical corpus size thresholds.

3. Adapter-based fine-tuning sidesteps the catastrophic forgetting problem but introduces its own failure mode.
Freezing pretrained weights and inserting trainable bottleneck adapters preserves the cross-lingual alignment built during pretraining, avoiding the 15–30% degradation in related-language transfer that full fine-tuning can produce on small corpora. But adapter rank interacts directly with fertility: high-fertility languages produce morphological fragment tokens with highly correlated gradients, giving the illusion of data volume while delivering low effective sample diversity. Adapters with insufficient rank lack capacity; those with excess rank collapse toward near-identity functions because the data cannot constrain them — ranks in the 16–48 range empirically dominate for high-fertility low-resource languages under ~10K training sentences.

4. Gradient aggregation at the word level recovers signal but assumes boundaries that may not exist.
Whole-word gradient aggregation collapses correlated subword fragment signals into a single update, recovering information density per training step. The approach breaks down for scriptio continua writing systems, polysynthetic languages, and languages where the word is not a coherent morphosyntactic unit — miscollation across incorrect boundaries injects structured noise worse than per-token gradients. Using the model's own hidden-state entropy or attention dispersion to infer morpheme boundaries dynamically is theoretically attractive but risks confirmation bias amplification: early poorly-initialized representations produce wrong boundaries, which reinforce wrong representations, in a self-reinforcing loop. A frozen reference model (analogous to the target network in deep Q-learning) can break this loop but introduces its own warm-up budget tradeoff.

Common Pitfalls
Mistaking token count for data richness. High fertility inflates the apparent size of a training corpus; 10K sentences in a high-fertility language may carry less gradient-accessible information than 3K sentences in English.
Applying adaptive optimizers naively. Adam and Adafactor assign inflated effective learning rates to rare tokens via stale second-moment estimates, producing large noisy updates on exactly the sparse target-language tokens where stability matters most.
Treating vocabulary extension as sufficient. Adding tokens without coordinating embedding initialization, adapter rank, and layer freezing strategy leaves most of the intervention's potential unrealized.
Ignoring activation statistics. Adapter collapse to near-identity functions is invisible in validation loss curves; it requires explicit monitoring of adapter output norms to detect.
Open Question for Deeper Work

The entire intervention stack described here — fertility measurement, vocabulary extension, adapter rank selection, gradient aggregation — requires making decisions before or early in training, yet the quality of those decisions depends on properties of the target language (morpheme boundaries, fertility distribution, embedding neighborhood structure) that are themselves most accurately estimated from a well-trained model. This circularity suggests a deeper question: is there a principled active learning or curriculum framework that could sequence these interventions dynamically, using the model's evolving representations to trigger transitions between adaptation stages, and can such a framework provide theoretical guarantees on convergence when the supervision signal and the segmentation oracle are derived from the same partially-trained source?






