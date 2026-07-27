Thesis: Grammar-constrained decoding silently decouples output validity from semantic faithfulness by amplifying small prompt variations into large structural commitments through probability mass collapse, beam trajectory lock-in, and attention miscalibration — producing systems where valid outputs are not reliable outputs.

Key Insights
1. Grammar masks amplify confusion rather than rescue from it

The intuition that grammar constraints prevent bad outputs is wrong in an important direction: constraints eliminate invalid token paths but cannot recover probability mass that has already been flattened across valid alternatives. At structurally critical positions — particularly the first key name in a required object — the surviving token is determined not by the model's semantic understanding at that moment but by the cumulative log-probability trajectory through all preceding structural tokens (braces, quotes, colons), which are semantically content-free. A model that is confused about which key to generate arrives at the key-name position with a flat distribution over valid options; the grammar mask preserves that flatness and forces a low-confidence commitment, which beam search then reinforces through score accumulation. The beginner sees valid JSON; the expert sees that validity and faithfulness have been silently decoupled.

2. Beam diversity collapses under joint grammatical and score pressure

Diversity mechanisms in beam search — including diverse beam search with penalty λ — operate by pushing beams apart at each step, but when the grammar mask produces near-identical valid token sets across all beams, diversity penalties can only push beams onto grammatically invalid paths that are immediately pruned. The result is that all surviving beams converge on the same structural trajectory early in generation, making the output effectively deterministic from a structural standpoint while remaining highly sensitive to prompt surface form, which determines which trajectory gets locked in before collapse occurs.

3. Pre-filling and prompt injection are partial remedies with distinct failure modes

Pre-filling structural tokens improves fidelity by preventing log-probability bleed through structure generation, but introduces attention sink distortion: pre-filled tokens enter the KV cache as high-certainty context, suppressing the model's tendency to copy key names from the prompt because structural scaffolding competes with semantic signal in the same middle-layer attention heads (approximately layers 12–24 in 7B-class models). Conversely, increasing key-name recency and frequency in the prompt recovers fidelity up to a ceiling imposed by distribution truncation: prompt repetition raises the floor of valid-token probabilities uniformly rather than sharpening the peak at the correct key, because attentional miscalibration has already flattened the residual stream at that position. Token budget pressure further hardens this ceiling, as positional and length-penalty terms increasingly dominate semantic attention signal near max-length.

4. Probe-gated logit intervention is the most direct path but faces a training signal problem

Activation steering and residual stream probes offer a more direct route to fidelity recovery than prompt or decoding manipulation because they operate before the grammar mask truncates the distribution. However, reliable schema-confusion probes require schema-counterfactual training objectives — labeling residual stream activations as confused when outputs differ across prompt paraphrases of the same schema — rather than correctness-supervised labels, which conflate genuine confusion with legitimate low-frequency key uncertainty. Schema structure diversity dominates probe generalization over prompt paraphrase diversity, and probes trained on shallow schemas likely exhibit phase-transition failure on recursive or polymorphic schemas at approximately depth 3–4, where the constraint graph topology shifts from tree-structured to graph-structured and the model loses reliable stack-tracking ability, reorganizing its attentional regime around positional rather than semantic signals.

Common Pitfalls
Trusting output validity as a proxy for faithfulness: schema-constrained outputs are frequently structurally valid but semantically wrong in ways no output-level validator can detect.
Assuming beam diversity helps: under grammar constraints, surviving beams are structurally clustered regardless of diversity penalty settings.
Over-relying on prompt repetition: past approximately 3 key-name mentions, induction heads suppress additional occurrences as redundant; recency matters more than frequency.
Deploying shallow-schema probes on deep schemas: probe misfires are silent and occur precisely on the most structurally complex outputs.
Open Question for Deeper Work

Does providing explicit nesting-path breadcrumbs in the prompt — a running trace of the current schema depth and active key context — restore linear separability of the confusion signal in the residual stream for recursive schemas, or does it merely shift the phase transition threshold without changing the fundamental geometry of attentional breakdown at self-referential constraint graph nodes? Answering this requires factorial experiments crossing schema depth with breadcrumb granularity while measuring both output fidelity and residual stream probe accuracy, a design that is currently feasible only for open-weight models under 13B parameters.






