# Polybridge Python Client

Official Python client library for the [Polybridge Analytics API](https://polybridge.ai).

## Installation

```bash
pip install polybridge-python-client
```

## Quick Start

```python
from polybridge import PolybridgeClient

# Initialize client with your API key
client = PolybridgeClient(api_key="your-api-key-here")

# Fetch timeseries data
result = client.fetch_timeseries(
    asset="BTC",
    horizons=["daily"],
    market_types=["up-or-down", "above"],
    hours=6,
)

# Access parsed dataframes
prob_df = result.dataframes.get("probabilities")
price_df = result.dataframes.get("prices")
```

## Features

- **High-level API**: Query by asset, horizon, and market type without worrying about market IDs
- **Automatic data aggregation**: Handles multiple markets and intervals automatically
- **Pandas integration**: Returns data as pandas DataFrames for easy analysis
- **Type hints**: Full type annotations for better IDE support
- **Error handling**: Clear error messages with API error details

## API Overview

### Market Catalog

Browse available markets:

```python
catalog = client.fetch_market_catalog(
    assets=["BTC", "ETH"],
    horizons=["daily", "weekly"],
    market_types=["up-or-down"],
)
```

### Timeseries Data

Fetch historical data with probabilities, prices, and options metrics:

```python
result = client.fetch_timeseries(
    asset="BTC",
    horizons=["daily", "weekly"],
    market_types=["up-or-down", "above"],
    hours=24,
    include_prices=True,
    include_options_metrics=True,
)
```

### Options Timeseries

Get specialized options data:

```python
from datetime import datetime, timedelta

end = datetime.now(timezone.utc)
start = end - timedelta(days=7)

# Up-or-down options with metrics
up_down_data = client.fetch_up_or_down_options_timeseries(
    asset="BTC",
    start_ts=start.isoformat(),
    end_ts=end.isoformat(),
    window_days=[7, 30],
)

# Above options with probabilities
above_data = client.fetch_above_options_timeseries(
    asset="BTC",
    start_ts=start.isoformat(),
    end_ts=end.isoformat(),
    format="long",  # or "wide"
)
```

### Nested Timeseries

Get hierarchical data structure:

```python
nested = client.fetch_nested_timeseries(
    asset="BTC",
    horizon="daily",
    hours=48,
    include_spot=True,
    include_perp=False,
)
```

## API Reference

### `PolybridgeClient`

Main client class for interacting with the API.

#### `__init__(api_key, *, base_url=DEFAULT_BASE_URL, timeout=60, session=None)`

Initialize the client.

- `api_key` (str): Your API key (required)
- `base_url` (str): API base URL (optional, defaults to production)
- `timeout` (int): Request timeout in seconds (default: 60)
- `session` (requests.Session): Custom session for connection pooling (optional)

#### `fetch_market_catalog(*, assets=None, horizons=None, market_types=None, start_ts=None, end_ts=None)`

Get market catalog matching filters.

Returns a dictionary with `"markets"` list.

#### `fetch_timeseries(*, asset, horizons, market_types=None, start_ts=None, end_ts=None, hours=6.0, include_prices=True, include_open_interest=True, include_options_metrics=False, prices_instrument="spot", chunk_size=10, include_probabilities=True)`

Fetch timeseries data for an asset.

Returns a `TimeseriesResult` with:
- `catalog`: List of market entries
- `responses`: Raw API responses by interval
- `dataframes`: Parsed pandas DataFrames

#### `fetch_nested_timeseries(*, asset, horizon, market_types=None, start_ts=None, end_ts=None, hours=6.0, include_spot=True, include_perp=False, include_open_interest=True, include_funding=False)`

Fetch nested timeseries data.

Returns a dictionary with `"records"` and `"meta"`.

#### `fetch_up_or_down_options_timeseries(*, asset, start_ts, end_ts, window_days=None, horizon="daily")`

Fetch up-or-down options data with metrics.

#### `fetch_above_options_timeseries(*, asset, start_ts, end_ts, format="long", horizon="daily")`

Fetch above options data with probabilities.

### `TimeseriesResult`

Dataclass containing:
- `catalog`: List[Dict[str, object]] - Market catalog entries
- `responses`: Dict[str, Dict[str, object]] - Raw API responses
- `dataframes`: Dict[str, pd.DataFrame] - Parsed DataFrames

## Requirements

- Python 3.8+
- requests >= 2.31.0
- pandas >= 2.0.0

## Development

### Environment Setup

First, set up a virtual environment:

**Using uv (recommended):**
```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all optional dependencies
uv pip install -e ".[dev,notebooks]"
```

**Using standard Python tools:**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,notebooks]"
```

### Development Workflow

```bash
# Clone the repository
git clone https://github.com/crowdvector/polybridge-python-client.git
cd polybridge-python-client

# Run tests
pytest

# Format code
black .

# Lint
ruff check .
```

### Optional Dependencies

- `dev`: Development tools (pytest, black, ruff, mypy)
- `notebooks`: Jupyter notebook support (jupyter, notebook, ipykernel, matplotlib)

Install specific groups:
```bash
pip install -e ".[dev]"          # Just dev tools
pip install -e ".[notebooks]"    # Just notebooks
pip install -e ".[dev,notebooks]" # Both
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/crowdvector/polybridge-python-client/issues).

## Changelog

### 0.1.0 (Initial Release)

- Initial release of Polybridge Python client
- Support for market catalog, timeseries, and options endpoints
- Pandas DataFrame integration
- Full type hints and documentation

