from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: int = Field(gt=0)
    item: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0)


class Order(BaseModel):
    id: int
    user_id: int
    item: str
    amount: float
    status: str
    notification_sent: bool
