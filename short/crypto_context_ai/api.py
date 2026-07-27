from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


API_BASE = "https://api.coingecko.com/api/v3"


@dataclass(frozen=True)
class PricePoint:
    timestamp_ms: int
    price: float


class CoinGeckoError(RuntimeError):
    """Raised when CoinGecko data cannot be loaded."""


def fetch_market_prices(coin: str, vs_currency: str = "usd", days: int = 30) -> List[PricePoint]:
    query = urlencode(
        {
            "vs_currency": vs_currency,
            "days": str(days),
            "interval": "hourly",
        }
    )
    url = f"{API_BASE}/coins/{coin}/market_chart?{query}"

    try:
        with urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise CoinGeckoError(f"CoinGecko returned HTTP {exc.code} for coin '{coin}'.") from exc
    except URLError as exc:
        raise CoinGeckoError("Unable to reach CoinGecko. Check your network connection.") from exc
    except json.JSONDecodeError as exc:
        raise CoinGeckoError("CoinGecko returned invalid JSON.") from exc

    prices = payload.get("prices")
    if not isinstance(prices, list) or not prices:
        raise CoinGeckoError(f"No price data returned for coin '{coin}'.")

    cleaned: List[PricePoint] = []
    for entry in prices:
        if not isinstance(entry, list) or len(entry) < 2:
            continue

        timestamp_ms, price = entry[0], entry[1]
        try:
            cleaned.append(PricePoint(timestamp_ms=int(timestamp_ms), price=float(price)))
        except (TypeError, ValueError):
            continue

    if len(cleaned) < 10:
        raise CoinGeckoError("Not enough valid price points were returned to run the model.")

    return cleaned
