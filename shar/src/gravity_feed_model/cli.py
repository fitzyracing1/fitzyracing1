from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .model import GravityFeedObservation, GravityFeedWeightedModel


def load_observations(csv_path: Path) -> list[GravityFeedObservation]:
    observations: list[GravityFeedObservation] = []
    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"head_m", "gate_open_fraction", "density_factor", "flow_rate_kg_s"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        for row in reader:
            observations.append(
                GravityFeedObservation(
                    head_m=float(row["head_m"]),
                    gate_open_fraction=float(row["gate_open_fraction"]),
                    density_factor=float(row["density_factor"]),
                    flow_rate_kg_s=float(row["flow_rate_kg_s"]),
                    sample_weight=float(row.get("sample_weight", 1.0)),
                )
            )
    return observations


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate gravity-feed weighted model")
    parser.add_argument("--input", required=True, type=Path, help="CSV input path")
    parser.add_argument("--head", type=float, default=2.0, help="Prediction head_m")
    parser.add_argument("--gate", type=float, default=0.5, help="Prediction gate_open_fraction")
    parser.add_argument("--density", type=float, default=1.0, help="Prediction density_factor")
    args = parser.parse_args()

    observations = load_observations(args.input)
    model = GravityFeedWeightedModel()
    model.fit(observations)
    prediction = model.predict(args.head, args.gate, args.density)

    print("Fitted coefficients:")
    print(f"b0={model.coefficients[0]:.6f}, b1={model.coefficients[1]:.6f}, b2={model.coefficients[2]:.6f}, b3={model.coefficients[3]:.6f}")
    print(f"Predicted flow rate (kg/s): {prediction:.6f}")


if __name__ == "__main__":
    main()
