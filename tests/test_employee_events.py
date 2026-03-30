"""
Tests for the employee_events Python package.
Run with:  pytest tests/test_employee_events.py -v
"""

import sqlite3
import pytest
from pathlib import Path

# ── Project path ─────────────────────────────────────────────────────
# Points to the SQLite database shipped inside the Python package source.
# Adjust this if running tests after `pip install` (the db is then inside
# the installed package directory).
DB_PATH = Path(__file__).parent.parent / "python-package" / "employee_events" / "employee_events.db"


# ════════════════════════════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def db_path():
    """
    Return the Path to employee_events.db.

    This fixture is used by all table-existence tests so they all share
    the same resolved database path.
    """
    return DB_PATH


# ════════════════════════════════════════════════════════════════════
# Tests
# ════════════════════════════════════════════════════════════════════

def test_db_exists(db_path):
    """The employee_events.db file must exist at the expected path."""
    assert db_path.exists(), (
        f"Database not found at: {db_path}\n"
        "Ensure the python-package has been built or the path is correct."
    )


def test_employee_table_exists(db_path):
    """The 'employee' table must exist in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='employee'"
    )
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "Table 'employee' was not found in the database."


def test_team_table_exists(db_path):
    """The 'team' table must exist in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='team'"
    )
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "Table 'team' was not found in the database."


def test_employee_events_table_exists(db_path):
    """The 'employee_events' table must exist in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='employee_events'"
    )
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "Table 'employee_events' was not found in the database."
