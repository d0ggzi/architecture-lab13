import logging

from src.db import repository
from src.service.clients import get_user, send_notification
from src.service.exceptions import OrderNotFound, ServiceUnavailable, UserNotFound

logger = logging.getLogger("order-service")


def create_order(user_id, item, amount):
    try:
        user = get_user(user_id)
    except ServiceUnavailable as exc:
        raise ServiceUnavailable("user-service is unavailable") from exc

    if user is None:
        raise UserNotFound(user_id)

    order_id = repository.create(user_id, item, amount)
    message = f"Заказ №{order_id} на «{item}» создан"
    notification_sent = False

    try:
        send_notification(order_id, user["id"], user["email"], message)
        notification_sent = True
    except ServiceUnavailable as exc:
        logger.warning("notification was not sent: %s", exc)

    repository.set_notification_sent(order_id, notification_sent)
    return repository.get_by_id(order_id)


def get_order(order_id):
    order = repository.get_by_id(order_id)
    if order is None:
        raise OrderNotFound(order_id)
    return order


def list_orders(limit, offset):
    return repository.list_orders(limit, offset)
