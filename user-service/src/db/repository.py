from src.db.database import retry_db, session


@retry_db
def create(name, email):
    with session() as connection:
        cursor = connection.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email),
        )
        return cursor.lastrowid


@retry_db
def get_by_id(user_id):
    with session() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


@retry_db
def list_users(limit, offset):
    with session() as connection:
        rows = connection.execute(
            "SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(row) for row in rows]
