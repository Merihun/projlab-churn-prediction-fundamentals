# Will They Stay? Predicting Subscription Churn

What this starter gives you, where things are, and the rules every check compares against.

Fernhill Box is Fernhill Outfitters' monthly box of outdoor kit. Every month some subscribers cancel.
Marketing has a retention offer, a free upgrade to the next box size, and the budget to send it to a limited
number of customers each month. They want a list of the customers most likely to cancel next month, and a
reason to trust it. You build that list: from the raw export to a tested command that writes it.

| Provided | What it is |
|----------|------------|
| `fernhill_box/` | Makes the data you work on. You do not change it. |
| `fernhill_churn/` | Your package. Each module has the functions a step asks for, with their docstrings and `raise NotImplementedError`: you replace that with the code. `cli.py` and `__main__.py` are written for you (step 8 adds one command). |
| `answers/` | Your written answers: `framing.txt`, `eda.md`, `leakage.md`, `baseline.txt`, `models.txt`, `model_card.md`. |
| `notebooks/explore.ipynb` | A notebook to look at the data in JupyterLab. Nothing in it is checked. |
| `Makefile` | `make data`, `make explore`, `make train`, `make score`, `make test`, `make lint`, `make notebook`, `make check`. Plain `make` lists them. |
| `pytest.ini`, `ruff.toml` | Settings for pytest and ruff. |

## Where to run Python

**In the lab** (recommended): start it with `docker compose up -d --build --wait`, then open a terminal in
the workspace with `docker compose exec workspace bash` (in VS Code or Codespaces: Terminal → New Terminal).
You are in `/workspace`, this folder. Python 3.12, pandas, scikit-learn, matplotlib, joblib, JupyterLab,
pytest and ruff are installed. JupyterLab is at <http://127.0.0.1:8888> (token `projlab`); open
`notebooks/explore.ipynb` there.

