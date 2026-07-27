from __future__ import annotations

import argparse

from crypto_context_ai.api import CoinGeckoError, fetch_market_prices
from crypto_context_ai.model import predict_from_price_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Predict the next crypto move from recent price context."
    )
    parser.add_argument("--coin", default="bitcoin", help="CoinGecko coin id, such as bitcoin.")
    parser.add_argument("--vs-currency", default="usd", help="Quote currency, default usd.")
    parser.add_argument("--days", type=int, default=30, help="Days of history to fetch.")
    parser.add_argument(
        "--window-size",
        type=int,
        default=24,
        help="Number of price points in the context window.",
    )
    parser.add_argument(
        "--neighbors",
        type=int,
        default=8,
        help="Number of similar historical windows to use.",
    )
    parser.add_argument(
        "--flat-threshold",
        type=float,
        default=0.002,
        help="Absolute return threshold to classify a move as flat.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        prices = fetch_market_prices(
            coin=args.coin,
            vs_currency=args.vs_currency,
            days=args.days,
        )
        prediction = predict_from_price_context(
            prices=prices,
            window_size=args.window_size,
            neighbors=args.neighbors,
            flat_threshold=args.flat_threshold,
        )
    except (CoinGeckoError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    expected_move_pct = prediction.expected_return * 100
    confidence_pct = prediction.confidence * 100

    print(f"Coin: {args.coin}")
    print(f"Last price: {prediction.last_price:.2f} {args.vs_currency.upper()}")
    print(f"Prediction: {prediction.direction}")
    print(f"Expected move: {expected_move_pct:.2f}%")
    print(f"Confidence: {confidence_pct:.1f}%")
    print(
        "Model basis: "
        f"{prediction.neighbors_used} nearest historical context windows "
        f"from {prediction.samples_used} samples"
    )
    return 0
