from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    order_id: int
    status: str
    total_price: float | None = None