**On your own computer**: you need Python 3.12. Make a virtual environment and install the pinned packages
once: `python3 -m venv .venv`, `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then
`python -m pip install -r requirements.txt`. Without the virtual environment the command may be `python3`;
with `make`, add `PYTHON=python3`.

Run every command from this folder (the one with `Makefile` in it): `python -m fernhill_churn` finds your
package because Python looks in the current folder.

## Make the data

    python -m fernhill_box        (or: make data)

It writes `data/raw/` and prints the five files and their rows. Every copy of the project gets exactly the
same files; run it again whenever you want them back as they were. `data/` is in `.gitignore`.

| File | One row per | Columns |
|------|-------------|---------|
| `customers.csv` | customer, from the CRM | `customer_id`, `created_on`, `age`, `region`, `acquisition_channel` |
| `subscriptions.csv` | subscription (one per customer) | `subscription_id`, `customer_id`, `plan`, `box_size`, `price_gbp` (a month), `started_on`, `status`, `cancelled_on`, `cancellation_reason` |
| `boxes.csv` | monthly box | `box_id`, `customer_id`, `scheduled_on`, `status` (`shipped` or `skipped`), `amount_gbp` (0.00 when skipped), `rating` (1 to 5, often blank) |
| `app_sessions.csv` | session in the Fernhill app | `session_id`, `customer_id`, `started_at` (date and time, UTC), `minutes` |
| `support_tickets.csv` | support ticket | `ticket_id`, `customer_id`, `opened_on`, `category` |

Fernhill Box launched on 1 July 2025 and the app on 1 April 2026. The export was taken on 1 October 2026: it
holds everything that happened before that day. A box is due every month on the day of the month the customer
started (the 28th at the latest).

## What is wrong with the files

Like every real export, these have problems. They are planted on purpose; the steps teach you to find them.

- **Text written in different ways**: in `customers.csv` some regions have extra spaces or other capitals
  (`" north west"`, `"NORTH WEST"`); in `subscriptions.csv` the plan does too (`"monthly "`, `"MONTHLY"`).
- **Missing values**: some ages and acquisition channels are blank, most boxes have no rating, a few prices
  are blank.
- **Impossible values**: some ages no customer can have, and some prices a subscription can't cost.
- **Duplicates**: some customers are in `customers.csv` twice.
- **Columns from the future**: three columns of `subscriptions.csv` were written on export day, not before.
  Step 4 is about finding them.
- **Imbalance**: most customers don't cancel in any given month.

## The rules

These are the definitions every check compares against.

**The cutoff** is 1 September 2026 (`CUTOFF` in `frame.py`). We predict September from what was known on the
morning of 1 September: anything dated on or after the cutoff can't be used.

**Active at the cutoff**: the subscription started before the cutoff (`started_on < cutoff`) and was not
cancelled before it (`cancelled_on` is empty or `cancelled_on >= cutoff`). These are the customers we score.

**Churned** (the label): 1 if `cancelled_on` is on or after the cutoff and before the same day a month later
(`cutoff <= cancelled_on < cutoff + 1 month`), else 0. For the cutoff of 1 September that is September.

**Cleaning**:

- Every text category (`region`, `acquisition_channel`, `plan`, `box_size`): spaces stripped from both ends,
  then lower case (`"North West "` becomes `"north west"`). A blank `acquisition_channel` becomes `"unknown"`.
- An `age` below 18 or above 100 is impossible and becomes missing (NaN); 18 and 100 are kept.
- A `price_gbp` of zero or less is impossible and becomes missing (NaN).
- One row per `customer_id` in the customers: the first one in the file, after cleaning.

**Features** of a customer at the cutoff, from the rows dated before it only. A window "of the last N days" is
`cutoff - N days <= date < cutoff`; for app sessions, the date and time `started_at`.

| Feature | Definition | When there is nothing |
|---------|------------|------------------------|
| `tenure_days` | days from `started_on` to the cutoff | |
| `age` | cleaned age | NaN |
| `price_gbp` | cleaned price | NaN |
| `boxes_last_90d` | boxes with status `shipped` scheduled in the last 90 days | 0 |
| `skips_last_90d` | boxes with status `skipped` scheduled in the last 90 days | 0 |
| `spend_last_90d` | sum of `amount_gbp` of the boxes scheduled in the last 90 days | 0 |
| `avg_rating_last_90d` | mean `rating` of the boxes scheduled in the last 90 days that have one | NaN |
| `days_since_last_box` | days from the latest `shipped` box scheduled before the cutoff (at any time) to the cutoff | NaN |
| `sessions_last_30d` | app sessions started in the last 30 days | 0 |
| `minutes_last_30d` | sum of their `minutes` | 0 |
| `days_since_last_session` | days from the date of the latest session before the cutoff (at any time) to the cutoff: a session at 22:00 the evening before counts as 1 | NaN |
| `tickets_last_90d` | support tickets opened in the last 90 days | 0 |
| `plan`, `box_size`, `region`, `acquisition_channel` | cleaned categories | |

**The model**: `random_state=42` everywhere; a quarter of the customers held back for testing, stratified by
`churned`; model comparison by ROC AUC with 5-fold stratified cross-validation (shuffled, `random_state=42`)
on the training customers only. Choose the model with the higher mean ROC AUC, unless logistic regression is
within 0.01 of it: then logistic regression, which is simpler to explain.

## The offer

Marketing's numbers (`evaluate.py`):

| Name | Value | Meaning |
|------|-------|---------|
| `OFFER_COST` | £15 | what one offer costs, whether or not the customer would have left |
| `SAVED_VALUE` | £120 | the margin from a customer who stays because of the offer |
| `SAVE_RATE` | 0.4 | in Marketing's spring trial, 4 in 10 customers who were about to cancel stayed when offered |
| `MAX_SHARE` | 0.10 | the budget: offers for at most 10% of the active customers in a month |

A customer is **offered** when their score is at or above the threshold. For a threshold, on a set of
customers whose outcome is known: `offers` = customers offered, `churners_reached` = offered customers who
churned, `precision` = churners_reached / offers (0 when there are no offers), `recall` = churners_reached /
all churners, and

    profit = churners_reached × SAVE_RATE × SAVED_VALUE − offers × OFFER_COST

Thresholds are 0.01, 0.02 … 0.99. **The chosen threshold** is the one with the highest profit among those
that offer to at most `MAX_SHARE` of the customers; on a tie, the highest of them.

## What you will have at the end

    python -m fernhill_churn explore                      reports/figures/ (three charts)
    python -m fernhill_churn train                        reports/ and models/churn_model.joblib
    python -m fernhill_churn score --month 2026-10        out/at_risk_2026-10.csv

| Writes | What it is |
|--------|------------|
| `reports/metrics.json` | the chosen model's results on the test customers, the threshold and its profit |
| `reports/profit_by_threshold.csv` | the profit table, one row per threshold |
| `reports/permutation_importance.csv` | how much each feature matters to the model |
| `reports/figures/*.png` | three exploration charts and four evaluation charts |
| `models/churn_model.joblib` | the fitted pipeline, its threshold, the model's name, the cutoff and the features |
| `out/at_risk_YYYY-MM.csv` | `customer_id,churn_probability,rank`: the customers active on the first day of the month whose score is at or above the threshold, most likely first, at most 10% of the active customers |

`tests/test_churn.py` holds your unit tests (`make test`), and `make lint` runs ruff on your code. `models/`
and `out/` are in `.gitignore`: `make train` and `make score` rebuild them.
