import fastapi
from fastapi import APIRouter, Query

from src.api.schemas import Order, OrderCreate
from src.service import orders
from src.service.exceptions import OrderNotFound, ServiceUnavailable, UserNotFound

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/orders", response_model=list[Order])
def list_orders(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return orders.list_orders(limit, offset)


@router.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    try:
        return orders.get_order(order_id)
    except OrderNotFound as exc:
        raise fastapi.HTTPException(status_code=404, detail="Order not found") from exc


@router.post("/orders", response_model=Order, status_code=201)
def create_order(order: OrderCreate):
    try:
        return orders.create_order(order.user_id, order.item, order.amount)
    except UserNotFound as exc:
        raise fastapi.HTTPException(status_code=404, detail="User not found") from exc
    except ServiceUnavailable as exc:
        raise fastapi.HTTPException(status_code=503, detail=str(exc)) from exc
