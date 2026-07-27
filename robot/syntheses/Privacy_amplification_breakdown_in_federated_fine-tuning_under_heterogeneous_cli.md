Thesis: The privacy guarantees reported for federated fine-tuning systems are systematically optimistic because they account for gradient noise in isolation, while adaptive aggregation, low-rank update geometry, server-side visibility, participation metadata, and timing side-channels each constitute independent leakage surfaces whose joint privacy loss has never been formally bounded in any deployed system.

Key Insights
1. Adaptive aggregation destroys the subsampling assumption that privacy amplification depends on

Adaptive aggregation rules make client selection data-dependent, collapsing the Poisson sampling assumption that amplification proofs require. In non-IID settings (Dirichlet α < 0.1), high-loss clients are systematically over-selected, making their effective participation probability approach 1 and per-round DP accounting vacuous. Restoring valid amplification requires uniform selection or pre-committed schedules — both costly in exactly the regimes where adaptive aggregation helps most.

2. Low-rank adapter structure concentrates privacy leakage geometrically

LoRA's reduced parameter count is beneficial, but small rank means the adapter's column space is dominated by few training examples, improving adversarial subspace membership inference by 5–15 AUC points over dense-update baselines. Standard Frobenius norm clipping understates true sensitivity — the correct quantity under subspace attacks is the spectral norm, up to √r times larger — making reported ε values in DP-LoRA literature likely optimistic.

3. A server-side adversary requires defenses well beyond standard DP

SecAgg prevents per-update inspection but not differencing attacks: subtracting consecutive round aggregates isolates clients whose participation changed, with residual noise negligible in 10–100 client cross-silo settings. Closing this gap requires SecAgg, local noise, differential participation policies, and verifiable update integrity simultaneously — a conjunction no deployed system satisfies.

4. Participation metadata and timing are unaccounted leakage surfaces

Institutions have characteristic compute and network profiles; arrival latency alone can de-anonymize participation even under cryptographic obliviousness. Genuine timing DP requires calibrated artificial delays adding 30–90 seconds per round, compounding into days across hundreds of fine-tuning rounds — operationally incompatible with frequent-update deployments.

5. Total privacy loss across all channels is currently unauditable

The field's working assumption that gradient DP dominates is unvalidated. Participation metadata attacks achieve membership inference AUC > 0.9 with zero gradient access in small cross-silo settings, suggesting the dominant-channel assumption fails in the highest-stakes deployments, and no governance structure equivalent to Apple's centralized privacy ledger exists for multi-institution FL.

Common Pitfalls
Reporting ε from gradient accounting alone and treating it as the system's end-to-end guarantee.
Using Frobenius norm clipping for LoRA when spectral norm is the correct sensitivity under subspace inference.
Treating SecAgg as sufficient against a malicious server; it prevents per-update inspection, not cross-round differencing.
Applying amplification-by-subsampling when client selection is loss-weighted or data-adaptive.
Conflating shuffler-model DP with central DP without verifying the cohort size and noise conditions the equivalence requires.
Open Question for Deeper Work

Can a unified privacy ledger for federated fine-tuning be constructed that formally tracks joint leakage across gradient content, participation metadata, and timing — and what institutional governance structure (analogous to financial audit or SOC 2 compliance) would make such a ledger externally verifiable rather than self-reported? This requires simultaneous progress in mechanism composition, distributed systems, and regulatory design, and is unlikely to be solved within any single community working alone.

Privacy amplification breakdown brief
Document · MD 
Download






Want to be notified when Claude responds?
Notify