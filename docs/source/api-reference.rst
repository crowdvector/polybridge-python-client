API Reference
=============

This page contains the complete API reference for the Polybridge Python Client.

Client
------

.. autoclass:: polybridge.PolybridgeClient
   :members:
   :undoc-members:
   :show-inheritance:

Types
-----

.. automodule:: polybridge.types
   :members:
   :undoc-members:
   :show-inheritance:

Constants
---------

Horizon to Interval Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The client uses the following mapping to convert horizons to data intervals:

.. code-block:: python

   HORIZON_INTERVAL_MAP = {
       "daily": "5m",     # 5-minute intervals
       "weekly": "30m",   # 30-minute intervals
       "monthly": "1h",   # 1-hour intervals
       "yearly": "4h",    # 4-hour intervals
   }

Default Base URL
~~~~~~~~~~~~~~~~

.. code-block:: python

   DEFAULT_BASE_URL = "https://us-central1-polymarket-analytics-api.cloudfunctions.net"
