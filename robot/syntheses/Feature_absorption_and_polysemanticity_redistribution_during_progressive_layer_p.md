Thesis: Progressive layer pruning does not simply shrink a transformer — it triggers a cascade of representational reorganization in surviving layers that interacts destructively with polysemanticity, compression, and fine-tuning recovery in ways invisible to aggregate benchmarks until catastrophic failure is imminent.

Key Insights
1. Absorption is mechanistically distinct from rescaling

When a layer is pruned, neighboring layers do not merely rescale their weights to compensate. Genuine feature absorption requires surviving layers to approximate compositions of nonlinear functions previously distributed across multiple layers, which increases the effective rank of their weight matrices. This rank growth is detectable via SVD (new singular value directions emerge) and via probe batteries: linear probes fail where nonlinear probes succeed on absorbed representations, and activation patching distinguishes the two cases cleanly. The distinction matters because rank growth directly conflicts with the low-rank assumptions underlying quantization methods like GPTQ and compression methods like LoRA, making prune-then-quantize pipelines compound their errors in ways neither technique causes alone.

2. Polysemantic interference falls hardest on rare features

Absorption increases representational pressure on surviving layers, and gradient descent during fine-tuning resolves this pressure by exploiting available directions regardless of prior occupancy — the same mechanism that creates polysemanticity in the first place, now amplified by sudden capacity reduction. Crucially, the interference damage is not uniformly distributed: rare tokens and low-frequency syntactic constructions generate insufficient gradient signal to protect themselves during fine-tuning, so polysemantic overloading degrades tail performance while leaving common-case metrics intact. This makes standard benchmarks structurally blind to the damage.

3. Fine-tuning corpus choice is as consequential as pruning algorithm

A low type-token ratio fine-tuning corpus (web crawl data, repetitive instruction sets like Alpaca) provides almost no gradient signal for rare features, leaving polysemantic interference in absorbed layers unresolved for exactly the representations most damaged by pruning. The practical implication is that standard pruning benchmark comparisons — which hold fine-tuning corpus constant — conflate algorithm quality with corpus-algorithm interaction effects. A corpus deliberately enriched in tail distribution, or synthetically constructed by identifying displaced features via activation diffing and generating maximally activating examples, would constitute a principled alternative.

4. SAE-feature distillation is theoretically superior but faces a validity problem

Using the unpruned model's sparse autoencoder feature activations as distillation targets — rather than output logits or raw hidden states — targets semantic geometry rather than basis-dependent linear geometry, which intermediate-representation matching literature suggests preserves rare-feature behavior better than output matching. However, pruning shifts the absorbed layers' activation distribution enough that the teacher SAE dictionary may have near-zero reconstruction fidelity on pruned model outputs before recovery begins. The fix requires either an affine adapter projecting the pruned model's activation space into the SAE's input space, or a second SAE trained on the pruned model to diff against the teacher — but SAE feature correspondence across dictionaries is an open and unsolved problem.

5. Compression ordering is a hidden pipeline variable

Prune-then-quantize and quantize-then-prune produce different effective rank profiles in surviving layers and therefore different downstream compression quality, yet most deployment pipelines treat them as interchangeable. Tracking singular value entropy per layer throughout a pruning schedule would detect rank growth early enough to apply rank-regularizing fine-tuning before damage propagates — but this diagnostic is absent from current tooling.

Common Pitfalls
Trusting aggregate perplexity: Polysemantic overload degrades rare-token performance long before aggregate loss moves; always stratify evaluation by token frequency decile.
Conflating rescaling with absorption: Assuming pruned models are just smaller versions of originals misses the nonlinear reorganization that makes subsequent compression unpredictable.
Ignoring compression ordering: Treating prune-then-quantize as equivalent to quantize-then-prune introduces uncontrolled rank-growth interactions.
Using the unpruned SAE uncritically: Applying the teacher's feature dictionary to pruned-model activations without first measuring reconstruction fidelity risks aligning to an invalid basis.
Open Question for Deeper Work

Can SAE feature correspondence be established across pruning-induced distribution shift? Diffing two SAE dictionaries — one from the unpruned model, one from the absorbed layers post-pruning — requires solving a feature alignment problem complicated by SAE solution non-uniqueness: two valid SAEs trained on related distributions may place equivalent features in arbitrarily rotated directions, making naive cosine similarity matching unreliable. A principled solution would need to establish correspondence up to the known symmetries of SAE training, identify features present in the teacher but absent in the pruned model, and detect genuinely novel entanglements created by absorption — all without assuming a shared coordinate system. Solving this would unlock targeted, geometry-aware recovery fine-tuning and make the entire prune-compress-deploy pipeline auditable at the feature level.






