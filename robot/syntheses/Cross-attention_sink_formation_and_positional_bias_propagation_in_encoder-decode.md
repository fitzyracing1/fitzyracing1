Thesis: Cross-attention sinks are not incidental artifacts but load-bearing structures that emerge from softmax's inability to express null attention, are systematically reinforced by standard training dynamics, and become acutely pathological under encoder-decoder length asymmetry — producing over-extraction, hallucination, and miscalibrated information routing that conventional metrics fail to detect.

Key Insights
1. Sinks are a structural consequence of softmax, not a training accident

Softmax cannot assign zero probability mass to any position, so when no encoder position is genuinely relevant, probability concentrates on positionally-biased anchors — typically position 0 and the final encoded position. These sink positions develop anomalously high key-vector L2 norms, which amplifies their logits independently of content. Crucially, the sink is functional: it acts as a null-attention surrogate, and selective suppression via weight decay or regularization relocates rather than eliminates it, because the underlying pressure remains.

2. Longer encoder sequences worsen, not dilute, the sink

Naive intuition suggests more keys should spread attention mass and raise entropy. The opposite occurs: as encoder length grows, additional positions contribute low logit scores that softmax exponentially suppresses together, making the sink relatively stronger. In BART and LED on long-document summarization, first-token attention weights exceeding 40% in individual heads have been observed at encoder lengths beyond 1024 tokens, and cross-attention entropy in early decoder layers decreases with encoder length — a direct inversion of the expected dilution effect.

3. Training reinforces sinks through the gradient path

Sink positions receive consistently large, directional gradients, which Adam's second-moment estimator fails to dampen effectively — accelerating rather than correcting their dominance. The encoder-conditional fraction of gradient reaching cross-attention parameters is small to begin with (estimated below 15-20% at decoder position 1), meaning most of the training signal at early positions teaches next-token frequency prediction rather than encoder-content routing. This feedback loop means sink formation is a trained behavior, not merely an initialization artifact.

4. Teacher forcing prevents cold-start cross-attention calibration

At decoder position 1, the query is formed solely from a learned start token embedding that receives undifferentiated gradient signal across all encoder relevance regimes. Teacher forcing ensures this condition never appears during training in the form the model encounters at inference, so the model never learns to calibrate cross-attention when decoder context is genuinely absent. Interventions like multiple specialized start tokens predictably collapse under gradient pressure because the loss at position 1 provides no contrastive signal to drive embedding differentiation.

5. The failure mode is behavioral over-extraction, not graceful degradation

Models without an explicit abstain mechanism do not ignore irrelevant encoder content — they hallucinate structure from it. Irrelevant or noisy encoder inputs produce confident, fluent outputs that are locally coherent with some encoder span but globally wrong. This is especially acute in retrieval-augmented settings, where retrieval errors compound rather than merely fail to help. Encoder dropout during training partially mitigates this by forcing decoder-only generation, suggesting the over-extraction is a learned dependency rather than an architectural inevitability.

Common Pitfalls
Conflating high attention weight with high information content. Sink positions dominate attention distributions precisely because they are reliable anchors, not because they carry the most relevant content.
Trusting perplexity and BLEU to detect sink pathology. These metrics are largely insensitive to whether information routing through cross-attention is correct, so severe sink formation can be invisible in standard evaluations.
Assuming regularization dissolves sinks. Selective weight decay, gradient clipping, and norm penalties relocate the sink by triggering compensatory growth elsewhere; they do not address the softmax pressure that creates it.
Treating the problem as symmetric. Encoder-decoder cross-attention has no guaranteed relevant position the way self-attention has the current token, making the null-attention problem structurally more acute than in self-attention sink analyses.
Open Question for Deeper Work

If encoder-conditional gradient is demonstrably recoverable via mean-ablation decomposition and is small at early decoder positions, would explicitly upweighting it during optimization improve cold-start cross-attention calibration — or would it create an over-reliance on encoder content that degrades performance when encoder input is noisy or absent? The answer requires jointly measuring cross-attention entropy calibration and task performance across a controlled range of encoder relevance levels, an experiment that cleanly separates the routing improvement from the brittleness risk and which has not yet been published.






