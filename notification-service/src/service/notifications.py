import logging

from src.db import repository

logger = logging.getLogger("notification-service")


def send_notification(order_id, user_id, email, message):
    notification = repository.create(order_id, user_id, email, message)
    logger.info("email to %s: %s", email, message)
    return notification


def list_notifications(limit, offset):
    return repository.list_notifications(limit, offset)
