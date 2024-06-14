import pandas as pd
import json
from db import engine, Product, Category, Order, Customer, Seller
from sqlalchemy.orm import sessionmaker


def clean_data_orders(file_path):
    print(f"File: {file_path}")
    df = pd.read_csv(file_path, sep=';')
    # Eliminar filas con valores nulos
    df.dropna(inplace=True)
    # Eliminar duplicados si existen
    df = df.drop_duplicates()
    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M')
    
    # Reemplazar comas por puntos y convertir a float
    df['price_MRP'] = df['price_MRP'].astype(str).str.replace(',', '.').astype(float)
    df['payment'] = df['payment'].astype(str).str.replace(',', '.').astype(float)
    
    # Convertir los otros campos a enteros
    df['quantity'] = df['quantity'].astype(int)
    df['rating'] = df['rating'].astype(int)
    df['product_weight_g'] = df['product_weight_g'].astype(int)
    df['product_length_cm'] = df['product_length_cm'].astype(int)
    df['product_height_cm'] = df['product_height_cm'].astype(int)
    df['product_width_cm'] = df['product_width_cm'].astype(int)
    df['payment_installments'] = df['payment_installments'].astype(int)
    


    # Crear las ordenes
    create_orders(df)

def create_orders(df):
    Session = sessionmaker(bind=engine)
    session = Session()
    for index, row in df.iterrows():
        if pd.isnull(row['product_id']) or pd.isnull(row['customer_id']) or pd.isnull(row['seller_id']) or pd.isnull(row['product_category']) or pd.isnull(row['order_id']):
            continue
        product = session.query(Product).filter_by(objectID=row['product_id']).first()
        ## Buscar otro attr para hacer el match
        if product is None:
            continue
        customer = session.query(Customer).filter_by(customer_id=row['customer_id']).one_or_none()
        if customer is None:
            customer = Customer(customer_id=row['customer_id'], city=row['customer_city'], state=row['customer_state'])
            session.add(customer)
            session.commit()

        seller = session.query(Seller).filter_by(seller_id=row['seller_id']).one_or_none()
        if seller is None:
            seller = Seller(seller_id=row['seller_id'], city=row['seller_city'], state=row['seller_state'])
            session.add(seller)
            session.commit()
        category = session.query(Category).filter_by(name=row['product_category']).one_or_none()
        if category is None:
            category = Category(name=row['product_category'])
            session.add(category)
            session.commit()
        order = session.query(Order).filter_by(order_id=row['order_id']).one_or_none()
        if order is None:
            order = Order(
                order_id=row['order_id'],
                customer_id=customer.id,
                quantity=row['quantity'] if row['quantity'] else 0,
                price_MRP=row['price_MRP'] if row['price_MRP'] else 0,
                payment=row['payment'] if row['payment'] else 0,
                timestamp=row['timestamp'] if row['timestamp'] else None,
                rating=row['rating'] if row['rating'] else 0,
                category_id=category.id,
                product_id=product.id,
                payment_type=row['payment_type'] if row['payment_type'] else None,
                order_status=row['order_status'] if row['order_status'] else None,
                weight=row['product_weight_g']  if row['product_weight_g'] else 0,
                length=row['product_length_cm'] if row['product_length_cm'] else 0,
                width=row['product_width_cm'] if row['product_width_cm'] else 0,
                height=row['product_height_cm'] if row['product_height_cm'] else 0,
                seller_id=seller.id,
                payment_installments=row['payment_installments' ] if row['payment_installments'] else 0,
            )
            session.add(order)
            session.commit()

def clean_data_products(file_path):
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f"File: {file_path}")
    with open(file_path, 'r') as file:
        data = json.load(file)
    for products in data:    
        if products['categories']:
            catergory = category_builder(products['categories'], session)
        price_min, price_max = check_price_range(products['price_range'])
        product = session.query(Product).filter_by(name=products['name']).one_or_none()
        if product is not None:
            continue
        product = Product(
            objectID=products['objectID'],
            name=products['name'],
            description=products['description'],
            brand=products['brand'],
            category_id=catergory.id,
            type=products['type'] ,
            price=products['price'] ,
            price_min=price_min if price_min else None,
            price_max=price_max if price_max else None,
            image=products['image'],
            free_shipping=products['free_shipping'],
            popularity=products['popularity'],
            rating=products['rating']
        )
        session.add(product)
        session.commit()


def category_builder(categories, session):
    parent = None
    for category in categories:
        current_category = session.query(Category).filter_by(name=category).one_or_none()
        if current_category is None:
            if parent is None:
                category = Category(name=category)
                session.add(category)
                session.commit()
            else:
                category = Category(name=category, parent_id=parent.id)
                session.add(category)
                session.commit()
            parent = category
        else:
            parent = current_category
    return parent

def check_price_range(price_range):
    if not price_range:
        return None, None
    if '-' in price_range:
        if price_range.split(' - ')[0].isalnum():
            price_min = int(price_range.split(' - ')[0])
        if price_range.split(' - ')[1].isalnum():
            price_max = int(price_range.split(' - ')[1])
    elif '>' in price_range:
        price_min = int(price_range.split('> ')[1])
        price_max = None
    elif '<' in price_range:
        price_min = None
        price_max = int(price_range.split('< ')[1])
    return price_min, price_max