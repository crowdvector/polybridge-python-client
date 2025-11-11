Examples
========

This page provides practical examples for common use cases.

Basic Examples
--------------

Fetching Recent Data
~~~~~~~~~~~~~~~~~~~~

Get the last 6 hours of data for Bitcoin:

.. code-block:: python

   from polybridge import PolybridgeClient

   client = PolybridgeClient(api_key="your-api-key-here")

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       market_types=["up-or-down"],
       hours=6,
   )

   prob_df = result.dataframes.get("probabilities")
   print(prob_df.head())

Multiple Assets
~~~~~~~~~~~~~~~

Query multiple assets separately:

.. code-block:: python

   assets = ["BTC", "ETH", "SOL"]
   results = {}

   for asset in assets:
       result = client.fetch_timeseries(
           asset=asset,
           horizons=["daily"],
           hours=24,
       )
       results[asset] = result.dataframes.get("probabilities")

   # Compare assets
   for asset, df in results.items():
       print(f"{asset}: {len(df)} records")

Comparing Horizons
~~~~~~~~~~~~~~~~~~

Compare predictions across different time horizons:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily", "weekly", "monthly"],
       market_types=["up-or-down"],
       hours=48,
   )

   # Access different intervals
   daily_df = result.dataframes.get("probabilities_5m")
   weekly_df = result.dataframes.get("probabilities_30m")
   monthly_df = result.dataframes.get("probabilities_1h")

   print(f"Daily markets: {len(daily_df)}")
   print(f"Weekly markets: {len(weekly_df)}")
   print(f"Monthly markets: {len(monthly_df)}")

Data Analysis Examples
----------------------

Probability Trends
~~~~~~~~~~~~~~~~~~

Analyze how probabilities change over time:

.. code-block:: python

   import matplotlib.pyplot as plt

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       market_types=["up-or-down"],
       hours=24,
   )

   prob_df = result.dataframes.get("probabilities")

   # Group by market and plot
   for market_id in prob_df['market_id'].unique():
       market_data = prob_df[prob_df['market_id'] == market_id]
       plt.plot(market_data['timestamp'], market_data['probability'], label=market_id)

   plt.xlabel('Time')
   plt.ylabel('Probability')
   plt.title('Probability Trends for BTC Daily Markets')
   plt.legend()
   plt.xticks(rotation=45)
   plt.tight_layout()
   plt.show()

Price Correlation
~~~~~~~~~~~~~~~~~

Examine correlation between market probabilities and spot prices:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=48,
       include_prices=True,
   )

   prob_df = result.dataframes.get("probabilities")
   price_df = result.dataframes.get("prices")

   # Merge on timestamp
   merged = prob_df.merge(price_df, on='timestamp', how='inner')

   # Calculate correlation
   correlation = merged[['probability', 'price']].corr()
   print("Correlation matrix:")
   print(correlation)

   # Scatter plot
   plt.scatter(merged['probability'], merged['price'], alpha=0.5)
   plt.xlabel('Probability')
   plt.ylabel('BTC Price (USD)')
   plt.title('Probability vs Price')
   plt.show()

Volatility Analysis
~~~~~~~~~~~~~~~~~~~

Analyze implied vs realized volatility:

.. code-block:: python

   from datetime import datetime, timedelta, timezone

   end = datetime.now(timezone.utc)
   start = end - timedelta(days=30)

   data = client.fetch_up_or_down_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       window_days=[7, 30],
   )

   import pandas as pd
   df = pd.DataFrame(data['rows'])

   # Plot IV vs RV
   fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

   # 7-day window
   ax1.plot(df['timestamp'], df['iv_7d'], label='Implied Volatility (7d)')
   ax1.plot(df['timestamp'], df['rv_7d'], label='Realized Volatility (7d)')
   ax1.set_title('7-Day Volatility Comparison')
   ax1.set_ylabel('Volatility')
   ax1.legend()
   ax1.tick_params(axis='x', rotation=45)

   # Volatility premium
   ax2.plot(df['timestamp'], df['volatility_premium_7d'], label='Volatility Premium (7d)', color='purple')
   ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)
   ax2.set_title('Volatility Premium (IV - RV)')
   ax2.set_xlabel('Time')
   ax2.set_ylabel('Premium')
   ax2.legend()
   ax2.tick_params(axis='x', rotation=45)

   plt.tight_layout()
   plt.show()

Advanced Examples
-----------------

Strike Price Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~

Analyze the distribution of strike prices for "above" markets:

