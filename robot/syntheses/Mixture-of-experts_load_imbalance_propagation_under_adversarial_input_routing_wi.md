Thesis: MoE load imbalance is not a routing misconfiguration problem but a systems-level failure mode in which gradient distortion, auxiliary loss geometry, hardware topology, and pipeline scheduling interact to create self-reinforcing collapse attractors that are invisible to standard per-layer utilization monitoring and persist through model distillation into downstream deployments.

Key Insights

1. Dropped token gradients actively reinforce overloaded experts.
When tokens are dropped at a saturated expert and passed through the residual bypass unchanged, the router receives a gradient computed on an unprocessed representation — and if that representation accidentally reduces the downstream loss, the router is rewarded for the very assignment that caused overflow. The auxiliary load-balancing loss (α ≈ 0.01 in Switch-Transformer, 0.001 in ST-MoE) operates on routing probabilities in expectation and is too smooth to counteract this per-token gradient signal, particularly when input batches are semantically homogeneous. Overflow tokens rerouted to second-choice experts corrupt those experts' gradient signals identically, propagating the distortion across the expert graph in a cascade that is structurally invisible to per-layer routing entropy metrics.

2. The z-loss and load-balancing loss jointly create a degenerate attractor.
The router z-loss (penalizing log-sum-exp of logits, α_z ≈ 0.001) and the auxiliary load-balancing loss share a joint minimum at the configuration where all router logits are small and equal — a degenerate state where the softmax is maximally uniform and the router is informationally inert. This configuration is not merely a theoretical concern: it is a genuine attractor in distributed training because uniform routing minimizes all-to-all communication variance, making the system run faster near the degenerate point and causing wall-clock-based monitoring to misidentify collapse as convergence. Escape requires the task loss gradient to dominate, which fails during late training or on easy batches when task loss curvature is locally small.

3. Expert-choice routing trades load balance for causal incompatibility.
Expert-choice routing guarantees per-batch load balance by construction but introduces orphan tokens — those selected by no expert — whose representations stall at residual stream values with no gradient accountability. More critically, expert-choice requires scoring all sequence positions before routing, making it causally incompatible with autoregressive inference. Systems that train with expert-choice and deploy with token-choice routing face a qualitative train-inference mismatch: expert weight matrices encounter activation distributions they were never trained on, with instability concentrated precisely in the layers where specialization is sharpest.

4. Out-of-distribution tokens cause LayerNorm-mediated FFN instability that propagates independently of routing.
Specialized experts develop LayerNorm γ/β parameters calibrated to their specific activation subspace. OOD tokens receive miscalibrated normalization, pushing SwiGLU gate activations into untrained regions and potentially producing bf16 overflow (>65504) that injects high-magnitude vectors into the residual stream. These spikes distort attention logit scaling at subsequent layers and push downstream routers into logit regimes they weren't trained on — a cross-layer instability cascade that is structurally independent of the routing failure that caused the OOD exposure, and is silent in most frameworks because NaN/inf values are zeroed during gradient accumulation.

5. Pipeline parallelism encodes hardware topology into routing specialization.
Differential gradient staleness across pipeline stages creates depth-dependent routing entropy profiles — early-stage experts develop higher entropy, later-stage experts sharper concentration — as an artifact of pipeline schedule rather than token semantics. This profile persists at inference and is inherited by student models via router distillation, permanently embedding hardware provenance into routing behavior. Pipeline degree is effectively an unacknowledged hyperparameter of expert specialization quality, confounding cross-paper MoE benchmark comparisons where infrastructure configurations differ.

Common Pitfalls
Trusting per-layer utilization histograms as sufficient diagnostics; they miss cross-layer cascade propagation and pipeline-depth artifacts.
Setting α once at initialization without decay scheduling; what regularizes at initialization can dominate and homogenize experts after task loss converges.
Assuming train-inference routing parity when switching between expert-choice training and token-choice inference; the mismatch is qualitative, not distributional.
Attributing bf16 overflow to learning rate misconfiguration rather than OOD expert activation, masking the true failure mode.
Open Question for Deeper Work

Can an adversarial probe reconstruct a model's pipeline training configuration — number of stages, microbatch size — from its inference-time per-layer routing entropy profile alone? If routing patterns encode hardware provenance with sufficient fidelity, this would demonstrate that published MoE quality comparisons are systematically confounded by infrastructure choices, and would motivate a standardized "routing fingerprint" diagnostic that must be reported alongside architectural hyperparameters in MoE research.






