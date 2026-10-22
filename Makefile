help:  ## list the targets (the default: plain `make` never regenerates your files)
	@grep -E '^[a-z-]+:.*## ' Makefile | sed 's/:.*## /\t/'

.PHONY: help data explore train score test lint notebook check

# The Python to run. On a Mac or Linux machine without a `python` command: make test PYTHON=python3
PYTHON ?= python
MONTH ?= 2026-10

data:  ## (re)create data/raw/ exactly as it was: Fernhill Box's export up to 30 September 2026
	$(PYTHON) -m fernhill_box

explore:  ## step 2: the three charts in reports/figures/
	$(PYTHON) -m fernhill_churn explore

train:  ## steps 7 and 8: fit the chosen model, choose the threshold, write reports/ and models/
	$(PYTHON) -m fernhill_churn train

score:  ## step 8: next month's list: make score MONTH=2026-10
	$(PYTHON) -m fernhill_churn score --month $(MONTH)

test:  ## your tests (step 8)
	$(PYTHON) -m pytest -q tests/test_churn.py

lint:  ## ruff on your code (and on tests/test_churn.py once step 8 creates it)
	$(PYTHON) -m ruff check fernhill_churn $(wildcard tests/test_churn.py)

notebook:  ## run the exploration notebook from top to bottom (it is saved with its outputs)
	$(PYTHON) -m jupyter nbconvert --to notebook --execute --inplace notebooks/explore.ipynb

check:  ## the project's checks on your machine: needs the local check kit in .projlabs/ (Review page)
	$(PYTHON) .projlabs/check.py
