from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.schemas.order_schema import OrderCreate
from app.tasks.order_tasks import process_order
from app.celery_app import celery_app

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/orders")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == order_data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    product = db.query(Product).filter(Product.id == order_data.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    order = Order(
        user_id=order_data.user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    task = process_order.delay(order.id)

    return {
        "message": "Order created and processing started",
        "order_id": order.id,
        "task_id": task.id
    }


@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.id,
        "status": order.status,
        "total_price": order.total_price
    }


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
