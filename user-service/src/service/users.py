import sqlite3

from src.db import repository
from src.service.exceptions import EmailAlreadyExists, UserNotFound


def create_user(name, email):
    try:
        user_id = repository.create(name, email)
    except sqlite3.IntegrityError as exc:
        raise EmailAlreadyExists(email) from exc
    return repository.get_by_id(user_id)


def get_user(user_id):
    user = repository.get_by_id(user_id)
    if user is None:
        raise UserNotFound(user_id)
    return user


def list_users(limit, offset):
    return repository.list_users(limit, offset)
