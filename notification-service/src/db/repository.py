from src.db.database import retry_db, session


def to_notification(row):
    data = dict(row)
    data["status"] = "sent"
    return data


@retry_db
def create(order_id, user_id, email, message):
    with session() as connection:
        connection.execute(
            "INSERT INTO notifications (order_id, user_id, email, message) "
            "VALUES (?, ?, ?, ?) ON CONFLICT(order_id) DO NOTHING",
            (order_id, user_id, email, message),
        )
        row = connection.execute(
            "SELECT * FROM notifications WHERE order_id = ?",
            (order_id,),
        ).fetchone()
    return to_notification(row)


@retry_db
def list_notifications(limit, offset):
    with session() as connection:
        rows = connection.execute(
            "SELECT * FROM notifications ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [to_notification(row) for row in rows]
