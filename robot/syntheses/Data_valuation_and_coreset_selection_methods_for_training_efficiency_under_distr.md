7:12 PM



Data valuation and coreset selection methods for training efficiency under distribution shift

Thesis: Coreset selection and data valuation methods developed under the i.i.d. assumption do not gracefully extend to distribution shift — every major component (influence estimation, Shapley scoring, density ratio weighting, prior specification) degrades in ways that compound rather than average out, and robustifying any single component without co-optimizing the others produces false confidence.

Key Insights

1. The fixed-distribution assumption is load-bearing in influence functions and Shapley values.
Influence functions score training points by their effect on a fixed test gradient; Shapley methods define value against a fixed validation set. Under distribution shift, the "test distribution" becomes a moving target — under DRO it is the worst-case distribution active at the current parameters, which changes as training data is perturbed. The clean linear approximation in influence functions drops a second-order term that is non-negligible when the active worst-case distribution shifts, and Shapley scores computed against source validation can be sign-reversed for the most valuable target-domain points. Patching the value function with an MMD-based target proximity term (as in DAVINZ) helps but does not restore the original theoretical guarantees.

2. Density estimation error propagates into coreset composition nonlinearly.Constructing a proxy target distribution from unlabeled target data is the practical entry point for handling covariate shift, but importance weight estimates have variance scaling as O(n_{target}^{-2/(d+4)}) — rendering them unreliable in moderate dimensions until target sample sizes reach the low thousands. Critically, coreset selection amplifies this error because it applies a threshold to the weight distribution's tail: small multiplicative errors in high-weight regions flip point inclusion, and switching density estimators (KMM vs. classifier-based ratio) changes top-quintile coreset membership by 30–40% at 200 target points, stabilizing only beyond roughly 2,000.

3. Tail shift creates a compounding double failure in two-phase adaptive designs.
When shift concentrates in low-density source regions, both density estimation and coreset