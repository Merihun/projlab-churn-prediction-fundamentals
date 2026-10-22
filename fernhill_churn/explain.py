"""Step 8: which features does the model lean on? Shuffle each one and see how much worse it gets."""

import pandas as pd


def permutation_importances(pipeline, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """For each column of X: how much the ROC AUC drops when that column is shuffled (mean and standard
    deviation over 10 shuffles). Columns feature, importance_mean, importance_std, largest first."""
    raise NotImplementedError("step 8")
