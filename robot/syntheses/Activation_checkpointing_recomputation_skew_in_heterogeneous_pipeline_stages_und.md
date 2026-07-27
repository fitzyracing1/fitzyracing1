Thesis: Activation checkpointing recomputation is not a uniform tax on training throughput but a stage-local, schedule-sensitive, and memory-state-dependent source of latency variance that compounds with pipeline scheduling decisions to produce throughput degradation, gradient corruption, and dynamic instability that static pipeline schedulers are structurally blind to.

Key Insights
1. Recomputation falls on the critical path when dependency structure forces serialization

Whether recomputation latency is hidden or exposed depends entirely on whether the runtime can overlap recompute kernels with independent backward work. In 1F1B schedules, no such overlap exists — the stage owns one micro-batch at a time and its compute stream is fully occupied, so any recompute kernel injected during backward serializes directly with gradient computation and inflates stage backward time. In interleaved 1F1B, overlap is theoretically possible across chunks but unrealized in Megatron-LM's default implementation because recompute and backward kernels share a single CUDA stream. The critical numerical threshold is whether recompute latency exceeds inter-stage communication latency (50–200µs on NVLink); above this, the stall propagates upstream.

2. PyTorch allocator fragmentation makes recompute latency stochastic and chunk-asymmetric

Transformer MLP activations (128MB+ in fp16 at typical training scales) land in PyTorch's large pool (>20MB threshold), which uses first-fit allocation without compaction. By the time later pipeline chunks execute their backward passes, repeated allocation and freeing of large blocks has fragmented the pool, leaving no contiguous region for recompute buffers and forcing synchronous cudaMalloc calls (50–500µs each). Earlier chunks execute against a clean pool and avoid this entirely. Setting max_split_size_mb to match the dominant activation tensor size prevents split-and-remainder fragmentation but shifts pressure onto smaller tensors, requiring a principled policy over the full recompute tensor size distribution rather than optimization for a single tensor.

3. Increasing micro-batch count can invert throughput beyond a memory-pressure crossover

The conventional Gpipe wisdom that higher micro-batch count M reduces pipeline bubble fraction breaks down under memory pressure asymmetry. More micro-batches means more simultaneously live activations on pressured stages, increasing recomputation frequency per backward pass. If aggregate recompute latency growth exceeds bubble reduction rate, throughput decreases with increasing M — empirically observed as a drop from 47% to 41% MFU in Megatron-LM A100 runs going from M=8 to M=16 on a 70B model. The crossover point is a function of the most-pressured stage's memory profile, which is itself a function of M, making this a coupled fixed-point problem invisible to static schedulers.

4. Non-deterministic recomputation produces stage-correlated gradient corruption

When recomputed activations traverse non-deterministic operations (dropout without enforced RNG state preservation, or floating-point reductions sensitive to memory alignment), the recomputed tensor differs numerically from the original. Stages that recompute more frequently contribute systematically biased gradients per accumulation window — corruption that does not average out across steps and drives parameter drift specifically in high-pressure middle stages. PyTorch's torch.utils.checkpoint prior to version 2.1 did not enforce RNG state preservation by default, making this a live production issue in Megatron-LM runs circa 2022–2023.

5. Corruption detection requires gradient statistics, not reference computation

Detecting stage-correlated gradient corruption in a live run without a clean reference forward pass (which itself requires the memory you lack) must rely on intrinsic gradient tensor properties: per-layer gradient cosine similarity across micro-batches should remain high (>0.95) for uncorrupted stages, while corrupted stages show reduced sign consistency and elevated kurtosis in the gradient distribution. Activation patching (substituting a cached reference activation to measure logit delta) can confirm corruption but requires sparse monitoring schedules (every ~500 steps) to avoid reintroducing the memory pressure that caused the problem.

Common Pitfalls
Treating recompute cost as constant: Profiling a single run and hardcoding stage time estimates ignores allocator-state-dependent variance, making schedule optimizations brittle across training duration.
Optimizing max_split_size_mb for one tensor: Eliminating cudaMalloc spikes for MLP activations without modeling attention score matrices and other recomputed tensors shifts fragmentation rather than eliminating it.
Assuming more micro-batches always helps: Increasing M to reduce bubble fraction without memory-pressure profiling can cross the throughput inversion point and actively harm MFU.
Ignoring RNG state in nested checkpoints: Using preserve_rng_state=False or failing to propagate it through nested torch.utils.checkpoint calls silently corrupts gradients in dropout-containing layers.
Open Question for Deeper Work

Can a runtime scheduler jointly optimize micro-batch count M, checkpoint granularity (which layers to checkpoint vs. cache), and CUDA stream assignment for recompute kernels — adapting all three in response to live allocator fragmentation signals — without requiring a globally synchronous reconfiguration step that itself introduces a pipeline stall? The challenge is that each of these decisions couples to the others: changing M shifts memory pressure, which changes which layers need checkpointing, which changes the recompute tensor size distribution, which changes the optimal max_split_size_mb. A principled solution likely requires a memory-aware pipeline simulator running in a shadow thread with sub-step latency, but no existing open-source framework implements this joint optimization.






