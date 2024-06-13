import os
import schedule
import time
from sqlalchemy.orm import sessionmaker
from db import engine, Product, Category, Order, Customer, Seller
from data_cleaning import clean_data_products, clean_data_orders
from dashboard import update_graph
from download_files import download_blobs
from dashboard import app

# Crear una sesión de SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

def job():
    # Eliminar archivos en tmp y download_files
    os.system("rm -rf ./tmp/*")

    # Eliminar todas las tuplas de las tablas
    session.query(Product).delete()
    session.query(Category).delete()
    session.query(Order).delete()
    session.query(Customer).delete()
    session.query(Seller).delete()
    session.commit()

    download_blobs()
    file_names = os.listdir('tmp')
    file_names = os.listdir('tmp')

    # Iterate over the file names
    for file_name in file_names:
        # Check if the file is a JSON file
        if file_name.endswith('.json'):
            # Read the JSON file
            file_path = os.path.join('tmp', file_name)

            # Clean the data
            clean_data_products(file_path)

    for file_name in file_names:
        # Check if the file is a CSV file
        if file_name.endswith('.csv'):
            # Read the CSV file
            file_path = os.path.join('tmp', file_name)
            clean_data_orders(file_path)
            

    # Ejecutar dashboard
    update_graph()
    app.run_server(debug=True)

# Programar el trabajo para que se ejecute cada 24 horas
schedule.every(5).minutes.do(job)

# Mantener el script en ejecución
while True:
    schedule.run_pending()
    time.sleep(1)