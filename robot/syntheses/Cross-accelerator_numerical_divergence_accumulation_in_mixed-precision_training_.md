Thesis: Mixed-precision training does not merely introduce bounded random noise — it injects structured, magnitude-dependent, topology-coupled precision errors that compound through optimizer state integration over long runs, and no single mitigation closes all the exposure points simultaneously.

Key Insights

1. The FP32 master weight is not a precision firewall.
Keeping weights in FP32 protects parameter storage but does nothing to correct gradients that arrived already corrupted. BF16's 7-bit mantissa means small gradient values are systematically rounded toward zero before they reach the optimizer; the FP32 accumulator receives a structurally biased input at every step. Over hundreds of thousands of steps, this manifests not as noise but as directional drift — particularly a suppression of updates for parameters with intermittently small gradients — that no amount of careful weight storage can repair.

2. The second-moment estimator is the most precision-vulnerable component of Adam.
Because squared gradients are strictly non-negative, rounding errors cannot cancel across steps the way signed gradient errors can in the first moment. When a small g² value is dwarfed by the current running estimate v_t, BF16 addition rounds the small term away entirely; v_t becomes a biased overestimate that persistently suppresses step sizes for affected parameters. This is the mechanism Dettmers et al. (2022) targeted with block-wise quantization in bitsandbytes, and promoting only v_t to FP32 — without also upcasting gradients before squaring — merely protects a high-precision bucket while pouring quantized liquid into it.

3. Ring-allreduce non-associativity seeds diverging optimizer trajectories across ranks.
BF16 addition is non-associative, and ring-allreduce reduces gradients in a topology-determined order that differs across ranks. Each rank therefore receives a slightly different effective gradient at every step. Because Adam's moment estimators are integrators with long memories (β₂ = 0.999 spans ~1000 steps), these per-step ULP-scale discrepancies compound geometrically rather than averaging out, producing measurable per-rank weight divergence after roughly 10k steps with no self-correcting mechanism, since only gradients — not optimizer states — are communicated across ranks.

4. ZeRO partitioning trades divergence for a stationary noise floor.
ZeRO eliminates inter-rank optimizer state divergence by assigning each parameter's state to exactly one rank, but it relocates the precision problem: the owning rank receives a BF16 reduce-scattered gradient whose corruption is inherited from the non-associative reduction, then broadcasts an updated BF16 weight back to all ranks, meaning gradients in the next step are computed from a quantized weight. The result is a bounded, non-compounding noise floor rather than a growing divergence — a more benign failure mode, but one that interacts with weight decay in magnitude-dependent ways that standard learning rate schedules cannot compensate for.

5. Kernel fusion introduces a compiler- and hardware-generation-coupled precision layer beneath the type system.
Fused optimizer kernels keep intermediate values in registers, where precision is determined by the CUDA compiler's FMA contraction decisions rather than by the programmer's type annotations. This means two semantically identical AdamW implementations can produce ULP-different results across GPU generations (A100 vs. H100) or CUDA versions, because the compiler generates different instruction sequences. This error category cannot be fixed by promoting buffers to FP32 — it lives below the type system — and in heterogeneous clusters mixing GPU generations within a single data-parallel job, it can introduce systematic per-node bias rather than mere non-determinism.

Common Pitfalls
Assuming BF16's wider dynamic range than FP16 makes precision problems negligible; the coarser mantissa creates a higher systematic quantization floor that matters more in long runs.
Promoting v_t to FP32 and considering the problem solved, without auditing whether g² is computed in BF16 before insertion.
Using weight decay applied to the BF16 gradient rather than the FP32 weight, coupling the decay magnitude to quantization noise.
Treating allreduce non-determinism as a reproducibility inconvenience rather than a source of compounding optimizer state bias.
Assuming ZeRO's single-owner design fully solves cross-rank precision problems without recognizing the BF16 broadcast weight feedback loop.
Open Question for Deeper Work

Does the magnitude-dependent precision distortion introduced by BF16 gradient quantization interact with the loss landscape's curvature structure in a parameter-specific way that could be exploited — rather than merely corrected — by designing optimizers that treat the quantization noise floor as an implicit regularizer, and if so, under what conditions does that implicit regularization improve rather than harm generalization?






