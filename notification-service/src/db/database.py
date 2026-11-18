import sqlite3
from contextlib import contextmanager
from pathlib import Path

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from src.settings.config import get_settings


def retry_db(func):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.2),
        retry=retry_if_exception_type(sqlite3.OperationalError),
        reraise=True,
    )(func)


@contextmanager
def session():
    settings = get_settings()
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


@retry_db
def init_db():
    with session() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS notifications ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "order_id INTEGER NOT NULL UNIQUE, "
            "user_id INTEGER NOT NULL, "
            "email TEXT NOT NULL, "
            "message TEXT NOT NULL, "
            "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_notifications_order_id "
            "ON notifications (order_id)"
        )
