Thesis: The apparent modularity of adapter-based multi-task learning is illusory — gradient interference, representational convergence, and routing collapse are structurally inevitable under task affinity mismatch, and each mitigation technique displaces rather than eliminates the core capacity conflict, manifesting it at a new architectural layer.

Key Insights
1. Fusion mechanism choice determines where interference surfaces, not whether it occurs

Additive fusion, AdapterFusion, and parameter averaging each relocate gradient interference rather than resolving it. Parameter averaging entangles task vectors irrecoverably at merge time, with accuracy losses exceeding 15% across four or more dissimilar tasks. AdapterFusion's dynamic gating provides the best per-input task discrimination but introduces a new single-point-of-failure: the fusion attention layer itself saturates around 8–12 tasks, with attention weights collapsing toward uniformity as adapter outputs become geometrically indistinguishable. The practitioner's error is choosing a fusion mechanism based on architectural elegance and assuming the interference problem is thereby solved; the correct framing is choosing which failure mode is most diagnosable and recoverable for the deployment context.

2. Attention collapse is an upstream representational failure, not an attention mechanism failure

When AdapterFusion's attention weights entropy-maximize toward log(K), the proximate cause is not a defect in the attention layer but convergence of adapter output representations in the backbone's embedding space. The early-warning signal is the stable rank of the per-example attention weight matrix dropping below K/2, which precedes metric degradation by 200–500 training steps. Interventions targeting the attention layer directly — entropy penalties, attention regularization — treat the symptom. The correct intervention is enforcing geometric separation between adapter output representations via orthogonality constraints or contrastive separation losses, maintaining the representational diversity that gives fusion attention its discriminative signal.

3. Frozen backbones worsen representational convergence as task count grows

A frozen backbone forces all K adapters to operate on identical input activations, making their outputs low-rank perturbations of the same fixed representation. Task-similar adapters inevitably produce overlapping output subspaces because there is no gradient path to diversify their inputs. Partial backbone fine-tuning with differential learning rates — fine-tuning upper-middle layers while freezing lower layers — restores the geometric degrees of freedom needed for inter-adapter separation. The optimal freeze boundary is not a fixed architectural heuristic but a data-driven signal: CKA between adapter outputs at each layer, with a unfreeze threshold around mean off-diagonal similarity of 0.85–0.90, making the boundary adaptive to the actual task geometry.

4. CKA-based monitoring has a hard reliability ceiling around K=12–16 tasks

Pairwise CKA scales as O(K²) in monitoring pairs and degrades as a geometric signal when tasks cluster into representational archetypes, making many measured pairs redundant while masking the critical distant-task signal. The three-regime taxonomy is: full pairwise CKA for K < 12, cluster-level CKA with task2vec-initialized centroids for K = 12–50, and learned routing with entropy regularization beyond K = 50. The transition points are determined by the intrinsic dimensionality of the task set, not compute budget.

5. Learned routing recreates capacity saturation through self-reinforcing asymmetry

At K > 50, sparse learned routers avoid combinatorial geometric monitoring but introduce new failure modes: semantic collapse (routing by surface statistics rather than task relevance), router logit instability (mitigated by z-loss from ST-MoE), and inference-time capacity bias under task ambiguity. High-capacity adapters accumulate a self-reinforcing routing preference because their broader training coverage produces higher logits for ambiguous inputs. Capacity tiering — designating explicit general-purpose adapters for ambiguous inputs — makes this asymmetry intentional, but requires careful confidence threshold calibration to prevent the general-purpose tier from cannibalizing task-specific routing.

Common Pitfalls
Treating low-rank adapter count as a capacity bound: collapsed adapter directions consume nominal rank without encoding task signal; monitor singular value spectra, not parameter count.
Using held-out accuracy as the primary collapse detector: representational convergence and routing degradation precede metric drops by hundreds of training steps; geometric signals must be monitored continuously.
Applying load balancing loss as a complete solution: balanced utilization and semantically meaningful routing are independent properties; a router can satisfy utilization constraints while routing on task-irrelevant features.
Setting freeze boundaries as fixed architectural hyperparameters: optimal boundaries vary with task combination geometry and should be treated as adaptive signals, not one-time design decisions.
Open Question for Deeper Work

When capacity tiering makes general-purpose adapters structurally responsible for absorbing ambiguous inputs, does the router's confidence threshold — which determines what counts as "ambiguous" — need to be jointly optimized with adapter specialization during training, or does post-hoc calibration suffice? More precisely: is there a training regime in which the general-purpose adapter's capacity and the router's confidence boundary co-evolve to a stable equilibrium, or does the system inevitably drift toward one tier dominating — and what is the theoretical condition that distinguishes convergent from divergent tiering dynamics?






