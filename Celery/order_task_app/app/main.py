from fastapi import FastAPI
from app.database import Base, engine
from app.routers.order_router import router as order_router
from app.routers.seed_router import router as seed_router

from app.models.user import User
from app.models.product import Product
from app.models.order import Order

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Task Management App")

app.include_router(order_router)
app.include_router(seed_router)
