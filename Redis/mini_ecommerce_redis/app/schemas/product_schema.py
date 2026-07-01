from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = None
    stock: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int

    class Config:
        from_attributes = True
