from types import SimpleNamespace
from sqlalchemy import create_engine, text

from mmx_engineering_spec_manager.utilities.migrations import migrate_sqlite_products_add_missing_columns


def _cols(engine, table: str):
    with engine.connect() as conn:
        res = conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
        return {row[1] for row in res}


def test_migration_adds_missing_product_columns_sqlite():
    # Start with a minimal products table missing the new columns
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quantity INTEGER
            )
            """
        )
    # Run migration
    migrate_sqlite_products_add_missing_columns(engine)

    cols = _cols(engine, "products")
    for c in ("width", "height", "depth", "x_origin_from_right", "y_origin_from_face", "z_origin_from_bottom", "specification_group_id"):
        assert c in cols


def test_migration_is_noop_when_columns_exist():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quantity INTEGER,
                width REAL,
                height REAL,
                depth REAL,
                x_origin_from_right REAL,
                y_origin_from_face REAL,
                z_origin_from_bottom REAL,
                specification_group_id INTEGER
            )
            """
        )
    before = _cols(engine, "products")
    migrate_sqlite_products_add_missing_columns(engine)
    after = _cols(engine, "products")
    assert before == after  # unchanged


def test_migration_returns_early_for_non_sqlite():
    # Provide a stub with a non-sqlite URL; function should return without accessing connection
    fake_engine = SimpleNamespace(url="postgresql://localhost/db")
    # Should not raise
    migrate_sqlite_products_add_missing_columns(fake_engine)  # type: ignore[arg-type]
