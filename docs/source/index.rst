Polybridge Python Client
========================

Official Python client library for the `Polybridge Analytics API <https://polybridge.ai>`_.

The Polybridge Python Client provides a high-level interface to query prediction market analytics data including probabilities, prices, and options metrics.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user-guide
   api-reference
   examples
   changelog

Features
--------

* **High-level API**: Query by asset, horizon, and market type without worrying about market IDs
* **Automatic data aggregation**: Handles multiple markets and intervals automatically
* **Pandas integration**: Returns data as pandas DataFrames for easy analysis
* **Type hints**: Full type annotations for better IDE support
* **Error handling**: Clear error messages with API error details

Quick Example
-------------

.. code-block:: python

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