.. code-block:: python

   from datetime import datetime, timedelta, timezone

   end = datetime.now(timezone.utc)
   start = end - timedelta(days=7)

   data = client.fetch_above_options_timeseries(
       asset="BTC",
       start_ts=start.isoformat(),
       end_ts=end.isoformat(),
       format="long",
   )

   import pandas as pd
   df = pd.DataFrame(data['rows'])

   # Get latest timestamp
   latest = df['timestamp'].max()
   latest_data = df[df['timestamp'] == latest]

   # Plot probability vs strike
   plt.figure(figsize=(10, 6))
   for horizon in latest_data['relative_horizon'].unique():
       horizon_data = latest_data[latest_data['relative_horizon'] == horizon]
       plt.plot(horizon_data['strike'], horizon_data['probability'],
                marker='o', label=f'Horizon: {horizon}')

   plt.xlabel('Strike Price (USD)')
   plt.ylabel('Probability')
   plt.title(f'BTC Above Probabilities by Strike ({latest})')
   plt.legend()
   plt.grid(True, alpha=0.3)
   plt.show()

Market Comparison
~~~~~~~~~~~~~~~~~

Compare different market types side by side:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       market_types=["up-or-down", "above", "below"],
       hours=24,
   )

   prob_df = result.dataframes.get("probabilities")

   # Aggregate by market type
   by_type = prob_df.groupby('market_type')['probability'].agg(['mean', 'std', 'count'])
   print("Market Statistics by Type:")
   print(by_type)

Custom Aggregations
~~~~~~~~~~~~~~~~~~~

Create custom aggregations across markets:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily", "weekly"],
       hours=48,
   )

   prob_df = result.dataframes.get("probabilities_5m")

   # Hourly averages
   prob_df['timestamp'] = pd.to_datetime(prob_df['timestamp'])
   prob_df.set_index('timestamp', inplace=True)
   hourly = prob_df.resample('1H')['probability'].mean()

   print("Hourly average probabilities:")
   print(hourly)

Real-time Monitoring
~~~~~~~~~~~~~~~~~~~~

Set up a simple monitoring script:

.. code-block:: python

   import time
   from datetime import datetime, timezone

   def monitor_market(client, asset, check_interval=300):
       """Monitor market every 5 minutes"""

       while True:
           try:
               result = client.fetch_timeseries(
                   asset=asset,
                   horizons=["daily"],
                   market_types=["up-or-down"],
                   hours=1,  # Just last hour
               )

               prob_df = result.dataframes.get("probabilities")

               if not prob_df.empty:
                   latest = prob_df.iloc[-1]
                   print(f"[{datetime.now(timezone.utc)}] {asset} - "
                         f"Probability: {latest['probability']:.4f}, "
                         f"Market: {latest['market_id']}")

               time.sleep(check_interval)

           except Exception as e:
               print(f"Error: {e}")
               time.sleep(check_interval)

   # Run monitor
   # monitor_market(client, "BTC", check_interval=300)

Export to CSV
~~~~~~~~~~~~~

Export data for external analysis:

.. code-block:: python

   result = client.fetch_timeseries(
       asset="BTC",
       horizons=["daily"],
       hours=48,
   )

   # Export all dataframes
   for name, df in result.dataframes.items():
       filename = f"btc_{name}.csv"
       df.to_csv(filename, index=False)
       print(f"Exported {len(df)} rows to {filename}")

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple assets and time ranges:

.. code-block:: python

   from datetime import datetime, timedelta, timezone

   assets = ["BTC", "ETH", "SOL"]
   days = 7

   all_data = {}

   end = datetime.now(timezone.utc)
   start = end - timedelta(days=days)

   for asset in assets:
       try:
           result = client.fetch_timeseries(
               asset=asset,
               horizons=["daily"],
               start_ts=start.isoformat(),
               end_ts=end.isoformat(),
           )

           prob_df = result.dataframes.get("probabilities")
           price_df = result.dataframes.get("prices")

           all_data[asset] = {
               'probabilities': prob_df,
               'prices': price_df,
               'market_count': len(result.catalog),
           }

           print(f"✓ {asset}: {len(prob_df)} probability records, {all_data[asset]['market_count']} markets")

       except Exception as e:
           print(f"✗ {asset}: Error - {e}")

   # Save summary
   summary = pd.DataFrame([
       {
           'asset': asset,
           'probability_records': len(data['probabilities']),
           'price_records': len(data['prices']),
           'markets': data['market_count'],
       }
       for asset, data in all_data.items()
   ])

   print("\nSummary:")
   print(summary)

Jupyter Notebook Examples
--------------------------

For interactive examples, check out the Jupyter notebooks in the ``examples/`` directory:

* ``query_updown_metrics.ipynb``: Up-or-down options analysis
* ``query_above_options_timeseries.ipynb``: Above options analysis

To run the notebooks:

.. code-block:: bash

   # Install notebook dependencies
   pip install -e ".[notebooks]"

   # Launch Jupyter
   jupyter notebook examples/

Next Steps
----------

* Review the :doc:`user-guide` for detailed explanations
* Check the :doc:`api-reference` for complete method documentation
