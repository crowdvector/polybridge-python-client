Changelog
=========

All notable changes to the Polybridge Python Client will be documented here.

Version 0.1.0 (Initial Release)
-------------------------------

**Release Date**: 2025-11-11

Features
~~~~~~~~

* Initial release of Polybridge Python client
* Support for market catalog, timeseries, and options endpoints
* Pandas DataFrame integration for easy data manipulation
* Full type hints and documentation
* High-level API for querying by asset, horizon, and market type
* Automatic data aggregation across multiple markets and intervals
* Clear error handling with API error details

Endpoints
~~~~~~~~~

* ``fetch_market_catalog``: Browse available prediction markets
* ``fetch_timeseries``: Fetch timeseries data with probabilities, prices, and metrics
* ``fetch_nested_timeseries``: Get hierarchical data structure
* ``fetch_up_or_down_options_timeseries``: Up-or-down options with metrics
* ``fetch_above_options_timeseries``: Above options with flexible output formats

Data Features
~~~~~~~~~~~~~

* Probability data from prediction markets
* Spot and perpetual price data
* Open interest tracking
* Options metrics (implied volatility, realized volatility, volatility premium)
* Configurable time ranges and data intervals
* Automatic chunking for large market requests

Developer Features
~~~~~~~~~~~~~~~~~~

* Python 3.8+ support
* Type hints throughout
* NumPy-style docstrings
* Connection pooling support
* Custom session support
* Configurable timeouts
* Development dependencies (pytest, black, ruff, mypy)
* Jupyter notebook examples

Known Limitations
~~~~~~~~~~~~~~~~~

* Options metrics only available for daily (1d) interval data
* Maximum request timeout: 600 seconds
