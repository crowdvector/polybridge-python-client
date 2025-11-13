"""High-level client for the Polybridge BigQuery-backed API.

This module provides a thin wrapper around the `/v1` endpoints so callers can
specify assets, horizons, and market types without worrying about individual
market identifiers or interval mappings.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Sequence

import pandas as pd
import requests

from polybridge.types import TimeseriesResult

# Horizon to interval mapping for API calls
HORIZON_INTERVAL_MAP: Dict[str, str] = {
    "daily": "5m",
    "weekly": "30m",
    "monthly": "1h",
    "yearly": "4h",
}

# Default API base URL
DEFAULT_BASE_URL = "https://us-central1-polymarket-analytics-api.cloudfunctions.net"


class PolybridgeClient:
    """High-level client for the Polybridge analytics API.

    This client provides a convenient interface to query prediction market
    analytics data including probabilities, prices, and options metrics.

    Example
    -------
    ```python
    from polybridge import PolybridgeClient

    client = PolybridgeClient(api_key="<your-key>")
    result = client.fetch_timeseries(
        asset="BTC",
        horizons=["daily"],
        market_types=["up-or-down", "above"],
        hours=6,
    )
    prob_df = result.dataframes.get("probabilities")
    price_df = result.dataframes.get("prices")
    ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 60,
        session: Optional[requests.Session] = None,
    ) -> None:
        """Initialize the Polybridge client.

        Parameters
        ----------
        api_key : str
            Your Polybridge API key (required)
        base_url : str, optional
            API base URL (defaults to production endpoint)
        timeout : int, optional
            Request timeout in seconds (default: 60)
        session : requests.Session, optional
            Custom requests session for connection pooling
        """
        if not api_key:
            raise ValueError("API key is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _post(self, endpoint: str, payload: Dict[str, object]) -> Dict[str, object]:
        """Make a POST request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=payload, timeout=self.timeout)

        # Always try to extract error details from response
        error_detail = ""
        try:
            error_data = response.json()
            if "error" in error_data:
                error_obj = error_data["error"]
                if isinstance(error_obj, dict):
                    error_detail = f"Code: {error_obj.get('code', 'UNKNOWN')}, Message: {error_obj.get('message', 'No message')}"
                    if "detail" in error_obj:
                        error_detail += f", Detail: {error_obj['detail']}"
                else:
                    error_detail = str(error_obj)
        except Exception:
            # If JSON parsing fails, use raw text
            error_detail = response.text[:500]  # Limit length

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise requests.HTTPError(
                f"{exc} | {error_detail if error_detail else response.text[:500]}",
                response=response,
            ) from None

        data = response.json()
        if "error" in data:
            error_obj = data["error"]
            error_msg = (
                error_obj.get("message", str(error_obj))
                if isinstance(error_obj, dict)
                else str(error_obj)
            )
            raise RuntimeError(f"API returned error: {error_msg}")
        return data

    @staticmethod
    def _to_iso(dt: datetime) -> str:
        """Convert datetime to ISO 8601 format with Z suffix."""
        return (
            dt.astimezone(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    @staticmethod
    def _ensure_datetime(value: Optional[str], *, fallback: datetime) -> datetime:
        """Parse ISO string to datetime or return fallback."""
        if value is None:
            return fallback
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _chunk(sequence: Sequence[str], size: int) -> Iterable[List[str]]:
        """Split sequence into chunks of given size."""
        for index in range(0, len(sequence), size):
            yield list(sequence[index : index + size])

    # ------------------------------------------------------------------
    # Catalog & timeseries APIs
    # ------------------------------------------------------------------
    def fetch_market_catalog(
        self,
        *,
        assets: Optional[Sequence[str]] = None,
        horizons: Optional[Sequence[str]] = None,
        market_types: Optional[Sequence[str]] = None,
        start_ts: Optional[str] = None,
        end_ts: Optional[str] = None,
    ) -> Dict[str, object]:
        """Fetch market catalog matching the given filters.

        Parameters
        ----------
        assets : Optional[Sequence[str]]
            Filter by asset symbols (e.g., ["BTC", "ETH"])
        horizons : Optional[Sequence[str]]
            Filter by horizons (e.g., ["daily", "weekly"])
        market_types : Optional[Sequence[str]]
            Filter by market types (e.g., ["up-or-down", "above"])
        start_ts : Optional[str]
            Start timestamp in ISO 8601 format
        end_ts : Optional[str]
            End timestamp in ISO 8601 format

        Returns
        -------
        Dict[str, object]
            Response containing "markets" list with catalog entries
        """
        payload: Dict[str, object] = {}
        if assets:
            payload["assets"] = list(assets)
        if horizons:
            payload["horizons"] = list(horizons)
        if market_types:
            payload["market_types"] = list(market_types)
        if start_ts:
            payload["start_ts"] = start_ts
        if end_ts:
            payload["end_ts"] = end_ts
        return self._post("api_v1_market_catalog", payload)

    def fetch_timeseries(
        self,
        *,
        asset: str,
        horizons: Sequence[str],
        market_types: Optional[Sequence[str]] = None,
        start_ts: Optional[str] = None,
        end_ts: Optional[str] = None,
        hours: float = 6.0,
        include_prices: bool = True,
        include_open_interest: bool = True,
        include_options_metrics: bool = False,
        prices_instrument: str = "spot",
        chunk_size: int = 10,
        include_probabilities: bool = True,
    ) -> TimeseriesResult:
        """Fetch timeseries data for an asset across multiple horizons.

        This is the main method for retrieving market data. It automatically
        handles catalog lookup, market grouping, and data aggregation.

        Parameters
        ----------
        asset : str
            Asset symbol (e.g., "BTC", "ETH")
        horizons : Sequence[str]
            List of horizons to fetch (e.g., ["daily", "weekly"])
        market_types : Optional[Sequence[str]]
            Filter by market types (e.g., ["up-or-down", "above"])
        start_ts : Optional[str]
            Start timestamp in ISO 8601 format (defaults to hours ago)
        end_ts : Optional[str]
            End timestamp in ISO 8601 format (defaults to now)
        hours : float
            Hours of data to fetch if timestamps not provided (default: 6.0)
        include_prices : bool
            Include price data (default: True)
        include_open_interest : bool
            Include open interest data (default: True)
        include_options_metrics : bool
            Include options metrics (IV, RV, etc.) (default: False)
        prices_instrument : str
            Price instrument type: "spot" or "perp" (default: "spot")
        chunk_size : int
            Number of markets to request per API call (default: 10)
        include_probabilities : bool
            Include probability data (default: True)

        Returns
        -------
        TimeseriesResult
            Result containing catalog, raw responses, and parsed dataframes
        """
        if not horizons:
            raise ValueError("At least one horizon must be provided")

        end_dt = self._ensure_datetime(end_ts, fallback=datetime.now(timezone.utc))
        start_dt = self._ensure_datetime(
            start_ts, fallback=end_dt - timedelta(hours=hours)
        )

        catalog_response = self.fetch_market_catalog(
            assets=[asset],
            horizons=horizons,
            market_types=market_types,
            start_ts=self._to_iso(start_dt) if start_ts else None,
            end_ts=self._to_iso(end_dt) if end_ts else None,
        )
        catalog = catalog_response.get("markets", [])
        if not catalog:
            return TimeseriesResult(catalog=[], responses={}, dataframes={})

        markets_by_interval: Dict[str, List[str]] = defaultdict(list)
        for entry in catalog:
            horizon = entry.get("horizon")
            market_id = entry.get("market_id")
            if not horizon or not market_id:
                continue
            interval = HORIZON_INTERVAL_MAP.get(horizon)
            if interval:
                markets_by_interval[interval].append(market_id)

        merged_responses: Dict[str, Dict[str, object]] = {}
        dataframes: Dict[str, pd.DataFrame] = {}

        for interval, market_ids in markets_by_interval.items():
            unique_ids = sorted(set(market_ids))
            if not unique_ids:
                continue

            aggregated: Dict[str, object] = {}

            for chunk in self._chunk(unique_ids, chunk_size):
                payload: Dict[str, object] = {
                    "markets": chunk,
                    "interval": interval,
                    "start_ts": self._to_iso(start_dt),
                    "end_ts": self._to_iso(end_dt),
                    "blocks": [],
                }

                if include_probabilities:
                    payload["blocks"].append("probabilities")

                if include_prices:
                    payload["blocks"].append("prices")
                    payload["prices"] = {
                        "instrument_type": prices_instrument,
                        "include_open_interest": include_open_interest,
                    }

                if include_options_metrics and interval == "1d":
                    payload["blocks"].append("options_metrics")

                response = self._post("api_v1_merged", payload)
                aggregated = self._merge_responses(aggregated, response)

            merged_responses[interval] = aggregated

            for block, frame in self._response_to_frames(aggregated).items():
                key = block if len(markets_by_interval) == 1 else f"{block}_{interval}"
                dataframes[key] = frame

        return TimeseriesResult(
            catalog=catalog,
            responses=merged_responses,
            dataframes=dataframes,
        )

    def fetch_up_or_down_options_timeseries(
        self,
        *,
        asset: str,
        start_ts: str,
        end_ts: str,
        window_days: Optional[Sequence[int]] = None,
        horizon: str = "daily",
    ) -> Dict[str, object]:
        """Fetch up-or-down options timeseries data with probabilities and metrics.

        Returns flattened time-series data with:
        - Up-or-down probabilities for "next" and "next+1" markets
        - Options metrics (IV, RV, volatility_premium) for both horizons
        - Spot prices with exchange source

        Parameters
        ----------
        asset : str
            Asset symbol (e.g., "BTC", "ETH")
        start_ts : str
            Start timestamp in ISO 8601 format
        end_ts : str
            End timestamp in ISO 8601 format
        window_days : Optional[Sequence[int]]
            Rolling window days for metrics (default: [7, 30])
        horizon : str
            Market horizon (default: "daily", only daily supported)

        Returns
        -------
        Dict[str, object]
            Response with "rows" (list of flattened records) and "meta"
        """
        payload: Dict[str, object] = {
            "asset": asset,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "horizon": horizon,
        }

        if window_days:
            payload["window_days"] = list(window_days)

        return self._post("api_v1_up_or_down_options_timeseries", payload)

    def fetch_above_options_timeseries(
        self,
        *,
        asset: str,
        start_ts: str,
        end_ts: str,
        format: str = "long",
        horizon: str = "daily",
    ) -> Dict[str, object]:
        """Fetch above options timeseries data with probabilities and prices.

        Returns flattened time-series data with:
        - Above probabilities for multiple relative horizons (e.g., "next", "next+1", ...)
        - Strike prices for each probability
        - Spot prices with exchange source

        Parameters
        ----------
        asset : str
            Asset symbol (e.g., "BTC", "ETH")
        start_ts : str
            Start timestamp in ISO 8601 format
        end_ts : str
            End timestamp in ISO 8601 format
        format : str
            Output format: "long" (one row per timestamp+horizon+strike) or
            "wide" (one row per timestamp, with sorted strike columns)
            Default: "long"
        horizon : str
            Market horizon (default: "daily", only daily supported)

        Returns
        -------
        Dict[str, object]
            Response with "rows" (list of flattened records) and "meta"
        """
        payload: Dict[str, object] = {
            "asset": asset,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "format": format,
            "horizon": horizon,
        }

        return self._post("api_v1_above_options_timeseries", payload)

    # ------------------------------------------------------------------
    # Response utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _merge_responses(
        destination: Dict[str, object], source: Dict[str, object]
    ) -> Dict[str, object]:
        """Merge API responses from multiple chunks."""
        if not destination:
            return source

        for block in ("probabilities", "prices", "options_metrics"):
            if block not in source:
                continue
            block_data = source[block]
            if block not in destination:
                destination[block] = {
                    "columns": block_data.get("columns", []),
                    "rows": list(block_data.get("rows", [])),
                }
            else:
                destination[block]["rows"].extend(block_data.get("rows", []))

        if "meta" in source:
            destination.setdefault("meta", source["meta"])

        return destination

    @staticmethod
    def _response_to_frames(response: Dict[str, object]) -> Dict[str, pd.DataFrame]:
        """Convert API response blocks to pandas DataFrames."""
        frames: Dict[str, pd.DataFrame] = {}
        for block in ("probabilities", "prices", "options_metrics"):
            if block in response and isinstance(response[block], dict):
                rows = response[block].get("rows", [])
                frames[block] = pd.DataFrame(rows) if rows else pd.DataFrame()
        return frames

