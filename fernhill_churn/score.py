"""Step 8: next month's list. Score every active customer and keep the ones worth an offer."""

from pathlib import Path


def score_month(month: str, data_dir: str | Path = "data/raw", model_path: str | Path = "models/churn_model.joblib",
                out_dir: str | Path = "out") -> Path:
    """Score the customers active on the first day of month (YYYY-MM) with the saved model, and write
    out_dir/at_risk_YYYY-MM.csv: customer_id, churn_probability (4 decimals), rank (1 = most likely to cancel),
    for the customers at or above the saved threshold, at most MAX_SHARE of the active customers."""
    raise NotImplementedError("step 8")
