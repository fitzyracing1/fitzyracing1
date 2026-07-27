Thesis: Mixed-precision training does not merely introduce quantization noise into weights and activations — it systematically corrupts the optimizer's internal model of loss landscape curvature through stochastic rounding error compounding in adaptive gradient statistics, driving attention layers into path-dependent attractor states that are invisible to standard monitoring, irreversible without joint weight-and-optimizer-state rollback, and detectable only through capability-agnostic geometric signatures derived from random matrix theory and second-moment spectral analysis.

Key Insights

1. Stochastic rounding bias breaks Adam's curvature approximation selectively along high-curvature directions.
SR is theoretically unbiased for linear operations, but Adam's nonlinear update rule — involving squaring gradients, exponential smoothing, square roots, and epsilon-stabilized division — breaks the linearity required for bias cancellation to propagate. The result is that v_t, Adam's second-moment estimate, integrates rounding errors over thousands of steps (under β₂=0.999, the effective memory horizon is ~1000 steps), and because v_t appears in the denominator of the update rule, small biases are amplified rather than averaged away. This amplification is strongest along high-curvature directions of the loss landscape — precisely where accurate curvature estimation matters most — making mixed-precision Adam systematically miscalibrated in the subspaces most critical to learning.

2. Attention layers are structurally disproportionate victims due to heavy-tailed, sparse gradient distributions.
Attention projection gradients exhibit kurtosis 4–8× higher than MLP layer gradients during the same training run (Molybog et al., 2023), driven by softmax-induced gradient competition that produces bursty, sparse activation patterns across steps. These heavy-tailed gradient events dominate v_t accumulation disproportionately and are also the events most likely to be rounded to incorrect exponent bins in BF16, creating a dual error: v_t over-damps updates along spike-dominated directions while under-damping directions the bursty signal missed, selectively collapsing the optimizer's effective learning rate in the attention subspaces responsible for precise token routing and relational computation.

3. The resulting miscalibration is a path-dependent attractor, not a self-correcting transient.
The feedback loop has three phases: spike integration (~50–200 steps), diversity collapse (~200–800 steps), and false stabilization. Once attention head diversity collapses due to suppressed updates, gradient variance drops — and the optimizer interprets this reduced variance as confirmation that the inflated v_t is correct. The system reaches a self-consistent but suboptimal fixed point from which standard training cannot escape, because v_t is a one-way accumulator. Recovery requires both optimizer state reset and weight rollback to a pre-collapse checkpoint; weight updates alone are insufficient.

4. Standard monitoring is blind to attractor onset; geometric signatures from random matrix theory fill the gap.
Loss curves and gradient norms lag attractor onset by 200–800 steps — the full length of the diversity collapse phase. Three capability-agnostic signatures reliably detect phase-1 spike integration before irreversibility: (a) the second derivative of effective rank trajectory (negative during pathological integration, positive during benign learning); (b) cross-head v_t cosine similarity concentration (pathological spikes drive artificial inter-head convergence); and (c) deviation of v_t eigenspectra from the Marchenko-Pastur bulk distribution, detectable via rank-10 randomized SVD. Together these form a computationally cheap monitoring system robust to the functional reassignment events that invalidate interpretability-grounded head-to-capability maps.

5. The geometric fingerprint of v_t collapse predicts capability-specific degradation before loss reflects it.
When v_t spectral entropy collapses onto 1–3 singular directions aligned with a head's functional subspace (principal angle < ~20–30°), the optimizer selectively suppresses updates to that head's core computational primitive — induction, copy suppression, coreference binding — producing benchmark-detectable capability degradation 500–1000 steps before aggregate validation loss shifts measurably, as established by circuit-level analysis (Conmy et al., 2023) and relation linearity work (Hernandez et al., 2023).

Common Pitfalls
Assuming SR unbiasedness is sufficient for optimizer correctness. Unbiasedness of individual rounding operations does not survive nonlinear composition through Adam's update rule.
Treating optimizer state checkpointing intervals as a storage problem only. Intervals exceeding ~100 steps virtually guarantee that anomaly detection occurs after the intervention window has closed.
Using loss spikes as rollback triggers. By the time the loss reflects attractor formation, the nearest safe checkpoint is already hundreds of steps behind the detection point.
Conflating benign high-curvature learning with pathological spike integration. Both reduce effective rank and elevate v_t — the distinguishing signal is the second derivative of the rank trajectory and the cross-layer coherence of v_t elevation.
Open Question for Deeper Work

Does the Marchenko-Pastur deviation signature remain valid during early training, when weight matrices are far from their converged spectral structure and gradient distributions are systematically non-stationary? The random matrix theory baseline assumes that healthy gradient inputs produce approximately Wishart-distributed second-moment matrices — an assumption that likely breaks down before the bulk eigenvalue distribution has stabilized, which may be thousands of steps into training for large models. Establishing the phase boundary at which RMT-based anomaly detection becomes reliable, and designing a complementary early-training monitor for the pre-RMT-validity regime, represents a concrete and consequential open problem at the intersection of optimizer theory, random matrix theory, and large-scale training practice.






