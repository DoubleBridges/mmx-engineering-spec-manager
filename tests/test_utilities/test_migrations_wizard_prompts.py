from types import SimpleNamespace
from sqlalchemy import create_engine

from mmx_engineering_spec_manager.utilities.migrations import migrate_sqlite_wizard_prompts_add_missing_columns


def _cols(engine, table: str):
    with engine.connect() as conn:
        res = conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
        return {row[1] for row in res}


def test_wizard_prompts_migration_adds_missing_spec_group_sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE wizard_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT,
                project_id INTEGER NOT NULL
            )
            """
        )
    migrate_sqlite_wizard_prompts_add_missing_columns(engine)
    cols = _cols(engine, "wizard_prompts")
    assert "specification_group_id" in cols


def test_wizard_prompts_migration_is_noop_when_column_exists():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE wizard_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT,
                project_id INTEGER NOT NULL,
                specification_group_id INTEGER
            )
            """
        )
    before = _cols(engine, "wizard_prompts")
    migrate_sqlite_wizard_prompts_add_missing_columns(engine)
    after = _cols(engine, "wizard_prompts")
    assert before == after


ess = SimpleNamespace(url="postgresql://localhost/db")

def test_wizard_prompts_migration_returns_early_for_non_sqlite():
    migrate_sqlite_wizard_prompts_add_missing_columns(ess)  # type: ignore[arg-type]
