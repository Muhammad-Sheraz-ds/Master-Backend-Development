from fastapi import FastAPI

from app.database import Base, engine
from app.routes.product_routes import router as product_router
from app.models import product_model


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mini E-commerce Redis Cache API"
)


app.include_router(product_router)


@app.get("/")
def home():
    return {
        "message": "Mini E-commerce Redis Cache API is running"
    }
