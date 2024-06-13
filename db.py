import os
from sqlalchemy import create_engine, ForeignKey, String, Column, Integer, Boolean, Float, DateTime
from sqlalchemy.orm import relationship, declarative_base

from dotenv import load_dotenv

Base = declarative_base()
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    DATABASE_URL = os.getenv("DATABASE_URL_PRODUCTION")
else:
    DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL)
connection = engine.connect()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    quantity = Column(Integer)
    price_MRP = Column(Integer)
    payment = Column(Float)
    timestamp = Column(DateTime)
    rating = Column(Integer)
    category_id = Column(Integer, ForeignKey('categories.id'))
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False) 
    payment_type = Column(String)
    order_status = Column(String)
    weight = Column(Integer)
    length = Column(Integer)
    height = Column(Integer)
    width = Column(Integer)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=False)
    payment_installments = Column(Integer)

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String)
    city = Column(String)
    state = Column(String)

class Seller(Base):
    __tablename__ = 'sellers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(String)
    city = Column(String)
    state = Column(String)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objectID = Column(String)
    name = Column(String)
    description = Column(String)
    brand = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id')) 
    type = Column(String)
    price = Column(Float)
    price_min = Column(Integer)
    price_max = Column(Integer)
    image = Column(String)
    free_shipping = Column(Boolean)
    popularity = Column(Integer)
    rating = Column(Integer)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    parent = relationship('Category', remote_side=[id])
    products = relationship('Product', backref='category')


Base.metadata.create_all(engine)

