from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.services.cache_service import get_cache, set_cache, delete_cache


def product_to_dict(product: Product):
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "stock": product.stock
    }


async def create_product_service(product_data: ProductCreate, db: Session):
    product = Product(
        name=product_data.name,
        category=product_data.category,
        price=product_data.price,
        stock=product_data.stock
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


async def get_product_service(product_id: int, db: Session):
    cache_key = f"product:{product_id}"

    cached_product = await get_cache(cache_key)

    if cached_product:
        return {
            "cache_status": "HIT",
            "source": "Redis Cache",
            "product": cached_product
        }

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_dict = product_to_dict(product)

    await set_cache(cache_key, product_dict)

    return {
        "cache_status": "MISS",
        "source": "Database",
        "product": product_dict
    }


async def update_product_service(
    product_id: int,
    product_data: ProductUpdate,
    db: Session
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.category is not None:
        product.category = product_data.category

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.stock is not None:
        product.stock = product_data.stock

    db.commit()
    db.refresh(product)

    cache_key = f"product:{product_id}"

    await delete_cache(cache_key)

    return {
        "message": "Product updated and old cache deleted",
        "product": product
    }
