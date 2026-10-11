from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import customer_only
from app.models.user import User
from app.models.product import Product
from app.models.shop import Cart, CartItem, Order, OrderItem

router = APIRouter(tags=["Cart and Orders"])

class CartInput(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

class QuantityInput(BaseModel):
    quantity: int = Field(gt=0)

def get_cart(db, user_id):
    cart = db.scalar(select(Cart).where(Cart.user_id == user_id))
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()
    return cart

def cart_response(db, cart):
    rows = db.execute(select(CartItem, Product).join(Product, CartItem.product_id == Product.id).where(CartItem.cart_id == cart.id)).all()
    items = [{"id": item.id, "product_id": product.id, "name": product.name, "price": product.price, "image_url": product.image_url, "quantity": item.quantity, "available_quantity": product.available_quantity, "status": product.status, "subtotal": product.price * item.quantity} for item, product in rows]
    return {"items": items, "grand_total": sum((x["subtotal"] for x in items), Decimal("0.00"))}

@router.get("/api/cart")
def view_cart(db: Session = Depends(get_db), user: User = Depends(customer_only)):
    cart = get_cart(db, user.id)
    db.commit()
    return cart_response(db, cart)

@router.post("/api/cart/items", status_code=201)
def add_to_cart(data: CartInput, db: Session = Depends(get_db), user: User = Depends(customer_only)):
    product = db.get(Product, data.product_id)
    if not product or product.status != "active":
        raise HTTPException(404, "Active product not found")
    cart = get_cart(db, user.id)
    item = db.scalar(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id))
    new_quantity = data.quantity + (item.quantity if item else 0)
    if new_quantity > product.available_quantity:
        raise HTTPException(400, "Quantity exceeds available stock")
    if item:
        item.quantity = new_quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=data.quantity))
    db.commit()
    return cart_response(db, cart)

@router.put("/api/cart/items/{item_id}")
def update_cart(item_id: int, data: QuantityInput, db: Session = Depends(get_db), user: User = Depends(customer_only)):
    cart = get_cart(db, user.id)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if not item:
        raise HTTPException(404, "Cart item not found")
    product = db.get(Product, item.product_id)
    if not product or product.status != "active" or data.quantity > product.available_quantity:
        raise HTTPException(400, "Product unavailable or insufficient stock")
    item.quantity = data.quantity
    db.commit()
    return cart_response(db, cart)

@router.delete("/api/cart/items/{item_id}")
def remove_cart(item_id: int, db: Session = Depends(get_db), user: User = Depends(customer_only)):
    cart = get_cart(db, user.id)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if not item:
        raise HTTPException(404, "Cart item not found")
    db.delete(item)
    db.commit()
    return cart_response(db, cart)

@router.post("/api/orders/checkout", status_code=201)
def checkout(db: Session = Depends(get_db), user: User = Depends(customer_only)):
    try:
        cart = get_cart(db, user.id)
        items = db.scalars(select(CartItem).where(CartItem.cart_id == cart.id).order_by(CartItem.product_id)).all()
        if not items:
            raise HTTPException(400, "Cart is empty")
        # Lock stock rows in stable order until the transaction commits.
        products = {p.id: p for p in db.scalars(select(Product).where(Product.id.in_([i.product_id for i in items])).order_by(Product.id).with_for_update()).all()}
        total = Decimal("0.00")
        for item in items:
            product = products.get(item.product_id)
            if not product or product.status != "active" or item.quantity <= 0 or item.quantity > product.available_quantity:
                raise HTTPException(400, f"Insufficient stock or inactive product: {item.product_id}")
            total += product.price * item.quantity
        order = Order(user_id=user.id, grand_total=total, status="placed")
        db.add(order)
        db.flush()
        for item in items:
            product = products[item.product_id]
            db.add(OrderItem(order_id=order.id, product_id=product.id, product_name=product.name, quantity=item.quantity, unit_price=product.price, subtotal=product.price * item.quantity))
            product.available_quantity -= item.quantity
            db.delete(item)
        order_id = order.id
        db.commit()
        return {"message": "Checkout successful", "order_id": order_id, "grand_total": total}
    except Exception:
        db.rollback()
        raise

@router.get("/api/orders")
def view_orders(db: Session = Depends(get_db), user: User = Depends(customer_only)):
    orders = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())).all()
    return [{"id": o.id, "grand_total": o.grand_total, "status": o.status, "created_at": o.created_at, "items": [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price, "subtotal": i.subtotal} for i in db.scalars(select(OrderItem).where(OrderItem.order_id == o.id)).all()]} for o in orders]
