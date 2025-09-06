from __future__ import annotations
from typing import Iterable, Set
from contextlib import contextmanager

from sqlalchemy.engine import Engine

from mmx_engineering_spec_manager.utilities.logging_config import get_logger


@contextmanager
def _connect(engine: Engine):
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


def _sqlite_table_columns(engine: Engine, table: str) -> Set[str]:
    cols: Set[str] = set()
    with _connect(engine) as conn:
        res = conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
        for row in res:
            # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
            cols.add(str(row[1]))
    return cols


def migrate_sqlite_products_add_missing_columns(engine: Engine) -> None:
    """
    Perform an in-place, minimal migration for SQLite to add newly introduced nullable
    columns on the 'products' table, if they are missing from an existing database.

    Added columns (all REAL/nullable):
      - width, height, depth
      - x_origin_from_right, y_origin_from_face, z_origin_from_bottom
    """
    logger = get_logger(__name__)

    try:
        # Only attempt for SQLite
        if not str(engine.url).startswith("sqlite"):
            return

        expected: dict[str, str] = {
            "width": "REAL",
            "height": "REAL",
            "depth": "REAL",
            "x_origin_from_right": "REAL",
            "y_origin_from_face": "REAL",
            "z_origin_from_bottom": "REAL",
        }
        existing = _sqlite_table_columns(engine, "products")
        to_add = [name for name in expected.keys() if name not in existing]
        if not to_add:
            return

        with _connect(engine) as conn:
            for col in to_add:
                sql = f"ALTER TABLE products ADD COLUMN {col} {expected[col]} NULL"
                conn.exec_driver_sql(sql)
                logger.info("Applied migration: %s", sql)
    except Exception as e:  # pragma: no cover
        # Do not crash app startup because of a failed helper migration
        logger.exception("SQLite migration for products failed: %s", e)
        # intentionally swallow to keep app usable; user can recreate DB if needed
        return
