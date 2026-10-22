"""Steps 5 and 6: a fair split, a pipeline that prepares the features, a baseline, and two models compared."""

import pandas as pd

# Step 6: the model you chose, by its name in candidate_models().
CHOSEN_MODEL = ""


def split(table: pd.DataFrame):
    """X_train, X_test, y_train, y_test: a quarter of the customers held back for testing, with the same share
    of churners on both sides, the same way on every run."""
    raise NotImplementedError("step 5")


def make_pipeline(model=None):
    """Fill the gaps, scale the numbers and one-hot encode the categories, then the model (by default a
    logistic regression that gives churners as much weight as everyone else together)."""
    raise NotImplementedError("step 5")


def first_results(table: pd.DataFrame) -> dict[str, float]:
    """The majority-class baseline and the first logistic regression on the test set, rounded to 3 decimals."""
    raise NotImplementedError("step 5")


def candidate_models() -> dict:
    """The two models to compare, by name."""
    raise NotImplementedError("step 6")


def compare_models(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """Each candidate in make_pipeline, scored by ROC AUC with 5-fold stratified cross-validation on the
    training set: columns model, mean_roc_auc, std_roc_auc, best first."""
    raise NotImplementedError("step 6")
