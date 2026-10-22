"""Step 2: profile the tables and save the three charts that show what is wrong and what matters."""

from pathlib import Path

import pandas as pd

from fernhill_churn.frame import CUTOFF

CHARTS = ("churn_by_plan.png", "age_distribution.png", "sessions_by_churn.png")


def profile(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column of df: its dtype, how many values are missing, what percentage that is (rounded
    to 1 decimal) and how many distinct values it has."""
    raise NotImplementedError("step 2")


def save_charts(raw: dict[str, pd.DataFrame], cutoff=CUTOFF, out_dir: str | Path = "reports/figures") -> list[Path]:
    """Save churn_by_plan.png, age_distribution.png and sessions_by_churn.png in out_dir; return their paths."""
    raise NotImplementedError("step 2")
