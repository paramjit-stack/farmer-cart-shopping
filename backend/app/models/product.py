from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    farmer_name = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    available_quantity = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500))
    status = Column(Enum("active", "inactive"), nullable=False, default="active")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
