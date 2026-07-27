Here is the synthesized brief:

Gradient checkpointing recomputation scheduling under heterogeneous memory bandwidth constraints in pipeline-parallel training

Thesis: In pipeline-parallel training across heterogeneous devices, gradient checkpointing cannot be treated as a static, globally uniform policy — the optimal assignment of which activations to store versus recompute is device-specific, schedule-dependent, and must adapt dynamically to runtime memory pressure, because the cost of getting it wrong is not just wasted memory but pipeline bubbles that compound across every microbatch in the steady state.

Key Insights

1. Recomputation timing is a scheduling problem, not just a memory problem.
In a 1F1B pipeline, recomputation of a microbatch's activations must complete before the backward gradient signal arrives at that stage, not after. The practical trigger is the backward pass of the preceding microbatch, which provides a prefetch window roughly equal to one backward-pass duration. Whether recomputation fits in this window depends on compute throughput and, critically, memory read bandwidth — if weights or activations have been evicted to DRAM or CPU memory, PCIe bandwidth at 25–50 GB/s rather than HBM at ~2 TB/s can inflate recomputation time by 40–80×, inserting bubbles of tens of milliseconds per microbatch that no amount of compute optimization can recover.

2. Device heterogeneity makes the "cheap to recompute vs. cheap to store" classification flip between stages.
An op like attention softmax has ~2 FLOPs/byte of arithmetic intensity, making it bandwidth-bound on an A30 (933 GB/s) and therefore expensive to recompute — better to store it. The same op on an A100 (2 TB/s) crosses the roofline differently and is relatively cheaper to recompute. A globally uniform checkpointing policy therefore systematically misassigns ops: it optimizes for one device class while penalizing others. The correct policy is compiled per device SKU by profiling empirical recompute-cost-per-byte and store-cost-per-byte during warmup steps, then used to build a per-rank policy table that the checkpointing wrapper consults at runtime.

3. The feasible operating point is a 2D frontier, not a single knob.
Relaxing checkpointing (storing more activations) reduces recomputation time but increases HBM occupancy; tightening it does the reverse. The feasible frontier in (checkpoint_fraction, microbatch_size) space is bounded above by device HBM capacity and below by the latency constraint that recomputation must finish within the backward gap. On a 24 GB A30, a single transformer layer at batch size 4, sequence length 2048, hidden dim 8192 already consumes 800 MB–1.2 GB of activations, so the frontier is narrow and CUDA allocator fragmentation — which consumes 10–15% of HBM invisibly — can push a theoretically feasible configuration into OOM in practice. Selective recomputation (Korthikanti et al., 2022) expands the frontier by targeting only high-intensity ops, cutting activation memory ~70% while adding only ~5% recomputation overhead.

4. Dynamic memory pressure requires a fragmentation-aware signal, not naive reserved-memory polling.
torch.cuda.memory_reserved() is misleading because it includes reclaimable freed blocks held by the allocator cache. A reliable pressure signal is active_bytes / (total_HBM - reclaimable_pool), derived from torch.cuda.memory_stats() fields, which measures pressure against memory that is genuinely unavailable to return. When this signal crosses a warning threshold, a tiered response — empty_cache() first for immediate headroom, then incremental policy tightening via a priority queue of currently-stored activations ranked by recompute-cost-per-byte — can prevent OOM without stopping the run. A dead-band controller with separate tighten and relax thresholds is essential to avoid oscillation, which can degrade throughput 20–40% through repeated autograd graph recompilation.

5. Forward-looking allocation simulation is powerful but breaks on external library opacity.
Since activation tensor sizes are statically known from the model config, a forward-looking allocator can simulate the next N alloc/free events and predict the largest contiguous free block at each future step — this is exactly what XLA's memory planner and PyTorch inductor's memory planning pass do for static graph regions. In pipeline-parallel training, the simulation breaks on three fronts: dynamic control flow in eager mode breaks lifetime tractability; multi-stream ordering constraints make simulated free events fire at wrong logical times; and external allocations from NCCL (500 MB–2 GB scratch buffers) and cuDNN workspaces are invisible to PyTorch's allocator. The practical architecture is a hybrid: simulate deterministic tensors statically, reserve a headroom budget for stochastic allocations, and validate against memory_snapshot() every K steps to detect drift.

Common Pitfalls

Treating pipeline bubble cost as fixed rather than as a function of recomputation latency causes practitioners to over-index on memory savings and under-index on scheduling. Assuming peak HBM bandwidth in roofline models — rather than actual sustained bandwidth under concurrent forward kernel load — leads to optimistic recomputation time estimates that miss bubbles in production. Using reserved memory as the OOM signal generates 3–5× more false alarms than active-bytes-based signals on high-activation-turnover workloads. And applying a uniform checkpointing policy across heterogeneous stages is perhaps the most common mistake: it silently pessimizes the slowest device, which then bottlenecks the entire pipeline in steady state.

Open Question for Deeper Work

The dead-band controller and per-device static policies both assume that the distribution of memory pressure events is stationary across training — but in practice, gradient accumulation schedules, dynamic loss scaling, and adaptive batch sizing all perturb this distribution non-stationarily. The open question is whether a lightweight online learning algorithm (e.g., a bandit over the discrete space of checkpoint granularity levels) could track the shifting pressure distribution and adapt the policy faster than a profiling-based approach, while remaining stable enough not to thrash — and what theoretical guarantees on regret would be achievable given the hard latency constraint that policy changes must take effect within one microbatch's forward time.






