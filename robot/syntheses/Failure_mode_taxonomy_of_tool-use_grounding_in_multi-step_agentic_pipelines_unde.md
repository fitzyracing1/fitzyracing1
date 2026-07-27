Thesis: The distinctive failure modes of tool-using agents in multi-step pipelines are not random bugs but a structured taxonomy arising from the interaction between incomplete world observation and the HTTP request-response abstraction, producing error cascades that are self-reinforcing, often invisible from inside the agent's context window, and whose damage is determined almost entirely by which actions were permitted to be irreversible.

Key Insights
1. Grounding failures are structurally guaranteed by the tool abstraction layer

HTTP 200 responses acknowledge receipt but suppress consequence. An agent that patches a CRM record, receives a success code, and proceeds has no native mechanism to observe that the API silently merged and deleted the target entity. This is not an edge case — it is the default behavior of every API that models side effects as internal state transitions rather than as observable events. The partial observability problem is therefore not incidental but architectural: the tool abstraction that makes agents powerful is the same abstraction that hides the world state they need to stay grounded.

2. Error cascades are endogenous, not independent

Each grounding failure degrades the observation available to the next step. An agent operating on a now-nonexistent entity ID will receive 404s, interpret them as transient errors, and may invoke compensating tool calls that create further state mutations — all while its context window contains a coherent-looking trace of confident actions. This endogeneity distinguishes multi-step agentic failures from i.i.d. API errors and means that aggregate failure probability grows faster than linearly with pipeline length.

3. Observation brokers close the gap but introduce a relevance problem

A broker that subscribes to CDC event streams (Debezium, Kafka) and injects contradicting state back into the agent's context can make invisible grounding failures visible. The hard sub-problem is relevance filtering: only events touching the agent's current entity footprint should be injected, but transitive relevance (a merged entity that was never in the original footprint) requires schema-aware graph traversal. Speculative plan shadowing with lightweight models (~7B parameters, ~200–400ms latency) can pre-populate subscriptions, but anchors to an intent model that breaks when the agent's goal shifts.

4. Goal erosion is the slow failure mode that evades step-level detection

Incremental goal drift — each refinement step below any discontinuity threshold — cumulatively constitutes task replacement while appearing locally coherent. Asynchronous re-anchoring audits using NLI models (DeBERTa-v3-large at ~4ms per pair) against a tamper-evident session anchor can catch cumulative drift without halting execution, but are purely preventive: they cannot undo irreversible side effects already committed during the erosion window.

5. Reversibility is the correct primitive for damage control, and enforcement must be exogenous

Tool calls should be gated on irreversibility as a function of epistemic confidence, enforced at the tool wrapper layer rather than in the agent's reasoning. Cryptographic signing of reversibility classifications — with governance keys held outside the product team — makes reclassification auditable and physically evident. Asymmetric auditability (overrides trigger immutable external audit events) converts organizational pressure to ship faster into reputational and regulatory exposure, which is the only pressure that reliably counteracts it.

Common Pitfalls
Treating tool errors as i.i.d. — evaluating agents on mocked APIs that don't model destructive side effects masked by success codes.
Conflating plan refinement with goal shift — triggering unnecessary footprint invalidation on routine entity extension, or missing genuine shifts because local signals are similar.
Allowing the session anchor to drift — summarizing long sessions by updating the anchor with evolved beliefs destroys its function as an independent reference point.
Placing reversibility gates inside the agent's reasoning — an agent undergoing goal erosion cannot reliably self-assess whether to invoke a confirmation gate.
Issuing emergency override tokens without auditability — emergency mechanisms that exist will be routinely used under shipping pressure unless use automatically generates external accountability signals.
Open Question for Deeper Work

At what point in the software development lifecycle can irreversibility classification be made binding before deployment — embedded in schema design, API contract negotiation, or data model review — such that the question of whether a tool call is reversible is settled architecturally rather than governed reactively after the tool exists and product teams are already dependent on it? This upstream binding problem is the most leveraged unsolved question in safe agentic pipeline design.






