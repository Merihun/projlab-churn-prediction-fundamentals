"""Steps 7 and 8: fit the chosen model, choose the threshold, and write what the business needs to trust it."""

from pathlib import Path

from fernhill_churn.frame import CUTOFF


def train(data_dir: str | Path = "data/raw", cutoff=CUTOFF, root: str | Path = ".") -> dict:
    """Fit CHOSEN_MODEL on the training customers, evaluate it on the test customers and write, under root,
    reports/metrics.json, reports/profit_by_threshold.csv, the four evaluation charts in reports/figures/,
    reports/permutation_importance.csv and models/churn_model.joblib. Returns the metrics."""
    raise NotImplementedError("step 7")
