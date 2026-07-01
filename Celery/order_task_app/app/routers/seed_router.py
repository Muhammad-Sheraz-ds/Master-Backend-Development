from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    # Check if user already exists
    user = db.query(User).filter(User.email == "alice@example.com").first()
    if not user:
        user = User(name="Alice", email="alice@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Check if product already exists
    product = db.query(Product).filter(Product.name == "Laptop").first()
    if not product:
        product = Product(name="Laptop", price=999.99, stock=10)
        db.add(product)
        db.commit()
        db.refresh(product)

    return {
        "message": "Database seeded successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock
        }
    }
