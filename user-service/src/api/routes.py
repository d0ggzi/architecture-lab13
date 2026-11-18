import fastapi
from fastapi import APIRouter, Query

from src.api.schemas import User, UserCreate
from src.service import users
from src.service.exceptions import EmailAlreadyExists, UserNotFound

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/users", response_model=list[User])
def list_users(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return users.list_users(limit, offset)


@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    try:
        return users.get_user(user_id)
    except UserNotFound as exc:
        raise fastapi.HTTPException(status_code=404, detail="User not found") from exc


@router.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    try:
        return users.create_user(user.name, user.email)
    except EmailAlreadyExists as exc:
        raise fastapi.HTTPException(status_code=409, detail="Email already in use") from exc
