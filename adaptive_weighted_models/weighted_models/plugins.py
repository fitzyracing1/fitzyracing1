from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .rag import build_index_from_documents, save_index
from .system import AdaptiveWeightedSystem


@dataclass
class PluginBootstrapResult:
    plugin: str
    profile: str
    output_dir: Path
    index_path: Path
    model_path: Path
    train_csv: Path
    predict_csv: Path
    predictions_csv: Path
    document_count: int
    train_rows: int
    predict_rows: int


def _write_csv(path: Path, header: list[str], rows: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def bootstrap_ready_player_one(output_dir: Path) -> PluginBootstrapResult:
    """Create an immediate, game-themed starter project state.

    Generates:
    - Retrieval documents for a Ready-Player-One-style arena knowledge base
    - Training and prediction CSV files
    - Trained model artifact
    - Prediction artifact
    - Search index artifact
    """

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    documents = [
        (
            "rpo_lore_1",
            "In the OASIS arena, player performance depends on reaction speed, route planning, "
            "and cooperative strategy. Stable teams improve survival odds in high-volatility rounds.",
        ),
        (
            "rpo_lore_2",
            "Risk control matters more than short bursts of aggression when match timers are long. "
            "Low latency and disciplined movement raise objective completion rates.",
        ),
        (
            "rpo_lore_3",
            "Adaptive weighting is useful in dynamic game modes: scouting and positioning can outweigh "
            "raw speed during puzzle phases, while speed dominates during chase phases.",
        ),
        (
            "rpo_lore_4",
            "When quality telemetry drops, use fallback context and conservative scoring. "
            "Retraining should trigger if recent prediction error rises against baseline.",
        ),
        (
            "rpo_lore_5",
            "Faction coordination affects raid outcomes. Gunters usually optimize puzzle efficiency, "
            "while Sixers apply aggressive but risk-heavy pushes. Avatar roles shape support potential.",
        ),
        (
            "rpo_lore_6",
            "Quest progression should combine objective completion, tactical consistency, and team survivability. "
            "IOI threat signals should down-rank overextended loadouts.",
        ),
    ]

    for source, text in documents:
        (docs_dir / f"{source}.txt").write_text(text, encoding="utf-8")

    index = build_index_from_documents(documents)
    index_path = output_dir / "search_index.pkl"
    save_index(index, index_path)

    rng = np.random.default_rng(7)
    n_train = 240
    n_predict = 60

    # Gameplay features with explicit Ready Player One mechanics.
    agility = rng.uniform(0.2, 1.0, n_train)
    focus = rng.uniform(0.2, 1.0, n_train)
    teamwork = rng.uniform(0.0, 1.0, n_train)
    efficiency = rng.uniform(0.1, 1.0, n_train)
    risk_control = rng.uniform(0.0, 1.0, n_train)
    latency_ms = rng.uniform(15.0, 140.0, n_train)

    faction_idx = rng.integers(0, 3, size=n_train)  # 0: gunters, 1: sixers, 2: rebels
    avatar_idx = rng.integers(0, 4, size=n_train)   # 0: rogue, 1: tank, 2: scout, 3: support
    faction_gunters = (faction_idx == 0).astype(float)
    faction_sixers = (faction_idx == 1).astype(float)
    faction_rebels = (faction_idx == 2).astype(float)
    avatar_rogue = (avatar_idx == 0).astype(float)
    avatar_tank = (avatar_idx == 1).astype(float)
    avatar_scout = (avatar_idx == 2).astype(float)
    avatar_support = (avatar_idx == 3).astype(float)

    quest_progress = np.clip(0.45 * focus + 0.35 * efficiency + 0.2 * agility + rng.normal(0.0, 0.06, n_train), 0.0, 1.0)
    ioi_threat = np.clip(rng.uniform(0.0, 1.0, n_train) + 0.2 * faction_sixers, 0.0, 1.0)
    ioi_risk_weight = np.clip(ioi_threat * (1.0 - risk_control), 0.0, 1.0)
    team_raid_match = np.clip(0.5 * teamwork + 0.3 * avatar_support + 0.2 * avatar_tank + rng.normal(0.0, 0.05, n_train), 0.0, 1.0)

    regime = (agility + focus > 1.2).astype(float)
    quality = np.clip(1.0 - (latency_ms / 200.0), 0.2, 1.0)
    segment = np.clip(0.4 * teamwork + 0.35 * efficiency + 0.25 * quest_progress, 0.0, 1.0)

    target = (
        1.4 * agility
        + 1.3 * focus
        + 1.1 * teamwork
        + 1.1 * efficiency
        + 0.8 * risk_control
        + 1.2 * quest_progress
        + 0.9 * team_raid_match
        + 0.35 * faction_gunters
        + 0.2 * faction_rebels
        + 0.25 * avatar_support
        + 0.15 * avatar_scout
        - 0.008 * latency_ms
        - 0.95 * ioi_risk_weight
        + 0.4 * regime
        + rng.normal(0.0, 0.08, n_train)
    )

    train_header = [
        "agility",
        "focus",
        "teamwork",
        "resource_efficiency",
        "risk_control",
        "latency_ms",
        "faction_gunters",
        "faction_sixers",
        "faction_rebels",
        "avatar_rogue",
        "avatar_tank",
        "avatar_scout",
        "avatar_support",
        "quest_progression_score",
        "ioi_threat",
        "ioi_risk_weight",
        "team_raid_matchmaking",
        "regime",
        "quality",
        "segment",
        "target",
    ]

    train_rows = [
        [
            float(agility[i]),
            float(focus[i]),
            float(teamwork[i]),
            float(efficiency[i]),
            float(risk_control[i]),
            float(latency_ms[i]),
            float(faction_gunters[i]),
            float(faction_sixers[i]),
            float(faction_rebels[i]),
            float(avatar_rogue[i]),
            float(avatar_tank[i]),
            float(avatar_scout[i]),
            float(avatar_support[i]),
            float(quest_progress[i]),
            float(ioi_threat[i]),
            float(ioi_risk_weight[i]),
            float(team_raid_match[i]),
            float(regime[i]),
            float(quality[i]),
            float(segment[i]),
            float(target[i]),
        ]
        for i in range(n_train)
    ]

    train_csv = output_dir / "train.csv"
    _write_csv(train_csv, train_header, train_rows)

    agility_p = rng.uniform(0.2, 1.0, n_predict)
    focus_p = rng.uniform(0.2, 1.0, n_predict)
    teamwork_p = rng.uniform(0.0, 1.0, n_predict)
    efficiency_p = rng.uniform(0.1, 1.0, n_predict)
    risk_control_p = rng.uniform(0.0, 1.0, n_predict)
    latency_ms_p = rng.uniform(15.0, 140.0, n_predict)
    faction_idx_p = rng.integers(0, 3, size=n_predict)
    avatar_idx_p = rng.integers(0, 4, size=n_predict)
    faction_gunters_p = (faction_idx_p == 0).astype(float)
    faction_sixers_p = (faction_idx_p == 1).astype(float)
    faction_rebels_p = (faction_idx_p == 2).astype(float)
    avatar_rogue_p = (avatar_idx_p == 0).astype(float)
    avatar_tank_p = (avatar_idx_p == 1).astype(float)
    avatar_scout_p = (avatar_idx_p == 2).astype(float)
    avatar_support_p = (avatar_idx_p == 3).astype(float)
    quest_progress_p = np.clip(0.45 * focus_p + 0.35 * efficiency_p + 0.2 * agility_p + rng.normal(0.0, 0.06, n_predict), 0.0, 1.0)
    ioi_threat_p = np.clip(rng.uniform(0.0, 1.0, n_predict) + 0.2 * faction_sixers_p, 0.0, 1.0)
    ioi_risk_weight_p = np.clip(ioi_threat_p * (1.0 - risk_control_p), 0.0, 1.0)
    team_raid_match_p = np.clip(0.5 * teamwork_p + 0.3 * avatar_support_p + 0.2 * avatar_tank_p + rng.normal(0.0, 0.05, n_predict), 0.0, 1.0)
    regime_p = (agility_p + focus_p > 1.2).astype(float)
    quality_p = np.clip(1.0 - (latency_ms_p / 200.0), 0.2, 1.0)
    segment_p = np.clip(0.4 * teamwork_p + 0.35 * efficiency_p + 0.25 * quest_progress_p, 0.0, 1.0)

    predict_header = [
        "agility",
        "focus",
        "teamwork",
        "resource_efficiency",
        "risk_control",
        "latency_ms",
        "faction_gunters",
        "faction_sixers",
        "faction_rebels",
        "avatar_rogue",
        "avatar_tank",
        "avatar_scout",
        "avatar_support",
        "quest_progression_score",
        "ioi_threat",
        "ioi_risk_weight",
        "team_raid_matchmaking",
        "regime",
        "quality",
        "segment",
    ]

    predict_rows = [
        [
            float(agility_p[i]),
            float(focus_p[i]),
            float(teamwork_p[i]),
            float(efficiency_p[i]),
            float(risk_control_p[i]),
            float(latency_ms_p[i]),
            float(faction_gunters_p[i]),
            float(faction_sixers_p[i]),
            float(faction_rebels_p[i]),
            float(avatar_rogue_p[i]),
            float(avatar_tank_p[i]),
            float(avatar_scout_p[i]),
            float(avatar_support_p[i]),
            float(quest_progress_p[i]),
            float(ioi_threat_p[i]),
            float(ioi_risk_weight_p[i]),
            float(team_raid_match_p[i]),
            float(regime_p[i]),
            float(quality_p[i]),
            float(segment_p[i]),
        ]
        for i in range(n_predict)
    ]

    predict_csv = output_dir / "predict.csv"
    _write_csv(predict_csv, predict_header, predict_rows)

    X_train = np.column_stack(
        [
            agility,
            focus,
            teamwork,
            efficiency,
            risk_control,
            latency_ms,
            faction_gunters,
            faction_sixers,
            faction_rebels,
            avatar_rogue,
            avatar_tank,
            avatar_scout,
            avatar_support,
            quest_progress,
            ioi_threat,
            ioi_risk_weight,
            team_raid_match,
        ]
    ).astype(float)
    Z_train = np.column_stack([regime, quality, segment, ioi_threat, team_raid_match]).astype(float)
    y_train = target.astype(float)

    model = AdaptiveWeightedSystem()
    model.fit(X_train, y_train, Z_train)
    model_path = output_dir / "model.pkl"
    model.save(model_path)

    X_predict = np.column_stack(
        [
            agility_p,
            focus_p,
            teamwork_p,
            efficiency_p,
            risk_control_p,
            latency_ms_p,
            faction_gunters_p,
            faction_sixers_p,
            faction_rebels_p,
            avatar_rogue_p,
            avatar_tank_p,
            avatar_scout_p,
            avatar_support_p,
            quest_progress_p,
            ioi_threat_p,
            ioi_risk_weight_p,
            team_raid_match_p,
        ]
    ).astype(float)
    Z_predict = np.column_stack([regime_p, quality_p, segment_p, ioi_threat_p, team_raid_match_p]).astype(float)
    predictions = model.predict(X_predict, Z_predict)
    assert isinstance(predictions, np.ndarray)

    predictions_csv = output_dir / "predictions.csv"
    _write_csv(predictions_csv, ["prediction"], [[float(v)] for v in predictions])

    return PluginBootstrapResult(
        plugin="ready_player_one",
        profile="mechanics",
        output_dir=output_dir,
        index_path=index_path,
        model_path=model_path,
        train_csv=train_csv,
        predict_csv=predict_csv,
        predictions_csv=predictions_csv,
        document_count=len(documents),
        train_rows=n_train,
        predict_rows=n_predict,
    )


def bootstrap_ready_player_one_live_ops(output_dir: Path) -> PluginBootstrapResult:
    """Create a live-ops simulation profile with seasonal drift and meta shifts."""

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    documents = [
        (
            "rpo_live_ops_1",
            "Seasonal leaderboard drift changes which loadouts dominate. Models should adapt across seasons "
            "instead of overfitting one patch cycle.",
        ),
        (
            "rpo_live_ops_2",
            "Faction meta shifts alter expected raid behavior. Gunters excel at puzzle cadence, Sixers push "
            "high-risk tempo, rebels stabilize objective defense.",
        ),
        (
            "rpo_live_ops_3",
            "Raid role balancing should reward healthy composition: support and tank roles reduce wipe risk, "
            "while over-indexing scouts can increase volatility.",
        ),
        (
            "rpo_live_ops_4",
            "When IOI pressure spikes, risk weighting should tighten and retraining cadence should increase "
            "to prevent stale policy drift.",
        ),
    ]

    for source, text in documents:
        (docs_dir / f"{source}.txt").write_text(text, encoding="utf-8")

    index = build_index_from_documents(documents)
    index_path = output_dir / "search_index.pkl"
    save_index(index, index_path)

    rng = np.random.default_rng(77)
    n_train = 480
    n_predict = 120

    agility = rng.uniform(0.2, 1.0, n_train)
    focus = rng.uniform(0.2, 1.0, n_train)
    teamwork = rng.uniform(0.0, 1.0, n_train)
    efficiency = rng.uniform(0.1, 1.0, n_train)
    risk_control = rng.uniform(0.0, 1.0, n_train)
    latency_ms = rng.uniform(15.0, 160.0, n_train)

    faction_idx = rng.integers(0, 3, size=n_train)
    avatar_idx = rng.integers(0, 4, size=n_train)
    faction_gunters = (faction_idx == 0).astype(float)
    faction_sixers = (faction_idx == 1).astype(float)
    faction_rebels = (faction_idx == 2).astype(float)
    avatar_rogue = (avatar_idx == 0).astype(float)
    avatar_tank = (avatar_idx == 1).astype(float)
    avatar_scout = (avatar_idx == 2).astype(float)
    avatar_support = (avatar_idx == 3).astype(float)

    season = rng.integers(1, 5, size=n_train).astype(float)
    seasonal_leaderboard_drift = np.clip((season - 1.0) / 3.0 + rng.normal(0.0, 0.08, n_train), 0.0, 1.0)
    faction_meta_shift = np.clip(0.5 * faction_sixers + 0.3 * faction_rebels + rng.normal(0.0, 0.1, n_train), 0.0, 1.0)
    raid_role_balance = np.clip(0.45 * avatar_support + 0.35 * avatar_tank + 0.2 * teamwork + rng.normal(0.0, 0.08, n_train), 0.0, 1.0)

    quest_progress = np.clip(0.4 * focus + 0.35 * efficiency + 0.25 * agility + rng.normal(0.0, 0.07, n_train), 0.0, 1.0)
    ioi_threat = np.clip(rng.uniform(0.0, 1.0, n_train) + 0.25 * faction_sixers + 0.3 * seasonal_leaderboard_drift, 0.0, 1.0)
    ioi_risk_weight = np.clip(ioi_threat * (1.0 - risk_control + 0.2 * faction_meta_shift), 0.0, 1.0)
    team_raid_match = np.clip(0.45 * teamwork + 0.3 * raid_role_balance + 0.25 * avatar_support + rng.normal(0.0, 0.06, n_train), 0.0, 1.0)

    regime = (agility + focus > 1.2).astype(float)
    quality = np.clip(1.0 - (latency_ms / 210.0), 0.15, 1.0)
    segment = np.clip(0.3 * teamwork + 0.25 * efficiency + 0.2 * quest_progress + 0.25 * raid_role_balance, 0.0, 1.0)

    target = (
        1.25 * agility
        + 1.2 * focus
        + 1.0 * teamwork
        + 1.0 * efficiency
        + 0.75 * risk_control
        + 1.1 * quest_progress
        + 0.8 * team_raid_match
        + 0.22 * faction_gunters
        + 0.18 * avatar_support
        + 0.15 * avatar_scout
        + 0.35 * raid_role_balance
        - 0.0075 * latency_ms
        - 0.9 * ioi_risk_weight
        - 0.5 * seasonal_leaderboard_drift
        - 0.35 * faction_meta_shift
        + 0.3 * regime
        + rng.normal(0.0, 0.1, n_train)
    )

    train_header = [
        "agility",
        "focus",
        "teamwork",
        "resource_efficiency",
        "risk_control",
        "latency_ms",
        "faction_gunters",
        "faction_sixers",
        "faction_rebels",
        "avatar_rogue",
        "avatar_tank",
        "avatar_scout",
        "avatar_support",
        "quest_progression_score",
        "ioi_threat",
        "ioi_risk_weight",
        "team_raid_matchmaking",
        "season",
        "seasonal_leaderboard_drift",
        "faction_meta_shift",
        "raid_role_balance",
        "regime",
        "quality",
        "segment",
        "target",
    ]

    train_rows = [
        [
            float(agility[i]),
            float(focus[i]),
            float(teamwork[i]),
            float(efficiency[i]),
            float(risk_control[i]),
            float(latency_ms[i]),
            float(faction_gunters[i]),
            float(faction_sixers[i]),
            float(faction_rebels[i]),
            float(avatar_rogue[i]),
            float(avatar_tank[i]),
            float(avatar_scout[i]),
            float(avatar_support[i]),
            float(quest_progress[i]),
            float(ioi_threat[i]),
            float(ioi_risk_weight[i]),
            float(team_raid_match[i]),
            float(season[i]),
            float(seasonal_leaderboard_drift[i]),
            float(faction_meta_shift[i]),
            float(raid_role_balance[i]),
            float(regime[i]),
            float(quality[i]),
            float(segment[i]),
            float(target[i]),
        ]
        for i in range(n_train)
    ]

    train_csv = output_dir / "train.csv"
    _write_csv(train_csv, train_header, train_rows)

    agility_p = rng.uniform(0.2, 1.0, n_predict)
    focus_p = rng.uniform(0.2, 1.0, n_predict)
    teamwork_p = rng.uniform(0.0, 1.0, n_predict)
    efficiency_p = rng.uniform(0.1, 1.0, n_predict)
    risk_control_p = rng.uniform(0.0, 1.0, n_predict)
    latency_ms_p = rng.uniform(15.0, 160.0, n_predict)
    faction_idx_p = rng.integers(0, 3, size=n_predict)
    avatar_idx_p = rng.integers(0, 4, size=n_predict)
    faction_gunters_p = (faction_idx_p == 0).astype(float)
    faction_sixers_p = (faction_idx_p == 1).astype(float)
    faction_rebels_p = (faction_idx_p == 2).astype(float)
    avatar_rogue_p = (avatar_idx_p == 0).astype(float)
    avatar_tank_p = (avatar_idx_p == 1).astype(float)
    avatar_scout_p = (avatar_idx_p == 2).astype(float)
    avatar_support_p = (avatar_idx_p == 3).astype(float)
    season_p = rng.integers(1, 5, size=n_predict).astype(float)
    seasonal_leaderboard_drift_p = np.clip((season_p - 1.0) / 3.0 + rng.normal(0.0, 0.08, n_predict), 0.0, 1.0)
    faction_meta_shift_p = np.clip(0.5 * faction_sixers_p + 0.3 * faction_rebels_p + rng.normal(0.0, 0.1, n_predict), 0.0, 1.0)
    raid_role_balance_p = np.clip(0.45 * avatar_support_p + 0.35 * avatar_tank_p + 0.2 * teamwork_p + rng.normal(0.0, 0.08, n_predict), 0.0, 1.0)
    quest_progress_p = np.clip(0.4 * focus_p + 0.35 * efficiency_p + 0.25 * agility_p + rng.normal(0.0, 0.07, n_predict), 0.0, 1.0)
    ioi_threat_p = np.clip(rng.uniform(0.0, 1.0, n_predict) + 0.25 * faction_sixers_p + 0.3 * seasonal_leaderboard_drift_p, 0.0, 1.0)
    ioi_risk_weight_p = np.clip(ioi_threat_p * (1.0 - risk_control_p + 0.2 * faction_meta_shift_p), 0.0, 1.0)
    team_raid_match_p = np.clip(0.45 * teamwork_p + 0.3 * raid_role_balance_p + 0.25 * avatar_support_p + rng.normal(0.0, 0.06, n_predict), 0.0, 1.0)
    regime_p = (agility_p + focus_p > 1.2).astype(float)
    quality_p = np.clip(1.0 - (latency_ms_p / 210.0), 0.15, 1.0)
    segment_p = np.clip(0.3 * teamwork_p + 0.25 * efficiency_p + 0.2 * quest_progress_p + 0.25 * raid_role_balance_p, 0.0, 1.0)

    predict_header = [
        "agility",
        "focus",
        "teamwork",
        "resource_efficiency",
        "risk_control",
        "latency_ms",
        "faction_gunters",
        "faction_sixers",
        "faction_rebels",
        "avatar_rogue",
        "avatar_tank",
        "avatar_scout",
        "avatar_support",
        "quest_progression_score",
        "ioi_threat",
        "ioi_risk_weight",
        "team_raid_matchmaking",
        "season",
        "seasonal_leaderboard_drift",
        "faction_meta_shift",
        "raid_role_balance",
        "regime",
        "quality",
        "segment",
    ]

    predict_rows = [
        [
            float(agility_p[i]),
            float(focus_p[i]),
            float(teamwork_p[i]),
            float(efficiency_p[i]),
            float(risk_control_p[i]),
            float(latency_ms_p[i]),
            float(faction_gunters_p[i]),
            float(faction_sixers_p[i]),
            float(faction_rebels_p[i]),
            float(avatar_rogue_p[i]),
            float(avatar_tank_p[i]),
            float(avatar_scout_p[i]),
            float(avatar_support_p[i]),
            float(quest_progress_p[i]),
            float(ioi_threat_p[i]),
            float(ioi_risk_weight_p[i]),
            float(team_raid_match_p[i]),
            float(season_p[i]),
            float(seasonal_leaderboard_drift_p[i]),
            float(faction_meta_shift_p[i]),
            float(raid_role_balance_p[i]),
            float(regime_p[i]),
            float(quality_p[i]),
            float(segment_p[i]),
        ]
        for i in range(n_predict)
    ]

    predict_csv = output_dir / "predict.csv"
    _write_csv(predict_csv, predict_header, predict_rows)

    X_train = np.column_stack(
        [
            agility,
            focus,
            teamwork,
            efficiency,
            risk_control,
            latency_ms,
            faction_gunters,
            faction_sixers,
            faction_rebels,
            avatar_rogue,
            avatar_tank,
            avatar_scout,
            avatar_support,
            quest_progress,
            ioi_threat,
            ioi_risk_weight,
            team_raid_match,
            season,
            seasonal_leaderboard_drift,
            faction_meta_shift,
            raid_role_balance,
        ]
    ).astype(float)
    Z_train = np.column_stack(
        [regime, quality, segment, ioi_threat, team_raid_match, seasonal_leaderboard_drift, faction_meta_shift]
    ).astype(float)
    y_train = target.astype(float)

    model = AdaptiveWeightedSystem()
    model.fit(X_train, y_train, Z_train)
    model_path = output_dir / "model.pkl"
    model.save(model_path)

    X_predict = np.column_stack(
        [
            agility_p,
            focus_p,
            teamwork_p,
            efficiency_p,
            risk_control_p,
            latency_ms_p,
            faction_gunters_p,
            faction_sixers_p,
            faction_rebels_p,
            avatar_rogue_p,
            avatar_tank_p,
            avatar_scout_p,
            avatar_support_p,
            quest_progress_p,
            ioi_threat_p,
            ioi_risk_weight_p,
            team_raid_match_p,
            season_p,
            seasonal_leaderboard_drift_p,
            faction_meta_shift_p,
            raid_role_balance_p,
        ]
    ).astype(float)
    Z_predict = np.column_stack(
        [regime_p, quality_p, segment_p, ioi_threat_p, team_raid_match_p, seasonal_leaderboard_drift_p, faction_meta_shift_p]
    ).astype(float)
    predictions = model.predict(X_predict, Z_predict)
    assert isinstance(predictions, np.ndarray)

    predictions_csv = output_dir / "predictions.csv"
    _write_csv(predictions_csv, ["prediction"], [[float(v)] for v in predictions])

    return PluginBootstrapResult(
        plugin="ready_player_one",
        profile="live_ops",
        output_dir=output_dir,
        index_path=index_path,
        model_path=model_path,
        train_csv=train_csv,
        predict_csv=predict_csv,
        predictions_csv=predictions_csv,
        document_count=len(documents),
        train_rows=n_train,
        predict_rows=n_predict,
    )
