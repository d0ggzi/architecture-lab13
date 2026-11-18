from fastapi import APIRouter, Query

from src.api.schemas import Notification, NotificationCreate
from src.service import notifications

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/notifications", response_model=list[Notification])
def list_notifications(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return notifications.list_notifications(limit, offset)


@router.post("/notify", response_model=Notification, status_code=201)
def send_notification(payload: NotificationCreate):
    return notifications.send_notification(
        payload.order_id,
        payload.user_id,
        payload.email,
        payload.message,
    )
