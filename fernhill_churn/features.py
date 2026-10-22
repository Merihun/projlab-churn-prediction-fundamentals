"""Step 4: features from what was known before the cutoff, and nothing after it."""

import pandas as pd

NUMERIC_FEATURES: list[str] = []  # step 4: the twelve numbers PROJECT.md defines
CATEGORICAL_FEATURES: list[str] = []  # step 4: the four categories
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

LEAKY_COLUMNS: list[str] = []  # step 4: the columns written after the cutoff


def build_features(raw: dict[str, pd.DataFrame], cutoff) -> pd.DataFrame:
    """One row per customer active at the cutoff: customer_id and the FEATURES, sorted by customer_id."""
    raise NotImplementedError("step 4")


def training_table(raw: dict[str, pd.DataFrame], cutoff) -> pd.DataFrame:
    """build_features with the label: customer_id, the FEATURES and churned, sorted by customer_id."""
    raise NotImplementedError("step 4")
