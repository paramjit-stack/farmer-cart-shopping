from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.shop import router as shop_router

app = FastAPI(title="Farmer Shopping Cart API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(shop_router)

@app.get("/")
def home():
    return {"message": "Farmer Shopping Cart API is running"}

@app.get("/health")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "success", "database": "connected"}
