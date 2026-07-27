Thesis: Model editing methods that successfully rewrite a single factual association systematically fail to propagate that change through compositional reasoning chains, because the architectural scope of any tractable edit is narrower than the distributed, multi-layer causal structure that multi-hop inference actually depends on — and current evaluation protocols are not designed to detect this gap.

Key Insights

1. The edit scope / inference scope mismatch is architectural, not incidental.
ROME-style edits patch MLP layers at specific token positions (empirically layers 15–17 in GPT-2 XL) because causal tracing identifies those as the site of direct fact recall. But a two-hop query doesn't re-query that MLP with the original subject token — it operates on an intermediate entity representation produced by the first hop, which activates entirely different weight clusters. The edit succeeds on the direct probe and fails on the compositional probe not because the edit was imprecise, but because the two probes run through genuinely different circuits.

2. Intermediate representations are geometrically contaminated, not cleanly updated.
After a first-hop edit, the intermediate entity in the residual stream is a blended vector sitting between the pre-edit and post-edit attractors — not a clean embedding of the new entity. Hernandez et al.'s linearity findings imply this contamination directly degrades second-hop key-matching in MLP layers whose weights were never touched. Verbalization via chain-of-thought accidentally rescues this by resetting the residual stream to a clean token embedding, which means CoT accuracy on compositional queries overestimates true edit propagation.

3. The second-hop weights themselves are the fundamental bottleneck.
Even with a clean intermediate embedding (via verbalization), the second-hop MLP weights encode associations trained under the old world-model and were never identified as edit-relevant. Knowledge is not stored in isolated (subject, relation, object) triples; adjacent relational facts are encoded semi-independently across overlapping value vectors. No current method — including MEMIT's multi-layer distribution — identifies or modifies these downstream weights, because doing so would require enumerating all compositionally dependent facts, a combinatorially hard problem.

4. Proxy signals for compositional failure are self-defeating under optimization.
Adjacent-relation probe entropy and output distribution KL divergence are tractable pre-screening signals for edit-induced compositional failure. But any proxy signal incorporated into an edit training objective will be optimized away without solving the underlying problem — the optimizer's easiest path is relational collapse (confident, correlated wrong answers) rather than genuine propagation. This destroys the diagnostic utility of the signal and produces failures that are harder to detect than the original unregularized failures.

5. Causal grounding is the necessary condition for valid evaluation, and no current benchmark meets it.
A metric remains informative under optimization pressure only if satisfying it requires instantiating the target property — here, that edited weights are causally load-bearing in the inference circuit for compositional queries. Behavioral probe batteries (CounterFact, MQuAKE) are fixed and finite, making them gameable. Geiger et al.'s causal abstraction alignment offers the right theoretical framework, but no published editing system implements causal verification at scale. Hase et al.'s finding that localization doesn't reliably inform editing further suggests that causal influence and edit effectiveness are measuring different things, undermining even the mechanistic motivation for where edits are placed.

Common Pitfalls
Conflating single-hop and compositional accuracy. Passing direct recall probes is necessary but not sufficient; most editing papers report only single-hop metrics.
Treating CoT accuracy as edit validation. Verbalization rescues second-hop geometry without fixing the underlying weight-level failure; CoT success masks broken inference pathways.
Assuming low probe entropy means consistent reasoning. Entropy reduction is achievable via memorization and circuit suppression, not only via genuine propagation.
Trusting that causal tracing identifies where to edit. The layer most causally influential for recall is not necessarily the layer where editing is most effective or sufficient.
Open Question for Deeper Work

What is the minimum structural description of a knowledge edit that would allow a system to automatically enumerate the full set of compositionally dependent facts that also require updating — and is that enumeration tractable without an explicit external knowledge graph, or does it require the model to have internalized something equivalent to one?






