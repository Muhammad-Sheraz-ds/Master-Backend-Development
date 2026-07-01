from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.services.product_service import (
    create_product_service,
    get_product_service,
    update_product_service
)
from app.services.cache_service import get_cache_ttl, delete_cache


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/")
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    return await create_product_service(product_data, db)


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    return await get_product_service(product_id, db)


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    return await update_product_service(product_id, product_data, db)


@router.get("/{product_id}/cache-ttl")
async def get_product_cache_ttl(product_id: int):
    cache_key = f"product:{product_id}"

    ttl = await get_cache_ttl(cache_key)

    return {
        "cache_key": cache_key,
        "ttl_seconds": ttl
    }


@router.delete("/{product_id}/cache")
async def delete_product_cache(product_id: int):
    cache_key = f"product:{product_id}"

    await delete_cache(cache_key)

    return {
        "message": "Cache deleted",
        "cache_key": cache_key
    }
