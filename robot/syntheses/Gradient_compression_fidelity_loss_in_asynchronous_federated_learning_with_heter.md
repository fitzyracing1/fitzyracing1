Thesis: Gradient compression and asynchronous heterogeneous updates are individually manageable sources of error in federated learning, but their interaction produces compounding, qualitatively distinct failure modes that cannot be remedied by treating them as independent additive costs — and every proposed correction mechanism discovered so far relocates rather than eliminates the underlying distribution-dependence obstruction.

Key Insights

1. Compressed residuals become coordinate-frame-invalidated debt, not merely stale signal.
In uncompressed async SGD, a stale gradient is harmful in proportion to parameter-space displacement — the signal is directionally degraded but structurally intact. Error-feedback buffers in compressed schemes (EF-SGD, top-k sparsification) store residuals defined as the complement of what was already transmitted, denominated in the coordinate frame of the model at compression time. When the global model moves substantially across missed rounds, these residuals lose their geometric validity entirely: they encode suppressed gradient mass from a loss landscape that no longer exists, and can become anti-correlated with the current gradient near saddles or after learning rate transitions. Unlike vanilla staleness, this failure is not bounded by τ·η·‖g‖ — it is a structured, sign-inconsistent injection whose damage accumulates additively across every missed round.

2. Filtering residuals by alignment with the global gradient silently erases minority client signal.
A natural correction — projecting residuals onto the current global gradient direction before injection — converts a poisoning problem into a representation collapse problem. In non-IID federated data, minority clients' gradients are structurally orthogonal to the majority-dominated global gradient, not because they are stale or corrupted but because they encode genuine local curvature the global model is actively moving away from. The alignment gate rejects these residuals every round, and because top-k compression already preferentially suppresses small-magnitude minority-relevant coordinates, the combination produces complete, silent erasure of minority signal — invisible in global loss curves while minority client local loss diverges.

3. Distribution-agnostic compression-compatible error feedback is information-theoretically impossible.
DIANA-style control variate schemes defer rather than eliminate the problem: the control variate itself becomes stale under heterogeneous update frequencies, recreating the residual-buffer problem one abstraction level up. The Barnes et al. (2020) lower bounds formalize the obstruction — any compressed estimator of a distributional divergence incurs irreducible error proportional to the KL divergence between client distributions and the compressor's implicit prior. Top-k sparsification's implicit prior is the majority gradient distribution, so minority clients pay a fidelity tax that cannot be recovered without distributional information. Second-order corrections (Hessian-based control variate updates) concentrate rather than dissolve this dependence, since Fisher information matrices are more anisotropic for minority clients than gradient vectors.

4. Scaffold's drift correction and compression interact to produce oscillation, not cancellation.
Applying Scaffold in the compressed regime requires compressing both the gradient channel and the control variate update channel. Compressing the control variate update corrupts the correction term rather than the gradient signal — a second-order geometry distortion. Artemis-style dual EF buffers manage both channels but require independent staleness bounds; however, the channels are coupled (control variate staleness is a function of gradient channel staleness over the same parameter trajectory), making independent threshold-setting provably suboptimal. The optimal threshold ratio scales with √(L_c/L_g), where L_c is itself heterogeneity-dependent and unknown.

5. Online heterogeneity estimation from compressed observations is self-referentially biased in the worst case.
Estimating L_c from inter-client disagreement in compressed control variate updates fails systematically: clients with similar minority distributions produce nearly identical compressed updates despite large true disagreement, causing the estimator to underestimate heterogeneity precisely where it is highest. This creates a positive feedback loop — underestimated L_c permits excessive staleness, increasing effective heterogeneity, further biasing the estimate downward — a potentially monotonically diverging failure rather than the bounded oscillation seen in EF-Scaffold.

Common Pitfalls
Treating compression error and staleness as additive independent costs — they interact multiplicatively through the coordinate-frame invalidation mechanism.
Evaluating FL compression schemes only on global metrics — minority client divergence is invisible in aggregate loss/accuracy curves.
Assuming control variates solve heterogeneity — Scaffold's guarantees assume lossless control variate communication; compressed Scaffold loses its convergence certificate.
Using staleness thresholds calibrated on IID benchmarks — threshold optimality is distribution-dependent; IID-calibrated thresholds are insufficiently conservative under high heterogeneity.
Open Question for Deeper Work

Does deliberately randomizing the compression operator across clients — assigning different random sparsification masks per client per round — break the correlated residual structure that drives both the heterogeneity estimation bias and the silent minority erasure problem, and if so, what is the precise tradeoff with convergence guarantees that implicitly depend on consistent coordinate selection for error accumulation to remain bounded? The tension is fundamental: decorrelating compression across clients to debias estimation may destroy the coordinate consistency that makes EF buffers theoretically tractable.






