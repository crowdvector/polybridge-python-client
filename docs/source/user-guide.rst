User Guide
==========

This guide covers the main concepts and usage patterns for the Polybridge Python Client.

Core Concepts
-------------

Assets
~~~~~~

Assets represent cryptocurrencies like BTC, ETH, SOL, etc. Each asset has associated prediction markets.

Horizons
~~~~~~~~

Horizons represent the time period for predictions:

* ``daily``: Next day predictions (uses 5-minute data intervals)
* ``weekly``: Next week predictions (uses 30-minute intervals)
* ``monthly``: Next month predictions (uses 1-hour intervals)
* ``yearly``: Next year predictions (uses 4-hour intervals)

Market Types
~~~~~~~~~~~~

Different types of prediction markets:

* ``up-or-down``: Binary markets predicting if price goes up or down
* ``above``: Markets predicting if price will be above certain strikes
* ``below``: Markets predicting if price will be below certain strikes

Client Initialization
---------------------

The PolybridgeClient requires an API key:

.. code-block:: python

   from polybridge import PolybridgeClient

   client = PolybridgeClient(api_key="your-api-key-here")

Optional Parameters
~~~~~~~~~~~~~~~~~~~

You can customize the client behavior:

.. code-block:: python

   import requests

   # Use custom session for connection pooling
   session = requests.Session()

   client = PolybridgeClient(
       api_key="your-api-key-here",
       base_url="https://custom-endpoint.example.com",  # Custom API endpoint
       timeout=120,  # Timeout in seconds (default: 60)
       session=session  # Custom requests session
   )

Working with Timeseries Data
-----------------------------

Basic Usage
~~~~~~~~~~~

The main method for fetching data is ``fetch_timeseries``:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       market_types=["up-or-down"],
       hours=24,  # Last 24 hours
   )

Understanding TimeseriesResult
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The result contains three main components:

.. code-block:: python

   # 1. Catalog: List of markets that matched your query
   print(len(result.catalog), "markets found")

   # 2. Responses: Raw API responses organized by interval
   for interval, response in result.responses.items():
       print(f"Interval {interval}: {len(response.get('probabilities', {}).get('rows', []))} rows")

   # 3. DataFrames: Parsed pandas DataFrames for easy analysis
   prob_df = result.dataframes.get("probabilities")
   price_df = result.dataframes.get("prices")

Data Blocks
~~~~~~~~~~~

You can control which data blocks are included:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=12,
       include_probabilities=True,      # Market probabilities (default: True)
       include_prices=True,              # Asset prices (default: True)
       include_open_interest=True,       # Open interest data (default: True)
       include_options_metrics=False,    # IV, RV, volatility premium (default: False)
   )

Price Instruments
~~~~~~~~~~~~~~~~~

Choose between spot and perpetual prices:

.. code-block:: python

   # Spot prices (default)
   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=6,
       prices_instrument="spot",
   )

   # Perpetual prices
   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=6,
       prices_instrument="perp",
   )

Custom Time Ranges
~~~~~~~~~~~~~~~~~~

Use ISO timestamps for precise time ranges:

.. code-block:: python

   from datetime import datetime, timedelta, timezone

   end = datetime.now(timezone.utc)
   start = end - timedelta(days=7)

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily", "weekly"],
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
   )

Multiple Horizons and Intervals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When fetching multiple horizons, dataframes are organized by interval:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily", "weekly"],  # 5m and 30m intervals
       market_types=["up-or-down"],
       hours=24,
   )

   # Access by interval suffix
   prob_5m = result.dataframes.get("probabilities_5m")
   prob_30m = result.dataframes.get("probabilities_30m")

   price_5m = result.dataframes.get("prices_5m")
   price_30m = result.dataframes.get("prices_30m")

Market Catalog
--------------

Browse Available Markets
~~~~~~~~~~~~~~~~~~~~~~~~

Use the catalog to discover available markets:

.. code-block:: python

   catalog = client.fetch_market_catalog(
       assets=["BTC", "ETH", "SOL"],
       horizons=["daily", "weekly"],
       market_types=["up-or-down", "above"],
   )

   for market in catalog["markets"]:
       print(f"{market['asset']:5} | {market['horizon']:7} | {market['market_type']:12} | {market['market_id']}")

Filter by Time Range
~~~~~~~~~~~~~~~~~~~~

Catalog can be filtered by when markets are active:

.. code-block:: python

   from datetime import datetime, timezone

   catalog = client.fetch_market_catalog(
       assets=["BTC"],
       start_ts=datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat(),
       end_ts=datetime(2025, 1, 31, tzinfo=timezone.utc).isoformat(),
   )

Specialized Endpoints
---------------------

Up-or-Down Options
~~~~~~~~~~~~~~~~~~

