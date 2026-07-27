Thesis: The central challenge in multi-task learning is not balancing loss magnitudes but managing gradient geometry in shared parameter space — and most standard interventions fail because they treat conflict as a per-step scalar problem rather than a structural, layer-specific, directional one.

Key Insights
1. Loss reweighting addresses magnitude, not direction

Dynamic reweighting schemes (GradNorm, uncertainty weighting) change how loudly each task speaks but cannot change what direction it points. Two tasks with opposing gradient directions remain in conflict regardless of their relative loss scales — reweighting can slow the damage but cannot resolve the underlying geometry. The optimizer still moves in a compromised direction, and in high-curvature regimes the dominant task actively warps the loss surface in ways that make other tasks' gradients structurally misleading as local descent directions.

2. Per-step gradient surgery is necessary but insufficient

Methods like PCGrad and MGDA resolve conflicts locally by projecting conflicting gradients or finding minimum-norm descent directions, and they do reduce destructive interference measurably. However, both operate without memory of gradient history, so they cannot distinguish transient conflict (a bad batch) from structural conflict (genuinely incompatible representations). They also silently discard gradient magnitude information — PCGrad zeros conflicting components, MGDA shrinks updates in high-conflict regimes — and gains on benchmarks like GLUE typically run only 1-3%, often vanishing beyond five tasks.

3. Conflict is layer-specific and temporally persistent

Gradient conflict is not uniform across a network. In transformers, upper layers concentrate the most destructive inter-task interference, while lower layers tend toward cooperation. Tracking per-layer exponential moving averages of inter-task gradient cosine similarity operationalizes the distinction between structural conflict (persistently negative EMA) and transient conflict (fluctuating near zero). This distinction determines the right intervention: structurally conflicting layers warrant hard routing (task-specific adapters, MoE), while transiently conflicting layers respond well to soft gradient surgery.

4. Architectural separation must be validated against capacity confounds

Inserting task-private parameters at a conflicting layer reduces interference but also adds capacity and removes implicit regularization from sharing. Without parameter-matched ablations — comparing a per-task adapter against a wider shared adapter of equivalent total size — it is impossible to attribute performance gains to conflict resolution rather than parameter count. The distinction matters: conflict-driven gains justify permanent separation, but capacity-driven gains may introduce fragility in low-data regimes where shared parameters provided essential inductive bias.

5. Cheap proxies can predict conflict before full joint training

Full per-task gradient materialization is too expensive for closed-loop control, but forward-pass proxies — particularly the stable rank of layer activation covariances and cross-task activation similarity — serve as leading indicators of conflict, detectable hundreds of steps before gradient geometry becomes structurally opposed. These proxies enable a task admission protocol: probe each candidate task on a frozen shared model for 500-1000 steps, flag rank collapse below ~30% of initialization as a high-conflict signal, and run a counterfactual joint probe to detect interaction effects before committing to expensive full MTL runs.

Common Pitfalls
Conflating loss balance with gradient compatibility. Achieving equal loss magnitudes across tasks is not a proxy for geometric compatibility; tasks can have balanced losses while fighting destructively in parameter space.
Ignoring gradient magnitude collapse as a Goodhart failure. Optimizing for high inter-task cosine similarity can drive one task's gradient to near-zero, producing spurious alignment that masks suppression rather than cooperation.
Attributing MTL gains without parameter-matched controls. Most published comparisons of shared versus task-specific architectures do not equate parameter counts, making attribution to conflict resolution rather than added capacity unreliable.
Using noisy per-step geometry as a controller input. Gradient cosine similarity has high minibatch variance; controllers that close the loop on raw per-step signals chase noise, while the smoothing needed for reliability introduces lag that defeats real-time control.
Open Question for Deeper Work

The probe-based admission protocol depends critically on the quality of the shared initialization: a poorly pre-trained or domain-mismatched base model may produce compatibility fingerprints that are artifacts of that initialization rather than intrinsic task relationships, generating systematic admission errors that only surface after full MTL runs. The open question is whether task compatibility is a property of the task pair alone, or a three-way interaction between the two tasks and the specific representational geometry of the base model — and if the latter, whether compatibility predictions can be made initialization-invariant through normalization, ensemble probing across multiple checkpoints, or theoretical characterization of which task properties guarantee conflict regardless of initialization.






