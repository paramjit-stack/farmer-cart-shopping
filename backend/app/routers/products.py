from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.shop import CartItem
from app.schemas.product import ProductInput, ProductOutput, StockInput, StatusInput
from app.core.dependencies import admin_only

router = APIRouter(tags=["Products"])

@router.get("/api/products", response_model=list[ProductOutput])
def public_products(search: str = "", category: str = "", db: Session = Depends(get_db)):
    query = select(Product).where(Product.status == "active")
    if search.strip():
        query = query.where(Product.name.ilike(f"%{search.strip()}%"))
    if category.strip():
        query = query.where(Product.category == category.strip())
    return db.scalars(query.order_by(Product.id.desc())).all()

@router.get("/api/products/{product_id}", response_model=ProductOutput)
def product_details(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or product.status != "active":
        raise HTTPException(404, "Product not found")
    return product

@router.get("/api/admin/products", response_model=list[ProductOutput], dependencies=[Depends(admin_only)])
def all_products(db: Session = Depends(get_db)):
    return db.scalars(select(Product).order_by(Product.id.desc())).all()

@router.post("/api/admin/products", response_model=ProductOutput, status_code=201, dependencies=[Depends(admin_only)])
def create_product(data: ProductInput, db: Session = Depends(get_db)):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/api/admin/products/{product_id}", response_model=ProductOutput, dependencies=[Depends(admin_only)])
def update_product(product_id: int, data: ProductInput, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    for key, value in data.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@router.patch("/api/admin/products/{product_id}/status", response_model=ProductOutput, dependencies=[Depends(admin_only)])
def update_status(product_id: int, data: StatusInput, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    product.status = data.status
    db.commit()
    db.refresh(product)
    return product

@router.patch("/api/admin/products/{product_id}/stock", response_model=ProductOutput, dependencies=[Depends(admin_only)])
def update_stock(product_id: int, data: StockInput, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    product.available_quantity = data.available_quantity
    db.commit()
    db.refresh(product)
    return product

@router.delete("/api/admin/products/{product_id}", dependencies=[Depends(admin_only)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    # Historical orders retain their item snapshots. Remove pending cart references first.
    for item in db.scalars(select(CartItem).where(CartItem.product_id == product_id)).all():
        db.delete(item)
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
