Quick Start
===========

This guide will help you get started with the Polybridge Python Client.

Setting Up
----------

First, initialize the client with your API key:

.. code-block:: python

   from polybridge import PolybridgeClient

   client = PolybridgeClient(api_key="your-api-key-here")

You can also customize the base URL, timeout, and session:

.. code-block:: python

   import requests

   session = requests.Session()
   client = PolybridgeClient(
       api_key="your-api-key-here",
       base_url="https://custom-endpoint.example.com",
       timeout=120,
       session=session
   )

Fetching Market Data
--------------------

Basic Timeseries Query
~~~~~~~~~~~~~~~~~~~~~~

Fetch timeseries data for an asset:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       market_types=["up-or-down", "above"],
       hours=6,
   )

   # Access the data
   prob_df = result.dataframes.get("probabilities")
   price_df = result.dataframes.get("prices")

   print(prob_df.head())
   print(price_df.head())

Multiple Horizons
~~~~~~~~~~~~~~~~~

Query multiple time horizons at once:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily", "weekly"],
       market_types=["up-or-down"],
       hours=24,
   )

   # DataFrames are separated by interval
   prob_5m_df = result.dataframes.get("probabilities_5m")
   prob_30m_df = result.dataframes.get("probabilities_30m")

Include Options Metrics
~~~~~~~~~~~~~~~~~~~~~~~

Add options metrics like implied volatility:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       market_types=["up-or-down"],
       hours=48,
       include_options_metrics=True,
   )

   options_df = result.dataframes.get("options_metrics")
   print(options_df[["timestamp", "iv_7d", "rv_7d", "volatility_premium_7d"]])

Browsing Markets
----------------

Explore Available Markets
~~~~~~~~~~~~~~~~~~~~~~~~~

Use the market catalog to see what's available:

.. code-block:: python

   catalog = client.fetch_market_catalog(
       assets=["BTC", "ETH"],
       horizons=["daily", "weekly"],
       market_types=["up-or-down"],
   )

   # View all markets
   for market in catalog["markets"]:
       print(f"{market['asset']} - {market['horizon']} - {market['market_type']}")

Specialized Queries
-------------------

Up-or-Down Options
~~~~~~~~~~~~~~~~~~

Get specialized up-or-down options data with metrics:

.. code-block:: python

   from datetime import datetime, timedelta, timezone

   end = datetime.now(timezone.utc)
   start = end - timedelta(days=7)

   data = client.fetch_up_or_down_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       window_days=[7, 30],
   )

   print(data["rows"][:5])

Above Options
~~~~~~~~~~~~~

Query above options with different output formats:

.. code-block:: python

   # Long format (one row per timestamp + horizon + strike)
   long_data = client.fetch_above_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       format="long",
   )

   # Wide format (one row per timestamp)
   wide_data = client.fetch_above_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       format="wide",
   )

Nested Timeseries
~~~~~~~~~~~~~~~~~

Get hierarchical data structure:

.. code-block:: python

   nested = client.fetch_nested_timeseries(
       asset="BTC",
       horizon="daily",
       hours=48,
       include_spot=True,
       include_perp=False,
   )

   print(f"Found {len(nested['records'])} records")

Error Handling
--------------

The client provides clear error messages:

.. code-block:: python

   try:
       result = client.fetch_timeseries(
           asset="INVALID",
           horizons=["daily"],
           hours=6,
       )
   except Exception as e:
       print(f"Error: {e}")

Next Steps
----------

* Read the :doc:`user-guide` for detailed explanations
* Check the :doc:`api-reference` for complete API documentation
* Explore the :doc:`examples` for more use cases
