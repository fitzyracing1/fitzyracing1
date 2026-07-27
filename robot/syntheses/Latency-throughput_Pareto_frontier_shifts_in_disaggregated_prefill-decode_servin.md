Thesis: In disaggregated prefill-decode serving, bursty request arrivals do not merely shift the latency-throughput Pareto frontier outward — they destabilize it into a stochastic band, because the causal coupling between prefill and decode pools, mediated by KV transfer bandwidth and HBM occupancy dynamics, converts arrival variance into cascading control failures that no single mitigation layer can contain in isolation.

Key Insights

1. The KV transfer fabric is the hidden binding constraint under bursts.
Most operators monitor GPU compute utilization and mistake it for the system's binding resource. Under bursty arrivals, the NVLink or RoCE interconnect saturates before either GPU pool hits compute limits, and the resulting transfer queue buildup creates a propagation delay between prefill completion and decode availability. This delay is not constant — it grows with burst magnitude — so the effective TTFT distribution develops a heavy right tail that is invisible in median-focused dashboards. The Pareto frontier shifts because throughput is capped by transfer bandwidth, not compute, at exactly the moments when latency pressure is highest.

2. Chunked prefill smooths injection but introduces batch-cadence misalignment risk.
Breaking large prompts into fixed-size chunks prevents single requests from monopolizing transfer bandwidth, but chunk size must be dynamically matched to the decode batch tick period. When chunk completion latency misaligns with batch cadence, partial KV states idle in HBM across batch ticks, consuming 15–20% of usable cache capacity and shrinking sustainable batch size. Dynamic chunk sizing via feedback control is the natural fix, but the feedback signal — batch tick duration — is corrupted under mixed-priority workloads where high-priority preemptions cause tick duration to drop spuriously, causing the controller to over-inject and trigger the cascade it was designed to prevent.

3. Priority partitioning trades utilization efficiency for isolation, with dynamic rebalancing as the fragile bridge.
Static priority-partitioned KV cache pools eliminate cross-priority interference but waste 25–40% of HBM under realistic arrival skew. Watermark-triggered borrowing and speculative pre-eviction recover some of this stranded capacity but introduce revocation latency (10–50ms on loaded systems) that reintroduces latency jitter for high-priority traffic during demand spikes. Speculative pre-eviction specifically fails when burst duration is shorter than the predictor's look-ahead window — the dominant failure mode under the heavy-tailed burst regimes that motivate disaggregation in the first place.

4. Early-warning signals upstream of the cluster enable sub-100ms rebalancing, but threshold calibration is fragile.
Gateway queue depth, client retry counters, and admission-time prompt length histograms lead actual decode demand by 5–30ms, providing actionable head start for the rebalancer. Delivering these signals within budget requires a sidecar-aggregator-migrator pipeline with stateless threshold-triggered binary outputs. However, thresholds calibrated offline on historical traces systematically underrepresent burst-regime tail behavior, producing either chronic false positives (thrashing) or false negatives (missed cascades). Online adaptation via bandit updates and increment-based thresholding on first-difference signals (which have lighter tails than level processes) are necessary to maintain calibration under distribution shift.

5. Counterfactual label construction is the unsolved core of closed-loop control.
Bandit-based threshold adaptation requires distinguishing genuine false positives from narrowly averted cascades, but the intervention prevents the outcome needed to generate the label. Shadow queuing models running no-intervention trajectories from frozen pre-intervention state snapshots provide approximate counterfactuals, while randomized holdout interventions (ε = 1–3%) generate unbiased direct observations at controlled SLO risk. Combining both with importance weighting yields a usable training signal, but the optimal ε is itself burst-dependent — highest information value and highest cascade risk coincide exactly during live bursts, making ε a dynamic policy variable rather than a fixed hyperparameter.

Common Pitfalls
Monitoring compute utilization instead of fabric bandwidth — GPU headroom looks healthy while the interconnect is the actual bottleneck.
Static chunk sizing — chunk size tuned at deployment drifts out of alignment as batch composition evolves, silently degrading HBM efficiency.
Using level signals rather than increment signals for thresholding — heavy-tailed marginal distributions make absolute thresholds unstable; differencing before thresholding is essential.
Treating the Pareto frontier as a stable curve — under bursty mixed-priority load it is a stochastic band; SLO commitments for low-priority traffic that assume a stable frontier are structurally unsound.
Open Question for Deeper Work

Can the shadow queuing model used for counterfactual label generation be made accurate enough to replace randomized holdout interventions entirely — eliminating cascade risk from the calibration loop — or is there a fundamental identifiability limit where no model of bounded complexity can distinguish "intervention was unnecessary" from "intervention was necessary and effective" without direct observation of the suppressed outcome?






