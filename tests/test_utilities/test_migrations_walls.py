from types import SimpleNamespace
from sqlalchemy import create_engine

from mmx_engineering_spec_manager.utilities.migrations import migrate_sqlite_walls_add_missing_columns


def _cols(engine, table: str):
    with engine.connect() as conn:
        res = conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
        return {row[1] for row in res}


def test_walls_migration_adds_missing_thicknesses_sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE walls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id TEXT,
                link_id_location TEXT,
                width REAL,
                height REAL,
                depth REAL,
                x_origin REAL,
                y_origin REAL,
                z_origin REAL,
                angle REAL,
                project_id INTEGER,
                location_id INTEGER
            )
            """
        )
    migrate_sqlite_walls_add_missing_columns(engine)
    cols = _cols(engine, "walls")
    assert "thicknesses" in cols


def test_walls_migration_is_noop_when_columns_exist():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE walls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id TEXT,
                link_id_location TEXT,
                width REAL,
                height REAL,
                depth REAL,
                x_origin REAL,
                y_origin REAL,
                z_origin REAL,
                angle REAL,
                thicknesses REAL,
                project_id INTEGER,
                location_id INTEGER
            )
            """
        )
    before = _cols(engine, "walls")
    migrate_sqlite_walls_add_missing_columns(engine)
    after = _cols(engine, "walls")
    assert before == after


def test_walls_migration_returns_early_for_non_sqlite():
    fake_engine = SimpleNamespace(url="postgresql://localhost/db")
    migrate_sqlite_walls_add_missing_columns(fake_engine)  # type: ignore[arg-type]
