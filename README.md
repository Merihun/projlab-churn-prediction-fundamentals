# Will They Stay? Predicting Subscription Churn

Start with **PROJECT.md**: what is provided, how to start the lab, the commands and the rules the checks use.

The lab (`docker compose up -d --build --wait`) runs two services:

- `workspace`: Python 3.12 with pandas, scikit-learn, matplotlib, joblib, JupyterLab, pytest and ruff. Open
  a terminal in it with `docker compose exec workspace bash`; this folder is `/workspace`. JupyterLab is at
  <http://127.0.0.1:8888> (token `projlab`).
- `postgres`: PostgreSQL 16, part of the lab template. This project doesn't use it.

Your code goes in `fernhill_churn/`, your written answers in `answers/`; the commands are in the `Makefile`
(`make` lists them).
