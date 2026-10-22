"""Step 3: clean the tables with written rules, and make one row per customer active at the cutoff."""

import pandas as pd


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """Regions and channels cleaned (a blank channel becomes "unknown"), ages outside 18 to 100 made missing,
    and one row per customer_id (the first), sorted by customer_id. The input is not changed."""
    raise NotImplementedError("step 3")


def clean_subscriptions(subscriptions: pd.DataFrame) -> pd.DataFrame:
    """Plans and box sizes cleaned, and prices that are not above zero made missing. The input is not changed."""
    raise NotImplementedError("step 3")


def base_table(raw: dict[str, pd.DataFrame], cutoff) -> pd.DataFrame:
    """One row per customer active at the cutoff, sorted by customer_id, with the columns customer_id,
    started_on, plan, box_size, price_gbp, age, region and acquisition_channel, all cleaned."""
    raise NotImplementedError("step 3")
