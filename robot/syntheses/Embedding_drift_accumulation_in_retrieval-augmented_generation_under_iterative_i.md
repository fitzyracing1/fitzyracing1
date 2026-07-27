Thesis: When a RAG index contains vectors encoded by multiple encoder versions — a near-universal condition in any production system with rolling updates — the resulting mixed-manifold index systematically distorts query-document score distributions in ways that are geometrically predictable, operationally invisible to standard recall metrics, and self-concealing under the very monitoring strategies most teams deploy.

Key Insights

1. The contamination source is unchanged documents, not updated ones.
Engineers instinctively re-encode modified documents when deploying a new encoder, but the silent failure originates in documents whose content never changed. Even identical text produces geometrically displaced embeddings under a new encoder, meaning every un-re-encoded document — regardless of content change — becomes a stale vector that occupies the wrong region of the embedding manifold. Because these documents appear correct from a content perspective, they are never flagged for re-indexing, and the contamination accumulates invisibly across the full corpus.

2. The failure mode — false positives vs. false negatives — is determined by manifold geometry, not staleness volume.
Whether a mixed-version index degrades toward phantom retrievals (false positives) or missed retrievals (false negatives) depends on the Fréchet distance between encoder manifolds and their relative anisotropy. Large cross-family manifold separation (e.g., GTE vs. E5) produces false negatives, as queries land far from stale vectors. Small separation with differential anisotropy (same model fine-tuned on hard negatives) produces false positives, as stale vectors cluster near query projections by geometric accident. This means mitigation strategies must be diagnosis-first: the wrong intervention applied to the wrong failure mode accelerates degradation.

3. Linear adapters close the gap only within their support boundary.
A learned linear projection aligning v1 vectors into v2's manifold is theoretically justified when the two manifolds are related by a low-rank affine transformation — a reasonable assumption for fine-tune pairs. However, the adapter provably fails on out-of-support documents (those far from anchor pairs in v1 space), on corpora with high lexical-semantic mismatch, and whenever v2 uses fundamentally different normalization geometry such as matryoshka representation learning. Empirically, well-fitted Procrustes adapters on BEIR recover only 60–75% of the nDCG gap on out-of-domain corpora. Trust scoring at index time — flagging each v1 vector by its distance to the anchor convex hull — enables selective adapter application and contains this failure.

4. Merged ranking from partitioned retrieval requires score exchangeability, which mixed-manifold indexes violate by construction.
RRF and score normalization both rest on the assumption that scores or ranks represent equivalent relevance signals across partitions. When v2 embeddings are more anisotropic, they compress into a narrow high-similarity band, causing systematic rank displacement and partition dominance in merged results. The resulting artifact — one partition flooding the top-K not through relevance but through score distribution shape — is undetectable without per-hit provenance logging. Platt scaling or isotonic regression calibration per partition, grounding scores in probability-of-relevance before merging, is the principled resolution.

5. Drift detectors become blind when reference and observation drift in lockstep.
EWMA-based monitors of inter-partition score gap and provenance ratio fail precisely when the ingestion rate outpaces the calibration window — the detector's baseline shifts with the phenomenon it is trying to detect, producing anomalously low signal variance rather than an alarm. The structural solution is an index-external anchor: a frozen sentinel corpus of semantically stable documents re-encoded by every new encoder version and probed on a fixed clock schedule, decoupled entirely from the ingestion pipeline.

Common Pitfalls
Assuming partial re-encoding is safe. Teams re-encode only modified documents, leaving unchanged documents as the primary contamination source.
Applying adapter alignment without trust scoring. Using a linear adapter uniformly across all v1 vectors ignores support boundaries and inflates scores for out-of-distribution documents.
Logging only aggregate recall metrics. Recall-at-K computed without a ground-truth re-index cannot distinguish clean retrieval from partition-dominated retrieval.
Treating the mix ratio as a fixed calibration constant. In high-velocity indexes, the stale fraction drifts faster than calibration windows track, invalidating all detectors that use it as a null reference.
Using content-volatile documents as sentinels. News articles or product descriptions shift in semantic meaning, confounding geometric drift signals with legitimate content change.
Open Question for Deeper Work

All detection and mitigation strategies described here operate at the index level, treating the query encoder as fixed and trustworthy. But in systems where the query encoder is itself updated incrementally — or where users fine-tune retrieval models on logged feedback — the query manifold drifts simultaneously with the document manifold, creating a coupled drift system where no external anchor is truly stable. The open question is: what is the minimum sufficient statistic over query-document interaction logs that allows a system to jointly estimate encoder version skew and corpus drift without any fixed reference, and under what conditions does this self-supervised estimation problem become unidentifiable?






