"""Step 1: load the export, and say who is a customer at the cutoff and who churned in the month after it."""

from datetime import date
from pathlib import Path

import pandas as pd

# Predict September 2026 from what was known on the morning of 1 September 2026.
CUTOFF = date(2026, 9, 1)


def load_raw(folder: str | Path = "data/raw") -> dict[str, pd.DataFrame]:
    """The five export files as DataFrames, keyed by file name without .csv, with their dates parsed."""
    raise NotImplementedError("step 1")


def active_at(subscriptions: pd.DataFrame, cutoff) -> pd.DataFrame:
    """The subscriptions that had started before the cutoff and were not cancelled before it."""
    raise NotImplementedError("step 1")


def label_table(subscriptions: pd.DataFrame, cutoff) -> pd.DataFrame:
    """One row per customer active at the cutoff: customer_id, and churned = 1 if they cancelled in the month
    that starts at the cutoff, else 0. Sorted by customer_id."""
    raise NotImplementedError("step 1")
