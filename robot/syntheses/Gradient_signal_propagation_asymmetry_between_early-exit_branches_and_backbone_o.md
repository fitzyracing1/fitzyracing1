Thesis: Training early-exit branches jointly with a shared backbone creates systematic gradient interference that corrupts representations, miscalibrates exit decisions, and silently erodes the efficiency gains adaptive computation networks were designed to deliver — and naive fixes at any single point in the system tend to displace the problem rather than resolve it.

Key Insights
1. Gradient conflict is geometric, not just scalar

When branch and backbone losses produce gradients with negative cosine similarity at shared layers, down-weighting the branch loss shrinks both the conflicting and the cooperative gradient components equally, discarding useful signal proportional to the damage avoided. The correct intervention is projection-based: PCGrad-style orthogonal projection removes only the conflicting component, and CAGrad-style methods track conflict geometry explicitly. Scalar loss weighting (as in vanilla BranchyNet) is a blunt instrument that addresses magnitude but not direction, and persistent negative cosine similarity at a specific layer is diagnostic of an architectural capacity problem that no reweighting scheme can fully solve.

2. Persistent conflict indicates architectural bottleneck, not just optimization noise

Occasional gradient conflict reflects mini-batch noise and transient representational reorganization; persistent conflict across batches and training phases means the layer cannot simultaneously serve two incompatible geometric objectives. The intervention is structural: residual adapters (LoRA-style, rank 4–16) inserted at the conflict point give branch gradients partially disjoint parameters to write to, absorbing the interference without corrupting the backbone's forward pass. Crucially, residual adapters are safer than series adapters because their near-zero initialization makes them nearly invisible to deeper layers at the start of training, bounding the damage to non-exiting inputs.

3. Threshold changes at inference cause measurable distributional shift

Deeper backbone layers become conditioned on the mixture of input difficulties seen during training. Sweeping the exit threshold at inference — routing more or fewer inputs to depth — shifts that mixture, and the degradation is asymmetric: aggressive loosening forces deep layers to handle a skewed population of only the hardest inputs, causing 2–4% accuracy drops on GLUE benchmarks in PABEE-style systems. Threshold-aware training (stochastic threshold variation during training) reduces this sensitivity but introduces its own pathology: deeper layers learn a rescue reflex, deferring classification rather than deciding, which flattens confidence curves and degrades early-exit accuracy even at the training threshold.

4. Branch confidence scores are systematically miscalibrated

Early-exit softmax confidence reflects both input separability and gradient interference distortion, producing ECE roughly 2–3× higher than the final exit. The miscalibration is class-dependent and distribution-tied, not random, so temperature scaling alone cannot fix it. This causes routing collapse: overconfident misroutes exit inputs that needed depth, while underconfident correct predictions waste compute on inputs that didn't — inverting the intended efficiency allocation and breaking the efficiency-accuracy curve measured at validation time.

5. Meta-classifier routing compounds errors in non-obvious ways

Replacing entropy thresholds with a learned exit predictor trained to predict final-exit agreement reframes routing as a meta-classification problem and reduces misrouting by 15–20% in SDN-style experiments. However, the meta-classifier's errors now compound with branch errors multiplicatively rather than additively, and under distribution shift or low-data regimes the meta-classifier can be strictly worse than a simple entropy threshold — particularly when the training set for the meta-classifier doesn't cover the tail of difficult inputs that most need correct routing.

Common Pitfalls
Treating loss weighting as a substitute for architectural intervention when persistent gradient conflict signals a capacity problem that reweighting cannot resolve.
Freezing the backbone during branch warmup for from-scratch networks, where early-layer features are random and branch heads converge on noise, miscalibrating the joint-training phase.
Assuming adapter insertion is neutral for non-exiting inputs — series adapters condition all downstream weights on branch-supervised transformations, making adapter removal catastrophic.
Measuring efficiency gains at a fixed threshold without sweeping the threshold at deployment, masking the distributional sensitivity that makes real-world efficiency unpredictable.
Conflating calibration failure with overconfidence — branch miscalibration is representational and class-correlated, not just a softmax sharpness problem fixable by temperature.
Open Question for Deeper Work

The meta-classifier routing approach assumes that final-exit agreement is a stable and meaningful proxy for "this input needed depth" — but in a network where backbone representations are themselves distorted by branch gradient interference, final-exit predictions may be systematically wrong on the same subpopulations that fool the branches. This raises the question of whether any routing criterion trained on the network's own outputs can escape the representational pathologies introduced during joint training, or whether reliable routing fundamentally requires either disentangled training objectives or an external oracle signal that doesn't inherit the network's own failure modes.






