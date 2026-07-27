Thesis: In online RLHF serving pipelines, speculative decoding's latency advantage is structurally fragile — draft model staleness under continuous policy shift causes acceptance rate collapse that follows superlinear degradation dynamics, and recovering that acceptance rate requires resolving a cascade of interdependent tensions between distillation objective choice, batch signal priority, architectural capacity constraints, and layer-freezing tradeoffs that cannot be addressed independently.

Key Insights
1. Acceptance Rate Collapse is Superlinear and Threshold-Governed

The expected acceptance rate α = Σ_x min(p_target(x), p_draft(x)) degrades approximately as α(k) ≈ α₀·exp(-sqrt(k·ΔKL_step/2)) after k PPO gradient steps, making early steps disproportionately damaging. Collapse is not gradual: reward sharpening concentrates target probability mass on high-reward token subsets, causing sudden modal misalignment rather than smooth drift. The steepness is controlled by reward sparsity, the PPO β coefficient, and reward sensitivity to early token positions. Critically, collapse hits hardest on high-reward completions — precisely the outputs most valuable to serve — making staleness an asymmetric and economically severe failure mode.

2. The Optimal Distillation Objective is Support-Weighted, Not Uniform

Standard token-level KL minimization is the wrong recovery objective because it distributes gradient signal uniformly across the vocabulary, whereas acceptance rate is determined exclusively by mass alignment in p_target's high-probability support. Support-weighted KL — concentrating distillation on tokens where p_target(x) > τ ≈ 0.05 — recovers acceptance rate at roughly 40% of the gradient steps required by full KL minimization. Reverse KL is preferable to forward KL during emergency recovery because its mode-seeking behavior forces the draft onto p_target's high-mass regions. Perplexity is a dangerously misleading staleness proxy: a draft can recover near-original perplexity while retaining catastrophically misaligned top-k predictions on the specific high-reward formats the updated target now prefers.

3. Batch Signal Sharing Introduces Asymmetric Gradient Interference

Using the RLHF training batch simultaneously for target PPO updates and draft distillation creates a moving-target problem where the draft distills a convex combination of pre- and post-update target distributions. The interference is asymmetric: PPO's importance sampling correction is more sensitive to concurrent compute than distillation loss. The correct resolution is sequential batch usage — target update first, checkpoint snapshot, then draft distillation on the frozen checkpoint as a replay buffer — augmented with a replay buffer of high-divergence prompts identified by the acceptance rate trip-wire to ensure recovery concentrates on latency-critical contexts.

4. Capacity Gap Creates a Hard Distillation Floor That RLHF Worsens

Independent smaller draft models face an irreducible approximation floor: RLHF sharpens target distributions toward low-entropy predictions, which are precisely hardest for lower-capacity models to represent. Empirically, the 7B-drafting-70B configuration degrades from α ≈ 0.75 on SFT targets to α ≈ 0.55 on RLHF-tuned targets even with fresh distillation, suggesting a capacity-gap floor near 0.5 that no distillation objective can breach. LayerSkip-style early-exit drafts sidestep this via weight-sharing, providing instantaneous co-updating — but this advantage inverts when RLHF gradient signal concentrates in early layers, causing exit heads to operate off-manifold and producing worse degradation than independent drafts.

5. Layer Freezing Tradeoffs Are Dynamic and Schedule-Dependent

Freezing early layers to protect early-exit draft geometric stability costs approximately 30–40% of effective gradient rank and 1.5–2× sample efficiency during reward optimization. However, at realistic serving scales (1000+ requests/minute on 70B models), a 60% acceptance rate drop costs more in GPU-hours than the compute overhead of slower PPO convergence. Critically, this tradeoff is not static: early in RLHF training, full fine-tuning's sample efficiency advantage dominates; late in training when reward improvement plateaus, freezing early layers costs nearly nothing in reward quality while preserving serving economics. An adaptive freeze schedule tied to reward improvement rate is the principled solution.

Common Pitfalls
Monitoring staleness via perplexity rather than direct acceptance rate measurement, which lags true divergence and underestimates collapse in high-reward output regions.
Fixed-interval draft update schedules that ignore reward variance, systematically over- or under-updating depending on training phase.
Simultaneous batch usage for target training and draft distillation, introducing gradient interference that degrades both objectives.
Assuming layer-freezing penalty is constant across training, leading to either over-freezing early in training (sacrificing reward optimization) or under-freezing late in training (unnecessarily sacrificing serving efficiency).
Conflating capacity gap with distillation objective quality, and continuing to refine objectives past the theoretical floor rather than switching to architectural solutions like early-exit or larger drafts.
Open Question for Deeper Work

Can the reward improvement rate, real-time acceptance rate signal, and draft staleness metric be unified into a joint state space and optimized via a single control policy — and if so, does that joint optimization exhibit stable equilibria, or do the feedback loops between serving latency, policy update rate, and draft refresh frequency create limit cycles or chaotic dynamics that make online RLHF serving with speculative decoding fundamentally harder to stabilize than either system in isolation?






