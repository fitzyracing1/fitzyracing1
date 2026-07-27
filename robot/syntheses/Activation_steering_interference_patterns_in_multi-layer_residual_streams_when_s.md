Thesis: Activation steering interference in residual streams is not primarily a representational problem of feature direction overlap but a computational problem of circuit substrate sharing, and this distinction exposes fundamental geometric, temporal, and architectural limits on steering's viability as both an interpretability tool and a safety intervention.

Key Insights
1. Orthogonality in representation space does not imply independence in computation

Two SAE features can have near-zero cosine similarity in the residual stream yet contend over the same attention heads, MLP neurons, or routing decisions. When a steering vector shifts a shared attention head's query, it alters the softmax attention pattern over all positions, corrupting any feature that depends on that head's output — regardless of whether the steering direction has any direct projection onto the second feature's residual-stream direction. The correct unit of independence analysis is the circuit graph, not the feature geometry, and interventions must be evaluated against the former.

2. Partial activation patching recovery is a topological diagnostic

When patching a shared head's output only partially restores a collaterally disrupted feature, the residual non-recovery encodes structural information: it distinguishes upstream information destruction (the head's input was already corrupted before it computed) from parallel path interference (the feature receives contributions through circuit edges that bypass the patched head). Discriminating these cases requires layerwise input patching and, when both failure modes co-occur, causal scrubbing against explicit circuit graph hypotheses. Treating partial recovery as noise rather than signal discards the most informative data the patching experiment produces.

3. Feasible steering windows are bounded by layer-resolved contribution profiles

The opportunity for selective intervention — targeting feature F without collateral damage to feature G — exists only in layers where F's circuit is actively computing and G's is not yet engaged or is already saturated. This window collapses entirely when F and G's critical computation layers overlap, a condition that is predictable from per-layer SAE reconstruction derivatives and is more likely in models with high cross-layer head composition scores. Late-layer steering reduces collateral damage not by accident but because it exploits the structural fact that many features complete their computation before the final layers.

4. MoE routing introduces input-conditional and intervention-conditional topology instability

In Mixture-of-Experts architectures, circuit substrate separation is not a fixed architectural property but a stochastic function of the router's input-dependent decisions. A steering vector can itself perturb routing logits, discretely swapping expert assignments and converting a clean-window intervention into a collapsed-window one — or worse, routing safety-critical features through more dangerous computational substrates than would have been used without the intervention. Router-aware vector design requires orthogonality to dangerous decision boundary normals, but this constraint set scales as O(L × K²) across layers and experts, and in deep, weakly-specialized MoE systems the feasible steering direction space collapses before meaningful target-feature projection can be achieved.

5. Steering vectors are policies over computational graphs, not constant causal nudges

The standard framing of activation steering as "adding a fixed causal perturbation" is only valid when the model's computational graph is input-invariant. In superposed dense models the graph is approximately fixed but the effective interference topology varies with feature co-activation patterns; in MoE models the graph is explicitly input- and intervention-dependent. This reframing implies that safety guarantees from steering require certifying the entire support of the induced distribution over computational graphs, not just average behavioral effects — a requirement absent from all current steering vector evaluations.

Common Pitfalls
Evaluating steering by target-feature effect alone while ignoring collateral suppression of co-substrate features, which may be subtle, nonlocal, and invisible to probes applied only at the steered layer.
Conflating SAE feature orthogonality with circuit independence, leading to the false conclusion that geometrically separable features can be steered independently.
Calibrating steering vectors on distributions where co-routing is rare, then deploying on distributions where router decision boundaries shift and the interference topology changes discontinuously.
Treating partial patching recovery as experimental noise rather than as a structural signal about parallel paths and upstream information loss.
Open Question for Deeper Work

Is there a quantifiable superposition density threshold — expressible in terms of the ratio of active features to ambient residual stream dimension — beyond which the SAE feature orthogonality constraints and circuit substrate overlap jointly guarantee that no steering vector can achieve selective single-feature intervention, and does this threshold have a closed-form relationship to the model's effective circuit depth and head composition scores? Establishing this bound would convert the current empirical observation that steering becomes unreliable in large, heavily superposed models into a principled geometric limit with direct implications for which model classes can be safely controlled via activation steering.