Get flattened time-series with options metrics:

.. code-block:: python

   from datetime import datetime, timedelta, timezone

   end = datetime.now(timezone.utc)
   start = end - timedelta(days=30)

   data = client.fetch_up_or_down_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       window_days=[7, 30],  # Rolling window calculations
       horizon="daily",
   )

   # Returns: rows with probabilities and metrics
   # - up/down probabilities for "next" and "next+1" markets
   # - iv_7d, iv_30d: implied volatility
   # - rv_7d, rv_30d: realized volatility
   # - volatility_premium_7d, volatility_premium_30d

Above Options
~~~~~~~~~~~~~

Query above options with flexible output formats:

.. code-block:: python

   # Long format: one row per (timestamp, horizon, strike)
   long_data = client.fetch_above_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       format="long",
       horizon="daily",
   )

   # Wide format: one row per timestamp with strike columns
   wide_data = client.fetch_above_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       format="wide",
       horizon="daily",
   )

Nested Timeseries
~~~~~~~~~~~~~~~~~

Get hierarchical data structure with markets nested by timestamp:

.. code-block:: python

   nested = client.fetch_nested_timeseries(
       asset="BTC",
       horizon="daily",
       market_types=["up-or-down", "above"],
       hours=24,
       include_spot=True,
       include_perp=False,
       include_open_interest=True,
       include_funding=False,
   )

   # Structure:
   # {
   #   "records": [
   #     {
   #       "timestamp": "...",
   #       "spot_price": {...},
   #       "markets": [...]
   #     }
   #   ],
   #   "meta": {...}
   # }

Working with DataFrames
-----------------------

Common DataFrame Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The returned DataFrames integrate seamlessly with pandas:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=24,
   )

   prob_df = result.dataframes.get("probabilities")

   # Basic operations
   print(prob_df.head())
   print(prob_df.describe())
   print(prob_df.columns)

   # Filtering
   recent = prob_df[prob_df['timestamp'] > '2025-01-01']

   # Grouping
   by_market = prob_df.groupby('market_id').mean()

   # Plotting
   import matplotlib.pyplot as plt
   prob_df.plot(x='timestamp', y='probability')
   plt.show()

Combining Price and Probability Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=48,
   )

   prob_df = result.dataframes.get("probabilities")
   price_df = result.dataframes.get("prices")

   # Merge on timestamp
   merged = prob_df.merge(price_df, on='timestamp', how='inner')

   # Analyze relationships
   correlation = merged[['probability', 'price']].corr()
   print(correlation)

Error Handling
--------------

API Errors
~~~~~~~~~~

The client raises clear exceptions with API error details:

.. code-block:: python

   import requests

   try:
       result = client.fetch_timeseries(
           asset="NONEXISTENT",
           horizons=["daily"],
           hours=6,
       )
   except requests.HTTPError as e:
       print(f"HTTP Error: {e}")
   except RuntimeError as e:
       print(f"API Error: {e}")

Validation Errors
~~~~~~~~~~~~~~~~~

The client validates inputs before making API calls:

.. code-block:: python

   try:
       client = PolybridgeClient(api_key="")
   except ValueError as e:
       print(f"Validation Error: {e}")

   try:
       result = client.fetch_timeseries(
           asset="BTC",
           horizons=[],  # Empty list
           hours=6,
       )
   except ValueError as e:
       print(f"Validation Error: {e}")

Best Practices
--------------

Connection Pooling
~~~~~~~~~~~~~~~~~~

Use a session for better performance with multiple requests:

.. code-block:: python

   import requests

   session = requests.Session()
   client = PolybridgeClient(api_key="your-key", session=session)

   # Make multiple requests efficiently
   btc_result = client.fetch_timeseries(asset="BTC", horizons=["daily"], hours=6)
   eth_result = client.fetch_timeseries(asset="ETH", horizons=["daily"], hours=6)
   sol_result = client.fetch_timeseries(asset="SOL", horizons=["daily"], hours=6)

Chunking Large Requests
~~~~~~~~~~~~~~~~~~~~~~~~

The client automatically chunks large market lists:

.. code-block:: python

   # This will be automatically split into chunks
   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily", "weekly", "monthly"],
       market_types=["up-or-down", "above"],
       hours=24,
       chunk_size=10,  # Request 10 markets at a time (default)
   )

Efficient Time Ranges
~~~~~~~~~~~~~~~~~~~~~

Request only the data you need:

.. code-block:: python

   # Good: specific time range
   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=6,  # Just last 6 hours
   )

   # Less efficient: large time range
   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=720,  # 30 days of 5-minute data
   )

Next Steps
----------

* Explore the :doc:`api-reference` for complete method documentation
* Check out the :doc:`examples` for more use cases
* See the :doc:`changelog` for version history
