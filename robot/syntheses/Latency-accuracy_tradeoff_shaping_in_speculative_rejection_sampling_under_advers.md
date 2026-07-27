Thesis: Speculative decoding's latency-accuracy Pareto frontier is not robust by construction — an adversary who controls draft quality can silently corrupt output distributions, steer generation toward low-probability target outputs, and evade detection indefinitely through slow drift, making inference-time sampling policy design a first-class security surface rather than a pure efficiency problem.

Key Insights

1. Systematic draft bias breaks the correction distribution's distributional guarantee.
Standard speculative decoding is distribution-exact only when draft probabilities are consistent estimators of the true draft distribution. When bias is systematic — as with quantized or pruned draft models that suppress low-frequency tokens — the correction term applied on rejection drifts directionally away from the true residual, corrupting the conditional output distribution at every rejection event. Unlike noise, which washes out in expectation, bias compounds: the marginal token distribution may still look close to the target while the conditional distribution after rejection events is systematically wrong, evading perplexity-based audits while degrading factuality and calibration.

2. Rejection events are an adversarial steering surface.
Because the correction distribution fires only on rejection, an adversary who controls draft probabilities can engineer which tokens get rejected and which get accepted. By assigning high draft probability to tokens they want suppressed (forcing acceptance, bypassing the target) and low probability to tokens they want promoted (engineering rejection, triggering the correction path), the adversary can concentrate correction mass on specific low-probability-but-nonzero target outputs. The hard bound is the target model's support: no mass can be injected where p_target is zero, but within that envelope the attack has real leverage, particularly against well-calibrated but uncertain target models.

3. Target entropy is the key vulnerability parameter, and tempering decouples security from robustness.
Higher target entropy improves robustness to benign draft noise but expands the adversarial manipulation surface by the same mechanism. The decoupling fix is asymmetric treatment: use the full target distribution for acceptance decisions but apply a sharpened, tempered version for the correction term, with temperature τ set as a monotone function of context-conditional entropy. This introduces a known, defender-controlled KL distortion in place of an adversarially steered one, converting an unbounded attack surface into a tunable security-accuracy parameter. Dynamic τ scheduling anchored to draft-independent context summaries prevents the adversary from gaming the entropy estimate through context manipulation.

4. The joint attack surface is harder but detectable — up to a slow-drift limit.
When an adversary must simultaneously manipulate both the prompt prefix and the draft probabilities, the optimization is strictly harder, and the signature is measurable: adversarial draft sequences produce structured, autocorrelated rejection patterns distinguishable from benign degradation's i.i.d. noise. Sequential detectors (CUSUM, SPRT) can flag adversarial conditions within 10–30 tokens at sub-1% false positive rates for moderate attack strengths. However, a slow-drift adversary who spreads manipulation across many tokens can stay below any fixed detection threshold, and increasing window size helps the adversary more than the defender due to asymmetric scaling of detection delay versus attack cost.

5. Intervention cost asymmetry dominates window-size tuning.
The correct design principle is not detecting accumulated damage after the fact but making each token's manipulation expensive per step — which is precisely what per-token correction tempering achieves. A practical hybrid runs a short-window sensitive detector (triggering temporary fallback to target-only decoding) alongside a long-window high-specificity detector (triggering session-level responses), accepting that slow attacks may cause bounded semantic damage while limiting its extent and providing offline attribution.

Common Pitfalls
Assuming distribution-exactness survives draft degradation. It does not — the guarantee is only as good as the draft probability estimates.
Treating acceptance rate as a proxy for output quality. An adversary can maintain a plausible acceptance rate while systematically corrupting the correction path.
Conflating prompt-level and sampling-level robustness. They protect different attack surfaces; stacking them gives strictly better coverage than either alone, but neither subsumes the other.
Using window size as the primary detection lever. This is exploitable; per-token intervention cost is the more robust design axis.
Open Question for Deeper Work

Can the tempered correction distribution's KL distortion budget ε be formally connected to a certified steering resistance — that is, a bound on how far the adversary can shift the output distribution's mean in any direction in semantic embedding space — as a function of τ, the target model's entropy profile, and the adversary's total manipulation budget across a generation episode? Such a certificate would transform the current heuristic defense into a quantitative security guarantee analogous to certified robustness radii in the adversarial examples literature.






