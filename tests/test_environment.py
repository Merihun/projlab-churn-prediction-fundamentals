"""Verify your lab. Run inside the workspace: python -m pytest -q tests/test_environment.py"""

import sys

import pytest


def test_python_version():
    assert sys.version_info[:2] == (3, 12), sys.version


def test_packages_import():
    import jupyterlab  # noqa: F401
    import pandas  # noqa: F401
    import psycopg  # noqa: F401


def test_machine_learning_packages():
    import joblib
    import matplotlib
    import sklearn

    assert sklearn.__version__ == "1.9.1", sklearn.__version__
    assert matplotlib.__version__ == "3.11.2", matplotlib.__version__
    assert joblib.__version__ == "1.6.0", joblib.__version__


@pytest.mark.service
def test_postgres_is_reachable(pg_conninfo):
    import psycopg

    with psycopg.connect(**pg_conninfo) as conn:
        version = conn.execute("SHOW server_version").fetchone()[0]
    assert version.startswith("16."), version
