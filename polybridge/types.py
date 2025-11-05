"""Type definitions for the Polybridge client."""

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass
class TimeseriesResult:
    """Container for API responses with parsed dataframes.

    Attributes
    ----------
    catalog : List[Dict[str, object]]
        Market catalog entries matching the query
    responses : Dict[str, Dict[str, object]]
        Raw API responses organized by interval
    dataframes : Dict[str, pd.DataFrame]
        Parsed pandas DataFrames for each data block
    """

    catalog: List[Dict[str, object]]
    responses: Dict[str, Dict[str, object]]
    dataframes: Dict[str, pd.DataFrame]

