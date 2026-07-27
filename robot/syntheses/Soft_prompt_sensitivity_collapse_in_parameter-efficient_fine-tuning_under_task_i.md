Thesis: Soft prompt sensitivity collapse is not primarily an optimization failure but a structural geometric problem — the attention mechanism's architecture, pretrained sink entrenchment, and multi-task basin narrowing combine to silently degrade the prompt's steering capacity while training loss remains deceptively acceptable, and addressing it requires co-designing the prompt optimization procedure with curvature-aware diagnostics and modular composition strategies rather than simply scaling prompt length or token count.

Key Insights
1. The Attention Pathway Creates Structural Gradient Asymmetry

Soft prompt tokens influence model behavior exclusively through the key-value attention pathway, making them subject to a zero-sum softmax competition against strongly pretrained internal representations. Unlike LoRA or adapter layers, which write directly onto the residual stream and inherit the residual highway's gradient protection, soft prompt tokens must survive intact through L successive attention filters — each of which can route around them entirely. Attention sink formation (Xiao et al., 2023) worsens this: sink tokens develop outsized key norms during pretraining that freeze into dominant attention patterns, and fully frozen backbone weights lock these patterns in permanently, starving prompt tokens of gradient signal. The fix is not deeper prompts alone but hybrid PEFT strategies that couple soft prompt training with lightweight attention-targeted components (IA³-style key/value rescaling) to actively rehabilitate gradient flow.

2. Deep Injection Rehabilitates Gradient Flow but Amplifies Cross-Task Interference

Per-layer prefix injection (Li and Liang, 2021) addresses gradient attenuation by shortcutting the multiplicative decay across layers, ensuring each depth receives a direct optimization signal. However, under multi-task training, the layer-coupling between Pₗ and Pₗ₊₁ creates an interference amplification cascade: updating early-layer prefixes shifts the activation distribution that later-layer prefixes were optimized against, and this covariate shift compounds destructively across tasks. MPT (Wang et al., 2023) demonstrated that naïve shared per-layer prefixes produced worse cross-task interference than input-only prompting. The resolution requires factoring per-layer parameters into shared and task-specific components, with the shared component rank set analytically via intrinsic dimensionality estimation (Aghajanyan et al., 2021) and Fisher Information spectrum analysis rather than grid search.

3. Certain Tasks Are Structurally Unrepresentable Through Soft Prompting

The effective task manifold accessible through soft prompts is strictly smaller than that reachable by full fine-tuning, because prompts cannot directly modify MLP-stored factual associations (Geva et al., 2021). This creates hard representability ceilings that prompt length scaling cannot overcome — empirically visible in the persistent gap on knowledge-intensive tasks (TriviaQA, NaturalQuestions) that does not close beyond ~20-100 prompt tokens. The Jacobian stable rank (squared Frobenius norm divided by squared spectral norm of ∂logits/∂prompt) provides a spectral early warning: collapse below an effective rank of ~3-5 within the first 10% of training reliably predicts unrepresentability before validation loss diverges, enabling early task routing decisions.

4. Basin Width Measurement Enables Dynamic Strategy Switching

Joint multi-task prompt optimization narrows the loss basin in prompt parameter space, creating a regime where stable rank regularization conflicts directly with task loss minimization. Basin width is measurable via Hessian spectral analysis (Ghorbani et al., 2019) or SAM-style perturbation sensitivity (Foret et al., 2021), and tracking the perturbation magnitude ε that produces a fixed loss increase δ gives a cheap continuous scalar signal. When ε drops below a critical threshold sustained over a training window, switching to post-hoc prompt arithmetic composition (Zhong et al., 2023; Ilharco et al.) avoids the narrowing problem entirely by combining independently trained single-task prompts in their respective wide basins.

Common Pitfalls
Trusting training loss as a proxy for prompt health: sensitivity collapse is invisible to loss monitoring; Jacobian stable rank must be tracked independently.
Treating prompt length as a universal fix: representability ceilings are structural, not capacity limitations — scaling tokens beyond saturation wastes compute.
Applying deep injection without task factorization: per-layer prefixes under multi-task training amplify rather than contain interference without explicit shared/task-specific decomposition.
Setting shared component rank by grid search: intrinsic dimensionality estimators provide principled targets; grid search over-ranks shared components and leaks task-specific structure into them.
Open Question for Deeper Work

Prompt arithmetic assumes that independently trained single-task prompt basins are positioned in embedding space such that their linear combinations remain in acceptable loss regions for all constituent tasks — but no formal guarantee exists for this. The geometry of inter-basin interpolation in prompt space is essentially unmapped: under what conditions on task similarity, model scale, and pretraining distribution do task-specific prompt basins form convex-compatible configurations, and can a pretraining-time objective be designed to encourage basin arrangements that are post-hoc composable rather than leaving composability to chance?






