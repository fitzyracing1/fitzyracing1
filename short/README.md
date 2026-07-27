# Crypto Context AI

`Crypto Context AI` is a small Python CLI that makes a simple price-direction prediction from recent crypto price context.

It uses one core idea:

- look at the latest window of prices
- find similar historical windows
- estimate the next move from what happened after those similar patterns

This is not financial advice, and it is not a trading guarantee. It is a lightweight pattern model intended as a starting point you can extend.

## What It Does

- Downloads recent market prices from CoinGecko's public API
- Builds rolling price-context windows
- Compares the current price shape to past shapes
- Predicts whether the next move is more likely `up`, `down`, or `flat`
- Returns a confidence score and supporting details

## Requirements

- Python 3.10+

No third-party packages are required.

## Run

```bash
python main.py --coin bitcoin
```

More examples:

```bash
python main.py --coin ethereum --vs-currency usd --days 30 --window-size 24 --neighbors 8
python main.py --coin solana --flat-threshold 0.002
```

## Arguments

- `--coin`: CoinGecko coin id, such as `bitcoin`, `ethereum`, `solana`
- `--vs-currency`: Quote currency, default `usd`
- `--days`: Number of days of historical data to fetch
- `--window-size`: Number of points in each context window
- `--neighbors`: Number of similar past windows to use
- `--flat-threshold`: Threshold for treating a move as flat

## Output

Example output:

```text
Coin: bitcoin
Last price: 68241.12 USD
Prediction: up
Expected move: 0.63%
Confidence: 71.4%
Model basis: 8 nearest historical context windows from 721 samples
```

## Notes

- CoinGecko rate limits public requests, so avoid hammering the API.
- This model only uses price context. It does not use news, order book data, volume, or on-chain data.
- For better performance, the next step would usually be adding more features and a proper ML model.
