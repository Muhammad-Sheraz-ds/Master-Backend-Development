import time
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.order import Order
from app.models.product import Product

@celery_app.task(name="process_order")
def process_order(order_id: int):
    db = SessionLocal()

    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return {"error": "Order not found"}

        order.status = "processing"
        db.commit()

        time.sleep(3)

        product = db.query(Product).filter(Product.id == order.product_id).first()

        if not product:
            order.status = "failed"
            db.commit()
            return {"error": "Product not found"}

        if product.stock < order.quantity:
            order.status = "failed"
            db.commit()
            return {
                "order_id": order.id,
                "message": "Not enough stock"
            }

        product.stock -= order.quantity
        order.total_price = product.price * order.quantity
        order.status = "completed"

        db.commit()

        return {
            "order_id": order.id,
            "status": order.status,
            "total_price": order.total_price
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()
