import logging
import time

import requests
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from src.service.exceptions import ServiceUnavailable
from src.settings.config import get_settings

settings = get_settings()

logger = logging.getLogger("order-service")


class CircuitBreaker:
    def __init__(self, threshold, timeout):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.opened_at = None

    def allow(self):
        if self.opened_at is None:
            return True
        if time.monotonic() - self.opened_at < self.timeout:
            return False
        self.failures = self.threshold - 1
        self.opened_at = None
        return True

    def success(self):
        self.failures = 0
        self.opened_at = None

    def failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = time.monotonic()


user_breaker = CircuitBreaker(settings.breaker_threshold, settings.breaker_timeout)
notification_breaker = CircuitBreaker(settings.breaker_threshold, settings.breaker_timeout)


@retry(
    stop=stop_after_attempt(settings.retry_attempts),
    wait=wait_fixed(settings.retry_wait),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def request(method, url, breaker, payload=None):
    try:
        return requests.request(method, url, json=payload, timeout=settings.request_timeout)
    except requests.RequestException:
        breaker.failure()
        raise


def get_user(user_id):
    if not user_breaker.allow():
        raise ServiceUnavailable("user-service is unavailable")

    try:
        response = request("GET", f"{settings.user_service_url}/users/{user_id}", user_breaker)
    except requests.RequestException as exc:
        logger.warning("user-service request failed: %s", exc)
        raise ServiceUnavailable("user-service is unavailable") from exc

    if response.status_code == 404:
        user_breaker.success()
        return None

    if response.status_code != 200:
        user_breaker.failure()
        raise ServiceUnavailable("user-service returned an error")

    user_breaker.success()
    return response.json()


def send_notification(order_id, user_id, email, message):
    if not notification_breaker.allow():
        raise ServiceUnavailable("notification-service is unavailable")

    payload = {
        "order_id": order_id,
        "user_id": user_id,
        "email": email,
        "message": message,
    }

    try:
        response = request(
            "POST",
            f"{settings.notification_service_url}/notify",
            notification_breaker,
            payload,
        )
    except requests.RequestException as exc:
        logger.warning("notification-service request failed: %s", exc)
        raise ServiceUnavailable("notification-service is unavailable") from exc

    if response.status_code != 201:
        notification_breaker.failure()
        raise ServiceUnavailable("notification-service returned an error")

    notification_breaker.success()
    return response.json()
