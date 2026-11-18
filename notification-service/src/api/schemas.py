from pydantic import BaseModel, EmailStr, Field


class NotificationCreate(BaseModel):
    order_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    email: EmailStr
    message: str = Field(min_length=1, max_length=500)


class Notification(BaseModel):
    id: int
    order_id: int
    user_id: int
    email: EmailStr
    message: str
    status: str
