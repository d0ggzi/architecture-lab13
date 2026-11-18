from src.db.database import retry_db, session


def to_order(row):
    data = dict(row)
    data["notification_sent"] = bool(data["notification_sent"])
    return data


@retry_db
def create(user_id, item, amount):
    with session() as connection:
        cursor = connection.execute(
            "INSERT INTO orders (user_id, item, amount, status) VALUES (?, ?, ?, ?)",
            (user_id, item, amount, "created"),
        )
        return cursor.lastrowid


@retry_db
def set_notification_sent(order_id, sent):
    with session() as connection:
        connection.execute(
            "UPDATE orders SET notification_sent = ? WHERE id = ?",
            (int(sent), order_id),
        )


@retry_db
def get_by_id(order_id):
    with session() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
    return to_order(row) if row else None


@retry_db
def list_orders(limit, offset):
    with session() as connection:
        rows = connection.execute(
            "SELECT * FROM orders ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [to_order(row) for row in rows]
