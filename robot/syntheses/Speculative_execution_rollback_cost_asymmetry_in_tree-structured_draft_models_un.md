Thesis: In tree-structured speculative decoding, rollback cost is not uniform across the tree but grows exponentially with depth, and vocabulary-skewed target distributions systematically concentrate rejections at positions where subtree waste is largest — creating a compounding inefficiency that aggregate acceptance rate metrics conceal and that cascades across quantization, device topology, and memory allocation decisions.

Key Insights
1. Rollback cost is a function of position, not just rejection probability

The fundamental asymmetry is geometric: rejecting a node at depth d in a width-W tree invalidates W^(D−d) candidate tokens of draft compute below it, while the target model has already paid full verification cost for all siblings at that depth. A 30% per-token rejection rate at depth 4 of a width-3 tree means routinely discarding 27 candidate tokens per rejection event. The expert concern is therefore not average acceptance rate but the covariance between rejection probability and subtree size — vocabulary-skewed targets concentrate rejections at shallow nodes (where the draft most frequently misses the target's narrow support), which is precisely where subtree waste is maximized.

2. Residual resampling and unembedding costs scale adversarially with vocabulary skew

The rejection correction step requires an O(|V|) scan to compute the residual distribution regardless of how concentrated p_target is, and vocabulary skew increases rejection rate while leaving scan cost fixed — worsening both terms simultaneously. At the sibling level, each node requires an independent unembedding projection (O(d_model × |V|) per sibling) even though attention over the shared prefix is amortized via tree masking. For LLaMA-3 70B's 128K vocabulary, a width-4 tree that rejects at depth 1 burns approximately 8GB of memory bandwidth on unembedding operations that contribute zero accepted tokens, versus ~2GB for a single-sequence speculative baseline.

3. Tree KV cache memory becomes a non-pageable bottleneck at moderate tree geometries

Tree attention masking requires all candidate nodes to remain KV-resident simultaneously, making speculative tree memory non-pageable in contrast to base context KV which can be managed via PagedAttention. At width-4 depth-4 on LLaMA-3 70B, the tree KV footprint is ~27MB per sequence — modest alone, but non-evictable and growing exponentially with width. The throughput flattening that SpecInfer and Eagle-2 report beyond width 4–6 reflects this memory pressure compressing batch size, which eliminates the parallelism that makes speculative decoding valuable.

4. Eagle-2's dynamic pruning is contingent on feature-conditioning alignment that quantization silently degrades

Eagle-2 sidesteps tree waste by pruning low-confidence nodes using draft confidence as a proxy for target acceptance — a proxy that is only reliable because the draft model is trained on the target's penultimate-layer hidden states, aligning the two models' representation spaces. Post-training quantization of the target shifts penultimate-layer activations most severely (errors compound through residual connections to the deepest layer), miscalibrating both draft token quality and pruning thresholds simultaneously. Bit-width is the dominant axis of degradation; draft models transfer reasonably across quantization algorithms within a bit-width but not across bit-width boundaries, implying a retraining matrix of O(bit-widths × base model variants) that most production deployments quietly ignore.

5. Device topology constraints bind before algorithmic constraints in disaggregated deployments

Eagle-2's hidden state transfer requirement (penultimate-layer activations from target to draft at every speculative step) makes the system's latency profile acutely sensitive to interconnect bandwidth. PCIe 4.0 introduces 50–150 microseconds of round-trip synchronization overhead per speculative cycle — comparable to the draft forward pass itself — while NVLink 4.0 reduces transfer cost to ~0.1 microseconds, making topology the binding constraint in heterogeneous or disaggregated infrastructure. Cross-node deployment over InfiniBand is effectively nonviable without large-batch amortization.

Common Pitfalls
Reporting average acceptance rate as the primary efficiency metric, which aggregates over all tree nodes and hides the depth-dependent cost asymmetry that determines actual throughput.
Deploying Eagle-2 against quantized targets without retraining the draft model, silently miscalibrating pruning thresholds.
Assuming tree KV memory is pageable and failing to account for its non-evictable reservation when sizing batch capacity.
Treating draft confidence as a universal proxy for target acceptance without verifying that the draft was trained against the specific target variant in deployment.
Open Question for Deeper Work

Does a draft model trained on fp16 target hidden states and then itself quantized to match the target's bit-width yield better pruning calibration than a draft model retrained from scratch against the quantized target's activations — and is there a quantization-aware distillation objective that could make a single draft model robust across bit-width regimes without per-variant retraining?






