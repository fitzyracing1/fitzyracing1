# Gravity Feed Weighted Model

This project provides a lightweight Python model to estimate gravity-feed mass flow rate using weighted effects from feed height, gate opening, and material bulk density.

## Model

The model predicts flow rate with a weighted linear form:

\[
\hat{q} = b_0 + b_1\sqrt{h} + b_2 g + b_3 d
\]

- `h`: head/height in meters
- `g`: gate opening fraction from `0.0` to `1.0`
- `d`: bulk density factor (relative scale)

The `fit()` method supports sample weights for weighted least squares.

## Quick Start

1. Create/activate your Python environment.
2. Install project dependencies:

```powershell
pip install -e .[dev]
```

3. Run tests:

```powershell
pytest
```

4. Run the CLI with example data:

```powershell
gravity-feed --input examples/sample_stream.csv
```

## CSV Input Format

Required headers:

- `head_m`
- `gate_open_fraction`
- `density_factor`
- `flow_rate_kg_s` (required for fitting)

## Notes

- This is a practical baseline model for calibration and monitoring.
- For production controls, validate against plant data and operating constraints.
