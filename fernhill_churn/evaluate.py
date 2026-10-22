"""Step 7: from scores to a decision. Who gets the retention offer, and what is it worth?"""

from pathlib import Path

import pandas as pd

# Marketing's numbers (PROJECT.md, "The offer").
OFFER_COST = 15.0  # £ per customer offered
SAVED_VALUE = 120.0  # £ of margin from a customer who stays because of the offer
SAVE_RATE = 0.4  # share of customers about to cancel who stay when offered
MAX_SHARE = 0.10  # the budget: offers for at most 10% of active customers a month
THRESHOLDS = [round(i / 100, 2) for i in range(1, 100)]


def profit_table(y_true, scores) -> pd.DataFrame:
    """For every threshold in THRESHOLDS: who would be offered (score at or above it), how many of them are
    churners, precision, recall and the expected profit of making those offers."""
    raise NotImplementedError("step 7")


def choose_threshold(table: pd.DataFrame, customers: int, max_share: float = MAX_SHARE) -> float:
    """The threshold with the highest profit among those that offer to at most max_share of the customers;
    on a tie, the highest such threshold (fewer offers for the same money)."""
    raise NotImplementedError("step 7")


def save_evaluation_charts(y_true, scores, threshold: float, out_dir: str | Path = "reports/figures") -> list[Path]:
    """confusion_matrix.png (at the threshold), roc_curve.png, precision_recall_curve.png and
    profit_by_threshold.png in out_dir; returns their paths."""
    raise NotImplementedError("step 7")
